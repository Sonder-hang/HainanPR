# 海南医院项目 — 数据库设计说明文档

> 文档版本：v1.0
> 更新日期：2026-05-18
> 数据库：MySQL (hainan_41811)

---

## 1. 数据库配置

| 配置项 | 值 |
|---|---|
| 数据库类型 | MySQL via PyMySQL |
| 连接地址 | 127.0.0.1:3306 |
| 数据库名 | hainan_41811 |
| 字符集 | utf8mb4 |
| ORM 框架 | SQLAlchemy |
| API 框架 | FastAPI |

---

## 2. ER 关系总览

```
user ────────────────────────── 用户认证与权限管理

hospital ─────────────────────── 医院基础数据（用于监控大屏）

hospital_admission_standard ─── 医院等级评审达标记录

core18_indicator (1) ──────────< core18_execution_log ── 核心18指标定义与执行日志
  （独立 core18 体系）

indicator (1) ─────────────────< indicator_execution ─── 指标定义（four + core18 统一）
  │
  └─ table_metadata (1) ───────< column_metadata ─────── 表结构元数据

four_elements_monitoring_record (1) ──┬─< personnel_violation ── 人员违规
                                       ├─< institution_anomaly ── 机构异常
                                       ├─< technology_warning ── 技术预警
                                       └─< equipment_anomaly ── 设备异常

dashboard_alert ───────────────────── 仪表盘告警
dashboard_statistics ───────────────── 仪表盘统计
text2sql_log ───────────────────────── Text2SQL 日志
```

---

## 3. 表详细说明

---

### 3.1 `user` — 用户表

存储系统用户信息。

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| id | INT (PK) | 用户唯一 ID | 1 |
| username | VARCHAR(100) UNIQUE | 登录用户名 | admin |
| password_hash | VARCHAR(255) | 密码哈希值 | bcrypt hash... |
| real_name | VARCHAR(100) | 真实姓名 | 张三 |
| role | VARCHAR(50) | 角色 | admin / viewer |
| scope_type | VARCHAR(20) | 权限范围类型 | province / hospital |
| scope_hospital_id | VARCHAR(50) | 限定医院 ID（scope_type=hospital 时生效） | HAINAN_001 |
| is_active | BOOL | 账户是否激活 | True |
| created_at | DATETIME | 创建时间 | 2025-01-01 10:00:00 |
| updated_at | DATETIME | 更新时间 | 2025-06-01 10:00:00 |

**使用场景：**
- 用户登录时查询 `username` 验证密码
- 权限过滤：根据 `scope_hospital_id` 限制医院数据访问范围

---

### 3.2 `hospital` — 医院基础信息表

存储医院基础数据，主要用于监控大屏。

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| id | VARCHAR(50) (PK) | 医院唯一 ID | HAINAN_001 |
| hospital_code | VARCHAR(50) | 医院编码（有索引） | 460001 |
| name | VARCHAR(200) | 医院名称 | 海南省人民医院 |
| level | VARCHAR(20) | 医院等级 | 三甲 |
| hospital_type | VARCHAR(20) | 类型 | 综合 |
| region | VARCHAR(100) | 所属区域 | 海口市 |
| address | VARCHAR(300) | 详细地址 | ... |
| contact | VARCHAR(50) | 联系方式 | ... |
| bed_count | INT | 床位数 | 2000 |
| is_active | INT | 是否启用 | 1 |
| created_at | DATETIME | 创建时间 | 2025-01-01 |
| updated_at | DATETIME | 更新时间 | 2025-01-01 |

**使用场景：**
- 下拉框选择医院时加载列表
- 监控大屏按医院级别、区域进行数据聚合展示
- 预警记录关联 `hospital_id`

---

### 3.3 `hospital_admission_standard` — 医院等级评审达标记录表

管理各医院的等级评审（晋升）申请与审批记录。

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| id | INT (PK) | 记录 ID | 1 |
| standard_code | VARCHAR(100) UNIQUE | 评审标准编号 | JBYL-2025-001 |
| standard_name | VARCHAR(300) | 评审标准名称 | 三级综合医院评审标准 |
| category | VARCHAR(100) | 评审类别 | 医疗质量 |
| level | VARCHAR(20) | 申报等级 | 三甲 |
| requirement | TEXT | 达标要求说明 | ... |
| documents_needed | JSON | 需提交的证明材料列表 | ["执业许可证", "床位数证明"] |
| check_items | JSON | 现场核查项目列表 | ["手术室配置", "重症监护室"] |
| pass_threshold | VARCHAR(200) | 通过分数线 | ≥800分 |
| status | VARCHAR(20) | 审批状态 | pending / approved / rejected |
| approved_hospital_id | VARCHAR(50) | 申报医院 ID | HAINAN_001 |
| approved_hospital_name | VARCHAR(200) | 申报医院名称 | 海南省人民医院 |
| approved_date | DATE | 审批通过日期 | 2025-06-01 |
| expiry_date | DATE | 证书有效期至 | 2028-06-01 |
| license_no | VARCHAR(100) | 证书编号 | L-460001 |
| license_front_image | VARCHAR(500) | 证书正面图片 URL | /uploads/license_front.jpg |
| license_back_image | VARCHAR(500) | 证书背面图片 URL | /uploads/license_back.jpg |
| other_images | JSON | 其他补充材料图片列表 | [] |
| remark | TEXT | 备注说明 | ... |
| created_at | DATETIME | 创建时间 | 2025-01-01 |
| updated_at | DATETIME | 更新时间 | 2025-06-01 |

**使用场景：**
- 管理员提交医院等级申报审批流程
- 前端展示各医院的等级证书与有效期
- 预警即将到期或已过期的证书

---

### 3.4 `core18_indicator` — 核心18项指标定义表

定义核心18项医疗质量指标的元数据，是核心18指标计算的核心配置表。

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| id | INT (PK) | 指标 ID | 1 |
| name | VARCHAR(200) | 指标名称 | 手术患者术后重返手术室率 |
| category | VARCHAR(100) | 指标分类 | 手术相关 |
| seq | INT | 排序序号 | 1 |
| scope | TEXT | 统计口径（定义哪些患者/科室纳入） | 择期手术患者 |
| work_content | TEXT | 工作内容说明 | ... |
| rule_logic | TEXT | 判定规则逻辑 | ... |
| formula | TEXT | 计算公式（文字描述） | 重返手术室人次 / 手术总人次 × 100% |
| description | TEXT | 指标详细说明 | ... |
| calc_method | VARCHAR(20) | 计算方式 | ratio / count / none |
| sql_content | TEXT | 完整计算 SQL（备选） | ... |
| prompt_content | TEXT | LLM prompt 提示词 | ... |
| involved_tables | JSON | 涉及的数据表列表 | ["emr_diagnosis", "emr_surgery"] |
| numerator_desc | TEXT | 分子定义文字说明 | 术后重返手术室的患者数 |
| denominator_desc | TEXT | 分母定义文字说明 | 同期手术患者总人数 |
| numerator_sql | TEXT | 分子 SQL 语句 | SELECT COUNT(DISTINCT patient_id) FROM ... |
| denominator_sql | TEXT | 分母 SQL 语句 | SELECT COUNT(DISTINCT patient_id) FROM ... |
| status | VARCHAR(20) | 指标状态 | pending / approved / active |
| is_computable | BOOL | 是否可计算 | True |
| use_llm | BOOL | 是否使用 LLM 生成 SQL | False |
| priority | VARCHAR(20) | 优先级 | high / medium / low |
| remark | TEXT | 备注 | ... |
| created_at | DATETIME | 创建时间 | 2025-01-01 |
| updated_at | DATETIME | 更新时间 | 2025-06-01 |

**使用场景：**
- 核心18指标配置管理页面：展示所有指标列表
- 执行计算时读取 `numerator_sql` 和 `denominator_sql` 执行查询
- 涉及多表时通过 `involved_tables` 展示指标数据来源

**使用示例：**
```python
# 后端读取指标定义并执行计算
indicator = db.query(Core18Indicator).filter(Core18Indicator.id == indicator_id).first()
num_count = db.execute(text(indicator.numerator_sql)).scalar()
den_count = db.execute(text(indicator.denominator_sql)).scalar()
rate = (num_count / den_count * 100) if den_count else 0
```

---

### 3.5 `core18_execution_log` — 核心18项指标执行日志表

记录每次对核心18指标的查询执行结果。

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| id | INT (PK) | 日志 ID | 1 |
| indicator_id | INT (FK) | 关联指标 ID | 1 |
| indicator_name | VARCHAR(200) | 指标名称（冗余存储） | 手术患者术后重返手术室率 |
| execution_type | VARCHAR(20) | 执行类型 | manual / scheduled |
| run_mode | VARCHAR(20) | 运行模式 | immediate / batch |
| time_range | VARCHAR(50) | 时间范围 | 全量 / 2025-Q1 |
| result_type | VARCHAR(20) | 结果类型 | ratio / count |
| calc_method | VARCHAR(20) | 计算方式 | SQL录入 |
| scope | VARCHAR(50) | 统计范围 | 全院 |
| logs | JSON | 执行过程日志 | [{"step": "分子查询", "result": 15}] |
| numerator_sql | TEXT | 本次分子 SQL | SELECT COUNT(*) FROM ... |
| denominator_sql | TEXT | 本次分母 SQL | SELECT COUNT(*) FROM ... |
| sql | TEXT | 完整 SQL | ... |
| numerator_count | INT | 分子计数结果 | 15 |
| denominator_count | INT | 分母计数结果 | 200 |
| rate_percent | FLOAT | 计算比率（%） | 7.5 |
| rate_formula | VARCHAR(200) | 展示公式 | 15/200×100%=7.5% |
| result_text | TEXT | 文字结果描述 | 7.5% |
| preview_data | JSON | 分子明细预览数据（前20条） | [{"patient_id": "P001", "surgery_date": "..."}] |
| denominator_preview_data | JSON | 分母明细预览数据 | [...] |
| error | TEXT | 整体错误信息 | ... |
| numerator_error | TEXT | 分子 SQL 错误 | ... |
| denominator_error | TEXT | 分母 SQL 错误 | ... |
| attempts | JSON | 重试记录 | [{"attempt": 1, "error": "..."}] |
| llm_thinking | TEXT | LLM 思考过程 | ... |
| llm_raw | TEXT | LLM 原始返回 | ... |
| cache_hit | BOOL | 是否命中缓存 | False |
| request_id | VARCHAR(100) | LLM 请求 ID | req_abc123 |
| conversation_id | VARCHAR(100) | LLM 会话 ID | conv_xyz789 |
| status | VARCHAR(20) | 执行状态 | pending / running / success / failed |
| execution_time | DATETIME | 执行时间 | 2025-06-01 10:00:00 |
| duration_seconds | FLOAT | 执行耗时（秒） | 2.35 |

**使用场景：**
- 用户点击"执行计算"后，后端记录每次执行过程
- 前端展示计算结果趋势图（历史执行记录）
- 执行失败时记录错误信息供排查
- 支持预览数据展示（前20条明细）

---

### 3.6 `indicator` — 通用指标定义表

统一的指标定义表，支持"四大指标"(four)和"核心18项"(core18)两类指标。

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| id | INT (PK) | 指标 ID | 1 |
| name | VARCHAR(200) | 指标名称 | 院内压疮发生率 |
| indicator_type | VARCHAR(20) | 指标类型 | four / core18 |
| category | VARCHAR(100) | 分类 | 安全指标 |
| seq | INT | 排序序号 | 1 |
| scope | TEXT | 统计口径 | 全院住院患者 |
| work_content | TEXT | 工作内容 | ... |
| rule_logic | TEXT | 判定规则 | ... |
| formula | TEXT | 计算公式 | (发生压疮患者数 / 住院患者总数) × 100% |
| description | TEXT | 指标描述 | ... |
| calc_method | VARCHAR(20) | 计算方式 | ratio / count / none |
| sql_content | TEXT | 完整 SQL | ... |
| prompt_content | TEXT | LLM prompt | ... |
| involved_tables | JSON | 涉及数据表 | ["emr_nursing_record"] |
| numerator_desc | TEXT | 分子说明 | 发生压疮的患者数 |
| denominator_desc | TEXT | 分母说明 | 同期住院患者总数 |
| numerator_sql | TEXT | 分子 SQL | ... |
| denominator_sql | TEXT | 分母 SQL | ... |
| status | VARCHAR(20) | 状态 | pending / active |
| is_computable | BOOL | 是否可计算 | True |
| use_llm | BOOL | 是否启用 LLM | False |
| platform_data_ready | BOOL | 平台数据是否就绪 | True |
| priority | VARCHAR(20) | 优先级 | high |
| remark | TEXT | 备注 | ... |
| regex_match | BOOL | 是否用正则匹配 | False |
| regex_rule | TEXT | 正则规则 | ... |
| calc_type | VARCHAR(20) | 结果类型 | ratio / count |
| date_field | VARCHAR(20) | 日期字段名 | discharge |
| created_at | DATETIME | 创建时间 | 2025-01-01 |
| updated_at | DATETIME | 更新时间 | 2025-06-01 |

**使用场景：**
- 统一管理所有指标（four + core18），替代原有分散体系
- 指标管理页展示所有指标，支持按类型、状态筛选
- 执行计算时与 `indicator_execution` 关联

---

### 3.7 `indicator_execution` — 通用指标执行日志表

统一体系的指标执行记录表。

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| id | INT (PK) | 日志 ID | 1 |
| indicator_id | INT (FK) | 关联指标 ID | 1 |
| indicator_name | VARCHAR(200) | 指标名称（冗余） | 院内压疮发生率 |
| execution_type | VARCHAR(20) | 执行类型 | manual / scheduled |
| kind | VARCHAR(20) | 指标种类 | core18 / four |
| run_mode | VARCHAR(20) | 运行模式 | immediate / batch |
| time_range | VARCHAR(50) | 时间范围 | 全量 / 2025-Q1 |
| result_type | VARCHAR(20) | 结果类型 | ratio / count |
| calc_method | VARCHAR(20) | 计算方式 | SQL录入 |
| scope | VARCHAR(50) | 统计范围 | 全院 |
| logs | JSON | 执行过程日志 | [...] |
| numerator_sql | TEXT | 分子 SQL | ... |
| denominator_sql | TEXT | 分母 SQL | ... |
| sql | TEXT | 完整 SQL | ... |
| numerator_count | INT | 分子计数 | 5 |
| denominator_count | INT | 分母计数 | 1000 |
| rate_percent | FLOAT | 比率（%） | 0.5 |
| rate_formula | VARCHAR(200) | 展示公式 | 5/1000×100%=0.5% |
| result_text | TEXT | 文字结果 | 0.5% |
| preview_data | JSON | 分子明细预览 | [...] |
| denominator_preview_data | JSON | 分母明细预览 | [...] |
| error | TEXT | 错误信息 | ... |
| numerator_error | TEXT | 分子 SQL 错误 | ... |
| denominator_error | TEXT | 分母 SQL 错误 | ... |
| attempts | JSON | 重试记录 | [...] |
| llm_thinking | TEXT | LLM 思考过程 | ... |
| llm_raw | TEXT | LLM 原始返回 | ... |
| cache_hit | BOOL | 缓存命中 | False |
| request_id | VARCHAR(100) | LLM 请求 ID | ... |
| conversation_id | VARCHAR(100) | LLM 会话 ID | ... |
| status | VARCHAR(20) | 执行状态 | pending / success / failed |
| execution_time | DATETIME | 执行时间 | 2025-06-01 10:00:00 |
| duration_seconds | FLOAT | 耗时（秒） | 1.25 |
| hospital_codes | JSON | 批量执行医院编码列表 | ["460001", "460002"] |
| time_mode | VARCHAR(20) | 时间粒度（月度/季度） | monthly |
| time_value | VARCHAR(20) | 时间值 | 2025-03 |
| date_field | VARCHAR(20) | 日期字段 | discharge |
| group_by_hospital | BOOL | 是否按医院分组展示 | True |
| hospital_results | JSON | 各医院分别计算结果 | [{"hospital_code": "460001", "rate": 0.5}, ...] |

**使用场景：**
- 指标计算执行后记录结果
- 支持批量按医院分别计算（`group_by_hospital=True`）
- 支持月度/季度时间维度（`time_mode=monthly/quarterly`）
- 前端展示历史执行趋势图
- hospital_codes和hospital_results对应关系为如果group_by_hospital为true，则hospital_codes为一个医院编码列表，hospital_results为一个list(dict)类型

---

### 3.8 `table_metadata` — 数据表元数据表

通过 Text2SQL 功能同步的业务数据库表结构信息。

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| id | INT (PK) | 表元数据 ID | 1 |
| table_name | VARCHAR(100) UNIQUE | 业务表名 | emr_diagnosis |
| business_definition | TEXT | 业务含义描述 | 电子病历诊断表 |
| data_granularity | TEXT | 数据粒度 | 每行一条诊断记录 |
| remarks | TEXT | 备注 | ... |
| field_count | INT | 字段数量 | 15 |
| formatted_text | TEXT | 格式化后的完整表结构文本 | (供 LLM 使用) |
| last_synced | DATETIME | 最后同步时间 | 2025-06-01 10:00:00 |
| source | VARCHAR(50) | 来源 | text2sql |

**使用场景：**
- Text2SQL 模块查询可用的业务表列表
- 前端展示表结构供用户了解数据来源
- 指标配置时选择 `involved_tables`

---

### 3.9 `column_metadata` — 数据列元数据表

与 `table_metadata` 一对一关联，存储每个字段的元数据。

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| id | INT (PK) | 列元数据 ID | 1 |
| table_id | INT (FK) | 所属表 ID | 1 |
| field_name | VARCHAR(100) | 字段名 | diagnosis_code |
| data_type | VARCHAR(50) | 数据类型 | VARCHAR(20) |
| meaning_cn | VARCHAR(500) | 字段含义（中文） | 诊断编码（ICD-10） |
| field_constraint | TEXT | 字段约束说明 | 主键，非空 |

**使用场景：**
- Text2SQL 生成 SQL 时，通过 `meaning_cn` 让 LLM 理解字段含义
- 前端表结构展示页面：展示每个表的字段详情

---

### 3.10 `four_elements_monitoring_record` — 四合理监控告警主表

"四合理"（合理用药、合理检查、合理治疗、合理收费）监控告警的主记录表。

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| id | INT (PK) | 记录 ID | 1 |
| hospital_id | VARCHAR(50) | 关联医院 ID | HAINAN_001 |
| factor | VARCHAR(20) | 违规因素 | personnel / institution / technology / equipment |
| record_type | VARCHAR(100) | 违规类型 | 超量处方 / 跨院执业 |
| title | VARCHAR(200) | 告警标题 | 跨院执业医师预警 |
| description | TEXT | 告警描述 | 医师在多个医院同时开具处方 |
| severity | VARCHAR(20) | 严重程度 | low / medium / high / critical |
| status | VARCHAR(20) | 处理状态 | pending / reviewing / resolved / dismissed |
| alert_time | DATETIME | 告警时间 | 2025-06-01 09:00:00 |
| resolved_time | DATETIME | 处理时间 | 2025-06-01 14:00:00 |
| handler | VARCHAR(100) | 处理人 | 李主任 |
| handler_comment | Text | 处理意见 | 已核实，为多点执业备案医师 |
| related_indicator_id | INT | 关联指标 ID | 5 |
| extra_data | JSON | 扩展数据 | {"prescription_id": "RX001"} |

**使用场景：**
- 监控大屏告警列表展示
- 告警详情页：展示具体违规信息和处理记录
- `factor` 字段区分四类违规，对应四个子表

---

### 3.11 `personnel_violation` — 人员违规子表

存储医师人员违规（多点执业超量处方、跨院执业等）明细。

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| id | INT (PK) | 明细 ID | 1 |
| record_id | INT (FK) | 关联告警主表 ID | 1 |
| physician_name | VARCHAR(100) | 医师姓名 | 王医生 |
| physician_id | VARCHAR(50) | 医师 ID | DOC_001 |
| violation_type | VARCHAR(50) | 违规类型 | 超量处方 / 跨院执业 |
| violation_details | TEXT | 违规详情 | 同一医师在3家医院开具抗生素处方 |
| prescription_count | INT | 处方数量（超量判断依据） | 150 |
| distance_traveled | FLOAT | 跨院行驶里程（km） | 280 |
| time_window | INT | 时间窗口（小时） | 24 |

**使用场景：**
- 医师多点执业监管：跨院超量处方检测
- 医师处方行为分析
- 关联 `four_elements_monitoring_record.factor="personnel"`

---

### 3.12 `institution_anomaly` — 机构异常子表

存储医院机构层面的异常数据（如均次费用超标、床位使用率异常）。

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| id | INT (PK) | 明细 ID | 1 |
| record_id | INT (FK) | 关联告警主表 ID | 1 |
| anomaly_type | VARCHAR(50) | 异常类型 | 均次费用超标 / 床位使用率异常 |
| anomaly_details | TEXT | 异常详情 | 月均次费用超过同级医院均值150% |
| threshold_value | INT | 阈值 | 5000 |
| actual_value | INT | 实际值 | 7800 |
| excess_percent | FLOAT | 超出百分比（%） | 56.0 |

**使用场景：**
- 医院均次费用监控
- 床位使用率异常预警
- 机构运营数据分析

---

### 3.13 `technology_warning` — 技术预警子表

存储医疗技术使用方面的预警（如技术准入不符、手术权限超标）。

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| id | INT (PK) | 明细 ID | 1 |
| record_id | INT (FK) | 关联告警主表 ID | 1 |
| warning_type | VARCHAR(50) | 预警类型 | 手术权限超标 / 技术准入不符 |
| warning_details | TEXT | 预警详情 | 主治医师独立开展四级手术 |
| patient_name | VARCHAR(100) | 患者姓名 | 张三 |
| patient_id | VARCHAR(50) | 患者 ID | PAT_001 |
| risk_level | VARCHAR(20) | 风险等级 | low / medium / high |

**使用场景：**
- 手术权限监管（低年资医师独立操作高难度手术）
- 医疗技术准入合规检查

---

### 3.14 `equipment_anomaly` — 设备异常子表

存储医疗设备使用异常（设备使用时长异常、阳性率异常）。

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| id | INT (PK) | 明细 ID | 1 |
| record_id | INT (FK) | 关联告警主表 ID | 1 |
| equipment_name | VARCHAR(200) | 设备名称 | 螺旋CT机 |
| equipment_code | VARCHAR(50) | 设备编码 | CT-001 |
| anomaly_type | VARCHAR(50) | 异常类型 | 阳性率异常 / 使用时长异常 |
| anomaly_details | TEXT | 异常详情 | CT阳性率低于标准值20个百分点 |
| positive_rate | FLOAT | 阳性率（Nullable） | 0.25 |
| usage_hours | FLOAT | 使用时长（小时） | 4500 |

**使用场景：**
- 设备使用效率分析
- CT/MRI 等检查设备阳性率监控（阳性率过低可能提示过度检查）

---

### 3.15 `dashboard_alert` — 仪表盘告警表

监控大屏上的实时告警记录。

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| id | INT (PK) | 告警 ID | 1 |
| time | DATETIME | 告警时间 | 2025-06-01 09:00:00 |
| factor | VARCHAR(20) | 告警因素 | personnel / institution / technology / equipment |
| level | VARCHAR(20) | 告警级别 | info / warning / critical |
| message | TEXT | 告警消息 | 某医师跨院开具处方超过规定次数 |
| hospital | VARCHAR(200) | 关联医院名称 | 海南省人民医院 |
| department | VARCHAR(100) | 关联科室 | 呼吸内科 |
| patient_id | VARCHAR(100) | 患者 ID | PAT_001 |
| handled | INT | 是否已处理（0/1） | 0 |
| handled_by | VARCHAR(100) | 处理人 | 李主任 |
| handled_time | DATETIME | 处理时间 | 2025-06-01 14:00:00 |
| handler_comment | Text | 处理意见 | 已核实为正常多点执业 |

**使用场景：**
- 大屏实时展示未处理告警数量
- 告警列表按级别高亮（critical 用红色）
- 支持管理员在线处理并填写处理意见

---

### 3.16 `dashboard_statistics` — 仪表盘统计数据表

存储每日/每时的统计数据聚合，用于大屏趋势图展示。

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| id | INT (PK) | 统计 ID | 1 |
| date | DATETIME UNIQUE | 统计时间点 | 2025-06-01 00:00:00 |
| personnel_alerts | INT | 人员告警数 | 5 |
| institution_alerts | INT | 机构告警数 | 3 |
| technology_alerts | INT | 技术告警数 | 2 |
| equipment_alerts | INT | 设备告警数 | 1 |
| total_alerts | INT | 总告警数 | 11 |
| high_risk_count | INT | 高风险告警数 | 2 |
| created_at | DATETIME | 创建时间 | 2025-06-01 00:05:00 |

**使用场景：**
- 大屏趋势折线图（按日/月展示告警数量变化）
- KPI 卡片展示当日告警总数和高风险数量
- 定时任务每日凌晨汇总前一天的告警统计

---

### 3.17 `text2sql_log` — Text2SQL 执行日志表

记录每次自然语言转 SQL 查询的执行记录。

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| id | INT (PK) | 日志 ID | 1 |
| user_id | INT | 用户 ID | 1 |
| user_question | TEXT | 用户输入的自然语言问题 | 查询最近一个月手术量最多的科室 |
| generated_sql | TEXT | LLM 生成的 SQL | SELECT dept, COUNT(*) FROM ... |
| sql_valid | BOOL | SQL 是否有效 | True |
| sql_error | TEXT | SQL 错误信息 | ... |
| execution_time | DATETIME | 执行时间 | 2025-06-01 10:00:00 |
| duration_ms | INT | 执行耗时（毫秒） | 1234 |
| selected_tables | JSON | 涉及的表 | ["emr_surgery", "emr_dept"] |
| llm_model | VARCHAR(100) | 调用的 LLM 模型 | gpt-4 |
| request_id | VARCHAR(100) | LLM 请求 ID | req_abc123 |
| session_id | VARCHAR(100) | 会话 ID | sess_xyz789 |
| status | VARCHAR(20) | 状态 | pending / success / failed |
| result_preview | JSON | 结果预览（最多20条） | [{"dept": "骨科", "count": 150}] |
| result_count | INT | 结果总条数 | 25 |
| indicator_name | VARCHAR(200) | 关联指标名称（可选） | 手术科室分布 |
| indicator_type | VARCHAR(50) | 关联指标类型 | core18 |

**使用场景：**
- 用户在 Text2SQL 页面提问，后端记录完整交互过程
- 管理员审计 LLM 生成 SQL 的准确性
- 统计 LLM 调用成本（按 model 聚合）
- 支持会话连续性（同一 `session_id` 可追问）

---

## 4. 字段使用模式总结

### 4.1 计算型指标的标准模式

大多数指标计算遵循以下模式：

```
indicator (配置) ──< indicator_execution (执行记录)
```

1. **配置阶段**：管理员在 `indicator` 表定义 `numerator_sql` 和 `denominator_sql`
2. **执行阶段**：用户发起计算 → 后端读取 SQL → 执行 → 结果写入 `indicator_execution`
3. **展示阶段**：前端读取历史执行记录，绘制趋势图

### 4.2 四合理监控的告警模式

```
four_elements_monitoring_record (主告警)
  ├─< personnel_violation (人员违规)
  ├─< institution_anomaly (机构异常)
  ├─< technology_warning (技术预警)
  └─< equipment_anomaly (设备异常)

主表 `factor` 字段决定查看哪个子表
```

### 4.3 LLM 与 SQL 的协作模式

| 场景 | 使用字段 |
|---|---|
| LLM 生成 SQL | `prompt_content` + `table_metadata.formatted_text` |
| 执行 SQL | `generated_sql` / `numerator_sql` / `denominator_sql` |
| LLM 思考过程 | `llm_thinking` + `llm_raw` |
| 缓存优化 | `cache_hit` |
| 重试记录 | `attempts` |
| 错误记录 | `error` / `numerator_error` / `denominator_error` |

---

## 5. 索引与约束

| 表名 | 索引字段 | 类型 |
|---|---|---|
| user | username | UNIQUE |
| hospital | hospital_code | INDEX |
| hospital_admission_standard | standard_code | UNIQUE |
| table_metadata | table_name | UNIQUE |
| dashboard_statistics | date | UNIQUE |

其余字段均无索引，在高频查询场景下（如按 `execution_time` 排序、按 `indicator_id` 筛选）可能出现性能瓶颈，建议根据实际查询频率补充复合索引。

---

## 6. 两套指标体系说明

项目中存在两套并行的指标体系：

| 对比项 | 旧体系 | 新统一体系 |
|---|---|---|
| 指标定义表 | `core18_indicator` | `indicator` |
| 执行日志表 | `core18_execution_log` | `indicator_execution` |
| 指标类型 | 仅 core18 | four + core18 |
| 批量执行 | 不支持 | 支持（`hospital_results`） |
| 时间维度 | 简单时间范围 | 支持月度/季度（`time_mode`） |
| 推荐状态 | 逐步废弃 | 优先使用 |

新体系通过 `indicator_execution.kind = "core18" | "four"` 字段区分指标类型，统一了数据模型。
