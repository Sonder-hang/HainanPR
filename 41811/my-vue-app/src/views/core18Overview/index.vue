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
          v-model="draftQueryType"
          class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
        >
          <option value="year">按年份</option>
          <option value="month">按月份</option>
        </select>
        <select
          v-model="draftYear"
          class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
        >
          <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
        </select>
        <select
          v-if="draftQueryType === 'month'"
          v-model="draftMonth"
          class="h-8 rounded border border-[#D1D5DB] bg-white px-3 text-[14px] text-[#374151] outline-none focus:border-[#2E57E5] focus:ring-1 focus:ring-[#2E57E5]"
        >
          <option v-for="month in months" :key="month.value" :value="month.value">{{ month.label }}</option>
        </select>
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

    <!-- 指标卡片区域 -->
    <div class="flex-1 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-6 min-h-0 grid-auto-rows-[140px] items-start grid-rows-none overflow-y-auto content-start">
      <!-- 动态渲染指标卡片 -->
      <div
        v-for="key in filteredIndicators"
        :key="key"
        class="relative cursor-pointer rounded-lg bg-white p-5 shadow-sm transition-transform hover:-translate-y-1 min-h-[140px] self-start"
        @click="goToIndicatorFinal(key)"
      >
        <!-- 指标解释按钮 -->
        <button
          type="button"
          class="absolute right-2 top-2 z-10 h-6 w-6 rounded-full text-[#596080] transition-colors hover:bg-[#F2F5FA] hover:text-[#0A6EFD]"
          @click.stop="openIndicatorDetail(key)"
          title="查看指标详情"
        >
          <svg class="mx-auto h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </button>

        <div class="mb-2 text-[14px] text-[#596080]">{{ indicatorNameMap[key] }}</div>
        <div class="mb-1 text-[28px] font-bold text-[#2E57E5]">{{ getIndicatorValue(key) }}</div>
      </div>
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
          <div v-if="currentIndicatorDetail" class="space-y-6">
            <!-- 指标名称 -->
            <div>
              <div class="mb-2 text-[14px] text-[#596080]">指标名称</div>
              <div class="text-[16px] font-medium text-[#1F264D]">{{ currentIndicatorDetail.name }}</div>
            </div>

            <!-- 分子（定义） -->
            <div>
              <div v-if="currentIndicatorDetail.numerator && currentIndicatorDetail.denominator" class="mb-2 text-[14px] text-[#596080]">分子</div>
              <div v-if="!currentIndicatorDetail.denominator" class="mb-2 text-[14px] text-[#596080]">定义</div>
              <div class="text-[14px] leading-relaxed text-[#1F264D]">{{ currentIndicatorDetail.numerator }}</div>
            </div>

            <!-- 分母 -->
            <div v-if="currentIndicatorDetail.denominator">
              <div class="mb-2 text-[14px] text-[#596080]">分母</div>
              <div class="text-[14px] leading-relaxed text-[#1F264D]">{{ currentIndicatorDetail.denominator }}</div>
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
import indicatorNameData from '@/data/indicator-name.json'
import describeData from '@/data/describe.json'
import CheckboxGroup from '@/components/ui/CheckboxGroup.vue'

// 年份和月份选项
const years = [2022, 2023, 2024, 2025, 2026];
const months = [
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
];

const getPreviousMonth = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth();
  if (month === 0) {
    return { year: year - 1, month: 12 };
  } else {
    return { year, month: month };
  }
};

const previousMonth = getPreviousMonth();
const draftQueryType = ref<'year' | 'month'>('month')
const draftYear = ref(previousMonth.year);
const draftMonth = ref(previousMonth.month);
const draftHospital = ref('province')
const draftSearchKeyword = ref('');
const draftSelectedIndicators = ref<string[]>([]);

const appliedQueryType = ref<'year' | 'month'>('month')
const appliedYear = ref(previousMonth.year);
const appliedMonth = ref(previousMonth.month);
const appliedHospital = ref('province')
const appliedSearchKeyword = ref('');
const appliedSelectedIndicators = ref<string[]>([]);

const indicatorOptions = computed(() => {
  return ALL_INDICATOR_KEYS.map(key => ({
    value: key,
    label: indicatorNameMap[key] || key
  }))
})

const hospitalOptions = [
  { value: 'province', label: '全省' },
  { value: 'hospitalA', label: '医院A' },
  { value: 'hospitalB', label: '医院B' },
  { value: 'hospitalC', label: '医院C' },
  { value: 'hospitalD', label: '医院D' },
  { value: 'hospitalE', label: '医院E' },
]

const router = useRouter()

// 指标详情抽屉状态
const drawerVisible = ref(false)
const currentIndicatorDetail = ref<{ name: string; numerator: string; denominator: string } | null>(null)

// 指标详情数据
const describeList = describeData as Array<{ name: string; numerator: string; denominator: string }>

function getIndicatorDetail(key: string) {
  const indicatorName = indicatorNameMap[key]
  if (!indicatorName) return null
  return describeList.find(item => item.name === indicatorName) || null
}

function openIndicatorDetail(key: string) {
  const detail = getIndicatorDetail(key)
  if (detail) {
    currentIndicatorDetail.value = detail
    drawerVisible.value = true
  }
}

function closeDrawer() {
  drawerVisible.value = false
  currentIndicatorDetail.value = null
}

// 指标名称映射
const indicatorNameMap = indicatorNameData as Record<string, string>

/** 总览页优先展示顺序（疾病谱/预期转归不良相关与分析类指标置顶，其余保持 JSON 原顺序） */
const PRIORITY_OVERVIEW_KEYS: string[] = [
  'icd10Subcategories',
  'icd9Cm3Categories',
  'deathPatientDefinition',
  'deathDiseaseSpectrum',
  'deathSurgicalSpectrum',
  'overallMortalityRate',
  'unexpectedRehospitalizationAnalysis',
  'unplannedReturnToORAnalysis',
  'perioperativeMortality',
]

const ALL_INDICATOR_KEYS = (() => {
  const fromJson = Object.keys(indicatorNameMap)
  const rest = fromJson.filter((k) => !PRIORITY_OVERVIEW_KEYS.includes(k))
  return [...PRIORITY_OVERVIEW_KEYS.filter((k) => k in indicatorNameMap), ...rest]
})()

type IndicatorCardData =
  | { rate: string; yoy: number; mom: number }
  | { count: string; yoy: number; mom: number }
  | { coverage: string; yoy: number; mom: number }

const COUNT_INDICATORS = new Set([
  'icd10Subcategories',
  'icd9Cm3Categories',
  'deathDiseaseSpectrum',
  'deathSurgicalSpectrum',
  'deathPatientDefinition',
])

function createDefaultIndicator(key: string): IndicatorCardData {
  if (COUNT_INDICATORS.has(key)) return { count: '0', yoy: 0, mom: 0 }
  return { rate: '0%', yoy: 0, mom: 0 }
}

const indicatorsSeed = {
  unexpectedRehospitalizationAnalysis: {
    rate: '5.2%',
    yoy: -0.3,
    mom: -0.1
  },
  unplannedReturnToORAnalysis: {
    rate: '2.2%',
    yoy: -0.5,
    mom: -0.2
  },
  overallMortalityRate: {
    rate: '2.5%',
    yoy: -0.2,
    mom: 0.0
  },
  perioperativeMortality: {
    rate: '1.2%',
    yoy: -0.3,
    mom: -0.1
  },
  deathPatientDefinition: {
    count: '0',
    yoy: 0,
    mom: 0
  },
  icd9Cm3Categories: {
    count: '1,250',
    yoy: 8.5,
    mom: 2.1
  },
  icd10Subcategories: {
    count: '1,620',
    yoy: 10.2,
    mom: 1.8
  },
  deathDiseaseSpectrum: {
    count: '156',
    yoy: 5.2,
    mom: 1.3
  },
  deathSurgicalSpectrum: {
    count: '89',
    yoy: 3.8,
    mom: 0.9
  },
  antibioticProphylaxis: {
    rate: '28.5%',
    yoy: -3.6,
    mom: -0.8
  },
  surgicalComplication: {
    rate: '6.8‰',
    yoy: -0.5,
    mom: -0.2
  },
  vteIncidence: {
    rate: '3.2‰',
    yoy: -0.3,
    mom: -0.1
  },
  preoperativeDiscussionRate: {
    rate: '95%',
    yoy: 1.2,
    mom: 0.5
  },
  emergencyConsultationTimelyRate: {
    rate: '95%',
    yoy: 0.8,
    mom: 0.3
  },
  deathCaseDiscussionWithin5DaysRate: {
    rate: '90%',
    yoy: 2.0,
    mom: 0.7
  },
  criticalValueTimelyDisposalRate: {
    rate: '94%',
    yoy: 1.5,
    mom: 0.4
  },
  patientAdmissionRoundRate: {
    rate: '98%',
    yoy: 0.5,
    mom: 0.2
  },
  seniorPhysicianRoundRate: {
    rate: '92%',
    yoy: 1.0,
    mom: 0.4
  },
  regularConsultationTimelyRate: {
    rate: '88%',
    yoy: 1.5,
    mom: 0.6
  },
  regularConsultationEffectiveRate: {
    rate: '90%',
    yoy: 0.8,
    mom: 0.3
  },
  unplannedRehospitalizationSurgeryDiscussionRate: {
    rate: '85%',
    yoy: 2.0,
    mom: 0.8
  },
  unplannedRehospitalizationSurgeryDiscussionCompleteRate: {
    rate: '88%',
    yoy: 1.5,
    mom: 0.6
  },
  highCostDiscussionRate: {
    rate: '75%',
    yoy: 3.0,
    mom: 1.0
  },
  departmentDirectorPresideDeathDiscussionRate: {
    rate: '82%',
    yoy: 1.2,
    mom: 0.5
  },
  surgeonParticipationInPreoperativeDiscussionRate: {
    rate: '98%',
    yoy: 0.3,
    mom: 0.1
  },
  preoperativePlanConsistencyRate: {
    rate: '93%',
    yoy: 0.8,
    mom: 0.3
  },
  surgeonConsistencyRate: {
    rate: '95%',
    yoy: 0.5,
    mom: 0.2
  },
  surgeonTimeOverlapRate: {
    rate: '5%',
    yoy: -0.5,
    mom: -0.2
  },
  anesthesiologistTimeOverlapRate: {
    rate: '8%',
    yoy: -0.3,
    mom: -0.1
  },
  complicationRateRatio: {
    rate: '1.2',
    yoy: 0.1,
    mom: 0.0
  },
  mortalityRateRatio: {
    rate: '1.5',
    yoy: 0.2,
    mom: 0.1
  },
  autologousBloodTransfusionRate: {
    rate: '35%',
    yoy: 2.5,
    mom: 0.8
  },
  preoperativeMultidisciplinaryDiscussionRateForLevel4: {
    rate: '85%',
    yoy: 1.5,
    mom: 0.6
  },
  longTermOrderTerminationRate: {
    rate: '92%',
    yoy: 0.8,
    mom: 0.3
  },
  criticalCareSuccessRate: {
    rate: '85%',
    yoy: 1.2,
    mom: 0.5
  },
  surgicalSpecialCareDischargeRate: {
    rate: '88%',
    yoy: 0.5,
    mom: 0.2
  },
  specialAntibioticConsultationRate: {
    rate: '90%',
    yoy: 1.0,
    mom: 0.4
  },
  bloodUsageEvaluationRate: {
    rate: '95%',
    yoy: 0.5,
    mom: 0.2
  }
}

const indicators = ref<Record<string, IndicatorCardData>>(
  ALL_INDICATOR_KEYS.reduce((acc, key) => {
    acc[key] = createDefaultIndicator(key)
    return acc
  }, {} as Record<string, IndicatorCardData>),
)

for (const [key, value] of Object.entries(indicatorsSeed)) {
  if (key in indicators.value) {
    (indicators.value as any)[key] = value
  }
}

const filteredIndicators = computed(() => {
  const keyword = appliedSearchKeyword.value.trim().toLowerCase();
  const selected = appliedSelectedIndicators.value;

  let filtered = ALL_INDICATOR_KEYS;
  if (keyword) {
    filtered = filtered.filter(key => {
      const name = indicatorNameMap[key] || key;
      return name.toLowerCase().includes(keyword);
    });
  }

  if (selected.length > 0) {
    filtered = filtered.filter(key => selected.includes(key));
  }

  return filtered;
});

const getIndicatorValue = (key: string) => {
  const indicator = (indicators.value as any)[key];
  if (!indicator) return '';
  if ('rate' in indicator) return indicator.rate;
  if ('count' in indicator) return indicator.count;
  if ('coverage' in indicator) return indicator.coverage;
  return '';
};

const handleQuery = () => {
  appliedQueryType.value = draftQueryType.value
  appliedYear.value = draftYear.value
  appliedMonth.value = draftMonth.value
  appliedHospital.value = draftHospital.value
  appliedSearchKeyword.value = draftSearchKeyword.value
  appliedSelectedIndicators.value = draftSelectedIndicators.value
  updateIndicators();
};

const goToIndicatorFinal = (overviewKey: string) => {
  if (drawerVisible.value) {
    closeDrawer()
  }

  router.push({
    path: '/indicator-final',
    query: {
      indicator: overviewKey || 'icd10Subcategories',
      queryType: appliedQueryType.value,
      year: String(appliedYear.value),
      month: String(appliedMonth.value),
      hospital: appliedHospital.value,
    },
  })
}

const updateIndicators = () => {
  Object.keys(indicators.value).forEach(key => {
    const indicator = (indicators.value as any)[key]
    if ('rate' in indicator) {
      const currentRate = parseFloat(indicator.rate);
      let change, newRate;

      if (key === 'surgicalComplication' || key === 'vteIncidence') {
        change = (Math.random() - 0.5) * 0.5;
        newRate = Math.max(0, currentRate + change);
        indicator.rate = newRate.toFixed(1) + '‰';
      } else if (key === 'complicationRateRatio' || key === 'mortalityRateRatio') {
        change = (Math.random() - 0.5) * 0.2;
        newRate = Math.max(0, currentRate + change);
        indicator.rate = newRate.toFixed(1);
      } else {
        change = (Math.random() - 0.5) * 0.5;
        newRate = Math.max(0, currentRate + change);
        indicator.rate = newRate.toFixed(1) + '%';
      }
    }
    if ('count' in indicator) {
      const currentCount = parseInt(indicator.count.replace(',', ''));
      const change = Math.floor((Math.random() - 0.5) * 100);
      const newCount = Math.max(0, currentCount + change);
      indicator.count = newCount.toLocaleString();
    }
  });
};

onMounted(() => {
  console.log('总览页面初始化');
});

onUnmounted(() => {
  drawerVisible.value = false
  currentIndicatorDetail.value = null
});
</script>
