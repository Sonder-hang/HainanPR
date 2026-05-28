<template>
  <div class="flex h-full min-h-0 flex-col bg-[#F4F6F8] p-5 font-sans">
    <!-- 顶部筛选器：仅指标选择 + 医院选择 + 查询按钮 -->
    <header class="mb-5 flex flex-wrap items-center justify-between gap-4">
      <h1 class="text-[24px] font-bold text-[#1F264D]">指标分析台</h1>
      <div class="flex flex-wrap items-center gap-2.5">
        <!-- 指标下拉 -->
        <select
          v-model="draftIndicator"
          class="h-8 min-w-[300px] rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
        >
          <option v-for="item in indicatorOptions" :key="item.value" :value="item.value">
            {{ item.label }}
          </option>
        </select>
        <!-- 医院下拉 -->
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

    <!-- 加载状态 -->
    <div v-if="isLoadingConfig" class="flex flex-1 items-center justify-center">
      <div class="text-[16px] text-[#596080]">加载中...</div>
    </div>

    <!-- 分析组件 -->
    <div v-else-if="currentConfig" class="min-h-0 flex-1">
      <!-- 死亡患者定义表 -->
      <DeathPatientDefinitionTable
        v-if="appliedIndicator === 'deathPatientDefinition'"
        :key="`death-table-${appliedIndicator}`"
        :title="currentConfig.title"
      />

      <!-- STRUCTURE 模板 -->
      <IndicatorAnalysis
        v-else-if="currentConfig.template_type === 'STRUCTURE'"
        :key="`structure-${appliedIndicator}`"
        :indicator_key="appliedIndicator"
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

      <!-- STRUCTURE-special 模板 -->
      <IndicatorAnalysis
        v-else-if="currentConfig.template_type === 'STRUCTURE-special'"
        :key="`structure-special-${appliedIndicator}`"
        :indicator_key="appliedIndicator"
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

      <!-- RATE 模板 -->
      <IndicatorAnalysisCategory2
        v-else-if="currentConfig.template_type === 'RATE'"
        :key="`rate-${appliedIndicator}`"
        :indicator_key="appliedIndicator"
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

      <!-- RATE-special 模板（率比） -->
      <IndicatorAnalysisCategory2
        v-else-if="currentConfig.template_type === 'RATE-special'"
        :key="`rate-special-${appliedIndicator}`"
        :indicator_key="appliedIndicator"
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

      <!-- COMPOSITE 模板 -->
      <IndicatorAnalysisCategory3
        v-else-if="currentConfig.template_type === 'COMPOSITE'"
        :key="`composite-${appliedIndicator}`"
        :indicator_key="appliedIndicator"
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

      <!-- 兜底：未匹配模板类型 -->
      <div v-else class="flex flex-1 items-center justify-center text-[#596080]">
        暂无该指标的配置信息
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="flex flex-1 items-center justify-center">
      <div class="text-[16px] text-[#596080]">暂无数据，请选择指标后查询</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import IndicatorAnalysis from '@/components/indicator/IndicatorAnalysis.vue'
import IndicatorAnalysisCategory2 from '@/components/indicator/IndicatorAnalysisCategory2.vue'
import IndicatorAnalysisCategory3 from '@/components/indicator/IndicatorAnalysisCategory3.vue'
import DeathPatientDefinitionTable from '@/components/indicator/DeathPatientDefinitionTable.vue'
import { core18Api, type IndicatorConfigItem } from '@/api/core18'

// ======================== 状态 ========================
const route = useRoute()
const router = useRouter()

// 指标配置列表（从后端一次性加载）
const indicatorConfigs = ref<IndicatorConfigItem[]>([])
const isLoadingConfig = ref(false)

// 指标选择（draft / applied 双状态）
const draftIndicator = ref('')
const appliedIndicator = ref('')
const isSettingFromRoute = ref(false)

// 指标ID（从总览页跳转时传入，用于精确查找）
const draftIndicatorId = ref<number | null>(null)

// 从 URL 接收的时间筛选（用于传递给左侧面版子组件）
const routeTimeMode = ref<'monthly' | 'quarterly' | null>(null)
const routeTimeValue = ref<string | null>(null)

// 医院列表（后端返回格式为 [{value, label}]）
const hospitalList = ref<{ value: string; label: string }[]>([])
const hospitalOptions = computed(() => [
  { value: 'province', label: '全省' },
  ...hospitalList.value.map(h => ({ value: h.value, label: h.label }))
])
const draftHospital = ref('province')
const appliedHospital = ref('province')

// ======================== 数据加载 ========================
async function loadIndicatorConfigs(params?: { time_mode?: string; time_value?: string }) {
  isLoadingConfig.value = true
  try {
    const res = await core18Api.getIndicatorConfigs({
      hospital_code: appliedHospital.value === 'province' ? undefined : appliedHospital.value,
      time_mode: params?.time_mode || 'monthly',
      time_value: params?.time_value,
    })
    indicatorConfigs.value = res || []
  } catch (e) {
    console.error('加载指标配置失败:', e)
    indicatorConfigs.value = []
  } finally {
    isLoadingConfig.value = false
  }
}

async function loadHospitals() {
  try {
    const res = await core18Api.getHospitals()
    hospitalList.value = res || []
  } catch (e) {
    console.error('加载医院列表失败:', e)
  }
}

// ======================== 计算属性 ========================
// 指标下拉选项（用于选择器）
const indicatorOptions = computed(() =>
  indicatorConfigs.value.map(cfg => ({
    value: cfg.indicator_key,
    label: cfg.indicator_name,
  }))
)

// 当前指标配置（用于渲染子组件）
const currentConfig = computed(() =>
  indicatorConfigs.value.find(cfg => cfg.indicator_key === appliedIndicator.value) ?? null
)

// ======================== URL 参数处理 ========================
// 从 cascader-unified.json 构建指标 key -> label 映射（仅用于 URL 回退匹配）
import cascaderData from '@/data/cascader-unified.json'
type CascaderNode = { label: string; value: string; children?: CascaderNode[] }

function getFirstIndicatorKey(): string {
  for (const level1 of cascaderData as CascaderNode[]) {
    for (const level2 of level1.children ?? []) {
      for (const indicator of level2.children ?? []) {
        return indicator.value
      }
    }
  }
  return ''
}

function findIndicatorKeyByName(name: string): string | null {
  for (const level1 of cascaderData as CascaderNode[]) {
    for (const level2 of level1.children ?? []) {
      for (const indicator of level2.children ?? []) {
        if (indicator.label === name) return indicator.value
      }
    }
  }
  return null
}

// 指标ID -> indicator_key 精确查找（从总览页跳转场景）
function findIndicatorKeyById(id: number): string | null {
  const found = indicatorConfigs.value.find(cfg => cfg.indicator_id === id)
  return found ? found.indicator_key : null
}

// 从 route query 提取 indicatorId
function applyIndicatorIdFromRouteQuery(indicatorId: unknown) {
  if (typeof indicatorId !== 'string') {
    draftIndicatorId.value = null
    return
  }
  const parsed = parseInt(indicatorId, 10)
  draftIndicatorId.value = isNaN(parsed) ? null : parsed
}

function applySelection() {
  appliedIndicator.value = draftIndicator.value
  appliedHospital.value = draftHospital.value
  // 清除 indicatorId，避免后续 watch 将其误用于指标查找
  draftIndicatorId.value = null
  isSettingFromRoute.value = true
  router.replace({
    query: {
      ...route.query,
      indicator: draftIndicator.value,
      hospital: draftHospital.value,
    },
  })
  nextTick(() => { isSettingFromRoute.value = false })
}

function applyIndicatorFromRouteQuery(indicator: unknown) {
  // 优先使用 indicatorId 精确匹配（从总览页跳转场景）
  if (draftIndicatorId.value !== null) {
    const key = findIndicatorKeyById(draftIndicatorId.value)
    if (key) {
      draftIndicator.value = key
      appliedIndicator.value = key
      return
    }
  }
  // 降级：按名称或 key 匹配
  if (typeof indicator !== 'string' || !indicator.trim()) return
  const key = indicator.trim()
  // 优先从已加载的配置中查找（精确匹配 key）
  const found = indicatorConfigs.value.find(cfg => cfg.indicator_key === key)
  if (found) {
    draftIndicator.value = key
    appliedIndicator.value = key
    return
  }
  // 兜底：用 cascader 数据查找（按名称匹配 key）
  const fallbackKey = findIndicatorKeyByName(key)
  if (fallbackKey) {
    draftIndicator.value = fallbackKey
    appliedIndicator.value = fallbackKey
  } else {
    // 最终兜底：取第一个指标
    const firstKey = getFirstIndicatorKey()
    if (firstKey) {
      draftIndicator.value = firstKey
      appliedIndicator.value = firstKey
    }
  }
}

function applyHospitalFromRouteQuery(hospital: unknown) {
  if (isSettingFromRoute.value) return
  if (typeof hospital !== 'string' || !hospital.trim()) return
  const valid = hospitalOptions.value.find((item: { value: string; label: string }) => item.value === hospital.trim())
  if (valid) {
    appliedHospital.value = hospital.trim()
    draftHospital.value = hospital.trim()
  }
}

// ======================== 生命周期 ========================
onMounted(async () => {
  // 解析时间筛选参数（来自总览页跳转）
  const qTimeMode = route.query.timeMode as string | undefined
  const qTimeValue = route.query.timeValue as string | undefined
  if (qTimeMode && qTimeValue) {
    if (qTimeMode === 'monthly' || qTimeMode === 'quarterly') {
      routeTimeMode.value = qTimeMode
      routeTimeValue.value = qTimeValue
    }
  }

  // 解析 indicatorId（用于精确查找指标）
  applyIndicatorIdFromRouteQuery(route.query.indicatorId)

  // 先加载 configs（使用跳转传入的时间筛选参数）
  await loadIndicatorConfigs({
    time_mode: routeTimeMode.value ?? 'monthly',
    time_value: routeTimeValue.value ?? undefined,
  })

  // 加载医院列表
  await loadHospitals()

  // 指标处理：优先用 ID 查找，降级用名称查找
  applyIndicatorFromRouteQuery(route.query.indicator)
  applyHospitalFromRouteQuery(route.query.hospital)

  // 如果 URL 没有指定指标，设置默认值
  if (!appliedIndicator.value) {
    const firstKey = getFirstIndicatorKey()
    draftIndicator.value = firstKey
    appliedIndicator.value = firstKey
  }
})

watch(() => route.query.indicatorId, id => applyIndicatorIdFromRouteQuery(id))
watch(() => route.query.indicator, indicator => applyIndicatorFromRouteQuery(indicator))
watch(() => route.query.hospital, hospital => applyHospitalFromRouteQuery(hospital))
</script>
