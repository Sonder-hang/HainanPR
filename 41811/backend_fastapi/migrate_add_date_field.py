"""添加 date_field 列到 indicator_execution 表"""
import pymysql

# 连接参数
conn = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="123456",
    database="hainan_41811",
    charset="utf8mb4",
)
cursor = conn.cursor()

try:
    # 检查列是否存在
    cursor.execute("DESCRIBE `indicator_execution`")
    columns = [row[0] for row in cursor.fetchall()]
    if "date_field" not in columns:
        cursor.execute(
            "ALTER TABLE `indicator_execution` ADD COLUMN `date_field` VARCHAR(20) DEFAULT NULL AFTER `time_value`"
        )
        conn.commit()
        print("成功添加 date_field 列到 indicator_execution 表")
    else:
        print("date_field 列已存在，无需修改")
except Exception as e:
    print(f"错误: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()
