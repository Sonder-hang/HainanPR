<template>
  <div>
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
          class="rounded-[2px] bg-emerald-600 px-4 py-2 text-[12px] text-white shadow-sm transition-colors hover:bg-emerald-700"
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

          <!-- 已有指标模板下拉（四要素和十八项核心制度指标均支持） -->
          <template v-if="form.kind === 'four' || form.kind === 'core18'">
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

          <!-- 计算类型（四要素和十八项核心制度指标均支持） -->
          <template v-if="form.kind === 'core18' || form.kind === 'four'">
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

            <!-- 模板类型 -->
            <label class="block text-[12px]">
              <span class="mb-1 block font-medium text-[#596080]">模板类型</span>
              <select
                v-model="form.templateType"
                class="w-full cursor-pointer rounded-[2px] border border-[#b8c9e8]/60 bg-white px-3 py-2 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
              >
                <option value="">自动推断（根据计算类型）</option>
                <option value="RATE">率型（RATE）</option>
                <option value="STRUCTURE">排行榜型（STRUCTURE）</option>
                <option value="STRUCTURE-special">双排行型（STRUCTURE-special）</option>
              </select>
              <p class="mt-0.5 text-[11px] text-[#B8BCCC]">
                STRUCTURE 适用于子项有排行分布（如 ICD 编码分布）
              </p>
            </label>

            <!-- 子项配置（JSON编辑器） -->
            <div v-if="form.kind === 'core18'">
              <label class="block text-[12px]">
                <span class="mb-1 flex items-center gap-1.5 font-medium text-[#596080]">
                  子项配置（JSON）
                  <span class="text-[#B8BCCC] font-normal">— STRUCTURE-special 专用，如为其他类型请留空</span>
                  <button
                    type="button"
                    @click.stop="subitemConfigHelpVisible = true"
                    class="w-4 h-4 rounded-full bg-[#b8c9e8]/60 text-[#596080] text-[11px] font-medium flex items-center justify-center hover:bg-[#2E57E5] hover:text-white transition-colors cursor-pointer"
                    title="子项配置说明"
                  >?</button>
                </span>
                <textarea
                  v-model="subitemConfigInput"
                  rows="5"
                  placeholder='{&#10;  "type": "COMPOSITE_MULTI_RANKING",&#10;  "rankings": [&#10;    { "id": "treatment", "name": "治疗性操作 TOP20", "key_prefix": "OP_T_", "color": "#12B881", "limit": 20 },&#10;    { "id": "diagnosis", "name": "诊断性操作 TOP20", "key_prefix": "OP_D_", "color": "#2E57E5", "limit": 20 }&#10;  ]&#10;}'
                  class="w-full resize-y rounded-[2px] border border-amber-200 bg-amber-50/40 px-3 py-2.5 font-mono text-[11px] leading-relaxed text-[#334155] focus:border-amber-400 focus:outline-none"
                  @focus="onSubitemConfigFocus"
                  @blur="onSubitemConfigBlur"
                />
              </label>
              <!-- 预览区（失焦后才更新） -->
              <div v-if="!subitemConfigFocused">
                <div v-if="subitemConfigParseError" class="mt-1 text-[11px] text-red-500">
                  JSON 格式错误：{{ subitemConfigParseError }}
                </div>
                <div v-else-if="subitemConfigDisplay" class="mt-1 text-[11px] text-emerald-600">
                  {{ subitemConfigDisplay }}
                </div>
              </div>
            </div>
          </template>

          <!-- 计算结果预览说明 -->
          <div class="rounded-[2px] border border-emerald-200 bg-emerald-50 p-3">
            <p class="mb-1.5 text-[11px] font-semibold text-emerald-700">计算结果预览说明</p>
            <p class="text-[11px] leading-relaxed text-emerald-600">
              <template v-if="(form.kind === 'core18' || form.kind === 'four') && form.calcType === 'ratio'">
                系统将执行分子 SQL 与分母 SQL，将两者 COUNT 结果相除并乘以 100% 作为指标值输出。SQL 中请仅写
                <code class="rounded bg-white/80 px-1 font-mono text-[10px] text-emerald-800">SELECT COUNT(*)</code>
                语句，查询返回的计数结果将参与比值计算。
              </template>
              <template v-else-if="(form.kind === 'core18' || form.kind === 'four') && form.calcType === 'count'">
                系统将执行 SQL 语句，直接输出 COUNT 查询的计数结果作为指标值。SQL 中请仅写
                <code class="rounded bg-white/80 px-1 font-mono text-[10px] text-emerald-800">SELECT COUNT(*)</code>
                语句。
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
              <!-- 分子时间过滤字段 -->
              <div class="mb-3">
                <p class="mb-1.5 text-[11px] font-medium text-[#596080]">分子时间过滤字段</p>
                <div class="flex items-center gap-2">
                  <select
                    v-model="form.numeratorDateField"
                    class="flex-1 cursor-pointer rounded-[2px] border border-purple-200 bg-purple-50/40 px-2 py-1.5 text-[11px] text-[#334155] focus:border-purple-400 focus:outline-none"
                  >
                    <option value="discharge">discharge（出院时间）</option>
                    <option value="admission">admission（入院时间）</option>
                    <option value="PSCP_OPN_DT">PSCP_OPN_DT（手术操作时间）</option>
                    <option value="VST_DT_TM">VST_DT_TM（就诊时间）</option>
                    <option value="ADMN_DT_TM">ADMN_DT_TM（入院时间）</option>
                    <option value="DSCG_DT_TM">DSCG_DT_TM（出院时间）</option>
                    <option value="custom">自定义…</option>
                  </select>
                  <input
                    v-if="form.numeratorDateField === 'custom'"
                    v-model="form.numeratorDateFieldCustom"
                    type="text"
                    placeholder="直接输入列名，如 t1.DSCG_DT_TM"
                    class="flex-1 rounded-[2px] border border-purple-300 bg-purple-50 px-2 py-1.5 text-[11px] font-mono focus:border-purple-400 focus:outline-none"
                  />
                </div>
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

          <!-- 分母 SQL（比值型显示） -->
          <div v-if="(form.kind === 'core18' || form.kind === 'four') && form.calcType === 'ratio'" class="rounded-[2px] border border-[#b8c9e8]/60 bg-white shadow-sm">
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
              <!-- 分母时间过滤字段 -->
              <div class="mb-3">
                <p class="mb-1.5 text-[11px] font-medium text-[#596080]">分母时间过滤字段</p>
                <div class="flex items-center gap-2">
                  <select
                    v-model="form.denominatorDateField"
                    class="flex-1 cursor-pointer rounded-[2px] border border-sky-200 bg-sky-50/40 px-2 py-1.5 text-[11px] text-[#334155] focus:border-sky-400 focus:outline-none"
                  >
                    <option value="discharge">discharge（出院时间）</option>
                    <option value="admission">admission（入院时间）</option>
                    <option value="PSCP_OPN_DT">PSCP_OPN_DT（手术操作时间）</option>
                    <option value="VST_DT_TM">VST_DT_TM（就诊时间）</option>
                    <option value="ADMN_DT_TM">ADMN_DT_TM（入院时间）</option>
                    <option value="DSCG_DT_TM">DSCG_DT_TM（出院时间）</option>
                    <option value="custom">自定义…</option>
                  </select>
                  <input
                    v-if="form.denominatorDateField === 'custom'"
                    v-model="form.denominatorDateFieldCustom"
                    type="text"
                    placeholder="直接输入列名，如 t1.DSCG_DT_TM"
                    class="flex-1 rounded-[2px] border border-sky-300 bg-sky-50 px-2 py-1.5 text-[11px] font-mono focus:border-sky-400 focus:outline-none"
                  />
                </div>
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

    <!-- 子项配置说明弹窗 -->
    <Teleport to="body">
      <div v-if="subitemConfigHelpVisible" class="fixed inset-0 z-[100] flex items-center justify-center bg-gray-900/50 backdrop-blur-sm" @click.self="subitemConfigHelpVisible = false">
        <div class="w-[620px] max-h-[80vh] bg-white rounded-[2px] shadow-2xl flex flex-col animate-fade-in border border-[#b8c9e8]/60">
          <div class="px-5 py-3.5 border-b border-[#b8c9e8]/60 flex justify-between items-center bg-[#e8eef9]">
            <h2 class="text-[14px] font-bold text-[#1F264D]">子项配置（JSON）说明</h2>
            <button @click="subitemConfigHelpVisible = false" class="p-1.5 hover:bg-[#b8c9e8]/30 rounded-full text-[#596080] transition-colors"><X class="w-4 h-4" /></button>
          </div>
          <div class="flex-1 overflow-y-auto p-5 space-y-4">

            <!-- 基础说明 -->
            <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
              <h3 class="font-bold text-[#1F264D] text-[13px] mb-2">子项配置是什么？</h3>
              <p class="text-[12px] text-[#596080] leading-relaxed">
                子项配置（JSON）仅用于 <strong>STRUCTURE-special（双排行榜型）</strong>，用于定义多排行榜的结构和 SQL 字段映射。其他类型（RATE / RATE-special / STRUCTURE）<strong>无需配置此项，留空即可</strong>。
              </p>
            </div>

            <!-- 五种模板类型与子项配置的关系 -->
            <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
              <h3 class="font-bold text-[#1F264D] text-[13px] mb-2">四种模板类型一览</h3>
              <div class="space-y-2 text-[11px]">
                <div class="flex items-start gap-2">
                  <span class="shrink-0 w-20 text-[10px] font-semibold text-[#1F264D] bg-[#e8eef9] px-1.5 py-0.5 rounded">STRUCTURE</span>
                  <span class="text-[#596080]">排行榜型，无需子项配置。SQL 直接返回分组聚合结果（见下方排行榜型 SQL 示例），系统自动渲染排行榜图表。</span>
                </div>
                <div class="flex items-start gap-2">
                  <span class="shrink-0 w-20 text-[10px] font-semibold text-[#1F264D] bg-[#e8eef9] px-1.5 py-0.5 rounded">STRUCTURE-special</span>
                  <span class="text-[#596080]">双排行榜型，无需子项配置。SQL 通过 <code class="font-mono text-[10px] bg-[#f0f4ff] px-1 rounded">ranking_key</code> 前缀区分治疗性/诊断性（如 <code class="font-mono text-[10px] bg-[#f0f4ff] px-1 rounded">OP_T_</code> / <code class="font-mono text-[10px] bg-[#f0f4ff] px-1 rounded">OP_D_</code>），系统自动拆分渲染两个排行榜。当前 ICD-9-CM-3 指标先用单排行榜实现（降级），双排行榜支持后续按相同前缀规则扩展。</span>
                </div>
                <div class="flex items-start gap-2">
                  <span class="shrink-0 w-20 text-[10px] font-semibold text-[#1F264D] bg-[#e8eef9] px-1.5 py-0.5 rounded">RATE / RATE-special</span>
                  <span class="text-[#596080]">比值型，无需子项配置。SQL 返回分子/分母计数，系统自动计算比值并渲染进度环和趋势图。</span>
                </div>
              </div>
            </div>

            <!-- 字段详解 -->
            <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
              <h3 class="font-bold text-[#1F264D] text-[13px] mb-3">字段详解</h3>
              <div class="space-y-2">
                <div class="grid grid-cols-[80px_1fr] gap-x-3 text-[11px]">
                  <span class="font-mono text-emerald-600 font-semibold">type</span>
                  <span class="text-[#596080]">必填。配置类型，取值 <code class="font-mono text-[10px] bg-[#f0f4ff] px-1 rounded">COMPOSITE_MULTI_RANKING</code></span>
                </div>
                <div class="border-t border-[#e8eef9]"></div>
                <div class="grid grid-cols-[100px_1fr] gap-x-3 text-[11px]">
                  <span class="font-mono text-emerald-600 font-semibold">rankings</span>
                  <span class="text-[#596080]">必填，排行榜配置数组。每个排行榜配置字段含义如下：</span>
                </div>
                <div class="ml-6 space-y-1.5 text-[11px] text-[#596080]">
                  <div class="grid grid-cols-[100px_1fr] gap-x-2">
                    <span class="font-mono text-sky-600">id</span>
                    <span>排行榜唯一标识（英文）</span>
                  </div>
                  <div class="grid grid-cols-[100px_1fr] gap-x-2">
                    <span class="font-mono text-sky-600">name</span>
                    <span>图表展示的排行榜名称（中文）</span>
                  </div>
                  <div class="grid grid-cols-[100px_1fr] gap-x-2">
                    <span class="font-mono text-sky-600">key_prefix</span>
                    <span>SQL 返回结果中该排行榜数据的 key 前缀（如 OP_T_、OP_D_）</span>
                  </div>
                  <div class="grid grid-cols-[100px_1fr] gap-x-2">
                    <span class="font-mono text-sky-600">color</span>
                    <span>该排行榜图表的展示颜色（如 #12B881）</span>
                  </div>
                  <div class="grid grid-cols-[100px_1fr] gap-x-2">
                    <span class="font-mono text-sky-600">limit</span>
                    <span>该排行榜展示上限，默认 20</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- SQL 返回格式要求 -->
            <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
              <h3 class="font-bold text-[#1F264D] text-[13px] mb-2">SQL 返回格式要求</h3>
              <div class="space-y-2 text-[11px] text-[#596080]">
                <div class="bg-gray-50 border border-gray-200 rounded-[2px] p-3">
                  <p class="font-semibold text-gray-600 mb-1">STRUCTURE-special（COMPOSITE_MULTI_RANKING）：通过 key_prefix 前缀区分多排行榜</p>
                  <p class="text-[11px] text-gray-500 mb-1.5">当 subitem_config.type 为 <code class="font-mono text-[10px] bg-white/80 px-1 rounded">COMPOSITE_MULTI_RANKING</code> 时，分析台以 <code class="font-mono text-[10px] bg-white/80 px-1 rounded">multi</code> 模式渲染多排行榜；通过 SQL 中排行榜维度的 key 前缀区分不同排行榜。</p>
                  <div class="font-mono text-[11px] text-[#334155] mt-1 bg-white rounded border border-gray-200 p-2">
-- 多排行榜，通过 key_prefix 前缀区分<br/>
-- 治疗性操作前缀 "OP_T_" + 手术编码<br/>
-- 诊断性操作前缀 "OP_D_" + 诊断编码<br/>
SELECT 'OP_T_'||ICD9CM_CODE AS ranking_key, COUNT(*) AS cnt FROM ...<br/>
UNION ALL<br/>
SELECT 'OP_D_'||DIAG_CODE AS ranking_key, COUNT(*) AS cnt FROM ...
                  </div>
                </div>
                <div class="bg-sky-50 border border-sky-200 rounded-[2px] p-3">
                  <p class="font-semibold text-sky-700 mb-1">STRUCTURE：单一排行榜，SQL 返回分组聚合后的多行数据</p>
                  <div class="font-mono text-[11px] text-[#334155] mt-1 bg-white rounded border border-sky-200 p-2">
SELECT ICD10_CODE, COUNT(*) AS disease_cnt FROM ...<br/>
GROUP BY ICD10_CODE ORDER BY disease_cnt DESC LIMIT 50
                  </div>
                  <p class="text-[11px] text-sky-600 mt-1.5">SQL 应返回分组聚合后的结果。STRUCTURE-special 仅需在 STRUCTURE 基础上通过 UNION ALL 和 key_prefix 前缀拼接多个排行榜即可。</p>
                </div>
              </div>
            </div>

            <!-- 注意事项 -->
            <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
              <h3 class="font-bold text-[#1F264D] text-[13px] mb-2">注意事项</h3>
              <ul class="text-[11px] text-[#596080] space-y-1.5 leading-relaxed">
                <li class="flex items-start gap-2">
                  <span class="mt-0.5 w-1.5 h-1.5 rounded-full bg-red-400 shrink-0"></span>
                  <span>JSON 中的字段名（如 key_prefix、ranking_key 等）与 SQL 返回的列名必须完全一致，<strong>大小写敏感</strong>。</span>
                </li>
                <li class="flex items-start gap-2">
                  <span class="mt-0.5 w-1.5 h-1.5 rounded-full bg-[#2E57E5] shrink-0"></span>
                  <span>不确定该用哪种类型时，先选择「自动推断」，系统会根据指标特征推荐合适的模板类型。</span>
                </li>
              </ul>
            </div>

          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, X } from 'lucide-vue-next'
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

const templateId = ref<string | number>('')
const templateList = ref<Indicator[]>([])

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
  numeratorDateField: 'discharge',
  numeratorDateFieldCustom: '',
  denominatorDateField: 'discharge',
  denominatorDateFieldCustom: '',
  numInvolvedTables: [] as string[],
  denInvolvedTables: [] as string[],
  promptContent: '',
  templateType: '' as '' | 'RATE' | 'STRUCTURE' | 'STRUCTURE-special',
  subitemConfig: '',
})

const subitemConfigInput = ref('')
const subitemConfigFocused = ref(false)
const subitemConfigDisplay = ref('')
const subitemConfigParseError = ref('')
const subitemConfigHelpVisible = ref(false)

function onSubitemConfigBlur() {
  subitemConfigFocused.value = false
  form.value.subitemConfig = subitemConfigInput.value
  if (!form.value.subitemConfig.trim()) {
    subitemConfigParseError.value = ''
    subitemConfigDisplay.value = ''
    return
  }
  try {
    JSON.parse(form.value.subitemConfig)
    subitemConfigParseError.value = ''
    subitemConfigDisplay.value = buildSubitemConfigSummary(form.value.subitemConfig)
  } catch (e: unknown) {
    subitemConfigParseError.value = e instanceof Error ? e.message : String(e)
    subitemConfigDisplay.value = ''
  }
}

function onSubitemConfigFocus() {
  subitemConfigFocused.value = true
  subitemConfigInput.value = form.value.subitemConfig
}

function buildSubitemConfigSummary(raw: string): string {
  try {
    const cfg = JSON.parse(raw)
    if (cfg.type === 'COMPOSITE_MULTI_RANKING') {
      const rankings = (cfg.rankings as Record<string, unknown>[] | undefined) ?? []
      return `多排行榜型，共 ${rankings.length} 个排行榜：${rankings.map((r) => String(r.name || r.id)).join('、')}`
    }
    return `type=${cfg.type}`
  } catch {
    return ''
  }
}

const templateOptions = computed(() => {
  return templateList.value.map((r) => ({
    value: String(r.id),
    label: r.name,
    seq: r.seq || 0,
  }))
})

const isEditing = computed(() => {
  return templateId.value !== ''
})

async function loadTemplateList() {
  try {
    const data = form.value.kind === 'core18'
      ? await indicatorsApi.getCore18Indicators()
      : await indicatorsApi.getFourIndicators()
    templateList.value = data || []
  } catch (e) {
    console.error('加载模板列表失败:', e)
    templateList.value = []
  }
}

function onTemplateChange() {
  if (!templateId.value) {
    form.value.name = ''
    form.value.category = ''
    form.value.seq = 1
    form.value.scope = ''
    form.value.workContent = ''
    form.value.ruleLogic = ''
    form.value.description = ''
    form.value.denominator = ''
    form.value.numerator = ''
    form.value.formula = ''
    form.value.numeratorSql = ''
    form.value.denominatorSql = ''
    form.value.numInvolvedTables = []
    form.value.denInvolvedTables = []
    form.value.promptContent = ''
    subitemConfigInput.value = ''
    subitemConfigParseError.value = ''
    subitemConfigDisplay.value = ''
    if (form.value.kind === 'core18') {
      form.value.calcType = 'ratio'
      form.value.computable = '是'
      form.value.useLlm = '否'
    } else {
      form.value.calcType = 'ratio'
    }
    return
  }

  const selected = templateList.value.find((r) => String(r.id) === String(templateId.value))
  if (!selected) return

  form.value.name = selected.name || ''
  form.value.category = selected.category || ''
  if (selected.seq) {
    form.value.seq = selected.seq
  }

  if (form.value.kind === 'core18') {
    form.value.description = selected.description || ''
    form.value.numerator = selected.numerator_desc || ''
    form.value.denominator = selected.denominator_desc || ''
    form.value.formula = selected.formula || ''
    form.value.numeratorSql = selected.numerator_sql || ''
    form.value.denominatorSql = selected.denominator_sql || ''
    form.value.promptContent = selected.prompt_content || ''

    // 时间过滤字段（优先读 numerator_date_field / denominator_date_field，兜底读 date_field）
    const rawNumDate = (selected as Record<string, unknown>).numerator_date_field as string | undefined
    const rawDenDate = (selected as Record<string, unknown>).denominator_date_field as string | undefined
    const rawDate   = (selected as Record<string, unknown>).date_field as string | undefined
    const numVal = rawNumDate || rawDate || 'discharge'
    const denVal = rawDenDate || rawDate || 'discharge'
    const known = ['discharge', 'admission', 'PSCP_OPN_DT', 'VST_DT_TM', 'ADMN_DT_TM', 'DSCG_DT_TM']
    form.value.numeratorDateField = known.includes(numVal) ? numVal : 'custom'
    form.value.numeratorDateFieldCustom = known.includes(numVal) ? '' : numVal
    form.value.denominatorDateField = known.includes(denVal) ? denVal : 'custom'
    form.value.denominatorDateFieldCustom = known.includes(denVal) ? '' : denVal

    if (selected.calc_type === 'ratio') {
      form.value.calcType = 'ratio'
    } else if (selected.calc_type === 'count') {
      form.value.calcType = 'count'
    }
    form.value.computable = selected.is_computable ? '是' : '否'
    form.value.useLlm = selected.use_llm ? '是' : '否'
    form.value.numInvolvedTables = Array.isArray(selected.involved_tables) ? selected.involved_tables : []
    form.value.denInvolvedTables = Array.isArray(selected.involved_tables) ? selected.involved_tables : []
    const rawTT = (selected as Record<string, unknown>).template_type as string | undefined
    form.value.templateType = (rawTT || '') as typeof form.value.templateType
    const rawSC = (selected as Record<string, unknown>).subitem_config
    form.value.subitemConfig = rawSC ? JSON.stringify(rawSC, null, 2) : ''
    subitemConfigInput.value = form.value.subitemConfig
    subitemConfigParseError.value = ''
    subitemConfigDisplay.value = buildSubitemConfigSummary(form.value.subitemConfig)
  } else {
    form.value.scope = selected.scope || ''
    form.value.workContent = selected.work_content || ''
    form.value.ruleLogic = selected.rule_logic || ''
    const combined = selected.sql_content || ''
    if (combined) {
      const parts = combined.split(/-- 分子 SQL|-- 分母 SQL|\n\n/)
      if (parts.length >= 3) {
        form.value.numeratorSql = (parts[1] || '').trim()
        form.value.denominatorSql = (parts[2] || '').trim()
      } else {
        form.value.numeratorSql = combined
      }
    } else {
      form.value.numeratorSql = selected.numerator_sql || ''
      form.value.denominatorSql = selected.denominator_sql || ''
    }
    form.value.promptContent = selected.prompt_content || ''
    const rawNumDate4 = (selected as Record<string, unknown>).numerator_date_field as string | undefined
    const rawDenDate4 = (selected as Record<string, unknown>).denominator_date_field as string | undefined
    const rawDate4    = (selected as Record<string, unknown>).date_field as string | undefined
    const numVal4 = rawNumDate4 || rawDate4 || 'discharge'
    const denVal4 = rawDenDate4 || rawDate4 || 'discharge'
    const known = ['discharge', 'admission', 'PSCP_OPN_DT', 'VST_DT_TM', 'ADMN_DT_TM', 'DSCG_DT_TM']
    form.value.numeratorDateField = known.includes(numVal4) ? numVal4 : 'custom'
    form.value.numeratorDateFieldCustom = known.includes(numVal4) ? '' : numVal4
    form.value.denominatorDateField = known.includes(denVal4) ? denVal4 : 'custom'
    form.value.denominatorDateFieldCustom = known.includes(denVal4) ? '' : denVal4
    form.value.numInvolvedTables = Array.isArray(selected.involved_tables) ? selected.involved_tables : []
    form.value.denInvolvedTables = Array.isArray(selected.involved_tables) ? selected.involved_tables : []
    if (selected.calc_type === 'count') {
      form.value.calcType = 'count'
    } else {
      form.value.calcType = 'ratio'
    }
  }
}

onMounted(async () => {
  await loadTemplateList()
  if (form.value.kind === 'four') {
    const list = templateList.value
    form.value.seq = Math.max(0, ...list.map((x) => x.seq || 0)) + 1
  }
})

watch(() => form.value.kind, async () => {
  templateId.value = ''
  await loadTemplateList()
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

function resolveDateField(selectVal: string, customVal: string): string {
  return selectVal === 'custom' ? customVal.trim() : selectVal
}

async function saveIndicator() {
  if (!form.value.name.trim()) {
    alert('请填写指标名称')
    return
  }

  saving.value = true
  try {
    const isRatio = (form.value.kind === 'core18' || form.value.kind === 'four') && form.value.calcType === 'ratio'
    const combinedSql = isRatio
      ? `-- 分子 SQL\n${form.value.numeratorSql.trim()}\n\n-- 分母 SQL\n${form.value.denominatorSql.trim()}`
      : form.value.numeratorSql.trim()

    if (form.value.kind === 'core18') {
      let parsedSubitemConfig: Record<string, unknown> | null = null
      if (form.value.subitemConfig.trim()) {
        try {
          parsedSubitemConfig = JSON.parse(form.value.subitemConfig)
        } catch {
          alert('subitem_config JSON 格式错误，请检查后重试')
          saving.value = false
          return
        }
      }
      const payload: Record<string, unknown> = {
        name: form.value.name.trim(),
        description: form.value.description.trim(),
        numerator_desc: form.value.numerator.trim(),
        denominator_desc: form.value.denominator.trim(),
        formula: form.value.formula.trim(),
        numerator_sql: form.value.numeratorSql.trim(),
        denominator_sql: form.value.denominatorSql.trim(),
        sql_content: combinedSql,
        prompt_content: form.value.promptContent.trim(),
        involved_tables: [...form.value.numInvolvedTables, ...form.value.denInvolvedTables],
        calc_type: form.value.calcType,
        is_computable: form.value.computable === '是',
        use_llm: form.value.useLlm === '是',
        calc_method: 'sql',
        numerator_date_field: resolveDateField(form.value.numeratorDateField, form.value.numeratorDateFieldCustom),
        ...(isRatio ? {
          denominator_date_field: resolveDateField(form.value.denominatorDateField, form.value.denominatorDateFieldCustom),
        } : {}),
      }
      if (form.value.templateType) {
        payload.template_type = form.value.templateType
      }
      if (parsedSubitemConfig) {
        payload.subitem_config = parsedSubitemConfig
      }

      if (isEditing.value && templateId.value) {
        await indicatorsApi.updateCore18Indicator(Number(templateId.value), payload)
        alert('指标已更新')
      } else {
        await indicatorsApi.createCore18Indicator(payload)
        alert('已保存到「十八项核心制度指标」列表')
      }
    } else {
      const payload = {
        name: form.value.name.trim(),
        category: form.value.category.trim(),
        seq: form.value.seq || 1,
        scope: form.value.scope.trim() || '',
        work_content: form.value.workContent.trim() || '',
        rule_logic: form.value.ruleLogic.trim() || '',
        numerator_sql: form.value.numeratorSql.trim(),
        denominator_sql: form.value.denominatorSql.trim(),
        sql_content: combinedSql,
        prompt_content: form.value.promptContent.trim(),
        involved_tables: form.value.numInvolvedTables,
        calc_method: 'sql' as const,
        calc_type: form.value.calcType,
        numerator_date_field: resolveDateField(form.value.numeratorDateField, form.value.numeratorDateFieldCustom),
        ...(isRatio ? {
          denominator_date_field: resolveDateField(form.value.denominatorDateField, form.value.denominatorDateFieldCustom),
        } : {}),
      }

      if (isEditing.value && templateId.value) {
        await indicatorsApi.updateFourIndicator(Number(templateId.value), payload)
        alert('指标已更新')
      } else {
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
