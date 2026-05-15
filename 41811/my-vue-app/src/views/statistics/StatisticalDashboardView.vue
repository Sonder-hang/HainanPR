<template>
  <div class="flex h-full min-h-0 flex-col bg-[#F7F9FC] font-sans text-[#1F264D]">
    <!-- 顶栏 -->
    <header class="flex min-h-[102px] shrink-0 flex-col justify-center gap-3 border-b border-[#b8c9e8]/60 bg-[#cbd9f4] px-6 py-4 shadow-[0_1px_3px_rgba(0,0,0,0.06)] sm:gap-0 sm:py-0">
      <!-- 标题行 + 状态Tab -->
      <div class="flex h-14 items-center justify-between border-b border-[#b8c9e8]/50 bg-[#e8eef9] px-6 -mx-6 px-6">
        <h1 class="text-xl font-bold text-[#1F264D]">统计与定期监测预警看板</h1>

        <div class="flex items-center rounded-[2px] border border-[#b8c9e8]/70 bg-[#e8eef9] p-1">
          <button
            v-for="tab in statusTabs"
            :key="tab.value"
            @click="filterStatus = tab.value"
            class="flex items-center gap-1.5 rounded-[2px] px-4 py-1.5 text-sm font-bold transition-colors"
            :class="
              filterStatus === tab.value
                ? 'bg-white shadow-sm text-[#1F264D] border border-[#b8c9e8]/70'
                : 'text-[#596080] hover:text-[#1F264D]'
            "
          >
            {{ tab.label }}
            <span
              v-if="tab.value === 'pending'"
              class="ml-1 rounded-full bg-red-100 px-1.5 py-0.5 text-[10px] font-bold text-red-600"
            >
              {{ pendingCount }}
            </span>
          </button>
        </div>
      </div>

      <!-- 筛选器行 -->
      <div class="flex flex-wrap items-center gap-3">
        <!-- 时间周期 -->
        <div class="flex h-8 items-center overflow-hidden rounded-[2px] border border-[#b8c9e8]/70 bg-white shadow-sm transition-colors hover:border-[#0A6EFD]">
          <div class="flex h-full items-center border-r border-[#b8c9e8]/70 bg-[#F7F9FC] px-2.5 text-[#596080]">
            <Calendar :size="14" />
          </div>
          <select
            v-model="filterDate"
            class="min-w-[140px] bg-transparent px-2 py-1 text-sm font-medium text-[#1F264D] outline-none cursor-pointer"
          >
            <option value="2026-Q1">2026年 第一季度</option>
            <option value="2025-Q4">2025年 第四季度</option>
            <option value="last-3-months">近三个月统算</option>
          </select>
        </div>

        <!-- 机构 -->
        <div class="flex h-8 items-center overflow-hidden rounded-[2px] border border-[#b8c9e8]/70 bg-white shadow-sm transition-colors hover:border-[#0A6EFD]">
          <div class="flex h-full items-center border-r border-[#b8c9e8]/70 bg-[#F7F9FC] px-2.5 text-[#596080]">
            <Building :size="14" />
          </div>
          <select
            v-model="filterHospital"
            class="min-w-[150px] bg-transparent px-2 py-1 text-sm font-medium text-[#1F264D] outline-none cursor-pointer"
          >
            <option value="all">全市所有医疗机构</option>
            <option value="市中心医院">市中心医院</option>
            <option value="康美">康美妇产民营医院</option>
            <option value="城南">城南社区卫生服务中心</option>
            <option value="慈爱">慈爱健康体检中心</option>
          </select>
        </div>

        <!-- 监管要素 -->
        <div class="flex h-8 items-center overflow-hidden rounded-[2px] border border-[#b8c9e8]/70 bg-white shadow-sm transition-colors hover:border-[#0A6EFD]">
          <select
            v-model="filterCategory"
            @change="filterRule = 'all'"
            class="min-w-[130px] bg-transparent px-3 py-1 text-sm font-medium text-[#1F264D] outline-none cursor-pointer"
          >
            <option value="all">所有监管要素</option>
            <option value="institution">机构要素</option>
            <option value="technical">技术要素</option>
            <option value="equipment">设备要素</option>
          </select>
        </div>

        <!-- 具体规则 -->
        <div
          class="flex h-8 items-center overflow-hidden rounded-[2px] border bg-white shadow-sm transition-colors"
          :class="filterCategory === 'all' ? 'border-[#E6E9F2] cursor-not-allowed' : 'border-[#b8c9e8]/70 hover:border-[#0A6EFD]'"
        >
          <select
            v-model="filterRule"
            :disabled="filterCategory === 'all'"
            class="min-w-[180px] bg-transparent px-3 py-1 text-sm"
            :class="
              filterCategory === 'all'
                ? 'text-[#B8BCCC] cursor-not-allowed bg-[#F7F9FC]'
                : 'font-medium text-[#1F264D] cursor-pointer'
            "
            outline-none
          >
            <option v-for="rule in ruleCategories[filterCategory]" :key="rule.id" :value="rule.id">
              {{ rule.name }}
            </option>
          </select>
        </div>
      </div>
    </header>

    <!-- 主体内容 -->
    <div class="flex min-h-0 flex-1 overflow-hidden">
      <!-- 左侧：异常主体清单 -->
      <aside class="flex w-[380px] shrink-0 flex-col border-r border-[#b8c9e8]/60 bg-white shadow-[inset_-1px_0_0_rgba(255,255,255,0.5)]">
        <div class="flex items-center justify-between border-b border-[#b8c9e8]/50 bg-[#e8eef9] p-3">
          <h2 class="flex items-center text-sm font-bold text-[#1F264D]">
            <Database :size="16" class="mr-2 text-[#0A6EFD]" />
            周期统算超限清单
          </h2>
        </div>

        <div class="alert-scroll flex-1 space-y-3 overflow-y-auto bg-[#F7F9FC] p-3">
          <template v-if="filteredAlerts.length > 0">
            <div
              v-for="item in filteredAlerts"
              :key="item.id"
              @click="selectedItem = item"
              class="relative cursor-pointer rounded-[2px] border-2 bg-white p-4 shadow-sm transition-all"
              :class="
                selectedItem?.id === item.id
                  ? 'border-[#0A6EFD] bg-[#EEF2FF]/40 shadow-md'
                  : 'border-transparent hover:border-[#0A6EFD]/50 hover:shadow-sm'
              "
            >
              <!-- 状态角标 -->
              <div
                class="absolute right-0 top-0 rounded-bl-lg rounded-tr-[2px] px-2 py-0.5 text-[10px] font-bold text-white"
                :class="item.status === 'pending' ? 'bg-[#E5455F]' : 'bg-[#12B881]'"
              >
                {{ item.status === 'pending' ? '待处置' : '已核实' }}
              </div>

              <div class="mb-2.5 flex items-start justify-between pr-8">
                <span class="rounded border border-[#b8c9e8]/70 bg-[#F7F9FC] px-1.5 py-0.5 text-[11px] font-bold text-[#596080]">
                  {{ item.category }} - 规则 {{ item.ruleId }}
                </span>
              </div>

              <h3
                class="mb-1.5 text-sm font-bold"
                :class="selectedItem?.id === item.id ? 'text-[#0A6EFD]' : 'text-[#1F264D]'"
              >
                {{ item.ruleName }}
              </h3>

              <p class="mb-3 flex items-center text-xs text-[#596080]">
                <Building :size="14" class="mr-1 text-[#B8BCCC]" />
                <span class="truncate">{{ item.hospital }} - {{ item.subject }}</span>
              </p>

              <div class="mt-2 flex items-center justify-between rounded border border-[#F7F9FC] bg-white p-2 shadow-sm">
                <div class="flex-1 text-center">
                  <div class="mb-0.5 text-[10px] font-bold text-[#596080]">阈值要求</div>
                  <div class="text-xs font-bold text-[#1F264D]">{{ item.metrics.threshold }}</div>
                </div>
                <div class="mx-2 h-6 w-px bg-[#E6E9F2]"></div>
                <div class="flex-1 text-center">
                  <div class="mb-0.5 text-[10px] font-bold text-[#E5455F]">实际检出</div>
                  <div class="text-sm font-black text-[#E5455F]">{{ item.metrics.actual }}</div>
                </div>
              </div>
            </div>
          </template>

          <div v-else class="flex h-full flex-col items-center justify-center text-[#B8BCCC]">
            <Filter :size="40" class="mb-3 opacity-30" />
            <p class="text-sm font-medium text-[#596080]">当前条件下无超限数据</p>
          </div>
        </div>
      </aside>

      <!-- 右侧：预警明细穿透区 -->
      <main class="flex min-h-0 flex-1 flex-col overflow-y-auto bg-[#F7F9FC]">
        <template v-if="selectedItem && filteredAlerts.some(a => a.id === selectedItem.id)">
          <div class="mx-auto w-full max-w-6xl space-y-6 p-6">

            <!-- 顶部标题与研判 -->
            <div class="relative overflow-hidden rounded-[2px] border border-[#b8c9e8]/60 bg-white p-5 shadow-sm">
              <div class="absolute top-0 right-0 -z-0 h-32 w-32 rounded-bl-full bg-[#EEF2FF]/50"></div>
              <div class="relative z-10">
                <div class="mb-4 flex items-start justify-between">
                  <div>
                    <div class="mb-1.5 flex items-center gap-3">
                      <h2 class="text-xl font-bold text-[#1F264D]">{{ selectedItem.hospital }}</h2>
                      <span class="rounded border border-[#0A6EFD]/30 bg-[#EEF2FF] px-2.5 py-0.5 text-xs font-bold text-[#0A6EFD]">
                        {{ selectedItem.subject }}
                      </span>
                    </div>
                    <div class="flex items-center text-xs font-medium text-[#596080]">
                      <Calendar :size="14" class="mr-1" />
                      统算取数周期：{{ selectedItem.timeWindow }}
                      <span class="mx-2 text-[#B8BCCC]">|</span>
                      预警单号：{{ selectedItem.id }}
                    </div>
                  </div>

                  <div
                    class="flex items-center gap-1.5 rounded-full border-2 px-4 py-1.5 text-sm font-bold"
                    :class="
                      selectedItem.status === 'pending'
                        ? 'border-[#E5455F] bg-[#FEF2F2] text-[#E5455F]'
                        : 'border-[#12B881] bg-[#ECFDF5] text-[#12B881]'
                    "
                  >
                    <AlertCircle v-if="selectedItem.status === 'pending'" :size="16" />
                    <CheckCircle2 v-else :size="16" />
                    {{ selectedItem.status === 'pending' ? '未核实处置' : '已核实闭环' }}
                  </div>
                </div>

                <div
                  class="border-l-4 rounded-r-md p-3 shadow-sm"
                  :class="
                    selectedItem.status === 'pending'
                      ? 'bg-[#FEF2F2]/80 border-[#E5455F]'
                      : 'border-[#596080] bg-[#F7F9FC]'
                  "
                >
                  <h4
                    class="mb-1 flex items-center text-sm font-bold"
                    :class="selectedItem.status === 'pending' ? 'text-[#E5455F]' : 'text-[#596080]'"
                  >
                    <AlertTriangle :size="16" class="mr-2" />
                    系统统算研判摘要
                  </h4>
                  <p
                    class="text-sm leading-relaxed font-medium"
                    :class="selectedItem.status === 'pending' ? 'text-[#E5455F]/80' : 'text-[#596080]'"
                  >
                    {{ selectedItem.summary }}
                  </p>
                </div>
              </div>
            </div>

            <!-- 图表 + 表格 -->
            <div class="grid grid-cols-1 gap-6 xl:grid-cols-3">
              <!-- 图表 -->
              <div class="flex h-[320px] flex-col rounded-[2px] border border-[#b8c9e8]/60 bg-white p-5 shadow-sm xl:col-span-1">
                <h3 class="mb-4 flex items-center text-sm font-bold text-[#1F264D]">
                  <PieChart :size="16" class="mr-2 text-[#0A6EFD]" />
                  数据趋势可视化
                </h3>
                <div class="relative flex-1 w-full">
                  <component :is="getChartComponent(selectedItem)" :item="selectedItem" />
                </div>
              </div>

              <!-- 表格 -->
              <div class="flex h-[320px] flex-col rounded-[2px] border border-[#b8c9e8]/60 bg-white p-5 shadow-sm xl:col-span-2">
                <div class="mb-4 flex items-center justify-between">
                  <h3 class="flex items-center text-sm font-bold text-[#1F264D]">
                    <Database :size="16" class="mr-2 text-[#0A6EFD]" />
                    底层单据溯源证据链
                  </h3>
                  <button class="flex items-center text-sm font-bold text-[#0A6EFD] transition-colors hover:text-[#2563EB]">
                    <Download :size="16" class="mr-1" />
                    导出本表
                  </button>
                </div>

                <div class="flex-1 overflow-auto rounded border border-[#b8c9e8]/60 bg-white shadow-inner">
                  <table class="w-full whitespace-nowrap text-left text-xs">
                    <thead class="sticky top-0 z-10 bg-[#F2F5FA] text-[#596080] shadow-sm">
                      <tr>
                        <th
                          v-for="(col, i) in selectedItem.drillDownColumns"
                          :key="i"
                          class="border-b border-[#b8c9e8]/60 px-3 py-2 font-bold"
                        >
                          {{ col }}
                        </th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-[#F7F9FC]">
                      <tr
                        v-for="(row, ri) in selectedItem.drillDownData"
                        :key="ri"
                        class="transition-colors hover:bg-[#EEF2FF]/50"
                      >
                        <td
                          v-for="(cell, ci) in row"
                          :key="ci"
                          class="px-3 py-2.5"
                          :class="ci === 0 ? 'font-bold text-[#1F264D]' : 'text-[#596080]'"
                        >
                          {{ cell }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <!-- 底部操作区 -->
            <div class="rounded-[2px] border border-[#b8c9e8]/60 bg-white p-5 shadow-sm">
              <h3 class="mb-4 flex items-center border-b border-[#F7F9FC] pb-2 text-sm font-bold text-[#1F264D]">
                <FileText :size="16" class="mr-2 text-[#0A6EFD]" />
                核实与处置操作
              </h3>

              <!-- 待处理状态 -->
              <div
                v-if="selectedItem.status === 'pending'"
                class="flex items-center justify-between rounded-lg border border-[#b8c9e8]/60 bg-[#F7F9FC] p-4"
              >
                <div class="text-sm text-[#596080]">
                  <span class="font-bold text-[#1F264D]">当前任务：</span>
                  需结合右侧溯源证据链，人工判定该主体是否存在实质性违规。
                </div>
                <div class="flex gap-3">
                  <button class="box-border flex h-[32px] items-center gap-2 rounded-[2px] border border-[#b8c9e8]/70 bg-white px-5 py-2.5 text-sm font-bold text-[#596080] shadow-sm transition-colors hover:bg-[#F3F4F6] hover:text-[#1F264D]">
                    情况合理 / 驳回预警
                  </button>
                  <button class="box-border flex h-[32px] items-center gap-2 rounded-[2px] bg-[#0A6EFD] px-5 py-2.5 text-sm font-bold text-white shadow-sm shadow-[#0A6EFD]/30 transition-colors hover:bg-[#2563EB]">
                    <AlertCircle :size="16" />
                    确认异常并下发整改
                  </button>
                </div>
              </div>

              <!-- 已处理状态 -->
              <div v-else class="border-l-2 border-[#12B881] pl-4 ml-2 mt-2 space-y-3">
                <div class="relative">
                  <div class="absolute -left-[21px] top-1 h-3 w-3 rounded-full border-2 border-white bg-[#12B881] shadow-sm"></div>
                  <p class="text-sm font-bold text-[#1F264D]">
                    已确认统计超标属实，约谈该院业务院长，并责令下月控制指标。
                  </p>
                  <p class="mt-1 flex items-center text-xs text-[#596080]">
                    <CheckCircle2 :size="14" class="mr-1 text-[#12B881]" />
                    处理人: 卫健委监管科李科长 · 2026-04-05 14:30
                  </p>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- 无选中 -->
        <div v-else class="flex h-full flex-col items-center justify-center bg-white text-[#B8BCCC]">
          <BarChart2 :size="64" class="mb-4 text-[#E6E9F2]" />
          <p class="font-medium">请在左侧清单中选择一项超限记录以查看深度溯源与处置</p>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Calendar, Building, Database, PieChart, AlertTriangle, AlertCircle,
  CheckCircle2, FileText, Download, BarChart2, Filter
} from 'lucide-vue-next'

// 规则分类映射
const ruleCategories: Record<string, { id: string; name: string }[]> = {
  all: [{ id: 'all', name: '所有具体规则' }],
  institution: [
    { id: 'all', name: '所有机构要素规则' },
    { id: '1', name: '1. 诊疗科目连续零业务量' }
  ],
  technical: [
    { id: 'all', name: '所有技术要素规则' },
    { id: '1', name: '1. 单一术式占比超50%' },
    { id: '2', name: '2. 未成年人受侵害预警' }
  ],
  equipment: [
    { id: 'all', name: '所有设备要素规则' },
    { id: '1', name: '1. 特定检查阳性率双超80%' },
    { id: '2', name: '2. 重点耗材监测超阈值' }
  ]
}

// 数据类型
interface ChartPoint { label: string; value: number; limit?: number; color?: string }
interface TimelinePoint { date: string; hospital: string; diagnosis: string; doctor: string }
interface AlertItem {
  id: string
  ruleId: string
  ruleName: string
  categoryId: string
  category: string
  hospital: string
  subject: string
  timeWindow: string
  status: string
  summary: string
  chartType: string
  metrics: { threshold: string; actual: string; unit: string }
  chartData: ChartPoint[] | TimelinePoint[]
  drillDownColumns: string[]
  drillDownData: string[][]
}

// 模拟数据
const mockStatisticalAlerts: AlertItem[] = [
  {
    id: 'STAT-EQ-002', ruleId: '2', ruleName: '重点耗材监测超阈值', categoryId: 'equipment',
    category: '设备要素', hospital: '市中心医院', subject: '骨科 (人工关节类耗材)',
    timeWindow: '2026年1月-3月', status: 'pending',
    summary: '第一季度骨科高值耗材使用金额超设定阈值 24%。',
    chartType: 'bar-threshold',
    metrics: { threshold: '500万', actual: '620万', unit: '万元' },
    chartData: [
      { label: '1月', value: 180, limit: 160 },
      { label: '2月', value: 190, limit: 160 },
      { label: '3月', value: 250, limit: 180 }
    ] as ChartPoint[],
    drillDownColumns: ['开具医生', '患者姓名', '耗材名称', '单价', '数量', '总金额'],
    drillDownData: [
      ['王建国 (主任)', '张三', '进口膝关节假体', '¥32,000', '1', '¥32,000'],
      ['李海 (副主任)', '李四', '骨盆修复钛板', '¥18,000', '2', '¥36,000'],
      ['王建国 (主任)', '赵六', '进口髋关节假体', '¥45,000', '1', '¥45,000']
    ]
  },
  {
    id: 'STAT-TC-002', ruleId: '2', ruleName: '未成年人受侵害高危预警', categoryId: 'technical',
    category: '技术要素', hospital: '全市跨机构流转', subject: '患者：张小明 (12岁)',
    timeWindow: '近6个月', status: 'pending',
    summary: '该患儿近半年内累计命中 3 次高危外伤/中毒诊断，存在疑似受侵害线索，建议移交相关部门核实。',
    chartType: 'timeline',
    metrics: { threshold: '≥2次', actual: '3次', unit: '高危就诊' },
    chartData: [
      { date: '2025-10-15', hospital: '市第一医院急诊', diagnosis: '左前臂桡骨骨折', doctor: '刘急诊' },
      { date: '2026-01-12', hospital: '区中医院门诊', diagnosis: '背部深二度烧烫伤', doctor: '陈外科' },
      { date: '2026-03-28', hospital: '市儿童医院住院', diagnosis: '急性一氧化碳中毒', doctor: '孙儿科' }
    ] as TimelinePoint[],
    drillDownColumns: ['就诊日期', '就诊机构', '接诊科室/医师', '高风险诊断 (ICD-10)', '患者转归', '医疗总费用'],
    drillDownData: [
      ['2026-03-28', '市儿童医院', '急诊科 / 孙儿科', '急性一氧化碳中毒 (T58.x00)', '留观/住院', '¥1,520.00'],
      ['2026-01-12', '区中医院', '外科门诊 / 陈外科', '背部深二度烧烫伤 (T21.200)', '门诊换药', '¥385.50'],
      ['2025-10-15', '市第一医院', '急诊骨科 / 刘急诊', '左前臂桡骨骨折 (S52.500)', '石膏固定', '¥980.00']
    ]
  },
  {
    id: 'STAT-TC-001', ruleId: '1', ruleName: '单一术式占比超50%', categoryId: 'technical',
    category: '技术要素', hospital: '康美妇产民营医院', subject: '妇产科',
    timeWindow: '2026年1月-3月', status: 'processed',
    summary: '系统监测该院【剖宫产术】占全院所有手术量比例达到 68%，远超 50% 警戒线，存在诱导手术嫌疑。',
    chartType: 'pie',
    metrics: { threshold: '50%', actual: '68%', unit: '手术占比' },
    chartData: [
      { label: '剖宫产术', value: 68, color: '#E5455F' },
      { label: '其他手术', value: 32, color: '#E6E9F2' }
    ] as ChartPoint[],
    drillDownColumns: ['手术时间', '患者', '主刀医生', '术式名称', '术前指征', '医保结算金额'],
    drillDownData: [
      ['2026-02-28', '林女士', '张主任', '子宫下段剖宫产术', '社会因素(要求剖宫产)', '¥6,500'],
      ['2026-02-27', '吴女士', '张主任', '子宫下段剖宫产术', '胎位不正', '¥7,200'],
      ['2026-02-26', '陈女士', '李医生', '子宫下段剖宫产术', '巨大儿', '¥6,800']
    ]
  },
  {
    id: 'STAT-IN-001', ruleId: '1', ruleName: '诊疗科目连续零业务量', categoryId: 'institution',
    category: '机构要素', hospital: '城南社区卫生服务中心', subject: '眼科',
    timeWindow: '近3个月', status: 'processed',
    summary: '该机构登记有【眼科】诊疗科目，但系统监测连续3个月无任何该科目的诊断业务。',
    chartType: 'zero-bar',
    metrics: { threshold: '＞0', actual: '0', unit: '接诊人次' },
    chartData: [
      { label: '1月', value: 0 },
      { label: '2月', value: 0 },
      { label: '3月', value: 0 }
    ] as ChartPoint[],
    drillDownColumns: ['核查建议', '责任联系人', '机构电话', '最近一次历史业务时间'],
    drillDownData: [
      ['建议通报卫健委，核实眼科医师是否离职，评估是否需注销该科目资质。', '王院长', '010-88887777', '2025年11月05日']
    ]
  },
  {
    id: 'STAT-EQ-001', ruleId: '1', ruleName: '特定检查阳性率双超80%', categoryId: 'equipment',
    category: '设备要素', hospital: '慈爱健康体检中心', subject: '幽门螺旋杆菌呼气试验',
    timeWindow: '近3个月', status: 'pending',
    summary: '该检查项目占全院检查总量 85%，且结果阳性率高达 88%，存在设备参数造假或过度检查嫌疑。',
    chartType: 'dual-bar',
    metrics: { threshold: '双80%', actual: '85% / 88%', unit: '占比/阳性率' },
    chartData: [
      { label: '业务量', value: 85, limit: 80, color: '#0A6EFD' },
      { label: '阳性率', value: 88, limit: 80, color: '#F58718' }
    ] as ChartPoint[],
    drillDownColumns: ['检查日期', '患者姓名', '检查项目', '检测数值', '结果判定', '开单医生'],
    drillDownData: [
      ['2026-03-30', '周杰', 'C13呼气试验', 'DOB=15.2', '阳性(+)', '体检科自动开单'],
      ['2026-03-30', '刘华', 'C13呼气试验', 'DOB=22.1', '阳性(+)', '体检科自动开单'],
      ['2026-03-29', '郭富', 'C13呼气试验', 'DOB=18.5', '阳性(+)', '体检科自动开单']
    ]
  }
]

// 状态筛选
const statusTabs = [
  { label: '全部预警', value: 'all' },
  { label: '待处理', value: 'pending' },
  { label: '已核实处理', value: 'processed' }
]

// 筛选状态
const filterDate = ref('2026-Q1')
const filterHospital = ref('all')
const filterCategory = ref('all')
const filterRule = ref('all')
const filterStatus = ref('all')
const selectedItem = ref<AlertItem>(mockStatisticalAlerts[1])

// 计算属性
const pendingCount = computed(() => mockStatisticalAlerts.filter(a => a.status === 'pending').length)

const filteredAlerts = computed(() => {
  return mockStatisticalAlerts.filter(a => {
    const matchHospital = filterHospital.value === 'all' || a.hospital.includes(filterHospital.value)
    const matchCategory = filterCategory.value === 'all' || a.categoryId === filterCategory.value
    const matchRule = filterRule.value === 'all' || a.ruleId === filterRule.value
    const matchStatus = filterStatus.value === 'all' || a.status === filterStatus.value
    return matchHospital && matchCategory && matchRule && matchStatus
  })
})

// 动态图表组件
import { defineComponent, h } from 'vue'

const BarThresholdChart = defineComponent({
  props: { item: Object as () => AlertItem },
  setup(props) {
    return () => {
      const data = props.item!.chartData as ChartPoint[]
      const maxVal = Math.max(...data.map(d => Math.max(d.value, d.limit || 0))) * 1.2
      const thresholdY = data[0]?.limit ? (data[0].limit / maxVal) * 100 : 80

      return h('div', { class: 'w-full h-full relative pl-8 pb-6 pt-4' }, [
        // Y轴线
        h('div', { class: 'absolute left-8 top-4 bottom-6 w-px bg-[#E6E9F2]' }),
        // X轴线
        h('div', { class: 'absolute left-8 bottom-6 right-0 h-px bg-[#E6E9F2]' }),
        // 阈值虚线
        h('div', {
          class: 'absolute left-8 right-0 border-t-2 border-dashed z-0 flex items-center',
          style: { bottom: `calc(1.5rem + ${thresholdY}%)` }
        }, [
          h('span', { class: 'absolute -right-2 -top-3 rounded bg-white px-1 text-[10px] font-bold text-[#E5455F]' }, '阈值线')
        ]),
        // 柱状图
        h('div', { class: 'absolute left-8 bottom-6 right-0 top-4 flex justify-around items-end' },
          data.map((d, idx) =>
            h('div', { key: idx, class: 'flex flex-col items-center h-full justify-end z-10 w-12 group relative' }, [
              h('span', {
                class: 'absolute -top-6 rounded bg-white px-1 text-xs font-bold opacity-0 group-hover:opacity-100 transition-opacity shadow-sm',
                style: { color: d.value > (d.limit || 0) ? '#E5455F' : '#0A6EFD' }
              }, d.value),
              h('div', {
                class: 'w-10 rounded-t-sm shadow-sm transition-all duration-500',
                style: {
                  height: `${(d.value / maxVal) * 100}%`,
                  backgroundColor: d.value > (d.limit || 0) ? '#E5455F' : '#0A6EFD'
                }
              }),
              h('span', { class: 'absolute -bottom-6 w-max text-xs font-medium text-[#596080]' }, d.label)
            ])
          )
        )
      ])
    }
  }
})

const PieChartDisplay = defineComponent({
  props: { item: Object as () => AlertItem },
  setup(props) {
    return () => {
      const data = props.item!.chartData as ChartPoint[]
      const main = data[0]
      const other = data[1]

      return h('div', { class: 'w-full h-full flex items-center justify-center space-x-6' }, [
        // 饼图
        h('div', {
          class: 'w-36 h-36 rounded-full shadow-inner relative',
          style: { background: `conic-gradient(#E5455F 0% ${main.value}%, #E6E9F2 ${main.value}% 100%)` }
        }, [
          h('div', { class: 'absolute inset-0 m-auto w-20 h-20 rounded-full flex flex-col items-center justify-center bg-white shadow-sm' }, [
            h('span', { class: 'text-xl font-bold text-[#E5455F]' }, `${main.value}%`),
            h('span', { class: 'text-[10px] text-[#596080]' }, '超标占比')
          ])
        ]),
        // 图例
        h('div', { class: 'flex flex-col space-y-3' }, [
          h('div', { class: 'flex items-center' }, [
            h('div', { class: 'w-3 h-3 rounded-sm mr-2 shadow-sm', style: { backgroundColor: '#E5455F' } }),
            h('span', { class: 'text-sm font-medium text-[#1F264D]' }, `${main.label} (${main.value}%)`)
          ]),
          h('div', { class: 'flex items-center' }, [
            h('div', { class: 'w-3 h-3 rounded-sm mr-2 shadow-sm', style: { backgroundColor: '#E6E9F2' } }),
            h('span', { class: 'text-sm text-[#596080]' }, `${other.label} (${other.value}%)`)
          ]),
          h('div', { class: 'mt-2 rounded border border-red-100 bg-red-50 p-1.5 text-[10px] font-medium text-[#E5455F]' }, '红线要求：不得高于 50%')
        ])
      ])
    }
  }
})

const TimelineChart = defineComponent({
  props: { item: Object as () => AlertItem },
  setup(props) {
    return () => {
      const visits = props.item!.chartData as TimelinePoint[]

      return h('div', { class: 'w-full h-full overflow-y-auto py-2 px-4 relative' }, [
        h('div', { class: 'absolute left-[23px] top-4 bottom-4 w-px bg-[#0A6EFD]/30' }),
        h('div', { class: 'space-y-4' },
          visits.map((visit, idx) =>
            h('div', { key: idx, class: 'relative pl-8' }, [
              h('div', { class: 'absolute left-[3px] top-1.5 w-3 h-3 rounded-full border-2 border-white bg-[#0A6EFD] shadow-sm z-10' }),
              h('div', { class: 'group cursor-pointer rounded border border-[#E6E9F2] bg-[#F7F9FC] p-2 shadow-sm transition-colors hover:border-[#0A6EFD]/50' }, [
                h('div', { class: 'flex items-center justify-between mb-1' }, [
                  h('span', { class: 'text-xs font-bold text-[#1F264D]' }, visit.date),
                  h('span', { class: 'rounded bg-[#EEF2FF] px-1.5 py-0.5 text-[10px] font-bold text-[#0A6EFD]' }, visit.hospital)
                ]),
                h('div', { class: 'text-xs font-bold text-[#E5455F] group-hover:text-[#C2385A] transition-colors' }, `【高危】 ${visit.diagnosis}`)
              ])
            ])
          )
        )
      ])
    }
  }
})

const ZeroBarChart = defineComponent({
  props: { item: Object as () => AlertItem },
  setup(props) {
    return () => {
      const data = props.item!.chartData as ChartPoint[]

      return h('div', { class: 'w-full h-full relative pl-8 pb-6 pt-4 bg-[#F7F9FC]/50 rounded overflow-hidden' }, [
        // 背景水印
        h('div', { class: 'absolute inset-0 flex items-center justify-center pointer-events-none' }, [
          h('span', { class: 'transform -rotate-12 rounded border-2 border-[#E6E9F2] px-3 py-1 text-sm font-bold text-[#B8BCCC]' }, '连续三个月零数据')
        ]),
        // X轴线
        h('div', { class: 'absolute left-8 bottom-6 right-0 h-px bg-[#E6E9F2]' }),
        // 柱子（极细）
        h('div', { class: 'absolute left-8 bottom-6 right-0 top-4 flex justify-around items-end' },
          data.map((d, idx) =>
            h('div', { key: idx, class: 'flex flex-col items-center h-full justify-end z-10 w-12 relative' }, [
              h('div', { class: 'w-10 rounded-t-sm shadow-sm', style: { height: '4px', backgroundColor: '#B8BCCC' } }),
              h('span', { class: 'absolute -bottom-6 text-xs font-bold text-[#596080]' }, d.label)
            ])
          )
        )
      ])
    }
  }
})

const DualBarChart = defineComponent({
  props: { item: Object as () => AlertItem },
  setup(props) {
    return () => {
      const data = props.item!.chartData as ChartPoint[]
      const maxVal = Math.max(...data.map(d => Math.max(d.value, d.limit || 0))) * 1.2
      const thresholdY = data[0]?.limit ? (data[0].limit / maxVal) * 100 : 80

      return h('div', { class: 'w-full h-full relative pl-8 pb-6 pt-4' }, [
        h('div', { class: 'absolute left-8 top-4 bottom-6 w-px bg-[#E6E9F2]' }),
        h('div', { class: 'absolute left-8 bottom-6 right-0 h-px bg-[#E6E9F2]' }),
        h('div', {
          class: 'absolute left-8 right-0 border-t-2 border-dashed z-0 flex items-center',
          style: { bottom: `calc(1.5rem + ${thresholdY}%)` }
        }, [
          h('span', { class: 'absolute -right-2 -top-3 rounded bg-white px-1 text-[10px] font-bold text-[#E5455F]' }, '80% 阈值')
        ]),
        h('div', { class: 'absolute left-8 bottom-6 right-0 top-4 flex justify-around items-end' },
          data.map((d, idx) =>
            h('div', { key: idx, class: 'flex flex-col items-center h-full justify-end z-10 w-12 group relative' }, [
              h('span', {
                class: 'absolute -top-6 rounded bg-white px-1 text-xs font-bold opacity-0 group-hover:opacity-100 transition-opacity shadow-sm'
              }, `${d.value}%`),
              h('div', {
                class: 'w-10 rounded-t-sm shadow-md transition-all duration-300',
                style: { height: `${d.value}%`, backgroundColor: d.color || '#0A6EFD' }
              }),
              h('span', { class: 'absolute -bottom-6 w-max text-xs font-medium text-[#596080]' }, d.label)
            ])
          )
        )
      ])
    }
  }
})

function getChartComponent(item: AlertItem) {
  const map: Record<string, unknown> = {
    'bar-threshold': BarThresholdChart,
    'pie': PieChartDisplay,
    'timeline': TimelineChart,
    'zero-bar': ZeroBarChart,
    'dual-bar': DualBarChart
  }
  return map[item.chartType] || BarThresholdChart
}
</script>

<style scoped>
.alert-scroll {
  scrollbar-width: thin;
  scrollbar-color: #B8BCCC transparent;
}
.alert-scroll::-webkit-scrollbar {
  width: 6px;
}
.alert-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.alert-scroll::-webkit-scrollbar-thumb {
  background-color: #B8BCCC;
  border-radius: 3px;
}
</style>
