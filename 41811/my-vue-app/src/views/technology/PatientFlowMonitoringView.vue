<template>
  <div class="flex h-full min-h-0 flex-col bg-[#F4F6F8] font-sans text-[#333333]">
    <header
      class="flex min-h-[102px] shrink-0 flex-col justify-center gap-4 border-b border-[#E5E7EB] bg-white px-4 py-4 shadow-sm sm:flex-row sm:items-center sm:justify-between sm:px-8"
    >
      <div class="flex min-w-0 flex-wrap items-center gap-3 sm:gap-4">
        <div class="hidden rounded-lg bg-[#E0E7FF] p-2 text-[#265EE6] sm:block">
          <Waypoints :size="24" />
        </div>
        <h2 class="text-[20px] font-bold tracking-tight text-[#1F2937] sm:text-[22px] lg:text-[24px]">
          患者跨机构异常流向监测 (防违规导流)
        </h2>
        <span
          class="inline-flex items-center gap-1.5 rounded-full border border-[#C7D2FE] bg-[#EEF2FF] px-3 py-1 text-[11px] font-bold tracking-wide text-[#265EE6] sm:text-[12px]"
        >
          <Activity :size="14" class="animate-pulse" />
          门诊与住院轨迹时间窗比对中
        </span>
      </div>
      <div class="flex flex-wrap items-center gap-3 sm:gap-4">
        <div class="relative min-w-0 flex-1 sm:flex-initial">
          <Search class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-[#9CA3AF]" :size="18" />
          <input
            v-model.trim="keyword"
            type="text"
            placeholder="输入医师、公立机构或民营机构名称..."
            class="w-full rounded-lg border border-[#D1D5DB] bg-[#F9FAFB] py-2.5 pl-10 pr-4 text-[14px] text-[#374151] outline-none transition-all placeholder:text-[#9CA3AF] focus:border-[#265EE6] focus:bg-white focus:ring-2 focus:ring-[#265EE6]/20 sm:w-[min(340px,100%)]"
          />
        </div>
        <button
          type="button"
          class="flex shrink-0 items-center gap-2 whitespace-nowrap rounded-lg bg-[#265EE6] px-5 py-2.5 text-[14px] font-medium text-white shadow-sm shadow-[#265EE6]/30 transition-colors hover:bg-[#1E4BD8]"
        >
          <Filter :size="16" />
          多维筛选
        </button>
      </div>
    </header>

    <div class="technology-scroll flex-1 overflow-y-auto p-6 sm:p-8">
      <div class="mx-auto max-w-[1400px] space-y-6 pb-12 animate-fade-in">
        <div class="flex flex-col overflow-hidden rounded-xl border border-[#E5E7EB] bg-white shadow-sm lg:flex-row">
          <div
            class="flex flex-col justify-center border-b border-[#E5E7EB] bg-gradient-to-br from-[#F8FAFC] to-[#F1F5F9] p-8 lg:w-[45%] lg:border-b-0 lg:border-r"
          >
            <div class="mb-4 w-fit rounded-xl border border-[#C7D2FE] bg-[#EEF2FF] p-3 text-[#265EE6] shadow-sm">
              <Users :size="28" stroke-width="2" />
            </div>
            <h3 class="mb-3 text-[20px] font-bold text-[#1F2937]">公转民异常导流 (卖客) 监测模型</h3>
            <p class="mb-4 text-[14px] leading-relaxed text-[#4B5563]">
              依据《医疗机构管理条例》及行风建设要求，严厉打击公立医院医师私自将患者诱导、转介至民营医院进行高价手术或消费的违规行为。<br /><br />
              系统依托门诊与住院大数据，建立<span class="font-bold text-[#EF4444]">“跨机构流动时间窗分析规则”</span>，精准锁定同一患者短期内跨性质机构就医轨迹，反查公立医师异常流失漏斗。
            </p>
          </div>

          <div class="relative flex flex-col justify-center bg-white p-8 lg:w-[55%]">
            <h4 class="mb-6 text-[14px] font-bold uppercase tracking-widest text-[#6B7280]">时间窗轨迹交叉比对机制演示</h4>

            <div class="relative z-10 mx-auto flex w-full max-w-[550px] flex-col gap-4">
              <div class="flex items-center justify-between">
                <div class="flex w-[160px] flex-col items-center gap-2">
                  <div class="flex h-14 w-14 items-center justify-center rounded-2xl border-2 border-[#A5B4FC] bg-[#EEF2FF] text-[#265EE6] shadow-sm">
                    <Building2 :size="24" />
                  </div>
                  <div class="text-center">
                    <span class="rounded bg-[#EEF2FF] px-2 py-0.5 text-[10px] font-bold text-[#265EE6]">起点: 公立机构</span>
                    <p class="mt-1 text-[13px] font-bold text-[#1F2937]">接诊医师看诊</p>
                  </div>
                </div>

                <div class="relative flex flex-1 flex-col items-center px-2">
                  <div class="absolute left-0 top-[28px] -z-10 h-[2px] w-full -translate-y-1/2 border-t-2 border-dashed border-[#9CA3AF]" />
                  <div class="absolute left-0 top-[28px] h-2 w-2 -translate-y-1/2 animate-[ping_2s_linear_infinite] rounded-full bg-[#265EE6]" />
                  <div class="absolute right-1/4 top-[28px] h-2 w-2 -translate-y-1/2 animate-[ping_2s_linear_infinite_0.5s] rounded-full bg-[#F59E0B]" />

                  <div class="mt-1 rounded-full border border-[#D1D5DB] bg-white px-3 py-1 shadow-sm">
                    <span class="text-[12px] font-bold text-[#4B5563]">时间窗: 1-7天内</span>
                  </div>
                  <p class="mt-2 text-[10px] text-[#9CA3AF]">患者唯一标识追踪</p>
                </div>

                <div class="flex w-[160px] flex-col items-center gap-2">
                  <div class="flex h-14 w-14 items-center justify-center rounded-2xl border-2 border-[#FDE68A] bg-[#FFFBEB] text-[#D97706] shadow-sm">
                    <Activity :size="24" />
                  </div>
                  <div class="text-center">
                    <span class="rounded bg-[#FFFBEB] px-2 py-0.5 text-[10px] font-bold text-[#D97706]">终点: 民营机构</span>
                    <p class="mt-1 text-[13px] font-bold text-[#1F2937]">收治入院/手术</p>
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
              <p class="text-[14px] font-medium text-[#6B7280]">全省跨机构就诊人次</p>
              <div class="rounded-lg bg-[#EEF2FF] p-2 text-[#265EE6]">
                <Waypoints :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#1F2937]">
              {{ kpi.crossVisits.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#6B7280]">人次</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#6B7280]">本月监测总流量池</p>
          </div>

          <div class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#F59E0B]">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#F59E0B]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-bold text-[#D97706]">涉嫌公转民异常流失</p>
              <div class="rounded-lg bg-[#FFFBEB] p-2 text-[#F59E0B]">
                <Users :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#D97706]">
              {{ kpi.suspectLost.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#D97706]">人</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#D97706]">触发 7 天内转换预警</p>
          </div>

          <div class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#EF4444]">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#EF4444]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-bold text-[#EF4444]">高嫌疑导流医师人数</p>
              <div class="rounded-lg bg-[#FEF2F2] p-2 text-[#EF4444]">
                <UserX :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#EF4444]">
              {{ kpi.suspectDoctors.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#EF4444]">人</span>
            </p>
            <p class="mt-2 text-[12px] font-bold text-[#EF4444]">流失呈高度集中态势</p>
          </div>

          <div class="flex flex-col justify-center rounded-xl border border-[#002140] bg-[#001529] p-6 text-white shadow-sm">
            <p class="mb-3 text-[14px] font-medium text-[#9CA3AF]">截获高频流失方向 TOP 2</p>
            <div class="space-y-3">
              <div>
                <div class="mb-1 flex items-center justify-between text-[12px]">
                  <span class="font-bold text-white">骨科微创/关节置换</span>
                  <span class="font-bold text-[#EF4444]">128 人</span>
                </div>
                <div class="h-1.5 w-full overflow-hidden rounded-full bg-[#002140]">
                  <div class="h-full w-[80%] bg-[#EF4444]" />
                </div>
              </div>
              <div>
                <div class="mb-1 flex items-center justify-between text-[12px]">
                  <span class="font-bold text-white">妇产科/VIP分娩</span>
                  <span class="font-bold text-[#F59E0B]">95 人</span>
                </div>
                <div class="h-1.5 w-full overflow-hidden rounded-full bg-[#002140]">
                  <div class="h-full w-[60%] bg-[#F59E0B]" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div class="flex flex-col rounded-xl border border-[#E5E7EB] bg-white shadow-sm lg:col-span-1">
            <div class="flex items-center justify-between border-b border-[#E5E7EB] bg-[#F9FAFB] p-5">
              <h3 class="flex items-center gap-2 text-[16px] font-bold text-[#1F2937]">
                <TrendingDown class="text-[#EF4444]" :size="18" />
                公立医师异常流失漏斗 TOP
              </h3>
            </div>

            <div class="flex-1 space-y-0 p-0">
              <div
                v-for="(d, idx) in filteredDoctorLeaders"
                :key="d.id"
                class="border-b border-[#E5E7EB] p-5 transition-colors hover:bg-[#F9FAFB]"
              >
                <div class="mb-2 flex items-center justify-between gap-3">
                  <div class="flex min-w-0 items-center gap-3">
                    <div
                      class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full font-bold"
                      :class="
                        idx === 0
                          ? 'bg-[#FEF2F2] text-[#EF4444]'
                          : idx === 1
                            ? 'bg-[#FFFBEB] text-[#D97706]'
                            : 'bg-[#F3F4F6] text-[#4B5563]'
                      "
                    >
                      {{ idx + 1 }}
                    </div>
                    <div class="min-w-0">
                      <p class="truncate text-[14px] font-bold text-[#1F2937]">{{ d.doctorLine }}</p>
                      <p class="truncate text-[11px] text-[#6B7280]">{{ d.orgDept }}</p>
                    </div>
                  </div>
                  <p class="shrink-0 text-[20px] font-black" :class="idx === 0 ? 'text-[#EF4444]' : idx === 1 ? 'text-[#D97706]' : 'text-[#4B5563]'">
                    {{ d.lostCount }} <span class="text-[11px] font-normal text-[#9CA3AF]">人</span>
                  </p>
                </div>
                <div v-if="d.concentrationNote" class="mt-3 rounded border p-2" :class="d.noteClass">
                  <p class="text-[11px]" :class="d.noteTextClass">
                    <span class="font-bold">主要去向集中度：</span>{{ d.concentrationNote }}
                  </p>
                </div>
                <p v-else class="mt-2 text-[11px] text-[#6B7280]">{{ d.briefNote }}</p>
              </div>
            </div>
          </div>

          <div class="flex flex-col overflow-hidden rounded-xl border border-[#E5E7EB] bg-white shadow-sm lg:col-span-2">
            <div class="flex items-center justify-between border-b border-[#E5E7EB] bg-[#F9FAFB] p-5">
              <h3 class="flex items-center gap-2 text-[16px] font-bold text-[#1F2937]">
                <Search class="text-[#265EE6]" :size="18" />
                患者跨机构异常流向追溯明细台账
              </h3>
              <div class="flex gap-2">
                <button
                  type="button"
                  class="flex items-center gap-1.5 rounded border border-[#D1D5DB] bg-white px-4 py-2 text-[13px] font-medium text-[#4B5563] shadow-sm transition-colors hover:bg-[#F3F4F6]"
                >
                  <Download :size="14" />
                  导出违规线索表
                </button>
              </div>
            </div>

            <div class="overflow-x-auto p-0">
              <table class="w-full min-w-[960px] text-left text-[14px]">
                <thead class="border-b border-[#E5E7EB] bg-[#F3F4F6]">
                  <tr>
                    <th class="w-[15%] p-4 font-semibold text-[#4B5563]">患者唯一标识</th>
                    <th class="w-[30%] border-l border-[#E0E7FF] bg-[#EEF2FF]/30 p-4 font-semibold text-[#4B5563]">
                      流出源头 (公立机构门诊)
                    </th>
                    <th class="w-[15%] border-l border-[#E5E7EB] p-4 text-center font-semibold text-[#4B5563]">时间窗间隔</th>
                    <th class="w-[30%] border-l border-[#FEF3C7] bg-[#FFFBEB]/50 p-4 font-semibold text-[#4B5563]">
                      流入终端 (民营机构业务)
                    </th>
                    <th class="w-[10%] border-l border-[#E5E7EB] p-4 text-center font-semibold text-[#4B5563]">操作</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-[#F3F4F6]">
                  <tr v-for="t in filteredTraces" :key="t.id" class="group transition-colors hover:bg-[#F9FAFB]">
                    <td class="p-4">
                      <p class="text-[14px] font-bold text-[#1F2937]">{{ t.patientName }}</p>
                      <p class="mt-1 font-mono text-[11px] text-[#6B7280]">ID: {{ t.patientId }}</p>
                    </td>
                    <td class="border-l border-[#E0E7FF] bg-[#EEF2FF]/20 p-4">
                      <div class="space-y-1 text-[12px] text-[#4B5563]">
                        <p><span class="text-[#9CA3AF]">接诊机构：</span><span class="font-bold text-[#1F2937]">{{ t.fromOrg }}</span></p>
                        <p>
                          <span class="text-[#9CA3AF]">接诊医师：</span
                          ><span :class="t.doctorColorClass + ' font-bold'">{{ t.doctorName }}</span>
                        </p>
                        <p><span class="text-[#9CA3AF]">门诊时间：</span>{{ t.fromDate }}</p>
                      </div>
                    </td>
                    <td class="border-l border-[#E5E7EB] p-4 text-center">
                      <div class="flex flex-col items-center">
                        <span class="rounded-full border px-2 py-0.5 text-[11px] font-bold" :class="t.windowBadgeClass">
                          {{ t.windowBadgeText }}
                        </span>
                        <ArrowRight class="mt-1 text-[#9CA3AF]" :size="16" />
                      </div>
                    </td>
                    <td class="border-l border-[#FEF3C7] bg-[#FFFBEB]/30 p-4">
                      <div class="space-y-1 text-[12px] text-[#4B5563]">
                        <p>
                          <span class="text-[#9CA3AF]">收治机构：</span><span class="font-bold text-[#D97706]">{{ t.toOrg }}</span>
                        </p>
                        <p><span class="text-[#9CA3AF]">发生业务：</span>{{ t.toBiz }}</p>
                        <p><span class="text-[#9CA3AF]">发生时间：</span>{{ t.toDate }}</p>
                      </div>
                    </td>
                    <td class="border-l border-[#E5E7EB] p-4 text-center">
                      <button
                        type="button"
                        class="w-full rounded border border-[#D1D5DB] bg-white px-2 py-1.5 text-[11px] font-medium text-[#4B5563] shadow-sm transition-colors hover:bg-[#F3F4F6]"
                      >
                        详情
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
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
  ArrowRight,
  Building2,
  Download,
  Filter,
  Search,
  TrendingDown,
  Users,
  UserX,
  Waypoints,
} from 'lucide-vue-next'

const keyword = ref('')

const kpi = ref({
  crossVisits: 12845,
  suspectLost: 432,
  suspectDoctors: 18,
})

type DoctorLeader = {
  id: string
  doctorLine: string
  orgDept: string
  lostCount: number
  concentrationNote?: string
  noteClass?: string
  noteTextClass?: string
  briefNote?: string
  keywords: string[]
}

const doctorLeaders = ref<DoctorLeader[]>([
  {
    id: 'd1',
    doctorLine: '李*明 (主任医师)',
    orgDept: '某市属三甲医院 · 骨科',
    lostCount: 45,
    concentrationNote: '92% (41人) 均流向了同一家民营机构（海口某康骨微创专科医院），且多在门诊后 3 天内发生转移。',
    noteClass: 'border-[#FECACA] bg-[#FEF2F2]',
    noteTextClass: 'text-[#991B1B]',
    keywords: ['李', '骨科', '三甲', '海口', '康骨', '微创'],
  },
  {
    id: 'd2',
    doctorLine: '张*梅 (副主任医师)',
    orgDept: '省妇幼保健院 · 产科',
    lostCount: 32,
    concentrationNote: '100% 流向了三亚市某高端月子与妇产医疗中心，产生高额生育套餐消费。',
    noteClass: 'border-[#FDE68A] bg-[#FFFBEB]',
    noteTextClass: 'text-[#92400E]',
    keywords: ['张', '产科', '妇幼', '三亚', '月子', '妇产'],
  },
  {
    id: 'd3',
    doctorLine: '王* (主治医师)',
    orgDept: '某县人民医院 · 口腔科',
    lostCount: 18,
    briefNote: '多流向其参股的镇中心某私立齿科诊所，存在自我利益输送嫌疑。',
    keywords: ['王', '口腔', '齿科', '诊所', '参股'],
  },
])

type TraceRow = {
  id: string
  patientName: string
  patientId: string
  fromOrg: string
  doctorName: string
  doctorColorClass: string
  fromDate: string
  windowBadgeText: string
  windowBadgeClass: string
  toOrg: string
  toBiz: string
  toDate: string
  keywords: string[]
}

const traces = ref<TraceRow[]>([
  {
    id: 't1',
    patientName: '陈*国',
    patientId: '460102***891',
    fromOrg: '某市属三甲医院',
    doctorName: '李*明 (骨科)',
    doctorColorClass: 'text-[#EF4444]',
    fromDate: '2026-03-25',
    windowBadgeText: '极短: 2 天',
    windowBadgeClass: 'bg-[#FEF2F2] text-[#EF4444] border-[#FECACA]',
    toOrg: '海口某康骨微创专科医院',
    toBiz: '办理入院及微创手术',
    toDate: '2026-03-27',
    keywords: ['陈', '三甲', '骨科', '康骨', '2天', '海口'],
  },
  {
    id: 't2',
    patientName: '王*燕',
    patientId: '460200***223',
    fromOrg: '省妇幼保健院',
    doctorName: '张*梅 (产科)',
    doctorColorClass: 'text-[#D97706]',
    fromDate: '2026-03-20',
    windowBadgeText: '仅隔 5 天',
    windowBadgeClass: 'bg-[#FFFBEB] text-[#D97706] border-[#FDE68A]',
    toOrg: '三亚某高端妇产医疗中心',
    toBiz: '产检建档与预付定金',
    toDate: '2026-03-25',
    keywords: ['王', '妇幼', '产科', '三亚', '5天', '妇产'],
  },
  {
    id: 't3',
    patientName: '刘*华',
    patientId: '460105***776',
    fromOrg: '某县人民医院',
    doctorName: '王* (口腔科)',
    doctorColorClass: 'text-[#4B5563]',
    fromDate: '2026-03-28',
    windowBadgeText: '极短: 1 天',
    windowBadgeClass: 'bg-[#FEF2F2] text-[#EF4444] border-[#FECACA]',
    toOrg: '镇中心某私立齿科诊所',
    toBiz: '种植牙高值耗材收费',
    toDate: '2026-03-29',
    keywords: ['刘', '口腔', '齿科', '1天', '诊所'],
  },
])

function containsIgnoreCase(v: string, q: string) {
  return v.toLowerCase().includes(q.toLowerCase())
}

const filteredDoctorLeaders = computed(() => {
  const q = keyword.value.trim()
  if (!q) return doctorLeaders.value
  return doctorLeaders.value.filter((x) =>
    [x.doctorLine, x.orgDept, ...(x.keywords ?? [])].some((v) => containsIgnoreCase(v, q)),
  )
})

const filteredTraces = computed(() => {
  const q = keyword.value.trim()
  if (!q) return traces.value
  return traces.value.filter((x) =>
    [x.patientName, x.patientId, x.fromOrg, x.toOrg, x.doctorName, ...(x.keywords ?? [])].some((v) =>
      containsIgnoreCase(v, q),
    ),
  )
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

