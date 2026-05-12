<template>
  <div class="flex h-full min-h-0 flex-col bg-[#F4F6F8] font-sans text-[#333333]">
    <header
      class="flex min-h-[102px] shrink-0 flex-col justify-center gap-4 border-b border-[#E5E7EB] bg-white px-4 py-4 shadow-sm sm:flex-row sm:items-center sm:justify-between sm:px-8"
    >
      <div class="flex min-w-0 flex-wrap items-center gap-3 sm:gap-4">
        <div class="hidden rounded-lg bg-[#FFFBEB] p-2 text-[#D97706] sm:block">
          <PieChart :size="24" />
        </div>
        <h2 class="text-[20px] font-bold tracking-tight text-[#1F2937] sm:text-[22px] lg:text-[24px]">
          单一病种诊疗结构畸形预警
        </h2>
        <span
          class="inline-flex items-center gap-1.5 rounded-full border border-[#FDE68A] bg-[#FFFBEB] px-3 py-1 text-[11px] font-bold tracking-wide text-[#D97706] sm:text-[12px]"
        >
          <Activity :size="14" class="animate-pulse" />
          全省住院病案首页实时解析中
        </span>
      </div>
      <div class="flex flex-wrap items-center gap-3 sm:gap-4">
        <div class="relative min-w-0 flex-1 sm:flex-initial">
          <Search class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-[#9CA3AF]" :size="18" />
          <input
            v-model.trim="keyword"
            type="text"
            placeholder="输入医疗机构、ICD编码或疾病名称..."
            class="w-full rounded-lg border border-[#D1D5DB] bg-[#F9FAFB] py-2.5 pl-10 pr-4 text-[14px] text-[#374151] outline-none transition-all placeholder:text-[#9CA3AF] focus:border-[#D97706] focus:bg-white focus:ring-2 focus:ring-[#D97706]/20 sm:w-[min(340px,100%)]"
          />
        </div>
        <button
          type="button"
          class="flex shrink-0 items-center gap-2 whitespace-nowrap rounded-lg bg-[#F59E0B] px-5 py-2.5 text-[14px] font-medium text-white shadow-sm shadow-[#F59E0B]/30 transition-colors hover:bg-[#D97706]"
        >
          <Filter :size="16" />
          高级筛选
        </button>
      </div>
    </header>

    <div class="technology-scroll flex-1 overflow-y-auto p-6 sm:p-8">
      <div class="mx-auto max-w-[1400px] space-y-6 pb-12 animate-fade-in">
        <div class="flex flex-col overflow-hidden rounded-xl border border-[#E5E7EB] bg-white shadow-sm lg:flex-row">
          <div
            class="flex flex-col justify-center border-b border-[#E5E7EB] bg-gradient-to-br from-[#F8FAFC] to-[#F1F5F9] p-8 lg:w-[45%] lg:border-b-0 lg:border-r"
          >
            <div class="mb-4 w-fit rounded-xl border border-[#FDE68A] bg-[#FFFBEB] p-3 text-[#D97706] shadow-sm">
              <BarChart2 :size="28" stroke-width="2" />
            </div>
            <h3 class="mb-3 text-[20px] font-bold text-[#1F2937]">诊疗结构畸形监测模型 (防骗保)</h3>
            <p class="mb-4 text-[14px] leading-relaxed text-[#4B5563]">
              依据《医疗机构校验管理办法》，个别医疗机构存在<span class="font-bold text-[#EF4444]">套用编码、下乡集中拉客骗保、统计口径造假</span>等严重违规行为。<br /><br />
              系统按月统计全省病案首页，设定法定红线：<strong class="text-[#991B1B]">连续三个月内，单一诊断(ICD10)或单一术式(ICD9-CM3)占全院总量的比例 &gt; 50%</strong>，即触发强制报警。
            </p>
          </div>

          <div class="relative flex flex-col justify-center bg-white p-8 lg:w-[55%]">
            <h4 class="mb-6 text-[14px] font-bold uppercase tracking-widest text-[#6B7280]">“3个月连续超标”预警触发机制</h4>

            <div class="relative z-10 mx-auto mt-2 flex w-full max-w-[550px] flex-col">
              <div class="absolute left-0 top-[28px] -z-10 h-[3px] w-[85%] rounded-full bg-gradient-to-r from-[#F59E0B] via-[#EF4444] to-[#991B1B]" />

              <div class="relative z-10 flex items-start justify-between">
                <div class="flex w-1/4 flex-col items-center gap-3">
                  <div class="flex h-14 w-14 items-center justify-center rounded-full border-[3px] border-[#F59E0B] bg-[#FFFBEB] shadow-sm">
                    <span class="text-[16px] font-black text-[#D97706]">&gt;50%</span>
                  </div>
                  <div class="text-center">
                    <p class="text-[13px] font-bold text-[#1F2937]">第 1 个月</p>
                    <p class="mt-1 text-[11px] font-medium text-[#6B7280]">占比超半数</p>
                  </div>
                </div>

                <div class="flex w-1/4 flex-col items-center gap-3">
                  <div class="flex h-14 w-14 items-center justify-center rounded-full border-[3px] border-[#EF4444] bg-[#FEF2F2] shadow-sm">
                    <span class="text-[16px] font-black text-[#EF4444]">&gt;50%</span>
                  </div>
                  <div class="text-center">
                    <p class="text-[13px] font-bold text-[#1F2937]">第 2 个月</p>
                    <p class="mt-1 text-[11px] font-medium text-[#6B7280]">持续高度单一</p>
                  </div>
                </div>

                <div class="relative flex w-1/4 flex-col items-center gap-3">
                  <div class="flex h-14 w-14 animate-pulse items-center justify-center rounded-full border-[4px] border-[#991B1B] bg-[#FEF2F2] shadow-[0_0_15px_rgba(153,27,27,0.4)]">
                    <span class="text-[16px] font-black text-[#991B1B]">&gt;50%</span>
                  </div>
                  <div class="absolute -top-10 whitespace-nowrap">
                    <span class="flex items-center gap-1 rounded bg-[#991B1B] px-2 py-1 text-[11px] font-bold text-white shadow-sm">
                      <AlertTriangle :size="12" /> 触发立案报警
                    </span>
                    <div class="mx-auto mt-0.5 h-0 w-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-[#991B1B]" />
                  </div>
                  <div class="text-center">
                    <p class="text-[13px] font-bold text-[#1F2937]">第 3 个月</p>
                    <p class="mt-1 text-[11px] font-bold text-[#991B1B]">锁定嫌疑机构</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 gap-6 md:grid-cols-4">
          <div class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#265EE6]">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#265EE6]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#6B7280]">全省医疗机构总数</p>
              <div class="rounded-lg bg-[#EEF2FF] p-2 text-[#265EE6]">
                <Building2 :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#1F2937]">
              {{ kpi.orgTotal.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#6B7280]">家</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#6B7280]">纳入病案首页实时分析</p>
          </div>

          <div class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#10B981]">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#10B981]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#6B7280]">本月病案首页解析量</p>
              <div class="rounded-lg bg-[#ECFDF5] p-2 text-[#10B981]">
                <FileText :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#1F2937]">
              84.5 <span class="ml-1 text-[14px] font-normal text-[#6B7280]">万份</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#10B981]">提取全部主诊断/主手术</p>
          </div>

          <div class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#EF4444]">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#EF4444]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-bold text-[#EF4444]">触发连续3月超标红线</p>
              <div class="rounded-lg bg-[#FEF2F2] p-2 text-[#EF4444]">
                <AlertOctagon :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#EF4444]">
              {{ kpi.redlineOrgs.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#EF4444]">家</span>
            </p>
            <p class="mt-2 text-[12px] font-bold text-[#EF4444]">已锁定，建议现场执法</p>
          </div>

          <div class="flex flex-col justify-center rounded-xl border border-[#002140] bg-[#001529] p-6 text-white shadow-sm">
            <p class="mb-2 text-[14px] font-medium text-[#9CA3AF]">高风险畸形病种 TOP 2</p>
            <div class="mt-2 space-y-3">
              <div>
                <p class="mb-1 text-[13px] font-bold text-white">
                  老年性白内障 <span class="text-[10px] font-normal text-[#6B7A90]">(H26.9)</span>
                </p>
                <div class="flex items-center gap-2">
                  <div class="h-1.5 w-full overflow-hidden rounded-full bg-[#002140]">
                    <div class="h-full w-[85%] bg-[#EF4444]" />
                  </div>
                  <span class="text-[11px] font-bold text-[#EF4444]">高发</span>
                </div>
              </div>
              <div>
                <p class="mb-1 text-[13px] font-bold text-white">
                  血液透析 <span class="text-[10px] font-normal text-[#6B7A90]">(39.95)</span>
                </p>
                <div class="flex items-center gap-2">
                  <div class="h-1.5 w-full overflow-hidden rounded-full bg-[#002140]">
                    <div class="h-full w-[65%] bg-[#F59E0B]" />
                  </div>
                  <span class="text-[11px] font-bold text-[#F59E0B]">频发</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="flex flex-col overflow-hidden rounded-xl border border-[#E5E7EB] bg-white shadow-sm">
          <div class="flex items-center justify-between border-b border-[#E5E7EB] bg-[#F9FAFB] p-5">
            <h3 class="flex items-center gap-2 text-[16px] font-bold text-[#1F2937]">
              <Database class="text-[#D97706]" :size="20" />
              全省医疗机构病种畸形排查线索台账
            </h3>
            <div class="flex gap-2">
              <button
                type="button"
                class="flex items-center gap-1.5 rounded border border-[#D1D5DB] bg-white px-4 py-2 text-[13px] font-medium text-[#4B5563] shadow-sm transition-colors hover:bg-[#F3F4F6]"
              >
                <Download :size="14" />
                导出专项核查名单
              </button>
            </div>
          </div>

          <div class="overflow-x-auto p-0">
            <table class="w-full min-w-[960px] text-left text-[14px]">
              <thead class="border-b border-[#E5E7EB] bg-[#F3F4F6]">
                <tr>
                  <th class="w-[18%] p-4 font-semibold text-[#4B5563]">预警医疗机构</th>
                  <th class="w-[25%] border-l border-[#E0E7FF] bg-[#EEF2FF]/30 p-4 font-semibold text-[#4B5563]">
                    高度聚焦的单一病种/术式
                  </th>
                  <th class="w-[22%] border-l border-[#FECACA] bg-[#FEF2F2]/30 p-4 font-semibold text-[#4B5563]">
                    连续3个月占比趋势
                  </th>
                  <th class="w-[20%] border-l border-[#E5E7EB] p-4 font-semibold text-[#4B5563]">系统定性分析</th>
                  <th class="w-[15%] border-l border-[#E5E7EB] p-4 text-center font-semibold text-[#4B5563]">监管操作</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#F3F4F6]">
                <tr v-for="row in filteredRows" :key="row.id" class="group transition-colors hover:bg-[#F9FAFB]">
                  <td class="p-4">
                    <p class="text-[14px] font-bold text-[#1F2937]">{{ row.orgName }}</p>
                    <p class="mt-1 text-[12px] text-[#6B7280]">机构级别：{{ row.orgLevel }}</p>
                  </td>
                  <td class="border-l border-[#E0E7FF] bg-[#EEF2FF]/20 p-4">
                    <p class="text-[13px] font-bold text-[#1F2937]">{{ row.focusName }}</p>
                    <p class="mt-1 font-mono text-[12px] text-[#6B7280]">{{ row.focusCodeLabel }}</p>
                  </td>
                  <td class="border-l border-[#FECACA] bg-[#FEF2F2]/30 p-4">
                    <div class="flex flex-col gap-1 font-mono text-[12px] text-[#4B5563]">
                      <span class="flex items-center justify-between">10月: <strong class="text-[#EF4444]">{{ row.m10 }}%</strong></span>
                      <span class="flex items-center justify-between">11月: <strong class="text-[#EF4444]">{{ row.m11 }}%</strong></span>
                      <span class="flex items-center justify-between">12月: <strong class="text-[#EF4444]">{{ row.m12 }}%</strong></span>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4">
                    <div class="flex flex-col gap-1.5">
                      <span class="w-fit rounded border px-2 py-0.5 text-[11px] font-bold" :class="row.badgeClass">
                        {{ row.badgeText }}
                      </span>
                      <p class="text-[11px] leading-tight text-[#6B7280]">{{ row.analysis }}</p>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4 text-center">
                    <button
                      v-if="row.actionText"
                      type="button"
                      class="w-full rounded border px-3 py-1.5 text-[12px] font-bold shadow-sm transition-colors"
                      :class="row.actionClass"
                    >
                      {{ row.actionText }}
                    </button>
                    <span v-else class="text-[13px] font-medium text-[#9CA3AF]">系统归档</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  Activity,
  AlertOctagon,
  BarChart2,
  Building2,
  Database,
  Download,
  FileText,
  Filter,
  PieChart,
  Search,
  AlertTriangle,
} from 'lucide-vue-next'

const keyword = ref('')

const kpi = ref({
  orgTotal: 3412,
  redlineOrgs: 6,
})

type LedgerRow = {
  id: string
  orgName: string
  orgLevel: string
  focusName: string
  focusCodeLabel: string
  m10: number
  m11: number
  m12: number
  badgeText: string
  badgeClass: string
  analysis: string
  actionText?: string
  actionClass?: string
  keywords: string[]
}

const rows = ref<LedgerRow[]>([
  {
    id: 'r1',
    orgName: '海口某康复医院',
    orgLevel: '二级',
    focusName: '脑梗死后遗症',
    focusCodeLabel: 'ICD-10: I69.3',
    m10: 52,
    m11: 55,
    m12: 58,
    badgeText: '压床挂床骗保风险',
    badgeClass: 'border-[#FECACA] bg-[#FEF2F2] text-[#EF4444]',
    analysis: '收治大量脑梗后遗症患者，可能存在无指征长期住院、挂床骗保行为。',
    actionText: '推送医保局',
    actionClass: 'border-[#FECACA] bg-[#FEF2F2] text-[#EF4444] hover:bg-[#EF4444] hover:text-white',
    keywords: ['海口', '康复', 'I69.3', '脑梗', '后遗症'],
  },
  {
    id: 'r2',
    orgName: '某镇中心卫生院',
    orgLevel: '一级',
    focusName: '急性上呼吸道感染',
    focusCodeLabel: 'ICD-10: J06.9',
    m10: 61,
    m11: 65,
    m12: 64,
    badgeText: '套用编码嫌疑',
    badgeClass: 'border-[#FDE68A] bg-[#FFFBEB] text-[#D97706]',
    analysis: '疾病谱过于单一，高度怀疑基层医师为图省事，所有感冒发烧均套用同一编码上传。',
    actionText: '下发整改督办',
    actionClass: 'border-[#FDE68A] bg-[#FFFBEB] text-[#D97706] hover:bg-[#D97706] hover:text-white',
    keywords: ['卫生院', 'J06.9', '上呼吸道', '感冒', '套用编码'],
  },
  {
    id: 'r3',
    orgName: '某县妇幼保健院',
    orgLevel: '二级',
    focusName: '剖宫产伴其他指征',
    focusCodeLabel: 'ICD-10: O82.8',
    m10: 51,
    m11: 46,
    m12: 53,
    badgeText: '专科医院正常波动',
    badgeClass: 'border-[#A7F3D0] bg-[#ECFDF5] text-[#10B981]',
    analysis: '中间月份降至安全线以下，未触发“连续三个月”红线，符合妇产专科业务特征。',
    keywords: ['妇幼', 'O82.8', '剖宫产'],
  },
])

function containsIgnoreCase(v: string, q: string) {
  return v.toLowerCase().includes(q.toLowerCase())
}

const filteredRows = computed(() => {
  const q = keyword.value.trim()
  if (!q) return rows.value
  return rows.value.filter((r) => r.keywords.some((k) => containsIgnoreCase(k, q)) || containsIgnoreCase(r.orgName, q))
})
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.5s ease-out forwards;
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.technology-scroll::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.technology-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.technology-scroll::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}
.technology-scroll::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>

