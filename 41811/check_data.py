"""快速诊断脚本：检查四要素执行记录的数据情况"""
import pymysql

conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    password='0826',
    database='hainan_41811',
    charset='utf8mb4'
)
cursor = conn.cursor(pymysql.cursors.DictCursor)

# 1. 检查有多少 kind=four 的执行记录
cursor.execute("SELECT COUNT(*) as cnt FROM indicator_execution WHERE kind='four'")
row = cursor.fetchone()
print(f"kind=four 执行记录总数: {row['cnt']}")

# 2. 查看最新几条
cursor.execute("""
    SELECT id, indicator_id, indicator_name, status, numerator_count,
           LEFT(preview_data, 200) as preview_data_str, execution_time
    FROM indicator_execution
    WHERE kind='four'
    ORDER BY execution_time DESC
    LIMIT 5
""")
rows = cursor.fetchall()
print(f"\n最新 5 条 kind=four 记录:")
for r in rows:
    pd = r['preview_data_str']
    print(f"  id={r['id']}, ind_id={r['indicator_id']}, status={r['status']}, "
          f"num_cnt={r['numerator_count']}, time={r['execution_time']}")
    print(f"    preview_data={pd[:100] if pd else 'NULL'}...")

# 3. 检查 indicator 表中 id 7-14 的指标
print("\n指标表 id 7-14:")
cursor.execute("SELECT id, name, category FROM indicator WHERE id BETWEEN 7 AND 14")
for r in cursor.fetchall():
    print(f"  id={r['id']}, name={r['name']}, category={r['category']}")

# 4. 检查 technology 模块的 rules 对应的 indicator_id 是否在 DB 中有执行记录
print("\n各规则对应的执行记录:")
for rule_id, ind_id in [(7,7),(8,8),(9,9),(10,10),(11,11),(12,12),(13,13),(14,14)]:
    cursor.execute("""
        SELECT COUNT(*) as cnt, MAX(numerator_count) as max_num,
               MAX(execution_time) as latest
        FROM indicator_execution
        WHERE indicator_id=%s AND kind='four' AND status='success'
    """, (ind_id,))
    r = cursor.fetchone()
    print(f"  规则 r{ind_id} (ind_id={ind_id}): count={r['cnt']}, max_num={r['max_num']}, latest={r['latest']}")

conn.close()
