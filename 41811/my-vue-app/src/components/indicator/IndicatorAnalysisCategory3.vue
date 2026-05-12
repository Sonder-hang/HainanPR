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

const props = defineProps({
  title: { type: String, default: '指标分析' },
  leftTitle: { type: String, default: '结构化数据率' },
  timeComparisonTitle: { type: String, default: '趋势分析' },
  hospitalComparisonTitle: { type: String, default: '医院对比' },
  showDeathToggle: { type: Boolean, default: false },
  dataTypes: { type: Array, default: () => [{ name: '数据1', key: 'data1' }, { name: '数据2', key: 'data2' }] },
  leftData: {
    type: Object,
    default: () => ({
      actual: { 2022: { data1: 1.0, data2: 2.0 }, 2023: { data1: 1.1, data2: 2.1 }, 2024: { data1: 1.2, data2: 2.2 }, 2025: { data1: 1.3, data2: 2.3 }, 2026: { data1: 1.4, data2: 2.4 } },
      estimated: { 2022: { data1: 1.1, data2: 2.1 }, 2023: { data1: 1.2, data2: 2.2 }, 2024: { data1: 1.3, data2: 2.3 }, 2025: { data1: 1.4, data2: 2.4 }, 2026: { data1: 1.5, data2: 2.5 } }
    })
  },
  timeTrendData: {
    type: Object,
    default: () => ({
      actual: { years: ['2022', '2023', '2024', '2025', '2026'], data1: [1.0, 1.1, 1.2, 1.3, 1.4], data2: [2.0, 2.1, 2.2, 2.3, 2.4] },
      estimated: { years: ['2022', '2023', '2024', '2025', '2026'], data1: [1.1, 1.2, 1.3, 1.4, 1.5], data2: [2.1, 2.2, 2.3, 2.4, 2.5] }
    })
  },
  hospitalComparisonData: { type: Object, default: () => ({}) },
  yAxisUnit: { type: String, default: '%' }
})

const emit = defineEmits(['update:selectedHospitals'])

const years = [2022, 2023, 2024, 2025, 2026]
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
const timeComparisonType = ref('year')
const timeComparisonDataType = ref('actual')
const hospitalComparisonType = ref('year')
const selectedComparisonYear = ref(2024)
const selectedComparisonYearForMonth = ref(2024)
const selectedComparisonMonth = ref(1)
const hospitalComparisonDataType = ref('actual')

const leftChartRef = ref<HTMLElement | null>(null)
const timeComparisonChartRef = ref<HTMLElement | null>(null)
const hospitalComparisonChartRef = ref<HTMLElement | null>(null)
const helpVisible = ref(false)
let leftChart: echarts.ECharts | null = null
let timeComparisonChart: echarts.ECharts | null = null
let hospitalComparisonChart: echarts.ECharts | null = null

const generateMonthlyData = (yearData: Record<string, number>, month: number) => {
  const monthFactors = [0.95, 0.9, 1.0, 0.98, 1.02, 1.0, 1.05, 1.03, 0.97, 0.95, 0.92, 0.98]
  const factor = monthFactors[month - 1]
  return Object.fromEntries(Object.entries(yearData).map(([key, value]) => [key, Number((value * factor).toFixed(1))]))
}

const initLeftChart = () => { if (leftChartRef.value) { leftChart = echarts.init(leftChartRef.value); updateLeftChart() } }

const updateLeftChart = () => {
  if (!leftChart) return
  const dataSource = (props.leftData as any)[leftDataType.value]
  let data: Record<string, number>
  if (leftQueryType.value === 'year') { data = dataSource[leftSelectedYear.value] || dataSource[2024] }
  else { const yearData = dataSource[leftSelectedYearForMonth.value] || dataSource[2024]; data = generateMonthlyData(yearData, leftSelectedMonth.value) }
  const chartData = (props.dataTypes as any[]).map(type => ({ name: type.name, value: data[type.key] }))
  const sortedData = [...chartData].sort((a, b) => a.value - b.value)
  leftChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: (params: any) => `${sortedData[params[0].dataIndex].name}<br/>${props.yAxisUnit}: ${sortedData[params[0].dataIndex].value}${props.yAxisUnit}` },
    grid: { left: '3%', right: '12%', bottom: '3%', top: '3%', containLabel: true },
    xAxis: { type: 'value', name: props.yAxisUnit, axisLabel: { formatter: `{value}${props.yAxisUnit}` } },
    yAxis: { type: 'category', data: sortedData.map(item => item.name), axisLabel: { fontSize: 11, width: 80, overflow: 'truncate' } },
    series: [{ type: 'bar', data: sortedData.map(item => ({ value: item.value, itemStyle: { color: '#2E57E5' } })), label: { show: true, position: 'right', formatter: `{c}${props.yAxisUnit}` }, barWidth: 18 }]
  }, true)
}

const initTimeComparisonChart = () => { if (timeComparisonChartRef.value) { timeComparisonChart = echarts.init(timeComparisonChartRef.value); updateTimeComparisonChart() } }

const updateTimeComparisonChart = () => {
  if (!timeComparisonChart) return
  const trendData = (props.timeTrendData as any)[timeComparisonDataType.value]
  const dataSource = (props.leftData as any)[timeComparisonDataType.value]
  let series: any[] = []
  if (timeComparisonType.value === 'year') {
    series = (props.dataTypes as any[]).map(type => ({ name: type.name, type: 'line', data: trendData[type.key] || [], smooth: true }))
  } else {
    const baseYearData = dataSource[2024]
    series = (props.dataTypes as any[]).map(type => ({
      name: type.name, type: 'line', smooth: true,
      data: months.map(month => {
        const monthFactors = [0.95, 0.9, 1.0, 0.98, 1.02, 1.0, 1.05, 1.03, 0.97, 0.95, 0.92, 0.98]
        return Number((baseYearData[type.key] * monthFactors[month.value - 1]).toFixed(1))
      })
    }))
  }
  timeComparisonChart.setOption({
    tooltip: { trigger: 'axis', formatter: (params: any) => { let result = params[0].name + '<br/>'; params.forEach((item: any) => { result += item.marker + item.seriesName + ': ' + item.value + props.yAxisUnit + '<br/>' }); return result } },
    legend: { data: series.map(s => s.name), top: 10, type: 'scroll' },
    grid: { left: '3%', right: '4%', bottom: '3%', top: 60, containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: timeComparisonType.value === 'year' ? trendData.years : ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'] },
    yAxis: { type: 'value', name: props.yAxisUnit, axisLabel: { formatter: `{value}${props.yAxisUnit}` } },
    series: series.map(s => ({ ...s, lineStyle: { width: 2 } }))
  }, true)
}

const initHospitalComparisonChart = () => { if (hospitalComparisonChartRef.value) { hospitalComparisonChart = echarts.init(hospitalComparisonChartRef.value); updateHospitalComparisonChart() } }

const updateHospitalComparisonChart = () => {
  if (!hospitalComparisonChart) return
  const hospitalDataMap = (props.hospitalComparisonData as any)[hospitalComparisonDataType.value]
  const series: any[] = (props.dataTypes as any[]).map(type => ({ name: type.name, type: 'bar', data: [] }))
  selectedHospitals.value.forEach(hospitalKey => {
    const hospital = hospitalDataMap[hospitalKey]
    let yearData: Record<string, number>
    if (hospitalComparisonType.value === 'year') { yearData = hospital[selectedComparisonYear.value] || hospital[2024] }
    else {
      const baseYearData = hospital[2024]
      const monthFactors = [0.95, 0.9, 1.0, 0.98, 1.02, 1.0, 1.05, 1.03, 0.97, 0.95, 0.92, 0.98]
      yearData = Object.fromEntries(Object.entries(baseYearData).map(([key, value]) => [key, Number((value * monthFactors[selectedComparisonMonth.value - 1]).toFixed(1))]))
    }
    ;(props.dataTypes as any[]).forEach((type, index) => { series[index].data.push(yearData[type.key]) })
  })
  hospitalComparisonChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: (params: any) => { let result = params[0].name + '<br/>'; params.forEach((item: any) => { result += item.marker + item.seriesName + ': ' + item.value + props.yAxisUnit + '<br/>' }); return result } },
    legend: { data: (props.dataTypes as any[]).map(t => t.name), top: 10, type: 'scroll' },
    grid: { left: '3%', right: '4%', bottom: '3%', top: 60, containLabel: true },
    xAxis: { type: 'category', data: selectedHospitals.value.map(key => hospitals.find(h => h.value === key)?.label || key) },
    yAxis: { type: 'value', name: props.yAxisUnit, axisLabel: { formatter: `{value}${props.yAxisUnit}` } },
    series
  }, true)
}

const handleResize = () => { leftChart?.resize(); timeComparisonChart?.resize(); hospitalComparisonChart?.resize() }
watch(selectedHospitals, (newValue) => { emit('update:selectedHospitals', newValue) })
onMounted(() => { initLeftChart(); initTimeComparisonChart(); initHospitalComparisonChart(); window.addEventListener('resize', handleResize) })
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
</style>
