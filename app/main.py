from fastapi import FastAPI
from sqlmodel import SQLModel
from app.api.v1 import auth, admin
from app.db.session import engine

app = FastAPI(title="Dengue API - SQLModel", version="1.0.0")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
