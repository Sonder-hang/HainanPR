export type IndicatorKind = 'four' | 'core18'
export type RunMode = 'immediate' | 'monthly' | 'quarterly'
export type RunStatus = 'running' | 'success' | 'failed' | 'pending'

export type ExecutionRecord = {
  id: string
  /** 指标类型 */
  kind: IndicatorKind
  /** 指标名称（四要素为序号，十八项为指标名） */
  indicatorName: string
  indicatorId: string
  /** 执行频率 */
  runMode: RunMode
  /** 时间范围描述 */
  timeRange: string
  /** 状态 */
  status: RunStatus
  /** 开始时间 */
  startTime: string
  /** 耗时（秒） */
  duration: number
  /** 产出条数（计数型：总条数；比值型：分子条数） */
  outputCount: number
  /** 比值型指标结果百分比（如 85.23%），计数型为 undefined */
  ratioPercent?: number
  /** 比值型分母真实全量条数，计数型为 undefined */
  denominatorCount?: number
  /** 比值型分子真实全量条数（用于详情抽屉显示），计数型为 undefined */
  numeratorCount?: number
  /** 执行结果列名（来自 preview_data） */
  resultColumns?: string[]
  /** 执行结果数据（来自 preview_data，只含预览行，非全量） */
  resultData?: Record<string, any>[]
  /** 分母预览列名 */
  denominatorPreviewColumns?: string[]
  /** 分母预览数据（只含预览行，非全量） */
  denominatorPreviewData?: Record<string, any>[]
  /** 使用的计算方式 */
  calcMethod: string
  /** 结果类型：ratio=比值型（百分比），count=计数型 */
  resultType: 'ratio' | 'count'
  /** 使用的 SQL 或 Prompt 片段 */
  usedScript: string
  /** 失败原因（若有） */
  errorMessage?: string
  /** 执行日志 */
  logs: { time: string; level: 'info' | 'warn' | 'error'; message: string }[]
}

const LOGS_SUCCESS = [
  { time: '10:00:01', level: 'info' as const, message: '开始加载指标配置...' },
  { time: '10:00:02', level: 'info' as const, message: '加载分母采集方案：从【病案首页】提取同期住院患者...' },
  { time: '10:00:03', level: 'info' as const, message: '分母数据提取完成，共 3,284 条记录。' },
  { time: '10:00:04', level: 'info' as const, message: '加载分子采集方案：从【转科记录】提取48h内转科患者...' },
  { time: '10:00:05', level: 'info' as const, message: '分子数据提取完成，共 127 条记录。' },
  { time: '10:00:06', level: 'info' as const, message: '分母 / 分子 比值计算中...' },
  { time: '10:00:07', level: 'info' as const, message: '执行完成。指标值：3.87%，较上月上升 0.12%。' },
]

const LOGS_FAILED = [
  { time: '14:23:01', level: 'info' as const, message: '开始加载指标配置...' },
  { time: '14:23:02', level: 'info' as const, message: '加载分母采集方案：从【死亡记录】提取死亡病例...' },
  { time: '14:23:03', level: 'warn' as const, message: '检测到数据源【死亡记录】本月无新增数据。' },
  { time: '14:23:04', level: 'error' as const, message: '分母数据量为 0，指标无法计算，终止执行。' },
]

const LOGS_RUNNING = [
  { time: '09:10:01', level: 'info' as const, message: '开始加载指标配置...' },
  { time: '09:10:02', level: 'info' as const, message: '分母数据源连接中...' },
  { time: '09:10:03', level: 'info' as const, message: '分母数据提取中，当前进度 45%...' },
]

export const MOCK_RECORDS: ExecutionRecord[] = [
  {
    id: 'exec-001',
    kind: 'core18',
    indicatorName: '患者入院 48 小时内转科的比例',
    indicatorId: 'c18-1',
    runMode: 'monthly',
    timeRange: '2026-02',
    status: 'success',
    startTime: '2026-03-01 10:00:01',
    duration: 6,
    outputCount: 3284,
    resultType: 'ratio',
    calcMethod: 'SQL录入',
    usedScript: 'SELECT COUNT(DISTINCT patient_id) FROM transfer_records\nWHERE TIMESTAMPDIFF(HOUR, admission_time, transfer_time) < 48\n  AND transfer_dept NOT IN ("重症医学科")\n  AND transfer_date BETWEEN "2026-02-01" AND "2026-02-28";',
    logs: LOGS_SUCCESS,
  },
  {
    id: 'exec-002',
    kind: 'core18',
    indicatorName: '上级医师查房记录规范率',
    indicatorId: 'c18-3',
    runMode: 'quarterly',
    timeRange: '2025-Q4',
    status: 'failed',
    startTime: '2026-03-05 14:23:01',
    duration: 3,
    outputCount: 0,
    resultType: 'ratio',
    calcMethod: '大模型Prompt',
    usedScript: '请从以下病历记录中提取上级医师查房内容，判断是否满足以下条件：\n1. 查房记录应记录上级医师对病史的补充；\n2. 查房记录应记录体格检查的新发现；\n3. 首次查房应有明确的诊疗意见；\n4. 首次查房应有病情评估记录；\n5. 首次查房应在患者入院后48小时内完成。',
    errorMessage: '分母数据量为 0，指标无法计算，终止执行。详见日志第 3 行。',
    logs: LOGS_FAILED,
  },
  {
    id: 'exec-003',
    kind: 'four',
    indicatorName: '序号 1 — 人员要素：医师职称超权限抗生素',
    indicatorId: 'fe-1',
    runMode: 'immediate',
    timeRange: '2026-03',
    status: 'running',
    startTime: '2026-04-02 09:10:01',
    duration: 0,
    outputCount: 0,
    resultType: 'ratio',
    calcMethod: 'SQL录入',
    usedScript: 'SELECT * FROM medical_orders a\nJOIN physician_title b ON a.physician_id = b.id\nWHERE a.drug_type IN ("限制级抗生素", "特殊级抗生素")\n  AND b.title_level < a.drug_required_level;',
    logs: LOGS_RUNNING,
  },
  {
    id: 'exec-004',
    kind: 'core18',
    indicatorName: '急会诊及时到位率',
    indicatorId: 'c18-5',
    runMode: 'monthly',
    timeRange: '2026-01',
    status: 'success',
    startTime: '2026-02-01 10:00:00',
    duration: 8,
    outputCount: 156,
    resultType: 'ratio',
    calcMethod: 'SQL录入',
    usedScript: 'SELECT COUNT(*) FROM emergency_consultation\nWHERE arrival_time - request_time <= INTERVAL 10 MINUTE;',
    logs: LOGS_SUCCESS,
  },
  {
    id: 'exec-005',
    kind: 'four',
    indicatorName: '序号 6 — 机构要素：科目零业务监测',
    indicatorId: 'fe-6',
    runMode: 'monthly',
    timeRange: '2026-01',
    status: 'success',
    startTime: '2026-02-01 10:05:00',
    duration: 11,
    outputCount: 9,
    resultType: 'count',
    calcMethod: 'SQL录入',
    usedScript: 'SELECT org_name, subject, COUNT(*) as months\nFROM business_records\nGROUP BY org_name, subject\nHAVING months = 0\nORDER BY months DESC;',
    logs: LOGS_SUCCESS,
  },
  {
    id: 'exec-006',
    kind: 'core18',
    indicatorName: '手术患者特级护理/一级护理出院率',
    indicatorId: 'c18-9',
    runMode: 'quarterly',
    timeRange: '2025-Q3',
    status: 'success',
    startTime: '2025-10-01 10:00:00',
    duration: 14,
    outputCount: 892,
    resultType: 'count',
    calcMethod: 'SQL录入',
    usedScript: 'SELECT COUNT(*) FROM patient_records\nWHERE nursing_level IN (1, 2)\n  AND discharge_date BETWEEN "2025-07-01" AND "2025-09-30";',
    logs: LOGS_SUCCESS,
  },
  {
    id: 'exec-007',
    kind: 'core18',
    indicatorName: '临床用血审核及输血病程记录完整率',
    indicatorId: 'c18-12',
    runMode: 'monthly',
    timeRange: '2026-04',
    status: 'pending',
    startTime: '—',
    duration: 0,
    outputCount: 0,
    resultType: 'ratio',
    calcMethod: 'SQL录入',
    usedScript: '-- 已排程，到达计划时间后自动执行。\nSELECT * FROM blood_transfusion_audit WHERE period = "2026-04";',
    logs: [
      {
        time: '08:00:00',
        level: 'info',
        message: '任务已排程，状态：等待中。统计周期：2026-04，将在计划时间点由调度自动启动。',
      },
    ],
  },
]
