<template>
  <div class="mx-auto max-w-[1200px] pb-10">
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
        <h1 class="text-[16px] font-bold text-[#1F264D]">
          {{ isEditing ? '指标调试更新' : '指标调试新增' }}
        </h1>
      </div>
      <button
        type="button"
        class="rounded-[2px] bg-emerald-600 px-4 py-2 text-[12px] text-white shadow-sm transition-colors hover:bg-emerald-700 disabled:opacity-60"
        :disabled="saving"
        @click="saveIndicator"
      >
        {{ isEditing ? '更新指标' : '保存指标' }}
      </button>
    </div>

    <!-- 主体：左侧基础信息 + 右侧 SQL 编辑 -->
    <div class="grid gap-4 lg:grid-cols-[420px_1fr]">
      <!-- 左侧：基础信息 -->
      <div class="space-y-4 rounded-[2px] border border-[#b8c9e8]/60 bg-white p-5 shadow-sm">
        <h3 class="text-[13px] font-semibold text-[#1F264D]">基础信息</h3>

        <!-- 指标类别 -->
        <label class="block text-[12px]">
          <span class="mb-1 block font-medium text-[#596080]">指标类别</span>
          <select
            v-model="form.kind"
            class="w-full cursor-pointer rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
          >
            <option value="core18">十八项核心制度指标</option>
            <option value="four">四要素监管指标</option>
          </select>
        </label>

        <!-- 已有指标模板下拉（仅 core18 有模板列表） -->
        <template v-if="form.kind === 'core18'">
          <label class="block text-[12px]">
            <span class="mb-1 block font-medium text-[#596080]">
              选择已有指标（作为模板或更新 SQL）
            </span>
            <SearchableSelect
              v-model="templateId"
              :options="templateOptions"
              placeholder="— 不引用模板，完全新建 —"
              search-placeholder="输入关键词搜索指标…"
              @change="onTemplateChange"
            />
          </label>
        </template>

        <!-- 四要素已有指标下拉 -->
        <template v-if="form.kind === 'four'">
          <label class="block text-[12px]">
            <span class="mb-1 block font-medium text-[#596080]">
              选择已有指标（作为模板或更新 SQL）
            </span>
            <SearchableSelect
              v-model="fourTemplateId"
              :options="fourTemplateOptions"
              placeholder="— 不引用模板，完全新建 —"
              search-placeholder="输入关键词搜索指标…"
              @change="onFourTemplateChange"
            />
          </label>
        </template>

        <!-- 计算类型（仅十八项核心制度指标） -->
        <template v-if="form.kind === 'core18'">
          <label class="block text-[12px]">
            <span class="mb-1 block font-medium text-[#596080]">计算类型</span>
            <div class="flex flex-wrap gap-3">
              <label class="flex cursor-pointer items-center gap-1.5">
                <input
                  v-model="form.calcType"
                  type="radio"
                  value="ratio"
                  class="accent-emerald-600"
                />
                <span class="text-[12px] text-[#1F264D]">比值型</span>
              </label>
              <label class="flex cursor-pointer items-center gap-1.5">
                <input
                  v-model="form.calcType"
                  type="radio"
                  value="count"
                  class="accent-emerald-600"
                />
                <span class="text-[12px] text-[#1F264D]">计数型</span>
              </label>
            </div>
          </label>
          <p class="mt-0.5 text-[11px] text-[#596080]">
            <span v-if="form.calcType === 'ratio'">填写分子 SQL 与分母 SQL，计算比值 = 分子 ÷ 分母 × 100%</span>
            <span v-else-if="form.calcType === 'count'">仅填写 SQL 语句，直接输出计数结果</span>
          </p>
        </template>

        <!-- 指标名称 -->
        <label class="block text-[12px]">
          <span class="mb-1 block font-medium text-[#596080]">指标名称</span>
          <input
            v-model="form.name"
            type="text"
            placeholder="如：患者入院 48 小时内转科的比例"
            class="w-full rounded-[2px] border border-[#b8c9e8]/60 px-3 py-2 text-[12px] focus:border-emerald-400 focus:outline-none"
          />
        </label>

        <!-- 四要素特有字段 -->
        <template v-if="form.kind === 'four'">
          <div class="grid grid-cols-2 gap-3">
            <label class="block text-[12px]">
              <span class="mb-1 block font-medium text-[#596080]">类别</span>
              <input
                v-model="form.category"
                type="text"
                placeholder="如：人员要素"
                class="w-full rounded-[2px] border border-[#b8c9e8]/60 px-2.5 py-2 text-[12px] focus:border-emerald-400 focus:outline-none"
              />
            </label>
            <label class="block text-[12px]">
              <span class="mb-1 block font-medium text-[#596080]">序号</span>
              <input
                v-model.number="form.seq"
                type="number"
                min="1"
                class="w-full rounded-[2px] border border-[#b8c9e8]/60 px-2.5 py-2 text-[12px] focus:border-emerald-400 focus:outline-none"
              />
            </label>
          </div>

          <!-- 计算类型（仅四要素） -->
          <label class="block text-[12px]">
            <span class="mb-1 block font-medium text-[#596080]">计算类型</span>
            <div class="flex flex-wrap gap-3">
              <label class="flex cursor-pointer items-center gap-1.5">
                <input
                  v-model="form.calcType"
                  type="radio"
                  value="ratio"
                  class="accent-emerald-600"
                />
                <span class="text-[12px] text-[#1F264D]">比值型</span>
              </label>
              <label class="flex cursor-pointer items-center gap-1.5">
                <input
                  v-model="form.calcType"
                  type="radio"
                  value="count"
                  class="accent-emerald-600"
                />
                <span class="text-[12px] text-[#1F264D]">计数型</span>
              </label>
            </div>
          </label>
          <p class="mt-0.5 text-[11px] text-[#596080]">
            <span v-if="form.calcType === 'ratio'">填写分子 SQL 与分母 SQL，计算比值 = 分子 ÷ 分母 × 100%</span>
            <span v-else-if="form.calcType === 'count'">仅填写 SQL 语句，直接输出计数结果</span>
          </p>
        </template>

        <!-- 范围（仅四要素） -->
        <template v-if="form.kind === 'four'">
          <label class="block text-[12px]">
            <span class="mb-1 block font-medium text-[#596080]">范围</span>
            <textarea
              v-model="form.scope"
              rows="2"
              placeholder="如：住院患者，跨越多个科室"
              class="w-full resize-y rounded-[2px] border border-[#b8c9e8]/60 px-2.5 py-2 text-[12px] focus:border-emerald-400 focus:outline-none"
            />
          </label>

          <label class="block text-[12px]">
            <span class="mb-1 block font-medium text-[#596080]">工作内容</span>
            <textarea
              v-model="form.workContent"
              rows="3"
              placeholder="如：监测医师是否存在超权限开具抗生素的行为"
              class="w-full resize-y rounded-[2px] border border-[#b8c9e8]/60 px-2.5 py-2 text-[12px] focus:border-emerald-400 focus:outline-none"
            />
          </label>

          <label class="block text-[12px]">
            <span class="mb-1 block font-medium text-[#596080]">规则逻辑</span>
            <textarea
              v-model="form.ruleLogic"
              rows="3"
              placeholder="如：同期存在越权开具抗生素的医师人次数"
              class="w-full resize-y rounded-[2px] border border-[#b8c9e8]/60 px-2.5 py-2 text-[12px] focus:border-emerald-400 focus:outline-none"
            />
          </label>
        </template>

        <!-- 十八项特有字段 -->
        <template v-if="form.kind === 'core18'">
          <div class="grid grid-cols-2 gap-3">
            <label class="block text-[12px]">
              <span class="mb-1 block font-medium text-[#596080]">是否可计算</span>
              <select
                v-model="form.computable"
                class="w-full cursor-pointer rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
              >
                <option value="是">是</option>
                <option value="否">否</option>
              </select>
            </label>
            <label class="block text-[12px]">
              <span class="mb-1 block font-medium text-[#596080]">需使用大模型</span>
              <select
                v-model="form.useLlm"
                class="w-full cursor-pointer rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
              >
                <option value="是">是</option>
                <option value="否">否</option>
              </select>
            </label>
          </div>

          <label class="block text-[12px]">
            <span class="mb-1 block font-medium text-[#596080]">说明</span>
            <textarea
              v-model="form.description"
              rows="2"
              class="w-full resize-y rounded-[2px] border border-[#b8c9e8]/60 px-2.5 py-2 text-[12px] focus:border-emerald-400 focus:outline-none"
            />
          </label>

          <label class="block text-[12px]" v-if="form.calcType === 'ratio'">
            <span class="mb-1 block font-medium text-[#596080]">分母</span>
            <textarea
              v-model="form.denominator"
              rows="2"
              placeholder="如：同期入院患者总人次数"
              class="w-full resize-y rounded-[2px] border border-[#b8c9e8]/60 px-2.5 py-2 text-[12px] focus:border-emerald-400 focus:outline-none"
            />
          </label>

          <label class="block text-[12px]" v-if="form.calcType === 'ratio'">
            <span class="mb-1 block font-medium text-[#596080]">分子</span>
            <textarea
              v-model="form.numerator"
              rows="2"
              placeholder="如：同期入院8小时内已下达检查或治疗医嘱的患者人次数"
              class="w-full resize-y rounded-[2px] border border-[#b8c9e8]/60 px-2.5 py-2 text-[12px] focus:border-emerald-400 focus:outline-none"
            />
          </label>

          <label class="block text-[12px]">
            <span class="mb-1 block font-medium text-[#596080]">计算公式</span>
            <input
              v-model="form.formula"
              type="text"
              placeholder="如：分子 ÷ 分母 × 100%"
              class="w-full rounded-[2px] border border-[#b8c9e8]/60 px-3 py-2 text-[12px] focus:border-emerald-400 focus:outline-none"
            />
          </label>
        </template>

        <!-- 计算结果预览说明 -->
        <div class="rounded-[2px] border border-emerald-200 bg-emerald-50 p-3">
          <p class="mb-1.5 text-[11px] font-semibold text-emerald-700">计算结果预览说明</p>
          <p class="text-[11px] leading-relaxed text-emerald-600">
            <template v-if="form.kind === 'core18' && form.calcType === 'ratio'">
              系统将执行分子 SQL 与分母 SQL，将两者 COUNT 结果相除并乘以 100% 作为指标值输出。SQL 中请仅写
              <code class="rounded bg-white/80 px-1 font-mono text-[10px] text-emerald-800">SELECT COUNT(*)</code>
              语句，查询返回的计数结果将参与比值计算。
            </template>
            <template v-else-if="form.kind === 'core18' && form.calcType === 'count'">
              系统将执行 SQL 语句，直接输出 COUNT 查询的计数结果作为指标值。SQL 中请仅写
              <code class="rounded bg-white/80 px-1 font-mono text-[10px] text-emerald-800">SELECT COUNT(*)</code>
              语句。
            </template>
            <template v-else-if="form.kind === 'four' && form.calcType === 'ratio'">
              系统将执行分子 SQL 与分母 SQL，将两者 COUNT 结果相除并乘以 100% 作为指标值输出。
            </template>
            <template v-else-if="form.kind === 'four' && form.calcType === 'count'">
              系统将执行 SQL 语句，直接输出 COUNT 查询的计数结果作为指标值。SQL 中请仅写
              <code class="rounded bg-white/80 px-1 font-mono text-[10px] text-emerald-800">SELECT COUNT(*)</code>
              语句。
            </template>
            <template v-else>
              系统将执行分子 SQL 与分母 SQL，将两者 COUNT 结果相除并乘以 100% 作为指标值输出。
            </template>
          </p>
        </div>
      </div>

      <!-- 右侧：SQL 编辑 -->
      <div class="space-y-4">
      <!-- 分子 SQL -->
      <div class="rounded-[2px] border border-[#b8c9e8]/60 bg-white shadow-sm">
        <div class="border-b border-[#e8eef9] bg-purple-50/80 px-4 py-2.5 text-[13px] font-semibold text-[#1F264D]">
          <template v-if="form.kind === 'core18' && form.calcType === 'ratio'">
            分子 SQL
            <span class="ml-2 text-[11px] font-normal text-[#596080]">返回计数，系统将作为分子参与比值计算</span>
          </template>
          <template v-else-if="form.kind === 'four' && form.calcType === 'ratio'">
            分子 SQL
            <span class="ml-2 text-[11px] font-normal text-[#596080]">返回计数，系统将作为分子参与比值计算</span>
          </template>
          <template v-else>
            SQL 语句
            <span class="ml-2 text-[11px] font-normal text-[#596080]">返回计数，直接输出计数结果</span>
          </template>
        </div>
          <div class="p-4">
          <!-- 涉及表（分子） -->
          <div>
            <p class="mb-1.5 text-[11px] font-medium text-[#596080]">涉及表（可多选）</p>
            <div class="mb-3 flex flex-wrap gap-x-4 gap-y-1.5 rounded-[2px] border border-[#b8c9e8]/60 bg-[#fafbff] px-3 py-2">
              <label
                v-for="t in ALL_TABLES"
                :key="t.code"
                class="flex cursor-pointer items-center gap-1 text-[11px] text-[#334155] hover:text-emerald-600"
              >
                <input
                  type="checkbox"
                  :value="t.code"
                  v-model="form.numInvolvedTables"
                  class="accent-emerald-600"
                />
                <span class="font-medium">{{ t.label }}</span>
              </label>
            </div>
            <p class="mb-2 text-[11px] text-[#94a3b8]">已选：<span class="font-mono text-[10px]">{{ form.numInvolvedTables.join(', ') || '—' }}</span></p>
          </div>
            <p class="mb-1.5 text-[11px] font-medium text-[#596080]">SQL 语句</p>
            <textarea
              v-model="form.numeratorSql"
              rows="7"
              placeholder="SELECT COUNT(DISTINCT patient_id) FROM your_table WHERE condition;"
              class="w-full resize-y rounded-[2px] border border-purple-200 bg-purple-50/40 px-3 py-2.5 font-mono text-[11px] leading-relaxed text-[#334155] focus:border-purple-400 focus:outline-none"
            />
            <div class="mt-3 flex items-center gap-2">
              <button
                type="button"
                class="rounded-[2px] border border-purple-300 bg-purple-50 px-3 py-1.5 text-[11px] text-purple-700 hover:bg-purple-100 disabled:opacity-50"
                :disabled="testingNum"
                @click="testNumSql"
              >
                {{ testingNum ? '测试中…' : '测试 SQL' }}
              </button>
              <span v-if="previewNum.rows.length" class="text-[11px] text-emerald-600">
                ✓ 执行成功，返回 {{ testNumCount }} 条
              </span>
            </div>
            <!-- 查询结果预览 -->
            <div v-if="previewNum.rows.length" class="mt-3 min-h-[100px] overflow-auto rounded-[2px] border border-dashed border-purple-200 bg-[#fafbff] p-2">
              <p class="mb-1.5 text-[11px] font-medium text-[#596080]">查询结果预览</p>
              <table class="w-full border-collapse text-left text-[11px]">
                <thead>
                  <tr class="border-b border-[#b8c9e8]/60 bg-white">
                    <th v-for="h in previewNum.headers" :key="h" class="px-2 py-1.5 font-semibold text-[#596080]">{{ h }}</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-[#e8eef9]">
                  <tr v-for="(r, ri) in previewNum.rows" :key="ri" class="bg-white/80">
                    <td v-for="h in previewNum.headers" :key="h" class="px-2 py-1.5 text-[#1F264D]">{{ r[h] }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- 分母 SQL（比值型显示 -->
        <div v-if="(form.kind === 'core18'&& form.calcType === 'ratio') || (form.kind === 'four' && form.calcType === 'ratio')" class="rounded-[2px] border border-[#b8c9e8]/60 bg-white shadow-sm">
          <div class="border-b border-[#e8eef9] bg-sky-50/80 px-4 py-2.5 text-[13px] font-semibold text-[#1F264D]">
            分母 SQL
            <span class="ml-2 text-[11px] font-normal text-[#596080]">返回计数，系统将作为分母参与比值计算</span>
          </div>
          <div class="p-4">
          <!-- 涉及表（分母） -->
          <div>
            <p class="mb-1.5 text-[11px] font-medium text-[#596080]">涉及表（可多选）</p>
            <div class="mb-3 flex flex-wrap gap-x-4 gap-y-1.5 rounded-[2px] border border-[#b8c9e8]/60 bg-[#fafbff] px-3 py-2">
              <label
                v-for="t in ALL_TABLES"
                :key="t.code"
                class="flex cursor-pointer items-center gap-1 text-[11px] text-[#334155] hover:text-emerald-600"
              >
                <input
                  type="checkbox"
                  :value="t.code"
                  v-model="form.denInvolvedTables"
                  class="accent-emerald-600"
                />
                <span class="font-medium">{{ t.label }}</span>
              </label>
            </div>
            <p class="mb-2 text-[11px] text-[#94a3b8]">已选：<span class="font-mono text-[10px]">{{ form.denInvolvedTables.join(', ') || '—' }}</span></p>
          </div>
            <p class="mb-1.5 text-[11px] font-medium text-[#596080]">SQL 语句</p>
            <textarea
              v-model="form.denominatorSql"
              rows="7"
              placeholder="SELECT COUNT(DISTINCT patient_id) FROM your_table;"
              class="w-full resize-y rounded-[2px] border border-sky-200 bg-sky-50/40 px-3 py-2.5 font-mono text-[11px] leading-relaxed text-[#334155] focus:border-sky-400 focus:outline-none"
            />
            <div class="mt-3 flex items-center gap-2">
              <button
                type="button"
                class="rounded-[2px] border border-sky-300 bg-sky-50 px-3 py-1.5 text-[11px] text-sky-700 hover:bg-sky-100 disabled:opacity-50"
                :disabled="testingDen"
                @click="testDenSql"
              >
                {{ testingDen ? '测试中…' : '测试 SQL' }}
              </button>
              <span v-if="previewDen.rows.length" class="text-[11px] text-emerald-600">
                ✓ 执行成功，返回 {{ testDenCount }} 条
              </span>
            </div>
            <!-- 查询结果预览 -->
            <div v-if="previewDen.rows.length" class="mt-3 min-h-[100px] overflow-auto rounded-[2px] border border-dashed border-sky-200 bg-[#fafbff] p-2">
              <p class="mb-1.5 text-[11px] font-medium text-[#596080]">查询结果预览</p>
              <table class="w-full border-collapse text-left text-[11px]">
                <thead>
                  <tr class="border-b border-[#b8c9e8]/60 bg-white">
                    <th v-for="h in previewDen.headers" :key="h" class="px-2 py-1.5 font-semibold text-[#596080]">{{ h }}</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-[#e8eef9]">
                  <tr v-for="(r, ri) in previewDen.rows" :key="ri" class="bg-white/80">
                    <td v-for="h in previewDen.headers" :key="h" class="px-2 py-1.5 text-[#1F264D]">{{ r[h] }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Prompt 内容（可选，补充说明） -->
        <div class="rounded-[2px] border border-[#b8c9e8]/60 bg-white shadow-sm">
          <div class="border-b border-[#e8eef9] bg-amber-50/80 px-4 py-2.5 text-[13px] font-semibold text-[#1F264D]">
            补充说明（可选）
          </div>
          <div class="p-4">
            <textarea
              v-model="form.promptContent"
              rows="3"
              placeholder="补充说明：口径范围、取数逻辑、数据质量注意事项等"
              class="w-full resize-y rounded-[2px] border border-amber-200 bg-amber-50/40 px-3 py-2.5 text-[12px] focus:border-amber-400 focus:outline-none"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft } from 'lucide-vue-next'
import {
  DEFAULT_CORE18,
  DEFAULT_FOUR_ELEMENTS,
  type Core18Indicator,
  type FourElementIndicator,
} from '@/data/indicatorManagementDefaults'
import { indicatorsApi, type Indicator } from '@/api/indicators'
import SearchableSelect from '@/components/ui/SearchableSelect.vue'

const ALL_TABLES = [
  { code: 'FACT_ADMN_MDC_HTR_RCD',  label: '入院病历记录' },
  { code: 'FACT_INHOS_ODR_INFMT',    label: '住院医嘱信息' },
  { code: 'FACT_DIAG_RECORD',        label: '诊断记录' },
  { code: 'FACT_OPERATION_RECORD',   label: '手术记录' },
  { code: 'FACT_LAB_RESULT',         label: '检验结果' },
  { code: 'FACT_MDC_RCD_HMPG',       label: '病案首页' },
  { code: 'FACT_MDC_RCD_HMPG_OPRT',  label: '病案首页-手术' },
  { code: 'FACT_MDC_RCD_HMPG_DIAG', label: '病案首页-诊断' },
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

const router = useRouter()

const STORAGE_FOUR = 'indicator-management-four-elements-v1'
const STORAGE_CORE = 'indicator-management-core18-v1'

const templateId = ref<string | number>('')
const templateList = ref<Indicator[]>([])
const fourTemplateId = ref<string | number>('')
const fourTemplateList = ref<Indicator[]>([])

const form = ref({
  kind: 'core18' as 'core18' | 'four',
  calcType: 'ratio' as 'ratio' | 'count',
  name: '',
  category: '',
  seq: 1,
  scope: '',
  workContent: '',
  ruleLogic: '',
  description: '',
  denominator: '',
  numerator: '',
  formula: '',
  computable: '是',
  useLlm: '否',
  numeratorSql: '',
  denominatorSql: '',
  numInvolvedTables: [] as string[],
  denInvolvedTables: [] as string[],
  promptContent: '',
})

const templateOptions = computed(() => {
  if (form.value.kind !== 'core18') return []
  return templateList.value.map((r) => ({
    value: String(r.id),
    label: r.name,
    seq: r.seq || 0,
  }))
})

const fourTemplateOptions = computed(() => {
  if (form.value.kind !== 'four') return []
  return fourTemplateList.value.map((r) => ({
    value: String(r.id),
    label: r.name,
    seq: r.seq || 0,
  }))
})

const isEditing = computed(() => {
  return (form.value.kind === 'core18' && templateId.value !== '') ||
    (form.value.kind === 'four' && fourTemplateId.value !== '')
})

async function loadTemplateList() {
  if (form.value.kind !== 'core18') {
    templateList.value = []
    return
  }
  try {
    const data = await indicatorsApi.getCore18Indicators()
    templateList.value = data || []
  } catch (e) {
    console.error('加载模板列表失败:', e)
    templateList.value = []
  }
}

async function loadFourTemplateList() {
  if (form.value.kind !== 'four') {
    fourTemplateList.value = []
    return
  }
  try {
    const data = await indicatorsApi.getFourIndicators()
    fourTemplateList.value = data || []
  } catch (e) {
    console.error('加载四要素模板列表失败:', e)
    fourTemplateList.value = []
  }
}

function onTemplateChange() {
  if (!templateId.value) {
    // 重置为新建状态
    form.value.name = ''
    form.value.calcType = 'ratio'
    form.value.description = ''
    form.value.denominator = ''
    form.value.numerator = ''
    form.value.formula = ''
    form.value.computable = '是'
    form.value.useLlm = '否'
    form.value.numeratorSql = ''
    form.value.denominatorSql = ''
    form.value.numInvolvedTables = []
    form.value.denInvolvedTables = []
    form.value.promptContent = ''
    return
  }

  const selected = templateList.value.find((r) => String(r.id) === String(templateId.value))
  if (!selected) return

  form.value.name = selected.name || ''
  form.value.description = selected.description || ''
  form.value.numerator = selected.numerator_desc || ''
  form.value.denominator = selected.denominator_desc || ''
  form.value.formula = selected.formula || ''
  form.value.numeratorSql = selected.numerator_sql || ''
  form.value.denominatorSql = selected.denominator_sql || ''
  form.value.promptContent = selected.prompt_content || ''

  if (selected.calc_type === 'ratio') {
    form.value.calcType = 'ratio'
  } else if (selected.calc_type === 'count') {
    form.value.calcType = 'count'
  }

  form.value.computable = selected.is_computable ? '是' : '否'
  form.value.useLlm = selected.use_llm ? '是' : '否'
  form.value.numInvolvedTables = Array.isArray(selected.involved_tables) ? selected.involved_tables : []
  form.value.denInvolvedTables = Array.isArray(selected.involved_tables) ? selected.involved_tables : []
}

function onFourTemplateChange() {
  if (!fourTemplateId.value) {
    // 重置为新建状态
    form.value.name = ''
    form.value.category = ''
    form.value.seq = Math.max(0, ...fourTemplateList.value.map(x => x.seq || 0)) + 1
    form.value.scope = ''
    form.value.workContent = ''
    form.value.ruleLogic = ''
    form.value.calcType = 'ratio'
    form.value.numeratorSql = ''
    form.value.denominatorSql = ''
    form.value.numInvolvedTables = []
    form.value.denInvolvedTables = []
    form.value.promptContent = ''
    return
  }

  const selected = fourTemplateList.value.find((r) => String(r.id) === String(fourTemplateId.value))
  if (!selected) return

  form.value.name = selected.name || ''
  form.value.category = selected.category || ''
  form.value.seq = selected.seq || 1
  form.value.scope = selected.scope || ''
  form.value.workContent = selected.work_content || ''
  form.value.ruleLogic = selected.rule_logic || ''
  form.value.numeratorSql = selected.numerator_sql || ''
  form.value.denominatorSql = selected.denominator_sql || ''
  form.value.promptContent = selected.prompt_content || ''

  if (selected.calc_type === 'ratio') {
    form.value.calcType = 'ratio'
  } else if (selected.calc_type === 'count') {
    form.value.calcType = 'count'
  }

  form.value.numInvolvedTables = Array.isArray(selected.involved_tables) ? selected.involved_tables : []
  form.value.denInvolvedTables = Array.isArray(selected.involved_tables) ? selected.involved_tables : []
}

onMounted(async () => {
  await loadTemplateList()
  await loadFourTemplateList()

  // 为四要素自动填入下一个序号
  try {
    const f = localStorage.getItem(STORAGE_FOUR)
    const list: FourElementIndicator[] = f ? JSON.parse(f) : JSON.parse(JSON.stringify(DEFAULT_FOUR_ELEMENTS))
    const localMax = Math.max(0, ...list.map((x) => x.seq))
    const backendMax = Math.max(0, ...fourTemplateList.value.map(x => x.seq || 0))
    form.value.seq = Math.max(localMax, backendMax) + 1
  } catch {
    form.value.seq = Math.max(1, ...fourTemplateList.value.map(x => x.seq || 0)) + 1
  }
})

// 切换指标类别时重新加载模板列表
watch(() => form.value.kind, async () => {
  templateId.value = ''
  fourTemplateId.value = ''
  await loadTemplateList()
  await loadFourTemplateList()
})

function goBack() {
  router.push({ path: '/indicator-management', query: { kind: form.value.kind } })
}

type PreviewResult = { headers: string[]; rows: Record<string, unknown>[] }

const previewNum = ref<PreviewResult>({ headers: [], rows: [] })
const previewDen = ref<PreviewResult>({ headers: [], rows: [] })
const testingNum = ref(false)
const testingDen = ref(false)
const saving = ref(false)
const testNumCount = ref<number | null>(null)
const testDenCount = ref<number | null>(null)

async function testNumSql() {
  if (!form.value.numeratorSql.trim()) {
    alert('请先填写分子 SQL 语句')
    return
  }
  testingNum.value = true
  previewNum.value = { headers: [], rows: [] }
  testNumCount.value = null
  try {
    const result = await indicatorsApi.testSql({ sql: form.value.numeratorSql, limit: 10 })
    if (result.ok) {
      previewNum.value = {
        headers: result.columns || [],
        rows: result.rows || [],
      }
      testNumCount.value = result.count
    } else {
      alert('SQL 执行失败：' + (result.error || result.count_error || '未知错误'))
    }
  } catch (e) {
    alert('测试失败：' + (e instanceof Error ? e.message : String(e)))
  } finally {
    testingNum.value = false
  }
}

async function testDenSql() {
  if (!form.value.denominatorSql.trim()) {
    alert('请先填写分母 SQL 语句')
    return
  }
  testingDen.value = true
  previewDen.value = { headers: [], rows: [] }
  testDenCount.value = null
  try {
    const result = await indicatorsApi.testSql({ sql: form.value.denominatorSql, limit: 10 })
    if (result.ok) {
      previewDen.value = {
        headers: result.columns || [],
        rows: result.rows || [],
      }
      testDenCount.value = result.count
    } else {
      alert('SQL 执行失败：' + (result.error || result.count_error || '未知错误'))
    }
  } catch (e) {
    alert('测试失败：' + (e instanceof Error ? e.message : String(e)))
  } finally {
    testingDen.value = false
  }
}

async function saveIndicator() {
  if (!form.value.name.trim()) {
    alert('请填写指标名称')
    return
  }

  saving.value = true
  try {
    const isRatio = form.value.kind === 'core18' && form.value.calcType === 'ratio'
    const combinedSqlCore = isRatio
      ? `-- 分子 SQL\n${form.value.numeratorSql.trim()}\n\n-- 分母 SQL\n${form.value.denominatorSql.trim()}`
      : form.value.numeratorSql.trim()

    if (form.value.kind === 'core18') {
      const payload = {
        name: form.value.name.trim(),
        description: form.value.description.trim(),
        numerator_desc: form.value.numerator.trim(),
        denominator_desc: form.value.denominator.trim(),
        formula: form.value.formula.trim(),
        numerator_sql: form.value.numeratorSql.trim(),
        denominator_sql: form.value.denominatorSql.trim(),
        sql_content: combinedSqlCore,
        prompt_content: form.value.promptContent.trim(),
        involved_tables: [...form.value.numInvolvedTables, ...form.value.denInvolvedTables],
        calc_type: form.value.calcType,
        is_computable: form.value.computable === '是',
        use_llm: form.value.useLlm === '是',
        calc_method: 'sql' as const,
      }

      if (isEditing.value && templateId.value) {
        // 更新已有指标
        await indicatorsApi.updateCore18Indicator(Number(templateId.value), payload)
        alert('指标已更新')
      } else {
        // 新建指标
        await indicatorsApi.createCore18Indicator(payload)
        alert('已保存到「十八项核心制度指标」列表')
      }
    } else {
      // 四要素：通过 API 保存到后端
      const combinedSqlFour = form.value.calcType === 'ratio'
        ? `-- 分子 SQL\n${form.value.numeratorSql.trim()}\n\n-- 分母 SQL\n${form.value.denominatorSql.trim()}`
        : form.value.numeratorSql.trim()

      const payload = {
        name: form.value.name.trim(),
        category: form.value.category.trim(),
        seq: form.value.seq || 1,
        scope: form.value.scope.trim(),
        work_content: form.value.workContent.trim(),
        rule_logic: form.value.ruleLogic.trim(),
        formula: form.value.calcType === 'ratio' ? '分子 ÷ 分母 × 100%' : '',
        sql_content: combinedSqlFour,
        prompt_content: form.value.promptContent.trim(),
        involved_tables: [...form.value.numInvolvedTables, ...form.value.denInvolvedTables],
        numerator_sql: form.value.numeratorSql.trim(),
        denominator_sql: form.value.denominatorSql.trim(),
        numerator_desc: '',
        denominator_desc: '',
        calc_type: form.value.calcType,
        is_computable: true,
        use_llm: false,
        calc_method: 'sql' as const,
      }

      if (isEditing.value && fourTemplateId.value) {
        // 更新已有指标
        await indicatorsApi.updateFourIndicator(Number(fourTemplateId.value), payload)
        alert('四要素指标已更新')
      } else {
        // 新建指标
        await indicatorsApi.createFourIndicator(payload)
        alert('已保存到「四要素监管指标」列表')
      }
    }

    goBack()
  } catch (e: unknown) {
    console.error('保存失败:', e)
    alert('保存失败：' + (e instanceof Error ? e.message : String(e)))
  } finally {
    saving.value = false
  }
}
</script>
