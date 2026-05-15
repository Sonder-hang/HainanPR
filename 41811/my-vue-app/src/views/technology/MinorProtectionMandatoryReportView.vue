<template>
  <div class="flex h-full min-h-0 flex-col bg-[#F4F6F8] font-sans text-[#333333]">
    <header
      class="flex min-h-[102px] shrink-0 flex-col justify-center gap-4 border-b border-[#E5E7EB] bg-white px-4 py-4 shadow-sm sm:flex-row sm:items-center sm:justify-between sm:px-8"
    >
      <div class="flex min-w-0 flex-wrap items-center gap-3 sm:gap-4">
        <div class="hidden rounded-lg bg-[#FFE4E6] p-2 text-[#E11D48] sm:block">
          <Baby :size="24" />
        </div>
        <h2 class="text-[20px] font-bold tracking-tight text-[#1F2937] sm:text-[22px] lg:text-[24px]">
          侵害未成年人强制报告协同监管
        </h2>
        <span
          class="inline-flex items-center gap-1.5 rounded-full border border-[#FECACA] bg-[#FEF2F2] px-3 py-1 text-[11px] font-bold tracking-wide text-[#E11D48] sm:text-[12px]"
        >
          <Activity :size="14" class="animate-pulse" />
          全省病案与诊断数据实时侦测中
        </span>
      </div>
      <div class="flex flex-wrap items-center gap-3 sm:gap-4">
        <div class="relative min-w-0 flex-1 sm:flex-initial">
          <Search class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-[#9CA3AF]" :size="18" />
          <input
            v-model.trim="keyword"
            type="text"
            placeholder="输入患者信息、诊断或医疗机构..."
            class="w-full rounded-lg border border-[#D1D5DB] bg-[#F9FAFB] py-2.5 pl-10 pr-4 text-[14px] text-[#374151] outline-none transition-all placeholder:text-[#9CA3AF] focus:border-[#E11D48] focus:bg-white focus:ring-2 focus:ring-[#E11D48]/20 sm:w-[min(340px,100%)]"
          />
        </div>
        <button
          type="button"
          class="flex shrink-0 items-center gap-2 whitespace-nowrap rounded-lg bg-[#E11D48] px-5 py-2.5 text-[14px] font-medium text-white shadow-sm shadow-[#E11D48]/30 transition-colors hover:bg-[#BE123C]"
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
            class="flex flex-col justify-center border-b border-[#E5E7EB] bg-gradient-to-br from-[#FFF1F2] to-[#FFE4E6]/30 p-8 lg:w-[40%] lg:border-b-0 lg:border-r"
          >
            <div class="mb-4 w-fit rounded-xl border border-[#FECACA] bg-[#FEF2F2] p-3 text-[#E11D48] shadow-sm">
              <ShieldAlert :size="28" stroke-width="2" />
            </div>
            <h3 class="mb-3 text-[20px] font-bold text-[#1F2937]">未成年人侵害强制报告模型</h3>
            <p class="mb-4 text-[14px] leading-relaxed text-[#4B5563]">
              依据《未成年人保护法》及强制报告制度，医疗机构在接诊中发现疑似侵害未成年人线索时必须上报。<br /><br />
              系统对全省 <span class="font-bold text-[#E11D48]">年龄 &lt; 18 周岁</span> 的就诊记录进行实时筛查，一旦匹配到<span class="font-bold text-[#E11D48]">“高风险诊断ICD10编码库”</span>，将强制锁定医生界面要求下达结论，并同步预警至公安与卫健委。
            </p>
          </div>

          <div class="relative flex flex-col justify-center bg-white p-8 lg:w-[60%]">
            <h4 class="mb-6 text-[14px] font-bold uppercase tracking-widest text-[#6B7280]">
              “智能筛查 ➔ 强制呈报 ➔ 公安联动”机制
            </h4>

            <div class="relative z-10 mx-auto flex w-full max-w-[650px] flex-col gap-4">
              <div class="flex items-center justify-between">
                <div class="flex w-[140px] flex-col items-center gap-2">
                  <div class="flex h-14 w-14 items-center justify-center rounded-2xl border-2 border-[#A5B4FC] bg-[#EEF2FF] text-[#265EE6] shadow-sm">
                    <Users :size="24" />
                  </div>
                  <div class="text-center">
                    <span class="rounded bg-[#EEF2FF] px-2 py-0.5 text-[10px] font-bold text-[#265EE6]">前置条件</span>
                    <p class="mt-1 text-[12px] font-bold text-[#1F2937]">年龄 &lt; 18周岁</p>
                  </div>
                </div>

                <div class="relative flex flex-1 flex-col items-center px-2">
                  <div class="absolute left-0 top-[28px] -z-10 h-[2px] w-full -translate-y-1/2 border-t-2 border-dashed border-[#9CA3AF]" />
                  <div class="mt-1 rounded-full border-2 border-[#F59E0B] bg-[#FFFBEB] p-2 shadow-[0_0_10px_rgba(245,158,11,0.3)]">
                    <Database class="text-[#D97706]" :size="18" />
                  </div>
                  <p class="mt-2 text-[11px] font-bold text-[#D97706]">匹配高风险ICD10库</p>
                  <p class="text-[10px] text-[#9CA3AF]">性病/损伤/妊娠流产</p>
                </div>

                <div class="relative flex flex-1 flex-col items-center px-2">
                  <div class="absolute left-0 top-[28px] -z-10 h-[2px] w-full -translate-y-1/2 border-t-2 border-dashed border-[#9CA3AF]" />
                  <div class="absolute left-1/4 top-[28px] h-2 w-2 -translate-y-1/2 animate-[ping_1.5s_linear_infinite] rounded-full bg-[#E11D48]" />
                  <div class="mt-1 rounded-full border-2 border-[#E11D48] bg-[#FEF2F2] p-2 shadow-[0_0_10px_rgba(225,29,72,0.3)]">
                    <AlertOctagon class="text-[#E11D48]" :size="18" />
                  </div>
                  <p class="mt-2 text-[11px] font-bold text-[#E11D48]">HIS强制弹窗</p>
                  <p class="text-[10px] text-[#9CA3AF]">要求医师提交结论</p>
                </div>

                <div class="flex w-[140px] flex-col items-center gap-2">
                  <div class="flex h-14 w-14 items-center justify-center rounded-2xl border-2 border-[#FECACA] bg-[#E11D48] text-white shadow-sm">
                    <ShieldAlert :size="24" />
                  </div>
                  <div class="text-center">
                    <span class="rounded bg-[#FEF2F2] px-2 py-0.5 text-[10px] font-bold text-[#E11D48]">疑似侵害线索</span>
                    <p class="mt-1 text-[12px] font-bold text-[#1F2937]">一键推送公安系统</p>
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
              <p class="text-[14px] font-medium text-[#6B7280]">全省未成年人就诊量</p>
              <div class="rounded-lg bg-[#EEF2FF] p-2 text-[#265EE6]">
                <Baby :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#1F2937]">
              {{ kpi.minorVisits.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#6B7280]">人次</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#6B7280]">本月累计扫描排查基数</p>
          </div>

          <div class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#F59E0B]">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#F59E0B]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-bold text-[#D97706]">触发高风险 ICD 预警</p>
              <div class="rounded-lg bg-[#FFFBEB] p-2 text-[#F59E0B]">
                <AlertTriangle :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#D97706]">
              {{ kpi.riskAlerts.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#D97706]">起</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#D97706]">已全部冻结医师系统要求确认</p>
          </div>

          <div class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#10B981]">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#10B981]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-bold text-[#10B981]">医师研判排除嫌疑</p>
              <div class="rounded-lg bg-[#ECFDF5] p-2 text-[#10B981]">
                <CheckCircle2 :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#10B981]">
              {{ kpi.excluded.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#10B981]">起</span>
            </p>
            <p class="mt-2 text-[12px] font-bold text-[#10B981]">确认为正常病理/生理现象</p>
          </div>

          <div class="group relative overflow-hidden rounded-xl border border-[#FECACA] bg-[#FEF2F2] p-6 shadow-sm transition-colors hover:border-[#E11D48]">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#E11D48]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-bold text-[#E11D48]">疑似侵害移交公安机关</p>
              <div class="rounded-lg bg-[#E11D48] p-2 text-white shadow-sm">
                <ShieldAlert :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#E11D48]">
              {{ kpi.transferred.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#E11D48]">起</span>
            </p>
            <p class="mt-2 text-[12px] font-bold text-[#E11D48]">已完成线索与物证同步</p>
          </div>
        </div>

        <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div class="flex flex-col rounded-xl border border-[#E5E7EB] bg-white shadow-sm lg:col-span-1">
            <div class="flex items-center justify-between border-b border-[#E5E7EB] bg-[#F9FAFB] p-5">
              <h3 class="flex items-center gap-2 text-[16px] font-bold text-[#1F2937]">
                <Database class="text-[#265EE6]" :size="18" />
                高风险诊断预警规则库
              </h3>
            </div>

            <div class="flex-1 space-y-4 p-5">
              <div class="rounded-lg border border-[#E5E7EB] bg-white p-4 shadow-sm">
                <div class="mb-2 flex items-center gap-2">
                  <span class="flex h-6 w-6 items-center justify-center rounded-full bg-[#EEF2FF] text-[12px] font-bold text-[#265EE6]">1</span>
                  <h4 class="font-bold text-[#1F2937]">性病方向</h4>
                </div>
                <div class="flex flex-wrap gap-2 text-[12px]">
                  <span class="rounded bg-[#F3F4F6] px-2 py-1 text-[#4B5563]">A50-A53 梅毒</span>
                  <span class="rounded bg-[#F3F4F6] px-2 py-1 text-[#4B5563]">A60 生殖器疱疹</span>
                  <span class="rounded bg-[#F3F4F6] px-2 py-1 text-[#4B5563]">B37.3 阴道念珠菌</span>
                </div>
              </div>

              <div class="rounded-lg border border-[#E5E7EB] bg-white p-4 shadow-sm">
                <div class="mb-2 flex items-center gap-2">
                  <span class="flex h-6 w-6 items-center justify-center rounded-full bg-[#FFFBEB] text-[12px] font-bold text-[#D97706]">2</span>
                  <h4 class="font-bold text-[#1F2937]">生殖器/泌尿道损伤</h4>
                </div>
                <div class="flex flex-wrap gap-2 text-[12px]">
                  <span class="rounded bg-[#F3F4F6] px-2 py-1 text-[#4B5563]">N76.5 阴道溃疡</span>
                  <span class="rounded bg-[#F3F4F6] px-2 py-1 text-[#4B5563]">N39.0 尿路感染</span>
                  <span class="rounded bg-[#F3F4F6] px-2 py-1 text-[#4B5563]">N72 宫颈炎</span>
                </div>
              </div>

              <div class="rounded-lg border border-[#FECACA] bg-[#FEF2F2]/50 p-4 shadow-sm">
                <div class="mb-2 flex items-center gap-2">
                  <span class="flex h-6 w-6 items-center justify-center rounded-full bg-[#E11D48] text-[12px] font-bold text-white">3</span>
                  <h4 class="font-bold text-[#991B1B]">流产/妊娠方向 (极高危)</h4>
                </div>
                <div class="flex flex-wrap gap-2 text-[12px]">
                  <span class="rounded border border-[#FECACA] bg-white px-2 py-1 font-medium text-[#E11D48]">O04 人工流产</span>
                  <span class="rounded border border-[#FECACA] bg-white px-2 py-1 font-medium text-[#E11D48]">O00 异位妊娠</span>
                  <span class="rounded border border-[#FECACA] bg-white px-2 py-1 font-medium text-[#E11D48]">Z32 妊娠测试</span>
                  <span class="rounded border border-[#FECACA] bg-white px-2 py-1 font-medium text-[#E11D48]">O03 自然流产</span>
                </div>
              </div>
            </div>
          </div>

          <div class="flex flex-col overflow-hidden rounded-xl border border-[#E5E7EB] bg-white shadow-sm lg:col-span-2">
            <div class="flex items-center justify-between border-b border-[#E5E7EB] bg-[#F9FAFB] p-5">
              <h3 class="flex items-center gap-2 text-[16px] font-bold text-[#1F2937]">
                <AlertOctagon class="text-[#E11D48]" :size="18" />
                疑似侵害未成年人强制报告线索台账
              </h3>
              <div class="flex gap-2">
                <button
                  type="button"
                  class="flex items-center gap-1.5 rounded border border-[#D1D5DB] bg-white px-4 py-2 text-[13px] font-medium text-[#4B5563] shadow-sm transition-colors hover:bg-[#F3F4F6]"
                >
                  <Download :size="14" />
                  导出办案线索表
                </button>
              </div>
            </div>

            <div class="overflow-x-auto p-0">
              <table class="w-full min-w-[960px] text-left text-[14px]">
                <thead class="border-b border-[#E5E7EB] bg-[#F3F4F6]">
                  <tr>
                    <th class="w-[15%] p-4 font-semibold text-[#4B5563]">未成年患者</th>
                    <th class="w-[25%] border-l border-[#E0E7FF] bg-[#EEF2FF]/30 p-4 font-semibold text-[#4B5563]">触发高危诊断 (ICD-10)</th>
                    <th class="w-[20%] border-l border-[#E5E7EB] p-4 font-semibold text-[#4B5563]">接诊机构与医师</th>
                    <th class="w-[25%] border-l border-[#FECACA] bg-[#FEF2F2]/30 p-4 font-semibold text-[#4B5563]">
                      医师强制报告判定结论
                    </th>
                    <th class="w-[15%] border-l border-[#E5E7EB] p-4 text-center font-semibold text-[#4B5563]">治安联动</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-[#F3F4F6]">
                  <tr v-for="row in filteredLedger" :key="row.id" class="group transition-colors hover:bg-[#F9FAFB]">
                    <td class="p-4">
                      <p class="text-[14px] font-bold text-[#1F2937]">{{ row.patientName }}</p>
                      <p
                        class="mt-1 w-fit rounded border border-[#FECACA] bg-[#FEF2F2] px-1.5 py-0.5 text-[11px] font-bold text-[#E11D48]"
                      >
                        {{ row.patientMeta }}
                      </p>
                    </td>
                    <td class="border-l border-[#E0E7FF] bg-[#EEF2FF]/20 p-4">
                      <span
                        class="mb-1 block w-max rounded border px-2 py-0.5 text-[11px] font-bold"
                        :class="row.categoryBadgeClass"
                      >
                        {{ row.category }}
                      </span>
                      <p class="mt-1.5 text-[13px] font-bold text-[#1F2937]">{{ row.icdText }}</p>
                    </td>
                    <td class="border-l border-[#E5E7EB] p-4">
                      <div class="space-y-1 text-[12px] text-[#4B5563]">
                        <p class="font-bold text-[#1F2937]">{{ row.orgName }}</p>
                        <p class="text-[#6B7280]">接诊医师: {{ row.doctorName }}</p>
                        <p class="text-[11px] text-[#9CA3AF]">{{ row.timeText }}</p>
                      </div>
                    </td>
                    <td class="border-l border-[#FECACA] bg-[#FEF2F2]/30 p-4">
                      <div class="flex flex-col gap-1.5">
                        <span class="flex w-fit items-center gap-1 rounded border px-2 py-1 text-[12px] font-bold" :class="row.decisionBadgeClass">
                          <component :is="row.decisionIcon" :size="14" />
                          {{ row.decisionTitle }}
                        </span>
                        <p class="text-[11px] leading-tight" :class="row.decisionTextClass">{{ row.decisionDetail }}</p>
                      </div>
                    </td>
                    <td class="border-l border-[#E5E7EB] p-4 text-center">
                      <button
                        v-if="row.action === 'reported'"
                        type="button"
                        class="flex w-full items-center justify-center gap-1.5 rounded border border-[#FECACA] bg-[#E11D48] px-2 py-2 text-[12px] font-bold text-white shadow-sm transition-colors hover:bg-[#BE123C]"
                      >
                        <ShieldAlert :size="14" />
                        已报公安
                      </button>
                      <button
                        v-else-if="row.action === 'urge'"
                        type="button"
                        class="w-full rounded border border-[#D1D5DB] bg-white px-2 py-2 text-[12px] font-medium text-[#4B5563] shadow-sm transition-colors hover:bg-[#F3F4F6]"
                      >
                        催办医师
                      </button>
                      <span v-else class="mt-2 block text-[12px] font-medium text-[#9CA3AF]">系统归档</span>
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
import type { Component } from 'vue'
import {
  Activity,
  AlertOctagon,
  AlertTriangle,
  Baby,
  CheckCircle2,
  Clock,
  Database,
  Download,
  Filter,
  Search,
  ShieldAlert,
  Users,
} from 'lucide-vue-next'

const keyword = ref('')

const kpi = ref({
  minorVisits: 8412,
  riskAlerts: 45,
  excluded: 38,
  transferred: 5,
})

type ActionType = 'reported' | 'urge' | 'archived'
type LedgerRow = {
  id: string
  patientName: string
  patientMeta: string
  category: string
  categoryBadgeClass: string
  icdText: string
  orgName: string
  doctorName: string
  timeText: string
  decisionIcon: Component
  decisionTitle: string
  decisionBadgeClass: string
  decisionDetail: string
  decisionTextClass: string
  action: ActionType
  keywords: string[]
}

const ledger = ref<LedgerRow[]>([
  {
    id: 'l1',
    patientName: '赵*',
    patientMeta: '女, 14岁',
    category: '流产/妊娠方向',
    categoryBadgeClass: 'bg-[#FEF2F2] text-[#E11D48] border-[#FECACA]',
    icdText: 'O04 人工流产及并发症',
    orgName: '市妇幼保健院',
    doctorName: '李*梅',
    timeText: '今日 09:12 入院',
    decisionIcon: AlertTriangle,
    decisionTitle: '医师确认：疑似遭受侵害',
    decisionBadgeClass: 'border-[#FDE68A] bg-[#FFFBEB] text-[#D97706]',
    decisionDetail: '患者在无监护人陪同下就医，且伴有非自愿性行为陈述，已稳住当事人。',
    decisionTextClass: 'text-[#92400E]',
    action: 'reported',
    keywords: ['赵', '14', 'O04', '人工流产', '妇幼', '李', '疑似', '侵害'],
  },
  {
    id: 'l2',
    patientName: '钱*',
    patientMeta: '男, 16岁',
    category: '性病方向',
    categoryBadgeClass: 'bg-[#F3F4F6] text-[#4B5563] border-[#D1D5DB]',
    icdText: 'A51 早期梅毒',
    orgName: '某皮肤病专科医院',
    doctorName: '王*',
    timeText: '昨日 16:30 门诊',
    decisionIcon: Clock,
    decisionTitle: '系统强阻断：等待医师提交结论',
    decisionBadgeClass: 'border-[#FECACA] bg-[#FEF2F2] text-[#E11D48]',
    decisionDetail: 'HIS 收费系统已被锁定，要求医师必须填写判定表单后方可开药。',
    decisionTextClass: 'text-[#991B1B]',
    action: 'urge',
    keywords: ['钱', '16', 'A51', '梅毒', '皮肤', '王', '等待结论', '强制'],
  },
  {
    id: 'l3',
    patientName: '孙*瑶',
    patientMeta: '女, 17岁',
    category: '生殖器/泌尿道损伤',
    categoryBadgeClass: 'bg-[#F3F4F6] text-[#4B5563] border-[#D1D5DB]',
    icdText: 'N39.0 尿路感染',
    orgName: '某县人民医院',
    doctorName: '张*生',
    timeText: '昨日 14:20 门诊',
    decisionIcon: CheckCircle2,
    decisionTitle: '医师确认：正常病理，排除侵害',
    decisionBadgeClass: 'border-[#A7F3D0] bg-[#ECFDF5] text-[#10B981]',
    decisionDetail: '经家属陪同问诊，系个人卫生习惯导致的普通病理感染，无外伤及违背意愿特征。',
    decisionTextClass: 'text-[#065F46]',
    action: 'archived',
    keywords: ['孙', '17', 'N39.0', '尿路感染', '人民医院', '张', '排除', '归档'],
  },
])

function containsIgnoreCase(v: string, q: string) {
  return v.toLowerCase().includes(q.toLowerCase())
}

const filteredLedger = computed(() => {
  const q = keyword.value.trim()
  if (!q) return ledger.value
  return ledger.value.filter((x) =>
    [
      x.patientName,
      x.patientMeta,
      x.category,
      x.icdText,
      x.orgName,
      x.doctorName,
      ...x.keywords,
    ].some((v) => containsIgnoreCase(v, q)),
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

