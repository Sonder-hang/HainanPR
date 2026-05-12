<template>
  <div class="flex h-full min-h-0 flex-col bg-[#F4F6F8] font-sans text-[#333333]">
    <header
      class="flex min-h-[102px] shrink-0 flex-col justify-center gap-4 border-b border-[#E5E7EB] bg-white px-4 py-4 shadow-sm sm:flex-row sm:items-center sm:justify-between sm:px-8"
    >
      <div class="flex min-w-0 flex-wrap items-center gap-3 sm:gap-4">
        <h2 class="text-[20px] font-bold tracking-tight text-[#1F2937] sm:text-[22px] lg:text-[24px]">
          多点执业记录监管
        </h2>
        <span
          class="inline-flex items-center gap-1 rounded-full border border-[#FDE68A] bg-[#FFFBEB] px-2.5 py-1 text-[11px] font-bold tracking-wide text-[#D97706] sm:text-[12px]"
        >
          <Activity :size="14" class="animate-pulse" />
          全省 HIS 数据实时检索中
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
            placeholder="输入医师姓名、身份证或民营机构名称..."
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

    <div class="multisite-scroll flex-1 overflow-y-auto p-6 sm:p-8">
      <div class="mx-auto max-w-[1400px] space-y-6 pb-12 animate-fade-in">
        <div class="flex flex-col overflow-hidden rounded-xl border border-[#E5E7EB] bg-white shadow-sm lg:flex-row">
          <div
            class="flex flex-col justify-center border-b border-[#E5E7EB] bg-gradient-to-br from-[#F8FAFC] to-[#F1F5F9] p-8 lg:w-[40%] lg:border-b-0 lg:border-r"
          >
            <div
              class="mb-4 w-fit rounded-xl border border-[#C7D2FE] bg-[#EEF2FF] p-3 text-[#265EE6] shadow-sm"
            >
              <MapPin :size="28" stroke-width="2" />
            </div>
            <h3 class="mb-3 text-[20px] font-bold text-[#1F2937]">公立向民营违规执业监测模型</h3>
            <p class="mb-4 text-[14px] leading-relaxed text-[#4B5563]">
              依据省卫生健康委加强公立医疗机构医师多点执业管理有关要求，<span class="font-bold text-[#EF4444]"
                >原则上严控公立医院医师至民营医院多点执业。</span
              >
            </p>
            <div class="mt-auto space-y-3">
              <div
                class="flex items-center gap-2 rounded border border-[#E5E7EB] bg-white p-2.5 text-[13px] text-[#4B5563] shadow-sm"
              >
                <Database class="shrink-0 text-[#265EE6]" :size="16" />
                <span
                  ><strong class="text-[#1F2937]">民科系统基准：</strong>提取主执业机构为“公立”的医师名单。</span
                >
              </div>
              <div
                class="flex items-center gap-2 rounded border border-[#E5E7EB] bg-white p-2.5 text-[13px] text-[#4B5563] shadow-sm"
              >
                <Search class="shrink-0 text-[#EF4444]" :size="16" />
                <span
                  ><strong class="text-[#1F2937]">HIS 系统侦测：</strong>在全省民营机构内检索该医师的业务签名留痕。</span
                >
              </div>
            </div>
          </div>

          <div class="relative flex flex-1 items-center justify-center bg-white p-8 lg:w-[60%]">
            <div class="relative z-10 flex w-full max-w-[600px] items-center justify-between">
              <div class="flex w-[140px] flex-col items-center gap-3 sm:w-[160px]">
                <div
                  class="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl border-2 border-[#A5B4FC] bg-[#EEF2FF] text-[#265EE6] shadow-inner sm:h-20 sm:w-20"
                >
                  <Building :size="36" />
                </div>
                <div class="text-center">
                  <p class="text-[15px] font-bold text-[#1F2937]">民科系统</p>
                  <p class="mt-0.5 text-[12px] text-[#6B7280]">公立医师池 (31,402人)</p>
                </div>
              </div>

              <div class="relative flex flex-1 flex-col items-center px-2">
                <div class="absolute left-0 right-0 top-[2.5rem] z-0 hidden h-[2px] -translate-y-1/2 bg-gradient-to-r from-[#A5B4FC] via-[#FCA5A5] to-[#FCA5A5] sm:block" />
                <div class="relative z-10 rounded-full border-2 border-[#F59E0B] bg-white p-3 shadow-[0_0_15px_rgba(245,158,11,0.3)]">
                  <FileWarning class="text-[#F59E0B]" :size="28" />
                </div>
                <p
                  class="mt-3 rounded-full border border-[#FDE68A] bg-[#FFFBEB] px-3 py-1 text-[13px] font-bold text-[#D97706]"
                >
                  智能比对碰撞
                </p>
              </div>

              <div class="flex w-[140px] flex-col items-center gap-3 sm:w-[160px]">
                <div
                  class="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl border-2 border-[#FCA5A5] bg-[#FEF2F2] text-[#EF4444] shadow-inner sm:h-20 sm:w-20"
                >
                  <Activity :size="36" />
                </div>
                <div class="text-center">
                  <p class="text-[15px] font-bold text-[#1F2937]">民营医院 HIS</p>
                  <p class="mt-0.5 text-[12px] text-[#6B7280]">处方/医嘱签名日志</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
          <div
            class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#265EE6]"
          >
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#265EE6]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#6B7280]">全省公立医师基数</p>
              <div class="rounded-lg bg-[#EEF2FF] p-2 text-[#265EE6]">
                <Users :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#1F2937]">
              31,402 <span class="ml-1 text-[14px] font-normal text-[#6B7280]">人</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#6B7280]">纳入监测范围</p>
          </div>

          <div
            class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#EF4444]"
          >
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#EF4444]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#6B7280]">捕获违规多点执业线索</p>
              <div class="rounded-lg bg-[#FEF2F2] p-2 text-[#EF4444]">
                <ShieldAlert :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#EF4444]">
              28 <span class="ml-1 text-[14px] font-normal text-[#6B7280]">人次</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#EF4444]">本月新增违规线索</p>
          </div>

          <div
            class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#F59E0B]"
          >
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#F59E0B]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#6B7280]">涉及违规接纳的民营机构</p>
              <div class="rounded-lg bg-[#FFFBEB] p-2 text-[#F59E0B]">
                <Building :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#1F2937]">
              12 <span class="ml-1 text-[14px] font-normal text-[#6B7280]">家</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#D97706]">需下发机构整改通知</p>
          </div>

          <div
            class="flex flex-col justify-center overflow-hidden rounded-xl border border-[#002140] bg-[#001529] p-6 text-white shadow-sm"
          >
            <p class="mb-3 text-[14px] font-medium text-[#9CA3AF]">最常被抓取的违规证据类型</p>
            <div class="space-y-2">
              <div class="flex items-center justify-between text-[13px]">
                <span class="flex items-center gap-2 text-white"
                  ><span class="h-1.5 w-1.5 shrink-0 rounded-full bg-[#EF4444]" /> 门诊电子处方签名</span
                >
                <span class="font-bold text-[#9CA3AF]">45%</span>
              </div>
              <div class="flex items-center justify-between text-[13px]">
                <span class="flex items-center gap-2 text-white"
                  ><span class="h-1.5 w-1.5 shrink-0 rounded-full bg-[#F59E0B]" /> 手术主刀/一助记录</span
                >
                <span class="font-bold text-[#9CA3AF]">35%</span>
              </div>
              <div class="flex items-center justify-between text-[13px]">
                <span class="flex items-center gap-2 text-white"
                  ><span class="h-1.5 w-1.5 shrink-0 rounded-full bg-[#265EE6]" /> 住院查房医嘱</span
                >
                <span class="font-bold text-[#9CA3AF]">20%</span>
              </div>
            </div>
          </div>
        </div>

        <div class="overflow-hidden rounded-xl border border-[#E5E7EB] bg-white shadow-sm">
          <div
            class="flex flex-col gap-3 border-b border-[#E5E7EB] bg-[#F9FAFB] p-5 sm:flex-row sm:items-center sm:justify-between"
          >
            <h3 class="flex items-center gap-2 text-[16px] font-bold text-[#1F2937]">
              <AlertTriangle class="text-[#EF4444]" :size="20" />
              公转民违规执业线索台账 (实时生成)
            </h3>
            <button
              type="button"
              class="rounded border border-[#D1D5DB] bg-white px-3 py-1.5 text-[13px] font-medium text-[#4B5563] transition-colors hover:bg-[#F3F4F6]"
            >
              导出工单
            </button>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full min-w-[900px] text-left text-[14px]">
              <thead class="border-b border-[#E5E7EB] bg-white">
                <tr>
                  <th class="w-[15%] p-4 font-semibold text-[#4B5563]">医师基础信息</th>
                  <th
                    class="w-[20%] border-l border-[#E0E7FF] bg-[#EEF2FF]/30 p-4 font-semibold text-[#4B5563]"
                  >
                    民科系统 (主执业机构)
                  </th>
                  <th
                    class="w-[30%] border-l border-[#FECACA] bg-[#FEF2F2]/30 p-4 font-semibold text-[#4B5563]"
                  >
                    异地 HIS (侦测违规执业痕迹)
                  </th>
                  <th class="w-[20%] border-l border-[#E5E7EB] p-4 font-semibold text-[#4B5563]">
                    智能研判结论
                  </th>
                  <th class="w-[15%] border-l border-[#E5E7EB] p-4 text-center font-semibold text-[#4B5563]">
                    卫健委联动操作
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#F3F4F6]">
                <tr class="group transition-colors hover:bg-[#F9FAFB]">
                  <td class="p-4">
                    <p class="text-[16px] font-bold text-[#1F2937]">
                      吴*峰 <span class="ml-1 text-[12px] font-normal text-[#9CA3AF]">男</span>
                    </p>
                    <p class="mt-1 font-mono text-[12px] text-[#6B7280]">460102********1234</p>
                    <p class="mt-0.5 text-[12px] text-[#6B7280]">副主任医师</p>
                  </td>
                  <td class="border-l border-[#E0E7FF] bg-[#EEF2FF]/20 p-4">
                    <div class="space-y-1.5 text-[13px]">
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">主机构:</span>
                        <span class="font-bold text-[#1F2937]">海南省中医院</span>
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">性质:</span>
                        <span
                          class="rounded border border-[#C7D2FE] bg-[#EEF2FF] px-2 py-0.5 text-[11px] font-bold text-[#265EE6]"
                          >公立三甲</span
                        >
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">多点备案:</span>
                        <span class="text-[#6B7280]">无备案记录</span>
                      </p>
                    </div>
                  </td>
                  <td class="border-l border-[#FECACA] bg-[#FEF2F2]/20 p-4">
                    <div class="space-y-1.5 text-[13px]">
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">发现机构:</span>
                        <span class="font-bold text-[#991B1B]">海口康华现代医院</span>
                        <span class="ml-1 rounded bg-[#F3F4F6] px-1.5 py-0.5 text-[10px] text-[#4B5563]"
                          >民营</span
                        >
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">抓取证据:</span>
                        <span
                          class="border-b border-dashed border-[#9CA3AF] font-medium text-[#374151]"
                          >门诊电子病历签名 (2份)</span
                        >
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">发生时间:</span>
                        <span class="font-mono text-[#EF4444]">昨日 14:30 - 15:45</span>
                      </p>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4">
                    <div class="flex items-start gap-1.5 text-[#EF4444]">
                      <ShieldAlert :size="16" class="mt-0.5 shrink-0" />
                      <div>
                        <p class="text-[14px] font-bold">未备案私自多点执业</p>
                        <p class="mt-1 text-[12px] leading-tight text-[#991B1B]">
                          公立医师未备案，在民营医院产生门诊接诊记录，涉嫌违规走穴。
                        </p>
                      </div>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4 text-center">
                    <div class="flex flex-col gap-2">
                      <button
                        type="button"
                        class="flex items-center justify-center gap-1 rounded border border-[#C7D2FE] bg-[#EEF2FF] px-3 py-1.5 text-[12px] font-bold text-[#265EE6] transition-colors hover:bg-[#265EE6] hover:text-white"
                      >
                        <Bell :size="12" />
                        提醒涉事医师
                      </button>
                      <button
                        type="button"
                        class="flex items-center justify-center gap-1 rounded border border-[#FECACA] bg-[#FEF2F2] px-3 py-1.5 text-[12px] font-bold text-[#EF4444] transition-colors hover:bg-[#EF4444] hover:text-white"
                      >
                        <Send :size="12" />
                        通报民营机构
                      </button>
                    </div>
                  </td>
                </tr>

                <tr class="group transition-colors hover:bg-[#F9FAFB]">
                  <td class="p-4">
                    <p class="text-[16px] font-bold text-[#1F2937]">
                      钱* <span class="ml-1 text-[12px] font-normal text-[#9CA3AF]">男</span>
                    </p>
                    <p class="mt-1 font-mono text-[12px] text-[#6B7280]">460200********5521</p>
                    <p class="mt-0.5 text-[12px] text-[#6B7280]">主任医师</p>
                  </td>
                  <td class="border-l border-[#E0E7FF] bg-[#EEF2FF]/20 p-4">
                    <div class="space-y-1.5 text-[13px]">
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">主机构:</span>
                        <span class="font-bold text-[#1F2937]">三亚市人民医院</span>
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">性质:</span>
                        <span
                          class="rounded border border-[#C7D2FE] bg-[#EEF2FF] px-2 py-0.5 text-[11px] font-bold text-[#265EE6]"
                          >公立三甲</span
                        >
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">多点备案:</span>
                        <span class="text-[#6B7280]">仅备案三亚某康复医院</span>
                      </p>
                    </div>
                  </td>
                  <td class="border-l border-[#FECACA] bg-[#FEF2F2]/20 p-4">
                    <div class="space-y-1.5 text-[13px]">
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">发现机构:</span>
                        <span class="font-bold text-[#991B1B]">三亚某医疗美容门诊部</span>
                        <span class="ml-1 rounded bg-[#F3F4F6] px-1.5 py-0.5 text-[10px] text-[#4B5563]"
                          >民营</span
                        >
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">抓取证据:</span>
                        <span
                          class="border-b border-dashed border-[#9CA3AF] font-medium text-[#374151]"
                          >双眼皮埋线手术操作记录</span
                        >
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">签名身份:</span>
                        <span class="font-bold text-[#EF4444]">主刀医师</span>
                      </p>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4">
                    <div class="flex items-start gap-1.5 text-[#F59E0B]">
                      <FileWarning :size="16" class="mt-0.5 shrink-0" />
                      <div>
                        <p class="text-[14px] font-bold">超备案范围多点执业</p>
                        <p class="mt-1 text-[12px] leading-tight text-[#92400E]">
                          医师虽有多点备案，但实际开展手术机构不在其备案白名单内。
                        </p>
                      </div>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4 text-center">
                    <div class="flex flex-col gap-2">
                      <button
                        type="button"
                        class="flex items-center justify-center gap-1 rounded border border-[#C7D2FE] bg-[#EEF2FF] px-3 py-1.5 text-[12px] font-bold text-[#265EE6] transition-colors hover:bg-[#265EE6] hover:text-white"
                      >
                        <Bell :size="12" />
                        提醒涉事医师
                      </button>
                      <button
                        type="button"
                        class="flex items-center justify-center gap-1 rounded border border-[#FECACA] bg-[#FEF2F2] px-3 py-1.5 text-[12px] font-bold text-[#EF4444] transition-colors hover:bg-[#EF4444] hover:text-white"
                      >
                        <Send :size="12" />
                        通报民营机构
                      </button>
                    </div>
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
  AlertTriangle,
  Activity,
  Bell,
  Building,
  Database,
  FileWarning,
  Filter,
  MapPin,
  Search,
  Send,
  ShieldAlert,
  Users,
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
.multisite-scroll::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.multisite-scroll::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}
</style>
