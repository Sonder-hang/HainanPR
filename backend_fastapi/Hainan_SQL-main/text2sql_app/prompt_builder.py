"""从 指标 + tables.json 子集构建发给模型的文本，支持三种指标类型。"""
import json
from pathlib import Path
from typing import Any, Optional

from config import INDICATORS_JSON, PROMPT_LOG_JSON, PROMPT_MAX_COLUMNS_PER_TABLE, TABLES_JSON

MAX_FIELD_MEANING_LEN = 200

INDICATOR_TYPES = ("分子分母比值型", "统计型", "大模型分析型")


# ========================== 新阶段：任务理解（对话1） ==========================

SYSTEM_PROMPT_UNDERSTAND = """你是一个医疗数据分析专家。请仔细分析用户的查询需求，并进行自我检查。

你的任务是：
1. 理解用户的查询意图
2. 识别需要用到的字段
3. 检查是否缺少必要信息
4. 制定SQL编写计划

【自我检查清单】
请逐项回答以下问题：

1. 查询意图理解：
   - 用户想要查询什么？（用一句话描述）

2. 需要用到的字段：
   表名.字段名 | 用途说明
   ───────────────────────────
   dept.dept_name | 科室名称（用于显示）
   outpatient.record_date | 门诊日期（用于筛选）
   ... | ...

3. SQL编写计划：
   - 需要哪些表？（JOIN关系）
   - 需要哪些筛选条件？（WHERE）
   - 是否需要分组？（GROUP BY）
   - 是否需要聚合？（COUNT/SUM/AVG...）
   - 是否需要排序？（ORDER BY）
   - 是否需要限制数量？（LIMIT）

4. 缺失信息检查：
   □ 我已理解用户的所有需求
   □ 没有缺少任何必要信息
   □ 字段映射关系明确

   如果有任何 □ 未勾选，请说明：
   [具体说明缺失的信息]

【输出格式】
请按以上格式输出 JSON 对象：
{
  "查询意图": "...",
  "使用字段": [{"字段": "...", "用途": "..."}],
  "SQL计划": {
    "JOIN": "...",
    "WHERE": "...",
    "GROUP BY": "...",
    "HAVING": "...",
    "ORDER BY": "..."
  },
  "缺失检查": {
    "理解正确": true/false,
    "信息完备": true/false,
    "缺失说明": null/字符串
  }
}

如果一切正常，明确输出 "我已准备好生成SQL" 在查询意图中。
如果有问题，请详细说明缺失信息。
请始终使用中文进行思考和回答。"""


def user_message_understand(
    tables_info: str,
    user_question: str,
) -> str:
    return f"""【用户勾选的表】
{tables_info}

【用户的查询需求】
{user_question}

请按照系统提示的格式输出任务理解结果。"""


# ========================== 新阶段：内容管道（标识符识别） ==========================

SYSTEM_PROMPT_CONTENT_PIPELINE = """你是一个医疗数据分析专家。基于以下信息，识别SQL需要用到的标识符。

【输出格式】
请输出需要用到的所有标识符的 JSON 对象：

{{
  "表名": {{
    "主表": "表名",
    "关联表": ["表名列表"]
  }},
  "字段": [
    {{"用途": "显示/筛选/统计/分组/关联", "表名.字段名": "..."}}
  ],
  "值": [
    {{"描述": "...", "对应字段": "..."}}
  ]
}}

请简洁输出，不要多余解释。
请始终使用中文进行思考和回答。"""


def user_message_content_pipeline(
    tables_info: str,
    confirmed_question: str,
) -> str:
    return f"""【用户勾选的表】
{tables_info}

【已确认的查询需求】
{confirmed_question}

请识别SQL需要用到的标识符，输出JSON对象。"""


# ========================== 新阶段：结构管道（SQL语法推导） ==========================

SYSTEM_PROMPT_STRUCTURE_PIPELINE = """你是一个专业的SQL工程师。基于以下信息，推导SQL的语法结构。

【输出格式】
请输出SQL的语法结构的 JSON 对象：

{{
  "SELECT": "需要显示的字段或聚合",
  "FROM": "主表名",
  "JOIN": "关联表及条件",
  "WHERE": "筛选条件",
  "GROUP BY": "分组字段",
  "HAVING": "分组后筛选条件",
  "ORDER BY": "排序字段 ASC/DESC",
  "LIMIT": "数量限制"
}}

请简洁输出，不要多余解释。
请始终使用中文进行思考和回答。"""


def user_message_structure_pipeline(
    confirmed_question: str,
    identifiers: str,
) -> str:
    return f"""【查询需求】
{confirmed_question}

【已识别的标识符】
{identifiers}

请推导SQL的语法结构，输出JSON对象。"""


# ========================== 新阶段：逻辑一致性检查（对话3） ==========================

SYSTEM_PROMPT_LOGIC_CHECK = """你是一个逻辑一致性检查专家。请将SQL转换回自然语言，并与原需求进行对比。

【输出格式】
请分两步输出：

第一步 - SQL转自然语言：
将SQL转换为自然语言描述，说明这个SQL在做什么查询。

第二步 - 逻辑对比：
对比原理解与SQL理解，判断是否逻辑一致。

输出 JSON 对象：
{{
  "sql理解": "SQL的自然语言描述",
  "一致性判断": "一致/不一致",
  "差异分析": "如不一致，详细说明差异点",
  "可能原因": ["可能原因1", "可能原因2"],
  "建议修正": "如需要修正，提供具体建议"
}}

请始终使用中文进行思考和回答。"""


def user_message_sql_to_nl(sql: str) -> str:
    return f"""【SQL语句】
{sql}

请将SQL转换为自然语言描述。"""


def user_message_logic_compare(original_intent: str, sql_understanding: str) -> str:
    return f"""【原查询意图】
{original_intent}

【SQL理解结果】
{sql_understanding}

请对比两个描述是否逻辑一致，输出JSON对象。"""


def load_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_indicators() -> list[dict[str, Any]]:
    return load_json(INDICATORS_JSON)


def save_indicators(data: list[dict[str, Any]]) -> None:
    with open(INDICATORS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_tables_catalog() -> dict[str, Any]:
    return load_json(TABLES_JSON)


def get_indicator_type(indicator: dict[str, Any]) -> str:
    t = indicator.get("类型", "分子分母比值型")
    return t if t in INDICATOR_TYPES else "分子分母比值型"


def build_supplement_info(indicator: dict[str, Any]) -> str:
    """从分子描述/分母描述或指标描述构建补充信息文本。"""
    itype = get_indicator_type(indicator)
    if itype == "分子分母比值型":
        n = indicator.get("分子描述", "")
        d = indicator.get("分母描述", "")
        if n or d:
            return f"分母：{d}\n分子：{n}"
        return indicator.get("补充信息", "")
    return indicator.get("指标描述", "") or indicator.get("补充信息", "")


def merge_indicator_prompt_fields(
    indicator: dict[str, Any],
    *,
    indicator_formula: Optional[str] = None,
    supplement_info: Optional[str] = None,
    numerator_desc: Optional[str] = None,
    denominator_desc: Optional[str] = None,
    indicator_desc: Optional[str] = None,
) -> dict[str, Any]:
    out = dict(indicator)
    if indicator_formula is not None:
        out["指标计算公式"] = indicator_formula
    if numerator_desc is not None:
        out["分子描述"] = numerator_desc
    if denominator_desc is not None:
        out["分母描述"] = denominator_desc
    if indicator_desc is not None:
        out["指标描述"] = indicator_desc
    if supplement_info is not None:
        out["补充信息"] = supplement_info
    else:
        out["补充信息"] = build_supplement_info(out)
    return out


def filter_tables_for_prompt(
    catalog: dict[str, Any],
    table_names: list[str],
) -> list[dict[str, Any]]:
    names = set(table_names)
    tables = catalog.get("tables") or []
    out = [t for t in tables if t.get("表名") in names]
    by_name = {t["表名"]: t for t in out}
    return [by_name[n] for n in table_names if n in by_name]


def get_all_table_names_with_comments(catalog: dict[str, Any]) -> list[dict[str, str]]:
    """返回所有表名及其业务定义/注释。"""
    tables = catalog.get("tables") or []
    return [
        {"表名": t.get("表名", ""), "业务定义": t.get("业务定义", "")}
        for t in tables
    ]


def format_schema_block(tables: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    cap = PROMPT_MAX_COLUMNS_PER_TABLE
    for t in tables:
        lines.append(f"物理表名：{t.get('表名', '')}")
        lines.append(f"业务定义：{t.get('业务定义', '')}")
        lines.append(f"数据粒度：{t.get('数据粒度', '')}")
        lines.append("字段说明：")
        all_cols = list(t.get("字段列表") or [])
        shown = all_cols if cap is None else all_cols[:cap]
        for col in shown:
            name = col.get("字段名", "")
            dtype = col.get("数据类型", "")
            meaning = col.get("中文含义", "") or ""
            if len(meaning) > MAX_FIELD_MEANING_LEN:
                meaning = meaning[: MAX_FIELD_MEANING_LEN] + "…"
            cst = col.get("约束说明", "") or ""
            extra = f" ({cst})" if cst else ""
            lines.append(f"  - {name} [{dtype}]: {meaning}{extra}")
        if cap is not None and len(all_cols) > cap:
            lines.append(
                f"  …（本表共 {len(all_cols)} 列，为缩短推理时间仅列示前 {cap} 列；"
                "生成 SQL 时请结合业务优先使用常见关联键如住院号、主键等）"
            )
        lines.append("")
    return "\n".join(lines).strip()


# ========================== 分子分母比值型 ==========================

SYSTEM_PROMPT_DUAL = """你是一个专业的医疗监管数据库工程师。请根据提供的指标定义、分子/分母补充说明以及勾选业务表的字段信息，**在一次回复中**同时给出分母与分子两条可在 MySQL 8.0 上执行的纯净 SQL。

**生成思路**：请先构思分母 SQL（分母代表基础总体人口），确定分母所需的表和字段；然后以分母为基础，在其上增加分子专属的筛选条件来构建分子 SQL。

硬性要求：
1. **只输出一个 JSON 对象**，不要 Markdown 代码围栏、不要前后解释文字。JSON 必须可被标准库解析。
2. JSON 仅包含两个字符串键（必须都存在且非空）：
   - "denominator_sql"：分母查询 SQL
   - "numerator_sql"：分子查询 SQL
3. 两条 SQL 均为单条语句，禁止 SQL 行内注释；必须使用表别名（如 t1、t2），列名加表别名前缀。**禁止在 SELECT 列表中用 `AS` 或尾随空格为结果列起展示别名**（禁止 `t1.XXX AS yyy`、`t1.XXX yyy`）；请写 `t1.物理字段名` 等形式，使结果集列名与 catalog 中的英文字段名一致，便于界面自动对照中文含义。
4. **SELECT 列要精简且有用**：禁止使用 `SELECT *`，不要堆砌与当前指标判定无关的冗余列。**分母**：一般包含界定明细粒度所需的标识列以及分母 WHERE/JOIN 判定所依赖的字段即可。**分子**：除上述与分母口径一致的必要标识与条件相关字段外，还应包含能够**在结果中展示、佐证「为何满足分子约束」**的字段，便于预览与人工核对；仍勿为「求全」引入与分子逻辑无关的大量列。
5. **分母与分子不一定要用上所有提供的表**——请你仔细分析分母和分子各自的业务含义后，再决定每条 SQL 分别需要哪些表和哪些字段。分母只需要满足基础总体人口的筛选逻辑；分子在分母基础上增加专属条件，若分子的判定逻辑需要额外的表则可以额外 JOIN，若不需要则不必强行关联。
6. 若表字段中存在作废/有效标识，须加入有效数据过滤；不要臆造不存在的列名。
7. 当前阶段不要加入院时间、统计周期等时间范围条件。
8. 禁止使用多语句；不要 USE database；不要写存储过程。

请始终使用中文进行思考和回答。"""


def user_message_dual(
    indicator: dict[str, Any],
    schema_text: str,
    *,
    regenerate_section: str = "",
) -> str:
    return f"""【指标名称】
{indicator.get("指标名", "")}

【指标计算公式】
{indicator.get("指标计算公式", "")}

【补充信息（含分母/分子文字定义）】
{indicator.get("补充信息", "")}

【可选业务表及字段】
（注意：以下是所有可能相关的表，分母和分子各自不一定要全部用上，请仔细分析后再决定每条 SQL 需要哪些表和字段。）
{schema_text}

{regenerate_section}
【当前任务】
请先构思分母，再以分母为基础构思分子，在同一回复中同时完成：
1. 「分母」查询：代表基础总体人口，返回满足分母判定逻辑的明细行；不要在外层套 COUNT。SELECT 只列必要列（粒度标识 + 分母判定所需字段），禁止 `SELECT *`，勿选无关列；**不要**用 `AS` 或空格给列重命名。
2. 「分子」查询：在分母的基础上增加分子专属筛选条件；如果分子的判定需要额外的表可以额外 JOIN，不需要则不必强行关联；明细行，不要外层 COUNT。除必要列外，请包含能**展示分子约束如何被满足**的字段（如判定用到的状态、时间、编码等），便于核对；仍避免无关宽列；**不要**用 `AS` 或空格给列重命名。

请**只输出**如下形式的 JSON（键名必须完全一致）：
{{"denominator_sql":"……","numerator_sql":"……"}}"""


def build_dual_retry_suffix(
    *,
    numerator_sql: str,
    denominator_sql: str,
    numerator_error: Optional[str],
    denominator_error: Optional[str],
) -> str:
    parts: list[str] = []
    if denominator_sql.strip():
        parts.append("【上次分母 SQL】\n" + denominator_sql.strip())
    if numerator_sql.strip():
        parts.append("【上次分子 SQL】\n" + numerator_sql.strip())
    if denominator_error:
        parts.append("【分母 SQL 的 MySQL 错误】\n" + denominator_error.strip())
    if numerator_error:
        parts.append("【分子 SQL 的 MySQL 错误】\n" + numerator_error.strip())
    if not parts:
        return ""
    return "\n\n".join(parts) + "\n\n请根据上述错误同时修正 JSON 中的 denominator_sql 与 numerator_sql，仍只输出合法 JSON。\n"


def build_regenerate_from_request(reg: Optional[Any] = None) -> str:
    if reg is None:
        return ""
    parts: list[str] = []
    fb = getattr(reg, "user_feedback", None) or ""
    if fb.strip():
        parts.append("【用户补充说明】\n" + fb.strip())
    pd = getattr(reg, "previous_denominator_sql", None) or ""
    pe_d = getattr(reg, "denominator_error", None) or ""
    if pd.strip():
        parts.append("【上次分母 SQL】\n" + pd.strip())
    if pe_d.strip():
        parts.append("【分母侧错误】\n" + pe_d.strip())
    pn = getattr(reg, "previous_numerator_sql", None) or ""
    pe_n = getattr(reg, "numerator_error", None) or ""
    if pn.strip():
        parts.append("【上次分子 SQL】\n" + pn.strip())
    if pe_n.strip():
        parts.append("【分子侧错误】\n" + pe_n.strip())
    if not parts:
        return ""
    return "\n\n".join(parts) + "\n\n请结合上述上下文重新输出仅含 denominator_sql 与 numerator_sql 的 JSON。\n"


# ========================== 统计型 ==========================

SYSTEM_PROMPT_STAT = """你是一个专业的医疗监管数据库工程师。请根据提供的指标定义和勾选业务表的字段信息，编写可在 MySQL 8.0 上执行的纯净统计查询 SQL。

硬性要求：
1. **只输出一个 JSON 对象**，不要 Markdown 代码围栏、不要前后解释文字。JSON 必须可被标准库解析。
2. JSON 仅包含一个字符串键（必须存在且非空）：
   - "sql"：统计查询 SQL
3. SQL 为单条语句，禁止 SQL 行内注释；必须使用表别名（如 t1、t2），列名加表别名前缀。**禁止在 SELECT 列表中用 `AS` 或尾随空格为结果列起展示别名**；请写 `t1.物理字段名` 等形式，使结果列名与 catalog 英文字段名一致。
4. **SELECT 列**：禁止 `SELECT *`，只选与统计口径、分组与展示相关的必要列，勿堆砌无关字段。
5. 若表字段中存在作废/有效标识（如 INVLD_FLG 等），须加入有效数据过滤；不要臆造不存在的列名。
6. 当前阶段不要加入院时间、统计周期等时间范围条件。
7. 禁止使用多语句；不要 USE database；不要写存储过程。

请始终使用中文进行思考和回答。"""


def user_message_stat(
    indicator: dict[str, Any],
    schema_text: str,
    *,
    regenerate_section: str = "",
) -> str:
    return f"""【指标名称】
{indicator.get("指标名", "")}

【指标描述】
{indicator.get("补充信息", "")}

【勾选业务表及字段】
{schema_text}

{regenerate_section}
【当前任务】
编写统计查询 SQL：返回符合指标定义的统计结果明细行；不要在外层套 COUNT（由系统另行统计总行数）。SELECT 只列必要列，禁止 `SELECT *`；**不要**用 `AS` 或空格给列重命名。

请**只输出**如下形式的 JSON（键名必须完全一致）：
{{"sql":"……"}}"""


def build_stat_retry_suffix(
    *,
    sql: str,
    error: Optional[str],
) -> str:
    parts: list[str] = []
    if sql.strip():
        parts.append("【上次 SQL】\n" + sql.strip())
    if error:
        parts.append("【MySQL 错误】\n" + error.strip())
    if not parts:
        return ""
    return "\n\n".join(parts) + "\n\n请根据上述错误修正 JSON 中的 sql，仍只输出合法 JSON。\n"


def build_stat_regenerate_from_request(reg: Optional[Any] = None) -> str:
    if reg is None:
        return ""
    parts: list[str] = []
    fb = getattr(reg, "user_feedback", None) or ""
    if fb.strip():
        parts.append("【用户补充说明】\n" + fb.strip())
    ps = getattr(reg, "previous_sql", None) or ""
    pe = getattr(reg, "sql_error", None) or ""
    if ps.strip():
        parts.append("【上次 SQL】\n" + ps.strip())
    if pe.strip():
        parts.append("【执行错误】\n" + pe.strip())
    if not parts:
        return ""
    return "\n\n".join(parts) + "\n\n请结合上述上下文重新输出仅含 sql 的 JSON。\n"


# ========================== 大模型分析型 ==========================

SYSTEM_PROMPT_ANALYSIS = """你是一个专业的医疗监管数据分析师。请根据提供的指标定义和勾选业务表的字段信息，编写可在 MySQL 8.0 上执行的分析查询 SQL，并对结果含义给出专业解读建议。

硬性要求：
1. **只输出一个 JSON 对象**，不要 Markdown 代码围栏、不要前后解释文字。JSON 必须可被标准库解析。
2. JSON 包含两个字符串键：
   - "sql"：分析查询 SQL（单条语句）
   - "analysis"：对该查询结果含义的专业解读、业务改进建议
3. SQL 为单条语句，禁止 SQL 行内注释；必须使用表别名（如 t1、t2），列名加表别名前缀。**禁止在 SELECT 列表中用 `AS` 或尾随空格为结果列起展示别名**；请写 `t1.物理字段名` 等形式，使结果列名与 catalog 英文字段名一致。
4. **SELECT 列**：禁止 `SELECT *`，只选支撑分析结论与结果解读所需的必要列，勿堆砌无关字段。
5. 若表字段中存在作废/有效标识（如 INVLD_FLG 等），须加入有效数据过滤；不要臆造不存在的列名。
6. 当前阶段不要加入院时间、统计周期等时间范围条件。
7. 禁止使用多语句；不要 USE database；不要写存储过程。

请始终使用中文进行思考和回答。"""


def user_message_analysis(
    indicator: dict[str, Any],
    schema_text: str,
    *,
    regenerate_section: str = "",
) -> str:
    return f"""【指标名称】
{indicator.get("指标名", "")}

【指标描述】
{indicator.get("补充信息", "")}

【勾选业务表及字段】
{schema_text}

{regenerate_section}
【当前任务】
编写分析查询 SQL，并给出对查询结果的专业解读和建议。SQL 的 SELECT 只列必要列，禁止 `SELECT *`；**不要**用 `AS` 或空格给列重命名。

请**只输出**如下形式的 JSON（键名必须完全一致）：
{{"sql":"……","analysis":"……"}}"""


def build_analysis_retry_suffix(
    *,
    sql: str,
    error: Optional[str],
) -> str:
    parts: list[str] = []
    if sql.strip():
        parts.append("【上次 SQL】\n" + sql.strip())
    if error:
        parts.append("【MySQL 错误】\n" + error.strip())
    if not parts:
        return ""
    return "\n\n".join(parts) + "\n\n请根据上述错误修正 JSON 中的 sql 和 analysis，仍只输出合法 JSON。\n"


# ========================== Prompt 预览构建 ==========================

def build_prompt_preview(
    indicator: dict[str, Any],
    schema_text: str,
) -> dict[str, str]:
    """根据指标类型构建 system_prompt 和 user_message 的预览文本。"""
    itype = get_indicator_type(indicator)
    if itype == "分子分母比值型":
        return {
            "system_prompt": SYSTEM_PROMPT_DUAL,
            "user_message": user_message_dual(indicator, schema_text),
        }
    elif itype == "统计型":
        return {
            "system_prompt": SYSTEM_PROMPT_STAT,
            "user_message": user_message_stat(indicator, schema_text),
        }
    else:
        return {
            "system_prompt": SYSTEM_PROMPT_ANALYSIS,
            "user_message": user_message_analysis(indicator, schema_text),
        }


# ========================== prompt_log.json 管理 ==========================

def load_prompt_log() -> dict[str, Any]:
    """加载 prompt_log.json，结构: { "指标名": [ {记录}, ... ], ... }"""
    if not PROMPT_LOG_JSON.is_file():
        return {}
    try:
        return load_json(PROMPT_LOG_JSON)
    except Exception:
        return {}


def save_prompt_log(data: dict[str, Any]) -> None:
    with open(PROMPT_LOG_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def append_prompt_log_entry(
    indicator_name: str,
    *,
    system_prompt: str,
    user_message: str,
    result_ok: bool,
    sql_summary: str = "",
    timestamp: str = "",
) -> None:
    """向 prompt_log.json 追加一条指标的 prompt 记录。"""
    from datetime import datetime, timezone

    log = load_prompt_log()
    if indicator_name not in log:
        log[indicator_name] = []

    entry = {
        "时间": timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "结果": "成功" if result_ok else "失败",
        "system_prompt": system_prompt,
        "user_message": user_message,
    }
    if sql_summary:
        entry["sql摘要"] = sql_summary

    log[indicator_name].append(entry)
    save_prompt_log(log)


# ========================== 新阶段 JSON 解析函数 ==========================

def _strip_json_fence(text: str) -> str:
    """去除 ```json ... ``` 包裹。"""
    t = text.strip()
    m = re.match(r"^```(?:json)?\s*([\s\S]*?)```\s*$", t, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return t


def _extract_json_object(raw: str) -> dict:
    """从模型回复中提取第一个完整的 JSON 对象。"""
    import re as _re
    t = _strip_json_fence(raw)
    start = t.find("{")
    end = t.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("回复中未找到 JSON 对象")
    return json.loads(t[start : end + 1])


def parse_understanding_json(raw: str) -> dict:
    """解析任务理解的 JSON 输出。"""
    return _extract_json_object(raw)


def parse_content_pipeline_json(raw: str) -> dict:
    """解析内容管道的 JSON 输出。"""
    return _extract_json_object(raw)


def parse_structure_pipeline_json(raw: str) -> dict:
    """解析结构管道的 JSON 输出。"""
    return _extract_json_object(raw)


def parse_logic_check_json(raw: str) -> dict:
    """解析逻辑检查的 JSON 输出。"""
    return _extract_json_object(raw)


import re
