"""Pydantic Schema - 用户管理"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime as dt


class UserBase(BaseModel):
    username: str
    real_name: str = ""
    role: str = "viewer"
    scope_type: str = "province"
    scope_hospital_id: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    real_name: Optional[str] = None
    role: Optional[str] = None
    scope_type: Optional[str] = None
    scope_hospital_id: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    created_at: Optional[dt] = None
    updated_at: Optional[dt] = None

    model_config = {"from_attributes": True}
