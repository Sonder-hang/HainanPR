<template>
  <div class="h-full flex flex-col bg-white">
    <!-- 二级Tab栏 -->
    <div class="bg-[#e8eef9] px-5 pt-3 border-b border-[#b8c9e8]/60 shrink-0">
      <div class="flex space-x-4 overflow-x-auto">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="pb-2.5 text-[12px] font-medium whitespace-nowrap transition-colors border-b-2"
          :class="activeTab === tab.id ? 'border-[#0A6EFD] text-[#0A6EFD]' : 'border-transparent text-[#596080] hover:text-[#1F264D]'"
        >
          {{ tab.name }}
        </button>
      </div>
    </div>

    <!-- 分类总览视图 -->
    <div v-if="activeTab === 'overview'" class="flex-1 p-5 overflow-y-auto animate-fade-in">
      <h2 class="text-[14px] font-bold text-[#1F264D] flex items-center">
        <Activity class="w-4 h-4 mr-2 text-[#0A6EFD]" />
        设备要素 — 监管规则总览
        <span class="ml-auto flex items-center gap-2">
          <!-- 医院筛选 -->
          <div class="relative hospital-filter">
            <div class="flex items-center gap-1.5 border border-[#b8c9e8]/60 rounded-[2px] px-2.5 py-1.5 cursor-pointer select-none hover:border-[#0A6EFD]/50 transition-colors bg-white text-[12px]"
              @click.stop="showHospitalFilter = !showHospitalFilter"
            >
              <MapPin class="w-3.5 h-3.5 text-[#0A6EFD] shrink-0" />
              <span class="font-medium text-[#1F264D]">{{ currentHospital.name }}</span>
              <ChevronDown class="w-3.5 h-3.5 text-[#596080] shrink-0 transition-transform" :class="showHospitalFilter ? 'rotate-180' : ''" />
            </div>
            <div v-if="showHospitalFilter" class="absolute right-0 top-full mt-1 w-[200px] bg-white border border-[#b8c9e8]/60 rounded-[2px] shadow-lg z-50 max-h-[280px] overflow-y-auto">
              <div
                v-for="h in hospitals"
                :key="h.id"
                class="flex items-center justify-between px-3 py-2 text-[12px] cursor-pointer hover:bg-[#e8eef9] transition-colors"
                :class="currentHospitalId === h.id ? 'bg-[#e8eef9] text-[#0A6EFD] font-medium' : 'text-[#1F264D]'"
                @click="selectHospital(h)"
              >
                <span>{{ h.name }}</span>
                <span v-if="h.level" class="text-[10px] text-[#B8BCCC] shrink-0 ml-2">{{ h.level }}</span>
              </div>
            </div>
          </div>
        </span>
      </h2>
      <div class="mb-5 bg-blue-50 border border-blue-200 rounded-[2px] p-3.5 text-[13px] text-blue-800">
        <p class="font-medium mb-0.5 text-[13px]">规则说明</p>
        <p class="text-blue-600 text-[12px]">设备要素审核范围：手术患者。对手术分级、医生授权、设备配置、检验阳性率等关键指标进行智能监测与预警。</p>
      </div>
      <div class="grid grid-cols-3 gap-4">
        <div
          v-for="rule in rules"
          :key="rule.id"
          @click="activeTab = rule.id"
          class="bg-white rounded-[2px] p-4 border border-[#b8c9e8]/60 shadow-sm hover:shadow-md hover:border-[#0A6EFD]/50 transition-all cursor-pointer group flex flex-col"
        >
          <div class="flex justify-between items-start mb-2.5">
            <div :class="['p-1.5 rounded-[2px]', rule.mode === 'alert' ? 'bg-red-50 text-red-500' : 'bg-emerald-50 text-emerald-500']">
              <ShieldAlert v-if="rule.mode === 'alert'" class="w-4 h-4" />
              <Activity v-else class="w-4 h-4" />
            </div>
          </div>
          <h3 class="font-bold text-[#1F264D] text-[13px] mb-1.5 group-hover:text-[#0A6EFD] transition-colors">{{ rule.name }}</h3>
          <p class="text-[#596080] text-[12px] flex-1 mb-3 leading-relaxed">{{ rule.desc }}</p>
          <div class="border-t border-[#b8c9e8]/40 pt-2.5">
            <div class="text-[11px] text-[#B8BCCC] mb-1">审核范围：<span class="text-[#596080] font-medium">{{ rule.scope }}</span></div>
            <div class="text-[11px] text-[#B8BCCC] mb-2">监测维度：<span class="text-[#596080] font-medium">{{ rule.threshold || '-' }}</span></div>
            <div class="flex items-center justify-between">
              <span :class="['text-[11px] font-medium px-2 py-0.5 rounded-full border', rule.mode === 'alert' ? 'border-red-200 text-red-600 bg-red-50' : 'border-emerald-200 text-emerald-600 bg-emerald-50']">
                {{ rule.mode === 'alert' ? '预警模式' : '常规监测' }}
              </span>
              <span class="text-[11px] font-bold" :class="rule.mode === 'alert' ? 'text-red-600' : 'text-emerald-600'">
                {{ rule.mode === 'alert' ? `${getMockCount(rule.id)} 条` : rule.metric }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 具体规则明细视图 -->
    <template v-else>
      <div class="p-4 shrink-0">
        <div :class="['border rounded-[2px] p-2.5 flex items-start', currentRule?.mode === 'alert' ? 'bg-blue-50/50 border-blue-200' : 'bg-emerald-50 border-emerald-200']">
          <Info :class="['w-3.5 h-3.5 mr-2 shrink-0 mt-0.5', currentRule?.mode === 'alert' ? 'text-[#0A6EFD]' : 'text-emerald-500']" />
          <div>
            <h4 :class="['text-[13px] font-medium', currentRule?.mode === 'alert' ? 'text-blue-800' : 'text-emerald-800']">{{ currentRule?.name }}</h4>
            <p :class="['text-[11px] mt-0.5', currentRule?.mode === 'alert' ? 'text-blue-600' : 'text-emerald-600']">{{ currentRule?.logic }}</p>
          </div>
        </div>
      </div>

      <div class="flex-1 px-4 pb-4 overflow-hidden flex flex-col">
        <div class="bg-white rounded-[2px] border border-[#b8c9e8]/60 flex-1 overflow-hidden flex flex-col shadow-sm">
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
                <input type="text" placeholder="搜索..." class="pl-8 pr-3 py-1.5 text-[12px] border border-[#b8c9e8]/60 rounded-[2px] focus:outline-none focus:border-[#0A6EFD] w-52 bg-white" />
              </div>
              <button @click="handleExport" class="px-3 py-1.5 text-[12px] bg-[#0A6EFD] text-white rounded-[2px] hover:bg-[#0a5fe0] transition-colors flex items-center gap-1">
                <Download class="w-3.5 h-3.5" /> 导出
              </button>
            </div>
          </div>

          <div v-if="currentRule?.mode === 'alert'" class="flex-1 overflow-auto">
            <table class="w-full text-left border-collapse">
              <thead class="bg-[#e8eef9] sticky top-0 z-10">
                <tr>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">预警时间</th>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">涉事机构</th>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">涉事人员</th>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">违规详情</th>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide text-right">操作</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#b8c9e8]/30">
                <tr v-for="row in tableData" :key="row.id" class="hover:bg-[#e8eef9]/40 transition-colors">
                  <td class="px-3.5 py-2.5 text-[12px] text-[#596080] whitespace-nowrap"><Clock class="w-3 h-3 inline mr-1 text-[#B8BCCC]"/>{{ row.time }}</td>
                  <td class="px-3.5 py-2.5 text-[12px] text-[#1F264D] font-medium">{{ row.org }}</td>
                  <td class="px-3.5 py-2.5 text-[12px] text-[#596080]">{{ row.person }}</td>
                  <td class="px-3.5 py-2.5 text-[12px] text-[#1F264D] max-w-xs truncate" :title="row.detail">{{ row.detail }}</td>
                  <td class="px-3.5 py-2.5 text-[12px] text-right">
                    <button @click="openDrawer(row)" class="text-[#0A6EFD] hover:text-[#1F264D] font-medium flex items-center justify-end w-full text-[11px]">
                      <Eye class="w-3 h-3 mr-1" /> 查看详情
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-else class="flex-1 overflow-auto">
            <table class="w-full text-left border-collapse">
              <thead class="bg-emerald-50/60 sticky top-0 z-10 border-b border-emerald-100">
                <tr>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">监测主体</th>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">核心指标</th>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">当前数值</th>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">辅助指标</th>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">统计结果</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#b8c9e8]/30">
                <tr v-for="row in tableData" :key="row.id" class="hover:bg-emerald-50/40 transition-colors">
                  <td class="px-3.5 py-3 text-[12px] text-[#1F264D] font-medium flex items-center">
                    <Monitor class="w-3.5 h-3.5 text-emerald-500 mr-2" /> {{ row.org }}
                  </td>
                  <td class="px-3.5 py-3 text-[12px] text-[#596080]">{{ row.metric1 }}</td>
                  <td class="px-3.5 py-3 text-[12px] font-bold text-emerald-600 text-[14px]">{{ row.value1 }}</td>
                  <td class="px-3.5 py-3 text-[12px] text-[#596080]">{{ row.metric2 || '-' }}</td>
                  <td class="px-3.5 py-3 text-[12px] text-[#1F264D] bg-[#f0f4ff] rounded font-mono text-[10px]">{{ row.value2 || '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>

    <!-- 详情抽屉 -->
    <div v-if="drawerData" class="fixed inset-0 z-50 flex justify-end bg-gray-900/50 backdrop-blur-sm">
      <div class="w-[580px] bg-white h-full shadow-2xl flex flex-col animate-slide-in border-l border-[#b8c9e8]/60">
        <div class="px-5 py-3.5 border-b border-[#b8c9e8]/60 flex justify-between items-center bg-[#e8eef9]">
          <h2 class="text-[14px] font-bold text-[#1F264D] flex items-center">
            <ShieldAlert class="w-4 h-4 text-red-500 mr-2" />
            预警证据链详情
          </h2>
          <button @click="drawerData = null" class="p-1.5 hover:bg-[#b8c9e8]/30 rounded-full text-[#596080] transition-colors">
            <X class="w-4 h-4" />
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-5 space-y-5">
          <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
            <div class="flex items-center justify-between mb-3">
              <h3 class="font-bold text-[#1F264D] text-[13px]">基本信息</h3>
              <span class="px-2 py-0.5 rounded-full text-[11px] font-medium border bg-red-50 text-red-600 border-red-200">触发预警</span>
            </div>
            <div class="grid grid-cols-2 gap-3 text-[12px]">
              <div><span class="text-[#596080] block mb-0.5">预警时间</span><span class="font-medium text-[#1F264D]">{{ drawerData.time }}</span></div>
              <div><span class="text-[#596080] block mb-0.5">涉事机构</span><span class="font-medium text-[#1F264D]">{{ drawerData.org }}</span></div>
              <div><span class="text-[#596080] block mb-0.5">涉事人员</span><span class="font-medium text-[#1F264D]">{{ drawerData.person }}</span></div>
              <div><span class="text-[#596080] block mb-0.5">违规类型</span><span class="font-medium text-[#1F264D]">{{ drawerData.violationType || currentRule?.name }}</span></div>
            </div>
          </div>
          <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
            <h3 class="font-bold text-[#1F264D] text-[13px] mb-2.5">违规判定依据</h3>
            <div class="bg-red-50 border border-red-200 rounded-[2px] p-3 text-[12px] text-red-800">
              <p class="font-medium mb-1">违规类型：{{ drawerData.violationType || currentRule?.name }}</p>
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
          </div>        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Activity, Calendar, ChevronDown, Clock, Download, Eye, Info, MapPin, Monitor, Search, ShieldAlert, X } from 'lucide-vue-next'
import { currentHospital, currentHospitalId, hospitals } from '../../stores/hospital'
import type { Hospital } from '../../stores/hospital'
import { exportToExcel } from '../../utils/exportExcel'

const showHospitalFilter = ref(false)
const startDate = ref('')
const endDate = ref('')

function selectHospital(h: Hospital) {
  currentHospitalId.value = h.id
  showHospitalFilter.value = false
}

function handleClickOutside(e: MouseEvent) {
  if (!(e.target as HTMLElement).closest('.hospital-filter')) {
    showHospitalFilter.value = false
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))

const rules = [
  { id: 'r15', mode: 'alert', name: '人机资质不符', desc: '手术分级、医生授权与设备配置匹配异常，系统自动报警。', scope: '手术患者', threshold: '手术分级-医生授权-设备配置', logic: '建立"手术分级-医生授权-设备配置"匹配规则，以手术分级为基准，医生授权对应资质等级，设备配置满足技术需求时自动报警。' },
  { id: 'r16', mode: 'alert', name: '设备账实不符', desc: '设备基本信息、数量品种与医疗机构设置申请及校验验证不一致。', scope: '-', threshold: '设备台账比对', logic: '在系统中对设备基本信息、数量及品种与医疗机构设置申请及校验验证是否一致进行核查。' },
  { id: 'r17', mode: 'alert', name: '检查阳性率异常', desc: '连续三个月内特定检查阳性率超过80%且该检查总量占全院80%时报警。', scope: '-', threshold: '阳性率>80% 且 占比>80%', logic: '建立"连续三个月内单一医疗机构特定检查或检验结果阳性率超过80%且该检查或检验总量占全院总量的80%"统计报警规则。' },
  { id: 'r18', mode: 'alert', name: '重点药品耗材超限', desc: '开展重点药品、耗材日常监测，开具的重点药品、耗材超过阈值时报警。', scope: '国家三级公立医院绩效考核', threshold: '耗材阈值', logic: '根据《国家三级公立医院绩效考核操作手册》，开展重点药品、耗材日常监测，开具的重点药品、耗材超过阈值时报警。' },
  { id: 'r19', mode: 'monitor', name: '设备负荷与闲置', desc: '诊断/治疗设备年平均服务患者数量统计分析。', scope: '-', threshold: '-', metric: '设备效能分析', logic: '统计诊断/治疗设备年平均服务患者数量，计算公式：患者的检查报告数量/设备数量。' },
]

const tabs = [{ id: 'overview', name: '分类总览' }, ...rules]
const activeTab = ref('overview')
const drawerData = ref<any>(null)
const currentRule = computed(() => rules.find(r => r.id === activeTab.value))

const MOCK_DATA: Record<string, any[]> = {
  r15: [
    { id: 'E001', time: '2026-03-29 10:00', org: '省立第一医院', person: '骨科 主任医师李某', violationType: '人机资质不符', detail: '主任医师开展三级关节镜手术，但该医师授权仅为二级手术资质，设备配置也不满足三级手术要求。', evidence: `[手术记录] 患者: 张某 | 三级关节镜手术 | 主刀: 李某(主任医师)\n[医师授权] 李某 | 授权级别: 二级\n[设备配置] 关节镜设备1套，三级手术要求2套\n>>> 异常判定: 医师授权等级与手术分级不匹配，且设备配置不足。` },
    { id: 'E002', time: '2026-03-28 14:30', org: '县人民医院', person: '外科 主治医师王某', violationType: '人机资质不符', detail: '主治医师开展四级腹腔镜手术，但未取得四级手术授权。', evidence: `[手术记录] 患者: 李某 | 四级腹腔镜手术 | 主刀: 王某(主治医师)\n[医师授权] 王某 | 授权级别: 三级，可开展一~三级手术\n>>> 异常判定: 主治医师越权开展四级手术。` },
    { id: 'E003', time: '2026-03-26 09:15', org: '市中心医院', person: '泌尿外科 副主任医师', violationType: '人机资质不符', detail: '副主任医师开展经皮肾镜碎石术（四级），但医师授权仅覆盖三级及以下手术。', evidence: `[手术记录] 四级经皮肾镜碎石术 | 主刀: 副主任医师\n[医师授权] 副主任医师 | 授权级别: 三级\n>>> 异常判定: 越权开展四级手术。` },
    { id: 'E004', time: '2026-03-24 11:00', org: '省立第三医院', person: '心内科 主治医师', violationType: '人机资质不符', detail: '主治医师开展冠脉支架置入术（三级），但未完成心脏介入诊疗技术培训，授权为二级手术资质。', evidence: `[手术记录] 冠脉支架置入术 | 主刀: 主治医师\n[医师授权] 主治医师 | 授权级别: 二级（未经介入培训）\n>>> 异常判定: 未完成专项培训即开展三级介入手术。` },
    { id: 'E005', time: '2026-03-22 15:30', org: '省肿瘤医院', person: '胸外科 主任医师', violationType: '人机资质不符', detail: '主任医师开展胸腔镜下肺叶切除术，但该手术室未配备符合三级手术要求的胸腔镜设备套装。', evidence: `[手术室配置] 2号手术室 | 胸腔镜设备: 1套（老旧型号）\n[手术需求] 三级胸腔镜手术须配备2套独立设备\n>>> 异常判定: 设备配置不满足三级手术要求。` },
    { id: 'E006', time: '2026-03-20 10:45', org: '康华医院', person: '外科', violationType: '人机资质不符', detail: '康华医院外科开展三级腹腔镜手术，但该机构手术室腹腔镜设备未通过年度校验。', evidence: `[设备档案] 腹腔镜设备 | 校验状态: ❌ 未通过（2025-12-31到期未检）\n[实际开展] 三级腹腔镜手术: 8例\n>>> 异常判定: 设备未校验仍开展相关手术。` },
  ],

  r16: [
    { id: 'E007', time: '2026-03-28 14:20', org: '省立第一医院', person: '设备科', violationType: '设备账实不符', detail: 'CT设备实际数量与备案数量不符，系统中登记2台，实际使用3台，超出许可数量1台。', evidence: `[系统备案] CT设备数量: 2台\n[实地核查] CT设备数量: 3台\n>>> 异常判定: 设备数量与备案不符，涉嫌违规增设设备。` },
    { id: 'E008', time: '2026-03-25 09:00', org: '康华医院', person: '设备科', violationType: '设备账实不符', detail: 'MRI设备型号与申请备案不符，申请为1.5T设备，实际使用3.0T设备。', evidence: `[设置申请] MRI设备型号: 1.5T\n[实际设备] MRI设备型号: 3.0T\n>>> 异常判定: 设备型号与申请不符，涉嫌违规配置高端设备。` },
    { id: 'E009', time: '2026-03-23 10:30', org: '市中心医院', person: '设备科', violationType: '设备账实不符', detail: 'DSA（数字减影血管造影机）设备登记数量与实际不符，系统显示1台，实际使用2台，其中1台为借用设备未备案。', evidence: `[系统登记] DSA设备: 1台\n[实际核查] DSA设备: 2台（其中1台为外借设备，未纳入本院固定资产）\n>>> 异常判定: 外借设备未纳入管理，账实不符。` },
    { id: 'E010', time: '2026-03-21 08:45', org: '省立第三医院', person: '设备科', violationType: '设备账实不符', detail: '直线加速器（放疗设备）年度校验已过期（2025-11-30到期），系统仍显示"在用"状态。', evidence: `[系统状态] 直线加速器 | 状态: 在用\n[校验记录] 上次校验: 2024-11-30 | 到期日: 2025-11-30 | 状态: ❌ 已过期\n>>> 异常判定: 校验过期设备仍在使用。` },
    { id: 'E011', time: '2026-03-19 14:00', org: '县人民医院', person: '设备科', violationType: '设备账实不符', detail: '全自动生化分析仪设备登记信息与实物不符，系统登记为"迈瑞BS-800"，实物为"罗氏C8000"，品牌型号均不相符。', evidence: `[系统登记] 品牌: 迈瑞BS-800 | 购入年份: 2022年\n[实物核查] 品牌: 罗氏C8000 | 购入年份: 2023年\n>>> 异常判定: 设备登记信息与实物严重不符。` },
    { id: 'E012', time: '2026-03-17 09:30', org: '仁爱医院', person: '医务科', violationType: '设备账实不符', detail: 'X射线计算机体层摄影设备(CT机)未取得辐射安全许可证，但系统显示"正常运行"。', evidence: `[系统状态] CT机 | 状态: 正常运行\n[许可证核查] 辐射安全许可证: ❌ 未取得\n>>> 异常判定: 无证设备仍在运行。` },
  ],

  r17: [
    { id: 'E013', time: '2026-03-27 08:00', org: '省立第一医院', person: '检验科', violationType: '检查阳性率异常', detail: '连续3个月内肿瘤标志物检测阳性率92%，且占全院检验总量85%，超出阈值。', evidence: `[统计分析] 2025-12~2026-02:\n- 总检测量: 1200例 | 阳性: 1104例\n- 阳性率: 92% > 80%阈值\n- 占全院总量: 85% > 80%阈值\n>>> 异常判定: 阳性率和占比均超出阈值。` },
    { id: 'E014', time: '2026-03-20 10:00', org: '县人民医院', person: '检验科', violationType: '检查阳性率异常', detail: '连续3个月内某项传染病检测阳性率达88%，且占全院检验总量82%。', evidence: `[统计分析] 传染病检测阳性率88%，占全院总量82%，均超出阈值。` },
    { id: 'E015', time: '2026-03-25 11:20', org: '市中心医院', person: '检验科', violationType: '检查阳性率异常', detail: '连续3个月内CT检查阳性率达91%（需手术患者比例），占全院CT总量87%，疑似过度检查。', evidence: `[统计分析] 2025-12~2026-02:\n- CT总检查量: 3500例 | 阳性(需手术): 3185例\n- 阳性率: 91% | 占全院: 87%\n>>> 异常判定: CT阳性率异常偏高，疑似过度检查。` },
    { id: 'E016', time: '2026-03-23 14:45', org: '省立第三医院', person: '放射科', violationType: '检查阳性率异常', detail: '连续3个月内MRI检查阳性率达86%，且占全院MRI总量83%，与同类三级医院均值(55%)差异显著。', evidence: `[统计分析] MRI阳性率: 86% | 占全院: 83%\n[对比数据] 同类三级医院均值: 55%\n>>> 异常判定: 与同类医院均值差异超过30%，疑似过度检查。` },
    { id: 'E017', time: '2026-03-20 09:30', org: '省肿瘤医院', person: '病理科', violationType: '检查阳性率异常', detail: '连续3个月内PET-CT检查阳性率达96%（肿瘤发现率），远高于指南参考值(30%)，疑似存在报告造假风险。', evidence: `[统计分析] PET-CT阳性率: 96%\n[指南参考] 肿瘤筛查阳性率参考值: 30%\n>>> 异常判定: 阳性率远超参考值，报告真实性存疑。` },
    { id: 'E018', time: '2026-03-18 10:15', org: '康华医院', person: '检验科', violationType: '检查阳性率异常', detail: '连续3个月内血糖检测阳性率(高血糖>7.0mmol/L)达94%，占全院检验总量90%，与实际情况偏离较大。', evidence: `[统计分析] 血糖检测阳性率: 94% | 占全院: 90%\n[地区均值] 成人高血糖患病率参考值: 约12%\n>>> 异常判定: 阳性率严重偏离地区患病率基准。` },
  ],

  r18: [
    { id: 'E019', time: '2026-03-30 16:00', org: '市中心医院', person: '医务科', violationType: '耗材超限', detail: '某高值耗材使用量超出国家三级公立医院绩效考核阈值150%。', evidence: `[耗材监测] 高值耗材: 某品牌冠脉支架\n[绩效考核阈值] 月使用量上限: 100个\n[实际使用] 月使用量: 253个 (超标153%)\n>>> 异常判定: 高值耗材使用量超出绩效考核阈值。` },
    { id: 'E020', time: '2026-03-28 11:20', org: '省立第一医院', person: '骨科', violationType: '耗材超限', detail: '人工关节耗材（髋关节假体）月使用量达320套，超出绩效考核目标值(200套)60%。', evidence: `[耗材监测] 髋关节假体 | 月使用量: 320套\n[绩效考核目标] 月上限: 200套\n>>> 异常判定: 耗材使用量超出绩效考核目标60%。` },
    { id: 'E021', time: '2026-03-26 14:30', org: '省立第三医院', person: '心内科', violationType: '耗材超限', detail: '冠脉支架使用量达180根/月，超出国家绩效考核指标（每百例介入手术不超过65根）。', evidence: `[耗材监测] 冠脉支架 | 月使用量: 180根\n[绩效考核指标] 每百例介入: 上限65根\n[介入手术量] 月手术量: 200例\n[理论上限] 200例×0.65 = 130根\n>>> 异常判定: 耗材使用效率比超标。` },
    { id: 'E022', time: '2026-03-24 09:15', org: '市中心医院', person: '神经外科', violationType: '耗材超限', detail: '弹簧圈（颅内血管栓塞材料）使用量超标，本月使用120个，绩效考核上限为80个。', evidence: `[耗材监测] 颅内弹簧圈 | 月使用量: 120个\n[绩效考核上限] 80个/月\n>>> 异常判定: 高值介入耗材超出绩效考核上限。` },
    { id: 'E023', time: '2026-03-22 10:00', org: '省立第一医院', person: '药剂科', violationType: '耗材超限', detail: '重点监控药品（质子泵抑制剂）DDDs值超标，本季度达28,000 DDDs，超出绩效考核指标(20,000 DDDs)40%。', evidence: `[药品监测] 质子泵抑制剂DDDs | 季度值: 28,000\n[绩效考核指标] 上限: 20,000 DDDs\n>>> 异常判定: 重点药品用量超出绩效考核指标。` },
    { id: 'E024', time: '2026-03-20 15:45', org: '县人民医院', person: '医务科', violationType: '耗材超限', detail: '一次性高值耗材（静脉营养袋）重复使用次数超出规定上限，涉及违规使用。', evidence: `[耗材监测] 静脉营养袋 | 规定: 一次性使用\n[实际记录] 同一批次产品使用记录: 重复使用3~5次\n>>> 异常判定: 一次性耗材重复使用，违反院感规定。` },
    { id: 'E025', time: '2026-03-18 11:30', org: '省肿瘤医院', person: '肿瘤科', violationType: '耗材超限', detail: '靶向药物伴随诊断试剂盒使用量超出采购计划200%，存在科室自行采购未报备问题。', evidence: `[耗材监测] 靶向药伴随诊断试剂盒 | 计划采购: 100人份\n[实际使用] 使用量: 320人份\n>>> 异常判定: 实际使用量超出计划200%，科室自行采购未报备。` },
  ],

  r19: [
    { id: 'm191', org: '省立第一医院', metric1: 'CT设备年检查量', value1: '12,500例', metric2: '设备数量', value2: '2台 | 效能: 6250例/台' },
    { id: 'm192', org: '省立第一医院', metric1: 'MRI设备年检查量', value1: '9,800例', metric2: '设备数量', value2: '2台 | 效能: 4900例/台' },
    { id: 'm193', org: '市中心医院', metric1: 'CT设备年检查量', value1: '8,200例', metric2: '设备数量', value2: '1台 | 效能: 8200例/台(满负荷)' },
    { id: 'm194', org: '市中心医院', metric1: 'MRI设备年检查量', value1: '4,200例', metric2: '设备数量', value2: '1台 | 效能: 4200例/台' },
    { id: 'm195', org: '省肿瘤医院', metric1: 'PET-CT年检查量', value1: '1,850例', metric2: '设备数量', value2: '1台 | 效能: 1850例/台' },
    { id: 'm196', org: '省肿瘤医院', metric1: 'CT设备年检查量', value1: '6,500例', metric2: '设备数量', value2: '1台 | 效能: 6500例/台' },
    { id: 'm197', org: '县人民医院', metric1: 'CT设备年检查量', value1: '2,100例', metric2: '设备数量', value2: '1台 | 效能: 2100例/台' },
    { id: 'm198', org: '县人民医院', metric1: 'MRI设备年检查量', value1: '300例', metric2: '设备数量', value2: '1台 | 效能: 300例/台(严重闲置)' },
    { id: 'm199', org: '省立第三医院', metric1: 'CT设备年检查量', value1: '4,500例', metric2: '设备数量', value2: '1台 | 效能: 4500例/台' },
    { id: 'm1910', org: '省立第三医院', metric1: '直线加速器年治疗量', value1: '890例', metric2: '设备数量', value2: '1台 | 效能: 890例/台' },
    { id: 'm1911', org: '康华医院', metric1: 'CT设备年检查量', value1: '800例', metric2: '设备数量', value2: '1台 | 效能: 800例/台(闲置)' },
    { id: 'm1912', org: '县第二医院', metric1: 'CT设备年检查量', value1: '450例', metric2: '设备数量', value2: '1台 | 效能: 450例/台(严重闲置)' },
  ],
}

const isAll = computed(() => currentHospitalId.value === 'all')

function matchHospital(item: any, hName: string): boolean {
  return item.org === hName || item.org.includes(hName)
}

const filteredData = computed(() => {
  const raw = MOCK_DATA[activeTab.value] || []
  let result = isAll.value ? raw : raw.filter(item => matchHospital(item, currentHospital.value.name))
  if (startDate.value) {
    result = result.filter((item: any) => !item.time || item.time >= startDate.value)
  }
  if (endDate.value) {
    result = result.filter((item: any) => !item.time || item.time <= endDate.value)
  }
  return result
})

const tableData = computed(() => filteredData.value)

const getMockCount = (id: string) => {
  if (isAll.value) return MOCK_DATA[id]?.length || 0
  return (MOCK_DATA[id] || []).filter((item: any) => matchHospital(item, currentHospital.value.name)).length
}
const openDrawer = (row: any) => { drawerData.value = row }

const equipColumns = [
  { field: 'time', header: '预警时间' },
  { field: 'org', header: '涉事机构' },
  { field: 'person', header: '涉事人员' },
  { field: 'detail', header: '违规详情' },
]

function handleExport() {
  const rule = currentRule.value
  const name = rule ? `${rule.no}-${rule.name}` : '设备要素总览'
  exportToExcel(tableData.value, equipColumns, `设备要素_${name}`)
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.animate-slide-in { animation: slideIn 0.3s ease-out; }
@keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }
</style>
