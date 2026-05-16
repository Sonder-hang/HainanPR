import sys
sys.path.insert(0, '.')
from sql_runner import execute_full

cols, rows, err = execute_full("SELECT MDC_ORG_CD, MDC_ORG_NM FROM DIM_MDC_ORG LIMIT 5")
print("Columns:", cols)
print("Rows:", rows)
print("Error:", err)
