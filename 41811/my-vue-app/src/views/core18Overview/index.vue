<template>
  <div class="flex h-full min-h-0 flex-col bg-[#F4F6F8] p-5 font-sans">
    <!-- 页面标题栏 -->
    <header class="mb-5 flex flex-wrap items-center justify-between gap-4">
      <h1 class="text-[24px] font-bold text-[#1F264D]">十八项核心制度总览</h1>
      <div class="flex flex-wrap items-center gap-2.5">
        <CheckboxGroup
          v-model="draftSelectedIndicators"
          :options="indicatorOptions"
          placeholder="请选择指标"
        />
        <input
          v-model="draftSearchKeyword"
          type="text"
          placeholder="请输入指标名称筛选"
          class="h-8 w-48 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none placeholder:text-[#B8BCCC] focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
        />
        <select
          v-model="draftTimeMode"
          class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
        >
          <option value="monthly">按月份</option>
          <option value="quarterly">按季度</option>
        </select>
        <select
          v-if="draftTimeMode === 'monthly'"
          v-model="draftYear"
          class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
        >
          <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}年</option>
        </select>
        <select
          v-if="draftTimeMode === 'monthly'"
          v-model="draftMonth"
          class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
        >
          <option v-for="month in monthOptions" :key="month.value" :value="month.value">{{ month.label }}</option>
        </select>
        <template v-if="draftTimeMode === 'quarterly'">
          <select
            v-model="draftQuarterYear"
            class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
          >
            <option v-for="year in quarterYearOptions" :key="year" :value="year">{{ year }}年</option>
          </select>
          <select
            v-model="draftQuarterNum"
            class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
          >
            <option v-for="q in quarterOptions" :key="q.value" :value="q.value">{{ q.label }}</option>
          </select>
        </template>
        <select
          v-model="draftHospital"
          class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
        >
          <option v-for="item in hospitalOptions" :key="item.value" :value="item.value">{{ item.label }}</option>
        </select>
        <button
          type="button"
          class="h-8 rounded bg-[#2E57E5] px-4 text-[14px] font-medium text-white transition-colors hover:bg-[#1E4BD8]"
          @click="handleQuery"
        >
          查询
        </button>
      </div>
    </header>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="flex flex-1 items-center justify-center">
      <div class="text-[16px] text-[#596080]">加载中...</div>
    </div>

    <!-- 指标卡片区域 -->
    <div v-else class="flex-1 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-6 min-h-0 grid-auto-rows-[140px] items-start grid-rows-none overflow-y-auto content-start">
      <!-- 动态渲染指标卡片 -->
      <div
        v-for="indicator in filteredIndicators"
        :key="indicator.id"
        class="relative cursor-pointer rounded-lg bg-white p-5 shadow-sm transition-transform hover:-translate-y-1 min-h-[140px] self-start"
        @click="goToIndicatorFinal(indicator)"
      >
        <!-- 指标解释按钮 -->
        <button
          type="button"
          class="absolute right-2 top-2 z-10 h-6 w-6 rounded-full text-[#596080] transition-colors hover:bg-[#F2F5FA] hover:text-[#0A6EFD]"
          @click.stop="openIndicatorDetail(indicator)"
          title="查看指标详情"
        >
          <svg class="mx-auto h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </button>

        <div class="mb-2 text-[14px] text-[#596080]">{{ indicator.name }}</div>
        <div class="mb-1 text-[28px] font-bold" :class="indicator.has_data ? 'text-[#2E57E5]' : 'text-[#B8BCCC]'">
          {{ getIndicatorValue(indicator) }}
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!isLoading && filteredIndicators.length === 0" class="flex flex-1 items-center justify-center">
      <div class="text-[16px] text-[#596080]">暂无数据</div>
    </div>

    <!-- 指标详情抽屉 -->
    <div
      v-if="drawerVisible"
      class="fixed inset-0 z-50 flex"
      @click="closeDrawer"
    >
      <!-- 抽屉内容 -->
      <div
        class="relative ml-auto flex h-full w-[500px] flex-col bg-white shadow-xl"
        @click.stop
      >
        <!-- 抽屉头部 -->
        <div class="flex items-center justify-between border-b border-[#E6E9F2] px-6 py-4">
          <h2 class="text-[20px] font-medium text-[#1F264D]">指标详情</h2>
          <button
            type="button"
            class="h-8 w-8 rounded-full text-[#596080] transition-colors hover:bg-[#F2F5FA] hover:text-[#1F264D]"
            @click="closeDrawer"
          >
            <svg class="mx-auto h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- 抽屉内容区域 -->
        <div class="flex-1 overflow-y-auto p-6">
          <div v-if="currentIndicator" class="space-y-6">
            <!-- 指标名称 -->
            <div>
              <div class="mb-2 text-[14px] text-[#596080]">指标名称</div>
              <div class="text-[16px] font-medium text-[#1F264D]">{{ currentIndicator.name }}</div>
            </div>

            <!-- 指标分类 -->
            <div v-if="currentIndicator.category">
              <div class="mb-2 text-[14px] text-[#596080]">指标分类</div>
              <div class="text-[14px] text-[#1F264D]">{{ currentIndicator.category }}</div>
            </div>

            <!-- 分子（定义） -->
            <div>
              <div class="mb-2 text-[14px] text-[#596080]">{{ currentIndicator.calc_type === 'ratio' ? '分子' : '定义' }}</div>
              <div class="text-[14px] leading-relaxed text-[#1F264D]">
                {{ getNumeratorDescription(currentIndicator) || '暂无描述' }}
              </div>
            </div>

            <!-- 分母 -->
            <div v-if="currentIndicator.calc_type === 'ratio'">
              <div class="mb-2 text-[14px] text-[#596080]">分母</div>
              <div class="text-[14px] leading-relaxed text-[#1F264D]">
                {{ currentIndicator.denominator_desc || '暂无描述' }}
              </div>
            </div>
          </div>
          <div v-else class="flex h-full items-center justify-center text-[#596080]">
            暂无指标详情信息
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import CheckboxGroup from '@/components/ui/CheckboxGroup.vue';
import { core18Api, type IndicatorCardItem } from '@/api/core18';

// 季度选项
const quarterYearOptions = computed(() => {
  const now = new Date().getFullYear()
  return [now - 3, now - 2, now - 1, now, now + 1]
})
const quarterOptions = [
  { value: '1', label: 'Q1（一季度）' },
  { value: '2', label: 'Q2（二季度）' },
  { value: '3', label: 'Q3（三季度）' },
  { value: '4', label: 'Q4（四季度）' },
]

// 年份和月份选项
const now = new Date()
const currentYear = now.getFullYear()
const yearOptions = computed(() => {
  return Array.from({ length: 10 }, (_, i) => currentYear - 5 + i)
})
const monthOptions = [
  { value: 1, label: '1月' },
  { value: 2, label: '2月' },
  { value: 3, label: '3月' },
  { value: 4, label: '4月' },
  { value: 5, label: '5月' },
  { value: 6, label: '6月' },
  { value: 7, label: '7月' },
  { value: 8, label: '8月' },
  { value: 9, label: '9月' },
  { value: 10, label: '10月' },
  { value: 11, label: '11月' },
  { value: 12, label: '12月' }
]

// 获取当前月份
const getCurrentMonth = () => {
  const date = new Date()
  return { year: date.getFullYear(), month: date.getMonth() + 1 }
}

const currentMonth = getCurrentMonth()

// 时间模式状态（draft 和 applied）
const draftTimeMode = ref<'monthly' | 'quarterly'>('monthly')
const draftYear = ref(currentMonth.year)
const draftMonth = ref(currentMonth.month)
const draftQuarterYear = ref(currentMonth.year)
const draftQuarterNum = ref('1')

const appliedTimeMode = ref<'monthly' | 'quarterly'>('monthly')
const appliedYear = ref(currentMonth.year)
const appliedMonth = ref(currentMonth.month)
const appliedQuarterYear = ref(currentMonth.year)
const appliedQuarterNum = ref('1')

const draftHospital = ref('province')
const draftSearchKeyword = ref('')
const draftSelectedIndicators = ref<number[]>([])

const appliedHospital = ref('province')
const appliedSearchKeyword = ref('')
const appliedSelectedIndicators = ref<number[]>([])

// 指标列表和分类（从后端获取）
const indicatorList = ref<IndicatorCardItem[]>([])
const categoryList = ref<string[]>([])
const isLoading = ref(false)

// 医院列表（后端获取，格式为 [{value, label}]）
const hospitalList = ref<{ value: string; label: string }[]>([])
const hospitalOptions = computed(() => [
  { value: 'province', label: '全省' },
  ...hospitalList.value.map(h => ({ value: h.value, label: h.label }))
])

// 指标选项（用于筛选器）
const indicatorOptions = computed(() => {
  return indicatorList.value.map(ind => ({
    value: ind.id,
    label: ind.name
  }))
})

// 过滤后的指标列表
const filteredIndicators = computed(() => {
  const keyword = appliedSearchKeyword.value.trim().toLowerCase()
  const selected = appliedSelectedIndicators.value

  let filtered = indicatorList.value

  // 按关键词过滤
  if (keyword) {
    filtered = filtered.filter(ind =>
      ind.name.toLowerCase().includes(keyword)
    )
  }

  // 按选中指标过滤
  if (selected.length > 0) {
    filtered = filtered.filter(ind => selected.includes(ind.id))
  }

  return filtered
})

// 获取指标值
const getIndicatorValue = (indicator: IndicatorCardItem) => {
  if (!indicator.has_data) return '暂无数据'
  if (indicator.calc_type === 'ratio') {
    // 比值型指标：显示百分比
    return indicator.rate_percent != null ? `${indicator.rate_percent.toFixed(1)}%` : '暂无数据'
  } else {
    // 计数型指标：显示 count 字段
    return indicator.count?.toLocaleString() ?? '暂无数据'
  }
}

// 获取分子描述（比值型用 numerator_desc，统计型用 description）
const getNumeratorDescription = (indicator: IndicatorCardItem) => {
  if (indicator.calc_type === 'ratio') {
    return indicator.numerator_desc
  }
  return indicator.description
}

// 加载医院列表
async function loadHospitals() {
  try {
    const res = await core18Api.getHospitals()
    hospitalList.value = res || []
  } catch (e) {
    console.error('加载医院列表失败:', e)
  }
}

// 加载指标总览数据
async function loadOverviewData() {
  isLoading.value = true
  try {
    const res = await core18Api.getOverviewData({
      hospital_code: appliedHospital.value === 'province' ? undefined : appliedHospital.value,
      time_mode: appliedTimeMode.value,
      time_value: getAppliedTimeValue(),
      keyword: appliedSearchKeyword.value || undefined,
      category: undefined,
    })
    indicatorList.value = res?.indicators || []
    categoryList.value = res?.categories || []
  } catch (e) {
    console.error('加载指标数据失败:', e)
    indicatorList.value = []
    categoryList.value = []
  } finally {
    isLoading.value = false
  }
}

// 获取当前应用的时间值
function getAppliedTimeValue(): string {
  if (appliedTimeMode.value === 'monthly') {
    return `${appliedYear.value}-${String(appliedMonth.value).padStart(2, '0')}`
  } else {
    return `${appliedQuarterYear.value}-Q${appliedQuarterNum.value}`
  }
}

const router = useRouter()

// 指标详情抽屉状态
const drawerVisible = ref(false)
const currentIndicator = ref<IndicatorCardItem | null>(null)

function openIndicatorDetail(indicator: IndicatorCardItem) {
  currentIndicator.value = indicator
  drawerVisible.value = true
}

function closeDrawer() {
  drawerVisible.value = false
  currentIndicator.value = null
}

const handleQuery = () => {
  appliedTimeMode.value = draftTimeMode.value
  appliedYear.value = draftYear.value
  appliedMonth.value = draftMonth.value
  appliedQuarterYear.value = draftQuarterYear.value
  appliedQuarterNum.value = draftQuarterNum.value
  appliedHospital.value = draftHospital.value
  appliedSearchKeyword.value = draftSearchKeyword.value
  appliedSelectedIndicators.value = draftSelectedIndicators.value
  loadOverviewData()
}

// 跳转到指标分析台
const goToIndicatorFinal = (indicator: IndicatorCardItem) => {
  if (drawerVisible.value) {
    closeDrawer()
  }

  router.push({
    path: '/indicator-final',
    query: {
      indicatorId: String(indicator.id),
      timeMode: appliedTimeMode.value,
      timeValue: getAppliedTimeValue(),
      hospital: appliedHospital.value,
    },
  })
}

onMounted(async () => {
  console.log('总览页面初始化')
  await loadHospitals()
  await loadOverviewData()
})

onUnmounted(() => {
  drawerVisible.value = false
  currentIndicator.value = null
})
</script>
