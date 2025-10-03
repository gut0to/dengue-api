# app/main.py
from fastapi import FastAPI
from app.api.v1 import auth, admin

app = FastAPI(title="Dengue API - SQLModel", version="1.0.0")

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])