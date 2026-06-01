/**
 * 十八项核心制度 API 服务
 */
import { httpClient } from '@/config/httpClient'
import { API_ENDPOINTS } from '@/config/api'

// ======================== 类型定义 ========================

export type TemplateType = 'STRUCTURE' | 'STRUCTURE-special' | 'RATE' | 'RATE-special' | 'COMPOSITE'

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

export interface IndicatorCardItem {
  id: number
  name: string
  category: string
  calc_type: 'ratio' | 'count'
  numerator_desc: string
  denominator_desc: string
  description: string
  has_data: boolean
  rate_percent: number | null
  numerator_count: number | null
  denominator_count: number | null
  count: number | null
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

export interface IndicatorConfigData {
  cardData?: Record<string, any>
  timeTrendData?: Record<string, any>
  hospitalComparisonData?: Record<string, any>
  leftData?: Record<string, any>
  leftData1?: Record<string, any>
  leftData2?: Record<string, any>
  totalCount?: number
  totalCountLabel?: string
  dataTypes?: Array<{ name: string; key: string }>
  yAxisUnit?: string
}

export interface IndicatorConfigItem {
  indicator_key: string
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
  data: IndicatorConfigData
}

export interface IndicatorDataResponse {
  indicator_key: string
  indicator_id: number
  template_type: TemplateType
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
  dataTypes?: Array<{ name: string; key: string }>
}

// ======================== API 服务 ========================

export const core18Api = {
  getOverview: () =>
    httpClient.get<Core18Overview>(API_ENDPOINTS.core18Overview),

  getIndicatorList: (params?: { keyword?: string; category?: string }) =>
    httpClient.get<Core18Indicator[]>(API_ENDPOINTS.core18Indicators, { params }),

  getExecutionData: (params: {
    hospital_code?: string
    time_mode: 'monthly' | 'quarterly'
    time_value: string
  }) =>
    httpClient.get<IndicatorExecutionData[]>(API_ENDPOINTS.core18ExecutionData, { params }),

  getOverviewData: (params: {
    hospital_code?: string
    time_mode: 'monthly' | 'quarterly'
    time_value: string
    keyword?: string
    category?: string
  }) =>
    httpClient.get<OverviewDataResponse>(API_ENDPOINTS.core18OverviewData, { params }),

  getHospitals: () =>
    httpClient.get<Array<{ value: string; label: string }>>(
      API_ENDPOINTS.hospitals
    ),

  getDeathPatients: (params: {
    hospital_code?: string
    time_mode?: string
    time_value?: string
    page?: number
    page_size?: number
    keyword?: string
  }) =>
    httpClient.get<DeathPatientResponse>(API_ENDPOINTS.core18DeathPatients, { params }),

  getIndicatorConfigs: (params?: {
    hospital_code?: string
    time_mode?: string
    time_value?: string
  }) =>
    httpClient.get<IndicatorConfigItem[]>(API_ENDPOINTS.core18IndicatorConfig, { params }),

  getIndicatorData: (params: {
    indicator_key: string
    hospital_code?: string
    time_mode?: string
    time_value?: string
    data_type?: 'card' | 'trend' | 'hospital' | 'left' | 'all'
    selected_hospitals?: string
  }) =>
    httpClient.get<IndicatorDataResponse>(API_ENDPOINTS.core18IndicatorData, { params }),
}
