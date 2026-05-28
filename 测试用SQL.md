# 测试用SQL

### 普通会诊及时完成率

```SQL
-- 分母：同期出院患者中普通会诊文书数量明细
-- 输出所有普通会诊记录，关联病案首页的入院、出院时间（忽略具体时间范围）
SELECT 
    h.INHOS_NO,
    h.MDC_ORG_CD,
    h.ADMN_DT_TM,        -- 入院时间
    h.DSCG_DT_TM,        -- 出院时间
    c.CSTT_TP,
    c.APL_DT_TM,         -- 申请时间
    c.CRT_TM             -- 创建时间
FROM FACT_CSTT_RCD c
JOIN ods_FACT_MDC_RCD_HMPG h 
    ON c.INHOS_NO = h.INHOS_NO 
   AND c.MDC_ORG_CD = h.MDC_ORG_CD
WHERE c.CSTT_TP LIKE '%普通会诊';
-- 分子：普通会诊24小时内完成的次数明细
-- 条件：创建时间 - 申请时间 < 24小时
SELECT 
    h.INHOS_NO,
    h.MDC_ORG_CD,
    h.MDC_ORG_NM,
    h.ADMN_DT_TM,
    h.DSCG_DT_TM,
    c.CSTT_TP,
    c.APL_DT_TM,
    c.CRT_TM,
    TIMESTAMPDIFF(HOUR, c.APL_DT_TM, c.CRT_TM) AS HOURS_DIFF  -- 输出小时差便于验证
FROM FACT_CSTT_RCD c
JOIN ods_FACT_MDC_RCD_HMPG h 
    ON c.INHOS_NO = h.INHOS_NO 
   AND c.MDC_ORG_CD = h.MDC_ORG_CD
WHERE c.CSTT_TP LIKE '%普通会诊'
  AND TIMESTAMPDIFF(HOUR, c.APL_DT_TM, c.CRT_TM) < 24;
```

### 普通会诊有效率

```SQL
-- 分母：同期出院患者中普通会诊文书数量明细
-- 输出所有普通会诊记录，关联患者入院、出院时间（忽略具体时间范围筛选）
SELECT 
    h.INHOS_NO,
    h.MDC_ORG_CD,
    h.ADMN_DT_TM,          -- 入院时间
    h.DSCG_DT_TM,          -- 出院时间
    c.CSTT_TP,
    c.CSTT_DT_TM           -- 会诊结束时间
FROM FACT_CSTT_RCD c
JOIN FACT_MDC_RCD_HMPG h 
    ON c.INHOS_NO = h.INHOS_NO 
   AND c.MDC_ORG_CD = h.MDC_ORG_CD
WHERE c.CSTT_TP LIKE '%普通会诊';
-- 分子：普通会诊结束后1小时内开具相关医嘱的次数明细
-- 条件：
--   1. 会诊类型为普通会诊
--   2. 医嘱开立时间在会诊结束时间之后，且时间差 < 1小时
--   3. 排除嘱托医嘱（ODR_ITM_TP_NM NOT LIKE '%嘱托%'）和出院医嘱（ODR_CGY_NM NOT LIKE '%出院%'）
--修正后的分子
WITH ord_with_nearest_cstt AS (
    SELECT 
        od.INHOS_NO,
        od.MDC_ORG_CD,
        od.MDC_ORG_NM,
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
)
SELECT 
    h.INHOS_NO,
    h.MDC_ORG_CD,
    h.MDC_ORG_NM,
    h.ADMN_DT_TM,
    h.DSCG_DT_TM,
    t.CSTT_TP,
    t.CSTT_END_TIME,
    t.ODR_OPN_DT_TM,
    t.ODR_ITM_TP_NM,
    t.ODR_CGY_NM,
    t.MINUTES_DIFF
FROM ord_with_nearest_cstt t
JOIN FACT_MDC_RCD_HMPG h
    ON t.INHOS_NO = h.INHOS_NO
   AND t.MDC_ORG_CD = h.MDC_ORG_CD
WHERE t.rn = 1
```

### 主要诊断ICD\-10编码亚目种类数

```SQL
SELECT
    t1.MDC_ORG_CD,
    t1.MDC_ORG_NM,
    UPPER(LEFT(REPLACE(REPLACE(REPLACE(t2.DIAG_CD, '.', ''), '-', ''), ' ', ''), 5)) AS sub_category, -- 亚目（前5位）
    COUNT(DISTINCT UPPER(REPLACE(REPLACE(REPLACE(t2.DIAG_CD, '.', ''), '-', ''), ' ', ''))) AS disease_cnt, -- 该亚目下不同疾病（标准化诊断代码）数量
FROM FACT_MDC_RCD_HMPG t1
INNER JOIN FACT_MDC_RCD_HMPG_DIAG t2
    ON t1.INHOS_NO = t2.INHOS_NO
    AND t1.MDC_ORG_CD = t2.MDC_ORG_CD
WHERE t2.MAIN_DIAG_FLG = '1'          -- 仅主要诊断
  AND t2.DIAG_CD NOT IN ('', '-')    -- 排除空及无效诊断代码
  AND t1.DSCG_DT_TM IS NOT NULL
GROUP BY t1.MDC_ORG_CD, t1.MDC_ORG_NM, sub_category
ORDER BY t1.MDC_ORG_CD, sub_category;
```

### 主要手术ICD\-9\-CM\-3四位码种类数

```SQL
SELECT 
    t1.mdc_org_CD,
    t1.MDC_ORG_NM,
    count(distinct upper(left(REPLACE(REPLACE(REPLACE(t2.OPRT_CD, '.', ''), '-', ''), ' ', ''),4))) as surgery_4code_cnt
from ods_FACT_MDC_RCD_HMPG t1
INNER JOIN ods_FACT_MDC_RCD_HMPG_OPRT t2
    on t1.INHOS_NO = t2.INHOS_NO
    and t1.MDC_ORG_CD = t2.MDC_ORG_CD
    where t1.DSCG_DT_TM IS NOT NULL
    and t2.MAIN_OPRT_FLG = '1'
    and t2.OPRT_CD not in (''.'-')
group by t1.MDC_ORG_CD, t1.MDC_ORG_NM
```

### 住院患者死亡疾病谱

```SQL
SELECT 
    t1.MDC_ORG_CD,
    upper(left(REPLACE(REPLACE(REPLACE(t2.DIAG_CD, '.', ''), '-', ''), ' ', ''),5)) AS DIAG_SUBCAT_CD,
    CASE
        WHEN t1.DSCG_WAY_NM LIKE '%死亡%' THEN '离院方式死亡'
        WHEN t1.TNOVR_CDT_NM LIKE '%死亡%' AND t1.DSCG_WAY_NM like '%非医嘱%' THEN '转归情况死亡'
        ELSE NULL
    END AS death_type, 
    COUNT(DISTINCT t1.INHOS_NO) AS DEATH_PATIENT_CNT
FROM ods_FACT_MDC_RCD_HMPG t1
INNER JOIN ods_FACT_MDC_RCD_HMPG_DIAG t2
    ON t1.INHOS_NO = t2.INHOS_NO
    AND t1.MDC_ORG_CD = t2.MDC_ORG_CD
WHERE t2.MAIN_DIAG_FLG = '1'
    and t2.DIAG_CD not in ('','-')
    AND ( t1.DSCG_WAY_NM LIKE '%死亡%'
    OR (t1.TNOVR_CDT_NM LIKE '%死亡%' AND t1.DSCG_WAY_NM like '%非医嘱%') )
GROUP BY 1, 2, 3  -- 优化点：直接使用位置编号，代表按前3列分组
HAVING death_type IS NOT NULL  -- 修复点：直接使用 SELECT 中定义的别名
ORDER BY t1.MDC_ORG_CD, DIAG_SUBCAT_CD, death_type;
```

### 住院患者围手术期死亡率

```SQL
WITH 
-- 1. 分母基础：所有出院且有一次以上手术的患者（去重到患者）
denominator_base AS (
    SELECT DISTINCT h.INHOS_NO, h.MDC_ORG_CD
    FROM FACT_MDC_RCD_HMPG h
    INNER JOIN FACT_MDC_RCD_HMPG_OPRT o
        ON h.INHOS_NO = o.INHOS_NO AND h.MDC_ORG_CD = o.MDC_ORG_CD
    WHERE h.DSCG_DT_TM IS NOT NULL
      AND o.OPRT_CD IS NOT NULL
      AND TRIM(o.OPRT_CD) <> ''
),

-- 2. 从病程记录提取明确死亡时间（复用一次）
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

-- 3. 明确死亡患者（离院方式=死亡，且存在有效的死亡记录时间）与手术的关联
clear_death_with_surgery AS (
    SELECT 
        h.INHOS_NO,
        h.MDC_ORG_CD,
        o.OPRT_DT,
        d.DEATH_DT_TM,
        -- 手术当日死亡标识
        CASE WHEN DATE(d.DEATH_DT_TM) = DATE(o.OPRT_DT) THEN 1 ELSE 0 END AS death_same_day,
        -- 术后24小时死亡标识
        CASE WHEN d.DEATH_DT_TM >= o.OPRT_DT 
              AND TIMESTAMPDIFF(HOUR, o.OPRT_DT, d.DEATH_DT_TM) <= 24 
             THEN 1 ELSE 0 END AS death_within_24h,
        -- 术后48小时死亡标识
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

-- 4. 转归死亡患者（转归=死亡，离院方式=非医嘱离院）与手术的关联
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

-- 5. 聚合至患者级别：只要该患者有任意一次手术满足某条件，即视为阳性
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

-- 6. 合并两类死亡标记（同一患者可能同时有两类死亡？理论上不会，但用 SUM 去重）
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

-- 7. 最终统计：分母总数 + 各分子人数
SELECT 
    COUNT(DISTINCT d.INHOS_NO, d.MDC_ORG_CD) AS denominator_surgery_patients,
    
    SUM(COALESCE(a.clear_same_day, 0)) AS numerator_clear_death_same_day,
    SUM(COALESCE(a.clear_24h, 0))        AS numerator_clear_death_24h,
    SUM(COALESCE(a.clear_48h, 0))        AS numerator_clear_death_48h,
    
    SUM(COALESCE(a.proxy_same_day, 0))   AS numerator_proxy_death_same_day,
    SUM(COALESCE(a.proxy_24h, 0))        AS numerator_proxy_death_24h,
    SUM(COALESCE(a.proxy_48h, 0))        AS numerator_proxy_death_48h,
    
    -- 可一并计算比率（避免除零）
    ROUND(SUM(COALESCE(a.clear_same_day, 0)) * 100.0 / 
          NULLIF(COUNT(DISTINCT d.INHOS_NO, d.MDC_ORG_CD), 0), 4) AS rate_clear_same_day,
    ROUND(SUM(COALESCE(a.clear_24h, 0)) * 100.0 / 
          NULLIF(COUNT(DISTINCT d.INHOS_NO, d.MDC_ORG_CD), 0), 4) AS rate_clear_24h,
    ROUND(SUM(COALESCE(a.clear_48h, 0)) * 100.0 / 
          NULLIF(COUNT(DISTINCT d.INHOS_NO, d.MDC_ORG_CD), 0), 4) AS rate_clear_48h,
    ROUND(SUM(COALESCE(a.proxy_same_day, 0)) * 100.0 / 
          NULLIF(COUNT(DISTINCT d.INHOS_NO, d.MDC_ORG_CD), 0), 4) AS rate_proxy_same_day,
    ROUND(SUM(COALESCE(a.proxy_24h, 0)) * 100.0 / 
          NULLIF(COUNT(DISTINCT d.INHOS_NO, d.MDC_ORG_CD), 0), 4) AS rate_proxy_24h,
    ROUND(SUM(COALESCE(a.proxy_48h, 0)) * 100.0 / 
          NULLIF(COUNT(DISTINCT d.INHOS_NO, d.MDC_ORG_CD), 0), 4) AS rate_proxy_48h
FROM denominator_base d
LEFT JOIN patient_agg a 
    ON d.INHOS_NO = a.INHOS_NO AND d.MDC_ORG_CD = a.MDC_ORG_CD;
```



