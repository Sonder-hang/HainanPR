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
    PreviewPageRequest, PreviewPageResponse, ExecutionHistoryResponse,
    ExecuteTaskSubmitResponse, TaskStatusResponse,
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
            {"value": h.hospital_code or h.id, "label": h.name}
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
            # rows 已经是字典列表（使用 DictCursor），转换为 value/label 格式
            return [{"value": r.get("MDC_ORG_CD", ""), "label": r.get("MDC_ORG_NM", "")} for r in rows]
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
    - limit: 返回记录数上限（默认100，上限500）
    - offset: 跳过数量
    """
    q = db.query(IndicatorExecution)
    if indicator_id:
        q = q.filter(IndicatorExecution.indicator_id == indicator_id)
    if keyword:
        q = q.filter(IndicatorExecution.indicator_name.contains(keyword))
    if status and status != 'all':
        q = q.filter(IndicatorExecution.status == status)
    if kind:
        q = q.filter(IndicatorExecution.kind == kind)

    # 先计算总数
    total = q.count()

    if offset is None:
        offset = 0
    if limit is None:
        limit = 100
    limit = min(limit, 500)

    rows = q.order_by(IndicatorExecution.execution_time.desc()).offset(offset).limit(limit).all()
    return rows, total


@router.get("/execution/", response_model=ExecutionHistoryResponse)
def list_executions(
    indicator_id: Optional[int] = None,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    kind: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    db: Session = Depends(get_db),
):
    rows, total = _list_executions(indicator_id, keyword, status, kind, limit, offset, db)
    import logging
    _log = logging.getLogger("indicators")
    _log.info(f"[list_executions] query returned {len(rows)} rows, total={total}")
    for i, r in enumerate(rows):
        _log.debug(f"[list_executions] row[{i}] id={r.id} logs={type(r.logs).__name__} attempts={type(r.attempts).__name__} preview_data={type(r.preview_data).__name__} hospital_results={type(r.hospital_results).__name__}")
    records = []
    for r in rows:
        for field in ("rate_formula", "numerator_sql", "denominator_sql", "sql",
                      "result_text", "llm_thinking", "llm_raw", "error"):
            if getattr(r, field, None) is None:
                setattr(r, field, "")
        if r.logs is None:
            r.logs = []
        if r.attempts is None:
            r.attempts = []
        if r.preview_data is None:
            r.preview_data = {}
        if r.denominator_preview_data is None:
            r.denominator_preview_data = {}
        if r.hospital_codes is None:
            r.hospital_codes = []
        if r.hospital_results is None:
            r.hospital_results = []
        try:
            records.append(IndicatorExecutionResponse.model_validate(r).model_dump(mode='json'))
        except Exception:
            import logging
            import traceback
            _log = logging.getLogger("indicators")
            _log.error(
                f"[list_executions] serialize failed id={r.id} | "
                f"logs={type(r.logs).__name__}={repr(r.logs)[:200]} | "
                f"attempts={type(r.attempts).__name__}={repr(r.attempts)[:200]} | "
                f"preview_data={type(r.preview_data).__name__}={repr(r.preview_data)[:200]} | "
                f"hospital_results={type(r.hospital_results).__name__}={repr(r.hospital_results)[:200]} | "
                f"fields={ {f: type(getattr(r, f)).__name__ for f in ['logs','attempts','preview_data','denominator_preview_data','hospital_codes','hospital_results']} }"
            )
            _log.error(f"[list_executions] traceback:\n{traceback.format_exc()}")
    return {"records": records, "total": total}


@router.get("/execution", response_model=ExecutionHistoryResponse)
def list_executions_no_slash(
    indicator_id: Optional[int] = None,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    kind: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    db: Session = Depends(get_db),
):
    rows, total = _list_executions(indicator_id, keyword, status, kind, limit, offset, db)
    import logging
    _log = logging.getLogger("indicators")
    _log.info(f"[list_executions_no_slash] query returned {len(rows)} rows, total={total}")
    for i, r in enumerate(rows):
        _log.debug(f"[list_executions_no_slash] row[{i}] id={r.id} logs={type(r.logs).__name__} attempts={type(r.attempts).__name__} preview_data={type(r.preview_data).__name__} hospital_results={type(r.hospital_results).__name__}")
    records = []
    for r in rows:
        for field in ("rate_formula", "numerator_sql", "denominator_sql", "sql",
                      "result_text", "llm_thinking", "llm_raw", "error"):
            if getattr(r, field, None) is None:
                setattr(r, field, "")
        if r.logs is None:
            r.logs = []
        if r.attempts is None:
            r.attempts = []
        if r.preview_data is None:
            r.preview_data = {}
        if r.denominator_preview_data is None:
            r.denominator_preview_data = {}
        if r.hospital_codes is None:
            r.hospital_codes = []
        if r.hospital_results is None:
            r.hospital_results = []
        try:
            records.append(IndicatorExecutionResponse.model_validate(r).model_dump(mode='json'))
        except Exception:
            import traceback
            _log.error(
                f"[list_executions_no_slash] serialize failed id={r.id} | "
                f"logs={type(r.logs).__name__}={repr(r.logs)[:200]} | "
                f"attempts={type(r.attempts).__name__}={repr(r.attempts)[:200]} | "
                f"preview_data={type(r.preview_data).__name__}={repr(r.preview_data)[:200]} | "
                f"hospital_results={type(r.hospital_results).__name__}={repr(r.hospital_results)[:200]} | "
                f"fields={ {f: type(getattr(r, f)).__name__ for f in ['logs','attempts','preview_data','denominator_preview_data','hospital_codes','hospital_results']} }"
            )
            _log.error(f"[list_executions_no_slash] traceback:\n{traceback.format_exc()}")
    return {"records": records, "total": total}


@router.delete("/execution/{execution_id}", status_code=204)
def delete_execution(execution_id: int, db: Session = Depends(get_db)):
    row = db.query(IndicatorExecution).filter(IndicatorExecution.id == execution_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    db.delete(row)
    db.commit()


@router.get("/execution/by-hospital/", response_model=Optional[IndicatorExecutionResponse])
def get_execution_by_hospital(
    indicator_id: int,
    hospital_code: str,
    time_mode: Optional[str] = None,
    time_value: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    查询指定指标+医院下的最新一条 group_by_hospital=1 的执行记录。
    hospital_results 中包含该医院对应的执行结果。
    支持时间筛选：time_mode (monthly/quarterly) 和 time_value (如 2026-05 或 2026-Q1)
    """
    query = db.query(IndicatorExecution).filter(
        IndicatorExecution.indicator_id == indicator_id,
        IndicatorExecution.group_by_hospital == True,
        IndicatorExecution.status == "success",
    )

    if time_mode and time_mode != 'immediate':
        query = query.filter(IndicatorExecution.run_mode == time_mode)
        if time_value:
            query = query.filter(IndicatorExecution.time_value == time_value)

    all_execs = query.order_by(IndicatorExecution.execution_time.desc()).all()

    for exec in all_execs:
        codes = exec.hospital_codes or []
        if isinstance(codes, list) and hospital_code in codes:
            return exec
    return None


@router.post("/execute/", response_model=ExecuteTaskSubmitResponse)
def execute_indicator(data: ExecuteRequest, db: Session = Depends(get_db)):
    """
    异步执行指标。

    1. 先在数据库创建一条 pending 记录（让前端立即展示）
    2. 提交 Celery 异步任务
    3. 返回 task_id，前端轮询 /execution/task/{task_id} 获取结果
    """
    from app.tasks.indicator_tasks import execute_indicator_task
    from datetime import datetime

    req_dict = data.model_dump()
    indicator_name = ""
    kind = data.business_type or "core18"

    # 查询指标名称
    if data.indicator_id:
        indicator = db.query(Indicator).filter(Indicator.id == data.indicator_id).first()
        if not indicator:
            raise HTTPException(status_code=404, detail="指标不存在")
        indicator_name = indicator.name
        ind_data = _obj_to_dict(indicator)
        ind_data.update({
            "kind": kind,
            "run_mode": data.run_mode or "immediate",
            "time_range": data.time_range or "全量",
            "result_type": data.result_type or "ratio",
            "calc_method": data.calc_method or "SQL录入",
            "hospital_codes": data.hospital_codes,
            "time_mode": data.time_mode,
            "time_value": data.time_value,
            "date_field": data.date_field or (indicator.date_field if indicator else "discharge"),
            "numerator_date_field": data.numerator_date_field or (indicator.numerator_date_field if indicator else "discharge"),
            "denominator_date_field": data.denominator_date_field or (indicator.denominator_date_field if indicator else "discharge"),
            "group_by_hospital": data.group_by_hospital if data.group_by_hospital is not None else True,
        })
    else:
        ind_data = {"id": None, **req_dict}

    # 预先创建 pending 记录，确保前端能查到
    exec_record = IndicatorExecution(
        indicator_id=data.indicator_id,
        indicator_name=indicator_name,
        kind=kind,
        run_mode=data.run_mode or "immediate",
        time_range=data.time_range or "全量",
        result_type=data.result_type or "ratio",
        calc_method=data.calc_method or "SQL录入",
        scope="",
        hospital_codes=data.hospital_codes,
        time_mode=data.time_mode,
        time_value=data.time_value,
        date_field=data.date_field or "discharge",
        group_by_hospital=data.group_by_hospital if data.group_by_hospital is not None else True,
        status="pending",
        execution_time=datetime.now(),
    )
    db.add(exec_record)
    db.commit()
    db.refresh(exec_record)

    # 提交 Celery 异步任务（传入 execution_id 以便更新预创建的记录）
    task = execute_indicator_task.delay(ind_data, execution_id=exec_record.id)

    logger.info(f"[Execute] 任务已提交 task_id={task.id}, execution_id={exec_record.id}")

    return ExecuteTaskSubmitResponse(
        task_id=task.id,
        execution_id=exec_record.id,
    )


@router.get("/execution/task/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str):
    """
    查询 Celery 任务状态和执行结果。
    前端轮询此接口直到 state 变为 SUCCESS 或 FAILURE。
    """
    from app.celery_app import celery_app

    res = celery_app.AsyncResult(task_id)
    state = res.state.upper()

    execution_id = None
    result_data = None

    if state == "SUCCESS":
        raw = res.result
        if isinstance(raw, int):
            execution_id = raw
            result_data = {"execution_id": raw}
        elif isinstance(raw, dict):
            execution_id = raw.get("execution_id")
            result_data = raw
        else:
            result_data = {"raw": str(raw)}
    elif state == "FAILURE":
        result_data = {"error": str(res.result)}

    return TaskStatusResponse(
        task_id=task_id,
        state=state,
        ready=res.ready(),
        result=result_data,
        execution_id=execution_id,
    )


@router.get("/execution/{execution_id}/detail", response_model=IndicatorExecutionResponse)
def get_execution_detail(execution_id: int, db: Session = Depends(get_db)):
    """
    根据执行记录 ID 获取完整结果。
    前端在任务完成后调用此接口拉取结果详情。
    """
    row = db.query(IndicatorExecution).filter(IndicatorExecution.id == execution_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    # FastAPI response_model 严格校验：None 值须转为空字符串以匹配 schema
    for field in ("rate_formula", "numerator_sql", "denominator_sql", "sql",
                  "result_text", "llm_thinking", "llm_raw"):
        if getattr(row, field, None) is None:
            setattr(row, field, "")
    if row.logs is None:
        row.logs = []
    if row.attempts is None:
        row.attempts = []
    if row.preview_data is None:
        row.preview_data = {}
    if row.denominator_preview_data is None:
        row.denominator_preview_data = {}
    if row.hospital_codes is None:
        row.hospital_codes = []
    if row.hospital_results is None:
        row.hospital_results = []
    if row.error is None:
        row.error = ""
    return row


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
    """根据执行记录 ID 获取指定页的预览数据（分子/分母），支持翻页和按医院筛选"""
    service = Text2SQLService()
    result = service.fetch_preview_page(
        execution_id=data.execution_id,
        target=data.target,
        page=data.page,
        page_size=data.page_size,
        db_session=db,
        hospital_code=data.hospital_code,
    )
    return result
