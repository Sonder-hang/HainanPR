"""路径与运行参数（LLM、数据库、SSH 隧道等在此修改）。"""
import os
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent

TABLES_JSON = ROOT / "tables.json"
INDICATORS_JSON = ROOT / "指标.json"
PROMPT_LOG_JSON = ROOT / "prompt_log.json"
EXTRACT_TABLES_SCRIPT = ROOT / "extract_tables.py"
LOG_DIR = ROOT / "logs"
STATIC_DIR = ROOT / "static"

PREVIEW_ROW_LIMIT = 200
LOG_PREVIEW_ROW_LIMIT = 10
SQL_RETRY_MAX = 3
# 分子分母比值型一次返回两条 SQL，MySQL 校验更难通过；单独提高重试上限（固定次数，非死循环）
SQL_RETRY_MAX_DUAL = 10

SQL_CACHE_ENABLED = True
SQL_CACHE_MAX_ENTRIES = 64

PROMPT_MAX_COLUMNS_PER_TABLE: Optional[int] = 500

# —— OpenAI 兼容 API ——
# 修改为本地大模型配置
OPENAI_API_KEY = "EMPTY"
OPENAI_BASE_URL = "http://10.114.255.26:9233/v1"
OPENAI_MODEL = "qwen"
# 采样温度；0 有利于相同输入下输出稳定（仍非所有网关/后端 100% 比特级可复现）
OPENAI_TEMPERATURE = 0.0
# 若网关支持 Chat Completions 的 seed，可设固定整数以增强可复现性；不支持时保持 None，避免多余参数
OPENAI_SEED: Optional[int] = None
OPENAI_TIMEOUT_SEC = 120.0
OPENAI_HTTP_TRUST_ENV = False

# —— SSH 隧道（自动建立，无需手动开终端） ——
SSH_TUNNEL_ENABLED = True                 # 设为 False 则直连 MySQL，不走隧道
SSH_HOST = "172.20.137.65"               # 跳板机 / 服务器 IP
SSH_PORT = 22133                         # SSH 端口
SSH_USER = "ubuntu"                      # SSH 用户名
# 认证二选一：填密码则不用私钥；私钥非空则同时可传（通常只配置一种）
# 生产环境建议 export TEXT2SQL_SSH_PASSWORD=...，不在仓库里写明文
SSH_PASSWORD = os.environ.get("TEXT2SQL_SSH_PASSWORD", "Tiankong1234")
SSH_KEY_PATH = ""                        # 私钥路径（支持 ~ 展开）；留空则仅用密码
SSH_REMOTE_BIND = ("127.0.0.1", 3306)    # 服务器上 MySQL 监听的地址和端口

# —— MySQL ——
# 修改为远程真实的医疗数据库
MYSQL_HOST = "10.114.96.57"
MYSQL_PORT = 12881
MYSQL_USER = "huali@tenant_xwjg"
MYSQL_PASSWORD = "H@3.14lia"
MYSQL_DATABASE = "xwjg_yw"
MYSQL_CONNECT_TIMEOUT_SEC = 10
MYSQL_READ_TIMEOUT_SEC = 120