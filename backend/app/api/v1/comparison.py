from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.services.comparison_service import ComparisonService
from app.crud.comparison import (
    create_comparison,
    get_comparison_by_id,
    get_all_comparisons
)
from app.schemas.comparison import (
    CreateComparisonRequest,
    ComparisonResponse,
    AnalyzeComparisonResponse,
    ComparisonHistoryResponse,
    ComparisonHistoryItem
)

router = APIRouter(prefix="/api/v1/comparison", tags=["候选人对比"])


@router.post("/create", response_model=ComparisonResponse, summary="创建候选人对比")
async def create_candidate_comparison(
    request: CreateComparisonRequest,
    db: Session = Depends(get_db)
):
    """
    创建候选人对比
    - 选择2-5个候选人
    - 汇总简历信息和面试评价
    """
    try:
        # 验证候选人数量
        if len(request.resume_ids) < 2:
            raise HTTPException(status_code=400, detail="至少需要2个候选人进行对比")

        if len(request.resume_ids) > 5:
            raise HTTPException(status_code=400, detail="最多支持5个候选人对比")

        # 构建对比数据
        comparison_data = ComparisonService.build_comparison_data(
            db,
            request.position_id,
            request.resume_ids
        )

        # 创建对比记录
        comparison = create_comparison(
            db,
            position_id=request.position_id,
            resume_ids=request.resume_ids,
            comparison_data=comparison_data
        )

        # 构建响应
        response_data = {
            "id": comparison.id,
            "position": comparison_data["position"],
            "candidates": comparison_data["candidates"],
            "created_at": comparison.created_at
        }

        return ComparisonResponse(**response_data)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建对比失败: {str(e)}")


@router.get("/{comparison_id}", response_model=dict, summary="获取对比详情")
def get_comparison_detail(comparison_id: int, db: Session = Depends(get_db)):
    """获取候选人对比详情"""
    try:
        comparison = get_comparison_by_id(db, comparison_id)

        if not comparison:
            raise HTTPException(status_code=404, detail="对比记录不存在")

        response_data = {
            "id": comparison.id,
            "position_id": comparison.position_id,
            "resume_ids": comparison.resume_ids,
            "comparison_data": comparison.comparison_data,
            "ai_analysis": comparison.ai_analysis,
            "ranking": comparison.ranking,
            "created_at": comparison.created_at
        }

        return {
            "code": 0,
            "message": "success",
            "data": response_data
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对比详情失败: {str(e)}")


@router.post("/{comparison_id}/analyze", response_model=AnalyzeComparisonResponse, summary="AI对比分析")
async def analyze_comparison(
    comparison_id: int,
    db: Session = Depends(get_db)
):
    """
    生成AI对比分析
    - 分析各候选人优劣势
    - 给出推荐排名
    - 提供录用建议
    """
    try:
        # 生成AI分析
        analysis_result = await ComparisonService.generate_ai_analysis(
            db,
            comparison_id
        )

        # 获取对比记录
        comparison = get_comparison_by_id(db, comparison_id)

        # 构建响应
        response_data = {
            "id": comparison.id,
            "comparison_summary": analysis_result["comparison_summary"],
            "candidate_analysis": analysis_result["candidate_analysis"],
            "ranking": analysis_result["ranking"],
            "recommendation": analysis_result["recommendation"],
            "hiring_advice": analysis_result["hiring_advice"]
        }

        return AnalyzeComparisonResponse(**response_data)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI分析失败: {str(e)}")


@router.get("/history", response_model=ComparisonHistoryResponse, summary="对比历史")
def get_comparison_history(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """获取对比历史列表"""
    try:
        skip = (page - 1) * page_size

        total, comparisons = get_all_comparisons(db, skip=skip, limit=page_size)

        items = []
        for comp in comparisons:
            # 从对比数据中提取候选人姓名
            candidate_names = []
            if comp.comparison_data and "candidates" in comp.comparison_data:
                candidate_names = [
                    c.get("name", "未知")
                    for c in comp.comparison_data["candidates"]
                ]

            # 获取岗位名称
            position_name = "未知岗位"
            if comp.comparison_data and "position" in comp.comparison_data:
                position_name = comp.comparison_data["position"].get("name", "未知岗位")

            items.append({
                "id": comp.id,
                "position_id": comp.position_id,
                "position_name": position_name,
                "resume_count": len(comp.resume_ids),
                "candidate_names": candidate_names,
                "created_at": comp.created_at
            })

        return ComparisonHistoryResponse(
            total=total,
            items=items
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对比历史失败: {str(e)}")


@router.get("/{comparison_id}/export", summary="导出对比报告")
def export_comparison_report(comparison_id: int, db: Session = Depends(get_db)):
    """
    导出对比报告为PDF
    TODO: 实现PDF生成功能
    """
    try:
        comparison = get_comparison_by_id(db, comparison_id)

        if not comparison:
            raise HTTPException(status_code=404, detail="对比记录不存在")

        # TODO: 使用reportlab或weasyprint生成PDF
        return {
            "code": 0,
            "message": "PDF导出功能开发中",
            "data": {
                "comparison_id": comparison_id,
                "status": "pending"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出报告失败: {str(e)}")
