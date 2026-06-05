<template>
  <div class="flex h-full min-h-0 flex-col bg-[#F4F6F8] p-5 font-sans">
    <header class="mb-5 flex flex-wrap items-center justify-between gap-4">
      <h1 class="text-[24px] font-bold text-[#1F264D]">指标分析台</h1>
      <div class="flex flex-wrap items-center gap-2.5">
        <select
          v-model="draftIndicatorId"
          class="h-8 min-w-[300px] rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
        >
          <option v-for="item in indicatorOptions" :key="item.value" :value="item.value">
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

    <div v-if="isLoadingConfig" class="flex flex-1 items-center justify-center">
      <div class="text-[16px] text-[#596080]">加载中...</div>
    </div>

    <div v-else-if="currentConfig" class="min-h-0 flex-1">
      <DeathPatientDefinitionTable
        v-if="isSpecialDeathPatientIndicator"
        :key="`death-table-${appliedIndicatorId}`"
        :title="currentConfig.title"
      />

      <IndicatorAnalysis
        v-else-if="currentConfig.template_type === 'STRUCTURE'"
        :key="`structure-${appliedIndicatorId}`"
        :indicator_id="appliedIndicatorId ?? undefined"
        :init-time-mode="routeTimeMode ?? undefined"
        :init-time-value="routeTimeValue ?? undefined"
        :init-hospital="appliedHospital"
        :title="currentConfig.title"
        :left-title="currentConfig.leftTitle || `${currentConfig.title}排行榜`"
        :left-chart-title="currentConfig.leftChartTitle || `${currentConfig.title} TOP10`"
        :left-chart-color="currentConfig.leftChartColor || '#2E57E5'"
        :time-comparison-title="currentConfig.timeComparisonTitle || `${currentConfig.title}趋势分析`"
        :hospital-comparison-title="currentConfig.hospitalComparisonTitle || `${currentConfig.title}医院对比`"
        :ranking-mode="currentConfig.rankingMode || 'single'"
        :show-death-toggle="currentConfig.showDeathToggle"
        :left-data="currentConfig.data.leftData || {}"
        :time-trend-data="currentConfig.data.timeTrendData || {}"
        :hospital-comparison-data="currentConfig.data.hospitalComparisonData || {}"
        :total-count="currentConfig.data.totalCount || 0"
        :total-count-label="currentConfig.totalCountLabel || `${currentConfig.title}总量`"
      />

      <IndicatorAnalysis
        v-else-if="currentConfig.template_type === 'STRUCTURE-special'"
        :key="`structure-special-${appliedIndicatorId}`"
        :indicator_id="appliedIndicatorId ?? undefined"
        :init-time-mode="routeTimeMode ?? undefined"
        :init-time-value="routeTimeValue ?? undefined"
        :init-hospital="appliedHospital"
        :title="currentConfig.title"
        :left-title="currentConfig.leftTitle || `${currentConfig.title}排行榜`"
        :left-chart-title1="currentConfig.leftChartTitle1 || '治疗性操作 TOP10'"
        :left-chart-title2="currentConfig.leftChartTitle2 || '诊断性操作 TOP10'"
        :left-chart-color1="currentConfig.leftChartColor1 || '#12B881'"
        :left-chart-color2="currentConfig.leftChartColor2 || '#2E57E5'"
        :time-comparison-title="currentConfig.timeComparisonTitle || `${currentConfig.title}趋势分析`"
        :hospital-comparison-title="currentConfig.hospitalComparisonTitle || `${currentConfig.title}医院对比`"
        :ranking-mode="currentConfig.rankingMode || 'double'"
        :show-death-toggle="currentConfig.showDeathToggle"
        :left-data="(currentConfig.rankingMode === 'double' || !currentConfig.rankingMode) ? (currentConfig.data.leftData1 || {}) : {}"
        :left-data1="currentConfig.data.leftData1 || {}"
        :left-data2="currentConfig.data.leftData2 || {}"
        :time-trend-data="currentConfig.data.timeTrendData || {}"
        :hospital-comparison-data="currentConfig.data.hospitalComparisonData || {}"
        :total-count="currentConfig.data.totalCount || 0"
        :total-count-label="currentConfig.totalCountLabel || `${currentConfig.title}总量`"
      />

      <IndicatorAnalysisCategory2
        v-else-if="currentConfig.template_type === 'RATE'"
        :key="`rate-${appliedIndicatorId}`"
        :indicator_id="appliedIndicatorId ?? undefined"
        :init-time-mode="routeTimeMode ?? undefined"
        :init-time-value="routeTimeValue ?? undefined"
        :init-hospital="appliedHospital"
        :title="currentConfig.title"
        :left-title="currentConfig.leftTitle || `${currentConfig.title}百分率直观展示`"
        :time-comparison-title="currentConfig.timeComparisonTitle || `${currentConfig.title}趋势分析`"
        :hospital-comparison-title="currentConfig.hospitalComparisonTitle || `${currentConfig.title}医院对比`"
        :show-death-toggle="currentConfig.showDeathToggle"
        :rate-label="currentConfig.rateLabel || '率'"
        :rate-unit="currentConfig.rateUnit || '%'"
        :max-rate="currentConfig.maxRate || 100"
        :y-axis-unit="currentConfig.yAxisUnit || '%'"
        :card-data="currentConfig.data.cardData || {}"
        :time-trend-data="currentConfig.data.timeTrendData || {}"
        :hospital-comparison-data="currentConfig.data.hospitalComparisonData || {}"
      />

      <IndicatorAnalysisCategory2
        v-else-if="currentConfig.template_type === 'RATE-special'"
        :key="`rate-special-${appliedIndicatorId}`"
        :indicator_id="appliedIndicatorId ?? undefined"
        :init-time-mode="routeTimeMode ?? undefined"
        :init-time-value="routeTimeValue ?? undefined"
        :init-hospital="appliedHospital"
        :title="currentConfig.title"
        :left-title="currentConfig.leftTitle || `${currentConfig.title}率比展示`"
        :time-comparison-title="currentConfig.timeComparisonTitle || `${currentConfig.title}趋势分析`"
        :hospital-comparison-title="currentConfig.hospitalComparisonTitle || `${currentConfig.title}医院对比`"
        :show-death-toggle="currentConfig.showDeathToggle"
        :rate-label="currentConfig.rateLabel || '率比'"
        :rate-unit="currentConfig.rateUnit || ''"
        :max-rate="currentConfig.maxRate || 10"
        :y-axis-unit="currentConfig.yAxisUnit || ''"
        :card-data="currentConfig.data.cardData || {}"
        :time-trend-data="currentConfig.data.timeTrendData || {}"
        :hospital-comparison-data="currentConfig.data.hospitalComparisonData || {}"
      />

      <IndicatorAnalysisCategory3
        v-else-if="currentConfig.template_type === 'COMPOSITE'"
        :key="`composite-${appliedIndicatorId}`"
        :indicator_id="appliedIndicatorId ?? undefined"
        :init-time-mode="routeTimeMode ?? undefined"
        :init-time-value="routeTimeValue ?? undefined"
        :init-hospital="appliedHospital"
        :title="currentConfig.title"
        :left-title="currentConfig.leftTitle || `${currentConfig.title}细分`"
        :time-comparison-title="currentConfig.timeComparisonTitle || `${currentConfig.title}趋势分析`"
        :hospital-comparison-title="currentConfig.hospitalComparisonTitle || `${currentConfig.title}医院对比`"
        :show-death-toggle="currentConfig.showDeathToggle"
        :data-types="currentConfig.data.dataTypes || []"
        :left-data="currentConfig.data.leftData || {}"
        :time-trend-data="currentConfig.data.timeTrendData || {}"
        :hospital-comparison-data="currentConfig.data.hospitalComparisonData || {}"
        :y-axis-unit="currentConfig.yAxisUnit || '%'"
      />

      <div v-else class="flex flex-1 items-center justify-center text-[#596080]">
        暂无该指标的配置信息
      </div>
    </div>

    <div v-else class="flex flex-1 items-center justify-center">
      <div class="text-[16px] text-[#596080]">暂无数据，请选择指标后查询</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import IndicatorAnalysis from '@/components/indicator/IndicatorAnalysis.vue'
import IndicatorAnalysisCategory2 from '@/components/indicator/IndicatorAnalysisCategory2.vue'
import IndicatorAnalysisCategory3 from '@/components/indicator/IndicatorAnalysisCategory3.vue'
import DeathPatientDefinitionTable from '@/components/indicator/DeathPatientDefinitionTable.vue'
import { core18Api, type IndicatorConfigItem } from '@/api/core18'

const SPECIAL_DEATH_PATIENT_NAME = '死亡或出院预期转归不良患者'

const route = useRoute()
const router = useRouter()

const indicatorConfigs = ref<IndicatorConfigItem[]>([])
const isLoadingConfig = ref(false)

const draftIndicatorId = ref<number | null>(null)
const appliedIndicatorId = ref<number | null>(null)
const isSettingFromRoute = ref(false)

const routeTimeMode = ref<'monthly' | 'quarterly' | null>(null)
const routeTimeValue = ref<string | null>(null)

const hospitalList = ref<{ value: string; label: string }[]>([])
const hospitalOptions = computed(() => [
  { value: 'province', label: '全省' },
  ...hospitalList.value.map(hospital => ({ value: hospital.value, label: hospital.label })),
])
const draftHospital = ref('province')
const appliedHospital = ref('province')

async function loadIndicatorConfigs(params?: { time_mode?: string; time_value?: string }) {
  isLoadingConfig.value = true
  try {
    const response = await core18Api.getIndicatorConfigs({
      hospital_code: appliedHospital.value === 'province' ? undefined : appliedHospital.value,
      time_mode: params?.time_mode || 'monthly',
      time_value: params?.time_value,
    })
    indicatorConfigs.value = response || []
  } catch (error) {
    console.error('加载指标配置失败:', error)
    indicatorConfigs.value = []
  } finally {
    isLoadingConfig.value = false
  }
}

async function loadHospitals() {
  try {
    const response = await core18Api.getHospitals()
    hospitalList.value = response || []
  } catch (error) {
    console.error('加载医院列表失败:', error)
  }
}

const indicatorOptions = computed(() =>
  indicatorConfigs.value.map(config => ({
    value: config.indicator_id,
    label: config.indicator_name,
  })),
)

const currentConfig = computed(() =>
  indicatorConfigs.value.find(config => config.indicator_id === appliedIndicatorId.value) ?? null,
)

const isSpecialDeathPatientIndicator = computed(() =>
  currentConfig.value?.indicator_name === SPECIAL_DEATH_PATIENT_NAME,
)

function getFirstIndicatorId(): number | null {
  return indicatorConfigs.value[0]?.indicator_id ?? null
}

function findIndicatorId(id: number): number | null {
  const found = indicatorConfigs.value.find(config => config.indicator_id === id)
  return found ? found.indicator_id : null
}

function applyIndicatorIdFromRouteQuery(indicatorId: unknown) {
  if (typeof indicatorId !== 'string') {
    return
  }
  const parsed = Number.parseInt(indicatorId, 10)
  if (Number.isNaN(parsed)) {
    return
  }
  const found = findIndicatorId(parsed)
  if (found !== null) {
    draftIndicatorId.value = found
    appliedIndicatorId.value = found
    return
  }
  const firstIndicatorId = getFirstIndicatorId()
  if (firstIndicatorId !== null) {
    draftIndicatorId.value = firstIndicatorId
    appliedIndicatorId.value = firstIndicatorId
  }
}

function applySelection() {
  appliedIndicatorId.value = draftIndicatorId.value
  appliedHospital.value = draftHospital.value
  isSettingFromRoute.value = true
  router.replace({
    query: {
      ...route.query,
      indicatorId: draftIndicatorId.value != null ? String(draftIndicatorId.value) : undefined,
      hospital: draftHospital.value,
    },
  })
  nextTick(() => {
    isSettingFromRoute.value = false
  })
}

function applyHospitalFromRouteQuery(hospital: unknown) {
  if (isSettingFromRoute.value) return
  if (typeof hospital !== 'string' || !hospital.trim()) return
  const valid = hospitalOptions.value.find(item => item.value === hospital.trim())
  if (valid) {
    appliedHospital.value = hospital.trim()
    draftHospital.value = hospital.trim()
  }
}

onMounted(async () => {
  const queryTimeMode = route.query.timeMode as string | undefined
  const queryTimeValue = route.query.timeValue as string | undefined
  if (queryTimeMode && queryTimeValue && (queryTimeMode === 'monthly' || queryTimeMode === 'quarterly')) {
    routeTimeMode.value = queryTimeMode
    routeTimeValue.value = queryTimeValue
  }

  await loadIndicatorConfigs({
    time_mode: routeTimeMode.value ?? 'monthly',
    time_value: routeTimeValue.value ?? undefined,
  })
  await loadHospitals()

  applyIndicatorIdFromRouteQuery(route.query.indicatorId)
  applyHospitalFromRouteQuery(route.query.hospital)

  if (!appliedIndicatorId.value) {
    const firstIndicatorId = getFirstIndicatorId()
    if (firstIndicatorId !== null) {
      draftIndicatorId.value = firstIndicatorId
      appliedIndicatorId.value = firstIndicatorId
    }
  }
})

watch(() => route.query.indicatorId, indicatorId => applyIndicatorIdFromRouteQuery(indicatorId))
watch(() => route.query.hospital, hospital => applyHospitalFromRouteQuery(hospital))
</script>
