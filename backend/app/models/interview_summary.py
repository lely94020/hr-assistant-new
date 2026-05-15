from sqlalchemy import Column, BigInteger, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class InterviewSummary(Base):
    """面试摘要表"""
    __tablename__ = "interview_summary"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    recording_id = Column(BigInteger, nullable=False, unique=True, comment="关联录音ID")
    resume_id = Column(BigInteger, nullable=False, comment="关联简历ID")
    summary_overview = Column(Text, nullable=False, comment="面试概要")
    key_qa = Column(JSON, nullable=True, comment="核心问答")
    technical_skills = Column(JSON, nullable=True, comment="技术能力标签")
    soft_skills = Column(JSON, nullable=True, comment="软技能标签")
    highlights = Column(Text, nullable=True, comment="亮点")
    concerns = Column(Text, nullable=True, comment="疑虑点")
    candidate_questions = Column(Text, nullable=True, comment="候选人提问")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")