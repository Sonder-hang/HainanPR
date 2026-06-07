<template v-bind="$attrs">
  <div class="flex h-full min-h-0 flex-col bg-[#F4F6F8] p-5 font-sans overflow-y-auto">
    <header class="mb-5 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-2">
        <h1 class="text-[24px] font-bold text-[#1F264D]">{{ title }}</h1>
        <button
          @click="helpVisible = true"
          class="w-5 h-5 rounded-full bg-[#b8c9e8]/60 text-[#596080] text-[12px] font-medium flex items-center justify-center hover:bg-[#2E57E5] hover:text-white transition-colors cursor-pointer"
          title="指标说明"
        >?</button>
      </div>
    </header>

    <div class="grid grid-cols-12 gap-5">
      <div class="col-span-12 lg:col-span-4">
        <div class="rounded-lg bg-white p-5 shadow-sm">
          <div class="mb-4">
            <h2 class="mb-3 text-[18px] font-bold text-[#1F264D]">{{ leftTitle }}</h2>
            <div class="flex flex-wrap items-center gap-2.5">
              <select
                v-model="leftQueryType"
                class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
              >
                <option value="monthly">按月份</option>
                <option value="quarterly">按季度</option>
              </select>
              <select
                v-if="leftQueryType === 'monthly'"
                v-model="leftSelectedYearForMonth"
                class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
              >
                <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}年</option>
              </select>
              <select
                v-if="leftQueryType === 'monthly'"
                v-model="leftSelectedMonth"
                class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
              >
                <option v-for="month in monthOptions" :key="month.value" :value="month.value">{{ month.label }}</option>
              </select>
              <template v-if="leftQueryType === 'quarterly'">
                <select
                  v-model="leftQuarterYear"
                  class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
                >
                  <option v-for="year in quarterYearOptions" :key="year" :value="year">{{ year }}年</option>
                </select>
                <select
                  v-model="leftQuarterNum"
                  class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
                >
                  <option v-for="q in quarterOptions" :key="q.value" :value="q.value">{{ q.label }}</option>
                </select>
              </template>
              <div v-if="showDeathToggle" class="flex rounded border border-[#D1D5DB] bg-white overflow-hidden">
                <button
                  type="button"
                  class="px-3 py-1.5 text-[14px] font-medium transition-colors"
                  :class="leftDataType === 'actual' ? 'bg-[#2E57E5] text-white' : 'text-[#374151] hover:bg-[#F3F4F6]'"
                  @click="leftDataType = 'actual'"
                >
                  实际死亡
                </button>
                <button
                  type="button"
                  class="px-3 py-1.5 text-[14px] font-medium transition-colors"
                  :class="leftDataType === 'estimated' ? 'bg-[#2E57E5] text-white' : 'text-[#374151] hover:bg-[#F3F4F6]'"
                  @click="leftDataType = 'estimated'"
                >
                  预估死亡
                </button>
              </div>
              <button
                type="button"
                class="h-8 rounded bg-[#2E57E5] px-4 text-[14px] font-medium text-white transition-colors hover:bg-[#1E4BD8]"
                @click="fetchLeftData"
              >
                查询
              </button>
            </div>
          </div>

          <div ref="leftChartRef" style="height: 500px;"></div>
        </div>
      </div>

      <div class="col-span-12 lg:col-span-8 space-y-5">
        <div class="rounded-lg bg-white p-5 shadow-sm">
          <div class="mb-4 flex flex-wrap items-center justify-between gap-4">
            <h2 class="text-[18px] font-bold text-[#1F264D]">{{ timeComparisonTitle }}</h2>
            <div class="flex items-center gap-2.5">
              <select
                v-model="timeComparisonType"
                class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
              >
                <option value="monthly">按月份</option>
                <option value="quarterly">按季度</option>
              </select>
              <div v-if="showDeathToggle" class="flex rounded border border-[#D1D5DB] bg-white overflow-hidden">
                <button
                  type="button"
                  class="px-3 py-1.5 text-[14px] font-medium transition-colors"
                  :class="timeComparisonDataType === 'actual' ? 'bg-[#2E57E5] text-white' : 'text-[#374151] hover:bg-[#F3F4F6]'"
                  @click="timeComparisonDataType = 'actual'"
                >
                  实际死亡
                </button>
                <button
                  type="button"
                  class="px-3 py-1.5 text-[14px] font-medium transition-colors"
                  :class="timeComparisonDataType === 'estimated' ? 'bg-[#2E57E5] text-white' : 'text-[#374151] hover:bg-[#F3F4F6]'"
                  @click="timeComparisonDataType = 'estimated'"
                >
                  预估死亡
                </button>
              </div>
              <button
                type="button"
                class="h-8 rounded bg-[#2E57E5] px-4 text-[14px] font-medium text-white transition-colors hover:bg-[#1E4BD8]"
                @click="fetchTrendData"
              >
                查询
              </button>
            </div>
          </div>
          <div ref="timeComparisonChartRef" class="w-full" style="height: 300px;"></div>
        </div>

        <div class="rounded-lg bg-white p-5 shadow-sm">
          <div class="mb-4 flex flex-wrap items-center justify-between gap-4">
            <h2 class="text-[18px] font-bold text-[#1F264D]">{{ hospitalComparisonTitle }}</h2>
            <div class="flex flex-wrap items-center gap-2.5">
              <MultiSelectDropdown
                v-model="selectedHospitals"
                :options="hospitals"
                placeholder="请选择医院"
              />
              <select
                v-model="hospitalComparisonType"
                class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
              >
                <option value="monthly">按月份</option>
                <option value="quarterly">按季度</option>
              </select>
              <select
                v-if="hospitalComparisonType === 'quarterly'"
                v-model="selectedComparisonYear"
                class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
              >
                <option v-for="year in quarterYearOptions" :key="year" :value="year">{{ year }}年</option>
              </select>
              <select
                v-if="hospitalComparisonType === 'quarterly'"
                v-model="selectedComparisonQuarter"
                class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
              >
                <option v-for="q in quarterOptions" :key="q.value" :value="q.value">{{ q.label }}</option>
              </select>
              <template v-if="hospitalComparisonType === 'monthly'">
                <select
                  v-model="selectedComparisonYearForMonth"
                  class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
                >
                  <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}年</option>
                </select>
                <select
                  v-model="selectedComparisonMonth"
                  class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
                >
                  <option v-for="month in monthOptions" :key="month.value" :value="month.value">{{ month.label }}</option>
                </select>
              </template>
              <div v-if="showDeathToggle" class="flex rounded border border-[#D1D5DB] bg-white overflow-hidden">
                <button
                  type="button"
                  class="px-3 py-1.5 text-[14px] font-medium transition-colors"
                  :class="hospitalComparisonDataType === 'actual' ? 'bg-[#2E57E5] text-white' : 'text-[#374151] hover:bg-[#F3F4F6]'"
                  @click="hospitalComparisonDataType = 'actual'"
                >
                  实际死亡
                </button>
                <button
                  type="button"
                  class="px-3 py-1.5 text-[14px] font-medium transition-colors"
                  :class="hospitalComparisonDataType === 'estimated' ? 'bg-[#2E57E5] text-white' : 'text-[#374151] hover:bg-[#F3F4F6]'"
                  @click="hospitalComparisonDataType = 'estimated'"
                >
                  预估死亡
                </button>
              </div>
              <button
                type="button"
                class="h-8 rounded bg-[#2E57E5] px-4 text-[14px] font-medium text-white transition-colors hover:bg-[#1E4BD8]"
                @click="fetchHospitalData"
              >
                查询
              </button>
            </div>
          </div>
          <div ref="hospitalComparisonChartRef" class="w-full" style="height: 300px;"></div>
        </div>
      </div>
    </div>
  </div>

  <div v-if="helpVisible" class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50 backdrop-blur-sm" @click.self="helpVisible = false">
    <div class="w-[560px] bg-white rounded-[2px] shadow-2xl flex flex-col animate-fade-in border border-[#b8c9e8]/60">
      <div class="px-5 py-3.5 border-b border-[#b8c9e8]/60 flex justify-between items-center bg-[#e8eef9]">
        <h2 class="text-[14px] font-bold text-[#1F264D]">指标说明</h2>
        <button @click="helpVisible = false" class="p-1.5 hover:bg-[#b8c9e8]/30 rounded-full text-[#596080] transition-colors"><X class="w-4 h-4" /></button>
      </div>
      <div class="flex-1 overflow-y-auto p-5 space-y-4">
        <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
          <h3 class="font-bold text-[#1F264D] text-[13px] mb-2">指标定义</h3>
          <p class="text-[12px] text-[#596080] leading-relaxed">
            {{ title }}：统计指定周期内多项指标的分类数据，通过排行榜展示各分类的数值大小，支持历史趋势分析和医院间对比。
          </p>
        </div>
        <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
          <h3 class="font-bold text-[#1F264D] text-[13px] mb-2">数据分类</h3>
          <ul class="text-[12px] text-[#596080] space-y-1.5 leading-relaxed">
            <li v-for="type in dataTypes" :key="type.key" class="flex items-start gap-2">
              <span class="mt-0.5 w-1.5 h-1.5 rounded-full bg-[#2E57E5] shrink-0"></span>
              {{ type.name }}
            </li>
          </ul>
        </div>
        <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
          <h3 class="font-bold text-[#1F264D] text-[13px] mb-2">数据来源</h3>
          <ul class="text-[12px] text-[#596080] space-y-1.5 leading-relaxed">
            <li class="flex items-start gap-2">
              <span class="mt-0.5 w-1.5 h-1.5 rounded-full bg-[#2E57E5] shrink-0"></span>
              入院病历记录：患者入院时的基本信息记录
            </li>
            <li class="flex items-start gap-2">
              <span class="mt-0.5 w-1.5 h-1.5 rounded-full bg-[#2E57E5] shrink-0"></span>
              住院医嘱信息：患者在院期间的医嘱执行记录
            </li>
            <li class="flex items-start gap-2">
              <span class="mt-0.5 w-1.5 h-1.5 rounded-full bg-[#2E57E5] shrink-0"></span>
              诊断记录：患者住院期间的诊断信息
            </li>
            <li class="flex items-start gap-2">
              <span class="mt-0.5 w-1.5 h-1.5 rounded-full bg-[#2E57E5] shrink-0"></span>
              病案首页：患者出院时的病案首页汇总信息
            </li>
          </ul>
        </div>
        <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
          <h3 class="font-bold text-[#1F264D] text-[13px] mb-2">统计口径</h3>
          <p class="text-[12px] text-[#596080] leading-relaxed">
            统计周期内，各分类指标的数值和分布情况。左侧排行榜按数值大小排序展示，趋势分析展示各分类的历史变化趋势，医院对比展示不同医院间的差异分布。
          </p>
        </div>
        <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
          <h3 class="font-bold text-[#1F264D] text-[13px] mb-2">计算方式</h3>
          <p class="text-[12px] text-[#596080] leading-relaxed">
            支持按年份和按月份两种统计口径，默认展示当年数据。左侧排行榜按数值降序排列，可通过顶部筛选器切换查询时间范围和数据类型。
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import { X } from 'lucide-vue-next'
import MultiSelectDropdown from '@/components/ui/MultiSelectDropdown.vue'
import { core18Api } from '@/api/core18'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  indicator_id: { type: Number, default: null },
  title: { type: String, default: '指标分析' },
  leftTitle: { type: String, default: '结构化数据率' },
  timeComparisonTitle: { type: String, default: '趋势分析' },
  hospitalComparisonTitle: { type: String, default: '医院对比' },
  showDeathToggle: { type: Boolean, default: false },
  dataTypes: {
    type: Array as () => Array<{ name: string; key: string }>,
    default: () => [{ name: '数据1', key: 'data1' }, { name: '数据2', key: 'data2' }]
  },
  yAxisUnit: { type: String, default: '%' },
  initTimeMode: { type: String, default: '' },
  initTimeValue: { type: String, default: '' },
  initHospital: { type: String, default: '' },
})

const now = new Date()
const currentYear = now.getFullYear()

// ---- 筛选器选项 ----
const yearOptions = Array.from({ length: 10 }, (_, i) => currentYear - 5 + i)
const quarterYearOptions = Array.from({ length: 7 }, (_, i) => currentYear - 3 + i)
const monthOptions = [
  { value: 1, label: '1月' }, { value: 2, label: '2月' }, { value: 3, label: '3月' },
  { value: 4, label: '4月' }, { value: 5, label: '5月' }, { value: 6, label: '6月' },
  { value: 7, label: '7月' }, { value: 8, label: '8月' }, { value: 9, label: '9月' },
  { value: 10, label: '10月' }, { value: 11, label: '11月' }, { value: 12, label: '12月' }
]
const quarterOptions = [
  { value: '1', label: 'Q1（一季度）' },
  { value: '2', label: 'Q2（二季度）' },
  { value: '3', label: 'Q3（三季度）' },
  { value: '4', label: 'Q4（四季度）' },
]

// ---- 医院列表 ----
const hospitals = ref<Array<{ value: string; label: string }>>([])
const fetchHospitals = async () => {
  try {
    const res = await core18Api.getHospitals() as Array<{ value: string; label: string }>
    hospitals.value = [{ value: 'all', label: '全省' }, ...(res || [])]
    const firstHospital = (res || [])[0]
    selectedHospitals.value = firstHospital ? ['all', firstHospital.value] : ['all']
  } catch (e) {
    console.error('获取医院列表失败:', e)
    hospitals.value = [{ value: 'all', label: '全省' }]
    selectedHospitals.value = ['all']
  }
}

// ---- 筛选器状态 ----
const selectedHospitals = ref<string[]>(['all'])
// 当前生效的医院范围（由 initHospital 初始化，受顶部筛选器控制）
const appliedHospital = ref('all')
watch(() => props.initHospital, (val) => {
  if (val) appliedHospital.value = val
}, { immediate: true })
// appliedHospital 变化时重新拉取排行榜和趋势数据
watch(appliedHospital, () => {
  fetchLeftData()
  fetchTrendData()
})

// 左侧排行榜
const leftQueryType = ref<'monthly' | 'quarterly'>('monthly')
const leftSelectedYearForMonth = ref(currentYear)
const leftSelectedMonth = ref(1)
const leftQuarterYear = ref(currentYear)
const leftQuarterNum = ref('1')
const leftDataType = ref('actual')

// 趋势图
const timeComparisonType = ref<'monthly' | 'quarterly'>('monthly')
const timeComparisonDataType = ref('actual')

// 医院对比
const hospitalComparisonType = ref<'monthly' | 'quarterly'>('monthly')
const selectedComparisonYear = ref(currentYear)
const selectedComparisonQuarter = ref('1')
const selectedComparisonYearForMonth = ref(currentYear)
const selectedComparisonMonth = ref(1)
const hospitalComparisonDataType = ref('actual')

// ---- 本地数据状态 ----
const localLeftData = ref<Record<string, any>>({})
const localTimeTrendData = ref<Record<string, any>>({})
const localHospitalComparisonData = ref<Record<string, any>>({})

// ---- 加载状态 ----
const isFetchingLeft = ref(false)
const isFetchingTrend = ref(false)
const isFetchingHospital = ref(false)

// ---- 帮助弹窗 ----
const helpVisible = ref(false)

// ---- 时间值构建函数 ----
const buildLeftTimeValue = () => {
  if (leftQueryType.value === 'monthly') {
    return `${leftSelectedYearForMonth.value}-${String(leftSelectedMonth.value).padStart(2, '0')}`
  }
  return `${leftQuarterYear.value}-Q${leftQuarterNum.value}`
}

const buildTrendTimeValue = () => {
  return timeComparisonType.value === 'monthly'
    ? `${currentYear}-${String(now.getMonth() + 1).padStart(2, '0')}`
    : `${currentYear}-Q${Math.ceil((now.getMonth() + 1) / 3)}`
}

const buildHospitalTimeValue = () => {
  if (hospitalComparisonType.value === 'monthly') {
    return `${selectedComparisonYearForMonth.value}-${String(selectedComparisonMonth.value).padStart(2, '0')}`
  }
  return `${selectedComparisonYear.value}-Q${selectedComparisonQuarter.value}`
}

// ---- 三个独立拉取函数 ----
const fetchLeftData = async () => {
  if (!props.indicator_id) return
  isFetchingLeft.value = true
  try {
    const res = await core18Api.getIndicatorData({
      indicator_id: props.indicator_id,
      time_mode: leftQueryType.value,
      time_value: buildLeftTimeValue(),
      data_type: 'left',
      hospital_code: appliedHospital.value === 'all' ? undefined : appliedHospital.value,
    }) as any
    if (res) {
      // 规范化 leftData 结构
      // COMPOSITE_RATE 格式: {actual: {time: {key: rate}}, estimated: {}}
      // 转为 {actual: {year: {key: rate}}, estimated: {year: {}}} 供季度/月度查询使用
      const norm = (raw: unknown): Record<string, any> => {
        if (raw && typeof raw === 'object' && !Array.isArray(raw)) {
          const obj = raw as Record<string, unknown>
          if (obj.actual) {
            return {
              actual: { [currentYear]: obj.actual },
              estimated: { [currentYear]: obj.estimated || {} },
            }
          }
        }
        return raw as Record<string, any>
      }
      localLeftData.value = norm(res.leftData)
      updateLeftChart()
    }
  } catch (e) {
    console.error('获取左侧排行榜数据失败:', e)
  } finally {
    isFetchingLeft.value = false
  }
}

const fetchTrendData = async () => {
  if (!props.indicator_id) return
  isFetchingTrend.value = true
  try {
    const res = await core18Api.getIndicatorData({
      indicator_id: props.indicator_id,
      time_mode: timeComparisonType.value,
      time_value: buildTrendTimeValue(),
      data_type: 'trend',
      hospital_code: appliedHospital.value === 'all' ? undefined : appliedHospital.value,
    }) as any
    if (res) {
      localTimeTrendData.value = res.timeTrendData || {}
      updateTimeComparisonChart()
    }
  } catch (e) {
    console.error('获取趋势数据失败:', e)
  } finally {
    isFetchingTrend.value = false
  }
}

const fetchHospitalData = async () => {
  if (!props.indicator_id) return
  isFetchingHospital.value = true
  try {
    const res = await core18Api.getIndicatorData({
      indicator_id: props.indicator_id,
      time_mode: hospitalComparisonType.value,
      time_value: buildHospitalTimeValue(),
      data_type: 'hospital',
      selected_hospitals: selectedHospitals.value.join(','),
    }) as any
    if (res) {
      localHospitalComparisonData.value = res.hospitalComparisonData || {}
      updateHospitalComparisonChart()
    }
  } catch (e) {
    console.error('获取医院对比数据失败:', e)
  } finally {
    isFetchingHospital.value = false
  }
}

// ---- 辅助函数 ----
const generateMonthlyData = (yearData: Record<string, number> | undefined, month: number): Record<string, number> => {
  if (!yearData) return {}
  const monthFactors = [0.95, 0.9, 1.0, 0.98, 1.02, 1.0, 1.05, 1.03, 0.97, 0.95, 0.92, 0.98]
  const factor = monthFactors[month - 1] || 1
  return Object.fromEntries(Object.entries(yearData).map(([key, value]) => [key, Number((value * factor).toFixed(1))]))
}

const generateQuarterlyData = (yearData: Record<string, number>, quarter: number) => {
  const monthFactors = [0.9, 0.85, 0.95, 0.92, 0.98, 1.0, 1.05, 1.08, 1.02, 0.95, 0.88, 0.92]
  const quarterMonths: Record<string, number[]> = {
    '1': [0, 1, 2],
    '2': [3, 4, 5],
    '3': [6, 7, 8],
    '4': [9, 10, 11],
  }
  const months = quarterMonths[String(quarter)] || [0, 1, 2]
  const factor = (monthFactors[months[0]] + monthFactors[months[1]] + monthFactors[months[2]]) / 3
  return Object.fromEntries(Object.entries(yearData).map(([key, value]) => [key, Number((value * factor).toFixed(1))]))
}

// ---- 图表渲染 ----
const leftChartRef = ref<HTMLElement | null>(null)
const timeComparisonChartRef = ref<HTMLElement | null>(null)
const hospitalComparisonChartRef = ref<HTMLElement | null>(null)
let leftChart: echarts.ECharts | null = null
let timeComparisonChart: echarts.ECharts | null = null
let hospitalComparisonChart: echarts.ECharts | null = null

const getDynamicYAxisMax = (data: number[]) => {
  const max = Math.max(...data.filter(v => typeof v === 'number' && !isNaN(v)))
  if (max === 0) return 100
  if (max <= 1) return 1
  if (max <= 5) return 5
  if (max <= 10) return 10
  if (max <= 20) return 20
  if (max <= 30) return 30
  if (max <= 50) return 50
  if (max <= 100) return 100
  return Math.ceil(max * 1.2)
}

const updateLeftChart = () => {
  if (!leftChart) return
  const dataSource = localLeftData.value[leftDataType.value]
  if (!dataSource) return

  let data: Record<string, number>
  if (leftQueryType.value === 'quarterly') {
    const yearData = dataSource[leftQuarterYear.value] || dataSource[currentYear]
    if (!yearData) return
    data = generateQuarterlyData(yearData, parseInt(leftQuarterNum.value))
  } else if (leftQueryType.value === 'monthly') {
    const yearData = dataSource[leftSelectedYearForMonth.value] || dataSource[currentYear]
    if (!yearData) return
    data = generateMonthlyData(yearData, leftSelectedMonth.value)
  } else {
    data = dataSource[currentYear]
    if (!data) return
  }
  const chartData = (props.dataTypes as any[]).map(type => ({ name: type.name, value: data[type.key] || 0 }))
  const sortedData = [...chartData].sort((a, b) => a.value - b.value)
  leftChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: (params: any) => `${sortedData[params[0].dataIndex].name}<br/>${props.yAxisUnit}: ${sortedData[params[0].dataIndex].value}${props.yAxisUnit}` },
    grid: { left: '3%', right: '12%', bottom: '3%', top: '3%', containLabel: true },
    xAxis: { type: 'value', name: props.yAxisUnit, axisLabel: { formatter: `{value}${props.yAxisUnit}` } },
    yAxis: { type: 'category', data: sortedData.map(item => item.name), axisLabel: { fontSize: 11, width: 80, overflow: 'truncate' } },
    series: [{ type: 'bar', data: sortedData.map(item => ({ value: item.value, itemStyle: { color: '#2E57E5' } })), label: { show: true, position: 'right', formatter: `{c}${props.yAxisUnit}` }, barWidth: 18 }]
  }, true)
}

const updateTimeComparisonChart = () => {
  if (!timeComparisonChart) return
  const trendData = localTimeTrendData.value[timeComparisonDataType.value]
  const dataSource = localLeftData.value[timeComparisonDataType.value]
  if (!dataSource || !trendData) return

  let xAxisData: string[] = []
  let series: any[] = []

  if (timeComparisonType.value === 'quarterly') {
    xAxisData = ['Q1', 'Q2', 'Q3', 'Q4']
    const quarterFactors = [0.9, 0.95, 1.0, 1.05]
    const baseYearData = dataSource[currentYear] || dataSource[Object.keys(dataSource)[0]]
    if (!baseYearData) return
    series = (props.dataTypes as any[]).map(type => ({
      name: type.name, type: 'line', smooth: true,
      data: quarterFactors.map(f => Number(((baseYearData[type.key] ?? 0) * f).toFixed(1)))
    }))
  } else if (timeComparisonType.value === 'monthly') {
    xAxisData = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    const baseYearData = dataSource[currentYear] || dataSource[Object.keys(dataSource)[0]]
    if (!baseYearData) return
    series = (props.dataTypes as any[]).map(type => ({
      name: type.name, type: 'line', smooth: true,
      data: monthOptions.map((_, idx) => {
        const monthFactors = [0.9, 0.85, 0.95, 0.92, 0.98, 1.0, 1.05, 1.08, 1.02, 0.95, 0.88, 0.92]
        return Number(((baseYearData[type.key] ?? 0) * monthFactors[idx] / 12).toFixed(1))
      })
    }))
  } else {
    xAxisData = trendData.years || []
    series = (props.dataTypes as any[]).map(type => ({ name: type.name, type: 'line', data: trendData[type.key] || [], smooth: true }))
  }

  timeComparisonChart.setOption({
    tooltip: { trigger: 'axis', formatter: (params: any) => { let result = params[0].name + '<br/>'; params.forEach((item: any) => { result += item.marker + item.seriesName + ': ' + item.value + props.yAxisUnit + '<br/>' }); return result } },
    legend: { data: series.map(s => s.name), top: 10, type: 'scroll' },
    grid: { left: '3%', right: '4%', bottom: '3%', top: 60, containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: xAxisData },
    yAxis: { type: 'value', name: props.yAxisUnit, axisLabel: { formatter: `{value}${props.yAxisUnit}` } },
    series: series.map(s => ({ ...s, lineStyle: { width: 2 } }))
  }, true)
}

const updateHospitalComparisonChart = () => {
  if (!hospitalComparisonChart) return
  const hospitalDataMap = localHospitalComparisonData.value[hospitalComparisonDataType.value]
  if (!hospitalDataMap) return

  const series: any[] = (props.dataTypes as any[]).map(type => ({ name: type.name, type: 'bar', data: [] }))
  const yearKey = hospitalComparisonType.value === 'monthly'
    ? String(selectedComparisonYearForMonth.value)
    : selectedComparisonYear.value
  selectedHospitals.value.forEach(hospitalKey => {
    const hospital = hospitalDataMap[hospitalKey]
    if (!hospital) {
      ;(props.dataTypes as any[]).forEach((_, index) => { series[index].data.push(0) })
      return
    }
    ;(props.dataTypes as any[]).forEach((_, index) => {
      series[index].data.push(hospital[yearKey] ?? 0)
    })
  })
  hospitalComparisonChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: (params: any) => { let result = params[0].name + '<br/>'; params.forEach((item: any) => { result += item.marker + item.seriesName + ': ' + item.value + props.yAxisUnit + '<br/>' }); return result } },
    legend: { data: (props.dataTypes as any[]).map(t => t.name), top: 10, type: 'scroll' },
    grid: { left: '3%', right: '4%', bottom: '3%', top: 60, containLabel: true },
    xAxis: { type: 'category', data: selectedHospitals.value.map(key => (hospitals.value as Array<{ value: string; label: string }>).find(h => h.value === key)?.label || key) },
    yAxis: { type: 'value', name: props.yAxisUnit, axisLabel: { formatter: `{value}${props.yAxisUnit}` }, max: getDynamicYAxisMax(series.flat()) },
    series
  }, true)
}

const initCharts = () => {
  if (leftChartRef.value) {
    leftChart = echarts.init(leftChartRef.value)
  }
  if (timeComparisonChartRef.value) {
    timeComparisonChart = echarts.init(timeComparisonChartRef.value)
  }
  if (hospitalComparisonChartRef.value) {
    hospitalComparisonChart = echarts.init(hospitalComparisonChartRef.value)
  }
}

const handleResize = () => {
  leftChart?.resize()
  timeComparisonChart?.resize()
  hospitalComparisonChart?.resize()
}

onMounted(async () => {
  initCharts()
  window.addEventListener('resize', handleResize)

  // 初始化左侧时间筛选（从总览页跳转时传入）
  if (props.initTimeMode) {
    leftQueryType.value = props.initTimeMode as 'monthly' | 'quarterly'
    if (props.initTimeMode === 'monthly' && props.initTimeValue) {
      const parts = props.initTimeValue.split('-')
      leftSelectedYearForMonth.value = parseInt(parts[0])
      leftSelectedMonth.value = parseInt(parts[1])
    } else if (props.initTimeMode === 'quarterly' && props.initTimeValue) {
      const parts = props.initTimeValue.split('-Q')
      leftQuarterYear.value = parseInt(parts[0])
      leftQuarterNum.value = parts[1]
    }
  }

  await fetchHospitals()
  await Promise.all([fetchLeftData(), fetchTrendData(), fetchHospitalData()])
})
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
</style>
