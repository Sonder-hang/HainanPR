<template>
  <div class="h-full flex flex-col bg-white">
    <!-- 二级Tab栏 -->
    <div class="bg-[#e8eef9] px-5 pt-3 border-b border-[#b8c9e8]/60 shrink-0">
      <div class="flex space-x-5 overflow-x-auto">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="pb-2.5 text-[13px] font-medium whitespace-nowrap transition-colors border-b-2"
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
        人员要素 — 监管规则总览
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
        <p class="text-blue-600 text-[12px]">人员要素审核范围：住院。对医师职称、执业记录、多点执业等关键信息进行智能监测与预警。</p>
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
            <div class="text-[11px] text-[#B8BCCC] mb-2">阈值：<span class="text-[#596080] font-medium">{{ rule.threshold }}</span></div>
            <div class="flex items-center justify-between">
              <span :class="['text-[11px] font-medium px-2 py-0.5 rounded-full border', rule.mode === 'alert' ? 'border-red-200 text-red-600 bg-red-50' : 'border-emerald-200 text-emerald-600 bg-emerald-50']">
                {{ rule.mode === 'alert' ? '预警模式' : '常规监测' }}
              </span>
              <span class="text-[11px] text-red-600 font-bold">{{ getMockCount(rule.id) }} 条</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 具体规则明细视图 -->
    <template v-else>
      <div class="p-4 shrink-0">
        <div class="border rounded-[2px] p-2.5 flex items-start bg-blue-50/50 border-blue-200">
          <Info class="w-3.5 h-3.5 mr-2 shrink-0 mt-0.5 text-[#0A6EFD]" />
          <div>
            <h4 class="text-[13px] font-medium text-blue-800">{{ currentRule?.name }}</h4>
            <p class="text-[11px] mt-0.5 text-blue-600">{{ currentRule?.logic }}</p>
          </div>
        </div>
      </div>

      <div class="flex-1 px-4 pb-4 overflow-hidden flex flex-col">
        <div class="bg-white rounded-[2px] border border-[#b8c9e8]/60 flex-1 overflow-hidden flex flex-col shadow-sm">
          <div class="p-3.5 border-b border-[#b8c9e8]/40 flex justify-between items-center shrink-0">
            <h3 class="font-semibold text-[#1F264D] flex items-center text-[13px]">
              违规预警数据列表
              <span class="ml-2 bg-red-100 text-red-600 py-0.5 px-2 rounded-full text-[11px] font-bold">{{ tableData.length }}</span>
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

          <div class="flex-1 overflow-auto">
            <table class="w-full text-left border-collapse">
              <thead class="bg-[#e8eef9] sticky top-0 z-10">
                <tr>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">预警时间</th>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">涉事机构</th>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">涉事医师</th>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">患者信息</th>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide">违规详情</th>
                  <th class="px-3.5 py-2.5 text-[11px] font-semibold text-[#596080] uppercase tracking-wide text-right">操作</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-[#b8c9e8]/30">
                <tr v-for="row in tableData" :key="row.id" class="hover:bg-[#e8eef9]/40 transition-colors group">
                  <td class="px-3.5 py-2.5 text-[12px] text-[#596080] whitespace-nowrap"><Clock class="w-3 h-3 inline mr-1 text-[#B8BCCC]"/>{{ row.time }}</td>
                  <td class="px-3.5 py-2.5 text-[12px] text-[#1F264D] font-medium">{{ row.org }}</td>
                  <td class="px-3.5 py-2.5 text-[12px]">
                    <div class="font-medium text-[#1F264D] text-[12px]">{{ row.doctor }}</div>
                    <div class="text-[11px] text-[#B8BCCC]">{{ row.title }}</div>
                  </td>
                  <td class="px-3.5 py-2.5 text-[12px] text-[#596080]">{{ row.patient }}</td>
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
              <div><span class="text-[#596080] block mb-0.5">触发时间</span><span class="font-medium text-[#1F264D]">{{ drawerData.time }}</span></div>
              <div><span class="text-[#596080] block mb-0.5">流水号</span><span class="font-medium text-[#1F264D] font-mono">PER-{{ drawerData.id }}-2026</span></div>
              <div><span class="text-[#596080] block mb-0.5">涉事机构</span><span class="font-medium text-[#1F264D]">{{ drawerData.org }}</span></div>
              <div><span class="text-[#596080] block mb-0.5">涉事医师</span><span class="font-medium text-[#1F264D]">{{ drawerData.doctor }}</span></div>
              <div><span class="text-[#596080] block mb-0.5">医师职称</span><span class="font-medium text-[#1F264D]">{{ drawerData.title }}</span></div>
              <div><span class="text-[#596080] block mb-0.5">患者信息</span><span class="font-medium text-[#1F264D]">{{ drawerData.patient }}</span></div>
            </div>
          </div>

          <div class="bg-white border border-[#b8c9e8]/60 rounded-[2px] p-4">
            <h3 class="font-bold text-[#1F264D] text-[13px] mb-2.5">违规判定依据</h3>
            <div class="bg-red-50 border border-red-200 rounded-[2px] p-3 text-[12px] text-red-800">
              <p class="font-medium mb-1">违规类型：{{ drawerData.violationType }}</p>
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
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Activity,
  Calendar,
  ChevronDown,
  Clock,
  Download,
  Eye,
  Info,
  MapPin,
  Search,
  ShieldAlert,
  X,
} from 'lucide-vue-next'
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
  {
    id: 'r1', mode: 'alert', name: '越权开具抗生素',
    desc: '医师职称与限制级、特殊级抗生素匹配异常，系统自动报警。',
    scope: '住院', threshold: '无',
    logic: '在系统中维护医师职称，设定"职称-限制级、特殊级抗生素"匹配规则，医生开了与自己职称不符的限制级或特殊级抗生素时自动报警。'
  },
  {
    id: 'r2', mode: 'alert', name: '时空轨迹异常',
    desc: '同一医师短时间内在不同医疗机构中出现诊疗记录，系统自动报警。',
    scope: '住院', threshold: '30分钟内',
    logic: '在系统中维护医师操作记录，设定"同一医师短时间内在不同医疗机构中出现诊疗记录"匹配规则，某个时间段内医生在不同机构内开了医嘱信息时自动报警。'
  },
  {
    id: 'r3', mode: 'alert', name: '多点执业冲突',
    desc: '对主执业机构在公立医院的医师发生民营医院多点执业或诊疗记录进行监测。',
    scope: '住院', threshold: '无',
    logic: '在系统中维护医师多点执业记录，设定"对主执业机构在公立医院的发生民营医院多点执业或诊疗记录"匹配规则，同一患者由同一医生在公立和民营医院都开了医嘱时自动报警。'
  },
]

const tabs = [{ id: 'overview', name: '分类总览' }, ...rules]
const activeTab = ref(route.query.tab as string || 'overview')
const drawerData = ref<any>(null)
const currentRule = computed(() => rules.find(r => r.id === activeTab.value))

watch(activeTab, (val) => {
  router.replace({ query: val === 'overview' ? {} : { tab: val } })
})

const MOCK_DATA: Record<string, any[]> = {
  r1: [
    { id: 'P001', time: '2026-03-31 09:12', org: '省立第一医院', doctor: '李华', title: '住院医师', patient: '张三 (Z20260301)', violationType: '越权开具特殊级抗生素', detail: '越权开具特殊级抗生素(美罗培南)。依据《抗菌药物临床应用管理办法》，住院医师无权开具特殊级抗生素。', evidence: `[医师档案] 姓名: 李华 | 职称: 住院医师 | 执业机构: 省立第一医院\n[处方记录] 药品: 美罗培南(注射剂) | 级别: 特殊级 | 开具时间: 09:12\n[系统判定] ❌ 违规: 住院医师无权开具特殊级抗生素。\n[规则依据] 《抗菌药物临床应用管理办法》第二十七条` },
    { id: 'P002', time: '2026-03-30 14:35', org: '省立第一医院', doctor: '张海燕', title: '主治医师', patient: '王丽 (Z20260302)', violationType: '越权开具限制级抗生素', detail: '开具限制级抗生素(头孢吡肟)，但未完成限制级抗生素使用授权备案。', evidence: `[医师档案] 姓名: 张海燕 | 职称: 主治医师 | 执业机构: 省立第一医院\n[处方记录] 药品: 头孢吡肟 | 级别: 限制级 | 开具时间: 14:35\n[系统判定] ❌ 违规: 限制级抗生素授权未审批。` },
    { id: 'P003', time: '2026-03-28 10:05', org: '省立第一医院', doctor: '陈志刚', title: '住院医师', patient: '赵敏 (Z20260281)', violationType: '越权开具特殊级抗生素', detail: '住院医师开具美罗培南(特殊级抗生素)，系统拦截并预警。', evidence: `[处方记录] 药品: 美罗培南 | 级别: 特殊级 | 开具时间: 10:05\n>>> 违规: 住院医师越权。` },
    { id: 'P004', time: '2026-03-31 08:45', org: '市中心医院', doctor: '王强', title: '主治医师', patient: '刘洋 (Z20260311)', violationType: '越权开具限制级抗生素', detail: '主治医师开具限制级抗生素(头孢吡肟)，但未完成限制级抗生素使用授权备案。', evidence: `[医师档案] 姓名: 王强 | 职称: 主治医师 | 执业机构: 市中心医院\n[处方记录] 药品: 头孢吡肟 | 级别: 限制级 | 开具时间: 08:45\n[系统判定] ❌ 违规: 限制级抗生素授权未审批。` },
    { id: 'P005', time: '2026-03-29 15:20', org: '市中心医院', doctor: '周慧敏', title: '住院医师', patient: '孙刚 (Z20260291)', violationType: '越权开具特殊级抗生素', detail: '住院医师开具亚胺培南(特殊级)，越权。', evidence: `[处方记录] 药品: 亚胺培南 | 级别: 特殊级\n>>> 违规: 住院医师越权。` },
    { id: 'P006', time: '2026-03-30 11:30', org: '省肿瘤医院', doctor: '吴斌', title: '副主任医师', patient: '郑红 (Z20260303)', violationType: '越权开具限制级抗生素', detail: '副主任医师开具限制级抗生素(头孢他啶)，授权备案已过期(2025-12-31到期)。', evidence: `[医师档案] 姓名: 吴斌 | 职称: 副主任医师 | 执业机构: 省肿瘤医院\n[授权有效期] ❌ 已过期: 限制级抗生素授权至2025-12-31。` },
    { id: 'P007', time: '2026-03-27 09:55', org: '省肿瘤医院', doctor: '黄莉', title: '主治医师', patient: '徐明 (Z20260271)', violationType: '越权开具特殊级抗生素', detail: '主治医师开具美罗培南(特殊级)，未完成特殊级抗生素申请流程。', evidence: `[处方记录] 药品: 美罗培南 | 级别: 特殊级\n>>> 违规: 特殊级抗生素申请流程未完成。` },
    { id: 'P008', time: '2026-03-31 10:18', org: '县人民医院', doctor: '刘医生', title: '住院医师', patient: '马丽 (Z20260312)', violationType: '越权开具特殊级抗生素', detail: '越权开具特殊级抗生素(美罗培南)。', evidence: `[医师档案] 姓名: 刘医生 | 职称: 住院医师 | 执业机构: 县人民医院\n[处方记录] 药品: 美罗培南 | 级别: 特殊级\n>>> 违规: 住院医师无权开具特殊级抗生素。` },
    { id: 'P009', time: '2026-03-29 14:00', org: '县人民医院', doctor: '韩建国', title: '主治医师', patient: '宋杰 (Z20260292)', violationType: '越权开具限制级抗生素', detail: '越权开具限制级抗生素(头孢曲松)，授权未审批。', evidence: `[处方记录] 药品: 头孢曲松 | 级别: 限制级\n>>> 违规: 授权未审批。` },
    { id: 'P010', time: '2026-03-30 08:30', org: '省立第三医院', doctor: '邓宇轩', title: '住院医师', patient: '冯娟 (Z20260304)', violationType: '越权开具特殊级抗生素', detail: '住院医师开具比阿培南(特殊级)，系统预警。', evidence: `[处方记录] 药品: 比阿培南 | 级别: 特殊级\n>>> 违规: 住院医师越权开具特殊级抗生素。` },
    { id: 'P011', time: '2026-03-28 16:40', org: '县第二医院', doctor: '杨涛', title: '住院医师', patient: '曹阳 (Z20260282)', violationType: '越权开具特殊级抗生素', detail: '越权开具美罗培南(特殊级)。', evidence: `[处方记录] 药品: 美罗培南 | 级别: 特殊级\n>>> 违规: 住院医师越权。` },
    { id: 'P012', time: '2026-03-31 13:20', org: '康华医院', doctor: '彭敏', title: '主治医师', patient: '蒋伟 (Z20260313)', violationType: '越权开具限制级抗生素', detail: '主治医师开具限制级(头孢哌酮舒巴坦)，授权备案中未通过审核。', evidence: `[处方记录] 药品: 头孢哌酮舒巴坦 | 级别: 限制级\n>>> 违规: 授权审核未通过。` },
    { id: 'P013', time: '2026-03-26 11:10', org: '仁爱医院', doctor: '卢刚', title: '住院医师', patient: '田甜 (Z20260261)', violationType: '越权开具特殊级抗生素', detail: '住院医师开具美罗培南(特殊级)。', evidence: `[处方记录] 药品: 美罗培南 | 级别: 特殊级\n>>> 违规: 住院医师越权。` },
  ],

  r2: [
    { id: 'S001', time: '2026-03-31 11:20', org: '市中心医院', org2: '仁爱医院', doctor: '赵伟', title: '副主任医师', patient: '-', violationType: '时空轨迹异常', detail: '25分钟内跨越30公里在两家医院产生门诊处方记录，涉嫌挂证或代挂号。', evidence: `[记录A] 机构: 市中心医院 | 医师: 赵伟 | 时间: 11:05:22\n[记录B] 机构: 仁爱医院 | 医师: 赵伟 | 时间: 11:20:45\n>>> 异常: 两地正常车程>30分钟，打卡仅隔15分钟，涉嫌挂证。` },
    { id: 'S002', time: '2026-03-29 16:40', org: '县人民医院', org2: '康华医院', doctor: '钱进', title: '主治医师', patient: '-', violationType: '时空轨迹异常', detail: '18分钟内跨越15公里在两家医疗机构产生处方记录，疑似挂证行为。', evidence: `[记录A] 机构: 县人民医院 | 医师: 钱进 | 时间: 16:22:10\n[记录B] 机构: 康华医院 | 医师: 钱进 | 时间: 16:40:55\n>>> 异常: 18分钟跨越15公里，疑似挂证。` },
    { id: 'S003', time: '2026-03-30 09:50', org: '省立第一医院', org2: '省立第三医院', doctor: '胡雪峰', title: '主任医师', patient: '-', violationType: '时空轨迹异常', detail: '38分钟内在两家省级医院同时产生处方记录，GPS轨迹显示两地相距8公里，疑似跨机构飞刀。', evidence: `[记录A] 机构: 省立第一医院 | 医师: 胡雪峰 | 时间: 09:22:15\n[记录B] 机构: 省立第三医院 | 医师: 胡雪峰 | 时间: 09:50:33\n>>> 异常: 两院同时在线，疑似跨机构飞刀。` },
    { id: 'S004', time: '2026-03-28 14:15', org: '省立第一医院', org2: '康华医院', doctor: '丁峰', title: '主治医师', patient: '-', violationType: '时空轨迹异常', detail: '22分钟内在两家医院产生诊疗记录，省立第一医院到康华医院正常车程约20分钟。', evidence: `[记录A] 省立第一医院 | 14:05:10\n[记录B] 康华医院 | 14:15:42\n>>> 异常: 记录时间间隔<正常车程。` },
    { id: 'S005', time: '2026-03-31 08:30', org: '市中心医院', org2: '县第二医院', doctor: '高健', title: '副主任医师', patient: '-', violationType: '时空轨迹异常', detail: '跨区域同时在线：市中心医院至县第二医院相距45公里，42分钟内同时产生处方记录。', evidence: `[记录A] 市中心医院 | 08:18:05\n[记录B] 县第二医院 | 08:30:22\n>>> 异常: 45公里42分钟内不可能到达，GPS定位存疑。` },
    { id: 'S006', time: '2026-03-29 17:00', org: '市中心医院', org2: '省立第三医院', doctor: '孙立军', title: '主任医师', patient: '-', violationType: '时空轨迹异常', detail: '省立第三医院与市中心医院相距12公里，19分钟内同时在线，异常。', evidence: `[记录A] 市中心医院 | 17:00:00\n[记录B] 省立第三医院 | 17:19:30\n>>> 异常: 记录疑似重复或时间造假。` },
    { id: 'S007', time: '2026-03-30 10:40', org: '省肿瘤医院', org2: '康华医院', doctor: '林海涛', title: '副主任医师', patient: '-', violationType: '时空轨迹异常', detail: '省肿瘤医院与康华医院相距25公里，28分钟内同时产生处方记录，涉嫌挂证。', evidence: `[记录A] 省肿瘤医院 | 10:40:00\n[记录B] 康华医院 | 10:55:10\n>>> 异常: 25公里28分钟内，存疑。` },
    { id: 'S008', time: '2026-03-27 15:30', org: '县人民医院', org2: '县第二医院', doctor: '郑明辉', title: '主治医师', patient: '-', violationType: '时空轨迹异常', detail: '两县医院相距20公里，25分钟内同时产生诊疗记录。', evidence: `[记录A] 县人民医院 | 15:30:00\n[记录B] 县第二医院 | 15:25:40\n>>> 异常: 交叉时间记录，存疑。` },
  ],

  r3: [
    { id: 'M001', time: '2026-03-30 10:15', org: '省立第一医院', org2: '康华医院', doctor: '孙磊', title: '主任医师', patient: '患者: 周某', violationType: '多点执业冲突', detail: '主执业在公立省立第一医院，同时在民营康华医院产生诊疗记录，违反公立医院医师多点执业管理规定。', evidence: `[就诊记录A] 机构: 省立第一医院(公立) | 医师: 孙磊 | 患者: 周某 | 时间: 03-28 09:00\n[就诊记录B] 机构: 康华医院(民营,多点) | 医师: 孙磊 | 患者: 周某 | 时间: 03-30 10:15\n>>> 违规: 公立主执业医师不得在民营机构多点接诊同类患者。` },
    { id: 'M002', time: '2026-03-27 15:30', org: '市中心医院', org2: '仁爱医院', doctor: '周涛', title: '副主任医师', patient: '患者: 吴某', violationType: '多点执业冲突', detail: '患者在公立医院住院后，转至民营医院由同一医师继续诊疗，涉嫌利益输送。', evidence: `[记录A] 机构: 市中心医院(公立) | 医师: 周涛 | 患者: 吴某 | 时间: 03-25 14:00\n[记录B] 机构: 仁爱医院(民营) | 医师: 周涛 | 患者: 吴某 | 时间: 03-27 15:30\n>>> 违规: 同一患者公私机构连续接诊。` },
    { id: 'M003', time: '2026-03-29 08:45', org: '省立第一医院', org2: '康华医院', doctor: '蒋志明', title: '主任医师', patient: '患者: 钱某', violationType: '多点执业冲突', detail: '主执业在省立第一医院（公立），多点执业至康华医院（民营），违反医师多点执业"公对私"限制。', evidence: `[记录A] 省立第一医院(公立) | 医师: 蒋志明 | 时间: 03-29 08:45\n[记录B] 康华医院(民营) | 医师: 蒋志明 | 时间: 03-29 14:20\n>>> 违规: 公立主执业医师不得在民营机构开展同类多点执业。` },
    { id: 'M004', time: '2026-03-31 09:30', org: '市中心医院', org2: '康华医院', doctor: '叶玲', title: '副主任医师', patient: '患者: 陈某', violationType: '多点执业冲突', detail: '市中心医院副主任医师在康华医院（民营）开展同类诊疗，违反多点执业规定。', evidence: `[记录A] 市中心医院(公立) | 医师: 叶玲 | 患者: 陈某 | 时间: 03-31 09:30\n[记录B] 康华医院(民营) | 医师: 叶玲 | 患者: 陈某 | 时间: 03-31 11:00\n>>> 违规: 公对私多点执业。` },
    { id: 'M005', time: '2026-03-28 14:20', org: '省肿瘤医院', org2: '康华医院', doctor: '杜建业', title: '主任医师', patient: '患者: 许某', violationType: '多点执业冲突', detail: '省肿瘤医院主任医师在康华医院开展肿瘤相关诊疗，违反肿瘤专科医师多点执业限制。', evidence: `[记录A] 省肿瘤医院(公立) | 医师: 杜建业 | 患者: 许某 | 时间: 03-26 10:00\n[记录B] 康华医院(民营) | 医师: 杜建业 | 患者: 许某 | 时间: 03-28 14:20\n>>> 违规: 肿瘤专科医师不得在民营机构开展同类多点执业。` },
    { id: 'M006', time: '2026-03-29 16:00', org: '省立第三医院', org2: '仁爱医院', doctor: '马志刚', title: '主治医师', patient: '患者: 何某', violationType: '多点执业冲突', detail: '省立第三医院主治医师在仁爱医院（民营）开展同类诊疗。', evidence: `[记录A] 省立第三医院(公立) | 医师: 马志刚 | 患者: 何某 | 时间: 03-29 09:00\n[记录B] 仁爱医院(民营) | 医师: 马志刚 | 患者: 何某 | 时间: 03-29 16:00\n>>> 违规: 公对私多点执业。` },
  ],
}

const isAll = computed(() => currentHospitalId.value === 'all')

function matchHospital(item: any, hName: string): boolean {
  return item.org === hName ||
    item.org2 === hName ||
    item.org.includes(hName) ||
    (item.multipleOrgs && item.multipleOrgs.some((o: string) => o === hName))
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

const personnelColumns = [
  { field: 'time', header: '预警时间' },
  { field: 'org', header: '涉事机构' },
  { field: 'doctor', header: '涉事医师' },
  { field: 'title', header: '职称' },
  { field: 'patient', header: '患者信息' },
  { field: 'detail', header: '违规详情' },
]

function handleExport() {
  const rule = currentRule.value
  const name = rule ? `${rule.no}-${rule.name}` : '人员要素总览'
  exportToExcel(tableData.value, personnelColumns, `人员要素_${name}`)
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.animate-slide-in { animation: slideIn 0.3s ease-out; }
@keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }
</style>
