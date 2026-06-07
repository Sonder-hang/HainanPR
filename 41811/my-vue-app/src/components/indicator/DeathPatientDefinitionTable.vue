<template>
  <div class="flex h-full min-h-0 flex-col bg-[#F4F6F8] p-5 font-sans overflow-y-auto">
    <header class="mb-5 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-2">
        <h1 class="text-[24px] font-bold text-[#1F264D]">{{ title }}</h1>
        <button
          @click="helpVisible = true"
          class="w-5 h-5 rounded-full bg-[#b8c9e8]/60 text-[#596080] text-[12px] font-medium flex items-center justify-center hover:bg-[#0A6EFD] hover:text-white transition-colors cursor-pointer"
          title="指标说明"
        >?</button>
      </div>
      <div class="flex flex-wrap items-center gap-2.5">
        <select
          v-model="timeMode"
          class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
        >
          <option value="monthly">按月份</option>
          <option value="quarterly">按季度</option>
        </select>
        <select
          v-if="timeMode === 'monthly'"
          v-model="selectedYear"
          class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
        >
          <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}年</option>
        </select>
        <select
          v-if="timeMode === 'monthly'"
          v-model="selectedMonth"
          class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
        >
          <option v-for="month in monthOptions" :key="month.value" :value="month.value">{{ month.label }}</option>
        </select>
        <template v-if="timeMode === 'quarterly'">
          <select
            v-model="selectedQuarterYear"
            class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
          >
            <option v-for="year in quarterYearOptions" :key="year" :value="year">{{ year }}年</option>
          </select>
          <select
            v-model="selectedQuarter"
            class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
          >
            <option v-for="q in quarterOptions" :key="q.value" :value="q.value">{{ q.label }}</option>
          </select>
        </template>
        <button
          @click="loadData"
          class="h-8 rounded bg-[#2E57E5] px-4 text-[14px] font-medium text-white transition-colors hover:bg-[#1E4BD8]"
        >
          查询
        </button>
      </div>
    </header>

    <div class="bg-white rounded-[2px] border border-[#b8c9e8]/60 flex-1 overflow-hidden flex flex-col shadow-sm">
      <div class="p-3.5 border-b border-[#b8c9e8]/40 flex justify-between items-center shrink-0">
        <h3 class="font-semibold text-[#1F264D] flex items-center text-[13px]">
          患者列表
          <span class="ml-2 bg-red-100 text-red-600 py-0.5 px-2 rounded-full text-[11px] font-bold">{{ totalItems }}</span>
        </h3>
        <div class="flex items-center gap-2">
          <div class="relative">
            <Search class="w-3.5 h-3.5 absolute left-2.5 top-1/2 transform -translate-y-1/2 text-[#B8BCCC]" />
            <input
              v-model="searchKeyword"
              type="text"
              placeholder="搜索患者ID、姓名、科室、医院..."
              class="pl-8 pr-3 py-1.5 text-[12px] border border-[#b8c9e8]/60 rounded-[2px] focus:outline-none focus:border-[#0A6EFD] w-64 bg-white"
              @input="handleSearch"
            />
          </div>
          <div class="text-[12px] text-[#596080]">第 {{ currentPage }} 页，共 {{ totalPages }} 页</div>
          <div class="flex items-center gap-1">
            <button @click="prevPage" :disabled="currentPage === 1" class="p-1.5 text-[#596080] hover:text-[#0A6EFD] disabled:text-[#B8BCCC] disabled:cursor-not-allowed">
              <ChevronLeft class="w-3.5 h-3.5" />
            </button>
            <button
              v-for="page in visiblePages"
              :key="page"
              @click="goToPage(page)"
              class="w-7 h-7 text-[12px] rounded-[2px] transition-colors"
              :class="page === currentPage ? 'bg-[#0A6EFD] text-white' : 'text-[#596080] hover:bg-[#e8eef9]'"
            >{{ page }}</button>
            <button @click="nextPage" :disabled="currentPage === totalPages" class="p-1.5 text-[#596080] hover:text-[#0A6EFD] disabled:text-[#B8BCCC] disabled:cursor-not-allowed">
              <ChevronRight class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      <div class="flex-1 overflow-auto">
        <table class="w-full text-left border-collapse">
          <thead class="bg-[#e8eef9] sticky top-0 z-10">
            <tr>
              <th v-for="header in displayHeaders" :key="header" class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">{{ header }}</th>
              <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide text-right">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[#b8c9e8]/30">
            <tr v-for="patient in paginatedData" :key="patient.id" class="hover:bg-[#e8eef9]/40 transition-colors group">
              <td class="px-3.5 py-2.5 text-[12px] text-[#596080] whitespace-nowrap font-mono">{{ patient.patient_id }}</td>
              <td class="px-3.5 py-2.5 text-[12px] text-[#1F264D] font-medium">{{ patient.patient_name }}</td>
              <td class="px-3.5 py-2.5 text-[12px] text-[#596080]">{{ patient.department }}</td>
              <td class="px-3.5 py-2.5 text-[12px] text-[#596080]">{{ patient.hospital }}</td>
              <td class="px-3.5 py-2.5 text-[12px] text-right">
                <button @click="openModal(patient)" class="text-[#0A6EFD] hover:text-[#1F264D] font-medium flex items-center justify-end w-full text-[11px]">
                  <Eye class="w-3 h-3 mr-1" /> 查看详情
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <div v-if="modalVisible" class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50 backdrop-blur-sm">
    <div class="w-[580px] bg-white rounded-[2px] shadow-2xl flex flex-col animate-fade-in border border-[#b8c9e8]/60">
      <div class="px-5 py-3.5 border-b border-[#b8c9e8]/60 flex justify-between items-center bg-[#e8eef9]">
        <h2 class="text-[14px] font-bold text-[#1F264D] flex items-center">患者详细信息</h2>
        <button @click="closeModal" class="p-1.5 hover:bg-[#b8c9e8]/30 rounded-full text-[#596080] transition-colors"><X class="w-4 h-4" /></button>
      </div>
      <div class="flex-1 overflow-y-auto p-5 space-y-5">
        <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
          <div class="mb-3"><h3 class="font-bold text-[#1F264D] text-[13px]">基本信息</h3></div>
          <div class="grid grid-cols-2 gap-3 text-[12px]">
            <div><span class="text-[#596080] block mb-0.5">医院名称</span><span class="font-medium text-[#1F264D]">{{ currentPatient?.hospital }}</span></div>
            <div><span class="text-[#596080] block mb-0.5">患者ID</span><span class="font-medium text-[#1F264D] font-mono">{{ currentPatient?.patient_id }}</span></div>
            <div><span class="text-[#596080] block mb-0.5">患者姓名</span><span class="font-medium text-[#1F264D]">{{ currentPatient?.patient_name }}</span></div>
            <div><span class="text-[#596080] block mb-0.5">科室名称</span><span class="font-medium text-[#1F264D]">{{ currentPatient?.department }}</span></div>
          </div>
        </div>
        <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
          <h3 class="font-bold text-[#1F264D] text-[13px] mb-2.5">转归判断依据</h3>
          <div class="bg-red-50 border border-red-200 rounded-[2px] p-3 text-[12px] text-red-800">
            <p class="font-medium mb-1">{{ currentPatient?.death_basis }}</p>
            <p class="text-red-700">{{ currentPatient?.death_basis_detail }}</p>
          </div>
        </div>
        <div>
          <h3 class="font-bold text-[#1F264D] text-[13px] mb-2.5 flex items-center">病历来源</h3>
          <div class="bg-[#f8faff] border border-[#b8c9e8]/60 rounded-[2px] p-4">
            <p class="text-[11px] text-[#B8BCCC] mb-1.5 font-mono">=== 病历来源信息 ===</p>
            <div class="bg-[#f0f4ff] p-2.5 rounded-[2px] text-[11px] font-mono text-[#596080] whitespace-pre-line leading-relaxed">{{ currentPatient?.death_record_source }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-if="helpVisible" class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50 backdrop-blur-sm" @click.self="helpVisible = false">
    <div class="w-[520px] bg-white rounded-[2px] shadow-2xl flex flex-col animate-fade-in border border-[#b8c9e8]/60">
      <div class="px-5 py-3.5 border-b border-[#b8c9e8]/60 flex justify-between items-center bg-[#e8eef9]">
        <h2 class="text-[14px] font-bold text-[#1F264D]">指标说明</h2>
        <button @click="helpVisible = false" class="p-1.5 hover:bg-[#b8c9e8]/30 rounded-full text-[#596080] transition-colors"><X class="w-4 h-4" /></button>
      </div>
      <div class="flex-1 overflow-y-auto p-5 space-y-4">
        <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
          <h3 class="font-bold text-[#1F264D] text-[13px] mb-2">指标定义</h3>
          <p class="text-[12px] text-[#596080] leading-relaxed">
            死亡或出院预期转归不良患者：指在住院期间被病案首页标记为死亡的患者，或经模型预估判定为预期转归不良（病情严重程度达到死亡风险阈值）的患者。
          </p>
        </div>
        <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
          <h3 class="font-bold text-[#1F264D] text-[13px] mb-2">数据来源</h3>
          <ul class="text-[12px] text-[#596080] space-y-1.5 leading-relaxed">
            <li class="flex items-start gap-2">
              <span class="mt-0.5 w-1.5 h-1.5 rounded-full bg-[#0A6EFD] shrink-0"></span>
              病案首页死亡标记：基于患者出院时病案首页记录的死亡状态
            </li>
            <li class="flex items-start gap-2">
              <span class="mt-0.5 w-1.5 h-1.5 rounded-full bg-[#0A6EFD] shrink-0"></span>
              模型预估：基于患者病情的严重程度模型预测
            </li>
          </ul>
        </div>
        <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
          <h3 class="font-bold text-[#1F264D] text-[13px] mb-2">统计口径</h3>
          <p class="text-[12px] text-[#596080] leading-relaxed">
            统计周期内，纳入死亡或预期转归不良的患者人次，按医院、科室进行分类汇总。
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { Search, Eye, ChevronLeft, ChevronRight, X } from 'lucide-vue-next'
import { core18Api, type DeathPatient } from '@/api/core18'

const props = defineProps({
  title: { type: String, default: '死亡或出院预期转归不良患者' },
  hospitalCode: { type: String, default: '' },
  tableHeaders: { type: Array as () => string[], default: () => [] },
})

// 时间筛选选项
const now = new Date()
const currentYear = now.getFullYear()
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

// 时间筛选状态
const timeMode = ref<'monthly' | 'quarterly'>('monthly')
const selectedYear = ref(currentYear)
const selectedMonth = ref(now.getMonth() + 1)
const selectedQuarterYear = ref(currentYear)
const selectedQuarter = ref('1')

// 搜索和分页
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const modalVisible = ref(false)
const helpVisible = ref(false)
const currentPatient = ref<DeathPatient | null>(null)

const DEFAULT_HEADERS = ['患者ID', '患者姓名', '科室名称', '医院名称']
const displayHeaders = computed(() => props.tableHeaders.length ? props.tableHeaders : DEFAULT_HEADERS)

// 后端数据
const patientsData = ref<DeathPatient[]>([])
const totalItems = ref(0)
const isLoading = ref(false)

// 获取时间值
function getTimeValue(): string {
  if (timeMode.value === 'monthly') {
    return `${selectedYear.value}-${String(selectedMonth.value).padStart(2, '0')}`
  } else {
    return `${selectedQuarterYear.value}-Q${selectedQuarter.value}`
  }
}

// 加载数据
async function loadData() {
  isLoading.value = true
  try {
    const res = await core18Api.getDeathPatients({
      hospital_code: props.hospitalCode || undefined,
      time_mode: timeMode.value,
      time_value: getTimeValue(),
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: searchKeyword.value,
    })
    patientsData.value = res.data || []
    totalItems.value = res.total || 0
  } catch (e) {
    console.error('加载死亡患者数据失败:', e)
  } finally {
    isLoading.value = false
  }
}

const filteredData = computed(() => {
  if (!searchKeyword.value.trim()) return patientsData.value
  const keyword = searchKeyword.value.toLowerCase()
  return patientsData.value.filter(patient =>
    patient.patientId?.toLowerCase().includes(keyword) ||
    patient.patientName?.toLowerCase().includes(keyword) ||
    patient.department?.toLowerCase().includes(keyword) ||
    patient.hospital?.toLowerCase().includes(keyword)
  )
})

const totalPages = computed(() => Math.ceil(totalItems.value / pageSize.value))
const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredData.value.slice(start, start + pageSize.value)
})
const visiblePages = computed(() => {
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages.value, start + maxVisible - 1)
  if (end - start + 1 < maxVisible) start = Math.max(1, end - maxVisible + 1)
  return Array.from({ length: end - start + 1 }, (_, i) => start + i)
})

const handleSearch = () => { currentPage.value = 1; loadData() }
const prevPage = () => { if (currentPage.value > 1) currentPage.value-- }
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++ }
const goToPage = (page: number) => { currentPage.value = page }
const openModal = (patient: any) => { currentPatient.value = patient; modalVisible.value = true }
const closeModal = () => { modalVisible.value = false; currentPatient.value = null }

watch(searchKeyword, () => { currentPage.value = 1 })
watch(currentPage, () => { loadData() })
watch(() => props.hospitalCode, () => { loadData() })

onMounted(() => { loadData() })
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
</style>
