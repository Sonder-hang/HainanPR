<template>
  <div class="flex h-full min-h-0 flex-col bg-[#F4F6F8] font-sans text-[#333333]">
    <header
      class="flex min-h-[102px] shrink-0 flex-col justify-center gap-4 border-b border-[#E5E7EB] bg-white px-4 py-4 shadow-sm sm:flex-row sm:items-center sm:justify-between sm:px-8"
    >
      <div class="flex min-w-0 flex-wrap items-center gap-3 sm:gap-4">
        <div class="hidden rounded-lg bg-[#E0F2FE] p-2 text-[#0284C7] sm:block">
          <FileCode :size="24" />
        </div>
        <h2 class="text-[20px] font-bold tracking-tight text-[#1F2937] sm:text-[22px] lg:text-[24px]">
          限制/禁止类医疗技术一致性监管
        </h2>
        <span
          class="inline-flex items-center gap-1.5 rounded-full border border-[#BAE6FD] bg-[#F0F9FF] px-3 py-1 text-[11px] font-bold tracking-wide text-[#0369A1] sm:text-[12px]"
        >
          <Activity :size="14" class="animate-pulse" />
          病案 ICD 与 VPN 备案库实时比对中
        </span>
      </div>
      <div class="flex flex-wrap items-center gap-3 sm:gap-4">
        <div class="relative min-w-0 flex-1 sm:flex-initial">
          <Search class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-[#9CA3AF]" :size="18" />
          <input
            v-model.trim="keyword"
            type="text"
            placeholder="输入手术名称、ICD9-CM3 或医师..."
            class="w-full rounded-lg border border-[#D1D5DB] bg-[#F9FAFB] py-2.5 pl-10 pr-4 text-[14px] text-[#374151] outline-none transition-all placeholder:text-[#9CA3AF] focus:border-[#0284C7] focus:bg-white focus:ring-2 focus:ring-[#0284C7]/20 sm:w-[min(340px,100%)]"
          />
        </div>
        <button
          type="button"
          class="flex shrink-0 items-center gap-2 whitespace-nowrap rounded-lg bg-[#0284C7] px-5 py-2.5 text-[14px] font-medium text-white shadow-sm shadow-[#0284C7]/30 transition-colors hover:bg-[#0369A1]"
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
            class="flex flex-col justify-center border-b border-[#E5E7EB] bg-gradient-to-br from-[#F8FAFC] to-[#F0F9FF] p-8 lg:w-[45%] lg:border-b-0 lg:border-r"
          >
            <div class="mb-4 w-fit rounded-xl border border-[#BAE6FD] bg-[#E0F2FE] p-3 text-[#0284C7] shadow-sm">
              <Stethoscope :size="28" stroke-width="2" />
            </div>
            <h3 class="mb-3 text-[20px] font-bold text-[#1F2937]">医疗技术准入三维比对筛查引擎</h3>
            <p class="mb-4 text-[14px] leading-relaxed text-[#4B5563]">
              依据《医疗技术临床应用管理办法》，系统对高危技术实施严格准入监管：<br />
              <span class="font-bold text-[#EF4444]">禁止类技术：</span>因伦理、安全性或被淘汰等原因，<strong class="text-[#991B1B]">绝对禁止应用</strong>。<br />
              <span class="font-bold text-[#F59E0B]">限制类技术：</span>难度大、风险高，必须进行<strong class="text-[#B45309]">省级 VPN 账号严格备案</strong>后方可开展。
            </p>
          </div>

          <div class="relative flex flex-col justify-center bg-white p-8 lg:w-[55%]">
            <h4 class="mb-6 text-[14px] font-bold uppercase tracking-widest text-[#6B7280]">底层数据关联与比对机制</h4>

            <div class="relative z-10 mx-auto flex w-full max-w-[500px] flex-col gap-6">
              <div class="flex items-center gap-4 rounded-lg border border-[#E5E7EB] bg-[#F9FAFB] p-4 shadow-sm">
                <div class="rounded-lg border border-[#BAE6FD] bg-[#E0F2FE] p-2.5 text-[#0284C7]">
                  <FileText :size="20" />
                </div>
                <div class="flex-1">
                  <p class="mb-1 text-[13px] font-medium text-[#6B7280]">数据源头：住院病案首页解析</p>
                  <p class="text-[14px] font-bold leading-tight text-[#1F2937]">
                    提取 <span class="text-[#0284C7]">ICD9-CM3 手术操作编码</span> 及 <span class="text-[#0284C7]">ICD10 诊断</span>
                  </p>
                </div>
              </div>

              <div class="relative flex items-center justify-center py-2">
                <div class="absolute -z-10 h-full w-[2px] bg-gradient-to-b from-[#0284C7] to-[#F59E0B]" />
                <div class="rounded-full border-[2px] border-[#0284C7] bg-white p-2 shadow-sm">
                  <ArrowDown class="text-[#0284C7]" :size="16" />
                </div>
                <span
                  class="absolute left-[55%] rounded-full border border-[#BAE6FD] bg-[#F0F9FF] px-2 py-0.5 text-[11px] font-bold text-[#0284C7]"
                >
                  智能规则匹配
                </span>
              </div>

              <div class="flex items-center gap-4 rounded-lg border border-[#FDE68A] bg-[#FFFBEB] p-4 shadow-sm">
                <div class="rounded-lg border border-[#FCD34D] bg-[#FEF3C7] p-2.5 text-[#D97706]">
                  <ShieldCheck :size="20" />
                </div>
                <div class="flex-1">
                  <p class="mb-1 text-[13px] font-medium text-[#6B7280]">校验终端：省医学学术交流管理中心</p>
                  <p class="text-[14px] font-bold leading-tight text-[#1F2937]">
                    核对 <span class="text-[#D97706]">限制类医疗技术 VPN 备案记录</span>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 gap-6 md:grid-cols-4">
          <div class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#0284C7]">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#0284C7]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#6B7280]">全省已备案限制类技术</p>
              <div class="rounded-lg bg-[#E0F2FE] p-2 text-[#0284C7]">
                <Database :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#1F2937]">
              {{ kpi.restrictedRegistered.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#6B7280]">项/人次</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#6B7280]">涵盖心血管、器官移植等</p>
          </div>

          <div class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#10B981]">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#10B981]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#6B7280]">今日病案手术解析量</p>
              <div class="rounded-lg bg-[#ECFDF5] p-2 text-[#10B981]">
                <Activity :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#1F2937]">
              {{ kpi.todayParsed.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#6B7280]">份</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#10B981]">底层 ICD 自动提取比对完成</p>
          </div>

          <div class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#F59E0B]">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#F59E0B]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-bold text-[#D97706]">未备案违规开展预警</p>
              <div class="rounded-lg bg-[#FFFBEB] p-2 text-[#F59E0B]">
                <ShieldAlert :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#D97706]">
              {{ kpi.unregisteredWarnings.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#D97706]">起</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#D97706]">涉嫌无资质“飞刀”或越权</p>
          </div>

          <div class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#EF4444]">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#EF4444]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-bold text-[#EF4444]">禁止类技术触碰红线</p>
              <div class="rounded-lg bg-[#FEF2F2] p-2 text-[#EF4444]">
                <AlertOctagon :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#EF4444]">
              {{ kpi.bannedRedlines.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#EF4444]">起</span>
            </p>
            <p class="mt-2 text-[12px] font-bold text-[#EF4444]">存在重大伦理或淘汰风险</p>
          </div>
        </div>

        <div class="flex flex-col overflow-hidden rounded-xl border border-[#E5E7EB] bg-white shadow-sm">
          <div class="flex items-center justify-between border-b border-[#E5E7EB] bg-[#F9FAFB] p-5">
            <h3 class="flex items-center gap-2 text-[16px] font-bold text-[#1F2937]">
              <FileWarning class="text-[#EF4444]" :size="20" />
              限制类/禁止类技术违规筛查台账 (实时)
            </h3>
            <div class="flex gap-2">
              <button
                type="button"
                class="flex items-center gap-1.5 rounded border border-[#D1D5DB] bg-white px-4 py-2 text-[13px] font-medium text-[#4B5563] shadow-sm transition-colors hover:bg-[#F3F4F6]"
              >
                <Download :size="14" />
                导出准入监管线索
              </button>
            </div>
          </div>

          <div class="overflow-x-auto p-0">
            <table class="w-full min-w-[960px] text-left text-[14px]">
              <thead class="border-b border-[#E5E7EB] bg-[#F3F4F6]">
                <tr>
                  <th class="w-[18%] p-4 font-semibold text-[#4B5563]">接诊机构与科室</th>
                  <th class="w-[15%] border-l border-[#E5E7EB] p-4 font-semibold text-[#4B5563]">主刀医师信息</th>
                  <th class="w-[25%] border-l border-[#E0E7FF] bg-[#EEF2FF]/30 p-4 font-semibold text-[#4B5563]">病案首页提取 (诊断/手术)</th>
                  <th class="w-[25%] border-l border-[#FECACA] bg-[#FEF2F2]/30 p-4 font-semibold text-[#4B5563]">引擎比对结论 (VPN备案库)</th>
                  <th class="w-[17%] border-l border-[#E5E7EB] p-4 text-center font-semibold text-[#4B5563]">执法监管操作</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#F3F4F6]">
                <tr v-for="row in filteredRows" :key="row.id" class="group transition-colors hover:bg-[#F9FAFB]">
                  <td class="p-4">
                    <p class="text-[14px] font-bold text-[#1F2937]">{{ row.orgName }}</p>
                    <p class="mt-1 text-[12px] text-[#6B7280]">{{ row.deptName }}</p>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4">
                    <p class="text-[13px] font-bold text-[#1F2937]">{{ row.doctorName }}</p>
                    <p class="mt-1 text-[12px] text-[#6B7280]">{{ row.doctorMeta }}</p>
                  </td>
                  <td class="border-l border-[#E0E7FF] bg-[#EEF2FF]/20 p-4">
                    <div class="space-y-2">
                      <div v-if="row.diagnosisText" class="flex items-start gap-1">
                        <span class="mt-0.5 shrink-0 rounded bg-[#E0F2FE] px-1 py-0.5 text-[10px] text-[#0284C7]">诊断</span>
                        <p class="text-[13px] font-medium text-[#4B5563] leading-tight">
                          {{ row.diagnosisText }}
                          <span class="font-mono text-[#9CA3AF]">({{ row.icd10 }})</span>
                        </p>
                      </div>
                      <div class="flex items-start gap-1">
                        <span class="mt-0.5 shrink-0 rounded bg-[#E0F2FE] px-1 py-0.5 text-[10px] text-[#0284C7]">手术</span>
                        <p class="text-[13px] font-bold text-[#1F2937] leading-tight">
                          {{ row.surgeryText }}
                          <span class="font-mono font-normal text-[#6B7280]">({{ row.icd9 }})</span>
                        </p>
                      </div>
                    </div>
                  </td>
                  <td class="border-l border-[#FECACA] bg-[#FEF2F2]/30 p-4">
                    <div class="flex flex-col gap-1.5">
                      <span
                        class="flex w-fit items-center gap-1 rounded border px-2 py-0.5 text-[12px] font-bold"
                        :class="row.badgeClass"
                      >
                        <component :is="row.badgeIcon" :size="12" />
                        {{ row.badgeText }}
                      </span>
                      <p class="mt-0.5 text-[12px] leading-tight" :class="row.detailClass">
                        {{ row.detailText }}
                      </p>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4 text-center">
                    <button
                      type="button"
                      class="w-full rounded border px-3 py-1.5 text-[12px] font-bold shadow-sm transition-colors"
                      :class="row.actionClass"
                    >
                      {{ row.actionText }}
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
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Component } from 'vue'
import {
  Activity,
  AlertOctagon,
  AlertTriangle,
  ArrowDown,
  Database,
  Download,
  FileCode,
  FileText,
  FileWarning,
  Filter,
  Search,
  ShieldAlert,
  ShieldCheck,
  Stethoscope,
} from 'lucide-vue-next'

const keyword = ref('')

const kpi = ref({
  restrictedRegistered: 4102,
  todayParsed: 12845,
  unregisteredWarnings: 24,
  bannedRedlines: 2,
})

type LedgerRow = {
  id: string
  orgName: string
  deptName: string
  doctorName: string
  doctorMeta: string
  diagnosisText?: string
  icd10?: string
  surgeryText: string
  icd9: string
  badgeIcon: Component
  badgeText: string
  badgeClass: string
  detailText: string
  detailClass: string
  actionText: string
  actionClass: string
  keywords: string[]
}

const rows = ref<LedgerRow[]>([
  {
    id: 'case-1',
    orgName: '海口某医疗美容医院',
    deptName: '整形外科',
    doctorName: '刘*',
    doctorMeta: '执业证: 11046****',
    surgeryText: '聚丙烯酰胺水凝胶注射隆胸',
    icd9: '85.520x',
    badgeIcon: AlertOctagon,
    badgeText: '国家禁止类技术',
    badgeClass: 'border-[#FECACA] bg-[#FEF2F2] text-[#EF4444]',
    detailText: '触碰绝对红线！该材料安全性存疑，已被临床淘汰，禁止开展！',
    detailClass: 'text-[#991B1B]',
    actionText: '立案停业查处',
    actionClass: 'border-[#FECACA] bg-[#FEF2F2] text-[#EF4444] hover:bg-[#EF4444] hover:text-white',
    keywords: ['聚丙烯酰胺', '隆胸', '85.520x', '刘', '整形外科', '医疗美容'],
  },
  {
    id: 'case-2',
    orgName: '某县级人民医院',
    deptName: '心血管内科',
    doctorName: '王*华',
    doctorMeta: '副主任医师',
    surgeryText: '冠状动脉支架植入术',
    icd9: '36.0601',
    badgeIcon: ShieldAlert,
    badgeText: '国家限制类技术 (未备案)',
    badgeClass: 'border-[#FDE68A] bg-[#FFFBEB] text-[#D97706]',
    detailText: '经 VPN 备案库核实，该医师未取得该项高危介入技术省级备案培训资质。',
    detailClass: 'text-[#92400E]',
    actionText: '下发警告调查',
    actionClass: 'border-[#FDE68A] bg-[#FFFBEB] text-[#D97706] hover:bg-[#D97706] hover:text-white',
    keywords: ['冠状动脉', '支架', '36.0601', '王', '心血管', '限制类'],
  },
  {
    id: 'case-3',
    orgName: '某市民营眼科医院',
    deptName: '眼底病专科',
    doctorName: '陈*',
    doctorMeta: '主治医师',
    diagnosisText: '干眼症',
    icd10: 'H04.1',
    surgeryText: '准分子激光原位角膜磨镶术[LASIK]',
    icd9: '11.7103',
    badgeIcon: AlertTriangle,
    badgeText: '适应症与技术不匹配',
    badgeClass: 'border-[#FDE68A] bg-[#FFFBEB] text-[#D97706]',
    detailText: '虽有“角膜屈光手术”备案，但“干眼症”不符合该限制类手术指征，涉嫌过度医疗造假。',
    detailClass: 'text-[#92400E]',
    actionText: '转交医保稽核',
    actionClass: 'border-[#FDE68A] bg-[#FFFBEB] text-[#D97706] hover:bg-[#D97706] hover:text-white',
    keywords: ['LASIK', '11.7103', '干眼症', 'H04.1', '陈', '眼科'],
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

