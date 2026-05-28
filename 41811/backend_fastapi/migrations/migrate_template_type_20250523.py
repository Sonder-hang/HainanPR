"""
数据库迁移脚本：为 indicator 表添加 template_type 字段并批量填充。
使用前请务必在测试环境执行！
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymysql
import json

# 数据库连接配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '22013232',
    'database': 'hainan',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}

# DB 指标名称 → cascader key 的精确映射表（43 条全覆盖）
DB_NAME_TO_KEY = {
    "患者入院 48 小时内转科的比例": "transferWithin48HoursRate",
    "患者入院 8 小时内查房率": "patientAdmissionRoundRate",
    "上级医师查房记录规范率": "seniorPhysicianRoundRate",
    "住院患者非计划手术率": "unplannedSurgeryRate",
    "急会诊及时到位率": "emergencyConsultationTimelyRate",
    "急会诊有效率": "emergencyConsultationEffectiveRate",
    "普通会诊及时完成率": "regularConsultationTimelyRate",
    "普通会诊有效率": "regularConsultationEffectiveRate",
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

# cascader key → template_type 映射（查 reflect-unified.json 规则 + 用户指定）
KEY_TO_TEMPLATE_TYPE = {
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
    "surgicalComplication": "RATE",  # 用户指定为 RATE
}


def add_column(conn):
    """添加 template_type 字段"""
    with conn.cursor() as cur:
        cur.execute("DESCRIBE indicator")
        columns = [row['Field'] for row in cur.fetchall()]
        if 'template_type' not in columns:
            print(">>> 添加 template_type 字段...")
            cur.execute("""
                ALTER TABLE indicator
                ADD COLUMN template_type VARCHAR(30) DEFAULT NULL
                COMMENT 'STRUCTURE | STRUCTURE-special | RATE | RATE-special | COMPOSITE'
            """)
            conn.commit()
            print("    字段添加成功。")
        else:
            print(">>> template_type 字段已存在，跳过。")


def migrate(conn):
    """批量填充 template_type"""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, name, calc_type FROM indicator WHERE indicator_type='core18' ORDER BY seq"
        )
        indicators = cur.fetchall()

    print(f"\n>>> 开始迁移 {len(indicators)} 个指标...")

    updated = 0
    skipped = 0
    errors = []

    for ind in indicators:
        ind_id = ind['id']
        ind_name = ind['name']
        calc_type = ind['calc_type']

        # 1. 通过映射表查 template_type
        template_type = None
        cascader_key = DB_NAME_TO_KEY.get(ind_name)

        if cascader_key and cascader_key in KEY_TO_TEMPLATE_TYPE:
            template_type = KEY_TO_TEMPLATE_TYPE[cascader_key]
        elif cascader_key:
            # 映射到 key 但不在 template_type 表中，根据 calc_type 推断
            if calc_type == 'count':
                template_type = 'STRUCTURE'
            else:
                template_type = 'RATE'
        else:
            # 无法匹配兜底
            if calc_type == 'count':
                template_type = 'STRUCTURE'
            else:
                template_type = 'RATE'
            errors.append(f"  [兜底] ID={ind_id} | {ind_name} -> {template_type}")

        # 更新数据库
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE indicator SET template_type=%s WHERE id=%s",
                (template_type, ind_id)
            )
        conn.commit()
        updated += 1

    print(f"\n>>> 迁移完成：更新 {updated} 条，跳过 {skipped} 条")

    if errors:
        print(f"\n>>> 兜底处理的指标（共 {len(errors)} 条，后端应检查是否正确）：")
        for e in errors:
            print(e)
    else:
        print("    所有指标均通过映射表匹配，无兜底处理。")


def verify(conn):
    """验证迁移结果"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COALESCE(template_type, 'NULL') as tt, COUNT(*) as cnt
            FROM indicator
            WHERE indicator_type='core18'
            GROUP BY template_type
            ORDER BY cnt DESC
        """)
        rows = cur.fetchall()

    print("\n>>> 迁移结果验证：")
    print(f"  {'template_type':<25} | count")
    print("  " + "-" * 40)
    total = 0
    for row in rows:
        print(f"  {row['tt']:<25} | {row['cnt']}")
        total += row['cnt']
    print(f"  {'TOTAL':<25} | {total}")

    expected = {
        'STRUCTURE': 4,
        'STRUCTURE-special': 1,
        'RATE': 32,
        'RATE-special': 2,
        'COMPOSITE': 4,
    }
    print("\n>>> 期望值核对：")
    for row in rows:
        tt = row['tt']
        cnt = row['cnt']
        if tt in expected:
            status = "OK" if cnt == expected[tt] else f"MISMATCH (期望 {expected[tt]})"
            print(f"  {tt:<25}: {cnt} {status}")
            del expected[tt]
    for tt, exp_cnt in expected.items():
        print(f"  {tt:<25}: 0  MISSING (期望 {exp_cnt})")


def main():
    print("=" * 60)
    print("indicator.template_type 迁移脚本")
    print("WARNING: 首次执行前请备份数据库！")
    print("=" * 60)

    conn = pymysql.connect(**DB_CONFIG)
    try:
        # 1. 添加字段
        add_column(conn)

        # 2. 批量填充
        migrate(conn)

        # 3. 验证
        verify(conn)

    finally:
        conn.close()
        print("\nDone.")


if __name__ == '__main__':
    main()
