<template>
  <div class="flex h-full min-h-0 flex-col bg-[#F4F6F8] font-sans text-[#333333]">
    <header
      class="flex min-h-[102px] shrink-0 flex-col justify-center gap-4 border-b border-[#E5E7EB] bg-white px-4 py-4 shadow-sm sm:flex-row sm:items-center sm:justify-between sm:px-8"
    >
      <div class="flex min-w-0 flex-wrap items-center gap-3 sm:gap-4">
        <div class="hidden rounded-lg bg-[#E0E7FF] p-2 text-[#265EE6] sm:block">
          <FlaskConical :size="24" />
        </div>
        <h2 class="text-[20px] font-bold tracking-tight text-[#1F2937] sm:text-[22px] lg:text-[24px]">
          第三方机构检验外送合规监管
        </h2>
        <span
          class="inline-flex items-center gap-1.5 rounded-full border border-[#C7D2FE] bg-[#EEF2FF] px-3 py-1 text-[11px] font-bold tracking-wide text-[#265EE6] sm:text-[12px]"
        >
          <Activity :size="14" class="animate-pulse" />
          医嘱数据与备案材料双向比对中
        </span>
      </div>
      <div class="flex flex-wrap items-center gap-3 sm:gap-4">
        <div class="relative min-w-0 flex-1 sm:flex-initial">
          <Search class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-[#9CA3AF]" :size="18" />
          <input
            v-model.trim="keyword"
            type="text"
            placeholder="输入医疗机构、检测项目或医师..."
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
              <Network :size="28" stroke-width="2" />
            </div>
            <h3 class="mb-3 text-[20px] font-bold text-[#1F2937]">外送样本检验防利益输送模型</h3>
            <p class="mb-4 text-[14px] leading-relaxed text-[#4B5563]">
              依据《公立医疗机构行风管理核心制度要点》，部分医疗机构与医师私自将标本外送至第三方检测机构（如昂贵的基因检测），存在<span class="font-bold text-[#EF4444]">利益输送及违规收费</span>的极高风险。<br /><br />
              系统建立双重监管防线：一是核验机构侧的<span class="font-bold text-[#265EE6]">合作协议与会议纪要材料</span>；二是抓取全省医嘱，追踪<span class="font-bold text-[#F59E0B]">开具高频外送检验的嫌疑医师</span>。
            </p>
          </div>

          <div class="relative flex flex-col justify-center bg-white p-8 lg:w-[55%]">
            <h4 class="mb-6 text-[14px] font-bold uppercase tracking-widest text-[#6B7280]">双重智能核验机制演示</h4>

            <div class="relative z-10 mx-auto flex w-full max-w-[500px] flex-col gap-5">
              <div class="flex items-center gap-4 rounded-lg border border-[#E5E7EB] bg-[#F9FAFB] p-4">
                <div class="rounded-lg border border-[#C7D2FE] bg-[#EEF2FF] p-2.5 text-[#265EE6]">
                  <FileCheck :size="20" />
                </div>
                <div class="flex-1">
                  <p class="mb-1 text-[13px] font-medium text-[#6B7280]">防线一：医疗机构行政备案审查</p>
                  <div class="flex flex-wrap gap-2">
                    <span class="flex items-center gap-1 rounded border border-[#A7F3D0] bg-[#ECFDF5] px-2 py-0.5 text-[12px] font-bold text-[#059669]">
                      <Check :size="12" :stroke-width="3" /> 院长办公会纪要
                    </span>
                    <span class="flex items-center gap-1 rounded border border-[#A7F3D0] bg-[#ECFDF5] px-2 py-0.5 text-[12px] font-bold text-[#059669]">
                      <Check :size="12" :stroke-width="3" /> 双方合作协议
                    </span>
                  </div>
                </div>
                <div class="hidden text-right sm:block">
                  <span class="rounded bg-[#EEF2FF] px-2 py-1 text-[12px] font-bold text-[#265EE6]">系统附件校验</span>
                </div>
              </div>

              <div class="flex items-center gap-4 rounded-lg border border-[#E5E7EB] bg-[#F9FAFB] p-4">
                <div class="rounded-lg border border-[#FECACA] bg-[#FEF2F2] p-2.5 text-[#EF4444]">
                  <TrendingUp :size="20" />
                </div>
                <div class="flex-1">
                  <p class="mb-1 text-[13px] font-medium text-[#6B7280]">防线二：医师开单医嘱数据追踪</p>
                  <p class="text-[14px] font-bold leading-tight text-[#1F2937]">提取 HIS 统计高价值外送项目异常开单排行</p>
                </div>
                <div class="hidden text-right sm:block">
                  <span class="rounded border border-[#FECACA] bg-[#FEF2F2] px-2 py-1 text-[12px] font-bold text-[#EF4444]">利益输送研判</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 gap-6 md:grid-cols-4">
          <div class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#265EE6]">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#265EE6]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#6B7280]">全省已报备外送检测项目</p>
              <div class="rounded-lg bg-[#EEF2FF] p-2 text-[#265EE6]">
                <FlaskConical :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#1F2937]">
              {{ kpi.registeredItems.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#6B7280]">项</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#6B7280]">包含基因检测、特殊病理等</p>
          </div>

          <div class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#10B981]">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#10B981]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#6B7280]">涉及承接第三方机构</p>
              <div class="rounded-lg bg-[#ECFDF5] p-2 text-[#10B981]">
                <Building2 :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#1F2937]">
              {{ kpi.thirdPartyLabs.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#6B7280]">家</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#10B981]">资质已由省级平台认证确认</p>
          </div>

          <div class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#F59E0B]">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#F59E0B]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-bold text-[#D97706]">合规备案材料缺失预警</p>
              <div class="rounded-lg bg-[#FFFBEB] p-2 text-[#F59E0B]">
                <FileWarning :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#D97706]">
              {{ kpi.missingDocsOrgs.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#D97706]">家机构</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#D97706]">缺协议或会议纪要，涉违规</p>
          </div>

          <div class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#EF4444]">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#EF4444]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-bold text-[#EF4444]">异常高频开单医师线索</p>
              <div class="rounded-lg bg-[#FEF2F2] p-2 text-[#EF4444]">
                <ShieldAlert :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#EF4444]">
              {{ kpi.suspectDoctors.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#EF4444]">人</span>
            </p>
            <p class="mt-2 text-[12px] font-bold text-[#EF4444]">个人开单量占全院该项目超40%</p>
          </div>
        </div>

        <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div class="flex flex-col rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm">
            <div class="mb-6 flex items-center justify-between border-b border-[#E5E7EB] pb-4">
              <h3 class="flex items-center gap-2 text-[16px] font-bold text-[#1F2937]">
                <FileText class="text-[#F59E0B]" :size="18" />
                机构外送备案合规性审查 (预警项)
              </h3>
            </div>

            <div class="space-y-4">
              <div
                v-for="item in filteredOrgAudits"
                :key="item.id"
                class="rounded-lg border p-4 transition-colors"
                :class="
                  item.status === 'violation'
                    ? 'border-[#FDE68A] bg-[#FFFBEB]/50 hover:bg-[#FFFBEB]'
                    : 'border-[#E5E7EB] bg-[#F9FAFB] hover:bg-slate-50'
                "
              >
                <div class="mb-3 flex items-start justify-between">
                  <div>
                    <p class="text-[14px] font-bold text-[#1F2937]">{{ item.orgName }}</p>
                    <p class="mt-0.5 text-[12px] text-[#6B7280]">
                      外送项目：<span class="font-bold text-[#1F2937]">{{ item.itemName }}</span>
                    </p>
                    <p class="mt-0.5 text-[12px] text-[#6B7280]">委托第三方：{{ item.thirdPartyName }}</p>
                  </div>
                  <span
                    class="rounded border px-2 py-0.5 text-[11px] font-bold"
                    :class="
                      item.status === 'violation'
                        ? 'border-[#FECACA] bg-[#FEF2F2] text-[#EF4444]'
                        : 'border-[#FDE68A] bg-[#FFFBEB] text-[#D97706]'
                    "
                  >
                    {{ item.status === 'violation' ? '未满足要求' : '异常预警' }}
                  </span>
                </div>
                <div class="flex flex-col gap-2 rounded border border-[#E5E7EB] bg-white p-3">
                  <div class="flex items-center justify-between text-[13px]">
                    <span class="text-[#4B5563]">院长办公会/党委会纪要：</span>
                    <span
                      class="flex items-center gap-1 font-bold"
                      :class="item.minutesOk ? 'text-[#10B981]' : 'text-[#EF4444]'"
                    >
                      <component :is="item.minutesOk ? Check : X" :size="14" :stroke-width="3" />
                      {{ item.minutesOk ? '已上传' : '未上传' }}
                    </span>
                  </div>
                  <div class="flex items-center justify-between text-[13px]">
                    <span class="text-[#4B5563]">双方业务合作协议：</span>
                    <span
                      v-if="!item.agreementLink"
                      class="flex items-center gap-1 font-bold text-[#EF4444]"
                    >
                      <X :size="14" :stroke-width="3" />
                      {{ item.agreementStatusText }}
                    </span>
                    <a
                      v-else
                      href="#"
                      class="flex items-center gap-1 font-bold text-[#265EE6] hover:underline"
                    >
                      <Paperclip :size="14" /> {{ item.agreementStatusText }}
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="flex flex-col overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm">
            <div class="mb-6 flex items-center justify-between border-b border-[#E5E7EB] pb-4">
              <h3 class="flex items-center gap-2 text-[16px] font-bold text-[#1F2937]">
                <TrendingUp class="text-[#EF4444]" :size="18" />
                外送检测畸高开单医师 (防回扣嫌疑)
              </h3>
            </div>

            <div class="space-y-5">
              <div
                v-for="doc in filteredDoctors"
                :key="doc.id"
                class="relative border-l-[3px] pl-4"
                :class="doc.level === 'high' ? 'border-[#EF4444]' : 'border-[#F59E0B]'"
              >
                <div class="mb-2 flex items-end justify-between gap-4">
                  <div class="min-w-0">
                    <p class="truncate text-[15px] font-bold text-[#1F2937]">
                      {{ doc.doctorName }}
                      <span class="ml-2 text-[12px] font-normal text-[#6B7280]">{{ doc.orgDept }}</span>
                    </p>
                    <p class="mt-1 truncate text-[12px] text-[#6B7280]">
                      关联高频外送项目: <span class="font-medium text-[#1F2937]">{{ doc.itemName }}</span>
                    </p>
                    <p class="truncate text-[12px] text-[#6B7280]">
                      关联承接第三方: <span class="font-medium text-[#1F2937]">{{ doc.thirdPartyName }}</span>
                    </p>
                  </div>
                  <div class="shrink-0 text-right">
                    <p class="text-[20px] font-black" :class="doc.level === 'high' ? 'text-[#EF4444]' : 'text-[#F59E0B]'">
                      {{ doc.monthCount }}
                      <span class="text-[12px] font-normal text-[#9CA3AF]">单 / 月</span>
                    </p>
                  </div>
                </div>
                <div class="mb-1 h-[8px] w-full overflow-hidden rounded-full bg-[#F3F4F6]">
                  <div
                    class="h-full"
                    :class="doc.level === 'high' ? 'bg-[#EF4444]' : 'bg-[#F59E0B]'"
                    :style="{ width: `${doc.sharePct}%` }"
                  />
                </div>
                <p class="text-[11px] font-bold" :class="doc.level === 'high' ? 'text-[#EF4444]' : 'text-[#D97706]'">
                  研判线索：{{ doc.clue }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div class="flex flex-col overflow-hidden rounded-xl border border-[#E5E7EB] bg-white shadow-sm">
          <div class="flex items-center justify-between border-b border-[#E5E7EB] bg-[#F9FAFB] p-5">
            <h3 class="flex items-center gap-2 text-[16px] font-bold text-[#1F2937]">
              <Database class="text-[#265EE6]" :size="20" />
              全省委托第三方检测管理明细台账
            </h3>
            <div class="flex gap-2">
              <button
                type="button"
                class="flex items-center gap-1.5 rounded border border-[#D1D5DB] bg-white px-4 py-2 text-[13px] font-medium text-[#4B5563] shadow-sm transition-colors hover:bg-[#F3F4F6]"
              >
                <Download :size="14" />
                导出违规督办单
              </button>
            </div>
          </div>

          <div class="overflow-x-auto p-0">
            <table class="w-full min-w-[960px] text-left text-[14px]">
              <thead class="border-b border-[#E5E7EB] bg-[#F3F4F6]">
                <tr>
                  <th class="w-[20%] p-4 font-semibold text-[#4B5563]">委托医疗机构</th>
                  <th class="w-[25%] border-l border-[#E0E7FF] bg-[#EEF2FF]/30 p-4 font-semibold text-[#4B5563]">外送检验项目 / 第三方机构</th>
                  <th class="w-[20%] border-l border-[#E5E7EB] p-4 font-semibold text-[#4B5563]">备案材料审查状态</th>
                  <th class="w-[20%] border-l border-[#E5E7EB] p-4 font-semibold text-[#4B5563]">开单数量异常监控</th>
                  <th class="w-[15%] border-l border-[#E5E7EB] p-4 text-center font-semibold text-[#4B5563]">处理操作</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#F3F4F6]">
                <tr v-for="row in filteredLedgerRows" :key="row.id" class="group transition-colors hover:bg-[#F9FAFB]">
                  <td class="p-4">
                    <p class="text-[14px] font-bold text-[#1F2937]">{{ row.orgName }}</p>
                    <p class="mt-1 text-[12px] text-[#6B7280]">核准科目：{{ row.approvedSubject }}</p>
                  </td>
                  <td class="border-l border-[#E0E7FF] bg-[#EEF2FF]/20 p-4">
                    <p class="text-[13px] font-bold text-[#1F2937]">{{ row.itemName }}</p>
                    <p class="mt-1 text-[12px] text-[#6B7280]">承接方：{{ row.thirdPartyName }}</p>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4" :class="row.docsStatus === 'missing' ? 'bg-[#FEF2F2]/30' : ''">
                    <div class="flex flex-col gap-1.5 text-[12px]">
                      <span class="flex items-center gap-1" :class="row.minutesOk ? 'font-medium text-[#10B981]' : 'font-bold text-[#EF4444]'">
                        <component :is="row.minutesOk ? Check : X" :size="14" :stroke-width="3" />
                        {{ row.minutesOk ? '会议纪要已传' : '缺院级会议纪要' }}
                      </span>
                      <span
                        v-if="row.agreementOk"
                        class="flex items-center gap-1 font-medium text-[#265EE6] hover:underline"
                      >
                        <Paperclip :size="14" /> 查看合作协议
                      </span>
                      <span
                        v-else
                        class="flex items-center gap-1 font-bold text-[#EF4444]"
                      >
                        <X :size="14" :stroke-width="3" /> 缺业务合作协议
                      </span>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4" :class="row.orderStatus === 'spike' ? 'bg-[#FEF2F2]/30' : ''">
                    <span
                      class="rounded border px-2 py-0.5 text-[12px] font-bold"
                      :class="
                        row.orderStatus === 'ok'
                          ? 'border-[#A7F3D0] bg-[#ECFDF5] text-[#10B981]'
                          : row.orderStatus === 'spike'
                            ? 'border-[#FECACA] bg-[#FEF2F2] text-[#EF4444]'
                            : 'border-[#D1D5DB] bg-[#F3F4F6] text-[#6B7280]'
                      "
                    >
                      {{ row.orderBadgeText }}
                    </span>
                    <p class="mt-1.5 text-[11px]" :class="row.orderStatus === 'spike' ? 'font-bold leading-tight text-[#991B1B]' : 'text-[#6B7280]'">
                      {{ row.orderDetail }}
                    </p>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4 text-center">
                    <button
                      v-if="row.actionButton"
                      type="button"
                      class="w-full rounded border px-3 py-1.5 text-[12px] font-bold shadow-sm transition-colors"
                      :class="row.actionButton.class"
                    >
                      {{ row.actionButton.label }}
                    </button>
                    <span v-else class="text-[13px] font-medium text-[#9CA3AF]">合规执行中</span>
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
  Building2,
  Check,
  Database,
  Download,
  FileCheck,
  FileText,
  FileWarning,
  Filter,
  FlaskConical,
  Network,
  Paperclip,
  Search,
  ShieldAlert,
  TrendingUp,
  X,
} from 'lucide-vue-next'

const keyword = ref('')

const kpi = ref({
  registeredItems: 2184,
  thirdPartyLabs: 67,
  missingDocsOrgs: 12,
  suspectDoctors: 8,
})

type OrgAuditStatus = 'violation' | 'warning'
type OrgAuditItem = {
  id: string
  orgName: string
  itemName: string
  thirdPartyName: string
  status: OrgAuditStatus
  minutesOk: boolean
  agreementLink?: string
  agreementStatusText: string
}

const orgAudits = ref<OrgAuditItem[]>([
  {
    id: 'audit-1',
    orgName: '某县级中医院',
    itemName: '全外显子组测序 (WES)',
    thirdPartyName: '华大基因检测中心',
    status: 'violation',
    minutesOk: false,
    agreementStatusText: '已过期 (超6个月)',
  },
  {
    id: 'audit-2',
    orgName: '海口某肿瘤专科医院',
    itemName: '肿瘤靶向用药基因检测 (112基因)',
    thirdPartyName: '金域医学检验所',
    status: 'warning',
    minutesOk: false,
    agreementLink: '#',
    agreementStatusText: '查阅附件 (2025版)',
  },
])

type DoctorLevel = 'high' | 'medium'
type DoctorItem = {
  id: string
  doctorName: string
  orgDept: string
  itemName: string
  thirdPartyName: string
  monthCount: number
  sharePct: number
  level: DoctorLevel
  clue: string
}

const doctors = ref<DoctorItem[]>([
  {
    id: 'doc-1',
    doctorName: '张*医师',
    orgDept: '省某三甲医院 · 肿瘤内科',
    itemName: 'PD-L1 伴随诊断检测',
    thirdPartyName: '某某生物科技有限公司',
    monthCount: 125,
    sharePct: 85,
    level: 'high',
    clue: '该医师个人开单量占该院该项目总外送量的 85%，涉嫌定向利益输送。',
  },
  {
    id: 'doc-2',
    doctorName: '李*华',
    orgDept: '海口某综合医院 · 优生优育科',
    itemName: '无创产前DNA检测 (NIPT)',
    thirdPartyName: '贝瑞基因',
    monthCount: 84,
    sharePct: 62,
    level: 'medium',
    clue: '个人开单量占科室外送总量的 62%，建议核查处方合理性与指征。',
  },
])

type LedgerDocsStatus = 'ok' | 'missing'
type LedgerOrderStatus = 'ok' | 'normal' | 'spike'
type LedgerRow = {
  id: string
  orgName: string
  approvedSubject: string
  itemName: string
  thirdPartyName: string
  docsStatus: LedgerDocsStatus
  minutesOk: boolean
  agreementOk: boolean
  orderStatus: LedgerOrderStatus
  orderBadgeText: string
  orderDetail: string
  actionButton?: { label: string; class: string }
}

const ledgerRows = ref<LedgerRow[]>([
  {
    id: 'ledger-1',
    orgName: '海南省某三甲医院',
    approvedSubject: '病理科',
    itemName: '组织病理学特殊染色',
    thirdPartyName: '金域医学检验中心',
    docsStatus: 'ok',
    minutesOk: true,
    agreementOk: true,
    orderStatus: 'ok',
    orderBadgeText: '无畸高集中开单',
    orderDetail: '本月共计: 34 单 (分布均匀)',
  },
  {
    id: 'ledger-2',
    orgName: '某县级中医院',
    approvedSubject: '医学检验科',
    itemName: '全外显子组测序 (WES)',
    thirdPartyName: '某生物检测科技公司',
    docsStatus: 'missing',
    minutesOk: false,
    agreementOk: false,
    orderStatus: 'normal',
    orderBadgeText: '开单量正常',
    orderDetail: '本月共计: 8 单',
    actionButton: {
      label: '锁定系统计费',
      class: 'border-[#FECACA] bg-[#FEF2F2] text-[#EF4444] hover:bg-[#EF4444] hover:text-white',
    },
  },
  {
    id: 'ledger-3',
    orgName: '某省属三甲综合医院',
    approvedSubject: '肿瘤内科',
    itemName: '肿瘤多基因测序套餐',
    thirdPartyName: '燃石医学',
    docsStatus: 'ok',
    minutesOk: true,
    agreementOk: true,
    orderStatus: 'spike',
    orderBadgeText: '集中畸高开单',
    orderDetail: '王* 医师开出 112 单，占科室该项目总量的 92%',
    actionButton: {
      label: '下发驻院纪检',
      class: 'border-[#FDE68A] bg-[#FFFBEB] text-[#D97706] hover:bg-[#D97706] hover:text-white',
    },
  },
])

function containsIgnoreCase(value: string, q: string) {
  return value.toLowerCase().includes(q.toLowerCase())
}

const filteredOrgAudits = computed(() => {
  const q = keyword.value.trim()
  if (!q) return orgAudits.value
  return orgAudits.value.filter((x) => [x.orgName, x.itemName, x.thirdPartyName].some((v) => containsIgnoreCase(v, q)))
})

const filteredDoctors = computed(() => {
  const q = keyword.value.trim()
  if (!q) return doctors.value
  return doctors.value.filter((x) =>
    [x.doctorName, x.orgDept, x.itemName, x.thirdPartyName].some((v) => containsIgnoreCase(v, q)),
  )
})

const filteredLedgerRows = computed(() => {
  const q = keyword.value.trim()
  if (!q) return ledgerRows.value
  return ledgerRows.value.filter((x) =>
    [x.orgName, x.approvedSubject, x.itemName, x.thirdPartyName].some((v) => containsIgnoreCase(v, q)),
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
