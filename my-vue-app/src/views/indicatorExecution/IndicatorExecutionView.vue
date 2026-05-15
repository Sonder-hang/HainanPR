<template>
  <div class="flex h-full min-h-0 flex-col bg-white">
    <!-- 执行发起区 -->
    <div class="shrink-0 border-b border-emerald-100 p-5">
      <h3 class="mb-4 flex items-center text-[13px] font-semibold text-[#1F264D]">
        <Zap class="mr-2 h-4 w-4 text-emerald-500" />
        指标执行
      </h3>
      <div class="flex flex-wrap items-end gap-3">
        <!-- 指标类型 -->
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
          <select
            v-model="runScope"
            class="cursor-pointer rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
          >
            <option value="">全省</option>
            <option value="hospital_a">医院 A</option>
            <option value="hospital_b">医院 B</option>
            <option value="hospital_c">医院 C</option>
          </select>
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

        <!-- 执行频率 -->
        <label class="flex flex-col gap-1 text-[12px]">
          <span class="text-[#596080]">执行频率</span>
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

        <!-- 时间范围（按月 / 按季度时显示） -->
        <label v-if="runMode !== 'immediate'" class="flex flex-col gap-1 text-[12px]">
          <span class="text-[#596080]">{{ runMode === 'monthly' ? '执行月份' : '执行季度' }}</span>
          <input
            v-if="runMode === 'monthly'"
            v-model="runTimeRange"
            type="month"
            class="rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
          />
          <select
            v-else
            v-model="runTimeRange"
            class="cursor-pointer rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
          >
            <option value="2025-Q4">2025年 Q4</option>
            <option value="2025-Q3">2025年 Q3</option>
            <option value="2025-Q2">2025年 Q2</option>
            <option value="2025-Q1">2025年 Q1</option>
          </select>
        </label>

        <!-- 执行按钮 -->
        <button
          type="button"
          class="flex items-center gap-1.5 rounded-[2px] bg-emerald-600 px-5 py-2 text-[12px] text-white transition-colors hover:bg-emerald-700"
          @click="handleRun"
        >
          <PlayCircle class="h-4 w-4" />
          {{ runMode === 'immediate' ? '立即执行' : '发起执行' }}
        </button>
      </div>
    </div>

    <!-- 执行历史列表 -->
    <div class="flex min-h-0 flex-1 flex-col overflow-hidden px-5 pb-5 pt-4">
      <div class="mb-3 flex items-center justify-between">
        <h3 class="flex items-center text-[13px] font-semibold text-[#1F264D]">
          <Clock class="mr-2 h-4 w-4 text-[#596080]" />
          执行记录
          <span class="ml-2 rounded-full bg-emerald-50 px-2 py-0.5 text-[11px] text-emerald-600">{{ records.length }}</span>
        </h3>
        <div class="flex items-center gap-2">
          <!-- 状态筛选 -->
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
      </div>

      <div class="min-h-0 flex-1 overflow-hidden rounded-[2px] border border-[#b8c9e8]/60 bg-white shadow-sm">
        <div class="h-full min-h-0 overflow-auto">
          <table class="w-full min-w-[880px] border-collapse text-left">
            <thead class="sticky top-0 z-10 border-b border-emerald-100 bg-emerald-50/95 backdrop-blur-sm">
              <tr>
                <th class="px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">指标名称</th>
                <th class="w-24 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">执行范围</th>
                <th class="w-28 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">类别</th>
                <th class="w-24 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">频率</th>
                <th class="w-24 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">时间范围</th>
                <th class="w-24 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">状态</th>
                <th class="w-24 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">耗时</th>
                <th class="w-32 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">产出结果</th>
                <th class="w-48 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">开始时间</th>
                <th class="w-20 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#b8c9e8]/30">
              <tr
                v-for="row in filteredRecords"
                :key="row.id"
                class="transition-colors hover:bg-emerald-50/30"
              >
                <td class="max-w-[240px] px-3 py-2.5 text-[12px] font-medium text-[#1F264D]">
                  <span class="line-clamp-1" :title="row.indicatorName">{{ row.indicatorName }}</span>
                </td>
                <td class="w-24 px-3 py-2.5 text-[12px] text-[#596080]">{{ row.scope || '全省' }}</td>
                <td class="w-28 px-3 py-2.5 text-[12px]">
                  <span
                    class="inline-block rounded border px-1.5 py-0.5 text-[11px] font-medium"
                    :class="row.kind === 'four' ? 'border-blue-200 bg-blue-50 text-blue-600' : 'border-purple-200 bg-purple-50 text-purple-600'"
                  >
                    {{ row.kind === 'four' ? '四要素' : '十八项' }}
                  </span>
                </td>
                <td class="w-24 px-3 py-2.5 text-[12px] text-[#596080]">{{ RUN_MODE_MAP[row.runMode] }}</td>
                <td class="w-24 px-3 py-2.5 text-[12px] text-[#596080]">{{ row.timeRange }}</td>
                <td class="w-24 px-3 py-2.5">
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
                <td class="w-24 px-3 py-2.5 text-[12px]" :class="row.status === 'failed' ? 'text-red-500' : 'text-[#596080]'">
                  <span v-if="row.duration > 0">{{ row.duration }}s</span>
                  <span v-else class="text-[#B8BCCC]">—</span>
                </td>
                <td class="w-32 px-3 py-2.5 text-[12px]">
                  <!-- 比值型：显示比率 + 分子/分母 -->
                  <template v-if="row.resultType === 'ratio' && row.outputCount > 0">
                    <div class="font-medium text-emerald-600">{{ row.ratioPercent != null ? row.ratioPercent.toFixed(2) + '%' : '—' }}</div>
                    <div class="text-[10px] text-[#B8BCCC]">{{ row.outputCount.toLocaleString() }} 条 / {{ row.denominatorCount?.toLocaleString() ?? '—' }} 条</div>
                  </template>
                  <!-- 计数型：显示条数 -->
                  <span v-else-if="row.outputCount > 0" class="font-medium text-emerald-600">{{ row.outputCount.toLocaleString() }} 条</span>
                  <span v-else class="text-[#B8BCCC]">—</span>
                </td>
                <td class="w-48 whitespace-nowrap px-3 py-2.5 text-[12px] text-[#596080]">{{ row.startTime }}</td>
                <td class="w-20 px-3 py-2.5">
                  <div class="flex items-center gap-2">
                    <button
                      type="button"
                      class="text-[11px] text-emerald-600 hover:text-emerald-800"
                      @click="openDetail(row)"
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
                <td colspan="9" class="py-12 text-center text-[13px] text-[#B8BCCC]">暂无执行记录</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 详情抽屉 -->
    <Transition name="drawer-slide">
      <div
        v-if="detailRecord"
        class="fixed inset-0 z-50 flex justify-end bg-gray-900/50 backdrop-blur-sm"
        @click.self="detailRecord = null"
      >
        <div class="flex h-full w-[min(640px,100vw)] flex-col border-l border-emerald-100 bg-white shadow-2xl">
          <!-- 抽屉头部 -->
          <div class="flex items-center justify-between border-b border-emerald-100 bg-emerald-50 px-5 py-3.5">
            <h2 class="flex items-center text-[14px] font-bold text-[#1F264D]">
              <Activity class="mr-2 h-4 w-4 text-emerald-500" />
              执行详情
            </h2>
            <button
              type="button"
              class="rounded-full p-1.5 text-[#596080] transition-colors hover:bg-emerald-100"
              @click="detailRecord = null"
            >
              <X class="h-4 w-4" />
            </button>
          </div>

          <!-- 概览卡片 -->
          <div class="shrink-0 border-b border-[#b8c9e8]/30 bg-[#f8faff] p-4">
            <div class="mb-2 text-[13px] font-semibold text-[#1F264D]">{{ detailRecord.indicatorName }}</div>
            <div class="grid grid-cols-4 gap-3 text-[12px]">
              <div class="rounded-[2px] bg-white p-2 text-center border border-[#b8c9e8]/40">
                <div class="text-[11px] text-[#596080]">状态</div>
                <div
                  class="mt-0.5 font-semibold"
                  :class="
                    detailRecord.status === 'success'
                      ? 'text-emerald-600'
                      : detailRecord.status === 'failed'
                        ? 'text-red-500'
                        : detailRecord.status === 'pending'
                          ? 'text-amber-700'
                          : 'text-blue-600'
                  "
                >
                  {{
                    detailRecord.status === 'pending'
                      ? '等待中'
                      : detailRecord.status === 'running'
                        ? '运行中'
                        : detailRecord.status === 'success'
                          ? '完成'
                          : detailRecord.status === 'failed'
                            ? '失败'
                            : '待执行'
                  }}
                </div>
              </div>
              <div class="rounded-[2px] bg-white p-2 text-center border border-[#b8c9e8]/40">
                <div class="text-[11px] text-[#596080]">耗时</div>
                <div class="mt-0.5 font-semibold text-[#1F264D]">{{ detailRecord.duration > 0 ? `${detailRecord.duration}s` : '—' }}</div>
              </div>
              <div class="rounded-[2px] bg-white p-2 text-center border border-[#b8c9e8]/40">
                <div class="text-[11px] text-[#596080]">产出条数</div>
                <div class="mt-0.5 font-semibold text-emerald-600">{{ detailRecord.outputCount > 0 ? detailRecord.outputCount.toLocaleString() : '—' }}</div>
              </div>
              <div class="rounded-[2px] bg-white p-2 text-center border border-[#b8c9e8]/40">
                <div class="text-[11px] text-[#596080]">结果类型</div>
                <div class="mt-0.5 font-semibold" :class="detailRecord.resultType === 'ratio' ? 'text-emerald-600' : 'text-blue-600'">
                  {{ detailRecord.resultType === 'ratio' ? '比值型' : '计数型' }}
                </div>
              </div>
            </div>
          </div>

          <!-- 详情内容 -->
          <div class="min-h-0 flex-1 space-y-4 overflow-y-auto p-5">
          <!-- 分子结果 -->
          <div>
            <h4 class="mb-2 flex items-center text-[12px] font-semibold text-[#1F264D]">
              <Code2 class="mr-1.5 h-3.5 w-3.5 text-[#596080]" />
              分子预览数据
            </h4>

            <div v-if="detailRecord.resultData && detailRecord.resultData.length > 0"
              class="rounded-[2px] border border-[#b8c9e8]/60 overflow-hidden">
              <div class="max-h-64 overflow-auto">
                <table class="w-full min-w-[500px] border-collapse text-left text-[11px]">
                  <thead class="sticky top-0 z-10 border-b border-[#b8c9e8]/60 bg-[#f0f4ff]">
                    <tr>
                      <th
                        v-for="col in detailRecord.resultColumns"
                        :key="col"
                        class="px-3 py-2 font-semibold text-[#596080]"
                      >{{ col }}</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-[#b8c9e8]/30">
                    <tr
                      v-for="(row, rIdx) in paginatedNumRows"
                      :key="rIdx"
                      class="hover:bg-emerald-50/30"
                    >
                      <td
                        v-for="col in detailRecord.resultColumns"
                        :key="col"
                        class="max-w-[200px] truncate px-3 py-2 text-[#334155]"
                        :title="String(row[col] ?? '—')"
                      >{{ row[col] ?? '—' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div class="border-t border-[#b8c9e8]/60 bg-[#f8faff] px-3 py-1.5 text-[11px] text-[#596080] flex items-center justify-between gap-2">
                <span>共 {{ detailRecord.numeratorCount?.toLocaleString() ?? '—' }} 条记录（分子全量），当前页预览 50 条</span>
                <div class="flex items-center gap-1">
                  <button
                    class="shrink-0 rounded px-1.5 py-0.5 transition-colors"
                    :class="numPage <= 1 ? 'cursor-not-allowed text-gray-300' : 'cursor-pointer text-[#596080] hover:bg-[#d0daeb]/40'"
                    :disabled="numPage <= 1"
                    @click="numPage = Math.max(1, numPage - 1)"
                  >&lt;</button>
                  <span class="min-w-[60px] text-center">{{ numPage }} / {{ numTotalPages }}</span>
                  <button
                    class="shrink-0 rounded px-1.5 py-0.5 transition-colors"
                    :class="numPage >= numTotalPages ? 'cursor-not-allowed text-gray-300' : 'cursor-pointer text-[#596080] hover:bg-[#d0daeb]/40'"
                    :disabled="numPage >= numTotalPages"
                    @click="numPage = Math.min(numTotalPages, numPage + 1)"
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
          <div v-if="detailRecord.resultType === 'ratio' && detailRecord.denominatorPreviewData?.rows?.length > 0">
            <h4 class="mb-2 flex items-center text-[12px] font-semibold text-[#1F264D]">
              <Code2 class="mr-1.5 h-3.5 w-3.5 text-[#596080]" />
              分母预览数据
            </h4>

            <div class="rounded-[2px] border border-[#b8c9e8]/60 overflow-hidden">
              <div class="max-h-64 overflow-auto">
                <table class="w-full min-w-[500px] border-collapse text-left text-[11px]">
                  <thead class="sticky top-0 z-10 border-b border-[#b8c9e8]/60 bg-[#f0f4ff]">
                    <tr>
                      <th
                        v-for="col in detailRecord.denominatorPreviewColumns"
                        :key="col"
                        class="px-3 py-2 font-semibold text-[#596080]"
                      >{{ col }}</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-[#b8c9e8]/30">
                    <tr
                      v-for="(row, rIdx) in paginatedDenRows"
                      :key="rIdx"
                      class="hover:bg-blue-50/30"
                    >
                      <td
                        v-for="col in detailRecord.denominatorPreviewColumns"
                        :key="col"
                        class="max-w-[200px] truncate px-3 py-2 text-[#334155]"
                        :title="String(row[col] ?? '—')"
                      >{{ row[col] ?? '—' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div class="border-t border-[#b8c9e8]/60 bg-[#f8faff] px-3 py-1.5 text-[11px] text-[#596080] flex items-center justify-between gap-2">
                <span>共 {{ detailRecord.denominatorCount?.toLocaleString() ?? '—' }} 条记录（分母全量），当前页预览 50 条</span>
                <div class="flex items-center gap-1">
                  <button
                    class="shrink-0 rounded px-1.5 py-0.5 transition-colors"
                    :class="denPage <= 1 ? 'cursor-not-allowed text-gray-300' : 'cursor-pointer text-[#596080] hover:bg-[#d0daeb]/40'"
                    :disabled="denPage <= 1"
                    @click="denPage = Math.max(1, denPage - 1)"
                  >&lt;</button>
                  <span class="min-w-[60px] text-center">{{ denPage }} / {{ denTotalPages }}</span>
                  <button
                    class="shrink-0 rounded px-1.5 py-0.5 transition-colors"
                    :class="denPage >= denTotalPages ? 'cursor-not-allowed text-gray-300' : 'cursor-pointer text-[#596080] hover:bg-[#d0daeb]/40'"
                    :disabled="denPage >= denTotalPages"
                    @click="denPage = Math.min(denTotalPages, denPage + 1)"
                  >&gt;</button>
                </div>
              </div>
            </div>
          </div>


            <!-- 执行日志 -->
            <div>
              <h4 class="mb-2 flex items-center text-[12px] font-semibold text-[#1F264D]">
                <ScrollText class="mr-1.5 h-3.5 w-3.5 text-[#596080]" />
                执行日志
              </h4>
              <div class="rounded-[2px] border border-[#b8c9e8]/60 bg-[#1a1f2e] p-3 font-mono text-[11px]">
                <div
                  v-for="(log, idx) in detailRecord.logs"
                  :key="idx"
                  class="flex gap-3 leading-7"
                >
                  <span class="shrink-0 text-[#4b6080]">{{ log.time }}</span>
                  <span
                    class="shrink-0 w-12 text-right"
                    :class="{
                      'text-emerald-400': log.level === 'info',
                      'text-amber-400': log.level === 'warn',
                      'text-red-400': log.level === 'error',
                    }"
                  >{{ log.level === 'info' ? '[INFO]' : log.level === 'warn' ? '[WARN]' : '[ERR!]' }}</span>
                  <span
                    :class="{
                      'text-[#d1d5db]': log.level === 'info',
                      'text-amber-300': log.level === 'warn',
                      'text-red-300': log.level === 'error',
                    }"
                  >{{ log.message }}</span>
                </div>
              </div>
            </div>

            <!-- 错误信息 -->
            <div v-if="detailRecord.errorMessage">
              <h4 class="mb-2 flex items-center text-[12px] font-semibold text-red-500">
                <AlertCircle class="mr-1.5 h-3.5 w-3.5" />
                错误信息
              </h4>
              <div class="rounded-[2px] border border-red-200 bg-red-50 p-3 text-[12px] text-red-700">{{ detailRecord.errorMessage }}</div>
            </div>
          </div>

          <!-- 底部操作 -->
          <div class="shrink-0 flex justify-end gap-2 border-t border-emerald-100 bg-white px-5 py-3">
            <button
              type="button"
              class="rounded-[2px] border border-[#b8c9e8]/60 px-4 py-2 text-[12px] text-[#596080] hover:bg-slate-50"
              @click="detailRecord = null"
            >关闭</button>
            <button
              type="button"
              class="flex items-center gap-1.5 rounded-[2px] bg-emerald-600 px-4 py-2 text-[12px] text-white hover:bg-emerald-700"
              @click="rerun(detailRecord)"
            >
              <RotateCcw class="h-3.5 w-3.5" />
              重新执行
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import {
  Activity,
  AlertCircle,
  CheckCircle2,
  Clock,
  Code2,
  PlayCircle,
  RotateCcw,
  X,
  XCircle,
  Zap,
} from 'lucide-vue-next'
import { indicatorsApi, type Indicator } from '@/api/indicators'
import { DEFAULT_CORE18 } from '@/data/indicatorManagementDefaults'
import { MOCK_RECORDS, type ExecutionRecord, type RunMode, type RunStatus } from '@/data/indicatorExecutionDefaults'

const RUN_MODE_OPTIONS: { value: RunMode; label: string }[] = [
  { value: 'immediate', label: '立即执行' },
  { value: 'monthly', label: '按月执行' },
  { value: 'quarterly', label: '按季度执行' },
]

const RUN_MODE_MAP: Record<RunMode, string> = {
  immediate: '立即执行',
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
const runScope = ref('')
const runIndicatorId = ref('')
const runMode = ref<RunMode>('immediate')
const runTimeRange = ref('')
const statusFilter = ref('all')
const records = ref<ExecutionRecord[]>([])
const detailRecord = ref<ExecutionRecord | null>(null)
const executingIds = ref<Set<string>>(new Set())

// 详情抽屉表格分页
const PAGE_SIZE = 50
const numPage = ref(1)
const denPage = ref(1)

// 真实指标列表
const allIndicators = ref<Indicator[]>([])

onMounted(async () => {
  await loadRecords()
  await loadIndicators()
})

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
    const history = await indicatorsApi.getExecutionHistory()
    if (history && history.length > 0) {
      records.value = history.map((exec: any) => {
        const ind = allIndicators.value.find((i: any) => i.id === exec.indicator)
        const rawCalcType = exec.indicator?.calc_type ?? ind?.calc_type ?? exec.result_type ?? 'ratio'
        const isCount = rawCalcType === 'count'
        const resultType: 'ratio' | 'count' = isCount ? 'count' : 'ratio'
        const outputCount = isCount
          ? (exec.count ?? exec.numerator_count ?? 0)
          : (exec.numerator_count ?? exec.denominator_count ?? 0)
        const resultColumns = exec.preview_data?.columns
          ?? exec.preview_columns
          ?? (exec.result_data ? Object.keys(exec.result_data?.[0] ?? {}) : undefined)
        const resultData = exec.preview_data?.rows ?? exec.preview_rows ?? exec.result_data
        // 分母预览数据
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
          outputCount,
          ratioPercent: isCount ? undefined : (exec.rate_percent ?? undefined),
          denominatorCount: isCount ? undefined : (exec.denominator_count ?? undefined),
          numeratorCount: isCount ? undefined : (exec.numerator_count ?? undefined),
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
  }))
})

const filteredRecords = computed(() => {
  if (statusFilter.value === 'all') return records.value
  return records.value.filter((r) => r.status === statusFilter.value)
})

async function handleRun() {
  const selectedInd = currentIndicatorOptions.value.find((x: any) => x.id == runIndicatorId.value)
  const scheduled = runMode.value !== 'immediate'
  const initialStatus: RunStatus = scheduled ? 'pending' : 'running'
  const rangeLabel = runTimeRange.value || '全量'
  const execId = `exec-${Date.now()}`
  const newRecord: ExecutionRecord = {
    id: execId,
    kind: runKind.value,
    indicatorName: selectedInd?.label ?? '全部指标',
    indicatorId: runIndicatorId.value,
    runMode: runMode.value,
    timeRange: rangeLabel,
    status: initialStatus,
    startTime: scheduled ? '—' : new Date().toLocaleString('zh-CN'),
    duration: 0,
    outputCount: 0,
    calcMethod: 'SQL录入',
    resultType: (selectedInd?.calc_type as 'ratio' | 'count') || 'ratio',
    usedScript: scheduled
      ? '-- 已排程，到达计划时间后自动执行。\nSELECT * FROM ...;'
      : selectedInd?.resultType === 'count'
        ? (selectedInd?.sql || selectedInd?.numerator_sql || selectedInd?.denominator_sql || '-- 正在执行，请稍候...')
        : selectedInd?.numerator_sql
          ? `【分子 SQL】\n${selectedInd.numerator_sql}\n\n【分母 SQL】\n${selectedInd.denominator_sql || '—'}`
          : selectedInd?.sql || '-- 正在执行，请稍候...\nSELECT * FROM ...;',
    logs: scheduled
      ? [{ time: new Date().toLocaleTimeString('zh-CN'), level: 'info' as const, message: `任务已排程，状态：等待中。统计周期：${rangeLabel}，将在计划时间点由调度自动启动。` }]
      : buildLogs({}, selectedInd?.calc_type === 'count'),
  }
  records.value = [newRecord, ...records.value]

  if (scheduled) {
    window.alert('定时任务已记录，排程功能开发中')
    return
  }

  // 真实执行
  if (!runIndicatorId.value) {
    window.alert('请先选择要执行的指标')
    return
  }
  executingIds.value.add(execId)
  try {
    const result = await indicatorsApi.executeIndicator({
      business_type: runKind.value,
      indicator_id: Number(runIndicatorId.value),
      kind: runKind.value,
      run_mode: runMode.value,
      time_range: rangeLabel,
      result_type: (selectedInd?.calc_type as 'ratio' | 'count') || 'ratio',
      calc_method: 'SQL录入',
      scope: runScope.value,
    })
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
      records.value[idx] = {
        ...records.value[idx],
        status: 'success',
        duration: exec.duration_seconds || 0,
        outputCount: countVal,
        ratioPercent: isRatio ? (rate ?? undefined) : undefined,
        denominatorCount: isRatio ? denCnt : undefined,
        numeratorCount: isRatio ? numCnt : undefined,
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
      }
      window.alert(isRatio
        ? `执行成功！指标值：${rate ?? '—'}%`
        : `执行成功！共 ${countVal} 条记录。`)
    }
    if (detailRecord.value?.id === execId) {
      detailRecord.value = records.value[idx]
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

function openDetail(row: ExecutionRecord) {
  numPage.value = 1
  denPage.value = 1
  detailRecord.value = row
}

// 分子分页数据
const paginatedNumRows = computed(() => {
  if (!detailRecord.value?.resultData) return []
  const all = detailRecord.value.resultData
  const total = all.length
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))
  const p = Math.min(numPage.value, totalPages)
  return all.slice((p - 1) * PAGE_SIZE, p * PAGE_SIZE)
})
const numTotalPages = computed(() =>
  detailRecord.value?.resultData
    ? Math.max(1, Math.ceil(detailRecord.value.resultData.length / PAGE_SIZE))
    : 1
)

// 分母分页数据
const paginatedDenRows = computed(() => {
  const rows = detailRecord.value?.denominatorPreviewData?.rows ?? []
  const total = rows.length
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))
  const p = Math.min(denPage.value, totalPages)
  return rows.slice((p - 1) * PAGE_SIZE, p * PAGE_SIZE)
})
const denTotalPages = computed(() =>
  detailRecord.value?.denominatorPreviewData?.rows
    ? Math.max(1, Math.ceil(detailRecord.value.denominatorPreviewData.rows.length / PAGE_SIZE))
    : 1
)

async function deleteRecord(row: ExecutionRecord) {
  if (!window.confirm(`确定删除执行记录「${row.indicatorName}」吗？`)) return
  try {
    await indicatorsApi.deleteExecution(Number(row.id))
    records.value = records.value.filter((r) => r.id !== row.id)
    if (detailRecord.value?.id === row.id) {
      detailRecord.value = null
    }
  } catch (e) {
    window.alert(`删除失败：${e}`)
  }
}

async function rerun(row: ExecutionRecord) {
  const idx = records.value.findIndex((r) => r.id === row.id)
  if (idx < 0) return
  const scheduled = row.runMode !== 'immediate'
  const execId = `exec-${Date.now()}`
  const copy: ExecutionRecord = {
    ...JSON.parse(JSON.stringify(row)),
    id: execId,
    status: scheduled ? 'pending' : 'running',
    startTime: scheduled ? '—' : new Date().toLocaleString('zh-CN'),
    duration: 0,
    outputCount: 0,
    ratioPercent: undefined,
    denominatorCount: undefined,
    numeratorCount: undefined,
    resultColumns: undefined,
    resultData: undefined,
    logs: scheduled
      ? [
          { time: new Date().toLocaleTimeString('zh-CN'), level: 'info' as const, message: `重新排程，等待中。统计周期：${row.timeRange}。` },
        ]
      : [{ time: new Date().toLocaleTimeString('zh-CN'), level: 'info' as const, message: '任务已重新提交...' }],
  }
  records.value = [copy, ...records.value]
  detailRecord.value = copy

  if (scheduled) {
    window.alert('定时任务已记录，排程功能开发中')
    return
  }

  executingIds.value.add(execId)
  try {
    const result = await indicatorsApi.executeIndicator({
      business_type: copy.kind,
      indicator_id: Number(copy.indicatorId) || undefined,
      kind: copy.kind,
      run_mode: copy.runMode,
      time_range: copy.timeRange,
      result_type: copy.resultType,
      calc_method: copy.calcMethod,
      scope: copy.scope || '',
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
        numeratorCount: isRatio ? numCnt : undefined,
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
    if (detailRecord.value?.id === execId) {
      detailRecord.value = records.value[i]
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
.drawer-slide-enter-active,
.drawer-slide-leave-active {
  transition: opacity 0.2s ease;
}
.drawer-slide-enter-active > :last-child,
.drawer-slide-leave-active > :last-child {
  transition: transform 0.25s ease;
}
.drawer-slide-enter-from,
.drawer-slide-leave-to {
  opacity: 0;
}
.drawer-slide-enter-from > :last-child,
.drawer-slide-leave-to > :last-child {
  transform: translateX(100%);
}
</style>
