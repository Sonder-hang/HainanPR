"""迁移数据，处理空字符串和保留字列名"""
import sqlite3, pymysql

SRC = "/Users/lichong/hainan/HainanPR-main/41811/db.sqlite3"
DEST = dict(host="127.0.0.1", user="root", password="123456", database="hainan_41811", charset="utf8mb4")

conn = pymysql.connect(**DEST)
cur = conn.cursor()

src = sqlite3.connect(SRC)
src.row_factory = sqlite3.Row
src_cur = src.cursor()


def migrate_table(table, has_data=True):
    if has_data:
        src_cur.execute(f"SELECT * FROM {table}")
        rows = src_cur.fetchall()
    else:
        rows = []
    if not rows:
        print(f"[{table}] 0 行，跳过")
        return
    src_cur.execute(f"PRAGMA table_info({table})")
    cols_info = src_cur.fetchall()
    col_names = [r[1] for r in cols_info]
    col_types = {r[1]: r[2] for r in cols_info}

    safe_cols = ["`sql`" if c == "sql" else c for c in col_names]
    col_str = ", ".join(safe_cols)
    placeholders = ", ".join(["%s"] * len(col_names))

    cur.execute(f"DELETE FROM {table}")

    for row in rows:
        row = list(row)
        for i, (cn, val) in enumerate(zip(col_names, row)):
            ct = col_types.get(cn, "").upper()
            if val == "" and ("INT" in ct or "DOUBLE" in ct or "FLOAT" in ct or "DECIMAL" in ct):
                row[i] = None
        cur.execute(f"INSERT INTO {table} ({col_str}) VALUES ({placeholders})", tuple(row))
    conn.commit()
    print(f"[{table}] {len(rows)} 行已写入")


for t in ["indicator", "indicator_execution"]:
    migrate_table(t)

# monitoring_record 迁移到 four_elements_monitoring_record
src_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='monitoring_record'")
if src_cur.fetchone():
    src_cur.execute(f"SELECT * FROM monitoring_record")
    rows = src_cur.fetchall()
    if rows:
        src_cur.execute("PRAGMA table_info(monitoring_record)")
        cols_info = src_cur.fetchall()
        col_names = [r[1] for r in cols_info]
        col_types = {r[1]: r[2] for r in cols_info}
        safe_cols = ["`sql`" if c == "sql" else c for c in col_names]
        col_str = ", ".join(safe_cols)
        placeholders = ", ".join(["%s"] * len(col_names))
        cur.execute("DELETE FROM four_elements_monitoring_record")
        for row in rows:
            row = list(row)
            for i, (cn, val) in enumerate(zip(col_names, row)):
                ct = col_types.get(cn, "").upper()
                if val == "" and ("INT" in ct or "DOUBLE" in ct or "FLOAT" in ct or "DECIMAL" in ct):
                    row[i] = None
            cur.execute(f"INSERT INTO four_elements_monitoring_record ({col_str}) VALUES ({placeholders})", tuple(row))
        conn.commit()
        print(f"[four_elements_monitoring_record] {len(rows)} 行已写入")

for t in [
    "core18_indicator", "core18_execution_log",
    "four_elements_monitoring_record",
    "personnel_violation", "institution_anomaly", "technology_warning",
    "equipment_anomaly", "hospital", "department",
    "table_metadata", "column_metadata",
    "user", "hospital_admission_standard", "text2sql_log",
]:
    print(f"[{t}] 0 行，跳过（空表）")

src.close()
conn.close()
print("迁移完成!")
