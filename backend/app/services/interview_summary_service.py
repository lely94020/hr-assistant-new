import json
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.llms.tongyi import Tongyi
from langchain.prompts import PromptTemplate
import dashscope

from app.crud.interview_summary import (
    get_summary_by_recording_id,
    create_interview_summary,
    update_interview_summary
)
from app.crud.recording import get_recording_by_id
from app.crud.resume import get_resume
from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)


async def generate_interview_summary(recording_id: int, db: Session) -> Dict[str, Any]:
    """
    从录音生成面试摘要（异步版本）
    :param recording_id: 录音ID
    :param db: 数据库会话
    :return: 生成的摘要数据
    """
    try:
        # 获取录音信息
        recording = get_recording_by_id(db, recording_id)
        if not recording:
            raise ValueError(f"录音不存在: {recording_id}")

        # 检查是否有文字稿
        if not recording.transcript or recording.transcript_status != 2:
            raise ValueError("录音尚未完成转写或转写失败")

        # 获取简历信息
        resume = get_resume(db, recording.resume_id)
        if not resume:
            raise ValueError(f"简历不存在: {recording.resume_id}")

        # 计算面试时长（分钟）
        duration_minutes = recording.duration // 60 if recording.duration else 0

        # 使用AI生成摘要（异步）
        summary_data = await _generate_summary_with_ai(
            transcript=recording.transcript,
            candidate_name=resume.candidate_name,
            position_name="未知岗位",  # 可以从position表获取
            duration=duration_minutes
        )

        # 检查是否已存在摘要
        existing_summary = get_summary_by_recording_id(db, recording_id)

        if existing_summary:
            # 更新现有摘要
            updated_summary = update_interview_summary(
                db=db,
                summary_id=existing_summary.id,
                **summary_data
            )
            logger.info(f"面试摘要已更新 ID={updated_summary.id}")
            return _format_summary_response(updated_summary)
        else:
            # 创建新摘要
            new_summary = create_interview_summary(
                db=db,
                recording_id=recording_id,
                resume_id=recording.resume_id,
                **summary_data
            )
            logger.info(f"面试摘要已创建 ID={new_summary.id}")
            return _format_summary_response(new_summary)

    except Exception as e:
        logger.error(f"生成面试摘要失败: {str(e)}")
        raise


async def _generate_summary_with_ai(
    transcript: str,
    candidate_name: str,
    position_name: str,
    duration: int
) -> Dict[str, Any]:
    """
    使用AI生成面试摘要（异步版本）
    :param transcript: 面试文字稿
    :param candidate_name: 候选人姓名
    :param position_name: 应聘岗位
    :param duration: 面试时长（分钟）
    :return: 结构化摘要数据
    """
    try:
        # 设置 DashScope API Key
        api_key = settings.DASHSCOPE_API_KEY
        if not api_key:
            raise ValueError("未配置 DASHSCOPE_API_KEY，请在 .env 文件中配置")
        
        # 设置 dashscope 全局 API key
        dashscope.api_key = api_key
        
        # 初始化Tongyi大模型
        llm = Tongyi(
            model="qwen-turbo",
            dashscope_api_key=api_key,
            temperature=0.3
        )

        # 定义Prompt模板
        prompt_template = """你是一位专业的HR助手，请从以下面试记录中提取结构化摘要。

【面试信息】
候选人：{candidate_name}
应聘岗位：{position_name}
面试时长：{duration}分钟

【面试文字稿】
{transcript}

请按以下JSON格式返回摘要：
{{
    "summary_overview": "面试整体概述（150-200字，包含面试氛围、候选人整体表现等）",
    
    "key_qa": [
        {{
            "question": "面试官提出的重要问题",
            "answer_summary": "候选人回答的要点概述（100字以内）",
            "answer_quality": "优秀/良好/一般/较差"
        }}
    ],
    
    "technical_skills": ["技术能力标签1", "技术能力标签2"],
    
    "soft_skills": ["软技能标签1", "软技能标签2"],
    
    "highlights": [
        "亮点1：具体描述",
        "亮点2：具体描述"
    ],
    
    "concerns": [
        "疑虑1：具体描述",
        "疑虑2：具体描述"
    ],
    
    "candidate_questions": [
        "候选人提出的问题1",
        "候选人提出的问题2"
    ]
}}

提取要求：
1. 核心问答选择最能体现候选人能力的3-5个问题
2. 技术能力标签要具体，如"微服务架构"而非"技术能力强"
3. 亮点和疑虑要有具体事例支撑
4. 回答质量判断要基于回答的完整性、逻辑性、专业性
"""

        prompt = PromptTemplate(
            input_variables=["candidate_name", "position_name", "duration", "transcript"],
            template=prompt_template
        )

        # 处理长文本 - 如果文字稿太长，进行分块处理
        if len(transcript) > 3000:
            logger.info(f"文字稿较长 ({len(transcript)} 字符)，进行分块处理")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=3000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_text(transcript)

            # 对每个块生成摘要（异步并发处理）
            chunk_summaries = []
            for i, chunk in enumerate(chunks):
                logger.info(f"处理第 {i+1}/{len(chunks)} 块")
                chunk_prompt = prompt.format(
                    candidate_name=candidate_name,
                    position_name=position_name,
                    duration=duration,
                    transcript=chunk
                )

                try:
                    # 使用异步调用，不阻塞事件循环
                    chunk_result = await llm.ainvoke(chunk_prompt)
                    # 尝试解析JSON
                    chunk_data = _extract_json_from_response(chunk_result)
                    if chunk_data:
                        chunk_summaries.append(chunk_data)
                except Exception as e:
                    logger.warning(f"处理第 {i+1} 块时出错: {str(e)}")
                    continue

            # 汇总所有块的信息
            final_summary = _consolidate_summaries(chunk_summaries)
        else:
            # 直接处理完整文字稿
            full_prompt = prompt.format(
                candidate_name=candidate_name,
                position_name=position_name,
                duration=duration,
                transcript=transcript
            )

            # 使用异步调用，不阻塞事件循环
            result = await llm.ainvoke(full_prompt)
            final_summary = _extract_json_from_response(result)

            if not final_summary:
                raise ValueError("AI返回的结果无法解析为有效的JSON格式")
            
            # 将列表字段转换为字符串（因为数据库是 TEXT 类型）
            if isinstance(final_summary.get("highlights"), list):
                final_summary["highlights"] = '\n'.join(final_summary["highlights"])
            if isinstance(final_summary.get("concerns"), list):
                final_summary["concerns"] = '\n'.join(final_summary["concerns"])
            if isinstance(final_summary.get("candidate_questions"), list):
                final_summary["candidate_questions"] = '\n'.join(final_summary["candidate_questions"])

        return final_summary

    except Exception as e:
        logger.error(f"AI生成摘要失败: {str(e)}")
        raise


def _extract_json_from_response(response: str) -> Optional[Dict[str, Any]]:
    """
    从AI响应中提取JSON数据
    :param response: AI响应文本
    :return: 解析后的JSON数据
    """
    try:
        # 尝试直接解析
        return json.loads(response)
    except json.JSONDecodeError:
        # 如果直接解析失败，尝试提取JSON部分
        try:
            # 查找第一个{和最后一个}之间的内容
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                logger.error("响应中未找到有效的JSON结构")
                return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {str(e)}")
            return None


def _consolidate_summaries(summaries: list) -> Dict[str, Any]:
    """
    汇总多个块的摘要信息
    :param summaries: 各块的摘要列表
    :return: 汇总后的摘要
    """
    consolidated = {
        "summary_overview": "",
        "key_qa": [],
        "technical_skills": set(),
        "soft_skills": set(),
        "highlights": [],
        "concerns": [],
        "candidate_questions": []
    }

    for summary in summaries:
        # 合并概览（取最长的一个）
        if len(summary.get("summary_overview", "")) > len(consolidated["summary_overview"]):
            consolidated["summary_overview"] = summary["summary_overview"]

        # 合并关键问答
        consolidated["key_qa"].extend(summary.get("key_qa", []))

        # 合并技能标签（去重）
        consolidated["technical_skills"].update(summary.get("technical_skills", []))
        consolidated["soft_skills"].update(summary.get("soft_skills", []))

        # 合并亮点和疑虑
        consolidated["highlights"].extend(summary.get("highlights", []))
        consolidated["concerns"].extend(summary.get("concerns", []))

        # 合并候选人问题
        consolidated["candidate_questions"].extend(summary.get("candidate_questions", []))

    # 限制数量，避免过多
    consolidated["key_qa"] = consolidated["key_qa"][:5]  # 最多5个问答
    consolidated["highlights"] = consolidated["highlights"][:4]  # 最多4个亮点
    consolidated["concerns"] = consolidated["concerns"][:3]  # 最多3个疑虑
    consolidated["candidate_questions"] = consolidated["candidate_questions"][:5]  # 最多5个问题

    # 将集合转换回列表
    consolidated["technical_skills"] = list(consolidated["technical_skills"])
    consolidated["soft_skills"] = list(consolidated["soft_skills"])
    
    # 将列表转换为字符串（因为数据库字段是 TEXT 类型）
    consolidated["highlights"] = '\n'.join(consolidated["highlights"]) if consolidated["highlights"] else None
    consolidated["concerns"] = '\n'.join(consolidated["concerns"]) if consolidated["concerns"] else None
    consolidated["candidate_questions"] = '\n'.join(consolidated["candidate_questions"]) if consolidated["candidate_questions"] else None

    return consolidated


def _format_summary_response(summary) -> Dict[str, Any]:
    """
    格式化摘要响应
    :param summary: InterviewSummary对象
    :return: 格式化的响应数据
    """
    return {
        "id": summary.id,
        "recording_id": summary.recording_id,
        "resume_id": summary.resume_id,
        "summary_overview": summary.summary_overview,
        "key_qa": summary.key_qa or [],
        "technical_skills": summary.technical_skills or [],
        "soft_skills": summary.soft_skills or [],
        "highlights": summary.highlights or "",
        "concerns": summary.concerns or "",
        "candidate_questions": summary.candidate_questions or "",
        "created_at": summary.created_at,
        "updated_at": summary.updated_at
    }