<template>
  <div class="h-full flex flex-col bg-white">
    <!-- 二级Tab栏 -->
    <div class="bg-[#e8eef9] px-5 pt-3 border-b border-[#b8c9e8]/60 shrink-0">
      <div class="flex space-x-5 overflow-x-auto">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="pb-2.5 text-[13px] font-medium whitespace-nowrap transition-colors border-b-2"
          :class="activeTab === tab.id ? 'border-[#0A6EFD] text-[#0A6EFD]' : 'border-transparent text-[#596080] hover:text-[#1F264D]'"
        >
          {{ tab.name }}
        </button>
      </div>
    </div>

    <!-- 分类总览视图 -->
    <div v-if="activeTab === 'overview'" class="flex-1 p-5 overflow-y-auto animate-fade-in">
      <h2 class="text-[14px] font-bold text-[#1F264D] flex items-center">
        <Activity class="w-4 h-4 mr-2 text-[#0A6EFD]" />
        人员要素 — 监管规则总览
        <span class="ml-auto flex items-center gap-2">
          <!-- 时间筛选 -->
          <div class="flex items-center gap-1 border border-[#b8c9e8]/60 rounded-[2px] px-2 bg-white text-[12px] h-[34px]">
            <button
              v-for="mode in TIME_MODE_OPTIONS"
              :key="mode.value"
              type="button"
              class="rounded px-2 text-[11px] transition-colors leading-[22px]"
              :class="timeMode === mode.value
                ? 'bg-[#0A6EFD] text-white font-medium'
                : 'text-[#596080] hover:bg-[#e8eef9]'"
              @click="timeMode = mode.value; hospitalVersion++"
            >{{ mode.label }}</button>
            <!-- 月份选择 -->
            <template v-if="timeMode === 'monthly'">
              <select
                v-model="selectedMonthYear"
                class="border-none bg-transparent text-[11px] text-[#1F264D] focus:outline-none cursor-pointer"
              >
                <option v-for="y in monthYearOptions" :key="y" :value="y">{{ y }}</option>
              </select>
              <span class="text-[#596080]">年</span>
              <select
                v-model="selectedMonthNum"
                class="border-none bg-transparent text-[11px] text-[#1F264D] focus:outline-none cursor-pointer"
              >
                <option v-for="m in MONTH_OPTIONS" :key="m.value" :value="m.value">{{ m.label }}</option>
              </select>
            </template>
            <!-- 季度选择 -->
            <template v-else-if="timeMode === 'quarterly'">
              <select
                v-model="selectedQuarterYear"
                class="border-none bg-transparent text-[11px] text-[#1F264D] focus:outline-none cursor-pointer"
              >
                <option v-for="y in quarterYearOptions" :key="y" :value="y">{{ y }}</option>
              </select>
              <span class="text-[#596080]">年</span>
              <select
                v-model="selectedQuarterNum"
                class="border-none bg-transparent text-[11px] text-[#1F264D] focus:outline-none cursor-pointer"
              >
                <option v-for="q in QUARTER_OPTIONS" :key="q.value" :value="q.value">{{ q.label }}</option>
              </select>
            </template>
          </div>
          <!-- 医院筛选 -->
          <div class="relative hospital-filter">
            <div class="flex items-center gap-1.5 border border-[#b8c9e8]/60 rounded-[2px] px-2.5 py-1.5 cursor-pointer select-none hover:border-[#0A6EFD]/50 transition-colors bg-white text-[12px]"
              @click.stop="showHospitalFilter = !showHospitalFilter"
            >
              <MapPin class="w-3.5 h-3.5 text-[#0A6EFD] shrink-0" />
              <span class="font-medium text-[#1F264D]">{{ currentHospital.name }}</span>
              <ChevronDown class="w-3.5 h-3.5 text-[#596080] shrink-0 transition-transform" :class="showHospitalFilter ? 'rotate-180' : ''" />
            </div>
            <div v-if="showHospitalFilter" class="absolute right-0 top-full mt-1 w-[200px] bg-white border border-[#b8c9e8]/60 rounded-[2px] shadow-lg z-50 max-h-[280px] overflow-y-auto">
              <div
                v-for="h in hospitalOptions"
                :key="h.id"
                class="flex items-center justify-between px-3 py-2 text-[12px] cursor-pointer hover:bg-[#e8eef9] transition-colors"
                :class="currentHospitalId === h.id ? 'bg-[#e8eef9] text-[#0A6EFD] font-medium' : 'text-[#1F264D]'"
                @click="selectHospital(h)"
              >
                <span>{{ h.name }}</span>
                <span v-if="h.level" class="text-[10px] text-[#B8BCCC] shrink-0 ml-2">{{ h.level }}</span>
              </div>
            </div>
          </div>
        </span>
      </h2>
      <div class="mb-5 bg-blue-50 border border-blue-200 rounded-[2px] p-3.5 text-[13px] text-blue-800">
        <p class="font-medium mb-0.5 text-[13px]">规则说明</p>
        <p class="text-blue-600 text-[12px]">人员要素审核范围：住院。对医师职称、执业记录、多点执业等关键信息进行智能监测与预警。</p>
      </div>
      <div class="grid grid-cols-3 gap-4">
        <div
          v-for="rule in rules"
          :key="rule.id"
          @click="activeTab = rule.id"
          class="bg-white rounded-[2px] p-4 border border-[#b8c9e8]/60 shadow-sm hover:shadow-md hover:border-[#0A6EFD]/50 transition-all cursor-pointer group flex flex-col"
        >
          <div class="flex justify-between items-start mb-2.5">
            <div :class="['p-1.5 rounded-[2px]', rule.mode === 'alert' ? 'bg-red-50 text-red-500' : 'bg-emerald-50 text-emerald-500']">
              <ShieldAlert v-if="rule.mode === 'alert'" class="w-4 h-4" />
              <Activity v-else class="w-4 h-4" />
            </div>
          </div>
          <h3 class="font-bold text-[#1F264D] text-[13px] mb-1.5 group-hover:text-[#0A6EFD] transition-colors">{{ rule.name }}</h3>
          <p class="text-[#596080] text-[12px] flex-1 mb-3 leading-relaxed">{{ rule.desc }}</p>
          <div class="border-t border-[#b8c9e8]/40 pt-2.5">
            <div class="text-[11px] text-[#B8BCCC] mb-1">审核范围：<span class="text-[#596080] font-medium">{{ rule.scope }}</span></div>
            <div class="text-[11px] text-[#B8BCCC] mb-2">阈值：<span class="text-[#596080] font-medium">{{ rule.threshold }}</span></div>
            <div class="flex items-center justify-between">
              <span :class="['text-[11px] font-medium px-2 py-0.5 rounded-full border', rule.mode === 'alert' ? 'border-red-200 text-red-600 bg-red-50' : 'border-emerald-200 text-emerald-600 bg-emerald-50']">
                {{ rule.mode === 'alert' ? '预警模式' : '常规监测' }}
              </span>
              <span class="text-[11px] text-red-600 font-bold">{{ getRuleCount(rule) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 具体规则明细视图 -->
    <template v-else>
      <div class="p-4 shrink-0">
        <div class="border rounded-[2px] p-2.5 flex items-start bg-blue-50/50 border-blue-200">
          <Info class="w-3.5 h-3.5 mr-2 shrink-0 mt-0.5 text-[#0A6EFD]" />
          <div>
            <h4 class="text-[13px] font-medium text-blue-800">{{ currentRule?.name }}</h4>
            <p class="text-[11px] mt-0.5 text-blue-600">{{ currentRule?.logic }}</p>
          </div>
        </div>
      </div>

      <div class="flex-1 px-4 pb-4 overflow-hidden flex flex-col">
        <div class="bg-white rounded-[2px] border border-[#b8c9e8]/60 flex-1 overflow-hidden flex flex-col shadow-sm">
          <div class="p-3.5 border-b border-[#b8c9e8]/40 flex justify-between items-center shrink-0">
            <h3 class="font-semibold text-[#1F264D] flex items-center text-[13px]">
              违规预警数据列表
              <span class="ml-2 bg-red-100 text-red-600 py-0.5 px-2 rounded-full text-[11px] font-bold">{{ tableData.length }}</span>
            </h3>
            <div class="flex items-center gap-2">
              <div class="flex items-center gap-1.5 border border-[#b8c9e8]/60 rounded-[2px] px-2.5 py-1.5 bg-white">
                <Calendar class="w-3.5 h-3.5 text-[#596080] shrink-0" />
                <input
                  type="date"
                  v-model="startDate"
                  class="text-[12px] text-[#1F264D] focus:outline-none bg-transparent w-[130px]"
                />
                <span class="text-[11px] text-[#B8BCCC]">至</span>
                <input
                  type="date"
                  v-model="endDate"
                  class="text-[12px] text-[#1F264D] focus:outline-none bg-transparent w-[130px]"
                />
                <button
                  v-if="startDate || endDate"
                  @click="startDate = ''; endDate = ''"
                  class="ml-0.5 text-[#B8BCCC] hover:text-[#596080] transition-colors"
                >
                  <X class="w-3 h-3" />
                </button>
              </div>
              <div class="relative">
                <Search class="w-3.5 h-3.5 absolute left-2.5 top-1/2 transform -translate-y-1/2 text-[#B8BCCC]" />
                <input type="text" placeholder="搜索..." class="pl-8 pr-3 py-1.5 text-[12px] border border-[#b8c9e8]/60 rounded-[2px] focus:outline-none focus:border-[#0A6EFD] w-52 bg-white" />
              </div>
              <button @click="handleExport" class="px-3 py-1.5 text-[12px] bg-[#0A6EFD] text-white rounded-[2px] hover:bg-[#0a5fe0] transition-colors flex items-center gap-1">
                <Download class="w-3.5 h-3.5" /> 导出
              </button>
            </div>
          </div>

          <div class="flex-1 overflow-auto">
            <table v-if="tableData.length > 0" class="w-full text-left border-collapse">
              <thead class="bg-[#e8eef9] sticky top-0 z-10">
                <tr>
                  <th v-for="col in realTableColumns" :key="col" class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">{{ col }}</th>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide text-right">操作</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#b8c9e8]/30">
                <tr v-for="(row, idx) in tableData" :key="row.id || idx" class="hover:bg-[#e8eef9]/40 transition-colors group">
                  <td v-for="col in realTableColumns" :key="col" class="px-3.5 py-2.5 text-[12px] text-[#596080] max-w-xs truncate" :title="String(row[col] ?? '-')">{{ row[col] ?? '-' }}</td>
                  <td class="px-3.5 py-2.5 text-[12px] text-right">
                    <button @click="openDrawer(row)" class="text-[#0A6EFD] hover:text-[#1F264D] font-medium flex items-center justify-end w-full text-[11px]">
                      <Eye class="w-3 h-3 mr-1" /> 查看详情
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-else class="flex flex-col items-center justify-center py-16 text-[#9CA3AF]">
              <Activity class="w-12 h-12 mb-3 opacity-30" />
              <p class="text-[13px]">暂无预警数据</p>
              <p class="text-[11px] mt-1">请在「指标执行」页面执行相应指标</p>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 详情抽屉 -->
    <div v-if="drawerData" class="fixed inset-0 z-50 flex justify-end bg-gray-900/50 backdrop-blur-sm">
      <div class="w-[580px] bg-white h-full shadow-2xl flex flex-col animate-slide-in border-l border-[#b8c9e8]/60">
        <div class="px-5 py-3.5 border-b border-[#b8c9e8]/60 flex justify-between items-center bg-[#e8eef9]">
          <h2 class="text-[14px] font-bold text-[#1F264D] flex items-center">
            <ShieldAlert class="w-4 h-4 text-red-500 mr-2" />
            预警证据链详情
          </h2>
          <button @click="drawerData = null" class="p-1.5 hover:bg-[#b8c9e8]/30 rounded-full text-[#596080] transition-colors">
            <X class="w-4 h-4" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-5 space-y-5">
          <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
            <div class="flex items-center justify-between mb-3">
              <h3 class="font-bold text-[#1F264D] text-[13px]">基本信息</h3>
              <span class="px-2 py-0.5 rounded-full text-[11px] font-medium border bg-red-50 text-red-600 border-red-200">触发预警</span>
            </div>
            <div class="grid grid-cols-2 gap-3 text-[12px]">
              <div><span class="text-[#596080] block mb-0.5">触发时间</span><span class="font-medium text-[#1F264D]">{{ drawerData.time || drawerData.预警时间 || '-' }}</span></div>
              <div><span class="text-[#596080] block mb-0.5">流水号</span><span class="font-medium text-[#1F264D] font-mono">{{ drawerData.id || '-' }}</span></div>
              <div><span class="text-[#596080] block mb-0.5">涉事机构</span><span class="font-medium text-[#1F264D]">{{ drawerData.org || drawerData.涉事机构 || drawerData.MDC_ORG_NM || '-' }}</span></div>
              <div><span class="text-[#596080] block mb-0.5">涉事医师</span><span class="font-medium text-[#1F264D]">{{ drawerData.doctor || drawerData.涉事医师 || '-' }}</span></div>
              <div><span class="text-[#596080] block mb-0.5">医师职称</span><span class="font-medium text-[#1F264D]">{{ drawerData.title || drawerData.职称 || '-' }}</span></div>
              <div><span class="text-[#596080] block mb-0.5">患者信息</span><span class="font-medium text-[#1F264D]">{{ drawerData.patient || drawerData.患者信息 || '-' }}</span></div>
            </div>
          </div>

          <div v-if="drawerData.violationType || drawerData.detail" class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
            <h3 class="font-bold text-[#1F264D] text-[13px] mb-2.5">违规判定依据</h3>
            <div class="bg-red-50 border border-red-200 rounded-[2px] p-3 text-[12px] text-red-800">
              <p v-if="drawerData.violationType || drawerData.detail" class="font-medium mb-1">违规类型：{{ drawerData.violationType || drawerData.detail || '-' }}</p>
              <p v-if="drawerData.detail" class="text-red-700">{{ drawerData.detail }}</p>
            </div>
          </div>

          <div v-if="drawerData.evidence">
            <h3 class="font-bold text-[#1F264D] text-[13px] mb-2.5 flex items-center">
              <Activity class="w-3.5 h-3.5 mr-1.5 text-[#0A6EFD]" />
              系统底层抓取证据
            </h3>
            <div class="bg-[#f8faff] border border-[#b8c9e8]/60 rounded-[2px] p-4">
              <p class="text-[11px] text-[#B8BCCC] mb-1.5 font-mono">=== 关联底层数据快照 ===</p>
              <div class="bg-[#f0f4ff] p-2.5 rounded-[2px] text-[11px] font-mono text-[#596080] whitespace-pre-line leading-relaxed">{{ drawerData.evidence }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Activity,
  Calendar,
  ChevronDown,
  Download,
  Eye,
  Info,
  MapPin,
  Search,
  ShieldAlert,
  X,
} from 'lucide-vue-next'
import { exportToExcel } from '../../utils/exportExcel'
import { useFourFactorExecutions, TIME_MODE_OPTIONS, MONTH_OPTIONS, QUARTER_OPTIONS } from '../../composables/useFourFactorExecutions'
import type { TimeMode } from '../../composables/useFourFactorExecutions'

const route = useRoute()
const router = useRouter()
const { fetchExecutions, fetchHospitals, hospitalList, getPreviewDataByHospital, getDenominatorPreviewDataByHospital, getCountByHospital, formatCountInMetric, executionRecords } = useFourFactorExecutions()

const showHospitalFilter = ref(false)
const startDate = ref('')
const endDate = ref('')
const currentHospitalId = ref('all')
const hospitalVersion = ref(0)

const timeMode = ref<TimeMode>('immediate')
const selectedMonthYear = ref(new Date().getFullYear().toString())
const selectedMonthNum = ref('01')
const selectedQuarterYear = ref(new Date().getFullYear().toString())
const selectedQuarterNum = ref('1')

const currentTimeValue = computed(() => {
  if (timeMode.value === 'monthly') {
    return `${selectedMonthYear.value}-${selectedMonthNum.value}`
  }
  if (timeMode.value === 'quarterly') {
    return `${selectedQuarterYear.value}-Q${selectedQuarterNum.value}`
  }
  return undefined
})

const monthYearOptions = computed(() => {
  const cur = new Date().getFullYear()
  const start = cur - 5
  return Array.from({ length: cur + 2 - start }, (_, i) => start + i)
})

const quarterYearOptions = computed(() => {
  const cur = new Date().getFullYear()
  const start = cur - 5
  return Array.from({ length: cur + 2 - start }, (_, i) => start + i)
})

const ruleCountCache = ref<Record<string, number>>({})
const rulePreviewCache = ref<Record<string, { columns: string[]; rows: any[] }>>({})
const countLoading = ref(false)

async function loadHospitalData() {
  if (currentHospitalId.value === 'all') {
    ruleCountCache.value = {}
    rulePreviewCache.value = {}
    return
  }
  countLoading.value = true
  try {
    const tm = timeMode.value
    const tv = currentTimeValue.value
    const promises = rules.map(async (rule) => {
      const key = `${rule.indicator_id}-${currentHospitalId.value}-${tm}-${tv || 'all'}`
      const [count, preview] = await Promise.all([
        getCountByHospital(rule.indicator_id, currentHospitalId.value, tm, tv),
        getPreviewDataByHospital(rule.indicator_id, currentHospitalId.value, tm, tv),
      ])
      ruleCountCache.value[key] = count
      rulePreviewCache.value[key] = preview || { columns: [], rows: [] }
    })
    await Promise.all(promises)
  } finally {
    countLoading.value = false
  }
}

export interface Hospital {
  id: string
  name: string
  level?: string
}

const hospitalOptions = computed<Hospital[]>(() => [
  { id: 'all', name: '全省', level: '' },
  ...hospitalList.value.map(h => ({ id: h.MDC_ORG_CD, name: h.MDC_ORG_NM })),
])

const currentHospital = computed(() =>
  hospitalOptions.value.find(h => h.id === currentHospitalId.value) || hospitalOptions.value[0]
)

function selectHospital(h: Hospital) {
  currentHospitalId.value = h.id
  hospitalVersion.value++
  showHospitalFilter.value = false
  loadHospitalData()
}

function handleClickOutside(e: MouseEvent) {
  if (!(e.target as HTMLElement).closest('.hospital-filter')) {
    showHospitalFilter.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  fetchExecutions()
  fetchHospitals()
})
onUnmounted(() => document.removeEventListener('click', handleClickOutside))

const rules = [
  {
    id: 'r1', indicator_id: 1, mode: 'alert', name: '越权开具抗生素',
    desc: '医师职称与限制级、特殊级抗生素匹配异常，系统自动报警。',
    scope: '住院', threshold: '无',
    logic: '在系统中维护医师职称，设定"职称-限制级、特殊级抗生素"匹配规则，医生开了与自己职称不符的限制级或特殊级抗生素时自动报警。'
  },
  {
    id: 'r2', indicator_id: 2, mode: 'alert', name: '时空轨迹异常',
    desc: '同一医师短时间内在不同医疗机构中出现诊疗记录，系统自动报警。',
    scope: '住院', threshold: '30分钟内',
    logic: '在系统中维护医师操作记录，设定"同一医师短时间内在不同医疗机构中出现诊疗记录"匹配规则，某个时间段内医生在不同机构内开了医嘱信息时自动报警。'
  },
  {
    id: 'r3', indicator_id: 3, mode: 'alert', name: '多点执业冲突',
    desc: '对主执业机构在公立医院的医师发生民营医院多点执业或诊疗记录进行监测。',
    scope: '住院', threshold: '无',
    logic: '在系统中维护医师多点执业记录，设定"对主执业机构在公立医院的发生民营医院多点执业或诊疗记录"匹配规则，同一患者由同一医生在公立和民营医院都开了医嘱时自动报警。'
  },
]

const tabs = [{ id: 'overview', name: '分类总览' }, ...rules]
const activeTab = ref(route.query.tab as string || 'overview')
const drawerData = ref<any>(null)
const currentRule = computed(() => rules.find(r => r.id === activeTab.value))

watch(activeTab, (val) => {
  router.replace({ query: val === 'overview' ? {} : { tab: val } })
})

const isAll = computed(() => currentHospitalId.value === 'all')

function findExecutionByTime(indicatorId: number): any | null {
  const tm = timeMode.value
  const tv = currentTimeValue.value
  return executionRecords.value
    .filter(r => r.indicator_id === indicatorId && r.status === 'success')
    .filter(r => {
      if (tm === 'immediate') return true
      if (r.run_mode !== tm) return false
      if (tv && r.time_value !== tv) return false
      return true
    })
    .sort((a, b) => new Date(b.execution_time).getTime() - new Date(a.execution_time).getTime())[0] || null
}

function getRuleCount(rule: any): string {
  if (!rule) return '-'
  void hospitalVersion.value
  if (currentHospitalId.value === 'all') {
    void countLoading.value
    void ruleCountCache.value
    const rec = findExecutionByTime(rule.indicator_id)
    if (!rec) return '-'
    return `${rec.numerator_count ?? 0} 条`
  }
  const tm = timeMode.value
  const tv = currentTimeValue.value
  const key = `${rule.indicator_id}-${currentHospitalId.value}-${tm}-${tv || 'all'}`
  const cnt = ruleCountCache.value[key]
  if (cnt === undefined || cnt === -1) return '-'
  return `${cnt} 条`
}

const currentIndicatorId = computed(() => {
  const rule = currentRule.value
  return rule?.indicator_id ?? null
})

const columnOrder = computed(() => {
  void hospitalVersion.value
  const indId = currentIndicatorId.value
  if (!indId) return []

  const rec = findExecutionByTime(indId)
  if (rec?.preview_data?.columns?.length) {
    return rec.preview_data.columns
  }
  if (rec?.preview_data?.rows?.length) {
    return Object.keys(rec.preview_data.rows[0])
  }

  if (currentHospitalId.value !== 'all') {
    const tm = timeMode.value
    const tv = currentTimeValue.value
    const key = `${indId}-${currentHospitalId.value}-${tm}-${tv || 'all'}`
    const preview = rulePreviewCache.value[key]
    if (preview?.columns?.length) return preview.columns
    if (preview?.rows?.length) return Object.keys(preview.rows[0])
  }

  return []
})

const realTableColumns = computed(() => columnOrder.value)

const realTableData = computed(() => {
  void hospitalVersion.value
  const indId = currentIndicatorId.value
  if (!indId) return []

  const cols = columnOrder.value
  if (!cols.length) return []

  if (currentHospitalId.value === 'all') {
    const rec = findExecutionByTime(indId)
    if (!rec?.preview_data?.rows?.length) return []
    return rec.preview_data.rows.map((row: any, idx: number) => {
      const item: any = { id: String(idx + 1), _raw: row }
      for (const col of cols) {
        item[col] = row[col]
      }
      return item
    })
  }

  const tm = timeMode.value
  const tv = currentTimeValue.value
  const key = `${indId}-${currentHospitalId.value}-${tm}-${tv || 'all'}`
  const preview = rulePreviewCache.value[key]
  if (!preview || !preview.rows?.length) return []
  return preview.rows.map((row: any, idx: number) => {
    const item: any = { id: String(idx + 1), _raw: row }
    for (const col of cols) {
      item[col] = row[col]
    }
    return item
  })
})

const tableData = computed(() => realTableData.value)

const openDrawer = (row: any) => { drawerData.value = row }

const personnelColumns = [
  { field: 'time', header: '预警时间' },
  { field: 'org', header: '涉事机构' },
  { field: 'doctor', header: '涉事医师' },
  { field: 'title', header: '职称' },
  { field: 'patient', header: '患者信息' },
  { field: 'detail', header: '违规详情' },
]

function handleExport() {
  const rule = currentRule.value
  const name = rule ? `${rule.id}-${rule.name}` : '人员要素总览'
  exportToExcel(tableData.value, personnelColumns, `人员要素_${name}`)
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.animate-slide-in { animation: slideIn 0.3s ease-out; }
@keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }
</style>
