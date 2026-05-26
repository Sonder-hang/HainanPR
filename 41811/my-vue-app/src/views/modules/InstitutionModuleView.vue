<template>
  <div class="h-full flex flex-col bg-white">
    <!-- 二级Tab栏 -->
    <div class="bg-[#e8eef9] px-5 pt-3 border-b border-[#b8c9e8]/60 shrink-0">
      <div class="flex space-x-5 overflow-x-auto">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="pb-2.5 text-[13px] font-medium whitespace-nowrap transition-colors border-b-2"
          :class="activeTab === tab.id ? 'border-[#0A6EFD] text-[#0A6EFD]' : 'border-transparent text-[#596080] hover:text-[#1F264D]'"
        >
          {{ tab.name }}
        </button>
      </div>
    </div>

    <!-- 分类总览视图 -->
    <div v-if="activeTab === 'overview'" class="flex-1 p-5 overflow-y-auto animate-fade-in">
      <h2 class="text-[14px] font-bold text-[#1F264D] mb-4 flex items-center">
        <Activity class="w-4 h-4 mr-2 text-[#0A6EFD]" />
        机构要素 — 监管规则总览
        <span class="ml-auto flex items-center gap-2">
          <!-- 时间筛选 -->
          <div class="flex items-center gap-1 border border-[#b8c9e8]/60 rounded-[2px] px-2 bg-white text-[12px] h-[34px]">
            <button
              v-for="mode in TIME_MODE_OPTIONS"
              :key="mode.value"
              type="button"
              class="rounded px-2 text-[11px] transition-colors leading-[22px]"
              :class="timeMode === mode.value
                ? 'bg-[#0A6EFD] text-white font-medium'
                : 'text-[#596080] hover:bg-[#e8eef9]'"
              @click="timeMode = mode.value; hospitalVersion++"
            >{{ mode.label }}</button>
            <template v-if="timeMode === 'monthly'">
              <select
                v-model="selectedMonthYear"
                class="border-none bg-transparent text-[11px] text-[#1F264D] focus:outline-none cursor-pointer"
              >
                <option v-for="y in monthYearOptions" :key="y" :value="y">{{ y }}</option>
              </select>
              <span class="text-[#596080]">年</span>
              <select
                v-model="selectedMonthNum"
                class="border-none bg-transparent text-[11px] text-[#1F264D] focus:outline-none cursor-pointer"
              >
                <option v-for="m in MONTH_OPTIONS" :key="m.value" :value="m.value">{{ m.label }}</option>
              </select>
            </template>
            <template v-else-if="timeMode === 'quarterly'">
              <select
                v-model="selectedQuarterYear"
                class="border-none bg-transparent text-[11px] text-[#1F264D] focus:outline-none cursor-pointer"
              >
                <option v-for="y in quarterYearOptions" :key="y" :value="y">{{ y }}</option>
              </select>
              <span class="text-[#596080]">年</span>
              <select
                v-model="selectedQuarterNum"
                class="border-none bg-transparent text-[11px] text-[#1F264D] focus:outline-none cursor-pointer"
              >
                <option v-for="q in QUARTER_OPTIONS" :key="q.value" :value="q.value">{{ q.label }}</option>
              </select>
            </template>
          </div>
        </span>
      </h2>
      <div class="mb-5 bg-blue-50 border border-blue-200 rounded-[2px] p-3.5 text-[13px] text-blue-800">
        <p class="font-medium mb-0.5 text-[13px]">规则说明</p>
        <p class="text-blue-600 text-[12px]">机构要素审核范围：住院。对医疗机构诊疗科目、收治能力、业务量等进行智能监测与预警。</p>
      </div>
      <div class="grid grid-cols-3 gap-4">
        <div
          v-for="rule in rules"
          :key="rule.id"
          @click="activeTab = rule.id"
          class="bg-white rounded-[2px] p-4 border border-[#b8c9e8]/60 shadow-sm hover:shadow-md hover:border-[#0A6EFD]/50 transition-all cursor-pointer group flex flex-col"
        >
          <div class="flex justify-between items-start mb-2.5">
            <div :class="[
              'p-1.5 rounded-[2px]',
              rule.mode === 'alert' ? 'bg-red-50 text-red-500' : 'bg-emerald-50 text-emerald-500'
            ]">
              <ShieldAlert v-if="rule.mode === 'alert'" class="w-4 h-4" />
              <Activity v-else class="w-4 h-4" />
            </div>
          </div>
          <h3 class="font-bold text-[#1F264D] text-[13px] mb-1.5 group-hover:text-[#0A6EFD] transition-colors">{{ rule.name }}</h3>
          <p class="text-[#596080] text-[12px] flex-1 mb-3 leading-relaxed">{{ rule.desc }}</p>
          <div class="border-t border-[#b8c9e8]/40 pt-2.5">
            <div class="text-[11px] text-[#B8BCCC] mb-1">审核范围：<span class="text-[#596080] font-medium">{{ rule.scope }}</span></div>
            <div class="text-[11px] text-[#B8BCCC] mb-2">监测维度：<span class="text-[#596080] font-medium">{{ rule.dimension }}</span></div>
            <div class="flex items-center justify-between">
              <span :class="[
                'text-[11px] font-medium px-2 py-0.5 rounded-full border',
                rule.mode === 'alert' ? 'border-red-200 text-red-600 bg-red-50' :
                'border-emerald-200 text-emerald-600 bg-emerald-50'
              ]">
                {{ rule.mode === 'alert' ? '预警模式' : '常规监测' }}
              </span>
              <span class="text-[11px] font-bold" :class="rule.mode === 'alert' ? 'text-red-600' : 'text-emerald-600'">
                {{ getRuleCount(rule) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 具体规则明细视图（r4/r5/r6/r7 统一模板） -->
    <template v-else>
      <!-- 顶部说明条 -->
      <div class="p-4 shrink-0">
        <div :class="['border rounded-[2px] p-2.5 flex items-start', currentRule?.mode === 'alert' ? 'bg-blue-50/50 border-blue-200' : 'bg-emerald-50 border-emerald-200']">
          <Info :class="['w-3.5 h-3.5 mr-2 shrink-0 mt-0.5', currentRule?.mode === 'alert' ? 'text-[#0A6EFD]' : 'text-emerald-500']" />
          <div>
            <h4 :class="['text-[13px] font-medium', currentRule?.mode === 'alert' ? 'text-blue-800' : 'text-emerald-800']">{{ currentRule?.name }}</h4>
            <p :class="['text-[11px] mt-0.5', currentRule?.mode === 'alert' ? 'text-blue-600' : 'text-emerald-600']">{{ currentRule?.logic }}</p>
          </div>
        </div>
      </div>

      <!-- 主体区域 -->
      <div class="flex-1 px-4 pb-4 overflow-hidden flex flex-col">
        <div class="bg-white rounded-[2px] border border-[#b8c9e8]/60 flex-1 overflow-hidden flex flex-col shadow-sm">
          <!-- 工具栏 -->
          <div class="p-3.5 border-b border-[#b8c9e8]/40 flex justify-between items-center shrink-0">
            <h3 class="font-semibold text-[#1F264D] flex items-center text-[13px]">
              {{ currentRule?.mode === 'alert' ? '违规预警数据列表' : '监测指标统计报表' }}
              <span v-if="currentRule?.mode === 'alert'" class="ml-2 bg-red-100 text-red-600 py-0.5 px-2 rounded-full text-[11px] font-bold">{{ tableData.length }}</span>
            </h3>
            <div class="flex items-center gap-2">
              <div class="flex items-center gap-1.5 border border-[#b8c9e8]/60 rounded-[2px] px-2.5 py-1.5 bg-white">
                <Calendar class="w-3.5 h-3.5 text-[#596080] shrink-0" />
                <input
                  type="date"
                  v-model="startDate"
                  class="text-[12px] text-[#1F264D] focus:outline-none bg-transparent w-[130px]"
                />
                <span class="text-[11px] text-[#B8BCCC]">至</span>
                <input
                  type="date"
                  v-model="endDate"
                  class="text-[12px] text-[#1F264D] focus:outline-none bg-transparent w-[130px]"
                />
                <button
                  v-if="startDate || endDate"
                  @click="startDate = ''; endDate = ''"
                  class="ml-0.5 text-[#B8BCCC] hover:text-[#596080] transition-colors"
                >
                  <X class="w-3 h-3" />
                </button>
              </div>
              <div class="relative">
                <Search class="w-3.5 h-3.5 absolute left-2.5 top-1/2 transform -translate-y-1/2 text-[#B8BCCC]" />
                <input type="text" v-model="keyword" placeholder="搜索..." class="pl-8 pr-3 py-1.5 text-[12px] border border-[#b8c9e8]/60 rounded-[2px] focus:outline-none focus:border-[#0A6EFD] w-52 bg-white" />
              </div>
              <button @click="handleExport" class="px-3 py-1.5 text-[12px] bg-[#0A6EFD] text-white rounded-[2px] hover:bg-[#0a5fe0] transition-colors flex items-center gap-1">
                <Download class="w-3.5 h-3.5" /> 导出
              </button>
            </div>
          </div>

          <!-- 预警模式表格（r4/r5） -->
          <div v-if="currentRule?.mode === 'alert'" class="flex-1 overflow-auto">
            <!-- 真实数据：动态列 -->
            <table v-if="realTableData.length > 0" class="w-full text-left border-collapse">
              <thead class="bg-[#e8eef9] sticky top-0 z-10">
                <tr>
                  <th v-for="col in realTableColumns" :key="col" class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">{{ col }}</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#b8c9e8]/30">
                <tr v-for="row in tableData" :key="row.id" class="hover:bg-[#e8eef9]/40 transition-colors">
                  <td v-for="col in realTableColumns" :key="col" class="px-3.5 py-2.5 text-[12px] text-[#596080] max-w-xs truncate" :title="String(row[col] ?? '-')">{{ row[col] ?? '-' }}</td>
                </tr>
              </tbody>
            </table>
            <div v-else class="flex flex-col items-center justify-center py-16 text-[#9CA3AF]">
              <Activity class="w-12 h-12 mb-3 opacity-30" />
              <p class="text-[13px]">暂无预警数据</p>
              <p class="text-[11px] mt-1">请在「指标执行」页面执行相应指标</p>
            </div>
          </div>

          <!-- 常规监测表格（r6/r7） -->
          <div v-else class="flex-1 overflow-auto">
            <table class="w-full text-left border-collapse">
              <thead :class="['sticky top-0 z-10 border-b', currentRule?.id === 'r7' ? 'bg-emerald-50/60 border-emerald-100' : 'bg-emerald-50/60 border-emerald-100']">
                <tr>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">医疗机构</th>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">机构类别 / 级别</th>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">许可证有效期</th>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">标准核验</th>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">风险预警</th>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide text-right">操作</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#b8c9e8]/30">
                <!-- r6 科目零业务 -->
                <template v-if="currentRule?.id === 'r6'">
                  <tr v-if="realTableData.length > 0" v-for="row in tableData" :key="row.id" class="hover:bg-emerald-50/40 transition-colors">
                    <td v-for="col in realTableColumns" :key="col" class="px-3.5 py-3 text-[12px] text-[#596080]">{{ row[col] ?? '-' }}</td>
                  </tr>
                  <tr v-if="realTableData.length === 0">
                    <td colspan="5" class="px-3.5 py-12 text-center text-[#9CA3AF]">
                      <Activity class="w-10 h-10 mx-auto mb-2 opacity-30" />
                      <p class="text-[13px]">暂无监测数据</p>
                      <p class="text-[11px] mt-1">请在「指标执行」页面执行相应指标</p>
                    </td>
                  </tr>
                </template>
                <!-- r7 医疗资质监测（保留 mock） -->
                <template v-else-if="currentRule?.id === 'r7'">
                  <tr v-for="row in tableData" :key="row.id" class="hover:bg-emerald-50/40 transition-colors">
                    <td class="px-3.5 py-3 text-[12px] text-[#1F264D] font-medium flex items-center">
                      <Building class="w-3.5 h-3.5 text-emerald-500 mr-2" /> {{ row.org || '-' }}
                    </td>
                    <td class="px-3.5 py-3 text-[12px]">
                      <span class="rounded border border-emerald-200 bg-emerald-50 px-1.5 py-0.5 text-[11px] font-medium text-emerald-600">{{ row.category || '-' }}</span>
                      <span class="ml-1 text-[11px] text-[#596080]">{{ row.level || '-' }}</span>
                    </td>
                    <td class="px-3.5 py-3 text-[12px]">
                      <span :class="row.licenseValid ? 'text-emerald-600 font-medium' : 'text-red-500 font-medium'">{{ row.licensePeriod || '-' }}</span>
                      <span class="ml-1.5 rounded px-1 py-0.5 text-[10px] font-medium" :class="row.licenseValid ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-500'">{{ row.licenseValid ? '有效' : '过期' }}</span>
                    </td>
                    <td class="px-3.5 py-3 text-[12px]">
                      <span :class="row.standardMeet ? 'text-emerald-600 font-medium' : 'text-red-500 font-medium'">{{ row.standardMeet ? '符合标准' : '存在不符合项' }}</span>
                    </td>
                    <td class="px-3.5 py-3 text-[12px]">
                      <span v-if="row.riskCount > 0" class="inline-flex items-center gap-1 rounded-full bg-red-50 px-2 py-0.5 text-[11px] font-bold text-red-500">
                        <AlertTriangle class="w-3 h-3"/>{{ row.riskCount }} 项预警
                      </span>
                      <span v-else class="text-[#9CA3AF]">暂无预警</span>
                    </td>
                    <td class="px-3.5 py-3 text-right">
                      <button @click="openDrawer(row)" class="text-[#0A6EFD] hover:text-[#1F264D] font-medium text-[11px]">
                        <Eye class="w-3 h-3 inline mr-1" />查看详情
                      </button>
                      <button @click="showLicenseImage(row)" class="ml-3 text-emerald-600 hover:text-emerald-700 font-medium text-[11px]">
                        <Shield class="w-3 h-3 inline mr-1" />查看资质
                      </button>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>

    <!-- 资质图片弹窗 -->
    <div v-if="licenseImageData" class="fixed inset-0 z-[200] flex items-center justify-center bg-gray-900/70 backdrop-blur-sm">
      <div class="bg-white rounded-lg shadow-2xl max-w-3xl w-full mx-4 overflow-hidden">
        <div class="px-5 py-3 border-b border-emerald-100 flex justify-between items-center bg-emerald-50">
          <h3 class="text-[14px] font-bold text-[#1F264D] flex items-center">
            <Shield class="w-4 h-4 text-emerald-500 mr-2" />
            {{ licenseImageData.org }} — 资质证照档案
          </h3>
          <button @click="licenseImageData = null" class="p-1.5 hover:bg-emerald-100 rounded-full text-[#596080] transition-colors">
            <X class="w-4 h-4" />
          </button>
        </div>
        <div class="p-4">
          <img src="/license-sample.png" :alt="licenseImageData.org + '资质证照'" class="w-full h-auto rounded border border-emerald-100" />
        </div>
      </div>
    </div>

    <!-- 详情抽屉 -->
    <div v-if="drawerData" class="fixed inset-0 z-50 flex justify-end bg-gray-900/50 backdrop-blur-sm">
      <div class="w-[580px] bg-white h-full shadow-2xl flex flex-col animate-slide-in border-l border-[#b8c9e8]/60">
        <!-- 抽屉头部 -->
        <div class="px-5 py-3.5 border-b border-[#b8c9e8]/60 flex justify-between items-center" :class="currentRule?.mode === 'alert' ? 'bg-[#e8eef9]' : 'bg-emerald-50'">
          <h2 class="text-[14px] font-bold text-[#1F264D] flex items-center">
            <ShieldAlert v-if="currentRule?.mode === 'alert'" class="w-4 h-4 text-red-500 mr-2" />
            <Activity v-else class="w-4 h-4 text-emerald-500 mr-2" />
            {{ currentRule?.mode === 'alert' ? '预警证据链详情' : '机构资质档案详情' }}
          </h2>
          <button @click="drawerData = null" class="p-1.5 hover:bg-[#b8c9e8]/30 rounded-full text-[#596080] transition-colors">
            <X class="w-4 h-4" />
          </button>
        </div>

        <!-- 抽屉内容 -->
        <div class="flex-1 overflow-y-auto p-5 space-y-4">
          <!-- 预警模式抽屉 -->
          <template v-if="currentRule?.mode === 'alert'">
            <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
              <div class="flex items-center justify-between mb-3">
                <h3 class="font-bold text-[#1F264D] text-[13px]">机构基本信息</h3>
                <span class="px-2 py-0.5 rounded-full text-[11px] font-medium border bg-red-50 text-red-600 border-red-200">触发预警</span>
              </div>
              <div class="grid grid-cols-2 gap-3 text-[12px]">
                <div><span class="text-[#596080] block mb-0.5">机构名称</span><span class="font-medium text-[#1F264D]">{{ drawerData.org }}</span></div>
                <div><span class="text-[#596080] block mb-0.5">违规类型</span><span class="font-medium text-[#1F264D]">{{ drawerData.violationType }}</span></div>
                <div><span class="text-[#596080] block mb-0.5">机构面积</span><span class="font-medium text-[#1F264D]">{{ drawerData.area || '-' }}</span></div>
                <div><span class="text-[#596080] block mb-0.5">核定床位</span><span class="font-medium text-[#1F264D]">{{ drawerData.beds || '-' }}</span></div>
              </div>
            </div>
            <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
              <h3 class="font-bold text-[#1F264D] text-[13px] mb-2.5">违规判定依据</h3>
              <div class="bg-red-50 border border-red-200 rounded-[2px] p-3 text-[12px] text-red-800">
                <p class="font-medium mb-1">违规类型：{{ drawerData.violationType }}</p>
                <p class="text-red-700">{{ drawerData.detail }}</p>
              </div>
            </div>
            <div>
              <h3 class="font-bold text-[#1F264D] text-[13px] mb-2.5 flex items-center">
                <Activity class="w-3.5 h-3.5 mr-1.5 text-[#0A6EFD]" />
                系统底层抓取证据
              </h3>
              <div class="bg-[#f8faff] border border-[#b8c9e8]/60 rounded-[2px] p-4">
                <p class="text-[11px] text-[#B8BCCC] mb-1.5 font-mono">=== 关联底层数据快照 ===</p>
                <div class="bg-[#f0f4ff] p-2.5 rounded-[2px] text-[11px] font-mono text-[#596080] whitespace-pre-line leading-relaxed">{{ drawerData.evidence }}</div>
              </div>
            </div>
          </template>

          <!-- r6 科目零业务抽屉 -->
          <template v-else-if="currentRule?.id === 'r6'">
            <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
              <div class="flex items-center justify-between mb-3">
                <h3 class="font-bold text-[#1F264D] text-[13px]">机构基本信息</h3>
                <span :class="['px-2 py-0.5 rounded-full text-[11px] font-medium border', drawerData.zeroMonths >= 3 ? 'bg-red-50 text-red-600 border-red-200' : 'bg-orange-50 text-orange-600 border-orange-200']">
                  {{ drawerData.zeroMonths >= 3 ? '触发预警' : '监测中' }}
                </span>
              </div>
              <div class="grid grid-cols-2 gap-3 text-[12px]">
                <div><span class="text-[#596080] block mb-0.5">机构名称</span><span class="font-medium text-[#1F264D]">{{ drawerData.org }}</span></div>
                <div><span class="text-[#596080] block mb-0.5">异常科目</span><span class="font-medium text-[#1F264D]">{{ drawerData.subject }}</span></div>
              </div>
            </div>
            <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
              <h3 class="font-bold text-[#1F264D] text-[13px] mb-2.5">零业务判定依据</h3>
              <div class="bg-red-50 border border-red-200 rounded-[2px] p-3 text-[12px] text-red-800">
                <p class="text-red-700">{{ drawerData.detail }}</p>
              </div>
            </div>
            <div>
              <h3 class="font-bold text-[#1F264D] text-[13px] mb-2.5 flex items-center">
                <Activity class="w-3.5 h-3.5 mr-1.5 text-emerald-500" />
                系统底层抓取证据
              </h3>
              <div class="bg-[#f8faff] border border-[#b8c9e8]/60 rounded-[2px] p-4">
                <p class="text-[11px] text-[#B8BCCC] mb-1.5 font-mono">=== 关联底层数据快照 ===</p>
                <div class="bg-[#f0f4ff] p-2.5 rounded-[2px] text-[11px] font-mono text-[#596080] whitespace-pre-line leading-relaxed">{{ drawerData.evidence }}</div>
              </div>
            </div>
          </template>

          <!-- r7 医疗资质监测抽屉 -->
          <template v-else-if="currentRule?.id === 'r7'">
            <!-- 基本信息 -->
            <div class="bg-white border border-emerald-100 rounded-[2px] p-4">
              <div class="flex items-center justify-between mb-3">
                <h3 class="font-bold text-[#1F264D] text-[13px]">机构基本信息</h3>
                <span :class="['px-2 py-0.5 rounded-full text-[11px] font-medium border', drawerData.standardMeet ? 'bg-emerald-50 text-emerald-600 border-emerald-200' : 'bg-orange-50 text-orange-600 border-orange-200']">
                  {{ drawerData.standardMeet ? '标准核验通过' : '标准核验异常' }}
                </span>
              </div>
              <div class="grid grid-cols-2 gap-3 text-[12px]">
                <div><span class="text-[#596080] block mb-0.5">机构名称</span><span class="font-medium text-[#1F264D]">{{ drawerData.org }}</span></div>
                <div><span class="text-[#596080] block mb-0.5">机构类别</span><span class="font-medium text-[#1F264D]">{{ drawerData.category }}</span></div>
                <div><span class="text-[#596080] block mb-0.5">执业地址</span><span class="font-medium text-[#1F264D]">{{ drawerData.address || '-' }}</span></div>
                <div><span class="text-[#596080] block mb-0.5">法定代表人</span><span class="font-medium text-[#1F264D]">{{ drawerData.legalPerson || '-' }}</span></div>
                <div><span class="text-[#596080] block mb-0.5">联系电话</span><span class="font-medium text-[#1F264D]">{{ drawerData.phone || '-' }}</span></div>
                <div><span class="text-[#596080] block mb-0.5">成立日期</span><span class="font-medium text-[#1F264D]">{{ drawerData.foundedDate || '-' }}</span></div>
              </div>
            </div>

            <!-- 执业许可证 -->
            <div class="bg-white border border-emerald-100 rounded-[2px] p-4">
              <h3 class="font-bold text-[#1F264D] text-[13px] mb-3 flex items-center">
                <Activity class="w-3.5 h-3.5 mr-1.5 text-emerald-500" />
                执业许可证信息
              </h3>
              <div class="grid grid-cols-2 gap-3 text-[12px]">
                <div><span class="text-[#596080] block mb-0.5">许可证号</span><span class="font-medium text-[#1F264D]">{{ drawerData.licenseNo || '-' }}</span></div>
                <div><span class="text-[#596080] block mb-0.5">有效期至</span><span :class="['font-medium', drawerData.licenseValid ? 'text-emerald-600' : 'text-red-500']">{{ drawerData.licenseExpire || '-' }}</span></div>
                <div><span class="text-[#596080] block mb-0.5">床位数量</span><span class="font-medium text-[#1F264D]">{{ drawerData.beds || '-' }} 张</span></div>
                <div><span class="text-[#596080] block mb-0.5">校验周期</span><span class="font-medium text-[#1F264D]">{{ drawerData.verifyCycle || '-' }}</span></div>
                <div class="col-span-2"><span class="text-[#596080] block mb-0.5">诊疗科目</span><span class="font-medium text-[#1F264D]">{{ drawerData.subjects || '-' }}</span></div>
              </div>
            </div>

            <!-- 标准核验 -->
            <div class="bg-white border border-emerald-100 rounded-[2px] p-4">
              <h3 class="font-bold text-[#1F264D] text-[13px] mb-3 flex items-center">
                <CheckCircle class="w-3.5 h-3.5 mr-1.5 text-emerald-500" />
                基本标准核验
              </h3>
              <table class="w-full text-left text-[12px]">
                <thead>
                  <tr class="bg-emerald-50/60">
                    <th class="py-2 px-3 font-semibold text-[#596080]">核验项目</th>
                    <th class="py-2 px-3 font-semibold text-[#596080]">标准要求</th>
                    <th class="py-2 px-3 font-semibold text-[#596080]">实际情况</th>
                    <th class="py-2 px-3 text-center font-semibold text-[#596080]">结论</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-[#e8eef9]/40">
                  <tr v-for="item in drawerData.standardItems" :key="item.name">
                    <td class="py-2 px-3 font-medium text-[#1F264D]">{{ item.name }}</td>
                    <td class="py-2 px-3 text-[#596080]">{{ item.requirement }}</td>
                    <td class="py-2 px-3 text-[#1F264D]">{{ item.actual }}</td>
                    <td class="py-2 px-3 text-center">
                      <span :class="item.meet ? 'text-emerald-600 font-medium' : 'text-red-500 font-medium'">{{ item.meet ? '符合' : '不符合' }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- 补充信息 -->
            <div class="bg-white border border-emerald-100 rounded-[2px] p-4">
              <h3 class="font-bold text-[#1F264D] text-[13px] mb-3 flex items-center">
                <Info class="w-3.5 h-3.5 mr-1.5 text-emerald-500" />
                补充机构信息
              </h3>
              <div class="grid grid-cols-2 gap-3 text-[12px]">
                <div><span class="text-[#596080] block mb-0.5">职工总数</span><span class="font-medium text-[#1F264D]">{{ drawerData.staffCount || '-' }} 人</span></div>
                <div><span class="text-[#596080] block mb-0.5">高级职称</span><span class="font-medium text-[#1F264D]">{{ drawerData.seniorCount || '-' }} 人</span></div>
                <div><span class="text-[#596080] block mb-0.5">年度门诊量</span><span class="font-medium text-[#1F264D]">{{ drawerData.outpatientCount || '-' }}</span></div>
                <div><span class="text-[#596080] block mb-0.5">年度住院量</span><span class="font-medium text-[#1F264D]">{{ drawerData.inpatientCount || '-' }}</span></div>
              </div>
            </div>

            <!-- 风险预警 -->
            <div class="bg-white border border-red-100 rounded-[2px] p-4">
              <h3 class="font-bold text-[#1F264D] text-[13px] mb-3 flex items-center">
                <ShieldAlert class="w-3.5 h-3.5 mr-1.5 text-red-400" />
                风险预警信息
              </h3>
              <div v-if="!drawerData.risks || drawerData.risks.length === 0" class="text-[12px] text-[#9CA3AF] text-center py-3">
                暂无风险预警
              </div>
              <div v-else class="space-y-2">
                <div v-for="risk in drawerData.risks" :key="risk.name" class="flex items-center justify-between rounded-lg border border-red-100 bg-red-50 p-3">
                  <div>
                    <p class="text-[12px] font-medium text-red-700">{{ risk.name }}</p>
                    <p class="text-[11px] text-red-400 mt-0.5">{{ risk.dept }}</p>
                  </div>
                  <span class="rounded-full bg-red-400 px-2.5 py-0.5 text-[11px] font-medium text-white">{{ risk.count }}次</span>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Activity,
  AlertTriangle,
  Building,
  Calendar,
  CheckCircle,
  Clock,
  Download,
  Eye,
  Info,
  Search,
  Shield,
  ShieldAlert,
  X,
} from 'lucide-vue-next'
import { exportToExcel } from '../../utils/exportExcel'
import { useFourFactorExecutions, TIME_MODE_OPTIONS, MONTH_OPTIONS, QUARTER_OPTIONS } from '../../composables/useFourFactorExecutions'
import type { TimeMode } from '../../composables/useFourFactorExecutions'

const route = useRoute()
const router = useRouter()
const { fetchExecutions, executionRecords, formatCountInMetric } = useFourFactorExecutions()

// 用于触发医院筛选变化时的重算（当前固定为全选，未来扩展筛选时自动生效）
const hospitalVersion = ref(0)
const currentHospitalId = ref('all')

// 时间筛选状态
const timeMode = ref<TimeMode>('immediate')
const selectedMonthYear = ref(new Date().getFullYear().toString())
const selectedMonthNum = ref('01')
const selectedQuarterYear = ref(new Date().getFullYear().toString())
const selectedQuarterNum = ref('1')

// 计算当前时间值
const currentTimeValue = computed(() => {
  if (timeMode.value === 'monthly') {
    return `${selectedMonthYear.value}-${selectedMonthNum.value}`
  }
  if (timeMode.value === 'quarterly') {
    return `${selectedQuarterYear.value}-Q${selectedQuarterNum.value}`
  }
  return undefined
})

// 月份年份选项（从5年前到当前年份+1年）
const monthYearOptions = computed(() => {
  const now = new Date()
  const cur = now.getFullYear()
  const start = cur - 5
  const years: number[] = []
  for (let y = start; y <= cur + 1; y++) {
    years.push(y)
  }
  return years
})

// 季度年份选项（从5年前到当前年份+1年）
const quarterYearOptions = computed(() => {
  const now = new Date()
  const cur = now.getFullYear()
  const start = cur - 5
  const years: number[] = []
  for (let y = start; y <= cur + 1; y++) {
    years.push(y)
  }
  return years
})

// indicator_id 对应 indicator.id（规则 ID 去掉 'r'）
const rules = [
  // 红色预警规则
  { id: 'r4', indicator_id: 4, mode: 'alert' as const, name: '超范围经营', desc: '诊断治疗与机构诊疗科目不符，系统自动报警。', scope: '住院', dimension: '资质审核', metric: '2 条', logic: '在系统中维护医疗机构诊疗科目信息，设定"诊断治疗-诊疗科目"匹配规则，医生开了与该医疗机构诊疗科目不符的诊断时自动报警。' },
  { id: 'r5', indicator_id: 5, mode: 'alert' as const, name: '收治能力超限', desc: '面积、床位与当日住院收治人数比例异常，系统自动拦截。', scope: '住院', dimension: '容量监测', metric: '2 条', logic: '在系统中设定"面积-床位-住院收治上限"联动模型，机构面积、床位数与当日在院患者人数比例异常时自动拦截，通报医保拒绝结算。' },
  // 绿色常规监测规则
  { id: 'r6', indicator_id: 6, mode: 'monitor' as const, name: '科目零业务监测', desc: '单一诊疗科目连续3个月"零"业务量统计，异常报警。', scope: '住院', dimension: '业务量监测', metric: '3 项异常', logic: '在系统中设定"机构-诊疗科目-业务量"匹配规则，对单一诊疗科目连续3个月"零"业务量的自动报警。' },
  { id: 'r7', indicator_id: 0, mode: 'monitor' as const, name: '医疗资质监测', desc: '展示机构基本信息、执业许可证、标准核验及风险预警等资质档案。', scope: '综合档案', dimension: '资质监测', metric: '完整档案', logic: '通过卫健委电子证照系统与病案首页实时同步，展示机构基本信息、执业许可证（正副本）、基本标准核验、补充信息及风险预警等多维度资质档案。' },
]

const tabs = [{ id: 'overview', name: '分类总览' }, ...rules]
const activeTab = ref(route.query.tab as string || 'overview')
const drawerData = ref<any>(null)
const licenseImageData = ref<any>(null)
const currentRule = computed(() => rules.find(r => r.id === activeTab.value))
const startDate = ref('')
const endDate = ref('')
const keyword = ref('')

watch(activeTab, (val) => {
  router.replace({ query: val === 'overview' ? {} : { tab: val } })
})

onMounted(() => {
  fetchExecutions()
})

const MOCK_DATA: Record<string, any[]> = {
  r4: [
    { id: 'I001', time: '2026-03-30 14:00', org: '康华医院', violationType: '超范围经营', detail: '该机构诊疗科目仅备案"内科、外科"，但实际开展眼科诊疗服务。', area: '3000㎡', beds: '100张', evidence: `[机构备案] 诊疗科目: 内科、外科\n[实际开展] 眼科诊疗服务记录: 23条\n>>> 异常判定: 备案科目与实际开展不符，涉嫌超范围经营。` },
    { id: 'I002', time: '2026-03-28 09:30', org: '仁爱医院', violationType: '超范围经营', detail: '该机构未备案放射诊疗科目，但实际开展X光检查服务。', area: '200㎡', beds: '10张', evidence: `[机构备案] 诊疗科目: 内科\n[实际开展] 放射诊疗(X光)记录: 8条\n>>> 异常判定: 未备案放射诊疗科目，涉嫌违规开展。` },
  ],
  r5: [
    { id: 'I003', time: '2026-03-29 23:45', org: '省立第一医院', violationType: '收治能力超限', detail: '核定床位800张，当日实际收治1089人，超出核定红线36%。', area: '50000㎡', beds: '800张', evidence: `[机构信息] 省立第一医院 | 面积: 50000㎡ | 核定床位: 800张\n[实时数据] 当日在院患者: 1089人\n>>> 异常判定: 超出"面积-床位-收治上限"联动模型红线，超限289人(36.1%)。` },
    { id: 'I004', time: '2026-03-27 22:00', org: '市中心医院', violationType: '收治能力超限', detail: '核定床位500张，当日实际收治680人，超出核定红线26%。', area: '35000㎡', beds: '500张', evidence: `[机构信息] 市中心医院 | 核定床位: 500张\n[实时数据] 当日在院患者: 680人 | 超限180人(26%)` },
  ],
  r6: [
    { id: 'I005', org: '康华医院', subject: '眼科', zeroMonths: 4, violationType: '零业务监测', detail: '眼科连续4个月无诊疗记录。', evidence: `[业务记录] 眼科: 2025-11~2026-02 连续4个月零业务` },
    { id: 'I006', org: '县第二医院', subject: '肿瘤科', zeroMonths: 3, violationType: '零业务监测', detail: '肿瘤科连续3个月无诊疗记录。', evidence: `[业务记录] 肿瘤科: 2025-12~2026-02 连续3个月零业务` },
    { id: 'I007', org: '省立第三医院', subject: '儿科', zeroMonths: 2, violationType: '零业务监测', detail: '儿科连续2个月无住院诊疗记录。', evidence: `[业务记录] 儿科: 2026-01~2026-02 连续2个月零住院业务` },
  ],
  r7: [
    {
      id: 'I101', org: '北京市第一人民医院', category: '综合医院', level: '三级',
      licensePeriod: '2023-01-01 ~ 2028-12-31', licenseValid: true, licenseExpire: '2028年12月31日', licenseNo: 'PDY12345678901234',
      standardMeet: true, riskCount: 0,
      beds: 600, verifyCycle: '3年', subjects: '急诊科、内科、外科、妇产科、儿科、中医科、麻醉科、康复科等',
      address: '北京市朝阳区XX路XX号', legalPerson: '张三（院长）', phone: '010-12345678', foundedDate: '2000年05月10日',
      standardItems: [
        { name: '床位数量', requirement: '≥500张', actual: '600张', meet: true },
        { name: '卫生技术人员', requirement: '≥1.03名/床', actual: '每床1.25名', meet: true },
        { name: '护士配备', requirement: '≥0.4名/床', actual: '每床0.42名', meet: true },
        { name: '临床科室数', requirement: '≥12个', actual: '15个', meet: true },
      ],
      staffCount: 1800, seniorCount: 320, outpatientCount: '120万人次', inpatientCount: '4.5万人次', risks: [],
    },
    {
      id: 'I102', org: '海口康宁康复医院', category: '康复医院', level: '二级',
      licensePeriod: '2024-01-01 ~ 2029-12-31', licenseValid: true, licenseExpire: '2029年12月31日', licenseNo: 'PDY98765432109876',
      standardMeet: false, riskCount: 2,
      beds: 310, verifyCycle: '3年', subjects: '康复医学科、中医科、内科',
      address: '海口市美兰区XX路XX号', legalPerson: '李四', phone: '0898-88888888', foundedDate: '2015年08月20日',
      standardItems: [
        { name: '床位数量', requirement: '≥300张', actual: '310张', meet: true },
        { name: '卫生技术人员', requirement: '≥1.4名/床', actual: '每床1.35名', meet: false },
      ],
      staffCount: 420, seniorCount: 58, outpatientCount: '18万人次', inpatientCount: '0.9万人次',
      risks: [
        { name: '卫生技术人员配备不足', dept: '卫生健康委员会医政科', count: 1 },
        { name: '放射科设备未按期校验', dept: '卫生健康委员会监督执法局', count: 1 },
      ],
    },
    {
      id: 'I103', org: '儋州市某综合医院', category: '综合医院', level: '二级',
      licensePeriod: '2022-06-01 ~ 2027-05-31', licenseValid: true, licenseExpire: '2027年05月31日', licenseNo: 'PDY54321098765432',
      standardMeet: false, riskCount: 1,
      beds: 350, verifyCycle: '3年', subjects: '内科、外科、妇产科、儿科、急诊科',
      address: '儋州市那大镇XX路XX号', legalPerson: '王五', phone: '0898-76543210', foundedDate: '2010年03月15日',
      standardItems: [
        { name: '床位数量', requirement: '100-499张', actual: '350张', meet: true },
        { name: '卫生技术人员', requirement: '≥0.88名/床', actual: '0.85名/床', meet: false },
        { name: '护士配备', requirement: '≥0.4名/床', actual: '0.41名/床', meet: true },
      ],
      staffCount: 520, seniorCount: 72, outpatientCount: '35万人次', inpatientCount: '1.8万人次',
      risks: [
        { name: '护理人员配备比例不足', dept: '卫生健康委员会医政科', count: 3 },
      ],
    },
  ],
}

const tableData = computed(() => {
  const rule = currentRule.value
  // r4/r5 (alert) 和 r6 (monitor)：真实数据
  if (rule?.mode === 'alert' || rule?.id === 'r6') {
    return realTableData.value
  }
  // r7：mock 数据
  let result = MOCK_DATA[activeTab.value] || []
  if (keyword.value) {
    result = result.filter((item: any) =>
      (item.org || item.name || '').toLowerCase().includes(keyword.value.toLowerCase()),
    )
  }
  if (startDate.value) {
    result = result.filter((item: any) => !item.time || item.time >= startDate.value)
  }
  if (endDate.value) {
    result = result.filter((item: any) => !item.time || item.time <= endDate.value)
  }
  return result
})

// 当前规则对应的指标 ID
const currentIndicatorId = computed(() => {
  const rule = currentRule.value
  return rule?.indicator_id && rule.indicator_id > 0 ? rule.indicator_id : null
})

// 真实预览数据列名
const realTableColumns = computed(() => {
  void hospitalVersion.value
  const indId = currentIndicatorId.value
  if (!indId) return []
  const rec = findExecutionByTime(indId)
  const preview = rec?.preview_data
  if (!preview) return []
  return preview.columns || (preview.rows?.[0] ? Object.keys(preview.rows[0]) : [])
})

// 真实预览数据
const realTableData = computed(() => {
  void hospitalVersion.value
  const indId = currentIndicatorId.value
  if (!indId) return []
  const rec = findExecutionByTime(indId)
  const preview = rec?.preview_data
  if (!preview || !preview.rows?.length) return []
  const cols = preview.columns || Object.keys(preview.rows[0])
  return preview.rows.map((row, idx) => {
    const item: any = { id: String(idx + 1), _raw: row }
    for (const col of cols) {
      item[col] = row[col]
    }
    return item
  })
})

/**
 * 注释：以下函数已废弃，请使用 getRuleCount 替代
 * const getMockCount = (id: string) => {
 *   const rule = rules.find(r => r.id === id)
 *   if (!rule || !rule.indicator_id) return MOCK_DATA[id]?.length || 0
 *   if (rule.mode === 'alert') return getAlertCount(rule.indicator_id)
 *   return getCount(rule.indicator_id)
 * }
 */

// 根据时间筛选条件过滤执行记录
function findExecutionByTime(indicatorId: number): any | null {
  const tm = timeMode.value
  const tv = currentTimeValue.value
  return executionRecords.value
    .filter(r => r.indicator_id === indicatorId && r.status === 'success')
    .filter(r => {
      if (tm === 'immediate') return true
      if (r.run_mode !== tm) return false
      if (tv && r.time_value !== tv) return false
      return true
    })
    .sort((a, b) => new Date(b.execution_time).getTime() - new Date(a.execution_time).getTime())[0] || null
}

function getRuleCount(rule: any): string {
  if (!rule) return '-'
  void hospitalVersion.value
  const rec = findExecutionByTime(rule.indicator_id)
  if (!rec) return '-'
  const cnt = rec.numerator_count ?? 0
  if (rule.mode !== 'monitor' || !rule.metric) return `${cnt} 条`
  return formatCountInMetric(rule.metric, cnt)
}

const openDrawer = (row: any) => { drawerData.value = row }
const showLicenseImage = (row: any) => { licenseImageData.value = row }

const institutionColumns = [
  { field: 'time', header: '预警时间' },
  { field: 'org', header: '涉事机构' },
  { field: 'violationType', header: '违规类型' },
  { field: 'detail', header: '违规详情' },
]

function handleExport() {
  const rule = currentRule.value
  const name = rule ? `${rule.id}-${rule.name}` : '机构要素总览'
  exportToExcel(tableData.value, institutionColumns, `机构要素_${name}`)
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.animate-slide-in { animation: slideIn 0.3s ease-out; }
@keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }
</style>
