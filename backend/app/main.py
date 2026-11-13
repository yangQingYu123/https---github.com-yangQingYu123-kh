import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import Employee, SessionLocal, init_db
from auth import verify_token, login
from app import schemas

app = FastAPI(title="员工管理系统 API", version="1.0.0")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="员工管理系统 API", version="1.0.0", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def session_middleware(request, call_next):
    request.state.db = SessionLocal()
    try:
        response = await call_next(request)
    except Exception:
        try:
            request.state.db.rollback()
        except Exception:
            pass
        raise
    finally:
        try:
            request.state.db.close()
        except Exception:
            pass
        SessionLocal.remove()
    return response


def resp(code: int = 0, msg: str = "ok", data=None):
    return {"code": code, "msg": msg, "data": data}


def conn(request: Request) -> Session:
    return request.state.db


@app.exception_handler(HTTPException)
async def http_handler(request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code,
                        content=resp(code=exc.status_code, msg=exc.detail, data=None))


@app.exception_handler(RequestValidationError)
async def validation_handler(request, exc: RequestValidationError):
    errors = []
    for e in exc.errors():
        loc = ".".join(str(x) for x in e["loc"][1:])
        errors.append({"field": loc or "body", "msg": e["msg"]})
    return JSONResponse(status_code=422,
                        content=resp(code=422, msg="参数校验失败", data=errors))


@app.post("/api/login")
def do_login(req: schemas.LoginReq):
    result = login(req.username, req.password)
    if not result:
        raise HTTPException(status_code=401, detail="账号或密码错误")
    return resp(data=result)


@app.get("/api/ping")
def ping(user: str = Depends(verify_token)):
    return resp(data={"user": user})


@app.get("/api/employees")
def list_employees(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    department: Optional[str] = None,
    db: Session = Depends(conn),
    _: str = Depends(verify_token),
):
    q = db.query(Employee)
    if keyword:
        like = f"%{keyword}%"
        q = q.filter((Employee.name.like(like)) | (Employee.emp_no.like(like)))
    if department:
        q = q.filter(Employee.department == department)
    total = q.count()
    items = (q.order_by(Employee.id.desc())
              .offset((page - 1) * page_size)
              .limit(page_size)
              .all())
    return resp(data={"total": total, "page": page, "page_size": page_size,
                      "items": [_to_dict(e) for e in items]})


@app.get("/api/employees/departments")
def list_departments(db: Session = Depends(conn), _: str = Depends(verify_token)):
    rows = db.query(Employee.department).distinct().order_by(Employee.department).all()
    return resp(data=[r[0] for r in rows])


@app.get("/api/employees/{emp_id}")
def get_employee(emp_id: int, db: Session = Depends(conn),
                 _: str = Depends(verify_token)):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail=f"员工 {emp_id} 不存在")
    return resp(data=_to_dict(emp))


@app.post("/api/employees", status_code=201)
def create_employee(payload: schemas.EmployeeCreate, db: Session = Depends(conn),
                    _: str = Depends(verify_token)):
    if db.query(Employee).filter(Employee.emp_no == payload.emp_no).first():
        raise HTTPException(status_code=409, detail=f"工号 {payload.emp_no} 已存在")
    emp = Employee(**payload.model_dump())
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return resp(data=_to_dict(emp))


@app.put("/api/employees/{emp_id}")
def update_employee(emp_id: int, payload: schemas.EmployeeUpdate,
                    db: Session = Depends(conn), _: str = Depends(verify_token)):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail=f"员工 {emp_id} 不存在")
    data = payload.model_dump(exclude_unset=True)
    if "emp_no" in data and data["emp_no"] != emp.emp_no:
        if db.query(Employee).filter(Employee.emp_no == data["emp_no"]).first():
            raise HTTPException(status_code=409, detail=f"工号 {data['emp_no']} 已存在")
    for k, v in data.items():
        setattr(emp, k, v)
    db.commit()
    db.refresh(emp)
    return resp(data=_to_dict(emp))


@app.delete("/api/employees/{emp_id}")
def delete_employee(emp_id: int, db: Session = Depends(conn),
                    _: str = Depends(verify_token)):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail=f"员工 {emp_id} 不存在")
    db.delete(emp)
    db.commit()
    return resp(data={"id": emp_id})


@app.get("/api/stats/departments")
def department_stats(db: Session = Depends(conn), _: str = Depends(verify_token)):
    today = date.today()
    rows = (db.query(Employee.department, func.count(Employee.id))
              .group_by(Employee.department)
              .order_by(Employee.department)
              .all())
    result = []
    for dept, count in rows:
        emps = db.query(Employee).filter(Employee.department == dept).all()
        avg_days = sum((today - e.hire_date).days for e in emps) / count
        result.append({"department": dept, "count": count, "avg_days": round(avg_days, 1)})
    return resp(data=result)


def _to_dict(e: Employee) -> dict:
    return {
        "id": e.id,
        "emp_no": e.emp_no,
        "name": e.name,
        "department": e.department,
        "position": e.position,
        "phone": e.phone,
        "hire_date": e.hire_date.isoformat() if e.hire_date else None,
        "status": e.status,
    }
