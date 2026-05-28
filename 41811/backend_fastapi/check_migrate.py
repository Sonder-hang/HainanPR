import pymysql
import json

conn = pymysql.connect(
    host='127.0.0.1', port=3306, user='root',
    password='22013232', database='hainan',
    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as cur:
    cur.execute(
        "SELECT id, name, calc_type, template_type FROM indicator "
        "WHERE indicator_type='core18' ORDER BY id"
    )
    rows = cur.fetchall()
conn.close()

# key -> template_type
KEY_TO_TT = {
    "deathPatientDefinition": "STRUCTURE",
    "deathDiseaseSpectrum": "STRUCTURE",
    "deathSurgicalSpectrum": "STRUCTURE",
    "icd10Subcategories": "STRUCTURE",
    "icd9Cm3Categories": "STRUCTURE-special",
    "overallMortalityRate": "COMPOSITE",
    "perioperativeMortality": "COMPOSITE",
    "unexpectedRehospitalizationAnalysis": "COMPOSITE",
    "unplannedReturnToORAnalysis": "COMPOSITE",
    "complicationRateRatio": "RATE-special",
    "mortalityRateRatio": "RATE-special",
    "surgicalComplication": "RATE",
}

# DB name -> cascader key
DB_NAME_TO_KEY = {
    "患者入院 48 小时内转科的比例": "transferWithin48HoursRate",
    "患者入院 8 小时内查房率": "patientAdmissionRoundRate",
    "上级医师查房记录规范率": "seniorPhysicianRoundRate",
    "住院患者非计划手术率": "unplannedSurgeryRate",
    "急会诊及时到位率": "emergencyConsultationTimelyRate",
    "急会诊有效率": "emergencyConsultationEffectiveRate",
    "普通会诊及时完成率": "regularConsultationTimelyRate",
    "普通会诊有效率": "emergencyConsultationEffectiveRate",
    "手术患者特级护理/一级护理出院率": "surgicalSpecialCareDischargeRate",
    "非计划再次住院/手术患者疑难病例讨论完成率": "unplannedRehospitalizationSurgeryDiscussionRate",
    "非计划再次住院/手术患者疑难病例讨论记录完整率": "unplannedRehospitalizationSurgeryDiscussionCompleteRate",
    "高额异常费用患者进行疑难病例讨论的占比": "highCostDiscussionRate",
    "急危重症患者抢救成功率": "criticalCareSuccessRate",
    "术前讨论完成率": "preoperativeDiscussionRate",
    "术者参加术前讨论率": "surgeonParticipationInPreoperativeDiscussionRate",
    "术前讨论计划手术一致率": "preoperativePlanConsistencyRate",
    "实际手术术者与计划手术术者一致率": "surgeonConsistencyRate",
    "死亡病例讨论 5 日完成率": "deathCaseDiscussionWithin5DaysRate",
    "科主任主持死亡病例讨论率": "departmentDirectorPresideDeathDiscussionRate",
    "长期医嘱当日终止率": "longTermOrderTerminationRate",
    "手术医师手术时间重合率": "surgeonTimeOverlapRate",
    "麻醉医师手术时间重合率": "anesthesiologistTimeOverlapRate",
    "四级手术与三级手术并发症发生率比": "complicationRateRatio",
    "四级手术与三级手术患者死亡率比": "mortalityRateRatio",
    "四级手术术前多学科讨论完成率": "preoperativeMultidisciplinaryDiscussionRateForLevel4",
    "三、四级手术实际开展率": "level3And4SurgeryImplementationRate",
    "危急值报告时间": "criticalValueReportTime",
    "住院患者危急值当日及时处置率": "criticalValueTimelyDisposalRate",
    "特殊使用级抗菌药物使用会诊率": "specialAntibioticConsultationRate",
    "临床用血后评估记录率": "bloodUsageEvaluationRate",
    "术中自体血回输率": "autologousBloodTransfusionRate",
    "主要诊断ICD-10编码亚目种类数": "icd10Subcategories",
    "主要手术ICD-9-CM-3四位码种类数": "icd9Cm3Categories",
    "死亡或出院预期转归不良患者": "deathPatientDefinition",
    "住院患者死亡疾病谱": "deathDiseaseSpectrum",
    "住院患者死亡手术谱": "deathSurgicalSpectrum",
    "患者住院、新生儿、手术患者住院总死亡率": "overallMortalityRate",
    "非预期再住院情况分析": "unexpectedRehospitalizationAnalysis",
    "非计划重返手术室再手术分析": "unplannedReturnToORAnalysis",
    "住院患者围手术期死亡率": "perioperativeMortality",
    "手术并发症发生率": "surgicalComplication",
    "I类切口手术抗菌药物预防使用率": "antibioticProphylaxis",
    "住院手术患者VTE发生率": "vteIncidence",
}

print("DB 实际值 vs 期望值：")
print(f"{'ID':>3} | {'期望':<22} | {'实际':<22} | {'状态'}")
print("-" * 65)

mismatches = []
for r in rows:
    ind_id = r['id']
    ind_name = r['name']
    calc_type = r['calc_type']
    actual_tt = r['template_type']

    cascader_key = DB_NAME_TO_KEY.get(ind_name)
    expected_tt = None
    if cascader_key and cascader_key in KEY_TO_TT:
        expected_tt = KEY_TO_TT[cascader_key]
    elif cascader_key:
        expected_tt = 'STRUCTURE' if calc_type == 'count' else 'RATE'
    else:
        expected_tt = 'STRUCTURE' if calc_type == 'count' else 'RATE'

    status = 'OK' if actual_tt == expected_tt else 'MISMATCH'
    if status == 'MISMATCH':
        mismatches.append((ind_id, ind_name, expected_tt, actual_tt))

    print(f"{ind_id:>3} | {expected_tt:<22} | {str(actual_tt):<22} | {status}")

print(f"\n共 {len(mismatches)} 个不匹配：")
for ind_id, name, expected, actual in mismatches:
    print(f"  ID={ind_id} | 期望={expected} | 实际={actual} | {name}")
