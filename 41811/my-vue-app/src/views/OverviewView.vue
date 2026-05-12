<template>
  <div class="animate-fade-in space-y-5">
    <div class="rounded border border-[#b8c9e8]/60 bg-white p-5 shadow-sm">
      <h3 class="mb-2 flex items-center gap-2 text-[13px] font-bold text-[#1F2937]">
        <FileText class="text-[#265EE6]" />
        报告导读
      </h3>
      <p class="text-[12px] leading-relaxed text-[#4B5563]">
        按照三医智慧监管工作要求，省卫生健康委医政处、规划信息处，省三医大数据中心利用三医平台数据，
        对2026年1月全省医疗服务数据进行了深度挖掘。本期报告共发现
        <span class="text-[13px] font-bold text-[#EF4444]">866</span> 起异常预警，
        涵盖机构床位超标、违规使用特殊级抗菌药、医师跨机构违规诊疗、违规开展限制类技术、重复收费及基层村卫生室"零业务"等多个核心维度。
      </p>
    </div>

    <div class="grid grid-cols-4 gap-4">
      <div
        v-for="(card, index) in summaryCards"
        :key="index"
        class="flex items-center gap-4 rounded border border-[#b8c9e8]/60 bg-white p-4 shadow-sm"
      >
        <div :class="['rounded border p-2.5 shrink-0', card.colorClass]">
          <component :is="card.icon" :size="22" />
        </div>
        <div>
          <p class="mb-0.5 text-[11px] font-medium text-[#6B7280]">{{ card.title }}</p>
          <p class="text-[24px] font-black leading-none text-[#1F2937]">
            {{ card.value }}
            <span class="ml-1 text-[11px] font-normal text-[#6B7280]">{{ card.unit }}</span>
          </p>
        </div>
      </div>
    </div>

    <div class="rounded border border-[#b8c9e8]/60 bg-white p-5 shadow-sm">
      <h3 class="mb-4 flex items-center gap-2 text-[13px] font-bold text-[#1F2937]">
        <BarChart3 class="text-[#265EE6]" />
        核心监管维度预警分布
      </h3>
      <div class="space-y-3.5">
        <div v-for="(bar, index) in progressBars" :key="index">
          <div class="mb-1 flex justify-between text-[12px]">
            <span class="font-medium text-[#374151]">{{ bar.label }}</span>
            <span class="font-bold text-[#1F2937]">{{ bar.value }} 起</span>
          </div>
          <div class="h-[8px] w-full overflow-hidden rounded-full bg-[#F3F4F6]">
            <div
              :class="['h-[8px] rounded-full', bar.color]"
              :style="{ width: `${(bar.value / totalAlert) * 100}%` }"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { FileText, AlertTriangle, Building, Stethoscope, BarChart3 } from 'lucide-vue-next'
import { currentHospitalId } from '../stores/hospital'

const isAll = computed(() => currentHospitalId.value === 'all')

const ALL = {
  total: 866, orgs: 63, doctors: 55, items: 20,
  bars: [
    { label: '技术要素 (限制类技术违规: 人工智能辅助手术等)', value: 762, color: 'bg-[#ef4444]' },
    { label: '基层网点 (公立村卫生室年门诊量为0)', value: 47, color: 'bg-[#F59E0B]' },
    { label: '医保要素 (心电监测/血氧等重复收费)', value: 20, color: 'bg-[#F97316]' },
    { label: '人员要素 (抗菌药越权/跨机构飞刀)', value: 15, color: 'bg-[#265EE6]' },
    { label: '机构要素 (床位面积比不达标)', value: 14, color: 'bg-[#6366F1]' },
  ],
}

const HOSP_DATA: Record<string, typeof ALL> = {
  h001: {
    total: 186, orgs: 1, doctors: 12, items: 5,
    bars: [
      { label: '技术要素', value: 95, color: 'bg-[#ef4444]' },
      { label: '人员要素', value: 42, color: 'bg-[#265EE6]' },
      { label: '机构要素', value: 18, color: 'bg-[#6366F1]' },
      { label: '设备要素', value: 31, color: 'bg-[#ea580c]' },
    ],
  },
  h002: {
    total: 147, orgs: 1, doctors: 10, items: 4,
    bars: [
      { label: '技术要素', value: 78, color: 'bg-[#ef4444]' },
      { label: '人员要素', value: 35, color: 'bg-[#265EE6]' },
      { label: '机构要素', value: 12, color: 'bg-[#6366F1]' },
      { label: '设备要素', value: 22, color: 'bg-[#ea580c]' },
    ],
  },
  h003: {
    total: 100, orgs: 1, doctors: 8, items: 3,
    bars: [
      { label: '技术要素', value: 68, color: 'bg-[#ef4444]' },
      { label: '人员要素', value: 15, color: 'bg-[#265EE6]' },
      { label: '机构要素', value: 5, color: 'bg-[#6366F1]' },
      { label: '设备要素', value: 12, color: 'bg-[#ea580c]' },
    ],
  },
  h004: {
    total: 90, orgs: 1, doctors: 9, items: 3,
    bars: [
      { label: '技术要素', value: 45, color: 'bg-[#ef4444]' },
      { label: '人员要素', value: 22, color: 'bg-[#265EE6]' },
      { label: '机构要素', value: 8, color: 'bg-[#6366F1]' },
      { label: '设备要素', value: 15, color: 'bg-[#ea580c]' },
    ],
  },
}

const data = computed(() => isAll.value ? ALL : (HOSP_DATA[currentHospitalId.value] || ALL))
const totalAlert = computed(() => data.value.total)

const summaryCards = computed(() => [
  { title: '总计异常事件', value: data.value.total, unit: '起', icon: AlertTriangle, colorClass: 'bg-[#FEF2F2] text-[#ef4444] border-[#FECACA]' },
  { title: '涉事医疗机构', value: data.value.orgs, unit: '家', icon: Building, colorClass: 'bg-[#EEF2FF] text-[#6366F1] border-[#C7D2FE]' },
  { title: '涉事医务人员', value: data.value.doctors, unit: '人', icon: Stethoscope, colorClass: 'bg-[#EFF6FF] text-[#265EE6] border-[#BAE6FD]' },
  { title: '违规收费项目', value: data.value.items, unit: '笔', icon: FileText, colorClass: 'bg-[#FFFBEB] text-[#F59E0B] border-[#FDE68A]' },
])

const progressBars = computed(() => data.value.bars)
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.4s ease-in-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
