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
                class="h-9 min-h-9 w-[200px] cursor-pointer appearance-none rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 pr-8 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
                style="background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2224%22%20height%3D%2224%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2394a3b8%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M6%209l6%206%206-6%22%2F%3E%3C%2Fsvg%3E'); background-repeat: no-repeat; background-position: right 0.5rem center; background-size: 1em;"
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
            <label class="flex flex-col gap-1 text-[12px]" style="min-width: 200px;">
              <span class="text-[#596080]">指标名称</span>
              <SearchableSelect
                v-model="runIndicatorId"
                :options="currentIndicatorOptions"
                placeholder="全部"
                search-placeholder="搜索指标名称…"
              />
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
            <span class="rounded-full bg-emerald-600 px-1.5 py-0.5 text-[11px] font-medium text-white">{{ historyTotal }}</span>
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
                      <td class="px-3 py-2.5 text-[12px] text-[#596080]">{{ resolveScopeLabel(row.scope) }}</td>
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

              <!-- 加载更多 -->
              <div
                v-if="records.length < historyTotal"
                class="flex items-center justify-center border-t border-[#b8c9e8]/30 bg-white px-4 py-2.5"
              >
                <button
                  type="button"
                  class="flex items-center gap-1.5 rounded-[2px] border border-emerald-200 bg-emerald-50 px-4 py-1.5 text-[12px] text-emerald-700 transition-colors hover:bg-emerald-100 disabled:cursor-not-allowed disabled:opacity-50"
                  :disabled="loadingMore"
                  @click="loadMore"
                >
                  <template v-if="loadingMore">
                    <span class="h-3.5 w-3.5 animate-spin rounded-full border border-emerald-400 border-t-transparent" />
                    加载中...
                  </template>
                  <template v-else>
                    加载更多
                  </template>
                </button>
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
                  <td class="px-3 py-2.5 font-medium text-[#1F264D]">{{ resolveScopeLabel(h.hospitalCode) }}</td>
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
        <div class="flex min-h-0 flex-1 rounded-[2px] border border-[#b8c9e8]/40 bg-white">
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
                  <span>共 {{ effectiveNumTotal.toLocaleString() }} 条记录</span>
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
                  <span>共 {{ effectiveDenTotal.toLocaleString() }} 条记录</span>
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
import { computed, ref, reactive, onMounted, nextTick, watch } from 'vue'
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
import SearchableSelect from '@/components/ui/SearchableSelect.vue'
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
const historyTotal = ref(0)
const historyOpen = ref(false)
const loadingMore = ref(false)
const selectedRecord = ref<ExecutionRecord | null>(null)
const selectedDetailHospCode = ref<string>('')
const executingIds = ref<Set<string>>(new Set())
const detailContainer = ref<HTMLElement | null>(null)

// 状态筛选变化时，如果有搜索关键词则重新加载
watch(statusFilter, async () => {
  if (searchKeyword.value) {
    await loadRecords()
  }
})

const PAGE_SIZE = 200
const MAX_DISPLAY = 2000
const numPage = ref(1)
const denPage = ref(1)
const numTotal = ref(0)
const denTotal = ref(0)

// 切换记录时重置医院筛选和分页
watch(selectedRecord, () => {
  selectedDetailHospCode.value = ''
  numPage.value = 1
  denPage.value = 1
  numTotal.value = 0
  denTotal.value = 0
})

// 切换医院时重新加载分子分母数据
watch(selectedDetailHospCode, () => {
  const rec = selectedRecord.value
  if (!rec || !rec.hospitalResults?.length) return
  numPage.value = 1
  denPage.value = 1
  if (selectedDetailHospCode.value) {
    loadNumPage(1)
    loadDenPage(1)
  }
})

// 分页缓存（key = `${executionId}_${target}_${page}`）
const numRowsCache = reactive(new Map<string, Record<string, unknown>[]>())
const denRowsCache = reactive(new Map<string, Record<string, unknown>[]>())
const numRowsLoading = ref(false)
const denRowsLoading = ref(false)

async function loadNumPage(page: number, setCurrent=true) {
  const rec = selectedRecord.value
  if (!rec?.id) return
  if (rec.status === 'running' || rec.status === 'pending') return
  // 优先使用数据库记录ID（执行后返回），否则降级到前端临时ID
  const apiId: number | string = rec.dbRecordId ?? rec.id
  const cacheKey = `${rec.id}_numerator_${selectedDetailHospCode.value || 'all'}_${page}`
  if (numRowsCache.has(cacheKey)) {
    if(setCurrent) numPage.value = page
    return
  }
  numRowsLoading.value = true
  try {
    const res = await indicatorsApi.getPreviewPage({
      execution_id: apiId,
      target: 'numerator',
      page,
      page_size: PAGE_SIZE,
      hospital_code: selectedDetailHospCode.value || undefined,
    })
    if (res.ok && res.rows) {
      numRowsCache.set(cacheKey, res.rows)
      if(setCurrent) numPage.value = page
      if (res.total_count != null) numTotal.value = res.total_count
    } else {
      console.warn('loadNumPage failed:', res.error)
    }
  } catch (e) {
    console.error('loadNumPage error:', e)
  } finally {
    numRowsLoading.value = false
  }
}

async function loadDenPage(page: number, setCurrent=true) {
  const rec = selectedRecord.value
  if (!rec?.id) return
  if (rec.status === 'running' || rec.status === 'pending') return
  // 优先使用数据库记录ID（执行后返回），否则降级到前端临时ID
  const apiId: number | string = rec.dbRecordId ?? rec.id
  const cacheKey = `${rec.id}_denominator_${selectedDetailHospCode.value || 'all'}_${page}`
  if (denRowsCache.has(cacheKey)) {
    if(setCurrent) denPage.value = page
    return
  }
  denRowsLoading.value = true
  try {
    const res = await indicatorsApi.getPreviewPage({
      execution_id: apiId,
      target: 'denominator',
      page,
      page_size: PAGE_SIZE,
      hospital_code: selectedDetailHospCode.value || undefined,
    })
    if (res.ok && res.rows) {
      denRowsCache.set(cacheKey, res.rows)
      if(setCurrent) denPage.value = page
      if (res.total_count != null) denTotal.value = res.total_count
    } else {
      console.warn('loadDenPage failed:', res.error)
    }
  } catch (e) {
    console.error('loadDenPage error:', e)
  } finally {
    denRowsLoading.value = false
  }
}

const numTotalPages = computed(() => {
  const effectiveTotal = Math.min(effectiveNumTotal.value, MAX_DISPLAY)
  return Math.max(1, Math.ceil(effectiveTotal / PAGE_SIZE))
})

const denTotalPages = computed(() => {
  const effectiveTotal = Math.min(effectiveDenTotal.value, MAX_DISPLAY)
  return Math.max(1, Math.ceil(effectiveTotal / PAGE_SIZE))
})

const effectiveNumTotal = computed(() => {
  const rec = selectedRecord.value
  const hospCode = selectedDetailHospCode.value
  if (hospCode && rec?.hospitalResults?.length) {
    const h = rec.hospitalResults.find((x: any) => x.hospitalCode === hospCode)
    if (h?.numeratorCount != null) return h.numeratorCount
  }
  return numTotal.value || rec?.numeratorCount || 0
})

const effectiveDenTotal = computed(() => {
  const rec = selectedRecord.value
  const hospCode = selectedDetailHospCode.value
  if (hospCode && rec?.hospitalResults?.length) {
    const h = rec.hospitalResults.find((x: any) => x.hospitalCode === hospCode)
    if (h?.denominatorCount != null) return h.denominatorCount
  }
  return denTotal.value || rec?.denominatorCount || 0
})

const canPaginateByApi = computed(() => !!selectedRecord.value?.id)

const numHasReachedMax = computed(() => effectiveNumTotal.value > MAX_DISPLAY)
const denHasReachedMax = computed(() => effectiveDenTotal.value > MAX_DISPLAY)

// 详情区：按医院筛选

const detailHospOptions = computed(() => {
  if (!selectedRecord.value?.groupByHospital || !selectedRecord.value?.hospitalResults?.length) return []
  return selectedRecord.value.hospitalResults.map((h) => ({
    value: h.hospitalCode,
    label: resolveScopeLabel(h.hospitalCode) || h.hospitalName || h.hospitalCode,
  }))
})

const paginatedNumRows = computed(() => {
  const rec = selectedRecord.value
  if (!rec) return []
  const hospCode = selectedDetailHospCode.value
  const cacheKey = `${rec.id}_numerator_${hospCode || 'all'}_${numPage.value}`
  const cached = numRowsCache.get(cacheKey)
  if (cached) return cached
  // 有缓存则直接返回；无缓存时：
  // - 未选医院 → 回退到执行时返回的原始 preview 数据
  if (!hospCode && numPage.value === 1) {
    return rec.resultData ?? []
  }
  return []
})

const paginatedDenRows = computed(() => {
  const rec = selectedRecord.value
  if (!rec) return []
  const hospCode = selectedDetailHospCode.value
  const cacheKey = `${rec.id}_denominator_${hospCode || 'all'}_${denPage.value}`
  const cached = denRowsCache.get(cacheKey)
  if (cached) return cached
  // 有缓存则直接返回；无缓存时：
  // - 未选医院 → 回退到执行时返回的原始 preview 数据
  if (!hospCode && denPage.value === 1) {
    return rec.denominatorPreviewData?.rows ?? []
  }
  return []
})

const allIndicators = ref<Indicator[]>([])
const hospitalList = ref<{ value: string; label: string }[]>([])

// 医院选项（多选下拉框）
const hospitalOptions = computed(() => [
  { value: '__all__', label: '全省' },
  ...hospitalList.value.map((h) => ({ value: h.value, label: h.label })),
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

async function loadRecords(append = false) {
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
    if (append) {
      params.offset = records.value.length
      params.limit = 100
    } else {
      params.limit = 100
    }
    const res = await indicatorsApi.getExecutionHistory(params)
    const history = res.records || []
    historyTotal.value = res.total ?? history.length
    if (append) {
      records.value = [...records.value, ...history.map((exec: any) => mapExecToRecord(exec))]
    } else {
      records.value = history.map((exec: any) => mapExecToRecord(exec))
    }
  } catch (e) {
    console.error('加载执行记录失败:', e)
    if (!append) {
      records.value = JSON.parse(JSON.stringify(MOCK_RECORDS))
    }
  }
}

function mapExecToRecord(exec: any): ExecutionRecord {
  const ind = allIndicators.value.find((i: any) => i.id === exec.indicator)
  const rawCalcType = exec.indicator?.calc_type ?? ind?.calc_type ?? exec.result_type ?? 'ratio'
  const isCount = rawCalcType === 'count'
  const resultType: 'ratio' | 'count' = isCount ? 'count' : 'ratio'
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
  const resultDataLen = Array.isArray(resultData) ? resultData.length : 0
  const outputCount = isCount
    ? (exec.count ?? exec.numerator_count ?? resultDataLen)
    : (exec.numerator_count ?? exec.denominator_count ?? resultDataLen)
  const numeratorCount = isCount
    ? (exec.count ?? exec.numerator_count ?? resultDataLen)
    : (exec.numerator_count ?? undefined)
  const denominatorCount = isCount
    ? undefined
    : (exec.denominator_count ?? undefined)
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
    denominatorCount,
    numeratorCount,
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
}

async function handleSearch() {
  await loadRecords(false)
}

async function loadMore() {
  if (loadingMore.value) return
  if (records.value.length >= historyTotal.value) return
  loadingMore.value = true
  try {
    await loadRecords(true)
  } finally {
    loadingMore.value = false
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

function resolveScopeLabel(scope: string): string {
  if (!scope) return '全省'
  const codes = String(scope).split(',')
  console.log('[resolveScopeLabel] 原始 scope:', scope, '| 切割后 codes:', codes)
  console.log('[resolveScopeLabel] hospitalOptions:', hospitalOptions.value)
  const names = codes.map(code => {
    const cleanCode = String(code).trim()
    const found = hospitalOptions.value.find(o => String(o.value).trim() === cleanCode)
    console.log(`[resolveScopeLabel] 正在匹配 code="${cleanCode}" | found:`, found)
    return found ? found.label : cleanCode
  })
  return names.join(', ')
}

const currentIndicatorOptions = computed(() => {
  const filtered = allIndicators.value.filter((x: any) => x.indicator_type === runKind.value)
  if (filtered.length === 0) {
    return runKind.value === 'four'
      ? DEFAULT_FOUR_ELEMENTS.map((x) => ({ value: x.id, id: x.id, label: `序号 ${x.seq} — ${x.category}：${x.workContent.slice(0, 20)}...` }))
      : DEFAULT_CORE18.map((x) => ({ value: x.id, id: x.id, label: x.name }))
  }
  return filtered.map((x: any) => ({
    value: x.id,
    label: x.name,
    id: x.id,
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
      // 全省：展开所有医院列表；单选医院：传对应列表
      group_by_hospital: true,
    }
    reqData.hospital_codes = runScopes.value.includes('__all__')
      ? (hospitalList.value.length > 0
          ? hospitalList.value.filter(h => h.value !== '__all__').map(h => h.value)
          : null)  // 后端会走 _sql_runner_get_hospitals 展开全省
      : runScopes.value.filter(Boolean)
    // 存储完整医院列表用于重跑
    const finalHospitalCodes = runScopes.value.includes('__all__')
      ? hospitalList.value.filter(h => h.value !== '__all__').map(h => h.value)
      : runScopes.value.filter(Boolean)
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
    // 异步执行：提交任务 → 轮询状态 → 完成时拉取详情
    const taskRes = await indicatorsApi.executeIndicator(reqData)
    const realExecId = taskRes.execution_id ?? execId

    // 用真实数据库 ID 替换前端临时 ID（让轮询能查到记录）
    const idx = records.value.findIndex((r) => r.id === execId)
    if (idx >= 0) {
      records.value[idx].id = realExecId
      records.value[idx].dbRecordId = realExecId
    }
    const currentExecId = realExecId

    // 轮询任务状态
    const pollInterval = 2500 // ms
    const maxWait = 10 * 60 * 1000 // 10 分钟超时
    const startPoll = Date.now()

    function scheduleNextPoll() {
      setTimeout(async () => {
        // 如果记录已被删除或用户已切换，停止轮询
        if (!records.value.find(r => r.id === currentExecId)) return
        try {
          const status = await indicatorsApi.getTaskStatus(taskRes.task_id)
          if (status.state === 'SUCCESS' || status.state === 'FAILURE') {
            await fetchExecutionResult(currentExecId, status)
          } else if (Date.now() - startPoll < maxWait) {
            scheduleNextPoll()
          } else {
            applyResultToRecord(currentExecId, {
              status: 'failed',
              errorMessage: '执行超时（超过10分钟）',
            })
          }
        } catch (e: any) {
          // 网络抖动时继续重试
          if (Date.now() - startPoll < maxWait) {
            scheduleNextPoll()
          }
        }
      }, pollInterval)
    }
    scheduleNextPoll()
  } catch (e: any) {
    const idx = records.value.findIndex((r) => r.id === execId)
    if (idx >= 0) {
      records.value[idx] = {
        ...records.value[idx],
        status: 'failed',
        errorMessage: e.message || String(e),
        logs: [
          ...records.value[idx].logs,
          { time: new Date().toLocaleTimeString('zh-CN'), level: 'error' as const, message: `请求失败：${e.message || e}` },
        ],
      }
    }
    window.alert(`请求失败：${e.message || e}`)
  } finally {
    executingIds.value.delete(execId)
  }
}

// 任务完成后拉取完整结果并更新页面记录
async function fetchExecutionResult(execId: number | string, statusResp: { state: string; result: Record<string, unknown> | null; execution_id: number | null }) {
  try {
    const detail = await indicatorsApi.getExecutionDetail(Number(execId))
    const exec = detail as any
    if (exec.error && !exec.ok) {
      applyResultToRecord(execId, {
        status: 'failed',
        errorMessage: exec.error,
      })
      window.alert(`执行失败：${exec.error}`)
      return
    }
    const numCnt = exec.numerator_count ?? 0
    const denCnt = exec.denominator_count ?? 0
    const rate = exec.rate_percent
    const rawResultType = exec.result_type ?? exec.calc_type ?? exec.indicator?.result_type
    const isRatio = rawResultType !== 'count'
    const resultType: 'ratio' | 'count' = isRatio ? 'ratio' : 'count'
    const previewRows = exec.preview_data?.rows ?? exec.preview_rows ?? []
    const countVal = isRatio ? numCnt : (exec.count ?? (Array.isArray(previewRows) ? previewRows.length : 0))

    applyResultToRecord(execId, {
      status: 'success',
      duration: exec.duration_seconds || 0,
      outputCount: countVal,
      ratioPercent: isRatio ? (rate ?? undefined) : undefined,
      denominatorCount: isRatio ? denCnt : undefined,
      numeratorCount: isRatio ? numCnt : countVal,
      resultType,
      resultColumns: exec.preview_data?.columns ?? exec.preview_columns,
      resultData: exec.preview_data?.rows ?? exec.preview_rows,
      denominatorPreviewColumns: exec.denominator_preview_columns ?? exec.denominator_preview_data?.columns,
      denominatorPreviewData: exec.denominator_preview_data ?? { columns: exec.denominator_preview_columns ?? [], rows: exec.denominator_preview_rows ?? [] },
      usedScript: isRatio
        ? (exec.numerator_sql ? `【分子 SQL】\n${exec.numerator_sql}\n\n【分母 SQL】\n${exec.denominator_sql || '—'}` : (exec.sql || ''))
        : (exec.sql || exec.numerator_sql || ''),
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
    })

    window.alert(isRatio
      ? `执行成功！指标值：${rate ?? '—'}%`
      : `执行成功！共 ${countVal} 条记录。`)
  } catch (e: any) {
    applyResultToRecord(execId, {
      status: 'failed',
      errorMessage: `拉取结果失败：${e.message || e}`,
    })
  }
}

// 统一将结果应用到记录
function applyResultToRecord(execId: number | string, updates: Partial<typeof records.value[0]>) {
  const idx = records.value.findIndex((r) => r.id === execId)
  if (idx < 0) return
  const prev = records.value[idx]
  records.value[idx] = { ...prev, ...updates }
  if (selectedRecord.value?.id === execId) {
    selectedRecord.value = records.value[idx]
  }
}

function selectRecord(row: ExecutionRecord) {
  numPage.value = 1
  denPage.value = 1
  numTotal.value = row.numeratorCount ?? 0
  denTotal.value = row.denominatorCount ?? 0
  selectedRecord.value = row
  historyOpen.value = false
  nextTick(() => {
    detailContainer.value?.scrollTo({ top: 0, behavior: 'smooth' })
  })
  // 预填第1页缓存（执行时已返回）
  const hasNum = row.resultData?.length
  const hasDen = row.denominatorPreviewData?.rows?.length
  if (row.id && !isNaN(Number(row.id))) {
    const numKey = `${row.id}_numerator_all_1`
    const denKey = `${row.id}_denominator_all_1`
    if (hasNum) numRowsCache.set(numKey, (row.resultData ?? []).slice(0, PAGE_SIZE))
    if (hasDen) denRowsCache.set(denKey, (row.denominatorPreviewData?.rows ?? []).slice(0, PAGE_SIZE))
    // 预加载第2页（仅当记录已持久化且数据量超过一页时）
    if (!executingIds.value.has(String(row.id))) {
      if (hasNum && (row.numeratorCount ?? 0) > PAGE_SIZE) {
        loadNumPage(2, false)
      }
      if (hasDen && (row.denominatorCount ?? 0) > PAGE_SIZE) {
        loadDenPage(2, false)
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
  historyTotal.value += 1
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
    // 异步重跑：提交任务 → 轮询 → 拉取结果
    const taskRes = await indicatorsApi.executeIndicator({
      business_type: copy.kind,
      indicator_id: Number(copy.indicatorId) || undefined,
      kind: copy.kind,
      run_mode: copy.runMode,
      time_range: copy.timeRange,
      result_type: copy.resultType,
      calc_method: copy.calcMethod,
      scope: copy.scope || '',
      hospital_codes: copy.hospitalCodes && copy.hospitalCodes.length > 0
        ? copy.hospitalCodes.filter(Boolean)
        : (copy.scope ? [copy.scope] : []),
      group_by_hospital: true,
      time_mode: timeMode,
      time_value: timeValue,
    })
    const realExecId = taskRes.execution_id ?? execId
    const copyIdx = records.value.findIndex((r) => r.id === execId)
    if (copyIdx >= 0) {
      records.value[copyIdx].id = realExecId
      records.value[copyIdx].dbRecordId = realExecId
    }

    const pollRerun = () => setTimeout(async () => {
      if (!records.value.find(r => r.id === realExecId)) return
      try {
        const status = await indicatorsApi.getTaskStatus(taskRes.task_id)
        if (status.state === 'SUCCESS' || status.state === 'FAILURE') {
          await fetchExecutionResult(realExecId, status)
        } else {
          pollRerun()
        }
      } catch {
        pollRerun()
      }
    }, 2500)
    pollRerun()
  } catch (e: any) {
    const i = records.value.findIndex((r) => r.id === execId)
    if (i >= 0) {
      records.value[i] = {
        ...records.value[i],
        status: 'failed',
        errorMessage: e.message || String(e),
        logs: [
          ...records.value[i].logs,
          { time: new Date().toLocaleTimeString('zh-CN'), level: 'error' as const, message: `请求失败：${e.message || e}` },
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
