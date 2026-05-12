<template>
  <!-- 页面根容器，直接作为路由主页面 -->
  <div class="flex h-full min-h-0 flex-col bg-[#F4F6F8] font-sans text-[#333333]">
    <!-- 页面级操作顶栏 -->
    <header
      class="flex min-h-[102px] shrink-0 flex-col justify-center gap-4 border-b border-[#E5E7EB] bg-white px-4 py-4 shadow-sm sm:flex-row sm:items-center sm:justify-between sm:px-8"
    >
      <div class="flex min-w-0 flex-wrap items-center gap-3 sm:gap-4">
        <h2 class="text-[20px] font-bold tracking-tight text-[#1F2937] sm:text-[22px] lg:text-[24px]">
          虚设科室数据异常监管
        </h2>
        <span
          class="inline-flex items-center gap-1.5 rounded-full border border-[#FDE68A] bg-[#FFFBEB] px-3 py-1 text-[11px] font-bold tracking-wide text-[#D97706] sm:text-[12px]"
        >
          <Clock :size="14" class="animate-pulse" />
          全省业务量空载侦测中
        </span>
      </div>
      <div class="flex flex-wrap items-center gap-3 sm:gap-4">
        <div class="relative min-w-0 flex-1 sm:flex-initial">
          <Search class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-[#9CA3AF]" :size="18" />
          <input
            v-model.trim="keyword"
            type="text"
            placeholder="输入医疗机构名称或核准诊疗科目..."
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

    <!-- 动态内容滚动区 -->
    <div class="institution-scroll flex-1 overflow-y-auto p-6 sm:p-8">
      <div class="mx-auto max-w-[1400px] space-y-6 pb-12 animate-fade-in">
        <!-- 政策导读与空载时间轴可视化 -->
        <div class="flex flex-col overflow-hidden rounded-xl border border-[#E5E7EB] bg-white shadow-sm lg:flex-row">
          <!-- 左侧：监管目的与依据 -->
          <div
            class="flex flex-col justify-center border-b border-[#E5E7EB] bg-gradient-to-br from-[#F8FAFC] to-[#F1F5F9] p-8 lg:w-[40%] lg:border-b-0 lg:border-r"
          >
            <div class="mb-4 w-fit rounded-xl border border-[#C7D2FE] bg-[#EEF2FF] p-3 text-[#265EE6] shadow-sm">
              <Minimize2 :size="28" stroke-width="2" />
            </div>
            <h3 class="mb-3 text-[20px] font-bold text-[#1F2937]">打击骗取资质：科室空载监测模型</h3>
            <p class="mb-4 text-[14px] leading-relaxed text-[#4B5563]">
              部分医疗机构为<span class="font-bold text-[#1F2937]">应付校验或骗取机构设置资质</span>，在执业许可证上挂牌了如“检验科、妇产科”等科目，但实际并未开展任何收治工作。<br /><br />
              依据《医疗机构校验管理办法》，系统通过 HIS 业务量抓取与疾病映射规则，自动筛查长期“零业务”的空壳科室。
            </p>
          </div>

          <!-- 右侧：红线阈值时间轴 UI -->
          <div class="relative flex flex-col justify-center bg-white p-8 lg:w-[60%]">
            <h4 class="mb-6 text-[14px] font-bold uppercase tracking-widest text-[#6B7280]">智能侦测时间轴与阈值触发机制</h4>

            <div class="relative z-10 mx-auto mt-4 flex w-full max-w-[600px] flex-col">
              <!-- 贯穿的时间线 -->
              <div class="absolute left-0 top-1/2 -z-10 h-[3px] w-full -translate-y-1/2 rounded-full bg-gradient-to-r from-[#10B981] via-[#F59E0B] to-[#EF4444]" />

              <div class="relative z-10 flex items-center justify-between">
                <!-- 节点 1：正常 -->
                <div class="flex flex-col items-center gap-2">
                  <div class="flex h-10 w-10 items-center justify-center rounded-full border-[3px] border-[#10B981] bg-[#ECFDF5] shadow-sm">
                    <Activity class="text-[#10B981]" :size="18" />
                  </div>
                  <div class="text-center">
                    <p class="text-[14px] font-bold text-[#1F2937]">有收治记录</p>
                    <p class="text-[12px] font-medium text-[#10B981]">正常营业状态</p>
                  </div>
                </div>

                <!-- 节点 2：警告 (1个月) -->
                <div class="flex flex-col items-center gap-2">
                  <div class="flex h-10 w-10 items-center justify-center rounded-full border-[3px] border-[#F59E0B] bg-[#FFFBEB] shadow-sm">
                    <Clock class="text-[#F59E0B]" :size="18" />
                  </div>
                  <div class="text-center">
                    <p class="text-[14px] font-bold text-[#1F2937]">空载 &gt; 1个月</p>
                    <p class="text-[12px] font-medium text-[#D97706]">黄色关注预警</p>
                  </div>
                </div>

                <!-- 节点 3：红线违规 (3个月) -->
                <div class="relative flex flex-col items-center gap-2">
                  <div class="flex h-12 w-12 animate-pulse items-center justify-center rounded-full border-[4px] border-[#EF4444] bg-[#FEF2F2] shadow-[0_0_15px_rgba(239,68,68,0.4)]">
                    <AlertOctagon class="text-[#EF4444]" :size="22" />
                  </div>
                  <div class="absolute -top-10 whitespace-nowrap">
                    <span class="rounded bg-[#EF4444] px-2 py-1 text-[12px] font-bold text-white shadow-sm">法定校验红线</span>
                    <div class="mx-auto mt-0.5 h-0 w-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-[#EF4444]" />
                  </div>
                  <div class="text-center">
                    <p class="text-[15px] font-bold text-[#991B1B]">零业务 &gt; 3个月</p>
                    <p class="text-[12px] font-bold text-[#EF4444]">涉嫌虚设科室 (立案)</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- KPI 统计卡片区 -->
        <div class="grid grid-cols-1 gap-6 md:grid-cols-4">
          <div class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#265EE6]">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#265EE6]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#6B7280]">全省机构核准科室总数</p>
              <div class="rounded-lg bg-[#EEF2FF] p-2 text-[#265EE6]">
                <Database :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#1F2937]">
              {{ kpi.totalApproved.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#6B7280]">个</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#6B7280]">实时扫描 HIS 底层映射</p>
          </div>

          <div class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#F59E0B]">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#F59E0B]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#6B7280]">空载超 1 个月预警</p>
              <div class="rounded-lg bg-[#FFFBEB] p-2 text-[#F59E0B]">
                <Clock :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#D97706]">
              {{ kpi.warnOver30.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#D97706]">个</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#D97706]">业务异常萎缩，需关注</p>
          </div>

          <div class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#EF4444]">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#EF4444]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-bold text-[#EF4444]">空载超 3 个月红线</p>
              <div class="rounded-lg bg-[#FEF2F2] p-2 text-[#EF4444]">
                <ShieldAlert :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#EF4444]">
              {{ kpi.redlineOver90.toLocaleString() }} <span class="ml-1 text-[14px] font-normal text-[#EF4444]">个</span>
            </p>
            <p class="mt-2 text-[12px] font-bold text-[#EF4444]">触发校验强制通报机制</p>
          </div>

          <div class="flex flex-col justify-center rounded-xl border border-[#002140] bg-[#001529] p-6 text-white shadow-sm">
            <p class="mb-3 text-[14px] font-medium text-[#9CA3AF]">全省虚设挂靠科室重灾区 TOP 3</p>
            <div class="space-y-3">
              <div v-for="(item, idx) in kpi.top3" :key="idx" class="flex items-center justify-between text-[13px]">
                <span class="flex items-center gap-1.5 text-white">
                  <div class="h-1.5 w-1.5 rounded-full" :style="{ background: item.color }" />
                  {{ item.name }}
                </span>
                <div class="flex items-center gap-2">
                  <div class="h-1.5 w-20 overflow-hidden rounded-full bg-[#002140]">
                    <div class="h-full" :style="{ width: `${item.percent}%`, background: item.color }" />
                  </div>
                  <span class="w-10 text-right font-bold" :style="{ color: item.color }">{{ item.percent }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 核心业务表格：虚设科室线索台账 -->
        <div class="flex flex-col overflow-hidden rounded-xl border border-[#E5E7EB] bg-white shadow-sm">
          <div class="flex items-center justify-between border-b border-[#E5E7EB] bg-[#F9FAFB] p-5">
            <h3 class="flex items-center gap-2 text-[16px] font-bold text-[#1F2937]">
              <AlertTriangle class="text-[#EF4444]" :size="20" />
              零业务/虚设科室异常线索台账
            </h3>
            <div class="flex gap-2">
              <button
                type="button"
                class="flex items-center gap-1.5 rounded border border-[#D1D5DB] bg-white px-4 py-2 text-[13px] font-medium text-[#4B5563] shadow-sm transition-colors hover:bg-[#F3F4F6]"
              >
                <Download :size="14" />
                导出核查工单
              </button>
            </div>
          </div>

          <div class="overflow-x-auto p-0">
            <table class="w-full min-w-[960px] text-left text-[14px]">
              <thead class="border-b border-[#E5E7EB] bg-[#F3F4F6]">
                <tr>
                  <th class="w-[20%] p-4 font-semibold text-[#4B5563]">医疗机构信息</th>
                  <th class="w-[15%] border-l border-[#E0E7FF] bg-[#EEF2FF]/30 p-4 font-semibold text-[#4B5563]">嫌疑虚设科目</th>
                  <th class="w-[25%] border-l border-[#FECACA] bg-[#FEF2F2]/30 p-4 font-semibold text-[#4B5563]">底层引擎映射解析期望</th>
                  <th class="w-[25%] border-l border-[#E5E7EB] p-4 font-semibold text-[#4B5563]">HIS业务量实际捕获</th>
                  <th class="w-[15%] border-l border-[#E5E7EB] p-4 text-center font-semibold text-[#4B5563]">监管处理操作</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#F3F4F6]">
                <tr v-for="row in filteredRows" :key="row.id" class="group transition-colors hover:bg-[#F9FAFB]">
                  <td class="p-4">
                    <p class="text-[15px] font-bold text-[#1F2937]">{{ row.orgName }}</p>
                    <p class="mt-1.5 text-[12px] text-[#6B7280]">机构编码：{{ row.orgCode }}</p>
                    <p class="mt-0.5 text-[12px] text-[#6B7280]">机构级别：{{ row.orgLevel }}</p>
                  </td>
                  <td class="border-l border-[#E0E7FF] bg-[#EEF2FF]/20 p-4">
                    <span class="block w-fit rounded border border-[#C7D2FE] bg-[#EEF2FF] px-3 py-1.5 text-[13px] font-bold text-[#265EE6]">
                      {{ row.suspectSubject }}
                    </span>
                  </td>
                  <td class="border-l border-[#FECACA] bg-[#FEF2F2]/20 p-4">
                    <div class="space-y-1.5 text-[13px]">
                      <p class="text-[#6B7280]">
                        <span class="font-medium text-[#1F2937]">应具备记录：</span>{{ row.expected }}
                      </p>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4">
                    <div class="flex flex-col gap-2">
                      <div class="flex items-center gap-1.5">
                        <span
                          class="rounded border px-2 py-0.5 text-[12px] font-bold"
                          :class="
                            row.daysNoBusiness >= 90
                              ? 'border-[#FECACA] bg-[#FEF2F2] text-[#EF4444]'
                              : 'border-[#FDE68A] bg-[#FFFBEB] text-[#D97706]'
                          "
                        >
                          {{ row.daysText }}
                        </span>
                        <span
                          class="text-[13px] font-bold"
                          :class="row.daysNoBusiness >= 90 ? 'text-[#991B1B]' : 'text-[#92400E]'"
                        >
                          {{ row.actualTitle }}
                        </span>
                      </div>
                      <p
                        class="mt-1 rounded border p-1.5 text-[12px] leading-tight"
                        :class="
                          row.daysNoBusiness >= 90
                            ? 'border-[#FEE2E2] bg-[#FEF2F2] text-[#7F1D1D]'
                            : 'border-[#FEF3C7] bg-[#FFFBEB] text-[#92400E]'
                        "
                      >
                        判定结论：{{ row.conclusion }}
                      </p>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4 text-center">
                    <button
                      type="button"
                      class="flex w-full items-center justify-center gap-1.5 rounded border px-3 py-2 text-[12px] font-bold shadow-sm transition-colors"
                      :class="
                        row.daysNoBusiness >= 90
                          ? 'border-[#FECACA] bg-[#FEF2F2] text-[#EF4444] hover:bg-[#EF4444] hover:text-white'
                          : 'border-[#FDE68A] bg-[#FFFBEB] text-[#D97706] hover:bg-[#D97706] hover:text-white'
                      "
                    >
                      <component :is="row.daysNoBusiness >= 90 ? AlertOctagon : Bell" :size="14" />
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
import {
  Activity,
  AlertOctagon,
  AlertTriangle,
  Bell,
  Clock,
  Database,
  Download,
  Filter,
  Minimize2,
  Search,
  ShieldAlert,
} from 'lucide-vue-next'

type LedgerRow = {
  id: string
  orgName: string
  orgCode: string
  orgLevel: string
  suspectSubject: string
  expected: string
  daysNoBusiness: number
  daysText: string
  actualTitle: string
  conclusion: string
  actionText: string
}

const keyword = ref('')

const rows = ref<LedgerRow[]>([
  {
    id: '460105882-lab',
    orgName: '海口康宁康复医院',
    orgCode: '460105882',
    orgLevel: '二级民营',
    suspectSubject: '医学检验科',
    expected: '三大常规检验报告、生化检验记录、LIS系统标本处理等。',
    daysNoBusiness: 125,
    daysText: '连续 125 天',
    actualTitle: '未发生任何检验业务',
    conclusion: '为满足定级硬性指标虚设检验科，实际标本全量非法外送第三方。',
    actionText: '发起撤销校验',
  },
  {
    id: '460200311-anesthesia',
    orgName: '某县现代医疗美容诊所',
    orgCode: '460200311',
    orgLevel: '未定级',
    suspectSubject: '麻醉科',
    expected: '全麻手术记录、麻醉药品(如丙泊酚)消耗、麻醉师术前访视。',
    daysNoBusiness: 98,
    daysText: '连续 98 天',
    actualTitle: '无合法麻醉记录单',
    conclusion: '无专职麻醉师打卡，涉嫌挂靠科室资质或违规开展“黑麻醉”。',
    actionText: '卫监局现场稽查',
  },
  {
    id: '460300122-ob',
    orgName: '某镇中心卫生院',
    orgCode: '460300122',
    orgLevel: '一级公立',
    suspectSubject: '妇产科专业',
    expected: 'ICD包含O类编码(妊娠/分娩)，产检本建档、妇科常规检查等。',
    daysNoBusiness: 42,
    daysText: '已空载 42 天',
    actualTitle: '门诊/住院人次均为0',
    conclusion: '业务极度萎缩，可能因专科人员流失导致事实停诊，触发黄色预警。',
    actionText: '下发督办提醒函',
  },
])

const filteredRows = computed(() => {
  const q = keyword.value.trim()
  if (!q) return rows.value
  return rows.value.filter((r) =>
    [r.orgName, r.orgCode, r.orgLevel, r.suspectSubject].some((v) => v.toLowerCase().includes(q.toLowerCase())),
  )
})

const kpi = computed(() => ({
  totalApproved: 21845,
  warnOver30: 182,
  redlineOver90: 34,
  top3: [
    { name: '医学检验科', percent: 80, color: '#EF4444' },
    { name: '麻醉科', percent: 55, color: '#F59E0B' },
    { name: '预防保健科', percent: 40, color: '#265EE6' },
  ],
}))
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
