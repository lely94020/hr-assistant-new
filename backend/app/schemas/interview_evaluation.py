from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


class DimensionScoreResponse(BaseModel):
    """维度评分响应"""
    score: int = Field(..., ge=0, le=100, description="评分")
    comment: Optional[str] = Field(None, max_length=200, description="评语")


class GenerateEvaluationRequest(BaseModel):
    """生成评价请求"""
    summary_id: int = Field(..., description="面试摘要ID")


class EvaluationScoresResponse(BaseModel):
    """评价分数响应"""
    professional: DimensionScoreResponse
    logic: DimensionScoreResponse
    communication: DimensionScoreResponse
    learning: DimensionScoreResponse
    teamwork: DimensionScoreResponse
    culture_fit: DimensionScoreResponse


class InterviewEvaluationResponse(BaseModel):
    """面试评价响应"""
    id: int
    resume_id: int
    recording_id: Optional[int] = None
    summary_id: Optional[int] = None
    scores: EvaluationScoresResponse
    total_score: float
    recommendation: str
    ai_comment: Optional[str] = None
    key_strengths: Optional[List[str]] = None
    improvement_areas: Optional[List[str]] = None
    hiring_suggestion: Optional[str] = None
    hr_comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HRCommentRequest(BaseModel):
    """HR补充评价请求"""
    hr_comment: str = Field(..., description="HR补充评价")


class UpdateHRCommentRequest(BaseModel):
    """更新HR评价请求"""
    hr_comment: Optional[str] = None