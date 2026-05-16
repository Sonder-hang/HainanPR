import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# 模拟 API 函数逻辑
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. 测试本地数据库
print("=== 测试本地数据库 ===")
from backend_fastapi.app.database import SessionLocal
from backend_fastapi.app.models.monitoring import Hospital

db = SessionLocal()
try:
    local_hospitals = db.query(Hospital).filter(Hospital.is_active == 1).order_by(Hospital.name).all()
    print(f"本地医院数量: {len(local_hospitals)}")
    for h in local_hospitals:
        print(f"  - id={h.id}, code={h.hospital_code}, name={h.name}")
finally:
    db.close()

# 2. 测试远程数据库
print("\n=== 测试远程数据库 ===")
sql_runner_path = r"d:\41811_fullstack\41811\backend_fastapi\Hainan_SQL-main\text2sql_app\sql_runner.py"
sys.path.insert(0, str(sql_runner_path.parent))
try:
    from sql_runner import execute_full
    sql = "SELECT MDC_ORG_CD, MDC_ORG_NM FROM DIM_MDC_ORG ORDER BY MDC_ORG_NM"
    cols, rows, err = execute_full(sql)
    print(f"列: {cols}")
    print(f"行数: {len(rows)}")
    if rows:
        print(f"第一条: {rows[0]}")
    if err:
        print(f"错误: {err}")
finally:
    sys.path.remove(str(sql_runner_path.parent))
