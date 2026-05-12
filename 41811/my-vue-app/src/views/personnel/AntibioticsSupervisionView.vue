<template>
  <div class="flex h-full min-h-0 flex-col bg-[#F4F6F8] font-sans text-[#333333]">
    <!-- 顶栏（嵌入全局壳，无左侧深色边栏） -->
    <header
      class="flex min-h-[102px] shrink-0 flex-col justify-center gap-4 border-b border-[#E5E7EB] bg-white px-4 py-4 shadow-sm sm:flex-row sm:items-center sm:justify-between sm:px-8"
    >
      <div class="flex min-w-0 flex-wrap items-center gap-3 sm:gap-4">
        <h2 class="text-[20px] font-bold tracking-tight text-[#1F2937] sm:text-[22px] lg:text-[24px]">
          抗菌药物分级管理智能监管
        </h2>
        <span
          class="inline-flex items-center gap-1 rounded-full border border-[#FECACA] bg-[#FEF2F2] px-2.5 py-1 text-[11px] font-bold tracking-wide text-[#EF4444] sm:text-[12px]"
        >
          <Activity :size="14" class="animate-pulse" />
          处方实时拦截监测中
        </span>
      </div>
      <div class="flex flex-wrap items-center gap-3 sm:gap-4">
        <div class="relative min-w-0 flex-1 sm:flex-initial">
          <Search
            class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-[#9CA3AF]"
            :size="18"
          />
          <input
            type="text"
            placeholder="输入药品名称、开单医师或机构..."
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

    <div class="abx-scroll flex-1 overflow-y-auto p-6 sm:p-8">
      <div class="mx-auto max-w-[1400px] space-y-6 pb-12 animate-fade-in">
        <!-- 政策与规则导读 -->
        <div
          class="flex flex-col gap-6 rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm lg:flex-row lg:items-start"
        >
          <div class="shrink-0 rounded-xl bg-[#EEF2FF] p-4 text-[#265EE6]">
            <Pill :size="32" stroke-width="1.5" />
          </div>
          <div class="min-w-0 flex-1">
            <h3 class="mb-2 text-[18px] font-bold text-[#1F2937]">抗菌药物分级管控规则引擎</h3>
            <p class="mb-3 text-[14px] leading-relaxed text-[#6B7280]">
              基于《抗菌药物临床应用管理办法》及《海南省2024版分级目录》建立实时审方规则：<br />
              1.
              <span class="font-bold text-[#EF4444]">特殊使用级：</span>必须由<span class="font-bold text-[#1F2937]"
                >副高级及以上</span
              >职称医师开具（系统实时比对HIS与民科职称数据）。<br />
              2.
              <span class="font-bold text-[#F59E0B]">标记“#”品种：</span>（如替加环素#、多粘菌素B#等）原则限三级医院使用，其他机构需抓取<span
                class="font-bold text-[#1F2937]"
                >3名副高会诊记录</span
              >。
            </p>
          </div>
          <button
            type="button"
            class="shrink-0 self-start rounded border border-[#D1D5DB] px-4 py-2 text-[13px] font-medium text-[#4B5563] transition-colors hover:bg-[#F3F4F6] lg:self-center"
          >
            查看完整药品目录
          </button>
        </div>

        <!-- KPI -->
        <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
          <div class="relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#EF4444]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#6B7280]">违规开单总频次</p>
              <div class="rounded-lg bg-[#FEF2F2] p-2 text-[#EF4444]">
                <AlertTriangle :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#1F2937]">
              145 <span class="ml-1 text-[14px] font-normal text-[#6B7280]">笔</span>
            </p>
            <p class="mt-2 flex items-center gap-1 text-[12px] font-medium text-[#EF4444]">环比上月上涨 12%</p>
          </div>

          <div class="relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#F59E0B]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#6B7280]">涉及医疗机构</p>
              <div class="rounded-lg bg-[#FFFBEB] text-[#F59E0B]">
                <Building :size="20" class="p-2" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#1F2937]">
              12 <span class="ml-1 text-[14px] font-normal text-[#6B7280]">家</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#D97706]">含 3 家三级综合医院</p>
          </div>

          <div class="relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm">
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#10B981]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#6B7280]">涉及违规医师</p>
              <div class="rounded-lg bg-[#ECFDF5] p-2 text-[#10B981]">
                <Users :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#1F2937]">
              34 <span class="ml-1 text-[14px] font-normal text-[#6B7280]">人</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#10B981]">多为初/中级越权开单</p>
          </div>

          <div
            class="relative overflow-hidden rounded-xl border border-[#002140] bg-[#001529] p-6 text-white shadow-sm"
          >
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#9CA3AF]">高频违规药品 TOP 1</p>
              <div class="rounded-lg bg-[#265EE6]/20 p-2 text-[#60A5FA]">
                <Activity :size="20" />
              </div>
            </div>
            <p class="truncate text-[22px] font-black text-white">亚胺培南西司他丁</p>
            <p
              class="mt-3 inline-block rounded bg-[#265EE6]/20 px-2 py-1 text-[12px] font-medium text-[#60A5FA]"
            >
              碳青霉烯类 / 特殊使用级
            </p>
          </div>
        </div>

        <!-- 多维度分析 -->
        <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div class="rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm">
            <h3 class="mb-5 flex items-center gap-2 text-[16px] font-bold text-[#1F2937]">
              <BarChart3 class="text-[#265EE6]" :size="18" />
              违规药品分类维度分析
            </h3>
            <div class="space-y-5">
              <div v-for="(item, index) in drugAnalysis" :key="index">
                <div class="mb-1.5 flex justify-between text-[13px]">
                  <span class="font-bold text-[#374151]"
                    >{{ item.name }}
                    <span class="ml-1 font-normal text-[#9CA3AF]">{{ item.type }}</span></span
                  >
                  <span class="font-bold text-[#EF4444]"
                    >{{ item.count }} <span class="text-[12px] font-normal text-[#9CA3AF]">次</span></span
                  >
                </div>
                <div class="h-[8px] w-full overflow-hidden rounded-full bg-[#F3F4F6]">
                  <div
                    :class="['h-[8px] rounded-full', item.color]"
                    :style="{ width: `${item.percent}%` }"
                  />
                </div>
              </div>
            </div>
          </div>

          <div class="rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm">
            <h3 class="mb-5 flex items-center gap-2 text-[16px] font-bold text-[#1F2937]">
              <Building class="text-[#F59E0B]" :size="18" />
              违规开单机构维度分析
            </h3>
            <div class="space-y-5">
              <div v-for="(item, index) in hospitalAnalysis" :key="index">
                <div class="mb-1.5 flex justify-between text-[13px]">
                  <span class="font-bold text-[#374151]"
                    >{{ item.name }}
                    <span class="ml-1 font-normal text-[#9CA3AF]">{{ item.level }}</span></span
                  >
                  <span class="font-bold text-[#F59E0B]"
                    >{{ item.count }} <span class="text-[12px] font-normal text-[#9CA3AF]">次</span></span
                  >
                </div>
                <div class="h-[8px] w-full overflow-hidden rounded-full bg-[#F3F4F6]">
                  <div
                    :class="['h-[8px] rounded-full', item.color]"
                    :style="{ width: `${item.percent}%` }"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 实时台账 -->
        <div class="overflow-hidden rounded-xl border border-[#E5E7EB] bg-white shadow-sm">
          <div
            class="flex flex-col gap-3 border-b border-[#E5E7EB] bg-[#F9FAFB] p-5 sm:flex-row sm:items-center sm:justify-between"
          >
            <h3 class="flex items-center gap-2 text-[16px] font-bold text-[#1F2937]">
              <ShieldAlert class="text-[#EF4444]" :size="20" />
              抗菌药物违规开单实时监测台账 (联动提醒中心)
            </h3>
            <button
              type="button"
              class="flex items-center justify-center gap-2 rounded bg-[#265EE6] px-4 py-2 text-[13px] font-bold text-white shadow-sm transition-colors hover:bg-[#1E4BD8]"
            >
              <Send :size="14" />
              一键群发警告提醒
            </button>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full min-w-[900px] text-left text-[14px]">
              <thead class="border-b border-[#E5E7EB] bg-[#F3F4F6]">
                <tr>
                  <th class="w-[18%] p-4 font-semibold text-[#4B5563]">开单时间 / 机构</th>
                  <th class="w-[15%] p-4 font-semibold text-[#4B5563]">开单医师 / 职称</th>
                  <th class="w-[20%] border-l border-[#E5E7EB] p-4 font-semibold text-[#4B5563]">
                    开具药品 / 级别
                  </th>
                  <th class="w-[27%] border-l border-[#E5E7EB] p-4 font-semibold text-[#4B5563]">
                    触发监控逻辑引擎判定
                  </th>
                  <th class="w-[20%] border-l border-[#E5E7EB] p-4 text-center font-semibold text-[#4B5563]">
                    实时提醒操作
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#E5E7EB]">
                <tr class="group transition-colors hover:bg-[#F9FAFB]">
                  <td class="p-4">
                    <p class="font-mono text-[13px] font-bold text-[#1F2937]">2026-01-10 16:22:20</p>
                    <p class="mt-1.5 text-[13px] text-[#4B5563]">海口市中医医院</p>
                  </td>
                  <td class="p-4">
                    <p class="text-[15px] font-bold text-[#1F2937]">许**</p>
                    <p
                      class="mt-1.5 inline-block rounded border border-[#E5E7EB] bg-[#F3F4F6] px-2 py-0.5 text-[12px] text-[#4B5563]"
                    >
                      中级 (主治医师)
                    </p>
                  </td>
                  <td class="border-l border-[#E5E7EB] bg-[#FEF2F2]/30 p-4">
                    <p class="text-[15px] font-bold text-[#991B1B]">亚胺培南西司他丁</p>
                    <div class="mt-1.5 flex flex-wrap items-center gap-1.5">
                      <span
                        class="rounded border border-[#FECACA] bg-[#FEE2E2] px-1.5 py-0.5 text-[11px] font-bold text-[#B91C1C]"
                        >特殊使用级</span
                      >
                      <span class="text-[12px] text-[#6B7280]">碳青霉烯类</span>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4">
                    <div class="flex items-start gap-2 text-[#EF4444]">
                      <AlertTriangle :size="16" class="mt-0.5 shrink-0" />
                      <div>
                        <p class="text-[13px] font-bold">职称越权违规</p>
                        <p class="mt-1 text-[12px] leading-tight text-[#7F1D1D]">
                          规则要求【副高级及以上】，实际为【主治医师】，无特殊级处方权。
                        </p>
                      </div>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4 text-center">
                    <div class="flex flex-wrap justify-center gap-2">
                      <button
                        type="button"
                        class="flex items-center gap-1 rounded border border-[#C7D2FE] bg-[#EEF2FF] px-3 py-1.5 text-[12px] font-bold text-[#265EE6] transition-colors hover:bg-[#265EE6] hover:text-white"
                      >
                        <Bell :size="12" />
                        提醒医师
                      </button>
                      <button
                        type="button"
                        class="rounded border border-[#D1D5DB] bg-white px-3 py-1.5 text-[12px] font-medium text-[#4B5563] transition-colors hover:bg-[#F3F4F6]"
                      >
                        通报医院
                      </button>
                    </div>
                  </td>
                </tr>

                <tr class="group transition-colors hover:bg-[#F9FAFB]">
                  <td class="p-4">
                    <p class="font-mono text-[13px] font-bold text-[#1F2937]">2026-01-10 14:15:00</p>
                    <p class="mt-1.5 text-[13px] text-[#4B5563]">
                      某县级人民医院
                      <span class="ml-1 rounded bg-[#E5E7EB] px-1 text-[11px]">二级</span>
                    </p>
                  </td>
                  <td class="p-4">
                    <p class="text-[15px] font-bold text-[#1F2937]">张**</p>
                    <p
                      class="mt-1.5 inline-block rounded border border-[#C7D2FE] bg-[#EEF2FF] px-2 py-0.5 text-[12px] font-bold text-[#265EE6]"
                    >
                      副高级 (副主任医师)
                    </p>
                  </td>
                  <td class="border-l border-[#E5E7EB] bg-[#FFFBEB]/30 p-4">
                    <p class="text-[15px] font-bold text-[#92400E]">替加环素#</p>
                    <div class="mt-1.5 flex flex-wrap items-center gap-1.5">
                      <span
                        class="rounded border border-[#FECACA] bg-[#FEE2E2] px-1.5 py-0.5 text-[11px] font-bold text-[#B91C1C]"
                        >特殊使用级</span
                      >
                      <span
                        class="rounded border border-[#FDE68A] bg-[#FEF3C7] px-1.5 py-0.5 text-[11px] font-bold text-[#D97706]"
                        >带#号管控</span
                      >
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4">
                    <div class="flex items-start gap-2 text-[#F59E0B]">
                      <FileWarning :size="16" class="mt-0.5 shrink-0" />
                      <div>
                        <p class="text-[13px] font-bold">超机构级别管控预警</p>
                        <p class="mt-1 text-[12px] leading-tight text-[#92400E]">
                          带#号药品限三级医院使用，二级机构使用未检索到【3名副高会诊记录】。
                        </p>
                      </div>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4 text-center">
                    <span
                      class="inline-flex items-center gap-1 rounded border border-[#A7F3D0] bg-[#ECFDF5] px-3 py-1.5 text-[12px] font-bold text-[#10B981]"
                    >
                      <CheckCircle :size="12" />
                      已通报医院
                    </span>
                  </td>
                </tr>

                <tr class="group transition-colors hover:bg-[#F9FAFB]">
                  <td class="p-4">
                    <p class="font-mono text-[13px] font-bold text-[#1F2937]">2026-01-09 09:30:12</p>
                    <p class="mt-1.5 text-[13px] text-[#4B5563]">省人民医院秀英院区</p>
                  </td>
                  <td class="p-4">
                    <p class="text-[15px] font-bold text-[#1F2937]">蒲**</p>
                    <p
                      class="mt-1.5 inline-block rounded border border-[#FECACA] bg-[#FEF2F2] px-2 py-0.5 text-[12px] font-bold text-[#EF4444]"
                    >
                      初级 (住院医师)
                    </p>
                  </td>
                  <td class="border-l border-[#E5E7EB] bg-[#FEF2F2]/30 p-4">
                    <p class="text-[15px] font-bold text-[#991B1B]">美罗培南</p>
                    <div class="mt-1.5 flex flex-wrap items-center gap-1.5">
                      <span
                        class="rounded border border-[#FECACA] bg-[#FEE2E2] px-1.5 py-0.5 text-[11px] font-bold text-[#B91C1C]"
                        >特殊使用级</span
                      >
                      <span class="text-[12px] text-[#6B7280]">碳青霉烯类</span>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4">
                    <div class="flex items-start gap-2 text-[#EF4444]">
                      <ShieldAlert :size="16" class="mt-0.5 shrink-0" />
                      <div>
                        <p class="text-[13px] font-bold">严重职称越权</p>
                        <p class="mt-1 text-[12px] leading-tight text-[#7F1D1D]">
                          初级医师开具特殊使用级药品，存在极大用药风险，已触发最高级别拦截。
                        </p>
                      </div>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4 text-center">
                    <button
                      type="button"
                      class="inline-flex items-center gap-1 rounded border border-[#FECACA] bg-[#FEF2F2] px-3 py-1.5 text-[12px] font-bold text-[#EF4444] transition-colors hover:bg-[#EF4444] hover:text-white"
                    >
                      <Bell :size="12" />
                      严重警告医师
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
import {
  ShieldAlert,
  Users,
  Activity,
  Search,
  Filter,
  Pill,
  AlertTriangle,
  Building,
  Bell,
  Send,
  FileWarning,
  CheckCircle,
  BarChart3,
} from 'lucide-vue-next'

const drugAnalysis = [
  { name: '亚胺培南西司他丁', type: '(碳青霉烯类/特殊级)', count: 48, percent: 85, color: 'bg-[#EF4444]' },
  { name: '替加环素#', type: '(四环素类/特殊级)', count: 35, percent: 60, color: 'bg-[#F87171]' },
  { name: '头孢哌酮/舒巴坦', type: '(头孢类/限制级)', count: 28, percent: 45, color: 'bg-[#F59E0B]' },
  { name: '多粘菌素B#', type: '(多粘菌素类/特殊级)', count: 18, percent: 30, color: 'bg-[#FBBF24]' },
  { name: '万古霉素', type: '(糖肽类/特殊级)', count: 16, percent: 25, color: 'bg-[#60A5FA]' },
]

const hospitalAnalysis = [
  { name: '海口市中医医院', level: '三级', count: 32, percent: 75, color: 'bg-[#F59E0B]' },
  { name: '海南省人民医院秀英院区', level: '三级', count: 28, percent: 65, color: 'bg-[#FBBF24]' },
  { name: '某县级人民医院', level: '二级', count: 22, percent: 50, color: 'bg-[#FCD34D]' },
  { name: '儋州市人民医院', level: '三级', count: 18, percent: 40, color: 'bg-[#60A5FA]' },
  { name: '三亚市妇幼保健院', level: '三级', count: 15, percent: 35, color: 'bg-[#93C5FD]' },
]
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

.abx-scroll::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.abx-scroll::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}
.abx-scroll::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>
