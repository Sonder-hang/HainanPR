"""Pydantic Schema - 指标分析台配置"""
from pydantic import BaseModel
from typing import Optional, List, Any, Literal


class SubIndicatorItem(BaseModel):
    """子指标下拉选项"""
    indicator_id: int
    display_name: str
    view_mode: Literal["rate", "structure", "ratio"]


class IndicatorConfigData(BaseModel):
    """分析台图表数据"""
    cardData: Optional[dict] = None
    timeTrendData: Optional[dict] = None
    hospitalComparisonData: Optional[dict] = None
    leftData: Optional[dict] = None
    leftData1: Optional[dict] = None
    leftData2: Optional[dict] = None
    totalCount: Optional[int] = None
    totalCountLabel: Optional[str] = None
    leftChartLimit: Optional[int] = None


class IndicatorConfigResponse(BaseModel):
    """指标分析台配置响应"""
    indicator_id: int
    indicator_name: str
    template_type: Literal["STRUCTURE", "STRUCTURE-special", "RATE", "RATE-special", "TABLE"]
    title: str
    showDeathToggle: bool = False
    rateLabel: str = "率"
    rateUnit: str = "%"
    maxRate: float = 100.0
    yAxisUnit: str = "%"
    leftTitle: Optional[str] = None
    leftChartTitle: Optional[str] = None
    leftChartTitle1: Optional[str] = None
    leftChartTitle2: Optional[str] = None
    leftChartColor: str = "#2E57E5"
    leftChartColor1: str = "#12B881"
    leftChartColor2: str = "#2E57E5"
    timeComparisonTitle: str = "趋势分析"
    hospitalComparisonTitle: str = "医院对比"
    totalCountLabel: Optional[str] = None
    rankingMode: Optional[Literal["single", "double", "multi"]] = None
    is_parent_indicator: bool = False
    parent_name: Optional[str] = None
    sub_indicators: Optional[List[SubIndicatorItem]] = None
    table_headers: Optional[List[str]] = None
    data: IndicatorConfigData = IndicatorConfigData()

    class Config:
        from_attributes = True
