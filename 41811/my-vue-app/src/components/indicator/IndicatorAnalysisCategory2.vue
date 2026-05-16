<template>
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
                <option value="year">按年份</option>
                <option value="month">按月份</option>
              </select>
              <select
                v-if="cardQueryType === 'year'"
                v-model="cardSelectedYear"
                class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
              >
                <option v-for="year in years" :key="year" :value="year">{{ year }}年</option>
              </select>
              <template v-if="cardQueryType === 'month'">
                <select
                  v-model="cardSelectedYearForMonth"
                  class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
                >
                  <option v-for="year in years" :key="year" :value="year">{{ year }}年</option>
                </select>
                <select
                  v-model="cardSelectedMonth"
                  class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
                >
                  <option v-for="month in months" :key="month.value" :value="month.value">{{ month.label }}</option>
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
                @click="updateCardData"
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
                <option value="year">按年份</option>
                <option value="month">按月份</option>
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
                @click="updateTimeComparisonChart"
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
                <option value="year">按年份</option>
                <option value="month">按月份</option>
              </select>
              <select
                v-if="hospitalComparisonType === 'year'"
                v-model="selectedComparisonYear"
                class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
              >
                <option v-for="year in years" :key="year" :value="year">{{ year }}年</option>
              </select>
              <template v-if="hospitalComparisonType === 'month'">
                <select
                  v-model="selectedComparisonYearForMonth"
                  class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
                >
                  <option v-for="year in years" :key="year" :value="year">{{ year }}年</option>
                </select>
                <select
                  v-model="selectedComparisonMonth"
                  class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
                >
                  <option v-for="month in months" :key="month.value" :value="month.value">{{ month.label }}</option>
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
                @click="updateHospitalComparisonChart"
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

const props = defineProps({
  title: { type: String, default: '指标分析' },
  leftTitle: { type: String, default: '百分率直观展示' },
  timeComparisonTitle: { type: String, default: '趋势分析' },
  hospitalComparisonTitle: { type: String, default: '医院对比' },
  showDeathToggle: { type: Boolean, default: false },
  rateLabel: { type: String, default: '率' },
  rateUnit: { type: String, default: '%' },
  maxRate: { type: Number, default: 100 },
  cardData: {
    type: Object,
    default: () => ({
      actual: { 2022: 82, 2023: 83, 2024: 85, 2025: 87, 2026: 89 },
      estimated: { 2022: 83, 2023: 84, 2024: 86, 2025: 88, 2026: 90 }
    })
  },
  timeTrendData: {
    type: Object,
    default: () => ({
      actual: { years: ['2022', '2023', '2024', '2025', '2026'], rates: [82, 83, 85, 87, 89] },
      estimated: { years: ['2022', '2023', '2024', '2025', '2026'], rates: [83, 84, 86, 88, 90] }
    })
  },
  hospitalComparisonData: {
    type: Object,
    default: () => ({
      actual: {
        hospitalA: { 2022: 83, 2023: 84, 2024: 86, 2025: 88, 2026: 90 },
        hospitalB: { 2022: 81, 2023: 82, 2024: 84, 2025: 86, 2026: 88 },
        hospitalC: { 2022: 84, 2023: 85, 2024: 87, 2025: 89, 2026: 91 },
        hospitalD: { 2022: 80, 2023: 81, 2024: 83, 2025: 85, 2026: 87 },
        hospitalE: { 2022: 82, 2023: 83, 2024: 85, 2025: 87, 2026: 89 },
      },
      estimated: {
        hospitalA: { 2022: 84, 2023: 85, 2024: 87, 2025: 89, 2026: 91 },
        hospitalB: { 2022: 82, 2023: 83, 2024: 85, 2025: 87, 2026: 89 },
        hospitalC: { 2022: 85, 2023: 86, 2024: 88, 2025: 90, 2026: 92 },
        hospitalD: { 2022: 81, 2023: 82, 2024: 84, 2025: 86, 2026: 88 },
        hospitalE: { 2022: 83, 2023: 84, 2024: 86, 2025: 88, 2026: 90 },
      }
    })
  },
  yAxisUnit: { type: String, default: '%' }
})

const emit = defineEmits(['update:selectedHospitals'])

const years = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
const months = [
  { value: 1, label: '1月' }, { value: 2, label: '2月' }, { value: 3, label: '3月' },
  { value: 4, label: '4月' }, { value: 5, label: '5月' }, { value: 6, label: '6月' },
  { value: 7, label: '7月' }, { value: 8, label: '8月' }, { value: 9, label: '9月' },
  { value: 10, label: '10月' }, { value: 11, label: '11月' }, { value: 12, label: '12月' }
]

const hospitals = [
  { value: 'hospitalA', label: '医院A' },
  { value: 'hospitalB', label: '医院B' },
  { value: 'hospitalC', label: '医院C' },
  { value: 'hospitalD', label: '医院D' },
  { value: 'hospitalE', label: '医院E' },
]

const selectedHospitals = ref(['hospitalA', 'hospitalB', 'hospitalC'])
const cardQueryType = ref('year')
const cardSelectedYear = ref(2024)
const cardSelectedYearForMonth = ref(2024)
const cardSelectedMonth = ref(1)
const cardDataType = ref('actual')
const timeComparisonType = ref('year')
const timeComparisonDataType = ref('actual')
const hospitalComparisonType = ref('year')
const selectedComparisonYear = ref(2024)
const selectedComparisonYearForMonth = ref(2024)
const selectedComparisonMonth = ref(1)
const hospitalComparisonDataType = ref('actual')
const currentRate = ref(85)
const helpVisible = ref(false)

const timeComparisonChartRef = ref<HTMLElement | null>(null)
const hospitalComparisonChartRef = ref<HTMLElement | null>(null)
let timeComparisonChart: echarts.ECharts | null = null
let hospitalComparisonChart: echarts.ECharts | null = null

const generateMonthlyRateData = (yearRate: number, month: number) => {
  const monthFactors = [0.95, 0.9, 1.0, 0.98, 1.02, 1.0, 1.05, 1.03, 0.97, 0.95, 0.92, 0.98]
  const factor = monthFactors[month - 1]
  return Number((yearRate * factor).toFixed(1))
}

const updateCardData = () => {
  const dataSource = (props.cardData as any)[cardDataType.value]
  if (cardQueryType.value === 'year') {
    currentRate.value = dataSource[cardSelectedYear.value] || dataSource[2024]
  } else {
    const yearRate = dataSource[cardSelectedYearForMonth.value] || dataSource[2024]
    currentRate.value = generateMonthlyRateData(yearRate, cardSelectedMonth.value)
  }
}

const initTimeComparisonChart = () => {
  if (timeComparisonChartRef.value) {
    timeComparisonChart = echarts.init(timeComparisonChartRef.value)
    updateTimeComparisonChart()
  }
}

const updateTimeComparisonChart = () => {
  if (!timeComparisonChart) return
  const trendData = (props.timeTrendData as any)[timeComparisonDataType.value]
  let xAxisData: string[] = []
  let seriesData: number[] = []

  if (timeComparisonType.value === 'year') {
    xAxisData = trendData.years
    seriesData = trendData.rates
  } else {
    xAxisData = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    const baseYearRate = (props.cardData as any)[cardDataType.value][2024]
    seriesData = months.map(month => generateMonthlyRateData(baseYearRate, month.value))
  }

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

const initHospitalComparisonChart = () => {
  if (hospitalComparisonChartRef.value) {
    hospitalComparisonChart = echarts.init(hospitalComparisonChartRef.value)
    updateHospitalComparisonChart()
  }
}

const updateHospitalComparisonChart = () => {
  if (!hospitalComparisonChart) return
  const hospitalDataMap = (props.hospitalComparisonData as any)[hospitalComparisonDataType.value]
  const seriesData: number[] = []

  selectedHospitals.value.forEach(hospitalKey => {
    const hospital = hospitalDataMap[hospitalKey]
    let rate: number
    if (hospitalComparisonType.value === 'year') {
      rate = hospital[selectedComparisonYear.value] || hospital[2024]
    } else {
      rate = generateMonthlyRateData(hospital[2024], selectedComparisonMonth.value)
    }
    seriesData.push(rate)
  })

  hospitalComparisonChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: (params: any) => params[0].name + '<br/>' + props.rateLabel + ': ' + params[0].value + props.yAxisUnit },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '3%', containLabel: true },
    xAxis: { type: 'category', data: selectedHospitals.value.map(key => hospitals.find(h => h.value === key)?.label || key) },
    yAxis: { type: 'value', name: props.rateLabel + ' (' + props.yAxisUnit + ')', axisLabel: { formatter: '{value}' + props.yAxisUnit } },
    series: [{ type: 'bar', data: seriesData, itemStyle: { color: '#2E57E5' }, label: { show: true, position: 'top', formatter: '{c}' + props.yAxisUnit }, barWidth: 40 }]
  }, true)
}

const handleResize = () => {
  timeComparisonChart?.resize()
  hospitalComparisonChart?.resize()
}

watch(selectedHospitals, (newValue) => { emit('update:selectedHospitals', newValue) })

onMounted(() => {
  updateCardData()
  initTimeComparisonChart()
  initHospitalComparisonChart()
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
</style>
