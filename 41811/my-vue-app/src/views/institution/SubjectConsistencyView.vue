<template>
  <div class="flex h-full min-h-0 flex-col bg-[#F4F6F8] font-sans text-[#333333]">
    <header
      class="flex min-h-[102px] shrink-0 flex-col justify-center gap-4 border-b border-[#E5E7EB] bg-white px-4 py-4 shadow-sm sm:flex-row sm:items-center sm:justify-between sm:px-8"
    >
      <div class="flex min-w-0 flex-wrap items-center gap-3 sm:gap-4">
        <h2 class="text-[20px] font-bold tracking-tight text-[#1F2937] sm:text-[22px] lg:text-[24px]">
          诊疗科目一致性监管
        </h2>
        <span
          class="inline-flex items-center gap-1 rounded-full border border-[#C7D2FE] bg-[#EEF2FF] px-2.5 py-1 text-[11px] font-bold tracking-wide text-[#265EE6] sm:text-[12px]"
        >
          <Database :size="14" class="animate-pulse" />
          住院首页/门诊病历实时解析中
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
            placeholder="输入医疗机构名称、诊断或手术名称..."
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
            class="flex flex-col justify-center border-b border-[#E5E7EB] bg-gradient-to-br from-[#F8FAFC] to-[#F1F5F9] p-8 lg:w-[40%] lg:border-b-0 lg:border-r"
          >
            <div
              class="mb-4 w-fit rounded-xl border border-[#C7D2FE] bg-[#EEF2FF] p-3 text-[#265EE6] shadow-sm"
            >
              <Network :size="28" stroke-width="2" />
            </div>
            <h3 class="mb-3 text-[20px] font-bold text-[#1F2937]">超科目执业多对多映射引擎</h3>
            <p class="mb-4 text-[14px] leading-relaxed text-[#4B5563]">
              基于《医疗机构管理条例实施细则》，建立医疗机构<span class="font-bold text-[#1F2937]"
                >执业许可证核准科目</span
              >
              与<span class="font-bold text-[#1F2937]">实际产生业务</span>的动态匹配网。有效排查和打击“挂羊头卖狗肉”等超执业范围违规行为。
            </p>
            <div class="mt-auto rounded-lg border border-[#E5E7EB] bg-white p-4 shadow-sm">
              <p class="mb-2 flex items-center gap-1.5 text-[13px] font-bold text-[#1F2937]">
                <FileText :size="14" class="text-[#265EE6]" />
                引擎匹配规则库来源：
              </p>
              <ul class="list-disc space-y-1.5 pl-4 text-[12px] text-[#6B7280]">
                <li>《医疗机构诊疗科目名录》</li>
                <li>《疾病分类与代码国家临床版2.0》</li>
                <li>《手术操作分类代码国家临床版3.0》</li>
                <li>海南省医疗保障局《医疗服务价格目录》</li>
              </ul>
            </div>
          </div>

          <div class="relative flex flex-col items-center justify-center bg-white p-8 lg:w-[60%]">
            <h4 class="mb-8 text-[14px] font-bold uppercase tracking-widest text-[#6B7280]">
              底层逻辑架构演示
            </h4>

            <div class="relative z-10 flex w-full max-w-[650px] items-stretch justify-between gap-2">
              <div class="flex w-[min(180px,30%)] flex-col items-center gap-2">
                <div
                  class="w-full rounded-lg border border-[#A5B4FC] bg-[#EEF2FF] p-4 text-center shadow-sm"
                >
                  <Building class="mx-auto mb-2 text-[#265EE6]" :size="24" />
                  <p class="text-[14px] font-bold text-[#1F2937]">核准诊疗科目</p>
                  <p class="mt-1 text-[11px] text-[#6B7280]">(取自电子证照系统)</p>
                </div>
                <div
                  class="mt-2 w-full rounded-md border border-[#E5E7EB] bg-white px-3 py-1.5 text-center text-[13px] font-medium text-[#4B5563] shadow-sm"
                >
                  例如：妇产科
                </div>
              </div>

              <div class="relative flex min-w-0 flex-1 flex-col items-center justify-center px-2 sm:px-4">
                <div class="absolute left-0 right-0 top-1/2 -z-10 hidden -translate-y-1/2 sm:flex">
                  <div class="h-[2px] w-1/2 bg-gradient-to-r from-[#A5B4FC] to-[#D1D5DB]" />
                  <div class="h-[2px] w-1/2 bg-gradient-to-r from-[#D1D5DB] to-[#FCA5A5]" />
                </div>
                <div
                  class="z-10 rounded-full border-[2px] border-[#F59E0B] bg-[#FFFBEB] p-2.5 shadow-[0_0_15px_rgba(245,158,11,0.3)]"
                >
                  <ArrowRightLeft class="text-[#D97706]" :size="20" />
                </div>
                <p class="mt-2 text-center text-[12px] font-bold text-[#D97706]">多对多匹配校验</p>
              </div>

              <div class="flex w-[min(220px,36%)] flex-col gap-3">
                <div
                  class="w-full rounded-lg border border-[#FCA5A5] bg-[#FEF2F2] p-4 text-center shadow-sm"
                >
                  <Activity class="mx-auto mb-2 text-[#EF4444]" :size="24" />
                  <p class="text-[14px] font-bold text-[#1F2937]">实际发生诊疗行为</p>
                  <p class="mt-1 text-[11px] text-[#6B7280]">(取自 HIS 病案首页/门诊病历)</p>
                </div>
                <div
                  class="flex w-full items-center gap-2 truncate rounded-md border border-[#FECACA] bg-white px-3 py-1.5 text-left text-[13px] font-medium text-[#EF4444] shadow-sm"
                >
                  <span class="h-2 w-2 shrink-0 rounded-full bg-[#EF4444]" />
                  诊断：前列腺增生
                </div>
                <div
                  class="flex w-full items-center gap-2 truncate rounded-md border border-[#FECACA] bg-white px-3 py-1.5 text-left text-[13px] font-medium text-[#EF4444] shadow-sm"
                >
                  <span class="h-2 w-2 shrink-0 rounded-full bg-[#EF4444]" />
                  手术：前列腺切除术
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
              <p class="text-[14px] font-medium text-[#6B7280]">全省受核查医疗机构</p>
              <div class="rounded-lg bg-[#EEF2FF] p-2 text-[#265EE6]">
                <Building :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#1F2937]">
              3,412 <span class="ml-1 text-[14px] font-normal text-[#6B7280]">家</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#6B7280]">涵盖全省各级公立/民营</p>
          </div>

          <div
            class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#F59E0B]"
          >
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#F59E0B]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#6B7280]">今日解析出院首页与病历</p>
              <div class="rounded-lg bg-[#FFFBEB] p-2 text-[#F59E0B]">
                <FileText :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#1F2937]">
              84.5 <span class="ml-1 text-[14px] font-normal text-[#6B7280]">万份</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#D97706]">完成自动化规则映射比对</p>
          </div>

          <div
            class="group relative overflow-hidden rounded-xl border border-[#E5E7EB] bg-white p-6 shadow-sm transition-colors hover:border-[#EF4444]"
          >
            <div class="absolute left-0 top-0 h-full w-1.5 bg-[#EF4444]" />
            <div class="mb-4 flex items-start justify-between">
              <p class="text-[14px] font-medium text-[#6B7280]">捕获超科目执业机构</p>
              <div class="rounded-lg bg-[#FEF2F2] p-2 text-[#EF4444]">
                <ShieldAlert :size="20" />
              </div>
            </div>
            <p class="text-[32px] font-black text-[#EF4444]">
              14 <span class="ml-1 text-[14px] font-normal text-[#6B7280]">家</span>
            </p>
            <p class="mt-2 text-[12px] font-medium text-[#EF4444]">存在严重跨范围诊疗行为</p>
          </div>

          <div
            class="flex flex-col justify-center overflow-hidden rounded-xl border border-[#002140] bg-[#001529] p-6 text-white shadow-sm"
          >
            <p class="mb-3 text-[14px] font-medium text-[#9CA3AF]">违规高发科室 TOP 3</p>
            <div class="space-y-3">
              <div class="flex items-center justify-between text-[13px]">
                <span class="text-white">医疗美容科</span>
                <div class="flex items-center gap-2">
                  <div class="h-1.5 w-20 overflow-hidden rounded-full bg-[#002140]">
                    <div class="h-full w-[80%] bg-[#EF4444]" />
                  </div>
                  <span class="w-8 text-right font-bold text-[#EF4444]">38%</span>
                </div>
              </div>
              <div class="flex items-center justify-between text-[13px]">
                <span class="text-white">全科医疗科</span>
                <div class="flex items-center gap-2">
                  <div class="h-1.5 w-20 overflow-hidden rounded-full bg-[#002140]">
                    <div class="h-full w-[55%] bg-[#F59E0B]" />
                  </div>
                  <span class="w-8 text-right font-bold text-[#F59E0B]">24%</span>
                </div>
              </div>
              <div class="flex items-center justify-between text-[13px]">
                <span class="text-white">妇产科</span>
                <div class="flex items-center gap-2">
                  <div class="h-1.5 w-20 overflow-hidden rounded-full bg-[#002140]">
                    <div class="h-full w-[30%] bg-[#265EE6]" />
                  </div>
                  <span class="w-8 text-right font-bold text-[#265EE6]">15%</span>
                </div>
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
              超科目执业违规线索台账 (基于病案解析)
            </h3>
            <button
              type="button"
              class="rounded border border-[#D1D5DB] bg-white px-3 py-1.5 text-[13px] font-medium text-[#4B5563] transition-colors hover:bg-[#F3F4F6]"
            >
              导出工单
            </button>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full min-w-[960px] text-left text-[14px]">
              <thead class="border-b border-[#E5E7EB] bg-white">
                <tr>
                  <th class="w-[18%] p-4 font-semibold text-[#4B5563]">医疗机构基本信息</th>
                  <th
                    class="w-[15%] border-l border-[#E0E7FF] bg-[#EEF2FF]/30 p-4 font-semibold text-[#4B5563]"
                  >
                    机构已核准科目
                  </th>
                  <th
                    class="w-[32%] border-l border-[#FECACA] bg-[#FEF2F2]/30 p-4 font-semibold text-[#4B5563]"
                  >
                    实际诊疗行为 (HIS 抓取)
                  </th>
                  <th class="w-[20%] border-l border-[#E5E7EB] p-4 font-semibold text-[#4B5563]">
                    智能研判结论
                  </th>
                  <th class="w-[15%] border-l border-[#E5E7EB] p-4 text-center font-semibold text-[#4B5563]">
                    处理操作
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#F3F4F6]">
                <tr class="group transition-colors hover:bg-[#F9FAFB]">
                  <td class="p-4">
                    <p class="text-[15px] font-bold text-[#1F2937]">某市第三妇产专科医院</p>
                    <p class="mt-1.5 text-[12px] text-[#6B7280]">机构编码：460100085</p>
                    <p class="mt-0.5 text-[12px] text-[#6B7280]">机构级别：二级</p>
                  </td>
                  <td class="border-l border-[#E0E7FF] bg-[#EEF2FF]/20 p-4">
                    <div class="flex flex-wrap gap-1.5">
                      <span
                        class="rounded border border-[#C7D2FE] bg-[#EEF2FF] px-2 py-0.5 text-[12px] font-bold text-[#265EE6]"
                        >妇产科专业</span
                      >
                      <span
                        class="rounded border border-[#C7D2FE] bg-[#EEF2FF] px-2 py-0.5 text-[12px] font-bold text-[#265EE6]"
                        >新生儿科</span
                      >
                    </div>
                  </td>
                  <td class="border-l border-[#FECACA] bg-[#FEF2F2]/20 p-4">
                    <div class="space-y-2 text-[13px]">
                      <p>
                        <span class="inline-block w-[70px] text-[#9CA3AF]">出院科室:</span>
                        <span class="font-bold text-[#1F2937]">妇产科病区</span>
                      </p>
                      <p class="flex items-start">
                        <span class="mt-0.5 inline-block w-[70px] shrink-0 text-[#9CA3AF]">住院诊断:</span>
                        <span class="font-medium text-[#991B1B]">良性前列腺增生 (N40)</span>
                      </p>
                      <p class="flex items-start">
                        <span class="mt-0.5 inline-block w-[70px] shrink-0 text-[#9CA3AF]">手术操作:</span>
                        <span
                          class="border-b border-dashed border-[#EF4444] font-bold text-[#EF4444]"
                          >经尿道前列腺切除术 (60.2900x)</span
                        >
                      </p>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4">
                    <div class="flex items-start gap-1.5 text-[#EF4444]">
                      <ShieldAlert :size="16" class="mt-0.5 shrink-0" />
                      <div>
                        <p class="text-[14px] font-bold">严重超科目执业</p>
                        <p class="mt-1 text-[12px] leading-tight text-[#991B1B]">
                          【前列腺切除】属泌尿外科。该机构未核准外科专业，且将其挂靠在产科，涉嫌严重违规或医保骗保造假。
                        </p>
                      </div>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4 text-center">
                    <button
                      type="button"
                      class="flex w-full items-center justify-center gap-1 rounded border border-[#FECACA] bg-[#FEF2F2] px-3 py-1.5 text-[12px] font-bold text-[#EF4444] transition-colors hover:bg-[#EF4444] hover:text-white"
                    >
                      <AlertTriangle :size="12" />
                      立案并停业整顿
                    </button>
                  </td>
                </tr>

                <tr class="group transition-colors hover:bg-[#F9FAFB]">
                  <td class="p-4">
                    <p class="text-[15px] font-bold text-[#1F2937]">海口某医疗美容诊所</p>
                    <p class="mt-1.5 text-[12px] text-[#6B7280]">机构编码：460105332</p>
                    <p class="mt-0.5 text-[12px] text-[#6B7280]">机构级别：未定级</p>
                  </td>
                  <td class="border-l border-[#E0E7FF] bg-[#EEF2FF]/20 p-4">
                    <div class="flex flex-wrap gap-1.5">
                      <span
                        class="rounded border border-[#C7D2FE] bg-[#EEF2FF] px-2 py-0.5 text-[12px] font-bold text-[#265EE6]"
                        >美容皮肤科</span
                      >
                      <span
                        class="rounded border border-[#C7D2FE] bg-[#EEF2FF] px-2 py-0.5 text-[12px] font-bold text-[#265EE6]"
                        >美容牙科</span
                      >
                    </div>
                  </td>
                  <td class="border-l border-[#FECACA] bg-[#FEF2F2]/20 p-4">
                    <div class="space-y-2 text-[13px]">
                      <p>
                        <span class="inline-block w-[70px] text-[#9CA3AF]">产生科室:</span>
                        <span class="font-bold text-[#1F2937]">激光室</span>
                      </p>
                      <p class="flex items-start">
                        <span class="mt-0.5 inline-block w-[70px] shrink-0 text-[#9CA3AF]">手术操作:</span>
                        <span
                          class="border-b border-dashed border-[#EF4444] font-bold text-[#EF4444]"
                          >硅胶假体植入隆胸术 (85.54)</span
                        >
                      </p>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4">
                    <div class="flex items-start gap-1.5 text-[#F59E0B]">
                      <FileWarning :size="16" class="mt-0.5 shrink-0" />
                      <div>
                        <p class="text-[14px] font-bold">超科目(美容外科)执业</p>
                        <p class="mt-1 text-[12px] leading-tight text-[#92400E]">
                          该机构仅核准“美容皮肤科”，隆胸手术属于“美容外科”范畴，无资质开展。
                        </p>
                      </div>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4 text-center">
                    <button
                      type="button"
                      class="flex w-full items-center justify-center gap-1 rounded border border-[#C7D2FE] bg-[#EEF2FF] px-3 py-1.5 text-[12px] font-bold text-[#265EE6] transition-colors hover:bg-[#265EE6] hover:text-white"
                    >
                      <Send :size="12" />
                      下发警告与罚款
                    </button>
                  </td>
                </tr>

                <tr class="group transition-colors hover:bg-[#F9FAFB]">
                  <td class="p-4">
                    <p class="text-[15px] font-bold text-[#1F2937]">某镇中心卫生院</p>
                    <p class="mt-1.5 text-[12px] text-[#6B7280]">机构编码：460300122</p>
                    <p class="mt-0.5 text-[12px] text-[#6B7280]">机构级别：一级</p>
                  </td>
                  <td class="border-l border-[#E0E7FF] bg-[#EEF2FF]/20 p-4">
                    <div class="flex flex-wrap gap-1.5">
                      <span
                        class="rounded border border-[#C7D2FE] bg-[#EEF2FF] px-2 py-0.5 text-[12px] font-bold text-[#265EE6]"
                        >内科专业</span
                      >
                      <span
                        class="rounded border border-[#C7D2FE] bg-[#EEF2FF] px-2 py-0.5 text-[12px] font-bold text-[#265EE6]"
                        >预防保健科</span
                      >
                    </div>
                  </td>
                  <td class="border-l border-[#FECACA] bg-[#FEF2F2]/20 p-4">
                    <div class="space-y-2 text-[13px]">
                      <p>
                        <span class="inline-block w-[70px] text-[#9CA3AF]">开单科室:</span>
                        <span class="font-bold text-[#1F2937]">综合内科门诊</span>
                      </p>
                      <p class="flex items-start">
                        <span class="mt-0.5 inline-block w-[70px] shrink-0 text-[#9CA3AF]">门诊收费:</span>
                        <span
                          class="border-b border-dashed border-[#EF4444] font-bold text-[#EF4444]"
                          >血液透析 (39.95)</span
                        >
                      </p>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4">
                    <div class="flex items-start gap-1.5 text-[#F59E0B]">
                      <FileWarning :size="16" class="mt-0.5 shrink-0" />
                      <div>
                        <p class="text-[14px] font-bold">超科目开展限制性项目</p>
                        <p class="mt-1 text-[12px] leading-tight text-[#92400E]">
                          血透要求具备“肾病学专业”及专门审批。该院仅有普通内科科目，涉嫌违规开展。
                        </p>
                      </div>
                    </div>
                  </td>
                  <td class="border-l border-[#E5E7EB] p-4 text-center">
                    <button
                      type="button"
                      class="flex w-full items-center justify-center gap-1 rounded border border-[#C7D2FE] bg-[#EEF2FF] px-3 py-1.5 text-[12px] font-bold text-[#265EE6] transition-colors hover:bg-[#265EE6] hover:text-white"
                    >
                      <Send :size="12" />
                      发送卫健委核查
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
  AlertTriangle,
  ArrowRightLeft,
  Building,
  Database,
  FileText,
  FileWarning,
  Filter,
  Network,
  Search,
  Send,
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
.institution-scroll::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.institution-scroll::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}
</style>
