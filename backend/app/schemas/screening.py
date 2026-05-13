from pydantic import BaseModel, Field
from typing import Optional, List


# ========== 岗位匹配筛选请求 ==========
class PositionMatchRequest(BaseModel):
    position_id: int = Field(..., description="目标岗位ID")
    top_n: int = Field(default=10, ge=5, le=50, description="返回数量，默认10，范围5-50")
    filters: Optional[dict] = Field(None, description="筛选条件")

    class Config:
        json_schema_extra = {
            "example": {
                "position_id": 1,
                "top_n": 10,
                "filters": {
                    "min_education": "本科",
                    "min_work_years": 3,
                    "required_skills": ["Java", "Spring"]
                }
            }
        }


# ========== 自定义条件筛选请求 ==========
class CustomScreeningRequest(BaseModel):
    query: str = Field(..., description="自定义筛选描述")
    top_n: int = Field(default=10, ge=5, le=50, description="返回数量")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "需要有5年以上微服务开发经验的Java工程师，熟悉高并发系统设计",
                "top_n": 10
            }
        }


# ========== 匹配分析结果 ==========
class MatchAnalysis(BaseModel):
    match_advantages: List[str] = Field(..., description="匹配优势列表")
    match_weaknesses: List[str] = Field(..., description="匹配短板列表")
    overall_comment: str = Field(..., description="综合评语")
    interview_suggestions: List[str] = Field(..., description="面试建议")


# ========== 单个匹配结果 ==========
class ScreeningResult(BaseModel):
    resume_id: int
    candidate_name: str
    education: Optional[str] = None
    work_years: Optional[int] = None
    current_position: Optional[str] = None
    current_company: Optional[str] = None
    skills: Optional[List[str]] = None
    match_score: float = Field(..., description="匹配度分数（0-100）")
    similarity: float = Field(..., description="向量相似度（0-1）")
    recommendation: str = Field(..., description="推荐等级")
    match_analysis: Optional[MatchAnalysis] = None


# ========== 筛选响应 ==========
class ScreeningResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: dict


# ========== 批量标记请求 ==========
class BatchMarkRequest(BaseModel):
    resume_ids: List[int] = Field(..., description="简历ID列表")
    mark_type: str = Field(..., description="标记类型：pass/reject/pending")

    class Config:
        json_schema_extra = {
            "example": {
                "resume_ids": [1, 2, 3],
                "mark_type": "pass"
            }
        }


# ========== 获取匹配分析响应 ==========
class AnalysisResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: dict