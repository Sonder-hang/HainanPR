import pymysql
pymysql.install_as_MySQLdb()

conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    password='22013232',
    database='hainan',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as cur:
    cur.execute("SELECT id, name, calc_type, category, status FROM indicator WHERE indicator_type='core18' ORDER BY seq")
    rows = cur.fetchall()

print(f'总指标数: {len(rows)}')
print()
print(f"{'ID':>3} | {'calc_type':<10} | {'category':<15} | name")
print('-' * 75)
for r in rows:
    print(f"{r['id']:>3} | {r['calc_type']:<10} | {str(r['category']):<15} | {r['name']}")
conn.close()
