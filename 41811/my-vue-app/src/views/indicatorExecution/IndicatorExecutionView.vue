<template>
  <div class="flex h-full min-h-0 flex-col bg-white">
    <!-- 顶部区域：执行表单 + 历史记录按钮 -->
    <div class="shrink-0 border-b border-emerald-100 p-5">
      <div class="flex items-start gap-6">
        <!-- 左侧：执行表单 -->
        <div class="flex-1">
          <h3 class="mb-4 flex items-center text-[13px] font-semibold text-[#1F264D]">
            <Zap class="mr-2 h-4 w-4 text-emerald-500" />
            指标执行
          </h3>
          <div class="flex flex-wrap items-end gap-3">
            <!-- 指标类别 -->
            <label class="flex flex-col gap-1 text-[12px]">
              <span class="text-[#596080]">指标类别</span>
              <select
                v-model="runKind"
                class="cursor-pointer rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
              >
                <option value="four">四要素监管指标</option>
                <option value="core18">十八项核心制度指标</option>
              </select>
            </label>

            <!-- 执行范围 -->
            <label class="flex flex-col gap-1 text-[12px]">
              <span class="text-[#596080]">执行范围</span>
              <MultiSelectDropdown
                v-model="runScopes"
                :options="hospitalOptions"
                placeholder="全省"
              />
            </label>

            <!-- 指标名称 -->
            <label class="flex flex-col gap-1 text-[12px]">
              <span class="text-[#596080]">指标名称</span>
              <select
                v-model="runIndicatorId"
                class="cursor-pointer rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
              >
                <option value="">全部</option>
                <option
                  v-for="ind in currentIndicatorOptions"
                  :key="ind.id"
                  :value="ind.id"
                >{{ ind.label }}</option>
              </select>
            </label>

            <!-- 执行方式 + 时间选择（按月/按季度时包裹在一个框内） -->
            <div
              v-if="runMode === 'monthly' || runMode === 'quarterly'"
              class="rounded border border-[#b8c9e8]/40 bg-[#f8faff] p-3"
            >
              <div class="flex items-end gap-3">
                <!-- 执行方式 -->
                <label class="flex flex-col gap-1 text-[12px]">
                  <span class="text-[#596080]">执行方式</span>
                  <div class="flex gap-1">
                    <button
                      v-for="mode in RUN_MODE_OPTIONS"
                      :key="mode.value"
                      type="button"
                      class="rounded-[2px] border px-3 py-2 text-[12px] transition-colors"
                      :class="runMode === mode.value
                        ? 'border-emerald-400 bg-emerald-50 text-emerald-700 font-medium'
                        : 'border-[#b8c9e8] bg-white text-[#596080] hover:border-emerald-200'"
                      @click="runMode = mode.value"
                    >{{ mode.label }}</button>
                  </div>
                </label>

                <!-- 月份选择 -->
                <label v-if="runMode === 'monthly'" class="flex flex-col gap-1 text-[12px]">
                  <span class="text-[#596080]">选择月份</span>
                  <div class="flex gap-1">
                    <select
                      v-model="selectedMonthYear"
                      class="cursor-pointer rounded-[2px] border border-[#b8c9e8]/60 bg-white px-2 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
                    >
                      <option v-for="y in monthYearOptions" :key="y" :value="y">{{ y }}年</option>
                    </select>
                    <select
                      v-model="selectedMonthNum"
                      class="cursor-pointer rounded-[2px] border border-[#b8c9e8]/60 bg-white px-2 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
                    >
                      <option v-for="m in MONTH_OPTIONS" :key="m.value" :value="m.value">{{ m.label }}</option>
                    </select>
                  </div>
                </label>

                <!-- 季度选择 -->
                <template v-else-if="runMode === 'quarterly'">
                  <label class="flex flex-col gap-1 text-[12px]">
                    <span class="text-[#596080]">选择年份</span>
                    <select
                      v-model="selectedQuarterYear"
                      class="cursor-pointer rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
                    >
                      <option v-for="y in quarterYearOptions" :key="y" :value="y">{{ y }}年</option>
                    </select>
                  </label>
                  <label class="flex flex-col gap-1 text-[12px]">
                    <span class="text-[#596080]">选择季度</span>
                    <select
                      v-model="selectedQuarterNum"
                      class="cursor-pointer rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
                    >
                      <option v-for="q in quarterOptionsOfYear" :key="q.value" :value="q.value">{{ q.label }}</option>
                    </select>
                  </label>
                </template>
              </div>
            </div>

            <!-- 执行方式（仅即时/全量模式，独立展示） -->
            <template v-else>
              <label class="flex flex-col gap-1 text-[12px]">
                <span class="text-[#596080]">执行方式</span>
                <div class="flex gap-1">
                  <button
                    v-for="mode in RUN_MODE_OPTIONS"
                    :key="mode.value"
                    type="button"
                    class="rounded-[2px] border px-3 py-2 text-[12px] transition-colors"
                    :class="runMode === mode.value
                      ? 'border-emerald-400 bg-emerald-50 text-emerald-700 font-medium'
                      : 'border-[#b8c9e8] bg-white text-[#596080] hover:border-emerald-200'"
                    @click="runMode = mode.value"
                  >{{ mode.label }}</button>
                </div>
              </label>
            </template>

            <!-- 执行按钮 -->
            <button
              type="button"
              class="flex items-center gap-1.5 rounded-[2px] bg-emerald-600 px-5 py-2 text-[12px] text-white transition-colors hover:bg-emerald-700"
              @click="handleRun"
            >
              <PlayCircle class="h-4 w-4" />
              {{ runMode === 'immediate' ? '全量执行' : '发起执行' }}
            </button>
          </div>
        </div>

        <!-- 右侧：历史执行记录按钮 -->
        <div class="relative shrink-0">
          <button
            type="button"
            class="flex items-center gap-2 rounded-[2px] border border-emerald-200 bg-emerald-50 px-4 py-2 text-[12px] text-emerald-700 transition-colors hover:bg-emerald-100"
            @click="historyOpen = !historyOpen"
          >
            <Clock class="h-4 w-4" />
            历史执行记录
            <span class="rounded-full bg-emerald-600 px-1.5 py-0.5 text-[11px] font-medium text-white">{{ records.length }}</span>
            <ChevronDown class="h-3.5 w-3.5 transition-transform" :class="historyOpen ? 'rotate-180' : ''" />
          </button>

          <!-- 历史记录下拉面板 -->
          <Transition name="dropdown">
            <div
              v-if="historyOpen"
              class="absolute right-0 top-full z-50 mt-2 max-h-[440px] w-[920px] overflow-hidden rounded-[2px] border border-[#b8c9e8]/60 bg-white shadow-xl"
            >
              <!-- 状态筛选 -->
              <div class="flex items-center justify-between border-b border-[#b8c9e8]/30 bg-emerald-50/80 px-4 py-2.5">
                <div class="flex items-center gap-3">
                  <span class="text-[12px] font-medium text-[#1F264D]">执行记录</span>
                  <!-- 搜索输入框 -->
                  <div class="relative">
                    <input
                      v-model="searchKeyword"
                      type="text"
                      placeholder="搜索指标名称..."
                      class="w-48 rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-1.5 pr-8 text-[12px] text-[#1F264D] placeholder-[#B8BCCC] focus:border-emerald-400 focus:outline-none"
                      @keyup.enter="handleSearch"
                    />
                    <button
                      type="button"
                      class="absolute right-2 top-1/2 -translate-y-1/2 cursor-pointer text-[#B8BCCC] hover:text-[#596080]"
                      @click="handleSearch"
                    >
                      <Search class="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>
                <div class="flex gap-1">
                  <button
                    v-for="f in STATUS_FILTERS"
                    :key="f.value"
                    type="button"
                    class="rounded-[2px] border px-2 py-1 text-[11px] transition-colors"
                    :class="statusFilter === f.value
                      ? 'border-emerald-400 bg-emerald-50 text-emerald-700'
                      : 'border-[#b8c9e8] bg-white text-[#596080] hover:border-emerald-200'"
                    @click="statusFilter = f.value"
                  >{{ f.label }}</button>
                </div>
              </div>

              <!-- 记录列表 -->
              <div class="overflow-auto" style="max-height: 360px;">
                <table class="w-full min-w-[880px] border-collapse text-left">
                  <thead class="sticky top-0 z-10 border-b border-[#b8c9e8]/30 bg-[#f8faff]">
                    <tr>
                      <th class="px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">指标名称</th>
                      <th class="w-20 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">执行范围</th>
                      <th class="w-24 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">类别</th>
                      <th class="w-20 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">频率</th>
                      <th class="w-20 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">时间范围</th>
                      <th class="w-20 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">状态</th>
                      <th class="w-16 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">耗时</th>
                      <th class="w-32 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">产出结果</th>
                      <th class="w-40 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">开始时间</th>
                      <th class="w-16 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">操作</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-[#b8c9e8]/20">
                    <tr
                      v-for="row in filteredRecords"
                      :key="row.id"
                      class="cursor-pointer transition-colors hover:bg-emerald-50/30"
                      :class="selectedRecord?.id === row.id ? 'bg-emerald-50/60' : ''"
                      @click="selectRecord(row)"
                    >
                      <td class="max-w-[200px] px-3 py-2.5 text-[12px] font-medium text-[#1F264D]">
                        <span class="line-clamp-1" :title="row.indicatorName">{{ row.indicatorName }}</span>
                      </td>
                      <td class="px-3 py-2.5 text-[12px] text-[#596080]">{{ row.scope || '全省' }}</td>
                      <td class="px-3 py-2.5 text-[12px]">
                        <span
                          class="inline-block rounded border px-1.5 py-0.5 text-[11px] font-medium"
                          :class="row.kind === 'four' ? 'border-blue-200 bg-blue-50 text-blue-600' : 'border-purple-200 bg-purple-50 text-purple-600'"
                        >
                          {{ row.kind === 'four' ? '四要素' : '十八项' }}
                        </span>
                      </td>
                      <td class="px-3 py-2.5 text-[12px] text-[#596080]">{{ RUN_MODE_MAP[row.runMode] }}</td>
                      <td class="px-3 py-2.5 text-[12px] text-[#596080]">{{ row.timeRange }}</td>
                      <td class="px-3 py-2.5">
                        <span
                          v-if="row.status === 'pending'"
                          class="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2 py-0.5 text-[11px] font-medium text-amber-700"
                        >
                          <span class="h-1.5 w-1.5 rounded-full bg-amber-500" />
                          等待中
                        </span>
                        <span
                          v-else-if="row.status === 'running'"
                          class="inline-flex items-center gap-1 rounded-full bg-blue-50 px-2 py-0.5 text-[11px] font-medium text-blue-600"
                        >
                          <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-blue-500" />
                          运行中
                        </span>
                        <span
                          v-else-if="row.status === 'success'"
                          class="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 text-[11px] font-medium text-emerald-600"
                        >
                          <CheckCircle2 class="h-3 w-3" />
                          完成
                        </span>
                        <span
                          v-else-if="row.status === 'failed'"
                          class="inline-flex items-center gap-1 rounded-full bg-red-50 px-2 py-0.5 text-[11px] font-medium text-red-500"
                        >
                          <XCircle class="h-3 w-3" />
                          失败
                        </span>
                        <span
                          v-else
                          class="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2 py-0.5 text-[11px] text-slate-500"
                        >待执行</span>
                      </td>
                      <td class="px-3 py-2.5 text-[12px]" :class="row.status === 'failed' ? 'text-red-500' : 'text-[#596080]'">
                        <span v-if="row.duration > 0">{{ row.duration }}s</span>
                        <span v-else class="text-[#B8BCCC]">—</span>
                      </td>
                      <td class="px-3 py-2.5 text-[12px]">
                        <template v-if="row.resultType === 'ratio' && row.outputCount > 0">
                          <div class="font-medium text-emerald-600">{{ row.ratioPercent != null ? row.ratioPercent.toFixed(2) + '%' : '—' }}</div>
                          <div class="text-[10px] text-[#B8BCCC]">{{ row.outputCount.toLocaleString() }} 条 / {{ row.denominatorCount?.toLocaleString() ?? '—' }} 条</div>
                        </template>
                        <span v-else-if="row.outputCount > 0" class="font-medium text-emerald-600">{{ row.outputCount.toLocaleString() }} 条</span>
                        <span v-else class="text-[#B8BCCC]">—</span>
                      </td>
                      <td class="whitespace-nowrap px-3 py-2.5 text-[12px] text-[#596080]">{{ row.startTime }}</td>
                      <td class="px-3 py-2.5" @click.stop>
                        <div class="flex items-center gap-2">
                          <button
                            type="button"
                            class="text-[11px] text-emerald-600 hover:text-emerald-800"
                            @click="selectRecord(row)"
                          >
                            查看
                          </button>
                          <button
                            type="button"
                            class="text-[11px] text-red-500 hover:text-red-700"
                            @click="deleteRecord(row)"
                          >
                            删除
                          </button>
                        </div>
                      </td>
                    </tr>
                    <tr v-if="filteredRecords.length === 0">
                      <td colspan="10" class="py-10 text-center text-[13px] text-[#B8BCCC]">暂无执行记录</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <!-- 主内容区：选中记录的详情 -->
    <div ref="detailContainer" class="min-h-0 flex-1 overflow-y-auto px-5 pb-5 pt-4">
      <!-- 有选中记录时显示详情 -->
      <template v-if="selectedRecord">
        <div class="mb-3 flex items-center justify-between">
          <h3 class="flex items-center text-[13px] font-semibold text-[#1F264D]">
            <Activity class="mr-2 h-4 w-4 text-emerald-500" />
            执行详情
            <span class="ml-2 rounded border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[11px] text-emerald-700">
              {{ selectedRecord.indicatorName }}
            </span>
          </h3>
          <div class="flex items-center gap-2">
            <button
              type="button"
              class="flex items-center gap-1.5 rounded-[2px] border border-[#b8c9e8] px-3 py-1.5 text-[12px] text-[#596080] transition-colors hover:bg-slate-50"
              @click="selectedRecord = null"
            >
              <X class="h-3.5 w-3.5" />
              关闭详情
            </button>
            <button
              type="button"
              class="flex items-center gap-1.5 rounded-[2px] bg-emerald-600 px-3 py-1.5 text-[12px] text-white transition-colors hover:bg-emerald-700"
              @click="rerun(selectedRecord)"
            >
              <RotateCcw class="h-3.5 w-3.5" />
              重新执行
            </button>
          </div>
        </div>

        <!-- 概览卡片 -->
        <div class="mb-4 shrink-0 rounded-[2px] border border-[#b8c9e8]/40 bg-[#f8faff] p-4">
          <div class="grid grid-cols-5 gap-3 text-[12px]">
            <div class="rounded-[2px] bg-white p-2.5 text-center border border-[#b8c9e8]/40">
              <div class="text-[11px] text-[#596080]">状态</div>
              <div
                class="mt-1 font-semibold"
                :class="
                  selectedRecord.status === 'success'
                    ? 'text-emerald-600'
                    : selectedRecord.status === 'failed'
                      ? 'text-red-500'
                      : selectedRecord.status === 'pending'
                        ? 'text-amber-700'
                        : 'text-blue-600'
                "
              >
                {{
                  selectedRecord.status === 'pending'
                    ? '等待中'
                    : selectedRecord.status === 'running'
                      ? '运行中'
                      : selectedRecord.status === 'success'
                        ? '完成'
                        : selectedRecord.status === 'failed'
                          ? '失败'
                          : '待执行'
                }}
              </div>
            </div>
            <div class="rounded-[2px] bg-white p-2.5 text-center border border-[#b8c9e8]/40">
              <div class="text-[11px] text-[#596080]">耗时</div>
              <div class="mt-1 font-semibold text-[#1F264D]">{{ selectedRecord.duration > 0 ? `${selectedRecord.duration}s` : '—' }}</div>
            </div>
            <div class="rounded-[2px] bg-white p-2.5 text-center border border-[#b8c9e8]/40">
              <div class="text-[11px] text-[#596080]">分子条数</div>
              <div class="mt-1 font-semibold text-emerald-600">{{ selectedRecord.numeratorCount != null ? selectedRecord.numeratorCount.toLocaleString() : '—' }}</div>
            </div>
            <div class="rounded-[2px] bg-white p-2.5 text-center border border-[#b8c9e8]/40">
              <div class="text-[11px] text-[#596080]">分母条数</div>
              <div class="mt-1 font-semibold text-emerald-600">{{ selectedRecord.denominatorCount != null ? selectedRecord.denominatorCount.toLocaleString() : '—' }}</div>
            </div>
            <div class="rounded-[2px] bg-white p-2.5 text-center border border-[#b8c9e8]/40">
              <div class="text-[11px] text-[#596080]">指标结果</div>
              <div class="mt-1 font-semibold" :class="selectedRecord.resultType === 'ratio' ? 'text-emerald-600' : 'text-blue-600'">
                <span v-if="selectedRecord.resultType === 'ratio' && selectedRecord.ratioPercent != null">{{ selectedRecord.ratioPercent.toFixed(2) }}%</span>
                <span v-else-if="selectedRecord.resultType === 'count' && selectedRecord.numeratorCount != null">{{ selectedRecord.numeratorCount.toLocaleString() }} 条</span>
                <span v-else>—</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 按医院分组显示 -->
        <div v-if="selectedRecord?.groupByHospital && selectedRecord?.hospitalResults?.length" class="mb-4 shrink-0 rounded-[2px] border border-[#b8c9e8]/40 bg-[#f8faff] p-4">
          <h4 class="mb-3 flex items-center text-[12px] font-semibold text-[#1F264D]">
            <Building2 class="mr-1.5 h-3.5 w-3.5 text-[#596080]" />
            各医院执行结果
          </h4>
          <div class="overflow-hidden rounded-[2px] border border-[#b8c9e8]/40">
            <table class="w-full border-collapse text-left text-[12px]">
              <thead class="bg-[#f8faff]">
                <tr>
                  <th class="px-3 py-2 font-semibold text-[#596080]">医院名称</th>
                  <th class="px-3 py-2 w-24 font-semibold text-[#596080] text-center">状态</th>
                  <th class="px-3 py-2 w-28 font-semibold text-[#596080] text-right">分子条数</th>
                  <th class="px-3 py-2 w-28 font-semibold text-[#596080] text-right">分母条数</th>
                  <th class="px-3 py-2 w-28 font-semibold text-[#596080] text-right">指标结果</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#b8c9e8]/20">
                <tr v-for="h in selectedRecord.hospitalResults" :key="h.hospitalCode" class="hover:bg-emerald-50/30">
                  <td class="px-3 py-2.5 font-medium text-[#1F264D]">{{ h.hospitalName }}</td>
                  <td class="px-3 py-2.5 text-center">
                    <span
                      v-if="h.status === 'success'"
                      class="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 text-[11px] font-medium text-emerald-600"
                    >
                      <CheckCircle2 class="h-3 w-3" />
                      完成
                    </span>
                    <span
                      v-else-if="h.status === 'failed'"
                      class="inline-flex items-center gap-1 rounded-full bg-red-50 px-2 py-0.5 text-[11px] font-medium text-red-500"
                    >
                      <XCircle class="h-3 w-3" />
                      失败
                    </span>
                    <span
                      v-else-if="h.status === 'running'"
                      class="inline-flex items-center gap-1 rounded-full bg-blue-50 px-2 py-0.5 text-[11px] font-medium text-blue-600"
                    >
                      <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-blue-500" />
                      运行中
                    </span>
                    <span v-else class="text-[#B8BCCC]">—</span>
                  </td>
                  <td class="px-3 py-2.5 text-right font-medium text-emerald-600">{{ h.numeratorCount?.toLocaleString() ?? '—' }}</td>
                  <td class="px-3 py-2.5 text-right font-medium text-emerald-600">{{ h.denominatorCount?.toLocaleString() ?? '—' }}</td>
                  <td class="px-3 py-2.5 text-right font-medium" :class="h.ratioPercent != null ? 'text-emerald-600' : 'text-[#596080]'">
                    {{ h.ratioPercent != null ? h.ratioPercent.toFixed(2) + '%' : (h.numeratorCount != null ? h.numeratorCount.toLocaleString() + ' 条' : '—') }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 详情内容 -->
        <div class="flex min-h-0 flex-1 gap-4 rounded-[2px] border border-[#b8c9e8]/40 bg-white">
          <!-- 左侧：分子/分母数据 -->
          <div class="min-h-0 flex-1 space-y-4 overflow-y-auto p-4">
            <!-- 分子结果 -->
            <div>
              <h4 class="mb-2 flex items-center text-[12px] font-semibold text-[#1F264D]">
                <Code2 class="mr-1.5 h-3.5 w-3.5 text-[#596080]" />
                分子预览数据
                <!-- 分医院筛选 -->
                <span v-if="selectedRecord?.groupByHospital && detailHospOptions.length" class="ml-3">
                  <select
                    v-model="selectedDetailHospCode"
                    class="rounded border border-[#b8c9e8]/60 bg-white px-2 py-0.5 text-[11px] text-[#1F264D] focus:outline-none focus:ring-1 focus:ring-[#596080]"
                  >
                    <option value="">全部医院汇总</option>
                    <option v-for="opt in detailHospOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                  </select>
                </span>
              </h4>
              <div v-if="selectedRecord.resultData && selectedRecord.resultData.length > 0"
                class="rounded-[2px] border border-[#b8c9e8]/60 overflow-hidden">
                <VirtualTable
                  v-if="paginatedNumRows.length > 0"
                  :columns="selectedRecord.resultColumns"
                  :rows="paginatedNumRows"
                  :row-height="36"
                  :overscan="8"
                  max-height="300px"
                />
                <!-- 加载骨架 -->
                <div v-else-if="numRowsLoading" class="p-4 space-y-2">
                  <div v-for="i in 5" :key="i" class="h-8 bg-[#f0f4ff] rounded animate-pulse" />
                </div>
                <div class="border-t border-[#b8c9e8]/60 bg-[#f8faff] px-3 py-1.5 text-[11px] text-[#596080] flex items-center justify-between gap-2">
                  <span>共 {{ selectedRecord.numeratorCount?.toLocaleString() ?? '—' }} 条记录</span>
                  <div class="flex items-center gap-1">
                    <button
                      class="shrink-0 rounded px-1.5 py-0.5 transition-colors"
                      :class="numPage <= 1 ? 'cursor-not-allowed text-gray-300' : 'cursor-pointer text-[#596080] hover:bg-[#d0daeb]/40'"
                      :disabled="numPage <= 1 || numRowsLoading"
                      @click="loadNumPage(Math.max(1, numPage - 1))"
                    >&lt;</button>
                    <span class="min-w-[60px] text-center">{{ numPage }} / {{ numTotalPages }}<span v-if="numRowsLoading" class="ml-1 text-amber-500">加载中</span></span>
                    <button
                      class="shrink-0 rounded px-1.5 py-0.5 transition-colors"
                      :class="numPage >= numTotalPages ? 'cursor-not-allowed text-gray-300' : 'cursor-pointer text-[#596080] hover:bg-[#d0daeb]/40'"
                      :disabled="numPage >= numTotalPages || numRowsLoading"
                      @click="loadNumPage(Math.min(numTotalPages, numPage + 1))"
                    >&gt;</button>
                  </div>
                </div>
              </div>
              <div v-else
                class="rounded-[2px] border border-[#b8c9e8]/60 bg-[#f8faff] p-4 text-center text-[12px] text-[#B8BCCC]">
                暂无分子结果数据
              </div>
            </div>

            <!-- 分母结果（仅比值型显示） -->
            <div v-if="selectedRecord.resultType === 'ratio' && selectedRecord.denominatorPreviewData?.rows?.length > 0">
              <h4 class="mb-2 flex items-center text-[12px] font-semibold text-[#1F264D]">
                <Code2 class="mr-1.5 h-3.5 w-3.5 text-[#596080]" />
                分母预览数据
              </h4>
              <div class="rounded-[2px] border border-[#b8c9e8]/60 overflow-hidden">
                <VirtualTable
                  v-if="paginatedDenRows.length > 0"
                  :columns="selectedRecord.denominatorPreviewColumns"
                  :rows="paginatedDenRows"
                  :row-height="36"
                  :overscan="8"
                  max-height="300px"
                />
                <!-- 加载骨架 -->
                <div v-else-if="denRowsLoading" class="p-4 space-y-2">
                  <div v-for="i in 5" :key="i" class="h-8 bg-[#f0f4ff] rounded animate-pulse" />
                </div>
                <div class="border-t border-[#b8c9e8]/60 bg-[#f8faff] px-3 py-1.5 text-[11px] text-[#596080] flex items-center justify-between gap-2">
                  <span>共 {{ selectedRecord.denominatorCount?.toLocaleString() ?? '—' }} 条记录</span>
                  <div class="flex items-center gap-1">
                    <button
                      class="shrink-0 rounded px-1.5 py-0.5 transition-colors"
                      :class="denPage <= 1 ? 'cursor-not-allowed text-gray-300' : 'cursor-pointer text-[#596080] hover:bg-[#d0daeb]/40'"
                      :disabled="denPage <= 1 || denRowsLoading"
                      @click="loadDenPage(Math.max(1, denPage - 1))"
                    >&lt;</button>
                    <span class="min-w-[60px] text-center">{{ denPage }} / {{ denTotalPages }}<span v-if="denRowsLoading" class="ml-1 text-amber-500">加载中</span></span>
                    <button
                      class="shrink-0 rounded px-1.5 py-0.5 transition-colors"
                      :class="denPage >= denTotalPages ? 'cursor-not-allowed text-gray-300' : 'cursor-pointer text-[#596080] hover:bg-[#d0daeb]/40'"
                      :disabled="denPage >= denTotalPages || denRowsLoading"
                      @click="loadDenPage(Math.min(denTotalPages, denPage + 1))"
                    >&gt;</button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 错误信息 -->
            <div v-if="selectedRecord.errorMessage">
              <h4 class="mb-2 flex items-center text-[12px] font-semibold text-red-500">
                <AlertCircle class="mr-1.5 h-3.5 w-3.5" />
                错误信息
              </h4>
              <div class="rounded-[2px] border border-red-200 bg-red-50 p-3 text-[12px] text-red-700">{{ selectedRecord.errorMessage }}</div>
            </div>
          </div>

          <!-- 右侧：执行日志 -->
        </div>
      </template>

      <!-- 无选中记录时显示空状态 -->
      <div v-else class="flex h-full flex-col items-center justify-center rounded-[2px] border border-dashed border-[#b8c9e8]/60 bg-[#f8faff]">
        <Clock class="mb-3 h-12 w-12 text-[#B8BCCC]" />
        <p class="text-[13px] text-[#B8BCCC]">点击右上角历史记录，查看执行详情</p>
        <p class="mt-1 text-[12px] text-[#C8D0E0]">或选择指标后发起新的执行任务</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, nextTick, watch } from 'vue'
import {
  Activity,
  AlertCircle,
  Building2,
  CheckCircle2,
  ChevronDown,
  Clock,
  Code2,
  PlayCircle,
  RotateCcw,
  Search,
  X,
  XCircle,
  Zap,
} from 'lucide-vue-next'
import VirtualTable from '@/components/VirtualTable.vue'
import MultiSelectDropdown from '@/components/ui/MultiSelectDropdown.vue'
import { indicatorsApi, type Indicator } from '@/api/indicators'
import { DEFAULT_CORE18, DEFAULT_FOUR_ELEMENTS } from '@/data/indicatorManagementDefaults'
import { MOCK_RECORDS, type ExecutionRecord, type RunMode, type RunStatus } from '@/data/indicatorExecutionDefaults'

const RUN_MODE_OPTIONS: { value: RunMode; label: string }[] = [
  { value: 'immediate', label: '全量执行' },
  { value: 'monthly', label: '按月执行' },
  { value: 'quarterly', label: '按季度执行' },
]

const RUN_MODE_MAP: Record<RunMode, string> = {
  immediate: '全量执行',
  monthly: '按月执行',
  quarterly: '按季度执行',
}

const STATUS_FILTERS: { value: string; label: string }[] = [
  { value: 'all', label: '全部' },
  { value: 'pending', label: '等待中' },
  { value: 'running', label: '运行中' },
  { value: 'success', label: '完成' },
  { value: 'failed', label: '失败' },
]

const runKind = ref<'four' | 'core18'>('core18')
const runScopes = ref<string[]>([])
const runIndicatorId = ref('')
const runMode = ref<RunMode>('immediate')

const MONTH_OPTIONS = [
  { value: '01', label: '1月' }, { value: '02', label: '2月' }, { value: '03', label: '3月' },
  { value: '04', label: '4月' }, { value: '05', label: '5月' }, { value: '06', label: '6月' },
  { value: '07', label: '7月' }, { value: '08', label: '8月' }, { value: '09', label: '9月' },
  { value: '10', label: '10月' }, { value: '11', label: '11月' }, { value: '12', label: '12月' },
]
const monthYearOptions = computed(() => {
  const now = new Date()
  const cur = now.getFullYear()
  return [cur - 1, cur, cur + 1]
})
const selectedMonthYear = ref(new Date().getFullYear())
const selectedMonthNum = ref('01')

const quarterYearOptions = computed(() => {
  const now = new Date()
  const cur = now.getFullYear()
  return [cur - 3, cur - 2, cur - 1, cur, cur + 1]
})
const selectedQuarterYear = ref(new Date().getFullYear())
const selectedQuarterNum = ref('1')
const quarterOptionsOfYear = computed(() => [
  { value: '1', label: 'Q1（一季度）' },
  { value: '2', label: 'Q2（二季度）' },
  { value: '3', label: 'Q3（三季度）' },
  { value: '4', label: 'Q4（四季度）' },
])
const statusFilter = ref('all')
const searchKeyword = ref('')
const records = ref<ExecutionRecord[]>([])
const historyOpen = ref(false)
const selectedRecord = ref<ExecutionRecord | null>(null)
const executingIds = ref<Set<string>>(new Set())
const detailContainer = ref<HTMLElement | null>(null)

// 状态筛选变化时，如果有搜索关键词则重新加载
watch(statusFilter, async () => {
  if (searchKeyword.value) {
    await loadRecords()
  }
})

const PAGE_SIZE = 50
const numPage = ref(1)
const denPage = ref(1)

// 切换记录时重置医院筛选和分页
watch(selectedRecord, () => {
  selectedDetailHospCode.value = ''
  numPage.value = 1
  denPage.value = 1
})

// 分页缓存（key = `${executionId}_${target}_${page}`）
const numRowsCache = new Map<string, Record<string, unknown>[]>()
const denRowsCache = new Map<string, Record<string, unknown>[]>()
const numRowsLoading = ref(false)
const denRowsLoading = ref(false)

async function loadNumPage(page: number) {
  const rec = selectedRecord.value
  if (!rec?.id) return
  if (rec.status === 'running' || rec.status === 'pending') return
  // 优先使用数据库记录ID（执行后返回），否则降级到前端临时ID
  const apiId: number | string = rec.dbRecordId ?? rec.id
  const cacheKey = `${rec.id}_numerator_${page}`
  if (numRowsCache.has(cacheKey)) {
    numPage.value = page
    return
  }
  numRowsLoading.value = true
  try {
    const res = await indicatorsApi.getPreviewPage({
      execution_id: apiId,
      target: 'numerator',
      page,
      page_size: PAGE_SIZE,
    })
    if (res.ok && res.rows) {
      numRowsCache.set(cacheKey, res.rows)
      numPage.value = page
    } else {
      console.warn('loadNumPage failed:', res.error)
    }
  } catch (e) {
    console.error('loadNumPage error:', e)
  } finally {
    numRowsLoading.value = false
  }
}

async function loadDenPage(page: number) {
  const rec = selectedRecord.value
  if (!rec?.id) return
  if (rec.status === 'running' || rec.status === 'pending') return
  // 优先使用数据库记录ID（执行后返回），否则降级到前端临时ID
  const apiId: number | string = rec.dbRecordId ?? rec.id
  const cacheKey = `${rec.id}_denominator_${page}`
  if (denRowsCache.has(cacheKey)) {
    denPage.value = page
    return
  }
  denRowsLoading.value = true
  try {
    const res = await indicatorsApi.getPreviewPage({
      execution_id: apiId,
      target: 'denominator',
      page,
      page_size: PAGE_SIZE,
    })
    if (res.ok && res.rows) {
      denRowsCache.set(cacheKey, res.rows)
      denPage.value = page
    } else {
      console.warn('loadDenPage failed:', res.error)
    }
  } catch (e) {
    console.error('loadDenPage error:', e)
  } finally {
    denRowsLoading.value = false
  }
}

const numTotalPages = computed(() =>
  selectedRecord.value?.numeratorCount
    ? Math.max(1, Math.ceil(selectedRecord.value.numeratorCount / PAGE_SIZE))
    : 1
)

const denTotalPages = computed(() =>
  selectedRecord.value?.denominatorCount
    ? Math.max(1, Math.ceil(selectedRecord.value.denominatorCount / PAGE_SIZE))
    : 1
)

const canPaginateByApi = computed(() => !!selectedRecord.value?.id)

// 详情区：按医院筛选
const selectedDetailHospCode = ref<string>('')

const detailHospOptions = computed(() => {
  if (!selectedRecord.value?.groupByHospital || !selectedRecord.value?.hospitalResults?.length) return []
  return selectedRecord.value.hospitalResults.map((h) => ({
    value: h.hospitalCode,
    label: h.hospitalName,
  }))
})

const paginatedNumRows = computed(() => {
  const rec = selectedRecord.value
  if (!rec) return []
  if (rec.groupByHospital && selectedDetailHospCode.value && rec.hospitalResults?.length) {
    const hosp = rec.hospitalResults.find((h) => h.hospitalCode === selectedDetailHospCode.value)
    return hosp?.previewData ?? []
  }
  const data = rec.resultData ?? []
  if (data.length > 0) return data
  const cacheKey = `${rec.id}_numerator_${numPage.value}`
  return numRowsCache.get(cacheKey) ?? []
})

const paginatedDenRows = computed(() => {
  const rec = selectedRecord.value
  if (!rec) return []
  if (rec.groupByHospital && selectedDetailHospCode.value && rec.hospitalResults?.length) {
    const hosp = rec.hospitalResults.find((h) => h.hospitalCode === selectedDetailHospCode.value)
    return hosp?.denominatorPreviewData ?? []
  }
  const data = rec.denominatorPreviewData?.rows ?? []
  if (data.length > 0) return data
  const cacheKey = `${rec.id}_denominator_${denPage.value}`
  return denRowsCache.get(cacheKey) ?? []
})

const allIndicators = ref<Indicator[]>([])
const hospitalList = ref<{ MDC_ORG_CD: string; MDC_ORG_NM: string }[]>([])

// 医院选项（多选下拉框）
const hospitalOptions = computed(() => [
  { value: '__all__', label: '全省' },
  ...hospitalList.value.map((h) => ({ value: h.MDC_ORG_CD, label: h.MDC_ORG_NM })),
])

onMounted(async () => {
  await Promise.all([loadRecords(), loadIndicators(), loadHospitals()])
})

async function loadHospitals() {
  try {
    const res = await indicatorsApi.getHospitals()
    hospitalList.value = res || []
  } catch (e) {
    console.error('加载医院列表失败:', e)
    hospitalList.value = []
  }
}

async function loadIndicators() {
  try {
    const [four, core18] = await Promise.all([
      indicatorsApi.getFourIndicators(),
      indicatorsApi.getCore18Indicators(),
    ])
    allIndicators.value = [...four, ...core18]
  } catch (e) {
    console.error('加载指标列表失败:', e)
  }
}

async function loadRecords() {
  try {
    const params: any = {}
    if (runIndicatorId.value) {
      params.indicator_id = Number(runIndicatorId.value)
    }
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    if (statusFilter.value !== 'all') {
      params.status = statusFilter.value
    }
    if (runKind.value) {
      params.kind = runKind.value
    }
    const history = await indicatorsApi.getExecutionHistory(params)
    if (history && history.length > 0) {
      records.value = history.map((exec: any) => {
        const ind = allIndicators.value.find((i: any) => i.id === exec.indicator)
        const rawCalcType = exec.indicator?.calc_type ?? ind?.calc_type ?? exec.result_type ?? 'ratio'
        const isCount = rawCalcType === 'count'
        const resultType: 'ratio' | 'count' = isCount ? 'count' : 'ratio'
        const outputCount = isCount
          ? (exec.count ?? exec.numerator_count ?? 0)
          : (exec.numerator_count ?? exec.denominator_count ?? 0)
        const isGroupByHospital = exec.group_by_hospital || false
        const hospitalResults = exec.hospital_results || []
        const firstHospWithData = hospitalResults.find((h: any) => h.preview_data && h.preview_data.length > 0)
        const execPreviewData = exec.preview_data || {}
        const resultColumns = execPreviewData.columns
          ?? exec.preview_columns
          ?? (exec.result_data ? Object.keys(exec.result_data?.[0] ?? {}) : undefined)
          ?? (isGroupByHospital && firstHospWithData && firstHospWithData.preview_data?.length ? Object.keys(firstHospWithData.preview_data[0] || {}) : undefined)
        const resultData = execPreviewData.rows ?? exec.preview_rows ?? exec.result_data
          ?? (isGroupByHospital && firstHospWithData ? firstHospWithData.preview_data : undefined)
        const denominatorPreviewColumns = exec.denominator_preview_columns
          ?? exec.denominator_preview_data?.columns
          ?? (exec.denominator_preview_data?.rows?.length ? Object.keys(exec.denominator_preview_data.rows[0]) : undefined)
        const denominatorPreviewData = exec.denominator_preview_data ?? { columns: exec.denominator_preview_columns ?? [], rows: exec.denominator_preview_rows ?? [] }
        return {
          id: String(exec.id),
          kind: exec.kind || exec.indicator?.indicator_type || 'core18',
          indicatorName: exec.indicator_name || ind?.name || `指标 #${exec.indicator}`,
          indicatorId: String(exec.indicator || ''),
          runMode: (exec.run_mode as RunMode) || 'immediate',
          timeRange: exec.time_range || '全量',
          status: (exec.status || 'pending') as RunStatus,
          startTime: exec.execution_time || '—',
          duration: exec.duration_seconds || 0,
          scope: exec.scope || '',
          dateField: exec.indicator?.date_field ?? ind?.date_field ?? 'discharge',
          outputCount,
          ratioPercent: isCount ? undefined : (exec.rate_percent ?? undefined),
          denominatorCount: isCount ? undefined : (exec.denominator_count ?? undefined),
          numeratorCount: isCount ? (exec.count ?? exec.numerator_count ?? 0) : (exec.numerator_count ?? undefined),
          resultType,
          resultColumns,
          resultData,
          denominatorPreviewColumns,
          denominatorPreviewData,
          calcMethod: exec.calc_method || ((exec.numerator_sql || exec.sql) ? 'SQL录入' : '大模型Prompt'),
          usedScript: isCount
            ? (exec.sql || exec.numerator_sql || exec.denominator_sql || '')
            : (exec.numerator_sql
                ? `【分子 SQL】\n${exec.numerator_sql}\n\n【分母 SQL】\n${exec.denominator_sql || '—'}`
                : (exec.sql || '')),
          errorMessage: exec.error || undefined,
          logs: exec.logs?.length ? exec.logs : buildLogs(exec, isCount),
          groupByHospital: exec.group_by_hospital || false,
          hospitalResults: (exec.hospital_results || []).map((h: any) => ({
            hospitalCode: h.hospital_code ?? '',
            hospitalName: h.hospital_name ?? '',
            status: h.status ?? 'pending',
            numeratorCount: h.numerator_count,
            denominatorCount: h.denominator_count,
            ratioPercent: h.ratio_percent,
            previewData: h.preview_data || [],
            denominatorPreviewData: h.denominator_preview_data || [],
            error: h.error || undefined,
          })),
        }
      })
    } else {
      records.value = JSON.parse(JSON.stringify(MOCK_RECORDS))
    }
  } catch (e) {
    console.error('加载执行记录失败:', e)
    records.value = JSON.parse(JSON.stringify(MOCK_RECORDS))
  }
}

async function handleSearch() {
  await loadRecords()
}

function buildLogs(exec: any, isCount: boolean = false): { time: string; level: 'info' | 'warn' | 'error'; message: string }[] {
  const logs = []
  const base = exec.execution_time ? new Date(exec.execution_time) : new Date()
  const t = (offset: number) => {
    const d = new Date(base.getTime() + offset * 1000)
    return d.toLocaleTimeString('zh-CN')
  }
  if (isCount) {
    logs.push({ time: t(0), level: 'info', message: '任务已提交...' })
    if (exec.numerator_sql || exec.sql) {
      logs.push({ time: t(1), level: 'info', message: '执行 SQL...' })
      if (exec.count != null) logs.push({ time: t(2), level: 'info', message: `查询结果：${exec.count} 条记录。` })
    }
    if (exec.error) {
      logs.push({ time: t(3), level: 'error', message: `错误：${exec.error}` })
    } else {
      logs.push({ time: t(3), level: 'info', message: `执行完成，共 ${exec.count ?? 0} 条记录。` })
    }
  } else {
    logs.push({ time: t(0), level: 'info', message: '任务已提交...' })
    if (exec.numerator_sql) {
      logs.push({ time: t(1), level: 'info', message: '执行分子 SQL...' })
      if (exec.numerator_count !== null) logs.push({ time: t(2), level: 'info', message: `分子结果：${exec.numerator_count} 条记录。` })
    }
    if (exec.denominator_sql) {
      logs.push({ time: t(3), level: 'info', message: '执行分母 SQL...' })
      if (exec.denominator_count !== null) logs.push({ time: t(4), level: 'info', message: `分母结果：${exec.denominator_count} 条记录。` })
    }
    if (exec.error) {
      logs.push({ time: t(5), level: 'error', message: `错误：${exec.error}` })
    } else {
      logs.push({ time: t(5), level: 'info', message: `执行完成。${exec.rate_percent != null ? `指标值：${exec.rate_percent}%` : ''}` })
    }
  }
  return logs
}

const currentIndicatorOptions = computed(() => {
  const filtered = allIndicators.value.filter((x: any) => x.indicator_type === runKind.value)
  if (filtered.length === 0) {
    return runKind.value === 'four'
      ? DEFAULT_FOUR_ELEMENTS.map((x) => ({ id: x.id, label: `序号 ${x.seq} — ${x.category}：${x.workContent.slice(0, 20)}...` }))
      : DEFAULT_CORE18.map((x) => ({ id: x.id, label: x.name }))
  }
  return filtered.map((x: any) => ({
    id: x.id,
    label: x.name,
    numerator_sql: x.numerator_sql,
    denominator_sql: x.denominator_sql,
    sql: x.sql_content,
    calc_type: x.calc_type ?? 'ratio',
    date_field: x.date_field ?? 'discharge',
  }))
})

const filteredRecords = computed(() => {
  if (statusFilter.value === 'all') return records.value
  return records.value.filter((r) => r.status === statusFilter.value)
})

async function handleRun() {
  const selectedInd = currentIndicatorOptions.value.find((x: any) => x.id == runIndicatorId.value)
  if (!runIndicatorId.value) {
    window.alert('请先选择要执行的指标')
    return
  }
  const scheduled = runMode.value !== 'immediate'
  let rangeLabel = '全量'
  if (runMode.value === 'monthly') {
    rangeLabel = `${selectedMonthYear.value}年${Number(selectedMonthNum.value)}月`
  } else if (runMode.value === 'quarterly') {
    const qmap: Record<string, string> = { '1': '一', '2': '二', '3': '三', '4': '四' }
    rangeLabel = `${selectedQuarterYear.value}年${qmap[selectedQuarterNum.value]}季度`
  }
  const execId = `exec-${Date.now()}`
  const newRecord: ExecutionRecord = {
    id: execId,
    kind: runKind.value,
    indicatorName: selectedInd?.label ?? '全部指标',
    indicatorId: runIndicatorId.value,
    runMode: runMode.value,
    timeRange: rangeLabel,
    status: 'running',
    startTime: new Date().toLocaleString('zh-CN'),
    duration: 0,
    outputCount: 0,
    scope: runScopes.value.includes('__all__') ? '' : runScopes.value.join(','),
    dateField: selectedInd?.date_field ?? 'discharge',
    calcMethod: 'SQL录入',
    resultType: (selectedInd?.calc_type as 'ratio' | 'count') || 'ratio',
    groupByHospital: true,
    usedScript: selectedInd?.resultType === 'count'
        ? (selectedInd?.sql || selectedInd?.numerator_sql || selectedInd?.denominator_sql || '-- 正在执行，请稍候...')
        : selectedInd?.numerator_sql
          ? `【分子 SQL】\n${selectedInd.numerator_sql}\n\n【分母 SQL】\n${selectedInd.denominator_sql || '—'}`
          : selectedInd?.sql || '-- 正在执行，请稍候...\nSELECT * FROM ...;',
    logs: buildLogs({}, selectedInd?.calc_type === 'count'),
  }
  records.value = [newRecord, ...records.value]
  selectedRecord.value = newRecord
  executingIds.value.add(execId)
  try {
    const reqData: any = {
      business_type: runKind.value,
      indicator_id: Number(runIndicatorId.value),
      kind: runKind.value,
      run_mode: runMode.value,
      time_range: rangeLabel,
      result_type: (selectedInd?.calc_type as 'ratio' | 'count') || 'ratio',
      calc_method: 'SQL录入',
      scope: runScopes.value.includes('__all__') ? '' : runScopes.value.join(','),
      group_by_hospital: runScopes.value.length > 0 && !runScopes.value.includes('__all__'),
    }
    reqData.hospital_codes = runScopes.value.includes('__all__') ? [] : runScopes.value
    // 存储完整医院列表用于重跑
    const finalHospitalCodes = runScopes.value.includes('__all__')
      ? hospitalList.value.map(h => h.MDC_ORG_CD)
      : runScopes.value
    newRecord.hospitalCodes = finalHospitalCodes
    console.log('发送请求 - runScopes:', runScopes.value, 'hospital_codes:', reqData.hospital_codes, 'group_by_hospital:', reqData.group_by_hospital)
    if (runMode.value === 'monthly' || runMode.value === 'quarterly') {
      reqData.time_mode = runMode.value
      reqData.time_value = runMode.value === 'monthly'
        ? `${selectedMonthYear.value}-${selectedMonthNum.value}`
        : `${selectedQuarterYear.value}-Q${selectedQuarterNum.value}`
    }
    if (selectedInd?.date_field) {
      reqData.date_field = selectedInd.date_field
    }
    const result = await indicatorsApi.executeIndicator(reqData)
    const idx = records.value.findIndex((r) => r.id === execId)
    if (idx < 0) return
    const exec = result as any
    if (exec.error && !exec.ok) {
      records.value[idx] = {
        ...records.value[idx],
        status: 'failed',
        duration: 0,
        errorMessage: exec.error,
        logs: [
          ...records.value[idx].logs,
          { time: new Date().toLocaleTimeString('zh-CN'), level: 'error', message: `执行失败：${exec.error}` },
        ],
      }
      window.alert(`执行失败：${exec.error}`)
    } else {
      const numCnt = exec.numerator_count ?? 0
      const denCnt = exec.denominator_count ?? 0
      const rate = exec.rate_percent
      const rawCalcType = exec.calc_type ?? exec.indicator?.calc_type ?? selectedInd?.calc_type
      const isRatio = rawCalcType !== 'count'
      const resultType: 'ratio' | 'count' = isRatio ? 'ratio' : 'count'
      const countVal = isRatio ? numCnt : (exec.count ?? 0)
      const updatedRecord = {
        ...records.value[idx],
        status: 'success',
        duration: exec.duration_seconds || 0,
        outputCount: countVal,
        ratioPercent: isRatio ? (rate ?? undefined) : undefined,
        denominatorCount: isRatio ? denCnt : undefined,
        numeratorCount: isRatio ? numCnt : (exec.count ?? numCnt ?? 0),
        resultType,
        resultColumns: exec.preview_data?.columns
          ?? exec.preview_columns
          ?? (exec.result_data ? Object.keys(exec.result_data?.[0] ?? {}) : undefined),
        resultData: exec.preview_data?.rows ?? exec.preview_rows ?? exec.result_data,
        denominatorPreviewColumns: exec.denominator_preview_columns
          ?? exec.denominator_preview_data?.columns
          ?? (exec.denominator_preview_data?.rows?.length ? Object.keys(exec.denominator_preview_data.rows[0]) : undefined),
        denominatorPreviewData: exec.denominator_preview_data ?? { columns: exec.denominator_preview_columns ?? [], rows: exec.denominator_preview_rows ?? [] },
        calcMethod: (exec.numerator_sql || exec.sql) ? 'SQL录入' : '大模型Prompt',
        usedScript: isRatio
          ? (exec.numerator_sql ? `【分子 SQL】\n${exec.numerator_sql}\n\n【分母 SQL】\n${exec.denominator_sql || '—'}` : (exec.sql || ''))
          : (exec.sql || exec.numerator_sql || ''),
        logs: [
          ...records.value[idx].logs,
          ...(isRatio
            ? [
                { time: new Date().toLocaleTimeString('zh-CN'), level: 'info' as const, message: `分子 SQL 执行完成：${numCnt} 条记录。` },
                { time: new Date().toLocaleTimeString('zh-CN'), level: 'info' as const, message: `分母 SQL 执行完成：${denCnt} 条记录。` },
                { time: new Date().toLocaleTimeString('zh-CN'), level: 'info' as const, message: `执行完成。指标值：${rate ?? '—'}%（${numCnt}/${denCnt}）` },
              ]
            : [
                { time: new Date().toLocaleTimeString('zh-CN'), level: 'info' as const, message: `SQL 执行完成：${countVal} 条记录。` },
              ]),
        ],
        dbRecordId: exec.db_record_id ?? null,
        groupByHospital: exec.group_by_hospital || false,
        hospitalResults: (exec.hospital_results || []).map((h: any) => ({
          hospitalCode: h.hospital_code ?? '',
          hospitalName: h.hospital_name ?? '',
          status: h.status ?? 'pending',
          numeratorCount: h.numerator_count,
          denominatorCount: h.denominator_count,
          ratioPercent: h.ratio_percent,
          previewData: h.preview_data || [],
          denominatorPreviewData: h.denominator_preview_data || [],
          error: h.error || undefined,
        })),
      }
      console.log('[DEBUG] runIndicator resultColumns:', updatedRecord.resultColumns, 'resultData length:', updatedRecord.resultData?.length)
      console.log('[DEBUG] runIndicator raw exec.preview_data:', exec.preview_data, 'preview_rows:', exec.preview_rows)
      records.value[idx] = updatedRecord
      if (selectedRecord.value?.id === execId) {
        selectedRecord.value = updatedRecord
      }
      window.alert(isRatio
        ? `执行成功！指标值：${rate ?? '—'}%`
        : `执行成功！共 ${countVal} 条记录。`)
    }
  } catch (e: any) {
    const idx = records.value.findIndex((r) => r.id === execId)
    if (idx >= 0) {
      records.value[idx] = {
        ...records.value[idx],
        status: 'failed',
        errorMessage: e.message || String(e),
        logs: [
          ...records.value[idx].logs,
          { time: new Date().toLocaleTimeString('zh-CN'), level: 'error', message: `请求失败：${e.message || e}` },
        ],
      }
    }
    window.alert(`请求失败：${e.message || e}`)
  } finally {
    executingIds.value.delete(execId)
  }
}

function selectRecord(row: ExecutionRecord) {
  numPage.value = 1
  denPage.value = 1
  selectedRecord.value = row
  historyOpen.value = false
  nextTick(() => {
    detailContainer.value?.scrollTo({ top: 0, behavior: 'smooth' })
  })
  // 预填第1页缓存（执行时已返回）
  const hasNum = row.resultData?.length
  const hasDen = row.denominatorPreviewData?.rows?.length
  if (row.id && !isNaN(Number(row.id))) {
    const numKey = `${row.id}_numerator_1`
    const denKey = `${row.id}_denominator_1`
    if (hasNum) numRowsCache.set(numKey, row.resultData)
    if (hasDen) denRowsCache.set(denKey, row.denominatorPreviewData.rows)
    // 预加载第2页（仅当记录已持久化且数据量超过一页时）
    if (!executingIds.value.has(String(row.id))) {
      if (hasNum && (row.numeratorCount ?? 0) > PAGE_SIZE) {
        loadNumPage(2)
      }
      if (hasDen && (row.denominatorCount ?? 0) > PAGE_SIZE) {
        loadDenPage(2)
      }
    }
  }
}

async function deleteRecord(row: ExecutionRecord) {
  if (!window.confirm(`确定删除执行记录「${row.indicatorName}」吗？`)) return
  try {
    await indicatorsApi.deleteExecution(Number(row.id))
    records.value = records.value.filter((r) => r.id !== row.id)
    if (selectedRecord.value?.id === row.id) {
      selectedRecord.value = null
    }
  } catch (e) {
    window.alert(`删除失败：${e}`)
  }
}

async function rerun(row: ExecutionRecord) {
  const idx = records.value.findIndex((r) => r.id === row.id)
  if (idx < 0) return
  const execId = `exec-${Date.now()}`
  const copy: ExecutionRecord = {
    ...JSON.parse(JSON.stringify(row)),
    id: execId,
    status: 'running',
    startTime: new Date().toLocaleString('zh-CN'),
    duration: 0,
    outputCount: 0,
    ratioPercent: undefined,
    denominatorCount: undefined,
    numeratorCount: undefined,
    resultColumns: undefined,
    resultData: undefined,
    scope: row.scope,
    logs: [{ time: new Date().toLocaleTimeString('zh-CN'), level: 'info' as const, message: '任务已重新提交...' }],
  }
  records.value = [copy, ...records.value]
  selectedRecord.value = copy

  executingIds.value.add(execId)
  try {
    let timeMode: string | undefined
    let timeValue: string | undefined
    if (copy.runMode === 'monthly') {
      const match = copy.timeRange.match(/^(\d+)年(\d+)月/)
      if (match) {
        timeMode = 'monthly'
        timeValue = `${match[1]}-${match[2].padStart(2, '0')}`
      }
    } else if (copy.runMode === 'quarterly') {
      const match = copy.timeRange.match(/^(\d+)年(.)季度/)
      if (match) {
        timeMode = 'quarterly'
        const qmap: Record<string, string> = { '一': '1', '二': '2', '三': '3', '四': '4' }
        timeValue = `${match[1]}-Q${qmap[match[2]] || '1'}`
      }
    }
    const result = await indicatorsApi.executeIndicator({
      business_type: copy.kind,
      indicator_id: Number(copy.indicatorId) || undefined,
      kind: copy.kind,
      run_mode: copy.runMode,
      time_range: copy.timeRange,
      result_type: copy.resultType,
      calc_method: copy.calcMethod,
      scope: copy.scope || '',
      // 优先使用已存储的完整医院列表（全省重跑时包含所有医院）
      hospital_codes: copy.hospitalCodes && copy.hospitalCodes.length > 0
        ? copy.hospitalCodes
        : (copy.scope ? [copy.scope] : []),
      group_by_hospital: true,
      time_mode: timeMode,
      time_value: timeValue,
    })
    const i = records.value.findIndex((r) => r.id === execId)
    if (i < 0) return
    const exec = result as any
    const numCnt = exec.numerator_count ?? 0
    const denCnt = exec.denominator_count ?? 0
    const rate = exec.rate_percent
    if (exec.error && !exec.ok) {
      records.value[i] = {
        ...records.value[i],
        status: 'failed',
        errorMessage: exec.error,
        logs: [
          ...records.value[i].logs,
          { time: new Date().toLocaleTimeString('zh-CN'), level: 'error', message: `执行失败：${exec.error}` },
        ],
      }
    } else {
      const rawCalcType = row.resultType
      const isRatio = rawCalcType !== 'count'
      const countVal = isRatio ? numCnt : ((exec.count ?? numCnt) || 0)
      records.value[i] = {
        ...records.value[i],
        status: 'success',
        duration: exec.duration_seconds || 0,
        outputCount: countVal,
        ratioPercent: isRatio ? (rate ?? undefined) : undefined,
        denominatorCount: isRatio ? denCnt : undefined,
        numeratorCount: isRatio ? numCnt : (exec.count ?? numCnt ?? 0),
        resultType: isRatio ? 'ratio' : 'count',
        resultColumns: exec.preview_data?.columns
          ?? exec.preview_columns
          ?? (exec.result_data ? Object.keys(exec.result_data?.[0] ?? {}) : undefined),
        resultData: exec.preview_data?.rows ?? exec.preview_rows ?? exec.result_data,
        denominatorPreviewColumns: exec.denominator_preview_columns
          ?? exec.denominator_preview_data?.columns
          ?? (exec.denominator_preview_data?.rows?.length ? Object.keys(exec.denominator_preview_data.rows[0]) : undefined),
        denominatorPreviewData: exec.denominator_preview_data ?? { columns: exec.denominator_preview_columns ?? [], rows: exec.denominator_preview_rows ?? [] },
        usedScript: isRatio
          ? (exec.numerator_sql ? `【分子 SQL】\n${exec.numerator_sql}\n\n【分母 SQL】\n${exec.denominator_sql || '—'}` : (exec.sql || ''))
          : (exec.sql || exec.numerator_sql || ''),
        logs: [
          ...records.value[i].logs,
          ...(isRatio
            ? [
                { time: new Date().toLocaleTimeString('zh-CN'), level: 'info' as const, message: `分子 SQL 执行完成：${numCnt} 条记录。` },
                { time: new Date().toLocaleTimeString('zh-CN'), level: 'info' as const, message: `分母 SQL 执行完成：${denCnt} 条记录。` },
                { time: new Date().toLocaleTimeString('zh-CN'), level: 'info' as const, message: `执行完成。指标值：${rate ?? '—'}%（${numCnt}/${denCnt}）` },
              ]
            : [
                { time: new Date().toLocaleTimeString('zh-CN'), level: 'info' as const, message: `SQL 执行完成：${countVal} 条记录。` },
              ]),
        ],
      }
    }
    if (selectedRecord.value?.id === execId) {
      selectedRecord.value = records.value[i]
    }
  } catch (e: any) {
    const i = records.value.findIndex((r) => r.id === execId)
    if (i >= 0) {
      records.value[i] = {
        ...records.value[i],
        status: 'failed',
        errorMessage: e.message || String(e),
        logs: [
          ...records.value[i].logs,
          { time: new Date().toLocaleTimeString('zh-CN'), level: 'error', message: `请求失败：${e.message || e}` },
        ],
      }
    }
  } finally {
    executingIds.value.delete(execId)
  }
}
</script>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
