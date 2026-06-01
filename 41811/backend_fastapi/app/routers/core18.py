"""十八项核心制度路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import time

from app.database import get_db
from app.models.core18 import Core18Indicator, Core18ExecutionLog
from app.models.indicator import Indicator, IndicatorExecution
from app.schemas.core18 import (
    Core18IndicatorCreate, Core18IndicatorUpdate, Core18IndicatorResponse,
    Core18ExecutionLogResponse,
)
from app.services.text2sql import Text2SQLService

router = APIRouter(tags=["十八项核心制度"])


@router.get("/overview")
def core18_overview(db: Session = Depends(get_db)):
    total = db.query(Core18Indicator).count()
    success = db.query(Core18Indicator).filter(Core18Indicator.status == "success").count()
    pending = db.query(Core18Indicator).filter(Core18Indicator.status == "pending").count()
    failed = db.query(Core18Indicator).filter(Core18Indicator.status == "failed").count()
    return {
        "total_indicators": total,
        "computed_indicators": success,
        "pending_indicators": pending,
        "failed_indicators": failed,
        "average_rate": None,
        "indicators_by_system": {},
    }


@router.get("/indicators/", response_model=list[Core18IndicatorResponse])
def list_indicators(keyword: str = None, db: Session = Depends(get_db)):
    q = db.query(Core18Indicator)
    if keyword:
        q = q.filter(Core18Indicator.name.contains(keyword))
    return q.all()


@router.post("/indicators/", response_model=Core18IndicatorResponse, status_code=201)
def create_indicator(data: Core18IndicatorCreate, db: Session = Depends(get_db)):
    obj = Core18Indicator(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/indicators/{pk}", response_model=Core18IndicatorResponse)
def get_indicator(pk: int, db: Session = Depends(get_db)):
    obj = db.query(Core18Indicator).filter(Core18Indicator.id == pk).first()
    if not obj:
        raise HTTPException(status_code=404, detail="指标不存在")
    return obj


@router.put("/indicators/{pk}", response_model=Core18IndicatorResponse)
def update_indicator(pk: int, data: Core18IndicatorUpdate, db: Session = Depends(get_db)):
    obj = db.query(Core18Indicator).filter(Core18Indicator.id == pk).first()
    if not obj:
        raise HTTPException(status_code=404, detail="指标不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/indicators/{pk}", status_code=204)
def delete_indicator(pk: int, db: Session = Depends(get_db)):
    obj = db.query(Core18Indicator).filter(Core18Indicator.id == pk).first()
    if not obj:
        raise HTTPException(status_code=404, detail="指标不存在")
    db.delete(obj)
    db.commit()


@router.get("/analysis")
def core18_analysis():
    return {"period": "month", "data": []}


@router.post("/execute/")
def core18_execute(indicator_id: int, db: Session = Depends(get_db)):
    indicator = db.query(Core18Indicator).filter(Core18Indicator.id == indicator_id).first()
    if not indicator:
        raise HTTPException(status_code=404, detail="指标不存在")

    service = Text2SQLService()
    start_time = time.time()
    ind_data = {k: v for k, v in indicator.__dict__.items() if not k.startswith("_")}
    result = service.execute_indicator(indicator_data=ind_data, db_session=db)
    duration = time.time() - start_time

    log = Core18ExecutionLog(
        indicator_id=indicator.id,
        indicator_name=indicator.name,
        kind="core18",
        run_mode="immediate",
        time_range="全量",
        result_type="ratio",
        calc_method="SQL录入",
        numerator_sql=result.get("numerator_sql", ""),
        denominator_sql=result.get("denominator_sql", ""),
        sql=result.get("sql", ""),
        numerator_count=result.get("numerator_count"),
        denominator_count=result.get("denominator_count"),
        rate_percent=result.get("rate_percent"),
        rate_formula=result.get("rate_formula", ""),
        result_text=result.get("analysis", ""),
        preview_data={"columns": result.get("preview_columns", []), "rows": result.get("preview_rows", [])},
        denominator_preview_data={"columns": result.get("denominator_preview_columns", []), "rows": result.get("denominator_preview_rows", [])},
        error=result.get("error", ""),
        numerator_error=result.get("numerator_error", ""),
        denominator_error=result.get("denominator_error", ""),
        attempts=result.get("attempts", []),
        llm_thinking=result.get("numerator_llm_thinking", "") or result.get("llm_thinking", ""),
        llm_raw=result.get("numerator_llm_raw", "") or result.get("llm_raw", ""),
        cache_hit=result.get("cache_hit", False),
        request_id=result.get("request_id", ""),
        conversation_id=result.get("conversation_id", ""),
        status="success" if result.get("ok") else "failed",
        duration_seconds=duration,
        subitem_data=result.get("subitem_data"),
    )
    db.add(log)

    # 同时写入 IndicatorExecution 表，使分析台页面可读取
    ind_obj = db.query(Indicator).filter(
        Indicator.id == indicator.id,
        Indicator.indicator_type == "core18"
    ).first()
    if ind_obj is None:
        ind_obj = db.query(Indicator).filter(
            Indicator.indicator_type == "core18",
            Indicator.name == indicator.name,
        ).first()
    if ind_obj is not None:
        exec_record = IndicatorExecution(
            indicator_id=ind_obj.id,
            indicator_name=indicator.name,
            kind="core18",
            run_mode="immediate",
            time_range="全量",
            result_type="ratio",
            calc_method="SQL录入",
            numerator_sql=result.get("numerator_sql", ""),
            denominator_sql=result.get("denominator_sql", ""),
            sql=result.get("sql", ""),
            numerator_count=result.get("numerator_count"),
            denominator_count=result.get("denominator_count"),
            count=result.get("count"),
            rate_percent=result.get("rate_percent"),
            rate_formula=result.get("rate_formula", ""),
            result_text=result.get("analysis", ""),
            preview_data={"columns": result.get("preview_columns", []), "rows": result.get("preview_rows", [])},
            denominator_preview_data={"columns": result.get("denominator_preview_columns", []), "rows": result.get("denominator_preview_rows", [])},
            error=result.get("error", ""),
            numerator_error=result.get("numerator_error", ""),
            denominator_error=result.get("denominator_error", ""),
            attempts=result.get("attempts", []),
            llm_thinking=result.get("numerator_llm_thinking", "") or result.get("llm_thinking", ""),
            llm_raw=result.get("numerator_llm_raw", "") or result.get("llm_raw", ""),
            cache_hit=result.get("cache_hit", False),
            request_id=result.get("request_id", ""),
            conversation_id=result.get("conversation_id", ""),
            status="success" if result.get("ok") else "failed",
            duration_seconds=duration,
            subitem_data=result.get("subitem_data"),
        )
        db.add(exec_record)

    if result.get("ok"):
        indicator.status = "success"
    db.commit()
    db.refresh(log)
    db.refresh(exec_record)
    return log
