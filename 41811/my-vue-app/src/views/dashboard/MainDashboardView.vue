<template>
  <div class="space-y-5 animate-fade-in">
    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center h-64">
      <div class="flex flex-col items-center gap-3">
        <div class="w-8 h-8 border-4 border-[#0A6EFD] border-t-transparent rounded-full animate-spin"></div>
        <span class="text-[13px] text-[#596080]">加载数据中...</span>
      </div>
    </div>

    <template v-else>
      <!-- 页面标题 + 筛选器 -->
      <div class="flex items-center justify-between">
        <h2 class="text-[16px] font-bold text-[#1F264D]">四要素总览</h2>
        <!-- 筛选器 -->
        <div class="flex items-center gap-2">
          <!-- 时间筛选 -->
          <div class="flex items-center gap-1 border border-[#b8c9e8]/60 rounded-[2px] px-2 bg-white h-[34px]">
            <button
              v-for="mode in TIME_MODE_OPTIONS"
              :key="mode.value"
              type="button"
              class="rounded px-2 text-[11px] transition-colors leading-[22px]"
              :class="timeMode === mode.value
                ? 'bg-[#0A6EFD] text-white font-medium'
                : 'text-[#596080] hover:bg-[#e8eef9]'"
              @click="timeMode = mode.value; refreshData()"
            >{{ mode.label }}</button>
            <!-- 月份选择 -->
            <template v-if="timeMode === 'monthly'">
              <select
                v-model="selectedMonthYear"
                class="border-none bg-transparent text-[11px] text-[#1F264D] focus:outline-none cursor-pointer"
                @change="refreshData"
              >
                <option v-for="y in monthYearOptions" :key="y" :value="y">{{ y }}</option>
              </select>
              <span class="text-[#596080]">年</span>
              <select
                v-model="selectedMonthNum"
                class="border-none bg-transparent text-[11px] text-[#1F264D] focus:outline-none cursor-pointer"
                @change="refreshData"
              >
                <option v-for="m in MONTH_OPTIONS" :key="m.value" :value="m.value">{{ m.label }}</option>
              </select>
            </template>
            <!-- 季度选择 -->
            <template v-else-if="timeMode === 'quarterly'">
              <select
                v-model="selectedQuarterYear"
                class="border-none bg-transparent text-[11px] text-[#1F264D] focus:outline-none cursor-pointer"
                @change="refreshData"
              >
                <option v-for="y in quarterYearOptions" :key="y" :value="y">{{ y }}</option>
              </select>
              <span class="text-[#596080]">年</span>
              <select
                v-model="selectedQuarterNum"
                class="border-none bg-transparent text-[11px] text-[#1F264D] focus:outline-none cursor-pointer"
                @change="refreshData"
              >
                <option v-for="q in QUARTER_OPTIONS" :key="q.value" :value="q.value">{{ q.label }}</option>
              </select>
            </template>
          </div>
          <!-- 医院筛选 -->
          <div class="relative hospital-filter">
            <div class="flex items-center gap-1.5 border border-[#b8c9e8]/60 rounded-[2px] px-2.5 py-1.5 cursor-pointer select-none hover:border-[#0A6EFD]/50 transition-colors bg-white text-[12px] h-[34px]"
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
        </div>
      </div>

      <!-- 四要素统计卡片 2x2 布局 -->
      <div class="grid grid-cols-2 gap-5">
        <!-- 人员要素卡片 -->
        <div
          @click="$router.push('/personnel')"
          class="bg-white rounded-[2px] border border-[#b8c9e8]/60 p-6 shadow-sm hover:border-[#0A6EFD]/60 hover:shadow-md transition-all cursor-pointer"
        >
          <div class="flex items-center mb-4">
            <div class="w-14 h-14 rounded-full bg-blue-50 flex items-center justify-center mr-4 shrink-0">
              <Users class="w-7 h-7 text-[#0A6EFD]" />
            </div>
            <div>
              <p class="text-[13px] text-[#596080] font-medium mb-0.5">人员要素违规报警</p>
              <h3 class="text-[32px] font-bold text-[#0A6EFD] leading-none">
                {{ stats.personnel }}
                <span class="text-[12px] font-normal text-[#B8BCCC]">次</span>
              </h3>
            </div>
          </div>
          <!-- 重点指标预警 -->
          <div>
            <h4 class="text-[12px] font-medium text-[#596080] mb-2">重点指标预警</h4>
            <div class="space-y-2">
              <div
                v-for="item in topIndicators.personnel"
                :key="item.name"
                @click="$router.push('/personnel')"
                class="cursor-pointer"
              >
                <div class="flex justify-between text-[11px] mb-0.5">
                  <span class="text-[#596080] truncate flex-1 mr-2">{{ item.name }}</span>
                  <span class="font-bold hover:underline text-[#0A6EFD] shrink-0">{{ item.count }}条</span>
                </div>
                <div class="h-1.5 bg-[#e8eef9] rounded-full overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all duration-500 hover:opacity-80 bg-[#0A6EFD]"
                    :style="{ width: `${item.percent}%` }"
                  ></div>
                </div>
              </div>
              <div v-if="topIndicators.personnel.length === 0" class="text-[12px] text-[#B8BCCC] text-center py-2">
                暂无数据
              </div>
            </div>
          </div>
        </div>

        <!-- 机构要素卡片 -->
        <div
          @click="$router.push('/institution')"
          class="bg-white rounded-[2px] border border-[#b8c9e8]/60 p-6 shadow-sm hover:border-purple-500/60 hover:shadow-md transition-all cursor-pointer"
        >
          <div class="flex items-center mb-4">
            <div class="w-14 h-14 rounded-full bg-purple-50 flex items-center justify-center mr-4 shrink-0">
              <Building class="w-7 h-7 text-purple-600" />
            </div>
            <div>
              <p class="text-[13px] text-[#596080] font-medium mb-0.5">机构运行预警记录</p>
              <h3 class="text-[32px] font-bold text-purple-600 leading-none">
                {{ stats.institution }}
                <span class="text-[12px] font-normal text-[#B8BCCC]">次</span>
              </h3>
            </div>
          </div>
          <!-- 重点指标预警 -->
          <div>
            <h4 class="text-[12px] font-medium text-[#596080] mb-2">重点指标预警</h4>
            <div class="space-y-2">
              <div
                v-for="item in topIndicators.institution"
                :key="item.name"
                @click="$router.push('/institution')"
                class="cursor-pointer"
              >
                <div class="flex justify-between text-[11px] mb-0.5">
                  <span class="text-[#596080] truncate flex-1 mr-2">{{ item.name }}</span>
                  <span class="font-bold hover:underline text-purple-600 shrink-0">{{ item.count }}条</span>
                </div>
                <div class="h-1.5 bg-[#e8eef9] rounded-full overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all duration-500 hover:opacity-80 bg-purple-600"
                    :style="{ width: `${item.percent}%` }"
                  ></div>
                </div>
              </div>
              <div v-if="topIndicators.institution.length === 0" class="text-[12px] text-[#B8BCCC] text-center py-2">
                暂无数据
              </div>
            </div>
          </div>
        </div>

        <!-- 技术要素卡片 -->
        <div
          @click="$router.push('/technology')"
          class="bg-white rounded-[2px] border border-[#b8c9e8]/60 p-6 shadow-sm hover:border-red-500/60 hover:shadow-md transition-all cursor-pointer"
        >
          <div class="flex items-center mb-4">
            <div class="w-14 h-14 rounded-full bg-red-50 flex items-center justify-center mr-4 shrink-0">
              <ShieldAlert class="w-7 h-7 text-red-600" />
            </div>
            <div>
              <p class="text-[13px] text-[#596080] font-medium mb-0.5">医疗技术高危拦截</p>
              <h3 class="text-[32px] font-bold text-red-600 leading-none">
                {{ stats.technology }}
                <span class="text-[12px] font-normal text-[#B8BCCC]">次</span>
              </h3>
            </div>
          </div>
          <!-- 重点指标预警 -->
          <div>
            <h4 class="text-[12px] font-medium text-[#596080] mb-2">重点指标预警</h4>
            <div class="space-y-2">
              <div
                v-for="item in topIndicators.technology"
                :key="item.name"
                @click="$router.push('/technology')"
                class="cursor-pointer"
              >
                <div class="flex justify-between text-[11px] mb-0.5">
                  <span class="text-[#596080] truncate flex-1 mr-2">{{ item.name }}</span>
                  <span class="font-bold hover:underline text-red-600 shrink-0">{{ item.count }}条</span>
                </div>
                <div class="h-1.5 bg-[#e8eef9] rounded-full overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all duration-500 hover:opacity-80 bg-red-600"
                    :style="{ width: `${item.percent}%` }"
                  ></div>
                </div>
              </div>
              <div v-if="topIndicators.technology.length === 0" class="text-[12px] text-[#B8BCCC] text-center py-2">
                暂无数据
              </div>
            </div>
          </div>
        </div>

        <!-- 设备要素卡片 -->
        <div
          @click="$router.push('/equipment')"
          class="bg-white rounded-[2px] border border-[#b8c9e8]/60 p-6 shadow-sm hover:border-orange-500/60 hover:shadow-md transition-all cursor-pointer"
        >
          <div class="flex items-center mb-4">
            <div class="w-14 h-14 rounded-full bg-orange-50 flex items-center justify-center mr-4 shrink-0">
              <Monitor class="w-7 h-7 text-orange-600" />
            </div>
            <div>
              <p class="text-[13px] text-[#596080] font-medium mb-0.5">设备效能异常监测</p>
              <h3 class="text-[32px] font-bold text-orange-600 leading-none">
                {{ stats.equipment }}
                <span class="text-[12px] font-normal text-[#B8BCCC]">次</span>
              </h3>
            </div>
          </div>
          <!-- 重点指标预警 -->
          <div>
            <h4 class="text-[12px] font-medium text-[#596080] mb-2">重点指标预警</h4>
            <div class="space-y-2">
              <div
                v-for="item in topIndicators.equipment"
                :key="item.name"
                @click="$router.push('/equipment')"
                class="cursor-pointer"
              >
                <div class="flex justify-between text-[11px] mb-0.5">
                  <span class="text-[#596080] truncate flex-1 mr-2">{{ item.name }}</span>
                  <span class="font-bold hover:underline text-orange-600 shrink-0">{{ item.count }}条</span>
                </div>
                <div class="h-1.5 bg-[#e8eef9] rounded-full overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all duration-500 hover:opacity-80 bg-orange-600"
                    :style="{ width: `${item.percent}%` }"
                  ></div>
                </div>
              </div>
              <div v-if="topIndicators.equipment.length === 0" class="text-[12px] text-[#B8BCCC] text-center py-2">
                暂无数据
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 重点预警分类统计 -->
      <div class="bg-white rounded-[2px] border border-[#b8c9e8]/60 p-5 shadow-sm">
        <h3 class="text-[13px] font-bold text-[#1F264D] mb-3.5">重点预警分类统计</h3>
        <div class="grid grid-cols-5 gap-3">
          <div
            v-for="item in alertCategories"
            :key="item.name"
            @click="$router.push(item.route)"
            class="text-center p-3 border border-[#b8c9e8]/40 rounded-[2px] hover:bg-[#e8eef9]/30 hover:border-[#0A6EFD]/50 transition-all cursor-pointer"
          >
            <div class="text-[22px] font-bold mb-0.5" :style="{ color: item.color }">{{ item.count }}</div>
            <div class="text-[11px] text-[#596080]">{{ item.name }}</div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Building, MapPin, ChevronDown, Monitor, ShieldAlert, Users } from 'lucide-vue-next'
import {
  TIME_MODE_OPTIONS,
  MONTH_OPTIONS,
  QUARTER_OPTIONS,
  type TimeMode,
  useFourFactorExecutions,
} from '@/composables/useFourFactorExecutions'

// 预警分类颜色配置
const ALERT_COLORS = ['#dc2626', '#7c3aed', '#2563eb', '#ea580c', '#9333ea']

const loading = ref(true)
const showHospitalFilter = ref(false)
const currentHospitalId = ref('all')

// 使用 composable
const {
  fetchHospitals,
  fetchExecutions,
  fetchIndicators,
  getLatestSuccess,
  getCountByHospital,
  getIndicatorCategory,
  getIndicatorName,
  hospitalList,
  executionRecords,
} = useFourFactorExecutions()

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

// 月份年份选项
const monthYearOptions = computed(() => {
  const now = new Date()
  const cur = now.getFullYear()
  const years: number[] = []
  for (let y = cur - 5; y <= cur + 1; y++) {
    years.push(y)
  }
  return years
})

// 季度年份选项
const quarterYearOptions = computed(() => {
  const now = new Date()
  const cur = now.getFullYear()
  const years: number[] = []
  for (let y = cur - 5; y <= cur + 1; y++) {
    years.push(y)
  }
  return years
})

interface Hospital {
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
  showHospitalFilter.value = false
  refreshData()
}

// 统计数据
const stats = ref({
  personnel: 0,
  institution: 0,
  technology: 0,
  equipment: 0,
})

// Top 指标数据
const topIndicators = ref<Record<string, { name: string; count: number; percent: number }[]>>({
  personnel: [],
  institution: [],
  technology: [],
  equipment: [],
})

// 预警分类统计
const alertCategories = ref<{ name: string; count: number; color: string; route: string }[]>([])

// 刷新数据
async function refreshData() {
  loading.value = true
  try {
    // 按分类汇总数据
    const categoryData: Record<string, { total: number; indicators: Map<string, number> }> = {
      personnel: { total: 0, indicators: new Map() },
      institution: { total: 0, indicators: new Map() },
      technology: { total: 0, indicators: new Map() },
      equipment: { total: 0, indicators: new Map() },
    }

    // 所有指标计数列表（用于预警分类统计）
    const allIndicators: { name: string; count: number; category: string }[] = []

    // 获取所有指标的唯一 ID
    const indicatorIds = [...new Set(executionRecords.value.map(r => r.indicator_id))]

    // 对每个指标获取计数
    for (const indicatorId of indicatorIds) {
      let count: number
      
      if (currentHospitalId.value === 'all') {
        const rec = getLatestSuccess(indicatorId, timeMode.value, currentTimeValue.value)
        count = rec?.numerator_count ?? 0
      } else {
        const result = await getCountByHospital(indicatorId, currentHospitalId.value, timeMode.value, currentTimeValue.value)
        count = result < 0 ? 0 : result
      }

      if (count <= 0) continue

      // 获取指标名称和分类
      const indicatorName = getIndicatorName(indicatorId)
      const category = getIndicatorCategory(indicatorId)

      // 记录到所有指标列表
      allIndicators.push({ name: indicatorName, count, category })

      // 累加到对应分类
      categoryData[category].total += count
      const existingCount = categoryData[category].indicators.get(indicatorName) || 0
      categoryData[category].indicators.set(indicatorName, existingCount + count)
    }

    // 更新统计数据
    stats.value.personnel = categoryData.personnel.total
    stats.value.institution = categoryData.institution.total
    stats.value.technology = categoryData.technology.total
    stats.value.equipment = categoryData.equipment.total

    // 计算最大分类计数，用于百分比
    const maxTotal = Math.max(
      stats.value.personnel,
      stats.value.institution,
      stats.value.technology,
      stats.value.equipment,
      1
    )

    // 构建 top 指标数据（每个分类取前3个）
    const buildTopIndicators = (category: string): { name: string; count: number; percent: number }[] => {
      const indicators = categoryData[category as keyof typeof categoryData].indicators
      const entries = Array.from(indicators.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3)
      return entries.map(([name, count]) => ({
        name,
        count,
        percent: Math.round((count / maxTotal) * 100),
      }))
    }

    topIndicators.value = {
      personnel: buildTopIndicators('personnel'),
      institution: buildTopIndicators('institution'),
      technology: buildTopIndicators('technology'),
      equipment: buildTopIndicators('equipment'),
    }

    // 更新预警分类统计（展示所有指标中 count 最大的前5个）
    const top5Indicators = allIndicators
      .sort((a, b) => b.count - a.count)
      .slice(0, 5)

    alertCategories.value = top5Indicators.map((item, idx) => ({
      name: item.name,
      count: item.count,
      color: ALERT_COLORS[idx % ALERT_COLORS.length],
      route: `/${item.category === 'personnel' ? 'personnel' : item.category === 'institution' ? 'institution' : item.category === 'technology' ? 'technology' : 'equipment'}`,
    }))

  } finally {
    loading.value = false
  }
}

function handleClickOutside(e: MouseEvent) {
  if (!(e.target as HTMLElement).closest('.hospital-filter')) {
    showHospitalFilter.value = false
  }
}

onMounted(async () => {
  document.addEventListener('click', handleClickOutside)
  await fetchHospitals()
  await fetchIndicators()
  await fetchExecutions()
  await refreshData()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
