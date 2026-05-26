/**
 * 四要素执行数据 composable
 * 从 API 获取 kind=four 的执行记录，按指标 ID 映射到各模块页面
 */
import { ref } from 'vue'
import { API_ENDPOINTS } from '../config/api'

export type TimeMode = 'immediate' | 'monthly' | 'quarterly'

export interface ExecutionRecord {
  id: number
  indicator_id: number
  indicator_name: string
  status: string
  numerator_count: number | null
  denominator_count: number | null
  rate_percent: number | null
  rate_formula: string
  preview_data: { columns: string[]; rows: any[] }
  denominator_preview_data: { columns: string[]; rows: any[] }
  execution_time: string
  error: string
  hospital_results: any[]
  group_by_hospital: boolean
  // 时间筛选字段
  run_mode?: TimeMode
  time_value?: string
  time_range?: string
}

// 时间筛选选项
export const TIME_MODE_OPTIONS: { value: TimeMode; label: string }[] = [
  { value: 'immediate', label: '全量' },
  { value: 'monthly', label: '按月' },
  { value: 'quarterly', label: '按季度' },
]

export const MONTH_OPTIONS = [
  { value: '01', label: '1月' }, { value: '02', label: '2月' }, { value: '03', label: '3月' },
  { value: '04', label: '4月' }, { value: '05', label: '5月' }, { value: '06', label: '6月' },
  { value: '07', label: '7月' }, { value: '08', label: '8月' }, { value: '09', label: '9月' },
  { value: '10', label: '10月' }, { value: '11', label: '11月' }, { value: '12', label: '12月' },
]

export const QUARTER_OPTIONS = [
  { value: '1', label: '第一季度' },
  { value: '2', label: '第二季度' },
  { value: '3', label: '第三季度' },
  { value: '4', label: '第四季度' },
]

export function getQuarterLabel(q: string): string {
  const map: Record<string, string> = { '1': '一', '2': '二', '3': '三', '4': '四' }
  return map[q] || q
}

export function getTimeRangeLabel(mode: TimeMode, timeValue?: string): string {
  if (mode === 'immediate') return '全量'
  if (mode === 'monthly' && timeValue) {
    const [year, month] = timeValue.split('-')
    return `${year}年${Number(month)}月`
  }
  if (mode === 'quarterly' && timeValue) {
    const [year, q] = timeValue.split('-')
    return `${year}年${getQuarterLabel(q.replace('Q', ''))}季度`
  }
  return '全量'
}

const executionRecords = ref<ExecutionRecord[]>([])
const hospitalList = ref<{ MDC_ORG_CD: string; MDC_ORG_NM: string }[]>([])
const loading = ref(false)
const hospitalLoading = ref(false)
const error = ref<string | null>(null)

// 缓存：key = `${indicatorId}-${hospitalCode}`, value = 执行结果中该医院的记录
const hospitalResultCache = ref<Record<string, any>>({})

// 指标列表缓存（包含 category）
const indicatorsList = ref<{ id: number; name: string; category: string }[]>([])

async function fetchHospitals() {
  if (hospitalList.value.length > 0 || hospitalLoading.value) return
  hospitalLoading.value = true
  try {
    const resp = await fetch(`${API_ENDPOINTS.hospitals}`)
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    const data = await resp.json()
    hospitalList.value = data.value || data || []
  } catch (e) {
    console.error('[useFourFactorExecutions] fetchHospitals failed', e)
    hospitalList.value = []
  } finally {
    hospitalLoading.value = false
  }
}

// 获取四要素指标列表（包含 category）
async function fetchIndicators() {
  if (indicatorsList.value.length > 0) return
  try {
    const resp = await fetch(`${API_ENDPOINTS.fourIndicators}`)
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    const data = await resp.json()
    indicatorsList.value = data.map((item: any) => ({
      id: item.id,
      name: item.name,
      category: item.category || '',
    }))
  } catch (e) {
    console.error('[useFourFactorExecutions] fetchIndicators failed', e)
  }
}

// 根据指标 ID 获取分类
function getIndicatorCategory(indicatorId: number): string {
  const indicator = indicatorsList.value.find(i => i.id === indicatorId)
  if (!indicator) return 'technology' // 默认返回 technology
  // 映射 category 到四要素分类
  const cat = indicator.category || ''
  if (cat.includes('人员') || cat.includes('人员要素')) return 'personnel'
  if (cat.includes('机构') || cat.includes('机构要素')) return 'institution'
  if (cat.includes('技术') || cat.includes('技术要素')) return 'technology'
  if (cat.includes('设备') || cat.includes('设备要素')) return 'equipment'
  return 'technology'
}

// 根据指标 ID 获取指标名称
function getIndicatorName(indicatorId: number): string {
  const indicator = indicatorsList.value.find(i => i.id === indicatorId)
  return indicator?.name || `指标${indicatorId}`
}

async function fetchExecutions() {
  if (executionRecords.value.length > 0 || loading.value) return

  loading.value = true
  error.value = null
  try {
    const resp = await fetch(`${API_ENDPOINTS.indicatorExecution}?kind=four`)
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    executionRecords.value = await resp.json()
  } catch (e: any) {
    error.value = e.message || '获取执行记录失败'
    console.error('[useFourFactorExecutions]', e)
  } finally {
    loading.value = false
  }
}

export function useFourFactorExecutions() {
  /**
   * 获取指定指标+时间模式的最新成功执行记录
   * @param indicatorId 指标ID
   * @param timeMode 时间模式
   * @param timeValue 时间值（如 "2026-05" 或 "2026-Q1"）
   */
  function getLatestSuccess(indicatorId: number, timeMode?: TimeMode, timeValue?: string): ExecutionRecord | null {
    const records = executionRecords.value
      .filter(r => r.indicator_id === indicatorId && r.status === 'success')
      .filter(r => {
        if (!timeMode || timeMode === 'immediate') return true
        if (r.run_mode !== timeMode) return false
        if (timeValue && r.time_value !== timeValue) return false
        return true
      })
      .sort((a, b) => new Date(b.execution_time).getTime() - new Date(a.execution_time).getTime())
    return records[0] || null
  }

  /**
   * 获取指定指标+时间模式的最新执行记录（不限状态）
   */
  function getLatest(indicatorId: number, timeMode?: TimeMode, timeValue?: string): ExecutionRecord | null {
    const records = executionRecords.value
      .filter(r => r.indicator_id === indicatorId)
      .filter(r => {
        if (!timeMode || timeMode === 'immediate') return true
        if (r.run_mode !== timeMode) return false
        if (timeValue && r.time_value !== timeValue) return false
        return true
      })
      .sort((a, b) => new Date(b.execution_time).getTime() - new Date(a.execution_time).getTime())
    return records[0] || null
  }

  function getCount(indicatorId: number, timeMode?: TimeMode, timeValue?: string): number {
    const rec = getLatestSuccess(indicatorId, timeMode, timeValue)
    return rec?.numerator_count ?? 0
  }

  function getAlertCount(indicatorId: number, timeMode?: TimeMode, timeValue?: string): number {
    const rec = getLatestSuccess(indicatorId, timeMode, timeValue)
    return rec?.numerator_count ?? 0
  }

  function hasRecord(indicatorId: number): boolean {
    return executionRecords.value.some(r => r.indicator_id === indicatorId && r.status === 'success')
  }

  function getResult(indicatorId: number, resultType: 'ratio' | 'count' = 'ratio', timeMode?: TimeMode, timeValue?: string): string {
    const rec = getLatestSuccess(indicatorId, timeMode, timeValue)
    if (!rec) return '-'
    if (resultType === 'count') {
      return rec.numerator_count != null ? `${rec.numerator_count} 条` : '-'
    }
    return rec.rate_percent != null ? `${rec.rate_percent.toFixed(2)}%` : '-'
  }

  function getStatus(indicatorId: number, timeMode?: TimeMode, timeValue?: string): string {
    const rec = getLatest(indicatorId, timeMode, timeValue)
    return rec?.status || 'pending'
  }

  function getPreviewData(indicatorId: number, timeMode?: TimeMode, timeValue?: string): { columns: string[]; rows: any[] } | null {
    const rec = getLatestSuccess(indicatorId, timeMode, timeValue)
    return rec?.preview_data || null
  }

  async function getPreviewDataByHospital(indicatorId: number, hospitalCode: string, timeMode?: TimeMode, timeValue?: string): Promise<{ columns: string[]; rows: any[] } | null> {
    if (hospitalCode === 'all') {
      const rec = getLatestSuccess(indicatorId, timeMode, timeValue)
      return rec?.preview_data || null
    }
    const result = await getHospitalResult(indicatorId, hospitalCode, timeMode, timeValue)
    if (!result) return null
    const rows = result.preview_data || []
    return { columns: rows.length ? Object.keys(rows[0]) : [], rows }
  }

  async function getDenominatorPreviewDataByHospital(indicatorId: number, hospitalCode: string, timeMode?: TimeMode, timeValue?: string): Promise<{ columns: string[]; rows: any[] } | null> {
    if (hospitalCode === 'all') {
      const rec = getLatestSuccess(indicatorId, timeMode, timeValue)
      return rec?.denominator_preview_data || null
    }
    const result = await getHospitalResult(indicatorId, hospitalCode, timeMode, timeValue)
    if (!result) return null
    const rows = result.denominator_preview_data || []
    return { columns: rows.length ? Object.keys(rows[0]) : [], rows }
  }

  function getDenominatorPreviewData(indicatorId: number, timeMode?: TimeMode, timeValue?: string): { columns: string[]; rows: any[] } | null {
    const rec = getLatestSuccess(indicatorId, timeMode, timeValue)
    return rec?.denominator_preview_data || null
  }

  function getHospitalResults(indicatorId: number, timeMode?: TimeMode, timeValue?: string): any[] {
    const rec = getLatestSuccess(indicatorId, timeMode, timeValue)
    return rec?.hospital_results || []
  }

  /**
   * 获取指定医院/全省的执行记录数量
   * 返回 -1 表示没有执行记录或数据不存在，返回 0 表示有数据但 count 为 0
   */
  async function getCountByHospital(indicatorId: number, hospitalCode: string, timeMode?: TimeMode, timeValue?: string): Promise<number> {
    if (hospitalCode === 'all') {
      const rec = getLatestSuccess(indicatorId, timeMode, timeValue)
      if (!rec) return -1
      return rec.numerator_count ?? 0
    }
    const result = await getHospitalResult(indicatorId, hospitalCode, timeMode, timeValue)
    if (!result) return -1
    return result.numerator_count ?? 0
  }

  async function getDenominatorCountByHospital(indicatorId: number, hospitalCode: string, timeMode?: TimeMode, timeValue?: string): Promise<number> {
    if (hospitalCode === 'all') {
      const rec = getLatestSuccess(indicatorId, timeMode, timeValue)
      if (!rec) return -1
      return rec.denominator_count ?? 0
    }
    const result = await getHospitalResult(indicatorId, hospitalCode, timeMode, timeValue)
    if (!result) return -1
    return result.denominator_count ?? 0
  }

  async function refresh() {
    executionRecords.value = []
    clearHospitalResultCache()
    await fetchExecutions()
  }

  /**
   * 获取指定指标+医院的最新执行结果中该医院的记录（从 group_by_hospital 执行中取）。
   * 会调用后端 API 按医院查询，缓存结果。
   */
  async function getHospitalResult(indicatorId: number, hospitalCode: string, timeMode?: TimeMode, timeValue?: string): Promise<any | null> {
    // 缓存 key 包含时间参数
    const cacheKey = `${indicatorId}-${hospitalCode}-${timeMode || 'immediate'}-${timeValue || ''}`
    if (hospitalResultCache.value[cacheKey] !== undefined) {
      return hospitalResultCache.value[cacheKey]
    }
    try {
      // 构建请求 URL，添加时间筛选参数
      const params = new URLSearchParams({
        indicator_id: String(indicatorId),
        hospital_code: hospitalCode,
      })
      if (timeMode && timeMode !== 'immediate') {
        params.set('time_mode', timeMode)
        if (timeValue) {
          params.set('time_value', timeValue)
        }
      }
      const resp = await fetch(`${API_ENDPOINTS.executionByHospital(indicatorId, hospitalCode)}?${params}`)
      if (!resp.ok) {
        hospitalResultCache.value[cacheKey] = null
        return null
      }
      const exec = await resp.json()
      if (!exec || !exec.hospital_results || !exec.hospital_codes) {
        hospitalResultCache.value[cacheKey] = null
        return null
      }
      // hospital_results 顺序与 hospital_codes 一一对应
      const idx = exec.hospital_codes.indexOf(hospitalCode)
      const result = idx >= 0 ? exec.hospital_results[idx] : null
      hospitalResultCache.value[cacheKey] = result
      return result
    } catch (e) {
      console.error('[useFourFactorExecutions] getHospitalResult failed', e)
      hospitalResultCache.value[cacheKey] = null
      return null
    }
  }

  /** 清除医院结果缓存（刷新时调用） */
  function clearHospitalResultCache() {
    hospitalResultCache.value = {}
  }

  /**
   * 注释：以下函数已废弃，请使用 getRuleCount 替代
   * function getMockCount(id: string, metric: string) {
   *   const rule = rules.find(r => r.id === id)
   *   if (!rule) return metric
   *   const cnt = rule.mode === 'alert' ? getAlertCount(rule.indicator_id) : getCount(rule.indicator_id)
   *   if (cnt <= 0) return metric
   *   return metric.replace(/\d+/, String(cnt))
   * }
   */

  function getRuleCount(id: string, metric: string): string {
    return metric
  }

  /**
   * 通用数字替换：将 metric 模板中的数字替换为真实 count
   * 如 metric="3家机构异常", count=5 → "5家机构异常"
   */
  function formatCountInMetric(metric: string, count: number): string {
    if (!metric || count < 0) return metric
    return metric.replace(/\d+(\.\d+)?/, String(count))
  }

  return {
    executionRecords,
    hospitalList,
    loading,
    hospitalLoading,
    error,
    fetchExecutions,
    fetchHospitals,
    fetchIndicators,
    getIndicatorCategory,
    getIndicatorName,
    getLatestSuccess,
    getLatest,
    getCount,
    getAlertCount,
    getResult,
    getStatus,
    getPreviewData,
    getPreviewDataByHospital,
    getDenominatorPreviewDataByHospital,
    getDenominatorPreviewData,
    getHospitalResults,
    getCountByHospital,
    getDenominatorCountByHospital,
    getHospitalResult,
    clearHospitalResultCache,
    formatCountInMetric,
    hasRecord,
    refresh,
  }
}
