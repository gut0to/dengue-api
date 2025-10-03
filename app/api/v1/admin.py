# app/api/v1/admin.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from jose import jwt, JWTError
from app.models.user import User
from app.schemas.user import UserOut, UserUpdateRole, UserToggle2FA
from app.db.session import get_session
from app.core.config import settings

router = APIRouter()

def get_current_user(token: str, session: Session):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise JWTError()
    except JWTError:
        raise HTTPException(status_code=401, detail="Não autenticado")
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Não autenticado")
    return user

def require_gestor(token: str, session: Session):
    user = get_current_user(token, session)
    if user.role != "gestor":
        raise HTTPException(status_code=403, detail="Acesso negado")
    return user

@router.get("/users", response_model=list[UserOut])
def list_users(token: str, session: Session = Depends(get_session)):
    require_gestor(token, session)
    users = session.exec(select(User)).all()
    return users

@router.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, token: str, session: Session = Depends(get_session)):
    require_gestor(token, session)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@router.put("/users/{user_id}/role")
def update_user_role(user_id: int, update_data: UserUpdateRole, token: str, session: Session = Depends(get_session)):
    require_gestor(token, session)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if update_data.role not in ["usuario", "gestor"]:
        raise HTTPException(status_code=400, detail="Função inválida")
    user.role = update_data.role
    session.add(user)
    session.commit()
    return {"msg": f"Função atualizada para {update_data.role}"}

@router.post("/users/{user_id}/toggle-2fa")
def toggle_2fa(user_id: int, update_data: UserToggle2FA, token: str, session: Session = Depends(get_session)):
    require_gestor(token, session)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    user.two_factor_enabled = update_data.two_factor_enabled
    session.add(user)
    session.commit()
    status_str = "ativado" if update_data.two_factor_enabled else "desativado"
    return {"msg": f"2FA {status_str} para {user.email}"}

@router.delete("/users/{user_id}")
def delete_user(user_id: int, token: str, session: Session = Depends(get_session)):
    require_gestor(token, session)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    session.delete(user)
    session.commit()
    return {"msg": "Usuário excluído"}