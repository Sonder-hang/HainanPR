<template>
  <div class="flex h-full min-h-0 flex-col bg-white">
    <!-- 执行发起区 -->
    <div class="shrink-0 border-b border-emerald-100 p-5">
      <h3 class="mb-4 flex items-center text-[13px] font-semibold text-[#1F264D]">
        <FileSpreadsheet class="mr-2 h-4 w-4 text-emerald-500" />
        报表中心
      </h3>
      <div class="flex flex-wrap items-end gap-3">
        <!-- 报表类型 -->
        <label class="flex flex-col gap-1 text-[12px]">
          <span class="text-[#596080]">报表类型</span>
          <select
            v-model="selectedReportType"
            class="cursor-pointer rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
          >
            <option v-for="report in reportTypes" :key="report.id" :value="report.id">
              {{ report.name }}
            </option>
          </select>
        </label>

        <!-- 时间范围 -->
        <label class="flex flex-col gap-1 text-[12px]">
          <span class="text-[#596080]">时间范围</span>
          <select
            v-model="timeRange"
            class="cursor-pointer rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
          >
            <option value="month">本月</option>
            <option value="quarter">本季度</option>
            <option value="year">本年</option>
            <option value="custom">自定义</option>
          </select>
        </label>

        <!-- 自定义时间范围 -->
        <template v-if="timeRange === 'custom'">
          <label class="flex flex-col gap-1 text-[12px]">
            <span class="text-[#596080]">开始日期</span>
            <input
              v-model="startDate"
              type="date"
              class="rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
            />
          </label>
          <label class="flex flex-col gap-1 text-[12px]">
            <span class="text-[#596080]">结束日期</span>
            <input
              v-model="endDate"
              type="date"
              class="rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
            />
          </label>
        </template>

        <!-- 医疗机构 -->
        <label class="flex flex-col gap-1 text-[12px]">
          <span class="text-[#596080]">医疗机构</span>
          <select
            v-model="selectedHospital"
            class="cursor-pointer rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
          >
            <option value="all">全部机构</option>
            <option v-for="h in hospitalOptions" :key="h.value" :value="h.value">
              {{ h.label }}
            </option>
          </select>
        </label>

        <!-- 生成简报按钮 -->
        <button
          type="button"
          class="flex items-center gap-1.5 rounded-[2px] border border-blue-400 bg-white px-4 py-2 text-[12px] text-blue-600 transition-colors hover:bg-blue-50"
          @click="showBriefModal = true"
        >
          <FileText class="h-4 w-4" />
          生成简报
        </button>

        <!-- 生成按钮 -->
        <button
          type="button"
          class="flex items-center gap-1.5 rounded-[2px] bg-emerald-600 px-5 py-2 text-[12px] text-white transition-colors hover:bg-emerald-700"
          :disabled="generating"
          @click="generateReport"
        >
          <Download class="h-4 w-4" />
          {{ generating ? '生成中...' : '生成报表' }}
        </button>
      </div>
    </div>

    <!-- 简报生成弹窗 -->
    <div v-if="showBriefModal" class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/40 backdrop-blur-sm" @click.self="showBriefModal = false">
      <div class="w-[420px] rounded-lg bg-white shadow-2xl">
        <div class="flex items-center justify-between border-b border-gray-100 px-5 py-4">
          <h3 class="text-[14px] font-semibold text-[#1F264D]">生成简报</h3>
          <button class="text-gray-400 hover:text-gray-600" @click="showBriefModal = false">
            <X class="h-5 w-5" />
          </button>
        </div>
        <div class="px-5 py-5">
          <div class="mb-5">
            <label class="mb-2 block text-[12px] font-medium text-[#596080]">简报期数</label>
            <div class="flex gap-2">
              <label class="flex items-center gap-2 text-[12px] text-[#1F264D]">
                <input v-model="briefPeriodType" type="radio" value="new" class="accent-emerald-600" />
                生成新一期
              </label>
              <label class="flex items-center gap-2 text-[12px] text-[#1F264D]">
                <input v-model="briefPeriodType" type="radio" value="custom" class="accent-emerald-600" />
                指定期数
              </label>
            </div>
          </div>

          <div v-if="briefPeriodType === 'custom'" class="mb-5">
            <label class="mb-2 block text-[12px] font-medium text-[#596080]">期数选择</label>
            <div class="flex gap-3">
              <label class="flex flex-col gap-1 text-[12px]">
                <span class="text-[#596080]">第几期</span>
                <input
                  v-model="briefPeriodNumber"
                  type="number"
                  min="1"
                  placeholder="如：1"
                  class="w-24 rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
                />
              </label>
              <label class="flex flex-col gap-1 text-[12px]">
                <span class="text-[#596080]">年份</span>
                <input
                  v-model="briefPeriodYear"
                  type="number"
                  min="2020"
                  placeholder="如：2026"
                  class="w-24 rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
                />
              </label>
              <label class="flex flex-col gap-1 text-[12px]">
                <span class="text-[#596080]">月份</span>
                <input
                  v-model="briefPeriodMonth"
                  type="number"
                  min="1"
                  max="12"
                  placeholder="如：1"
                  class="w-20 rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
                />
              </label>
            </div>
            <p class="mt-1.5 text-[11px] text-[#B8BCCC]">格式示例：第1期，2026年1月</p>
          </div>

          <div class="mb-5 rounded-[2px] bg-emerald-50/60 border border-emerald-100 px-4 py-3">
            <p class="text-[12px] text-[#596080]">提示：简报将按模板生成，包含七个监管规则的数据分析结果，支持导出为 Word 文档。</p>
          </div>
        </div>
        <div class="flex justify-end gap-2 border-t border-gray-100 px-5 py-4">
          <button
            type="button"
            class="rounded-[2px] border border-gray-200 px-4 py-2 text-[12px] text-gray-600 transition-colors hover:bg-gray-50"
            @click="showBriefModal = false"
          >
            取消
          </button>
          <button
            type="button"
            class="flex items-center gap-1.5 rounded-[2px] bg-blue-600 px-4 py-2 text-[12px] text-white transition-colors hover:bg-blue-700"
            :disabled="generatingBrief"
            @click="confirmGenerateBrief"
          >
            <FileText class="h-4 w-4" />
            {{ generatingBrief ? '生成中...' : '确认生成' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 报表预览区 -->
    <div class="flex min-h-0 flex-1 flex-col overflow-hidden px-5 pb-5 pt-4">
      <div class="mb-3 flex items-center justify-between">
        <h3 class="flex items-center text-[13px] font-semibold text-[#1F264D]">
          <Eye class="mr-2 h-4 w-4 text-[#596080]" />
          报表预览
        </h3>
        <div class="flex items-center gap-2">
          <button
            v-if="reportData"
            type="button"
            class="flex items-center gap-1.5 rounded-[2px] bg-emerald-600 px-4 py-2 text-[12px] text-white transition-colors hover:bg-emerald-700"
            @click="exportExcel"
          >
            <FileDown class="h-4 w-4" />
            导出 Excel
          </button>
        </div>
      </div>

      <div class="min-h-0 flex-1 overflow-hidden rounded-[2px] border border-[#b8c9e8]/60 bg-white shadow-sm">
        <div v-if="!reportData" class="flex h-full items-center justify-center">
          <div class="text-center text-[#B8BCCC]">
            <FileSpreadsheet class="mx-auto mb-3 h-16 w-16 text-[#d1d5db]" />
            <p class="text-[14px]">请选择报表类型并点击"生成报表"</p>
            <p class="mt-1 text-[12px]">生成的报表将显示在此处</p>
          </div>
        </div>
        <div v-else ref="reportPreviewRef" class="h-full overflow-auto p-6">
          <!-- 报表标题 -->
          <div class="mb-6 text-center">
            <h1 class="text-[20px] font-bold text-[#1F264D]">{{ currentReport?.name }}</h1>
            <p class="mt-1 text-[12px] text-[#596080]">
              统计周期：{{ timeRangeLabel }} | 生成时间：{{ new Date().toLocaleString('zh-CN') }}
            </p>
          </div>

          <!-- 报表内容 -->
          <div class="overflow-x-auto">
            <table class="w-full border-collapse text-left text-[12px]">
              <thead>
                <tr class="bg-emerald-50">
                  <th
                    v-for="header in reportData.headers"
                    :key="header"
                    class="border border-[#b8c9e8]/60 px-3 py-2 font-semibold text-[#1F264D]"
                  >
                    {{ header }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(row, index) in reportData.rows"
                  :key="index"
                  class="border border-[#b8c9e8]/60 hover:bg-emerald-50/40"
                >
                  <td
                    v-for="(cell, cellIndex) in row"
                    :key="cellIndex"
                    class="border border-[#b8c9e8]/60 px-3 py-2"
                    :class="getCellClass(cell)"
                  >
                    {{ cell }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载提示 -->
    <div v-if="generating" class="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/30 backdrop-blur-sm">
      <div class="rounded-lg bg-white p-6 shadow-xl">
        <div class="flex items-center gap-3">
          <div class="h-8 w-8 animate-spin rounded-full border-4 border-emerald-200 border-t-emerald-600"></div>
          <span class="text-[14px] text-[#1F264D]">正在生成报表，请稍候...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Download, Eye, FileDown, FileSpreadsheet, FileText, X } from 'lucide-vue-next'
import * as XLSX from 'xlsx'

type ReportType = {
  id: string
  name: string
  description: string
}

type ReportData = {
  headers: string[]
  rows: (string | number)[][]
  summary?: Record<string, string>
}

// 报表类型定义
const reportTypes: ReportType[] = [
  { id: 'bedAreaRatio', name: '医疗机构床位面积比符合性监测', description: '监测医疗机构床位面积是否符合标准要求' },
  { id: 'antibioticManagement', name: '抗菌药物分级管理监测', description: '监测抗菌药物分级管理执行情况' },
  { id: 'crossInstitutionDiagnosis', name: '医师跨机构诊疗异常数据监测', description: '监测医师跨机构诊疗异常情况' },
  { id: 'villageClinicWarning', name: '村卫生室年度服务量低线预警', description: '预警村卫生室年度服务量低于标准的机构' },
  { id: 'restrictedTechUsage', name: '国家级限制性技术使用监测', description: '监测国家级限制性技术使用情况' },
  { id: 'duplicateCharging', name: '重复收费监测', description: '监测可能存在重复收费的情况' },
]

const hospitalOptions = [
  { value: 'hospitalA', label: '省立第一医院' },
  { value: 'hospitalB', label: '市中心医院' },
  { value: 'hospitalC', label: '省肿瘤医院' },
  { value: 'hospitalD', label: '县人民医院' },
  { value: 'hospitalE', label: '康华医院' },
]

const selectedReportType = ref('bedAreaRatio')
const timeRange = ref('month')
const startDate = ref('')
const endDate = ref('')
const selectedHospital = ref('all')
const generating = ref(false)
const generatingBrief = ref(false)
const reportData = ref<ReportData | null>(null)
const reportPreviewRef = ref<HTMLElement | null>(null)

// 简报弹窗
const showBriefModal = ref(false)
const briefPeriodType = ref('new')
const briefPeriodNumber = ref('')
const briefPeriodYear = ref(new Date().getFullYear())
const briefPeriodMonth = ref(new Date().getMonth() + 1)

const currentReport = computed(() => reportTypes.find(r => r.id === selectedReportType.value))

const timeRangeLabel = computed(() => {
  switch (timeRange.value) {
    case 'month': return '本月'
    case 'quarter': return '本季度'
    case 'year': return '本年'
    case 'custom': return `${startDate.value} 至 ${endDate.value}`
    default: return ''
  }
})

function getCellClass(cell: string | number): string {
  if (typeof cell === 'string') {
    if (cell.includes('不符合') || cell.includes('预警') || cell.includes('异常')) {
      return 'text-red-600 font-medium'
    }
    if (cell.includes('符合') || cell.includes('正常')) {
      return 'text-emerald-600 font-medium'
    }
  }
  return 'text-[#1F264D]'
}

// 生成报表数据
async function generateReport() {
  generating.value = true
  
  // 模拟生成延迟
  await new Promise(resolve => setTimeout(resolve, 1500))
  
  reportData.value = generateMockData(selectedReportType.value)
  generating.value = false
}

// 根据报表类型生成模拟数据
function generateMockData(reportType: string): ReportData {
  switch (reportType) {
    case 'bedAreaRatio':
      return {
        headers: ['序号', '机构名称', '床位数', '实际面积(㎡)', '标准面积(㎡)', '面积比', '是否符合', '备注'],
        rows: [
          ['1', '省立第一医院', 1200, 15600, 14400, '1.08', '符合', '-'],
          ['2', '市中心医院', 800, 9800, 9600, '1.02', '符合', '-'],
          ['3', '省肿瘤医院', 600, 6800, 7200, '0.94', '不符合', '需增加面积或减少床位'],
          ['4', '县人民医院', 400, 5200, 4800, '1.08', '符合', '-'],
          ['5', '康华医院', 300, 3600, 3600, '1.00', '符合', '-'],
        ],
        summary: {
          '总机构数': '5家',
          '符合标准': '4家',
          '不符合标准': '1家',
          '符合率': '80%'
        }
      }
    
    case 'antibioticManagement':
      return {
        headers: ['序号', '机构名称', '非限制级使用率', '限制级使用率', '特殊级使用率', '越级使用次数', '管理评级', '备注'],
        rows: [
          ['1', '省立第一医院', '68%', '25%', '7%', 3, 'A级', '-'],
          ['2', '市中心医院', '72%', '22%', '6%', 5, 'B级', '-'],
          ['3', '省肿瘤医院', '65%', '28%', '7%', 8, 'B级', '越级使用略多'],
          ['4', '县人民医院', '75%', '20%', '5%', 2, 'A级', '-'],
          ['5', '康华医院', '70%', '24%', '6%', 4, 'A级', '-'],
        ],
        summary: {
          '总机构数': '5家',
          'A级机构': '3家',
          'B级机构': '2家',
          '平均越级使用': '4.4次'
        }
      }
    
    case 'crossInstitutionDiagnosis':
      return {
        headers: ['序号', '医师姓名', '执业机构', '诊疗机构', '跨机构诊疗次数', '异常类型', '风险等级', '备注'],
        rows: [
          ['1', '张某某', '省立第一医院', '市中心医院', 45, '频繁跨机构', '高', '需核查'],
          ['2', '李某某', '市中心医院', '省肿瘤医院', 32, '正常', '低', '-'],
          ['3', '王某某', '省肿瘤医院', '康华医院', 28, '正常', '低', '-'],
          ['4', '赵某某', '县人民医院', '省立第一医院', 56, '频繁跨机构', '高', '需重点核查'],
          ['5', '孙某某', '康华医院', '市中心医院', 18, '正常', '低', '-'],
        ],
        summary: {
          '监测医师数': '5人',
          '异常人数': '2人',
          '高风险人数': '2人',
          '需核查次数': '101次'
        }
      }
    
    case 'villageClinicWarning':
      return {
        headers: ['序号', '机构名称', '所属区域', '年度服务量', '标准下限', '完成率', '预警等级', '备注'],
        rows: [
          ['1', '阳光村卫生室', '城东区', 850, 1000, '85%', '黄色预警', '接近标准'],
          ['2', '幸福村卫生室', '城西区', 620, 1000, '62%', '红色预警', '需重点关注'],
          ['3', '和平村卫生室', '城南镇', 1100, 1000, '110%', '正常', '-'],
          ['4', '团结村卫生室', '城北镇', 980, 1000, '98%', '黄色预警', '接近标准'],
          ['5', '进步村卫生室', '开发区', 450, 1000, '45%', '红色预警', '严重不足'],
        ],
        summary: {
          '监测机构数': '5家',
          '达标机构': '1家',
          '黄色预警': '2家',
          '红色预警': '2家'
        }
      }
    
    case 'restrictedTechUsage':
      return {
        headers: ['序号', '机构名称', '技术名称', '备案数量', '实际开展', '开展率', '人员资质', '备注'],
        rows: [
          ['1', '省立第一医院', '器官移植', 20, 18, '90%', '符合', '-'],
          ['2', '市中心医院', '心脏支架介入', 50, 48, '96%', '符合', '-'],
          ['3', '省肿瘤医院', '造血干细胞移植', 15, 10, '67%', '基本符合', '开展率偏低'],
          ['4', '县人民医院', '心导管检查', 30, 28, '93%', '符合', '-'],
          ['5', '康华医院', '射频消融术', 25, 22, '88%', '符合', '-'],
        ],
        summary: {
          '监测机构数': '5家',
          '符合要求': '5家',
          '需关注': '1家',
          '平均开展率': '86.8%'
        }
      }
    
    case 'duplicateCharging':
      return {
        headers: ['序号', '机构名称', '患者ID', '收费项目', '收费次数', '涉及金额(元)', '疑似重复类型', '备注'],
        rows: [
          ['1', '省立第一医院', 'P001234', '常规心电图', 3, 90, '同日重复收费', '待核实'],
          ['2', '市中心医院', 'P005678', '血常规检查', 2, 40, '跨日重复收费', '待核实'],
          ['3', '省肿瘤医院', 'P008901', 'CT平扫', 2, 600, '剂量重复', '需核查'],
          ['4', '县人民医院', 'P002345', '超声检查', 4, 320, '项目拆分', '疑似违规'],
          ['5', '康华医院', 'P006789', '生化全套', 2, 160, '同日重复收费', '待核实'],
        ],
        summary: {
          '监测机构数': '5家',
          '疑似重复条目': '5条',
          '涉及金额': '1,210元',
          '需重点核查': '2条'
        }
      }
    
    default:
      return { headers: [], rows: [] }
  }
}

// 导出 Excel
function exportExcel() {
  if (!reportData.value) return
  
  const ws = XLSX.utils.aoa_to_sheet([
    [currentReport.value?.name || ''],
    [`统计周期：${timeRangeLabel.value}`],
    [`生成时间：${new Date().toLocaleString('zh-CN')}`],
    [],
    reportData.value.headers,
    ...reportData.value.rows,
  ])
  
  // 添加汇总
  if (reportData.value.summary) {
    const summaryRows = Object.entries(reportData.value.summary).map(([key, value]) => [key, value])
    ws['!rows'] = [
      { hpt: 30 }, // 标题行高度
      { hpt: 20 }, // 统计周期行
      { hpt: 20 }, // 生成时间行
      { hpt: 10 }, // 空行
      ...Array(reportData.value.headers.length + 1).fill({ hpt: 25 }), // 表头和数据行
      ...Array(summaryRows.length).fill({ hpt: 20 }), // 汇总行
    ]
  }
  
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '报表')
  
  const fileName = `${currentReport.value?.name}_${new Date().toISOString().slice(0, 10).replace(/-/g, '')}.xlsx`
  XLSX.writeFile(wb, fileName)
}

// 确认生成简报
async function confirmGenerateBrief() {
  let periodNumber: string
  let periodYear: number
  let periodMonth: number

  if (briefPeriodType.value === 'new') {
    periodNumber = '1'
    periodYear = new Date().getFullYear()
    periodMonth = new Date().getMonth() + 1
  } else {
    if (!briefPeriodNumber.value || !briefPeriodYear.value || !briefPeriodMonth.value) {
      alert('请填写完整的期数信息')
      return
    }
    periodNumber = String(briefPeriodNumber.value)
    periodYear = Number(briefPeriodYear.value)
    periodMonth = Number(briefPeriodMonth.value)
  }

  showBriefModal.value = false
  generatingBrief.value = true
  try {
    const params = new URLSearchParams({
      period_number: periodNumber,
      period_year: String(periodYear),
      period_month: String(periodMonth),
    })
    const response = await fetch(`/api/report/brief-report/download?${params}`)
    if (!response.ok) throw new Error('下载失败')
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const disposition = response.headers.get('Content-Disposition')
    let filename = `三医智慧监管大数据分析简报_第${periodNumber}期_${periodYear}年${String(periodMonth).padStart(2, '0')}月.docx`
    if (disposition) {
      const match = disposition.match(/filename\*?=['"]?(?:UTF-8'')?([^;\n"']+)/i)
      if (match) filename = decodeURIComponent(match[1])
    }
    a.download = filename
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('生成简报失败:', error)
    alert('生成简报失败，请重试')
  } finally {
    generatingBrief.value = false
  }
}

// 导出图片
async function exportImage() {
  if (!reportPreviewRef.value) return
  
  try {
    const canvas = await html2canvas(reportPreviewRef.value, {
      scale: 2,
      useCORS: true,
      backgroundColor: '#ffffff'
    })
    
    const link = document.createElement('a')
    link.download = `${currentReport.value?.name}_${new Date().toISOString().slice(0, 10).replace(/-/g, '')}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
  } catch (error) {
    console.error('导出图片失败:', error)
    alert('导出图片失败，请重试')
  }
}
</script>
