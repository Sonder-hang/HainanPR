# 数据库迁移脚本使用说明

## 迁移内容

为 `indicator` 表添加 `template_type` 字段，并批量填充现有 43 个 core18 指标的模板类型。

字段可选值：`STRUCTURE | STRUCTURE-special | RATE | RATE-special | COMPOSITE`

## 前置条件

```bash
conda activate mark-fatsapi
cd 41811/backend_fastapi/migrations
```

## 执行迁移

```bash
python migrate_template_type_20250523.py
```

脚本会自动完成以下步骤：
1. 检查并添加 `template_type` 字段（如已存在则跳过）
2. 根据映射表批量填充每个指标的模板类型
3. 输出验证结果

## 验证结果

```python
python -c "
import pymysql
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='22013232', database='hainan', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
with conn.cursor() as cur:
    cur.execute(\"SELECT COALESCE(template_type,'NULL') as tt, COUNT(*) as cnt FROM indicator WHERE indicator_type='core18' GROUP BY template_type ORDER BY cnt DESC\")
    for r in cur.fetchall(): print(r)
conn.close()
"
```

期望输出：

| template_type | count |
|---|---|
| RATE | 32 |
| STRUCTURE | 4 |
| COMPOSITE | 4 |
| RATE-special | 2 |
| STRUCTURE-special | 1 |
| **TOTAL** | **43** |

## 回滚（如需）

```sql
UPDATE indicator SET template_type = NULL WHERE indicator_type = 'core18';
-- 或完全删除字段（谨慎操作）：
-- ALTER TABLE indicator DROP COLUMN template_type;
```

## 注意事项

- 生产环境执行前务必在测试环境验证
- 脚本幂等，多次执行安全
