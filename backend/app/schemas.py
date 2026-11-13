from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional, List


class EmployeeBase(BaseModel):
    emp_no: str = Field(..., min_length=1, max_length=32, description="工号")
    name: str = Field(..., min_length=1, max_length=64, description="姓名")
    department: str = Field(..., min_length=1, max_length=64, description="部门")
    position: str = Field("", max_length=64)
    phone: str = Field("", max_length=20)
    hire_date: date
    status: str = Field("active", pattern="^(active|resigned)$")

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("姓名不能为空")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def phone_digits(cls, v: str) -> str:
        if v and not v.isdigit():
            raise ValueError("手机号必须为数字")
        if v and len(v) != 11:
            raise ValueError("手机号必须为 11 位")
        return v


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    emp_no: Optional[str] = None
    name: Optional[str] = Field(None, min_length=1, max_length=64)
    department: Optional[str] = Field(None, min_length=1, max_length=64)
    position: Optional[str] = ""
    phone: Optional[str] = None
    hire_date: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^(active|resigned)$")


class EmployeeOut(EmployeeBase):
    id: int

    class Config:
        from_attributes = True


class EmployeeList(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[EmployeeOut]


class LoginReq(BaseModel):
    username: str
    password: str


class LoginRes(BaseModel):
    token: str
    username: str


class StatsItem(BaseModel):
    department: str
    count: int
    avg_days: float


class StatsRes(BaseModel):
    items: List[StatsItem]
