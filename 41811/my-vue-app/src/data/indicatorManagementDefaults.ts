/** 计算方式枚举 */
export type CalcMethod = 'none' | 'textToSql' | 'sql' | 'prompt'

export const CALC_METHOD_LABELS: Record<CalcMethod, string> = {
  none: '未设置',
  textToSql: 'Text-to-SQL',
  sql: 'SQL录入',
  prompt: '大模型Prompt',
}

/** 四要素监管指标 — 默认数据 */
export type FourElementIndicator = {
  id: string
  /** 指标名称 */
  name: string
  seq: number
  category: string
  scope: string
  workContent: string
  ruleLogic: string
  /** 是否使用大模型计算 */
  useLlm: string
  /** 计算类型：ratio | count */
  calcType: 'ratio' | 'count'
  /** 当 calcType 为 ratio/count 时填写 */
  sqlContent: string
}

/** 十八项核心制度相关指标 */
export type Core18Indicator = {
  id: string
  seq: number
  name: string
  useLlm: string
  computable: string
  denominator: string
  numerator: string
  description: string
  denomCollectPlan: string
  denomSource: string
  denomPlatformTable: string
  numeratorCollectPlan: string
  numeratorSource: string
  numeratorPlatformTable: string
  formula: string
  platformDataReady: string
  platformSupportOutput: string
  remark: string
  priority: string
  regexMatch: string
  regexRule: string
  /** 计算方式 */
  calcMethod: CalcMethod
  /** 计算类型：ratio | count */
  calcType: 'ratio' | 'count'
  /** 当 calcMethod 为 sql/textToSql 时填写 */
  sqlContent: string
  /** 当 calcMethod 为 prompt 时填写 */
  promptContent: string
}

export const DEFAULT_FOUR_ELEMENTS: FourElementIndicator[] = [
  // 1 — 人员要素
  { id: 'fe-1', name: '越权开具抗生素', seq: 1, category: '人员要素', scope: '审核范围：住院', workContent: '在系统中维护医师职称，设定「职称-限制级、特殊级抗生素」匹配规则，对超范围业务自动报警。', ruleLogic: '医生开了与自己职称不符的限制级或者特殊级抗生素', useLlm: '否', calcType: 'ratio', sqlContent: '' },
  // 2 — 人员要素
  { id: 'fe-2', name: '时空轨迹异常', seq: 2, category: '人员要素', scope: '时间阈值：半小时。审核范围：住院', workContent: '在系统中维护医师操作记录，设定「同一医师短时间内在不同医疗机构中出现诊疗记录」匹配规则，对超范围业务自动报警。', ruleLogic: '某个时间段内医生在不同机构内容开了医嘱信息', useLlm: '否', calcType: 'ratio', sqlContent: '' },
  // 3 — 人员要素
  { id: 'fe-3', name: '多点执业冲突', seq: 3, category: '人员要素', scope: '审核范围：住院', workContent: '在系统中维护医师多点执业记录，设定「对主执业机构在公立医院的发生民营医院多点执业或诊疗记录」匹配规则，对超范围业务自动报警。', ruleLogic: '同一个患者，先后在公立以及民营医院诊治，由同一个医生在公立医院也在民营医院开了医嘱', useLlm: '否', calcType: 'ratio', sqlContent: '' },
  // 4 — 机构要素
  { id: 'fe-4', name: '超范围经营', seq: 4, category: '机构要素', scope: '审核范围：住院', workContent: '资质方面：在系统中维护医疗机构诊疗科目信息，设定「诊断治疗-诊疗科目」匹配规则，对超范围业务自动报警。', ruleLogic: '医生开了与该医疗机构诊疗科目不符的诊断', useLlm: '否', calcType: 'ratio', sqlContent: '' },
  // 5 — 机构要素
  { id: 'fe-5', name: '收治能力超限', seq: 5, category: '机构要素', scope: '审核范围：住院', workContent: '在系统中设定「面积-床位-住院收治上限」联动模型，超限自动拦截，通报医保拒绝结算、直至取消机构资质。', ruleLogic: '机构面积以及床位数之间的逻辑关系；机构床位数与当日在院患者人数', useLlm: '否', calcType: 'ratio', sqlContent: '' },
  // 6 — 机构要素
  { id: 'fe-6', name: '科目零业务监测', seq: 6, category: '机构要素', scope: '审核范围：住院', workContent: '在系统中设定「机构-诊疗科目-业务量」匹配规则，对单一诊疗科目连续3个月「零」业务量的自动报警。', ruleLogic: '医疗机构连续3月无诊疗科目对应的诊断', useLlm: '否', calcType: 'ratio', sqlContent: '' },
  // 7 — 技术要素
  { id: 'fe-7', name: '限制类技术核查', seq: 7, category: '技术要素', scope: '审核技术来源：国家限制性目录；审核范围：住院', workContent: '限制类技术备案情况与系统进一步关联，建立「限制类技术备案记录-备案医师-技术开展」匹配规则，对超范围业务自动报警。', ruleLogic: '对开展限制性技术的机构、医生的范围进行审核', useLlm: '否', calcType: 'ratio', sqlContent: '' },
  // 8 — 技术要素
  { id: 'fe-8', name: '诊疗异常聚集', seq: 8, category: '技术要素', scope: '审核指标：主诊和主手；审核范围：住院；审核粒度：最细粒度', workContent: '在系统中维护医疗机构诊断、手术等统计功能，建立「连续三个月内单一医疗机构单一诊断和单一术式占比超过全院50%」统计报警规则。', ruleLogic: '在一定时间范围内，对医院开展的诊断、手术频率进行统计。', useLlm: '否', calcType: 'ratio', sqlContent: '' },
  // 9 — 技术要素
  { id: 'fe-9', name: '公立患者流失', seq: 9, category: '技术要素', scope: '公立医院门诊就诊时间；民营医院住院就诊时间', workContent: '在系统中维护患者流动统计功能建立「民营医院收治患者来源于公立医院情况」数据分析功能，统计公立医院及医师个人患者流失数据。', ruleLogic: '在一定的时间范围内，统计患者前后两次的不同机构入院情况。', useLlm: '否', calcType: 'ratio', sqlContent: '' },
  // 10 — 技术要素
  { id: 'fe-10', name: '未成年人高危预警', seq: 10, category: '技术要素', scope: '审核范围：未成年人', workContent: '在系统中构建未成年人受侵害风险监测预警功能，建立「高风险诊断识别与线索溯源」数据分析模型，通过匹配门诊及住院全量诊疗数据，统计并预警疑似侵害未成年人线索。', ruleLogic: '在一定的时间范围内，监测未成年人患者就诊主诊断及次诊断 ICD10 编码匹配「侵害未成年人高风险诊断编码库」。', useLlm: '是', calcType: 'ratio', sqlContent: '' },
  // 11 — 技术要素
  { id: 'fe-11', name: '麻精药品异常', seq: 11, category: '技术要素', scope: '审核范围：门急诊', workContent: '在系统中建立「麻醉、精神类药品处方超量及重复购药」监测预警功能。关联患者诊疗信息，针对门急诊普通患者执行控缓释制剂 7 天量、癌痛及慢性痛患者执行 15 天量的校验规则，实时识别并命中短时间内异常购麻醉、精神类药品行为。', ruleLogic: '在一定时间范围内，监测门急诊患者异常购麻醉、精神类药品行为。', useLlm: '否', calcType: 'ratio', sqlContent: '' },
  // 12 — 技术要素
  { id: 'fe-12', name: '限制类技术超范围', seq: 12, category: '技术要素', scope: '—', workContent: '在系统中构建「限制类技术开展情况」监测功能，从机构权限、医师权限、患者转归、培训质量四个层面进行核查与分析', ruleLogic: '核查限制类技术是否超出机构可开展范围、是否超出医师个人可开展范围。', useLlm: '否', calcType: 'ratio', sqlContent: '' },
  // 13 — 技术要素
  { id: 'fe-13', name: '抗肿瘤药物规范', seq: 13, category: '技术要素', scope: '审核范围：抗肿瘤药物', workContent: '对医疗机构开具的抗肿瘤药物，联合疾病诊断、TNM分期、病理诊断等数据进行分析，规范肿瘤诊疗行为', ruleLogic: '结合需先行基因检测的药物目录，识别抗肿瘤药物使用是否存在无分子靶点检测依据的疑点行为。', useLlm: '是', calcType: 'ratio', sqlContent: '' },
  // 14 — 技术要素
  { id: 'fe-14', name: '肿瘤分期规范率', seq: 14, category: '技术要素', scope: '审核范围：肿瘤患者', workContent: '监测首次治疗前临床TNM分期诊断情况。', ruleLogic: '结合肿瘤患者病例，识别首次治疗前是否完成临床TNM分期评估，统计分期诊断率。', useLlm: '是', calcType: 'ratio', sqlContent: '' },
  // 15 — 设备要素
  { id: 'fe-15', name: '人机资质不符', seq: 15, category: '设备要素', scope: '审核范围：手术患者', workContent: '建立「手术分级-医生授权-设备配置」匹配规则，对超范围业务自动报警。', ruleLogic: '以手术分级为基准，医生授权对应资质等级，设备配置满足技术需求。', useLlm: '否', calcType: 'ratio', sqlContent: '' },
  // 16 — 设备要素
  { id: 'fe-16', name: '设备账实不符', seq: 16, category: '设备要素', scope: '—', workContent: '在系统中对设备基本信息、数量及品种与医疗机构设置申请及校验验证是否一致。', ruleLogic: '验证设备对申请和使用是否一致。', useLlm: '否', calcType: 'ratio', sqlContent: '' },
  // 17 — 设备要素
  { id: 'fe-17', name: '检查阳性率异常', seq: 17, category: '设备要素', scope: '—', workContent: '在系统中维护医疗机构设备出具检查检验结果统计分析功能，建立「连续三个月内单一医疗机构特定检查或检验结果阳性率超过80%且该检查或检验总量占全院总量的80%」统计报警规则。', ruleLogic: '在一定的时间范围内，统计机构检验项目频次、检验结果阳性占比。', useLlm: '否', calcType: 'ratio', sqlContent: '' },
  // 18 — 设备要素
  { id: 'fe-18', name: '重点药品耗材超限', seq: 18, category: '设备要素', scope: '国家三级公立医院绩效考核操作手册中耗材', workContent: '开展重点药品、耗材日常监测。', ruleLogic: '开具的重点药品、耗材，超过阈值。', useLlm: '否', calcType: 'ratio', sqlContent: '' },
  // 19 — 设备要素
  { id: 'fe-19', name: '设备负荷与闲置', seq: 19, category: '设备要素', scope: '—', workContent: '诊断/治疗设备年平均服务患者数量。', ruleLogic: '患者的检查报告数量/设备数量。', useLlm: '否', calcType: 'ratio', sqlContent: '' },
]

export const DEFAULT_CORE18: Core18Indicator[] = [
  // 1
  { id: 'c18-1', seq: 1, name: '患者入院 48 小时内转科的比例', useLlm: '否', computable: '是', denominator: '同期入院患者总人次数', numerator: '入院48小时内转科患者人次数', description: '本指标不包括患者转入/转出ICU的情况。', denomCollectPlan: '入院记录病例数', denomSource: '入院记录', denomPlatformTable: '', numeratorCollectPlan: '满足下列条件的转科记录：转科时间-入院时间<48H；转出/转入科室均不含重症医学科', numeratorSource: '转科记录', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '否', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 2
  { id: 'c18-2', seq: 2, name: '患者入院 8 小时内查房率', useLlm: '否', computable: '是', denominator: '同期入院患者总人次数', numerator: '入院8小时内开具检查或治疗医嘱的患者人次数', description: '无', denomCollectPlan: '入院记录病例数', denomSource: '入院记录', denomPlatformTable: '', numeratorCollectPlan: '最早的医嘱下达时间-入院时间<8H', numeratorSource: '医嘱', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '否', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 3
  { id: 'c18-3', seq: 3, name: '上级医师查房记录规范率', useLlm: '是', computable: '是', denominator: '同期住院患者病例总数量', numerator: '住院患者病历中上级医师查房记录规范、完整的病例数量', description: '无', denomCollectPlan: '入院记录病例数', denomSource: '入院记录', denomPlatformTable: '', numeratorCollectPlan: '上级医师查房记录含病史补充、体格检查新发现、诊疗意见、病情评估、48H内完成、分析讨论与鉴别诊断', numeratorSource: '主治医师首次查房记录', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '否', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 4
  { id: 'c18-4', seq: 4, name: '住院患者非计划手术率', useLlm: '否', computable: '是', denominator: '同期住院患者总人次数', numerator: '行非计划手术的住院患者人次数', description: '无', denomCollectPlan: '入院记录病例数', denomSource: '入院记录', denomPlatformTable: '', numeratorCollectPlan: '手术类型=「非计划」', numeratorSource: '手术记录/手术申请单', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '否', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 5
  { id: 'c18-5', seq: 5, name: '急会诊及时到位率', useLlm: '否', computable: '是', denominator: '同期急会诊总次数', numerator: '急会诊记录中10分钟内到位的急会诊次数', description: '急会诊范围：患者疾病超出本科室处置能力且可能随时危及生命，需要其他科室立刻协助诊疗、参与抢救的会诊申请。', denomCollectPlan: '出院患者中急会诊文书数量；医嘱中有「急会诊」', denomSource: '急会诊申请单/急会诊记录', denomPlatformTable: '', numeratorCollectPlan: '达到时间-申请时间 < 10min', numeratorSource: '急会诊申请单', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '否', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 6
  { id: 'c18-6', seq: 6, name: '急会诊有效率', useLlm: '否', computable: '是', denominator: '同期急会诊总次数', numerator: '急会诊后开具相关医嘱的次数', description: '申请急会诊后40分钟内开具相关医嘱。', denomCollectPlan: '急会诊病例数或医嘱中包含「急会诊」的数量', denomSource: '急会诊申请单', denomPlatformTable: '', numeratorCollectPlan: '医嘱下达时间-急会诊申请时间<40min', numeratorSource: '医嘱；急会诊申请单', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '否', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 7
  { id: 'c18-7', seq: 7, name: '普通会诊及时完成率', useLlm: '否', computable: '是', denominator: '同期普通会诊总次数', numerator: '普通会诊24小时内完成次数', description: '会诊医师电子签章时间即为会诊完成时间。', denomCollectPlan: '会诊记录数量', denomSource: '会诊记录', denomPlatformTable: '', numeratorCollectPlan: '会诊时间-申请时间<24H', numeratorSource: '会诊记录', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '否', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 8
  { id: 'c18-8', seq: 8, name: '普通会诊有效率', useLlm: '否', computable: '是', denominator: '同期普通会诊患者总次数', numerator: '普通会诊结束后开具相关医嘱的次数', description: '申请普通会诊后24小时内开具相关医嘱。', denomCollectPlan: '会诊记录数量', denomSource: '会诊记录', denomPlatformTable: '', numeratorCollectPlan: '会诊时间+24H内医嘱数量', numeratorSource: '医嘱', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '否', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 9
  { id: 'c18-9', seq: 9, name: '手术患者特级护理/一级护理出院率', useLlm: '否', computable: '是', denominator: '同期手术患者总数量', numerator: '手术患者出院时为特级护理/一级护理级别的患者数量', description: '无', denomCollectPlan: '病案首页手术编码不空', denomSource: '病案首页', denomPlatformTable: '', numeratorCollectPlan: "护理等级代码='1' or '2'", numeratorSource: '一般护理记录', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '护理记录采集口径为%级护理%', priority: '', regexMatch: '是', regexRule: '%级护理%', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 10（跳过床旁交接班 c18-10）
  { id: 'c18-10', seq: 10, name: '非计划再次住院/手术患者疑难病例讨论完成率', useLlm: '否', computable: '是', denominator: '同期非计划再次住院/手术的数量', numerator: '对非计划再次住院/手术患者进行疑难病例讨论的数量', description: '无', denomCollectPlan: '非计划再入院/非计划再次手术规则见HQMS', denomSource: '病案首页', denomPlatformTable: '', numeratorCollectPlan: '疑难病例讨论记录不空', numeratorSource: '疑难病例讨论记录', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '否', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 11
  { id: 'c18-11', seq: 11, name: '非计划再次住院/手术患者疑难病例讨论记录完整率', useLlm: '是', computable: '是', denominator: '同期对非计划再次住院/手术患者进行疑难病例讨论的数量', numerator: '讨论并将讨论结论记入病历的数量', description: '无', denomCollectPlan: '病案首页+存在疑难病例讨论记录', denomSource: '病案首页', denomPlatformTable: '', numeratorCollectPlan: '讨论记录内容要素完整、结论记入病历', numeratorSource: '疑难病例讨论记录', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '否', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 12
  { id: 'c18-12', seq: 12, name: '高额异常费用患者进行疑难病例讨论的占比', useLlm: '否', computable: '是', denominator: '同期高额异常费用患者数量', numerator: '对产生高额异常费用患者进行疑难病例讨论的数量', description: '高额异常费用：一个住院周期内医疗费用20万元以上（各地可调整）。', denomCollectPlan: '住院期间总费用>20万的病例数量', denomSource: '', denomPlatformTable: '', numeratorCollectPlan: '包含疑难病例讨论', numeratorSource: '疑难病例讨论', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '采集口径为%疑难%讨论%', priority: '', regexMatch: '是', regexRule: '%疑难%讨论%', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 13
  { id: 'c18-13', seq: 13, name: '急危重症患者抢救成功率', useLlm: '', computable: '是', denominator: '同期急危重症患者抢救的总例次数', numerator: '急危重症患者抢救成功的例次数', description: '抢救成功指经抢救后存活超过24小时或存活至下一次抢救开始。', denomCollectPlan: '', denomSource: '', denomPlatformTable: '', numeratorCollectPlan: '', numeratorSource: '', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '否', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 14
  { id: 'c18-14', seq: 14, name: '术前讨论完成率', useLlm: '否', computable: '是', denominator: '同期手术总例数', numerator: '完成术前讨论的手术例数', description: '除抢救生命为目的的急诊手术外，术前讨论完成时间晚于手术医嘱和同意书签署视为未完成。', denomCollectPlan: '病案首页中手术编码不空', denomSource: '', denomPlatformTable: '', numeratorCollectPlan: '', numeratorSource: '', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '采集口径为%术前%讨论%', priority: '', regexMatch: '是', regexRule: '%术前%讨论%', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 15
  { id: 'c18-15', seq: 15, name: '术者参加术前讨论率', useLlm: '否', computable: '是', denominator: '同期进行术前讨论手术总例数', numerator: '术者参加术前讨论的手术例数', description: '术者指手术的主要完成人。', denomCollectPlan: '病案首页手术+存在术前讨论', denomSource: '术前讨论', denomPlatformTable: '', numeratorCollectPlan: '术前讨论参加人员名单包含手术记录中术者', numeratorSource: '术前讨论；手术记录', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '采集口径为%术前%讨论%', priority: '', regexMatch: '是', regexRule: '%术前%讨论%', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 16
  { id: 'c18-16', seq: 16, name: '术前讨论计划手术一致率', useLlm: '是', computable: '是', denominator: '同期手术总例数', numerator: '实际开展手术与术前讨论计划手术一致的手术例数', description: '无', denomCollectPlan: '病案首页手术为国临版3.0手术与介入治疗', denomSource: '病案首页', denomPlatformTable: '', numeratorCollectPlan: '「术前讨论」和「手术记录」中手术名称相同', numeratorSource: '术前讨论；手术记录', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '采集口径为%术前%讨论%', priority: '', regexMatch: '是', regexRule: '%术前%讨论%', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 17
  { id: 'c18-17', seq: 17, name: '实际手术术者与计划手术术者一致率', useLlm: '否', computable: '存疑', denominator: '同期手术总例数', numerator: '实际开展手术术者与计划手术术者一致的手术例数', description: '无', denomCollectPlan: '病案首页手术为国临版3.0', denomSource: '病案首页', denomPlatformTable: '', numeratorCollectPlan: '「术前讨论」和「手术记录」中术者名称或编码相同', numeratorSource: '术前讨论；手术记录', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '否', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 18
  { id: 'c18-18', seq: 18, name: '死亡病例讨论 5 日完成率', useLlm: '否', computable: '是', denominator: '同期死亡病例总数量', numerator: '患者死亡5个工作日内完成死亡病例讨论的病例数量', description: '无', denomCollectPlan: '死亡记录数量', denomSource: '死亡记录', denomPlatformTable: '', numeratorCollectPlan: '死亡病例讨论记录.讨论日期时间-死亡记录.死亡日期时间<5D', numeratorSource: '死亡病例讨论记录', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '采集口径为%死亡%讨论%', priority: '', regexMatch: '是', regexRule: '%死亡%讨论%', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 19（跳过医务部门 c18-20）
  { id: 'c18-19', seq: 19, name: '科主任主持死亡病例讨论率', useLlm: '否', computable: '是', denominator: '同期死亡病例总数量', numerator: '死亡病例讨论由科主任主持的病例数量', description: '无', denomCollectPlan: '死亡记录数量', denomSource: '死亡记录', denomPlatformTable: '', numeratorCollectPlan: "专业技术职务类别代码='1'或'2'", numeratorSource: '死亡病例讨论记录', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '采集口径为%死亡%讨论%', priority: '', regexMatch: '是', regexRule: '%死亡%讨论%', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 20（跳过死亡患者病案上传率 c18-22）
  { id: 'c18-20', seq: 20, name: '长期医嘱当日终止率', useLlm: '/', computable: '否，当日停止时间判断存疑', denominator: '同期开具长期医嘱总数量', numerator: '开具长期医嘱后当日终止执行的医嘱数量', description: '无', denomCollectPlan: '', denomSource: '', denomPlatformTable: '', numeratorCollectPlan: '', numeratorSource: '', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '否', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 21
  { id: 'c18-21', seq: 21, name: '手术医师手术时间重合率', useLlm: '否', computable: '存疑', denominator: '同期住院患者手术总例数', numerator: '同一时间内手术医师为同一人的手术例数', description: '「同一时间」指手术未结束时间与其他手术开始时间重合。', denomCollectPlan: '病案首页手术记录为国临版3.0', denomSource: '病案首页', denomPlatformTable: '', numeratorCollectPlan: '手术开始/结束时间重合同一术者', numeratorSource: '手术记录', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '否', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 22
  { id: 'c18-22', seq: 22, name: '麻醉医师手术时间重合率', useLlm: '否', computable: '存疑', denominator: '同期住院患者手术总例数', numerator: '同一时间内手术麻醉医师为同一人的手术例数', description: '无', denomCollectPlan: '病案首页手术记录为国临版3.0', denomSource: '病案首页', denomPlatformTable: '', numeratorCollectPlan: '手术开始/结束时间重合同一麻醉师', numeratorSource: '手术记录', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '否', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 23
  { id: 'c18-23', seq: 23, name: '四级手术与三级手术并发症发生率比', useLlm: '是', computable: '是', denominator: '三级手术并发症发生率', numerator: '四级手术并发症发生率', description: '三、四级手术按本机构手术分级目录；并发症范围见规范。', denomCollectPlan: '病案首页+手术级别3+并发症记录', denomSource: '病案首页；手术记录/术后首次病程', denomPlatformTable: '', numeratorCollectPlan: '手术级别4+记录并发症', numeratorSource: '病案首页；手术记录/术后首次病程', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '否', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 24
  { id: 'c18-24', seq: 24, name: '四级手术与三级手术患者死亡率比', useLlm: '否', computable: '是', denominator: '三级手术患者死亡率', numerator: '四级手术患者死亡率', description: '各级手术患者死亡率为死亡人数占同期各级手术患者人数的比例。', denomCollectPlan: '手术级别3+死亡记录', denomSource: '病案首页/手术执行信息；死亡记录', denomPlatformTable: '', numeratorCollectPlan: '手术级别4+死亡记录', numeratorSource: '病案首页/手术记录；死亡记录', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '否', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 25
  { id: 'c18-25', seq: 25, name: '四级手术术前多学科讨论完成率', useLlm: '是', computable: '是', denominator: '同期四级手术总例数', numerator: '术前完成多学科讨论的四级手术例数', description: '限制类技术按照四级手术进行管理。', denomCollectPlan: '病案首页手术级别代码=4', denomSource: '病案首页', denomPlatformTable: '', numeratorCollectPlan: '术前讨论中包含多学科讨论内容', numeratorSource: '术前讨论', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '采集口径为%四级%术前%多学科%讨论%', priority: '', regexMatch: '是', regexRule: '%四级%术前%多学科%讨论%', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 26（跳过新技术 c18-30）
  { id: 'c18-26', seq: 26, name: '三、四级手术实际开展率', useLlm: '/', computable: '是，每家医院三四级手术备案列表', denominator: '同期备案的三、四级手术术种数', numerator: '实际开展的三、四级手术术种数', description: '三、四级手术备案按《医疗机构手术分级管理办法》报送目录信息。', denomCollectPlan: '', denomSource: '', denomPlatformTable: '', numeratorCollectPlan: '', numeratorSource: '', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '否', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 27
  { id: 'c18-27', seq: 27, name: '危急值报告时间', useLlm: '/', computable: '否', denominator: 'n为实际报告的危急值项目数', numerator: 'X(n+1)/2 或中位数公式', description: 'X为出现危急值到临床科室获取危急值的时间；分别统计住院/门诊/急诊。', denomCollectPlan: '病程记录/护理记录「危急值」', denomSource: '', denomPlatformTable: '', numeratorCollectPlan: '', numeratorSource: '', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '否', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 28
  { id: 'c18-28', seq: 28, name: '住院患者危急值当日及时处置率', useLlm: '否', computable: '是，三医平台不支持', denominator: '同期临床科室接获住院患者危急值项目数', numerator: '当日处置的住院患者危急值项目数', description: '仅统计住院；当日处置以当日病程记录为准，无记录视为未处置。', denomCollectPlan: '病程记录/护理记录「危急值」', denomSource: '', denomPlatformTable: '', numeratorCollectPlan: '', numeratorSource: '', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '否', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 29
  { id: 'c18-29', seq: 29, name: '特殊使用级抗菌药物使用会诊率', useLlm: '是', computable: '是，特殊使用级抗菌药物列表', denominator: '同期特殊使用级抗菌药物使用医嘱总数量', numerator: '使用医嘱与会诊记录相对应的医嘱数量', description: '会诊同意后按程序合理使用。', denomCollectPlan: '医嘱中包含特殊抗菌用药', denomSource: '医嘱', denomPlatformTable: '', numeratorCollectPlan: '会诊意见含同意使用特殊使用级含义', numeratorSource: '会诊记录', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '抗菌药采集口径为%抗菌药%', priority: '', regexMatch: '是', regexRule: '%抗菌药%', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 30
  { id: 'c18-30', seq: 30, name: '临床用血后评估记录率', useLlm: '是', computable: '否', denominator: '同期临床输血治疗病例总例次数', numerator: '输血治疗后规范书写评估输血记录例次数', description: '无', denomCollectPlan: '输血记录不空', denomSource: '输血记录', denomPlatformTable: '', numeratorCollectPlan: '输血病程记录完整详细（含原因、成分、量、血型、观察、不良反应及处置）', numeratorSource: '输血记录', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '采集口径为%输血%评估%', priority: '', regexMatch: '是', regexRule: '%输血%评估%', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 31
  { id: 'c18-31', seq: 31, name: '术中自体血回输率', useLlm: '是', computable: '否', denominator: '同期术中进行输血患者总数量', numerator: '术中使用自体血回输的患者数量', description: '无', denomCollectPlan: '输血记录不空', denomSource: '输血记录', denomPlatformTable: '', numeratorCollectPlan: '洗涤式自体血回输或病程/手术记录相关信息', numeratorSource: '输血记录/手术记录/医嘱/病程记录', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '是', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 32
  { id: 'c18-32', seq: 32, name: '主要诊断ICD-10编码亚目种类数', useLlm: '', computable: '', denominator: '', numerator: '', description: '', denomCollectPlan: '', denomSource: '', denomPlatformTable: '', numeratorCollectPlan: '', numeratorSource: '', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '统计类拓展指标', priority: '', regexMatch: '', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 33
  { id: 'c18-33', seq: 33, name: '主要手术ICD-9-CM-3四位码种类数', useLlm: '', computable: '', denominator: '', numerator: '', description: '', denomCollectPlan: '', denomSource: '', denomPlatformTable: '', numeratorCollectPlan: '', numeratorSource: '', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 34
  { id: 'c18-34', seq: 34, name: '死亡或出院预期转归不良患者', useLlm: '', computable: '', denominator: '', numerator: '', description: '', denomCollectPlan: '', denomSource: '', denomPlatformTable: '', numeratorCollectPlan: '', numeratorSource: '', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 35
  { id: 'c18-35', seq: 35, name: '住院患者死亡疾病谱', useLlm: '', computable: '', denominator: '', numerator: '', description: '', denomCollectPlan: '', denomSource: '', denomPlatformTable: '', numeratorCollectPlan: '', numeratorSource: '', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 36
  { id: 'c18-36', seq: 36, name: '住院患者死亡手术谱', useLlm: '', computable: '', denominator: '', numerator: '', description: '', denomCollectPlan: '', denomSource: '', denomPlatformTable: '', numeratorCollectPlan: '', numeratorSource: '', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 37
  { id: 'c18-37', seq: 37, name: '患者住院、新生儿、手术患者住院总死亡率', useLlm: '', computable: '', denominator: '', numerator: '', description: '', denomCollectPlan: '', denomSource: '', denomPlatformTable: '', numeratorCollectPlan: '', numeratorSource: '', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 38
  { id: 'c18-38', seq: 38, name: '非预期再住院情况分析', useLlm: '', computable: '', denominator: '', numerator: '', description: '', denomCollectPlan: '', denomSource: '', denomPlatformTable: '', numeratorCollectPlan: '', numeratorSource: '', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 39
  { id: 'c18-39', seq: 39, name: '非计划重返手术室再手术分析', useLlm: '', computable: '', denominator: '', numerator: '', description: '', denomCollectPlan: '', denomSource: '', denomPlatformTable: '', numeratorCollectPlan: '', numeratorSource: '', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 40
  { id: 'c18-40', seq: 40, name: '住院患者围手术期死亡率', useLlm: '', computable: '', denominator: '', numerator: '', description: '', denomCollectPlan: '', denomSource: '', denomPlatformTable: '', numeratorCollectPlan: '', numeratorSource: '', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 41
  { id: 'c18-41', seq: 41, name: '手术并发症发生率', useLlm: '', computable: '', denominator: '', numerator: '', description: '', denomCollectPlan: '', denomSource: '', denomPlatformTable: '', numeratorCollectPlan: '', numeratorSource: '', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 42
  { id: 'c18-42', seq: 42, name: 'I类切口手术抗菌药物预防使用率', useLlm: '', computable: '', denominator: '', numerator: '', description: '', denomCollectPlan: '', denomSource: '', denomPlatformTable: '', numeratorCollectPlan: '', numeratorSource: '', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
  // 43
  { id: 'c18-43', seq: 43, name: '住院手术患者VTE发生率', useLlm: '', computable: '', denominator: '', numerator: '', description: '', denomCollectPlan: '', denomSource: '', denomPlatformTable: '', numeratorCollectPlan: '', numeratorSource: '', numeratorPlatformTable: '', formula: '', platformDataReady: '', platformSupportOutput: '', remark: '', priority: '', regexMatch: '', regexRule: '', calcMethod: 'none', sqlContent: '', promptContent: '' },
]
