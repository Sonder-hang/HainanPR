/**
 * API 配置
 */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export const API_ENDPOINTS = {
  // 系统
  health: `${API_BASE_URL}/api/system/health/`,
  config: `${API_BASE_URL}/api/system/config/`,
  hospitals: `${API_BASE_URL}/api/system/hospitals/`,
  refreshTables: `${API_BASE_URL}/api/system/refresh-tables/`,

  // 总览大屏
  dashboardOverview: `${API_BASE_URL}/api/dashboard/overview/`,
  dashboardStats: `${API_BASE_URL}/api/dashboard/stats/`,
  dashboardAlerts: `${API_BASE_URL}/api/dashboard/alerts/`,
  factorDistribution: `${API_BASE_URL}/api/dashboard/factor-distribution/`,

  // 四要素监管
  personnelMonitoring: `${API_BASE_URL}/api/monitoring/personnel/`,
  institutionMonitoring: `${API_BASE_URL}/api/monitoring/institution/`,
  technologyMonitoring: `${API_BASE_URL}/api/monitoring/technology/`,
  equipmentMonitoring: `${API_BASE_URL}/api/monitoring/equipment/`,
  alertCategories: `${API_BASE_URL}/api/monitoring/alert-categories/`,

  // 指标管理 - 四要素
  fourIndicators: `${API_BASE_URL}/api/indicators/four`,
  fourIndicator: (id: number) => `${API_BASE_URL}/api/indicators/four/${id}`,
  fourIndicatorCreate: `${API_BASE_URL}/api/indicators/four/create`,
  fourIndicatorUpdate: (id: number) => `${API_BASE_URL}/api/indicators/four/update/${id}`,
  fourIndicatorDelete: (id: number) => `${API_BASE_URL}/api/indicators/four/delete/${id}`,

  // 指标管理 - 十八项
  core18Indicators: `${API_BASE_URL}/api/indicators/core18`,
  core18Indicator: (id: number) => `${API_BASE_URL}/api/indicators/core18/${id}`,
  core18IndicatorCreate: `${API_BASE_URL}/api/indicators/core18/create`,
  core18IndicatorUpdate: (id: number) => `${API_BASE_URL}/api/indicators/core18/update/${id}`,
  core18IndicatorDelete: (id: number) => `${API_BASE_URL}/api/indicators/core18/delete/${id}`,

  // 执行相关
  indicatorExecution: `${API_BASE_URL}/api/indicators/execution/`,
  executionByHospital: (indicatorId: number, hospitalCode: string) =>
    `${API_BASE_URL}/api/indicators/execution/by-hospital/?indicator_id=${indicatorId}&hospital_code=${hospitalCode}`,
  deleteExecution: (id: number) => `${API_BASE_URL}/api/indicators/execution/${id}`,
  executeIndicator: `${API_BASE_URL}/api/indicators/execute/`,
  executeIndicatorStream: `${API_BASE_URL}/api/indicators/execute/stream/`,
  previewPage: `${API_BASE_URL}/api/indicators/execution/preview-page/`,
  testSql: `${API_BASE_URL}/api/indicators/test-sql/`,
  hospitals: `${API_BASE_URL}/api/indicators/hospitals/`,

  // 表结构
  tables: `${API_BASE_URL}/api/indicators/tables/`,
  columnMeanings: `${API_BASE_URL}/api/indicators/column-meanings/`,
  promptPreview: `${API_BASE_URL}/api/indicators/prompt-preview/`,

  // 十八项核心制度
  core18Overview: `${API_BASE_URL}/api/core18/overview/`,
  core18Analysis: `${API_BASE_URL}/api/core18/analysis/`,
  core18Execute: `${API_BASE_URL}/api/core18/execute/`,
}
