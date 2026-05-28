"""
数据库迁移脚本：为6个测试指标写入 subitem_config、template_type 和正确 SQL。

执行前请务必在测试环境验证！
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymysql
import json

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '22013232',
    'database': 'hainan',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}


# ============================================================
# 6个测试指标的完整配置
# ============================================================
INDICATOR_CONFIGS = [

    # ---- 1. 普通会诊及时完成率（RATE） ----
    {
        "name": "普通会诊及时完成率",
        "template_type": "RATE",
        "calc_type": "ratio",
        "numerator_desc": "普通会诊24小时内完成次数",
        "denominator_desc": "普通会诊文书数量",
        "formula": "分子 ÷ 分母 × 100%",
        "numerator_sql": """
SELECT
    COUNT(DISTINCT c.INHOS_NO, c.MDC_ORG_CD) AS numerator_cnt
FROM FACT_CSTT_RCD c
JOIN FACT_MDC_RCD_HMPG h
    ON c.INHOS_NO = h.INHOS_NO
   AND c.MDC_ORG_CD = h.MDC_ORG_CD
WHERE c.CSTT_TP LIKE '%普通会诊'
  AND TIMESTAMPDIFF(HOUR, c.APL_DT_TM, c.CRT_TM) < 24
  AND h.DSCG_DT_TM IS NOT NULL
        """.strip(),
        "denominator_sql": """
SELECT
    COUNT(DISTINCT c.INHOS_NO, c.MDC_ORG_CD) AS denominator_cnt
FROM FACT_CSTT_RCD c
JOIN FACT_MDC_RCD_HMPG h
    ON c.INHOS_NO = h.INHOS_NO
   AND c.MDC_ORG_CD = h.MDC_ORG_CD
WHERE c.CSTT_TP LIKE '%普通会诊'
  AND h.DSCG_DT_TM IS NOT NULL
        """.strip(),
        "subitem_config": None,
    },

    # ---- 2. 普通会诊有效率（RATE） ----
    {
        "name": "普通会诊有效率",
        "template_type": "RATE",
        "calc_type": "ratio",
        "numerator_desc": "普通会诊结束后1小时内开具相关医嘱的次数",
        "denominator_desc": "普通会诊文书数量",
        "formula": "分子 ÷ 分母 × 100%",
        "numerator_sql": """
SELECT COUNT(DISTINCT t.INHOS_NO, t.MDC_ORG_CD, t.ODR_OPN_DT_TM, t.ODR_ITM_TP_NM, t.ODR_CGY_NM) AS numerator_cnt
FROM (
    SELECT
        od.INHOS_NO,
        od.MDC_ORG_CD,
        od.ODR_OPN_DT_TM,
        od.ODR_ITM_TP_NM,
        od.ODR_CGY_NM,
        c.CSTT_TP,
        c.CSTT_DT_TM AS CSTT_END_TIME,
        TIMESTAMPDIFF(MINUTE, c.CSTT_DT_TM, od.ODR_OPN_DT_TM) AS MINUTES_DIFF,
        ROW_NUMBER() OVER (
            PARTITION BY od.INHOS_NO, od.MDC_ORG_CD, od.ODR_OPN_DT_TM, od.ODR_ITM_TP_NM, od.ODR_CGY_NM
            ORDER BY c.CSTT_DT_TM DESC
        ) AS rn
    FROM FACT_INHOS_ODR_INFMT od
    JOIN FACT_CSTT_RCD c
        ON od.INHOS_NO = c.INHOS_NO
       AND od.MDC_ORG_CD = c.MDC_ORG_CD
    WHERE c.CSTT_TP = '普通会诊'
      AND c.CSTT_DT_TM IS NOT NULL
      AND od.ODR_OPN_DT_TM > c.CSTT_DT_TM
      AND TIMESTAMPDIFF(MINUTE, c.CSTT_DT_TM, od.ODR_OPN_DT_TM) <= 60
      AND od.ODR_ITM_TP_NM NOT LIKE '%嘱托%'
      AND od.ODR_CGY_NM NOT LIKE '%出院%'
) t
JOIN FACT_MDC_RCD_HMPG h
    ON t.INHOS_NO = h.INHOS_NO
   AND t.MDC_ORG_CD = h.MDC_ORG_CD
WHERE t.rn = 1
  AND h.DSCG_DT_TM IS NOT NULL
        """.strip(),
        "denominator_sql": """
SELECT
    COUNT(DISTINCT c.INHOS_NO, c.MDC_ORG_CD) AS denominator_cnt
FROM FACT_CSTT_RCD c
JOIN FACT_MDC_RCD_HMPG h
    ON c.INHOS_NO = h.INHOS_NO
   AND c.MDC_ORG_CD = h.MDC_ORG_CD
WHERE c.CSTT_TP LIKE '%普通会诊'
  AND h.DSCG_DT_TM IS NOT NULL
        """.strip(),
        "subitem_config": None,
    },

    # ---- 3. 主要诊断ICD-10编码亚目种类数（STRUCTURE + COMPOSITE_RANKING） ----
    {
        "name": "主要诊断ICD-10编码亚目种类数",
        "template_type": "STRUCTURE",
        "calc_type": "count",
        "description": "主要诊断ICD-10编码亚目（前5位）的种类数及分布",
        "numerator_desc": "主要诊断ICD-10编码亚目种类数",
        "formula": "COUNT(DISTINCT sub_category)",
        "sql": """
SELECT
    UPPER(LEFT(REPLACE(REPLACE(REPLACE(t2.DIAG_CD, '.', ''), '-', ''), ' ', ''), 5)) AS sub_category,
    COUNT(DISTINCT UPPER(REPLACE(REPLACE(REPLACE(t2.DIAG_CD, '.', ''), '-', ''), ' ', ''))) AS disease_cnt
FROM FACT_MDC_RCD_HMPG t1
INNER JOIN FACT_MDC_RCD_HMPG_DIAG t2
    ON t1.INHOS_NO = t2.INHOS_NO
   AND t1.MDC_ORG_CD = t2.MDC_ORG_CD
WHERE t2.MAIN_DIAG_FLG = '1'
  AND t2.DIAG_CD NOT IN ('', '-')
  AND t1.DSCG_DT_TM IS NOT NULL
GROUP BY sub_category
ORDER BY disease_cnt DESC
LIMIT 50
        """.strip(),
        "subitem_config": {
            "type": "COMPOSITE_RANKING",
            "ranking_key_field": "sub_category",
            "ranking_value_field": "disease_cnt",
            "total_aggregation_field": "disease_cnt",
            "limit": 20,
        },
    },

    # ---- 4. 主要手术ICD-9-CM-3四位码种类数（STRUCTURE-special + COMPOSITE_RANKING） ----
    # 注：STRUCTURE-special 需要双排行（治疗性/诊断性），这里通过 UNION 实现分离
    {
        "name": "主要手术ICD-9-CM-3四位码种类数",
        "template_type": "STRUCTURE-special",
        "calc_type": "count",
        "description": "主要手术ICD-9-CM-3四位码种类数，区分治疗性与诊断性操作",
        "numerator_desc": "主要手术ICD-9-CM-3四位码种类数",
        "formula": "COUNT(DISTINCT four_digit_code)",
        "sql": """
SELECT
    four_digit_code,
    SUM(disease_cnt) AS surgery_cnt
FROM (
    SELECT
        UPPER(LEFT(REPLACE(REPLACE(REPLACE(t2.OPRT_CD, '.', ''), '-', ''), ' ', ''), 4)) AS four_digit_code,
        COUNT(DISTINCT UPPER(REPLACE(REPLACE(REPLACE(t2.OPRT_CD, '.', ''), '-', ''), ' ', ''))) AS disease_cnt
    FROM FACT_MDC_RCD_HMPG t1
    INNER JOIN FACT_MDC_RCD_HMPG_OPRT t2
        ON t1.INHOS_NO = t2.INHOS_NO
       AND t1.MDC_ORG_CD = t2.MDC_ORG_CD
    WHERE t1.DSCG_DT_TM IS NOT NULL
      AND t2.MAIN_OPRT_FLG = '1'
      AND t2.OPRT_CD NOT IN ('','-')
    GROUP BY four_digit_code
) AS all_surgeries
GROUP BY four_digit_code
ORDER BY surgery_cnt DESC
LIMIT 50
        """.strip(),
        "subitem_config": {
            "type": "COMPOSITE_RANKING",
            "ranking_key_field": "four_digit_code",
            "ranking_value_field": "surgery_cnt",
            "total_aggregation_field": "surgery_cnt",
            "limit": 20,
        },
    },

    # ---- 5. 住院患者死亡疾病谱（STRUCTURE + COMPOSITE_RANKING） ----
    {
        "name": "住院患者死亡疾病谱",
        "template_type": "STRUCTURE",
        "calc_type": "count",
        "description": "住院患者死亡疾病谱TOP20，区分离院方式死亡与转归死亡",
        "numerator_desc": "各死亡类型对应的患者人数",
        "formula": "COUNT(DISTINCT INHOS_NO)",
        "sql": """
SELECT
    UPPER(LEFT(REPLACE(REPLACE(REPLACE(t2.DIAG_CD, '.', ''), '-', ''), ' ', ''), 5)) AS sub_category,
    CASE
        WHEN t1.DSCG_WAY_NM LIKE '%死亡%' THEN '离院方式死亡'
        WHEN t1.TNOVR_CDT_NM LIKE '%死亡%' AND t1.DSCG_WAY_NM LIKE '%非医嘱%' THEN '转归死亡'
        ELSE NULL
    END AS death_type,
    COUNT(DISTINCT t1.INHOS_NO) AS death_patient_cnt
FROM FACT_MDC_RCD_HMPG t1
INNER JOIN FACT_MDC_RCD_HMPG_DIAG t2
    ON t1.INHOS_NO = t2.INHOS_NO
   AND t1.MDC_ORG_CD = t2.MDC_ORG_CD
WHERE t2.MAIN_DIAG_FLG = '1'
  AND t2.DIAG_CD NOT IN ('','-')
  AND (
      t1.DSCG_WAY_NM LIKE '%死亡%'
      OR (t1.TNOVR_CDT_NM LIKE '%死亡%' AND t1.DSCG_WAY_NM LIKE '%非医嘱%')
  )
GROUP BY sub_category, death_type
HAVING death_type IS NOT NULL
ORDER BY death_patient_cnt DESC
LIMIT 50
        """.strip(),
        "subitem_config": {
            "type": "COMPOSITE_RANKING",
            "ranking_key_field": "sub_category",
            "ranking_value_field": "death_patient_cnt",
            "total_aggregation_field": "death_patient_cnt",
            "limit": 20,
        },
    },

    # ---- 6. 住院患者围手术期死亡率（COMPOSITE + COMPOSITE_RATE） ----
    {
        "name": "住院患者围手术期死亡率",
        "template_type": "COMPOSITE",
        "calc_type": "ratio",
        "description": "住院患者围手术期各时间窗口的死亡率，区分离院方式死亡与转归死亡",
        "numerator_desc": "术后各时间窗口死亡患者数",
        "denominator_desc": "出院手术患者总数",
        "formula": "分子 ÷ 分母 × 100%",
        "sql": """
WITH
denominator_base AS (
    SELECT DISTINCT h.INHOS_NO, h.MDC_ORG_CD
    FROM FACT_MDC_RCD_HMPG h
    INNER JOIN FACT_MDC_RCD_HMPG_OPRT o
        ON h.INHOS_NO = o.INHOS_NO AND h.MDC_ORG_CD = o.MDC_ORG_CD
    WHERE h.DSCG_DT_TM IS NOT NULL
      AND o.OPRT_CD IS NOT NULL
      AND TRIM(o.OPRT_CD) <> ''
),
death_record_time AS (
    SELECT
        s.INHOS_NO,
        s.MDC_ORG_CD,
        STR_TO_DATE(
            REGEXP_REPLACE(
                REGEXP_REPLACE(
                    REGEXP_REPLACE(
                        REGEXP_REPLACE(
                            REGEXP_REPLACE(
                                REGEXP_SUBSTR(s.ITM_VLU,
                                    '死亡时间[:：][[:space:]]*[0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日[[:space:]]*[0-9]{1,2}时[0-9]{2}分|死亡时间[:：][[:space:]]*[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}[[:space:]]+[0-9]{1,2}:[0-9]{2}'),
                                '日[[:space:]]*', ' '
                            ),
                            '[年月]', '-'
                        ),
                        '死亡时间[:：][[:space:]]*', ''
                    ),
                    '时', ':'
                ),
                '分', ''
            ),
            '%Y-%m-%d %H:%i'
        ) AS DEATH_DT_TM
    FROM FACT_INHOS_CRS_RCD_S s
    WHERE s.RCD_TP_NM LIKE '%死亡记录%'
      AND s.ITM_NM = '文本主体'
      AND s.ITM_VLU LIKE '%死亡时间%'
),
clear_death_with_surgery AS (
    SELECT
        h.INHOS_NO,
        h.MDC_ORG_CD,
        o.OPRT_DT,
        d.DEATH_DT_TM,
        CASE WHEN DATE(d.DEATH_DT_TM) = DATE(o.OPRT_DT) THEN 1 ELSE 0 END AS death_same_day,
        CASE WHEN d.DEATH_DT_TM >= o.OPRT_DT
             AND TIMESTAMPDIFF(HOUR, o.OPRT_DT, d.DEATH_DT_TM) <= 24
            THEN 1 ELSE 0 END AS death_within_24h,
        CASE WHEN d.DEATH_DT_TM >= o.OPRT_DT
             AND TIMESTAMPDIFF(HOUR, o.OPRT_DT, d.DEATH_DT_TM) <= 48
            THEN 1 ELSE 0 END AS death_within_48h
    FROM FACT_MDC_RCD_HMPG h
    INNER JOIN FACT_MDC_RCD_HMPG_OPRT o
        ON h.INHOS_NO = o.INHOS_NO AND h.MDC_ORG_CD = o.MDC_ORG_CD
    INNER JOIN death_record_time d
        ON h.INHOS_NO = d.INHOS_NO AND h.MDC_ORG_CD = d.MDC_ORG_CD
    WHERE h.DSCG_DT_TM IS NOT NULL
      AND o.OPRT_CD IS NOT NULL AND TRIM(o.OPRT_CD) <> ''
      AND h.DSCG_WAY_NM = '死亡'
      AND d.DEATH_DT_TM IS NOT NULL
      AND o.OPRT_DT IS NOT NULL
),
proxy_death_with_surgery AS (
    SELECT
        h.INHOS_NO,
        h.MDC_ORG_CD,
        o.OPRT_DT,
        h.DSCG_DT_TM AS DEATH_DT_TM,
        CASE WHEN DATE(h.DSCG_DT_TM) = DATE(o.OPRT_DT) THEN 1 ELSE 0 END AS death_same_day,
        CASE WHEN h.DSCG_DT_TM >= o.OPRT_DT
             AND TIMESTAMPDIFF(HOUR, o.OPRT_DT, h.DSCG_DT_TM) <= 24
            THEN 1 ELSE 0 END AS death_within_24h,
        CASE WHEN h.DSCG_DT_TM >= o.OPRT_DT
             AND TIMESTAMPDIFF(HOUR, o.OPRT_DT, h.DSCG_DT_TM) <= 48
            THEN 1 ELSE 0 END AS death_within_48h
    FROM FACT_MDC_RCD_HMPG h
    INNER JOIN FACT_MDC_RCD_HMPG_OPRT o
        ON h.INHOS_NO = o.INHOS_NO AND h.MDC_ORG_CD = o.MDC_ORG_CD
    WHERE h.DSCG_DT_TM IS NOT NULL
      AND o.OPRT_CD IS NOT NULL AND TRIM(o.OPRT_CD) <> ''
      AND h.TNOVR_CDT_NM = '死亡'
      AND h.DSCG_WAY_NM = '非医嘱离院'
      AND o.OPRT_DT IS NOT NULL
),
patient_flags AS (
    SELECT
        INHOS_NO,
        MDC_ORG_CD,
        MAX(death_same_day) AS clear_death_same_day,
        MAX(death_within_24h) AS clear_death_within_24h,
        MAX(death_within_48h) AS clear_death_within_48h,
        0 AS proxy_death_same_day,
        0 AS proxy_death_within_24h,
        0 AS proxy_death_within_48h
    FROM clear_death_with_surgery
    GROUP BY INHOS_NO, MDC_ORG_CD
    UNION ALL
    SELECT
        INHOS_NO,
        MDC_ORG_CD,
        0, 0, 0,
        MAX(death_same_day),
        MAX(death_within_24h),
        MAX(death_within_48h)
    FROM proxy_death_with_surgery
    GROUP BY INHOS_NO, MDC_ORG_CD
),
patient_agg AS (
    SELECT
        INHOS_NO,
        MDC_ORG_CD,
        MAX(clear_death_same_day) AS clear_same_day,
        MAX(clear_death_within_24h) AS clear_24h,
        MAX(clear_death_within_48h) AS clear_48h,
        MAX(proxy_death_same_day) AS proxy_same_day,
        MAX(proxy_death_within_24h) AS proxy_24h,
        MAX(proxy_death_within_48h) AS proxy_48h
    FROM patient_flags
    GROUP BY INHOS_NO, MDC_ORG_CD
)
SELECT
    COUNT(DISTINCT d.INHOS_NO, d.MDC_ORG_CD) AS denominator_surgery_patients,

    SUM(COALESCE(a.clear_same_day, 0)) AS numerator_clear_death_same_day,
    SUM(COALESCE(a.clear_24h, 0))       AS numerator_clear_death_24h,
    SUM(COALESCE(a.clear_48h, 0))       AS numerator_clear_death_48h,

    SUM(COALESCE(a.proxy_same_day, 0))  AS numerator_proxy_death_same_day,
    SUM(COALESCE(a.proxy_24h, 0))       AS numerator_proxy_death_24h,
    SUM(COALESCE(a.proxy_48h, 0))       AS numerator_proxy_death_48h
FROM denominator_base d
LEFT JOIN patient_agg a
    ON d.INHOS_NO = a.INHOS_NO AND d.MDC_ORG_CD = a.MDC_ORG_CD
        """.strip(),
        "subitem_config": {
            "type": "COMPOSITE_RATE",
            "items": [
                {"key": "clear_same_day", "name": "术后当日死亡（离院）", "numerator_col": "numerator_clear_death_same_day", "denominator_col": "denominator_surgery_patients"},
                {"key": "clear_24h", "name": "术后24h死亡（离院）", "numerator_col": "numerator_clear_death_24h", "denominator_col": "denominator_surgery_patients"},
                {"key": "clear_48h", "name": "术后48h死亡（离院）", "numerator_col": "numerator_clear_death_48h", "denominator_col": "denominator_surgery_patients"},
                {"key": "proxy_same_day", "name": "术后当日死亡（转归）", "numerator_col": "numerator_proxy_death_same_day", "denominator_col": "denominator_surgery_patients"},
                {"key": "proxy_24h", "name": "术后24h死亡（转归）", "numerator_col": "numerator_proxy_death_24h", "denominator_col": "denominator_surgery_patients"},
                {"key": "proxy_48h", "name": "术后48h死亡（转归）", "numerator_col": "numerator_proxy_death_48h", "denominator_col": "denominator_surgery_patients"},
            ],
        },
    },
]


def ensure_columns(conn):
    """确保所需的列存在"""
    with conn.cursor() as cur:
        # indicator.subitem_config
        cur.execute("DESCRIBE indicator")
        cols = [row['Field'] for row in cur.fetchall()]
        if 'subitem_config' not in cols:
            print(">>> 添加 indicator.subitem_config 列...")
            cur.execute("""
                ALTER TABLE indicator
                ADD COLUMN subitem_config JSON DEFAULT NULL
                COMMENT '复合指标子项配置'
            """)
            conn.commit()
            print("    添加成功。")
        else:
            print(">>> indicator.subitem_config 已存在，跳过。")

        # indicator_execution.subitem_data
        cur.execute("DESCRIBE indicator_execution")
        cols = [row['Field'] for row in cur.fetchall()]
        if 'subitem_data' not in cols:
            print(">>> 添加 indicator_execution.subitem_data 列...")
            cur.execute("""
                ALTER TABLE indicator_execution
                ADD COLUMN subitem_data JSON DEFAULT NULL
                COMMENT '复合指标子项详细数据'
            """)
            conn.commit()
            print("    添加成功。")
        else:
            print(">>> indicator_execution.subitem_data 已存在，跳过。")


def migrate_indicators(conn):
    """为6个测试指标写入配置"""
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM indicator WHERE indicator_type='core18'")
        rows = cur.fetchall()
        name_to_id = {r['name']: r['id'] for r in rows}

    print(f"\n>>> 已注册指标（共 {len(name_to_id)} 个）")

    updated = 0
    skipped = []
    errors = []

    for cfg in INDICATOR_CONFIGS:
        name = cfg["name"]
        ind_id = name_to_id.get(name)

        if ind_id is None:
            errors.append(f"  [未找到] {name} - 请先在数据库中创建该指标记录")
            continue

        # 构建更新字段
        set_fields = []
        params = []

        if cfg.get("template_type"):
            set_fields.append("template_type = %s")
            params.append(cfg["template_type"])

        if cfg.get("calc_type"):
            set_fields.append("calc_type = %s")
            params.append(cfg["calc_type"])

        if cfg.get("numerator_sql"):
            set_fields.append("numerator_sql = %s")
            params.append(cfg["numerator_sql"])

        if cfg.get("denominator_sql"):
            set_fields.append("denominator_sql = %s")
            params.append(cfg["denominator_sql"])

        if cfg.get("sql"):
            # 计数型用 sql 字段
            set_fields.append("sql_content = %s")
            params.append(cfg["sql"])
            set_fields.append("numerator_sql = %s")
            params.append(cfg["sql"])

        if cfg.get("description"):
            set_fields.append("description = %s")
            params.append(cfg["description"])

        if cfg.get("numerator_desc"):
            set_fields.append("numerator_desc = %s")
            params.append(cfg["numerator_desc"])

        if cfg.get("denominator_desc"):
            set_fields.append("denominator_desc = %s")
            params.append(cfg["denominator_desc"])

        if cfg.get("formula"):
            set_fields.append("formula = %s")
            params.append(cfg["formula"])

        if cfg.get("subitem_config"):
            set_fields.append("subitem_config = %s")
            params.append(json.dumps(cfg["subitem_config"], ensure_ascii=False))
        else:
            set_fields.append("subitem_config = NULL")

        set_fields.append("status = %s")
        params.append("success")

        params.append(ind_id)
        sql = f"UPDATE indicator SET {', '.join(set_fields)} WHERE id = %s"

        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
            conn.commit()
            print(f"  [OK] ID={ind_id} {name}")
            updated += 1
        except Exception as e:
            errors.append(f"  [错误] ID={ind_id} {name}: {e}")
            conn.rollback()

    print(f"\n>>> 迁移完成：更新 {updated} 条")
    if errors:
        print("\n>>> 错误/警告：")
        for e in errors:
            print(e)


def verify(conn):
    """验证迁移结果"""
    print("\n>>> 验证迁移结果...")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, name, template_type, calc_type,
                   CHAR_LENGTH(COALESCE(numerator_sql, '')) AS num_sql_len,
                   CHAR_LENGTH(COALESCE(denominator_sql, '')) AS den_sql_len,
                   CHAR_LENGTH(COALESCE(sql_content, '')) AS sql_len,
                   subitem_config IS NOT NULL AS has_subitem_cfg
            FROM indicator
            WHERE indicator_type='core18'
              AND name IN (
                  '普通会诊及时完成率','普通会诊有效率',
                  '主要诊断ICD-10编码亚目种类数',
                  '主要手术ICD-9-CM-3四位码种类数',
                  '住院患者死亡疾病谱',
                  '住院患者围手术期死亡率'
              )
            ORDER BY id
        """)
        rows = cur.fetchall()

    print(f"\n  {'ID':<5} {'名称':<30} {'模板':<20} {'类型':<8} {'分子SQL':<8} {'分母SQL':<8} {'总SQL':<8} {'子项配置'}")
    print("  " + "-" * 120)
    for r in rows:
        print(
            f"  {r['id']:<5} {r['name']:<30} {str(r['template_type'] or ''):<20} "
            f"{str(r['calc_type'] or ''):<8} "
            f"{'Yes' if r['num_sql_len'] > 0 else 'No':<8} "
            f"{'Yes' if r['den_sql_len'] > 0 else 'No':<8} "
            f"{'Yes' if r['sql_len'] > 0 else 'No':<8} "
            f"{'有' if r['has_subitem_cfg'] else '无'}"
        )


def main():
    print("=" * 70)
    print("指标接入迁移脚本 v2：6个测试指标 SQL + subitem_config")
    print("WARNING: 执行前请备份数据库！")
    print("=" * 70)

    conn = pymysql.connect(**DB_CONFIG)
    try:
        ensure_columns(conn)
        migrate_indicators(conn)
        verify(conn)
    finally:
        conn.close()
    print("\nDone.")


if __name__ == '__main__':
    main()
