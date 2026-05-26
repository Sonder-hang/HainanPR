"""添加缺失的列到 indicator_execution 表"""
import pymysql

conn = pymysql.connect(host='127.0.0.1', user='root', password='0826', database='hainan_41811', charset='utf8mb4')
cur = conn.cursor()

# 检查现有列
cur.execute('DESCRIBE indicator_execution')
existing_cols = [r[0] for r in cur.fetchall()]

# 需要添加的列
new_columns = [
    ("hospital_codes", "JSON DEFAULT NULL COMMENT '执行时选中的医院代码列表'"),
    ("time_mode", "VARCHAR(20) DEFAULT NULL COMMENT 'monthly=月度, quarterly=季度'"),
    ("time_value", "VARCHAR(20) DEFAULT NULL COMMENT '如 2026-04 或 2026-Q1'"),
    ("date_field", "VARCHAR(20) DEFAULT NULL COMMENT 'discharge=出院时间, admission=入院时间'"),
    ("group_by_hospital", "TINYINT(1) DEFAULT 0 COMMENT '是否按医院分组执行'"),
    ("hospital_results", "JSON DEFAULT NULL COMMENT '各医院执行结果列表'"),
]

for col_name, col_def in new_columns:
    if col_name not in existing_cols:
        sql = f"ALTER TABLE indicator_execution ADD COLUMN {col_name} {col_def}"
        try:
            cur.execute(sql)
            print(f"已添加列: {col_name}")
        except Exception as e:
            print(f"添加列 {col_name} 失败: {e}")
    else:
        print(f"列已存在: {col_name}")

conn.commit()
conn.close()
print("\n迁移完成!")
