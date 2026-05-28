/**
 * 指标管理 API 服务
 */
import { httpClient } from '@/config/httpClient'
import { API_ENDPOINTS } from '@/config/api'

// ======================== 类型定义 ========================

export interface Indicator {
  id: number
  name: string
  indicator_type: 'four' | 'core18'
  indicator_type_display: string
  category: string
  seq: number
  scope: string
  work_content: string
  rule_logic: string
  formula: string
  description: string
  calc_method: 'none' | 'textToSql' | 'sql' | 'prompt'
  calc_method_display: string
  sql_content: string
  prompt_content: string
  involved_tables: string[]
  numerator_desc: string
  denominator_desc: string
  numerator_sql: string
  denominator_sql: string
  status: 'pending' | 'running' | 'success' | 'failed'
  status_display: string
  is_computable: boolean
  use_llm: boolean
  platform_data_ready: boolean
  priority: string
  remark: string
  regex_match: boolean
  regex_rule: string
  calc_type: string
  template_type: string | null
  subitem_config: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

export interface IndicatorExecution {
  id: number
  indicator: number
  indicator_name: string
  execution_type: 'auto' | 'manual' | 'scheduled'
  execution_type_display: string
  kind: string                    // four | core18
  run_mode: string                // immediate | monthly | quarterly
  time_range: string              // 时间范围描述
  result_type: string             // ratio | count
  calc_method: string             // SQL录入 | 大模型Prompt
  scope: string                  // 执行范围：全省 | hospital_a | hospital_b | hospital_c
  logs: ExecutionLog[]
  numerator_sql: string
  denominator_sql: string
  sql: string
  numerator_count: number | null
  denominator_count: number | null
  rate_percent: number | null
  rate_formula: string
  result_text: string
  preview_data: {
    columns: string[]
    rows: Record<string, unknown>[]
  }
  error: string
  numerator_error: string
  denominator_error: string
  attempts: AttemptRecord[]
  llm_thinking: string
  llm_raw: string
  cache_hit: boolean
  request_id: string
  conversation_id: string
  status: 'pending' | 'running' | 'success' | 'failed'
  status_display: string
  execution_time: string
  duration_seconds: number | null
}

export interface ExecutionLog {
  time: string
  level: 'info' | 'warn' | 'error'
  message: string
}

export interface AttemptRecord {
  attempt: number
  sql: string
  count: number | null
  error: string | null
}

export interface ExecuteRequest {
  business_type?: string  // 业务分类：'core18' | 'four'
  indicator_id?: number
  indicator_index?: number
  indicator_name?: string
  selected_tables?: string[]
  indicator_formula?: string
  supplement_info?: string
  numerator_desc?: string
  denominator_desc?: string
  indicator_desc?: string
  custom_system_prompt?: string
  custom_user_message?: string
  regenerate?: RegenerateContext
  mode?: 'select' | 'create' | 'edit'
  prompt_modified?: boolean
  conversation_id?: string
  conversation_history?: ConversationHistoryItem[]
  // 执行记录字段（透传到后端保存）
  kind?: string
  run_mode?: string
  time_range?: string
  result_type?: string
  calc_method?: string
  scope?: string
  logs?: ExecutionLog[]
  group_by_hospital?: boolean
}

export interface RegenerateContext {
  previous_numerator_sql?: string
  previous_denominator_sql?: string
  numerator_error?: string
  denominator_error?: string
  previous_sql?: string
  sql_error?: string
  user_feedback?: string
}

export interface ConversationHistoryItem {
  assistant_raw: string
  user_feedback: string
}

export interface ExecuteResponse {
  ok: boolean
  request_id: string
  conversation_id: string
  indicator: Indicator
  indicator_type: string
  selected_tables: string[]
  numerator_sql: string
  denominator_sql: string
  sql: string
  /** 真实全量数据条数（执行 SQL COUNT(*) 的结果） */
  numerator_count: number | null
  denominator_count: number | null
  /** 计数型结果条数（count 指标使用） */
  count: number | null
  rate_percent: number | null
  rate_formula: string
  preview_columns: string[]
  preview_rows: Record<string, unknown>[]
  denominator_preview_columns: string[]
  denominator_preview_rows: Record<string, unknown>[]
  error: string | null
  numerator_error: string | null
  denominator_error: string | null
  numerator_attempts: AttemptRecord[]
  denominator_attempts: AttemptRecord[]
  attempts: AttemptRecord[]
  numerator_llm_thinking: string | null
  llm_thinking: string | null
  numerator_llm_raw: string | null
  llm_raw: string | null
  cache_hit: boolean
  // 新增字段
  logs: ExecutionLog[]
  duration_seconds: number | null
  group_by_hospital?: boolean
  hospital_results?: Array<{
    hospital_code: string
    hospital_name: string
    numerator_count: number | null
    denominator_count: number | null
    ratio_percent: number | null
    status: string
    error?: string
    preview_data?: Record<string, unknown>[]
  }>
}

export interface TestSqlRequest {
  sql: string
  limit?: number
}

export interface TestSqlResponse {
  ok: boolean
  columns: string[]
  rows: Record<string, unknown>[]
  count: number | null
  error: string | null
  count_error: string | null
}

export interface TableInfo {
  table_name: string
  business_definition: string
  field_count: number
}

export interface PreviewPageRequest {
  execution_id: number
  target: 'numerator' | 'denominator'
  page: number
  page_size: number
}

export interface PreviewPageResponse {
  ok: boolean
  error?: string | null
  columns: string[]
  rows: Record<string, unknown>[]
}

export interface PromptPreviewResponse {
  system_prompt: string
  user_message: string
  error?: string
}

// ======================== API 服务 ========================

export const indicatorsApi = {
  // ----- 四要素指标 -----

  /**
   * 获取四要素指标列表
   */
  getFourIndicators: (params?: { keyword?: string }) =>
    httpClient.get<Indicator[]>(API_ENDPOINTS.fourIndicators, { params }),

  /**
   * 获取四要素指标详情
   */
  getFourIndicator: (id: number) =>
    httpClient.get<Indicator>(API_ENDPOINTS.fourIndicator(id)),

  /**
   * 创建四要素指标
   */
  createFourIndicator: (data: Partial<Indicator>) =>
    httpClient.post<Indicator>(API_ENDPOINTS.fourIndicatorCreate, data),

  /**
   * 更新四要素指标
   */
  updateFourIndicator: (id: number, data: Partial<Indicator>) =>
    httpClient.put<Indicator>(API_ENDPOINTS.fourIndicatorUpdate(id), data),

  /**
   * 删除四要素指标
   */
  deleteFourIndicator: (id: number) =>
    httpClient.delete<void>(API_ENDPOINTS.fourIndicatorDelete(id)),

  // ----- 十八项核心指标 -----

  /**
   * 获取十八项指标列表
   */
  getCore18Indicators: (params?: { keyword?: string }) =>
    httpClient.get<Indicator[]>(API_ENDPOINTS.core18Indicators, { params }),

  /**
   * 获取十八项指标详情
   */
  getCore18Indicator: (id: number) =>
    httpClient.get<Indicator>(API_ENDPOINTS.core18Indicator(id)),

  /**
   * 创建十八项指标
   */
  createCore18Indicator: (data: Partial<Indicator>) =>
    httpClient.post<Indicator>(API_ENDPOINTS.core18IndicatorCreate, data),

  /**
   * 更新十八项指标
   */
  updateCore18Indicator: (id: number, data: Partial<Indicator>) =>
    httpClient.put<Indicator>(API_ENDPOINTS.core18IndicatorUpdate(id), data),

  /**
   * 删除十八项指标
   */
  deleteCore18Indicator: (id: number) =>
    httpClient.delete<void>(API_ENDPOINTS.core18IndicatorDelete(id)),

  // ----- 执行相关 -----

  /**
   * 获取执行历史
   * @param params 支持 indicator_id, keyword, status, kind, limit, offset
   */
  getExecutionHistory: (params?: {
    indicator_id?: number
    keyword?: string
    status?: string
    kind?: string
    limit?: number
    offset?: number
  }) =>
    httpClient.get<{ records: IndicatorExecution[]; total: number }>(API_ENDPOINTS.indicatorExecution, { params }),

  /**
   * 删除执行记录
   */
  deleteExecution: (id: number) =>
    httpClient.delete<void>(API_ENDPOINTS.deleteExecution(id)),

  /**
   * 执行指标（同步）
   */
  executeIndicator: (data: ExecuteRequest) =>
    httpClient.post<ExecuteResponse>(API_ENDPOINTS.executeIndicator, data),

  /**
   * 获取预览数据分页（分子/分母）
   */
  getPreviewPage: (data: PreviewPageRequest) =>
    httpClient.post<PreviewPageResponse>(API_ENDPOINTS.previewPage, data),

  /**
   * 获取医院列表
   */
  getHospitals: () =>
    httpClient.get<Array<{ MDC_ORG_CD: string; MDC_ORG_NM: string }>>(API_ENDPOINTS.hospitals),

  /**
   * 测试 SQL
   */
  testSql: (data: TestSqlRequest) =>
    httpClient.post<TestSqlResponse>(API_ENDPOINTS.testSql, data),

  // ----- 表结构 -----

  /**
   * 获取表列表
   */
  getTables: () => httpClient.get<TableInfo[]>(API_ENDPOINTS.tables),

  /**
   * 获取字段含义
   */
  getColumnMeanings: () =>
    httpClient.get<Record<string, string>>(API_ENDPOINTS.columnMeanings),

  /**
   * Prompt 预览
   */
  getPromptPreview: (data: Partial<ExecuteRequest>) =>
    httpClient.post<PromptPreviewResponse>(API_ENDPOINTS.promptPreview, data),
}

// ======================== 流式执行 ========================

export async function* executeIndicatorStream(data: ExecuteRequest) {
  const client = httpClient as unknown as {
    stream: (url: string, body?: unknown) => AsyncGenerator<string, void, unknown>
  }

  for await (const chunk of client.stream(API_ENDPOINTS.executeIndicatorStream, data)) {
    try {
      yield JSON.parse(chunk)
    } catch {
      yield { raw: chunk }
    }
  }
}
