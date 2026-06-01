# 41811 医疗监管系统

医院数据指标管理系统，包含四要素监管、十八项核心制度指标管理、Text2SQL 数据查询等功能。

## 项目架构

```
41811/
├── backend_fastapi/              # FastAPI 后端服务
│   ├── app/
│   │   ├── models/             # SQLAlchemy 数据模型
│   │   ├── routers/            # API 路由
│   │   ├── schemas/            # Pydantic 数据验证
│   │   ├── services/           # 业务逻辑服务
│   │   ├── tasks/              # Celery 异步任务
│   │   └── celery_app.py       # Celery 配置
│   ├── main.py                 # FastAPI 入口（python -m uvicorn main:app）
│   ├── requirements.txt         # Python 依赖
│   └── .env                    # 环境变量配置
├── my-vue-app/                 # Vue 3 前端
│   ├── src/
│   │   ├── api/               # API 调用封装
│   │   ├── components/        # 可复用组件
│   │   ├── composables/       # Vue 组合式函数（hooks）
│   │   ├── views/             # 页面视图
│   │   ├── router/            # 路由配置
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── data/              # 静态配置文件（cascader 数据等）
│   │   └── utils/             # 工具函数
│   ├── package.json
│   └── vite.config.ts
├── rebuild_tables.py           # 数据库表重建脚本
├── migrate_to_mysql.py        # SQLite → MySQL 数据迁移脚本
└── hainan-18core-latest.sql  # 数据库初始化 SQL
```

## 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue 3 + TypeScript + Vite + TailwindCSS | SPA 单页应用 |
| 后端 | FastAPI + SQLAlchemy + Pydantic | Python REST API |
| 数据库 | MySQL 8.0 | 主数据库 |
| 异步任务 | Celery + Redis | 指标执行异步化，多用户并发支持 |
| Text2SQL | FastAPI + LLM API | 自然语言转 SQL |
| 图表 | ECharts | 数据可视化 |

## 核心流程：指标执行异步化

用户点击"执行指标"时，系统使用 **Celery + Redis** 实现异步处理：

```
用户点"执行"
     ↓
后端接口(8001) → 把任务写入 Redis → 立即返回 task_id（页面不卡住）
     ↓
Celery Worker(后台) ← 从 Redis 拿任务 → 真正执行 SQL
     ↓
执行结果写入 MySQL
     ↓
前端每 2.5 秒轮询 task_id 状态 → 完成后自动更新页面
```

**好处：**
- 页面不卡住，用户可以正常操作
- 多用户同时执行，互不干扰（Worker 默认 10 个并发）
- 服务器重启后任务不丢失（队列在 Redis 中持久化）

## 环境要求

- Python 3.9+
- Node.js 18+
- MySQL 8.0+
- Redis（指标执行异步化必须）
- Git

---

## 一、初次上手

### 1.1 安装基础环境

| 工具 | 版本 | 说明 |
|------|------|------|
| Python | 3.9+ | 后端运行环境 |
| Node.js | 18+ | 前端构建 |
| MySQL | 8.0+ | 主数据库 |
| Redis | 6.0+ | 异步任务队列（新增） |

### 1.2 安装 Redis

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis

# 验证
redis-cli ping
# 返回 PONG 表示正常
```

### 1.3 启动 MySQL，创建数据库

```sql
mysql -u root -p

CREATE DATABASE hainan_41811 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 1.4 修改数据库密码

`rebuild_tables.py` 和 `backend_fastapi/.env` 中的 MySQL 密码目前是 `123456`，如果不同需要修改：

**`rebuild_tables.py`（第 3 行）：**
```python
DEST = dict(host="127.0.0.1", user="root", password="你的密码", database="hainan_41811", charset="utf8mb4")
```

**`backend_fastapi/.env`（DATABASE_URL 行）：**
```env
DATABASE_URL=mysql+pymysql://root:你的密码@127.0.0.1:3306/hainan_41811
```

### 1.5 导入数据库初始化 SQL

```bash
mysql -u root -p hainan_41811 < hainan-18core-latest.sql
```

> 此 SQL 文件包含所有表结构和十八项核心制度指标的初始配置。

### 1.6 启动后端

```bash
cd backend_fastapi
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

> 后端地址：http://localhost:8001
> API 文档：http://localhost:8001/docs

### 1.7 启动 Celery Worker（指标执行异步化，必须）

```bash
cd backend_fastapi
python3 -m celery -A app.celery_app worker --loglevel=info
```

> Worker 启动后会自动连接到 Redis，默认 10 个并发进程处理指标执行任务。

### 1.8 启动前端

```bash
cd my-vue-app
npm install
npm run dev
```

访问 http://localhost:5173

---

## 二、完整部署清单

| 步骤 | 命令 | 说明 |
|------|------|------|
| 1 | 在 MySQL 创建数据库 | `CREATE DATABASE hainan_41811...` |
| 2 | 安装 Redis 并启动 | `brew services start redis` |
| 3 | 修改密码 | `rebuild_tables.py` + `.env` |
| 4 | 安装后端依赖 | `cd backend_fastapi && pip install -r requirements.txt` |
| 5 | 导入数据库初始化 SQL | `mysql -u root -p hainan_41811 < hainan-18core-latest.sql` |
| 6 | 启动后端 | `python -m uvicorn main:app --port 8001` |
| 7 | 启动 Celery Worker | `python3 -m celery -A app.celery_app worker --loglevel=info` |
| 8 | 启动前端 | `cd my-vue-app && npm run dev` |

---

## 三、Celery + Redis 详解

### 3.1 它们的作用

- **Redis**：任务队列的消息中间件，存放待执行的任务和结果
- **Celery**：异步任务执行框架，Worker 从 Redis 拿任务、处理、更新结果

### 3.2 配置说明

`backend_fastapi/.env` 中的配置：

```env
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
```

服务器部署时将 `127.0.0.1` 换成实际 Redis 地址。

### 3.3 控制并发数

默认 10 个并发进程同时处理任务，可按服务器配置调整：

```bash
# 4 个并发
python3 -m celery -A app.celery_app worker --loglevel=info --concurrency=4

# 100 个并发
python3 -m celery -A app.celery_app worker --loglevel=info --concurrency=100
```

### 3.4 进程管理（线上推荐用 Supervisor）

```ini
# /etc/supervisor/conf.d/celery.conf
[program:celery]
command=cd /path/to/backend_fastapi && python3 -m celery -A app.celery_app worker --loglevel=info --concurrency=4
directory=/path/to/backend_fastapi
autostart=true
autorestart=true
stderr_logfile=/var/log/celery.err.log
stdout_logfile=/var/log/celery.out.log
```

### 3.5 断网服务器部署

服务器无法联网时，需要先在有网的机器上打包依赖：

```bash
# 有网机器上下载所有包
mkdir wheelhouse
pip download "celery[redis]" redis -d wheelhouse/
tar -czvf wheelhouse.tar.gz wheelhouse/

# 服务器上传后安装
pip install --no-index --find-links=wheelhouse "celery[redis]" redis
```

或使用 Docker（推荐）：

```bash
docker run -d --name redis -p 6379:6379 redis:7
```

### 3.6 不装 Redis/Celery 能否运行

可以。系统完全兼容同步模式，只是指标执行时页面会"等待"较长时间，没有异步体验。只需不启动 Celery Worker 即可。

---

## 四、数据库说明

| 表名 | 说明 |
|------|------|
| `user` | 用户信息表，含权限（全省/医院级） |
| `indicator` | 四要素 + 十八项指标库 |
| `indicator_execution` | 指标执行记录（含排行榜 subitem_data） |
| `core18_indicator` | 十八项核心制度指标定义 |
| `core18_execution_log` | 十八项查询记录 |
| `hospital` | 医院数据库（含 hospital_code） |
| `four_elements_monitoring_record` | 四要素监控记录 |
| `personnel_violation` | 人员违规子表 |
| `institution_anomaly` | 机构异常子表 |
| `technology_warning` | 技术异常子表 |
| `equipment_anomaly` | 设备异常子表 |
| `table_metadata` | 四大库表元数据 |
| `column_metadata` | 四大库字段元数据 |
| `hospital_admission_standard` | 医院准入标准 |
| `text2sql_log` | Text2SQL 日志 |

---

## 五、后端 API 路由说明

| 路由文件 | 说明 |
|------|------|
| `indicators.py` | 指标管理 CRUD + 异步执行 |
| `core18.py` | 十八项核心制度 API |
| `core18_indicator_config.py` | 十八项指标分析台配置与数据 API |
| `core18_overview.py` | 十八项总览数据 API |
| `monitoring.py` | 四要素监管数据 API |
| `dashboard.py` | 仪表盘数据 API |
| `report.py` | 报表中心 API |
| `system.py` | 系统管理 API |

**异步执行相关接口：**

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/indicators/execute/` | 提交异步执行任务，返回 task_id |
| GET | `/api/indicators/execution/task/{task_id}` | 轮询任务状态 |
| GET | `/api/indicators/execution/{id}/detail` | 拉取执行结果详情 |
| GET | `/api/indicators/execution/by-hospital/` | 按医院查询执行记录 |

**指标分析台相关接口：**

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/core18/indicator-config/` | 获取指标配置列表（含模板类型） |
| GET | `/api/core18/indicator-data/` | 获取指标图表数据（排行榜/趋势/医院对比） |

---

## 六、前端页面说明

| 目录 | 说明 |
|------|------|
| `indicatorManagement/` | 指标管理页面（含大模型新增） |
| `indicatorExecution/` | 指标执行页面（异步轮询） |
| `core18IndicatorFinal/` | 十八项指标分析台（排行榜/趋势/医院对比） |
| `core18Overview/` | 十八项总览仪表盘 |
| `institution/` | 机构监管 |
| `personnel/` | 人员监管 |
| `technology/` | 技术监管 |
| `modules/` | 四要素各模块主视图（人员/机构/技术/设备） |
| `analysis/` | 数据分析 |
| `statistics/` | 统计报表 |
| `reportCenter/` | 报表中心 |
| `dashboard/` | 仪表盘 |
| `comparison/` | 数据对比 |

---

## 七、常见问题

### Q: 指标执行页面没有反应？
确认 Celery Worker 已启动：
```bash
python3 -m celery -A app.celery_app worker --loglevel=info
```

### Q: `ModuleNotFoundError`
```bash
cd backend_fastapi
pip install -r requirements.txt
```

### Q: Redis 连接失败
确认 Redis 已启动：
```bash
redis-cli ping  # 应返回 PONG
```

### Q: SQL 执行报错
检查 SQL 末尾是否有多余分号，相关修复见 `sql_runner.py`。

### Q: Text2SQL 连接失败
确认 Text2SQL 服务已启动，并检查 `.env` 中的 `TEXT2SQL_BACKEND_URL`。

### Q: 排行榜没有数据？
- 确认指标已在"指标管理"页面执行过
- 执行记录需要包含 `subitem_data`（排行榜子项数据），明细级 SQL（无 GROUP BY 聚合）可能无法生成排行榜数据
- 检查数据库 `indicator_execution` 表中对应记录的 `subitem_data` 字段是否有数据

### Q: 修改了模型文件
```bash
python rebuild_tables.py      # 重建表结构（会清空数据）
python migrate_to_mysql.py    # 恢复数据（如果有）
# 或重新导入初始化 SQL：
mysql -u root -p hainan_41811 < hainan-18core-latest.sql
```

---

## 八、项目维护

### 添加新数据库表

1. 在 `backend_fastapi/app/models/` 下创建新模型
2. 在 `backend_fastapi/app/schemas/` 下创建 Pydantic Schema
3. 在 `main.py` 中 import 新模型
4. 重新导入初始化 SQL 或运行迁移脚本

### 添加新 API 路由

1. 在 `backend_fastapi/app/routers/` 下创建路由文件
2. 在 `main.py` 中 include 该 router
3. 重启后端服务

### 添加新指标

1. 在数据库 `indicator` 表中插入新记录，或在管理页面通过 UI 添加
2. 设置正确的 `indicator_type`（`core18` / `four_elements`）
3. 配置 `template_type`（`STRUCTURE` / `RATE` / `COMPOSITE` 等）
4. 编写 SQL 并在指标执行页面执行
