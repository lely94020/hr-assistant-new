from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.position import JobPosition
from app.schemas.position import PositionCreate, PositionUpdate
from typing import Optional

def get_position_list(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    position_name: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[int] = None
):
    """获取岗位列表（分页+筛选）"""
    # 只查未软删除的数据
    query = db.query(JobPosition).filter(JobPosition.is_deleted == 0)

    # 筛选条件
    if position_name:
        query = query.filter(JobPosition.position_name.like(f"%{position_name}%"))
    if department:
        query = query.filter(JobPosition.department.like(f"%{department}%"))
    if status is not None:
        query = query.filter(JobPosition.status == status)

    # 总数
    total = query.count()

    # 分页
    # 按创建时间降序排序，跳过前面的记录（(page - 1) * page_size），并限制返回的记录数量为page_size
    items = query.order_by(JobPosition.created_at.desc()) \
                 .offset((page - 1) * page_size) \
                 .limit(page_size) \
                 .all()

    return total, items

def get_position_by_id(db: Session, position_id: int):
    """根据ID获取岗位"""
    return db.query(JobPosition).filter(
        and_(JobPosition.id == position_id, JobPosition.is_deleted == 0)
    ).first()

def check_duplicate_position(db: Session, department: str, position_name: str, exclude_id: Optional[int] = None) -> bool:
    """检查同一部门下是否存在同名岗位"""
    query = db.query(JobPosition).filter(
        and_(
            JobPosition.department == department,
            JobPosition.position_name == position_name,
            JobPosition.is_deleted == 0
        )
    )
    if exclude_id is not None:
        query = query.filter(JobPosition.id != exclude_id)
    return query.first() is not None


def create_position(db: Session, position: PositionCreate):
    """创建岗位"""
    # 检查是否已存在同名岗位
    if check_duplicate_position(db, position.department, position.position_name):
        raise ValueError(f"部门 '{position.department}' 下已存在岗位 '{position.position_name}'")

    db_position = JobPosition(**position.model_dump())
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position

def update_position(db: Session, position_id: int, position: PositionUpdate):
    """更新岗位"""
    db_position = get_position_by_id(db, position_id)
    if not db_position:
        return None

    update_data = position.model_dump(exclude_unset=True)

    # 保护 NOT NULL 字段：禁止显式设为 None
    not_null_fields = {"position_name", "department", "job_description", "requirements"}
    for field in not_null_fields:
        if field in update_data and update_data[field] is None:
            raise ValueError(f"字段 '{field}' 不能为空")

    # 如果更新了部门或岗位名称，检查是否与已有记录重复
    new_department = update_data.get("department", db_position.department)
    new_position_name = update_data.get("position_name", db_position.position_name)
    if "department" in update_data or "position_name" in update_data:
        if check_duplicate_position(db, new_department, new_position_name, exclude_id=position_id):
            raise ValueError(f"部门 '{new_department}' 下已存在岗位 '{new_position_name}'")

    for key, value in update_data.items():
        setattr(db_position, key, value)
    db.commit()
    db.refresh(db_position)
    return db_position

def delete_position(db: Session, position_id: int):
    """删除岗位（软删除）"""
    db_position = get_position_by_id(db, position_id)
    if db_position:
        db_position.is_deleted = 1
        db.commit()
    return db_position