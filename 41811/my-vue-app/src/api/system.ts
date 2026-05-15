/**
 * System API 服务
 */
import { httpClient } from '@/config/httpClient'
import { API_ENDPOINTS } from '@/config/api'

export interface HealthCheck {
  ok: boolean
  service: string
  version: string
  backend_health: {
    ok: boolean
    model?: string
    error?: string
  }
}

export interface SystemConfig {
  indicator_types: Array<{ value: string; label: string }>
  calc_methods: Array<{ value: string; label: string }>
  factor_types: Array<{ value: string; label: string }>
}

export interface Hospital {
  value: string
  label: string
  level: string
  type: string
}

export interface RefreshTablesResult {
  ok: boolean
  synced_tables?: number
  table_list?: string[]
  error?: string
  stdout?: string
  stderr?: string
}

export const systemApi = {
  /**
   * 健康检查
   */
  healthCheck: () => httpClient.get<HealthCheck>(API_ENDPOINTS.health),

  /**
   * 获取系统配置
   */
  getConfig: () => httpClient.get<SystemConfig>(API_ENDPOINTS.config),

  /**
   * 获取医院列表
   */
  getHospitals: () => httpClient.get<Hospital[]>(API_ENDPOINTS.hospitals),

  /**
   * 刷新表结构
   */
  refreshTables: () => httpClient.post<RefreshTablesResult>(API_ENDPOINTS.refreshTables),
}
