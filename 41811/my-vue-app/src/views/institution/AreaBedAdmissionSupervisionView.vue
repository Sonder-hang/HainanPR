<template>
  <div class="flex h-full min-h-0 flex-col bg-[#F4F6F8] font-sans text-[#333333]">
    <header
      class="flex min-h-[102px] shrink-0 flex-col justify-center gap-4 border-b border-[#E5E7EB] bg-white px-4 py-4 shadow-sm sm:flex-row sm:items-center sm:justify-between sm:px-8"
    >
      <div class="flex min-w-0 flex-wrap items-center gap-3 sm:gap-4">
        <div class="hidden rounded-lg bg-[#E0E7FF] p-2 text-[#265EE6] sm:block">
          <BedDouble :size="24" />
        </div>
        <h2 class="text-[20px] font-bold tracking-tight text-[#1F2937] sm:text-[22px] lg:text-[24px]">
          机构面积床位与收治红线监管
        </h2>
        <span
          class="inline-flex items-center gap-1.5 rounded-full border border-[#FECACA] bg-[#FEF2F2] px-3 py-1 text-[11px] font-bold tracking-wide text-[#EF4444] sm:text-[12px]"
        >
          <Activity :size="14" class="animate-pulse" />
          实时抓取 HIS 在院护理医嘱中
        </span>
      </div>
      <div class="flex flex-wrap items-center gap-3 sm:gap-4">
        <div class="relative min-w-0 flex-1 sm:flex-initial">
          <Search class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-[#9CA3AF]" :size="18" />
          <input
            v-model.trim="keyword"
            type="text"
            placeholder="输入医疗机构名称检索负荷..."
            class="w-full rounded-lg border border-[#D1D5DB] bg-[#F9FAFB] py-2.5 pl-10 pr-4 text-[14px] text-[#374151] outline-none transition-all placeholder:text-[#9CA3AF] focus:border-[#265EE6] focus:bg-white focus:ring-2 focus:ring-[#265EE6]/20 sm:w-[min(340px,100%)]"
          />
        </div>
        <button
          type="button"
          class="flex shrink-0 items-center gap-2 whitespace-nowrap rounded-lg bg-[#265EE6] px-5 py-2.5 text-[14px] font-medium text-white shadow-sm shadow-[#265EE6]/30 transition-colors hover:bg-[#1E4BD8]"
        >
          <Filter :size="16" />
          高级筛选
        </button>
      </div>
    </header>

    <div class="institution-scroll flex-1 overflow-y-auto p-6 sm:p-8">
      <div class="mx-auto max-w-[1400px] space-y-6 pb-12 animate-fade-in">
        <div class="flex flex-col overflow-hidden rounded-xl border border-[#E5E7EB] bg-white shadow-sm lg:flex-row">
          <div
            class="flex flex-col justify-center border-b border-[#E5E7EB] bg-gradient-to-br from-[#F8FAFC] to-[#F1F5F9] p-8 lg:w-[45%] lg:border-b-0 lg:border-r"
          >
            <div class="mb-4 w-fit rounded-xl border border-[#C7D2FE] bg-[#EEF2FF] p-3 text-[#265EE6] shadow-sm">
              <Building2 :size="28" stroke-width="2" />
            </div>
            <h3 class="mb-3 text-[20px] font-bold text-[#1F2937]">机构超收负荷智能监测引擎</h3>
            <p class="mb-4 text-[14px] leading-relaxed text-[#4B5563]">
              部分医疗机构为追求经济效益，严重违反《医疗机构基本标准（试行）》盲目加床超收，带来极大的医疗质量与消防安全隐患。<br /><br />
              系统通过<span class="font-bold text-[#EF4444]">“理论床位上限算法”</span>与<span class="font-bold text-[#265EE6]">“HIS护理医嘱反查在院人数”</span>双重印证，实时锁定超负荷违规机构。
            </p>
          </div>

          <div class="relative flex flex-col justify-center bg-white p-8 lg:w-[55%]">
            <h4 class="mb-6 text-[14px] font-bold uppercase tracking-widest text-[#6B7280]">底层核心算法演示</h4>

            <div class="relative z-10 mx-auto flex w-full max-w-[500px] flex-col gap-5">
              <div class="flex items-center gap-4 rounded-lg border border-[#E5E7EB] bg-[#F9FAFB] p-4">
                <div class="rounded-lg border border-[#C7D2FE] bg-[#EEF2FF] p-2 text-[#265EE6]">
                  <Calculator :size="20" />
                </div>
                <div class="flex-1">
                  <p class="mb-1 text-[13px] font-medium text-[#6B7280]">Step 1. 计算法定理论床位红线</p>
                  <p class="text-[14px] font-bold text-[#1F2937]">机构总建筑面积 ÷ 机构等级平米/床标准</p>
                </div>
                <div class="text-right">
                  <p class="text-[11px] text-[#9CA3AF]">例: 1万㎡ ÷ 60㎡/床</p>
                  <p class="text-[14px] font-bold text-[#265EE6]">= 166 张上限</p>
                </div>
              </div>

              <div class="flex items-center gap-4 rounded-lg border border-[#E5E7EB] bg-[#F9FAFB] p-4">
                <div class="rounded-lg border border-[#FECACA] bg-[#FEF2F2] p-2 text-[#EF4444]">
                  <ClipboardList :size="20" />
                </div>
                <div class="flex-1">
                  <p class="mb-1 text-[13px] font-medium text-[#6B7280]">Step 2. 抓取实际在院人数</p>
                  <p class="text-[14px] font-bold leading-tight text-[#1F2937]">
                    查 HIS <span class="text-[#EF4444]">长期护理医嘱</span> 且 停止时间为空
                  </p>
                </div>
                <div class="text-right">
                  <p class="text-[11px] text-[#9CA3AF]">提取: I/II/III级及特级护理</p>
                  <p class="text-[14px] font-bold text-[#EF4444]">= 201 人在院</p>
                </div>
              </div>

              <div class="absolute bottom-[42px] right-[40px] top-[42px] -z-10 hidden w-[2px] bg-gradient-to-b from-[#265EE6] to-[#EF4444] md:block" />
              <div class="absolute right-[28px] top-1/2 z-10 hidden -translate-y-1/2 rounded-full border-2 border-[#F59E0B] bg-white p-1.5 shadow-sm md:block">
                <ArrowRightLeft class="text-[#F59E0B]" :size="16" />
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 gap-6 md:grid-cols-4">
          <div class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#265EE6]">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#265EE6]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#6B7280]">纳入监控机构总数</p>
              <div class="rounded-lg bg-[#EEF2FF] p-2 text-[#265EE6]">
                <Building2 :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#1F2937]">
              {{ kpi.monitoredOrgs.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#6B7280]">家</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#6B7280]">已配置核准建筑面积</p>
          </div>

          <div class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#265EE6]">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#265EE6]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#6B7280]">全省实时在院总人数</p>
              <div class="rounded-lg bg-[#EEF2FF] p-2 text-[#265EE6]">
                <Users :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#1F2937]">
              {{ kpi.totalInHospital.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#6B7280]">人</span>
            </p>
            <p class="mt-2 flex items-center gap-1 text-[12px] font-medium text-[#265EE6]">
              <TrendingUp :size="12" /> 较昨日新增 {{ kpi.dayDelta.toLocaleString() }} 人
            </p>
          </div>

          <div class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#EF4444]">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#EF4444]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-bold text-[#EF4444]">违规超载运行机构</p>
              <div class="rounded-lg bg-[#FEF2F2] p-2 text-[#EF4444]">
                <AlertTriangle :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#EF4444]">
              {{ kpi.overloadOrgs.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#EF4444]">家</span>
            </p>
            <p class="mt-2 text-[12px] font-bold text-[#EF4444]">已触发自动警告工单</p>
          </div>

          <div class="flex flex-col justify-center rounded-xl border border-[#002140] bg-[#001529] p-6 text-white shadow-sm">
            <p class="mb-2 text-[14px] font-medium text-[#9CA3AF]">最高超负荷峰值记录</p>
            <p class="mb-2 text-[36px] font-black leading-none text-[#EF4444]">
              {{ kpi.peakLoadPct }}<span class="text-[18px]">%</span>
            </p>
            <p class="truncate text-[12px] text-[#6B7A90]">{{ kpi.peakOrgName }}</p>
            <p class="truncate text-[12px] text-[#6B7A90]">
              上限 {{ kpi.peakLimit }} 张，实际在院 {{ kpi.peakActual }} 人
            </p>
          </div>
        </div>

        <div class="flex flex-col overflow-hidden rounded-xl border border-[#E5E7EB] bg-white shadow-sm">
          <div class="flex items-center justify-between border-b border-[#E5E7EB] bg-[#F9FAFB] p-5">
            <h3 class="flex items-center gap-2 text-[16px] font-bold text-[#1F2937]">
              <ShieldAlert class="text-[#EF4444]" :size="20" />
              面积床位超载红线违规台账
            </h3>
            <div class="flex gap-2">
              <button
                type="button"
                class="flex items-center gap-1.5 rounded border border-[#D1D5DB] bg-white px-4 py-2 text-[13px] font-medium text-[#4B5563] shadow-sm transition-colors hover:bg-[#F3F4F6]"
              >
                <Download :size="14" />
                导出整改通知单
              </button>
            </div>
          </div>

          <div class="overflow-x-auto p-0">
            <table class="w-full min-w-[960px] text-left text-[14px]">
              <thead class="border-b border-[#E5E7EB] bg-[#F3F4F6]">
                <tr>
                  <th class="w-[20%] p-4 font-semibold text-[#4B5563]">医疗机构基本信息</th>
                  <th class="w-[25%] border-l border-[#E0E7FF] bg-[#EEF2FF]/30 p-4 font-semibold text-[#4B5563]">
                    法定理论床位上限测算
                  </th>
                  <th class="w-[25%] border-l border-[#FECACA] bg-[#FEF2F2]/30 p-4 font-semibold text-[#4B5563]">
                    实时在院患者动态 (HIS抓取)
                  </th>
                  <th class="w-[15%] border-l border-[#E5E7EB] p-4 font-semibold text-[#4B5563]">智能研判结论</th>
                  <th class="w-[15%] border-l border-[#E5E7EB] p-4 text-center font-semibold text-[#4B5563]">
                    监管处理操作
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#F3F4F6]">
                <tr v-for="row in filteredRows" :key="row.id" class="group transition-colors hover:bg-[#F9FAFB]">
                  <td class="p-4">
                    <p class="text-[15px] font-bold text-[#1F2937]">{{ row.orgName }}</p>
                    <p class="mt-1.5 text-[12px] text-[#6B7280]">机构编码：{{ row.orgCode }}</p>
                    <p class="mt-0.5 text-[12px] text-[#6B7280]">
                      标准：<span class="font-bold text-[#265EE6]">{{ row.sqmPerBed }} ㎡/床</span> ({{ row.orgTypeLabel }})
                    </p>
                  </td>
                  <td class="border-l border-[#E0E7FF] bg-[#EEF2FF]/20 p-4">
                    <div class="space-y-1 text-[13px] text-[#4B5563]">
                      <p>
                        核准建筑面积：<span class="font-bold text-[#1F2937]">{{ row.areaSqm.toLocaleString() }} ㎡</span>
                      </p>
                      <div class="mt-2 inline-block rounded border border-[#C7D2FE] bg-[#EEF2FF] p-1.5 text-[12px] text-[#265EE6]">
                        算法极限：{{ row.areaSqm.toLocaleString() }} ÷ {{ row.sqmPerBed }} =
                        <span class="font-bold text-[#1F2937]">{{ row.bedLimit }}张</span>
                      </div>
                    </div>
                  </td>
                  <td class="border-l border-[#FECACA] bg-[#FEF2F2]/20 p-4">
                    <div class="space-y-1.5 text-[13px]">
                      <p class="text-[#6B7280]">当前长期护理医嘱激活数：</p>
                      <p class="text-[24px] font-black" :class="row.inHospitalTextClass">
                        {{ row.inHospital.toLocaleString() }}
                        <span class="text-[12px] font-normal" :class="row.inHospitalSubClass">人</span>
                      </p>
                    </div>
                    <div class="mt-2 flex h-2 w-full overflow-hidden rounded-full bg-slate-200">
                      <div
                        class="h-full bg-[#10B981]"
                        :style="{ width: `${barGreenPercent(row)}%` }"
                      />
                      <div
                        v-if="row.inHospital > row.bedLimit"
                        class="h-full flex-1 progress-striped"
                        :class="row.overflowBarClass"
                      />
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4">
                    <div class="flex flex-col gap-1.5">
                      <span class="w-fit rounded border px-2 py-0.5 text-[12px] font-bold" :class="row.badgeClass">
                        {{ row.verdictTitle }}
                      </span>
                      <p class="text-[12px] leading-tight" :class="row.verdictTextClass">
                        {{ row.verdictDetail }}
                      </p>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4 text-center">
                    <div v-if="row.actions.length" class="flex flex-col gap-2">
                      <button
                        v-for="(act, i) in row.actions"
                        :key="i"
                        type="button"
                        class="flex w-full items-center justify-center gap-1.5 rounded border px-3 py-1.5 text-[12px] shadow-sm transition-colors"
                        :class="act.buttonClass"
                      >
                        <component :is="act.icon" :size="14" />
                        {{ act.label }}
                      </button>
                    </div>
                    <span v-else class="text-[12px] font-medium text-[#9CA3AF]">无需操作</span>
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
import type { Component } from 'vue'
import {
  Activity,
  AlertTriangle,
  ArrowRightLeft,
  BedDouble,
  Bell,
  Building2,
  Calculator,
  ClipboardList,
  Download,
  Filter,
  Search,
  Send,
  ShieldAlert,
  TrendingUp,
  Users,
} from 'lucide-vue-next'

type LedgerAction = {
  label: string
  icon: Component
  buttonClass: string
}

type LedgerRow = {
  id: string
  orgName: string
  orgCode: string
  orgTypeLabel: string
  sqmPerBed: number
  areaSqm: number
  bedLimit: number
  inHospital: number
  verdictTitle: string
  verdictDetail: string
  badgeClass: string
  verdictTextClass: string
  inHospitalTextClass: string
  inHospitalSubClass: string
  overflowBarClass: string
  actions: LedgerAction[]
}

const keyword = ref('')

const kpi = ref({
  monitoredOrgs: 214,
  totalInHospital: 54208,
  dayDelta: 412,
  overloadOrgs: 14,
  peakLoadPct: 186,
  peakOrgName: '万宁市某精神病专科医院',
  peakLimit: 150,
  peakActual: 279,
})

const rows = ref<LedgerRow[]>([
  {
    id: '1',
    orgName: '万宁市某精神病医院',
    orgCode: '460105882',
    orgTypeLabel: '二级精神专科',
    sqmPerBed: 40,
    areaSqm: 6035,
    bedLimit: 150,
    inHospital: 279,
    verdictTitle: '严重超负荷 (186%)',
    verdictDetail: '实在院人数远超面积标准上限，存在极高消防与医疗安全隐患。',
    badgeClass: 'border-[#FECACA] bg-[#FEF2F2] text-[#EF4444]',
    verdictTextClass: 'text-[#7F1D1D]',
    inHospitalTextClass: 'text-[#EF4444]',
    inHospitalSubClass: 'text-[#991B1B]',
    overflowBarClass: 'bg-[#EF4444]',
    actions: [
      {
        label: '下发限期整改',
        icon: Bell,
        buttonClass:
          'border-[#FECACA] bg-[#FEF2F2] font-bold text-[#EF4444] hover:bg-[#EF4444] hover:text-white',
      },
      {
        label: '通报市卫健委',
        icon: Send,
        buttonClass: 'border-[#D1D5DB] bg-white font-medium text-[#4B5563] hover:bg-[#F3F4F6]',
      },
    ],
  },
  {
    id: '2',
    orgName: '儋州市某综合医院',
    orgCode: '460200311',
    orgTypeLabel: '二级综合',
    sqmPerBed: 45,
    areaSqm: 25836,
    bedLimit: 574,
    inHospital: 800,
    verdictTitle: '违规超载 (139%)',
    verdictDetail: '超出理论上限226人，违规在走廊加床收治。',
    badgeClass: 'border-[#FDE68A] bg-[#FFFBEB] text-[#D97706]',
    verdictTextClass: 'text-[#92400E]',
    inHospitalTextClass: 'text-[#F59E0B]',
    inHospitalSubClass: 'text-[#92400E]',
    overflowBarClass: 'bg-[#F59E0B]',
    actions: [
      {
        label: '下发警告函',
        icon: Bell,
        buttonClass:
          'border-[#FDE68A] bg-[#FFFBEB] font-bold text-[#D97706] hover:bg-[#D97706] hover:text-white',
      },
    ],
  },
  {
    id: '3',
    orgName: '海口某妇产科医院',
    orgCode: '460100412',
    orgTypeLabel: '二级妇产专科',
    sqmPerBed: 45,
    areaSqm: 8000,
    bedLimit: 177,
    inHospital: 110,
    verdictTitle: '合规运行 (62%)',
    verdictDetail: '床位使用率处于健康安全区间，空间充裕。',
    badgeClass: 'border-[#A7F3D0] bg-[#ECFDF5] text-[#10B981]',
    verdictTextClass: 'text-[#065F46]',
    inHospitalTextClass: 'text-[#10B981]',
    inHospitalSubClass: 'text-[#065F46]',
    overflowBarClass: '',
    actions: [],
  },
])

function barGreenPercent(row: LedgerRow) {
  if (row.inHospital <= 0) return 0
  if (row.inHospital > row.bedLimit) {
    return Math.min(100, (row.bedLimit / row.inHospital) * 100)
  }
  return Math.min(100, (row.inHospital / row.bedLimit) * 100)
}

const filteredRows = computed(() => {
  const q = keyword.value.trim()
  if (!q) return rows.value
  return rows.value.filter((r) =>
    [r.orgName, r.orgCode, r.orgTypeLabel].some((v) => v.toLowerCase().includes(q.toLowerCase())),
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

.progress-striped {
  background-image: linear-gradient(
    45deg,
    rgba(255, 255, 255, 0.25) 25%,
    transparent 25%,
    transparent 50%,
    rgba(255, 255, 255, 0.25) 50%,
    rgba(255, 255, 255, 0.25) 75%,
    transparent 75%,
    transparent
  );
  background-size: 1rem 1rem;
  animation: progress-stripes 1s linear infinite;
}

@keyframes progress-stripes {
  from {
    background-position: 1rem 0;
  }
  to {
    background-position: 0 0;
  }
}

.institution-scroll::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.institution-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.institution-scroll::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}
.institution-scroll::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>
