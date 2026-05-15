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
      <!-- 四大要素统计卡片 -->
      <div class="grid grid-cols-4 gap-5">
        <div
          @click="$router.push('/personnel')"
          class="bg-white rounded-[2px] border border-[#b8c9e8]/60 p-5 flex items-center shadow-sm hover:border-[#0A6EFD]/60 hover:shadow-md transition-all cursor-pointer"
        >
          <div class="w-13 h-13 rounded-full bg-blue-50 flex items-center justify-center mr-4 shrink-0">
            <Users class="w-6 h-6 text-[#0A6EFD]" />
          </div>
          <div>
            <p class="text-[12px] text-[#596080] font-medium mb-1">人员要素违规报警</p>
            <h3 class="text-[28px] font-bold text-[#0A6EFD] leading-none">
              {{ overviewData?.personnel_alerts ?? 0 }}
              <span class="text-[11px] font-normal text-[#B8BCCC]">次</span>
            </h3>
          </div>
        </div>
        <div
          @click="$router.push('/institution')"
          class="bg-white rounded-[2px] border border-[#b8c9e8]/60 p-5 flex items-center shadow-sm hover:border-purple-500/60 hover:shadow-md transition-all cursor-pointer"
        >
          <div class="w-13 h-13 rounded-full bg-purple-50 flex items-center justify-center mr-4 shrink-0">
            <Building class="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <p class="text-[12px] text-[#596080] font-medium mb-1">机构运行预警记录</p>
            <h3 class="text-[28px] font-bold text-purple-600 leading-none">
              {{ overviewData?.institution_alerts ?? 0 }}
              <span class="text-[11px] font-normal text-[#B8BCCC]">次</span>
            </h3>
          </div>
        </div>
        <div
          @click="$router.push('/technology')"
          class="bg-white rounded-[2px] border border-[#b8c9e8]/60 p-5 flex items-center shadow-sm hover:border-red-500/60 hover:shadow-md transition-all cursor-pointer"
        >
          <div class="w-13 h-13 rounded-full bg-red-50 flex items-center justify-center mr-4 shrink-0">
            <ShieldAlert class="w-6 h-6 text-red-600" />
          </div>
          <div>
            <p class="text-[12px] text-[#596080] font-medium mb-1">医疗技术高危拦截</p>
            <h3 class="text-[28px] font-bold text-red-600 leading-none">
              {{ overviewData?.technology_alerts ?? 0 }}
              <span class="text-[11px] font-normal text-[#B8BCCC]">次</span>
            </h3>
          </div>
        </div>
        <div
          @click="$router.push('/equipment')"
          class="bg-white rounded-[2px] border border-[#b8c9e8]/60 p-5 flex items-center shadow-sm hover:border-orange-500/60 hover:shadow-md transition-all cursor-pointer"
        >
          <div class="w-13 h-13 rounded-full bg-orange-50 flex items-center justify-center mr-4 shrink-0">
            <Monitor class="w-6 h-6 text-orange-600" />
          </div>
          <div>
            <p class="text-[12px] text-[#596080] font-medium mb-1">设备效能异常监测</p>
            <h3 class="text-[28px] font-bold text-orange-600 leading-none">
              {{ overviewData?.equipment_alerts ?? 0 }}
              <span class="text-[11px] font-normal text-[#B8BCCC]">次</span>
            </h3>
          </div>
        </div>
      </div>

      <!-- 四要素分布 + 实时拦截滚动 -->
      <div class="grid grid-cols-3 gap-5">
        <!-- 四要素分布 -->
        <div class="bg-white rounded-[2px] border border-[#b8c9e8]/60 p-5 shadow-sm">
          <h3 class="text-[13px] font-bold text-[#1F264D] mb-3.5">四要素预警分布</h3>
          <div class="space-y-3.5">
            <div
              v-for="item in factorStats"
              :key="item.name"
              @click="$router.push(item.route)"
              class="cursor-pointer"
            >
              <div class="flex justify-between text-[12px] mb-1">
                <span class="text-[#596080]">{{ item.name }}</span>
                <span class="font-bold hover:underline" :style="{ color: item.color }">{{ item.count }}条</span>
              </div>
              <div class="h-2 bg-[#e8eef9] rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-500 hover:opacity-80"
                  :style="{ width: `${item.percent}%`, backgroundColor: item.color }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 实时拦截滚动 -->
        <div class="col-span-2 bg-white rounded-[2px] border border-[#b8c9e8]/60 p-5 shadow-sm">
          <div class="flex items-center justify-between mb-3.5">
            <h3 class="text-[13px] font-bold text-[#1F264D] flex items-center">
              <span class="w-2 h-2 bg-red-500 rounded-full mr-2 animate-pulse"></span>
              实时拦截/预警滚动屏
            </h3>
            <span class="text-[11px] text-[#B8BCCC]">近24小时</span>
          </div>
          <div class="space-y-2.5">
            <div
              v-for="(item, i) in overviewData?.recent_alerts ?? mockAlerts"
              :key="i"
              class="flex items-center justify-between p-2.5 hover:bg-[#e8eef9]/50 rounded-[2px] border transition-colors"
              :class="item.level === 'high' ? 'border-red-200/60' : 'border-[#b8c9e8]/40'"
            >
              <div class="flex items-center gap-3">
                <span class="text-[11px] text-[#B8BCCC] font-mono">{{ formatTime(item.time) }}</span>
                <span
                  :class="['px-2 py-0.5 rounded-full text-[10px] font-medium border', item.level === 'high' ? 'bg-red-50 text-red-600 border-red-200' : 'bg-orange-50 text-orange-600 border-orange-200']"
                >
                  {{ item.level === 'high' ? '高危' : '预警' }}
                </span>
                <span class="text-[12px] font-medium text-[#1F264D]">{{ item.message }}</span>
              </div>
              <RouterLink
                :to="getNavPath(item.message)"
                class="text-[#0A6EFD] text-[11px] hover:underline font-medium"
              >前往核查</RouterLink>
            </div>
          </div>
        </div>
      </div>

      <!-- 重点预警分类统计 -->
      <div class="bg-white rounded-[2px] border border-[#b8c9e8]/60 p-5 shadow-sm">
        <h3 class="text-[13px] font-bold text-[#1F264D] mb-3.5">重点预警分类统计</h3>
        <div class="grid grid-cols-5 gap-3">
          <div
            v-for="item in overviewData?.alert_categories ?? alertCategories"
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
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { Building, Monitor, ShieldAlert, Users } from 'lucide-vue-next'
import { dashboardApi, type DashboardOverview, type FactorDistribution } from '@/api/dashboard'

const loading = ref(true)
const overviewData = ref<DashboardOverview | null>(null)

/** 四要素条数（与顶部卡片一致）；图表按条数从高到低排序，条形宽度相对最大值等比缩放 */
const factorStats = computed(() => {
  const distribution = overviewData.value?.factor_distribution ?? []
  if (!distribution.length) {
    // 兜底静态数据
    return [
      { name: '人员要素', count: 0, color: '#0A6EFD', route: '/personnel', percent: 0 },
      { name: '机构要素', count: 0, color: '#7c3aed', route: '/institution', percent: 0 },
      { name: '技术要素', count: 0, color: '#dc2626', route: '/technology', percent: 0 },
      { name: '设备要素', count: 0, color: '#ea580c', route: '/equipment', percent: 0 },
    ]
  }
  const max = Math.max(...distribution.map((x) => x.count), 1)
  return [...distribution]
    .sort((a, b) => b.count - a.count)
    .map((x) => ({
      name: x.name,
      count: x.count,
      color: x.color,
      route: x.route,
      percent: Math.round((x.count / max) * 100),
    }))
})

const mockAlerts = [
  { time: new Date().toISOString(), msg: '【技术要素】县人民医院疑似侵害未成年人高风险诊断线索。', level: 'high' },
  { time: new Date().toISOString(), msg: '【人员要素】赵伟医师25分钟内跨越30公里产生门诊处方记录。', level: 'high' },
  { time: new Date().toISOString(), msg: '【人员要素】越权开具特殊级抗生素（美罗培南）预警。', level: 'warning' },
  { time: new Date().toISOString(), msg: '【机构要素】省立第一医院单日住院收治人数超出核定床位数。', level: 'warning' },
  { time: new Date().toISOString(), msg: '【设备要素】某县人民医院CT设备阳性率异常，高达95%。', level: 'warning' },
]

const alertCategories = [
  { name: '越权开具抗生素', count: 36, color: '#dc2626', route: '/personnel?tab=r1' },
  { name: '时空轨迹异常', count: 28, color: '#7c3aed', route: '/personnel?tab=r2' },
  { name: '多点执业冲突', count: 19, color: '#2563eb', route: '/personnel?tab=r3' },
  { name: '超范围经营', count: 15, color: '#ea580c', route: '/institution?tab=r4' },
  { name: '收治能力超限', count: 23, color: '#9333ea', route: '/institution?tab=r5' },
]

function getNavPath(msg: string) {
  if (msg.includes('人员要素')) return '/personnel'
  if (msg.includes('机构要素')) return '/institution'
  if (msg.includes('技术要素')) return '/technology'
  if (msg.includes('设备要素')) return '/equipment'
  return '/dashboard'
}

function formatTime(isoString: string) {
  try {
    const d = new Date(isoString)
    return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  } catch {
    return '--:--'
  }
}

async function loadData() {
  loading.value = true
  try {
    overviewData.value = await dashboardApi.getOverview()
  } catch (e) {
    console.error('加载总览数据失败:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
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
