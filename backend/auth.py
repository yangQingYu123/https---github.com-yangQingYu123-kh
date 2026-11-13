import os
import jwt
from datetime import datetime, timedelta
from fastapi import Header, HTTPException

SECRET = os.getenv("JWT_SECRET", "emp-mgmt-dev-secret-change-me")
ALGO = "HS256"
EXP_HOURS = 12


def create_token(username: str) -> str:
    payload = {
        "sub": username,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=EXP_HOURS),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def verify_token(authorization: str = Header(default="")) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供认证令牌")
    token = authorization[7:]
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="令牌已过期")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="令牌无效")


def login(username: str, password: str) -> dict:
    """账号 admin / 密码 admin123"""
    if username == "admin" and password == "admin123":
        return {"token": create_token(username), "username": username}
    return {}
