import pymysql
import json
from collections import Counter

conn = pymysql.connect(
    host='127.0.0.1', port=3306, user='root',
    password='22013232', database='hainan',
    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as cur:
    cur.execute(
        "SELECT id, name, calc_type FROM indicator WHERE indicator_type='core18' ORDER BY seq"
    )
    rows = cur.fetchall()
conn.close()

with open('../my-vue-app/src/data/cascader-unified.json', 'r', encoding='utf-8') as f:
    cascader = json.load(f)

cascader_map = {}
for level1 in cascader:
    for level2 in (level1.get('children') or []):
        for ind in (level2.get('children') or []):
            cascader_map[ind['value']] = ind['label']

template_rules = {
    'deathPatientDefinition': 'STRUCTURE',
    'deathDiseaseSpectrum': 'STRUCTURE',
    'deathSurgicalSpectrum': 'STRUCTURE',
    'icd10Subcategories': 'STRUCTURE',
    'icd9Cm3Categories': 'STRUCTURE-special',
    'overallMortalityRate': 'COMPOSITE',
    'perioperativeMortality': 'COMPOSITE',
    'unexpectedRehospitalizationAnalysis': 'COMPOSITE',
    'unplannedReturnToORAnalysis': 'COMPOSITE',
    'complicationRateRatio': 'RATE-special',
    'mortalityRateRatio': 'RATE-special',
    'surgicalComplication': 'RATE',
}

lines = []
lines.append(f'DB count: {len(rows)}, cascader count: {len(cascader_map)}')
lines.append('')
lines.append(f"{'DB_ID':>5} | {'calc':<8} | {'cascader_key':<40} | template_type")
lines.append('-' * 90)

unmatched_db = []
all_mapped = []

for r in rows:
    db_name = r['name']
    db_calc = r['calc_type']
    matched_key = None
    for key, label in cascader_map.items():
        if label == db_name:
            matched_key = key
            break
    if not matched_key:
        for key, label in cascader_map.items():
            if len(label) >= 8 and db_name.startswith(label[:8]):
                matched_key = key
                break
    if matched_key:
        if matched_key in template_rules:
            tt = template_rules[matched_key]
        elif db_calc == 'count':
            tt = 'STRUCTURE'
        else:
            tt = 'RATE'
        lines.append(f"{r['id']:>5} | {db_calc:<8} | {matched_key:<40} | {tt}")
        all_mapped.append(tt)
    else:
        lines.append(f"{r['id']:>5} | {db_calc:<8} | {'[UNMATCHED]':<40} | ???")
        unmatched_db.append((r['id'], r['name'], db_calc))
        all_mapped.append('UNKNOWN')

lines.append('')
lines.append('=== TEMPLATE STATS ===')
for t, cnt in sorted(Counter(all_mapped).items()):
    lines.append(f'  {t}: {cnt}')
lines.append('')
lines.append('=== DB INDICATORS NOT IN CASCADER ===')
for uid, uname, ucalc in unmatched_db:
    lines.append(f'  ID={uid} | calc_type={ucalc} | {uname}')
lines.append('')
lines.append('=== CASCADER KEYS NOT IN DB ===')
cascader_in_db = {}
for r in rows:
    for key, label in cascader_map.items():
        if label == r['name'] or (len(label) >= 8 and r['name'].startswith(label[:8])):
            cascader_in_db[key] = True
            break
for key, label in cascader_map.items():
    if key not in cascader_in_db:
        lines.append(f'  key={key} | label={label}')

output = '\n'.join(lines)
print(output)
with open('mapping_result.txt', 'w', encoding='utf-8') as f:
    f.write(output)
