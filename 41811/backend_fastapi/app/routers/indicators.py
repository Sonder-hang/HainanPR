"""指标管理路由"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from app.database import get_db
from app.models.indicator import Indicator, IndicatorExecution, TableMetadata
from app.schemas.indicator import (
    IndicatorCreate, IndicatorUpdate, IndicatorResponse,
    IndicatorExecutionResponse, ExecuteRequest, TestSqlRequest,
)
from app.services.text2sql import Text2SQLService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["指标管理"])


def _obj_to_dict(obj) -> dict:
    return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}


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

@router.get("/execution/", response_model=list[IndicatorExecutionResponse])
def list_executions(indicator_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(IndicatorExecution).options(joinedload(IndicatorExecution.indicator))
    if indicator_id:
        q = q.filter(IndicatorExecution.indicator_id == indicator_id)
    rows = q.order_by(IndicatorExecution.execution_time.desc()).limit(100).all()
    for row in rows:
        if not row.indicator_name and row.indicator:
            row.indicator_name = row.indicator.name
    return rows


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
