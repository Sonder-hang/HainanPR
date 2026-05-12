<template>
  <div class="flex h-full min-h-0 flex-col bg-[#F4F6F8] font-sans text-[#333333]">
    <!-- 顶栏（嵌入全局壳，不含左侧深色边栏） -->
    <header
      class="flex min-h-[102px] shrink-0 flex-col justify-center gap-4 border-b border-[#E5E7EB] bg-white px-4 py-4 shadow-sm sm:flex-row sm:items-center sm:justify-between sm:px-8"
    >
      <div class="flex min-w-0 flex-wrap items-center gap-3">
        <h2 class="text-[20px] font-bold tracking-tight text-[#1F2937] sm:text-[22px] lg:text-[24px]">
          诊疗记录监管与预警中心
        </h2>
        <span
          class="inline-flex items-center gap-1 rounded-full border border-[#FECACA] bg-[#FEF2F2] px-3 py-1 text-[11px] font-bold tracking-wide text-[#EF4444] sm:text-[12px]"
        >
          <Activity :size="14" class="animate-pulse" />
          实时捕获异常线索
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
            placeholder="输入医师、身份证或疾病ICD编码..."
            class="w-full min-w-0 rounded-lg border border-[#D1D5DB] bg-[#F9FAFB] py-2.5 pl-10 pr-4 text-[14px] text-[#374151] outline-none transition-all placeholder:text-[#9CA3AF] focus:border-[#265EE6] focus:bg-white focus:ring-2 focus:ring-[#265EE6]/20 sm:w-[min(340px,100%)]"
          />
        </div>
        <button
          type="button"
          class="flex shrink-0 items-center gap-2 whitespace-nowrap rounded-lg bg-[#265EE6] px-5 py-2.5 text-[14px] font-medium text-white shadow-sm shadow-[#265EE6]/30 transition-colors hover:bg-[#1E4BD8]"
        >
          <Filter :size="16" />
          综合筛选
        </button>
      </div>
    </header>

    <div class="treatment-scroll relative flex-1 overflow-y-auto p-6 sm:p-8">
      <div class="mx-auto max-w-[1400px] space-y-6 pb-12 animate-fade-in">
        <!-- KPI -->
        <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
          <div class="flex items-center justify-between rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm">
            <div>
              <p class="mb-1 text-[14px] font-medium text-[#6B7280]">今日解析病历数据</p>
              <p class="text-[28px] font-black text-[#1F2937]">
                128,402 <span class="text-[12px] font-normal text-[#9CA3AF]">份</span>
              </p>
            </div>
            <div class="rounded-lg bg-[#EEF2FF] p-3 text-[#265EE6]">
              <Database :size="24" />
            </div>
          </div>
          <div class="flex items-center justify-between rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm">
            <div>
              <p class="mb-1 text-[14px] font-medium text-[#6B7280]">建立疾病/范围映射规则</p>
              <p class="text-[28px] font-black text-[#1F2937]">
                45,190 <span class="text-[12px] font-normal text-[#9CA3AF]">条</span>
              </p>
            </div>
            <div class="rounded-lg bg-[#ECFDF5] p-3 text-[#10B981]">
              <Network :size="24" />
            </div>
          </div>
          <div
            class="group relative overflow-hidden rounded-xl border border-[#EF4444]/30 bg-white shadow-md"
          >
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#EF4444]" />
            <div class="flex items-center justify-between p-6 pl-7">
              <div>
                <p class="mb-1 text-[14px] font-bold text-[#EF4444]">短时跨机构异常预警</p>
                <p class="text-[28px] font-black text-[#B91C1C]">
                  3 <span class="text-[12px] font-normal text-[#EF4444]">名医师</span>
                </p>
              </div>
              <div class="rounded-lg bg-[#FEF2F2] p-3 text-[#EF4444]">
                <Clock :size="24" />
              </div>
            </div>
          </div>
          <div
            class="group relative overflow-hidden rounded-xl border border-[#F59E0B]/30 bg-white shadow-md"
          >
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#F59E0B]" />
            <div class="flex items-center justify-between p-6 pl-7">
              <div>
                <p class="mb-1 text-[14px] font-bold text-[#D97706]">超执业范围预警</p>
                <p class="text-[28px] font-black text-[#92400E]">
                  17 <span class="text-[12px] font-normal text-[#D97706]">份病历</span>
                </p>
              </div>
              <div class="rounded-lg bg-[#FFFBEB] p-3 text-[#F59E0B]">
                <FileWarning :size="24" />
              </div>
            </div>
          </div>
        </div>

        <!-- 模块 1：短时跨机构 -->
        <div class="overflow-hidden rounded-xl border border-[#E5E7EB] bg-white shadow-sm">
          <div
            class="flex flex-col gap-4 border-b border-[#E5E7EB] bg-[#F9FAFB] p-5 sm:flex-row sm:items-center sm:justify-between"
          >
            <div>
              <h3 class="flex items-center gap-2 text-[18px] font-bold text-[#1F2937]">
                <Clock class="text-[#EF4444]" :size="20" />
                医师短时跨机构诊疗异常监测雷达 (1小时内)
              </h3>
              <p class="mt-1.5 text-[13px] text-[#6B7280]">
                底层逻辑：同一医师(身份证/资格证)在
                <span class="font-bold text-[#EF4444]">1小时内</span>，在不同医疗机构系统中出现签名或操作记录，涉嫌冒名顶替或违规飞刀。
              </p>
            </div>
            <button
              type="button"
              class="shrink-0 rounded border border-[#D1D5DB] bg-white px-4 py-2 text-[13px] font-medium text-[#4B5563] transition-colors hover:bg-[#F3F4F6]"
            >
              导出线索清单
            </button>
          </div>

          <div class="bg-[#FEF2F2]/30 p-6">
            <div class="rounded-xl border border-[#FECACA] bg-white p-6 shadow-sm">
              <div
                class="mb-6 flex flex-col gap-4 border-b border-[#FEE2E2] pb-4 sm:flex-row sm:items-center sm:justify-between"
              >
                <div class="flex items-center gap-4">
                  <div
                    class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full border border-[#FECACA] bg-[#FEF2F2] text-[18px] font-bold text-[#EF4444]"
                  >
                    庄*
                  </div>
                  <div>
                    <p class="text-[16px] font-bold text-[#1F2937]">涉事医师：庄**</p>
                    <p class="mt-0.5 font-mono text-[13px] text-[#6B7280]">
                      证件号码：440803197106172932
                    </p>
                  </div>
                </div>
                <div class="text-left sm:text-right">
                  <span
                    class="inline-flex items-center gap-1.5 rounded-full bg-[#EF4444] px-3 py-1.5 text-[13px] font-bold text-white shadow-sm"
                  >
                    <OctagonAlert :size="16" />
                    高危：时空极度冲突
                  </span>
                </div>
              </div>

              <div class="relative flex flex-col items-center gap-6 lg:flex-row">
                <!-- 地点 A -->
                <div class="relative w-full flex-1 rounded-lg border border-[#E5E7EB] bg-[#F9FAFB] p-5">
                  <span
                    class="absolute -top-3 left-4 rounded bg-[#6B7280] px-2 py-0.5 text-[11px] text-white shadow-sm"
                    >时间起点</span
                  >
                  <div class="mb-2 flex items-center gap-2">
                    <MapPin class="text-[#4B5563]" :size="18" />
                    <h4 class="text-[15px] font-bold text-[#1F2937]">东方市人民医院</h4>
                  </div>
                  <p class="mb-3 text-[13px] text-[#6B7280]">记录来源：门急诊 (编号:2485972)</p>
                  <div class="rounded border border-[#E5E7EB] bg-white p-3 shadow-inner">
                    <p class="font-mono text-[18px] font-bold text-[#374151]">
                      2026-01-09 <span class="text-[#265EE6]">09:51:29</span>
                    </p>
                    <p class="mt-1 text-[12px] text-[#9CA3AF]">处方类型：门特</p>
                  </div>
                </div>

                <!-- 中间 -->
                <div
                  class="relative z-10 flex w-full shrink-0 flex-col items-center justify-center py-4 lg:w-[140px] lg:py-0"
                >
                  <div
                    class="pointer-events-none absolute left-0 right-0 top-1/2 -z-10 hidden h-[2px] -translate-y-1/2 bg-gradient-to-r from-[#D1D5DB] via-[#EF4444] to-[#D1D5DB] lg:block"
                  />
                  <div
                    class="mb-2 rounded-full border-2 border-[#EF4444] bg-[#FEF2F2] p-2 shadow-[0_0_15px_rgba(239,68,68,0.3)]"
                  >
                    <Clock class="text-[#EF4444]" :size="24" />
                  </div>
                  <p class="rounded bg-white px-2 text-[14px] font-black text-[#EF4444]">相差仅 24 分钟</p>
                  <p class="mt-1 bg-white px-1 text-center text-[11px] text-[#EF4444]">物理距离无法达成</p>
                </div>

                <!-- 地点 B -->
                <div
                  class="relative w-full flex-1 rounded-lg border border-[#FECACA] bg-[#FEF2F2] p-5 shadow-sm"
                >
                  <span
                    class="absolute -top-3 left-4 rounded bg-[#EF4444] px-2 py-0.5 text-[11px] text-white shadow-sm"
                    >冲突终点</span
                  >
                  <div class="mb-2 flex items-center gap-2">
                    <Building class="text-[#EF4444]" :size="18" />
                    <h4 class="text-[15px] font-bold text-[#991B1B]">海南医学院第二附属医院</h4>
                  </div>
                  <p class="mb-3 text-[13px] text-[#EF4444]">记录来源：住院流水 (编号:1315713)</p>
                  <div class="rounded border border-[#FECACA] bg-white p-3 shadow-inner">
                    <p class="font-mono text-[18px] font-bold text-[#B91C1C]">
                      2026-01-09 <span class="text-[#EF4444]">10:16:27</span>
                    </p>
                    <p
                      class="mt-2 bg-[#FFF1F2] p-1.5 text-[13px] font-medium text-[#1F2937] rounded"
                    >
                      医嘱：申请O型RhD阳性新鲜冰冻血浆200ML
                    </p>
                  </div>
                </div>
              </div>

              <div class="mt-6 flex flex-wrap justify-end gap-3 border-t border-[#FEE2E2] pt-4">
                <button
                  type="button"
                  class="rounded border border-[#D1D5DB] bg-white px-5 py-2 text-[13px] font-medium text-[#4B5563] transition-colors hover:bg-[#F3F4F6]"
                >
                  标记为误报
                </button>
                <button
                  type="button"
                  class="flex items-center gap-2 rounded bg-[#EF4444] px-5 py-2 text-[13px] font-bold text-white shadow-sm transition-colors hover:bg-[#DC2626]"
                >
                  <ShieldAlert :size="16" />
                  下发警告并冻结权限
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 模块 2：超执业范围 -->
        <div class="overflow-hidden rounded-xl border border-[#E5E7EB] bg-white shadow-sm">
          <div class="border-b border-[#E5E7EB] bg-[#F9FAFB] p-5">
            <h3 class="flex items-center gap-2 text-[18px] font-bold text-[#1F2937]">
              <Network class="text-[#F59E0B]" :size="20" />
              超执业范围智能拦截引擎 (病历数据反向解析)
            </h3>
            <p class="mt-1.5 text-[13px] text-[#6B7280]">
              底层逻辑：基于省人民医院海量病历解析，建立
              <span class="font-bold text-[#1F2937]">ICD诊断/手术代码 ↔ 对应亚专科 ↔ 法定执业类别</span>
              的映射知识库，智能比对越界行为。
            </p>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full min-w-[900px] text-left text-[14px]">
              <thead class="border-b border-[#E5E7EB] bg-[#F3F4F6]">
                <tr>
                  <th class="w-[15%] p-4 font-semibold text-[#4B5563]">涉事机构与医师</th>
                  <th class="w-[20%] p-4 font-semibold text-[#4B5563]">法定执业范围 (民科)</th>
                  <th class="w-[25%] border-l border-[#E5E7EB] p-4 font-semibold text-[#4B5563]">
                    HIS捕获实际行为 (病历/医嘱)
                  </th>
                  <th class="w-[30%] border-l border-[#E5E7EB] p-4 font-semibold text-[#4B5563]">
                    AI 映射引擎分析过程
                  </th>
                  <th class="w-[10%] p-4 text-center font-semibold text-[#4B5563]">处理</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#E5E7EB]">
                <tr class="group transition-colors hover:bg-[#F9FAFB]">
                  <td class="p-4">
                    <p class="text-[15px] font-bold text-[#1F2937]">某民营口腔诊所</p>
                    <p class="mt-1 flex items-center gap-1 text-[13px] text-[#4B5563]">
                      <Stethoscope :size="14" class="text-[#9CA3AF]" />
                      王*平
                    </p>
                  </td>
                  <td class="p-4">
                    <span
                      class="inline-block rounded border border-[#C7D2FE] bg-[#EEF2FF] px-3 py-1.5 text-[13px] font-bold text-[#265EE6]"
                      >口腔专业</span
                    >
                  </td>
                  <td class="border-l border-[#E5E7EB] bg-[#FFFBEB]/30 p-4">
                    <p class="mb-1 text-[13px] text-[#6B7280]">门诊主诊断与处方：</p>
                    <p class="text-[14px] font-bold text-[#1F2937]">K35.8 急性单纯性阑尾炎</p>
                    <p class="mt-1 text-[12px] text-[#9CA3AF]">开具：头孢克肟及腹部彩超</p>
                  </td>
                  <td class="border-l border-[#E5E7EB] bg-[#FFFBEB]/50 p-4">
                    <div class="flex items-start gap-2">
                      <Share2 class="mt-0.5 shrink-0 text-[#F59E0B]" :size="16" />
                      <div>
                        <div
                          class="mb-2 flex w-fit items-center rounded border border-[#E5E7EB] bg-white px-2 py-1 font-mono text-[12px] text-[#6B7280] shadow-sm"
                        >
                          K35.8
                          <ArrowRight :size="12" class="mx-1 text-[#D1D5DB]" />
                          普外科
                          <ArrowRight :size="12" class="mx-1 text-[#D1D5DB]" />
                          <span class="ml-1 font-bold text-[#1F2937]">外科专业</span>
                        </div>
                        <p class="text-[13px] leading-tight text-[#92400E]">
                          该疾病及处置属于<span class="font-bold">【外科专业】</span>范畴，与医师当前备案资质<span
                            class="font-bold"
                            >【口腔专业】</span
                          >存在严重冲突！
                        </p>
                      </div>
                    </div>
                  </td>
                  <td class="p-4 text-center">
                    <button
                      type="button"
                      class="rounded border border-[#FDE68A] bg-[#FEF3C7] px-3 py-1.5 text-[13px] font-bold text-[#D97706] hover:underline"
                    >
                      下发警告
                    </button>
                  </td>
                </tr>

                <tr class="group transition-colors hover:bg-[#F9FAFB]">
                  <td class="p-4">
                    <p class="text-[15px] font-bold text-[#1F2937]">某县级中医院</p>
                    <p class="mt-1 flex items-center gap-1 text-[13px] text-[#4B5563]">
                      <Stethoscope :size="14" class="text-[#9CA3AF]" />
                      刘*
                    </p>
                  </td>
                  <td class="p-4">
                    <span
                      class="inline-block rounded border border-[#E5E7EB] bg-[#F3F4F6] px-3 py-1.5 text-[13px] font-bold text-[#4B5563]"
                      >中医专业</span
                    >
                  </td>
                  <td class="border-l border-[#E5E7EB] bg-[#FFFBEB]/30 p-4">
                    <p class="mb-1 text-[13px] text-[#6B7280]">住院部手术操作：</p>
                    <p class="text-[14px] font-bold text-[#1F2937]">85.520x 聚丙烯酰胺水凝胶注射隆胸</p>
                  </td>
                  <td class="border-l border-[#E5E7EB] bg-[#FFFBEB]/50 p-4">
                    <div class="flex items-start gap-2">
                      <Share2 class="mt-0.5 shrink-0 text-[#F59E0B]" :size="16" />
                      <div>
                        <div
                          class="mb-2 flex w-fit items-center rounded border border-[#E5E7EB] bg-white px-2 py-1 font-mono text-[12px] text-[#6B7280] shadow-sm"
                        >
                          85.520x
                          <ArrowRight :size="12" class="mx-1 text-[#D1D5DB]" />
                          医疗美容科
                          <ArrowRight :size="12" class="mx-1 text-[#D1D5DB]" />
                          <span class="ml-1 font-bold text-[#1F2937]">外科/医美专业</span>
                        </div>
                        <p class="text-[13px] leading-tight text-[#92400E]">
                          该手术操作属于<span class="font-bold">【外科/医美专业】</span>，与医师<span
                            class="font-bold"
                            >【中医专业】</span
                          >冲突，且涉及违规操作。
                        </p>
                      </div>
                    </div>
                  </td>
                  <td class="p-4 text-center">
                    <button
                      type="button"
                      class="rounded border border-[#FDE68A] bg-[#FEF3C7] px-3 py-1.5 text-[13px] font-bold text-[#D97706] hover:underline"
                    >
                      下发警告
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
  Database,
  Network,
  Clock,
  FileWarning,
  Search,
  Filter,
  MapPin,
  Building,
  OctagonAlert,
  ArrowRight,
  Share2,
  Activity,
  Stethoscope,
} from 'lucide-vue-next'
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

.treatment-scroll::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.treatment-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.treatment-scroll::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}
.treatment-scroll::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>
