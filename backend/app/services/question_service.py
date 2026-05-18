# app/services/question_service.py
import os
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from langchain_community.chat_models import ChatTongyi
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.models.position import JobPosition
from app.models.resume import Resume
from app.models.question import InterviewQuestion
from app.crud import question as question_crud


class QuestionService:
    """智能面试题生成服务"""

    # 题目类型映射：英文 -> 中文
    QUESTION_TYPE_MAP = {
        "technical": "技术类",
        "behavioral": "行为类",
        "situational": "情景类",
        "open": "开放类"
    }

    # 反向映射：中文 -> 英文
    QUESTION_TYPE_REVERSE_MAP = {
        "技术类": "technical",
        "行为类": "behavioral",
        "情景类": "situational",
        "开放类": "open"
    }

    # 难度等级映射：英文 -> 中文
    DIFFICULTY_MAP = {
        "junior": "初级",
        "middle": "中级",
        "senior": "高级"
    }

    # 反向映射：中文 -> 英文
    DIFFICULTY_REVERSE_MAP = {
        "初级": "junior",
        "中级": "middle",
        "高级": "senior"
    }

    @staticmethod
    async def generate_questions(
        db: Session,
        mode: str,
        position_id: Optional[int] = None,
        resume_id: Optional[int] = None,
        question_types: List[str] = ["technical"],
        difficulty: str = "middle",
        count: int = 5,
        with_answer: bool = True
    ) -> List[Dict[str, Any]]:
        """
        生成面试题
        :param db: 数据库会话
        :param mode: 生成模式 position/resume/mixed
        :param position_id: 岗位ID
        :param resume_id: 简历ID
        :param question_types: 题目类型列表
        :param difficulty: 难度等级
        :param count: 题目数量
        :param with_answer: 是否生成参考答案
        :return: 生成的题目列表
        """
        # 验证模式
        if mode not in ["position", "resume", "mixed"]:
            raise ValueError("无效的生成模式，必须是 position/resume/mixed")

        # 获取岗位信息
        position = None
        if mode in ["position", "mixed"] and position_id:
            position = db.query(JobPosition).filter(
                JobPosition.id == position_id,
                JobPosition.is_deleted == 0
            ).first()
            if not position:
                raise ValueError("岗位不存在")

        # 获取简历信息
        resume = None
        if mode in ["resume", "mixed"] and resume_id:
            resume = db.query(Resume).filter(
                Resume.id == resume_id,
                Resume.is_deleted == 0
            ).first()
            if not resume:
                raise ValueError("简历不存在")

        # 验证参数
        if mode == "position" and not position:
            raise ValueError("基于岗位生成需要提供有效的岗位ID")
        if mode == "resume" and not resume:
            raise ValueError("基于简历生成需要提供有效的简历ID")
        if mode == "mixed" and not (position and resume):
            raise ValueError("混合生成需要同时提供有效的岗位ID和简历ID")

        # 调用AI生成题目
        questions = await QuestionService._call_ai_generate(
            position=position,
            resume=resume,
            mode=mode,
            question_types=question_types,
            difficulty=difficulty,
            count=count,
            with_answer=with_answer
        )

        # 保存到数据库（临时保存，is_saved=0）
        questions_data = []
        for q in questions:
            # 将中文类型转换为英文存储
            question_type_cn = q.get("type", "技术类")
            question_type_en = QuestionService.QUESTION_TYPE_REVERSE_MAP.get(question_type_cn, question_type_cn)

            # 将中文难度转换为英文存储
            difficulty_cn = q.get("difficulty", "中级")
            difficulty_en = QuestionService.DIFFICULTY_REVERSE_MAP.get(difficulty_cn, difficulty_cn)

            question_data = {
                "position_id": position_id if position else None,
                "resume_id": resume_id if resume else None,
                "question_type": question_type_en,
                "difficulty": difficulty_en,
                "question_content": q.get("question", ""),
                "reference_answer": q.get("reference_answer"),
                "scoring_points": q.get("scoring_points"),
                "source": q.get("source", ""),
                "is_saved": 0
            }
            questions_data.append(question_data)

        # 创建题目记录
        db_questions = question_crud.create_questions(db, questions_data)

        # 转换为响应格式
        result = []
        for db_q in db_questions:
            result.append({
                "id": db_q.id,
                "type": db_q.question_type,
                "type_name": QuestionService.QUESTION_TYPE_MAP.get(db_q.question_type, db_q.question_type),
                "difficulty": db_q.difficulty,
                "difficulty_name": QuestionService.DIFFICULTY_MAP.get(db_q.difficulty, db_q.difficulty),
                "question": db_q.question_content,
                "reference_answer": db_q.reference_answer,
                "scoring_points": db_q.scoring_points or [],
                "source": db_q.source or ""
            })

        return result

    @staticmethod
    async def _call_ai_generate(
        position: Optional[JobPosition],
        resume: Optional[Resume],
        mode: str,
        question_types: List[str],
        difficulty: str,
        count: int,
        with_answer: bool
    ) -> List[Dict[str, Any]]:
        """调用AI生成面试题"""
        try:
            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                raise Exception("未配置 DASHSCOPE_API_KEY 环境变量")

            llm = ChatTongyi(
                model="qwen-plus",
                temperature=0.7,
                dashscope_api_key=api_key
            )

            # 构建prompt
            prompt_template = QuestionService._build_prompt(mode)
            prompt = ChatPromptTemplate.from_template(prompt_template)
            chain = prompt | llm | JsonOutputParser()

            # 准备输入数据
            input_data = {
                "position_name": position.position_name if position else "",
                "job_description": position.job_description[:500] if position else "",
                "requirements": position.requirements[:500] if position else "",
                "candidate_name": resume.candidate_name if resume else "",
                "education": resume.education if resume else "",
                "school": resume.school if resume else "",
                "major": resume.major if resume else "",
                "work_years": resume.work_years if resume else 0,
                "current_position": resume.current_position if resume else "",
                "current_company": resume.current_company if resume else "",
                "skills": ", ".join(resume.skills) if resume and resume.skills else "",
                "work_experience_summary": QuestionService._format_work_experience(resume) if resume else "",
                "project_experience_summary": QuestionService._format_project_experience(resume) if resume else "",
                "question_types": "/".join([QuestionService.QUESTION_TYPE_MAP.get(t, t) for t in question_types]),
                "difficulty": QuestionService.DIFFICULTY_MAP.get(difficulty, difficulty),
                "count": count,
                "with_answer": "是" if with_answer else "否"
            }

            # 调用AI（使用异步方法）
            response = await chain.ainvoke(input_data)

            # 解析返回结果
            if isinstance(response, dict) and "questions" in response:
                questions = response["questions"]
            elif isinstance(response, list):
                questions = response
            else:
                raise Exception("AI返回格式不正确")

            # 验证和清理数据
            validated_questions = []
            for q in questions[:count]:
                validated_q = {
                    "type": q.get("type", "技术类"),
                    "difficulty": q.get("difficulty", QuestionService.DIFFICULTY_MAP.get(difficulty, difficulty)),
                    "question": q.get("question", ""),
                    "reference_answer": q.get("reference_answer") if with_answer else None,
                    "scoring_points": q.get("scoring_points", []),
                    "source": q.get("source", "")
                }
                validated_questions.append(validated_q)

            return validated_questions

        except Exception as e:
            error_msg = f"AI生成面试题失败: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            raise Exception(error_msg)

    @staticmethod
    def _build_prompt(mode: str) -> str:
        """根据模式构建prompt"""
        base_prompt = """你是一位资深的技术面试官，请根据以下信息生成面试题目。

【目标岗位】
岗位名称：{position_name}
岗位职责：
{job_description}

任职要求：
{requirements}

【候选人信息】
姓名：{candidate_name}
学历：{education} - {school} - {major}
工作年限：{work_years}年
当前职位：{current_position} @ {current_company}
技能标签：{skills}
工作经历摘要：{work_experience_summary}
项目经验摘要：{project_experience_summary}

【生成要求】
- 题目类型：{question_types}（可多选：技术类/行为类/情景类/开放类）
- 难度等级：{difficulty}（初级/中级/高级）
- 题目数量：{count}题
- 是否生成参考答案：{with_answer}

请按以下JSON格式返回：
{{
    "questions": [
        {{
            "type": "技术类",
            "difficulty": "中级",
            "question": "题目内容",
            "reference_answer": "参考答案（如需要）",
            "scoring_points": ["评分要点1", "评分要点2"],
            "source": "基于岗位要求/基于候选人经历"
        }}
    ]
}}

要求：
1. 技术类题目要结合岗位技术栈和候选人技能
2. 行为类题目要基于候选人的工作经历设计
3. 题目要有区分度，能考察真实能力
4. 参考答案要给出关键点，不要过于冗长"""

        return base_prompt

    @staticmethod
    def _format_work_experience(resume: Resume) -> str:
        """格式化工作经历"""
        if not resume.work_experience:
            return "无"

        summaries = []
        for exp in resume.work_experience[:3]:  # 只取前3段经历
            company = exp.get("company", "")
            position = exp.get("position", "")
            duration = exp.get("duration", "")
            desc = exp.get("description", "")[:100]
            summaries.append(f"{company} {position} ({duration}): {desc}")

        return "; ".join(summaries)

    @staticmethod
    def _format_project_experience(resume: Resume) -> str:
        """格式化项目经验"""
        if not resume.project_experience:
            return "无"

        summaries = []
        for proj in resume.project_experience[:3]:  # 只取前3个项目
            name = proj.get("name", "")
            role = proj.get("role", "")
            desc = proj.get("description", "")[:100]
            summaries.append(f"{name} ({role}): {desc}")

        return "; ".join(summaries)

    @staticmethod
    def update_question(db: Session, question_id: int, updates: dict) -> Dict[str, Any]:
        """更新面试题"""
        db_question = question_crud.update_question(db, question_id, updates)
        if not db_question:
            raise ValueError("题目不存在")

        return {
            "id": db_question.id,
            "type": db_question.question_type,
            "type_name": QuestionService.QUESTION_TYPE_MAP.get(db_question.question_type, db_question.question_type),
            "difficulty": db_question.difficulty,
            "difficulty_name": QuestionService.DIFFICULTY_MAP.get(db_question.difficulty, db_question.difficulty),
            "question": db_question.question_content,
            "reference_answer": db_question.reference_answer,
            "scoring_points": db_question.scoring_points or [],
            "source": db_question.source or ""
        }

    @staticmethod
    def delete_question(db: Session, question_id: int) -> bool:
        """删除面试题"""
        return question_crud.delete_question(db, question_id)

    @staticmethod
    def save_to_question_bank(db: Session, question_ids: List[int]) -> Dict[str, Any]:
        """保存题目到题库"""
        updated_count = question_crud.save_questions_to_bank(db, question_ids)
        return {
            "saved_count": updated_count,
            "message": f"成功保存{updated_count}道题目到题库"
        }

    @staticmethod
    def get_questions(
        db: Session,
        position_id: Optional[int] = None,
        resume_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取面试题列表"""
        skip = (page - 1) * page_size

        questions = question_crud.get_questions_by_position_and_resume(
            db, position_id, resume_id, skip, page_size
        )

        items = []
        for q in questions:
            items.append({
                "id": q.id,
                "type": q.question_type,
                "type_name": QuestionService.QUESTION_TYPE_MAP.get(q.question_type, q.question_type),
                "difficulty": q.difficulty,
                "difficulty_name": QuestionService.DIFFICULTY_MAP.get(q.difficulty, q.difficulty),
                "question": q.question_content,
                "reference_answer": q.reference_answer,
                "scoring_points": q.scoring_points or [],
                "source": q.source or ""
            })

        # 获取总数
        from sqlalchemy import func
        query = db.query(func.count(InterviewQuestion.id))
        if position_id:
            query = query.filter(InterviewQuestion.position_id == position_id)
        if resume_id:
            query = query.filter(InterviewQuestion.resume_id == resume_id)

        total = query.scalar()

        return {
            "total": total,
            "items": items,
            "page": page,
            "page_size": page_size
        }
