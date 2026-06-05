"""Pydantic Schema - 指标分析台配置"""
from pydantic import BaseModel
from typing import Optional, List, Any, Literal


class IndicatorConfigData(BaseModel):
    """分析台图表数据"""
    # RATE 类型
    cardData: Optional[dict] = None          # 圆形进度环数据
    timeTrendData: Optional[dict] = None    # 时间趋势数据
    hospitalComparisonData: Optional[dict] = None  # 医院对比数据

    # STRUCTURE / STRUCTURE-special 类型
    leftData: Optional[dict] = None
    leftData1: Optional[dict] = None        # STRUCTURE-special 第一组
    leftData2: Optional[dict] = None        # STRUCTURE-special 第二组
    totalCount: Optional[int] = None
    totalCountLabel: Optional[str] = None
    leftChartLimit: Optional[int] = None    # 排行榜展示上限（默认20），由 subitem_config.limit 决定

    # COMPOSITE 类型
    dataTypes: Optional[List[dict]] = None  # [{name, key}, ...]
    yAxisUnit: Optional[str] = "%"


class IndicatorConfigResponse(BaseModel):
    """指标分析台配置响应"""
    indicator_key: str                       # cascader key，如 transferWithin48HoursRate
    indicator_id: int
    indicator_name: str
    template_type: Literal["STRUCTURE", "STRUCTURE-special", "RATE", "RATE-special", "COMPOSITE"]
    title: str                               # 展示标题
    # 通用配置
    showDeathToggle: bool = False
    rateLabel: str = "率"
    rateUnit: str = "%"
    maxRate: float = 100.0
    yAxisUnit: str = "%"
    leftTitle: Optional[str] = None
    leftChartTitle: Optional[str] = None
    leftChartTitle1: Optional[str] = None    # STRUCTURE-special
    leftChartTitle2: Optional[str] = None    # STRUCTURE-special
    leftChartColor: str = "#2E57E5"
    leftChartColor1: str = "#12B881"
    leftChartColor2: str = "#2E57E5"
    timeComparisonTitle: str = "趋势分析"
    hospitalComparisonTitle: str = "医院对比"
    totalCountLabel: Optional[str] = None
    # rankingMode: single=单排行榜, double=双排行榜, multi=多排行榜（由 subitem_config.type 决定）
    rankingMode: Optional[Literal["single", "double", "multi"]] = None
    # 数据
    data: IndicatorConfigData = IndicatorConfigData()

    class Config:
        from_attributes = True
