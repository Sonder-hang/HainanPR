"""指标管理路由"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List

from app.database import get_db
from app.models.indicator import Indicator, IndicatorExecution, TableMetadata
from app.schemas.indicator import (
    IndicatorCreate, IndicatorUpdate, IndicatorResponse,
    IndicatorExecutionResponse, ExecuteRequest, TestSqlRequest,
    PreviewPageRequest, PreviewPageResponse,
)
from app.services.text2sql import Text2SQLService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["指标管理"])


def _obj_to_dict(obj) -> dict:
    return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}


# ---- 医院列表 ----

@router.get("/hospitals/", response_model=List[dict])
def list_hospitals(db: Session = Depends(get_db)):
    """获取医疗机构列表（优先从本地 hospital 表读取，备用从远程 DIM_MDC_ORG 查询）"""
    # 优先从本地 hospital 表读取
    from app.models.monitoring import Hospital as LocalHospital
    local_hospitals = db.query(LocalHospital).filter(LocalHospital.is_active == 1).order_by(LocalHospital.name).all()
    if local_hospitals:
        return [
            {"MDC_ORG_CD": h.hospital_code or h.id, "MDC_ORG_NM": h.name}
            for h in local_hospitals
        ]

    # 备用：从远程数据库查询
    import sys
    from pathlib import Path
    runner_path = Path(__file__).parent.parent.parent / "Hainan_SQL-main" / "text2sql_app" / "sql_runner.py"
    if runner_path.exists():
        sys.path.insert(0, str(runner_path.parent))
        try:
            from sql_runner import execute_full
            sql = "SELECT MDC_ORG_CD, MDC_ORG_NM FROM DIM_MDC_ORG ORDER BY MDC_ORG_NM"
            cols, rows, err = execute_full(sql)
            if err:
                logger.error(f"获取医院列表失败: {err}")
                return []
            # rows 已经是字典列表（使用 DictCursor），直接返回
            return rows
        except Exception as e:
            logger.error(f"获取医院列表异常: {e}")
            return []
        finally:
            if str(runner_path.parent) in sys.path:
                sys.path.remove(str(runner_path.parent))
    return []


# ---- 四要素指标 CRUD ----

@router.get("/four", response_model=list[IndicatorResponse])
def list_four(keyword: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Indicator).filter(Indicator.indicator_type == "four")
    if keyword:
        q = q.filter(Indicator.name.contains(keyword))
    return q.all()


@router.get("/four/{pk}", response_model=IndicatorResponse)
def get_four(pk: int, db: Session = Depends(get_db)):
    obj = db.query(Indicator).filter(Indicator.id == pk, Indicator.indicator_type == "four").first()
    if not obj:
        raise HTTPException(status_code=404, detail="指标不存在")
    return obj


@router.post("/four/create", response_model=IndicatorResponse, status_code=201)
def create_four(data: IndicatorCreate, db: Session = Depends(get_db)):
    obj = Indicator(**data.model_dump())
    obj.indicator_type = "four"
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/four/update/{pk}", response_model=IndicatorResponse)
def update_four(pk: int, data: IndicatorUpdate, db: Session = Depends(get_db)):
    obj = db.query(Indicator).filter(Indicator.id == pk, Indicator.indicator_type == "four").first()
    if not obj:
        raise HTTPException(status_code=404, detail="指标不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/four/delete/{pk}", status_code=204)
def delete_four(pk: int, db: Session = Depends(get_db)):
    obj = db.query(Indicator).filter(Indicator.id == pk, Indicator.indicator_type == "four").first()
    if not obj:
        raise HTTPException(status_code=404, detail="指标不存在")
    db.delete(obj)
    db.commit()


# ---- 十八项核心指标 CRUD ----

@router.get("/core18", response_model=list[IndicatorResponse])
def list_core18(keyword: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Indicator).filter(Indicator.indicator_type == "core18")
    if keyword:
        q = q.filter(Indicator.name.contains(keyword))
    return q.all()


@router.get("/core18/{pk}", response_model=IndicatorResponse)
def get_core18(pk: int, db: Session = Depends(get_db)):
    obj = db.query(Indicator).filter(Indicator.id == pk, Indicator.indicator_type == "core18").first()
    if not obj:
        raise HTTPException(status_code=404, detail="指标不存在")
    return obj


@router.post("/core18/create", response_model=IndicatorResponse, status_code=201)
def create_core18(data: IndicatorCreate, db: Session = Depends(get_db)):
    obj = Indicator(**data.model_dump())
    obj.indicator_type = "core18"
    db.add(obj)
    db.commit()
    db.refresh(obj)
    # 同步到 text2sql 服务（指标.json）
    sync_data = {
        "name": obj.name,
        "formula": obj.formula or "",
        "numerator_desc": obj.numerator_desc or "",
        "denominator_desc": obj.denominator_desc or "",
        "description": obj.description or "",
        "involved_tables": obj.involved_tables or [],
        "numerator_sql": obj.numerator_sql or "",
        "denominator_sql": obj.denominator_sql or "",
        "sql": obj.sql_content or "",
    }
    service = Text2SQLService()
    sync_result = service.sync_indicator(sync_data)
    if not sync_result.get("ok"):
        logger.warning(f"指标同步到 text2sql 失败: {sync_result.get('error')}")
    return obj


@router.put("/core18/update/{pk}", response_model=IndicatorResponse)
def update_core18(pk: int, data: IndicatorUpdate, db: Session = Depends(get_db)):
    obj = db.query(Indicator).filter(Indicator.id == pk, Indicator.indicator_type == "core18").first()
    if not obj:
        raise HTTPException(status_code=404, detail="指标不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/core18/delete/{pk}", status_code=204)
def delete_core18(pk: int, db: Session = Depends(get_db)):
    obj = db.query(Indicator).filter(Indicator.id == pk, Indicator.indicator_type == "core18").first()
    if not obj:
        raise HTTPException(status_code=404, detail="指标不存在")
    db.delete(obj)
    db.commit()


# ---- 执行相关 ----

def _list_executions(
    indicator_id: Optional[int] = None,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    kind: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    获取执行历史记录列表，支持搜索、筛选
    
    - keyword: 按指标名称模糊搜索
    - status: 按状态筛选 (pending/running/success/failed)
    - kind: 按类型筛选 (four/core18)
    - offset: 跳过数量
    """
    q = db.query(IndicatorExecution).options(joinedload(IndicatorExecution.indicator))
    if indicator_id:
        q = q.filter(IndicatorExecution.indicator_id == indicator_id)
    if keyword:
        q = q.filter(IndicatorExecution.indicator_name.contains(keyword))
    if status and status != 'all':
        q = q.filter(IndicatorExecution.status == status)
    if kind:
        q = q.filter(IndicatorExecution.kind == kind)
    
    # 获取总数（用于分页信息）
    total = q.count()
    
    # 不限制返回数量
    limit = None
    
    if offset is None:
        offset = 0
    
    rows = q.order_by(IndicatorExecution.execution_time.desc()).offset(offset)
    if limit is not None:
        rows = rows.limit(limit)
    rows = rows.all()
    for row in rows:
        if not row.indicator_name and row.indicator:
            row.indicator_name = row.indicator.name
    return rows


@router.get("/execution/", response_model=list[IndicatorExecutionResponse])
def list_executions(
    indicator_id: Optional[int] = None,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    kind: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    db: Session = Depends(get_db),
):
    return _list_executions(indicator_id, keyword, status, kind, limit, offset, db)


@router.get("/execution", response_model=list[IndicatorExecutionResponse])
def list_executions_no_slash(
    indicator_id: Optional[int] = None,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    kind: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    db: Session = Depends(get_db),
):
    return _list_executions(indicator_id, keyword, status, kind, limit, offset, db)


@router.delete("/execution/{execution_id}", status_code=204)
def delete_execution(execution_id: int, db: Session = Depends(get_db)):
    row = db.query(IndicatorExecution).filter(IndicatorExecution.id == execution_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    db.delete(row)
    db.commit()


@router.post("/execute/")
def execute_indicator(data: ExecuteRequest, db: Session = Depends(get_db)):
    service = Text2SQLService()
    req_dict = data.model_dump()
    if data.indicator_id:
        indicator = db.query(Indicator).filter(Indicator.id == data.indicator_id).first()
        if not indicator:
            raise HTTPException(status_code=404, detail="指标不存在")
        ind_data = _obj_to_dict(indicator)
        # 补充 ExecuteRequest 中传入的额外字段
        ind_data["kind"] = data.business_type or "core18"
        ind_data["run_mode"] = data.run_mode or "immediate"
        ind_data["time_range"] = data.time_range or "全量"
        ind_data["result_type"] = data.result_type or "ratio"
        ind_data["calc_method"] = data.calc_method or "SQL录入"
        # 补充医院和时间筛选参数
        ind_data["hospital_codes"] = data.hospital_codes
        ind_data["time_mode"] = data.time_mode
        ind_data["time_value"] = data.time_value
        ind_data["date_field"] = data.date_field or "discharge"
        ind_data["group_by_hospital"] = data.group_by_hospital if data.group_by_hospital is not None else True
        logger.info(f"[Execute] 接收到的请求数据: hospital_codes={data.hospital_codes}, time_mode={data.time_mode}, time_value={data.time_value}, date_field={ind_data['date_field']}, group_by_hospital={ind_data['group_by_hospital']}")
    else:
        ind_data = {"id": None, **req_dict}

    return service.execute_indicator(indicator_data=ind_data, db_session=db)


@router.post("/test-sql/")
def test_sql(data: TestSqlRequest):
    service = Text2SQLService()
    return service.test_sql(data.sql, data.limit)


# ---- 表结构 ----

@router.get("/tables/")
def list_tables(db: Session = Depends(get_db)):
    tables = db.query(TableMetadata).all()
    return [{"table_name": t.table_name, "business_definition": t.business_definition, "field_count": t.field_count} for t in tables]


@router.get("/column-meanings/")
def column_meanings():
    service = Text2SQLService()
    return service.get_column_meanings()


@router.post("/prompt-preview/")
def prompt_preview(data: dict):
    service = Text2SQLService()
    return service.prompt_preview(data)


@router.post("/execution/preview-page", response_model=PreviewPageResponse)
def get_preview_page(data: PreviewPageRequest, db: Session = Depends(get_db)):
    """根据执行记录 ID 获取指定页的预览数据（分子/分母），支持翻页"""
    service = Text2SQLService()
    result = service.fetch_preview_page(
        execution_id=data.execution_id,
        target=data.target,
        page=data.page,
        page_size=data.page_size,
        db_session=db,
    )
    return result
