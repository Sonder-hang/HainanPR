<template>
  <div class="h-full flex flex-col overflow-hidden">
    <!-- 顶部筛选栏 -->
    <div class="shrink-0 border-b border-gray-200 bg-white px-6 py-3">
      <div class="flex items-center space-x-3 flex-wrap gap-y-2">
        <!-- 要素大类联动下拉 -->
        <div class="flex items-center bg-white border border-gray-300 rounded-md overflow-hidden shadow-sm h-8 hover:border-blue-400 transition-colors">
          <div class="px-2.5 border-r border-gray-300 text-gray-500 flex items-center h-full">
            <Layers class="w-3.5 h-3.5" />
          </div>
          <select
            v-model="filterCategory"
            class="px-3 py-1 text-sm font-bold text-blue-700 bg-transparent focus:outline-none cursor-pointer min-w-[130px]"
          >
            <option value="equipment">设备比对要素</option>
            <option value="personnel">人员比对要素</option>
            <option value="institution">机构比对要素</option>
          </select>
        </div>

        <!-- 具体规则选择 -->
        <div
          :class="[
            'flex items-center bg-white border rounded-md overflow-hidden shadow-sm transition-colors h-8',
            filterCategory === 'all' ? 'border-gray-200' : 'border-blue-400'
          ]"
        >
          <select
            v-model="filterRule"
            :disabled="filterCategory === 'all'"
            :class="[
              'px-3 py-1 text-sm font-bold bg-transparent focus:outline-none min-w-[250px]',
              filterCategory === 'all'
                ? 'text-gray-400 bg-gray-50 cursor-not-allowed'
                : 'text-gray-800 cursor-pointer'
            ]"
          >
            <option v-for="rule in ruleCategories[filterCategory]" :key="rule.id" :value="rule.id">
              {{ rule.name }}
            </option>
          </select>
        </div>

        <div class="h-4 w-px bg-gray-300 mx-2"></div>

        <!-- 机构选择 -->
        <div class="flex items-center bg-white border border-gray-300 rounded-md overflow-hidden shadow-sm h-8 hover:border-blue-400 transition-colors">
          <div class="px-2.5 border-r border-gray-300 text-gray-500 flex items-center h-full">
            <Building class="w-3.5 h-3.5" />
          </div>
          <select
            v-model="filterHospital"
            class="px-2 py-1 text-sm font-medium text-gray-700 bg-transparent focus:outline-none cursor-pointer min-w-[160px]"
          >
            <option value="all">全市所有医疗机构</option>
            <option value="市第一人民医院">市第一人民医院</option>
            <option value="区中心医院">区中心医院</option>
          </select>
        </div>

        <!-- 比对结果快速过滤 (仅设备比对时显示) -->
        <div
          v-if="filterRule === 'eq-16'"
          class="flex items-center bg-white border border-gray-300 rounded-md overflow-hidden shadow-sm h-8"
        >
          <select
            v-model="filterStatus"
            class="px-3 py-1 text-sm font-bold text-gray-700 bg-transparent focus:outline-none cursor-pointer min-w-[170px]"
          >
            <option value="all">全量设备比对清单</option>
            <option value="consistent">只看：账实相符/在检</option>
            <option value="unapproved">重点查：未批先用</option>
            <option value="mismatch_qty">重点查：数量超配</option>
            <option value="calibration_overdue">重点查：强检超期</option>
          </select>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="flex-1 overflow-y-auto p-6 bg-slate-50">
      <div class="max-w-[1400px] mx-auto">
        <!-- 设备比对规则16 -->
        <div v-if="filterRule === 'eq-16'" class="space-y-6 animate-fade-in">
          <!-- 第一段：比对结果全局 KPI 卡片 -->
          <div class="grid grid-cols-4 gap-4">
            <div class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex flex-col relative overflow-hidden">
              <div class="absolute left-0 top-0 bottom-0 w-1 bg-blue-500"></div>
              <span class="text-gray-500 text-sm font-bold mb-2">系统核查设备总品类</span>
              <div class="flex items-baseline space-x-1">
                <span class="text-3xl font-black text-blue-600">{{ filteredData.length }}</span>
                <span class="text-sm font-bold text-gray-400">类</span>
              </div>
              <div class="mt-2 text-xs font-bold text-gray-500 bg-gray-50 inline-block px-2 py-1 rounded w-max border border-gray-100">基于医保上传目录提取</div>
            </div>
            <div class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex flex-col relative overflow-hidden">
              <div class="absolute left-0 top-0 bottom-0 w-1 bg-green-500"></div>
              <span class="text-gray-500 text-sm font-bold mb-2">完全合规 (账实相符/在检)</span>
              <div class="flex items-baseline space-x-1">
                <span class="text-3xl font-black text-green-500">{{ consistentCount }}</span>
                <span class="text-sm font-bold text-gray-400">类</span>
              </div>
              <div class="mt-2 text-xs font-bold text-gray-500 bg-gray-50 inline-block px-2 py-1 rounded w-max border border-gray-100">配置资质与检定均合规</div>
            </div>
            <div class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex flex-col relative overflow-hidden">
              <div class="absolute left-0 top-0 bottom-0 w-1 bg-orange-500"></div>
              <span class="text-gray-500 text-sm font-bold mb-2">底册比对异常 (超配/未批)</span>
              <div class="flex items-baseline space-x-1">
                <span class="text-3xl font-black text-orange-500">{{ abnormalCount }}</span>
                <span class="text-sm font-bold text-gray-400">类</span>
              </div>
              <div class="mt-2 text-xs font-bold text-orange-600 bg-orange-50 inline-block px-2 py-1 rounded w-max border border-orange-100">需重点核查采购配置流程</div>
            </div>
            <div class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex flex-col relative overflow-hidden">
              <div class="absolute left-0 top-0 bottom-0 w-1 bg-purple-500"></div>
              <span class="text-gray-500 text-sm font-bold mb-2">计量强检超期 (高危)</span>
              <div class="flex items-baseline space-x-1">
                <span class="text-3xl font-black text-purple-600">{{ overdueCount }}</span>
                <span class="text-sm font-bold text-gray-400">类</span>
              </div>
              <div class="mt-2 text-xs font-bold text-purple-600 bg-purple-50 inline-block px-2 py-1 rounded w-max border border-purple-100">禁止使用并冻结医保报销</div>
            </div>
          </div>

          <!-- 第二段：双列对比核心数据表 -->
          <div class="bg-white rounded-xl border border-gray-200 shadow-sm flex flex-col overflow-hidden">
            <div class="p-4 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
              <h3 class="text-sm font-bold text-gray-800 flex items-center">
                <Database class="w-4 h-4 mr-2 text-blue-600" />
                【{{ filterHospital === 'all' ? '全市' : filterHospital }}】 设备配置许可与强制检定比对明细表
              </h3>
            </div>

            <div class="overflow-x-auto">
              <table class="w-full text-left text-sm whitespace-nowrap min-w-[1000px]">
                <thead>
                  <tr>
                    <th rowspan="2" class="px-4 py-3 bg-gray-100 border-b border-r border-gray-200 font-bold text-gray-700 w-64 align-middle">
                      设备名称与类别
                    </th>
                    <th colspan="3" class="px-4 py-2 bg-blue-50 border-b border-r border-blue-200 font-bold text-blue-800 text-center">
                      卫健委审批/配置许可数据 (应有)
                    </th>
                    <th colspan="3" class="px-4 py-2 bg-slate-50 border-b border-r border-slate-200 font-bold text-slate-800 text-center">
                      医保/医院实际上报数据 (实有)
                    </th>
                    <th rowspan="2" class="px-4 py-3 bg-gray-100 border-b border-gray-200 font-bold text-gray-700 text-center align-middle w-48">
                      系统比对结论
                    </th>
                    <th rowspan="2" class="px-4 py-3 bg-gray-100 border-b border-gray-200 font-bold text-gray-700 text-center align-middle w-28">
                      操作
                    </th>
                  </tr>
                  <tr>
                    <th class="px-4 py-2 bg-white border-b border-r border-gray-200 text-xs font-bold text-gray-500">许可数量</th>
                    <th class="px-4 py-2 bg-white border-b border-r border-gray-200 text-xs font-bold text-gray-500">登记型号</th>
                    <th class="px-4 py-2 bg-white border-b border-r border-blue-200 text-xs font-bold text-gray-500">许可状态</th>
                    <th class="px-4 py-2 bg-white border-b border-r border-gray-200 text-xs font-bold text-gray-500">实际上报数量</th>
                    <th class="px-4 py-2 bg-white border-b border-r border-gray-200 text-xs font-bold text-gray-500">实际上报型号</th>
                    <th class="px-4 py-2 bg-white border-b border-r border-slate-200 text-xs font-bold text-gray-500">强制检定状态</th>
                  </tr>
                </thead>

                <tbody class="divide-y divide-gray-200">
                  <tr
                    v-for="(item, index) in filteredData"
                    :key="index"
                    class="hover:bg-blue-50/30 transition-colors"
                  >
                    <td class="px-4 py-4 border-r border-gray-100">
                      <div class="font-bold text-gray-900">{{ item.equipmentName }}</div>
                      <div class="text-xs text-gray-500 mt-1">{{ item.category }}</div>
                    </td>

                    <td
                      :class="[
                        'px-4 py-4 border-r border-gray-100 font-bold text-center',
                        item.matchStatus === 'mismatch_qty' ? 'text-gray-900' : 'text-gray-700'
                      ]"
                    >
                      {{ item.approvedData.quantity }} 台
                    </td>
                    <td class="px-4 py-4 border-r border-gray-100 text-xs text-gray-600 truncate max-w-[150px]">
                      {{ item.approvedData.models }}
                    </td>
                    <td
                      :class="[
                        'px-4 py-4 border-r border-blue-100 text-xs font-bold',
                        item.matchStatus === 'unapproved' ? 'text-red-500' : 'text-green-600'
                      ]"
                    >
                      {{ item.approvedData.licenseStatus }}
                    </td>

                    <td
                      :class="[
                        'px-4 py-4 border-r border-gray-100 font-bold text-center',
                        item.matchStatus === 'mismatch_qty'
                          ? item.actualData.quantity > item.approvedData.quantity
                            ? 'text-red-600 bg-red-50/50'
                            : 'text-orange-600'
                          : 'text-gray-700'
                      ]"
                    >
                      {{ item.actualData.quantity }} 台
                    </td>
                    <td class="px-4 py-4 border-r border-gray-100 text-xs text-gray-600 truncate max-w-[150px]">
                      {{ item.actualData.models }}
                    </td>
                    <td
                      :class="[
                        'px-4 py-4 border-r border-slate-100 text-xs font-bold',
                        item.matchStatus === 'calibration_overdue'
                          ? 'text-red-500 bg-red-50/50'
                          : item.actualData.calibration === '-'
                          ? 'text-gray-400'
                          : 'text-green-600'
                      ]"
                    >
                      {{ item.actualData.calibration }}
                    </td>

                    <td class="px-4 py-4 text-center">
                      <span
                        :class="[
                          'inline-flex items-center px-2 py-1 rounded text-xs font-bold',
                          getStatusBadgeClass(item.matchStatus)
                        ]"
                      >
                        <component :is="getStatusIcon(item.matchStatus)" class="w-3.5 h-3.5 mr-1" />
                        {{ item.matchDesc }}
                      </span>
                    </td>

                    <td class="px-4 py-4 text-center">
                      <template v-if="item.matchStatus === 'consistent'">
                        <span class="text-gray-400 text-xs font-medium">-</span>
                      </template>
                      <template v-else-if="confirmedIds.includes(item.id)">
                        <span class="inline-flex items-center text-green-600 text-xs font-bold">
                          <CheckCircle2 class="w-3.5 h-3.5 mr-1" />已核查
                        </span>
                      </template>
                      <template v-else>
                        <button
                          @click="handleConfirm(item.id)"
                          class="px-3 py-1.5 bg-white border border-blue-300 text-blue-600 hover:bg-blue-50 rounded text-xs font-bold transition-colors shadow-sm"
                        >
                          核实确认
                        </button>
                      </template>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- 底部操作指导 -->
          <div class="bg-orange-50 border border-orange-200 rounded-lg p-4 flex items-start space-x-3 shadow-sm">
            <AlertCircle class="w-5 h-5 text-orange-500 shrink-0 mt-0.5" />
            <div>
              <h4 class="text-sm font-bold text-orange-800 mb-1">系统干预与核查指引</h4>
              <p class="text-xs text-orange-700 leading-relaxed font-medium">
                1. 对于 <span class="font-bold text-red-600">"未批先用"</span> 或 <span class="font-bold text-purple-600">"计量强检超期"</span> 的设备，系统将自动对该设备在院内关联的医保结算通道进行熔断阻断。<br/>
                2. 对于 <span class="font-bold text-orange-600">"数量超配"</span> 或有账无物的异常条目，请及时点击"核实确认"并移交线下实地校验。
              </p>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div
          v-else
          class="h-[400px] flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-xl bg-gray-50 text-gray-400"
        >
          <ArrowRightLeft class="w-16 h-16 mb-4 opacity-40 text-blue-500" />
          <p class="font-bold text-xl text-gray-600 mb-2">标准双底册比对框架已就绪</p>
          <p class="text-sm mt-2 font-medium">请在顶部下拉框中选择具体的【比对要素】与【规则项目】。</p>
          <div class="mt-6 flex space-x-4 text-xs text-gray-400 bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div class="flex items-center">
              <CheckCircle2 class="w-4 h-4 text-green-500 mr-1" /> 支持设备账实比对
            </div>
            <div class="w-px bg-gray-200"></div>
            <div class="flex items-center">
              <Users class="w-4 h-4 text-orange-500 mr-1" /> 支持人员注册比对
            </div>
            <div class="w-px bg-gray-200"></div>
            <div class="flex items-center">
              <Building class="w-4 h-4 text-blue-500 mr-1" /> 支持机构床位比对
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Activity,
  AlertCircle,
  ArrowRightLeft,
  Building,
  CheckCircle2,
  Database,
  Layers,
  Users,
  FileSearch,
  XCircle,
  TimerOff,
  AlertTriangle,
} from 'lucide-vue-next'

// 比对规则分类映射表
const ruleCategories: Record<string, Array<{ id: string; name: string }>> = {
  all: [{ id: 'all', name: '请先选择比对要素' }],
  equipment: [
    { id: 'all', name: '所有设备比对专题' },
    { id: 'eq-16', name: '设备配置许可与实际上报验证' },
  ],
  personnel: [
    { id: 'all', name: '所有人员比对专题' },
    { id: 'pe-mock', name: '执业注册点与医保结算点比对 (示例)' },
  ],
  institution: [
    { id: 'all', name: '所有机构比对专题' },
    { id: 'in-mock', name: '机构备案床位与实际床位比对 (示例)' },
  ],
}

// 模拟的比对数据
const mockComparisonData = [
  {
    id: 'EQ-DIFF-001',
    equipmentName: '64排及以上螺旋CT',
    category: '甲类大型设备',
    hospital: '市第一人民医院',
    approvedData: {
      quantity: 2,
      models: 'GE Discovery, 联影 uCT780',
      licenseStatus: '已许可 (至2028年)',
    },
    actualData: {
      quantity: 2,
      models: 'GE Discovery, 联影 uCT780',
      calibration: '已强检 (合格)',
    },
    matchStatus: 'consistent',
    matchDesc: '账实相符且在检',
  },
  {
    id: 'EQ-DIFF-002',
    equipmentName: '3.0T 医用磁共振成像设备 (MRI)',
    category: '乙类大型设备',
    hospital: '市第一人民医院',
    approvedData: {
      quantity: 1,
      models: '西门子 MAGNETOM',
      licenseStatus: '已许可 (至2027年)',
    },
    actualData: {
      quantity: 2,
      models: '西门子 MAGNETOM, 飞利浦 Lumina',
      calibration: '已强检 (合格)',
    },
    matchStatus: 'mismatch_qty',
    matchDesc: '数量超配 (超1台)',
  },
  {
    id: 'EQ-DIFF-003',
    equipmentName: '正电子发射型磁共振成像系统 (PET-MR)',
    category: '甲类大型设备',
    hospital: '市第一人民医院',
    approvedData: {
      quantity: 0,
      models: '-',
      licenseStatus: '未取得配置许可',
    },
    actualData: {
      quantity: 1,
      models: '联影 uPMR 790',
      calibration: '未检定',
    },
    matchStatus: 'unapproved',
    matchDesc: '无资质使用 (未批先用)',
  },
  {
    id: 'EQ-DIFF-004',
    equipmentName: '多参数监护仪 / 医用输液泵',
    category: '强制检定计量设备',
    hospital: '市第一人民医院',
    approvedData: {
      quantity: 45,
      models: '多品牌混合',
      licenseStatus: '无需专项许可',
    },
    actualData: {
      quantity: 45,
      models: '多品牌混合',
      calibration: '超期未检 (逾期2个月)',
    },
    matchStatus: 'calibration_overdue',
    matchDesc: '计量强检超期',
  },
  {
    id: 'EQ-DIFF-005',
    equipmentName: '体外冲击波碎石机',
    category: '常规治疗设备',
    hospital: '市第一人民医院',
    approvedData: {
      quantity: 1,
      models: '国产 XXX型',
      licenseStatus: '已备案',
    },
    actualData: {
      quantity: 0,
      models: '-',
      calibration: '-',
    },
    matchStatus: 'missing',
    matchDesc: '长期闲置或有账无物',
  },
]

// 状态管理
const filterCategory = ref('equipment')
const filterRule = ref('eq-16')
const filterHospital = ref('市第一人民医院')
const filterStatus = ref('all')
const confirmedIds = ref<string[]>([])

// 筛选后的数据
const filteredData = computed(() => {
  return mockComparisonData.filter((item) => {
    const matchHospital = filterHospital.value === 'all' || item.hospital === filterHospital.value
    const matchStatus = filterStatus.value === 'all' || item.matchStatus === filterStatus.value
    return matchHospital && matchStatus
  })
})

// 统计计数
const consistentCount = computed(() => {
  return mockComparisonData.filter((item) => item.matchStatus === 'consistent').length
})

const abnormalCount = computed(() => {
  return mockComparisonData.filter(
    (item) => item.matchStatus === 'mismatch_qty' || item.matchStatus === 'unapproved' || item.matchStatus === 'missing'
  ).length
})

const overdueCount = computed(() => {
  return mockComparisonData.filter((item) => item.matchStatus === 'calibration_overdue').length
})

// 确认操作
const handleConfirm = (id: string) => {
  if (!confirmedIds.value.includes(id)) {
    confirmedIds.value.push(id)
  }
}

// 状态徽章样式
const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'consistent':
      return 'bg-green-100 text-green-700 border border-green-200'
    case 'mismatch_qty':
      return 'bg-orange-100 text-orange-700 border border-orange-200'
    case 'unapproved':
      return 'bg-red-100 text-red-700 border border-red-200'
    case 'missing':
      return 'bg-gray-100 text-gray-600 border border-gray-300'
    case 'calibration_overdue':
      return 'bg-purple-100 text-purple-700 border border-purple-200'
    default:
      return ''
  }
}

// 状态图标
const getStatusIcon = (status: string) => {
  switch (status) {
    case 'consistent':
      return CheckCircle2
    case 'mismatch_qty':
      return AlertTriangle
    case 'unapproved':
      return XCircle
    case 'missing':
      return FileSearch
    case 'calibration_overdue':
      return TimerOff
    default:
      return Activity
  }
}
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
