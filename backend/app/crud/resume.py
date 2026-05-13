from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.resume import Resume
from app.schemas.resume import ResumeCreate, ResumeUpdate
from typing import List, Optional, Dict, Any
import os
import shutil
from pathlib import Path


def get_resume(db: Session, resume_id: int) -> Optional[Resume]:
    """获取单个简历"""
    return db.query(Resume).filter(Resume.id == resume_id, Resume.is_deleted == 0).first()


def get_resumes(
    db: Session,
    keyword: Optional[str] = None,
    position_id: Optional[int] = None,
    education: Optional[str] = None,
    work_years_min: Optional[int] = None,
    work_years_max: Optional[int] = None,
    status: Optional[int] = None,
    page: int = 1,
    page_size: int = 10
) -> Dict[str, Any]:
    """分页查询简历列表"""
    query = db.query(Resume).filter(Resume.is_deleted == 0)

    # 筛选条件
    if keyword:
        query = query.filter(Resume.candidate_name.like(f"%{keyword}%"))
    if position_id:
        query = query.filter(Resume.position_id == position_id)
    if education:
        query = query.filter(Resume.education == education)
    if work_years_min is not None:
        query = query.filter(Resume.work_years >= work_years_min)
    if work_years_max is not None:
        query = query.filter(Resume.work_years <= work_years_max)
    if status is not None:
        query = query.filter(Resume.status == status)

    # 总数
    total = query.count()

    # 分页
    offset = (page - 1) * page_size
    items = query.order_by(Resume.created_at.desc()).offset(offset).limit(page_size).all()

    return {
        "total": total,
        "items": items,
        "page": page,
        "page_size": page_size
    }


def create_resume(db: Session, resume_data: ResumeCreate) -> Resume:
    """创建简历"""
    db_resume = Resume(**resume_data.dict())
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume


def update_resume(db: Session, resume_id: int, resume_data: ResumeUpdate) -> Optional[Resume]:
    """更新简历"""
    db_resume = get_resume(db, resume_id)
    if not db_resume:
        return None

    update_data = resume_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_resume, field, value)

    db.commit()
    db.refresh(db_resume)
    return db_resume


def delete_resume(db: Session, resume_id: int) -> bool:
    """删除简历（软删除）"""
    db_resume = get_resume(db, resume_id)
    if not db_resume:
        return False

    db_resume.is_deleted = 1
    db.commit()
    return True


def update_resume_status(db: Session, resume_id: int, status: int) -> Optional[Resume]:
    """更新简历状态"""
    db_resume = get_resume(db, resume_id)
    if not db_resume:
        return None

    db_resume.status = status
    db.commit()
    db.refresh(db_resume)
    return db_resume


def bind_position(db: Session, resume_id: int, position_id: int) -> Optional[Resume]:
    """关联岗位"""
    db_resume = get_resume(db, resume_id)
    if not db_resume:
        return None

    db_resume.position_id = position_id
    db.commit()
    db.refresh(db_resume)
    return db_resume


def save_uploaded_file(file, upload_dir: str = "uploads/resumes") -> Dict[str, Any]:
    """保存上传的文件"""
    # 创建上传目录
    Path(upload_dir).mkdir(parents=True, exist_ok=True)

    # 获取文件信息
    file_name = file.filename
    file_extension = os.path.splitext(file_name)[1].lower()
    file_type = file_extension.lstrip('.')

    # 生成唯一文件名
    import uuid
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)

    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 获取文件大小
    file_size = os.path.getsize(file_path)

    return {
        "file_path": file_path,
        "file_name": file_name,
        "file_type": file_type,
        "file_size": file_size,
        "unique_filename": unique_filename
    }


def batch_delete_resumes(db: Session, resume_ids: List[int]) -> int:
    """批量删除简历"""
    count = db.query(Resume).filter(
        Resume.id.in_(resume_ids),
        Resume.is_deleted == 0
    ).update({Resume.is_deleted: 1}, synchronize_session=False)
    db.commit()
    return count
