/**
 * 十八项核心制度 API 服务
 */
import { httpClient } from '@/config/httpClient'
import { API_ENDPOINTS } from '@/config/api'

// ======================== 类型定义 ========================

export type TemplateType = 'STRUCTURE' | 'STRUCTURE-special' | 'RATE' | 'RATE-special' | 'TABLE'

export interface Core18Overview {
  total_indicators: number
  computed_indicators: number
  pending_indicators: number
  failed_indicators: number
}

export interface Core18Indicator {
  id: number
  name: string
  category: string
  seq: number
  scope: string
  formula: string
  description: string
  numerator_desc: string
  denominator_desc: string
  calc_type: 'ratio' | 'count'
  status: string
}

export interface IndicatorExecutionData {
  indicator_id: number
  indicator_name: string
  category: string
  calc_type: 'ratio' | 'count'
  has_data: boolean
  rate_percent: number | null
  numerator_count: number | null
  denominator_count: number | null
}

// ======================== 总览卡片子指标类型 ========================

export interface SubIndicatorCardItem {
  indicator_id: number
  display_name: string
  rate_percent: number | null
  count: number | null
  calc_type: 'ratio' | 'count'
}

export interface IndicatorCardItem {
  id: number
  name: string
  category: string
  calc_type: 'ratio' | 'count'
  numerator_desc: string
  denominator_desc: string
  description: string
  has_data: boolean
  // 比值型指标字段
  rate_percent: number | null
  numerator_count: number | null
  denominator_count: number | null
  // 计数型指标字段
  count: number | null
  // 虚拟父指标相关字段
  is_virtual_parent: boolean
  parent_name?: string
  sub_indicators?: SubIndicatorCardItem[]
  rate_ratio?: number | null
}

export interface OverviewDataResponse {
  indicators: IndicatorCardItem[]
  categories: string[]
}

export interface DeathPatient {
  id: number
  patient_id: string
  patient_name: string
  department: string
  hospital: string
  death_basis: string
  death_basis_detail: string
  death_record_source: string
  death_time?: string
}

export interface DeathPatientResponse {
  total: number
  page: number
  page_size: number
  data: DeathPatient[]
}

// ======================== 指标分析台类型 ========================

export interface SubIndicatorItem {
  indicator_id: number
  display_name: string
  view_mode: 'rate' | 'structure' | 'ratio'
}

export interface IndicatorConfigData {
  cardData?: Record<string, any>
  timeTrendData?: Record<string, any>
  hospitalComparisonData?: Record<string, any>
  leftData?: Record<string, any>
  leftData1?: Record<string, any>
  leftData2?: Record<string, any>
  totalCount?: number
  totalCountLabel?: string
  leftChartLimit?: number
}

export interface IndicatorConfigItem {
  indicator_id: number
  indicator_name: string
  template_type: TemplateType
  title: string
  showDeathToggle: boolean
  rateLabel: string
  rateUnit: string
  maxRate: number
  yAxisUnit: string
  leftTitle?: string
  leftChartTitle?: string
  leftChartTitle1?: string
  leftChartTitle2?: string
  leftChartColor: string
  leftChartColor1: string
  leftChartColor2: string
  timeComparisonTitle: string
  hospitalComparisonTitle: string
  totalCountLabel?: string
  rankingMode?: 'single' | 'double' | 'multi'
  // 虚拟父指标相关字段
  is_virtual_parent: boolean
  parent_name?: string
  sub_indicators?: SubIndicatorItem[]
  table_headers?: string[]
  rate_ratio_value?: number | null
  data: IndicatorConfigData
}

export interface IndicatorDataResponse {
  indicator_id: number
  indicator_name?: string
  template_type?: TemplateType
  has_data: boolean
  rate_percent?: number | null
  numerator_count?: number | null
  denominator_count?: number | null
  totalCount?: number
  cardData?: Record<string, any>
  timeTrendData?: Record<string, any>
  hospitalComparisonData?: Record<string, any>
  leftData?: Record<string, any>
  leftData1?: Record<string, any>
  leftData2?: Record<string, any>
  multiRankingData?: Record<string, any>
  dataTypes?: Array<{ name: string; key: string }>
  // 虚拟父指标相关字段
  is_virtual_parent?: boolean
  parent_name?: string
  rate_ratio_value?: number | null
  time_mode?: string
  time_value?: string
}

// ======================== API 服务 ========================

export const core18Api = {
  /**
   * 获取总览统计数据
   */
  getOverview: () =>
    httpClient.get<Core18Overview>(API_ENDPOINTS.core18Overview),

  /**
   * 获取十八项核心制度指标列表
   * @param params 可选参数: keyword, category
   */
  getIndicatorList: (params?: { keyword?: string; category?: string }) =>
    httpClient.get<Core18Indicator[]>(API_ENDPOINTS.core18Indicators, { params }),

  /**
   * 获取指标执行数据
   * @param params hospital_code, time_mode, time_value
   */
  getExecutionData: (params: {
    hospital_code?: string
    time_mode: 'monthly' | 'quarterly'
    time_value: string
  }) =>
    httpClient.get<IndicatorExecutionData[]>(API_ENDPOINTS.core18ExecutionData, { params }),

  /**
   * 总览页面统一接口 - 获取指标卡片数据和分类列表
   * @param params hospital_code, time_mode, time_value, keyword, category
   */
  getOverviewData: (params: {
    hospital_code?: string
    time_mode: 'monthly' | 'quarterly'
    time_value: string
    keyword?: string
    category?: string
  }) =>
    httpClient.get<OverviewDataResponse>(API_ENDPOINTS.core18OverviewData, { params }),

  /**
   * 获取医院列表
   */
  getHospitals: () =>
    httpClient.get<Array<{ value: string; label: string }>>(
      API_ENDPOINTS.hospitals
    ),

  /**
   * 获取死亡患者列表
   * @param params hospital_code, time_mode, time_value, page, page_size, keyword
   */
  getDeathPatients: (params: {
    hospital_code?: string
    time_mode?: string
    time_value?: string
    page?: number
    page_size?: number
    keyword?: string
  }) =>
    httpClient.get<DeathPatientResponse>(API_ENDPOINTS.core18DeathPatients, { params }),

  /**
   * 获取所有指标的分析台配置（元数据，含 template_type）
   * @param params hospital_code, time_mode, time_value
   */
  getIndicatorConfigs: (params?: {
    hospital_code?: string
    time_mode?: string
    time_value?: string
  }) =>
    httpClient.get<IndicatorConfigItem[]>(API_ENDPOINTS.core18IndicatorConfig, { params }),

  /**
   * 获取单个指标的图表数据（各子组件按自身时间筛选调用）
   * @param params indicator_id, hospital_code, time_mode, time_value, data_type, selected_hospitals, death_type_filter
   */
  getIndicatorData: (params: {
    indicator_id: number
    hospital_code?: string
    time_mode?: string
    time_value?: string
    data_type?: 'card' | 'trend' | 'hospital' | 'left' | 'all'
    selected_hospitals?: string
    death_type_filter?: 'actual' | 'estimated'
    sub_indicator?: number
  }) =>
    httpClient.get<IndicatorDataResponse>(API_ENDPOINTS.core18IndicatorData, { params }),
}
