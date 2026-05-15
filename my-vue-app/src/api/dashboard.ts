/**
 * Dashboard API 服务
 */
import { httpClient } from '@/config/httpClient'
import { API_ENDPOINTS } from '@/config/api'

export interface DashboardAlert {
  id: number
  time: string
  factor: 'personnel' | 'institution' | 'technology' | 'equipment'
  factor_display: string
  level: 'high' | 'warning' | 'info'
  level_display: string
  message: string
  hospital: string
  department: string
  patient_id: string
  handled: boolean
  handled_by: string
  handled_time: string
  handler_comment: string
}

export interface FactorDistribution {
  name: string
  count: number
  color: string
  percent: number
  route: string
}

export interface AlertCategory {
  name: string
  count: number
  color: string
  route: string
}

export interface DashboardOverview {
  personnel_alerts: number
  institution_alerts: number
  technology_alerts: number
  equipment_alerts: number
  recent_alerts: DashboardAlert[]
  alert_categories: AlertCategory[]
  factor_distribution: FactorDistribution[]
}

export interface DashboardStats {
  date: string
  personnel_alerts: number
  institution_alerts: number
  technology_alerts: number
  equipment_alerts: number
  total_alerts: number
  high_risk_count: number
}

export const dashboardApi = {
  /**
   * 获取总览数据
   */
  getOverview: () => httpClient.get<DashboardOverview>(API_ENDPOINTS.dashboardOverview),

  /**
   * 获取统计数据
   */
  getStats: () => httpClient.get<DashboardStats[]>(API_ENDPOINTS.dashboardStats),

  /**
   * 获取预警列表
   */
  getAlerts: (params?: {
    level?: string
    factor?: string
    handled?: boolean
  }) => httpClient.get<DashboardAlert[]>(API_ENDPOINTS.dashboardAlerts, { params }),

  /**
   * 获取要素分布
   */
  getFactorDistribution: () => httpClient.get<FactorDistribution[]>(API_ENDPOINTS.factorDistribution),
}
