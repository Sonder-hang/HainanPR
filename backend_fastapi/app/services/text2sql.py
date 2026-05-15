"""Text-to-SQL 服务集成层"""
import httpx
import logging
from typing import Any, Dict, Optional
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


class Text2SQLService:
    def __init__(self):
        from app.config import settings
        self.base_url = settings.TEXT2SQL_BACKEND_URL.rstrip("/")
        self.timeout = httpx.Timeout(300.0, connect=10.0)
        self.client = httpx.Client(timeout=self.timeout)

    def _make_url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def health_check(self) -> Dict[str, Any]:
        try:
            resp = self.client.get(self._make_url("/api/health"))
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return {"ok": False, "error": str(e)}

    def get_indicators(self) -> Dict[str, Any]:
        try:
            resp = self.client.get(self._make_url("/api/indicators"))
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"indicators": [], "error": str(e)}

    def get_tables_list(self) -> Dict[str, Any]:
        try:
            resp = self.client.get(self._make_url("/api/tables_list"))
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"tables": [], "error": str(e)}

    def get_column_meanings(self) -> Dict[str, Any]:
        try:
            resp = self.client.get(self._make_url("/api/column_meanings"))
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"meanings": {}, "error": str(e)}

    def prompt_preview(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            resp = self.client.post(self._make_url("/api/prompt_preview"), json=data)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"system_prompt": "", "user_message": "", "error": str(e)}

    def _resolve_indicator_type(self, business_type: Optional[str], calc_type: Optional[str]) -> Optional[str]:
        if business_type == "core18":
            return "统计型" if calc_type == "count" else "分子分母比值型"
        if business_type == "four":
            return "分子分母比值型"
        if business_type:
            return "分子分母比值型"
        return None

    def execute_indicator(self, indicator_data: Dict[str, Any], db_session=None) -> Dict[str, Any]:
        """优先直接执行已保存的 SQL（不走 LLM）；若无保存 SQL 才调用 text2sql 服务生成。"""
        import time
        start_time = time.time()

        # 提取保存的 SQL
        numerator_sql = indicator_data.get("numerator_sql") or indicator_data.get("numerator_sql") or ""
        denominator_sql = indicator_data.get("denominator_sql") or indicator_data.get("denominator_sql") or ""
        single_sql = indicator_data.get("sql") or indicator_data.get("sql_content") or ""
        ind_type = indicator_data.get("indicator_type") or indicator_data.get("类型") or ""

        def _exec_sql(sql: str, include_rows: bool = True, fetch_all: bool = False):
            if not (sql and sql.strip()):
                return None, "SQL 为空", [], []
            runner_path = Path(__file__).parent.parent.parent / "Hainan_SQL-main" / "text2sql_app" / "sql_runner.py"
            if runner_path.exists():
                sys.path.insert(0, str(runner_path.parent))
                try:
                    if fetch_all:
                        from sql_runner import execute_full
                        cols, rows, err = execute_full(sql)
                        return len(rows), err, cols, rows
                    elif include_rows:
                        from sql_runner import execute_count, execute_limited
                        cnt, cnt_err = execute_count(sql)
                        if cnt_err or cnt is None:
                            return None, cnt_err or "计数失败", [], []
                        cols, rows, prev_err = execute_limited(sql, limit=50)
                        return cnt, prev_err, cols, rows
                    else:
                        from sql_runner import execute_count
                        cnt, err = execute_count(sql)
                        return cnt, err, [], []
                except Exception as e:
                    return None, str(e), [], []
                finally:
                    if str(runner_path.parent) in sys.path:
                        sys.path.remove(str(runner_path.parent))
            result = self.test_sql(sql, limit=10000)
            return result.get("count"), result.get("error"), [], []

        # 提取新增字段（来自 ExecuteRequest 或指标对象）
        kind = indicator_data.get("kind") or indicator_data.get("business_type") or "core18"
        run_mode = indicator_data.get("run_mode") or "immediate"
        time_range = indicator_data.get("time_range") or "全量"
        result_type = indicator_data.get("result_type") or "ratio"
        calc_method = indicator_data.get("calc_method") or "SQL录入"
        indicator_name = indicator_data.get("name") or indicator_data.get("indicator_name") or ""

        def _to_serializable_rows(rows: list) -> list:
            """将 rows 中的 Decimal/非 JSON 类型转为可序列化类型"""
            result = []
            for row in rows:
                clean = {}
                for k, v in row.items():
                    if hasattr(v, '__float__') and not isinstance(v, (int, str, bool, type(None))):
                        clean[k] = float(v)
                    else:
                        clean[k] = v
                result.append(clean)
            return result

        def _save(result: Dict) -> None:
            """统一保存执行记录到数据库"""
            if not db_session:
                return
            try:
                from app.models.indicator import IndicatorExecution
                indicator_id = indicator_data.get("indicator_id") or indicator_data.get("id")
                if indicator_id:
                    db_session.add(IndicatorExecution(
                        indicator_id=indicator_id,
                        indicator_name=indicator_name,
                        kind=kind,
                        run_mode=run_mode,
                        time_range=time_range,
                        result_type=result_type,
                        calc_method=calc_method,
                        scope=indicator_data.get("scope", ""),
                        numerator_sql=result.get("numerator_sql", ""),
                        denominator_sql=result.get("denominator_sql", ""),
                        sql=result.get("sql", ""),
                        numerator_count=result.get("numerator_count"),
                        denominator_count=result.get("denominator_count"),
                        rate_percent=result.get("rate_percent"),
                        rate_formula=result.get("rate_formula", ""),
                        result_text=result.get("analysis", ""),
                        preview_data={"columns": result.get("preview_columns", []), "rows": _to_serializable_rows(result.get("preview_rows", []))},
                        denominator_preview_data={"columns": result.get("denominator_preview_columns", []), "rows": _to_serializable_rows(result.get("denominator_preview_rows", []))},
                        error=result.get("error", ""),
                        attempts=result.get("numerator_attempts", []) or result.get("attempts", []),
                        llm_thinking=result.get("numerator_llm_thinking", "") or result.get("llm_thinking", ""),
                        llm_raw=result.get("numerator_llm_raw", "") or result.get("llm_raw", ""),
                        cache_hit=result.get("cache_hit", False),
                        request_id=result.get("request_id", ""),
                        conversation_id=result.get("conversation_id", ""),
                        status="success" if result.get("ok") else "failed",
                        logs=result.get("logs", []),
                        duration_seconds=result.get("duration_seconds"),
                    ))
                    db_session.commit()
            except Exception as e:
                logger.error(f"保存执行记录失败: {e}")
                db_session.rollback()

        # --- 有已保存 SQL，直接执行 ---
        if numerator_sql and denominator_sql:
            # 比值型需要同时获取分子和分母的预览数据
            num_cnt, num_err, num_cols, num_rows = _exec_sql(numerator_sql)
            den_cnt, den_err, den_cols, den_rows = _exec_sql(denominator_sql)
            rate = round(num_cnt * 100.0 / den_cnt, 4) if (den_cnt and num_cnt is not None and den_cnt != 0) else None
            ok = num_err is None and den_err is None and num_cnt is not None and den_cnt is not None
            duration = round(time.time() - start_time, 3)
            logs = []
            if ok:
                logs = [
                    {"time": time.strftime("%H:%M:%S"), "level": "info", "message": "执行分子 SQL..."},
                    {"time": time.strftime("%H:%M:%S"), "level": "info", "message": f"分子结果：{num_cnt} 条记录。"},
                    {"time": time.strftime("%H:%M:%S"), "level": "info", "message": "执行分母 SQL..."},
                    {"time": time.strftime("%H:%M:%S"), "level": "info", "message": f"分母结果：{den_cnt} 条记录。"},
                    {"time": time.strftime("%H:%M:%S"), "level": "info", "message": f"执行完成。指标值：{rate}%（{num_cnt}/{den_cnt}）"},
                ]
            else:
                logs = [
                    {"time": time.strftime("%H:%M:%S"), "level": "info", "message": "执行分子 SQL..."},
                    {"time": time.strftime("%H:%M:%S"), "level": "info", "message": f"分子结果：{num_cnt} 条记录。" if num_cnt is not None else f"分子执行出错：{num_err}"},
                    {"time": time.strftime("%H:%M:%S"), "level": "info", "message": "执行分母 SQL..."},
                    {"time": time.strftime("%H:%M:%S"), "level": "info", "message": f"分母结果：{den_cnt} 条记录。" if den_cnt is not None else f"分母执行出错：{den_err}"},
                    {"time": time.strftime("%H:%M:%S"), "level": "error", "message": f"执行失败：{num_err or den_err}"},
                ]
            result = {
                "ok": ok,
                "indicator_type": ind_type,
                "numerator_sql": numerator_sql,
                "denominator_sql": denominator_sql,
                "numerator_count": num_cnt,
                "denominator_count": den_cnt,
                "rate_percent": rate,
                "rate_formula": f"{num_cnt}/{den_cnt}={rate}%" if rate is not None else None,
                "error": num_err or den_err or None,
                "numerator_error": num_err,
                "denominator_error": den_err,
                "preview_columns": num_cols,
                "preview_rows": _to_serializable_rows(num_rows),
                "preview_data": {"columns": num_cols, "rows": _to_serializable_rows(num_rows)},
                "denominator_preview_columns": den_cols,
                "denominator_preview_rows": _to_serializable_rows(den_rows),
                "denominator_preview_data": {"columns": den_cols, "rows": _to_serializable_rows(den_rows)},
                "numerator_attempts": [{"attempt": 1, "sql": numerator_sql, "count": num_cnt, "error": num_err}],
                "denominator_attempts": [{"attempt": 1, "sql": denominator_sql, "count": den_cnt, "error": den_err}],
                "request_id": "",
                "conversation_id": "",
                "cache_hit": False,
                "logs": logs,
                "duration_seconds": duration,
            }
            _save(result)
            return result

        if single_sql:
            cnt, err, cols, rows = _exec_sql(single_sql)
            calc_type = indicator_data.get("calc_type") or "ratio"
            duration = round(time.time() - start_time, 3)

            # 统计型指标：如果结果有 patient_cnt 列，加和得到最终指标值
            stat_count = cnt
            if cols and rows and "patient_cnt" in cols:
                total = sum(float(r.get("patient_cnt") or 0) for r in rows)
                stat_count = int(total)

            logs = []
            if err is None and cnt is not None:
                logs = [
                    {"time": time.strftime("%H:%M:%S"), "level": "info", "message": "执行 SQL..."},
                    {"time": time.strftime("%H:%M:%S"), "level": "info", "message": f"查询结果：{cnt} 条记录。"},
                    {"time": time.strftime("%H:%M:%S"), "level": "info", "message": f"执行完成，共 {stat_count} 人次。"},
                ]
            else:
                logs = [
                    {"time": time.strftime("%H:%M:%S"), "level": "info", "message": "执行 SQL..."},
                    {"time": time.strftime("%H:%M:%S"), "level": "error", "message": f"执行失败：{err}"},
                ]
            result = {
                "ok": err is None and cnt is not None,
                "indicator_type": ind_type,
                "indicator": {"calc_type": calc_type},
                "calc_type": calc_type,
                "sql": single_sql,
                "count": stat_count,
                "error": err,
                "preview_columns": cols,
                "preview_rows": _to_serializable_rows(rows),
                "preview_data": {"columns": cols, "rows": _to_serializable_rows(rows)},
                "attempts": [{"attempt": 1, "sql": single_sql, "count": stat_count, "error": err}],
                "request_id": "",
                "conversation_id": "",
                "cache_hit": False,
                "logs": logs,
                "duration_seconds": duration,
            }
            _save(result)
            return result

        # --- 无保存 SQL，走 text2sql 服务生成 ---
        try:
            request_data = {
                "indicator_index": indicator_data.get("indicator_index") or indicator_data.get("id"),
                "indicator_name": indicator_data.get("indicator_name") or indicator_data.get("name", ""),
                "selected_tables": indicator_data.get("selected_tables") or indicator_data.get("involved_tables", []),
                "indicator_formula": indicator_data.get("indicator_formula") or indicator_data.get("formula") or indicator_data.get("rule_logic", ""),
                "numerator_desc": indicator_data.get("numerator_desc", ""),
                "denominator_desc": indicator_data.get("denominator_desc", ""),
                "indicator_desc": indicator_data.get("indicator_desc") or indicator_data.get("description", ""),
            }
            indicator_type = self._resolve_indicator_type(
                indicator_data.get("business_type"),
                indicator_data.get("calc_type"),
            )
            if indicator_type:
                request_data["indicator_type"] = indicator_type
            if indicator_data.get("mode"):
                request_data["mode"] = indicator_data["mode"]
            if indicator_data.get("prompt_modified") is not None:
                request_data["prompt_modified"] = indicator_data["prompt_modified"]
            if indicator_data.get("conversation_id"):
                request_data["conversation_id"] = indicator_data["conversation_id"]
            if indicator_data.get("conversation_history"):
                request_data["conversation_history"] = indicator_data["conversation_history"]
            if indicator_data.get("regenerate"):
                request_data["regenerate"] = indicator_data["regenerate"]

            resp = self.client.post(self._make_url("/api/run"), json=request_data)
            resp.raise_for_status()
            result = resp.json()
            result["duration_seconds"] = round(time.time() - start_time, 3)
            # 确保返回字段包含 preview_data（兼容前端）
            if "preview_data" not in result:
                result["preview_data"] = {
                    "columns": result.get("preview_columns", []),
                    "rows": result.get("preview_rows", []),
                }
            _save(result)
            return result
        except httpx.HTTPError as e:
            logger.error(f"执行指标失败 (HTTP): {e}")
            return {"ok": False, "error": f"HTTP错误: {str(e)}", "indicator_type": indicator_data.get("indicator_type", "unknown")}
        except Exception as e:
            logger.error(f"执行指标失败: {e}")
            return {"ok": False, "error": str(e), "indicator_type": indicator_data.get("indicator_type", "unknown")}

    def test_sql(self, sql: str, limit: int = 200) -> Dict[str, Any]:
        try:
            resp = self.client.post(self._make_url("/api/test_sql"), json={"sql": sql, "limit": limit})
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"ok": False, "columns": [], "rows": [], "count": None, "error": str(e)}

    def refresh_tables(self) -> Dict[str, Any]:
        try:
            resp = self.client.post(self._make_url("/api/refresh_tables"))
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def sync_indicator(self, indicator_data: Dict[str, Any]) -> Dict[str, Any]:
        """将指标同步到 text2sql 服务的 指标.json"""
        try:
            payload = {
                "指标名": indicator_data.get("name", ""),
                "类型": "分子分母比值型",
                "指标计算公式": indicator_data.get("formula", "") or indicator_data.get("indicator_formula", ""),
                "分子描述": indicator_data.get("numerator_desc", "") or indicator_data.get("numerator", ""),
                "分母描述": indicator_data.get("denominator_desc", "") or indicator_data.get("denominator", ""),
                "指标描述": indicator_data.get("description", "") or "",
                "涉及到表": indicator_data.get("involved_tables", []) or indicator_data.get("selected_tables", []),
                "numerator_sql": indicator_data.get("numerator_sql", ""),
                "denominator_sql": indicator_data.get("denominator_sql", ""),
                "sql": indicator_data.get("sql", ""),
            }
            resp = self.client.post(self._make_url("/api/indicators/add"), json=payload)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"同步指标到 text2sql 失败: {e}")
            return {"ok": False, "error": str(e)}

