"""Text-to-SQL 服务集成层"""
import httpx
import logging
from typing import Any, Dict, Optional, Union
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


class Text2SQLService:
    def __init__(self):
        from app.config import settings
        self.base_url = settings.TEXT2SQL_BACKEND_URL.rstrip("/")
        self.timeout = httpx.Timeout(300.0, connect=10.0)
        transport = httpx.HTTPTransport(local_address="127.0.0.1")
        self.client = httpx.Client(
            timeout=self.timeout,
            transport=transport,
        )

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
            return "统计型" if calc_type == "count" else "分子分母比值型"
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
            # 标准化：MySQL 列名大小写不敏感，但已知 LLM 生成的 SQL 大写列名与实际 DB 不匹配
            # 将大写列名（不在引号内）替换为小写
            import re
            known_cols = [
                "DSCG_DT_TM", "ADMN_DT_TM", "PRM_KEY", "MDC_ORG_CD", "MDC_ORG_NM",
                "ADMN_MDC_HTR_RCD_NO", "INHOS_NO", "PTT_NM", "CHF_COMPLNT",
                "PST_ILLNS_HST", "DSES_HST", "ODNR_HLTH_CDT_CD", "ADMN_DT_TM",
                "OPRT_SQNC_NO", "OPRT_CD", "OPRT_NM", "OPRT_DT", "PLN_IMPLMT_OPRT_CD",
                "PLN_IMPLMT_OPRT_NM", "DIAG_CD", "DIAG_NM", "MAIN_DIAG_FLG",
                "MDC_RCD_NO", "INHOS_TMS", "GDR_CD", "GDR_NM", "BTH_DT", "AGE",
                "AGE_UNT", "NATN_CD", "NATN_NM", "HLTH_CRD_NO", "MDC_PAY_WAY_CD",
                "MDC_PAY_WAY_NM", "INHOS_MDC_TP_CD", "INHOS_MDC_TP_NM", "NM",
                "ID_CRD_NO", "DTH_DT_TM", "DSCG_WAY_CD", "DSCG_WAY_NM",
                "TNOVR_CDT_CD", "TNOVR_CDT_NM", "INVLD_FLG", "OPRT_TP_CD",
                "OPRT_TP_NM", "DAY31_DSCG_AGN_INHOS_FLG", "MDC_RCD_NO",
            ]
            for col in known_cols:
                sql = re.sub(r'(?<![`"\w])' + col + r'(?![`"\w])', col.lower(), sql)
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
            """将 rows 中的 Decimal/datetime 等非 JSON 类型转为可序列化类型"""
            result = []
            for row in rows:
                clean = {}
                for k, v in row.items():
                    if hasattr(v, 'strftime'):  # datetime 对象
                        clean[k] = v.strftime("%Y-%m-%d %H:%M:%S")
                    elif hasattr(v, '__float__') and not isinstance(v, (int, str, bool, type(None))):
                        clean[k] = float(v)
                    else:
                        clean[k] = v
                result.append(clean)
            return result

        def _to_serializable_logs(logs: list) -> list:
            """将 logs 中的 datetime/Decimal 类型转为可序列化类型"""
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
            """将任意对象（dict/list/datetime/Decimal）递归转为 JSON 可序列化类型"""
            if hasattr(obj, 'strftime'):
                return obj.strftime("%Y-%m-%d %H:%M:%S")
            elif hasattr(obj, '__float__') and not isinstance(obj, (int, str, bool, type(None), list, dict)):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: _to_serializable_any(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_to_serializable_any(item) for item in obj]
            return obj

        def _save(result: Dict) -> Optional[int]:
            """统一保存执行记录到数据库，返回记录ID"""
            if not db_session:
                return None
            try:
                from datetime import datetime
                from app.models.indicator import IndicatorExecution
                indicator_id = indicator_data.get("indicator_id") or indicator_data.get("id")
                exec_record = IndicatorExecution(
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
                        count=result.get("count"),
                        rate_percent=result.get("rate_percent"),
                        rate_formula=result.get("rate_formula", ""),
                        result_text=result.get("analysis", ""),
                        preview_data={"columns": result.get("preview_columns", []), "rows": _to_serializable_rows(result.get("preview_rows", []))},
                        denominator_preview_data={"columns": result.get("denominator_preview_columns", []), "rows": _to_serializable_rows(result.get("denominator_preview_rows", []))},
                        error=result.get("error", ""),
                        attempts=_to_serializable_any(result.get("numerator_attempts", []) or result.get("attempts", [])),
                        llm_thinking=result.get("numerator_llm_thinking", "") or result.get("llm_thinking", ""),
                        llm_raw=result.get("numerator_llm_raw", "") or result.get("llm_raw", ""),
                        cache_hit=result.get("cache_hit", False),
                        request_id=result.get("request_id", ""),
                        conversation_id=result.get("conversation_id", ""),
                        status="success" if result.get("ok") else "failed",
                        logs=_to_serializable_logs(result.get("logs", [])),
                        duration_seconds=result.get("duration_seconds"),
                        execution_time=datetime.now(),
                        # 批量执行相关字段
                        hospital_codes=indicator_data.get("hospital_codes"),
                        time_mode=indicator_data.get("time_mode"),
                        time_value=indicator_data.get("time_value"),
                        date_field=indicator_data.get("date_field"),
                        group_by_hospital=result.get("group_by_hospital", False),
                        hospital_results=result.get("hospital_results", []),
                    )
                db_session.add(exec_record)
                db_session.commit()
                db_session.refresh(exec_record)
                return exec_record.id
            except Exception as e:
                logger.error(f"保存执行记录失败: {e}")
                db_session.rollback()
                return None

        def _inject_hospital_filter(sql: str, hospital_codes: list = None) -> str:
            """向 SQL 注入医院筛选条件 - 识别子查询并正确注入"""
            if not sql or not hospital_codes:
                logger.info(f"[医院过滤] SQL或hospital_codes为空，跳过过滤 - sql_exists={bool(sql)}, codes={hospital_codes}")
                return sql
            
            import re
            
            codes_str = "','".join(hospital_codes)
            
            sql_clean = sql.strip().rstrip(';').strip()
            
            # 找主表别名 (跳过子查询内的 FROM/JOIN)
            table_aliases = set()
            # 排除关键字
            keywords = {'SELECT', 'WHERE', 'AND', 'OR', 'ON', 'AS', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'JOIN', 'FROM'}
            # 先找 AS 别名
            for m in re.finditer(r'(?:FROM|JOIN)\s+(\w+)\s+AS\s+(\w+)', sql_clean, re.IGNORECASE):
                alias = m.group(2)
                if alias.upper() not in keywords:
                    table_aliases.add(alias)
            # 再找隐式别名 (FROM table alias 或 JOIN table alias)
            # 关键：确保别名后面有空白或结束，而不是紧跟 WHERE
            for m in re.finditer(r'(?:FROM|JOIN)\s+(\w+)\s+(\w+)\b', sql_clean, re.IGNORECASE):
                alias = m.group(2)
                if alias.upper() not in keywords:
                    table_aliases.add(alias)
            
            main_alias = list(table_aliases)[0] if table_aliases else None
            
            # 检查外层 SELECT 是否已经有无别名的 MDC_ORG_CD 字段
            # 移除注释后检查
            outer_select_match = re.search(r'\bSELECT\s+(.*?)\s+FROM\s*\(', sql_clean, re.IGNORECASE | re.DOTALL)
            has_outer_mdc_org = False
            if outer_select_match:
                outer_cols_raw = outer_select_match.group(1)
                # 移除行内注释和块注释
                outer_cols = re.sub(r'--[^\n]*', '', outer_cols_raw)
                outer_cols = re.sub(r'/\*.*?\*/', '', outer_cols, flags=re.DOTALL)
                # 检查是否有不带表别名的 MDC_ORG_CD 列
                # 例如: "MDC_ORG_CD," 或 "MDC_ORG_CD\n" 或 "(MDC_ORG_CD" 等
                if re.search(r'(?<!\w\.)\bMDC_ORG_CD\b(?!\s*=)', outer_cols):
                    has_outer_mdc_org = True
            
            if has_outer_mdc_org:
                hospital_filter = f" AND MDC_ORG_CD IN ('{codes_str}')"
            elif main_alias:
                hospital_filter = f" AND {main_alias}.MDC_ORG_CD IN ('{codes_str}')"
            else:
                hospital_filter = f" AND MDC_ORG_CD IN ('{codes_str}')"
            
            logger.info(f"[医院过滤] 表别名/表名: {table_aliases}, 使用: {main_alias}, 外层有MDC: {has_outer_mdc_org}")
            
            # 找到最外层的 WHERE
            outer_pattern = r'\)\s+(?:AS\s+)?\w+\s+WHERE\b'
            all_matches = list(re.finditer(outer_pattern, sql_clean, re.IGNORECASE | re.DOTALL))
            
            # 找到主 FROM 子句开始的位置
            main_from_pos = sql_clean.upper().find('FROM')
            
            # 从后往前找最近的外层 WHERE
            outer_where_pos = -1
            for m in reversed(all_matches):
                paren_pos = m.start()
                if paren_pos >= main_from_pos:
                    outer_where_pos = m.start()
                    break
            
            if outer_where_pos >= 0:
                # 找到 WHERE 关键字位置
                where_start = outer_where_pos + sql_clean[outer_where_pos:].upper().find('WHERE')
                after_where_raw = sql_clean[where_start + 5:]
                after_where = after_where_raw.strip()
                
                clause_match = re.search(r'\b(ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|UNION)\b', after_where, re.IGNORECASE)
                
                if clause_match:
                    insert_pos = where_start + 5 + clause_match.start()
                    new_sql = sql_clean[:insert_pos] + hospital_filter + " " + after_where
                else:
                    new_sql = sql_clean[:where_start + 5] + after_where_raw + hospital_filter
                logger.info(f"[医院过滤] 在外层WHERE后注入")
            else:
                # 没有子查询，在 ORDER BY 等关键字前追加
                clause_pattern = r'\b(ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|UNION\b)'
                match = re.search(clause_pattern, sql_clean, re.IGNORECASE)
                
                if match:
                    before = sql_clean[:match.start()].rstrip().rstrip(';').strip()
                    after = sql_clean[match.start():]
                    if before.upper().endswith(('AND', 'OR')):
                        before = before[:-3].strip()
                    new_sql = before + " " + hospital_filter + " " + after
                else:
                    sql_clean = sql_clean.rstrip().rstrip(';').strip()
                    if sql_clean.upper().endswith(('AND', 'OR')):
                        sql_clean = sql_clean[:-3].strip()
                    new_sql = sql_clean + " " + hospital_filter
                logger.info(f"[医院过滤] 无子查询，在ORDER BY前追加")
            
            logger.info(f"[医院过滤] 过滤后SQL: {new_sql[:300]}...")
            return new_sql

        def _inject_time_filter(sql: str, time_mode: str = None, time_value: str = None, date_field: str = "discharge") -> str:
            """向 SQL 注入时间筛选条件 - 在外层 WHERE 之后追加"""
            if not sql or not time_mode or not time_value:
                return sql

            import re

            sql_clean = sql.strip().rstrip(';').strip()

            # 尝试从 SQL 中提取实际存在的时间字段
            # 不同表使用的日期字段：dscg_dt_tm(出院), admn_dt_tm(入院), vst_dt_tm(就诊), rsc_dt_tm(抢救), oprt_dt_tm(手术)
            possible_date_fields = [
                "dscg_dt_tm", "admn_dt_tm", "vst_dt_tm", "rsc_dt_tm", "oprt_dt_tm",
                "dth_dt_tm", "odr_opn_dt_tm", "dscs_dt_tm",
            ]
            found_field = None
            for field in possible_date_fields:
                # 检查 SQL 中是否已存在该字段（带或不带表别名前缀）
                if re.search(r'(?<!\w)' + field + r'(?!\w)', sql_clean, re.IGNORECASE):
                    found_field = field
                    break

            if not found_field:
                logger.warning(f"[_inject_time_filter] SQL 中未找到已知时间字段，跳过时间过滤注入")
                return sql

            if time_mode == "monthly":
                year, month = time_value.split("-")
                start_date = f"{year}-{month}-01"
                import calendar
                last_day = calendar.monthrange(int(year), int(month))[1]
                end_date = f"{year}-{month}-{last_day:02d}"
            elif time_mode == "quarterly":
                year, quarter = time_value.split("-Q")
                q = int(quarter)
                start_month = (q - 1) * 3 + 1
                end_month = q * 3
                start_date = f"{year}-{start_month:02d}-01"
                import calendar
                last_day = calendar.monthrange(int(year), end_month)[1]
                end_date = f"{year}-{end_month:02d}-{last_day:02d}"
            else:
                return sql

            time_filter = f"AND DATE({found_field}) BETWEEN '{start_date}' AND '{end_date}'"
            
            sql_clean = sql.strip().rstrip(';').strip()
            
            # 找到子查询结束后的外层 WHERE
            outer_pattern = r'\)\s+(?:AS\s+)?\w+\s+WHERE\b'
            all_matches = list(re.finditer(outer_pattern, sql_clean, re.IGNORECASE | re.DOTALL))
            
            if all_matches:
                last_match = all_matches[-1]
                where_start = last_match.start() + sql_clean[last_match.start():].upper().find('WHERE')
                after_where_raw = sql_clean[where_start + 5:]
                
                clause_match = re.search(r'\b(ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|UNION)\b', after_where_raw, re.IGNORECASE)
                
                if clause_match:
                    insert_pos = where_start + 5 + clause_match.start()
                    return sql_clean[:insert_pos] + " " + time_filter + " " + after_where_raw.strip()
                else:
                    return sql_clean[:where_start + 5] + after_where_raw + " " + time_filter
            
            # 没有子查询，在 ORDER BY 等关键字前追加
            clause_pattern = r'\b(ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|UNION\b)'
            match = re.search(clause_pattern, sql_clean, re.IGNORECASE)
            
            if match:
                before_clause = sql_clean[:match.start()].rstrip().rstrip(';').strip()
                after_clause = sql_clean[match.start():]
                
                if before_clause.upper().endswith(('AND', 'OR')):
                    before_clause = before_clause[:-3].strip()
                
                return before_clause + " " + time_filter + " " + after_clause
            else:
                sql_clean = sql_clean.rstrip().rstrip(';').strip()
                if sql_clean.upper().endswith(('AND', 'OR')):
                    sql_clean = sql_clean[:-3].strip()
                return sql_clean + " " + time_filter

        # --- 有已保存 SQL，直接执行 ---
        # 应用医院和时间筛选
        hospital_codes = indicator_data.get("hospital_codes")
        time_mode = indicator_data.get("time_mode")
        time_value = indicator_data.get("time_value")
        date_field = indicator_data.get("date_field", "discharge")
        group_by_hospital = indicator_data.get("group_by_hospital", False)
        
        logger.info(f"[医院过滤] hospital_codes={hospital_codes}, time_mode={time_mode}, time_value={time_value}, group_by_hospital={group_by_hospital}")
        
        # 获取医院名称映射 + 全省时展开医院列表
        hospital_names = {}
        all_hospitals = []
        try:
            from sql_runner import get_hospitals
            all_hospitals = get_hospitals()
            for h in all_hospitals:
                hospital_names[h.get("MDC_ORG_CD")] = h.get("MDC_ORG_NM", h.get("MDC_ORG_CD"))
        except Exception:
            pass
        
        # 当 group_by_hospital=True 但 hospital_codes 为空时（前端选了"全省"），
        # 展开为所有医院代码，确保能走分组执行逻辑
        if group_by_hospital and not hospital_codes and all_hospitals:
            hospital_codes = [h.get("MDC_ORG_CD") for h in all_hospitals]
            logger.info(f"[医院过滤] 全省模式，展开医院列表，共 {len(hospital_codes)} 家医院")
        
        # 计数型 group_by 医院分组在后面处理（见 596 行）
            numerator_sql = _inject_hospital_filter(numerator_sql, hospital_codes)
            numerator_sql = _inject_time_filter(numerator_sql, time_mode, time_value, date_field)
        if denominator_sql:
            denominator_sql = _inject_hospital_filter(denominator_sql, hospital_codes)
            denominator_sql = _inject_time_filter(denominator_sql, time_mode, time_value, date_field)
        
        # 明确为计数型时，即使有分子分母 SQL 也走单 SQL 分支
        calc_type_raw = indicator_data.get("calc_type") or "ratio"
        is_count_type = calc_type_raw == "count"

        # 仅当有分子分母 SQL 且非计数型时才走比值型分支
        if numerator_sql and denominator_sql and not is_count_type:
            # 比值型需要同时获取分子和分母的预览数据

            # 如果需要按医院分组执行（比值型）
            if group_by_hospital and hospital_codes and len(hospital_codes) > 0:
                hospital_results = []
                total_num_cnt = 0
                total_den_cnt = 0
                all_ok = True
                all_logs = []

                for i, hosp_code in enumerate(hospital_codes):
                    hosp_name = hospital_names.get(hosp_code, hosp_code)
                    hosp_logs = [{"time": time.strftime("%H:%M:%S"), "level": "info", "message": f"[{hosp_name}] 开始执行..."}]

                    hosp_num_sql = _inject_hospital_filter(numerator_sql, [hosp_code])
                    hosp_num_sql = _inject_time_filter(hosp_num_sql, time_mode, time_value, date_field)
                    hosp_den_sql = _inject_hospital_filter(denominator_sql, [hosp_code])
                    hosp_den_sql = _inject_time_filter(hosp_den_sql, time_mode, time_value, date_field)

                    hosp_num_cnt, hosp_num_err, hosp_num_cols, hosp_num_rows = _exec_sql(hosp_num_sql)
                    hosp_den_cnt, hosp_den_err, hosp_den_cols, hosp_den_rows = _exec_sql(hosp_den_sql)

                    hosp_rate = round(hosp_num_cnt * 100.0 / hosp_den_cnt, 4) if (hosp_den_cnt and hosp_num_cnt is not None and hosp_den_cnt != 0) else None
                    hosp_ok = hosp_num_err is None and hosp_den_err is None

                    if not hosp_ok:
                        all_ok = False

                    total_num_cnt += (hosp_num_cnt or 0)
                    total_den_cnt += (hosp_den_cnt or 0)

                    hosp_logs.extend([
                        {"time": time.strftime("%H:%M:%S"), "level": "info", "message": f"[{hosp_name}] 分子：{hosp_num_cnt} 条"},
                        {"time": time.strftime("%H:%M:%S"), "level": "info", "message": f"[{hosp_name}] 分母：{hosp_den_cnt} 条"},
                    ])
                    if hosp_rate is not None:
                        hosp_logs.append({"time": time.strftime("%H:%M:%S"), "level": "info", "message": f"[{hosp_name}] 指标值：{hosp_rate}%"})
                    if hosp_num_err:
                        hosp_logs.append({"time": time.strftime("%H:%M:%S"), "level": "error", "message": f"[{hosp_name}] 分子执行出错：{hosp_num_err}"})
                    if hosp_den_err:
                        hosp_logs.append({"time": time.strftime("%H:%M:%S"), "level": "error", "message": f"[{hosp_name}] 分母执行出错：{hosp_den_err}"})

                    hospital_results.append({
                        "hospital_code": hosp_code,
                        "hospital_name": hosp_name,
                        "numerator_count": hosp_num_cnt,
                        "denominator_count": hosp_den_cnt,
                        "ratio_percent": hosp_rate,
                        "status": "success" if hosp_ok else "failed",
                        "error": hosp_num_err or hosp_den_err,
                        "preview_data": _to_serializable_rows(hosp_num_rows[:10]) if hosp_num_rows else [],
                        "denominator_preview_data": _to_serializable_rows(hosp_den_rows[:10]) if hosp_den_rows else [],
                    })
                    all_logs.extend(hosp_logs)

                total_rate = round(total_num_cnt * 100.0 / total_den_cnt, 4) if total_den_cnt != 0 else None
                all_logs.append({"time": time.strftime("%H:%M:%S"), "level": "info", "message": f"汇总执行完成。总体指标值：{total_rate}%（{total_num_cnt}/{total_den_cnt}）"})

                first_preview = []
                first_cols = []
                first_den_preview = []
                first_den_cols = []
                for hosp in hospital_results:
                    pd = hosp.get("preview_data", [])
                    if pd and not first_preview:
                        first_preview = pd
                        first_cols = list(pd[0].keys()) if pd else []
                    dpd = hosp.get("denominator_preview_data", [])
                    if dpd and not first_den_preview:
                        first_den_preview = dpd
                        first_den_cols = list(dpd[0].keys()) if dpd else []

                result = {
                    "ok": all_ok,
                    "indicator_type": ind_type,
                    "numerator_sql": numerator_sql,
                    "denominator_sql": denominator_sql,
                    "numerator_count": total_num_cnt,
                    "denominator_count": total_den_cnt,
                    "rate_percent": total_rate,
                    "rate_formula": f"{total_num_cnt}/{total_den_cnt}={total_rate}%" if total_rate is not None else None,
                    "error": None if all_ok else "部分医院执行失败",
                    "preview_columns": first_cols,
                    "preview_rows": first_preview,
                    "preview_data": {"columns": first_cols, "rows": first_preview},
                    "denominator_preview_columns": first_den_cols,
                    "denominator_preview_rows": first_den_preview,
                    "denominator_preview_data": {"columns": first_den_cols, "rows": first_den_preview},
                    "request_id": "",
                    "conversation_id": "",
                    "cache_hit": False,
                    "logs": all_logs,
                    "duration_seconds": round(time.time() - start_time, 3),
                    "group_by_hospital": True,
                    "hospital_results": hospital_results,
                }
                db_record_id = _save(result)
                if db_record_id is not None:
                    result["db_record_id"] = db_record_id
                return result

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
            db_record_id = _save(result)
            if db_record_id is not None:
                result["db_record_id"] = db_record_id
            return result

        # 计数型指标：优先用 single_sql；若无则用 numerator_sql（适用于四要素计数型）
        sql_to_exec = single_sql if single_sql else (numerator_sql if is_count_type else "")

        logger.info(f"[计数型 group_by] group_by_hospital={group_by_hospital}, hospital_codes={hospital_codes}, len={len(hospital_codes) if hospital_codes else 0}, sql_to_exec={bool(sql_to_exec)}, single_sql={bool(single_sql)}, numerator_sql={bool(numerator_sql)}, is_count_type={is_count_type}")
        # 如果需要按医院分组执行（计数型）
        if group_by_hospital and hospital_codes and len(hospital_codes) > 0 and sql_to_exec:
            hospital_results = []
            total_count = 0
            all_ok = True
            all_logs = []
            first_preview = []
            first_cols = []

            for hosp_code in hospital_codes:
                hosp_name = hospital_names.get(hosp_code, hosp_code)
                hosp_logs = [{"time": time.strftime("%H:%M:%S"), "level": "info", "message": f"[{hosp_name}] 开始执行..."}]

                hosp_sql = _inject_hospital_filter(sql_to_exec, [hosp_code])
                hosp_sql = _inject_time_filter(hosp_sql, time_mode, time_value, date_field or "discharge")
                hosp_cnt, hosp_err, hosp_cols, hosp_rows = _exec_sql(hosp_sql)

                stat_count = hosp_cnt
                if hosp_cols and hosp_rows and "patient_cnt" in hosp_cols:
                    total = sum(float(r.get("patient_cnt") or 0) for r in hosp_rows)
                    stat_count = int(total)

                hosp_ok = hosp_err is None
                if not hosp_ok:
                    all_ok = False

                total_count += (stat_count or 0)
                hosp_logs.extend([
                    {"time": time.strftime("%H:%M:%S"), "level": "info", "message": f"[{hosp_name}] 查询结果：{hosp_cnt} 条记录。"},
                    {"time": time.strftime("%H:%M:%S"), "level": "info", "message": f"[{hosp_name}] 执行完成，共 {stat_count} 人次。"},
                ])
                if hosp_err:
                    hosp_logs.append({"time": time.strftime("%H:%M:%S"), "level": "error", "message": f"[{hosp_name}] 执行出错：{hosp_err}"})

                preview = _to_serializable_rows(hosp_rows[:10]) if hosp_rows else []
                if preview and not first_preview:
                    first_preview = preview
                    first_cols = list(preview[0].keys()) if preview else []

                hospital_results.append({
                    "hospital_code": hosp_code,
                    "hospital_name": hosp_name,
                    "numerator_count": stat_count,
                    "count": stat_count,
                    "status": "success" if hosp_ok else "failed",
                    "error": hosp_err,
                    "preview_data": preview,
                    "preview_columns": list(preview[0].keys()) if preview else [],
                })
                all_logs.extend(hosp_logs)

            all_logs.append({"time": time.strftime("%H:%M:%S"), "level": "info", "message": f"汇总执行完成，共 {total_count} 人次。"})
            duration = round(time.time() - start_time, 3)
            result = {
                "ok": all_ok,
                "indicator_type": ind_type,
                "indicator": {"calc_type": calc_type_raw},
                "calc_type": calc_type_raw,
                "sql": sql_to_exec,
                "count": total_count,
                "numerator_count": total_count,
                "error": None if all_ok else "部分医院执行失败",
                "preview_columns": first_cols,
                "preview_rows": first_preview,
                "preview_data": {"columns": first_cols, "rows": first_preview},
                "request_id": "",
                "conversation_id": "",
                "cache_hit": False,
                "logs": all_logs,
                "duration_seconds": duration,
                "group_by_hospital": True,
                "hospital_results": hospital_results,
            }
            db_record_id = _save(result)
            if db_record_id is not None:
                result["db_record_id"] = db_record_id
            return result

        if sql_to_exec:
            sql_to_exec = _inject_hospital_filter(sql_to_exec, hospital_codes)
            sql_to_exec = _inject_time_filter(sql_to_exec, time_mode, time_value, date_field)

        if sql_to_exec:
            cnt, err, cols, rows = _exec_sql(sql_to_exec)
            calc_type = indicator_data.get("calc_type") or "ratio"
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
            duration = round(time.time() - start_time, 3)
            result = {
                "ok": err is None and cnt is not None,
                "indicator_type": ind_type,
                "indicator": {"calc_type": calc_type},
                "calc_type": calc_type,
                "sql": sql_to_exec,
                "count": stat_count,
                "error": err,
                "preview_columns": cols,
                "preview_rows": _to_serializable_rows(rows),
                "preview_data": {"columns": cols, "rows": _to_serializable_rows(rows)},
                "attempts": [{"attempt": 1, "sql": sql_to_exec, "count": stat_count, "error": err}],
                "request_id": "",
                "conversation_id": "",
                "cache_hit": False,
                "logs": logs,
                "duration_seconds": duration,
            }
            db_record_id = _save(result)
            if db_record_id is not None:
                result["db_record_id"] = db_record_id
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
                    "rows": _to_serializable_rows(result.get("preview_rows", [])),
                }
            else:
                # 也要序列化 preview_data 中的 rows
                if "rows" in result["preview_data"]:
                    result["preview_data"]["rows"] = _to_serializable_rows(result["preview_data"]["rows"])
            # 序列化 denominator_preview_rows
            if "denominator_preview_data" in result and "rows" in result["denominator_preview_data"]:
                result["denominator_preview_data"]["rows"] = _to_serializable_rows(result["denominator_preview_data"]["rows"])
            elif result.get("denominator_preview_rows"):
                result["denominator_preview_data"] = {
                    "rows": _to_serializable_rows(result.get("denominator_preview_rows", [])),
                    "columns": result.get("denominator_preview_columns", []),
                }
            db_record_id = _save(result)
            if db_record_id is not None:
                result["db_record_id"] = db_record_id
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

    def fetch_preview_page(
        self,
        execution_id: Union[int, str],
        target: str = "numerator",  # "numerator" | "denominator"
        page: int = 1,
        page_size: int = 50,
        db_session=None,
    ) -> Dict[str, Any]:
        """根据执行记录 ID 获取指定页的预览数据（支持前端临时ID和数据库整数ID）"""
        import sys
        from pathlib import Path
        import time as time_mod

        if not db_session:
            return {"ok": False, "error": "数据库会话不可用", "columns": [], "rows": []}

        try:
            from app.models.indicator import IndicatorExecution
            record = None
            # 前端临时ID格式: "exec-1747401600123"
            if isinstance(execution_id, str) and execution_id.startswith("exec-"):
                exec_int = int(execution_id.split("-")[1])
                # 通过 execution_time 范围查找最接近的记录
                from datetime import datetime as dt
                import time as time_mod
                target_ts = exec_int / 1000
                min_ts = target_ts - 2  # 前后2秒范围内
                max_ts = target_ts + 2
                records_found = db_session.query(IndicatorExecution).filter(
                    IndicatorExecution.execution_time >= dt.fromtimestamp(min_ts),
                    IndicatorExecution.execution_time <= dt.fromtimestamp(max_ts),
                ).order_by(IndicatorExecution.execution_time.desc()).limit(5).all()
                # 精确匹配 execution_time 秒级
                for r in records_found:
                    r_ts = r.execution_time.timestamp()
                    if abs(r_ts - target_ts) < 2:
                        record = r
                        break
            else:
                record = db_session.query(IndicatorExecution).filter(
                    IndicatorExecution.id == int(execution_id)
                ).first()
            if not record:
                return {"ok": False, "error": f"执行记录不存在 (id={execution_id})", "columns": [], "rows": []}

            if target == "numerator":
                raw_sql = record.numerator_sql or record.sql or ""
            elif target == "denominator":
                raw_sql = record.denominator_sql or ""
            else:
                return {"ok": False, "error": f"未知 target: {target}", "columns": [], "rows": []}

            if not raw_sql:
                return {"ok": False, "error": "该执行记录无原始 SQL", "columns": [], "rows": []}

            # 重新应用医院和时间过滤
            def _inject_hospital_filter(sql: str, codes: list = None) -> str:
                if not sql or not codes:
                    return sql
                import re
                codes_str = "','".join(codes)
                sql_clean = sql.strip().rstrip(';').strip()
                table_aliases = set()
                keywords = {'SELECT', 'WHERE', 'AND', 'OR', 'ON', 'AS', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'JOIN', 'FROM'}
                for m in re.finditer(r'(?:FROM|JOIN)\s+(\w+)\s+AS\s+(\w+)', sql_clean, re.IGNORECASE):
                    alias = m.group(2)
                    if alias.upper() not in keywords:
                        table_aliases.add(alias)
                for m in re.finditer(r'(?:FROM|JOIN)\s+(\w+)\s+(\w+)\b', sql_clean, re.IGNORECASE):
                    alias = m.group(2)
                    if alias.upper() not in keywords:
                        table_aliases.add(alias)
                main_alias = list(table_aliases)[0] if table_aliases else None
                outer_select_match = re.search(r'\bSELECT\s+(.*?)\s+FROM\s*\(', sql_clean, re.IGNORECASE | re.DOTALL)
                has_outer_mdc = False
                if outer_select_match:
                    outer_cols = re.sub(r'--[^\n]*', '', outer_select_match.group(1))
                    outer_cols = re.sub(r'/\*.*?\*/', '', outer_cols, flags=re.DOTALL)
                    if re.search(r'(?<!\w\.)\bMDC_ORG_CD\b(?!\s*=)', outer_cols):
                        has_outer_mdc = True
                if has_outer_mdc:
                    hospital_filter = f" AND MDC_ORG_CD IN ('{codes_str}')"
                elif main_alias:
                    hospital_filter = f" AND {main_alias}.MDC_ORG_CD IN ('{codes_str}')"
                else:
                    hospital_filter = f" AND MDC_ORG_CD IN ('{codes_str}')"
                outer_pattern = r'\)\s+(?:AS\s+)?\w+\s+WHERE\b'
                all_matches = list(re.finditer(outer_pattern, sql_clean, re.IGNORECASE | re.DOTALL))
                main_from_pos = sql_clean.upper().find('FROM')
                outer_where_pos = -1
                for m in reversed(all_matches):
                    if m.start() >= main_from_pos:
                        outer_where_pos = m.start()
                        break
                if outer_where_pos >= 0:
                    where_start = outer_where_pos + sql_clean[outer_where_pos:].upper().find('WHERE')
                    after_where_raw = sql_clean[where_start + 5:]
                    clause_match = re.search(r'\b(ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|UNION)\b', after_where_raw, re.IGNORECASE)
                    if clause_match:
                        insert_pos = where_start + 5 + clause_match.start()
                        return sql_clean[:insert_pos] + hospital_filter + " " + after_where_raw
                    else:
                        return sql_clean[:where_start + 5] + after_where_raw + hospital_filter
                else:
                    clause_pattern = r'\b(ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|UNION\b)'
                    match = re.search(clause_pattern, sql_clean, re.IGNORECASE)
                    if match:
                        before = sql_clean[:match.start()].rstrip().rstrip(';').strip()
                        if before.upper().endswith(('AND', 'OR')):
                            before = before[:-3].strip()
                        return before + " " + hospital_filter + " " + sql_clean[match.start():]
                    else:
                        sql_clean2 = sql_clean.rstrip().rstrip(';').strip()
                        if sql_clean2.upper().endswith(('AND', 'OR')):
                            sql_clean2 = sql_clean2[:-3].strip()
                        return sql_clean2 + " " + hospital_filter

            def _inject_time_filter(sql: str, t_mode: str = None, t_value: str = None, d_field: str = "discharge") -> str:
                if not sql or not t_mode or not t_value:
                    return sql
                import re, calendar
                sql_clean = sql.strip().rstrip(';').strip()
                possible_date_fields = [
                    "dscg_dt_tm", "admn_dt_tm", "vst_dt_tm", "rsc_dt_tm", "oprt_dt_tm",
                    "dth_dt_tm", "odr_opn_dt_tm", "dscs_dt_tm",
                ]
                found_field = None
                for field in possible_date_fields:
                    if re.search(r'(?<!\w)' + field + r'(?!\w)', sql_clean, re.IGNORECASE):
                        found_field = field
                        break
                if not found_field:
                    return sql
                if t_mode == "monthly":
                    year, month = t_value.split("-")
                    start_date = f"{year}-{month}-01"
                    last_day = calendar.monthrange(int(year), int(month))[1]
                    end_date = f"{year}-{month}-{last_day:02d}"
                elif t_mode == "quarterly":
                    year, quarter = t_value.split("-Q")
                    q = int(quarter)
                    start_month = (q - 1) * 3 + 1
                    end_month = q * 3
                    start_date = f"{year}-{start_month:02d}-01"
                    last_day = calendar.monthrange(int(year), end_month)[1]
                    end_date = f"{year}-{end_month:02d}-{last_day:02d}"
                else:
                    return sql
                time_filter = f"AND DATE({found_field}) BETWEEN '{start_date}' AND '{end_date}'"
                sql_clean = sql.strip().rstrip(';').strip()
                outer_pattern = r'\)\s+(?:AS\s+)?\w+\s+WHERE\b'
                all_matches = list(re.finditer(outer_pattern, sql_clean, re.IGNORECASE | re.DOTALL))
                if all_matches:
                    last_match = all_matches[-1]
                    where_start = last_match.start() + sql_clean[last_match.start():].upper().find('WHERE')
                    after_where_raw = sql_clean[where_start + 5:]
                    clause_match = re.search(r'\b(ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|UNION)\b', after_where_raw, re.IGNORECASE)
                    if clause_match:
                        insert_pos = where_start + 5 + clause_match.start()
                        return sql_clean[:insert_pos] + " " + time_filter + " " + after_where_raw.strip()
                    else:
                        return sql_clean[:where_start + 5] + after_where_raw + " " + time_filter
                else:
                    clause_pattern = r'\b(ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|UNION\b)'
                    match = re.search(clause_pattern, sql_clean, re.IGNORECASE)
                    if match:
                        before_clause = sql_clean[:match.start()].rstrip().rstrip(';').strip()
                        if before_clause.upper().endswith(('AND', 'OR')):
                            before_clause = before_clause[:-3].strip()
                        return before_clause + " " + time_filter + " " + sql_clean[match.start():]
                    else:
                        sql_clean2 = sql_clean.rstrip().rstrip(';').strip()
                        if sql_clean2.upper().endswith(('AND', 'OR')):
                            sql_clean2 = sql_clean2[:-3].strip()
                        return sql_clean2 + " " + time_filter

            sql = _inject_hospital_filter(raw_sql, record.hospital_codes or [])
            sql = _inject_time_filter(sql, record.time_mode, record.time_value, record.date_field or "discharge")

            # 执行分页查询
            offset = (page - 1) * page_size
            runner_path = Path(__file__).parent.parent.parent / "Hainan_SQL-main" / "text2sql_app" / "sql_runner.py"
            if runner_path.exists():
                sys.path.insert(0, str(runner_path.parent))
                try:
                    from sql_runner import fetch_preview_page as _fetch
                    cols, rows, err = _fetch(sql, limit=page_size, offset=offset)
                    if err:
                        return {"ok": False, "error": err, "columns": [], "rows": []}
                    def _to_serializable(r):
                        clean = {}
                        for k, v in r.items():
                            if hasattr(v, 'strftime'):
                                clean[k] = v.strftime("%Y-%m-%d %H:%M:%S")
                            elif hasattr(v, '__float__') and not isinstance(v, (int, str, bool, type(None))):
                                clean[k] = float(v)
                            else:
                                clean[k] = v
                        return clean
                    return {"ok": True, "columns": cols, "rows": [_to_serializable(r) for r in rows]}
                finally:
                    if str(runner_path.parent) in sys.path:
                        sys.path.remove(str(runner_path.parent))
            else:
                return {"ok": False, "error": "sql_runner 路径不存在", "columns": [], "rows": []}
        except Exception as e:
            logger.error(f"fetch_preview_page 失败: {e}")
            return {"ok": False, "error": str(e), "columns": [], "rows": []}

