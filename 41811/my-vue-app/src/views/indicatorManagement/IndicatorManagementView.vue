<template>
  <div class="flex h-full min-h-0 flex-col bg-white">
    <!-- 说明条（与科目零业务监测一致的 emerald 信息条，无额外框格） -->
    <div class="shrink-0 p-4">
      <div class="flex items-start rounded-[2px] border border-emerald-200 bg-emerald-50 p-2.5">
        <Info class="mr-2 mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-500" />
        <div>
          <h4 class="text-[13px] font-medium text-emerald-800">指标管理</h4>
        </div>
      </div>
    </div>

    <div class="flex min-h-0 flex-1 flex-col px-4 pb-4">
      <div class="flex min-h-0 flex-1 flex-col overflow-hidden rounded-[2px] border border-[#b8c9e8]/60 bg-white shadow-sm">
        <!-- 工具栏 -->
        <div class="flex shrink-0 items-center justify-between border-b border-emerald-100 bg-emerald-50/50 p-3.5">
          <h3 class="flex items-center text-[13px] font-semibold text-[#1F264D]">
            <Table2 class="mr-2 h-4 w-4 text-emerald-500" />
            {{ kindLabel }} — 共 {{ currentList.length }} 条
          </h3>
          <div class="flex flex-wrap items-center gap-2 relative">
            <div>
              <Search class="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[#B8BCCC]" />
              <input
                v-model="keyword"
                type="text"
                placeholder="搜索..."
                class="w-52 rounded-[2px] border border-[#b8c9e8]/60 bg-white py-1.5 pl-8 pr-3 text-[12px] focus:border-emerald-400 focus:outline-none"
              />
            </div>
            <select
              v-model="indicatorKind"
              class="cursor-pointer rounded-[2px] border border-emerald-200 bg-white py-1.5 pl-2.5 pr-8 text-[12px] text-[#1F264D] focus:border-emerald-400 focus:outline-none"
            >
              <option value="four">四要素监管指标</option>
              <option value="core18">十八项核心制度指标</option>
            </select>
            <!-- 新增（分裂按钮） -->
            <div>
              <div class="flex rounded-[2px] overflow-hidden">
                <button
                  type="button"
                  class="flex items-center gap-1 bg-emerald-600 px-3 py-1.5 text-[12px] text-white transition-colors hover:bg-emerald-700"
                  @click="openCreate('llm')"
                >
                  <Plus class="h-3.5 w-3.5" />
                  新增
                </button>
                <button
                  type="button"
                  class="flex items-center bg-emerald-600 px-1.5 py-1.5 text-[12px] text-white transition-colors hover:bg-emerald-700"
                  @click.stop="showAddMenu = !showAddMenu"
                >
                  <ChevronDown class="h-3 w-3" />
                </button>
              </div>
              <!-- 下拉菜单 -->
              <Transition name="dropdown-fade">
                <div
                  v-if="showAddMenu"
                  class="absolute left-0 top-full z-20 mt-1 min-w-[180px] rounded-[2px] border border-[#b8c9e8]/60 bg-white py-1 shadow-lg"
                >
                  <button
                    type="button"
                    class="flex w-full items-center gap-2 px-3 py-2 text-left text-[12px] text-[#1F264D] transition-colors hover:bg-emerald-50"
                    @click="openCreate('llm'); showAddMenu = false"
                  >
                    <Sparkles class="h-3.5 w-3.5 shrink-0 text-purple-500" />
                    <span>
                      <span class="font-medium">大模型新增</span>
                      <span class="ml-1 text-[11px] text-[#596080]">— 自然语言生成 SQL</span>
                    </span>
                  </button>
                  <button
                    type="button"
                    class="flex w-full items-center gap-2 px-3 py-2 text-left text-[12px] text-[#1F264D] transition-colors hover:bg-emerald-50"
                    @click="openCreate('sql'); showAddMenu = false"
                  >
                    <Database class="h-3.5 w-3.5 shrink-0 text-purple-500" />
                    <span>
                      <span class="font-medium">指标调试新增</span>
                      <span class="ml-1 text-[11px] text-[#596080]">— SQL 语句定义指标</span>
                    </span>
                  </button>
                </div>
              </Transition>
            </div>
          </div>
        </div>

        <!-- 表格 -->
        <div class="min-h-0 flex-1 overflow-auto">
          <!-- 四要素 -->
          <table v-if="indicatorKind === 'four'" class="w-full border-collapse text-left">
            <thead class="sticky top-0 z-10 border-b border-emerald-100 bg-emerald-50/60">
              <tr>
                <th class="w-12 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">序号</th>
                <th class="min-w-[160px] px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">指标名称</th>
                <th class="min-w-[88px] px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">类别</th>
                <th class="min-w-[120px] px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">范围</th>
                <th class="min-w-[200px] px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">规则逻辑</th>
                <th class="w-32 px-3 py-2.5 text-right text-[11px] font-semibold uppercase tracking-wide text-[#596080]">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#b8c9e8]/30">
              <tr v-for="row in filteredFour" :key="row.id" class="transition-colors hover:bg-emerald-50/40">
                <td class="px-3 py-2.5 text-[12px] text-[#596080]">{{ row.seq }}</td>
                <td class="max-w-xs px-3 py-2.5 text-[12px] font-medium text-[#1F264D]"><span class="line-clamp-2">{{ row.name || '—' }}</span></td>
                <td class="px-3 py-2.5 text-[12px] font-medium text-[#1F264D]">{{ row.category }}</td>
                <td class="max-w-[220px] px-3 py-2.5 text-[12px] text-[#596080]"><span class="line-clamp-1">{{ row.scope }}</span></td>
                <td class="max-w-[280px] px-3 py-2.5 text-[12px] text-[#596080]"><span class="line-clamp-2">{{ row.ruleLogic || '—' }}</span></td>
                <td class="whitespace-nowrap px-3 py-2.5 text-right text-[12px]">
                  <button type="button" class="mr-2 text-emerald-600 hover:text-emerald-800" @click="openEditFour(row)">编辑</button>
                  <button type="button" class="text-red-500 hover:text-red-700" @click="confirmDeleteFour(row)">删除</button>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- 十八项 -->
          <table v-else class="w-full border-collapse text-left">
            <thead class="sticky top-0 z-10 border-b border-emerald-100 bg-emerald-50/60">
              <tr>
                <th class="w-12 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">序号</th>
                <th class="min-w-[180px] px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">指标名</th>
                <th class="w-20 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">大模型</th>
                <th class="w-32 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">可计算</th>
                <th class="min-w-[110px] px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">分母</th>
                <th class="min-w-[110px] px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">分子</th>
                <th class="w-20 px-3 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[#596080]">计算类型</th>
                <th class="w-32 px-3 py-2.5 text-right text-[11px] font-semibold uppercase tracking-wide text-[#596080]">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#b8c9e8]/30">
              <tr v-for="row in filteredCore18" :key="row.id" class="transition-colors hover:bg-emerald-50/40">
                <td class="px-3 py-2.5 text-[12px] text-[#596080]">{{ row.seq }}</td>
                <td class="px-3 py-2.5 text-[12px] font-medium text-[#1F264D]">{{ row.name }}</td>
                <td class="px-3 py-2.5 text-[12px] text-[#596080]">{{ row.useLlm || '—' }}</td>
                <td class="px-3 py-2.5 text-[12px] text-[#596080]">{{ row.computable || '—' }}</td>
                <td class="max-w-xs px-3 py-2.5 text-[12px] text-[#596080]"><span class="line-clamp-2">{{ row.denominator }}</span></td>
                <td class="max-w-xs px-3 py-2.5 text-[12px] text-[#596080]"><span class="line-clamp-2">{{ row.numerator }}</span></td>
                <td class="px-3 py-2.5">
                  <span
                    v-if="row.calcMethod === 'textToSql' || row.calcMethod === 'sql'"
                    class="inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium"
                    :class="{
                      'bg-emerald-50 text-emerald-600 border border-emerald-200': row.calcType === 'ratio',
                      'bg-rose-50 text-rose-600 border border-rose-200': row.calcType === 'count',
                    }"
                  >{{ row.calcType === 'ratio' ? '比值型' : '计数型' }}</span>
                  <span v-else class="text-[11px] text-[#B8BCCC]">—</span>
                </td>
                <td class="whitespace-nowrap px-3 py-2.5 text-right text-[12px]">
                  <button type="button" class="mr-2 text-emerald-600 hover:text-emerald-800" @click="openEditCore18(row)">编辑</button>
                  <button type="button" class="text-red-500 hover:text-red-700" @click="confirmDeleteCore18(row)">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 抽屉：四要素表单 -->
    <Transition name="drawer-slide">
      <div
        v-if="drawerFour"
        class="fixed inset-0 z-50 flex justify-end bg-gray-900/50 backdrop-blur-sm"
        @click.self="closeDrawer"
      >
        <div class="flex h-full w-[min(560px,100%)] flex-col border-l border-emerald-100 bg-white shadow-2xl">
          <div class="flex items-center justify-between border-b border-emerald-100 bg-emerald-50 px-5 py-3.5">
            <h2 class="flex items-center text-[14px] font-bold text-[#1F264D]">
              <Activity class="mr-2 h-4 w-4 text-emerald-500" />
              {{ fourForm.id ? '编辑指标' : '新增指标' }}
            </h2>
            <button type="button" class="rounded-full p-1.5 text-[#596080] transition-colors hover:bg-emerald-100" @click="closeDrawer">
              <X class="h-4 w-4" />
            </button>
          </div>
          <div class="flex-1 space-y-4 overflow-y-auto p-5">
            <label class="block text-[12px]">
              <span class="mb-1 block text-[#596080]">类别</span>
              <input v-model="fourForm.category" type="text" class="w-full rounded-[2px] border border-[#b8c9e8]/60 px-2.5 py-2 text-[12px] focus:border-emerald-400 focus:outline-none" />
            </label>
            <label class="block text-[12px]">
              <span class="mb-1 block text-[#596080]">指标名称</span>
              <input v-model="fourForm.name" type="text" placeholder="如：越权开具抗生素" class="w-full rounded-[2px] border border-[#b8c9e8]/60 px-2.5 py-2 text-[12px] focus:border-emerald-400 focus:outline-none" />
            </label>
            <label class="block text-[12px]">
              <span class="mb-1 block text-[#596080]">范围</span>
              <textarea v-model="fourForm.scope" rows="2" class="w-full resize-y rounded-[2px] border border-[#b8c9e8]/60 px-2.5 py-2 text-[12px] focus:border-emerald-400 focus:outline-none" />
            </label>
            <label class="block text-[12px]">
              <span class="mb-1 block text-[#596080]">工作内容</span>
              <textarea v-model="fourForm.workContent" rows="3" class="w-full resize-y rounded-[2px] border border-[#b8c9e8]/60 px-2.5 py-2 text-[12px] focus:border-emerald-400 focus:outline-none" />
            </label>
            <label class="block text-[12px]">
              <span class="mb-1 block text-[#596080]">规则逻辑</span>
              <textarea v-model="fourForm.ruleLogic" rows="3" class="w-full resize-y rounded-[2px] border border-[#b8c9e8]/60 px-2.5 py-2 text-[12px] focus:border-emerald-400 focus:outline-none" />
            </label>

            <!-- 是否使用大模型计算 -->
            <div>
              <span class="mb-1 block text-[12px] text-[#596080]">是否使用大模型计算</span>
              <div class="flex flex-wrap gap-2">
                <button
                  type="button"
                  class="rounded-[2px] border px-3 py-1.5 text-[12px] transition-colors"
                  :class="fourForm.useLlm === '是'
                    ? 'bg-blue-500 border-blue-500 text-white'
                    : 'border-[#b8c9e8] bg-white text-[#596080] hover:border-emerald-400'"
                  @click="fourForm.useLlm = '是'"
                >是</button>
                <button
                  type="button"
                  class="rounded-[2px] border px-3 py-1.5 text-[12px] transition-colors"
                  :class="fourForm.useLlm === '否'
                    ? 'bg-gray-400 border-gray-400 text-white'
                    : 'border-[#b8c9e8] bg-white text-[#596080] hover:border-emerald-400'"
                  @click="fourForm.useLlm = '否'"
                >否</button>
              </div>
            </div>

            <!-- 计算类型（比值型/计数型） -->
            <div>
              <span class="mb-1 block text-[12px] text-[#596080]">计算类型</span>
              <div class="flex flex-wrap gap-2">
                <button
                  type="button"
                  class="rounded-[2px] border px-3 py-1.5 text-[12px] transition-colors"
                  :class="fourForm.calcType === 'ratio'
                    ? 'bg-emerald-500 border-emerald-500 text-white'
                    : 'border-[#b8c9e8] bg-white text-[#596080] hover:border-emerald-400'"
                  @click="fourForm.calcType = 'ratio'"
                >比值型</button>
                <button
                  type="button"
                  class="rounded-[2px] border px-3 py-1.5 text-[12px] transition-colors"
                  :class="fourForm.calcType === 'count'
                    ? 'bg-emerald-500 border-emerald-500 text-white'
                    : 'border-[#b8c9e8] bg-white text-[#596080] hover:border-emerald-400'"
                  @click="fourForm.calcType = 'count'"
                >计数型</button>
              </div>
              <p class="mt-1 text-[11px] text-[#596080]">
                {{ fourForm.calcType === 'ratio' ? '需填写分子 SQL 与分母 SQL' : '仅需填写一条 SQL 语句' }}
              </p>
            </div>

            <!-- SQL 内容 -->
            <div class="rounded-[2px] border border-blue-200 bg-blue-50 p-3">
              <p class="mb-2 text-[11px] font-medium text-blue-600">SQL 内容（由大模型自动生成，或手工录入）</p>
              <p v-if="fourForm.calcType === 'ratio'" class="mb-2 text-[11px] text-blue-500">
                请按以下格式填写，分子在前、分母在后，用 <code class="font-mono bg-white/70 px-1">-- 分子</code> / <code class="font-mono bg-white/70 px-1">-- 分母</code> 分隔
              </p>
              <textarea
                v-model="fourForm.sqlContent"
                rows="6"
                placeholder="-- 分子&#10;SELECT COUNT(DISTINCT patient_id) FROM ... WHERE ...&#10;&#10;-- 分母&#10;SELECT COUNT(DISTINCT patient_id) FROM ..."
                class="w-full resize-y rounded-[2px] border border-blue-200 bg-white px-2.5 py-2 font-mono text-[11px] focus:border-blue-400 focus:outline-none"
              />
            </div>
          </div>
          <div class="flex justify-end gap-2 border-t border-emerald-100 bg-white px-5 py-3">
            <button type="button" class="rounded-[2px] border border-[#b8c9e8]/60 px-4 py-2 text-[12px] text-[#596080] hover:bg-slate-50" @click="closeDrawer">取消</button>
            <button type="button" class="rounded-[2px] bg-emerald-600 px-4 py-2 text-[12px] text-white hover:bg-emerald-700" @click="saveFour">保存</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 抽屉：十八项表单 -->
    <Transition name="drawer-slide">
      <div
        v-if="drawerCore18"
        class="fixed inset-0 z-50 flex justify-end bg-gray-900/50 backdrop-blur-sm"
        @click.self="closeDrawer"
      >
        <div class="flex h-full w-[min(640px,100%)] flex-col border-l border-emerald-100 bg-white shadow-2xl">
          <div class="flex items-center justify-between border-b border-emerald-100 bg-emerald-50 px-5 py-3.5">
            <h2 class="flex items-center text-[14px] font-bold text-[#1F264D]">
              <Activity class="mr-2 h-4 w-4 text-emerald-500" />
              {{ core18Form.id ? '编辑指标' : '新增指标' }}
            </h2>
            <button type="button" class="rounded-full p-1.5 text-[#596080] transition-colors hover:bg-emerald-100" @click="closeDrawer">
              <X class="h-4 w-4" />
            </button>
          </div>
          <div class="flex-1 space-y-3 overflow-y-auto p-5">
            <!-- 指标名 -->
            <div class="text-[12px]">
              <label class="mb-1 block text-[#596080]">指标名</label>
              <input v-model="core18Form.name" type="text" class="w-full rounded-[2px] border border-[#b8c9e8]/60 px-2.5 py-2 text-[12px] focus:border-emerald-400 focus:outline-none" />
            </div>

            <!-- 计算类型（比值型/计数型） -->
            <div>
              <span class="mb-1 block text-[12px] text-[#596080]">计算类型</span>
              <div class="flex flex-wrap gap-2">
                <button
                  type="button"
                  class="rounded-[2px] border px-3 py-1.5 text-[12px] transition-colors"
                  :class="core18Form.calcType === 'ratio'
                    ? 'bg-emerald-500 border-emerald-500 text-white'
                    : 'border-[#b8c9e8] bg-white text-[#596080] hover:border-emerald-400'"
                  @click="core18Form.calcType = 'ratio'"
                >比值型</button>
                <button
                  type="button"
                  class="rounded-[2px] border px-3 py-1.5 text-[12px] transition-colors"
                  :class="core18Form.calcType === 'count'
                    ? 'bg-emerald-500 border-emerald-500 text-white'
                    : 'border-[#b8c9e8] bg-white text-[#596080] hover:border-emerald-400'"
                  @click="core18Form.calcType = 'count'"
                >计数型</button>
              </div>
              <p class="mt-1 text-[11px] text-[#596080]">
                {{ core18Form.calcType === 'ratio' ? '需填写分子 SQL 与分母 SQL' : '仅需填写一条 SQL 语句' }}
              </p>
            </div>

            <!-- SQL 内容 -->
            <div class="rounded-[2px] border border-blue-200 bg-blue-50 p-3">
              <p class="mb-2 text-[11px] font-medium text-blue-600">SQL 内容（由大模型自动生成，或手工录入）</p>
              <p v-if="core18Form.calcType === 'ratio'" class="mb-2 text-[11px] text-blue-500">
                请按以下格式填写，分子在前、分母在后，用 <code class="font-mono bg-white/70 px-1">-- 分子</code> / <code class="font-mono bg-white/70 px-1">-- 分母</code> 分隔
              </p>
              <p v-else class="mb-2 text-[11px] text-blue-500">
                填写一条 SQL 语句，直接输出计数结果
              </p>
              <textarea
                v-model="core18Form.sqlContent"
                rows="6"
                :placeholder="core18Form.calcType === 'ratio'
                  ? '-- 分子\nSELECT COUNT(DISTINCT patient_id) FROM ... WHERE ...\n\n-- 分母\nSELECT COUNT(DISTINCT patient_id) FROM ...'
                  : 'SELECT COUNT(DISTINCT col) FROM table WHERE ...'"
                class="w-full resize-y rounded-[2px] border border-blue-200 bg-white px-2.5 py-2 font-mono text-[11px] focus:border-blue-400 focus:outline-none"
              />
            </div>

            <!-- 核心业务字段 -->
            <div v-for="field in core18Fields" :key="field.key" class="text-[12px]">
              <label class="mb-1 block text-[#596080]">{{ field.label }}</label>
              <textarea
                v-if="field.long"
                v-model="core18Form[field.key]"
                rows="2"
                class="w-full resize-y rounded-[2px] border border-[#b8c9e8]/60 px-2.5 py-2 text-[12px] focus:border-emerald-400 focus:outline-none"
              />
              <input
                v-else
                v-model="core18Form[field.key]"
                type="text"
                class="w-full rounded-[2px] border border-[#b8c9e8]/60 px-2.5 py-2 text-[12px] focus:border-emerald-400 focus:outline-none"
              />
            </div>
          </div>
          <div class="flex justify-end gap-2 border-t border-emerald-100 bg-white px-5 py-3">
            <button type="button" class="rounded-[2px] border border-[#b8c9e8]/60 px-4 py-2 text-[12px] text-[#596080] hover:bg-slate-50" @click="closeDrawer">取消</button>
            <button type="button" class="rounded-[2px] bg-emerald-600 px-4 py-2 text-[12px] text-white hover:bg-emerald-700" @click="saveCore18">保存</button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Activity, ChevronDown, Database, Info, Plus, Search, Sparkles, Table2, X } from 'lucide-vue-next'
import {
  CALC_METHOD_LABELS,
  DEFAULT_CORE18,
  DEFAULT_FOUR_ELEMENTS,
  type CalcMethod,
  type Core18Indicator,
  type FourElementIndicator,
} from '@/data/indicatorManagementDefaults'
import { API_ENDPOINTS } from '@/config/api'
import { indicatorsApi, type Indicator } from '@/api/indicators'

const CALC_METHOD_OPTIONS: CalcMethod[] = ['none', 'textToSql', 'sql', 'prompt']

const router = useRouter()
const route = useRoute()

const indicatorKind = ref<'four' | 'core18'>('four')
const keyword = ref('')

const fourList = ref<FourElementIndicator[]>([])
const core18List = ref<Core18Indicator[]>([])

const drawerFour = ref(false)
const drawerCore18 = ref(false)

const fourForm = ref<FourElementIndicator>(emptyFour())
const core18Form = ref<Core18Indicator>(emptyCore18())
const showAddMenu = ref(false)

const kindLabel = computed(() =>
  indicatorKind.value === 'four' ? '四要素监管指标' : '十八项核心制度指标',
)

const currentList = computed(() => (indicatorKind.value === 'four' ? fourList.value : core18List.value))

function emptyFour(): FourElementIndicator {
  return {
    id: '',
    name: '',
    seq: fourList.value.length + 1,
    category: '',
    scope: '',
    workContent: '',
    ruleLogic: '',
    useLlm: '否',
    calcType: 'ratio',
    sqlContent: '',
  }
}

function emptyCore18(): Core18Indicator {
  return {
    id: '',
    seq: core18List.value.length + 1,
    name: '',
    useLlm: '',
    computable: '',
    denominator: '',
    numerator: '',
    description: '',
    denomCollectPlan: '',
    denomSource: '',
    denomPlatformTable: '',
    numeratorCollectPlan: '',
    numeratorSource: '',
    numeratorPlatformTable: '',
    formula: '',
    platformDataReady: '',
    platformSupportOutput: '',
    remark: '',
    priority: '',
    regexMatch: '',
    regexRule: '',
    calcMethod: 'none',
    calcType: 'ratio',
    sqlContent: '',
    promptContent: '',
  }
}

const core18Fields: { key: keyof Core18Indicator; label: string; long?: boolean }[] = [
  { key: 'useLlm', label: '需使用大模型计算' },
  { key: 'computable', label: '是否可计算' },
  { key: 'denominator', label: '分母', long: true },
  { key: 'numerator', label: '分子', long: true },
  { key: 'description', label: '说明', long: true },
  { key: 'denomCollectPlan', label: '分母采集方案', long: true },
  { key: 'denomSource', label: '分母来源' },
  { key: 'denomPlatformTable', label: '分母三医平台数据表名称', long: true },
  { key: 'numeratorCollectPlan', label: '分子采集方案', long: true },
  { key: 'numeratorSource', label: '分子来源' },
  { key: 'numeratorPlatformTable', label: '分子三医平台数据表名称', long: true },
  { key: 'formula', label: '计算公式', long: true },
  { key: 'platformDataReady', label: '三医平台中是否具备相关数据源（含备注）', long: true },
  { key: 'platformSupportOutput', label: '三医平台现有数据是否支持产出' },
  { key: 'remark', label: '备注', long: true },
  { key: 'priority', label: '产出优先级' },
  { key: 'regexMatch', label: '传统正则匹配' },
  { key: 'regexRule', label: '传统正则口径', long: true },
]

async function loadFromBackend() {
  try {
    const [four, core18] = await Promise.all([
      indicatorsApi.getFourIndicators().catch(async (e) => {
        const text = await fetch(API_ENDPOINTS.fourIndicators).then(r => r.text()).catch(() => 'fetch failed')
        console.error('[four API call failed]', e, '| raw response:', text.slice(0, 200))
        return []
      }),
      indicatorsApi.getCore18Indicators().catch(async (e) => {
        const text = await fetch(API_ENDPOINTS.core18Indicators).then(r => r.text()).catch(() => 'fetch failed')
        console.error('[core18 API call failed]', e, '| raw response:', text.slice(0, 200))
        return []
      }),
    ])
    console.log('[API] four:', four.length, 'core18:', core18.length)
    fourList.value = four.length > 0 ? four.map(_backendToFour) : JSON.parse(JSON.stringify(DEFAULT_FOUR_ELEMENTS))
    core18List.value = core18.length > 0 ? core18.map(_backendToCore18) : JSON.parse(JSON.stringify(DEFAULT_CORE18))
  } catch (e) {
    console.error('[loadFromBackend]', e)
    fourList.value = JSON.parse(JSON.stringify(DEFAULT_FOUR_ELEMENTS))
    core18List.value = JSON.parse(JSON.stringify(DEFAULT_CORE18))
  }
}

function _backendToFour(row: Indicator): FourElementIndicator {
  return {
    id: String(row.id),
    name: row.name,
    seq: row.seq || 1,
    category: row.category || '',
    scope: row.scope || '',
    workContent: row.work_content || '',
    ruleLogic: row.rule_logic || '',
    useLlm: row.use_llm ? '是' : '否',
    calcType: (row.calc_type as 'ratio' | 'count') || 'ratio',
    sqlContent: row.sql_content || '',
  }
}

function _backendToCore18(row: Indicator): Core18Indicator {
  return {
    id: String(row.id),
    seq: row.seq || 1,
    name: row.name,
    useLlm: row.use_llm ? '是' : '',
    computable: row.is_computable ? '是' : '',
    denominator: row.denominator_desc || row.description || '',
    numerator: row.numerator_desc || '',
    description: row.description || '',
    denomCollectPlan: '',
    denomSource: '',
    denomPlatformTable: '',
    numeratorCollectPlan: '',
    numeratorSource: '',
    numeratorPlatformTable: '',
    formula: row.formula || '',
    platformDataReady: '',
    platformSupportOutput: '',
    remark: row.remark || '',
    priority: row.priority || '',
    regexMatch: row.regex_match ? '是' : '',
    regexRule: row.regex_rule || '',
    calcMethod: (row.use_llm ? 'textToSql' : 'sql') as CalcMethod,
    calcType: (row.calc_type as 'ratio' | 'count') || 'ratio',
    sqlContent: row.sql_content || '',
    promptContent: row.prompt_content || '',
  }
}

onMounted(() => {
  loadFromBackend()
  document.addEventListener('click', closeAddMenuIfOpen)
})

onUnmounted(() => {
  document.removeEventListener('click', closeAddMenuIfOpen)
})

function closeAddMenuIfOpen() {
  showAddMenu.value = false
}

function matchesKeyword(text: string) {
  if (!keyword.value.trim()) return true
  return text.toLowerCase().includes(keyword.value.trim().toLowerCase())
}

const filteredFour = computed(() => {
  const k = keyword.value.trim().toLowerCase()
  const base = fourList.value
  if (!k) return [...base].sort((a, b) => a.seq - b.seq)
  return base
    .filter(
      (r) =>
        matchesKeyword(r.name) ||
        matchesKeyword(r.category) ||
        matchesKeyword(r.scope) ||
        matchesKeyword(r.workContent) ||
        matchesKeyword(r.ruleLogic) ||
        String(r.seq).includes(k),
    )
    .sort((a, b) => a.seq - b.seq)
})

const filteredCore18 = computed(() => {
  const k = keyword.value.trim().toLowerCase()
  const base = core18List.value
  if (!k) return [...base].sort((a, b) => a.seq - b.seq)
  return base
    .filter((r) => {
      const flat = [String(r.seq), r.name, r.useLlm, r.computable, r.denominator, r.numerator, r.description].join(' ')
      return flat.toLowerCase().includes(k)
    })
    .sort((a, b) => a.seq - b.seq)
})

watch(indicatorKind, () => {
  keyword.value = ''
})

watch(
  () => route.query.kind,
  (k) => {
    if (k === 'four' || k === 'core18') indicatorKind.value = k
  },
  { immediate: true },
)

function openCreate(mode: 'llm' | 'sql') {
  if (mode === 'llm') {
    router.push({
      path: '/indicator-management/new',
      query: { kind: indicatorKind.value },
    })
  } else {
    router.push({
      path: '/indicator-management/sql-add',
      query: { kind: indicatorKind.value },
    })
  }
}

function openEditFour(row: FourElementIndicator) {
  fourForm.value = { ...row }
  drawerFour.value = true
}

function openEditCore18(row: Core18Indicator) {
  core18Form.value = { ...row }
  drawerCore18.value = true
}

function closeDrawer() {
  drawerFour.value = false
  drawerCore18.value = false
}

async function saveFour() {
  const f = fourForm.value
  if (!f.name.trim()) {
    alert('请填写指标名称')
    return
  }
  try {
    const payload = {
      name: f.name,
      category: f.category,
      scope: f.scope,
      work_content: f.workContent,
      rule_logic: f.ruleLogic,
      use_llm: f.useLlm === '是',
      calc_method: f.useLlm === '是' ? 'textToSql' : 'sql',
      calc_type: f.calcType,
      sql_content: f.sqlContent,
    }
    if (f.id) {
      await indicatorsApi.updateFourIndicator(Number(f.id), payload)
    } else {
      await indicatorsApi.createFourIndicator(payload)
    }
    await loadFromBackend()
    closeDrawer()
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e)
    alert(`保存失败: ${msg}`)
  }
}

async function saveCore18() {
  const f = core18Form.value
  if (!f.name.trim()) {
    alert('请填写指标名')
    return
  }
  try {
    const payload = {
      name: f.name,
      formula: f.formula,
      description: f.description,
      denominator_desc: f.denominator,
      numerator_desc: f.numerator,
      use_llm: f.useLlm === '是',
      calc_method: f.useLlm === '是' ? 'textToSql' : 'sql',
      calc_type: f.calcType,
      sql_content: f.sqlContent,
      remark: f.remark,
    }
    if (f.id) {
      await indicatorsApi.updateCore18Indicator(Number(f.id), payload)
    } else {
      await indicatorsApi.createCore18Indicator(payload)
    }
    await loadFromBackend()
    closeDrawer()
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e)
    alert(`保存失败: ${msg}`)
  }
}

async function confirmDeleteFour(row: FourElementIndicator) {
  if (!confirm(`确定删除序号 ${row.seq} 的指标吗？`)) return
  try {
    if (row.id) await indicatorsApi.deleteFourIndicator(Number(row.id))
    await loadFromBackend()
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e)
    alert(`删除失败: ${msg}`)
  }
}

async function confirmDeleteCore18(row: Core18Indicator) {
  if (!confirm(`确定删除「${row.name}」吗？`)) return
  try {
    if (row.id) await indicatorsApi.deleteCore18Indicator(Number(row.id))
    await loadFromBackend()
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e)
    alert(`删除失败: ${msg}`)
  }
}
</script>

<style scoped>
.drawer-slide-enter-active,
.drawer-slide-leave-active {
  transition: opacity 0.2s ease;
}
.drawer-slide-enter-active > div:last-child,
.drawer-slide-leave-active > div:last-child {
  transition: transform 0.25s ease;
}
.drawer-slide-enter-from,
.drawer-slide-leave-to {
  opacity: 0;
}
.drawer-slide-enter-from > div:last-child,
.drawer-slide-leave-to > div:last-child {
  transform: translateX(100%);
}

/* 新增分裂按钮下拉动画 */
.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
