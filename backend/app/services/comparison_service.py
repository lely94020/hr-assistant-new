from sqlalchemy.orm import Session
from app.crud.comparison import create_comparison, update_comparison_analysis
from app.crud.resume import get_resume
from app.crud.interview_evaluation import get_latest_evaluation_by_resume_id
from app.crud.position import get_position_by_id
from typing import List, Dict, Any
import os
import json

# LangChain相关
from langchain_community.chat_models import ChatTongyi
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser


class ComparisonService:
    """候选人对比服务"""

    @staticmethod
    def gather_candidate_data(db: Session, resume_ids: List[int]) -> List[Dict[str, Any]]:
        """收集候选人数据"""
        candidates = []

        for resume_id in resume_ids:
            resume = get_resume(db, resume_id)
            if not resume:
                continue

            # 获取面试评价
            evaluation = get_latest_evaluation_by_resume_id(db, resume_id)

            candidate_data = {
                "resume_id": resume.id,
                "name": resume.candidate_name,
                "education": resume.education,
                "school": resume.school,
                "major": resume.major,
                "work_years": resume.work_years,
                "current_company": resume.current_company,
                "current_position": resume.current_position,
                "skills": resume.skills or [],
                "evaluation": None
            }

            if evaluation:
                candidate_data["evaluation"] = {
                    "professional_score": evaluation.professional_score,
                    "logic_score": evaluation.logic_score,
                    "communication_score": evaluation.communication_score,
                    "learning_score": evaluation.learning_score,
                    "teamwork_score": evaluation.teamwork_score,
                    "culture_score": evaluation.culture_score,
                    "total_score": float(evaluation.total_score)
                }

            candidates.append(candidate_data)

        return candidates

    @staticmethod
    def build_comparison_data(
        db: Session,
        position_id: int,
        resume_ids: List[int]
    ) -> Dict[str, Any]:
        """构建对比数据"""
        position = get_position_by_id(db, position_id)
        if not position:
            raise ValueError(f"岗位不存在: position_id={position_id}")

        candidates = ComparisonService.gather_candidate_data(db, resume_ids)

        if len(candidates) < 2:
            raise ValueError("至少需要2个候选人进行对比")

        if len(candidates) > 5:
            raise ValueError("最多支持5个候选人对比")

        return {
            "position": {
                "id": position.id,
                "name": position.position_name,
                "requirements": position.requirements
            },
            "candidates": candidates
        }

    @staticmethod
    async def generate_ai_analysis(
        db: Session,
        comparison_id: int
    ) -> Dict[str, Any]:
        """生成AI对比分析"""
        comparison = ComparisonService._get_comparison_with_data(db, comparison_id)

        if not comparison:
            raise ValueError(f"对比记录不存在: comparison_id={comparison_id}")

        if not comparison.comparison_data:
            raise ValueError("对比数据不存在，请先创建对比")

        position_data = comparison.comparison_data.get("position", {})
        candidates = comparison.comparison_data.get("candidates", [])

        if len(candidates) < 2:
            raise ValueError("候选人数量不足")

        # 构建Prompt
        prompt = ComparisonService._build_comparison_prompt(
            position_data,
            candidates
        )

        try:
            # 调用AI生成分析
            llm = ChatTongyi(
                model="qwen-plus",
                temperature=0.2,
                dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
            )

            chain = prompt | llm | JsonOutputParser()
            analysis_result = chain.invoke({})

            # 验证返回结果
            ComparisonService._validate_analysis_result(analysis_result, candidates)

            # 保存到数据库
            update_comparison_analysis(
                db,
                comparison_id,
                ai_analysis=analysis_result,
                ranking=analysis_result.get("ranking", [])
            )

            return analysis_result

        except Exception as e:
            raise Exception(f"AI分析失败: {str(e)}")

    @staticmethod
    def _get_comparison_with_data(db: Session, comparison_id: int):
        """获取对比记录（带数据）"""
        from app.crud.comparison import get_comparison_by_id
        return get_comparison_by_id(db, comparison_id)

    @staticmethod
    def _build_comparison_prompt(
        position_data: Dict[str, Any],
        candidates: List[Dict[str, Any]]
    ) -> ChatPromptTemplate:
        """构建对比分析Prompt"""

        # 构建候选人信息文本
        candidates_text = ""
        for idx, candidate in enumerate(candidates):
            label = chr(65 + idx)  # A, B, C, D, E
            eval_data = candidate.get("evaluation") or {}

            candidates_text += f"""
候选人{label} - {candidate['name']}：
- 学历：{candidate.get('education') or '未知'} - {candidate.get('school') or '未知'}
- 专业：{candidate.get('major') or '未知'}
- 工作年限：{candidate.get('work_years') or 0}年
- 当前职位：{candidate.get('current_position') or '未知'} @ {candidate.get('current_company') or '未知'}
- 技能：{', '.join(candidate.get('skills') or [])}
- 面试评分：专业{eval_data.get('professional_score') or 0}分、逻辑{eval_data.get('logic_score') or 0}分、沟通{eval_data.get('communication_score') or 0}分、学习{eval_data.get('learning_score') or 0}分、团队{eval_data.get('teamwork_score') or 0}分、文化{eval_data.get('culture_score') or 0}分
- 综合得分：{eval_data.get('total_score') or 0}分
"""

        prompt_template = f"""你是一位资深的招聘顾问，请对以下候选人进行对比分析。

【目标岗位】
岗位名称：{position_data.get('name', '未知')}
核心要求：{position_data.get('requirements', '无')}

【候选人信息】
{candidates_text}

请按以下JSON格式返回对比分析：
{{
    "comparison_summary": "对比总结（200字，概述各候选人的整体情况和差异）",
    
    "candidate_analysis": [
        {{
            "name": "候选人姓名",
            "advantages_over_others": ["相比其他候选人的优势1", "优势2"],
            "disadvantages": ["相比其他候选人的劣势1"],
            "suitable_scenarios": "最适合的场景（如急需上岗、长期培养等）",
            "risk_points": "录用风险点"
        }}
    ],
    
    "ranking": [
        {{
            "rank": 1,
            "name": "候选人姓名",
            "score": 综合推荐分,
            "reason": "排名第一的理由（50字）"
        }}
    ],
    
    "recommendation": {{
        "best_choice": "最佳人选姓名",
        "reason": "推荐理由（100字）",
        "alternative": "备选人选姓名",
        "alternative_reason": "备选理由"
    }},
    
    "hiring_advice": "最终录用建议（150字，包含决策建议和注意事项）"
}}

分析要求：
1. 客观公正，基于数据和面试表现
2. 突出每个候选人的差异化优势
3. 考虑岗位需求的匹配度
4. 给出明确的排名和推荐
5. 必须返回有效的JSON格式
6. 如果某些候选人缺少面试评分，请主要基于简历信息进行评估
"""

        return ChatPromptTemplate.from_template(prompt_template)

    @staticmethod
    def _validate_analysis_result(result: Dict[str, Any], candidates: List[Dict[str, Any]]):
        """验证AI分析结果"""
        required_fields = [
            "comparison_summary",
            "candidate_analysis",
            "ranking",
            "recommendation",
            "hiring_advice"
        ]

        for field in required_fields:
            if field not in result:
                raise ValueError(f"AI返回结果缺少必要字段: {field}")

        # 验证候选人分析数量
        if len(result["candidate_analysis"]) != len(candidates):
            raise ValueError("候选人分析数量与实际候选人数量不匹配")

        # 验证排名
        if len(result["ranking"]) != len(candidates):
            raise ValueError("排名数量与实际候选人数量不匹配")

        # 验证排名序号
        ranks = [item["rank"] for item in result["ranking"]]
        expected_ranks = list(range(1, len(candidates) + 1))
        if sorted(ranks) != expected_ranks:
            raise ValueError("排名序号不正确")