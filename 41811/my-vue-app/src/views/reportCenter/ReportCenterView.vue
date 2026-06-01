<template>
  <div class="flex h-full min-h-0 flex-col bg-white">
    <!-- 执行发起区 -->
    <div class="shrink-0 border-b border-emerald-100 p-5">
      <div class="flex items-start gap-6">
        <div class="flex-1">
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
                class="h-9 min-h-9 w-[200px] cursor-pointer appearance-none rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 pr-8 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
                style="background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2224%22%20height%3D%2224%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2394a3b8%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M6%209l6%206%206-6%22%2F%3E%3C%2Fsvg%3E'); background-repeat: no-repeat; background-position: right 0.5rem center; background-size: 1em;"
              >
                <option v-for="report in reportTypes" :key="report.id" :value="report.id">
                  {{ report.name }}
                </option>
              </select>
            </label>

            <!-- 执行方式 + 时间选择（始终渲染，用 v-show 切换，高度固定） -->
            <div class="rounded border border-[#b8c9e8]/40 bg-[#f8faff] p-3">
              <div class="flex items-end gap-3">
                <!-- 执行方式 -->
                <label class="flex flex-col gap-1 text-[12px]">
                  <span class="text-[#596080]">执行方式</span>
                  <div class="flex gap-1">
                    <button
                      v-for="m in REPORT_MODE_OPTIONS"
                      :key="m.value"
                      type="button"
                      class="rounded-[2px] border px-3 py-2 text-[12px] transition-colors"
                      :class="reportMode === m.value
                        ? 'border-emerald-400 bg-emerald-50 text-emerald-700 font-medium'
                        : 'border-[#b8c9e8] bg-white text-[#596080] hover:border-emerald-200'"
                      @click="reportMode = m.value"
                    >{{ m.label }}</button>
                  </div>
                </label>

                <!-- 月份选择 -->
                <label v-show="reportMode === 'monthly'" class="flex flex-col gap-1 text-[12px]">
                  <span class="text-[#596080]">选择月份</span>
                  <div class="flex gap-1">
                    <select
                      v-model="selectedMonthYear"
                      class="h-9 min-h-9 cursor-pointer rounded-[2px] border border-[#b8c9e8]/60 bg-white px-2 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
                    >
                      <option v-for="y in monthYearOptions" :key="y" :value="y">{{ y }}年</option>
                    </select>
                    <select
                      v-model="selectedMonthNum"
                      class="h-9 min-h-9 cursor-pointer rounded-[2px] border border-[#b8c9e8]/60 bg-white px-2 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
                    >
                      <option v-for="m in MONTH_OPTIONS" :key="m.value" :value="m.value">{{ m.label }}</option>
                    </select>
                  </div>
                </label>

                <!-- 季度选择 -->
                <label v-show="reportMode === 'quarterly'" class="flex flex-col gap-1 text-[12px]">
                  <span class="text-[#596080]">选择年份</span>
                  <select
                    v-model="selectedQuarterYear"
                    class="h-9 min-h-9 cursor-pointer rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
                  >
                    <option v-for="y in quarterYearOptions" :key="y" :value="y">{{ y }}年</option>
                  </select>
                </label>
                <label v-show="reportMode === 'quarterly'" class="flex flex-col gap-1 text-[12px]">
                  <span class="text-[#596080]">选择季度</span>
                  <select
                    v-model="selectedQuarterNum"
                    class="h-9 min-h-9 cursor-pointer rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
                  >
                    <option v-for="q in quarterOptionsOfYear" :key="q.value" :value="q.value">{{ q.label }}</option>
                  </select>
                </label>
              </div>
            </div>

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
import { ref, computed, watch } from 'vue'
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

// 报表类型定义（对应赛思7个附件，删除超范围用药）
const reportTypes: ReportType[] = [
  { id: 'antibioticManagement',      name: '抗菌药物分级管理监测',       description: '附件1：抗菌药物分级管理监测，监测特殊使用级抗菌药物越权使用情况' },
  { id: 'crossInstitutionDiagnosis', name: '医师跨机构诊疗异常数据监测', description: '附件2：医师跨机构诊疗异常监测，监测同一医师短时间内不同机构开医嘱情况' },
  { id: 'restrictedTechUsage',       name: '国家级限制性技术使用监测',    description: '附件3：国家级限制性技术使用监测，监测限制类技术超范围开展情况' },
  { id: 'practiceOverdue',          name: '医师执业超期异常监控',        description: '附件4：医师执业超期异常监控，监测诊疗时间超出多点执业备案有效期的情况' },
  { id: 'practiceLocation',         name: '医师执业地点异常监控',        description: '附件5：医师执业地点异常监控，监测在未备案机构开展诊疗活动的情况' },
  { id: 'minorProtection',          name: '未成年人异常诊疗情形监测',    description: '附件7：未成年人异常诊疗情形监测，识别疑似侵害未成年人线索' },
]

const selectedReportType = ref('minorProtection')

type ReportMode = 'immediate' | 'monthly' | 'quarterly'
const REPORT_MODE_OPTIONS = [
  { value: 'monthly'   as ReportMode, label: '按月' },
  { value: 'quarterly' as ReportMode, label: '按季度' },
]
const reportMode = ref<ReportMode>('monthly')

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
const selectedMonthNum = ref(String(new Date().getMonth() + 1).padStart(2, '0'))

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
  switch (reportMode.value) {
    case 'monthly':
      return `${selectedMonthYear.value}年${Number(selectedMonthNum.value)}月`
    case 'quarterly':
      const qmap: Record<string, string> = { '1': '一', '2': '二', '3': '三', '4': '四' }
      return `${selectedQuarterYear.value}年${qmap[selectedQuarterNum.value]}季度`
    default:
      return ''
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
  try {
    const body: Record<string, unknown> = {
      report_type: selectedReportType.value,
    }
    if (reportMode.value === 'monthly') {
      body.time_mode = 'monthly'
      body.time_value = `${selectedMonthYear.value}-${selectedMonthNum.value}`
    } else {
      body.time_mode = 'quarterly'
      body.time_value = `${selectedQuarterYear.value}-Q${selectedQuarterNum.value}`
    }

    const res = await fetch('/api/report/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: '未知错误' }))
      alert('生成报表失败：' + (err.detail || res.statusText))
      reportData.value = null
    } else {
      const json = await res.json()
      if (json.headers && json.headers.length > 0) {
        reportData.value = {
          headers: json.headers,
          rows: json.rows,
          summary: json.summary || {},
        }
      } else {
        reportData.value = {
          headers: [],
          rows: [],
          summary: { '预警总数': json.total_count || 0, '执行状态': json.ok ? '成功' : '失败' },
        }
      }
    }
  } catch (e) {
    console.error('报表生成失败', e)
    alert('报表生成失败，请检查后端服务是否启动')
    reportData.value = null
  }
  generating.value = false
}

// 导出 Excel（全量数据，不走预览的 limit）
async function exportExcel() {
  if (!reportData.value) return

  generating.value = true
  try {
    const body: Record<string, unknown> = {
      report_type: selectedReportType.value,
    }
    if (reportMode.value === 'monthly') {
      body.time_mode = 'monthly'
      body.time_value = `${selectedMonthYear.value}-${selectedMonthNum.value}`
    } else {
      body.time_mode = 'quarterly'
      body.time_value = `${selectedQuarterYear.value}-Q${selectedQuarterNum.value}`
    }

    const res = await fetch('/api/report/export-full', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: '未知错误' }))
      alert('导出失败：' + (err.detail || res.statusText))
      return
    }

    const fullData = await res.json()
    const headers = fullData.headers || []
    const rows = fullData.rows || []

    const ws = XLSX.utils.aoa_to_sheet([
      [currentReport.value?.name || ''],
      [`统计周期：${timeRangeLabel.value}`],
      [`导出时间：${new Date().toLocaleString('zh-CN')}`],
      [`数据总量：${fullData.total || rows.length} 条`],
      [],
      headers,
      ...rows,
    ])

    ws['!cols'] = headers.map(() => ({ wch: 18 }))

    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '报表')
    const fileName = `${currentReport.value?.name}_${new Date().toISOString().slice(0, 10).replace(/-/g, '')}.xlsx`
    XLSX.writeFile(wb, fileName)
  } catch (e) {
    console.error('导出失败', e)
    alert('导出失败，请检查后端服务')
  } finally {
    generating.value = false
  }
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
