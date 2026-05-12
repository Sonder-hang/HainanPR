/**
 * 四要素监管 API 服务
 */
import { httpClient } from '@/config/httpClient'
import { API_ENDPOINTS } from '@/config/api'

export interface Hospital {
  value: string
  label: string
  level: string
  type: string
}

export interface PersonnelViolation {
  id: number
  physician_name: string
  physician_id: string
  violation_type: string
  violation_type_display: string
  violation_details: string
  prescription_count: number
  distance_traveled: number
  time_window: number
}

export interface InstitutionAnomaly {
  id: number
  anomaly_type: string
  anomaly_type_display: string
  anomaly_details: string
  threshold_value: number
  actual_value: number
  excess_percent: number
}

export interface TechnologyWarning {
  id: number
  warning_type: string
  warning_type_display: string
  warning_details: string
  patient_name: string
  patient_id: string
  risk_level: string
  risk_level_display: string
}

export interface EquipmentAnomaly {
  id: number
  equipment_name: string
  equipment_code: string
  anomaly_type: string
  anomaly_type_display: string
  anomaly_details: string
  positive_rate: number | null
  usage_hours: number
}

export interface PersonnelMonitoringData {
  total_violations: number
  unresolved_violations: number
  violations_by_type: Record<string, number>
  recent_violations: PersonnelViolation[]
  physicians_at_risk: Array<{
    name: string
    violations: number
    level: string
  }>
}

export interface InstitutionMonitoringData {
  total_anomalies: number
  unresolved_anomalies: number
  anomalies_by_type: Record<string, number>
  hospitals_over_capacity: Array<{
    name: string
    type: string
    excess: string
  }>
  recent_anomalies: InstitutionAnomaly[]
}

export interface TechnologyMonitoringData {
  total_warnings: number
  unresolved_warnings: number
  warnings_by_type: Record<string, number>
  high_risk_warnings: Array<{
    patient: string
    type: string
    hospital: string
  }>
  recent_warnings: TechnologyWarning[]
}

export interface EquipmentMonitoringData {
  total_anomalies: number
  unresolved_anomalies: number
  anomalies_by_type: Record<string, number>
  equipment_needing_attention: Array<{
    name: string
    positive_rate: string
    usage_hours: string
    status: string
  }>
  recent_anomalies: EquipmentAnomaly[]
}

export const monitoringApi = {
  /**
   * 获取医院列表
   */
  getHospitals: () => httpClient.get<Hospital[]>(API_ENDPOINTS.hospitals),

  /**
   * 人员监管
   */
  getPersonnelMonitoring: () =>
    httpClient.get<PersonnelMonitoringData>(API_ENDPOINTS.personnelMonitoring),

  /**
   * 机构监管
   */
  getInstitutionMonitoring: () =>
    httpClient.get<InstitutionMonitoringData>(API_ENDPOINTS.institutionMonitoring),

  /**
   * 技术监管
   */
  getTechnologyMonitoring: () =>
    httpClient.get<TechnologyMonitoringData>(API_ENDPOINTS.technologyMonitoring),

  /**
   * 设备监管
   */
  getEquipmentMonitoring: () =>
    httpClient.get<EquipmentMonitoringData>(API_ENDPOINTS.equipmentMonitoring),

  /**
   * 预警分类
   */
  getAlertCategories: () =>
    httpClient.get<Array<{ name: string; count: number; color: string; route: string }>>(
      API_ENDPOINTS.alertCategories
    ),
}
