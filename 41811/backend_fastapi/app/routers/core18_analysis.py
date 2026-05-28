"""十八项核心制度分析路由

注意: 当前死亡患者查询等分析功能已在 core18_overview.py 中实现。
本文件作为扩展分析功能预留。
"""
from fastapi import APIRouter

router = APIRouter(tags=["十八项核心制度-分析"])


@router.get("/analysis-overview")
def analysis_overview():
    """
    指标分析总览
    预留接口，后续可扩展趋势分析、同比环比等功能
    """
    return {
        "period": "month",
        "data": [],
        "message": "请使用 /api/core18/execution-data/ 获取指标执行数据"
    }
