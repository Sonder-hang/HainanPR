<template>
  <div class="flex h-full min-h-0 flex-col bg-[#F4F6F8] p-5 font-sans">
    <header class="mb-5 flex flex-wrap items-center justify-between gap-4">
      <h1 class="text-[24px] font-bold text-[#1F264D]">指标分析台</h1>
      <div class="flex flex-wrap items-center gap-2.5">
        <select
          v-model="draftIndicator"
          class="h-8 min-w-[300px] rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
        >
          <option v-for="item in allIndicatorOptions" :key="item.value" :value="item.value">
            {{ item.label }}
          </option>
        </select>
        <select
          v-model="draftHospital"
          class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
        >
          <option v-for="item in hospitalOptions" :key="item.value" :value="item.value">
            {{ item.label }}
          </option>
        </select>
        <button
          type="button"
          class="h-8 rounded bg-[#2E57E5] px-4 text-[14px] font-medium text-white transition-colors hover:bg-[#1E4BD8]"
          @click="applySelection"
        >
          查询
        </button>
      </div>
    </header>

    <div class="min-h-0 flex-1">
      <DeathPatientDefinitionTable
        v-if="appliedIndicator === 'deathPatientDefinition'"
        :key="`death-table-${appliedIndicator}`"
        :title="currentTitle"
      />
      <IndicatorAnalysis
        v-else-if="templateType === 'STRUCTURE'"
        :key="`structure-${appliedIndicator}`"
        :title="currentStructureConfig.title"
        :left-title="currentStructureConfig.leftTitle"
        :left-chart-title="currentStructureConfig.leftChartTitle"
        :left-chart-color="currentStructureConfig.leftChartColor"
        :time-comparison-title="currentStructureConfig.timeComparisonTitle"
        :hospital-comparison-title="currentStructureConfig.hospitalComparisonTitle"
        :ranking-mode="'single'"
        :show-death-toggle="currentStructureConfig.showDeathToggle"
        :left-data="currentStructureConfig.leftData"
        :time-trend-data="currentStructureConfig.timeTrendData"
        :hospital-comparison-data="currentStructureConfig.hospitalComparisonData"
        :total-count="currentStructureConfig.totalCount"
        :total-count-label="currentStructureConfig.totalCountLabel"
      />

      <IndicatorAnalysis
        v-else-if="templateType === 'STRUCTURE-special'"
        :key="`structure-special-${appliedIndicator}`"
        :title="currentStructureSpecialConfig.title"
        :left-title="currentStructureSpecialConfig.leftTitle"
        :left-chart-title1="currentStructureSpecialConfig.leftChartTitle1"
        :left-chart-title2="currentStructureSpecialConfig.leftChartTitle2"
        :left-chart-color1="'#12B881'"
        :left-chart-color2="'#2E57E5'"
        :time-comparison-title="currentStructureSpecialConfig.timeComparisonTitle"
        :hospital-comparison-title="currentStructureSpecialConfig.hospitalComparisonTitle"
        :ranking-mode="'double'"
        :show-death-toggle="currentStructureSpecialConfig.showDeathToggle"
        :left-data1="currentStructureSpecialConfig.leftData1"
        :left-data2="currentStructureSpecialConfig.leftData2"
        :time-trend-data="currentStructureSpecialConfig.timeTrendData"
        :hospital-comparison-data="currentStructureSpecialConfig.hospitalComparisonData"
        :total-count="currentStructureSpecialConfig.totalCount"
        :total-count-label="currentStructureSpecialConfig.totalCountLabel"
      />

      <IndicatorAnalysisCategory2
        v-else-if="templateType === 'RATE'"
        :key="`rate-${appliedIndicator}`"
        :title="currentTitle"
        :left-title="`${currentTitle}百分率直观展示`"
        :time-comparison-title="`${currentTitle}趋势分析`"
        :hospital-comparison-title="`${currentTitle}医院对比`"
        :show-death-toggle="isDeathRelated"
        :rate-label="'率'"
        :rate-unit="'%'"
        :max-rate="100 / 1.1"
        :y-axis-unit="'%'"
        :card-data="rateData"
        :time-trend-data="rateTimeData"
        :hospital-comparison-data="rateHospitalData"
      />

      <IndicatorAnalysisCategory2
        v-else-if="templateType === 'RATE-special'"
        :key="`rate-special-${appliedIndicator}`"
        :title="currentTitle"
        :left-title="`${currentTitle}率比展示`"
        :time-comparison-title="`${currentTitle}趋势分析`"
        :hospital-comparison-title="`${currentTitle}医院对比`"
        :show-death-toggle="isDeathRelated"
        :rate-label="'率比'"
        :rate-unit="''"
        :max-rate="10"
        :y-axis-unit="''"
        :card-data="rateRatioData"
        :time-trend-data="rateRatioTimeData"
        :hospital-comparison-data="rateRatioHospitalData"
      />

      <IndicatorAnalysisCategory3
        v-else
        :key="`composite-${appliedIndicator}`"
        :title="currentCompositeConfig.title"
        :left-title="currentCompositeConfig.leftTitle"
        :time-comparison-title="currentCompositeConfig.timeComparisonTitle"
        :hospital-comparison-title="currentCompositeConfig.hospitalComparisonTitle"
        :show-death-toggle="currentCompositeConfig.showDeathToggle"
        :data-types="currentCompositeConfig.dataTypes"
        :left-data="currentCompositeConfig.leftData"
        :time-trend-data="currentCompositeConfig.timeTrendData"
        :hospital-comparison-data="currentCompositeConfig.hospitalComparisonData"
        :y-axis-unit="currentCompositeConfig.yAxisUnit"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import cascaderData from '@/data/cascader-unified.json'
import reflectData from '@/data/reflect-unified.json'
import IndicatorAnalysis from '@/components/indicator/IndicatorAnalysis.vue'
import IndicatorAnalysisCategory2 from '@/components/indicator/IndicatorAnalysisCategory2.vue'
import IndicatorAnalysisCategory3 from '@/components/indicator/IndicatorAnalysisCategory3.vue'
import DeathPatientDefinitionTable from '@/components/indicator/DeathPatientDefinitionTable.vue'

type CascaderNode = {
  label: string
  value: string
  children?: CascaderNode[]
}

type TemplateType = 'STRUCTURE' | 'STRUCTURE-special' | 'RATE' | 'RATE-special' | 'COMPOSITE'

const cascaderOptions = cascaderData as CascaderNode[]
const reflectMap = reflectData as unknown as Record<string, string[]>
const route = useRoute()
const router = useRouter()

const draftIndicator = ref(getFirstIndicatorValue())
const appliedIndicator = ref(getFirstIndicatorValue())
const hospitalOptions = [
  { value: 'province', label: '全省' },
  { value: 'hospitalA', label: '医院A' },
  { value: 'hospitalB', label: '医院B' },
  { value: 'hospitalC', label: '医院C' },
  { value: 'hospitalD', label: '医院D' },
  { value: 'hospitalE', label: '医院E' },
]
const draftHospital = ref('province')
const appliedHospital = ref('province')
const isSettingFromRoute = ref(false)

function getFirstIndicatorValue(): string {
  for (const level1 of cascaderOptions) {
    for (const level2 of level1.children ?? []) {
      for (const indicator of level2.children ?? []) {
        return indicator.value
      }
    }
  }
  return ''
}

const allIndicatorOptions = computed(() => {
  const options: Array<{ value: string; label: string }> = []
  for (const level1 of cascaderOptions) {
    for (const level2 of level1.children ?? []) {
      for (const indicator of level2.children ?? []) {
        options.push({ value: indicator.value, label: indicator.label })
      }
    }
  }
  return options
})

const currentTitle = computed(() => {
  const option = allIndicatorOptions.value.find((item) => item.value === appliedIndicator.value)
  return option?.label ?? '指标分析'
})

const templateType = computed<TemplateType>(() => {
  if (reflectMap['STRUCTURE-special']?.includes(appliedIndicator.value)) return 'STRUCTURE-special'
  if (reflectMap['STRUCTURE']?.includes(appliedIndicator.value)) return 'STRUCTURE'
  if (reflectMap['RATE-special']?.includes(appliedIndicator.value)) return 'RATE-special'
  if (reflectMap['RATE']?.includes(appliedIndicator.value)) return 'RATE'
  return 'COMPOSITE'
})

function applySelection() {
  appliedIndicator.value = draftIndicator.value
  appliedHospital.value = draftHospital.value
  isSettingFromRoute.value = true
  router.replace({
    query: { ...route.query, indicator: draftIndicator.value, hospital: draftHospital.value }
  })
  nextTick(() => { isSettingFromRoute.value = false })
}

function findCascaderPathByIndicator(indicatorValue: string) {
  for (const level1 of cascaderOptions) {
    for (const level2 of level1.children ?? []) {
      for (const indicator of level2.children ?? []) {
        if (indicator.value === indicatorValue) {
          return { indicator: indicator.value }
        }
      }
    }
  }
  return null
}

function applyIndicatorFromRouteQuery(indicator: unknown) {
  if (typeof indicator !== 'string' || !indicator.trim()) return
  const path = findCascaderPathByIndicator(indicator.trim())
  if (!path) { console.warn(`指标 "${indicator}" 未找到`); return }
  isSettingFromRoute.value = true
  try {
    appliedIndicator.value = path.indicator
    draftIndicator.value = path.indicator
  } finally {
    nextTick(() => { isSettingFromRoute.value = false })
  }
}

function applyHospitalFromRouteQuery(hospital: unknown) {
  if (isSettingFromRoute.value) return
  if (typeof hospital !== 'string' || !hospital.trim()) return
  const validHospital = hospitalOptions.find(item => item.value === hospital.trim())
  if (validHospital) { appliedHospital.value = hospital.trim(); draftHospital.value = hospital.trim() }
}

onMounted(() => {
  applyIndicatorFromRouteQuery(route.query.indicator)
  applyHospitalFromRouteQuery(route.query.hospital)
})

watch(() => route.query.indicator, (indicator) => { applyIndicatorFromRouteQuery(indicator) })
watch(() => route.query.hospital, (hospital) => { applyHospitalFromRouteQuery(hospital) })

const deathIndicatorSet = new Set([
  'deathDiseaseSpectrum', 'deathSurgicalSpectrum', 'deathPatientDefinition',
  'overallMortalityRate', 'perioperativeMortality',
])
const isDeathRelated = computed(() => deathIndicatorSet.has(appliedIndicator.value))

function hashString(str: string): number {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash
  }
  return Math.abs(hash)
}

function generateRateData(indicator: string) {
  const hash = hashString(indicator)
  const base = 70 + (hash % 30)
  const trend = hash % 3
  const years = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
  const actual: Record<number, number> = {}
  const estimated: Record<number, number> = {}
  years.forEach((year, index) => {
    let value = base + index * 2
    if (trend === 1) value = base + (4 - index) * 2
    if (trend === 2) value = base + (index % 2 === 0 ? 0 : 3)
    actual[year] = value
    estimated[year] = value - 1
  })
  return { actual, estimated }
}

function generateRateTimeData(indicator: string) {
  const data = generateRateData(indicator)
  const years = ['2022', '2023', '2024', '2025', '2026']
  return {
    actual: { years, rates: years.map(year => data.actual[parseInt(year)]) },
    estimated: { years, rates: years.map(year => data.estimated[parseInt(year)]) }
  }
}

function generateRateHospitalData(indicator: string) {
  const hash = hashString(indicator)
  const base = 70 + (hash % 30)
  const hospitals = ['hospitalA', 'hospitalB', 'hospitalC', 'hospitalD', 'hospitalE']
  const years = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
  const actual: Record<string, Record<number, number>> = {}
  const estimated: Record<string, Record<number, number>> = {}
  hospitals.forEach((hospital, hospitalIndex) => {
    const hospitalBase = base + hospitalIndex * 2
    const hospitalTrend = (hash + hospitalIndex) % 3
    const hospitalActual: Record<number, number> = {}
    const hospitalEstimated: Record<number, number> = {}
    years.forEach((year, yearIndex) => {
      let value = hospitalBase + yearIndex * 2
      if (hospitalTrend === 1) value = hospitalBase + (4 - yearIndex) * 2
      if (hospitalTrend === 2) value = hospitalBase + (yearIndex % 2 === 0 ? 0 : 3)
      hospitalActual[year] = value
      hospitalEstimated[year] = value - 1
    })
    actual[hospital] = hospitalActual
    estimated[hospital] = hospitalEstimated
  })
  return { actual, estimated }
}

const structureSingleData = {
  actual: {
    2022: [{ name: '项目A', value: 980 }, { name: '项目B', value: 860 }, { name: '项目C', value: 720 }],
    2023: [{ name: '项目A', value: 1010 }, { name: '项目B', value: 900 }, { name: '项目C', value: 760 }],
    2024: [{ name: '项目A', value: 1050 }, { name: '项目B', value: 930 }, { name: '项目C', value: 780 }],
    2025: [{ name: '项目A', value: 1090 }, { name: '项目B', value: 970 }, { name: '项目C', value: 820 }],
    2026: [{ name: '项目A', value: 1130 }, { name: '项目B', value: 1000 }, { name: '项目C', value: 850 }],
  },
  estimated: {
    2022: [{ name: '项目A', value: 940 }, { name: '项目B', value: 830 }, { name: '项目C', value: 700 }],
    2023: [{ name: '项目A', value: 980 }, { name: '项目B', value: 870 }, { name: '项目C', value: 730 }],
    2024: [{ name: '项目A', value: 1020 }, { name: '项目B', value: 900 }, { name: '项目C', value: 760 }],
    2025: [{ name: '项目A', value: 1060 }, { name: '项目B', value: 940 }, { name: '项目C', value: 790 }],
    2026: [{ name: '项目A', value: 1100 }, { name: '项目B', value: 980 }, { name: '项目C', value: 820 }],
  },
}
const structureSingleTimeData = {
  actual: { years: ['2022', '2023', '2024', '2025', '2026'], data: [2560, 2670, 2760, 2880, 2980] },
  estimated: { years: ['2022', '2023', '2024', '2025', '2026'], data: [2470, 2580, 2680, 2790, 2900] },
}
const structureSingleHospitalData = {
  actual: {
    hospitalA: { name: '医院A', data: [2800, 2920, 3050, 3180, 3320] },
    hospitalB: { name: '医院B', data: [2500, 2610, 2730, 2860, 2980] },
    hospitalC: { name: '医院C', data: [2300, 2410, 2520, 2630, 2750] },
    hospitalD: { name: '医院D', data: [2100, 2200, 2310, 2410, 2520] },
    hospitalE: { name: '医院E', data: [1950, 2040, 2130, 2220, 2310] },
  },
  estimated: {
    hospitalA: { name: '医院A', data: [2700, 2820, 2940, 3070, 3200] },
    hospitalB: { name: '医院B', data: [2420, 2530, 2640, 2760, 2880] },
    hospitalC: { name: '医院C', data: [2240, 2340, 2440, 2550, 2660] },
    hospitalD: { name: '医院D', data: [2040, 2130, 2220, 2310, 2410] },
    hospitalE: { name: '医院E', data: [1890, 1970, 2060, 2140, 2230] },
  },
}

const structureDoubleData2 = {
  actual: {
    2022: [{ name: '项目甲', value: 760 }, { name: '项目乙', value: 660 }, { name: '项目丙', value: 520 }],
    2023: [{ name: '项目甲', value: 790 }, { name: '项目乙', value: 680 }, { name: '项目丙', value: 540 }],
    2024: [{ name: '项目甲', value: 820 }, { name: '项目乙', value: 710 }, { name: '项目丙', value: 570 }],
    2025: [{ name: '项目甲', value: 850 }, { name: '项目乙', value: 740 }, { name: '项目丙', value: 590 }],
    2026: [{ name: '项目甲', value: 880 }, { name: '项目乙', value: 770 }, { name: '项目丙', value: 620 }],
  },
  estimated: {
    2022: [{ name: '项目甲', value: 730 }, { name: '项目乙', value: 630 }, { name: '项目丙', value: 500 }],
    2023: [{ name: '项目甲', value: 760 }, { name: '项目乙', value: 660 }, { name: '项目丙', value: 520 }],
    2024: [{ name: '项目甲', value: 790 }, { name: '项目乙', value: 690 }, { name: '项目丙', value: 550 }],
    2025: [{ name: '项目甲', value: 820 }, { name: '项目乙', value: 720 }, { name: '项目丙', value: 570 }],
    2026: [{ name: '项目甲', value: 850 }, { name: '项目乙', value: 740 }, { name: '项目丙', value: 600 }],
  },
}

const currentStructureConfig = computed(() => {
  const isDeath = deathIndicatorSet.has(appliedIndicator.value)
  return {
    title: currentTitle.value,
    leftTitle: isDeath ? '预期转归不良相关排行榜' : `${currentTitle.value}排行榜`,
    leftChartTitle: isDeath ? '预期转归不良相关 TOP10' : `${currentTitle.value} TOP10`,
    leftChartColor: isDeath ? '#E5455F' : '#2E57E5',
    timeComparisonTitle: `${currentTitle.value}趋势分析`,
    hospitalComparisonTitle: `${currentTitle.value}医院对比`,
    showDeathToggle: isDeath,
    leftData: structureSingleData,
    timeTrendData: structureSingleTimeData,
    hospitalComparisonData: structureSingleHospitalData,
    totalCount: structureSingleTimeData.actual.data[structureSingleTimeData.actual.data.length - 1],
    totalCountLabel: `${currentTitle.value}总量`,
  }
})

const currentStructureSpecialConfig = computed(() => {
  const isDeath = deathIndicatorSet.has(appliedIndicator.value)
  return {
    title: currentTitle.value,
    leftTitle: `${currentTitle.value}排行榜`,
    leftChartTitle1: '治疗性操作 TOP10',
    leftChartTitle2: '诊断性操作 TOP10',
    timeComparisonTitle: `${currentTitle.value}趋势分析`,
    hospitalComparisonTitle: `${currentTitle.value}医院对比`,
    showDeathToggle: isDeath,
    leftData1: structureSingleData,
    leftData2: structureDoubleData2,
    timeTrendData: structureSingleTimeData,
    hospitalComparisonData: structureSingleHospitalData,
    totalCount: structureSingleTimeData.actual.data[structureSingleTimeData.actual.data.length - 1],
    totalCountLabel: `${currentTitle.value}总量`,
  }
})

const rateData = computed(() => generateRateData(appliedIndicator.value))
const rateTimeData = computed(() => generateRateTimeData(appliedIndicator.value))
const rateHospitalData = computed(() => generateRateHospitalData(appliedIndicator.value))

function generateRateRatioData(indicator: string) {
  const hash = hashString(indicator)
  const base = 1.5 + (hash % 150) / 100
  const trend = hash % 3
  const years = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
  const actual: Record<number, number> = {}
  const estimated: Record<number, number> = {}
  years.forEach((year, index) => {
    let value = base + index * 0.1
    if (trend === 1) value = base + (4 - index) * 0.1
    if (trend === 2) value = base + (index % 2 === 0 ? 0 : 0.15)
    actual[year] = Number(value.toFixed(1))
    estimated[year] = Number((value - 0.1).toFixed(1))
  })
  return { actual, estimated }
}

function generateRateRatioTimeData(indicator: string) {
  const data = generateRateRatioData(indicator)
  const years = ['2022', '2023', '2024', '2025', '2026']
  return {
    actual: { years, rates: years.map(year => data.actual[parseInt(year)]) },
    estimated: { years, rates: years.map(year => data.estimated[parseInt(year)]) }
  }
}

function generateRateRatioHospitalData(indicator: string) {
  const hash = hashString(indicator)
  const base = 1.5 + (hash % 150) / 100
  const hospitals = ['hospitalA', 'hospitalB', 'hospitalC', 'hospitalD', 'hospitalE']
  const years = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
  const actual: Record<string, Record<number, number>> = {}
  const estimated: Record<string, Record<number, number>> = {}
  hospitals.forEach((hospital, hospitalIndex) => {
    const hospitalBase = base + hospitalIndex * 0.2
    const hospitalTrend = (hash + hospitalIndex) % 3
    const hospitalActual: Record<number, number> = {}
    const hospitalEstimated: Record<number, number> = {}
    years.forEach((year, yearIndex) => {
      let value = hospitalBase + yearIndex * 0.1
      if (hospitalTrend === 1) value = hospitalBase + (4 - yearIndex) * 0.1
      if (hospitalTrend === 2) value = hospitalBase + (yearIndex % 2 === 0 ? 0 : 0.15)
      hospitalActual[year] = Number(value.toFixed(1))
      hospitalEstimated[year] = Number((value - 0.1).toFixed(1))
    })
    actual[hospital] = hospitalActual
    estimated[hospital] = hospitalEstimated
  })
  return { actual, estimated }
}

const rateRatioData = computed(() => generateRateRatioData(appliedIndicator.value))
const rateRatioTimeData = computed(() => generateRateRatioTimeData(appliedIndicator.value))
const rateRatioHospitalData = computed(() => generateRateRatioHospitalData(appliedIndicator.value))

const mortalityDataTypes = [
  { name: '患者住院死亡率', key: 'inpatient' },
  { name: '新生儿患者住院死亡率', key: 'neonatal' },
  { name: '手术患者死亡率', key: 'surgical' },
  { name: '术后24小时死亡率', key: 'post24h' },
  { name: '术后48小时死亡率', key: 'post48h' },
]
const mortalityLeftData = {
  actual: {
    2022: { inpatient: 2.8, neonatal: 2.1, surgical: 3.5, post24h: 1.0, post48h: 1.8 },
    2023: { inpatient: 2.7, neonatal: 2.0, surgical: 3.4, post24h: 0.9, post48h: 1.7 },
    2024: { inpatient: 2.5, neonatal: 1.8, surgical: 3.2, post24h: 0.8, post48h: 1.5 },
    2025: { inpatient: 2.4, neonatal: 1.7, surgical: 3.1, post24h: 0.7, post48h: 1.4 },
    2026: { inpatient: 2.3, neonatal: 1.6, surgical: 3.0, post24h: 0.6, post48h: 1.3 },
  },
  estimated: {
    2022: { inpatient: 3.1, neonatal: 2.3, surgical: 3.8, post24h: 1.1, post48h: 2.0 },
    2023: { inpatient: 3.0, neonatal: 2.2, surgical: 3.7, post24h: 1.0, post48h: 1.9 },
    2024: { inpatient: 2.8, neonatal: 2.0, surgical: 3.5, post24h: 0.9, post48h: 1.7 },
    2025: { inpatient: 2.7, neonatal: 1.9, surgical: 3.4, post24h: 0.8, post48h: 1.6 },
    2026: { inpatient: 2.6, neonatal: 1.8, surgical: 3.3, post24h: 0.7, post48h: 1.5 },
  },
}
const mortalityTimeTrendData = {
  actual: {
    years: ['2022', '2023', '2024', '2025', '2026'],
    inpatient: [2.8, 2.7, 2.5, 2.4, 2.3],
    neonatal: [2.1, 2.0, 1.8, 1.7, 1.6],
    surgical: [3.5, 3.4, 3.2, 3.1, 3.0],
    post24h: [1.0, 0.9, 0.8, 0.7, 0.6],
    post48h: [1.8, 1.7, 1.5, 1.4, 1.3],
  },
  estimated: {
    years: ['2022', '2023', '2024', '2025', '2026'],
    inpatient: [3.1, 3.0, 2.8, 2.7, 2.6],
    neonatal: [2.3, 2.2, 2.0, 1.9, 1.8],
    surgical: [3.8, 3.7, 3.5, 3.4, 3.3],
    post24h: [1.1, 1.0, 0.9, 0.8, 0.7],
    post48h: [2.0, 1.9, 1.7, 1.6, 1.5],
  },
}
const mortalityHospitalComparisonData = (() => {
  const hospitals = ['hospitalA', 'hospitalB', 'hospitalC', 'hospitalD', 'hospitalE']
  const bases = { hospitalA: { inpatient: 2.9, neonatal: 2.2, surgical: 3.6, post24h: 1.1, post48h: 1.9 }, hospitalB: { inpatient: 2.7, neonatal: 2.0, surgical: 3.4, post24h: 0.9, post48h: 1.7 }, hospitalC: { inpatient: 3.0, neonatal: 2.3, surgical: 3.7, post24h: 1.2, post48h: 2.0 }, hospitalD: { inpatient: 2.8, neonatal: 2.1, surgical: 3.5, post24h: 1.1, post48h: 1.9 }, hospitalE: { inpatient: 2.7, neonatal: 2.0, surgical: 3.4, post24h: 1.0, post48h: 1.8 } }
  const estBases = { hospitalA: { inpatient: 3.2, neonatal: 2.4, surgical: 3.9, post24h: 1.2, post48h: 2.1 }, hospitalB: { inpatient: 3.0, neonatal: 2.2, surgical: 3.7, post24h: 1.0, post48h: 1.9 }, hospitalC: { inpatient: 3.3, neonatal: 2.5, surgical: 4.0, post24h: 1.3, post48h: 2.2 }, hospitalD: { inpatient: 3.1, neonatal: 2.3, surgical: 3.8, post24h: 1.2, post48h: 2.1 }, hospitalE: { inpatient: 3.0, neonatal: 2.2, surgical: 3.7, post24h: 1.1, post48h: 2.0 } }
  const years = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
  const actual: Record<string, Record<number, typeof bases.hospitalA>> = {}
  const estimated: Record<string, Record<number, typeof bases.hospitalA>> = {}
  hospitals.forEach(h => {
    actual[h] = {}; estimated[h] = {}
    years.forEach((year, i) => { actual[h][year] = bases[h]; estimated[h][year] = estBases[h] })
  })
  return { actual, estimated }
})()

const rehospitalizationDataTypes = [
  { name: '当日再住院', key: 'sameDay' },
  { name: '2-15天再住院', key: 'twoToFifteenDays' },
  { name: '0-31天再住院', key: 'zeroToThirtyOneDays' },
]
const rehospitalizationLeftData = {
  actual: {
    2022: { sameDay: 0.5, twoToFifteenDays: 2.3, zeroToThirtyOneDays: 4.8 },
    2023: { sameDay: 0.4, twoToFifteenDays: 2.2, zeroToThirtyOneDays: 4.6 },
    2024: { sameDay: 0.3, twoToFifteenDays: 2.0, zeroToThirtyOneDays: 4.3 },
    2025: { sameDay: 0.3, twoToFifteenDays: 1.9, zeroToThirtyOneDays: 4.1 },
    2026: { sameDay: 0.2, twoToFifteenDays: 1.8, zeroToThirtyOneDays: 3.9 },
  },
  estimated: {
    2022: { sameDay: 0.6, twoToFifteenDays: 2.5, zeroToThirtyOneDays: 5.2 },
    2023: { sameDay: 0.5, twoToFifteenDays: 2.4, zeroToThirtyOneDays: 5.0 },
    2024: { sameDay: 0.4, twoToFifteenDays: 2.2, zeroToThirtyOneDays: 4.7 },
    2025: { sameDay: 0.4, twoToFifteenDays: 2.1, zeroToThirtyOneDays: 4.5 },
    2026: { sameDay: 0.3, twoToFifteenDays: 2.0, zeroToThirtyOneDays: 4.3 },
  },
}
const rehospitalizationTimeTrendData = {
  actual: {
    years: ['2022', '2023', '2024', '2025', '2026'],
    sameDay: [0.5, 0.4, 0.3, 0.3, 0.2],
    twoToFifteenDays: [2.3, 2.2, 2.0, 1.9, 1.8],
    zeroToThirtyOneDays: [4.8, 4.6, 4.3, 4.1, 3.9],
  },
  estimated: {
    years: ['2022', '2023', '2024', '2025', '2026'],
    sameDay: [0.6, 0.5, 0.4, 0.4, 0.3],
    twoToFifteenDays: [2.5, 2.4, 2.2, 2.1, 2.0],
    zeroToThirtyOneDays: [5.2, 5.0, 4.7, 4.5, 4.3],
  },
}
const rehospitalizationHospitalComparisonData = (() => {
  const hospitals = ['hospitalA', 'hospitalB', 'hospitalC', 'hospitalD', 'hospitalE']
  const bases = {
    hospitalA: { sameDay: 0.6, twoToFifteenDays: 2.4, zeroToThirtyOneDays: 4.9 },
    hospitalB: { sameDay: 0.5, twoToFifteenDays: 2.3, zeroToThirtyOneDays: 4.8 },
    hospitalC: { sameDay: 0.7, twoToFifteenDays: 2.5, zeroToThirtyOneDays: 5.1 },
    hospitalD: { sameDay: 0.4, twoToFifteenDays: 2.2, zeroToThirtyOneDays: 4.6 },
    hospitalE: { sameDay: 0.5, twoToFifteenDays: 2.3, zeroToThirtyOneDays: 4.8 },
  }
  const estBases = {
    hospitalA: { sameDay: 0.7, twoToFifteenDays: 2.6, zeroToThirtyOneDays: 5.3 },
    hospitalB: { sameDay: 0.6, twoToFifteenDays: 2.5, zeroToThirtyOneDays: 5.2 },
    hospitalC: { sameDay: 0.8, twoToFifteenDays: 2.7, zeroToThirtyOneDays: 5.5 },
    hospitalD: { sameDay: 0.5, twoToFifteenDays: 2.4, zeroToThirtyOneDays: 5.0 },
    hospitalE: { sameDay: 0.6, twoToFifteenDays: 2.5, zeroToThirtyOneDays: 5.2 },
  }
  const years = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
  const actual: Record<string, Record<number, typeof bases.hospitalA>> = {}
  const estimated: Record<string, Record<number, typeof bases.hospitalA>> = {}
  hospitals.forEach(h => {
    actual[h] = {}; estimated[h] = {}
    years.forEach(year => { actual[h][year] = bases[h]; estimated[h][year] = estBases[h] })
  })
  return { actual, estimated }
})()

const returnToOrDataTypes = [
  { name: '同一住院周期内重返', key: 'sameAdmission' },
  { name: '同一住院周期且48小时内重返', key: 'sameAdmission48h' },
]
const returnToOrLeftData = {
  actual: {
    2022: { sameAdmission: 1.2, sameAdmission48h: 0.8 },
    2023: { sameAdmission: 1.1, sameAdmission48h: 0.7 },
    2024: { sameAdmission: 1.0, sameAdmission48h: 0.6 },
    2025: { sameAdmission: 0.9, sameAdmission48h: 0.5 },
    2026: { sameAdmission: 0.8, sameAdmission48h: 0.4 },
  },
  estimated: {
    2022: { sameAdmission: 1.3, sameAdmission48h: 0.9 },
    2023: { sameAdmission: 1.2, sameAdmission48h: 0.8 },
    2024: { sameAdmission: 1.1, sameAdmission48h: 0.7 },
    2025: { sameAppointment: 1.0, sameAdmission48h: 0.6 },
    2026: { sameAdmission: 0.9, sameAdmission48h: 0.5 },
  },
}
const returnToOrTimeTrendData = {
  actual: {
    years: ['2022', '2023', '2024', '2025', '2026'],
    sameAdmission: [1.2, 1.1, 1.0, 0.9, 0.8],
    sameAdmission48h: [0.8, 0.7, 0.6, 0.5, 0.4],
  },
  estimated: {
    years: ['2022', '2023', '2024', '2025', '2026'],
    sameAdmission: [1.3, 1.2, 1.1, 1.0, 0.9],
    sameAdmission48h: [0.9, 0.8, 0.7, 0.6, 0.5],
  },
}
const returnToOrHospitalComparisonData = (() => {
  const hospitals = ['hospitalA', 'hospitalB', 'hospitalC', 'hospitalD', 'hospitalE']
  const bases = {
    hospitalA: { sameAdmission: 1.3, sameAdmission48h: 0.9 }, hospitalB: { sameAdmission: 1.2, sameAdmission48h: 0.8 },
    hospitalC: { sameAdmission: 1.4, sameAdmission48h: 1.0 }, hospitalD: { sameAdmission: 1.1, sameAdmission48h: 0.7 },
    hospitalE: { sameAdmission: 1.2, sameAdmission48h: 0.8 },
  }
  const estBases = {
    hospitalA: { sameAdmission: 1.4, sameAdmission48h: 1.0 }, hospitalB: { sameAdmission: 1.3, sameAdmission48h: 0.9 },
    hospitalC: { sameAdmission: 1.5, sameAdmission48h: 1.1 }, hospitalD: { sameAdmission: 1.2, sameAdmission48h: 0.8 },
    hospitalE: { sameAdmission: 1.3, sameAdmission48h: 0.9 },
  }
  const years = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
  const actual: Record<string, Record<number, typeof bases.hospitalA>> = {}
  const estimated: Record<string, Record<number, typeof bases.hospitalA>> = {}
  hospitals.forEach(h => {
    actual[h] = {}; estimated[h] = {}
    years.forEach(year => { actual[h][year] = bases[h]; estimated[h][year] = estBases[h] })
  })
  return { actual, estimated }
})()

const perioperativeMortalityDataTypes = [
  { name: '手术当日死亡率', key: 'sameDay' },
  { name: '手术后24小时死亡率', key: 'post24h' },
  { name: '手术48小时死亡率', key: 'post48h' },
]
const perioperativeMortalityLeftData = {
  actual: {
    2022: { sameDay: 0.5, post24h: 0.8, post48h: 1.2 },
    2023: { sameDay: 0.4, post24h: 0.7, post48h: 1.1 },
    2024: { sameDay: 0.3, post24h: 0.6, post48h: 1.0 },
    2025: { sameDay: 0.3, post24h: 0.5, post48h: 0.9 },
    2026: { sameDay: 0.2, post24h: 0.4, post48h: 0.8 },
  },
  estimated: {
    2022: { sameDay: 0.6, post24h: 0.9, post48h: 1.3 },
    2023: { sameDay: 0.5, post24h: 0.8, post48h: 1.2 },
    2024: { sameDay: 0.4, post24h: 0.7, post48h: 1.1 },
    2025: { sameDay: 0.4, post24h: 0.6, post48h: 1.0 },
    2026: { sameDay: 0.3, post24h: 0.5, post48h: 0.9 },
  },
}
const perioperativeMortalityTimeTrendData = {
  actual: {
    years: ['2022', '2023', '2024', '2025', '2026'],
    sameDay: [0.5, 0.4, 0.3, 0.3, 0.2],
    post24h: [0.8, 0.7, 0.6, 0.5, 0.4],
    post48h: [1.2, 1.1, 1.0, 0.9, 0.8],
  },
  estimated: {
    years: ['2022', '2023', '2024', '2025', '2026'],
    sameDay: [0.6, 0.5, 0.4, 0.4, 0.3],
    post24h: [0.9, 0.8, 0.7, 0.6, 0.5],
    post48h: [1.3, 1.2, 1.1, 1.0, 0.9],
  },
}
const perioperativeMortalityHospitalComparisonData = (() => {
  const hospitals = ['hospitalA', 'hospitalB', 'hospitalC', 'hospitalD', 'hospitalE']
  const bases = {
    hospitalA: { sameDay: 0.6, post24h: 0.9, post48h: 1.3 }, hospitalB: { sameDay: 0.5, post24h: 0.8, post48h: 1.2 },
    hospitalC: { sameDay: 0.7, post24h: 1.0, post48h: 1.4 }, hospitalD: { sameDay: 0.4, post24h: 0.7, post48h: 1.1 },
    hospitalE: { sameDay: 0.5, post24h: 0.8, post48h: 1.2 },
  }
  const estBases = {
    hospitalA: { sameDay: 0.7, post24h: 1.0, post48h: 1.4 }, hospitalB: { sameDay: 0.6, post24h: 0.9, post48h: 1.3 },
    hospitalC: { sameDay: 0.8, post24h: 1.1, post48h: 1.5 }, hospitalD: { sameDay: 0.5, post24h: 0.8, post48h: 1.2 },
    hospitalE: { sameDay: 0.6, post24h: 0.9, post48h: 1.3 },
  }
  const years = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
  const actual: Record<string, Record<number, typeof bases.hospitalA>> = {}
  const estimated: Record<string, Record<number, typeof bases.hospitalA>> = {}
  hospitals.forEach(h => {
    actual[h] = {}; estimated[h] = {}
    years.forEach(year => { actual[h][year] = bases[h]; estimated[h][year] = estBases[h] })
  })
  return { actual, estimated }
})()

const compositeConfigMap: Record<string, any> = {
  overallMortalityRate: {
    title: '患者住院死亡率', leftTitle: '死亡率细分', timeComparisonTitle: '死亡率趋势分析', hospitalComparisonTitle: '死亡率医院对比',
    showDeathToggle: true, dataTypes: mortalityDataTypes, leftData: mortalityLeftData, timeTrendData: mortalityTimeTrendData,
    hospitalComparisonData: mortalityHospitalComparisonData, yAxisUnit: '%',
  },
  perioperativeMortality: {
    title: '住院患者围手术期死亡率', leftTitle: '围手术期死亡率细分', timeComparisonTitle: '围手术期死亡率趋势分析', hospitalComparisonTitle: '围手术期死亡率医院对比',
    showDeathToggle: true, dataTypes: perioperativeMortalityDataTypes, leftData: perioperativeMortalityLeftData, timeTrendData: perioperativeMortalityTimeTrendData,
    hospitalComparisonData: perioperativeMortalityHospitalComparisonData, yAxisUnit: '%',
  },
  unexpectedRehospitalizationAnalysis: {
    title: '非预期再住院情况分析', leftTitle: '再住院情况细分', timeComparisonTitle: '再住院趋势分析', hospitalComparisonTitle: '再住院医院对比',
    showDeathToggle: false, dataTypes: rehospitalizationDataTypes, leftData: rehospitalizationLeftData, timeTrendData: rehospitalizationTimeTrendData,
    hospitalComparisonData: rehospitalizationHospitalComparisonData, yAxisUnit: '%',
  },
  unplannedReturnToORAnalysis: {
    title: '非计划重返手术室再手术分析', leftTitle: '重返手术室情况细分', timeComparisonTitle: '重返手术室趋势分析', hospitalComparisonTitle: '重返手术室医院对比',
    showDeathToggle: false, dataTypes: returnToOrDataTypes, leftData: returnToOrLeftData, timeTrendData: returnToOrTimeTrendData,
    hospitalComparisonData: returnToOrHospitalComparisonData, yAxisUnit: '%',
  },
}

const currentCompositeConfig = computed(() => {
  return compositeConfigMap[appliedIndicator.value] ?? {
    title: currentTitle.value,
    leftTitle: `${currentTitle.value}结构化指标`,
    timeComparisonTitle: `${currentTitle.value}趋势分析`,
    hospitalComparisonTitle: `${currentTitle.value}医院对比`,
    showDeathToggle: false,
    dataTypes: rehospitalizationDataTypes,
    leftData: rehospitalizationLeftData,
    timeTrendData: rehospitalizationTimeTrendData,
    hospitalComparisonData: rehospitalizationHospitalComparisonData,
    yAxisUnit: '%',
  }
})
</script>
