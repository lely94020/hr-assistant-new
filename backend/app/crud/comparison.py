from sqlalchemy.orm import Session
from app.models.comparison import CandidateComparison
from typing import List, Optional
import json


def create_comparison(
    db: Session,
    position_id: int,
    resume_ids: List[int],
    comparison_data: dict = None,
    created_by: int = None
) -> CandidateComparison:
    """创建候选人对比记录"""
    db_comparison = CandidateComparison(
        position_id=position_id,
        resume_ids=resume_ids,
        comparison_data=comparison_data,
        created_by=created_by
    )
    db.add(db_comparison)
    db.commit()
    db.refresh(db_comparison)
    return db_comparison


def get_comparison_by_id(db: Session, comparison_id: int) -> Optional[CandidateComparison]:
    """根据ID获取对比记录"""
    return db.query(CandidateComparison).filter(
        CandidateComparison.id == comparison_id
    ).first()


def update_comparison_analysis(
    db: Session,
    comparison_id: int,
    ai_analysis: dict,
    ranking: list
) -> Optional[CandidateComparison]:
    """更新对比分析的AI结果"""
    db_comparison = db.query(CandidateComparison).filter(
        CandidateComparison.id == comparison_id
    ).first()

    if db_comparison:
        db_comparison.ai_analysis = ai_analysis
        db_comparison.ranking = ranking
        db.commit()
        db.refresh(db_comparison)

    return db_comparison


def get_comparisons_by_position(
    db: Session,
    position_id: int,
    skip: int = 0,
    limit: int = 20
) -> List[CandidateComparison]:
    """获取岗位的对比历史"""
    return db.query(CandidateComparison).filter(
        CandidateComparison.position_id == position_id
    ).order_by(
        CandidateComparison.created_at.desc()
    ).offset(skip).limit(limit).all()


def get_all_comparisons(
    db: Session,
    skip: int = 0,
    limit: int = 20
) -> tuple:
    """获取所有对比历史（分页）"""
    query = db.query(CandidateComparison)
    total = query.count()
    items = query.order_by(
        CandidateComparison.created_at.desc()
    ).offset(skip).limit(limit).all()

    return total, items