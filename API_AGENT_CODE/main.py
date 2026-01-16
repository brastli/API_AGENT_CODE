from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
import time

import db

app = FastAPI(title="API Agent (MySQL Enabled)")


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: str | None = Field(default=None, max_length=255)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: str | None = Field(default=None, max_length=255)


@app.on_event("startup")
def on_startup():
    # DB 必须可用
    if not db.ping_db():
        raise RuntimeError("DB ping failed")

    # 把 API 名字/方式/路径写入 api_registry
    # 先查有没有！！！
    entries = []
    for r in app.routes:
        methods = getattr(r, "methods", None)
        path = getattr(r, "path", None)
        name = getattr(r, "name", None)
        if not methods or not path:
            continue
        for m in methods:
            if m in {"HEAD", "OPTIONS"}:
                continue
            entries.append((name or "", m, path))
    if entries:
        db.upsert_api_registry(entries)


@app.middleware("http")
async def audit_middleware(request, call_next):
    start = time.time()
    resp = await call_next(request)
    latency_ms = int((time.time() - start) * 1000)

    # 每次请求写审计日志：证明 API 确实 call DB
    try:
        db.insert_audit_log(request.method, request.url.path, resp.status_code, latency_ms)
    except Exception:
        pass

    return resp


@app.get("/")
def root():
    return {"message": "Hello, World! (DB enabled)"}


@app.get("/db/health")
def db_health():
    return {"db_ok": db.ping_db()}


# ---- users CRUD ----

@app.get("/users", tags=["users"])
def list_users(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    return {"items": db.fetch_users(limit=limit, offset=offset), "limit": limit, "offset": offset}


@app.get("/users/{user_id}", tags=["users"])
def get_user(user_id: int):
    row = db.fetch_user(user_id)
    if not row:
        raise HTTPException(status_code=404, detail="user not found")
    return row


@app.post("/users", tags=["users"])
def create_user(payload: UserCreate):
    try:
        new_id = db.create_user(payload.username, payload.email)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"create failed: {e}")
    return {"id": new_id, "username": payload.username, "email": payload.email}


@app.patch("/users/{user_id}", tags=["users"])
def patch_user(user_id: int, payload: UserUpdate):
    try:
        ok = db.update_user(user_id, payload.username, payload.email)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"update failed: {e}")
    if not ok:
        raise HTTPException(status_code=404, detail="user not found or no fields updated")
    return {"updated": True, "id": user_id}


@app.delete("/users/{user_id}", tags=["users"])
def remove_user(user_id: int):
    ok = db.delete_user(user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="user not found")
    return {"deleted": True, "id": user_id}
