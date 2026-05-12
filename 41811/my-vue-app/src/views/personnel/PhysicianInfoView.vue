<template>
  <div class="flex h-full min-h-0 flex-col bg-[#F4F6F8] font-sans text-[#333333]">
    <!-- 顶栏：医师信息管理与核验中心 -->
    <header
      class="flex h-[102px] shrink-0 items-center justify-between border-b border-[#E5E7EB] bg-white px-6 shadow-sm sm:px-8"
    >
      <div class="flex min-w-0 flex-1 flex-wrap items-center gap-3 sm:gap-4">
        <h2 class="text-[18px] font-bold tracking-tight text-[#1F2937] sm:text-[22px] lg:text-[24px]">
          医师信息管理与核验中心
        </h2>
        <span
          class="inline-flex shrink-0 items-center gap-1 rounded-full border border-[#C7D2FE] bg-[#EEF2FF] px-2.5 py-1 text-[11px] font-medium tracking-wide text-[#265EE6] sm:text-[12px]"
        >
          <Activity :size="12" />
          数据实时比对中
        </span>
      </div>
      <div class="ml-3 flex shrink-0 flex-wrap items-center justify-end gap-2 sm:gap-4">
        <div class="relative hidden md:block">
          <Search
            class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-[#9CA3AF]"
            :size="18"
          />
          <input
            type="text"
            placeholder="输入医师姓名、身份证号或执业证号..."
            class="w-[min(320px,28vw)] rounded-lg border border-[#D1D5DB] bg-[#F9FAFB] py-2.5 pl-10 pr-4 text-[14px] text-[#374151] outline-none transition-all placeholder:text-[#9CA3AF] focus:border-[#265EE6] focus:bg-white focus:ring-2 focus:ring-[#265EE6]/20"
          />
        </div>
        <button
          type="button"
          class="flex items-center gap-2 whitespace-nowrap rounded-lg bg-[#265EE6] px-4 py-2.5 text-[14px] font-medium text-white shadow-sm shadow-[#265EE6]/30 transition-colors hover:bg-[#1E4BD8] sm:px-5"
        >
          <Filter :size="16" />
          高级检索
        </button>
      </div>
    </header>

    <!-- 动态内容 -->
    <div class="physician-scroll relative flex-1 overflow-y-auto p-6 sm:p-8">
      <div class="mx-auto max-w-[1400px] space-y-6 pb-12 animate-fade-in">
        <!-- 业务导读与政策依据 -->
        <div
          class="flex flex-col gap-6 rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm sm:flex-row sm:items-start"
        >
          <div class="shrink-0 rounded-xl bg-[#EEF2FF] p-4 text-[#265EE6]">
            <Database :size="32" stroke-width="1.5" />
          </div>
          <div class="min-w-0">
            <h3 class="mb-2 text-[18px] font-bold text-[#1F2937]">全省医师双源数据核验引擎</h3>
            <p class="text-[14px] leading-relaxed text-[#6B7280]">
              基于《深化卫生专业技术人员职称制度改革的指导意见》，系统已自动关联提取
              <span class="font-bold text-[#1F2937]">民科系统（法定执业资格与状态）</span> 与
              <span class="font-bold text-[#1F2937]">医院 HIS 系统（实际接诊与职称聘用）</span>
              数据。 自动识别并预警离职僵尸账号、高职低聘/低职高聘、以及超法定执业范围开展诊疗等高危违规行为。
            </p>
          </div>
        </div>

        <!-- KPI -->
        <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
          <div
            class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#265EE6]"
          >
            <div class="absolute left-0 top-0 h-full w-1 bg-[#10B981]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#6B7280]">民科系统在册总人数</p>
              <div class="rounded-lg bg-[#ECFDF5] p-2 text-[#10B981]">
                <UserCheck :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#1F2937]">
              42,158 <span class="ml-1 text-[14px] font-normal text-[#6B7280]">人</span>
            </p>
            <p class="mt-2 flex items-center gap-1 text-[12px] font-medium text-[#10B981]">
              已激活匹配 HIS 数据 97.2%
            </p>
          </div>

          <div
            class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#265EE6]"
          >
            <div class="absolute left-0 top-0 h-full w-1 bg-[#265EE6]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#6B7280]">职称/亚专科盘活数据</p>
              <div class="rounded-lg bg-[#EEF2FF] p-2 text-[#265EE6]">
                <Stethoscope :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#1F2937]">
              15,204 <span class="ml-1 text-[14px] font-normal text-[#6B7280]">条</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#265EE6]">精准细分至骨关节外科等</p>
          </div>

          <div
            class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#EF4444]"
          >
            <div class="absolute left-0 top-0 h-full w-1 bg-[#EF4444]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#6B7280]">发现僵尸数据预警</p>
              <div class="rounded-lg bg-[#FEF2F2] p-2 text-[#EF4444]">
                <UserMinus :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#EF4444]">
              38 <span class="ml-1 text-[14px] font-normal text-[#6B7280]">个</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#EF4444]">涉嫌离职后无资质接诊！</p>
          </div>

          <div
            class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#F59E0B]"
          >
            <div class="absolute left-0 top-0 h-full w-1 bg-[#F59E0B]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#6B7280]">超执业范围预警</p>
              <div class="rounded-lg bg-[#FFFBEB] p-2 text-[#F59E0B]">
                <AlertTriangle :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#F59E0B]">
              12 <span class="ml-1 text-[14px] font-normal text-[#6B7280]">起</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#D97706]">跨专业收治/手术行为</p>
          </div>
        </div>

        <!-- 比对明细表 -->
        <div class="overflow-hidden rounded-xl border border-[#E5E7EB] bg-white shadow-sm">
          <div class="flex flex-col gap-3 border-b border-[#E5E7EB] bg-[#F9FAFB] p-5 sm:flex-row sm:items-center sm:justify-between">
            <h3 class="flex items-center gap-2 text-[16px] font-bold text-[#1F2937]">
              <ArrowRightLeft class="text-[#265EE6]" :size="20" />
              异常核验名册：民科系统法定资质 VS 医院 HIS 实际业务
            </h3>
            <button
              type="button"
              class="rounded border border-[#D1D5DB] bg-white px-3 py-1.5 text-[12px] font-medium text-[#4B5563] transition-colors hover:bg-[#F3F4F6]"
            >
              导出异常名单
            </button>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full min-w-[900px] text-left text-[14px]">
              <thead class="border-b border-[#E5E7EB] bg-white">
                <tr>
                  <th class="w-[15%] p-4 font-semibold text-[#4B5563]">医师基础信息</th>
                  <th
                    class="w-[30%] border-l border-[#E0E7FF] bg-[#EEF2FF]/30 p-4 font-semibold text-[#4B5563]"
                  >
                    民科系统 (法定备案)
                  </th>
                  <th
                    class="w-[30%] border-l border-[#E5E7EB] bg-[#F3F4F6]/50 p-4 font-semibold text-[#4B5563]"
                  >
                    HIS 系统 (实际院内数据)
                  </th>
                  <th class="w-[15%] border-l border-[#E5E7EB] p-4 font-semibold text-[#4B5563]">
                    引擎核验结论
                  </th>
                  <th class="w-[10%] p-4 text-center font-semibold text-[#4B5563]">操作</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#F3F4F6]">
                <!-- Case 1 -->
                <tr class="group transition-colors hover:bg-[#F9FAFB]">
                  <td class="p-4">
                    <p class="text-[16px] font-bold text-[#1F2937]">
                      张*伟 <span class="ml-1 text-[12px] font-normal text-[#9CA3AF]">男</span>
                    </p>
                    <p class="mt-1 font-mono text-[12px] text-[#6B7280]">460102********1234</p>
                    <p class="mt-0.5 text-[12px] text-[#6B7280]">海口市某综合医院</p>
                  </td>
                  <td class="border-l border-[#E0E7FF] bg-[#EEF2FF]/20 p-4">
                    <div class="space-y-1.5 text-[13px]">
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">状态:</span>
                        <span
                          class="rounded border border-[#FECACA] bg-[#FEF2F2] px-2 py-0.5 text-[12px] font-bold text-[#EF4444]"
                          >已离职 / 注销</span
                        >
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">职级:</span>
                        <span class="font-medium text-[#374151]">中级 (主治医师)</span>
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">范围:</span>
                        <span class="text-[#374151]">外科专业</span>
                      </p>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] bg-[#F3F4F6]/30 p-4">
                    <div class="space-y-1.5 text-[13px]">
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">HIS状态:</span>
                        <span class="font-bold text-[#10B981]">账号活跃在用</span>
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">聘用职称:</span>
                        <span class="font-medium text-[#374151]">主治医师</span>
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">近期痕迹:</span>
                        <span class="text-[#374151]">今日开具骨科门诊处方3份</span>
                      </p>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4">
                    <div class="flex items-start gap-1.5 text-[#EF4444]">
                      <ShieldAlert :size="16" class="mt-0.5 shrink-0" />
                      <div>
                        <p class="text-[14px] font-bold">僵尸账号预警</p>
                        <p class="mt-1 text-[12px] leading-tight">法定已离职，但HIS仍有业务，涉嫌他人冒用。</p>
                      </div>
                    </div>
                  </td>
                  <td class="p-4 text-center">
                    <button type="button" class="text-[13px] font-medium text-[#265EE6] hover:underline">
                      一键封停
                    </button>
                  </td>
                </tr>

                <!-- Case 2 -->
                <tr class="group transition-colors hover:bg-[#F9FAFB]">
                  <td class="p-4">
                    <p class="text-[16px] font-bold text-[#1F2937]">
                      李* <span class="ml-1 text-[12px] font-normal text-[#9CA3AF]">女</span>
                    </p>
                    <p class="mt-1 font-mono text-[12px] text-[#6B7280]">460200********5521</p>
                    <p class="mt-0.5 text-[12px] text-[#6B7280]">三亚市某人民医院</p>
                  </td>
                  <td class="border-l border-[#E0E7FF] bg-[#EEF2FF]/20 p-4">
                    <div class="space-y-1.5 text-[13px]">
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">状态:</span>
                        <span class="font-medium text-[#10B981]">在职注册</span>
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">职级:</span>
                        <span
                          class="rounded border border-[#FDE68A] bg-[#FFFBEB] px-2 py-0.5 text-[12px] font-bold text-[#D97706]"
                          >初级 (医士/医师)</span
                        >
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">范围:</span>
                        <span class="text-[#374151]">内科专业</span>
                      </p>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] bg-[#F3F4F6]/30 p-4">
                    <div class="space-y-1.5 text-[13px]">
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">HIS状态:</span>
                        <span class="font-medium text-[#10B981]">正常</span>
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">聘用职称:</span>
                        <span class="font-bold text-[#374151]">副主任医师 (HIS配置)</span>
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">近期痕迹:</span>
                        <span class="text-[#374151]"
                          >开具<span class="font-medium text-[#265EE6]">替加环素</span>(特殊级抗菌药)</span
                        >
                      </p>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4">
                    <div class="flex items-start gap-1.5 text-[#F59E0B]">
                      <FileWarning :size="16" class="mt-0.5 shrink-0" />
                      <div>
                        <p class="text-[14px] font-bold">职称不符/违规用药</p>
                        <p class="mt-1 text-[12px] leading-tight text-[#92400E]">
                          法定仅为初级，HIS高配副高，越权开具抗菌药。
                        </p>
                      </div>
                    </div>
                  </td>
                  <td class="p-4 text-center">
                    <button type="button" class="text-[13px] font-medium text-[#265EE6] hover:underline">
                      限期整改
                    </button>
                  </td>
                </tr>

                <!-- Case 3 -->
                <tr class="group transition-colors hover:bg-[#F9FAFB]">
                  <td class="p-4">
                    <p class="text-[16px] font-bold text-[#1F2937]">
                      赵* <span class="ml-1 text-[12px] font-normal text-[#9CA3AF]">男</span>
                    </p>
                    <p class="mt-1 font-mono text-[12px] text-[#6B7280]">11046000000****</p>
                    <p class="mt-0.5 text-[12px] text-[#6B7280]">海口某民营口腔诊所</p>
                  </td>
                  <td class="border-l border-[#E0E7FF] bg-[#EEF2FF]/20 p-4">
                    <div class="space-y-1.5 text-[13px]">
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">状态:</span>
                        <span class="font-medium text-[#10B981]">在职注册</span>
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">职级:</span>
                        <span class="font-medium text-[#374151]">中级 (主治医师)</span>
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">范围:</span>
                        <span
                          class="rounded border border-[#C7D2FE] bg-[#EEF2FF] px-2 py-0.5 text-[12px] font-bold text-[#265EE6]"
                          >口腔专业</span
                        >
                      </p>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] bg-[#F3F4F6]/30 p-4">
                    <div class="space-y-1.5 text-[13px]">
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">所在科室:</span>
                        <span class="font-bold text-[#374151]">全科门诊</span>
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">聘用职称:</span>
                        <span class="font-medium text-[#374151]">主治医师</span>
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">近期痕迹:</span>
                        <span class="text-[#374151]"
                          >收治主诊断: <span class="font-bold text-[#EF4444]">急性阑尾炎</span></span
                        >
                      </p>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4">
                    <div class="flex items-start gap-1.5 text-[#F59E0B]">
                      <AlertTriangle :size="16" class="mt-0.5 shrink-0" />
                      <div>
                        <p class="text-[14px] font-bold">超执业范围预警</p>
                        <p class="mt-1 text-[12px] leading-tight text-[#92400E]">
                          法定为口腔，实际开展外科诊疗(阑尾炎)。
                        </p>
                      </div>
                    </div>
                  </td>
                  <td class="p-4 text-center">
                    <button type="button" class="text-[13px] font-medium text-[#265EE6] hover:underline">
                      下发警告
                    </button>
                  </td>
                </tr>

                <!-- Case 4 -->
                <tr class="group transition-colors hover:bg-[#F9FAFB]">
                  <td class="p-4">
                    <p class="text-[16px] font-bold text-[#1F2937]">
                      周*明 <span class="ml-1 text-[12px] font-normal text-[#9CA3AF]">男</span>
                    </p>
                    <p class="mt-1 font-mono text-[12px] text-[#6B7280]">460300********8899</p>
                    <p class="mt-0.5 text-[12px] text-[#6B7280]">省人民医院</p>
                  </td>
                  <td class="border-l border-[#E0E7FF] bg-[#EEF2FF]/20 p-4">
                    <div class="space-y-1.5 text-[13px]">
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">状态:</span>
                        <span class="font-medium text-[#10B981]">在职注册</span>
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">职级:</span>
                        <span class="font-medium text-[#374151]">正高级 (主任医师)</span>
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">范围:</span>
                        <span class="font-medium text-[#374151]">外科专业</span>
                      </p>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] bg-[#F3F4F6]/30 p-4">
                    <div class="space-y-1.5 text-[13px]">
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">所在科室:</span>
                        <span
                          class="rounded border border-[#A7F3D0] bg-[#ECFDF5] px-2 py-0.5 text-[12px] font-bold text-[#059669]"
                          >骨关节外科 (亚专科)</span
                        >
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">聘用职称:</span>
                        <span class="font-medium text-[#374151]">主任医师</span>
                      </p>
                      <p>
                        <span class="inline-block w-16 text-[#9CA3AF]">近期痕迹:</span>
                        <span class="text-[#374151]">近期手术排班正常</span>
                      </p>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4">
                    <div class="flex items-start gap-1.5 text-[#10B981]">
                      <CheckCircle :size="16" class="mt-0.5 shrink-0" />
                      <div>
                        <p class="text-[14px] font-bold">数据已激活映射</p>
                        <p class="mt-1 text-[12px] leading-tight text-[#065F46]">
                          资质完全匹配，已成功盘活至亚专科层级。
                        </p>
                      </div>
                    </div>
                  </td>
                  <td class="p-4 text-center">
                    <button
                      type="button"
                      class="text-[13px] font-medium text-[#6B7280] hover:text-[#1F2937]"
                    >
                      查看档案
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
  Activity,
  Search,
  Filter,
  Database,
  UserCheck,
  Stethoscope,
  UserMinus,
  AlertTriangle,
  ArrowRightLeft,
  FileWarning,
  CheckCircle,
  ShieldAlert,
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

.physician-scroll::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.physician-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.physician-scroll::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}
.physician-scroll::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>
