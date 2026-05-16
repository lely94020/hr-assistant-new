from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class CandidateBasicInfo(BaseModel):
    """候选人基本信息"""
    resume_id: int
    name: str
    education: Optional[str] = None
    school: Optional[str] = None
    major: Optional[str] = None
    work_years: Optional[int] = None
    current_company: Optional[str] = None
    current_position: Optional[str] = None
    skills: Optional[List[str]] = None


class EvaluationScores(BaseModel):
    """评价分数"""
    professional_score: int
    logic_score: int
    communication_score: int
    learning_score: int
    teamwork_score: int
    culture_score: int
    total_score: float


class CandidateDetail(CandidateBasicInfo):
    """候选人详细信息（包含评价）"""
    evaluation: Optional[EvaluationScores] = None


class CreateComparisonRequest(BaseModel):
    """创建对比请求"""
    position_id: int = Field(..., description="岗位ID")
    resume_ids: List[int] = Field(..., min_length=2, max_length=5, description="简历ID列表(2-5个)")


class ComparisonResponse(BaseModel):
    """对比响应"""
    id: int
    position: Dict[str, Any]
    candidates: List[CandidateDetail]
    created_at: datetime

    class Config:
        from_attributes = True


class CandidateAnalysis(BaseModel):
    """候选人分析"""
    name: str
    advantages_over_others: List[str]
    disadvantages: List[str]
    suitable_scenarios: str
    risk_points: str


class RankingItem(BaseModel):
    """排名项"""
    rank: int
    name: str
    score: float
    reason: str


class Recommendation(BaseModel):
    """推荐信息"""
    best_choice: str
    reason: str
    alternative: str
    alternative_reason: str


class AIAnalysisResult(BaseModel):
    """AI分析结果"""
    comparison_summary: str
    candidate_analysis: List[CandidateAnalysis]
    ranking: List[RankingItem]
    recommendation: Recommendation
    hiring_advice: str


class AnalyzeComparisonResponse(BaseModel):
    """AI分析响应"""
    id: int
    comparison_summary: str
    candidate_analysis: List[CandidateAnalysis]
    ranking: List[RankingItem]
    recommendation: Recommendation
    hiring_advice: str

    class Config:
        from_attributes = True


class ComparisonHistoryItem(BaseModel):
    """对比历史项"""
    id: int
    position_id: int
    position_name: str
    resume_count: int
    candidate_names: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ComparisonHistoryResponse(BaseModel):
    """对比历史响应"""
    total: int
    items: List[ComparisonHistoryItem]