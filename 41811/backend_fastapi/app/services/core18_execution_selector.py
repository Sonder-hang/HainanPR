from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.indicator import IndicatorExecution


PROVINCE_PLACEHOLDER = "province"


def is_province_scope(hospital_code: Optional[str]) -> bool:
    return not hospital_code or hospital_code == PROVINCE_PLACEHOLDER


def execution_matches_hospital(execution: IndicatorExecution, hospital_code: str) -> bool:
    return bool(
        execution.group_by_hospital
        and isinstance(execution.hospital_codes, list)
        and hospital_code in execution.hospital_codes
    )


def pick_latest_execution_for_scope(
    executions: list[IndicatorExecution],
    hospital_code: Optional[str],
) -> Optional[IndicatorExecution]:
    if not executions:
        return None

    if is_province_scope(hospital_code):
        non_grouped = [execution for execution in executions if not execution.group_by_hospital]
        if non_grouped:
            return max(non_grouped, key=lambda execution: execution.execution_time or datetime.min)
        return max(executions, key=lambda execution: execution.execution_time or datetime.min)

    matched = [
        execution
        for execution in executions
        if execution_matches_hospital(execution, hospital_code)
    ]
    if not matched:
        return None
    return max(matched, key=lambda execution: execution.execution_time or datetime.min)


def get_latest_execution_for_scope(
    db: Session,
    indicator_id: int,
    time_mode: str,
    time_value: Optional[str],
    hospital_code: Optional[str],
) -> Optional[IndicatorExecution]:
    query = db.query(IndicatorExecution).filter(
        IndicatorExecution.indicator_id == indicator_id,
        IndicatorExecution.status == "success",
        IndicatorExecution.time_mode == time_mode,
    )
    if time_value:
        query = query.filter(IndicatorExecution.time_value == time_value)

    executions = query.all()
    return pick_latest_execution_for_scope(executions, hospital_code)


def get_latest_trend_executions_by_time_value(
    db: Session,
    indicator_id: int,
    time_mode: str,
    time_values: list[str],
    hospital_code: Optional[str],
) -> dict[str, IndicatorExecution]:
    if not time_values:
        return {}

    executions = db.query(IndicatorExecution).filter(
        IndicatorExecution.indicator_id == indicator_id,
        IndicatorExecution.status == "success",
        IndicatorExecution.time_mode == time_mode,
        IndicatorExecution.time_value.in_(time_values),
    ).all()

    executions_by_time_value: dict[str, list[IndicatorExecution]] = {}
    for execution in executions:
        if not execution.time_value:
            continue
        executions_by_time_value.setdefault(execution.time_value, []).append(execution)

    latest_by_time_value: dict[str, IndicatorExecution] = {}
    for time_value, grouped_executions in executions_by_time_value.items():
        picked = pick_latest_execution_for_scope(grouped_executions, hospital_code)
        if picked is not None:
            latest_by_time_value[time_value] = picked

    return latest_by_time_value


def get_all_grouped_executions(
    db: Session,
    indicator_id: int,
    time_mode: str,
    time_value: Optional[str],
) -> list[IndicatorExecution]:
    """
    返回所有满足条件的分组执行记录（group_by_hospital=True）。
    不同医院的分组数据可能分散在多条执行记录中（如每次只跑部分医院），
    因此需要返回所有记录，由调用方合并 hospital_results。
    """
    query = db.query(IndicatorExecution).filter(
        IndicatorExecution.indicator_id == indicator_id,
        IndicatorExecution.status == "success",
        IndicatorExecution.time_mode == time_mode,
        IndicatorExecution.group_by_hospital.is_(True),
    )
    if time_value:
        query = query.filter(IndicatorExecution.time_value == time_value)

    executions = query.all()
    if not executions:
        return []

    return sorted(executions, key=lambda e: e.execution_time or datetime.min, reverse=True)


def get_latest_grouped_execution(
    db: Session,
    indicator_id: int,
    time_mode: str,
    time_value: Optional[str],
) -> Optional[IndicatorExecution]:
    """
    兼容旧接口：返回所有匹配记录中最新的那条（单个医院/单次查询场景仍可用）。
    """
    executions = get_all_grouped_executions(db, indicator_id, time_mode, time_value)
    return executions[0] if executions else None
