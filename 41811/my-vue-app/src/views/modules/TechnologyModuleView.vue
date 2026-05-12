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
        技术要素 — 监管规则总览
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
        <p class="text-blue-600 text-[12px]">技术要素涵盖限制类技术、抗肿瘤药物、麻精药品、未成年保护等多个维度，对医疗技术开展进行全流程智能监测与预警。</p>
      </div>
      <div class="grid grid-cols-4 gap-4">
        <div
          v-for="rule in rules"
          :key="rule.id"
          @click="activeTab = rule.id"
          class="bg-white rounded-[2px] p-3.5 border border-[#b8c9e8]/60 shadow-sm hover:shadow-md hover:border-[#0A6EFD]/50 transition-all cursor-pointer group flex flex-col"
        >
          <div class="flex justify-between items-start mb-2">
            <div :class="['p-1.5 rounded-[2px]', rule.mode === 'alert' ? 'bg-red-50 text-red-500' : 'bg-emerald-50 text-emerald-500']">
              <ShieldAlert v-if="rule.mode === 'alert'" class="w-4 h-4" />
              <Activity v-else class="w-4 h-4" />
            </div>
          </div>
          <h3 class="font-bold text-[#1F264D] text-[12px] mb-1 group-hover:text-[#0A6EFD] transition-colors">{{ rule.name }}</h3>
          <p class="text-[#596080] text-[11px] flex-1 mb-2.5 leading-relaxed">{{ rule.desc }}</p>
          <div class="border-t border-[#b8c9e8]/40 pt-2">
            <div class="text-[10px] text-[#B8BCCC] mb-1">审核范围：<span class="text-[#596080] font-medium">{{ rule.scope }}</span></div>
            <div class="flex items-center justify-between">
              <span :class="['text-[10px] font-medium px-1.5 py-0.5 rounded-full border', rule.mode === 'alert' ? 'border-red-200 text-red-600 bg-red-50' : 'border-emerald-200 text-emerald-600 bg-emerald-50']">
                {{ rule.mode === 'alert' ? '预警模式' : '常规监测' }}
              </span>
              <span class="text-[10px] font-bold" :class="rule.mode === 'alert' ? 'text-red-600' : 'text-emerald-600'">
                {{ rule.mode === 'alert' ? `${getMockCount(rule.id)} 条` : (rule.metric || '-') }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 具体规则明细视图 -->
    <template v-else>
      <div class="p-3.5 shrink-0">
        <div :class="['border rounded-[2px] p-2.5 flex items-start', currentRule?.mode === 'alert' ? 'bg-blue-50/50 border-blue-200' : 'bg-emerald-50 border-emerald-200']">
          <Info :class="['w-3.5 h-3.5 mr-2 shrink-0 mt-0.5', currentRule?.mode === 'alert' ? 'text-[#0A6EFD]' : 'text-emerald-500']" />
          <div>
            <h4 :class="['text-[12px] font-medium', currentRule?.mode === 'alert' ? 'text-blue-800' : 'text-emerald-800']">{{ currentRule?.name }}</h4>
            <p :class="['text-[11px] mt-0.5', currentRule?.mode === 'alert' ? 'text-blue-600' : 'text-emerald-600']">{{ currentRule?.logic }}</p>
          </div>
        </div>
      </div>

      <div class="flex-1 px-4 pb-4 overflow-hidden flex flex-col">
        <div class="bg-white rounded-[2px] border border-[#b8c9e8]/60 flex-1 overflow-hidden flex flex-col shadow-sm">
          <div class="p-3 border-b border-[#b8c9e8]/40 flex justify-between items-center shrink-0">
            <h3 class="font-semibold text-[#1F264D] flex items-center text-[12px]">
              {{ currentRule?.mode === 'alert' ? '违规预警数据列表' : '监测指标统计报表' }}
              <span v-if="currentRule?.mode === 'alert'" class="ml-2 bg-red-100 text-red-600 py-0.5 px-2 rounded-full text-[10px] font-bold">{{ tableData.length }}</span>
            </h3>
            <div class="flex items-center gap-2">
              <div class="flex items-center gap-1.5 border border-[#b8c9e8]/60 rounded-[2px] px-2.5 py-1 bg-white">
                <Calendar class="w-3.5 h-3.5 text-[#596080] shrink-0" />
                <input
                  type="date"
                  v-model="startDate"
                  class="text-[11px] text-[#1F264D] focus:outline-none bg-transparent w-[120px]"
                />
                <span class="text-[10px] text-[#B8BCCC]">至</span>
                <input
                  type="date"
                  v-model="endDate"
                  class="text-[11px] text-[#1F264D] focus:outline-none bg-transparent w-[120px]"
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
                <Search class="w-3.5 h-3.5 absolute left-2 top-1/2 transform -translate-y-1/2 text-[#B8BCCC]" />
                <input type="text" placeholder="搜索..." class="pl-7 pr-2.5 py-1 text-[11px] border border-[#b8c9e8]/60 rounded-[2px] focus:outline-none focus:border-[#0A6EFD] w-44 bg-white" />
              </div>
              <button @click="handleExport" class="px-2.5 py-1 text-[11px] bg-[#0A6EFD] text-white rounded-[2px] hover:bg-[#0a5fe0] transition-colors flex items-center gap-1">
                <Download class="w-3.5 h-3.5" /> 导出
              </button>
            </div>
          </div>

          <div v-if="currentRule?.mode === 'alert'" class="flex-1 overflow-auto">
            <table class="w-full text-left border-collapse">
              <thead class="bg-[#e8eef9] sticky top-0 z-10">
                <tr>
                  <th class="px-3 py-2 text-[10px] font-semibold text-[#596080] uppercase tracking-wide">预警时间</th>
                  <th class="px-3 py-2 text-[10px] font-semibold text-[#596080] uppercase tracking-wide">涉事机构</th>
                  <th class="px-3 py-2 text-[10px] font-semibold text-[#596080] uppercase tracking-wide">涉事人员</th>
                  <th class="px-3 py-2 text-[10px] font-semibold text-[#596080] uppercase tracking-wide">违规详情</th>
                  <th class="px-3 py-2 text-[10px] font-semibold text-[#596080] uppercase tracking-wide text-right">操作</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#b8c9e8]/30">
                <tr v-for="row in tableData" :key="row.id" class="hover:bg-[#e8eef9]/40 transition-colors">
                  <td class="px-3 py-2 text-[11px] text-[#596080] whitespace-nowrap"><Clock class="w-2.5 h-2.5 inline mr-1 text-[#B8BCCC]"/>{{ row.time }}</td>
                  <td class="px-3 py-2 text-[11px] text-[#1F264D] font-medium">{{ row.org }}</td>
                  <td class="px-3 py-2 text-[11px] text-[#596080]">{{ row.person }}</td>
                  <td class="px-3 py-2 text-[11px] text-[#1F264D] max-w-xs truncate" :title="row.detail">{{ row.detail }}</td>
                  <td class="px-3 py-2 text-[11px] text-right">
                    <button @click="openDrawer(row)" class="text-[#0A6EFD] hover:text-[#1F264D] font-medium flex items-center justify-end w-full text-[11px]">
                      <Eye class="w-2.5 h-2.5 mr-1" /> 查看详情
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
                  <th class="px-3 py-2 text-[10px] font-semibold text-[#596080] uppercase tracking-wide">监测主体</th>
                  <th class="px-3 py-2 text-[10px] font-semibold text-[#596080] uppercase tracking-wide">核心指标</th>
                  <th class="px-3 py-2 text-[10px] font-semibold text-[#596080] uppercase tracking-wide">当前数值</th>
                  <th class="px-3 py-2 text-[10px] font-semibold text-[#596080] uppercase tracking-wide">辅助指标</th>
                  <th class="px-3 py-2 text-[10px] font-semibold text-[#596080] uppercase tracking-wide">统计结果</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#b8c9e8]/30">
                <tr v-for="row in tableData" :key="row.id" class="hover:bg-emerald-50/40 transition-colors">
                  <td class="px-3 py-2.5 text-[11px] text-[#1F264D] font-medium flex items-center">
                    <Building class="w-3.5 h-3.5 text-emerald-500 mr-1.5" /> {{ row.org }}
                  </td>
                  <td class="px-3 py-2.5 text-[11px] text-[#596080]">{{ row.metric1 }}</td>
                  <td class="px-3 py-2.5 text-[11px] font-bold text-emerald-600 text-[13px]">{{ row.value1 }}</td>
                  <td class="px-3 py-2.5 text-[11px] text-[#596080]">{{ row.metric2 || '-' }}</td>
                  <td class="px-3 py-2.5 text-[11px] text-[#1F264D] bg-[#f0f4ff] rounded font-mono text-[10px]">{{ row.value2 || '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>

    <!-- 详情抽屉 -->
    <div v-if="drawerData" class="fixed inset-0 z-50 flex justify-end bg-gray-900/50 backdrop-blur-sm">
      <div class="w-[560px] bg-white h-full shadow-2xl flex flex-col animate-slide-in border-l border-[#b8c9e8]/60">
        <div class="px-5 py-3 border-b border-[#b8c9e8]/60 flex justify-between items-center bg-[#e8eef9]">
          <h2 class="text-[13px] font-bold text-[#1F264D] flex items-center">
            <ShieldAlert class="w-4 h-4 text-red-500 mr-2" />
            预警证据链详情
          </h2>
          <button @click="drawerData = null" class="p-1 hover:bg-[#b8c9e8]/30 rounded-full text-[#596080] transition-colors">
            <X class="w-4 h-4" />
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-4 space-y-4">
          <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-3.5">
            <div class="flex items-center justify-between mb-2.5">
              <h3 class="font-bold text-[#1F264D] text-[12px]">基本信息</h3>
              <span class="px-2 py-0.5 rounded-full text-[10px] font-medium border bg-red-50 text-red-600 border-red-200">触发预警</span>
            </div>
            <div class="grid grid-cols-2 gap-2.5 text-[11px]">
              <div><span class="text-[#596080] block mb-0.5">预警时间</span><span class="font-medium text-[#1F264D]">{{ drawerData.time }}</span></div>
              <div><span class="text-[#596080] block mb-0.5">涉事机构</span><span class="font-medium text-[#1F264D]">{{ drawerData.org }}</span></div>
              <div><span class="text-[#596080] block mb-0.5">涉事人员</span><span class="font-medium text-[#1F264D]">{{ drawerData.person }}</span></div>
              <div><span class="text-[#596080] block mb-0.5">违规类型</span><span class="font-medium text-[#1F264D]">{{ drawerData.violationType || '-' }}</span></div>
            </div>
          </div>
          <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-3.5">
            <h3 class="font-bold text-[#1F264D] text-[12px] mb-2">违规判定依据</h3>
            <div class="bg-red-50 border border-red-200 rounded-[2px] p-2.5 text-[11px] text-red-800">
              <p class="font-medium mb-1">违规类型：{{ drawerData.violationType || currentRule?.name }}</p>
              <p class="text-red-700">{{ drawerData.detail }}</p>
            </div>
          </div>
          <div>
            <h3 class="font-bold text-[#1F264D] text-[12px] mb-2 flex items-center">
              <Activity class="w-3 h-3 mr-1 text-[#0A6EFD]" />
              系统底层抓取证据
            </h3>
            <div class="bg-[#f8faff] border border-[#b8c9e8]/60 rounded-[2px] p-3.5">
              <p class="text-[10px] text-[#B8BCCC] mb-1 font-mono">=== 关联底层数据快照 ===</p>
              <div class="bg-[#f0f4ff] p-2 rounded-[2px] text-[10px] font-mono text-[#596080] whitespace-pre-line leading-relaxed">{{ drawerData.evidence }}</div>
            </div>
          </div>        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Activity, Building, Calendar, ChevronDown, Clock, Download, Eye, Info, MapPin, Search, ShieldAlert, X } from 'lucide-vue-next'
import { currentHospital, currentHospitalId, hospitals } from '../../stores/hospital'
import type { Hospital } from '../../stores/hospital'
import { exportToExcel } from '../../utils/exportExcel'

const route = useRoute()
const router = useRouter()

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
  { id: 'r7', mode: 'alert', name: '限制类技术核查', scope: '住院', threshold: '国家限制性目录', logic: '限制类技术备案情况与系统关联，建立"限制类技术备案记录-备案医师-技术开展"匹配规则，对超范围业务自动报警。', desc: '限制类技术备案与实际开展匹配核查' },
  { id: 'r8', mode: 'alert', name: '诊疗异常聚集', scope: '住院', threshold: '单一诊断/术式>50%', logic: '连续三个月内单一医疗机构单一诊断和单一术式占比超过全院50%时报警。', desc: '单一术式占比超全院50%预警' },
  { id: 'r9', mode: 'monitor', name: '公立患者流失', scope: '门诊/住院', threshold: '-', metric: '3家机构异常', logic: '建立"民营医院收治患者来源于公立医院情况"数据分析功能，统计公立医院及医师个人患者流失数据。', desc: '民营医院收治公立患者流失分析' },
  { id: 'r10', mode: 'alert', name: '未成年人高危预警', scope: '未成年人', threshold: '高风险诊断编码', logic: '通过匹配门诊及住院全量诊疗数据，统计并预警疑似侵害未成年人线索。', desc: '侵害未成年人高风险诊断线索监测' },
  { id: 'r11', mode: 'alert', name: '麻精药品异常', scope: '门急诊', threshold: '7天/15天量', logic: '针对门急诊普通患者执行控缓释制剂7天量、癌痛及慢性痛患者执行15天量的校验规则。', desc: '麻精药品处方超量及重复购药监测' },
  { id: 'r12', mode: 'alert', name: '限制类技术超范围', scope: '-', threshold: '机构/医师权限', logic: '从机构权限、医师权限、患者转归、培训质量四个层面核查限制类技术是否超出可开展范围。', desc: '限制类技术机构/医师权限核查' },
  { id: 'r13', mode: 'alert', name: '抗肿瘤药物规范', scope: '抗肿瘤药物', threshold: '需基因检测药物', logic: '对医疗机构开具的抗肿瘤药物，联合疾病诊断、TNM分期、病理诊断等数据进行分析。', desc: '抗肿瘤药物无基因检测预警' },
  { id: 'r14', mode: 'monitor', name: '肿瘤分期规范率', scope: '肿瘤患者', threshold: '-', metric: '全省85.4%', logic: '监测首次治疗前临床TNM分期诊断情况，统计分期诊断率。', desc: '肿瘤患者首次治疗前TNM分期评估率' },
]

const tabs = [{ id: 'overview', name: '分类总览' }, ...rules]
const activeTab = ref(route.query.tab as string || 'overview')
const drawerData = ref<any>(null)
const currentRule = computed(() => rules.find(r => r.id === activeTab.value))

watch(activeTab, (val) => {
  router.replace({ query: val === 'overview' ? {} : { tab: val } })
})

const MOCK_DATA: Record<string, any[]> = {
  r7: [
    { id: 'T001', time: '2026-03-28 10:00', org: '县人民医院', person: '王某 (主治医师)', violationType: '限制类技术超范围', detail: '该医师未完成"心血管介入诊疗技术"备案，但实际开展相关手术。', evidence: `[医师备案] 王某 | 备案技术: 普通外科手术\n[实际开展] 心血管介入诊疗手术: 3例\n>>> 异常判定: 未备案限制类技术，涉嫌超范围开展。` },
    { id: 'T002', time: '2026-03-26 14:30', org: '省立第一医院', person: '李某 (副主任医师)', violationType: '限制类技术超范围', detail: '神经外科医师开展"脑血管支架置入术"，但备案仅为普通神经外科手术资质。', evidence: `[医师备案] 李某 | 备案技术: 神经外科手术\n[实际开展] 脑血管支架置入术: 2例\n>>> 异常判定: 未备案限制类技术。` },
    { id: 'T003', time: '2026-03-25 09:15', org: '市中心医院', person: '黄主任 (主任医师)', violationType: '限制类技术超范围', detail: '肿瘤科主任开展"全身放射治疗"技术，但机构未取得该限制类技术资质备案。', evidence: `[机构资质] 市中心医院 | 限制类技术备案: 普外、妇科等\n[实际开展] 全身放射治疗: 5例\n>>> 异常判定: 机构未取得限制类技术资质。` },
    { id: 'T004', time: '2026-03-22 16:45', org: '省立第三医院', person: '许医生 (主治医师)', violationType: '限制类技术超范围', detail: '开展"消化内镜粘膜下剥离术(ESD)"，但医师未完成相应培训合格证明。', evidence: `[医师备案] 许医生 | 备案技术: 常规内镜诊疗\n[实际开展] ESD手术: 4例\n>>> 异常判定: 未备案限制类技术。` },
    { id: 'T005', time: '2026-03-20 11:20', org: '县第二医院', person: '陈医生 (住院医师)', violationType: '限制类技术超范围', detail: '开展"关节镜下游离体摘除术"，但该医师仅完成一级手术资质备案。', evidence: `[医师备案] 陈医生 | 备案级别: 一级手术\n[实际开展] 关节镜下游离体摘除术: 3例（三级手术）\n>>> 异常判定: 越级开展手术。` },
  ],

  r8: [
    { id: 'T006', time: '2026-03-25 09:00', org: '省立第一医院', person: '骨科', violationType: '诊疗异常聚集', detail: '骨科连续3个月内膝关节镜手术占比达78%，超出全院50%阈值。', evidence: `[统计分析] 骨科 2025-12~2026-02:\n- 膝关节镜手术: 312例\n- 骨科总手术: 400例\n- 占比: 78%\n>>> 异常判定: 单一术式占比超过全院50%阈值。` },
    { id: 'T007', time: '2026-03-20 10:30', org: '市中心医院', person: '泌尿外科', violationType: '诊疗异常聚集', detail: '泌尿外科连续3个月内输尿管镜碎石术占比达65%，疑似存在过度诊疗。', evidence: `[统计分析] 泌尿外科 2025-12~2026-02:\n- 输尿管镜碎石术: 245例\n- 科室总手术: 376例\n- 占比: 65%\n>>> 异常判定: 单一术式占比超过全院50%阈值。` },
    { id: 'T008', time: '2026-03-18 14:00', org: '省肿瘤医院', person: '乳腺外科', violationType: '诊疗异常聚集', detail: '乳腺外科连续3个月内"乳腺癌保乳手术"占比达72%，与同级别医院差异显著。', evidence: `[统计分析] 乳腺外科 2025-12~2026-02:\n- 保乳手术: 198例\n- 科室总手术: 275例\n- 占比: 72%\n>>> 异常判定: 术式分布异常。` },
    { id: 'T009', time: '2026-03-15 08:45', org: '县人民医院', person: '普外科', violationType: '诊疗异常聚集', detail: '普外科连续3个月内腹腔镜胆囊切除术占比达82%，明显高于全省均值(45%)。', evidence: `[统计分析] 普外科 2025-12~2026-02:\n- 腹腔镜胆囊切除术: 310例\n- 科室总手术: 378例\n- 占比: 82% | 全省均值: 45%\n>>> 异常判定: 与全省均值差异超过30个百分点。` },
    { id: 'T010', time: '2026-03-12 15:20', org: '省立第三医院', person: '心内科', violationType: '诊疗异常聚集', detail: '心内科连续3个月内冠脉支架置入术占比达68%，存在过度医疗风险。', evidence: `[统计分析] 心内科 2025-12~2026-02:\n- 冠脉支架置入术: 289例\n- 科室总手术: 425例\n- 占比: 68%\n>>> 异常判定: 术式聚集，存在过度医疗风险。` },
  ],

  r9: [
    { id: 'm91', org: '省立第一医院', metric1: '患者流失总数', value1: '342人', metric2: '主要流向', value2: '康华医院 (65%)' },
    { id: 'm92', org: '市中心医院', metric1: '患者流失总数', value1: '128人', metric2: '主要流向', value2: '仁爱医院 (40%)' },
    { id: 'm93', org: '县人民医院', metric1: '患者流失总数', value1: '89人', metric2: '主要流向', value2: '某民营诊所 (55%)' },
    { id: 'm94', org: '省立第三医院', metric1: '患者流失总数', value1: '156人', metric2: '主要流向', value2: '康华医院 (48%)' },
    { id: 'm95', org: '省肿瘤医院', metric1: '患者流失总数', value1: '67人', metric2: '主要流向', value2: '康华医院 (72%)' },
  ],

  r10: [
    { id: 'T011', time: '2026-03-30 15:30', org: '县人民医院', person: '急诊科', violationType: '未成年人高危', detail: '患者: 某女 (8岁)。主诊断: 多处软组织挫伤伴撕裂伤。匹配"侵害未成年人高风险诊断编码库"，触发预警。', evidence: `[患者信息] 姓名: 某女 | 年龄: 8岁 | 性别: 女\n[主诊断] ICD10: T00.901 | 多处软组织挫伤伴撕裂伤\n>>> 异常判定: 高风险诊断+多处损伤，疑似侵害未成年人线索。` },
    { id: 'T012', time: '2026-03-29 20:15', org: '市中心医院', person: '儿科', violationType: '未成年人高危', detail: '患者: 某男 (5岁)。反复外伤就诊，30天内第3次因外伤就诊，触发异常聚集预警。', evidence: `[患者信息] 姓名: 某男 | 年龄: 5岁\n[就诊记录] 第1次: 03-10 外伤 | 第2次: 03-20 外伤 | 第3次: 03-29 外伤\n>>> 异常判定: 未成年人反复外伤就诊，疑似虐待。` },
    { id: 'T013', time: '2026-03-28 11:00', org: '省立第一医院', person: '急诊科', violationType: '未成年人高危', detail: '患者: 某女 (11岁)。主诊断: 四肢多处骨折。对应"高能量损伤+低龄"模式，疑似意外伤或虐待。', evidence: `[患者信息] 姓名: 某女 | 年龄: 11岁\n[主诊断] 四肢多处骨折（高能量损伤）\n>>> 异常判定: 低龄+高能量损伤组合，触发预警。` },
    { id: 'T014', time: '2026-03-27 09:30', org: '省肿瘤医院', person: '儿科肿瘤科', violationType: '未成年人高危', detail: '患者: 某男 (6岁)。反复就诊，30天内第4次因不明原因发热入院，疑似漏诊重大疾病。', evidence: `[患者信息] 姓名: 某男 | 年龄: 6岁\n[就诊记录] 30天内第4次入院，均以"不明原因发热"为主诉\n>>> 异常判定: 反复入院且诊断不明，疑似漏诊。` },
    { id: 'T015', time: '2026-03-26 16:00', org: '省立第三医院', person: '骨科', violationType: '未成年人高危', detail: '患者: 某女 (9岁)。主诊断: 股骨骨折。主诉与体征不符，疑似非意外伤。', evidence: `[患者信息] 姓名: 某女 | 年龄: 9岁\n[影像检查] X光: 左股骨骨折（横形骨折，高能量特征）\n[主诉] 自述从床上跌落\n>>> 异常判定: 骨折类型与主诉不符，疑似非意外伤。` },
  ],

  r11: [
    { id: 'T016', time: '2026-03-31 08:10', org: '社区卫生服务中心', person: '刘医生', violationType: '麻精药品异常', detail: '患者: 王某。7天内第3次开具控缓释制剂(盐酸羟考酮)，超出7天量限制。', evidence: `[患者信息] 姓名: 王某 | 类别: 普通患者\n[处方记录] 03-25: 7天量 | 03-28: 7天量 | 03-31: 7天量\n>>> 异常判定: 7天内第3次开药，超出7天量限制。` },
    { id: 'T017', time: '2026-03-30 11:20', org: '仁爱医院', person: '陈医生', violationType: '麻精药品异常', detail: '患者: 李某。癌痛患者15天内开具30天量硫酸吗啡缓释片。', evidence: `[患者信息] 姓名: 李某 | 类别: 癌痛患者\n>>> 异常判定: 癌痛患者超量开具麻精药品。` },
    { id: 'T018', time: '2026-03-29 14:45', org: '省立第一医院', person: '疼痛科 王主任', violationType: '麻精药品异常', detail: '患者: 张某。连续3个月使用芬太尼透皮贴剂，月用量超过规定限量。', evidence: `[患者信息] 姓名: 张某 | 药品: 芬太尼透皮贴剂\n[用量统计] 月处方量: 6贴（规定限量: 4贴/月）\n>>> 异常判定: 连续超量使用麻精药品。` },
    { id: 'T019', time: '2026-03-28 09:30', org: '市中心医院', person: '肿瘤科 李医生', violationType: '麻精药品异常', detail: '患者: 赵某。30天内累计开具泰勒宁(氨酚羟考酮)120片，远超同类药品规定用量。', evidence: `[患者信息] 姓名: 赵某 | 药品: 氨酚羟考酮\n[30天处方量] 120片 | 规定限量: 60片/月\n>>> 异常判定: 累计用量超过规定限量2倍。` },
    { id: 'T020', time: '2026-03-27 16:20', org: '康华医院', person: '内科 孙医生', violationType: '麻精药品异常', detail: '患者: 周某。非癌痛患者开具盐酸吗啡缓释片(30mg)，违反非癌痛禁用原则。', evidence: `[患者信息] 姓名: 周某 | 诊断: 腰椎间盘突出\n[处方] 盐酸吗啡缓释片30mg | 诊断: 非癌痛\n>>> 异常判定: 非癌痛患者开具吗啡缓释制剂，违反用药规范。` },
    { id: 'T021', time: '2026-03-26 10:00', org: '县人民医院', person: '急诊科', violationType: '麻精药品异常', detail: '患者: 吴某。7天内重复开具盐酸哌替啶注射剂（规定：癌痛患者最长3天用量）。', evidence: `[患者信息] 姓名: 吴某 | 诊断: 急性腰扭伤（非癌痛）\n[处方] 盐酸哌替啶 | 7天用量: 7支\n>>> 异常判定: 非癌痛患者开具哌替啶，超规定剂量。` },
  ],

  r12: [
    { id: 'T022', time: '2026-03-27 14:00', org: '康华医院', person: '医务科', violationType: '限制类技术超范围', detail: '机构未取得"造血干细胞移植术"资质，但已开展2例手术。', evidence: `[机构资质] 康华医院 | 无造血干细胞移植术备案\n[实际开展] 造血干细胞移植术: 2例\n>>> 异常判定: 未取得资质开展限制类技术。` },
    { id: 'T023', time: '2026-03-25 10:30', org: '仁爱医院', person: '医务科', violationType: '限制类技术超范围', detail: '机构未取得"人工耳蜗植入术"资质，但备案系统中已出现相关收费记录。', evidence: `[机构资质] 仁爱医院 | 无人工耳蜗植入术资质\n[收费记录] 人工耳蜗植入术: 1例\n>>> 异常判定: 未取得资质开展限制类技术。` },
    { id: 'T024', time: '2026-03-23 09:00', org: '省立第一医院', person: '器官移植中心', violationType: '限制类技术超范围', detail: '机构已取得肝脏移植资质，但未经批准开展肺脏移植业务。', evidence: `[机构资质] 省立第一医院 | 已备案: 肝脏移植\n[业务开展] 肺脏移植: 3例（未备案）\n>>> 异常判定: 超资质范围开展移植手术。` },
    { id: 'T025', time: '2026-03-20 15:45', org: '市中心医院', person: '神经外科', violationType: '限制类技术超范围', detail: '神经外科主任开展"深部脑刺激术(DBS)"，但机构仅完成帕金森病DBS手术资质备案，未覆盖运动障碍疾病全范围。', evidence: `[机构备案] 深部脑刺激术: 仅限帕金森病\n[实际开展] 用于肌张力障碍: 2例\n>>> 异常判定: 超出备案病种范围。` },
    { id: 'T026', time: '2026-03-18 11:30', org: '省肿瘤医院', person: '放射治疗中心', violationType: '限制类技术超范围', detail: '"质子重离子治疗"设备已到位，但机构未完成国家限制类技术备案即开始收治患者。', evidence: `[机构备案] 质子重离子治疗: 未备案\n[实际收治] 患者入组: 12例\n>>> 异常判定: 设备启用前未完成限制类技术备案。` },
  ],

  r13: [
    { id: 'T027', time: '2026-03-26 10:30', org: '省肿瘤医院', person: '肿瘤科 张主任', violationType: '抗肿瘤药物不规范', detail: '患者: 赵某。使用贝伐珠单抗，但无VEGF基因检测结果。', evidence: `[处方信息] 药品: 贝伐珠单抗 | 检测记录: VEGF基因检测未做\n>>> 异常判定: 使用抗肿瘤药物前未完成分子靶点检测。` },
    { id: 'T028', time: '2026-03-25 14:20', org: '市中心医院', person: '肿瘤科 刘医生', violationType: '抗肿瘤药物不规范', detail: '患者: 钱某。使用吉非替尼(易瑞沙)，但EGFR基因检测结果未归档，疑似先用药后检测。', evidence: `[处方信息] 药品: 吉非替尼 | 检测记录: EGFR检测报告中（归档中）\n>>> 异常判定: 先用药后归档检测报告，流程不规范。` },
    { id: 'T029', time: '2026-03-24 09:15', org: '省立第一医院', person: '血液科 周主任', violationType: '抗肿瘤药物不规范', detail: '患者: 孙某。使用伊马替尼治疗慢性髓系白血病，但融合基因BCR-ABL检测阳性确认前已启动用药。', evidence: `[处方信息] 药品: 伊马替尼 | 检测记录: BCR-ABL尚未确诊\n>>> 异常判定: 确诊前启动靶向治疗。` },
    { id: 'T030', time: '2026-03-22 11:40', org: '省肿瘤医院', person: '肿瘤科 李医生', violationType: '抗肿瘤药物不规范', detail: '患者: 郑某。使用曲妥珠单抗(赫赛汀)，但HER2免疫组化检测结果为阴性，不符合用药指征。', evidence: `[处方信息] 药品: 曲妥珠单抗 | HER2检测: 免疫组化(-)\n>>> 异常判定: HER2阴性不符合赫赛汀用药指征。` },
    { id: 'T031', time: '2026-03-20 16:00', org: '市中心医院', person: '胃肠外科', violationType: '抗肿瘤药物不规范', detail: '患者: 吴某。使用西妥昔单抗治疗结直肠癌，但KRAS基因检测结果为突变型(不适合该药)。', evidence: `[处方信息] 药品: 西妥昔单抗 | KRAS检测: 突变型\n>>> 异常判定: KRAS突变型患者不适用西妥昔单抗。` },
    { id: 'T032', time: '2026-03-19 10:30', org: '省立第三医院', person: '肿瘤科', violationType: '抗肿瘤药物不规范', detail: '患者: 冯某。使用奥希替尼(Tagrisso)治疗非小细胞肺癌，但无T790M基因突变确认报告。', evidence: `[处方信息] 药品: 奥希替尼 | T790M检测: 未做\n>>> 异常判定: 使用三代TKI前须确认T790M突变状态。` },
  ],

  r14: [
    { id: 'm141', org: '全省平均', metric1: 'TNM分期评估率', value1: '85.4%', metric2: '环比上月', value2: '+2.1%' },
    { id: 'm142', org: '省肿瘤医院', metric1: 'TNM分期评估率', value1: '98.2%', metric2: '未评估病例', value2: '12例' },
    { id: 'm143', org: '县人民医院', metric1: 'TNM分期评估率', value1: '45.6%', metric2: '未评估病例', value2: '89例' },
    { id: 'm144', org: '市中心医院', metric1: 'TNM分期评估率', value1: '72.3%', metric2: '未评估病例', value2: '45例' },
    { id: 'm145', org: '省立第一医院', metric1: 'TNM分期评估率', value1: '88.7%', metric2: '未评估病例', value2: '23例' },
    { id: 'm146', org: '省立第三医院', metric1: 'TNM分期评估率', value1: '68.5%', metric2: '未评估病例', value2: '56例' },
    { id: 'm147', org: '县第二医院', metric1: 'TNM分期评估率', value1: '32.1%', metric2: '未评估病例', value2: '102例' },
  ],
}

const isAll = computed(() => currentHospitalId.value === 'all')

function matchHospital(item: any, hName: string): boolean {
  if (item.org === '全省平均') return false
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

const techColumns = [
  { field: 'time', header: '预警时间' },
  { field: 'org', header: '涉事机构' },
  { field: 'person', header: '涉事人员' },
  { field: 'detail', header: '违规详情' },
]

function handleExport() {
  const rule = currentRule.value
  const name = rule ? `${rule.no}-${rule.name}` : '技术要素总览'
  exportToExcel(tableData.value, techColumns, `技术要素_${name}`)
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.animate-slide-in { animation: slideIn 0.3s ease-out; }
@keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }
</style>
