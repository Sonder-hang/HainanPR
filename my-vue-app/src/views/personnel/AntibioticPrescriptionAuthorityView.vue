<template>
  <!-- 【模板一：双向规则碰撞与拦截】通用骨架 -->
  <div class="flex h-full min-h-0 flex-col bg-[#F7F9FC] font-sans text-[#1F264D]">

    <!-- 1. 动态顶栏区 -->
    <header
      class="flex min-h-[102px] shrink-0 flex-col justify-center gap-4 border-b border-[#E6E9F2] bg-white px-4 py-4 shadow-sm sm:flex-row sm:items-center sm:justify-between sm:px-8"
    >
      <div class="flex min-w-0 flex-wrap items-center gap-3 sm:gap-4">
        <div class="hidden rounded-[2px] bg-[#EEF2FF] p-2 text-[#0A6EFD] sm:block">
          <component :is="pageConfig.icon" :size="24" />
        </div>
        <h2 class="text-[20px] font-bold tracking-tight text-[#1F264D] sm:text-[22px] lg:text-[24px]">
          {{ pageConfig.title }}
        </h2>
        <span
          class="inline-flex items-center gap-1.5 rounded-full border border-[#FCA5A5] bg-[#FEF2F2] px-3 py-1 text-[11px] font-bold tracking-wide text-[#E5455F] sm:text-[12px]"
        >
          <Activity :size="14" class="animate-pulse" />
          {{ pageConfig.pulseText }}
        </span>
      </div>
      <div class="flex flex-wrap items-center gap-3 sm:gap-4">
        <div class="relative min-w-0 flex-1 sm:flex-initial">
          <Search
            class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-[#B8BCCC]"
            :size="18"
          />
          <input
            v-model.trim="keyword"
            type="text"
            :placeholder="pageConfig.searchPlaceholder"
            class="box-border h-[32px] w-full rounded-[2px] border border-[#E6E9F2] bg-[#F7F9FC] py-2.5 pl-10 pr-4 text-[14px] text-[#1F264D] outline-none transition-all placeholder:text-[#B8BCCC] focus:border-[#0A6EFD] focus:bg-white focus:ring-2 focus:ring-[#0A6EFD]/20 sm:w-[min(340px,100%)]"
          />
        </div>
        <button
          type="button"
          class="box-border flex h-[32px] shrink-0 items-center gap-2 whitespace-nowrap rounded-[2px] bg-[#2E57E5] px-5 py-2.5 text-[14px] font-medium text-white shadow-sm shadow-[#2E57E5]/30 transition-colors hover:bg-[#1E4BD8]"
        >
          <Filter :size="16" />
          高级筛选
        </button>
      </div>
    </header>

    <!-- 2. 动态内容滚动区 -->
    <div class="technology-scroll flex-1 overflow-y-auto bg-[#F7F9FC] p-6 sm:p-8">
      <div class="mx-auto max-w-[1400px] space-y-6 pb-12 animate-fade-in">

        <!-- 3. 通用规则引擎解构模块 -->
        <div class="flex flex-col overflow-hidden rounded-[2px] border border-[#E6E9F2] bg-white shadow-sm lg:flex-row">
          <div
            class="flex flex-col justify-center border-b border-[#E6E9F2] bg-gradient-to-br from-[#F2F5FA] to-[#F7F9FC] p-8 lg:w-[45%] lg:border-b-0 lg:border-r"
          >
            <h3 class="mb-3 text-[18px] font-bold text-[#1F264D]">{{ ruleConfig.title }}</h3>
            <p class="text-[14px] leading-relaxed text-[#596080]" v-html="ruleConfig.description" />
          </div>

          <div class="relative flex flex-col justify-center bg-white p-8 lg:w-[55%]">
            <div class="relative z-10 mx-auto flex w-full max-w-[500px] items-stretch justify-between">

              <!-- 左侧实体 -->
              <div class="flex w-[160px] flex-col items-center gap-2">
                <div
                  class="flex h-14 w-14 items-center justify-center rounded-[2px] border border-[#BFDBFE] bg-[#EEF2FF] text-[#0A6EFD] shadow-sm"
                >
                  <component :is="ruleConfig.leftIcon" :size="24" />
                </div>
                <p class="text-[14px] font-bold text-[#1F264D]">{{ ruleConfig.leftEntityName }}</p>
                <p class="rounded bg-[#F2F5FA] px-2 py-0.5 text-[11px] text-[#596080]">
                  {{ ruleConfig.leftEntityDesc }}
                </p>
              </div>

              <!-- 碰撞引擎 -->
              <div class="relative flex flex-1 flex-col items-center justify-center px-2">
                <div
                  class="absolute left-0 top-[28px] -z-10 h-[2px] w-full -translate-y-1/2 bg-gradient-to-r from-[#BFDBFE] via-[#FCA5A5] to-[#FCA5A5]"
                />
                <div class="absolute left-1/4 top-[29px] h-2 w-2 animate-ping rounded-full bg-[#0A6EFD]" />
                <div
                  class="absolute right-1/4 top-[29px] h-2 w-2 animate-ping rounded-full bg-[#E5455F]"
                  style="animation-delay: 0.5s"
                />
                <div
                  class="mt-3 rounded-full border-[2px] border-[#F58718] bg-[#FFFBEB] p-2 shadow-[0_0_10px_rgba(245,135,24,0.2)]"
                >
                  <ArrowRightLeft class="text-[#F58718]" :size="18" />
                </div>
                <p class="mt-2 text-[11px] font-bold text-[#F58718]">规则强校验拦截</p>
              </div>

              <!-- 右侧实体 -->
              <div class="flex w-[160px] flex-col items-center gap-2">
                <div
                  class="flex h-14 w-14 items-center justify-center rounded-[2px] border border-[#FCA5A5] bg-[#FEF2F2] text-[#E5455F] shadow-sm"
                >
                  <component :is="ruleConfig.rightIcon" :size="24" />
                </div>
                <p class="text-[14px] font-bold text-[#1F264D]">{{ ruleConfig.rightEntityName }}</p>
                <p class="rounded bg-[#F2F5FA] px-2 py-0.5 text-[11px] text-[#596080]">
                  {{ ruleConfig.rightEntityDesc }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- 4. 动态通用 KPI 卡片区 -->
        <div class="grid grid-cols-1 gap-6 md:grid-cols-4">
          <div
            v-for="(kpi, index) in kpiData"
            :key="index"
            class="group relative overflow-hidden rounded-[2px] border border-[#E6E9F2] bg-white p-6 shadow-sm transition-colors"
            :style="{ '--hover-color': kpi.color }"
            :class="`hover:border-[var(--hover-color)]`"
          >
            <div class="absolute left-0 top-0 h-full w-1.5" :style="{ backgroundColor: kpi.color }" />
            <div class="mb-4 flex items-start justify-between">
              <p
                class="text-[14px] font-medium"
                :class="kpi.isAlert ? 'text-[#E5455F] font-bold' : 'text-[#596080]'"
              >
                {{ kpi.label }}
              </p>
              <div
                class="rounded-[2px] p-2"
                :style="{ backgroundColor: kpi.bgColor, color: kpi.color }"
              >
                <component :is="kpi.icon" :size="20" />
              </div>
            </div>
            <p
              class="text-[32px] font-black text-[#1F264D]"
              :style="{ color: kpi.isAlert ? kpi.color : '#1F264D' }"
            >
              {{ kpi.value }} <span class="ml-1 text-[14px] font-normal text-[#596080]">{{ kpi.unit }}</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#596080]">{{ kpi.subtext }}</p>
          </div>
        </div>

        <!-- 5. 动态通用违规明细台账 -->
        <div class="flex flex-col overflow-hidden rounded-[2px] border border-[#E6E9F2] bg-white shadow-sm">
          <div class="flex items-center justify-between border-b border-[#E6E9F2] bg-[#F2F5FA] p-5">
            <h3 class="flex items-center gap-2 text-[16px] font-bold text-[#1F264D]">
              <AlertOctagon class="text-[#E5455F]" :size="18" />
              {{ tableConfig.title }}
            </h3>
            <button
              type="button"
              @click="handleExport"
              class="box-border flex h-[32px] items-center gap-1.5 rounded-[2px] border border-[#E6E9F2] bg-white px-4 py-2 text-[13px] font-medium text-[#596080] shadow-sm transition-colors hover:bg-[#F3F4F6]"
            >
              <Download :size="14" />
              导出违规明细
            </button>
          </div>

          <div class="overflow-x-auto p-0">
            <table class="w-full min-w-[960px] text-left text-[14px]">
              <thead class="border-b border-[#E6E9F2] bg-[#F2F5FA]">
                <tr>
                  <th
                    v-for="(col, idx) in tableConfig.columns"
                    :key="idx"
                    class="p-4 font-semibold text-[#596080]"
                    :class="col.class"
                  >
                    {{ col.label }}
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#F7F9FC]">
                <tr
                  v-for="(row, rIdx) in filteredTableData"
                  :key="rIdx"
                  class="group transition-colors hover:bg-[#EFF6FF]"
                >
                  <!-- 左侧 A实体 列 -->
                  <td class="p-4">
                    <p class="text-[14px] font-bold text-[#1F264D]">{{ row.leftPrimary }}</p>
                    <p class="mt-1 text-[12px] text-[#596080]">{{ row.leftSecondary }}</p>
                    <span
                      v-if="row.leftTag"
                      class="mt-1 inline-block rounded border border-[#D7D9E5] bg-[#F2F5FA] px-1.5 py-0.5 text-[11px] font-medium text-[#596080]"
                    >
                      {{ row.leftTag }}
                    </span>
                  </td>

                  <!-- 右侧 B实体 列 -->
                  <td class="border-l border-[#BFDBFE] bg-[#EEF2FF]/20 p-4">
                    <p class="text-[13px] font-bold text-[#1F264D]">{{ row.rightPrimary }}</p>
                    <p class="mt-1 font-mono text-[12px] text-[#596080]">{{ row.rightSecondary }}</p>
                    <span v-if="row.rightTag" :class="row.rightTagColorClass">
                      {{ row.rightTag }}
                    </span>
                  </td>

                  <!-- 碰撞结论 列 -->
                  <td class="border-l border-[#FCA5A5] bg-[#FEF2F2]/30 p-4">
                    <div class="flex flex-col gap-1.5">
                      <span
                        class="flex w-fit items-center gap-1 rounded border px-2 py-0.5 text-[12px] font-bold"
                        :class="row.alertLevel === 'high' ? 'bg-[#FEF2F2] border-[#FCA5A5] text-[#E5455F]' : 'bg-[#FFFBEB] border-[#FDE68A] text-[#F58718]'"
                      >
                        <component :is="row.alertLevel === 'high' ? AlertOctagon : AlertTriangle" :size="12" />
                        {{ row.conclusionTitle }}
                      </span>
                      <p
                        class="text-[11px] leading-tight"
                        :class="row.alertLevel === 'high' ? 'text-[#991B1B]' : 'text-[#92400E]'"
                      >
                        {{ row.conclusionDesc }}
                      </p>
                    </div>
                  </td>

                  <!-- 动态操作 列 -->
                  <td class="border-l border-[#E6E9F2] p-4 text-center">
                    <button
                      type="button"
                      class="box-border h-[32px] w-full rounded-[2px] border px-3 text-[12px] font-bold shadow-sm transition-colors"
                      :class="row.actionBtnClass"
                    >
                      {{ row.actionBtnText }}
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
import {
  Activity,
  AlertOctagon,
  AlertTriangle,
  ArrowRightLeft,
  Download,
  FileText,
  Filter,
  Pill,
  Search,
  ShieldAlert,
  Users,
} from 'lucide-vue-next'
import { exportToExcel } from '../../utils/exportExcel'
const keyword = ref('')

// 1. 页面基础配置
const pageConfig = {
  title: '抗菌药物处方权合规监管 (人员要素)',
  icon: ShieldAlert,
  pulseText: '医师权限与医嘱流水实时比对中',
  searchPlaceholder: '输入开单医师、药品名称检索...',
}

// 2. 规则碰撞说明配置
const ruleConfig = {
  title: '处方权限智能拦截模型',
  description:
    '依据《抗菌药物临床应用管理办法》，医师开具抗菌药物必须与其<span class="font-bold text-[#0A6EFD]">专业技术职称</span>相匹配。<br/>系统将对住院医嘱进行强校验：严禁低职称医师越权开具<span class="font-bold text-[#E5455F]">限制使用级/特殊使用级</span>抗菌药，违规即刻拦截并追责。',
  leftEntityName: '人员要素信息库',
  leftEntityDesc: '获取医师真实职称',
  leftIcon: Users,
  rightEntityName: 'HIS 病区医嘱',
  rightEntityDesc: '抓取抗生素医嘱明细',
  rightIcon: Pill,
}

// 3. 顶部 KPI 卡片配置
const kpiData = [
  {
    label: '全省实时在职医师数',
    value: '31,402',
    unit: '人',
    subtext: '包含公立与民营机构',
    icon: Users,
    color: '#0A6EFD',
    bgColor: '#EEF2FF',
    isAlert: false,
  },
  {
    label: '今日病区开具抗菌药',
    value: '8,412',
    unit: '份',
    subtext: '已全部经过底层引擎校验',
    icon: FileText,
    color: '#12B881',
    bgColor: '#ECFDF5',
    isAlert: false,
  },
  {
    label: '触发越权违规拦截',
    value: '45',
    unit: '起',
    subtext: '限制级28起，特殊级17起',
    icon: AlertTriangle,
    color: '#F58718',
    bgColor: '#FFFBEB',
    isAlert: true,
  },
  {
    label: '涉嫌严重牟利异常医师',
    value: '3',
    unit: '人',
    subtext: '高频屡次试探越权开单',
    icon: AlertOctagon,
    color: '#E5455F',
    bgColor: '#FEF2F2',
    isAlert: true,
  },
]

// 4. 底部台账表格配置
const tableConfig = {
  title: '实时越权开单拦截明细台账',
  columns: [
    { label: '左侧校验元：开单医师实体', class: 'w-[20%]' },
    {
      label: '右侧校验元：实际开具药品 (HIS)',
      class: 'w-[25%] bg-[#EEF2FF]/30 border-l border-[#E0E7FF]',
    },
    {
      label: '双向碰撞逻辑研判结论',
      class: 'w-[35%] bg-[#FEF2F2]/30 border-l border-[#FECACA]',
    },
    { label: '自动触发监管操作', class: 'w-[20%] text-center border-l border-[#E5E7EB]' },
  ],
}

// 5. 表格数据体
const tableData = [
  {
    leftPrimary: '王* (全科医学科)',
    leftSecondary: '执业机构：某镇中心卫生院',
    leftTag: '住院医师 (初级)',
    rightPrimary: '替加环素 (注射用)',
    rightSecondary: '数量: 5支 | 用法: 静脉滴注',
    rightTag: '特殊使用级 (#限制)',
    rightTagColorClass: 'mt-1 inline-block rounded border border-[#FCA5A5] bg-[#FEF2F2] px-1.5 py-0.5 text-[11px] font-bold text-[#E5455F]',
    alertLevel: 'high',
    conclusionTitle: '严重越权 (跨两级违规)',
    conclusionDesc: '住院医师无权开具特殊使用级抗生素，且该药品(#)原则上限三级医院使用，系统已强制阻断计费并上报。',
    actionBtnText: '下发停权通报单',
    actionBtnClass: 'border-[#E5455F] bg-[#FEF2F2] text-[#E5455F] hover:bg-[#E5455F] hover:text-white',
    keywords: ['王', '全科', '替加环素', '特殊', '越权', '住院医师'],
  },
  {
    leftPrimary: '李*生 (骨科)',
    leftSecondary: '执业机构：海口某民营骨科医院',
    leftTag: '主治医师 (中级)',
    rightPrimary: '亚胺培南/西司他丁',
    rightSecondary: '数量: 2盒 | 用法: 静推',
    rightTag: '特殊使用级',
    rightTagColorClass: 'mt-1 inline-block rounded border border-[#FCA5A5] bg-[#FEF2F2] px-1.5 py-0.5 text-[11px] font-bold text-[#E5455F]',
    alertLevel: 'high',
    conclusionTitle: '职称权限不符',
    conclusionDesc: '开具特殊使用级要求【副高级及以上】，该医师为中级职称，权限校验不通过。',
    actionBtnText: '驳回处方要求重开',
    actionBtnClass: 'border-[#E5455F] bg-[#FEF2F2] text-[#E5455F] hover:bg-[#E5455F] hover:text-white',
    keywords: ['李', '骨科', '亚胺培南', '特殊', '中级', '权限'],
  },
  {
    leftPrimary: '张*华 (呼吸内科)',
    leftSecondary: '执业机构：琼海市人民医院',
    leftTag: '住院医师 (初级)',
    rightPrimary: '头孢哌酮/舒巴坦',
    rightSecondary: '数量: 10支 | 用法: 输液',
    rightTag: '限制使用级',
    rightTagColorClass: 'mt-1 inline-block rounded border border-[#FDE68A] bg-[#FFFBEB] px-1.5 py-0.5 text-[11px] font-bold text-[#F58718]',
    alertLevel: 'warn',
    conclusionTitle: '轻度越权拦截',
    conclusionDesc: '初级职称开具限制级药物。系统检测到其尚未通过本年度【限制级抗菌药培训考核】，处方权暂未解锁。',
    actionBtnText: '系统警告并退回',
    actionBtnClass: 'border-[#F58718] bg-[#FFFBEB] text-[#F58718] hover:bg-[#F58718] hover:text-white',
    keywords: ['张', '呼吸', '头孢', '限制', '初级', '培训'],
  },
]

function containsIgnoreCase(v: string, q: string) {
  return v.toLowerCase().includes(q.toLowerCase())
}

const filteredTableData = computed(() => {
  const q = keyword.value.trim()
  if (!q) return tableData
  return tableData.filter((x) =>
    [x.leftPrimary, x.leftSecondary, x.rightPrimary, x.rightSecondary, ...x.keywords].some((v) =>
      containsIgnoreCase(v, q),
    ),
  )
})

const antibioticColumns = [
  { field: 'leftPrimary', header: '开单医师' },
  { field: 'leftSecondary', header: '执业机构' },
  { field: 'leftTag', header: '职称' },
  { field: 'rightPrimary', header: '开具药品' },
  { field: 'rightSecondary', header: '数量/用法' },
  { field: 'rightTag', header: '药品级别' },
  { field: 'conclusionTitle', header: '违规结论' },
  { field: 'conclusionDesc', header: '违规详情' },
]

function handleExport() {
  exportToExcel(filteredTableData.value, antibioticColumns, '越权开单拦截明细台账')
}
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
  background: #D7D9E5;
  border-radius: 10px;
}
.technology-scroll::-webkit-scrollbar-thumb:hover {
  background: #B8BCCC;
}
</style>
