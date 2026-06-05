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
                v-model="cardQueryType"
                class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
              >
                <option value="monthly">按月份</option>
                <option value="quarterly">按季度</option>
              </select>
              <select
                v-if="cardQueryType === 'monthly'"
                v-model="cardSelectedYearForMonth"
                class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
              >
                <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}年</option>
              </select>
              <select
                v-if="cardQueryType === 'monthly'"
                v-model="cardSelectedMonth"
                class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
              >
                <option v-for="month in monthOptions" :key="month.value" :value="month.value">{{ month.label }}</option>
              </select>
              <template v-if="cardQueryType === 'quarterly'">
                <select
                  v-model="cardQuarterYear"
                  class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
                >
                  <option v-for="year in quarterYearOptions" :key="year" :value="year">{{ year }}年</option>
                </select>
                <select
                  v-model="cardQuarterNum"
                  class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
                >
                  <option v-for="q in quarterOptions" :key="q.value" :value="q.value">{{ q.label }}</option>
                </select>
              </template>
              <div v-if="showDeathToggle" class="flex rounded border border-[#D1D5DB] bg-white overflow-hidden">
                <button
                  type="button"
                  class="px-3 py-1.5 text-[14px] font-medium transition-colors"
                  :class="cardDataType === 'actual' ? 'bg-[#2E57E5] text-white' : 'text-[#374151] hover:bg-[#F3F4F6]'"
                  @click="cardDataType = 'actual'"
                >
                  实际死亡
                </button>
                <button
                  type="button"
                  class="px-3 py-1.5 text-[14px] font-medium transition-colors"
                  :class="cardDataType === 'estimated' ? 'bg-[#2E57E5] text-white' : 'text-[#374151] hover:bg-[#F3F4F6]'"
                  @click="cardDataType = 'estimated'"
                >
                  预估死亡
                </button>
              </div>
              <button
                type="button"
                class="h-8 rounded bg-[#2E57E5] px-4 text-[14px] font-medium text-white transition-colors hover:bg-[#1E4BD8]"
                @click="fetchCardData"
              >
                查询
              </button>
            </div>
          </div>

          <div class="flex items-center justify-center py-8">
            <div class="relative flex h-48 w-48 items-center justify-center">
              <svg class="absolute h-full w-full transform -rotate-90" viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke="#E6E9F2"
                  stroke-width="8"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke="#2E57E5"
                  stroke-width="8"
                  stroke-dasharray="283"
                  :stroke-dashoffset="283 - (currentRate / maxRate) * 283"
                  stroke-linecap="round"
                  class="transition-all duration-1000"
                />
              </svg>
              <div class="text-center">
                <div class="text-[36px] font-bold text-[#2E57E5]">{{ currentRate }}{{ rateUnit }}</div>
                <div class="text-[14px] text-[#596080]">{{ rateLabel }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-span-12 lg:col-span-8">
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
      </div>

      <div class="col-span-12">
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
            {{ title }}：统计指定周期内相关指标的百分率情况，通过圆形进度环直观展示当前指标率，并支持历史趋势和医院间对比分析。
          </p>
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
            统计周期内，指标的百分率计算方式为：指标事件发生次数 / 同期总人次 × 100%。支持按年份和按月份两种统计口径，可通过顶部筛选器切换查询时间范围。
          </p>
        </div>
        <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
          <h3 class="font-bold text-[#1F264D] text-[13px] mb-2">计算方式</h3>
          <p class="text-[12px] text-[#596080] leading-relaxed">
            {{ rateLabel }} = 分子事件数 / 分母总人次 × {{ rateUnit || '100%' }}。左侧圆形进度环直观展示当前周期的百分率，趋势分析展示历史变化趋势，医院对比展示不同医院间的差异。
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

// ---- 医院列表（从后端加载，含 all 全省） ----
const hospitals = ref<Array<{ value: string; label: string }>>([])
const fetchHospitals = async () => {
  try {
    const res = await core18Api.getHospitals() as Array<{ value: string; label: string }>
    hospitals.value = [{ value: 'all', label: '全省' }, ...(res || [])]
    // 默认：全省 + 医院列表第一家
    const firstHospital = (res || [])[0]
    selectedHospitals.value = firstHospital ? ['all', firstHospital.value] : ['all']
  } catch (e) {
    console.error('获取医院列表失败:', e)
    hospitals.value = [{ value: 'all', label: '全省' }]
    selectedHospitals.value = ['all']
  }
}

const props = defineProps({
  indicator_id: { type: Number, default: null },
  title: { type: String, default: '指标分析' },
  leftTitle: { type: String, default: '百分率直观展示' },
  timeComparisonTitle: { type: String, default: '趋势分析' },
  hospitalComparisonTitle: { type: String, default: '医院对比' },
  showDeathToggle: { type: Boolean, default: false },
  rateLabel: { type: String, default: '率' },
  rateUnit: { type: String, default: '%' },
  maxRate: { type: Number, default: 100 },
  yAxisUnit: { type: String, default: '%' },
  initTimeMode: { type: String, default: '' },
  initTimeValue: { type: String, default: '' },
  initHospital: { type: String, default: '' },
})

const now = new Date()
const currentYear = now.getFullYear()

// ---- 筛选器状态 ----
const selectedHospitals = ref<string[]>(['all'])
// 当前生效的医院范围（由 initHospital 初始化，受顶部筛选器控制）
const appliedHospital = ref('all')
watch(() => props.initHospital, (val) => {
  if (val) appliedHospital.value = val
}, { immediate: true })
// appliedHospital 变化时重新拉取卡片和趋势数据
watch(appliedHospital, () => {
  fetchCardData()
  fetchTrendData()
})

// 卡片
const cardQueryType = ref<'monthly' | 'quarterly'>('monthly')
const cardSelectedYearForMonth = ref(currentYear)
const cardSelectedMonth = ref(1)
const cardQuarterYear = ref(currentYear)
const cardQuarterNum = ref('1')
const cardDataType = ref('actual')

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
const currentRate = ref<number>(0)
const localCardData = ref<Record<string, Record<string, number | null>>>({})
const localTimeTrendData = ref<Record<string, any>>({})
const localHospitalComparisonData = ref<Record<string, Record<string, Record<string, number | null>>>>({})

const isFetchingCard = ref(false)
const isFetchingTrend = ref(false)
const isFetchingHospital = ref(false)

const helpVisible = ref(false)

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
  { value: '1', label: 'Q1（一季度）' }, { value: '2', label: 'Q2（二季度）' },
  { value: '3', label: 'Q3（三季度）' }, { value: '4', label: 'Q4（四季度）' },
]
const buildCardTimeValue = () => {
  if (cardQueryType.value === 'monthly') {
    return `${cardSelectedYearForMonth.value}-${String(cardSelectedMonth.value).padStart(2, '0')}`
  }
  return `${cardQuarterYear.value}-Q${cardQuarterNum.value}`
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
const fetchCardData = async () => {
  if (!props.indicator_id) return
  isFetchingCard.value = true
  try {
    const res = await core18Api.getIndicatorData({
      indicator_id: props.indicator_id,
      time_mode: cardQueryType.value,
      time_value: buildCardTimeValue(),
      data_type: 'card',
      hospital_code: appliedHospital.value === 'all' ? undefined : appliedHospital.value,
    }) as any
    if (res) {
      localCardData.value = res.cardData || {}
      const dataSource = localCardData.value[cardDataType.value] || {}
      currentRate.value = dataSource[buildCardTimeValue()] ?? dataSource[cardSelectedYearForMonth.value] ?? 0
    }
  } catch (e) {
    console.error('获取卡片数据失败:', e)
  } finally {
    isFetchingCard.value = false
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

// ---- 图表渲染 ----
const timeComparisonChartRef = ref<HTMLElement | null>(null)
const hospitalComparisonChartRef = ref<HTMLElement | null>(null)
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

const updateTimeComparisonChart = () => {
  if (!timeComparisonChart) return
  const trendData = localTimeTrendData.value[timeComparisonDataType.value]
  if (!trendData) return
  const xAxisData = trendData.years || []
  const seriesData = trendData.rates || trendData.data || []

  timeComparisonChart.setOption({
    tooltip: { trigger: 'axis', formatter: (params: any) => params[0].name + '<br/>' + props.rateLabel + ': ' + params[0].value + props.yAxisUnit },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: xAxisData },
    yAxis: { type: 'value', name: props.rateLabel + ' (' + props.yAxisUnit + ')', axisLabel: { formatter: '{value}' + props.yAxisUnit } },
    series: [{
      name: props.rateLabel, type: 'line', data: seriesData, smooth: true,
      lineStyle: { width: 2, color: '#2E57E5' },
      itemStyle: { color: '#2E57E5' },
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(46, 87, 229, 0.3)' }, { offset: 1, color: 'rgba(46, 87, 229, 0.05)' }] } }
    }]
  }, true)
}

const updateHospitalComparisonChart = () => {
  if (!hospitalComparisonChart) return
  const hospitalDataMap = localHospitalComparisonData.value[hospitalComparisonDataType.value]
  const seriesData: (number | 0)[] = []

  selectedHospitals.value.forEach(hospitalKey => {
    const hospital = hospitalDataMap?.[hospitalKey]
    if (!hospital) { seriesData.push(0); return }
    const yearKey = hospitalComparisonType.value === 'monthly'
      ? String(selectedComparisonYearForMonth.value)
      : selectedComparisonYear.value
    seriesData.push(hospital[yearKey] ?? 0)
  })

  hospitalComparisonChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: (params: any) => params[0].name + '<br/>' + props.rateLabel + ': ' + params[0].value + props.yAxisUnit },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '3%', containLabel: true },
    xAxis: { type: 'category', data: selectedHospitals.value.map(key => (hospitals.value as Array<{ value: string; label: string }>).find(h => h.value === key)?.label || key) },
    yAxis: { type: 'value', name: props.rateLabel + ' (' + props.yAxisUnit + ')', axisLabel: { formatter: '{value}' + props.yAxisUnit }, max: getDynamicYAxisMax(seriesData) },
    series: [{ type: 'bar', data: seriesData, itemStyle: { color: '#2E57E5' }, label: { show: true, position: 'top', formatter: '{c}' + props.yAxisUnit }, barWidth: 40 }]
  }, true)
}

const initCharts = () => {
  if (timeComparisonChartRef.value) {
    timeComparisonChart = echarts.init(timeComparisonChartRef.value)
  }
  if (hospitalComparisonChartRef.value) {
    hospitalComparisonChart = echarts.init(hospitalComparisonChartRef.value)
  }
}

const handleResize = () => {
  timeComparisonChart?.resize()
  hospitalComparisonChart?.resize()
}

onMounted(async () => {
  initCharts()
  window.addEventListener('resize', handleResize)

  // 初始化卡片时间筛选（从总览页跳转时传入）
  if (props.initTimeMode) {
    cardQueryType.value = props.initTimeMode as 'monthly' | 'quarterly'
    if (props.initTimeMode === 'monthly' && props.initTimeValue) {
      const parts = props.initTimeValue.split('-')
      cardSelectedYearForMonth.value = parseInt(parts[0])
      cardSelectedMonth.value = parseInt(parts[1])
    } else if (props.initTimeMode === 'quarterly' && props.initTimeValue) {
      const parts = props.initTimeValue.split('-Q')
      cardQuarterYear.value = parseInt(parts[0])
      cardQuarterNum.value = parts[1]
    }
  }

  await fetchHospitals()
  await Promise.all([fetchCardData(), fetchTrendData(), fetchHospitalData()])
})
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
</style>
