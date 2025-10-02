from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="usuario")  
    is_active = Column(Boolean, default=False)  
    two_factor_enabled = Column(Boolean, default=False)
    confirmation_token = Column(String, nullable=True)
    reset_token = Column(String, nullable=True)