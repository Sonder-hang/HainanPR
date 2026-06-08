<template>
  <div class="h-full flex flex-col bg-white">
    <!-- 二级Tab栏 -->
    <div class="bg-[#e8eef9] px-5 pt-3 border-b border-[#b8c9e8]/60 shrink-0">
      <div class="flex space-x-4 overflow-x-auto">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="pb-2.5 text-[12px] font-medium whitespace-nowrap transition-colors border-b-2"
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
        设备要素 — 监管规则总览
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
        <p class="text-blue-600 text-[12px]">设备要素审核范围：手术患者。对手术分级、医生授权、设备配置、检验阳性率等关键指标进行智能监测与预警。</p>
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
            <div class="text-[11px] text-[#B8BCCC] mb-2">监测维度：<span class="text-[#596080] font-medium">{{ rule.threshold || '-' }}</span></div>
            <div class="flex items-center justify-between">
              <span :class="['text-[11px] font-medium px-2 py-0.5 rounded-full border', rule.mode === 'alert' ? 'border-red-200 text-red-600 bg-red-50' : 'border-emerald-200 text-emerald-600 bg-emerald-50']">
                {{ rule.mode === 'alert' ? '预警模式' : '常规监测' }}
              </span>
              <span class="text-[11px] font-bold" :class="rule.mode === 'alert' ? 'text-red-600' : 'text-emerald-600'">
                {{ getRuleCount(rule) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 具体规则明细视图 -->
    <template v-else>
      <div class="p-4 shrink-0">
        <div :class="['border rounded-[2px] p-2.5 flex items-start', currentRule?.mode === 'alert' ? 'bg-blue-50/50 border-blue-200' : 'bg-emerald-50 border-emerald-200']">
          <Info :class="['w-3.5 h-3.5 mr-2 shrink-0 mt-0.5', currentRule?.mode === 'alert' ? 'text-[#0A6EFD]' : 'text-emerald-500']" />
          <div>
            <h4 :class="['text-[13px] font-medium', currentRule?.mode === 'alert' ? 'text-blue-800' : 'text-emerald-800']">{{ currentRule?.name }}</h4>
            <p :class="['text-[11px] mt-0.5', currentRule?.mode === 'alert' ? 'text-blue-600' : 'text-emerald-600']">{{ currentRule?.logic }}</p>
          </div>
        </div>
      </div>

      <div class="flex-1 px-4 pb-4 overflow-hidden flex flex-col">
        <div class="bg-white rounded-[2px] border border-[#b8c9e8]/60 flex-1 overflow-hidden flex flex-col shadow-sm">
          <div class="p-3.5 border-b border-[#b8c9e8]/40 flex justify-between items-center shrink-0">
            <h3 class="font-semibold text-[#1F264D] flex items-center text-[13px]">
              {{ currentRule?.mode === 'alert' ? '违规预警数据列表' : '监测指标统计报表' }}
              <span v-if="currentRule?.mode === 'alert'" class="ml-2 bg-red-100 text-red-600 py-0.5 px-2 rounded-full text-[11px] font-bold">{{ tableData.length }}</span>
            </h3>
            <div class="flex items-center gap-2">
              <div class="relative">
                <Search class="w-3.5 h-3.5 absolute left-2.5 top-1/2 transform -translate-y-1/2 text-[#B8BCCC]" />
                <input type="text" placeholder="搜索..." class="pl-8 pr-3 py-1.5 text-[12px] border border-[#b8c9e8]/60 rounded-[2px] focus:outline-none focus:border-[#0A6EFD] w-52 bg-white" />
              </div>
              <button @click="handleExport" class="px-3 py-1.5 text-[12px] bg-[#0A6EFD] text-white rounded-[2px] hover:bg-[#0a5fe0] transition-colors flex items-center gap-1">
                <Download class="w-3.5 h-3.5" /> 导出
              </button>
            </div>
          </div>

          <div v-if="currentRule?.mode === 'alert'" class="flex-1 overflow-auto">
            <table v-if="realTableData.length > 0" class="w-full text-left border-collapse">
              <thead class="bg-[#e8eef9] sticky top-0 z-10">
                <tr>
                  <th v-for="col in realTableColumns" :key="String(col)" class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">{{ col }}</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#b8c9e8]/30">
                <tr v-for="row in tableData" :key="row.id" class="hover:bg-[#e8eef9]/40 transition-colors">
                  <td v-for="col in realTableColumns" :key="String(col)" class="px-3.5 py-2.5 text-[12px] text-[#596080] max-w-xs truncate" :title="String(row[col] ?? '-')">{{ row[col] ?? '-' }}</td>
                </tr>
              </tbody>
            </table>
            <div v-else class="flex flex-col items-center justify-center py-16 text-[#9CA3AF]">
              <Activity class="w-12 h-12 mb-3 opacity-30" />
              <p class="text-[13px]">暂无预警数据</p>
              <p class="text-[11px] mt-1">请在「指标执行」页面执行相应指标</p>
            </div>
          </div>

          <div v-else class="flex-1 overflow-auto">
            <table v-if="realTableData.length > 0" class="w-full text-left border-collapse">
              <thead class="bg-emerald-50/60 sticky top-0 z-10 border-b border-emerald-100">
                <tr>
                  <th v-for="col in realTableColumns" :key="String(col)" class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">{{ col }}</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#b8c9e8]/30">
                <tr v-for="row in tableData" :key="row.id" class="hover:bg-emerald-50/40 transition-colors">
                  <td v-for="col in realTableColumns" :key="String(col)" class="px-3.5 py-2.5 text-[12px] text-[#596080]">{{ row[col] ?? '-' }}</td>
                </tr>
              </tbody>
            </table>
            <div v-else class="flex flex-col items-center justify-center py-16 text-[#9CA3AF]">
              <Activity class="w-12 h-12 mb-3 opacity-30" />
              <p class="text-[13px]">暂无监测数据</p>
              <p class="text-[11px] mt-1">请在「指标执行」页面执行相应指标</p>
            </div>
          </div>

          <div v-if="getDetailTotalCount() > 0" class="px-3 py-2 border-t border-[#b8c9e8]/40 bg-[#f8faff] flex items-center justify-between shrink-0">
            <div class="text-[12px] text-[#596080]">第 {{ detailCurrentPage }} 页，共 {{ detailTotalPages }} 页</div>
            <div class="flex items-center gap-1">
              <button @click="prevDetailPage" :disabled="detailCurrentPage === 1" class="p-1.5 text-[#596080] hover:text-[#0A6EFD] disabled:text-[#B8BCCC] disabled:cursor-not-allowed">
                <ChevronLeft class="w-3.5 h-3.5" />
              </button>
              <button
                v-for="page in detailVisiblePages"
                :key="page"
                @click="goToDetailPage(page)"
                class="w-7 h-7 text-[12px] rounded-[2px] transition-colors"
                :class="page === detailCurrentPage ? 'bg-[#0A6EFD] text-white' : 'text-[#596080] hover:bg-[#e8eef9]'"
              >{{ page }}</button>
              <button @click="nextDetailPage" :disabled="detailCurrentPage === detailTotalPages" class="p-1.5 text-[#596080] hover:text-[#0A6EFD] disabled:text-[#B8BCCC] disabled:cursor-not-allowed">
                <ChevronRight class="w-3.5 h-3.5" />
              </button>
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
              <div><span class="text-[#596080] block mb-0.5">预警时间</span><span class="font-medium text-[#1F264D]">{{ drawerData.time }}</span></div>
              <div><span class="text-[#596080] block mb-0.5">涉事机构</span><span class="font-medium text-[#1F264D]">{{ drawerData.org }}</span></div>
              <div><span class="text-[#596080] block mb-0.5">涉事人员</span><span class="font-medium text-[#1F264D]">{{ drawerData.person }}</span></div>
              <div><span class="text-[#596080] block mb-0.5">违规类型</span><span class="font-medium text-[#1F264D]">{{ drawerData.violationType || currentRule?.name }}</span></div>
            </div>
          </div>
          <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
            <h3 class="font-bold text-[#1F264D] text-[13px] mb-2.5">违规判定依据</h3>
            <div class="bg-red-50 border border-red-200 rounded-[2px] p-3 text-[12px] text-red-800">
              <p class="font-medium mb-1">违规类型：{{ drawerData.violationType || currentRule?.name }}</p>
              <p class="text-red-700">{{ drawerData.detail }}</p>
            </div>
          </div>
          <div>
            <h3 class="font-bold text-[#1F264D] text-[13px] mb-2.5 flex items-center">
              <Activity class="w-3.5 h-3.5 mr-1.5 text-[#0A6EFD]" />
              系统底层抓取证据
            </h3>
            <div class="bg-[#f8faff] border border-[#b8c9e8]/60 rounded-[2px] p-4">
              <p class="text-[11px] text-[#B8BCCC] mb-1.5 font-mono">=== 关联底层数据快照 ===</p>
              <div class="bg-[#f0f4ff] p-2.5 rounded-[2px] text-[11px] font-mono text-[#596080] whitespace-pre-line leading-relaxed">{{ drawerData.evidence }}</div>
            </div>
          </div>        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { Activity, ChevronDown, ChevronLeft, ChevronRight, Clock, Download, Eye, Info, MapPin, Monitor, Search, ShieldAlert, X } from 'lucide-vue-next'
import { exportToExcel } from '../../utils/exportExcel'
import { useFourFactorExecutions, TIME_MODE_OPTIONS, MONTH_OPTIONS, QUARTER_OPTIONS } from '../../composables/useFourFactorExecutions'
import { useDetailPagination } from '../../composables/useDetailPagination'
import type { TimeMode } from '../../composables/useFourFactorExecutions'

export interface Hospital {
  id: string
  name: string
  level?: string
}

const showHospitalFilter = ref(false)
const DETAIL_PAGE_SIZE = 10
const { fetchExecutions, fetchHospitals, hospitalList, getPreviewDataByHospital, getDenominatorPreviewDataByHospital, getCountByHospital, getDenominatorCountByHospital, formatCountInMetric, executionRecords } = useFourFactorExecutions()

const currentHospitalId = ref('all')
const hospitalVersion = ref(0)

// 时间筛选状态
const timeMode = ref<TimeMode>('immediate')
const selectedMonthYear = ref(new Date().getFullYear().toString())
const selectedMonthNum = ref('01')
const selectedQuarterYear = ref(new Date().getFullYear().toString())
const selectedQuarterNum = ref('1')

// 计算当前时间值
const currentTimeValue = computed(() => {
  if (timeMode.value === 'monthly') {
    return `${selectedMonthYear.value}-${selectedMonthNum.value}`
  }
  if (timeMode.value === 'quarterly') {
    return `${selectedQuarterYear.value}-Q${selectedQuarterNum.value}`
  }
  return undefined
})

// 月份年份选项（从5年前到当前年份+1年）
const monthYearOptions = computed(() => {
  const now = new Date()
  const cur = now.getFullYear()
  const start = cur - 5
  const years: number[] = []
  for (let y = start; y <= cur + 1; y++) {
    years.push(y)
  }
  return years
})

// 季度年份选项（从5年前到当前年份+1年）
const quarterYearOptions = computed(() => {
  const now = new Date()
  const cur = now.getFullYear()
  const start = cur - 5
  const years: number[] = []
  for (let y = start; y <= cur + 1; y++) {
    years.push(y)
  }
  return years
})

const hospitalOptions = computed<Hospital[]>(() => [
  { id: 'all', name: '全省', level: '' },
  ...hospitalList.value.map(h => ({ id: h.MDC_ORG_CD, name: h.MDC_ORG_NM })),
])

const currentHospital = computed(() =>
  hospitalOptions.value.find(h => h.id === currentHospitalId.value) || hospitalOptions.value[0]
)

// 缓存：key = `${rule.indicator_id}-${hospitalId}`, value = count
const ruleCountCache = ref<Record<string, number>>({})
const ruleDenomCountCache = ref<Record<string, number>>({})
const rulePreviewCache = ref<Record<string, { columns: string[]; rows: any[] }>>({})
const ruleDenomPreviewCache = ref<Record<string, { columns: string[]; rows: any[] }>>({})
const countLoading = ref(false)

async function loadHospitalData() {
  if (currentHospitalId.value === 'all') {
    ruleCountCache.value = {}
    ruleDenomCountCache.value = {}
    rulePreviewCache.value = {}
    ruleDenomPreviewCache.value = {}
    return
  }
  countLoading.value = true
  try {
    const tm = timeMode.value
    const tv = currentTimeValue.value
    const promises = rules.map(async (rule) => {
      const key = `${rule.indicator_id}-${currentHospitalId.value}-${tm}-${tv || 'all'}`
      const [count, denomCount, preview, denomPreview] = await Promise.all([
        getCountByHospital(rule.indicator_id, currentHospitalId.value, tm, tv),
        getDenominatorCountByHospital(rule.indicator_id, currentHospitalId.value, tm, tv),
        getPreviewDataByHospital(rule.indicator_id, currentHospitalId.value, tm, tv),
        getDenominatorPreviewDataByHospital(rule.indicator_id, currentHospitalId.value, tm, tv),
      ])
      ruleCountCache.value[key] = count
      ruleDenomCountCache.value[key] = denomCount
      rulePreviewCache.value[key] = preview || { columns: [], rows: [] }
      ruleDenomPreviewCache.value[key] = denomPreview || { columns: [], rows: [] }
    })
    await Promise.all(promises)
  } finally {
    countLoading.value = false
  }
}

function selectHospital(h: Hospital) {
  currentHospitalId.value = h.id
  hospitalVersion.value++
  showHospitalFilter.value = false
  void loadHospitalData()
}

watch(currentHospitalId, () => {
  hospitalVersion.value++
  if (currentHospitalId.value !== 'all') {
    void loadHospitalData()
  }
})

watch([timeMode, currentTimeValue], () => {
  hospitalVersion.value++
  if (currentHospitalId.value !== 'all') {
    void loadHospitalData()
  }
})

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

// indicator_id 对应 indicator.id（规则 ID 去掉 'r'）
const rules = [
  { id: 'r15', indicator_id: 15, mode: 'alert', name: '人机资质不符', desc: '手术分级、医生授权与设备配置匹配异常，系统自动报警。', scope: '手术患者', threshold: '手术分级-医生授权-设备配置', logic: '建立"手术分级-医生授权-设备配置"匹配规则，以手术分级为基准，医生授权对应资质等级，设备配置满足技术需求时自动报警。' },
  { id: 'r16', indicator_id: 16, mode: 'alert', name: '设备账实不符', desc: '设备基本信息、数量品种与医疗机构设置申请及校验验证不一致。', scope: '-', threshold: '设备台账比对', logic: '在系统中对设备基本信息、数量及品种与医疗机构设置申请及校验验证是否一致进行核查。' },
  { id: 'r17', indicator_id: 17, mode: 'alert', name: '检查阳性率异常', desc: '连续三个月内特定检查阳性率超过80%且该检查总量占全院80%时报警。', scope: '-', threshold: '阳性率>80% 且 占比>80%', logic: '建立"连续三个月内单一医疗机构特定检查或检验结果阳性率超过80%且该检查或检验总量占全院总量的80%"统计报警规则。' },
  { id: 'r18', indicator_id: 18, mode: 'alert', name: '重点药品耗材超限', desc: '开展重点药品、耗材日常监测，开具的重点药品、耗材超过阈值时报警。', scope: '国家三级公立医院绩效考核', threshold: '耗材阈值', logic: '根据《国家三级公立医院绩效考核操作手册》，开展重点药品、耗材日常监测，开具的重点药品、耗材超过阈值时报警。' },
  { id: 'r19', indicator_id: 19, mode: 'monitor', name: '设备负荷与闲置', desc: '诊断/治疗设备年平均服务患者数量统计分析。', scope: '-', threshold: '-', metric: '设备效能分析', logic: '统计诊断/治疗设备年平均服务患者数量，计算公式：患者的检查报告数量/设备数量。' },
]

const tabs = [{ id: 'overview', name: '分类总览' }, ...rules]
const activeTab = ref('overview')
const drawerData = ref<any>(null)
const currentRule = computed(() => rules.find(r => r.id === activeTab.value))

const MOCK_DATA: Record<string, any[]> = {
  r15: [
    { id: 'E001', time: '2026-03-29 10:00', org: '省立第一医院', person: '骨科 主任医师李某', violationType: '人机资质不符', detail: '主任医师开展三级关节镜手术，但该医师授权仅为二级手术资质，设备配置也不满足三级手术要求。', evidence: `[手术记录] 患者: 张某 | 三级关节镜手术 | 主刀: 李某(主任医师)\n[医师授权] 李某 | 授权级别: 二级\n[设备配置] 关节镜设备1套，三级手术要求2套\n>>> 异常判定: 医师授权等级与手术分级不匹配，且设备配置不足。` },
    { id: 'E002', time: '2026-03-28 14:30', org: '县人民医院', person: '外科 主治医师王某', violationType: '人机资质不符', detail: '主治医师开展四级腹腔镜手术，但未取得四级手术授权。', evidence: `[手术记录] 患者: 李某 | 四级腹腔镜手术 | 主刀: 王某(主治医师)\n[医师授权] 王某 | 授权级别: 三级，可开展一~三级手术\n>>> 异常判定: 主治医师越权开展四级手术。` },
    { id: 'E003', time: '2026-03-26 09:15', org: '市中心医院', person: '泌尿外科 副主任医师', violationType: '人机资质不符', detail: '副主任医师开展经皮肾镜碎石术（四级），但医师授权仅覆盖三级及以下手术。', evidence: `[手术记录] 四级经皮肾镜碎石术 | 主刀: 副主任医师\n[医师授权] 副主任医师 | 授权级别: 三级\n>>> 异常判定: 越权开展四级手术。` },
    { id: 'E004', time: '2026-03-24 11:00', org: '省立第三医院', person: '心内科 主治医师', violationType: '人机资质不符', detail: '主治医师开展冠脉支架置入术（三级），但未完成心脏介入诊疗技术培训，授权为二级手术资质。', evidence: `[手术记录] 冠脉支架置入术 | 主刀: 主治医师\n[医师授权] 主治医师 | 授权级别: 二级（未经介入培训）\n>>> 异常判定: 未完成专项培训即开展三级介入手术。` },
    { id: 'E005', time: '2026-03-22 15:30', org: '省肿瘤医院', person: '胸外科 主任医师', violationType: '人机资质不符', detail: '主任医师开展胸腔镜下肺叶切除术，但该手术室未配备符合三级手术要求的胸腔镜设备套装。', evidence: `[手术室配置] 2号手术室 | 胸腔镜设备: 1套（老旧型号）\n[手术需求] 三级胸腔镜手术须配备2套独立设备\n>>> 异常判定: 设备配置不满足三级手术要求。` },
    { id: 'E006', time: '2026-03-20 10:45', org: '康华医院', person: '外科', violationType: '人机资质不符', detail: '康华医院外科开展三级腹腔镜手术，但该机构手术室腹腔镜设备未通过年度校验。', evidence: `[设备档案] 腹腔镜设备 | 校验状态: ❌ 未通过（2025-12-31到期未检）\n[实际开展] 三级腹腔镜手术: 8例\n>>> 异常判定: 设备未校验仍开展相关手术。` },
  ],

  r16: [
    { id: 'E007', time: '2026-03-28 14:20', org: '省立第一医院', person: '设备科', violationType: '设备账实不符', detail: 'CT设备实际数量与备案数量不符，系统中登记2台，实际使用3台，超出许可数量1台。', evidence: `[系统备案] CT设备数量: 2台\n[实地核查] CT设备数量: 3台\n>>> 异常判定: 设备数量与备案不符，涉嫌违规增设设备。` },
    { id: 'E008', time: '2026-03-25 09:00', org: '康华医院', person: '设备科', violationType: '设备账实不符', detail: 'MRI设备型号与申请备案不符，申请为1.5T设备，实际使用3.0T设备。', evidence: `[设置申请] MRI设备型号: 1.5T\n[实际设备] MRI设备型号: 3.0T\n>>> 异常判定: 设备型号与申请不符，涉嫌违规配置高端设备。` },
    { id: 'E009', time: '2026-03-23 10:30', org: '市中心医院', person: '设备科', violationType: '设备账实不符', detail: 'DSA（数字减影血管造影机）设备登记数量与实际不符，系统显示1台，实际使用2台，其中1台为借用设备未备案。', evidence: `[系统登记] DSA设备: 1台\n[实际核查] DSA设备: 2台（其中1台为外借设备，未纳入本院固定资产）\n>>> 异常判定: 外借设备未纳入管理，账实不符。` },
    { id: 'E010', time: '2026-03-21 08:45', org: '省立第三医院', person: '设备科', violationType: '设备账实不符', detail: '直线加速器（放疗设备）年度校验已过期（2025-11-30到期），系统仍显示"在用"状态。', evidence: `[系统状态] 直线加速器 | 状态: 在用\n[校验记录] 上次校验: 2024-11-30 | 到期日: 2025-11-30 | 状态: ❌ 已过期\n>>> 异常判定: 校验过期设备仍在使用。` },
    { id: 'E011', time: '2026-03-19 14:00', org: '县人民医院', person: '设备科', violationType: '设备账实不符', detail: '全自动生化分析仪设备登记信息与实物不符，系统登记为"迈瑞BS-800"，实物为"罗氏C8000"，品牌型号均不相符。', evidence: `[系统登记] 品牌: 迈瑞BS-800 | 购入年份: 2022年\n[实物核查] 品牌: 罗氏C8000 | 购入年份: 2023年\n>>> 异常判定: 设备登记信息与实物严重不符。` },
    { id: 'E012', time: '2026-03-17 09:30', org: '仁爱医院', person: '医务科', violationType: '设备账实不符', detail: 'X射线计算机体层摄影设备(CT机)未取得辐射安全许可证，但系统显示"正常运行"。', evidence: `[系统状态] CT机 | 状态: 正常运行\n[许可证核查] 辐射安全许可证: ❌ 未取得\n>>> 异常判定: 无证设备仍在运行。` },
  ],

  r17: [
    { id: 'E013', time: '2026-03-27 08:00', org: '省立第一医院', person: '检验科', violationType: '检查阳性率异常', detail: '连续3个月内肿瘤标志物检测阳性率92%，且占全院检验总量85%，超出阈值。', evidence: `[统计分析] 2025-12~2026-02:\n- 总检测量: 1200例 | 阳性: 1104例\n- 阳性率: 92% > 80%阈值\n- 占全院总量: 85% > 80%阈值\n>>> 异常判定: 阳性率和占比均超出阈值。` },
    { id: 'E014', time: '2026-03-20 10:00', org: '县人民医院', person: '检验科', violationType: '检查阳性率异常', detail: '连续3个月内某项传染病检测阳性率达88%，且占全院检验总量82%。', evidence: `[统计分析] 传染病检测阳性率88%，占全院总量82%，均超出阈值。` },
    { id: 'E015', time: '2026-03-25 11:20', org: '市中心医院', person: '检验科', violationType: '检查阳性率异常', detail: '连续3个月内CT检查阳性率达91%（需手术患者比例），占全院CT总量87%，疑似过度检查。', evidence: `[统计分析] 2025-12~2026-02:\n- CT总检查量: 3500例 | 阳性(需手术): 3185例\n- 阳性率: 91% | 占全院: 87%\n>>> 异常判定: CT阳性率异常偏高，疑似过度检查。` },
    { id: 'E016', time: '2026-03-23 14:45', org: '省立第三医院', person: '放射科', violationType: '检查阳性率异常', detail: '连续3个月内MRI检查阳性率达86%，且占全院MRI总量83%，与同类三级医院均值(55%)差异显著。', evidence: `[统计分析] MRI阳性率: 86% | 占全院: 83%\n[对比数据] 同类三级医院均值: 55%\n>>> 异常判定: 与同类医院均值差异超过30%，疑似过度检查。` },
    { id: 'E017', time: '2026-03-20 09:30', org: '省肿瘤医院', person: '病理科', violationType: '检查阳性率异常', detail: '连续3个月内PET-CT检查阳性率达96%（肿瘤发现率），远高于指南参考值(30%)，疑似存在报告造假风险。', evidence: `[统计分析] PET-CT阳性率: 96%\n[指南参考] 肿瘤筛查阳性率参考值: 30%\n>>> 异常判定: 阳性率远超参考值，报告真实性存疑。` },
    { id: 'E018', time: '2026-03-18 10:15', org: '康华医院', person: '检验科', violationType: '检查阳性率异常', detail: '连续3个月内血糖检测阳性率(高血糖>7.0mmol/L)达94%，占全院检验总量90%，与实际情况偏离较大。', evidence: `[统计分析] 血糖检测阳性率: 94% | 占全院: 90%\n[地区均值] 成人高血糖患病率参考值: 约12%\n>>> 异常判定: 阳性率严重偏离地区患病率基准。` },
  ],

  r18: [
    { id: 'E019', time: '2026-03-30 16:00', org: '市中心医院', person: '医务科', violationType: '耗材超限', detail: '某高值耗材使用量超出国家三级公立医院绩效考核阈值150%。', evidence: `[耗材监测] 高值耗材: 某品牌冠脉支架\n[绩效考核阈值] 月使用量上限: 100个\n[实际使用] 月使用量: 253个 (超标153%)\n>>> 异常判定: 高值耗材使用量超出绩效考核阈值。` },
    { id: 'E020', time: '2026-03-28 11:20', org: '省立第一医院', person: '骨科', violationType: '耗材超限', detail: '人工关节耗材（髋关节假体）月使用量达320套，超出绩效考核目标值(200套)60%。', evidence: `[耗材监测] 髋关节假体 | 月使用量: 320套\n[绩效考核目标] 月上限: 200套\n>>> 异常判定: 耗材使用量超出绩效考核目标60%。` },
    { id: 'E021', time: '2026-03-26 14:30', org: '省立第三医院', person: '心内科', violationType: '耗材超限', detail: '冠脉支架使用量达180根/月，超出国家绩效考核指标（每百例介入手术不超过65根）。', evidence: `[耗材监测] 冠脉支架 | 月使用量: 180根\n[绩效考核指标] 每百例介入: 上限65根\n[介入手术量] 月手术量: 200例\n[理论上限] 200例×0.65 = 130根\n>>> 异常判定: 耗材使用效率比超标。` },
    { id: 'E022', time: '2026-03-24 09:15', org: '市中心医院', person: '神经外科', violationType: '耗材超限', detail: '弹簧圈（颅内血管栓塞材料）使用量超标，本月使用120个，绩效考核上限为80个。', evidence: `[耗材监测] 颅内弹簧圈 | 月使用量: 120个\n[绩效考核上限] 80个/月\n>>> 异常判定: 高值介入耗材超出绩效考核上限。` },
    { id: 'E023', time: '2026-03-22 10:00', org: '省立第一医院', person: '药剂科', violationType: '耗材超限', detail: '重点监控药品（质子泵抑制剂）DDDs值超标，本季度达28,000 DDDs，超出绩效考核指标(20,000 DDDs)40%。', evidence: `[药品监测] 质子泵抑制剂DDDs | 季度值: 28,000\n[绩效考核指标] 上限: 20,000 DDDs\n>>> 异常判定: 重点药品用量超出绩效考核指标。` },
    { id: 'E024', time: '2026-03-20 15:45', org: '县人民医院', person: '医务科', violationType: '耗材超限', detail: '一次性高值耗材（静脉营养袋）重复使用次数超出规定上限，涉及违规使用。', evidence: `[耗材监测] 静脉营养袋 | 规定: 一次性使用\n[实际记录] 同一批次产品使用记录: 重复使用3~5次\n>>> 异常判定: 一次性耗材重复使用，违反院感规定。` },
    { id: 'E025', time: '2026-03-18 11:30', org: '省肿瘤医院', person: '肿瘤科', violationType: '耗材超限', detail: '靶向药物伴随诊断试剂盒使用量超出采购计划200%，存在科室自行采购未报备问题。', evidence: `[耗材监测] 靶向药伴随诊断试剂盒 | 计划采购: 100人份\n[实际使用] 使用量: 320人份\n>>> 异常判定: 实际使用量超出计划200%，科室自行采购未报备。` },
  ],

  r19: [
    { id: 'm191', org: '省立第一医院', metric1: 'CT设备年检查量', value1: '12,500例', metric2: '设备数量', value2: '2台 | 效能: 6250例/台' },
    { id: 'm192', org: '省立第一医院', metric1: 'MRI设备年检查量', value1: '9,800例', metric2: '设备数量', value2: '2台 | 效能: 4900例/台' },
    { id: 'm193', org: '市中心医院', metric1: 'CT设备年检查量', value1: '8,200例', metric2: '设备数量', value2: '1台 | 效能: 8200例/台(满负荷)' },
    { id: 'm194', org: '市中心医院', metric1: 'MRI设备年检查量', value1: '4,200例', metric2: '设备数量', value2: '1台 | 效能: 4200例/台' },
    { id: 'm195', org: '省肿瘤医院', metric1: 'PET-CT年检查量', value1: '1,850例', metric2: '设备数量', value2: '1台 | 效能: 1850例/台' },
    { id: 'm196', org: '省肿瘤医院', metric1: 'CT设备年检查量', value1: '6,500例', metric2: '设备数量', value2: '1台 | 效能: 6500例/台' },
    { id: 'm197', org: '县人民医院', metric1: 'CT设备年检查量', value1: '2,100例', metric2: '设备数量', value2: '1台 | 效能: 2100例/台' },
    { id: 'm198', org: '县人民医院', metric1: 'MRI设备年检查量', value1: '300例', metric2: '设备数量', value2: '1台 | 效能: 300例/台(严重闲置)' },
    { id: 'm199', org: '省立第三医院', metric1: 'CT设备年检查量', value1: '4,500例', metric2: '设备数量', value2: '1台 | 效能: 4500例/台' },
    { id: 'm1910', org: '省立第三医院', metric1: '直线加速器年治疗量', value1: '890例', metric2: '设备数量', value2: '1台 | 效能: 890例/台' },
    { id: 'm1911', org: '康华医院', metric1: 'CT设备年检查量', value1: '800例', metric2: '设备数量', value2: '1台 | 效能: 800例/台(闲置)' },
    { id: 'm1912', org: '县第二医院', metric1: 'CT设备年检查量', value1: '450例', metric2: '设备数量', value2: '1台 | 效能: 450例/台(严重闲置)' },
  ],
}

const isAll = computed(() => currentHospitalId.value === 'all')

function matchHospital(item: any, hName: string): boolean {
  if (item.org === '全省平均') return false
  return item.org === hName || item.org.includes(hName)
}

// 当前规则对应的指标 ID
const currentIndicatorId = computed(() => {
  const rule = currentRule.value
  return rule?.indicator_id ?? null
})

// 获取列顺序：优先使用全省执行记录的列顺序，保持一致性
const columnOrder = computed(() => {
  void hospitalVersion.value
  const indId = currentIndicatorId.value
  if (!indId) return []

  // 优先从全省执行记录获取列顺序
  const rec = findExecutionByTime(indId)
  if (rec?.preview_data?.columns?.length) {
    return rec.preview_data.columns
  }
  if (rec?.preview_data?.rows?.length) {
    return Object.keys(rec.preview_data.rows[0])
  }

  // 如果没有全省记录，使用当前医院缓存的列顺序
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

// 真实预览数据列名
const realTableColumns = computed(() => {
  return columnOrder.value
})

// 真实预览数据
const realTableData = computed(() => {
  void hospitalVersion.value
  const indId = currentIndicatorId.value
  if (!indId) return []

  const cols = columnOrder.value
  if (!cols.length) return []

  // 全省模式：使用全局执行记录的数据
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

const filteredData = computed(() => realTableData.value)

const {
  currentPage: detailCurrentPage,
  totalCount: detailTotalCount,
  totalPages: detailTotalPages,
  visiblePages: detailVisiblePages,
  pagedRows: tableData,
  prevPage: prevDetailPage,
  nextPage: nextDetailPage,
  goToPage: goToDetailPage,
  resetPage: resetDetailPage,
} = useDetailPagination({
  rows: filteredData,
  pageSize: DETAIL_PAGE_SIZE,
  resetDeps: [currentRule],
})

function getDetailTotalCount(): number {
  return detailTotalCount.value
}

/**
 * 注释：以下函数已废弃，请使用 getRuleCount 替代
 * const getMockCount = (id: string) => {
 *   const rule = rules.find(r => r.id === id)
 *   if (!rule) return 0
 *   if (rule.mode === 'alert') return getAlertCount(rule.indicator_id)
 *   return getCount(rule.indicator_id)
 * }
 */

// 根据时间筛选条件过滤执行记录
function findExecutionByTime(indicatorId: number): any | null {
  const tm = timeMode.value
  const tv = currentTimeValue.value
  const results = executionRecords.value
    .filter(r => r.indicator_id === indicatorId && r.status === 'success')
    .filter(r => {
      if (tm === 'immediate') return true
      if (r.run_mode !== tm) return false
      if (tv && r.time_value !== tv) return false
      return true
    })
    .sort((a, b) => new Date(b.execution_time).getTime() - new Date(a.execution_time).getTime())

  console.log('[findExecutionByTime]', {
    indicatorId,
    timeMode: tm,
    timeValue: tv,
    matchedCount: results.length,
    records: results.map(r => ({
      id: r.id,
      execution_time: r.execution_time,
      run_mode: r.run_mode,
      time_value: r.time_value,
      status: r.status,
      numerator_count: r.numerator_count,
      preview_data_rows: r.preview_data?.rows?.length,
      preview_data_cols: r.preview_data?.columns,
    })),
  })

  return results[0] || null
}

function getRuleCount(rule: any): string {
  if (!rule) return '-'
  void hospitalVersion.value
  if (currentHospitalId.value === 'all') {
    void countLoading.value
    void ruleCountCache.value
    const rec = findExecutionByTime(rule.indicator_id)
    if (!rec) return '-'
    const cnt = rec.numerator_count ?? 0
    if (rule.mode !== 'monitor' || !rule.metric) return `${cnt} 条`
    return formatCountInMetric(rule.metric, cnt)
  }
  const tm = timeMode.value
  const tv = currentTimeValue.value
  const key = `${rule.indicator_id}-${currentHospitalId.value}-${tm}-${tv || 'all'}`
  const cnt = ruleCountCache.value[key]
  if (cnt === undefined || cnt === -1) return '-'
  if (rule.mode !== 'monitor' || !rule.metric) return `${cnt} 条`
  return formatCountInMetric(rule.metric, cnt)
}

const openDrawer = (row: any) => { drawerData.value = row }

const equipColumns = [
  { field: 'time', header: '预警时间' },
  { field: 'org', header: '涉事机构' },
  { field: 'person', header: '涉事人员' },
  { field: 'detail', header: '违规详情' },
]

function handleExport() {
  const rule = currentRule.value
  const name = rule ? `${rule.id}-${rule.name}` : '设备要素总览'
  exportToExcel(tableData.value, equipColumns, `设备要素_${name}`)
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.animate-slide-in { animation: slideIn 0.3s ease-out; }
@keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }
</style>
