from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.position import (
    PositionCreate, PositionUpdate, PositionResponse, PositionListResponse
)
from app.crud import position as crud

# 所有接口前缀；接口文档分组名
router = APIRouter(prefix="/api/v1/positions", tags=["岗位管理"])

@router.get("", response_model=PositionListResponse, summary="获取岗位列表")
def get_positions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    position_name: Optional[str] = Query(None, description="岗位名称"),
    department: Optional[str] = Query(None, description="部门"),
    status: Optional[int] = Query(None, description="状态"),
    db: Session = Depends(get_db)
):
    """获取岗位列表，支持分页和筛选"""
    total, items = crud.get_position_list(
        db, page, page_size, position_name, department, status
    )
    return PositionListResponse(
        total=total,
        items=[PositionResponse.model_validate(item) for item in items],
        page=page,
        page_size=page_size
    )

@router.get("/{position_id}", response_model=PositionResponse, summary="获取岗位详情")
def get_position(position_id: int, db: Session = Depends(get_db)):
    """根据ID获取岗位详情"""
    db_position = crud.get_position_by_id(db, position_id)
    if not db_position:
        raise HTTPException(status_code=404, detail="岗位不存在")
    return PositionResponse.model_validate(db_position)

@router.post("", response_model=PositionResponse, summary="创建岗位")
def create_position(position: PositionCreate, db: Session = Depends(get_db)):
    """创建新岗位"""
    return PositionResponse.model_validate(crud.create_position(db, position))

@router.put("/{position_id}", response_model=PositionResponse, summary="更新岗位")
def update_position(
    position_id: int,
    position: PositionUpdate,
    db: Session = Depends(get_db)
):
    """更新岗位信息"""
    db_position = crud.update_position(db, position_id, position)
    if not db_position:
        raise HTTPException(status_code=404, detail="岗位不存在")
    return PositionResponse.model_validate(db_position)

@router.delete("/{position_id}", summary="删除岗位")
def delete_position(position_id: int, db: Session = Depends(get_db)):
    """删除岗位（软删除）"""
    db_position = crud.delete_position(db, position_id)
    if not db_position:
        raise HTTPException(status_code=404, detail="岗位不存在")
    return {"message": "删除成功"}