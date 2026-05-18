from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, DECIMAL, JSON, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base


class InterviewEvaluation(Base):
    """面试评价表"""
    __tablename__ = "interview_evaluation"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    resume_id = Column(BigInteger, nullable=False, comment="关联简历ID")
    recording_id = Column(BigInteger, nullable=True, comment="关联录音ID")
    summary_id = Column(BigInteger, nullable=True, comment="关联摘要ID")

    professional_score = Column(Integer, nullable=False, comment="专业能力评分")
    professional_comment = Column(String(200), nullable=True, comment="专业能力评语")

    logic_score = Column(Integer, nullable=False, comment="逻辑思维评分")
    logic_comment = Column(String(200), nullable=True, comment="逻辑思维评语")

    communication_score = Column(Integer, nullable=False, comment="沟通表达评分")
    communication_comment = Column(String(200), nullable=True, comment="沟通表达评语")

    learning_score = Column(Integer, nullable=False, comment="学习能力评分")
    learning_comment = Column(String(200), nullable=True, comment="学习能力评语")

    teamwork_score = Column(Integer, nullable=False, comment="团队协作评分")
    teamwork_comment = Column(String(200), nullable=True, comment="团队协作评语")

    culture_score = Column(Integer, nullable=False, comment="文化匹配评分")
    culture_comment = Column(String(200), nullable=True, comment="文化匹配评语")

    total_score = Column(DECIMAL(5, 2), nullable=False, comment="综合加权得分")
    recommendation = Column(String(20), nullable=False, comment="推荐等级")

    ai_comment = Column(Text, nullable=True, comment="AI综合评语")
    key_strengths = Column(JSON, nullable=True, comment="核心优势")
    improvement_areas = Column(JSON, nullable=True, comment="待提升领域")
    hiring_suggestion = Column(Text, nullable=True, comment="录用建议")

    hr_comment = Column(Text, nullable=True, comment="HR补充评价")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")