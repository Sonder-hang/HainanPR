"""FastAPI 应用入口"""
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router, prefix="/api/dashboard")
app.include_router(monitoring.router, prefix="/api/monitoring")
app.include_router(indicators.router, prefix="/api/indicators")
app.include_router(core18.router, prefix="/api/core18")
app.include_router(system.router, prefix="/api/system")
app.include_router(report.router, prefix="/api/report")


@app.get("/")
def root():
    return {"message": "41811 医疗监管系统 API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health():
    return {"ok": True, "service": "FastAPI Backend"}
