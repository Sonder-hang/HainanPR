"""
数据库迁移脚本：为 indicator 表补充分子/分母时间字段。
用于修复 ORM 模型新增字段后，旧数据库表缺列导致的查询报错。
"""
import pymysql

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "22013232",
    "database": "hainan",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


COLUMNS_TO_ADD = [
    (
        "numerator_date_field",
        "VARCHAR(50) DEFAULT NULL COMMENT '分子时间过滤字段' AFTER `date_field`",
    ),
    (
        "denominator_date_field",
        "VARCHAR(50) DEFAULT NULL COMMENT '分母时间过滤字段' AFTER `numerator_date_field`",
    ),
]


def ensure_columns(conn):
    with conn.cursor() as cur:
        cur.execute("DESCRIBE indicator")
        existing = {row["Field"] for row in cur.fetchall()}

        for column_name, column_ddl in COLUMNS_TO_ADD:
            if column_name in existing:
                print(f">>> {column_name} 已存在，跳过。")
                continue

            print(f">>> 添加 {column_name} 字段...")
            cur.execute(f"ALTER TABLE indicator ADD COLUMN {column_name} {column_ddl}")
            conn.commit()
            print(f"    {column_name} 添加成功。")


def backfill_defaults(conn):
    with conn.cursor() as cur:
        print(">>> 用 date_field 回填空的 numerator_date_field / denominator_date_field ...")
        cur.execute(
            """
            UPDATE indicator
            SET
                numerator_date_field = COALESCE(numerator_date_field, date_field),
                denominator_date_field = COALESCE(denominator_date_field, date_field)
            WHERE numerator_date_field IS NULL OR denominator_date_field IS NULL
            """
        )
        affected = cur.rowcount
        conn.commit()
        print(f"    已回填 {affected} 条记录。")


def verify(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) AS total,
                   SUM(CASE WHEN numerator_date_field IS NOT NULL THEN 1 ELSE 0 END) AS numerator_filled,
                   SUM(CASE WHEN denominator_date_field IS NOT NULL THEN 1 ELSE 0 END) AS denominator_filled
            FROM indicator
            """
        )
        row = cur.fetchone()
        print(">>> 校验结果：")
        print(f"    total={row['total']}")
        print(f"    numerator_filled={row['numerator_filled']}")
        print(f"    denominator_filled={row['denominator_filled']}")


if __name__ == "__main__":
    conn = pymysql.connect(**DB_CONFIG)
    try:
        ensure_columns(conn)
        backfill_defaults(conn)
        verify(conn)
    finally:
        conn.close()
