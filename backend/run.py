import uvicorn
import os

if __name__ == "__main__":
    # 数据库通过环境变量覆盖
    import tempfile
    db_path = os.getenv("EMP_DB_PATH", os.path.join(tempfile.gettempdir(), "emp_mgmt_employees.db"))
    os.environ.setdefault("DATABASE_URL", f"sqlite:///{db_path}")
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "true") == "true",
    )
