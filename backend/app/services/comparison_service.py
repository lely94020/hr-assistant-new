from sqlalchemy.orm import Session
from app.crud.comparison import create_comparison, update_comparison_analysis
from app.crud.resume import get_resume
from app.crud.interview_evaluation import get_latest_evaluation_by_resume_id
from app.crud.position import get_position_by_id
from app.core.config import settings
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

        # 检查 API Key 配置
        api_key = settings.DASHSCOPE_API_KEY
        if not api_key:
            raise ValueError("未配置 DASHSCOPE_API_KEY，请在 .env 文件中配置")

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
                dashscope_api_key=api_key,
                request_timeout=120  # 设置120秒超时
            )

            # 构建完整的 chain
            chain = prompt | llm | JsonOutputParser()
            
            # 准备输入变量
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

            # 使用异步调用，传入正确的变量
            analysis_result = await chain.ainvoke({
                "position_name": position_data.get('name', '未知'),
                "requirements": position_data.get('requirements', '无'),
                "candidates_text": candidates_text
            })

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

        prompt_template = """你是一位资深的招聘顾问，请对以下候选人进行对比分析。

【目标岗位】
岗位名称：{position_name}
核心要求：{requirements}

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

        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        # 返回带有输入变量的完整 chain
        return prompt

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

        import logging
        logger = logging.getLogger(__name__)

        # ==================== 验证候选人分析数量 ====================
        if len(result["candidate_analysis"]) != len(candidates):
            logger.warning(
                f"候选人分析数量不匹配: 期望{len(candidates)}个，实际{len(result['candidate_analysis'])}个"
            )
            
            actual_count = len(result["candidate_analysis"])
            expected_count = len(candidates)
            
            # 构建已分析的候选人名称集合
            analyzed_names = {item.get("name") for item in result["candidate_analysis"]}
            all_candidate_names = {c["name"] for c in candidates}
            
            # 找出缺失的候选人
            missing_names = all_candidate_names - analyzed_names
            
            if actual_count > expected_count:
                # 多余的删除（保留前 N 个）
                result["candidate_analysis"] = result["candidate_analysis"][:expected_count]
            elif missing_names:
                # 为缺失的候选人补充默认分析
                for candidate in candidates:
                    if candidate["name"] in missing_names:
                        result["candidate_analysis"].append({
                            "name": candidate["name"],
                            "advantages_over_others": ["信息不足，无法评估"],
                            "disadvantages": ["数据不完整"],
                            "suitable_scenarios": "需要更多信息才能评估",
                            "risk_points": "缺少面试评价或简历信息不完整"
                        })
                        
                        if len(result["candidate_analysis"]) >= expected_count:
                            break

        # ==================== 验证排名数量 ====================
        if len(result["ranking"]) != len(candidates):
            logger.warning(
                f"排名数量不匹配: 期望{len(candidates)}个，实际{len(result['ranking'])}个"
            )
            
            actual_count = len(result["ranking"])
            expected_count = len(candidates)
            
            # 构建已排名的候选人名称集合
            ranked_names = {item.get("name") for item in result["ranking"]}
            all_candidate_names = {c["name"] for c in candidates}
            
            # 找出未排名的候选人
            unranked_names = all_candidate_names - ranked_names
            
            if actual_count > expected_count:
                # 多余的删除
                result["ranking"] = result["ranking"][:expected_count]
            elif unranked_names:
                # 为未排名的候选人补充默认排名
                rank_num = actual_count + 1
                
                for candidate in candidates:
                    if candidate["name"] in unranked_names:
                        result["ranking"].append({
                            "rank": rank_num,
                            "name": candidate["name"],
                            "score": 0,
                            "reason": "未获得AI排名，可能需要进一步评估"
                        })
                        rank_num += 1
                        
                        if len(result["ranking"]) >= expected_count:
                            break

        # ==================== 验证排名序号 ====================
        ranks = [item["rank"] for item in result["ranking"]]
        expected_ranks = list(range(1, len(candidates) + 1))
        
        # 如果排名序号不正确，重新分配
        if sorted(ranks) != expected_ranks:
            logger.warning(f"排名序号不正确: {ranks}，按分数重新分配")
            
            # 按分数降序排列，重新分配排名
            result["ranking"].sort(key=lambda x: x.get("score", 0), reverse=True)
            for idx, item in enumerate(result["ranking"]):
                item["rank"] = idx + 1
