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
                v-model="leftQueryType"
                class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
              >
                <option value="year">按年份</option>
                <option value="month">按月份</option>
              </select>
              <select
                v-if="leftQueryType === 'year'"
                v-model="leftSelectedYear"
                class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
              >
                <option v-for="year in years" :key="year" :value="year">{{ year }}年</option>
              </select>
              <template v-if="leftQueryType === 'month'">
                <select
                  v-model="leftSelectedYearForMonth"
                  class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
                >
                  <option v-for="year in years" :key="year" :value="year">{{ year }}年</option>
                </select>
                <select
                  v-model="leftSelectedMonth"
                  class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
                >
                  <option v-for="month in months" :key="month.value" :value="month.value">{{ month.label }}</option>
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
                @click="updateLeftChart"
              >
                查询
              </button>
            </div>
            <div class="mt-3 p-3 bg-[#F2F5FA] rounded-lg">
              <div class="text-[14px] text-[#596080]">{{ totalCountLabel }}: <span class="font-bold text-[#2E57E5]">{{ currentTotalCount }}</span></div>
            </div>
          </div>

          <template v-if="rankingMode === 'single'">
            <div>
              <h3 class="mb-2 text-[14px] font-semibold" :style="{ color: leftChartColor }">{{ leftChartTitle }}</h3>
              <div ref="singleChartRef" style="height: 450px;"></div>
            </div>
          </template>
          <template v-else-if="rankingMode === 'double'">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <h3 class="mb-2 text-[14px] font-semibold" :style="{ color: leftChartColor1 }">{{ leftChartTitle1 }}</h3>
                <div ref="leftChartRef1" style="height: 450px;"></div>
              </div>
              <div>
                <h3 class="mb-2 text-[14px] font-semibold" :style="{ color: leftChartColor2 }">{{ leftChartTitle2 }}</h3>
                <div ref="leftChartRef2" style="height: 450px;"></div>
              </div>
            </div>
          </template>
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
            {{ title }}：统计指定周期内各项指标的总量和分布情况，按医院和科室进行分类汇总展示。
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
              病案首页：患者出院时的病案首页汇总信息
            </li>
          </ul>
        </div>
        <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
          <h3 class="font-bold text-[#1F264D] text-[13px] mb-2">统计口径</h3>
          <p class="text-[12px] text-[#596080] leading-relaxed">
            统计周期内，纳入的患者人次和医嘱执行情况，按医院、科室进行分类汇总，包含排行榜、趋势分析和医院对比三个维度。
          </p>
        </div>
        <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
          <h3 class="font-bold text-[#1F264D] text-[13px] mb-2">计算方式</h3>
          <p class="text-[12px] text-[#596080] leading-relaxed">
            支持按年份和按月份两种统计口径，默认展示当年数据，可通过顶部筛选器切换查询时间范围。
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
  leftTitle: { type: String, default: '排行榜' },
  leftChartTitle: { type: String, default: '排行榜' },
  leftChartTitle1: { type: String, default: '排行榜1' },
  leftChartTitle2: { type: String, default: '排行榜2' },
  leftChartColor: { type: String, default: '#2E57E5' },
  leftChartColor1: { type: String, default: '#12B881' },
  leftChartColor2: { type: String, default: '#2E57E5' },
  timeComparisonTitle: { type: String, default: '纵向时间对比' },
  hospitalComparisonTitle: { type: String, default: '横向医院对比' },
  rankingMode: { type: String, default: 'single' },
  showDeathToggle: { type: Boolean, default: false },
  totalCount: { type: Number, default: null },
  totalCountLabel: { type: String, default: '总数' },
  leftData: { type: Object, default: () => ({}) },
  leftData1: { type: Object, default: () => ({}) },
  leftData2: { type: Object, default: () => ({}) },
  timeTrendData: { type: Object, default: () => ({}) },
  hospitalComparisonData: { type: Object, default: () => ({}) }
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
const leftQueryType = ref('year')
const leftSelectedYear = ref(2024)
const leftSelectedYearForMonth = ref(2024)
const leftSelectedMonth = ref(1)
const leftDataType = ref('actual')
const currentTotalCount = ref(0)
const timeComparisonType = ref('year')
const timeComparisonDataType = ref('actual')
const hospitalComparisonType = ref('year')
const selectedComparisonYear = ref(2024)
const selectedComparisonYearForMonth = ref(2024)
const selectedComparisonMonth = ref(1)
const hospitalComparisonDataType = ref('actual')

const singleChartRef = ref<HTMLElement | null>(null)
const leftChartRef1 = ref<HTMLElement | null>(null)
const leftChartRef2 = ref<HTMLElement | null>(null)
const timeComparisonChartRef = ref<HTMLElement | null>(null)
const hospitalComparisonChartRef = ref<HTMLElement | null>(null)
const helpVisible = ref(false)
let singleChart: echarts.ECharts | null = null
let leftChart1: echarts.ECharts | null = null
let leftChart2: echarts.ECharts | null = null
let timeComparisonChart: echarts.ECharts | null = null
let hospitalComparisonChart: echarts.ECharts | null = null

const generateMonthlyData = (yearData: { name: string; value: number }[], month: number) => {
  const monthFactors = [0.9, 0.85, 0.95, 0.92, 0.98, 1.0, 1.05, 1.08, 1.02, 0.95, 0.88, 0.92]
  const factor = monthFactors[month - 1] / 12
  return yearData.map(item => ({ name: item.name, value: Math.floor(item.value * factor) }))
}

const calculateTotalCount = () => {
  const calculateDataSourceTotal = (dataSource: any) => {
    let data: { name: string; value: number }[]
    if (leftQueryType.value === 'year') { data = dataSource[leftDataType.value][leftSelectedYear.value] || dataSource[leftDataType.value][2024] }
    else { const yearData = dataSource[leftDataType.value][leftSelectedYearForMonth.value] || dataSource[leftDataType.value][2024]; data = generateMonthlyData(yearData, leftSelectedMonth.value) }
    return data.reduce((sum, item) => sum + item.value, 0)
  }
  if (props.rankingMode === 'single') { currentTotalCount.value = calculateDataSourceTotal(props.leftData) }
  else if (props.rankingMode === 'double') { currentTotalCount.value = calculateDataSourceTotal(props.leftData1) + calculateDataSourceTotal(props.leftData2) }
  return currentTotalCount.value
}

const makeBarOption = (data: { name: string; value: number }[], color: string) => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: '3%', right: '12%', bottom: '3%', top: '3%', containLabel: true },
  xAxis: { type: 'value', show: false },
  yAxis: { type: 'category', data: data.map(item => item.name), axisLabel: { fontSize: 10, width: 70, overflow: 'truncate' }, axisLine: { show: false }, axisTick: { show: false } },
  series: [{ type: 'bar', data: data.map(item => ({ value: item.value, itemStyle: { color } })), label: { show: true, position: 'right', fontSize: 10, formatter: '{c}' }, barWidth: 12 }]
})

const initSingleChart = () => { if (singleChartRef.value) { singleChart = echarts.init(singleChartRef.value); updateSingleChart() } }
const updateSingleChart = () => {
  if (!singleChart) return
  const dataSource = (props.leftData as any)[leftDataType.value]
  let data: { name: string; value: number }[]
  if (leftQueryType.value === 'year') { data = dataSource[leftSelectedYear.value] || dataSource[2024] }
  else { const yearData = dataSource[leftSelectedYearForMonth.value] || dataSource[2024]; data = generateMonthlyData(yearData, leftSelectedMonth.value) }
  const sortedData = [...data].sort((a, b) => a.value - b.value)
  singleChart.setOption(makeBarOption(sortedData, props.leftChartColor), true)
}

const initLeftChart1 = () => { if (leftChartRef1.value) { leftChart1 = echarts.init(leftChartRef1.value); updateLeftChart1() } }
const updateLeftChart1 = () => {
  if (!leftChart1) return
  const dataSource = (props.leftData1 as any)[leftDataType.value]
  let data: { name: string; value: number }[]
  if (leftQueryType.value === 'year') { data = dataSource[leftSelectedYear.value] || dataSource[2024] }
  else { const yearData = dataSource[leftSelectedYearForMonth.value] || dataSource[2024]; data = generateMonthlyData(yearData, leftSelectedMonth.value) }
  const sortedData = [...data].sort((a, b) => a.value - b.value)
  leftChart1.setOption(makeBarOption(sortedData, props.leftChartColor1), true)
}

const initLeftChart2 = () => { if (leftChartRef2.value) { leftChart2 = echarts.init(leftChartRef2.value); updateLeftChart2() } }
const updateLeftChart2 = () => {
  if (!leftChart2) return
  const dataSource = (props.leftData2 as any)[leftDataType.value]
  let data: { name: string; value: number }[]
  if (leftQueryType.value === 'year') { data = dataSource[leftSelectedYear.value] || dataSource[2024] }
  else { const yearData = dataSource[leftSelectedYearForMonth.value] || dataSource[2024]; data = generateMonthlyData(yearData, leftSelectedMonth.value) }
  const sortedData = [...data].sort((a, b) => a.value - b.value)
  leftChart2.setOption(makeBarOption(sortedData, props.leftChartColor2), true)
}

const updateLeftChart = () => {
  if (props.rankingMode === 'single') updateSingleChart()
  else if (props.rankingMode === 'double') { updateLeftChart1(); updateLeftChart2() }
  calculateTotalCount()
}

const initTimeComparisonChart = () => { if (timeComparisonChartRef.value) { timeComparisonChart = echarts.init(timeComparisonChartRef.value); updateTimeComparisonChart() } }
const updateTimeComparisonChart = () => {
  if (!timeComparisonChart) return
  const trendData = (props.timeTrendData as any)[timeComparisonDataType.value]
  let xAxisData: string[] = []
  let seriesData: number[] = []
  if (timeComparisonType.value === 'year') { xAxisData = trendData.years; seriesData = trendData.data }
  else {
    xAxisData = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    const baseValue = trendData.data[trendData.data.length - 1]
    seriesData = months.map((month, index) => {
      const monthFactors = [0.9, 0.85, 0.95, 0.92, 0.98, 1.0, 1.05, 1.08, 1.02, 0.95, 0.88, 0.92]
      return Math.floor(baseValue / 12 * monthFactors[index])
    })
  }
  timeComparisonChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: xAxisData },
    yAxis: { type: 'value', name: '数量' },
    series: [{ name: '数量', type: 'line', data: seriesData, smooth: true, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(46, 87, 229, 0.3)' }, { offset: 1, color: 'rgba(46, 87, 229, 0.05)' }] } }, lineStyle: { width: 2, color: '#2E57E5' }, itemStyle: { color: '#2E57E5' } }]
  }, true)
}

const initHospitalComparisonChart = () => { if (hospitalComparisonChartRef.value) { hospitalComparisonChart = echarts.init(hospitalComparisonChartRef.value); updateHospitalComparisonChart() } }
const updateHospitalComparisonChart = () => {
  if (!hospitalComparisonChart) return
  const hospitalDataMap = (props.hospitalComparisonData as any)[hospitalComparisonDataType.value]
  const data = selectedHospitals.value.map(hospitalKey => {
    const hospital = hospitalDataMap[hospitalKey]
    let value: number
    if (hospitalComparisonType.value === 'year') { value = hospital.data[years.indexOf(selectedComparisonYear.value)] || hospital.data[hospital.data.length - 1] }
    else { value = Math.floor(hospital.data[hospital.data.length - 1] / 12 * (selectedComparisonMonth.value / 12 + 0.5)) }
    return { name: hospital.name, value }
  })
  hospitalComparisonChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: { type: 'category', data: data.map(item => item.name) },
    yAxis: { type: 'value', name: '数量' },
    series: [{ type: 'bar', data: data.map(item => item.value), itemStyle: { color: '#2E57E5' }, label: { show: true, position: 'top', formatter: '{c}' } }]
  }, true)
}

const handleResize = () => { singleChart?.resize(); leftChart1?.resize(); leftChart2?.resize(); timeComparisonChart?.resize(); hospitalComparisonChart?.resize() }
watch(selectedHospitals, (newValue) => { emit('update:selectedHospitals', newValue) })
onMounted(() => {
  if (props.rankingMode === 'single') initSingleChart()
  else if (props.rankingMode === 'double') { initLeftChart1(); initLeftChart2() }
  initTimeComparisonChart()
  initHospitalComparisonChart()
  calculateTotalCount()
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
</style>
