from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import os
import json
import warnings

from app.models.resume import Resume
from app.models.position import JobPosition
from langchain_community.chat_models import ChatTongyi
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.embeddings import DashScopeEmbeddings

try:
    from pymilvus import connections, Collection, utility
    MILVUS_AVAILABLE = True
    print("✅ Milvus 客户端导入成功（筛选服务）")
except ImportError:
    MILVUS_AVAILABLE = False
    print("⚠️ pymilvus未安装，向量搜索功能将不可用")


class ScreeningService:
    """智能简历筛选服务"""
    
    MILVUS_HOST = "localhost"
    MILVUS_PORT = "19530"
    COLLECTION_NAME = "resumes"
    _milvus_initialized = False
    
    @staticmethod
    def _init_milvus():
        """初始化Milvus连接（单例模式，避免重复连接）"""
        if not MILVUS_AVAILABLE:
            print("警告: Milvus不可用，跳过向量搜索")
            return False
        
        # 如果已经初始化过，直接返回成功
        if ScreeningService._milvus_initialized:
            return True
        
        try:
            # 抑制弃用警告
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                connections.connect(
                    host=ScreeningService.MILVUS_HOST,
                    port=ScreeningService.MILVUS_PORT
                )
            ScreeningService._milvus_initialized = True
            print("✅ Milvus 连接成功（筛选服务）")
            return True
        except Exception as e:
            print(f"Milvus连接失败: {str(e)}")
            return False
    
    @staticmethod
    def _close_milvus():
        """关闭Milvus连接"""
        if not MILVUS_AVAILABLE:
            return
        
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                connections.disconnect("default")
            ScreeningService._milvus_initialized = False
            print("✅ Milvus 连接已关闭（筛选服务）")
        except Exception as e:
            print(f"关闭Milvus连接失败: {str(e)}")
    
    @staticmethod
    def _skill_matches(required_skill: str, resume_skill: str) -> bool:
        """
        精确匹配技能，避免子字符串误匹配
        例如："java" 不应该匹配 "javascript"
        """
        required_lower = required_skill.lower().strip()
        resume_lower = resume_skill.lower().strip()
        
        # 完全相等
        if required_lower == resume_lower:
            return True
        
        # 处理常见缩写和别名
        skill_aliases = {
            "js": ["javascript"],
            "javascript": ["js"],
            "py": ["python"],
            "python": ["py"],
            "c++": ["cpp", "c plus plus"],
            "cpp": ["c++", "c plus plus"],
            "c#": ["csharp", "c sharp"],
            "csharp": ["c#", "c sharp"],
            "node": ["nodejs", "node.js"],
            "nodejs": ["node", "node.js"],
            "react": ["reactjs", "react.js"],
            "vue": ["vuejs", "vue.js"],
            "angular": ["angularjs", "angular.js"],
        }
        
        # 检查是否是别名关系
        aliases = skill_aliases.get(required_lower, [])
        if resume_lower in aliases:
            return True
        
        # 检查单词边界匹配（用空格、逗号等分隔的完整单词）
        import re
        pattern = r'\b' + re.escape(required_lower) + r'\b'
        if re.search(pattern, resume_lower):
            return True
        
        return False
    
    @staticmethod
    def _calculate_match_score(similarity: float, resume: Resume, 
                               min_education: Optional[str] = None,
                               min_work_years: Optional[int] = None,
                               required_skills: Optional[List[str]] = None) -> float:
        """
        计算最终匹配分数
        公式：最终匹配分数 = 向量相似度分数 * 0.6 + 条件匹配分数 * 0.4
        """
        # 向量相似度分数 (0-100)
        vector_score = max(0, min(1, similarity)) * 100
        
        # 条件匹配分数
        condition_scores = []
        
        # 学历匹配
        if min_education and resume.education:
            education_levels = {
                "大专": 1,
                "本科": 2,
                "硕士": 3,
                "博士": 4
            }
            resume_level = education_levels.get(resume.education, 0)
            required_level = education_levels.get(min_education, 0)
            if resume_level >= required_level:
                condition_scores.append(100)
            else:
                condition_scores.append(0)
        
        # 工作年限匹配
        if min_work_years is not None and resume.work_years is not None:
            if resume.work_years >= min_work_years:
                condition_scores.append(100)
            else:
                # 部分匹配，按比例给分
                ratio = resume.work_years / min_work_years if min_work_years > 0 else 0
                condition_scores.append(ratio * 100)
        
        # 技能匹配（使用精确匹配）
        if required_skills and resume.skills:
            matched_skills = sum(1 for skill in required_skills 
                               if any(ScreeningService._skill_matches(skill, s) for s in resume.skills))
            skill_ratio = matched_skills / len(required_skills) if required_skills else 0
            condition_scores.append(skill_ratio * 100)
        
        # 计算条件匹配平均分
        condition_score = sum(condition_scores) / len(condition_scores) if condition_scores else 50
        
        # 最终分数
        final_score = vector_score * 0.6 + condition_score * 0.4
        
        return round(final_score, 2)
    
    @staticmethod
    def _get_recommendation_level(score: float) -> str:
        """根据分数获取推荐等级"""
        if score >= 85:
            return "强烈推荐"
        elif score >= 70:
            return "推荐"
        elif score >= 55:
            return "一般"
        else:
            return "不推荐"
    
    @staticmethod
    async def _generate_match_analysis(position: JobPosition, resume: Resume) -> Dict[str, Any]:
        """使用LangChain生成匹配分析报告"""
        try:
            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                raise Exception("未配置 DASHSCOPE_API_KEY 环境变量")
            
            llm = ChatTongyi(
                model="qwen-plus",
                temperature=0.1,
                dashscope_api_key=api_key
            )
            
            prompt_template = """请分析以下候选人与目标岗位的匹配程度：

【目标岗位】
岗位名称：{position_name}
岗位职责：{job_description}
任职要求：{requirements}

【候选人信息】
姓名：{candidate_name}
学历：{education} - {school}
工作年限：{work_years}年
当前职位：{current_position} @ {current_company}
技能：{skills}
简历摘要：{resume_summary}

请按以下格式返回分析结果（只返回JSON，不要有其他文字说明）：
{{
    "match_advantages": ["优势1", "优势2", "优势3"],
    "match_weaknesses": ["短板1", "短板2"],
    "overall_comment": "综合评语（100字左右）",
    "interview_suggestions": ["建议考察方向1", "建议考察方向2"]
}}"""
            
            prompt = ChatPromptTemplate.from_template(prompt_template)
            chain = prompt | llm | JsonOutputParser()
            
            # 准备数据，确保所有字段都有值
            analysis_data = {
                "position_name": position.position_name or "未知岗位",
                "job_description": (position.job_description or "")[:500],
                "requirements": (position.requirements or "")[:500],
                "candidate_name": resume.candidate_name or "未知",
                "education": resume.education or "未知",
                "school": resume.school or "未知",
                "work_years": resume.work_years or 0,
                "current_position": resume.current_position or "未知",
                "current_company": resume.current_company or "未知",
                "skills": ", ".join(resume.skills) if resume.skills else "无",
                "resume_summary": resume.resume_summary or ""
            }
            
            # 使用异步调用，避免阻塞事件循环
            analysis = await chain.ainvoke(analysis_data)
            
            # 验证返回结果格式
            if not isinstance(analysis, dict):
                raise Exception("AI返回格式不正确")
            
            # 确保必需的字段存在
            required_fields = ["match_advantages", "match_weaknesses", "overall_comment", "interview_suggestions"]
            for field in required_fields:
                if field not in analysis:
                    analysis[field] = [] if field != "overall_comment" else "分析完成"
            
            return analysis
            
        except Exception as e:
            error_msg = f"AI分析生成失败: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            
            # 返回默认分析
            return {
                "match_advantages": ["需要人工评估"],
                "match_weaknesses": ["AI分析暂时不可用"],
                "overall_comment": "系统暂时无法生成详细分析，请HR手动评估候选人与岗位的匹配度",
                "interview_suggestions": ["请重点考察候选人综合能力", "建议进行技术面试"]
            }
    
    @staticmethod
    async def screen_by_position(db: Session, position_id: int, top_n: int = 10,
                                 filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        根据岗位进行智能简历筛选
        """
        if not MILVUS_AVAILABLE:
            raise Exception("Milvus不可用，无法进行向量检索")
        
        # 1. 获取岗位信息
        position = db.query(JobPosition).filter(
            JobPosition.id == position_id,
            JobPosition.is_deleted == 0
        ).first()
        
        if not position:
            raise Exception("岗位不存在")
        
        # 2. 初始化Milvus
        if not ScreeningService._init_milvus():
            raise Exception("Milvus连接失败")
        
        # 3. 检查集合是否存在
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            if not utility.has_collection(ScreeningService.COLLECTION_NAME):
                raise Exception("简历向量集合不存在，请先上传简历")
            
            collection = Collection(ScreeningService.COLLECTION_NAME)
            collection.load()
        
        # 4. 将岗位JD向量化
        jd_text = f"{position.position_name}\n{position.job_description}\n{position.requirements}"
        
        try:
            embeddings = DashScopeEmbeddings(
                model="text-embedding-v1",
                dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
            )
            query_vector = embeddings.embed_query(jd_text)
        except Exception as e:
            raise Exception(f"岗位JD向量化失败: {str(e)}")
        
        # 5. 执行向量检索
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }
        
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                results = collection.search(
                    data=[query_vector],
                    anns_field="embedding",
                    param=search_params,
                    limit=top_n * 2,  # 多取一些，后续过滤
                    output_fields=["resume_id"]
                )
        except Exception as e:
            raise Exception(f"向量检索失败: {str(e)}")
        
        # 6. 处理检索结果
        matched_resumes = []
        
        # 收集所有 resume_id
        resume_ids = []
        for hits in results:
            for hit in hits:
                resume_id = hit.entity.get("resume_id")
                if resume_id:
                    resume_ids.append(resume_id)
        
        # 批量查询简历，避免 N+1 问题
        if resume_ids:
            resumes_dict = {r.id: r for r in db.query(Resume).filter(
                Resume.id.in_(resume_ids),
                Resume.is_deleted == 0
            ).all()}
            
            for hits in results:
                for hit in hits:
                    resume_id = hit.entity.get("resume_id")
                    similarity = hit.score
                    
                    # 从字典中获取简历详情
                    resume = resumes_dict.get(resume_id)
                    
                    if resume:
                        # 应用筛选条件
                        if filters:
                            min_education = filters.get("min_education")
                            min_work_years = filters.get("min_work_years")
                            required_skills = filters.get("required_skills", [])
                            
                            # 学历过滤
                            if min_education and resume.education:
                                education_levels = ["大专", "本科", "硕士", "博士"]
                                if resume.education not in education_levels or min_education not in education_levels:
                                    pass  # 如果学历不在预期列表中，跳过此过滤
                                elif education_levels.index(resume.education) < education_levels.index(min_education):
                                    continue
                            
                            # 工作年限过滤
                            if min_work_years is not None and resume.work_years is not None:
                                if resume.work_years < min_work_years:
                                    continue
                            
                            # 必备技能过滤（使用精确匹配）
                            if required_skills and resume.skills:
                                has_all_skills = all(
                                    any(ScreeningService._skill_matches(req_skill, s) for s in resume.skills)
                                    for req_skill in required_skills
                                )
                                if not has_all_skills:
                                    continue
                        
                        # 计算匹配分数
                        match_score = ScreeningService._calculate_match_score(
                            similarity, resume,
                            filters.get("min_education") if filters else None,
                            filters.get("min_work_years") if filters else None,
                            filters.get("required_skills") if filters else None
                        )
                        
                        # 获取推荐等级
                        recommendation = ScreeningService._get_recommendation_level(match_score)
                        
                        matched_resumes.append({
                            "resume": resume,
                            "similarity": similarity,
                            "match_score": match_score,
                            "recommendation": recommendation
                        })
        
        # 7. 按匹配分数排序
        matched_resumes.sort(key=lambda x: x["match_score"], reverse=True)
        
        # 8. 取前top_n个，生成详细分析
        print(f"📊 找到 {len(matched_resumes)} 份匹配简历，开始生成AI分析...")
        final_results = []
        for idx, item in enumerate(matched_resumes[:top_n], 1):
            resume = item["resume"]
            print(f"   [{idx}/{min(top_n, len(matched_resumes))}] 正在分析: {resume.candidate_name}")
            
            # 生成AI分析（异步）
            match_analysis = await ScreeningService._generate_match_analysis(position, resume)
            
            final_results.append({
                "resume_id": resume.id,
                "candidate_name": resume.candidate_name,
                "education": resume.education,
                "work_years": resume.work_years,
                "current_position": resume.current_position,
                "current_company": resume.current_company,
                "skills": resume.skills,
                "match_score": item["match_score"],
                "similarity": round(item["similarity"], 4),
                "recommendation": item["recommendation"],
                "match_analysis": match_analysis
            })
        
        print(f"✅ AI分析完成，返回 {len(final_results)} 个结果")
        
        return {
            "position": {
                "id": position.id,
                "name": position.position_name
            },
            "total_matched": len(final_results),
            "results": final_results
        }
    
    @staticmethod
    async def screen_by_custom_query(db: Session, query: str, top_n: int = 10) -> Dict[str, Any]:
        """
        根据自定义查询条件进行智能筛选
        """
        if not MILVUS_AVAILABLE:
            raise Exception("Milvus不可用，无法进行向量检索")
        
        # 1. 初始化Milvus
        if not ScreeningService._init_milvus():
            raise Exception("Milvus连接失败")
        
        # 2. 检查集合是否存在
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            if not utility.has_collection(ScreeningService.COLLECTION_NAME):
                raise Exception("简历向量集合不存在，请先上传简历")
            
            collection = Collection(ScreeningService.COLLECTION_NAME)
            collection.load()
        
        # 3. 将自定义查询向量化
        try:
            embeddings = DashScopeEmbeddings(
                model="text-embedding-v1",
                dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
            )
            query_vector = embeddings.embed_query(query)
        except Exception as e:
            raise Exception(f"查询文本向量化失败: {str(e)}")
        
        # 4. 执行向量检索
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }
        
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                results = collection.search(
                    data=[query_vector],
                    anns_field="embedding",
                    param=search_params,
                    limit=top_n,
                    output_fields=["resume_id"]
                )
        except Exception as e:
            raise Exception(f"向量检索失败: {str(e)}")
        
        # 5. 处理检索结果
        matched_resumes = []
        
        # 收集所有 resume_id
        resume_ids = []
        for hits in results:
            for hit in hits:
                resume_id = hit.entity.get("resume_id")
                if resume_id:
                    resume_ids.append(resume_id)
        
        # 批量查询简历，避免 N+1 问题
        if resume_ids:
            resumes_dict = {r.id: r for r in db.query(Resume).filter(
                Resume.id.in_(resume_ids),
                Resume.is_deleted == 0
            ).all()}
            
            for hits in results:
                for hit in hits:
                    resume_id = hit.entity.get("resume_id")
                    similarity = hit.score
                    
                    # 从字典中获取简历详情
                    resume = resumes_dict.get(resume_id)
                    
                    if resume:
                        # 对于自定义查询，简化评分计算
                        match_score = round(max(0, min(1, similarity)) * 100, 2)
                        recommendation = ScreeningService._get_recommendation_level(match_score)
                        
                        matched_resumes.append({
                            "resume": resume,
                            "similarity": similarity,
                            "match_score": match_score,
                            "recommendation": recommendation
                        })
        
        # 6. 按匹配分数排序
        matched_resumes.sort(key=lambda x: x["match_score"], reverse=True)
        
        # 7. 生成结果
        final_results = []
        for item in matched_resumes[:top_n]:
            resume = item["resume"]
            
            final_results.append({
                "resume_id": resume.id,
                "candidate_name": resume.candidate_name,
                "education": resume.education,
                "work_years": resume.work_years,
                "current_position": resume.current_position,
                "current_company": resume.current_company,
                "skills": resume.skills,
                "match_score": item["match_score"],
                "similarity": round(item["similarity"], 4),
                "recommendation": item["recommendation"],
                "match_analysis": None  # 自定义查询暂不生成详细分析
            })
        
        return {
            "query": query,
            "total_matched": len(final_results),
            "results": final_results
        }
    
    @staticmethod
    async def get_resume_analysis(db: Session, resume_id: int, position_id: int) -> Dict[str, Any]:
        """
        获取单个简历与岗位的匹配分析
        """
        # 获取简历
        resume = db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.is_deleted == 0
        ).first()
        
        if not resume:
            raise Exception("简历不存在")
        
        # 获取岗位
        position = db.query(JobPosition).filter(
            JobPosition.id == position_id,
            JobPosition.is_deleted == 0
        ).first()
        
        if not position:
            raise Exception("岗位不存在")
        
        # 生成AI分析
        match_analysis = await ScreeningService._generate_match_analysis(position, resume)
        
        return {
            "resume_id": resume.id,
            "candidate_name": resume.candidate_name,
            "position_id": position.id,
            "position_name": position.position_name,
            "analysis": match_analysis
        }
    
    @staticmethod
    def batch_mark_resumes(db: Session, resume_ids: List[int], mark_type: str) -> Dict[str, Any]:
        """
        批量标记简历筛选结果
        mark_type: pass(通过初筛) / reject(不通过) / pending(待定)
        """
        # 状态映射
        status_map = {
            "pass": 2,      # 初筛通过
            "reject": 5,    # 已淘汰
            "pending": 1    # 待筛选
        }
        
        if mark_type not in status_map:
            raise Exception("无效的标记类型，只能是 pass/reject/pending")
        
        # 防御：空列表检查
        if not resume_ids:
            raise Exception("简历ID列表不能为空")
        
        new_status = status_map[mark_type]
        
        # 批量更新状态
        count = db.query(Resume).filter(
            Resume.id.in_(resume_ids),
            Resume.is_deleted == 0
        ).update(
            {Resume.status: new_status},
            synchronize_session=False
        )
        db.commit()
        
        status_name_map = {
            2: "初筛通过",
            5: "已淘汰",
            1: "待筛选"
        }
        
        return {
            "message": f"成功标记{count}份简历为'{status_name_map[new_status]}'",
            "marked_count": count,
            "new_status": new_status,
            "status_name": status_name_map[new_status]
        }