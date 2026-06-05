"""Celery 应用配置"""
import os
from celery import Celery

# 默认 Redis 地址，生产环境通过环境变量覆盖
_default_broker = os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
_default_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/0")

celery_app = Celery(
    "hainan_tasks",
    broker=_default_broker,
    backend=_default_backend,
    include=["app.tasks.indicator_tasks"],
)

# 任务结果过期时间：24 小时
celery_app.conf.result_expires = 60 * 60 * 24

# 任务序列化方式
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]

# 任务队列
celery_app.conf.task_default_queue = "default"

# 任务执行超时
celery_app.conf.task_soft_time_limit = 600  # 10 分钟软超时
celery_app.conf.task_time_limit = 660       # 11 分钟硬超时

# 防止任务重复执行
celery_app.conf.task_acks_late = True
celery_app.conf.worker_prefetch_multiplier = 1
