<template>
  <div class="mx-auto max-w-[1400px] pb-10">
    <!-- 顶栏 -->
    <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
      <div class="flex flex-wrap items-center gap-3">
        <button
          type="button"
          class="flex items-center gap-1.5 rounded-[2px] border border-[#b8c9e8]/80 bg-white px-3 py-2 text-[12px] text-[#1F264D] shadow-sm transition-colors hover:bg-[#e8eef9]"
          @click="goBack"
        >
          <ArrowLeft class="h-3.5 w-3.5" />
          返回指标管理
        </button>
        <h1 class="text-[16px] font-bold text-[#1F264D]">指标调试新增</h1>
      </div>
      <button
        type="button"
        class="rounded-[2px] bg-emerald-600 px-4 py-2 text-[12px] text-white shadow-sm transition-colors hover:bg-emerald-700"
        :disabled="busy || !hasSql"
        @click="handleSave"
      >
        {{ templateId ? '保存' : '保存为新指标' }}
      </button>
    </div>

    <!-- 配置区 -->
    <div class="space-y-4 rounded-[2px] border border-[#b8c9e8]/60 bg-white p-5 shadow-sm">
      <div class="grid gap-4 md:grid-cols-2">
        <label class="block text-[12px]">
          <span class="mb-1 block font-medium text-[#596080]">指标类别</span>
          <select
            v-model="kind"
            class="w-full cursor-pointer rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] focus:border-[#0A6EFD] focus:outline-none"
          >
            <option value="core18">十八项核心制度指标</option>
            <option value="four">四要素监管指标</option>
          </select>
        </label>
        <label class="block text-[12px]">
          <span class="mb-1 block font-medium text-[#596080]">选择指标（可选已有项作为模板）</span>
          <SearchableSelect
            v-model="templateId"
            :options="templateOptions"
            placeholder="— 不引用模板，完全新建 —"
            search-placeholder="输入关键词搜索指标…"
            @change="onTemplateChange"
          />
        </label>
      </div>

      <label v-if="kind === 'core18'" class="block text-[12px]">
        <span class="mb-1 block font-medium text-[#596080]">新指标名称</span>
        <input
          v-model="newIndicatorName"
          type="text"
          placeholder="保存时使用；若引用模板可在此基础上修改名称"
          class="w-full rounded-[2px] border border-[#b8c9e8]/60 px-3 py-2 text-[12px] focus:border-[#0A6EFD] focus:outline-none"
        />
      </label>

      <div v-else>
        <label class="block text-[12px]">
          <span class="mb-1 block font-medium text-[#596080]">类别（保存必填）</span>
          <input
            v-model="fourCategory"
            type="text"
            placeholder="如：人员要素"
            class="w-full rounded-[2px] border border-[#b8c9e8]/60 px-3 py-2 text-[12px] focus:border-[#0A6EFD] focus:outline-none"
          />
        </label>
      </div>

      <!-- 计算类型（仅十八项核心制度指标） -->
      <template v-if="kind === 'core18'">
        <label class="block text-[12px]">
          <span class="mb-1 block font-medium text-[#596080]">计算类型</span>
          <div class="flex flex-wrap gap-3">
            <label class="flex cursor-pointer items-center gap-1.5">
              <input v-model="calcType" type="radio" value="ratio" class="accent-emerald-600" />
              <span class="text-[12px] text-[#1F264D]">比值型</span>
            </label>
            <label class="flex cursor-pointer items-center gap-1.5">
              <input v-model="calcType" type="radio" value="count" class="accent-emerald-600" />
              <span class="text-[12px] text-[#1F264D]">计数型</span>
            </label>
          </div>
        </label>
        <p class="mt-0.5 text-[11px] text-[#596080]">
          <span v-if="calcType === 'ratio'">填写分子 SQL 与分母 SQL，计算比值 = 分子 ÷ 分母 × 100%</span>
          <span v-else-if="calcType === 'count'">仅填写一条 SQL 语句，直接输出计数结果</span>
        </p>
      </template>

      <!-- 涉及表 -->
      <div>
        <p class="mb-2 text-[12px] font-medium text-[#596080]">涉及表（可多选）</p>
        <div class="flex flex-wrap gap-x-4 gap-y-2 rounded-[2px] border border-[#b8c9e8]/60 bg-[#fafbff] px-3 py-2.5">
          <label
            v-for="t in availableTables"
            :key="t.code"
            class="flex cursor-pointer items-center gap-1.5 text-[11px] text-[#334155] hover:text-emerald-600"
          >
            <input
              type="checkbox"
              :value="t.code"
              v-model="selectedTables"
              class="accent-emerald-600"
            />
            <span class="font-medium">{{ t.label }}</span>
            <span class="text-[10px] text-[#94a3b8]">{{ t.code }}</span>
          </label>
        </div>
        <p class="mt-1 text-[11px] text-[#94a3b8]">
          已选 {{ selectedTables.length }} 张表，已选表名：
          <span class="font-mono text-[10px]">{{ selectedTables.join(', ') || '—' }}</span>
        </p>
      </div>

      <label class="block text-[12px]">
        <span class="mb-1 flex items-center justify-between font-medium text-[#596080]">
          <span>指标计算公式（自然语言）</span>
          <Sparkles class="h-3.5 w-3.5 text-pink-400" aria-hidden="true" />
        </span>
        <div class="relative">
          <textarea
            v-model="formulaText"
            rows="4"
            placeholder="例：同期入院8小时内已下达检查或治疗医嘱的患者人次数 / 同期入院患者总人次数 × 100%"
            class="w-full resize-y rounded-[2px] border border-[#b8c9e8]/60 bg-[#fafbff] px-3 py-2.5 pr-10 text-[12px] leading-relaxed focus:border-[#0A6EFD] focus:outline-none"
          />
        </div>
      </label>

      <label class="block text-[12px]">
        <span class="mb-1 block font-medium text-[#596080]">补充信息（建议写明分子、分母口径或规则说明）</span>
        <textarea
          v-model="supplementaryText"
          rows="5"
          placeholder="分母：…&#10;分子：…&#10;（或四要素：范围、工作内容、规则逻辑等）"
          class="w-full resize-y rounded-[2px] border border-[#b8c9e8]/60 px-3 py-2.5 text-[12px] leading-relaxed focus:border-[#0A6EFD] focus:outline-none"
        />
      </label>

      <div class="flex flex-wrap items-center gap-2">
        <button
          type="button"
          class="rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-1.5 text-[11px] text-[#596080] hover:bg-slate-50"
          @click="restoreTemplateDefaults"
        >
          公式与补充信息恢复为当前指标文件默认
        </button>
      </div>

      <label class="block text-[12px]">
        <span class="mb-1 block font-medium text-[#596080]">再生成时附加说明（可选）</span>
        <input
          v-model="regenerateHint"
          type="text"
          placeholder="例：关联键统一使用 INHOS_NO"
          class="w-full rounded-[2px] border border-[#b8c9e8]/60 px-3 py-2 text-[12px] focus:border-[#0A6EFD] focus:outline-none"
        />
      </label>

      <div class="flex flex-wrap items-center gap-3 border-t border-[#e8eef9] pt-4">
        <button
          type="button"
          class="rounded-[2px] bg-[#0A6EFD] px-5 py-2.5 text-[12px] font-medium text-white shadow-sm transition-colors hover:bg-[#0958d9]"
          :disabled="busy"
          @click="generateAndExecute(false)"
        >
          {{ busy ? '执行中…' : '生成并执行' }}
        </button>
        <button
          type="button"
          class="rounded-[2px] border border-[#0A6EFD]/40 bg-white px-4 py-2 text-[12px] text-[#0A6EFD] transition-colors hover:bg-blue-50"
          :disabled="busy || !hasPreviousSql"
          @click="generateAndExecute(true)"
        >
          用上次 SQL + 说明再生成
        </button>
        <label class="flex cursor-pointer items-center gap-2 text-[12px] text-[#596080]">
          <input v-model="streamOutput" type="checkbox" class="rounded border-[#b8c9e8]" />
          流式显示模型输出
        </label>
      </div>

      <!-- 流式日志 -->
      <div
        v-if="streamLog"
        class="max-h-32 overflow-y-auto rounded-[2px] border border-slate-200 bg-[#1e293b] p-3 font-mono text-[10px] text-slate-200"
      >
        <pre class="whitespace-pre-wrap">{{ streamLog }}</pre>
      </div>

      <!-- 错误提示 -->
      <div v-if="executeError" class="rounded-[2px] border border-red-200 bg-red-50 p-3 text-[12px] text-red-600">
        {{ executeError }}
      </div>
    </div>

    <!-- 分子 / 分母 双栏（计数型时单栏） -->
    <div class="mt-5 grid gap-4 lg:grid-cols-2">

      <!-- 左侧：分子 SQL（或单一 SQL） -->
      <section class="flex min-h-[420px] flex-col rounded-[2px] border border-[#b8c9e8]/60 bg-white shadow-sm">
        <div class="border-b border-[#e8eef9] bg-sky-50/80 px-4 py-2.5 text-[13px] font-semibold text-[#1F264D]">
          <template v-if="kind === 'core18' && calcType === 'count'">
            SQL 语句
          </template>
          <template v-else>
            {{ kind === 'core18' ? '分子' : '主规则 SQL' }}
          </template>
        </div>
        <div class="min-h-0 flex-1 p-4">
          <p class="mb-1.5 text-[11px] font-medium text-[#596080]">SQL</p>
          <textarea
            v-model="sqlNumerator"
            readonly
            rows="10"
            class="mb-4 w-full resize-y rounded-[2px] border border-sky-200/80 bg-sky-50/40 px-2.5 py-2 font-mono text-[11px] leading-relaxed text-[#334155]"
          />
          <p class="mb-1.5 text-[11px] font-medium text-[#596080]">查询结果预览</p>
          <div class="min-h-[140px] overflow-auto rounded-[2px] border border-dashed border-[#b8c9e8]/80 bg-[#f8fafc] p-2">
            <table v-if="previewNum.rows.length" class="w-full border-collapse text-left text-[11px]">
              <thead>
                <tr class="border-b border-[#b8c9e8]/60 bg-white">
                  <th
                    v-for="h in previewNum.headers"
                    :key="h"
                    class="px-2 py-1.5 font-semibold text-[#596080]"
                  >{{ h }}</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#e8eef9]">
                <tr v-for="(r, ri) in previewNum.rows" :key="ri" class="bg-white/80">
                  <td v-for="h in previewNum.headers" :key="h" class="px-2 py-1.5 text-[#1F264D]">
                    {{ r[h] }}
                  </td>
                </tr>
              </tbody>
            </table>
            <p v-else class="py-8 text-center text-[12px] text-[#94a3b8]">执行后将显示表格</p>
          </div>
        </div>
      </section>

      <!-- 右侧：分母 SQL（仅比值型显示） -->
      <section
        v-if="!(kind === 'core18' && calcType === 'count')"
        class="flex min-h-[420px] flex-col rounded-[2px] border border-[#b8c9e8]/60 bg-white shadow-sm"
      >
        <div class="border-b border-[#e8eef9] bg-sky-50/80 px-4 py-2.5 text-[13px] font-semibold text-[#1F264D]">
          <template v-if="kind === 'core18'">
            分母
          </template>
          <template v-else>
            辅助 / 全量口径 SQL
          </template>
        </div>
        <div class="min-h-0 flex-1 p-4">
          <p class="mb-1.5 text-[11px] font-medium text-[#596080]">SQL</p>
          <textarea
            v-model="sqlDenominator"
            readonly
            rows="10"
            class="mb-4 w-full resize-y rounded-[2px] border border-sky-200/80 bg-sky-50/40 px-2.5 py-2 font-mono text-[11px] leading-relaxed text-[#334155]"
          />
          <p class="mb-1.5 text-[11px] font-medium text-[#596080]">查询结果预览</p>
          <div class="min-h-[140px] overflow-auto rounded-[2px] border border-dashed border-[#b8c9e8]/80 bg-[#f8fafc] p-2">
            <table v-if="previewDen.rows.length" class="w-full border-collapse text-left text-[11px]">
              <thead>
                <tr class="border-b border-[#b8c9e8]/60 bg-white">
                  <th
                    v-for="h in previewDen.headers"
                    :key="h"
                    class="px-2 py-1.5 font-semibold text-[#596080]"
                  >{{ h }}</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#e8eef9]">
                <tr v-for="(r, ri) in previewDen.rows" :key="ri" class="bg-white/80">
                  <td v-for="h in previewDen.headers" :key="h" class="px-2 py-1.5 text-[#1F264D]">
                    {{ r[h] }}
                  </td>
                </tr>
              </tbody>
            </table>
            <p v-else class="py-8 text-center text-[12px] text-[#94a3b8]">执行后将显示表格</p>
          </div>
        </div>
      </section>

    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Sparkles } from 'lucide-vue-next'
import SearchableSelect from '@/components/ui/SearchableSelect.vue'
import { indicatorsApi, type Indicator, type ExecuteResponse } from '@/api/indicators'

// ======================== 静态数据 ========================
const availableTables = [
  { code: 'FACT_ADMN_MDC_HTR_RCD',  label: '入院病历记录（入院病历记录）' },
  { code: 'FACT_INHOS_ODR_INFMT',    label: '住院医嘱信息' },
  { code: 'FACT_DIAG_RECORD',        label: '诊断记录' },
  { code: 'FACT_OPERATION_RECORD',   label: '手术记录' },
  { code: 'FACT_LAB_RESULT',         label: '检验结果' },
  { code: 'FACT_MDC_RCD_HMPG',       label: '病案首页' },
  { code: 'FACT_MDC_RCD_HMPG_OPRT',  label: '病案首页-手术' },
  { code: 'FACT_MDC_RCD_HMPG_DIAG',  label: '病案首页-诊断' },
  { code: 'FACT_MDC_RCD_HMPG_FEE',   label: '病案首页-费用' },
  { code: 'FACT_INHOS_DIAG_INFMT',   label: '住院诊断信息表' },
  { code: 'FACT_INHOS_CRS_RCD_S',    label: '住院病程记录' },
  { code: 'FACT_OPRT_EXEC_INFMT',    label: '手术执行信息表' },
  { code: 'FACT_OPRT_RCD_S',         label: '手术记录' },
  { code: 'FACT_POPRT_DSCS_RCD',     label: '术前讨论' },
  { code: 'FACT_EXAM_RCD',           label: '检查记录' },
  { code: 'FACT_EXAM_RPT',           label: '检查报告' },
  { code: 'FACT_TEST_APL',           label: '检验申请单' },
  { code: 'FACT_TEST_RCD',           label: '检验记录' },
  { code: 'FACT_TEST_RPT_CVT_RSLT', label: '检验报告-常规结果' },
  { code: 'FACT_PTHLG_RCD',          label: '病理记录' },
  { code: 'FACT_PTHLG_RPT',         label: '病理报告' },
  { code: 'FACT_RSC_RCD',            label: '抢救记录' },
  { code: 'FACT_OTPT_FEE_STLMT',     label: '门诊费用结算' },
  { code: 'FACT_DTH_RCD',            label: '死亡记录' },
  { code: 'DIM_CHRG_ITM_INFMT',      label: '收费项目信息表' },
  { code: 'DIM_DRG_INFMT',           label: '药品信息' },
  { code: 'DIM_MDC_ORG',            label: '医疗机构' },
]

const defaultIndicatorList = ref<Indicator[]>([])

// ======================== 状态 ========================
const route = useRoute()
const router = useRouter()

const kind = ref<'core18' | 'four'>(
  route.query.kind === 'four' ? 'four' : 'core18',
)
const calcType = ref<'ratio' | 'count'>('ratio')

const templateId = ref('')
const newIndicatorName = ref('')
const fourCategory = ref('')
const selectedTables = ref<string[]>(['FACT_ADMN_MDC_HTR_RCD', 'FACT_INHOS_ODR_INFMT'])
const formulaText = ref('')
const supplementaryText = ref('')
const regenerateHint = ref('')
const streamOutput = ref(false)
const streamLog = ref('')
const busy = ref(false)
const executeError = ref('')

const sqlNumerator = ref('')
const sqlDenominator = ref('')
const lastNumSql = ref('')
const lastDenSql = ref('')
const lastSqlError = ref('')
const conversationId = ref('')

const previewNum = ref<{ headers: string[]; rows: Record<string, unknown>[] }>({ headers: [], rows: [] })
const previewDen = ref<{ headers: string[]; rows: Record<string, unknown>[] }>({ headers: [], rows: [] })

// ======================== 计算属性 ========================
const hasSql = computed(() => {
  if (kind.value === 'core18' && calcType.value === 'count') {
    return !!sqlNumerator.value.trim()
  }
  return !!(sqlNumerator.value.trim() && sqlDenominator.value.trim())
})

const hasPreviousSql = computed(() => {
  if (kind.value === 'core18' && calcType.value === 'count') {
    return !!lastNumSql.value
  }
  return !!(lastNumSql.value && lastDenSql.value)
})

const templateOptions = computed(() => {
  const list = defaultIndicatorList.value
  if (kind.value === 'core18') {
    return list.filter(i => i.indicator_type === 'core18').map((r, idx) => ({
      value: String(r.id),
      label: r.name,
      seq: idx + 1,
    }))
  }
  return list.filter(i => i.indicator_type === 'four').map((r, idx) => ({
    value: String(r.id),
    label: `${r.category} — ${r.name}`,
    seq: idx + 1,
  }))
})

// ======================== 生命周期 ========================
onMounted(async () => {
  await loadIndicatorList()
  const qId = route.query.template as string
  if (qId) {
    templateId.value = qId
    restoreTemplateDefaults()
  }
})

watch(kind, (k) => {
  templateId.value = ''
  calcType.value = 'ratio'
})

// ======================== 方法 ========================
async function loadIndicatorList() {
  try {
    const [four, core18] = await Promise.all([
      indicatorsApi.getFourIndicators().catch(() => []),
      indicatorsApi.getCore18Indicators().catch(() => []),
    ])
    defaultIndicatorList.value = [...core18, ...four]
  } catch (e) {
    console.error('加载指标列表失败:', e)
  }
}

function goBack() {
  router.push({
    path: '/indicator-management',
    query: { kind: kind.value },
  })
}

function onTemplateChange() {
  if (templateId.value) restoreTemplateDefaults()
}

function restoreTemplateDefaults() {
  const id = templateId.value
  if (!id) {
    formulaText.value = ''
    supplementaryText.value = ''
    selectedTables.value = ['FACT_ADMN_MDC_HTR_RCD', 'FACT_INHOS_ODR_INFMT']
    return
  }

  const list = defaultIndicatorList.value
  if (kind.value === 'core18') {
    const row = list.find(r => String(r.id) === id && r.indicator_type === 'core18')
    if (!row) return
    newIndicatorName.value = row.name
    formulaText.value = row.formula || row.description || ''
    supplementaryText.value = [
      `分子：${row.numerator_desc || '—'}`,
      '',
      `分母：${row.denominator_desc || '—'}`,
    ].join('\n')
    return
  }

  const row = list.find(r => String(r.id) === id && r.indicator_type === 'four')
  if (!row) return
  fourCategory.value = row.category
  formulaText.value = row.rule_logic || ''
  supplementaryText.value = [`范围：${row.scope || '—'}`, '', `工作内容：${row.work_content || '—'}`].join('\n')
}

async function appendStreamLog(line: string) {
  streamLog.value += `${line}\n`
  if (streamOutput.value) {
    await new Promise(r => setTimeout(r, 120))
  }
}

async function generateAndExecute(useLast: boolean) {
  busy.value = true
  streamLog.value = ''
  executeError.value = ''
  previewNum.value = { headers: [], rows: [] }
  previewDen.value = { headers: [], rows: [] }

  const isCount = kind.value === 'core18' && calcType.value === 'count'

  // 解析补充信息中的分母/分子
  const { denom, numer } = parseSupplementaryForCore18()

  // 构建请求
  const requestData: Parameters<typeof indicatorsApi.executeIndicator>[0] = {
    business_type: kind.value,
    calc_type: calcType.value,
    selected_tables: selectedTables.value,
    indicator_formula: formulaText.value,
    supplement_info: supplementaryText.value,
    numerator_desc: numer,
    denominator_desc: denom,
    conversation_id: useLast ? conversationId.value : undefined,
    mode: 'create',
  }

  if (!useLast) {
    conversationId.value = crypto.randomUUID()
    requestData.conversation_id = conversationId.value
  }

  if (regenerateHint.value.trim()) {
    if (isCount) {
      requestData.regenerate = {
        user_feedback: regenerateHint.value.trim(),
        previous_sql: lastNumSql.value || undefined,
        sql_error: lastSqlError.value || undefined,
      }
    } else {
      requestData.regenerate = {
        user_feedback: regenerateHint.value.trim(),
        previous_numerator_sql: lastNumSql.value || undefined,
        previous_denominator_sql: lastDenSql.value || undefined,
      }
    }
  }

  await appendStreamLog('[请求] 开始生成 SQL…')
  await appendStreamLog(`[配置] 涉及表: ${selectedTables.value.join(', ')}`)

  try {
    const result = await indicatorsApi.executeIndicator(requestData)
    handleExecuteResult(result)
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e)
    executeError.value = msg
    await appendStreamLog(`[错误] ${msg}`)
  } finally {
    busy.value = false
  }
}

function handleExecuteResult(result: ExecuteResponse) {
  const isCount = kind.value === 'core18' && calcType.value === 'count'

    if (result.ok) {
    if (isCount) {
      sqlNumerator.value = result.sql || ''
      lastNumSql.value = result.sql || ''
      previewNum.value = {
        headers: result.preview_columns || [],
        rows: result.preview_rows || [],
      }
    } else {
      sqlNumerator.value = result.numerator_sql || ''
      sqlDenominator.value = result.denominator_sql || ''
      lastNumSql.value = result.numerator_sql || ''
      lastDenSql.value = result.denominator_sql || ''
      previewNum.value = {
        headers: result.preview_columns || [],
        rows: result.preview_rows || [],
      }
      // 尝试获取分母预览（需要单独调用）
      if (result.denominator_sql) {
        fetchDenPreview(result.denominator_sql)
      }
    }
    streamLog.value += `[完成] SQL 生成成功！\n`
    if (isCount) {
      if (result.count !== null) {
        const previewRows = result.preview_rows?.length ?? 0
        streamLog.value += `[计数] ${result.count.toLocaleString()} 条（前端预览 ${previewRows} 条）\n`
      }
    } else {
      if (result.numerator_count !== null) {
        const previewRows = result.preview_rows?.length ?? 0
        streamLog.value += `[计数] 分子: ${result.numerator_count.toLocaleString()} 条（前端预览 ${previewRows} 条）\n`
      }
      if (result.denominator_count !== null) {
        const previewDenRows = result.denominator_preview_rows?.length ?? 0
        streamLog.value += `[计数] 分母: ${result.denominator_count.toLocaleString()} 条（前端预览 ${previewDenRows} 条）\n`
      }
      if (result.rate_percent !== null) {
        streamLog.value += `[比率] ${result.rate_percent}%\n`
      }
    }
  } else {
    executeError.value = result.error || '执行失败'
    streamLog.value += `[失败] ${result.error}\n`
    // 如果有上次 SQL 的错误信息，也显示
    const numErr = result.numerator_attempts?.[0]?.error
    const denErr = result.denominator_attempts?.[0]?.error
    const cntErr = result.attempts?.[0]?.error  // 计数型的错误在 attempts 里
    if (numErr) streamLog.value += `[分子错误] ${numErr}\n`
    if (denErr) streamLog.value += `[分母错误] ${denErr}\n`
    if (cntErr) {
      streamLog.value += `[SQL 错误] ${cntErr}\n`
      lastSqlError.value = cntErr
    }
  }
}

async function fetchDenPreview(sql: string) {
  try {
    const result = await indicatorsApi.testSql({ sql, limit: 10 })
    if (result.ok) {
      previewDen.value = {
        headers: result.columns || [],
        rows: result.rows || [],
      }
    }
  } catch {
    // 忽略分母预览错误
  }
}

function parseSupplementaryForCore18(): { denom: string; numer: string } {
  const text = supplementaryText.value
  const dm = text.match(/分母[：:]\s*([^\n]+)/)
  const nm = text.match(/分子[：:]\s*([^\n]+)/)
  return {
    denom: dm?.[1]?.trim() || text.slice(0, 200) || '—',
    numer: nm?.[1]?.trim() || '—',
  }
}

async function handleSave() {
  const isCount = kind.value === 'core18' && calcType.value === 'count'
  const combinedSql = isCount
    ? sqlNumerator.value
    : `-- 分子\n${sqlNumerator.value}\n\n-- 分母\n${sqlDenominator.value}`

  try {
    if (kind.value === 'core18') {
      const name = newIndicatorName.value.trim()
      if (!name) {
        alert('请填写指标名称')
        return
      }
      const { denom, numer } = parseSupplementaryForCore18()
      const data = {
        name,
        formula: formulaText.value,
        numerator_desc: numer,
        denominator_desc: denom,
        involved_tables: selectedTables.value,
        use_llm: true,
        calc_method: 'textToSql',
        calc_type: calcType.value,
        sql_content: combinedSql,
      }
      if (templateId.value) {
        await indicatorsApi.updateCore18Indicator(Number(templateId.value), data)
        alert('已更新指标')
      } else {
        await indicatorsApi.createCore18Indicator({ ...data, indicator_type: 'core18' })
        alert('已保存到「十八项」指标列表')
      }
      goBack()
      return
    }

    if (!fourCategory.value.trim()) {
      alert('请填写类别')
      return
    }
    const lines = supplementaryText.value.split('\n\n')
    const scope = lines[0]?.replace(/^范围[：:]\s*/, '').trim() || ''
    const work = lines.find(l => l.startsWith('工作内容'))?.replace(/^工作内容[：:]\s*/, '').trim() || supplementaryText.value.slice(0, 400)
    const data = {
      category: fourCategory.value.trim(),
      scope: scope || '—',
      work_content: work || formulaText.value.slice(0, 400) || '—',
      rule_logic: formulaText.value || '—',
      involved_tables: selectedTables.value,
      use_llm: true,
      calc_method: 'textToSql',
      calc_type: calcType.value,
      sql_content: combinedSql,
    }
    if (templateId.value) {
      await indicatorsApi.updateFourIndicator(Number(templateId.value), data)
      alert('已更新指标')
    } else {
      await indicatorsApi.createFourIndicator({ ...data, indicator_type: 'four' })
      alert('已保存到「四要素」指标列表')
    }
    goBack()
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e)
    alert(`保存失败: ${msg}`)
  }
}
</script>
