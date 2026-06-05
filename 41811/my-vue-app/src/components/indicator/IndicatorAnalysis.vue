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
          <template v-else-if="rankingMode === 'multi'">
            <div class="grid grid-cols-2 gap-3">
              <div v-for="(_, rankingId) in multiRankingData" :key="rankingId">
                <h3 class="mb-2 text-[14px] font-semibold" :style="{ color: getMultiRankingColor(rankingId) }">{{ getMultiRankingTitle(rankingId) }}</h3>
                <div :ref="el => registerMultiChartRef(el as HTMLElement | null, rankingId)" style="height: 450px;"></div>
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
import { core18Api } from '@/api/core18'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  indicator_key: { type: String, default: '' },
  title: { type: String, default: '指标分析' },
  leftTitle: { type: String, default: '排行榜' },
  leftChartTitle: { type: String, default: '排行榜' },
  leftChartLimit: { type: Number, default: 20 },
  leftChartTitle1: { type: String, default: '排行榜1' },
  leftChartTitle2: { type: String, default: '排行榜2' },
  leftChartColor: { type: String, default: '#2E57E5' },
  leftChartColor1: { type: String, default: '#12B881' },
  leftChartColor2: { type: String, default: '#2E57E5' },
  timeComparisonTitle: { type: String, default: '纵向时间对比' },
  hospitalComparisonTitle: { type: String, default: '横向医院对比' },
  rankingMode: { type: String, default: 'single' },
  showDeathToggle: { type: Boolean, default: false },
  totalCountLabel: { type: String, default: '总数' },
  initTimeMode: { type: String, default: '' },
  initTimeValue: { type: String, default: '' },
  initHospital: { type: String, default: '' },
})

const now = new Date()
const currentYear = now.getFullYear()

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

const selectedHospitals = ref<string[]>(['all'])
// 当前生效的医院范围（由 initHospital 初始化，受顶部筛选器控制）
const appliedHospital = ref('all')
watch(() => props.initHospital, (val) => {
  if (val) appliedHospital.value = val
}, { immediate: true })
watch(
  () => [props.indicator_key, props.initTimeMode, props.initTimeValue],
  () => {
    hasConsumedRouteTrendAnchor.value = false
    if (props.initTimeMode === 'quarterly' || props.initTimeMode === 'monthly') {
      timeComparisonType.value = props.initTimeMode
    }
  },
  { immediate: true }
)
// appliedHospital 变化时重新拉取排行榜和趋势数据（不受子组件自身时间筛选影响）
watch(appliedHospital, () => {
  fetchLeftData()
  fetchTrendData()
})
const leftQueryType = ref<'monthly' | 'quarterly'>('monthly')
const leftSelectedYearForMonth = ref(currentYear)
const leftSelectedMonth = ref(1)
const leftQuarterYear = ref(currentYear)
const leftQuarterNum = ref('1')
const leftDataType = ref('actual')
const currentTotalCount = ref(0)
const timeComparisonType = ref<'monthly' | 'quarterly'>('monthly')
const timeComparisonDataType = ref('actual')
const hasConsumedRouteTrendAnchor = ref(false)
const hospitalComparisonType = ref<'monthly' | 'quarterly'>('quarterly')
const selectedComparisonYear = ref(currentYear)
const selectedComparisonQuarter = ref('1')
const selectedComparisonYearForMonth = ref(currentYear)
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

// Multi-ranking mode state (COMPOSITE_MULTI_RANKING)
const multiRankingData = ref<Record<string, any>>({})
const multiChartRefs = ref<Record<string, HTMLElement | null>>({})
const multiCharts = ref<Record<string, echarts.ECharts | null>>({})
const multiRankingConfig = ref<Array<{ id: string; name: string; color: string }>>([])

const getMultiRankingColor = (rankingId: string) => {
  return multiRankingConfig.value.find(r => r.id === rankingId)?.color || '#2E57E5'
}
const getMultiRankingTitle = (rankingId: string) => {
  return multiRankingConfig.value.find(r => r.id === rankingId)?.name || rankingId
}
const registerMultiChartRef = (el: HTMLElement | null, rankingId: string) => {
  multiChartRefs.value[rankingId] = el
  if (el && !multiCharts.value[rankingId]) {
    multiCharts.value[rankingId] = echarts.init(el)
  }
}
const updateMultiCharts = () => {
  for (const [rankingId, chart] of Object.entries(multiCharts.value)) {
    if (!chart) continue
    const data = multiRankingData.value[rankingId]?.actual || []
    if (!data.length) continue
    const sortedData = [...data].sort((a, b) => a.value - b.value)
    chart.setOption(makeBarOption(sortedData, getMultiRankingColor(rankingId)), true)
  }
}
const resizeMultiCharts = () => {
  for (const chart of Object.values(multiCharts.value)) {
    chart?.resize()
  }
}

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

const localLeftData = ref<Record<string, any>>({})
const localLeftData1 = ref<Record<string, any>>({})
const localLeftData2 = ref<Record<string, any>>({})
const localTimeTrendData = ref<Record<string, any>>({})
const localHospitalComparisonData = ref<Record<string, any>>({})

const isFetchingLeft = ref(false)
const isFetchingTrend = ref(false)
const isFetchingHospital = ref(false)

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

const buildLeftTimeValue = () => {
  if (leftQueryType.value === 'monthly') {
    return `${leftSelectedYearForMonth.value}-${String(leftSelectedMonth.value).padStart(2, '0')}`
  }
  return `${leftQuarterYear.value}-Q${leftQuarterNum.value}`
}

const buildTrendTimeValue = () => {
  const shouldUseRouteAnchor = !hasConsumedRouteTrendAnchor.value
    && !!props.initTimeMode
    && !!props.initTimeValue
    && props.initTimeMode === timeComparisonType.value

  if (shouldUseRouteAnchor) {
    hasConsumedRouteTrendAnchor.value = true
    return props.initTimeValue
  }

  const currentDate = new Date()
  const year = currentDate.getFullYear()
  if (timeComparisonType.value === 'monthly') {
    return `${year}-${String(currentDate.getMonth() + 1).padStart(2, '0')}`
  }
  return `${year}-Q${Math.ceil((currentDate.getMonth() + 1) / 3)}`
}

const buildHospitalTimeValue = () => {
  if (hospitalComparisonType.value === 'monthly') {
    return `${selectedComparisonYearForMonth.value}-${String(selectedComparisonMonth.value).padStart(2, '0')}`
  }
  return `${selectedComparisonYear.value}-Q${selectedComparisonQuarter.value}`
}

const makeBarOption = (data: { name: string; value: number }[], color: string) => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: '3%', right: '12%', bottom: '3%', top: '3%', containLabel: true },
  xAxis: { type: 'value', show: false },
  yAxis: { type: 'category', data: data.map(item => item.name), axisLabel: { fontSize: 10, width: 70, overflow: 'truncate' }, axisLine: { show: false }, axisTick: { show: false } },
  series: [{ type: 'bar', data: data.map(item => ({ value: item.value, itemStyle: { color } })), label: { show: true, position: 'right', fontSize: 10, formatter: '{c}' }, barWidth: 12 }]
})

const updateSingleChart = () => {
  if (!singleChart) return
  const actualData = localLeftData.value?.actual
  if (!actualData || !Array.isArray(actualData) || actualData.length === 0) return
  const data: { name: string; value: number }[] = actualData
  const sortedData = [...data].sort((a, b) => a.value - b.value)
  singleChart.setOption(makeBarOption(sortedData, props.leftChartColor), true)
}

const updateLeftChart1 = () => {
  if (!leftChart1) return
  const actualData = localLeftData1.value?.actual
  if (!actualData || !Array.isArray(actualData) || actualData.length === 0) return
  const data: { name: string; value: number }[] = actualData
  const sortedData = [...data].sort((a, b) => a.value - b.value)
  leftChart1.setOption(makeBarOption(sortedData, props.leftChartColor1), true)
}

const updateLeftChart2 = () => {
  if (!leftChart2) return
  const actualData = localLeftData2.value?.actual
  if (!actualData || !Array.isArray(actualData) || actualData.length === 0) return
  const data: { name: string; value: number }[] = actualData
  const sortedData = [...data].sort((a, b) => a.value - b.value)
  leftChart2.setOption(makeBarOption(sortedData, props.leftChartColor2), true)
}

const updateLeftChart = () => {
  if (props.rankingMode === 'single') updateSingleChart()
  else if (props.rankingMode === 'double') { updateLeftChart1(); updateLeftChart2() }
  else if (props.rankingMode === 'multi') updateMultiCharts()
}

const updateTimeComparisonChart = () => {
  if (!timeComparisonChart) return
  const trendData = localTimeTrendData.value[timeComparisonDataType.value]
  if (!trendData) return
  // STRUCTURE 趋势格式: { years: [...], data: [...] }（STRUCTURE 用 count 而非 rate）
  // RATE 趋势格式: { years: [...], rates: [...] }（比值型用 rate_percent）
  const xAxisData: string[] = trendData.years || []
  let seriesData: number[] = trendData.data || []

  // 若 data 为空或长度不匹配，用 rates 兜底（比值型指标）
  if (!seriesData.length && trendData.rates) {
    seriesData = trendData.rates
  }

  timeComparisonChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: xAxisData },
    yAxis: { type: 'value', name: '数量' },
    series: [{
      name: '数量',
      type: 'line',
      data: seriesData,
      smooth: true,
      areaStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(46, 87, 229, 0.3)' },
            { offset: 1, color: 'rgba(46, 87, 229, 0.05)' }
          ]
        }
      },
      lineStyle: { width: 2, color: '#2E57E5' },
      itemStyle: { color: '#2E57E5' }
    }]
  }, true)
}

const updateHospitalComparisonChart = () => {
  if (!hospitalComparisonChart) return
  const hospitalDataMap = localHospitalComparisonData.value[hospitalComparisonDataType.value]
  if (!hospitalDataMap) return
  const yearKey = hospitalComparisonType.value === 'monthly'
    ? String(selectedComparisonYearForMonth.value)
    : selectedComparisonYear.value
  const data = selectedHospitals.value.map(hospitalKey => {
    const hospital = hospitalDataMap[hospitalKey]
    const name = (hospitals.value as Array<{ value: string; label: string }>).find(h => h.value === hospitalKey)?.label || hospitalKey
    return { name, value: hospital ? (hospital[yearKey] ?? 0) : 0 }
  })
  hospitalComparisonChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: { type: 'category', data: data.map(item => item.name) },
    yAxis: { type: 'value', name: '数量', max: getDynamicYAxisMax(data.map(item => item.value)) },
    series: [{ type: 'bar', data: data.map(item => item.value), itemStyle: { color: '#2E57E5' }, label: { show: true, position: 'top', formatter: '{c}' } }]
  }, true)
}

const initCharts = () => {
  if (singleChartRef.value) {
    singleChart = echarts.init(singleChartRef.value)
  }
  if (leftChartRef1.value) {
    leftChart1 = echarts.init(leftChartRef1.value)
  }
  if (leftChartRef2.value) {
    leftChart2 = echarts.init(leftChartRef2.value)
  }
  if (timeComparisonChartRef.value) {
    timeComparisonChart = echarts.init(timeComparisonChartRef.value)
  }
  if (hospitalComparisonChartRef.value) {
    hospitalComparisonChart = echarts.init(hospitalComparisonChartRef.value)
  }
}

const handleResize = () => {
  singleChart?.resize()
  leftChart1?.resize()
  leftChart2?.resize()
  timeComparisonChart?.resize()
  hospitalComparisonChart?.resize()
  resizeMultiCharts()
}

const fetchLeftData = async () => {
  if (!props.indicator_key) return
  isFetchingLeft.value = true
  try {
    const res = await core18Api.getIndicatorData({
      indicator_key: props.indicator_key,
      time_mode: leftQueryType.value,
      time_value: buildLeftTimeValue(),
      data_type: 'left',
      hospital_code: appliedHospital.value === 'all' ? undefined : appliedHospital.value,
      // 死亡相关指标支持 death_type 切换筛选
      death_type_filter: props.showDeathToggle ? leftDataType.value as 'actual' | 'estimated' : undefined,
    }) as any
    if (res) {
      // leftData 格式（backend 已规范化为）：
      //   {"actual": [{name, value}, ...], "estimated": []}
      // totalCount 由后端直接传入，代表该时间段的完整总数量（非 TOP20 之和）
      if (props.rankingMode === 'single') {
        // 确保 leftData 是正确格式
        if (res.leftData && typeof res.leftData === 'object' && 'actual' in res.leftData) {
          localLeftData.value = res.leftData
        } else {
          localLeftData.value = { actual: res.leftData || [], estimated: [] }
        }
        localLeftData1.value = {}
        localLeftData2.value = {}
      } else if (props.rankingMode === 'double') {
        // 优先使用 leftData1/leftData2；若均为空，降级使用 leftData（单一排行场景）
        const raw1 = res.leftData1 || {}
        const raw2 = res.leftData2 || {}
        const hasData1 = !!(raw1.actual && (raw1.actual.length > 0 || Object.keys(raw1.actual).length > 0))
        const hasData2 = !!(raw2.actual && (raw2.actual.length > 0 || Object.keys(raw2.actual).length > 0))

        if (hasData1) {
          localLeftData1.value = raw1
        } else if (res.leftData && res.leftData.actual) {
          // 降级：使用 leftData 作为 leftData1（单一排行场景，如ICD-9-CM-3四位码种类数）
          localLeftData1.value = res.leftData
        } else {
          localLeftData1.value = { actual: [], estimated: [] }
        }
        localLeftData2.value = hasData2 ? raw2 : { actual: [], estimated: [] }
      } else if (props.rankingMode === 'multi') {
        // COMPOSITE_MULTI_RANKING: 从 multiRankingData 获取多排行榜数据
        multiRankingData.value = res.multiRankingData || {}
        // 同步更新各子图表
        updateMultiCharts()
      } else {
        localLeftData.value = res.leftData || {}
        localLeftData1.value = res.leftData1 || {}
        localLeftData2.value = res.leftData2 || {}
      }
      // totalCount 由后端传入，直接使用
      if (res.totalCount !== undefined && res.totalCount !== null) {
        currentTotalCount.value = Number(res.totalCount) || 0
      }
      updateLeftChart()
    }
  } catch (e) {
    console.error('获取排行榜数据失败:', e)
  } finally {
    isFetchingLeft.value = false
  }
}

const fetchTrendData = async () => {
  if (!props.indicator_key) return
  isFetchingTrend.value = true
  try {
    const res = await core18Api.getIndicatorData({
      indicator_key: props.indicator_key,
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
  if (!props.indicator_key) return
  isFetchingHospital.value = true
  try {
    const res = await core18Api.getIndicatorData({
      indicator_key: props.indicator_key,
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
