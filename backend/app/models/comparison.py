from sqlalchemy import Column, BigInteger, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class CandidateComparison(Base):
    """候选人对比表"""
    __tablename__ = "candidate_comparison"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    position_id = Column(BigInteger, nullable=False, comment="岗位ID")
    resume_ids = Column(JSON, nullable=False, comment="简历ID列表")
    comparison_data = Column(JSON, nullable=True, comment="对比数据快照")
    ai_analysis = Column(JSON, nullable=True, comment="AI分析结果")
    ranking = Column(JSON, nullable=True, comment="推荐排名")
    created_by = Column(BigInteger, nullable=True, comment="创建人")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")