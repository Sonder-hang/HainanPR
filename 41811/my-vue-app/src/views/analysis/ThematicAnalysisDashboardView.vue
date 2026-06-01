<template>
  <div class="h-full flex flex-col overflow-hidden">
    <!-- 顶部筛选栏 -->
    <div class="shrink-0 border-b border-gray-200 bg-white px-6 py-3">
      <div class="flex items-center space-x-3 flex-wrap gap-y-2">
        <!-- 日期筛选 -->
        <div class="flex items-center bg-gray-50 border border-gray-300 rounded-md overflow-hidden shadow-sm h-8 hover:border-blue-400 transition-colors">
          <div class="px-2.5 border-r border-gray-300 text-gray-500 flex items-center h-full">
            <Calendar class="w-3.5 h-3.5" />
          </div>
          <select
            v-model="filterDate"
            class="px-2 py-1 text-sm font-medium text-gray-700 bg-transparent focus:outline-none cursor-pointer min-w-[140px]"
          >
            <option value="2026-Q1">2026年 第一季度</option>
            <option value="last-year">2025年 完整财年</option>
          </select>
        </div>

        <!-- 机构筛选 -->
        <div class="flex items-center bg-gray-50 border border-gray-300 rounded-md overflow-hidden shadow-sm h-8 hover:border-blue-400 transition-colors">
          <div class="px-2.5 border-r border-gray-300 text-gray-500 flex items-center h-full">
            <Building class="w-3.5 h-3.5" />
          </div>
          <select
            v-model="filterHospital"
            class="px-2 py-1 text-sm font-medium text-gray-700 bg-transparent focus:outline-none cursor-pointer min-w-[150px]"
          >
            <option value="all">全市所有医疗机构</option>
            <option value="市一院">市第一人民医院</option>
          </select>
        </div>

        <div class="h-4 w-px bg-gray-300 mx-2"></div>

        <!-- 分析要素选择 -->
        <div class="flex items-center bg-white border border-gray-300 rounded-md overflow-hidden shadow-sm h-8">
          <select
            v-model="filterCategory"
            class="px-3 py-1 text-sm font-bold text-blue-700 bg-blue-50 focus:outline-none cursor-pointer min-w-[130px]"
          >
            <option value="all">请选择分析要素</option>
            <option value="technical">技术要素专题</option>
            <option value="equipment">设备要素专题</option>
          </select>
        </div>

        <!-- 具体专题选择 -->
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
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="flex-1 overflow-y-auto p-6 bg-slate-50">
      <div class="max-w-[1400px] mx-auto">
        <!-- 标准化渲染器 -->
        <div v-if="filterRule !== 'all'" class="space-y-6 animate-fade-in">
          <!-- 第一段：四大 KPI 卡片 -->
          <div class="grid grid-cols-4 gap-4">
            <div
              v-for="(kpi, idx) in currentReport?.kpis"
              :key="idx"
              :class="[
                'bg-white p-5 rounded-xl border shadow-sm flex flex-col relative overflow-hidden',
                getStatusColor(kpi.status)
              ]"
            >
              <!-- 装饰侧边条 -->
              <div :class="['absolute left-0 top-0 bottom-0 w-1', getStatusBgClass(kpi.status)]"></div>
              <span class="text-gray-500 text-sm font-bold mb-2 z-10">{{ kpi.label }}</span>
              <div class="flex items-baseline space-x-1 z-10">
                <span :class="['text-3xl font-black', getTextColor(kpi.status)]">{{ kpi.val }}</span>
                <span class="text-sm font-bold text-gray-400 mb-1">{{ kpi.unit }}</span>
              </div>
              <div
                class="mt-2 text-xs font-bold text-gray-500 bg-gray-50 inline-block px-2 py-1 rounded w-max border border-gray-100 z-10"
              >
                {{ kpi.desc }}
              </div>
            </div>
          </div>

          <!-- 第二段：两个维度的汇总表格 -->
          <div class="grid grid-cols-2 gap-6 h-72">
            <!-- 维度表 1 -->
            <div class="bg-white rounded-xl border border-gray-200 shadow-sm flex flex-col">
              <div class="p-4 border-b border-gray-100 bg-gray-50/50 rounded-t-xl">
                <h3 class="text-sm font-bold text-gray-800 flex items-center">
                  <component :is="currentReport?.dim1?.icon" class="w-4 h-4 mr-2 text-blue-500" />
                  {{ currentReport?.dim1?.title }}
                </h3>
              </div>
              <div class="flex-1 overflow-auto p-4">
                <table class="w-full text-left text-sm whitespace-nowrap">
                  <thead class="text-gray-500 font-bold border-b border-gray-200">
                    <tr>
                      <th v-for="(h, i) in currentReport?.dim1?.headers" :key="i" class="pb-2">{{ h }}</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-100">
                    <tr v-for="(row, i) in currentReport?.dim1?.data" :key="i" class="hover:bg-gray-50">
                      <td
                        v-for="(cell, j) in row"
                        :key="j"
                        :class="[
                          'py-3',
                          j === 0 ? 'font-bold text-gray-400' : j === 1 ? 'font-bold text-gray-800' : 'text-gray-600'
                        ]"
                      >
                        {{ cell }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 维度表 2 -->
            <div class="bg-white rounded-xl border border-gray-200 shadow-sm flex flex-col">
              <div class="p-4 border-b border-gray-100 bg-gray-50/50 rounded-t-xl">
                <h3 class="text-sm font-bold text-gray-800 flex items-center">
                  <component :is="currentReport?.dim2?.icon" class="w-4 h-4 mr-2 text-orange-500" />
                  {{ currentReport?.dim2?.title }}
                </h3>
              </div>
              <div class="flex-1 overflow-auto p-4">
                <table class="w-full text-left text-sm whitespace-nowrap">
                  <thead class="text-gray-500 font-bold border-b border-gray-200">
                    <tr>
                      <th v-for="(h, i) in currentReport?.dim2?.headers" :key="i" class="pb-2">{{ h }}</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-100">
                    <tr v-for="(row, i) in currentReport?.dim2?.data" :key="i" class="hover:bg-gray-50">
                      <td
                        v-for="(cell, j) in row"
                        :key="j"
                        :class="['py-3', j === 0 ? 'font-bold text-gray-800' : 'text-gray-600']"
                      >
                        {{ cell }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- 第三段：底层溯源大表 -->
          <div class="bg-white rounded-xl border border-gray-200 shadow-sm flex flex-col">
            <div class="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50 rounded-t-xl">
              <h3 class="text-sm font-bold text-gray-800 flex items-center">
                <Database class="w-4 h-4 mr-2 text-blue-500" />
                {{ currentReport?.detail?.title }}
              </h3>
              <button
                class="text-xs text-blue-600 font-bold hover:underline flex items-center bg-white border border-gray-300 px-3 py-1.5 rounded shadow-sm"
              >
                <Download class="w-3 h-3 mr-1" />
                导出当前清查明细
              </button>
            </div>
            <div class="overflow-auto p-4">
              <table class="w-full text-left text-sm whitespace-nowrap border border-gray-200 rounded-lg">
                <thead class="bg-gray-100 text-gray-700 font-bold sticky top-0">
                  <tr>
                    <th
                      v-for="(h, i) in currentReport?.detail?.headers"
                      :key="i"
                      class="px-4 py-3 border-b border-gray-200"
                    >
                      {{ h }}
                    </th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  <tr v-for="(row, i) in currentReport?.detail?.data" :key="i" class="hover:bg-blue-50/50">
                    <td
                      v-for="(cell, j) in row"
                      :key="j"
                      :class="['px-4 py-3', j === 0 ? 'font-bold text-gray-900' : 'text-gray-600']"
                    >
                      {{ cell }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div
          v-else
          class="h-[400px] flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-xl bg-gray-50 text-gray-400"
        >
          <FileText class="w-16 h-16 mb-4 opacity-40 text-blue-500" />
          <p class="font-bold text-xl text-gray-600 mb-2">标准化 BI 分析框架已就绪</p>
          <p class="text-sm mt-2 font-medium">请在顶部下拉框中选择具体的【分析要素】与【规则专题】。</p>
          <div class="mt-6 flex space-x-4 text-xs text-gray-400 bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div class="flex flex-col items-center">
              <div class="bg-blue-100 text-blue-600 p-2 rounded mb-1">
                <BarChart2 class="w-4 h-4" />
              </div>
              统一的 KPI 卡片
            </div>
            <div class="w-px bg-gray-200"></div>
            <div class="flex flex-col items-center">
              <div class="bg-orange-100 text-orange-600 p-2 rounded mb-1">
                <Users class="w-4 h-4" />
              </div>
              双维度排名表格
            </div>
            <div class="w-px bg-gray-200"></div>
            <div class="flex flex-col items-center">
              <div class="bg-green-100 text-green-600 p-2 rounded mb-1">
                <Database class="w-4 h-4" />
              </div>
              底层证据链追溯
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
  BarChart2,
  Calendar,
  Download,
  FileText,
  Layers,
  Users,
  Target,
  Stethoscope,
  Database,
  Building,
  AlertTriangle,
} from 'lucide-vue-next'

// 专题大屏分类映射表
const ruleCategories: Record<string, Array<{ id: string; name: string }>> = {
  all: [{ id: 'all', name: '请先选择监管要素' }],
  technical: [
    { id: 'all', name: '所有技术要素专题' },
    { id: 'tc-1', name: '1. 患者流向监测 ' },
    { id: 'tc-2', name: '2. 限制类技术四维分析 ' },
    { id: 'tc-3', name: '3. 无靶点检测开药核查 ' },
    { id: 'tc-4', name: '4. 肿瘤TNM分期率统计 ' },
  ],
  equipment: [{ id: 'all', name: '所有设备要素专题' }, { id: 'eq-1', name: '1. 大型设备服务效能分析 ' }],
}

// 标准化 BI 报告数据源
const reportDataStore: Record<string, any> = {
  'tc-1': {
    title: '患者流向与倒卖利益输送监测报告',
    kpis: [
      { label: '公立机构流失总人次', val: '1,284', unit: '人次', status: 'danger', desc: '同比上涨 12.5%' },
      { label: '高危流向民营占比', val: '68.2%', unit: '', status: 'warning', desc: '集中度极高' },
      { label: '疑似"倒卖"医师', val: '14', unit: '人', status: 'danger', desc: '高频流转源头' },
      { label: '洞察结论', val: '重点排查', unit: '', status: 'info', desc: '市一院心内科存在异常利益输送嫌疑' },
    ],
    dim1: {
      title: '主要流出方分布 (公立)',
      icon: Users,
      headers: ['排名', '流出机构', '重点科室', '流失人次'],
      data: [
        ['1', '市第一人民医院', '心内科', '450'],
        ['2', '市中医院', '骨科', '320'],
        ['3', '区中心医院', '全科', '210'],
        ['4', '市妇幼保健院', '妇科', '180'],
      ],
    },
    dim2: {
      title: '主要流入方分布 (民营)',
      icon: Building,
      headers: ['排名', '流入机构', '收治专长', '流入人次'],
      data: [
        ['1', '阳光康复医院', '心脑血管康复', '380'],
        ['2', '仁爱骨科专科', '骨外科', '290'],
        ['3', '慈铭体检中心', '综合体检', '150'],
        ['4', '瑞丽医疗美容', '医美整形', '110'],
      ],
    },
    detail: {
      title: '底层流水清查表 (间隔 < 7天)',
      headers: ['患者姓名', '首诊机构/医师 (流出方)', '复诊机构 (流入方)', '间隔时长', '诊断相关性', '民营产生费用'],
      data: [
        ['张*三', '市一院 / 王建国(心内)', '阳光康复医院', '2天', '高度一致(冠心病)', '¥4,500'],
        ['李*华', '市中院 / 刘海(骨科)', '仁爱骨科专科', '1天', '一致(骨折术后)', '¥2,800'],
        ['王*芳', '市妇幼 / 陈丽(妇科)', '康美妇产医院', '3天', '中度相关', '¥1,200'],
        ['赵*伟', '区中心 / 张伟(内科)', '慈铭体检中心', '5天', '弱相关(要求体检)', '¥3,500'],
      ],
    },
  },
  'tc-2': {
    title: '限制类技术四维合规性审查报告',
    kpis: [
      { label: '限制技术开展总例数', val: '8,421', unit: '例', status: 'info', desc: '本期统算总量' },
      { label: '机构越权异常率', val: '2.4%', unit: '', status: 'danger', desc: '未备案机构强行开展' },
      { label: '医师越权异常率', val: '5.1%', unit: '', status: 'danger', desc: '主刀医师无操作资质' },
      { label: '转归不良率预警', val: '0.8%', unit: '', status: 'warning', desc: '术后并发症或二次入院' },
    ],
    dim1: {
      title: '高发违规技术排名',
      icon: Stethoscope,
      headers: ['排名', '限制类技术名称', '管理级别', '违规检出数'],
      data: [
        ['1', '全身麻醉下巨乳缩小术', '国家级', '45'],
        ['2', '体外受精-胚胎移植技术', '省级', '32'],
        ['3', '同种异体肾移植术', '国家级', '12'],
        ['4', '放射性粒子植入治疗技术', '省级', '8'],
      ],
    },
    dim2: {
      title: '四维异常原因分布',
      icon: AlertTriangle,
      headers: ['核查维度', '异常原因说明', '涉及机构数', '违规人次'],
      data: [
        ['医师权限', '主刀医师未在备案名单内', '12家', '429人次'],
        ['机构权限', '机构诊疗科目或技术未备案', '5家', '201人次'],
        ['患者转归', '出院后15天内因并发症再入院', '8家', '67人次'],
        ['培训质量', '系统登记的培训证书已过期', '24家', '18人次'],
      ],
    },
    detail: {
      title: '四维核查异常穿透台账',
      headers: ['发生机构', '技术名称', '主刀医师', '核查维控结果', '发生日期', '状态'],
      data: [
        ['远大医疗美容', '全身麻醉下巨乳缩小术', '高强 (主治)', '机构越权 + 医师越权', '2026-03-25', '待查处'],
        ['市中心医院', '同种异体肾移植术', '李军 (主任)', '转归异常 (排异感染)', '2026-03-20', '重点关注'],
        ['区人民医院', '体外受精-胚胎移植技术', '张萍 (副主任)', '培训记录过期', '2026-03-18', '发函警告'],
        ['星健骨科医院', '人工髋关节置换术', '刘洋 (副主任)', '机构未备案该项技术', '2026-03-15', '待查处'],
      ],
    },
  },
  'tc-3': {
    title: '无靶点检测滥用抗肿瘤靶向药审查报告',
    kpis: [
      { label: '靶向药处方总量', val: '12,450', unit: '笔', status: 'info', desc: '监测范围内门诊/住院' },
      { label: '无基因记录违规处方', val: '128', unit: '笔', status: 'danger', desc: '未见病理靶点支撑' },
      { label: '违规开药检出率', val: '1.0%', unit: '', status: 'warning', desc: '高于往期平均值' },
      { label: '预估违规医保拒付', val: '145.2', unit: '万元', status: 'danger', desc: '亟需追回资金' },
    ],
    dim1: {
      title: '违规靶向药品种排名',
      icon: Activity,
      headers: ['排名', '药品通用名', '核心限制靶点', '违规笔数'],
      data: [
        ['1', '吉非替尼片', 'EGFR 突变阳性', '45笔'],
        ['2', '曲妥珠单抗', 'HER2 阳性', '38笔'],
        ['3', '奥希替尼', 'EGFR T790M 突变', '25笔'],
        ['4', '克唑替尼', 'ALK 融合基因', '20笔'],
      ],
    },
    dim2: {
      title: '违规处方来源科室分布',
      icon: Building,
      headers: ['排名', '重点科室', '涉及机构数量', '违规笔数'],
      data: [
        ['1', '肿瘤内科', '8家', '65笔'],
        ['2', '呼吸内科', '6家', '32笔'],
        ['3', '胸外科', '5家', '18笔'],
        ['4', '乳腺外科', '4家', '13笔'],
      ],
    },
    detail: {
      title: '无靶点检测开药核查明细 (基因匹配失败流水)',
      headers: ['开具药品', '患者姓名', '开具机构与科室', '责任医师', '系统核查结论', '涉及金额'],
      data: [
        ['吉非替尼片', '赵*刚', '市第一医院 / 肿瘤内科', '李主任', '未查询到 EGFR 突变阳性记录', '¥3,500'],
        ['曲妥珠单抗', '孙*梅', '市中医院 / 乳腺外科', '张医师', '未查询到 HER2 阳性病理依据', '¥8,200'],
        ['奥希替尼', '吴*强', '区中心医院 / 呼吸科', '王主任', '未查询到 EGFR T790M 突变记录', '¥15,000'],
        ['克唑替尼', '郑*华', '市肿瘤医院 / 胸外科', '陈医师', '未查询到 ALK 融合报告', '¥12,800'],
      ],
    },
  },
  'tc-4': {
    title: '肿瘤患者治疗前 TNM 分期率考核报告',
    kpis: [
      { label: '新发肿瘤就诊人次', val: '1,431', unit: '人', status: 'info', desc: '本期首次确诊' },
      { label: '有TNM分期记录数', val: '1,036', unit: '人', status: 'info', desc: '病案首页有记录' },
      { label: '全市整体分期率', val: '72.4%', unit: '', status: 'danger', desc: '低于卫健委 80% 要求' },
      { label: '严重不达标机构数', val: '2', unit: '家', status: 'danger', desc: '分期率低于 60%' },
    ],
    dim1: {
      title: '各机构 TNM 分期率考核红黑榜',
      icon: Building,
      headers: ['机构名称', '新发病例', '完成评估', '分期率 (考核)'],
      data: [
        ['市肿瘤医院', '890例', '854例', '95.9% (达标)'],
        ['市第一医院', '320例', '285例', '89.0% (达标)'],
        ['区人民医院', '76例', '41例', '53.9% (未达标)'],
        ['市第二医院', '145例', '62例', '42.7% (未达标)'],
      ],
    },
    dim2: {
      title: '易漏评肿瘤病种分布',
      icon: Target,
      headers: ['病种分类', 'ICD-10', '漏评例数', '病种分期率'],
      data: [
        ['肺恶性肿瘤', 'C34.x', '145例', '68%'],
        ['胃恶性肿瘤', 'C16.x', '98例', '71%'],
        ['结肠恶性肿瘤', 'C18.x', '65例', '75%'],
        ['乳房恶性肿瘤', 'C50.x', '42例', '82%'],
      ],
    },
    detail: {
      title: '底层病案首页 TNM 缺失患者清单 (抽查督办用)',
      headers: ['患者姓名', '收治机构', '主治医师', '主要诊断 (ICD-10)', '入院时间', '系统标记'],
      data: [
        ['李*国', '市第二医院', '赵强', '支气管恶性肿瘤 (C34.900)', '2026-03-25', '首次放化疗前无TNM记录'],
        ['王*芳', '市第二医院', '陈斌', '胃底恶性肿瘤 (C16.100)', '2026-03-22', '首次手术前无TNM记录'],
        ['周*明', '区人民医院', '刘华', '结肠恶性肿瘤 (C18.900)', '2026-03-18', '病案首页缺失分期字段'],
        ['吴*萍', '区人民医院', '孙丽', '乳房下内恶性肿瘤 (C50.300)', '2026-03-10', '无临床分期评估单'],
      ],
    },
  },
  'eq-1': {
    title: '大型医疗设备配置与服务效能清查报告',
    kpis: [
      { label: '入网大型设备总数', val: '214', unit: '台', status: 'info', desc: '包含 CT/MRI/PET' },
      { label: '年均服务患者数', val: '8,520', unit: '人次', status: 'info', desc: '台均负荷参考' },
      { label: '效能低下闲置设备', val: '12', unit: '台', status: 'warning', desc: '低于均值 50%' },
      { label: '严重超负荷设备', val: '3', unit: '台', status: 'danger', desc: '存在造假/强制检查嫌疑' },
    ],
    dim1: {
      title: '设备效能红黑榜 (按单台日均检查量)',
      icon: Layers,
      headers: ['排名', '所属机构', '设备名称', '日均检查量'],
      data: [
        ['超载 1', '市一院', 'GE 64排CT', '210 人次 (异常偏高)'],
        ['超载 2', '市中院', '联影 3.0T MRI', '185 人次 (偏高)'],
        ['闲置 1', '慈铭体检', '西门子 PET-CT', '5 人次 (资源浪费)'],
        ['闲置 2', '城南中心', '国产 16排CT', '8 人次 (资源浪费)'],
      ],
    },
    dim2: {
      title: '全网大型设备类别分布',
      icon: Database,
      headers: ['设备类别', '配置总台数', '全网总检查量', '平均产能利用率'],
      data: [
        ['CT 机', '125 台', '1,050,000 人次', '85% (正常)'],
        ['核磁共振 (MRI)', '65 台', '420,000 人次', '92% (偏高)'],
        ['PET-CT', '12 台', '15,000 人次', '35% (偏低)'],
        ['直线加速器', '12 台', '28,000 人次', '75% (正常)'],
      ],
    },
    detail: {
      title: '疑似异常设备重点监测台账 (超负荷/闲置)',
      headers: ['机构名称', '配置科室', '设备名称/型号', '本期累计产生报告数', '单台核定负荷', '系统预警判定'],
      data: [
        ['市第一医院', '放射科', 'GE 64排螺旋CT (设备编号A01)', '14,500 份', '约 8,000 份', '严重超负荷 (查滥用)'],
        ['市中医院', '影像中心', '联影 3.0T MRI (设备编号B02)', '9,200 份', '约 6,500 份', '负荷偏高'],
        ['慈铭体检中心', '特检部', '西门子 PET-CT (设备编号C01)', '320 份', '约 3,000 份', '严重闲置 (查违规配置)'],
        ['城南卫生中心', '放射科', '东软 16排CT (设备编号A55)', '650 份', '约 5,000 份', '严重闲置'],
      ],
    },
  },
}

// 状态管理
const filterDate = ref('2026-Q1')
const filterHospital = ref('all')
const filterCategory = ref('technical')
const filterRule = ref('tc-1')

// 获取当前报告数据
const currentReport = computed(() => {
  return reportDataStore[filterRule.value] || null
})

// 统一颜色的帮助函数
const getStatusColor = (status: string) => {
  if (status === 'danger') return 'text-red-600 bg-red-50 border-red-200'
  if (status === 'warning') return 'text-orange-600 bg-orange-50 border-orange-200'
  return 'text-blue-600 bg-blue-50 border-blue-200'
}

const getStatusBgClass = (status: string) => {
  if (status === 'danger') return 'bg-red-500'
  if (status === 'warning') return 'bg-orange-500'
  return 'bg-blue-500'
}

const getTextColor = (status: string) => {
  if (status === 'danger') return 'text-red-500'
  if (status === 'warning') return 'text-orange-500'
  return 'text-blue-500'
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
