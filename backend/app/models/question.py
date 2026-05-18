# app/models/question.py
from sqlalchemy import Column, BigInteger, String, Text, Integer, SmallInteger, DateTime, JSON
from sqlalchemy.sql import func
from app.db.database import Base


class InterviewQuestion(Base):
    """面试题表"""
    __tablename__ = "interview_question"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    position_id = Column(BigInteger, nullable=True, comment="关联岗位ID")
    resume_id = Column(BigInteger, nullable=True, comment="关联简历ID")
    question_type = Column(String(20), nullable=False, comment="题目类型：technical/behavioral/situational/open")
    difficulty = Column(String(10), nullable=False, comment="难度等级：junior/middle/senior")
    question_content = Column(Text, nullable=False, comment="题目内容")
    reference_answer = Column(Text, nullable=True, comment="参考答案")
    scoring_points = Column(JSON, nullable=True, comment="评分要点数组")
    source = Column(String(50), nullable=True, comment="题目来源说明")
    is_saved = Column(SmallInteger, default=0, comment="是否保存到题库")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
