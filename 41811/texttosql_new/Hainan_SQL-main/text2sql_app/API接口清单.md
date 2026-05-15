# API 接口清单

基址：`http://127.0.0.1:8000`  
全局 CORS 已开启（`allow_origins=["*"]`）  
Swagger 文档：http://127.0.0.1:8000/docs

---

## 一、页面路由

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 指标调试主页 |
| GET | `/log` | 工作流日志页 |

---

## 二、基础接口

### 1. 健康检查

```
GET /api/health
```

**响应：**

```json
{ "ok": true, "model": "qwen3.5-35b-a3b" }
```

---

### 2. 获取所有指标

```
GET /api/indicators
```

**响应：**

```json
{
  "indicators": [
    {
      "指标名": "患者入院8小时内查房率",
      "类型": "分子分母比值型",
      "指标计算公式": "...",
      "分子描述": "...",
      "分母描述": "...",
      "涉及到表": ["FACT_ADMN_MDC_HTR_RCD", "FACT_INHOS_ODR_INFMT"],
      "numerator_sql": "SELECT ...",
      "denominator_sql": "SELECT ...",
      "last_system_prompt": "...",
      "last_user_message": "..."
    }
  ]
}
```

---

### 3. 获取所有表名

```
GET /api/tables_list
```

**响应：**

```json
{
  "tables": [
    { "name": "FACT_ADMN_MDC_HTR_RCD", "comment": "入院病历记录" },
    { "name": "FACT_INHOS_ODR_INFMT", "comment": "住院医嘱信息" }
  ]
}
```

---

### 4. 刷新表结构

```
POST /api/refresh_tables
```

从数据库重新提取表结构并更新 `tables.json`。

**响应：**

```json
{ "ok": true, "stdout": "..." }
```

失败时 `ok: false`，附带 `stdout` / `stderr`。

---

## 三、指标管理

### 5. 新增指标

```
POST /api/indicators/add
Content-Type: application/json
```

**请求体：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| 指标名 | string | 是 | |
| 类型 | string | 是 | `分子分母比值型` / `统计型` / `大模型分析型` |
| 涉及到表 | string[] | 否 | 物理表名列表 |
| 指标计算公式 | string | 否 | 比值型用 |
| 分子描述 | string | 否 | 比值型用 |
| 分母描述 | string | 否 | 比值型用 |
| 指标描述 | string | 否 | 统计型/分析型用 |
| numerator_sql | string | 否 | 已确认的分子 SQL |
| denominator_sql | string | 否 | 已确认的分母 SQL |
| sql | string | 否 | 统计型/分析型已确认 SQL |
| system_prompt | string | 否 | 最后一次使用的 system prompt |
| user_message | string | 否 | 最后一次使用的 user message |

**响应：**

```json
{ "ok": true, "index": 3, "indicator": { ... } }
```

---

### 6. 更新指标

```
PUT /api/indicators/{index}
Content-Type: application/json
```

**路径参数：** `index` — 指标在数组中的下标（从 0 开始）

**请求体：** 同新增指标。

**响应：**

```json
{ "ok": true, "indicator": { ... } }
```

---

### 7. 删除指标

```
DELETE /api/indicators/{index}
```

**响应：**

```json
{ "ok": true, "removed": "患者入院8小时内查房率" }
```

---

## 四、SQL 生成

### 8. 生成 SQL（同步）

```
POST /api/run
Content-Type: application/json
```

**请求体：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| indicator_index | int | 否* | 已有指标下标 |
| indicator_type | string | 否* | 新增时的指标类型 |
| indicator_name | string | 否* | 新增时的指标名 |
| selected_tables | string[] | 否 | 为 null 则使用指标自带的"涉及到表" |
| indicator_formula | string | 否 | 覆盖指标计算公式 |
| supplement_info | string | 否 | 覆盖补充信息 |
| numerator_desc | string | 否 | 覆盖分子描述 |
| denominator_desc | string | 否 | 覆盖分母描述 |
| indicator_desc | string | 否 | 覆盖指标描述（统计型/分析型） |
| custom_system_prompt | string | 否 | 自定义 system prompt |
| custom_user_message | string | 否 | 自定义 user message |
| regenerate | object | 否 | 再生成上下文（见下） |
| mode | string | 否 | 前端操作模式: `select` / `create` / `edit` |
| prompt_modified | bool | 否 | 用户是否修改了默认 Prompt（默认 false） |
| conversation_id | string | 否 | 会话 ID，再生成时复用首次生成的 conversation_id |
| conversation_history | object[] | 否 | 多轮对话历史（见下） |

> *`indicator_index` 和 `indicator_type + indicator_name` 二选一。

**`conversation_history` 数组（多轮对话）：**

每个元素代表一轮已完成的对话：

| 字段 | 类型 | 说明 |
|------|------|------|
| assistant_raw | string | 该轮模型的原始回复 |
| user_feedback | string | 用户对该轮的反馈/修改建议 |

**`regenerate` 对象（兼容旧方式，多轮对话时可忽略）：**

| 字段 | 类型 | 说明 |
|------|------|------|
| previous_numerator_sql | string | 上次分子 SQL |
| previous_denominator_sql | string | 上次分母 SQL |
| numerator_error | string | 分子错误 |
| denominator_error | string | 分母错误 |
| previous_sql | string | 上次 SQL（统计/分析型） |
| sql_error | string | SQL 错误（统计/分析型） |
| user_feedback | string | 用户补充说明 |

**成功响应（比值型）：**

```json
{
  "request_id": "uuid",
  "conversation_id": "uuid",
  "request_ts_iso": "2026-04-04T...",
  "ok": true,
  "indicator": { ... },
  "indicator_type": "分子分母比值型",
  "selected_tables": ["..."],
  "numerator_sql": "SELECT ...",
  "denominator_sql": "SELECT ...",
  "numerator_count": 123,
  "denominator_count": 456,
  "rate_percent": 26.9737,
  "rate_formula": "123/456=0.269737",
  "preview_columns": ["col1", "col2"],
  "preview_rows": [["v1", "v2"]],
  "denominator_preview_columns": ["col1"],
  "denominator_preview_rows": [["v1"]],
  "numerator_preview_error": null,
  "denominator_preview_error": null,
  "numerator_attempts": [{ "attempt": 1, "sql": "...", "count": 123, "error": null }],
  "denominator_attempts": [{ "attempt": 1, "sql": "...", "count": 456, "error": null }],
  "cache_hit": false,
  "error": null
}
```

**成功响应（统计型/分析型）：**

```json
{
  "request_id": "uuid",
  "conversation_id": "uuid",
  "ok": true,
  "indicator_type": "统计型",
  "sql": "SELECT ...",
  "count": 789,
  "analysis": "",
  "preview_columns": ["col1"],
  "preview_rows": [["v1"]],
  "preview_error": null,
  "attempts": [{ "attempt": 1, "sql": "...", "count": 789, "error": null }],
  "error": null
}
```

失败时 `ok: false`，`error` 含原因。

---

### 9. 生成 SQL（流式 SSE）

```
POST /api/run/stream
Content-Type: application/json
```

请求体与 `/api/run` 完全相同。响应为 SSE（`text/event-stream`）。

**事件类型：**

| event | data 说明 |
|-------|----------|
| `start` | `request_id`, `request_ts_iso`, `indicator_type` |
| `attempt_start` | `attempt`, `max_attempts` |
| `llm_delta` | `role`(`reasoning`/`content`), `text` — 模型 token 增量 |
| `llm_end` | `attempt`, `llm_seconds` |
| `phase` | `phase`: `mysql_count` / `mysql_preview` |
| `error` | `message` — 致命错误 |
| `done` | 与 `/api/run` 同步响应相同的完整 JSON |

---

### 10. 测试 SQL

```
POST /api/test_sql
Content-Type: application/json
```

**请求体：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sql | string | 是 | 要执行的 SQL |
| limit | int | 否 | 返回行数上限，默认 200 |

**响应：**

```json
{
  "ok": true,
  "columns": ["col1", "col2"],
  "rows": [["v1", "v2"]],
  "count": 100,
  "error": null,
  "count_error": null
}
```

---

### 11. Prompt 预览

```
POST /api/prompt_preview
Content-Type: application/json
```

构建 Prompt 但不调用模型，用于预览。

**请求体：**

| 字段 | 类型 | 说明 |
|------|------|------|
| indicator_index | int | 已有指标下标 |
| indicator_type | string | 指标类型（新增时） |
| indicator_name | string | 指标名（新增时） |
| selected_tables | string[] | 勾选的表 |
| indicator_formula | string | 指标公式 |
| numerator_desc | string | 分子描述 |
| denominator_desc | string | 分母描述 |
| indicator_desc | string | 指标描述 |

**响应：**

```json
{
  "system_prompt": "你是一个专业的医疗监管数据库工程师...",
  "user_message": "【指标名称】..."
}
```

---

## 五、日志

### 12. 获取工作流日志

```
GET /api/logs?max_requests=40
```

**响应：**

日志按 `conversation_id` 分组为会话，每个会话包含多个 round（多轮迭代）：

```json
{
  "requests": [
    {
      "conversation_id": "uuid",
      "ts_iso": "...",
      "rounds": [
        {
          "request_id": "uuid",
          "ts_iso": "...",
          "conversation_id": "uuid",
          "run": { "event": "run_start", "payload": { "轮次": 1, "是否再生成": false, ... } },
          "llm_rounds": [ ... ],
          "end": { ... }
        },
        {
          "request_id": "uuid2",
          "ts_iso": "...",
          "conversation_id": "uuid",
          "run": { "event": "run_start", "payload": { "轮次": 2, "是否再生成": true, "用户反馈": "分子条件不对" } },
          "llm_rounds": [ ... ],
          "end": { ... }
        }
      ]
    }
  ]
}
```

---

### 13. 删除日志

```
DELETE /api/logs/{conversation_id}
```

删除该会话（conversation_id）下所有轮次的日志。也兼容传入单个 request_id。

**响应：**

```json
{ "ok": true, "removed": 12, "files": ["workflow_20260404.jsonl"] }
```

---

## 六、Prompt 日志

### 14. 获取全部 Prompt 日志

```
GET /api/prompt_log
```

返回 `prompt_log.json` 全部内容（按指标名分组的历史记录）。

---

### 15. 获取指定指标的 Prompt 历史

```
GET /api/prompt_log/{indicator_name}
```

**响应：**

```json
{
  "indicator_name": "患者入院8小时内查房率",
  "history": [
    {
      "timestamp": "2026-04-04T...",
      "system_prompt": "...",
      "user_message": "...",
      "result_ok": true,
      "sql_summary": "..."
    }
  ]
}
```

---

## 七、错误码

| HTTP 状态码 | 说明 |
|-------------|------|
| 200 | 成功（业务失败通过 `ok: false` + `error` 表达） |
| 400 | 参数错误（如 index 越界、SQL 为空） |
| 404 | 资源不存在 |
| 500 | 服务端异常（文件缺失等） |
| 504 | 脚本执行超时 |
