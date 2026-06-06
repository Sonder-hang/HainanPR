"""Text-to-SQL 服务集成层"""
import calendar
import httpx
import logging
import re
import time as time_mod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import sys

logger = logging.getLogger(__name__)

# =============================================================================
# 模块级工具函数
# =============================================================================

def _to_serializable_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """将 rows 中的 Decimal/datetime 等非 JSON 类型转为可序列化类型"""
    result = []
    for row in rows:
        clean = {}
        for k, v in row.items():
            if hasattr(v, "strftime"):
                clean[k] = v.strftime("%Y-%m-%d %H:%M:%S")
            elif hasattr(v, "__float__") and not isinstance(v, (int, str, bool, type(None))):
                clean[k] = float(v)
            else:
                clean[k] = v
        result.append(clean)
    return result


def _to_serializable_logs(logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """将 logs 中的 datetime/Decimal 类型转为可序列化类型"""
    result = []
    for log in logs:
        clean = {}
        for k, v in log.items():
            if hasattr(v, "strftime"):
                clean[k] = v.strftime("%H:%M:%S")
            elif hasattr(v, "__float__") and not isinstance(v, (int, str, bool, type(None))):
                clean[k] = float(v)
            else:
                clean[k] = v
        result.append(clean)
    return result


def _to_serializable_any(obj: Any) -> Any:
    """将任意对象（dict/list/datetime/Decimal）递归转为 JSON 可序列化类型"""
    if hasattr(obj, "strftime"):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    elif hasattr(obj, "__float__") and not isinstance(
        obj, (int, str, bool, type(None), list, dict)
    ):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: _to_serializable_any(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_to_serializable_any(item) for item in obj]
    return obj


def _now_ts() -> str:
    return time_mod.strftime("%H:%M:%S")


def _build_time_range(time_mode: Optional[str], time_value: Optional[str]) -> tuple:
    """根据 time_mode 和 time_value 返回 (start_dt, end_dt)"""
    if not time_mode or not time_value:
        return "", ""
    if time_mode == "monthly":
        year, month = time_value.split("-")
        start = f"{year}-{month}-01 00:00:00"
        last_day = calendar.monthrange(int(year), int(month))[1]
        end = f"{year}-{month}-{last_day:02d} 23:59:59"
    elif time_mode == "quarterly":
        year, quarter = time_value.split("-Q")
        q = int(quarter)
        start_month = (q - 1) * 3 + 1
        end_month = q * 3
        start = f"{year}-{start_month:02d}-01 00:00:00"
        last_day = calendar.monthrange(int(year), end_month)[1]
        end = f"{year}-{end_month:02d}-{last_day:02d} 23:59:59"
    elif time_mode == "year":
        start = f"{time_value}-01-01 00:00:00"
        end = f"{time_value}-12-31 23:59:59"
    else:
        start, end = "", ""
    return start, end


# =============================================================================
# Text2SQLService
# =============================================================================


class Text2SQLService:
    """指标 SQL 执行服务

    支持四种业务流：
    - 比值型（ratio）：分子/分母
    - 复合率型（COMPOSITE_RATE）：多子项聚合
    - 复合排行型（COMPOSITE_RANKING）：排行榜
    - 计数型（count）：单 SQL 计数
    """

    # -------------------------------------------------------------------------
    # 初始化：一次性注入 sql_runner 路径，避免并发场景下反复 sys.path 操作
    # -------------------------------------------------------------------------

    def __init__(self) -> None:
        from app.config import settings

        self.base_url = settings.TEXT2SQL_BACKEND_URL.rstrip("/")
        self.timeout = httpx.Timeout(300.0, connect=10.0)
        transport = httpx.HTTPTransport(local_address="127.0.0.1")
        self.client = httpx.Client(timeout=self.timeout, transport=transport)

        # 将 sql_runner 路径一次性注入 sys.path，后续直接 import
        runner_path = Path(__file__).parent.parent.parent / "Hainan_SQL-main" / "text2sql_app" / "sql_runner.py"
        if runner_path.exists():
            runner_parent = str(runner_path.parent)
            if runner_parent not in sys.path:
                sys.path.insert(0, runner_parent)
            self._sql_runner_parent = runner_parent
            self._sql_runner_execute_full = self._import_sql_runner("execute_full")
            self._sql_runner_execute_count = self._import_sql_runner("execute_count")
            self._sql_runner_execute_limited = self._import_sql_runner("execute_limited")
            self._sql_runner_get_hospitals = self._import_sql_runner("get_hospitals")
            self._sql_runner_fetch_preview_page = self._import_sql_runner("fetch_preview_page")
        else:
            self._sql_runner_parent = None
            self._sql_runner_execute_full = None
            self._sql_runner_execute_count = None
            self._sql_runner_execute_limited = None
            self._sql_runner_get_hospitals = None
            self._sql_runner_fetch_preview_page = None

    def _import_sql_runner(self, name: str):
        """从 sql_runner 动态导入指定函数"""
        try:
            from sql_runner import globals as _g
            return getattr(_g, name, None)
        except Exception:
            pass
        try:
            from sql_runner import execute_full, execute_count, execute_limited, get_hospitals, fetch_preview_page
            mapping = {
                "execute_full": execute_full,
                "execute_count": execute_count,
                "execute_limited": execute_limited,
                "get_hospitals": get_hospitals,
                "fetch_preview_page": fetch_preview_page,
            }
            return mapping.get(name)
        except Exception as e:
            logger.warning(f"无法从 sql_runner 导入 {name}: {e}")
            return None

    # -------------------------------------------------------------------------
    # 静态工具
    # -------------------------------------------------------------------------

    @staticmethod
    def _parse_numeric(v: Any) -> Optional[float]:
        """将任意值转为数值类型，用于 SQL 列值解析"""
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return v
        try:
            return int(v)
        except (ValueError, TypeError):
            try:
                return float(v)
            except (ValueError, TypeError):
                return None

    # -------------------------------------------------------------------------
    # SQL 执行（内部）
    # -------------------------------------------------------------------------

    def _exec_sql(
        self,
        sql: str,
        include_rows: bool = True,
        fetch_all: bool = False,
    ) -> Tuple[Optional[int], Optional[str], List[str], List[Dict[str, Any]]]:
        """
        执行 SQL 并返回 (count, error, columns, rows)

        - fetch_all=True        → execute_full（全量取回）
        - include_rows=True      → execute_count + execute_limited（计数 + 预览）
        - include_rows=False     → execute_count（仅计数）
        """
        if not (sql and sql.strip()):
            return None, "SQL 为空", [], []

        if "{FILTER_PLACEHOLDER}" in sql:
            logger.error(f"[_exec_sql] 致命：占位符未被替换！SQL前100字符: {sql[:100]}")
            raise ValueError(f"占位符未替换: {sql[:100]}")

        if self._sql_runner_execute_full is None:
            logger.warning(f"[_exec_sql] sql_runner不可用，走HTTP回退: {sql[:100]!r}")
            result = self.test_sql(sql, limit=10000)
            logger.warning(f"[_exec_sql] HTTP回退完成，count={result.get('count')}, err={result.get('error')}")
            return result.get("count"), result.get("error"), [], []

        try:
            import time as _t2
            t0 = _t2.time()
            if fetch_all:
                cols, rows, err = self._sql_runner_execute_full(sql)
                elapsed = _t2.time() - t0
                logger.info(f"[_exec_sql] sql_runner成功，fetch_all耗时{elapsed:.1f}s，行数={len(rows) if rows else 0}, err={err}")
                return len(rows) if rows else 0, err, cols, rows or []
            elif include_rows:
                cnt, cnt_err = self._sql_runner_execute_count(sql)
                if cnt_err or cnt is None:
                    logger.warning(f"[_exec_sql] execute_count 失败: {cnt_err}，尝试降级使用 execute_limited 获取行数...")
                    cols, rows, prev_err = self._sql_runner_execute_limited(sql, limit=10000)
                    if not prev_err and rows is not None:
                        return len(rows), None, cols, rows
                    return None, cnt_err or "计数失败", [], []

                cols, rows, prev_err = self._sql_runner_execute_limited(sql, limit=200)
                return cnt, prev_err, cols, rows or []
            else:
                cnt, err = self._sql_runner_execute_count(sql)
                return cnt, err, [], []
        except Exception as e:
            return None, str(e), [], []

    # -------------------------------------------------------------------------
    # SQL 注入器
    # -------------------------------------------------------------------------

    def _build_time_conditions(self, time_mode: str, time_value: str, time_col: str) -> str:
        """
        【阶段一·时间组装】在 Python 端计算精确起止时间戳，
        生成不带任何函数的纯净区间查询，保护 B+Tree 索引不被破坏。
        """
        if not time_mode or not time_value:
            return ""
        if time_mode == "monthly":
            year, month = time_value.split("-")
            start = f"{year}-{month}-01 00:00:00"
            last_day = calendar.monthrange(int(year), int(month))[1]
            end = f"{year}-{month}-{last_day:02d} 23:59:59"
        elif time_mode == "quarterly":
            year, quarter = time_value.split("-Q")
            q = int(quarter)
            start_month = (q - 1) * 3 + 1
            end_month = q * 3
            start = f"{year}-{start_month:02d}-01 00:00:00"
            last_day = calendar.monthrange(int(year), end_month)[1]
            end = f"{year}-{end_month:02d}-{last_day:02d} 23:59:59"
        elif time_mode == "year":
            start = f"{time_value}-01-01 00:00:00"
            end = f"{time_value}-12-31 23:59:59"
        else:
            return ""
        return f"{time_col} >= '{start}' AND {time_col} <= '{end}'"

    def _inject_filters(
        self,
        sql: str,
        hospital_codes: Optional[List[str]] = None,
        time_mode: Optional[str] = None,
        time_value: Optional[str] = None,
        time_col_name: Optional[str] = None,
        time_col_name_2: Optional[str] = None,
        is_aggregate: bool = False,
    ) -> str:
        """
        【阶段一·万能 SQL 注入器】
        将所有过滤条件（时间 + 医院）在 Python 端组装完毕，
        通过 {FILTER_PLACEHOLDER} / {FILTER_PLACEHOLDER_2} 精准替换注入到 SQL 最内层，
        实现 Predicate Pushdown，把运算下推给数据库引擎。

        参数：
          sql                  带 {FILTER_PLACEHOLDER} 占位符的原始 SQL
          hospital_codes       选中的医院代码列表，为空则不注入
          time_mode            monthly / quarterly
          time_value           如 '2026-05' 或 '2026-Q1'
          time_col_name        主时间字段全名，如 't1.DSCG_DT_TM'
          time_col_name_2      次时间字段全名（如门诊/住院用不同字段）
          is_aggregate         True 时，若医院非空则追加 GROUP BY MDC_ORG_CD
        """
        if not sql:
            return sql

        # ── 调试日志 ─────────────────────────────────────────────────────────
        logger.info(f"[_inject_filters] 入口 SQL 前150字符: {sql[:150]!r}")
        logger.info(f"[_inject_filters] 含反斜杠n数量: {sql.count(chr(92)+'n')}")

        # ① 时间条件（主）
        time_cond_1 = ""
        if time_mode and time_value and time_col_name:
            time_cond_1 = self._build_time_conditions(time_mode, time_value, time_col_name)

        # ①b 时间条件（次）
        time_cond_2 = ""
        if time_mode and time_value and time_col_name_2:
            time_cond_2 = self._build_time_conditions(time_mode, time_value, time_col_name_2)

        # ── 辅助：按占位符锚点局部推断该层级的表别名 ────────────────────────
        def _find_effective_alias(sql_segment: str, placeholder: str) -> str:
            """
            从占位符位置向前扫描，寻找括号深度=0层级最近的有效表别名。
            核心：跟踪括号深度，只处理括号深度=0的FROM，避免被子查询内部FROM干扰。
            """
            if not sql_segment or not placeholder:
                return ""

            idx = sql_segment.find(placeholder)
            if idx == -1:
                return ""

            prefix = sql_segment[:idx].strip()
            if not prefix:
                return ""

            # 预处理1：移除所有 SQL 注释
            prefix = re.sub(r'/\*.*?\*/', '', prefix, flags=re.DOTALL)
            prefix = re.sub(r'--.*?$', '', prefix, flags=re.MULTILINE)

            # 预处理2：统一处理反引号
            prefix = prefix.replace('`', '')

            tokens = re.split(r'\s+', prefix.upper())
            orig_tokens = re.split(r'\s+', prefix)

            # 关键字列表：这些词绝对不可能是别名
            KEYWORDS = {
                'JOIN', 'LEFT', 'RIGHT', 'INNER', 'FULL',
                'WHERE', 'GROUP', 'ORDER', 'HAVING', 'LIMIT',
                'UNION', 'AND', 'OR', 'ON', 'SELECT', 'FROM', 'WITH',
            }

            # 核心：从后往前扫描，跟踪括号深度，只处理括号深度=0的FROM
            bracket_depth = 0
            for i in range(len(tokens) - 1, -1, -1):
                token = tokens[i]

                # 先更新括号深度（遇到)加1，遇到(减1）
                bracket_depth += token.count(')')
                bracket_depth -= token.count('(')

                # 只有括号深度=0时，才处理FROM关键字
                if bracket_depth == 0 and token == 'FROM':
                    j = i + 1
                    if j >= len(tokens):
                        continue

                    # 情况1：FROM 后面是子查询
                    if tokens[j].startswith('('):
                        sub_bracket_depth = 0
                        while j < len(tokens):
                            sub_bracket_depth += tokens[j].count('(')
                            sub_bracket_depth -= tokens[j].count(')')

                            if sub_bracket_depth == 0:
                                j += 1
                                while j < len(tokens) and tokens[j] == 'AS':
                                    j += 1
                                if j < len(tokens) and tokens[j] and tokens[j] not in KEYWORDS:
                                    alias = orig_tokens[j]
                                    alias = re.sub(r'[;,)]$', '', alias)
                                    return alias
                                else:
                                    # 子查询没有别名，返回空
                                    return ""
                            j += 1

                    # 情况2：FROM 后面是普通表 / CTE
                    else:
                        # 跳过表名
                        j += 1

                        # 跳过 AS
                        while j < len(tokens) and tokens[j] == 'AS':
                            j += 1

                        # 有显式别名，且不是关键字
                        if j < len(tokens) and tokens[j] and tokens[j] not in KEYWORDS:
                            alias = orig_tokens[j]
                            alias = re.sub(r'[;,)]$', '', alias)
                            return alias
                        # 没有显式别名，使用表名本身
                        else:
                            table_name = orig_tokens[i + 1]
                            alias = re.sub(r'[;,)]$', '', table_name)
                            if '.' in alias:
                                alias = alias.split('.')[-1]
                            return alias

            # 兜底正则
            match = re.search(
                r"FROM\s*(?:\([^)]*\)\s*|\w+\.)?(\w+)\s*(?:AS\s+)?(\w+)?",
                prefix,
                re.IGNORECASE | re.DOTALL,
            )
            if match:
                return match.group(2) or match.group(1)

            return ""

        # ── 占位符存在性检测（需在 has_ph1/has_ph2 使用前定义） ───────────
        clean_sql = sql.rstrip().rstrip("；").rstrip(";").strip()
        has_ph1 = bool(re.search(r"\{\s*FILTER_PLACEHOLDER\s*\}", clean_sql, re.IGNORECASE))
        has_ph2 = bool(re.search(r"\{\s*FILTER_PLACEHOLDER_2\s*\}", clean_sql, re.IGNORECASE))

        # ── 主占位符别名（占位符所在层级局部推断） ────────────────────────
        alias_for_ph1 = ""
        if time_col_name and "." in time_col_name:
            alias_for_ph1 = time_col_name.split(".")[0]
        elif time_col_name_2 and "." in time_col_name_2:
            alias_for_ph1 = time_col_name_2.split(".")[0]
        elif has_ph1:
            alias_for_ph1 = _find_effective_alias(sql, "{FILTER_PLACEHOLDER}")

        # ── 次占位符别名 ────────────────────────────────────────────────
        alias_for_ph2 = ""
        if time_col_name_2 and "." in time_col_name_2:
            alias_for_ph2 = time_col_name_2.split(".")[0]
        elif has_ph2:
            alias_for_ph2 = _find_effective_alias(sql, "{FILTER_PLACEHOLDER_2}")
        # 如果次占位符没有专属别名，降级沿用主占位符的
        if not alias_for_ph2 and alias_for_ph1:
            alias_for_ph2 = alias_for_ph1

        # ── 医院条件（主占位符层级） ────────────────────────────────────
        hosp_cond = ""
        if hospital_codes and len(hospital_codes) > 0:
            codes_str = "','".join(str(c) for c in hospital_codes)
            if alias_for_ph1:
                hosp_cond = f"{alias_for_ph1}.MDC_ORG_CD IN ('{codes_str}')"
            else:
                hosp_cond = f"MDC_ORG_CD IN ('{codes_str}')"

        # ── 医院条件（次占位符层级） ────────────────────────────────────
        hosp_cond_2 = ""
        if hospital_codes and len(hospital_codes) > 0:
            codes_str = "','".join(str(c) for c in hospital_codes)
            if alias_for_ph2:
                hosp_cond_2 = f"{alias_for_ph2}.MDC_ORG_CD IN ('{codes_str}')"
            else:
                hosp_cond_2 = f"MDC_ORG_CD IN ('{codes_str}')"

        # ── 合并第一组占位符条件（时间1 + 医院） ───────────────────────
        parts_1: List[str] = []
        if time_cond_1:
            parts_1.append(time_cond_1)
        if hosp_cond:
            parts_1.append(hosp_cond)

        # ── 合并第二组占位符条件（时间2 + 医院） ───────────────────────
        parts_2: List[str] = []
        if time_cond_2:
            parts_2.append(time_cond_2)
            if hosp_cond_2:
                parts_2.append(hosp_cond_2)

        # 无任何条件时，删除所有占位符
        if not parts_1 and not parts_2:
            return (
                sql.replace("{FILTER_PLACEHOLDER}", "")
                   .replace("{FILTER_PLACEHOLDER_2}", "")
                   .strip()
                   .rstrip(";")
                   .strip()
            )

        # ③ 占位符替换模式
        replaced = clean_sql

        if parts_1 and has_ph1:
            combined_1 = " AND ".join(parts_1)
            before_ph_match = re.search(r"\{\s*FILTER_PLACEHOLDER\s*\}", replaced, re.IGNORECASE)
            before_ph = replaced[:before_ph_match.start()].rstrip() if before_ph_match else replaced.rstrip()
            last_word = before_ph.upper().split()[-1] if before_ph.split() else ""
            if before_ph == "":
                replaced = re.sub(r"\{\s*FILTER_PLACEHOLDER\s*\}", combined_1, replaced, flags=re.IGNORECASE)
            elif last_word in ("AND", "OR"):
                replaced = re.sub(r"\{\s*FILTER_PLACEHOLDER\s*\}", combined_1, replaced, flags=re.IGNORECASE)
            else:
                replaced = re.sub(r"\{\s*FILTER_PLACEHOLDER\s*\}", f"AND {combined_1}", replaced, flags=re.IGNORECASE)
        elif parts_1 and not has_ph1:
            logger.warning(f"[_inject_filters] 未找到占位符，跳过头部强制拼接。SQL前100字符: {replaced[:100]}")
            pass
        else:
            replaced = re.sub(r"\s+(AND|OR)\s*\{\s*FILTER_PLACEHOLDER\s*\}", "", replaced, flags=re.IGNORECASE)
            replaced = re.sub(r"\{\s*FILTER_PLACEHOLDER\s*\}", "", replaced, flags=re.IGNORECASE)

        if parts_2 and has_ph2:
            combined_2 = " AND ".join(parts_2)
            before_ph2_match = re.search(r"\{\s*FILTER_PLACEHOLDER_2\s*\}", replaced, re.IGNORECASE)
            before_ph2 = replaced[:before_ph2_match.start()].rstrip() if before_ph2_match else replaced.rstrip()
            last_word2 = before_ph2.upper().split()[-1] if before_ph2.split() else ""
            if before_ph2 == "":
                replaced = re.sub(r"\{\s*FILTER_PLACEHOLDER_2\s*\}", combined_2, replaced, flags=re.IGNORECASE)
            elif last_word2 in ("AND", "OR"):
                replaced = re.sub(r"\{\s*FILTER_PLACEHOLDER_2\s*\}", combined_2, replaced, flags=re.IGNORECASE)
            else:
                replaced = re.sub(r"\{\s*FILTER_PLACEHOLDER_2\s*\}", f"AND {combined_2}", replaced, flags=re.IGNORECASE)
        elif parts_2 and not has_ph2:
            pass
        else:
            replaced = re.sub(r"\{\s*FILTER_PLACEHOLDER_2\s*\}", "", replaced, flags=re.IGNORECASE)

        # 清理末尾悬空的 AND/OR
        replaced = replaced.strip().rstrip(";").strip()

        # ④ 回退兼容模式（无占位符时，在最外层 WHERE 注入）
        if not has_ph1 and not has_ph2:
            logger.warning(
                f"[_inject_filters] SQL未添加 {{FILTER_PLACEHOLDER}} 占位符，"
                f"将在最外层注入过滤条件，这会导致谓词下推失效，严重影响查询性能！SQL前100: {replaced[:100]}"
            )

            # 尝试推断主表的别名，用于医院过滤条件
            main_alias = alias_for_ph1
            if not main_alias:
                # 从 SQL 首行 FROM 子句推断
                alias_match = re.search(
                    r"FROM\s+(?:[\w`]+\.?\w*\s+)?(?:AS\s+)?([\w`]+)(?:\s|,|$)",
                    sql,
                    re.IGNORECASE,
                )
                if alias_match:
                    candidate = alias_match.group(1).strip("`")
                    if candidate.upper() not in {
                        "SELECT", "WHERE", "AND", "OR", "ON", "JOIN",
                        "INNER", "LEFT", "RIGHT", "OUTER",
                    }:
                        main_alias = candidate

            parts_all: List[str] = []
            if time_cond_1:
                parts_all.append(time_cond_1)
            if time_cond_2:
                parts_all.append(time_cond_2)
            if hospital_codes and len(hospital_codes) > 0:
                codes_str = "','".join(str(c) for c in hospital_codes)
                if main_alias:
                    parts_all.append(f"{main_alias}.MDC_ORG_CD IN ('{codes_str}')")
                else:
                    parts_all.append(f"MDC_ORG_CD IN ('{codes_str}')")
            if not parts_all:
                return replaced.rstrip().rstrip(";").strip()

            new_filter = "AND " + " AND ".join(parts_all)
            sql_clean = replaced

            clause_pattern = r"\b(ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|UNION)\b"
            match = re.search(clause_pattern, sql_clean, re.IGNORECASE)
            if match:
                before = sql_clean[: match.start()].rstrip().rstrip(";").strip()
                if before.upper().endswith(("AND", "OR")):
                    before = before[:-3].strip()
                replaced = before + " " + new_filter + " " + sql_clean[match.start() :]
            else:
                s = sql_clean.rstrip().rstrip(";").strip()
                # 去掉末尾的 AND/OR 再追加新过滤条件
                while s.upper().endswith("AND") or s.upper().endswith("OR"):
                    s = s[:-3].strip()
                replaced = s + " " + new_filter

        # ⑤ 不自动追加 GROUP BY（聚合逻辑由 SQL 本身或智能聚合逻辑负责）
        # 注意：某些 SQL（如 SELECT DISTINCT + GROUP BY）在 only_full_group_by 模式下
        # 要求 SELECT 字段都在 GROUP BY 中，自动追加会破坏这类 SQL。

        logger.info(f"[_inject_filters] 最终 SQL 片段: {replaced[:300]}")
        return replaced

    def _save_execution_record(
        self,
        result: Dict[str, Any],
        db_session,
        indicator_data: Dict[str, Any],
    ) -> Optional[int]:
        """统一保存执行记录到数据库，返回记录ID"""
        if not db_session:
            return None
        try:
            from app.models.indicator import IndicatorExecution

            kind = indicator_data.get("kind") or indicator_data.get("business_type") or "core18"
            run_mode = indicator_data.get("run_mode") or "immediate"
            time_range = indicator_data.get("time_range") or "全量"
            result_type = indicator_data.get("result_type") or "ratio"
            calc_method = indicator_data.get("calc_method") or "SQL录入"
            indicator_name = (
                indicator_data.get("name") or indicator_data.get("indicator_name") or ""
            )
            indicator_id = indicator_data.get("indicator_id") or indicator_data.get("id")

            if indicator_id is None:
                logger.warning(
                    f"[_save_execution_record] indicator_id 为 None，跳过保存执行记录。"
                    f"indicator_name={indicator_name}"
                )
                return None

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
                preview_data={
                    "columns": result.get("preview_columns", []),
                    "rows": _to_serializable_rows(result.get("preview_rows", [])),
                },
                denominator_preview_data={
                    "columns": result.get("denominator_preview_columns", []),
                    "rows": _to_serializable_rows(result.get("denominator_preview_rows", [])),
                },
                error=result.get("error", ""),
                attempts=_to_serializable_any(
                    result.get("numerator_attempts", []) or result.get("attempts", [])
                ),
                llm_thinking=(
                    result.get("numerator_llm_thinking", "") or result.get("llm_thinking", "")
                ),
                llm_raw=(
                    result.get("numerator_llm_raw", "") or result.get("llm_raw", "")
                ),
                cache_hit=result.get("cache_hit", False),
                request_id=result.get("request_id", ""),
                conversation_id=result.get("conversation_id", ""),
                status="success" if result.get("ok") else "failed",
                logs=_to_serializable_logs(result.get("logs", [])),
                duration_seconds=result.get("duration_seconds"),
                execution_time=datetime.now(),
                hospital_codes=indicator_data.get("hospital_codes"),
                time_mode=indicator_data.get("time_mode"),
                time_value=indicator_data.get("time_value"),
                date_field=indicator_data.get("date_field"),
                group_by_hospital=result.get("group_by_hospital", False),
                hospital_results=result.get("hospital_results", []),
                subitem_data=_to_serializable_any(result.get("subitem_data")),
            )
            db_session.add(exec_record)
            db_session.commit()
            db_session.refresh(exec_record)
            return exec_record.id
        except Exception as e:
            logger.error(f"保存执行记录失败: {e}")
            db_session.rollback()
            return None

    # -------------------------------------------------------------------------
    # 策略方法
    # -------------------------------------------------------------------------

    # 时间字段元数据值 → 数据库实际列名
    _TIME_COL_MAP: Dict[str, str] = {
        "discharge":   "DSCG_DT_TM",
        "admission":   "ADMN_DT_TM",
        "PSCP_OPN_DT": "PSCP_OPN_DT",
        "VST_DT_TM":   "VST_DT_TM",
        "ADMN_DT_TM":  "ADMN_DT_TM",
        "DSCG_DT_TM":  "DSCG_DT_TM",
    }

    def _resolve_time_col(self, date_field: str) -> str:
        """元数据值（如 'discharge'）映射为数据库实际列名（如 'DSCG_DT_TM'）。

        如果 date_field 已经是完整列引用（如 't1.DSCG_DT_TM'），直接返回。
        """
        if not date_field:
            return "DSCG_DT_TM"
        # 已经是完整列名（如 t1.DSCG_DT_TM），直接返回
        if "." in date_field:
            return date_field
        return self._TIME_COL_MAP.get(date_field, date_field)

    def _get_hospital_names(self) -> Dict[str, str]:
        """获取医院代码→名称映射"""
        names: Dict[str, str] = {}
        if self._sql_runner_get_hospitals:
            try:
                for h in self._sql_runner_get_hospitals():
                    key = (h.get("MDC_ORG_CD") or "").upper()
                    names[key] = h.get("MDC_ORG_NM", h.get("MDC_ORG_CD") or key)
            except Exception:
                pass
        return names

    # -------------------------------------------------------------------------
    # 策略 1：比值型（分子/分母）
    # -------------------------------------------------------------------------

    def _execute_ratio_indicator(
        self,
        numerator_sql: str,
        denominator_sql: str,
        ind_type: str,
        hospital_codes: Optional[List[str]],
        time_mode: Optional[str],
        time_value: Optional[str],
        time_col_num: str,
        time_col_den: str,
        group_by_hospital: bool,
        hospital_names: Dict[str, str],
        db_session,
        indicator_data: Dict[str, Any],
        skip_save: bool,
        start_time: float,
    ) -> Dict[str, Any]:
        """
        比值型指标执行器
        - time_col_num  ：分子 SQL 的时间过滤列
        - time_col_den  ：分母 SQL 的时间过滤列（可能与分子不同）
        - group_by_hospital=True：一次查询所有医院，O(1) 路由
        - group_by_hospital=False：单次查询（不分组）
        """
        # ── 分组执行（O(1) 路由） ─────────────────────────────────────────
        if group_by_hospital and hospital_codes and len(hospital_codes) > 0:
            all_logs: List[Dict[str, Any]] = []
            all_ok = True

            # ① 一次查询分子（使用分子时间过滤列 time_col_num）
            final_num_sql = self._inject_filters(
                numerator_sql,
                hospital_codes=hospital_codes,
                time_mode=time_mode,
                time_value=time_value,
                time_col_name=time_col_num,
                is_aggregate=True,
            )
            logger.info(f"[_execute_ratio_indicator] 分子注入后SQL前200字符: {final_num_sql[:200]!r}")
            logger.info(f"[_execute_ratio_indicator] 分子含反斜杠n数量: {final_num_sql.count(chr(92)+'n')}")
            num_total_cnt, num_err, num_cols, num_rows = self._exec_sql(
                final_num_sql, include_rows=True, fetch_all=True
            )

            # 保留原始明细数据用于预览（智能聚合后会覆盖 num_cols/num_rows）
            preview_num_cols = num_cols
            preview_num_rows = num_rows

            # 【智能聚合】分子 SQL 为明细查询时，自动包裹聚合子查询
            if (
                not num_err
                and num_cols
                and "numerator_cnt" not in num_cols
                and "MDC_ORG_CD" in num_cols
            ):
                if "numerator_cnt" not in final_num_sql.lower():
                    agg_sql = (
                        f"SELECT MDC_ORG_CD, COUNT(*) AS numerator_cnt FROM ("
                        f"{final_num_sql}"
                        f") AS _num_detail GROUP BY MDC_ORG_CD"
                    )
                    num_total_cnt, num_err, num_cols, num_rows = self._exec_sql(
                        agg_sql, include_rows=True, fetch_all=True
                    )
                    if not num_err:
                        logger.info(
                            f"[智能聚合] 包裹后行数: {len(num_rows)}, "
                            f"医院: {[r.get('MDC_ORG_CD') for r in num_rows]}"
                        )
                    else:
                        logger.warning(f"[智能聚合] 包裹失败: {num_err}")

            # GROUP BY 失败时回退：按医院逐个查询
            if num_err and (
                "not in GROUP BY" in str(num_err) or " Expression " in str(num_err)
            ):
                logger.warning(f"GROUP BY 失败，回退到单院循环执行: {num_err}")
                num_dict: Dict[str, float] = {}
                _preview_num_cols: Optional[List[str]] = None
                _preview_num_rows: Optional[List[Dict[str, Any]]] = None
                for i, hosp_code in enumerate(hospital_codes):
                    hosp_sql = self._inject_filters(
                        numerator_sql,
                        [hosp_code],
                        time_mode,
                        time_value,
                        time_col_num,
                    )
                    cnt, err, cols, rows = self._exec_sql(hosp_sql, include_rows=False, fetch_all=True)
                    if err:
                        all_logs.append(
                            {
                                "time": _now_ts(),
                                "level": "error",
                                "message": f"分子[{hosp_code}]出错: {err}",
                            }
                        )
                    else:
                        num_dict[str(hosp_code)] = float(cnt or 0)
                        if i == 0 and cols and rows:
                            _preview_num_cols = cols
                            _preview_num_rows = rows
                if _preview_num_cols is not None and _preview_num_rows is not None:
                    preview_num_cols = _preview_num_cols
                    preview_num_rows = _preview_num_rows
            elif num_err:
                all_ok = False
                all_logs.append(
                    {
                        "time": _now_ts(),
                        "level": "error",
                        "message": f"分子 SQL 执行出错：{num_err}",
                    }
                )
                num_dict = {}
            else:
                # 【O(1) 路由】将结果转为 {MDC_ORG_CD: 值} 字典
                num_dict = {}
                for row in num_rows:
                    key = row.get("MDC_ORG_CD") or row.get("mdc_org_cd")
                    if key:
                        num_dict[str(key)] = float(row.get("numerator_cnt", 0) or 0)
                    elif len(hospital_codes) == 1 and not num_dict:
                        num_dict[hospital_codes[0]] = float(
                            row.get("numerator_cnt", 0) or 0
                        )

            # ② 一次查询分母（使用分母时间过滤列 time_col_den）
            final_den_sql = self._inject_filters(
                denominator_sql,
                hospital_codes=hospital_codes,
                time_mode=time_mode,
                time_value=time_value,
                time_col_name=time_col_den,
                is_aggregate=True,
            )
            den_total_cnt, den_err, den_cols, den_rows = self._exec_sql(
                final_den_sql, include_rows=True, fetch_all=True
            )

            # 保留原始明细数据用于预览
            preview_den_cols = den_cols
            preview_den_rows = den_rows

            # 【智能聚合】分母 SQL 为明细查询时，自动包裹聚合子查询
            if (
                not den_err
                and den_cols
                and "denominator_cnt" not in den_cols
                and "MDC_ORG_CD" in den_cols
            ):
                if "denominator_cnt" not in final_den_sql.lower():
                    agg_sql = (
                        f"SELECT MDC_ORG_CD, COUNT(DISTINCT INHOS_NO) AS denominator_cnt FROM ("
                        f"{final_den_sql}"
                        f") AS _den_detail GROUP BY MDC_ORG_CD"
                    )
                    den_total_cnt, den_err, den_cols, den_rows = self._exec_sql(
                        agg_sql, include_rows=True, fetch_all=True
                    )
                    if not den_err:
                        logger.info(
                            f"[智能聚合] 分母包裹后行数: {len(den_rows)}, "
                            f"医院: {[r.get('MDC_ORG_CD') for r in den_rows]}"
                        )
                    else:
                        logger.warning(f"[智能聚合] 分母包裹失败: {den_err}")

            den_dict: Dict[str, float] = {}
            _preview_den_cols: Optional[List[str]] = None
            _preview_den_rows: Optional[List[Dict[str, Any]]] = None
            if den_err and (
                "not in GROUP BY" in str(den_err) or " Expression " in str(den_err)
            ):
                logger.warning(f"分母 GROUP BY 失败，回退到单院循环执行: {den_err}")
                for i, hosp_code in enumerate(hospital_codes):
                    hosp_sql = self._inject_filters(
                        denominator_sql,
                        [hosp_code],
                        time_mode,
                        time_value,
                        time_col_den,
                    )
                    cnt, err, cols, rows = self._exec_sql(hosp_sql)
                    if not err:
                        den_dict[str(hosp_code)] = float(cnt or 0)
                        if i == 0 and cols and rows:
                            _preview_den_cols = cols
                            _preview_den_rows = rows
                if _preview_den_cols is not None and _preview_den_rows is not None:
                    preview_den_cols = _preview_den_cols
                    preview_den_rows = _preview_den_rows
            elif den_err:
                all_ok = False
                all_logs.append(
                    {
                        "time": _now_ts(),
                        "level": "error",
                        "message": f"分母 SQL 执行出错：{den_err}",
                    }
                )
            else:
                for row in den_rows:
                    key = row.get("MDC_ORG_CD") or row.get("mdc_org_cd")
                    if key:
                        den_dict[str(key)] = float(row.get("denominator_cnt", 0) or 0)
                    elif len(hospital_codes) == 1 and not den_dict:
                        den_dict[hospital_codes[0]] = float(
                            row.get("denominator_cnt", 0) or 0
                        )

            # ③ 遍历医院列表组装结果
            hospital_results: List[Dict[str, Any]] = []
            total_num_cnt = 0.0
            total_den_cnt = 0.0

            # 过滤出指定医院的明细行（用于医院筛选时的预览）
            def _filter_by_hosp(rows, hosp):
                return [r for r in rows if str(r.get("MDC_ORG_CD") or r.get("mdc_org_cd") or "") == str(hosp)]

            for hosp_code in hospital_codes:
                hosp_name = hospital_names.get(str(hosp_code).upper(), hosp_code)
                hosp_num = num_dict.get(str(hosp_code), 0.0)
                hosp_den = den_dict.get(str(hosp_code), 0.0)
                hosp_rate = (
                    round(hosp_num * 100.0 / hosp_den, 4)
                    if hosp_den and hosp_den != 0
                    else None
                )
                total_num_cnt += hosp_num
                total_den_cnt += hosp_den

                # 该医院的原始明细行（智能聚合前保留）
                hosp_num_rows = _filter_by_hosp(preview_num_rows, hosp_code)
                hosp_den_rows = _filter_by_hosp(preview_den_rows, hosp_code)

                hospital_results.append(
                    {
                        "hospital_code": hosp_code,
                        "hospital_name": hosp_name,
                        "numerator_count": int(hosp_num),
                        "denominator_count": int(hosp_den),
                        "ratio_percent": hosp_rate,
                        "status": "success",
                        "preview_data": {
                            "columns": list(hosp_num_rows[0].keys()) if hosp_num_rows else [],
                            "rows": _to_serializable_rows(hosp_num_rows[:10])
                        },
                        "preview_columns": list(hosp_num_rows[0].keys()) if hosp_num_rows else [],
                        "denominator_preview_data": {
                            "columns": list(hosp_den_rows[0].keys()) if hosp_den_rows else [],
                            "rows": _to_serializable_rows(hosp_den_rows[:10])
                        },
                        "denominator_preview_columns": list(hosp_den_rows[0].keys()) if hosp_den_rows else [],
                    }
                )

                all_logs.append(
                    {
                        "time": _now_ts(),
                        "level": "info",
                        "message": f"[{hosp_name}] {int(hosp_num)}/{int(hosp_den)} = {hosp_rate}%",
                    }
                )

            total_rate = (
                round(total_num_cnt * 100.0 / total_den_cnt, 4)
                if total_den_cnt and total_den_cnt != 0
                else None
            )
            all_logs.append(
                {
                    "time": _now_ts(),
                    "level": "info",
                    "message": f"汇总完成。总体指标值：{total_rate}%（{int(total_num_cnt)}/{int(total_den_cnt)}）",
                }
            )

            result = {
                "ok": all_ok,
                "indicator_type": ind_type,
                "numerator_sql": final_num_sql,
                "denominator_sql": final_den_sql,
                "numerator_count": int(total_num_cnt),
                "denominator_count": int(total_den_cnt),
                "rate_percent": total_rate,
                "rate_formula": (
                    f"{int(total_num_cnt)}/{int(total_den_cnt)}={total_rate}%"
                    if total_rate is not None
                    else None
                ),
                "error": None if all_ok else "SQL执行失败",
                "preview_columns": preview_num_cols or [],
                "preview_rows": _to_serializable_rows(preview_num_rows[:10]) if preview_num_rows else [],
                "preview_data": {
                    "columns": preview_num_cols or [],
                    "rows": _to_serializable_rows(preview_num_rows[:10]) if preview_num_rows else [],
                },
                "denominator_preview_columns": preview_den_cols or [],
                "denominator_preview_rows": _to_serializable_rows(preview_den_rows[:10]) if preview_den_rows else [],
                "denominator_preview_data": {
                    "columns": preview_den_cols or [],
                    "rows": _to_serializable_rows(preview_den_rows[:10]) if preview_den_rows else [],
                },
                "request_id": "",
                "conversation_id": "",
                "cache_hit": False,
                "logs": all_logs,
                "duration_seconds": round(time_mod.time() - start_time, 3),
                "group_by_hospital": True,
                "hospital_results": hospital_results,
            }
            if not skip_save:
                db_record_id = self._save_execution_record(
                    result, db_session, indicator_data
                )
            else:
                db_record_id = None
            if db_record_id is not None:
                result["db_record_id"] = db_record_id
            return result

        # ── 不分组执行 ──────────────────────────────────────────────────────
        # 时间过滤始终注入，医院过滤仅在有选择时注入
        num_sql = self._inject_filters(
            numerator_sql,
            hospital_codes=hospital_codes,
            time_mode=time_mode,
            time_value=time_value,
            time_col_name=time_col_num,
            is_aggregate=False,
        )
        den_sql = self._inject_filters(
            denominator_sql,
            hospital_codes=hospital_codes,
            time_mode=time_mode,
            time_value=time_value,
            time_col_name=time_col_den,
            is_aggregate=False,
        )
        num_cnt, num_err, num_cols, num_rows = self._exec_sql(num_sql)
        den_cnt, den_err, den_cols, den_rows = self._exec_sql(den_sql)

        rate = (
            round(num_cnt * 100.0 / den_cnt, 4)
            if (den_cnt and num_cnt is not None and den_cnt != 0)
            else None
        )
        ok = (
            num_err is None
            and den_err is None
            and num_cnt is not None
            and den_cnt is not None
        )
        duration = round(time_mod.time() - start_time, 3)
        logs: List[Dict[str, Any]] = []
        if ok:
            logs = [
                {"time": _now_ts(), "level": "info", "message": "执行分子 SQL..."},
                {
                    "time": _now_ts(),
                    "level": "info",
                    "message": f"分子结果：{num_cnt} 条记录。",
                },
                {"time": _now_ts(), "level": "info", "message": "执行分母 SQL..."},
                {
                    "time": _now_ts(),
                    "level": "info",
                    "message": f"分母结果：{den_cnt} 条记录。",
                },
                {
                    "time": _now_ts(),
                    "level": "info",
                    "message": f"执行完成。指标值：{rate}%（{num_cnt}/{den_cnt}）",
                },
            ]
        else:
            logs = [
                {"time": _now_ts(), "level": "info", "message": "执行分子 SQL..."},
                {
                    "time": _now_ts(),
                    "level": "info",
                    "message": (
                        f"分子结果：{num_cnt} 条记录。"
                        if num_cnt is not None
                        else f"分子执行出错：{num_err}"
                    ),
                },
                {"time": _now_ts(), "level": "info", "message": "执行分母 SQL..."},
                {
                    "time": _now_ts(),
                    "level": "info",
                    "message": (
                        f"分母结果：{den_cnt} 条记录。"
                        if den_cnt is not None
                        else f"分母执行出错：{den_err}"
                    ),
                },
                {
                    "time": _now_ts(),
                    "level": "error",
                    "message": f"执行失败：{num_err or den_err}",
                },
            ]

        result = {
            "ok": ok,
            "indicator_type": ind_type,
            "numerator_sql": numerator_sql,
            "denominator_sql": denominator_sql,
            "numerator_count": num_cnt,
            "denominator_count": den_cnt,
            "rate_percent": rate,
            "rate_formula": (
                f"{num_cnt}/{den_cnt}={rate}%" if rate is not None else None
            ),
            "error": num_err or den_err or None,
            "numerator_error": num_err,
            "denominator_error": den_err,
            "preview_columns": num_cols,
            "preview_rows": _to_serializable_rows(num_rows),
            "preview_data": {
                "columns": num_cols,
                "rows": _to_serializable_rows(num_rows),
            },
            "denominator_preview_columns": den_cols,
            "denominator_preview_rows": _to_serializable_rows(den_rows),
            "denominator_preview_data": {
                "columns": den_cols,
                "rows": _to_serializable_rows(den_rows),
            },
            "numerator_attempts": [
                {"attempt": 1, "sql": numerator_sql, "count": num_cnt, "error": num_err}
            ],
            "denominator_attempts": [
                {"attempt": 1, "sql": denominator_sql, "count": den_cnt, "error": den_err}
            ],
            "request_id": "",
            "conversation_id": "",
            "cache_hit": False,
            "logs": logs,
            "duration_seconds": duration,
        }
        if not skip_save:
            db_record_id = self._save_execution_record(result, db_session, indicator_data)
        else:
            db_record_id = None
        if db_record_id is not None:
            result["db_record_id"] = db_record_id
        return result

    # -------------------------------------------------------------------------
    # 策略 2：复合率型
    # -------------------------------------------------------------------------

    def _execute_composite_rate(
        self,
        sql_to_exec: str,
        subitem_config: Dict[str, Any],
        ind_type: str,
        hospital_codes: Optional[List[str]],
        time_mode: Optional[str],
        time_value: Optional[str],
        time_col_num: str,
        group_by_hospital: bool,
        hospital_names: Dict[str, str],
        db_session,
        indicator_data: Dict[str, Any],
        skip_save: bool,
        start_time: float,
    ) -> Dict[str, Any]:
        """复合率型指标执行器"""

        def _calc_composite_rate(exec_sql_str: str) -> Tuple:
            """内部：对给定 SQL 计算各子项的分子/分母/比率"""
            cnt, err, cols, rows = self._exec_sql(
                exec_sql_str, include_rows=True, fetch_all=True
            )
            if err or not rows:
                return cnt, err, cols, rows, [], 0, None
            row = rows[0]
            sub = []
            hosp_num = 0
            hosp_den: Optional[float] = None
            for item_cfg in items_config:
                num_col = item_cfg.get("numerator_col", "")
                den_col = item_cfg.get("denominator_col", "")
                num_v = self._parse_numeric(row.get(num_col))
                den_v = self._parse_numeric(row.get(den_col))
                rate_v = (
                    round(num_v * 100.0 / den_v, 4)
                    if (den_v and num_v is not None and den_v != 0)
                    else None
                )
                if num_v is not None:
                    hosp_num += num_v
                if den_v is not None and hosp_den is None:
                    hosp_den = den_v
                sub.append({
                    "key": item_cfg.get("key", ""),
                    "name": item_cfg.get("name", ""),
                    "numerator": num_v,
                    "denominator": den_v,
                    "rate": rate_v,
                })
            return cnt, None, cols, rows, sub, hosp_num, hosp_den

        items_config = subitem_config.get("items", [])
        all_logs: List[Dict[str, Any]] = []
        hospital_results: List[Dict[str, Any]] = []
        total_num_overall = 0.0
        total_den_overall: Optional[float] = None
        all_ok = True

        # ── 按医院分组执行 ──────────────────────────────────────────────────
        if group_by_hospital and hospital_codes and len(hospital_codes) > 0:
            for hosp_code in hospital_codes:
                hosp_name = hospital_names.get(hosp_code.upper(), hosp_code)
                hosp_logs = [
                    {"time": _now_ts(), "level": "info", "message": f"[{hosp_name}] 开始执行..."}
                ]
                hosp_exec_sql = self._inject_filters(
                    sql_to_exec, [hosp_code], time_mode, time_value, time_col_num
                )
                cnt, err, cols, rows, sub_data, hosp_num, hosp_den = _calc_composite_rate(
                    hosp_exec_sql
                )
                hosp_ok = err is None
                if not hosp_ok:
                    all_ok = False
                total_num_overall += hosp_num or 0
                if hosp_den is not None and total_den_overall is None:
                    total_den_overall = hosp_den
                hosp_logs.append(
                    {
                        "time": _now_ts(),
                        "level": "info",
                        "message": f"[{hosp_name}] 分子：{hosp_num}，分母：{hosp_den}",
                    }
                )
                for item in sub_data:
                    hosp_logs.append(
                        {
                            "time": _now_ts(),
                            "level": "info",
                            "message": f"  子项【{item['name']}】：{item['numerator']}/{item['denominator']} = {item['rate']}%",
                        }
                    )
                hospital_results.append({
                    "hospital_code": hosp_code,
                    "hospital_name": hosp_name,
                    "numerator_count": hosp_num,
                    "denominator_count": hosp_den,
                    "ratio_percent": (
                        round(hosp_num * 100.0 / hosp_den, 4)
                        if (hosp_den and hosp_num is not None and hosp_den != 0)
                        else None
                    ),
                    "status": "success" if hosp_ok else "failed",
                    "error": err,
                    "preview_data": {
                        "columns": list(rows[0].keys()) if rows else [],
                        "rows": _to_serializable_rows(rows[:10])
                    } if rows else {"columns": [], "rows": []},
                })
                all_logs.extend(hosp_logs)

            total_rate_overall = (
                round(total_num_overall * 100.0 / total_den_overall, 4)
                if (total_den_overall and total_num_overall > 0 and total_den_overall != 0)
                else None
            )
            all_logs.append(
                {
                    "time": _now_ts(),
                    "level": "info",
                    "message": f"全省汇总：{total_num_overall}/{total_den_overall}={total_rate_overall}%",
                }
            )
            first_preview_data = hospital_results[0].get("preview_data") if hospital_results else None
            first_rows = first_preview_data.get("rows", []) if first_preview_data else []
            first_cols = first_preview_data.get("columns", []) if first_preview_data else []

            result = {
                "ok": all_ok,
                "indicator_type": ind_type,
                "sql": sql_to_exec,
                "numerator_count": total_num_overall,
                "denominator_count": total_den_overall,
                "rate_percent": total_rate_overall,
                "rate_formula": (
                    f"{total_num_overall}/{total_den_overall}={total_rate_overall}%"
                    if total_rate_overall is not None
                    else None
                ),
                "error": None if all_ok else "部分医院执行失败",
                "preview_columns": first_cols,
                "preview_rows": first_rows,
                "preview_data": {"columns": first_cols, "rows": first_rows},
                "request_id": "",
                "conversation_id": "",
                "cache_hit": False,
                "logs": all_logs,
                "duration_seconds": round(time_mod.time() - start_time, 3),
                "group_by_hospital": True,
                "hospital_results": hospital_results,
                "subitem_data": (
                    _to_serializable_any(hospital_results[0].get("preview_data"))
                    if hospital_results
                    else None
                ),
            }
            if not skip_save:
                db_record_id = self._save_execution_record(
                    result, db_session, indicator_data
                )
            else:
                db_record_id = None
            if db_record_id is not None:
                result["db_record_id"] = db_record_id
            return result

        # ── 不分组执行 ──────────────────────────────────────────────────────
        exec_sql = self._inject_filters(
            sql_to_exec, hospital_codes, time_mode, time_value, time_col_num
        )
        cnt, err, cols, rows, sub_data, hosp_num, hosp_den = _calc_composite_rate(
            exec_sql
        )
        if err:
            all_logs.append(
                {"time": _now_ts(), "level": "error", "message": f"SQL 执行出错：{err}"}
            )
            result = {
                "ok": False,
                "indicator_type": ind_type,
                "error": err,
                "logs": all_logs,
            }
            if not skip_save:
                db_record_id = self._save_execution_record(
                    result, db_session, indicator_data
                )
            else:
                db_record_id = None
            if db_record_id is not None:
                result["db_record_id"] = db_record_id
            return result

        all_logs.append(
            {"time": _now_ts(), "level": "info", "message": f"SQL 执行完成，共 {cnt} 条记录。"}
        )
        all_logs.append(
            {
                "time": _now_ts(),
                "level": "info",
                "message": f"总分子：{hosp_num}，总分母：{hosp_den}",
            }
        )
        for item in sub_data:
            all_logs.append(
                {
                    "time": _now_ts(),
                    "level": "info",
                    "message": f"  子项【{item['name']}】：{item['numerator']}/{item['denominator']} = {item['rate']}%",
                }
            )
        total_rate_overall = (
            round(hosp_num * 100.0 / hosp_den, 4)
            if (hosp_den and hosp_num is not None and hosp_den != 0)
            else None
        )
        result = {
            "ok": True,
            "indicator_type": ind_type,
            "sql": exec_sql,
            "numerator_count": hosp_num,
            "denominator_count": hosp_den,
            "rate_percent": total_rate_overall,
            "rate_formula": (
                f"{hosp_num}/{hosp_den}={total_rate_overall}%"
                if total_rate_overall is not None
                else None
            ),
            "error": None,
            "preview_columns": cols or [],
            "preview_rows": _to_serializable_rows(rows[:20]) if rows else [],
            "preview_data": {
                "columns": cols or [],
                "rows": _to_serializable_rows(rows[:20]) if rows else [],
            },
            "request_id": "",
            "conversation_id": "",
            "cache_hit": False,
            "logs": all_logs,
            "duration_seconds": round(time_mod.time() - start_time, 3),
            "subitem_data": _to_serializable_any(sub_data),
        }
        if not skip_save:
            db_record_id = self._save_execution_record(result, db_session, indicator_data)
        else:
            db_record_id = None
        if db_record_id is not None:
            result["db_record_id"] = db_record_id
        return result

    # -------------------------------------------------------------------------
    # 策略 3：复合排行型
    # -------------------------------------------------------------------------

    def _execute_composite_ranking(
        self,
        sql_to_exec: str,
        subitem_config: Dict[str, Any],
        ind_type: str,
        hospital_codes: Optional[List[str]],
        time_mode: Optional[str],
        time_value: Optional[str],
        time_col_num: str,
        group_by_hospital: bool,
        hospital_names: Dict[str, str],
        db_session,
        indicator_data: Dict[str, Any],
        skip_save: bool,
        start_time: float,
    ) -> Dict[str, Any]:
        """复合计数型/排行榜型指标执行器"""

        def _safe_float(v: Any) -> float:
            if v is None:
                return 0.0
            try:
                return float(v)
            except (ValueError, TypeError):
                return 0.0

        ranking_key_field = subitem_config.get("ranking_key_field", "ranking_key")
        ranking_value_field = subitem_config.get("ranking_value_field", "ranking_value")
        total_agg_field = subitem_config.get("total_aggregation_field", ranking_value_field)
        ranking_limit = subitem_config.get("limit", 20)

        all_logs: List[Dict[str, Any]] = []
        hospital_results: List[Dict[str, Any]] = []
        total_count_overall = 0.0
        all_ok = True
        all_hospital_ranking_items: List[Dict[str, Any]] = []

        # ── 按医院分组执行 ──────────────────────────────────────────────────
        if group_by_hospital and hospital_codes and len(hospital_codes) > 0:
            for hosp_code in hospital_codes:
                hosp_name = hospital_names.get(hosp_code.upper(), hosp_code)
                hosp_logs = [
                    {"time": _now_ts(), "level": "info", "message": f"[{hosp_name}] 开始执行..."}
                ]
                hosp_exec_sql = self._inject_filters(
                    sql_to_exec, [hosp_code], time_mode, time_value, time_col_num
                )
                total_cnt, total_err, cols, rows = self._exec_sql(
                    hosp_exec_sql, include_rows=True, fetch_all=True
                )
                hosp_ok = total_err is None
                if not hosp_ok:
                    all_ok = False
                hosp_logs.append(
                    {
                        "time": _now_ts(),
                        "level": "info",
                        "message": f"[{hosp_name}] SQL完成，共 {total_cnt} 条记录。",
                    }
                )
                hosp_total_count = sum(
                    _safe_float(r.get(total_agg_field, 0)) for r in rows
                )
                total_count_overall += hosp_total_count
                hosp_ranked = sorted(
                    rows,
                    key=lambda r: _safe_float(r.get(ranking_value_field, 0)),
                    reverse=True,
                )
                hosp_ranked = hosp_ranked[:ranking_limit]
                hosp_sub_data: List[Dict[str, Any]] = []
                for r in hosp_ranked:
                    item = {
                        "ranking_key": r.get(ranking_key_field, ""),
                        "ranking_value": _safe_float(r.get(ranking_value_field, 0)),
                        **r,
                    }
                    hosp_sub_data.append(item)
                    all_hospital_ranking_items.append(
                        {**item, "_hospital_code": hosp_code, "_hospital_name": hosp_name}
                    )
                hosp_preview = _to_serializable_rows(hosp_ranked)
                hospital_results.append({
                    "hospital_code": hosp_code,
                    "hospital_name": hosp_name,
                    "numerator_count": int(hosp_total_count),
                    "count": int(hosp_total_count),
                    "status": "success" if hosp_ok else "failed",
                    "error": total_err,
                    "preview_data": {
                        "columns": list(hosp_ranked[0].keys()) if hosp_ranked else [],
                        "rows": _to_serializable_rows(hosp_ranked)
                    } if hosp_ranked else {"columns": [], "rows": []},
                    "preview_columns": list(hosp_ranked[0].keys()) if hosp_ranked else [],
                    "subitem_data": hosp_sub_data,
                })
                hosp_logs.append(
                    {
                        "time": _now_ts(),
                        "level": "info",
                        "message": f"[{hosp_name}] 总数：{int(hosp_total_count)}，排行TOP{ranking_limit}已生成。",
                    }
                )
                all_logs.extend(hosp_logs)

            # 构建全省全局排行榜
            from collections import defaultdict

            has_death_type = any("death_type" in str(r) for r in rows)
            if has_death_type:
                global_agg: Dict = defaultdict(lambda: defaultdict(float))
                for item in all_hospital_ranking_items:
                    key = str(item.get("ranking_key", ""))
                    d_type = str(item.get("death_type") or "")
                    global_agg[key][d_type] += item.get("ranking_value", 0.0)
                global_subitem_data: List[Dict[str, Any]] = []
                for rank_key, type_vals in global_agg.items():
                    for d_type, rank_val in type_vals.items():
                        global_subitem_data.append({
                            "ranking_key": rank_key,
                            "ranking_value": rank_val,
                            "death_type": d_type,
                        })
            else:
                global_agg = defaultdict(float)
                for item in all_hospital_ranking_items:
                    key = str(item.get("ranking_key", ""))
                    global_agg[key] += item.get("ranking_value", 0.0)
                global_subitem_data = [
                    {"ranking_key": rank_key, "ranking_value": rank_val}
                    for rank_key, rank_val in global_agg.items()
                ]
            all_logs.append(
                {
                    "time": _now_ts(),
                    "level": "info",
                    "message": f"全省汇总：总数量={int(total_count_overall)}，全局TOP{ranking_limit}排行已生成。",
                }
            )
            first_preview_data = hospital_results[0].get("preview_data") if hospital_results else None
            first_rows = first_preview_data.get("rows", []) if first_preview_data else []
            first_cols = first_preview_data.get("columns", []) if first_preview_data else []

            result = {
                "ok": all_ok,
                "indicator_type": ind_type,
                "sql": sql_to_exec,
                "count": int(total_count_overall),
                "numerator_count": int(total_count_overall),
                "error": None if all_ok else "部分医院执行失败",
                "preview_columns": first_cols,
                "preview_rows": first_rows,
                "preview_data": {"columns": first_cols, "rows": first_rows},
                "request_id": "",
                "conversation_id": "",
                "cache_hit": False,
                "logs": all_logs,
                "duration_seconds": round(time_mod.time() - start_time, 3),
                "group_by_hospital": True,
                "hospital_results": hospital_results,
                "subitem_data": _to_serializable_any(global_subitem_data),
            }
            if not skip_save:
                db_record_id = self._save_execution_record(
                    result, db_session, indicator_data
                )
            else:
                db_record_id = None
            if db_record_id is not None:
                result["db_record_id"] = db_record_id
            return result

        # ── 不分组执行 ──────────────────────────────────────────────────────
        exec_sql = self._inject_filters(
            sql_to_exec, hospital_codes, time_mode, time_value, time_col_num
        )
        total_cnt, total_err, cols, rows = self._exec_sql(
            exec_sql, include_rows=True, fetch_all=True
        )
        logs = [{"time": _now_ts(), "level": "info", "message": "执行复合计数型指标 SQL..."}]
        if total_err:
            logs.append(
                {"time": _now_ts(), "level": "error", "message": f"SQL 执行出错：{total_err}"}
            )
            result = {
                "ok": False,
                "indicator_type": ind_type,
                "error": total_err,
                "logs": logs,
            }
            if not skip_save:
                db_record_id = self._save_execution_record(
                    result, db_session, indicator_data
                )
            else:
                db_record_id = None
            if db_record_id is not None:
                result["db_record_id"] = db_record_id
            return result

        total_count = sum(_safe_float(r.get(total_agg_field, 0)) for r in rows)
        ranked_rows = sorted(
            rows, key=lambda r: _safe_float(r.get(ranking_value_field, 0)), reverse=True
        )
        ranked_rows = ranked_rows[:ranking_limit]
        subitem_data: List[Dict[str, Any]] = []
        for r in ranked_rows:
            subitem_data.append({
                "ranking_key": r.get(ranking_key_field, ""),
                "ranking_value": _safe_float(r.get(ranking_value_field, 0)),
                **r,
            })
        logs.extend([
            {
                "time": _now_ts(),
                "level": "info",
                "message": f"SQL 执行完成，共 {total_cnt} 条记录。",
            },
            {
                "time": _now_ts(),
                "level": "info",
                "message": f"总数量：{int(total_count)}，TOP{ranking_limit}排行已生成。",
            },
        ])
        result = {
            "ok": True,
            "indicator_type": ind_type,
            "sql": exec_sql,
            "count": int(total_count),
            "numerator_count": int(total_count),
            "error": None,
            "preview_columns": cols or [],
            "preview_rows": _to_serializable_rows(ranked_rows),
            "preview_data": {
                "columns": cols or [],
                "rows": _to_serializable_rows(ranked_rows),
            },
            "request_id": "",
            "conversation_id": "",
            "cache_hit": False,
            "logs": logs,
            "duration_seconds": round(time_mod.time() - start_time, 3),
            "subitem_data": _to_serializable_any(subitem_data),
        }
        if not skip_save:
            db_record_id = self._save_execution_record(result, db_session, indicator_data)
        else:
            db_record_id = None
        if db_record_id is not None:
            result["db_record_id"] = db_record_id
        return result

    # -------------------------------------------------------------------------
    # 策略 4：计数型
    # -------------------------------------------------------------------------

    def _execute_count_indicator(
        self,
        sql_to_exec: str,
        ind_type: str,
        calc_type_raw: str,
        hospital_codes: Optional[List[str]],
        time_mode: Optional[str],
        time_value: Optional[str],
        time_col_num: str,
        time_col_den: str,
        group_by_hospital: bool,
        hospital_names: Dict[str, str],
        db_session,
        indicator_data: Dict[str, Any],
        skip_save: bool,
        start_time: float,
    ) -> Dict[str, Any]:
        """计数型指标执行器"""
        logger.info(
            f"[计数型 group_by] group_by_hospital={group_by_hospital}, "
            f"hospital_codes={hospital_codes}, "
            f"len={len(hospital_codes) if hospital_codes else 0}, "
            f"sql_to_exec={bool(sql_to_exec)}"
        )

        # ── 按医院分组执行 ──────────────────────────────────────────────────
        if group_by_hospital and hospital_codes and len(hospital_codes) > 0 and sql_to_exec:
            hospital_results: List[Dict[str, Any]] = []
            total_count = 0
            all_ok = True
            all_logs: List[Dict[str, Any]] = []
            all_preview_rows: List[Dict[str, Any]] = []
            all_preview_cols: List[str] = []

            for hosp_code in hospital_codes:
                hosp_name = hospital_names.get(hosp_code.upper(), hosp_code)
                hosp_logs = [
                    {"time": _now_ts(), "level": "info", "message": f"[{hosp_name}] 开始执行..."}
                ]
                hosp_sql = self._inject_filters(
                    sql_to_exec,
                    [hosp_code],
                    time_mode,
                    time_value,
                    time_col_num or "discharge",
                    time_col_den or "discharge",
                )
                # 替换 {{time_value_start}} / {{time_value_end}} / {{time_value}} 为实际值
                if "{{time_value" in hosp_sql:
                    start_dt, end_dt = _build_time_range(time_mode, time_value)
                    hosp_sql = hosp_sql.replace("{{time_value_start}}", start_dt).replace("{{time_value_end}}", end_dt)
                    # {{time_value}} 用月份字符串（如 2026-04）替换，适配 SUBSTR 比对
                    month_str = time_value if (time_mode == "monthly") else time_value
                    hosp_sql = hosp_sql.replace("{{time_value}}", month_str)
                hosp_cnt, hosp_err, hosp_cols, hosp_rows = self._exec_sql(hosp_sql)

                stat_count = hosp_cnt
                if hosp_cols and hosp_rows and "patient_cnt" in hosp_cols:
                    total = sum(float(r.get("patient_cnt") or 0) for r in hosp_rows)
                    stat_count = int(total)

                hosp_ok = hosp_err is None
                if not hosp_ok:
                    all_ok = False
                total_count += stat_count or 0
                hosp_logs.extend([
                    {
                        "time": _now_ts(),
                        "level": "info",
                        "message": f"[{hosp_name}] 查询结果：{hosp_cnt} 条记录。",
                    },
                    {
                        "time": _now_ts(),
                        "level": "info",
                        "message": f"[{hosp_name}] 执行完成，共 {stat_count} 人次。",
                    },
                ])
                if hosp_err:
                    hosp_logs.append(
                        {
                            "time": _now_ts(),
                            "level": "error",
                            "message": f"[{hosp_name}] 执行出错：{hosp_err}",
                        }
                    )
                preview = _to_serializable_rows(hosp_rows[:10]) if hosp_rows else []
                if preview:
                    all_preview_rows.extend(preview)
                    if not all_preview_cols:
                        all_preview_cols = list(preview[0].keys()) if preview else []

                hospital_results.append({
                    "hospital_code": hosp_code,
                    "hospital_name": hosp_name,
                    "numerator_count": stat_count,
                    "count": stat_count,
                    "status": "success" if hosp_ok else "failed",
                    "error": hosp_err,
                    "preview_data": {
                        "columns": list(preview[0].keys()) if preview else [],
                        "rows": _to_serializable_rows(preview)
                    } if preview else {"columns": [], "rows": []},
                    "preview_columns": list(preview[0].keys()) if preview else [],
                })
                all_logs.extend(hosp_logs)

            all_logs.append(
                {
                    "time": _now_ts(),
                    "level": "info",
                    "message": f"汇总执行完成，共 {total_count} 人次。",
                }
            )
            duration = round(time_mod.time() - start_time, 3)
            result = {
                "ok": all_ok,
                "indicator_type": ind_type,
                "indicator": {"calc_type": calc_type_raw},
                "calc_type": calc_type_raw,
                "sql": sql_to_exec,
                "count": total_count,
                "numerator_count": total_count,
                "error": None if all_ok else "部分医院执行失败",
                "preview_columns": all_preview_cols,
                "preview_rows": all_preview_rows,
                "preview_data": {
                    "columns": all_preview_cols,
                    "rows": all_preview_rows,
                },
                "request_id": "",
                "conversation_id": "",
                "cache_hit": False,
                "logs": all_logs,
                "duration_seconds": duration,
                "group_by_hospital": True,
                "hospital_results": hospital_results,
            }
            if not skip_save:
                db_record_id = self._save_execution_record(
                    result, db_session, indicator_data
                )
            else:
                db_record_id = None
            if db_record_id is not None:
                result["db_record_id"] = db_record_id
            return result

        # ── 不分组执行 ──────────────────────────────────────────────────────
        if sql_to_exec:
            sql_to_exec = self._inject_filters(
                sql_to_exec,
                hospital_codes,
                time_mode,
                time_value,
                time_col_num,
            )

        if not sql_to_exec:
            return {"ok": False, "error": "无 SQL 可执行", "indicator_type": ind_type}

        cnt, err, cols, rows = self._exec_sql(sql_to_exec)
        calc_type = indicator_data.get("calc_type") or "ratio"
        stat_count = cnt
        if cols and rows and "patient_cnt" in cols:
            total = sum(float(r.get("patient_cnt") or 0) for r in rows)
            stat_count = int(total)

        # 计算 subitem_data（排行榜 TOP20），用于 STRUCTURE 型指标展示
        subitem_data: Optional[List[Dict[str, Any]]] = None
        if cols and rows and not err:
            ranking_key_col: Optional[str] = None
            ranking_val_col: Optional[str] = None
            for col in cols:
                col_lower = col.lower()
                if any(
                    k in col_lower
                    for k in ["diag_cd", "icd", "code", " oprt_cd", "科室", "dept", "名称", "name"]
                ):
                    ranking_key_col = col
                    break
            if ranking_key_col:
                for col in cols:
                    col_lower = col.lower()
                    if any(
                        k in col_lower
                        for k in ["cnt", "count", "人次", "num", "患者"]
                    ):
                        ranking_val_col = col
                        break
            if not ranking_val_col:
                ranking_val_col = cols[1] if len(cols) > 1 else None
            if ranking_key_col and ranking_val_col:
                ranked: List[Dict[str, Any]] = []
                for r in rows:
                    key = r.get(ranking_key_col) or r.get(ranking_key_col.lower()) or ""
                    val = r.get(ranking_val_col) or r.get(ranking_val_col.lower()) or 0
                    if key:
                        try:
                            ranked.append({"ranking_key": str(key), "ranking_value": float(val)})
                        except (ValueError, TypeError):
                            pass
                ranked.sort(key=lambda x: x["ranking_value"], reverse=True)
                subitem_data = ranked[:20]

        logs: List[Dict[str, Any]] = []
        if err is None and cnt is not None:
            logs = [
                {"time": _now_ts(), "level": "info", "message": "执行 SQL..."},
                {
                    "time": _now_ts(),
                    "level": "info",
                    "message": f"查询结果：{cnt} 条记录。",
                },
                {
                    "time": _now_ts(),
                    "level": "info",
                    "message": f"执行完成，共 {stat_count} 人次。",
                },
            ]
        else:
            logs = [
                {"time": _now_ts(), "level": "info", "message": "执行 SQL..."},
                {"time": _now_ts(), "level": "error", "message": f"执行失败：{err}"},
            ]
        duration = round(time_mod.time() - start_time, 3)
        result = {
            "ok": err is None and cnt is not None,
            "indicator_type": ind_type,
            "indicator": {"calc_type": calc_type},
            "calc_type": calc_type,
            "sql": sql_to_exec,
            "count": stat_count,
            "subitem_data": subitem_data,
            "error": err,
            "preview_columns": cols,
            "preview_rows": _to_serializable_rows(rows),
            "preview_data": {
                "columns": cols,
                "rows": _to_serializable_rows(rows),
            },
            "attempts": [
                {"attempt": 1, "sql": sql_to_exec, "count": stat_count, "error": err}
            ],
            "request_id": "",
            "conversation_id": "",
            "cache_hit": False,
            "logs": logs,
            "duration_seconds": duration,
        }
        if not skip_save:
            db_record_id = self._save_execution_record(result, db_session, indicator_data)
        else:
            db_record_id = None
        if db_record_id is not None:
            result["db_record_id"] = db_record_id
        return result

    # -------------------------------------------------------------------------
    # 主入口：execute_indicator（路由层）
    # -------------------------------------------------------------------------

    def execute_indicator(
        self,
        indicator_data: Dict[str, Any],
        db_session=None,
        skip_save: bool = False,
    ) -> Dict[str, Any]:
        """
        指标执行主入口。

        优先直接执行已保存的 SQL（不走 LLM）；
        若无保存 SQL 才调用 text2sql 服务生成。

        根据 calc_type / subitem_config 路由到四个策略方法之一：
        1. _execute_ratio_indicator      → 比值型
        2. _execute_composite_rate       → 复合率型
        3. _execute_composite_ranking    → 复合排行型
        4. _execute_count_indicator      → 计数型
        """
        start_time = time_mod.time()

        # ── 提取 SQL ──────────────────────────────────────────────────────────
        numerator_sql = (
            indicator_data.get("numerator_sql") or indicator_data.get("numerator_sql") or ""
        )
        denominator_sql = (
            indicator_data.get("denominator_sql")
            or indicator_data.get("denominator_sql")
            or ""
        )
        single_sql = indicator_data.get("sql") or indicator_data.get("sql_content") or ""
        ind_type = (
            indicator_data.get("indicator_type") or indicator_data.get("类型") or ""
        )

        # ── 提取元字段 ───────────────────────────────────────────────────────
        kind = indicator_data.get("kind") or indicator_data.get("business_type") or "core18"
        run_mode = indicator_data.get("run_mode") or "immediate"
        time_range = indicator_data.get("time_range") or "全量"
        result_type = indicator_data.get("result_type") or "ratio"
        calc_method = indicator_data.get("calc_method") or "SQL录入"

        # ── 医院过滤参数 ────────────────────────────────────────────────────
        raw_codes = indicator_data.get("hospital_codes")
        # 空数组规范为 None（全省模式由后端展开）
        hospital_codes: Optional[List[str]] = raw_codes if (raw_codes and len(raw_codes) > 0) else None
        time_mode: Optional[str] = indicator_data.get("time_mode")
        time_value: Optional[str] = indicator_data.get("time_value")
        date_field = indicator_data.get("date_field", "discharge")
        group_by_hospital = indicator_data.get("group_by_hospital", True)

        logger.info(
            f"[医院过滤] hospital_codes={hospital_codes}, "
            f"time_mode={time_mode}, time_value={time_value}, "
            f"group_by_hospital={group_by_hospital}"
        )

        # ── 医院名称映射 + 全省展开 ──────────────────────────────────────────
        hospital_names = self._get_hospital_names()
        all_hospitals: List[Dict[str, Any]] = []
        if self._sql_runner_get_hospitals:
            try:
                all_hospitals = self._sql_runner_get_hospitals()
            except Exception:
                pass

        if group_by_hospital and not hospital_codes and all_hospitals:
            hospital_codes = [h.get("MDC_ORG_CD") for h in all_hospitals]
            logger.info(f"[医院过滤] 全省模式，展开医院列表，共 {len(hospital_codes)} 家医院")

        # ── 时间字段映射（分子/分母各自独立）───────────────────────────────
        # numerator_date_field / denominator_date_field：来自DB字段，支持分子分母时间过滤不同
        # date_field：兜底默认值（兼容旧数据）
        raw_num_date  = indicator_data.get("numerator_date_field") or indicator_data.get("date_field") or "discharge"
        raw_den_date  = indicator_data.get("denominator_date_field") or indicator_data.get("date_field") or "discharge"
        time_col_num  = self._resolve_time_col(raw_num_date)
        time_col_den  = self._resolve_time_col(raw_den_date)
        logger.info(
            f"[时间字段] numerator_date_field={raw_num_date} -> {time_col_num}, "
            f"denominator_date_field={raw_den_date} -> {time_col_den}"
        )

        # ── 计数型标志 ──────────────────────────────────────────────────────
        calc_type_raw = indicator_data.get("calc_type") or "ratio"
        is_count_type = calc_type_raw == "count"

        # ── 路由分发 ────────────────────────────────────────────────────────
        subitem_config = indicator_data.get("subitem_config")

        # 策略 1：比值型（分子分母 SQL + 非计数型）
        if numerator_sql and denominator_sql and not is_count_type:
            return self._execute_ratio_indicator(
                numerator_sql=numerator_sql,
                denominator_sql=denominator_sql,
                ind_type=ind_type,
                hospital_codes=hospital_codes,
                time_mode=time_mode,
                time_value=time_value,
                time_col_num=time_col_num,
                time_col_den=time_col_den,
                group_by_hospital=group_by_hospital,
                hospital_names=hospital_names,
                db_session=db_session,
                indicator_data=indicator_data,
                skip_save=skip_save,
                start_time=start_time,
            )

        # 策略 2 & 3：复合指标（subitem_config 非空）
        sql_to_exec = single_sql if single_sql else (
            numerator_sql if is_count_type else ""
        )
        if subitem_config and sql_to_exec:
            config_type = subitem_config.get("type")
            if config_type == "COMPOSITE_RATE":
                return self._execute_composite_rate(
                    sql_to_exec=sql_to_exec,
                    subitem_config=subitem_config,
                    ind_type=ind_type,
                    hospital_codes=hospital_codes,
                    time_mode=time_mode,
                    time_value=time_value,
                    time_col_num=time_col_num,
                    group_by_hospital=group_by_hospital,
                    hospital_names=hospital_names,
                    db_session=db_session,
                    indicator_data=indicator_data,
                    skip_save=skip_save,
                    start_time=start_time,
                )
            if config_type == "COMPOSITE_RANKING":
                return self._execute_composite_ranking(
                    sql_to_exec=sql_to_exec,
                    subitem_config=subitem_config,
                    ind_type=ind_type,
                    hospital_codes=hospital_codes,
                    time_mode=time_mode,
                    time_value=time_value,
                    time_col_num=time_col_num,
                    group_by_hospital=group_by_hospital,
                    hospital_names=hospital_names,
                    db_session=db_session,
                    indicator_data=indicator_data,
                    skip_save=skip_save,
                    start_time=start_time,
                )

        # 策略 4：计数型
        if sql_to_exec or is_count_type:
            return self._execute_count_indicator(
                sql_to_exec=sql_to_exec,
                ind_type=ind_type,
                calc_type_raw=calc_type_raw,
                hospital_codes=hospital_codes,
                time_mode=time_mode,
                time_value=time_value,
                time_col_num=time_col_num,
                time_col_den=time_col_den,
                group_by_hospital=group_by_hospital,
                hospital_names=hospital_names,
                db_session=db_session,
                indicator_data=indicator_data,
                skip_save=skip_save,
                start_time=start_time,
            )

        # ── 无保存 SQL，走 text2sql 服务生成 ──────────────────────────────
        try:
            request_data: Dict[str, Any] = {
                "indicator_index": (
                    indicator_data.get("indicator_index") or indicator_data.get("id")
                ),
                "indicator_name": (
                    indicator_data.get("indicator_name") or indicator_data.get("name", "")
                ),
                "selected_tables": (
                    indicator_data.get("selected_tables")
                    or indicator_data.get("involved_tables", [])
                ),
                "indicator_formula": (
                    indicator_data.get("indicator_formula")
                    or indicator_data.get("formula")
                    or indicator_data.get("rule_logic", "")
                ),
                "numerator_desc": indicator_data.get("numerator_desc", ""),
                "denominator_desc": indicator_data.get("denominator_desc", ""),
                "indicator_desc": (
                    indicator_data.get("indicator_desc")
                    or indicator_data.get("description", "")
                ),
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
            result["duration_seconds"] = round(time_mod.time() - start_time, 3)

            if "preview_data" not in result:
                result["preview_data"] = {
                    "columns": result.get("preview_columns", []),
                    "rows": _to_serializable_rows(result.get("preview_rows", [])),
                }
            else:
                if "rows" in result["preview_data"]:
                    result["preview_data"]["rows"] = _to_serializable_rows(
                        result["preview_data"]["rows"]
                    )
            if (
                "denominator_preview_data" in result
                and "rows" in result["denominator_preview_data"]
            ):
                result["denominator_preview_data"]["rows"] = _to_serializable_rows(
                    result["denominator_preview_data"]["rows"]
                )
            elif result.get("denominator_preview_rows"):
                result["denominator_preview_data"] = {
                    "rows": _to_serializable_rows(result.get("denominator_preview_rows", [])),
                    "columns": result.get("denominator_preview_columns", []),
                }

            if not skip_save:
                db_record_id = self._save_execution_record(
                    result, db_session, indicator_data
                )
            else:
                db_record_id = None
            if db_record_id is not None:
                result["db_record_id"] = db_record_id
            return result

        except httpx.HTTPError as e:
            logger.error(f"执行指标失败 (HTTP): {e}")
            return {
                "ok": False,
                "error": f"HTTP错误: {str(e)}",
                "indicator_type": indicator_data.get("indicator_type", "unknown"),
            }
        except Exception as e:
            logger.error(f"执行指标失败: {e}")
            return {
                "ok": False,
                "error": str(e),
                "indicator_type": indicator_data.get("indicator_type", "unknown"),
            }

    # -------------------------------------------------------------------------
    # HTTP 代理方法（转发给 text2sql 后端）
    # -------------------------------------------------------------------------

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

    def _resolve_indicator_type(
        self, business_type: Optional[str], calc_type: Optional[str]
    ) -> Optional[str]:
        if business_type == "core18":
            return "统计型" if calc_type == "count" else "分子分母比值型"
        if business_type == "four":
            return "统计型" if calc_type == "count" else "分子分母比值型"
        if business_type:
            return "分子分母比值型"
        return None

    def test_sql(self, sql: str, limit: int = 200) -> Dict[str, Any]:
        import time as _t
        t0 = _t.time()
        try:
            resp = self.client.post(
                self._make_url("/api/test_sql"), json={"sql": sql, "limit": limit}, timeout=300
            )
            elapsed = _t.time() - t0
            resp.raise_for_status()
            result = resp.json()
            logger.info(f"[test_sql] HTTP成功，耗时{elapsed:.1f}s，count={result.get('count')}, err={result.get('error')}")
            return result
        except httpx.TimeoutException:
            elapsed = _t.time() - t0
            logger.error(f"[test_sql] HTTP超时，耗时{elapsed:.1f}s，SQL前150: {sql[:150]!r}")
            return {"ok": False, "columns": [], "rows": [], "count": None, "error": f"HTTP请求超时({elapsed:.0f}s)"}
        except Exception as e:
            elapsed = _t.time() - t0
            logger.error(f"[test_sql] HTTP失败，耗时{elapsed:.1f}s，错误={e}")
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
                "指标计算公式": (
                    indicator_data.get("formula", "")
                    or indicator_data.get("indicator_formula", "")
                ),
                "分子描述": (
                    indicator_data.get("numerator_desc", "")
                    or indicator_data.get("numerator", "")
                ),
                "分母描述": (
                    indicator_data.get("denominator_desc", "")
                    or indicator_data.get("denominator", "")
                ),
                "指标描述": indicator_data.get("description", ""),
                "涉及到表": (
                    indicator_data.get("involved_tables", [])
                    or indicator_data.get("selected_tables", [])
                ),
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
        target: str = "numerator",
        page: int = 1,
        page_size: int = 50,
        db_session=None,
        hospital_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """根据执行记录 ID 获取指定页的预览数据（支持前端临时ID和数据库整数ID）
        hospital_code 非空时，仅执行该医院的 SQL 并返回分页数据（用于按医院筛选）。
        """
        if not db_session:
            return {"ok": False, "error": "数据库会话不可用", "columns": [], "rows": [], "total_count": 0}

        try:
            from app.models.indicator import IndicatorExecution

            record = None
            # 前端临时ID格式: "exec-1747401600123"
            if isinstance(execution_id, str) and execution_id.startswith("exec-"):
                exec_int = int(execution_id.split("-")[1])
                target_ts = exec_int / 1000
                min_ts = target_ts - 2
                max_ts = target_ts + 2
                records_found = (
                    db_session.query(IndicatorExecution)
                    .filter(
                        IndicatorExecution.execution_time
                        >= datetime.fromtimestamp(min_ts),
                        IndicatorExecution.execution_time
                        <= datetime.fromtimestamp(max_ts),
                    )
                    .order_by(IndicatorExecution.execution_time.desc())
                    .limit(5)
                    .all()
                )
                for r in records_found:
                    r_ts = r.execution_time.timestamp()
                    if abs(r_ts - target_ts) < 2:
                        record = r
                        break
            else:
                record = (
                    db_session.query(IndicatorExecution)
                    .filter(IndicatorExecution.id == int(execution_id))
                    .first()
                )

            if not record:
                return {
                    "ok": False,
                    "error": f"执行记录不存在 (id={execution_id})",
                    "columns": [],
                    "rows": [],
                    "total_count": 0,
                }

            if target == "numerator":
                raw_sql = record.numerator_sql or record.sql or ""
            elif target == "denominator":
                raw_sql = record.denominator_sql or ""
            else:
                return {"ok": False, "error": f"未知 target: {target}", "columns": [], "rows": [], "total_count": 0}

            if not raw_sql:
                return {
                    "ok": False,
                    "error": "该执行记录无原始 SQL",
                    "columns": [],
                    "rows": [],
                    "total_count": 0,
                }

            # hospital_code 非空时：优先从 hospital_results 取已存储的明细行
            if hospital_code and record.hospital_results:
                hosp_data = next(
                    (h for h in record.hospital_results
                     if str(h.get("hospital_code") or "") == str(hospital_code)),
                    None
                )
                if hosp_data:
                    if target == "numerator":
                        prev_data = hosp_data.get("preview_data") or {}
                        # 兼容：可能是 dict {columns, rows} 或旧的纯数组
                        if isinstance(prev_data, dict):
                            cols = prev_data.get("columns") or hosp_data.get("preview_columns") or []
                            raw_rows = prev_data.get("rows") or []
                        else:
                            cols = hosp_data.get("preview_columns") or []
                            raw_rows = prev_data if isinstance(prev_data, list) else []
                        total_count = hosp_data.get("numerator_count", 0)
                    else:
                        prev_data = hosp_data.get("denominator_preview_data") or {}
                        if isinstance(prev_data, dict):
                            cols = prev_data.get("columns") or hosp_data.get("denominator_preview_columns") or []
                            raw_rows = prev_data.get("rows") or []
                        else:
                            cols = hosp_data.get("denominator_preview_columns") or []
                            raw_rows = prev_data if isinstance(prev_data, list) else []
                        total_count = hosp_data.get("denominator_count", 0)
                    offset = (page - 1) * page_size
                    return {
                        "ok": True,
                        "columns": cols,
                        "rows": raw_rows[offset:offset + page_size],
                        "total_count": total_count,
                    }
                # hospital_results 中没有该医院 → 回退到重新执行 SQL

            # 【阶段一·预览页】复用 execute_indicator 中的万能注入器
            # numerator 用 numerator_date_field，denominator 用 denominator_date_field
            time_col_for_preview = self._resolve_time_col(
                (record.numerator_date_field if target == "numerator" else (record.denominator_date_field or record.date_field))
                or "discharge"
            )
            # hospital_code 非空时仅执行该医院的 SQL（用于按医院筛选）
            codes_to_use = [hospital_code] if hospital_code else (record.hospital_codes or [])
            sql = self._inject_filters(
                raw_sql,
                hospital_codes=codes_to_use,
                time_mode=record.time_mode,
                time_value=record.time_value,
                time_col_name=time_col_for_preview,
                is_aggregate=False,
            )

            # 执行分页查询
            offset = (page - 1) * page_size
            if self._sql_runner_fetch_preview_page is not None:
                try:
                    cols, rows, err = self._sql_runner_fetch_preview_page(
                        sql, limit=page_size, offset=offset
                    )
                    if err:
                        return {"ok": False, "error": err, "columns": [], "rows": [], "total_count": 0}
                    # 优先取该医院的分子/分母计数；没有时用全院计数
                    hosp_count = None
                    if hospital_code and record.hospital_results:
                        for h in record.hospital_results:
                            if str(h.get("hospital_code") or "") == str(hospital_code):
                                hosp_count = h.get("numerator_count") if target == "numerator" else h.get("denominator_count")
                                break
                    total_count = hosp_count if hosp_count is not None else (record.numerator_count if target == "numerator" else (record.denominator_count or 0))
                    return {
                        "ok": True,
                        "columns": cols,
                        "rows": _to_serializable_rows(rows),
                        "total_count": total_count,
                    }
                except Exception as e:
                    return {
                        "ok": False,
                        "error": str(e),
                        "columns": [],
                        "rows": [],
                        "total_count": 0,
                    }
            else:
                return {
                    "ok": False,
                    "error": "sql_runner 不可用",
                    "columns": [],
                    "rows": [],
                    "total_count": 0,
                }

        except Exception as e:
            logger.error(f"fetch_preview_page 失败: {e}")
            return {"ok": False, "error": str(e), "columns": [], "rows": [], "total_count": 0}
