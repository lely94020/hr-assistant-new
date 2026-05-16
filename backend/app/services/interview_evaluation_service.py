import json
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from langchain_community.llms.tongyi import Tongyi
from langchain.prompts import PromptTemplate
import dashscope

from app.crud.interview_evaluation import create_interview_evaluation
from app.crud.interview_summary import get_summary_by_id
from app.crud.recording import get_recording_by_id
from app.crud.resume import get_resume
from app.core.config import settings

logger = logging.getLogger(__name__)


EVALUATION_WEIGHTS = {
    "professional": 0.30,
    "logic": 0.20,
    "communication": 0.15,
    "learning": 0.15,
    "teamwork": 0.10,
    "culture_fit": 0.10
}


def generate_interview_evaluation(summary_id: int, db: Session) -> Dict[str, Any]:
    """
    基于面试摘要生成AI评价
    :param summary_id: 面试摘要ID
    :param db: 数据库会话
    :return: 生成的评价数据
    """
    try:
        summary = get_summary_by_id(db, summary_id)
        if not summary:
            raise ValueError(f"面试摘要不存在: {summary_id}")

        resume = get_resume(db, summary.resume_id)
        if not resume:
            raise ValueError(f"简历不存在: {summary.resume_id}")

        recording = get_recording_by_id(db, summary.recording_id) if summary.recording_id else None

        position_name = "未知岗位"
        requirements = ""

        evaluation_data = _generate_evaluation_with_ai(
            candidate_name=resume.candidate_name,
            position_name=position_name,
            requirements=requirements,
            summary_overview=summary.summary_overview,
            key_qa=summary.key_qa,
            technical_skills=summary.technical_skills,
            soft_skills=summary.soft_skills,
            highlights=summary.highlights,
            concerns=summary.concerns
        )

        new_evaluation = create_interview_evaluation(
            db=db,
            resume_id=summary.resume_id,
            recording_id=summary.recording_id,
            summary_id=summary_id,
            **evaluation_data
        )

        logger.info(f"面试评价已创建 ID={new_evaluation.id}")
        return _format_evaluation_response(new_evaluation)

    except Exception as e:
        logger.error(f"生成面试评价失败: {str(e)}")
        raise


def _generate_evaluation_with_ai(
    candidate_name: str,
    position_name: str,
    requirements: str,
    summary_overview: str,
    key_qa: Optional[list],
    technical_skills: Optional[list],
    soft_skills: Optional[list],
    highlights: Optional[str],
    concerns: Optional[str]
) -> Dict[str, Any]:
    """
    使用AI生成面试评价
    """
    try:
        api_key = settings.DASHSCOPE_API_KEY
        if not api_key:
            raise ValueError("未配置 DASHSCOPE_API_KEY")

        dashscope.api_key = api_key

        llm = Tongyi(
            model="qwen-turbo",
            dashscope_api_key=api_key,
            temperature=0.3
        )

        key_qa_text = ""
        if key_qa and isinstance(key_qa, list):
            for i, qa in enumerate(key_qa[:5], 1):
                if isinstance(qa, dict):
                    key_qa_text += f"{i}. 问：{qa.get('question', '')}\n   答：{qa.get('answer_summary', '')}\n\n"

        technical_skills_str = ", ".join(technical_skills) if technical_skills else "未提取"
        soft_skills_str = ", ".join(soft_skills) if soft_skills else "未提取"
        highlights_str = highlights if highlights else "无明显亮点"
        concerns_str = concerns if concerns else "无明显疑虑"

        prompt_template = """你是一位资深的HR评估专家，请根据以下面试摘要对候选人进行多维度评价。

【基本信息】
候选人：{candidate_name}
应聘岗位：{position_name}
岗位要求：{requirements}

【面试摘要】
面试概要：{summary_overview}

核心问答表现：
{key_qa_text}

能力标签：
- 技术能力：{technical_skills}
- 软技能：{soft_skills}

亮点：{highlights}
疑虑：{concerns}

请按以下JSON格式返回评价结果：
{{
    "scores": {{
        "professional": {{
            "score": 85,
            "comment": "对这个维度的具体评价（50字以内）"
        }},
        "logic": {{
            "score": 90,
            "comment": "..."
        }},
        "communication": {{
            "score": 80,
            "comment": "..."
        }},
        "learning": {{
            "score": 88,
            "comment": "..."
        }},
        "teamwork": {{
            "score": 82,
            "comment": "..."
        }},
        "culture_fit": {{
            "score": 78,
            "comment": "..."
        }}
    }},
    "total_score": 84.7,
    "recommendation": "推荐",
    "overall_comment": "综合评语（200-300字，包含优势、不足、发展建议）",
    "key_strengths": ["核心优势1", "核心优势2"],
    "improvement_areas": ["待提升领域1", "待提升领域2"],
    "hiring_suggestion": "录用建议和理由（100字）"
}}

评分标准：
- 90-100：表现优秀，明显超出期望
- 75-89：表现良好，符合期望
- 60-74：表现一般，勉强达到要求
- 0-59：表现较差，未达到要求

权重说明：
- 专业能力：30%
- 逻辑思维：20%
- 沟通表达：15%
- 学习能力：15%
- 团队协作：10%
- 文化匹配：10%

综合得分计算公式：Σ(各维度得分 × 权重)

请基于面试表现客观评分，不要过于宽松或苛刻。
"""

        prompt = PromptTemplate(
            input_variables=[
                "candidate_name", "position_name", "requirements",
                "summary_overview", "key_qa_text", "technical_skills",
                "soft_skills", "highlights", "concerns"
            ],
            template=prompt_template
        )

        full_prompt = prompt.format(
            candidate_name=candidate_name,
            position_name=position_name,
            requirements=requirements,
            summary_overview=summary_overview,
            key_qa_text=key_qa_text,
            technical_skills=technical_skills_str,
            soft_skills=soft_skills_str,
            highlights=highlights_str,
            concerns=concerns_str
        )

        result = llm.invoke(full_prompt)
        evaluation_json = _extract_json_from_response(result)

        if not evaluation_json:
            raise ValueError("AI返回的结果无法解析为有效的JSON格式")

        scores = evaluation_json.get("scores", {})

        professional_score = scores.get("professional", {}).get("score", 0)
        logic_score = scores.get("logic", {}).get("score", 0)
        communication_score = scores.get("communication", {}).get("score", 0)
        learning_score = scores.get("learning", {}).get("score", 0)
        teamwork_score = scores.get("teamwork", {}).get("score", 0)
        culture_score = scores.get("culture_fit", {}).get("score", 0)

        calculated_total = (
            professional_score * EVALUATION_WEIGHTS["professional"] +
            logic_score * EVALUATION_WEIGHTS["logic"] +
            communication_score * EVALUATION_WEIGHTS["communication"] +
            learning_score * EVALUATION_WEIGHTS["learning"] +
            teamwork_score * EVALUATION_WEIGHTS["teamwork"] +
            culture_score * EVALUATION_WEIGHTS["culture_fit"]
        )

        total_score = evaluation_json.get("total_score", round(calculated_total, 2))

        recommendation = evaluation_json.get("recommendation", "")
        if not recommendation:
            if total_score >= 90:
                recommendation = "强烈推荐"
            elif total_score >= 75:
                recommendation = "推荐"
            elif total_score >= 60:
                recommendation = "可考虑"
            else:
                recommendation = "不推荐"

        return {
            "professional_score": professional_score,
            "professional_comment": scores.get("professional", {}).get("comment"),
            "logic_score": logic_score,
            "logic_comment": scores.get("logic", {}).get("comment"),
            "communication_score": communication_score,
            "communication_comment": scores.get("communication", {}).get("comment"),
            "learning_score": learning_score,
            "learning_comment": scores.get("learning", {}).get("comment"),
            "teamwork_score": teamwork_score,
            "teamwork_comment": scores.get("teamwork", {}).get("comment"),
            "culture_score": culture_score,
            "culture_comment": scores.get("culture_fit", {}).get("comment"),
            "total_score": total_score,
            "recommendation": recommendation,
            "ai_comment": evaluation_json.get("overall_comment"),
            "key_strengths": evaluation_json.get("key_strengths", []),
            "improvement_areas": evaluation_json.get("improvement_areas", []),
            "hiring_suggestion": evaluation_json.get("hiring_suggestion"),
            "hr_comment": None
        }

    except Exception as e:
        logger.error(f"AI生成评价失败: {str(e)}")
        raise


def _extract_json_from_response(response: str) -> Optional[Dict[str, Any]]:
    """从AI响应中提取JSON数据"""
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        try:
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


def _format_evaluation_response(evaluation) -> Dict[str, Any]:
    """格式化评价响应"""
    return {
        "id": evaluation.id,
        "resume_id": evaluation.resume_id,
        "recording_id": evaluation.recording_id,
        "summary_id": evaluation.summary_id,
        "scores": {
            "professional": {
                "score": evaluation.professional_score,
                "comment": evaluation.professional_comment
            },
            "logic": {
                "score": evaluation.logic_score,
                "comment": evaluation.logic_comment
            },
            "communication": {
                "score": evaluation.communication_score,
                "comment": evaluation.communication_comment
            },
            "learning": {
                "score": evaluation.learning_score,
                "comment": evaluation.learning_comment
            },
            "teamwork": {
                "score": evaluation.teamwork_score,
                "comment": evaluation.teamwork_comment
            },
            "culture_fit": {
                "score": evaluation.culture_score,
                "comment": evaluation.culture_comment
            }
        },
        "total_score": float(evaluation.total_score),
        "recommendation": evaluation.recommendation,
        "ai_comment": evaluation.ai_comment,
        "key_strengths": evaluation.key_strengths or [],
        "improvement_areas": evaluation.improvement_areas or [],
        "hiring_suggestion": evaluation.hiring_suggestion,
        "hr_comment": evaluation.hr_comment,
        "created_at": evaluation.created_at,
        "updated_at": evaluation.updated_at
    }