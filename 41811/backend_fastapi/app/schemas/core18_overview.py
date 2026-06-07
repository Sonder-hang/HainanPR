"""Pydantic Schema - 十八项核心制度总览"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Core18OverviewResponse(BaseModel):
    """总览统计响应"""
    total_indicators: int = 0
    computed_indicators: int = 0
    pending_indicators: int = 0
    failed_indicators: int = 0


class SubIndicatorCardItem(BaseModel):
    """子指标卡片数据（虚拟父指标内嵌展示用）"""
    indicator_id: int
    display_name: str
    rate_percent: Optional[float] = None
    count: Optional[int] = None
    calc_type: str = "ratio"


class IndicatorCardItem(BaseModel):
    """指标卡片数据 - 包含指标信息和执行数据"""
    id: int
    name: str  # 指标名称
    category: str = ""  # 分类
    calc_type: str = "ratio"  # ratio | count
    # 详情描述（比值型用 numerator_desc/denominator_desc，统计型用 description）
    numerator_desc: str = ""
    denominator_desc: str = ""
    description: str = ""
    # 执行数据
    has_data: bool = False
    # 比值型指标字段
    rate_percent: Optional[float] = None
    numerator_count: Optional[int] = None
    denominator_count: Optional[int] = None
    # 计数型指标字段
    count: Optional[int] = None
    # 虚拟父指标相关字段
    is_virtual_parent: bool = False  # 是否虚拟父指标卡片
    parent_name: Optional[str] = None  # 虚拟父指标名
    sub_indicators: Optional[List[SubIndicatorCardItem]] = None  # 子指标列表（虚拟父指标时填充）
    rate_ratio: Optional[float] = None  # 率比值（率比型虚拟父指标时填充）

    class Config:
        from_attributes = True


class OverviewResponse(BaseModel):
    """总览页面统一响应"""
    indicators: List[IndicatorCardItem] = []  # 所有指标卡片数据
    categories: List[str] = []  # 所有分类列表，用于筛选器


class IndicatorExecutionData(BaseModel):
    """指标执行数据"""
    indicator_id: int
    indicator_name: str
    category: str = ""
    calc_type: str = "ratio"  # ratio | count
    has_data: bool = False
    rate_percent: Optional[float] = None
    numerator_count: Optional[int] = None
    denominator_count: Optional[int] = None


class DeathPatientQuery(BaseModel):
    """死亡患者查询参数"""
    hospital_code: Optional[str] = None
    time_mode: str = "monthly"  # monthly | quarterly
    time_value: Optional[str] = None
    page: int = 1
    page_size: int = 20
    keyword: str = ""


class DeathPatient(BaseModel):
    """死亡患者信息"""
    id: int
    patient_id: str
    patient_name: str
    department: str
    hospital: str
    death_basis: str
    death_basis_detail: str
    death_record_source: str
    death_time: Optional[str] = None

    class Config:
        from_attributes = True


class DeathPatientResponse(BaseModel):
    """死亡患者列表响应"""
    total: int = 0
    page: int = 1
    page_size: int = 20
    data: List[DeathPatient] = []


class ExecutionDataQuery(BaseModel):
    """执行数据查询参数"""
    hospital_code: Optional[str] = None
    time_mode: str = "monthly"  # monthly | quarterly
    time_value: Optional[str] = None
