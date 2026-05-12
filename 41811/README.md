# 41811 医疗监管系统

医院数据指标管理系统，包含四要素监管、十八项核心制度指标管理、Text2SQL 数据查询等功能。

## 项目架构

```
41811/
├── backend_fastapi/          # FastAPI 后端服务（主 API）
│   ├── app/                 # 应用核心代码
│   │   ├── models/         # SQLAlchemy 数据模型
│   │   ├── routers/        # API 路由
│   │   ├── schemas/        # Pydantic 数据验证
│   │   └── services/       # 业务逻辑服务
│   ├── Hainan_SQL-main/    # Text2SQL 服务模块
│   │   └── text2sql_app/   # 自然语言转 SQL
│   ├── main.py             # FastAPI 入口
│   ├── requirements.txt     # Python 依赖
│   └── .env                # 环境变量配置
├── my-vue-app/             # Vue 3 前端
│   ├── src/
│   │   ├── api/            # API 调用封装
│   │   ├── components/     # 可复用组件
│   │   ├── views/           # 页面视图
│   │   ├── router/         # 路由配置
│   │   ├── stores/          # Pinia 状态管理
│   │   └── utils/          # 工具函数
│   └── package.json
├── rebuild_tables.py        # 数据库表重建脚本
└── migrate_to_mysql.py      # SQLite → MySQL 数据迁移脚本
```

## 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue 3 + TypeScript + Vite + TailwindCSS | SPA 单页应用 |
| 后端 | FastAPI + SQLAlchemy + Pydantic | Python REST API |
| 数据库 | MySQL 8.0 | 主数据库 |
| Text2SQL | FastAPI + LLM API | 自然语言转 SQL |
| 图表 | ECharts | 数据可视化 |

## 环境要求

- Python 3.9+
- Node.js 18+
- MySQL 8.0+
- Git

## 一、初次拿到项目（快速上手）

> 按以下顺序执行，最快 10 分钟跑起来。

### 1.1 安装基础环境

| 工具 | 版本 | 说明 |
|------|------|------|
| Python | 3.9+ | 后端运行环境 |
| Node.js | 18+ | 前端构建 |
| MySQL | 8.0+ | 主数据库 |

### 1.2 启动 MySQL，创建数据库

```sql
-- 登录 MySQL
mysql -u root -p

-- 创建数据库
CREATE DATABASE hainan_41811 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 1.3 修改脚本中的数据库密码

`rebuild_tables.py` 和 `backend_fastapi/.env` 中的 MySQL 密码目前是 `123456`。如果你的 MySQL 密码不同，需要修改以下文件：

**修改 `rebuild_tables.py`（第 3 行）：**
```python
DEST = dict(host="127.0.0.1", user="root", password="你的密码", database="hainan_41811", charset="utf8mb4")
```

**修改 `backend_fastapi/.env`（DATABASE_URL 行）：**
```env
DATABASE_URL=mysql+pymysql://root:你的密码@127.0.0.1:3306/hainan_41811
```

> 后续新增模型后也只需改这两处，然后重新运行 `rebuild_tables.py` 即可。

### 1.4 重建数据库表（首次必须）

```bash
python rebuild_tables.py
```

> 此脚本会**删除并重建** `hainan_41811` 数据库中的所有表，建完后数据库为空。

### 1.5 插入种子数据（可选）

如果 `backend_fastapi/db.sqlite3` 中有数据，执行迁移脚本：

```bash
python migrate_to_mysql.py
```

### 1.6 启动后端

```bash
cd backend_fastapi
pip install -r requirements.txt
python main.py
```

服务启动后访问 http://localhost:8000/docs 查看 API 文档。

### 1.7 启动 Text2SQL 服务（如需自然语言查询）

```bash
cd backend_fastapi/Hainan_SQL-main/text2sql_app
pip install -r requirements.txt
python run.py
```

### 1.8 启动前端

```bash
cd my-vue-app
npm install
npm run dev
```

访问 http://localhost:5173

---

## 二、后续维护

### 修改了模型文件怎么办

每次修改 `backend_fastapi/app/models/` 下的文件后，执行以下两步：

```bash
# 1. 重建所有表（破坏性，会清空数据）
python rebuild_tables.py

# 2. 恢复种子数据（如果有）
python migrate_to_mysql.py
```

### 完整部署清单

| 步骤 | 命令 | 说明 |
|------|------|------|
| 1 | 在 MySQL 创建数据库 | `CREATE DATABASE hainan_41811...` |
| 2 | 修改脚本中的密码 | `rebuild_tables.py` + `backend_fastapi/.env` |
| 3 | 安装后端依赖 | `cd backend_fastapi && pip install -r requirements.txt` |
| 4 | 重建数据库表 | `python rebuild_tables.py` |
| 5 | 迁移种子数据 | `python migrate_to_mysql.py`（可选） |
| 6 | 启动后端 | `cd backend_fastapi && python main.py` |
| 7 | 安装 Text2SQL 依赖 | `cd backend_fastapi/Hainan_SQL-main/text2sql_app && pip install -r requirements.txt` |
| 8 | 启动 Text2SQL | `python run.py` |
| 9 | 安装前端依赖 | `cd my-vue-app && npm install` |
| 10 | 启动前端 | `cd my-vue-app && npm run dev` |

---

## 三、数据库说明

| 表名 | 说明 |
|------|------|
| `user` | 用户信息表，含权限（全省/医院级） |
| `indicator` | 四要素 + 十八项指标库 |
| `indicator_execution` | 四要素查询记录 |
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
| `hospital_admission_standard` | 医院准入标准（含资质图片） |
| `text2sql_log` | Text2SQL 日志 |

## 二、后端部署

### 2.1 安装依赖

```bash
cd backend_fastapi
pip install -r requirements.txt
```

主要依赖：
- fastapi
- uvicorn
- sqlalchemy
- pymysql
- python-multipart
- pydantic

### 2.2 配置环境变量

编辑 `backend_fastapi/.env`：

```env
# 数据库配置
DATABASE_URL=mysql+pymysql://root:123456@127.0.0.1:3306/hainan_41811

# Text2SQL 服务地址（本地运行时）
TEXT2SQL_BACKEND_URL=http://127.0.0.1:8001

# LLM API 配置（根据实际填写）
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.example.com/v1
LLM_MODEL=gpt-4o
```

### 2.3 启动后端服务

```bash
cd backend_fastapi
python main.py
# 或使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## 三、Text2SQL 服务部署

Text2SQL 模块提供自然语言转 SQL 的能力，位于 `backend_fastapi/Hainan_SQL-main/text2sql_app/`。

### 3.1 安装依赖

```bash
cd backend_fastapi/Hainan_SQL-main/text2sql_app
pip install -r requirements.txt
```

主要依赖：
- fastapi
- uvicorn
- httpx
- pymysql
- openai（或其他 LLM SDK）

### 3.2 配置

编辑 `backend_fastapi/Hainan_SQL-main/text2sql_app/config.py` 或设置环境变量：

```python
# MySQL 连接配置
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "123456"
MYSQL_DATABASE = "hainan_41811"

# LLM API
OPENAI_API_KEY = "your_api_key"
OPENAI_BASE_URL = "https://api.openai.com/v1"
MODEL_NAME = "gpt-4o"

# SSH 隧道（可选，远程服务器时使用）
SSH_TUNNEL_ENABLED = False
```

### 3.3 启动 Text2SQL 服务

```bash
cd backend_fastapi/Hainan_SQL-main/text2sql_app
python run.py
# 或
python main.py
```

服务启动后访问：
- 主界面：http://localhost:8001
- API 文档：http://localhost:8001/docs

## 四、前端部署

### 4.1 安装依赖

```bash
cd my-vue-app
npm install
```

### 4.2 配置

编辑 `my-vue-app/.env`：

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_TEXT2SQL_URL=http://localhost:8001
```

### 4.3 开发模式

```bash
cd my-vue-app
npm run dev
```

访问：http://localhost:5173

### 4.4 生产构建

```bash
cd my-vue-app
npm run build
```

构建产物输出到 `dist/`，可部署到 Nginx 等 Web 服务器。

Nginx 配置示例：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/my-vue-app/dist;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

## 五、Docker 部署（可选）

### 5.1 后端 Docker 镜像构建

```bash
cd backend_fastapi
docker build -t 41811-backend .
docker run -d -p 8000:8000 --env-file .env 41811-backend
```

### 5.2 Docker Compose

```bash
cd backend_fastapi
docker-compose up -d
```

## 六、快速启动脚本

项目根目录提供了一键启动脚本（Windows PowerShell）：

```powershell
# 启动所有服务
.\start_local.ps1

# 停止所有服务
.\stop_local.ps1
```

## 七、目录说明

### 7.1 后端 API（backend_fastapi/app/routers/）

| 路由文件 | 说明 |
|------|------|
| `indicators.py` | 指标管理（四要素 + 十八项）CRUD |
| `core18.py` | 十八项核心制度 API |
| `monitoring.py` | 四要素监管数据 API |
| `dashboard.py` | 仪表盘数据 API |
| `report.py` | 报表中心 API |
| `system.py` | 系统管理 API |

### 7.2 前端页面（my-vue-app/src/views/）

| 目录 | 说明 |
|------|------|
| `indicatorManagement/` | 指标管理页面（含大模型新增） |
| `indicatorExecution/` | 指标执行页面 |
| `institution/` | 机构监管 |
| `personnel/` | 人员监管 |
| `technology/` | 技术监管 |
| `modules/` | 各模块主视图 |
| `analysis/` | 数据分析 |
| `statistics/` | 统计报表 |
| `reportCenter/` | 报表中心 |
| `dashboard/` | 仪表盘 |
| `comparison/` | 数据对比 |

### 7.3 数据库相关脚本

| 文件 | 说明 |
|------|------|
| `rebuild_tables.py` | 删除重建所有表（破坏性） |
| `migrate_to_mysql.py` | SQLite 数据迁移到 MySQL |

> 注意：修改了模型文件（models/*.py）后，需要重新运行 `rebuild_tables.py` 重建表结构，然后 `migrate_to_mysql.py` 恢复数据。

## 八、常见问题

### Q: 启动后端报错 `ModuleNotFoundError`
确保在正确的虚拟环境中运行：
```bash
cd backend_fastapi
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### Q: SQL 执行报错 `You have an error in your SQL syntax`
检查 SQL 末尾是否有 `);` 或多余的 `LIMIT`，相关修复见 `sql_runner.py`。

### Q: Text2SQL 服务连接失败
确认 Text2SQL 服务已启动（端口 8001），并检查 `.env` 中的 `TEXT2SQL_BACKEND_URL` 配置正确。

### Q: 数据库表结构与模型不一致
运行 `rebuild_tables.py` 重建表结构，然后 `migrate_to_mysql.py` 恢复数据：
```bash
python rebuild_tables.py
python migrate_to_mysql.py
```

### Q: 前端无法访问后端 API
确认后端服务在 8000 端口运行，前端 `.env` 中 `VITE_API_BASE_URL` 指向正确的地址。

## 九、项目维护

### 添加新数据库表

1. 在 `backend_fastapi/app/models/` 下创建新模型文件
2. 在 `backend_fastapi/app/schemas/` 下创建对应的 Pydantic Schema
3. 在 `main.py` 中 import 新模型
4. 运行 `rebuild_tables.py` 重建表
5. 迁移数据：`python migrate_to_mysql.py`（如有已有数据）

### 添加新 API 路由

1. 在 `backend_fastapi/app/routers/` 下创建新路由文件
2. 在 `backend_fastapi/main.py` 中 include 该 router
3. 重启后端服务

### 修改指标

指标数据存储在 `indicator` 表中，分为 `four`（四要素）和 `core18`（十八项）两种类型，通过 `indicator_type` 字段区分。
