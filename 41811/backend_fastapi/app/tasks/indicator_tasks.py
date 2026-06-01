"""指标执行异步任务"""
import logging
from celery import Task
from app.celery_app import celery_app
from app.services.text2sql import Text2SQLService

logger = logging.getLogger(__name__)


class IndicatorTask(Task):
    """指标执行任务基类"""
    _service = None

    @property
    def service(self):
        if self._service is None:
            self._service = Text2SQLService()
        return self._service

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        pass


def _to_serializable_rows(rows: list) -> list:
    result = []
    for row in rows:
        clean = {}
        for k, v in row.items():
            if hasattr(v, 'strftime'):
                clean[k] = v.strftime("%Y-%m-%d %H:%M:%S")
            elif hasattr(v, '__float__') and not isinstance(v, (int, str, bool, type(None))):
                clean[k] = float(v)
            else:
                clean[k] = v
        result.append(clean)
    return result


def _to_serializable_logs(logs: list) -> list:
    result = []
    for log in logs:
        clean = {}
        for k, v in log.items():
            if hasattr(v, 'strftime'):
                clean[k] = v.strftime("%H:%M:%S")
            elif hasattr(v, '__float__') and not isinstance(v, (int, str, bool, type(None))):
                clean[k] = float(v)
            else:
                clean[k] = v
        result.append(clean)
    return result


def _to_serializable_any(obj):
    if hasattr(obj, 'strftime'):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    elif hasattr(obj, '__float__') and not isinstance(obj, (int, str, bool, type(None), list, dict)):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: _to_serializable_any(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_to_serializable_any(item) for item in obj]
    return obj


@celery_app.task(
    bind=True,
    base=IndicatorTask,
    name="indicator.execute",
    max_retries=0,
)
def execute_indicator_task(self, indicator_data: dict, execution_id: int = None):
    """
    异步执行指标，完成后更新预创建的执行记录。

    Args:
        indicator_data: 指标配置数据
        execution_id: 预先创建的 pending 记录 ID（由 /execute/ 接口传入）
    """
    from app.database import SessionLocal
    from app.models.indicator import IndicatorExecution
    from datetime import datetime

    db = None
    try:
        db = SessionLocal()

        # 强制从数据库读取最新时间字段（indicator_data 可能被 Redis 缓存旧值）
        indicator_id = indicator_data.get("indicator_id") or indicator_data.get("id")
        if indicator_id:
            from app.models.indicator import Indicator
            ind = db.query(Indicator).filter(Indicator.id == indicator_id).first()
            if ind:
                if ind.date_field:
                    indicator_data["date_field"] = ind.date_field
                if getattr(ind, "numerator_date_field", None):
                    indicator_data["numerator_date_field"] = ind.numerator_date_field
                if getattr(ind, "denominator_date_field", None):
                    indicator_data["denominator_date_field"] = ind.denominator_date_field

        # 执行指标计算（skip_save=True，由本任务负责更新预创建的记录）
        result = self.service.execute_indicator(
            indicator_data=indicator_data,
            db_session=db,
            skip_save=True,
        )

        # 更新预创建的执行记录
        if execution_id:
            record = db.query(IndicatorExecution).filter(IndicatorExecution.id == execution_id).first()
            if record:
                ok = result.get("ok", False) if isinstance(result, dict) else False
                record.status = "success" if ok else "failed"
                record.error = result.get("error", "") if isinstance(result, dict) else ""
                record.numerator_sql = result.get("numerator_sql", "") if isinstance(result, dict) else ""
                record.denominator_sql = result.get("denominator_sql", "") if isinstance(result, dict) else ""
                record.sql = result.get("sql", "") if isinstance(result, dict) else ""
                record.numerator_count = result.get("numerator_count")
                record.denominator_count = result.get("denominator_count")
                record.count = result.get("count")
                record.rate_percent = result.get("rate_percent")
                record.rate_formula = result.get("rate_formula", "") if isinstance(result, dict) else ""
                record.result_text = result.get("analysis", "") if isinstance(result, dict) else ""

                r = result if isinstance(result, dict) else {}
                record.preview_data = {
                    "columns": r.get("preview_columns", []),
                    "rows": _to_serializable_rows(r.get("preview_rows", []))
                }
                record.denominator_preview_data = {
                    "columns": r.get("denominator_preview_columns", []),
                    "rows": _to_serializable_rows(r.get("denominator_preview_rows", []))
                }
                record.attempts = _to_serializable_any(
                    r.get("numerator_attempts", []) or r.get("attempts", [])
                )
                record.llm_thinking = r.get("numerator_llm_thinking", "") or r.get("llm_thinking", "")
                record.llm_raw = r.get("numerator_llm_raw", "") or r.get("llm_raw", "")
                record.cache_hit = r.get("cache_hit", False)
                record.request_id = r.get("request_id", "")
                record.conversation_id = r.get("conversation_id", "")
                record.duration_seconds = r.get("duration_seconds")
                record.group_by_hospital = r.get("group_by_hospital", False)
                record.hospital_results = r.get("hospital_results", [])
                record.subitem_data = r.get("subitem_data")
                record.logs = _to_serializable_logs(r.get("logs", []))

                db.commit()
                logger.info(f"[CeleryTask] 更新执行记录 {execution_id} 完成，状态={record.status}")
                return {"execution_id": execution_id, "ok": ok}

        # 无 execution_id 时返回结果数据（降级兼容）
        return result

    except Exception as e:
        logger.error(f"[CeleryTask] execute_indicator failed: {e}", exc_info=True)
        if db and execution_id:
            try:
                record = db.query(IndicatorExecution).filter(IndicatorExecution.id == execution_id).first()
                if record:
                    record.status = "failed"
                    record.error = str(e)
                    record.logs = [{"time": datetime.now().strftime("%H:%M:%S"), "level": "error", "message": str(e)}]
                    db.commit()
                    return {"execution_id": execution_id, "error": str(e)}
            except Exception as inner_e:
                logger.error(f"[CeleryTask] 更新失败记录异常: {inner_e}")
        return {"error": str(e)}
    finally:
        if db:
            db.close()
