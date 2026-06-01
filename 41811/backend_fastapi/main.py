"""FastAPI 应用入口"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base

# 导入所有模型，确保 Base.metadata.create_all 能识别
from app.models.indicator import Indicator, IndicatorExecution, TableMetadata, ColumnMetadata
from app.models.core18 import Core18Indicator, Core18ExecutionLog
from app.models.monitoring import (
    Hospital, FourElementsMonitoringRecord,
    PersonnelViolation, InstitutionAnomaly, TechnologyWarning, EquipmentAnomaly,
)
from app.models.user import User
from app.models.admission import HospitalAdmissionStandard
from app.models.text2sql_log import Text2SQLLog

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="41811 医疗监管系统 API",
    description="四要素监管 + 十八项核心制度 + 指标管理",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 允许的源列表（与 CORSMiddleware 保持一致）
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:8002",
    "http://127.0.0.1:8002",
]


class CORSMiddlewareFix(BaseHTTPMiddleware):
    """
    确保所有响应（包括 307 重定向）都带上 CORS 头。
    FastAPI 的 CORSMiddleware 不处理由路由产生的重定向响应，
    导致浏览器跨域请求失败。
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        origin = request.headers.get("origin", "")
        if origin and origin in ALLOWED_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
        return response


app.add_middleware(CORSMiddlewareFix)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import dashboard, monitoring, indicators, core18, core18_overview, core18_analysis, system, report, core18_indicator_config

app.include_router(dashboard.router, prefix="/api/dashboard")
app.include_router(monitoring.router, prefix="/api/monitoring")
app.include_router(indicators.router, prefix="/api/indicators")
app.include_router(core18.router, prefix="/api/core18")
app.include_router(core18_overview.router, prefix="/api/core18")
app.include_router(core18_analysis.router, prefix="/api/core18")
app.include_router(core18_indicator_config.router, prefix="/api/core18")
app.include_router(system.router, prefix="/api/system")
app.include_router(report.router, prefix="/api/report")


@app.get("/")
def root():
    return {"message": "41811 医疗监管系统 API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health():
    return {"ok": True, "service": "FastAPI Backend"}
