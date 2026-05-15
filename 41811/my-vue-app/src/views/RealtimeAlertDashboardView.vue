<template>
  <div class="flex h-full min-h-0 flex-col bg-[#F7F9FC] font-sans text-[#1F264D]">

    <!-- 1. 动态顶栏区 -->
    <header
      class="flex min-h-[102px] shrink-0 flex-col justify-center gap-4 border-b border-[#E6E9F2] bg-white px-4 py-4 shadow-sm sm:flex-row sm:items-center sm:justify-between sm:px-8"
    >
      <div class="flex min-w-0 flex-wrap items-center gap-3 sm:gap-4">
        <div class="hidden rounded-[2px] bg-[#EEF2FF] p-2 text-[#0A6EFD] sm:block">
          <ShieldAlert :size="24" />
        </div>
        <h2 class="text-[20px] font-bold tracking-tight text-[#1F264D] sm:text-[22px] lg:text-[24px]">
          单据违规审核看板
        </h2>
        <span
          class="inline-flex items-center gap-1.5 rounded-full border border-[#97DEC6] bg-[#ECFDF5] px-3 py-1 text-[11px] font-bold tracking-wide text-[#12B881] sm:text-[12px]"
        >
          <Activity :size="14" class="animate-pulse" />
          自动报警引擎运行中
        </span>
      </div>
      <div class="flex flex-wrap items-center gap-3 sm:gap-4">
        <div class="relative min-w-0 flex-1 sm:flex-initial">
          <Search
            class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-[#B8BCCC]"
            :size="18"
          />
          <input
            v-model="keyword"
            type="text"
            placeholder="搜索医院、科室、医生姓名..."
            class="box-border h-[32px] w-full rounded-[2px] border border-[#E6E9F2] bg-[#F7F9FC] py-2.5 pl-10 pr-4 text-[14px] text-[#1F264D] outline-none transition-all placeholder:text-[#B8BCCC] focus:border-[#0A6EFD] focus:bg-white focus:ring-2 focus:ring-[#0A6EFD]/20 sm:w-[min(300px,100%)]"
          />
        </div>
        <button
          type="button"
          class="box-border flex h-[32px] shrink-0 items-center gap-2 whitespace-nowrap rounded-[2px] bg-[#2E57E5] px-5 py-2.5 text-[14px] font-medium text-white shadow-sm shadow-[#2E57E5]/30 transition-colors hover:bg-[#1E4BD8]"
        >
          <Filter :size="16" />
          高级筛选
        </button>
      </div>
    </header>

    <!-- 2. 动态内容滚动区 -->
    <div class="alert-scroll flex flex-1 flex-col overflow-hidden">
      <!-- 全局筛选栏：要素分类与级联规则 -->
      <div
        class="flex shrink-0 flex-wrap items-center gap-3 border-b border-[#E6E9F2] bg-[#F7F9FC] px-6 py-3"
      >
        <!-- 一级分类：要素 -->
        <div
          class="flex items-center overflow-hidden rounded-[2px] border border-[#E6E9F2] bg-white shadow-sm"
        >
          <select
            v-model="filterCategory"
            class="box-border h-[32px] min-w-[140px] border-r border-[#E6E9F2] bg-transparent px-3 py-2.5 text-[14px] font-medium text-[#1F264D] outline-none"
            @change="filterRule = 'all'"
          >
            <option value="all">全部要素分类</option>
            <option value="personnel">人员要素</option>
            <option value="institution">机构要素</option>
            <option value="technical">技术要素</option>
            <option value="equipment">设备要素</option>
          </select>
        </div>

        <!-- 二级分类：具体规则 (级联) -->
        <div
          class="flex items-center overflow-hidden rounded-[2px] border border-[#E6E9F2] bg-white shadow-sm"
        >
          <select
            v-model="filterRule"
            :disabled="filterCategory === 'all'"
            class="box-border h-[32px] min-w-[220px] bg-transparent px-3 py-2.5 text-[14px] font-medium outline-none sm:min-w-[240px]"
            :class="
              filterCategory === 'all'
                ? 'text-[#B8BCCC] cursor-not-allowed'
                : 'text-[#1F264D]'
            "
          >
            <option
              v-for="rule in ruleCategories[filterCategory]"
              :key="rule.id"
              :value="rule.id"
            >
              {{ rule.name }}
            </option>
          </select>
        </div>

        <div class="flex-1" />

        <!-- 状态切换按钮 -->
        <div
          class="flex items-center gap-1 rounded-[2px] border border-[#E6E9F2] bg-[#F7F9FC] p-1"
        >
          <button
            v-for="s in STATUS_TABS"
            :key="s.value"
            type="button"
            class="box-border h-[32px] shrink-0 rounded-[2px] px-4 text-[13px] font-medium transition-all"
            :class="
              filterStatus === s.value
                ? s.activeClass
                : 'text-[#596080] hover:text-[#1F264D]'
            "
            @click="filterStatus = s.value"
          >
            {{ s.label }}
          </button>
        </div>
      </div>

      <!-- 报警列表区 -->
      <div class="alert-scroll flex-1 overflow-auto bg-[#F7F9FC] p-6">
        <div
          class="flex flex-col overflow-hidden rounded-[2px] border border-[#E6E9F2] bg-white shadow-sm"
        >
          <!-- KPI 摘要条 -->
          <div class="flex flex-wrap gap-6 border-b border-[#E6E9F2] bg-[#F2F5FA] px-6 py-4">
            <div
              v-for="kpi in kpiSummary"
              :key="kpi.label"
              class="flex items-center gap-3"
            >
              <span class="text-[13px] text-[#596080]">{{ kpi.label }}</span>
              <span
                class="text-[18px] font-black"
                :class="kpi.valueClass"
              >{{ kpi.value }}</span>
            </div>
          </div>

          <table class="w-full min-w-[960px] text-left text-[14px]">
            <thead class="border-b border-[#E6E9F2] bg-[#F2F5FA]">
              <tr class="text-[13px] font-bold text-[#596080]">
                <th class="p-4 w-[140px]">报警时间</th>
                <th class="p-4 w-[120px]">要素分类</th>
                <th class="p-4 w-[200px]">自动触发规则</th>
                <th class="p-4 min-w-[200px]">违规主体 (机构/医生)</th>
                <th class="p-4">系统研判简述</th>
                <th class="p-4 w-[90px] text-center">状态</th>
                <th class="p-4 w-[80px] text-center">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#F7F9FC]">
              <tr
                v-for="alert in filteredAlerts"
                :key="alert.id"
                class="group cursor-pointer transition-colors hover:bg-[#EFF6FF]"
                :class="selectedAlert?.id === alert.id ? 'bg-[#EFF6FF]' : ''"
                @click="openDrawer(alert)"
              >
                <td class="p-4 whitespace-nowrap">
                  <span class="text-[13px] text-[#1F264D]">{{ alert.time.split(' ')[0] }}</span
                  ><br />
                  <span class="text-[12px] text-[#B8BCCC]">{{
                    alert.time.split(' ')[1]
                  }}</span>
                </td>
                <td class="p-4">
                  <span
                    class="inline-flex items-center rounded border px-2 py-0.5 text-[12px] font-medium"
                    :class="categoryTagClass(alert.categoryId)"
                  >
                    {{ alert.categoryName }}
                  </span>
                </td>
                <td class="p-4">
                  <p class="text-[13px] font-bold text-[#0A6EFD]">{{
                    alert.ruleName
                  }}</p>
                  <p
                    class="mt-0.5 flex items-center text-[11px] font-bold"
                    :class="
                      alert.actionType === 'intercept'
                        ? 'text-[#E5455F]'
                        : 'text-[#12B881]'
                    "
                  >
                    <Activity :size="11" class="mr-1" />
                    {alert.actionType === 'intercept'
                      ? '已执行医保拦截'
                      : '系统自动报警'}
                  </p>
                </td>
                <td class="p-4">
                  <p class="flex items-center text-[13px] font-medium text-[#1F264D]">
                    <Building2 :size="13" class="mr-1.5 text-[#B8BCCC]" />
                    {{ alert.hospital }}
                  </p>
                  <p class="mt-1 flex items-center text-[12px] text-[#596080]">
                    <Stethoscope :size="12" class="mr-1.5 text-[#B8BCCC]" />
                    {{ alert.department }} · {{ alert.doctor }}
                  </p>
                </td>
                <td class="p-4">
                  <p
                    class="line-clamp-2 text-[13px] leading-relaxed"
                    :class="
                      alert.actionType === 'intercept'
                        ? 'text-[#991B1B]'
                        : 'text-[#1F264D]'
                    "
                  >
                    {{ alert.detailMsg }}
                  </p>
                </td>
                <td class="p-4 text-center">
                  <span
                    class="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-[12px] font-bold"
                    :class="
                      alert.status === 'pending'
                        ? 'bg-[#FEF2F2] text-[#E5455F]'
                        : 'bg-[#F0FDF4] text-[#12B881]'
                    "
                  >
                    <component
                      :is="alert.status === 'pending' ? AlertOctagon : CheckCircle2"
                      :size="12"
                    />
                    {{ alert.status === 'pending' ? '待处理' : '已处理' }}
                  </span>
                </td>
                <td class="p-4 text-center">
                  <button
                    type="button"
                    class="box-border h-[32px] w-full rounded-[2px] border px-3 text-[12px] font-bold transition-colors"
                    :class="
                      alert.status === 'pending'
                        ? 'border-[#E5455F] bg-[#FEF2F2] text-[#E5455F] hover:bg-[#E5455F] hover:text-white'
                        : 'border-[#E6E9F2] bg-white text-[#596080] hover:bg-[#F3F4F6]'
                    "
                    @click.stop="openDrawer(alert)"
                  >
                    {{ alert.status === 'pending' ? '处理' : '查看' }}
                  </button>
                </td>
              </tr>

              <!-- 空状态 -->
              <tr v-if="filteredAlerts.length === 0">
                <td colspan="7" class="p-12 text-center text-[14px] text-[#B8BCCC]">
                  暂无符合条件的违规记录
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 详情抽屉 -->
    <Transition name="drawer">
      <div
        v-if="drawerVisible"
        class="fixed inset-0 z-50 flex justify-end"
      >
        <!-- 遮罩层 -->
        <div
          class="absolute inset-0 bg-black/20 backdrop-blur-[2px]"
          @click="closeDrawer"
        />

        <!-- 抽屉主体 -->
        <div
          class="relative z-10 flex w-[480px] flex-col overflow-hidden bg-white shadow-2xl"
        >
          <!-- 抽屉头部 -->
          <div
            class="flex shrink-0 items-center justify-between border-b border-[#E6E9F2] bg-[#F2F5FA] px-6 py-4"
          >
            <div class="flex items-center gap-3">
              <div
                class="flex h-10 w-10 items-center justify-center rounded-[2px]"
                :class="
                  selectedAlert?.actionType === 'intercept'
                    ? 'bg-[#FEF2F2] text-[#E5455F]'
                    : 'bg-[#EEF2FF] text-[#0A6EFD]'
                "
              >
                <AlertOctagon :size="20" />
              </div>
              <div>
                <h3 class="text-[16px] font-bold text-[#1F264D]">
                  {{ selectedAlert?.ruleName }}
                </h3>
                <p class="text-[12px] text-[#B8BCCC]">{{ selectedAlert?.id }}</p>
              </div>
            </div>
            <button
              type="button"
              class="rounded-[2px] p-2 text-[#B8BCCC] transition-colors hover:bg-[#F3F4F6] hover:text-[#1F264D]"
              @click="closeDrawer"
            >
              <X :size="18" />
            </button>
          </div>

          <!-- 抽屉内容 -->
          <div v-if="selectedAlert" class="alert-scroll flex-1 overflow-auto p-6 space-y-6">
            <!-- 基本信息 -->
            <section>
              <h4 class="mb-3 text-[13px] font-bold uppercase tracking-wider text-[#B8BCCC]">
                基本信息
              </h4>
              <div class="rounded-[2px] border border-[#E6E9F2] bg-[#F7F9FC] p-4">
                <div class="grid grid-cols-2 gap-4 text-[13px]">
                  <div>
                    <p class="text-[#B8BCCC]">报警时间</p>
                    <p class="mt-1 font-medium text-[#1F264D]">{{ selectedAlert.time }}</p>
                  </div>
                  <div>
                    <p class="text-[#B8BCCC]">要素分类</p>
                    <p class="mt-1 font-medium text-[#1F264D]">
                      {{ selectedAlert.categoryName }}
                    </p>
                  </div>
                  <div>
                    <p class="text-[#B8BCCC]">触发机构</p>
                    <p class="mt-1 font-medium text-[#1F264D]">{{ selectedAlert.hospital }}</p>
                  </div>
                  <div>
                    <p class="text-[#B8BCCC]">关联科室</p>
                    <p class="mt-1 font-medium text-[#1F264D]">{{ selectedAlert.department }}</p>
                  </div>
                  <div v-if="selectedAlert.patient !== '不适用'">
                    <p class="text-[#B8BCCC]">涉及患者</p>
                    <p class="mt-1 font-medium text-[#1F264D]">{{ selectedAlert.patient }}</p>
                  </div>
                  <div>
                    <p class="text-[#B8BCCC]">处理状态</p>
                    <p class="mt-1">
                      <span
                        class="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-[12px] font-bold"
                        :class="
                          selectedAlert.status === 'pending'
                            ? 'bg-[#FEF2F2] text-[#E5455F]'
                            : 'bg-[#F0FDF4] text-[#12B881]'
                        "
                      >
                        {{ selectedAlert.status === 'pending' ? '待处理' : '已处理' }}
                      </span>
                    </p>
                  </div>
                </div>
              </div>
            </section>

            <!-- 违规描述 -->
            <section>
              <h4 class="mb-3 text-[13px] font-bold uppercase tracking-wider text-[#B8BCCC]">
                违规描述
              </h4>
              <div
                class="rounded-[2px] border p-4 text-[13px] leading-relaxed"
                :class="
                  selectedAlert.actionType === 'intercept'
                    ? 'border-[#E5455F] bg-[#FEF2F2]/40 text-[#991B1B]'
                    : 'border-[#BFDBFE] bg-[#EFF6FF]/40 text-[#1E40AF]'
                "
              >
                {{ selectedAlert.detailMsg }}
              </div>
            </section>

            <!-- 证据明细 -->
            <section>
              <h4 class="mb-3 text-[13px] font-bold uppercase tracking-wider text-[#B8BCCC]">
                证据明细
              </h4>
              <div class="rounded-[2px] border border-[#E6E9F2] p-4">
                <dl class="space-y-3 text-[13px]">
                  <template v-for="(val, key) in selectedAlert.evidence" :key="key">
                    <div class="flex gap-2">
                      <dt class="w-[120px] shrink-0 text-[#B8BCCC]">
                        {{ evidenceLabels[key] || key }}
                      </dt>
                      <dd class="flex-1 font-medium text-[#1F264D]">{{ val }}</dd>
                    </div>
                  </template>
                </dl>
              </div>
            </section>

            <!-- 操作区 -->
            <section v-if="selectedAlert.status === 'pending'">
              <h4 class="mb-3 text-[13px] font-bold uppercase tracking-wider text-[#B8BCCC]">
                监管处置
              </h4>
              <div class="space-y-3">
                <textarea
                  v-model="disposeNote"
                  rows="3"
                  placeholder="输入处置备注..."
                  class="box-border h-[80px] w-full resize-none rounded-[2px] border border-[#E6E9F2] bg-white p-3 text-[13px] text-[#1F264D] outline-none transition focus:border-[#0A6EFD] focus:ring-2 focus:ring-[#0A6EFD]/20 placeholder:text-[#B8BCCC]"
                />
                <div class="flex gap-3">
                  <button
                    type="button"
                    class="box-border flex h-[32px] flex-1 items-center justify-center gap-2 rounded-[2px] bg-[#12B881] px-4 py-2.5 text-[14px] font-bold text-white shadow-sm transition-colors hover:bg-[#0F9D6E]"
                  >
                    <CheckCircle2 :size="16" />
                    标记已处理
                  </button>
                  <button
                    type="button"
                    class="box-border flex h-[32px] flex-1 items-center justify-center gap-2 rounded-[2px] border border-[#E6E9F2] bg-white px-4 py-2.5 text-[14px] font-bold text-[#1F264D] shadow-sm transition-colors hover:bg-[#F3F4F6]"
                  >
                    <Send :size="16" />
                    移交上级
                  </button>
                </div>
              </div>
            </section>

            <!-- 已处理时的备注展示 -->
            <section v-else>
              <h4 class="mb-3 text-[13px] font-bold uppercase tracking-wider text-[#B8BCCC]">
                处置记录
              </h4>
              <div class="rounded-[2px] border border-[#97DEC6] bg-[#ECFDF5] p-4">
                <p class="text-[13px] text-[#065F46]">
                  该记录已于 {{ selectedAlert.time.split(' ')[0] }} 由系统审核员处理完成。
                </p>
              </div>
            </section>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  Activity,
  AlertOctagon,
  CheckCircle2,
  Filter,
  Search,
  Send,
  ShieldAlert,
  Stethoscope,
  X,
  Building2,
} from 'lucide-vue-next'

// ---------------------------------------------------------------------------
// 规则分类映射表
// ---------------------------------------------------------------------------
type RuleItem = { id: string; name: string }

const ruleCategories: Record<string, RuleItem[]> = {
  all: [{ id: 'all', name: '所有具体规则' }],
  personnel: [
    { id: 'all', name: '所有人员要素规则' },
    { id: '1', name: '1. 越权开具抗菌药物' },
    { id: '2', name: '2. 短时多机构接诊' },
    { id: '3', name: '3. 公立/民营多点执业冲突' },
  ],
  institution: [
    { id: 'all', name: '所有机构要素规则' },
    { id: '1', name: '1. 超科目范围诊疗' },
    { id: '2', name: '2. 超面积/床位收治上限' },
  ],
  technical: [
    { id: 'all', name: '所有技术要素规则' },
    { id: '1', name: '1. 超范围开展限制类技术' },
    { id: '2', name: '2. 麻精药品异常开具' },
  ],
  equipment: [
    { id: 'all', name: '所有设备要素规则' },
    { id: '1', name: '1. 手术分级与设备资质不符' },
  ],
}

// ---------------------------------------------------------------------------
// 证据字段中文映射
// ---------------------------------------------------------------------------
const evidenceLabels: Record<string, string> = {
  orderId: '医嘱编号',
  drugName: '药品名称',
  drugClass: '药品分级',
  doctorTitle: '医师职称',
  requiredTitle: '所需职称',
  record1: '记录①',
  record2: '记录②',
  timeDiff: '时间间隔',
  distance: '机构间距',
  patientName: '患者姓名',
  publicRecord: '公立记录',
  privateRecord: '民营记录',
  attendingDoctor: '主诊医师',
  recordId: '病历编号',
  diagnosis: '诊断内容',
  registeredSubjects: '登记科目',
  conflictSubject: '冲突科目',
  registeredArea: '登记面积',
  approvedBeds: '核定床位',
  maxLimit: '最高收治',
  currentInpatients: '当前在院',
  actionTaken: '系统动作',
  technologyName: '技术名称',
  techLevel: '技术等级',
  institutionRecord: '机构备案',
  doctorRecord: '医师资质',
  patientType: '患者类型',
  prescribedDays: '开具天数',
  limitDays: '规定上限',
  surgeryName: '手术名称',
  surgeryLevel: '手术等级',
  missingEquipment: '缺失设备',
  currentEquipment: '现有设备',
}

// ---------------------------------------------------------------------------
// 模拟数据
// ---------------------------------------------------------------------------
type AlertStatus = 'pending' | 'processed'
type ActionType = 'alert' | 'intercept'
type CategoryId = 'personnel' | 'institution' | 'technical' | 'equipment'

interface Alert {
  id: string
  time: string
  categoryId: CategoryId
  categoryName: string
  ruleId: string
  ruleName: string
  actionType: ActionType
  status: AlertStatus
  hospital: string
  department: string
  doctor: string
  patient: string
  detailMsg: string
  evidence: Record<string, string>
}

const allAlerts = ref<Alert[]>([
  {
    id: 'AL-20260331-001',
    time: '2026-03-31 09:15:22',
    categoryId: 'personnel',
    categoryName: '人员要素',
    ruleId: '1',
    ruleName: '越权开具抗菌药物',
    actionType: 'alert',
    status: 'pending',
    hospital: '市第一人民医院',
    department: '呼吸内科',
    doctor: '张医生 (住院医师)',
    patient: '李四 (男 45岁)',
    detailMsg:
      '触发自动报警：该医生开具特殊级抗菌药物【美罗培南】，其当前职称（住院医师）无该权限。',
    evidence: {
      orderId: 'ORD-882910',
      drugName: '注射用美罗培南 (1.0g)',
      drugClass: '特殊使用级',
      doctorTitle: '住院医师',
      requiredTitle: '副主任医师及以上',
    },
  },
  {
    id: 'AL-20260330-042',
    time: '2026-03-30 14:20:15',
    categoryId: 'personnel',
    categoryName: '人员要素',
    ruleId: '2',
    ruleName: '短时多机构接诊',
    actionType: 'alert',
    status: 'pending',
    hospital: '市第二医院 / 阳光民营医院',
    department: '内科',
    doctor: '陈医生',
    patient: '不适用',
    detailMsg:
      '触发自动报警：该医师30分钟内先后在市第二医院和阳光民营医院产生多笔诊疗记录。',
    evidence: {
      record1: '14:05 - 市第二医院门诊接诊记录',
      record2: '14:20 - 阳光民营医院电子处方记录',
      timeDiff: '15分钟',
      distance: '约12公里',
    },
  },
  {
    id: 'AL-20260331-003',
    time: '2026-03-31 10:45:00',
    categoryId: 'personnel',
    categoryName: '人员要素',
    ruleId: '3',
    ruleName: '公立/民营多点执业冲突',
    actionType: 'alert',
    status: 'pending',
    hospital: '市中医院 / 仁爱民营诊所',
    department: '中医科',
    doctor: '林大夫',
    patient: '王五 (男 30岁)',
    detailMsg:
      '触发自动报警：同一患者先后在公立医院和民营诊所就诊，且由同一位医生开具处方，存在违规引导患者去民营机构消费/套保嫌疑。',
    evidence: {
      patientName: '王五 (医保卡尾号 8821)',
      publicRecord: '09:00 - 市中医院门诊挂号',
      privateRecord: '10:30 - 仁爱民营诊所中药处方',
      attendingDoctor: '林大夫 (主执业机构:市中医院)',
    },
  },
  {
    id: 'AL-20260330-056',
    time: '2026-03-30 16:30:00',
    categoryId: 'institution',
    categoryName: '机构要素',
    ruleId: '1',
    ruleName: '超科目范围诊疗',
    actionType: 'alert',
    status: 'processed',
    hospital: '康复专科门诊部',
    department: '全科',
    doctor: '李医生',
    patient: '周七 (女 28岁)',
    detailMsg:
      '触发自动报警：产生【妇产科】相关诊断记录，该机构未登记妇产科诊疗科目资质。',
    evidence: {
      recordId: 'REC-9921',
      diagnosis: '妊娠期糖尿病 (O24.4)',
      registeredSubjects: '内科, 康复医学科',
      conflictSubject: '妇产科',
    },
  },
  {
    id: 'AL-20260331-004',
    time: '2026-03-31 08:12:30',
    categoryId: 'institution',
    categoryName: '机构要素',
    ruleId: '2',
    ruleName: '超面积/床位收治上限',
    actionType: 'intercept',
    status: 'pending',
    hospital: '安康老年护理院',
    department: '住院部',
    doctor: '系统自动拦截',
    patient: '孙大爷 (男 78岁)',
    detailMsg:
      '触发自动拦截：该机构当前在院患者人数已超过系统根据其营业面积和核定床位数计算的最高收治上限，已自动通报医保拒绝结算。',
    evidence: {
      registeredArea: '1200 平方米',
      approvedBeds: '50 张',
      maxLimit: '55 人 (含加床浮动)',
      currentInpatients: '56 人 (超限 1 人)',
      actionTaken: '已阻断本次入院医保登记',
    },
  },
  {
    id: 'AL-20260331-005',
    time: '2026-03-31 11:05:15',
    categoryId: 'technical',
    categoryName: '技术要素',
    ruleId: '1',
    ruleName: '超范围开展限制类技术',
    actionType: 'alert',
    status: 'pending',
    hospital: '远大医疗美容医院',
    department: '美容外科',
    doctor: '高医生',
    patient: '赵女士 (女 35岁)',
    detailMsg:
      '触发自动报警：试图开展国家限制类技术，系统校验"限制类技术备案记录"发现机构与医师均无相关备案资质。',
    evidence: {
      technologyName: '全身麻醉下巨乳缩小术',
      techLevel: '国家级限制类技术',
      institutionRecord: '无该项技术机构备案',
      doctorRecord: '无限制类技术主刀资质',
    },
  },
  {
    id: 'AL-20260331-002',
    time: '2026-03-31 08:45:10',
    categoryId: 'technical',
    categoryName: '技术要素',
    ruleId: '2',
    ruleName: '麻精药品异常开具',
    actionType: 'alert',
    status: 'processed',
    hospital: '区中心医院',
    department: '疼痛科',
    doctor: '王主任',
    patient: '赵六 (女 62岁)',
    detailMsg: '触发自动报警：为门诊普通患者开具控缓释制剂超过7天规定用量。',
    evidence: {
      orderId: 'ORD-882905',
      drugName: '盐酸羟考酮缓释片',
      patientType: '门诊普通患者',
      prescribedDays: '14天',
      limitDays: '7天',
    },
  },
  {
    id: 'AL-20260329-088',
    time: '2026-03-29 10:05:00',
    categoryId: 'equipment',
    categoryName: '设备要素',
    ruleId: '1',
    ruleName: '手术分级与设备资质不符',
    actionType: 'alert',
    status: 'processed',
    hospital: '县人民医院',
    department: '普外科',
    doctor: '刘主任',
    patient: '吴八 (男 55岁)',
    detailMsg:
      '触发自动报警：拟开展四级手术，但当前手术室设备配置未达到相应技术需求标准。',
    evidence: {
      surgeryName: '腹腔镜下胰十二指肠切除术',
      surgeryLevel: '四级手术',
      missingEquipment: '高清3D腹腔镜系统、术中超声',
      currentEquipment: '基础腹腔镜系统',
    },
  },
])

// ---------------------------------------------------------------------------
// 筛选状态
// ---------------------------------------------------------------------------
const filterStatus = ref<string>('all')
const filterCategory = ref<string>('all')
const filterRule = ref<string>('all')
const keyword = ref('')

// ---------------------------------------------------------------------------
// 状态标签配置（规范色值）
// ---------------------------------------------------------------------------
const STATUS_TABS = [
  {
    value: 'all',
    label: '全部',
    activeClass: 'bg-white shadow-sm text-[#1F264D] border border-[#E6E9F2]',
  },
  {
    value: 'pending',
    label: '待处理',
    activeClass:
      'bg-white shadow-sm text-[#E5455F] border border-[#E5455F]',
  },
  {
    value: 'processed',
    label: '已处理',
    activeClass: 'bg-white shadow-sm text-[#12B881] border border-[#97DEC6]',
  },
]

// ---------------------------------------------------------------------------
// 过滤后数据
// ---------------------------------------------------------------------------
const filteredAlerts = computed(() => {
  return allAlerts.value.filter((a) => {
    const matchStatus =
      filterStatus.value === 'all' || a.status === filterStatus.value
    const matchCategory =
      filterCategory.value === 'all' || a.categoryId === filterCategory.value
    const matchRule =
      filterRule.value === 'all' || a.ruleId === filterRule.value
    const q = keyword.value.trim().toLowerCase()
    const matchKeyword =
      !q ||
      a.hospital.toLowerCase().includes(q) ||
      a.department.toLowerCase().includes(q) ||
      a.doctor.toLowerCase().includes(q) ||
      a.patient.toLowerCase().includes(q)
    return matchStatus && matchCategory && matchRule && matchKeyword
  })
})

// ---------------------------------------------------------------------------
// KPI 摘要（规范色值）
// ---------------------------------------------------------------------------
const kpiSummary = computed(() => {
  const total = allAlerts.value.length
  const pending = allAlerts.value.filter((a) => a.status === 'pending').length
  const processed = allAlerts.value.filter((a) => a.status === 'processed').length
  const intercept = allAlerts.value.filter((a) => a.actionType === 'intercept').length
  return [
    { label: '违规总数', value: total, valueClass: 'text-[#1F264D]' },
    { label: '待处理', value: pending, valueClass: 'text-[#E5455F]' },
    { label: '已处理', value: processed, valueClass: 'text-[#12B881]' },
    { label: '已拦截', value: intercept, valueClass: 'text-[#F58718]' },
  ]
})

// ---------------------------------------------------------------------------
// 分类标签样式（规范色值）
// ---------------------------------------------------------------------------
function categoryTagClass(cat: CategoryId): string {
  const map: Record<CategoryId, string> = {
    personnel: 'border-[#BFDBFE] bg-[#EFF6FF] text-[#0A6EFD]',
    institution: 'border-[#FED7AA] bg-[#FFF7ED] text-[#C2410C]',
    technical: 'border-[#FCA5A5] bg-[#FEF2F2] text-[#DC2626]',
    equipment: 'border-[#97DEC6] bg-[#ECFDF5] text-[#065F46]',
  }
  return map[cat] || 'border-[#E6E9F2] bg-[#F7F9FC] text-[#596080]'
}

// ---------------------------------------------------------------------------
// 抽屉
// ---------------------------------------------------------------------------
const drawerVisible = ref(false)
const selectedAlert = ref<Alert | null>(null)
const disposeNote = ref('')

function openDrawer(alert: Alert) {
  selectedAlert.value = alert
  disposeNote.value = ''
  drawerVisible.value = true
}

function closeDrawer() {
  drawerVisible.value = false
  setTimeout(() => {
    selectedAlert.value = null
  }, 300)
}
</script>

<style scoped>
/* 滚动条 */
.alert-scroll::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.alert-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.alert-scroll::-webkit-scrollbar-thumb {
  background: #D7D9E5;
  border-radius: 10px;
}
.alert-scroll::-webkit-scrollbar-thumb:hover {
  background: #B8BCCC;
}

/* 页面淡入 */
.animate-fade-in {
  animation: fadeIn 0.4s ease-out forwards;
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

/* 抽屉过渡动画 */
.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.25s ease;
}
.drawer-enter-active .relative.z-10,
.drawer-leave-active .relative.z-10 {
  transition: transform 0.25s ease;
}
.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}
.drawer-enter-from .relative.z-10,
.drawer-leave-to .relative.z-10 {
  transform: translateX(100%);
}
</style>
