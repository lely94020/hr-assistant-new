from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.services.screening_service import ScreeningService
from app.schemas.screening import (
    PositionMatchRequest,
    CustomScreeningRequest,
    BatchMarkRequest,
    ScreeningResponse,
    AnalysisResponse
)

router = APIRouter(prefix="/api/v1/screening", tags=["智能简历筛选"])


@router.post("/match", response_model=ScreeningResponse, summary="岗位匹配筛选")
async def screen_by_position(
    request: PositionMatchRequest,
    db: Session = Depends(get_db)
):
    """
    选择目标岗位，系统自动从简历库中检索最匹配的候选人

    - **position_id**: 目标岗位ID
    - **top_n**: 返回数量，默认10，范围5-50
    - **filters**: 可选的筛选条件（最低学历、最少工作年限、必备技能）
    """
    try:
        result = await ScreeningService.screen_by_position(
            db=db,
            position_id=request.position_id,
            top_n=request.top_n,
            filters=request.filters
        )

        return ScreeningResponse(
            code=0,
            message="success",
            data=result
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"筛选失败: {str(e)}")


@router.post("/custom", response_model=ScreeningResponse, summary="自定义条件筛选")
async def screen_by_custom_query(
    request: CustomScreeningRequest,
    db: Session = Depends(get_db)
):
    """
    HR输入自定义的筛选要求，进行智能检索

    - **query**: 自定义筛选描述文本
    - **top_n**: 返回数量，默认10，范围5-50
    """
    try:
        result = await ScreeningService.screen_by_custom_query(
            db=db,
            query=request.query,
            top_n=request.top_n
        )

        return ScreeningResponse(
            code=0,
            message="success",
            data=result
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"筛选失败: {str(e)}")


@router.get("/analysis/{resume_id}", response_model=AnalysisResponse, summary="获取匹配分析")
async def get_resume_analysis(
    resume_id: int,
    position_id: int,
    db: Session = Depends(get_db)
):
    """
    获取单份简历与指定岗位的详细匹配分析

    - **resume_id**: 简历ID
    - **position_id**: 岗位ID
    """
    try:
        result = await ScreeningService.get_resume_analysis(
            db=db,
            resume_id=resume_id,
            position_id=position_id
        )

        return AnalysisResponse(
            code=0,
            message="success",
            data=result
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分析失败: {str(e)}")


@router.post("/batch-mark", summary="批量标记筛选结果")
def batch_mark_resumes(
    request: BatchMarkRequest,
    db: Session = Depends(get_db)
):
    """
    批量标记简历的筛选结果

    - **resume_ids**: 简历ID列表
    - **mark_type**: 标记类型
        - pass: 通过初筛
        - reject: 不通过
        - pending: 待定
    """
    try:
        result = ScreeningService.batch_mark_resumes(
            db=db,
            resume_ids=request.resume_ids,
            mark_type=request.mark_type
        )

        return {
            "code": 0,
            "message": "success",
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量标记失败: {str(e)}")