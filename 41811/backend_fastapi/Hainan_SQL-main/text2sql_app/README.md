# Text-to-SQL 指标调试服务

医疗监管指标 SQL 生成与调试工具。支持三种指标类型（分子分母比值型 / 统计型 / 大模型分析型），通过 LLM 生成可执行 SQL 并在 MySQL 上验证。

## 快速启动

```bash
cd text2sql_app
pip install -r requirements.txt
python run.py
```

浏览器打开 http://127.0.0.1:8000

## 核心特性

- **三种指标类型**：分子分母比值型、统计型、大模型分析型
- **多轮对话迭代**：再生成时采用多轮对话模式，模型保留完整上下文，用户只需描述修改建议
- **会话日志链**：同一指标的多次迭代自动归入同一会话，日志页按会话分组展示每轮反馈与结果
- **Prompt 可编辑**：支持查看/修改 System Prompt 和 User Message，修改过的 Prompt 自动记录到 prompt_log.json
- **指标管理**：新增、编辑、删除指标，SQL 可手动修改并保存

## 多轮对话机制

1. **首次生成**：发送完整 System Prompt + User Message 给模型
2. **再生成**：将之前所有轮次的模型回复和用户反馈组装为多轮消息，模型看到完整对话历史
3. **日志追踪**：同一会话内的所有轮次通过 `conversation_id` 关联，日志页自动分组展示

## 项目结构

```
text2sql_app/
├── run.py              # 启动入口
├── main.py             # FastAPI 应用（路由、业务逻辑）
├── config.py           # 所有配置（LLM、MySQL、SSH 隧道）
├── prompt_builder.py   # Prompt 构建与指标管理
├── llm_client.py       # LLM 调用（支持单轮/多轮对话）
├── sql_runner.py       # MySQL 执行（自动 SSH 隧道）
├── sql_cache.py        # SQL LRU 缓存
├── logging_utils.py    # 日志工具（按 conversation_id 分组）
├── extract_tables.py   # 提取数据库表结构到 tables.json
├── 指标.json            # 指标定义与已保存的 SQL
├── tables.json         # 数据库表结构描述
├── prompt_log.json     # 修改过的 Prompt 历史记录
├── requirements.txt    # Python 依赖
├── static/
│   ├── index.html      # 主页（指标选择/新增/编辑/SQL 生成与测试）
│   └── log.html        # 日志查看页（按会话分组，展示多轮对话）
└── logs/               # 运行日志（workflow_YYYYMMDD.jsonl）
```

## 配置

编辑 `config.py`，主要参数：

- **LLM**：`OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL`
- **SSH 隧道**：`SSH_TUNNEL_ENABLED`、`SSH_HOST`、`SSH_PORT`、`SSH_USER`、`SSH_PASSWORD`（可用环境变量 `TEXT2SQL_SSH_PASSWORD` 覆盖）或 `SSH_KEY_PATH`（二选一）
- **MySQL**：`MYSQL_USER`、`MYSQL_PASSWORD`、`MYSQL_DATABASE`

SSH 隧道启用后自动建立，无需手动操作。

## 页面

- `/` — 指标调试主页（选择/新增/编辑指标、生成 SQL、测试、保存）
- `/log` — 工作流日志（按会话分组，展示多轮迭代链路）
