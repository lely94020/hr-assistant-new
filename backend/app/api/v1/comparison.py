from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
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
def create_candidate_comparison(
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


@router.get("/{comparison_id}/export", response_class=HTMLResponse, summary="导出对比报告")
def export_comparison_report(comparison_id: int, db: Session = Depends(get_db)):
    """导出对比报告为HTML（可在浏览器中打印为PDF）"""
    try:
        comparison = get_comparison_by_id(db, comparison_id)

        if not comparison:
            raise HTTPException(status_code=404, detail="对比记录不存在")

        data = comparison.comparison_data or {}
        position = data.get("position", {})
        candidates = data.get("candidates", [])
        ai_analysis = comparison.ai_analysis or {}
        ranking = comparison.ranking or []

        # 构建候选人表格行
        candidate_rows = ""
        fields = [
            ("name", "姓名"), ("education", "学历"), ("school", "院校"),
            ("major", "专业"), ("work_years", "工作年限"),
            ("current_company", "当前公司"), ("current_position", "当前职位"),
            ("skills", "技能标签")
        ]
        for label_key in fields:
            prop, label = label_key
            cells = "<td style='font-weight:bold;background:#f5f7fa;padding:8px 12px;border:1px solid #e4e7ed'>{}</td>".format(label)
            for c in candidates:
                val = c.get(prop)
                if prop == "skills" and isinstance(val, list):
                    val = "、".join(val)
                if prop == "work_years" and val:
                    val = f"{val}年"
                cells += "<td style='padding:8px 12px;border:1px solid #e4e7ed;text-align:center'>{}</td>".format(val or "-")
            candidate_rows += "<tr>{}</tr>".format(cells)

        # 评分
        score_rows = ""
        dimension_map = {
            "professional_score": "专业能力", "logic_score": "逻辑思维",
            "communication_score": "沟通表达", "learning_score": "学习能力",
            "teamwork_score": "团队协作", "culture_score": "文化匹配"
        }
        for field, dim_name in dimension_map.items():
            cells = "<td style='font-weight:bold;background:#f5f7fa;padding:8px 12px;border:1px solid #e4e7ed'>{}</td>".format(dim_name)
            for c in candidates:
                ev = c.get("evaluation") or {}
                score = ev.get(field)
                bar_width = score if score else 0
                cells += "<td style='padding:8px 12px;border:1px solid #e4e7ed;text-align:center'><div style='background:#e4e7ed;border-radius:4px;overflow:hidden'><div style='height:18px;width:{}%;background:#409eff;border-radius:4px'></div></div><span style='font-size:12px;color:#606266'>{}</span></td>".format(bar_width, score or "-")
            score_rows += "<tr>{}</tr>".format(cells)

        # AI 分析
        analysis_html = ""
        if ai_analysis:
            analysis_html += "<h2 style='color:#303133;border-bottom:2px solid #409eff;padding-bottom:8px;margin-top:30px'>AI对比分析</h2>"
            summary = ai_analysis.get("comparison_summary") or ai_analysis.get("comparisonSummary") or ""
            if summary:
                analysis_html += "<div style='background:#f0f9eb;padding:12px 16px;border-radius:4px;color:#606266;line-height:1.8;margin-bottom:20px'>{}</div>".format(summary)

            cand_analysis = ai_analysis.get("candidate_analysis") or ai_analysis.get("candidateAnalysis") or []
            for ca in cand_analysis:
                name = ca.get("name", "未知")
                advs = ca.get("advantages_over_others") or ca.get("advantages") or []
                disads = ca.get("disadvantages") or []
                analysis_html += "<div style='margin-bottom:20px'><h3 style='color:#303133'>{} 分析</h3>".format(name)
                analysis_html += "<div style='display:flex;gap:20px'>"
                analysis_html += "<div style='flex:1'><h4 style='color:#67c23a'>优势</h4><ul>"
                for a in advs:
                    analysis_html += "<li style='color:#606266;line-height:1.8'>{}</li>".format(a)
                analysis_html += "</ul></div>"
                analysis_html += "<div style='flex:1'><h4 style='color:#e6a23c'>劣势</h4><ul>"
                for d in disads:
                    analysis_html += "<li style='color:#606266;line-height:1.8'>{}</li>".format(d)
                analysis_html += "</ul></div></div></div>"

            rec = ai_analysis.get("recommendation") or {}
            advice = ai_analysis.get("hiring_advice") or ai_analysis.get("hiringAdvice") or ""
            if rec or advice:
                analysis_html += "<div style='background:#f5f7fa;padding:16px;border-radius:4px;margin-top:20px'>"
                if rec.get("best_choice") or rec.get("bestChoice"):
                    analysis_html += "<p><strong>最佳人选：</strong>{}</p>".format(rec.get("best_choice") or rec.get("bestChoice"))
                if rec.get("reason"):
                    analysis_html += "<p style='color:#606266'>{}</p>".format(rec["reason"])
                if rec.get("alternative") or rec.get("alternativeChoice"):
                    analysis_html += "<p><strong>备选人选：</strong>{}</p>".format(rec.get("alternative") or rec.get("alternativeChoice"))
                if rec.get("alternative_reason") or rec.get("alternativeReason"):
                    analysis_html += "<p style='color:#606266'>{}</p>".format(rec.get("alternative_reason") or rec.get("alternativeReason"))
                if advice:
                    analysis_html += "<p style='color:#409eff;font-weight:500;margin-top:12px'>{}</p>".format(advice)
                analysis_html += "</div>"

        # 排名
        ranking_html = ""
        if ranking:
            ranking_html += "<h2 style='color:#303133;border-bottom:2px solid #409eff;padding-bottom:8px;margin-top:30px'>综合排名</h2><ol>"
            for r in sorted(ranking, key=lambda x: x.get("rank", 99)):
                name = r.get("name", "未知")
                score = r.get("score", "-")
                reason = r.get("reason", "")
                ranking_html += "<li style='margin-bottom:12px;line-height:1.8'><strong>{}（{}分）</strong><br><span style='color:#606266'>{}</span></li>".format(name, score, reason)
            ranking_html += "</ol>"

        html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>候选人对比报告</title></head>
<body style="font-family:'Microsoft YaHei','PingFang SC',sans-serif;padding:40px;color:#303133;max-width:1000px;margin:0 auto">
<h1 style="text-align:center;color:#303133;font-size:24px;margin-bottom:30px">候选人对比报告</h1>
<div style="display:flex;gap:20px;margin-bottom:30px;color:#606266">
<div><strong>对比岗位：</strong>{}</div>
<div><strong>对比人数：</strong>{}人</div>
<div><strong>创建时间：</strong>{}</div>
</div>
<h2 style="color:#303133;border-bottom:2px solid #409eff;padding-bottom:8px">基础信息对比</h2>
<table style="width:100%;border-collapse:collapse;margin-bottom:30px">{}</table>
<h2 style="color:#303133;border-bottom:2px solid #409eff;padding-bottom:8px">能力维度评分</h2>
<table style="width:100%;border-collapse:collapse;margin-bottom:30px">{}</table>
{}{}
<div style="text-align:center;color:#909399;margin-top:50px;font-size:12px;border-top:1px solid #e4e7ed;padding-top:20px">
由企业HR智能助手生成 · {}
</div>
</body>
</html>""".format(
            position.get("name", "未知岗位"),
            len(candidates),
            comparison.created_at.strftime("%Y-%m-%d %H:%M") if comparison.created_at else "-",
            candidate_rows,
            score_rows,
            ranking_html,
            analysis_html,
            comparison.created_at.strftime("%Y-%m-%d") if comparison.created_at else ""
        )

        return HTMLResponse(content=html_content, status_code=200)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出报告失败: {str(e)}")
