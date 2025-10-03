# app/db/session.py
from sqlmodel import create_engine, Session
from app.core.config import settings

DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def get_session():
    with Session(engine) as session:
        yield session