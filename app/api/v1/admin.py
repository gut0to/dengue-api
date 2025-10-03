from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from jose import jwt, JWTError
from app.models.user import User
from app.schemas.user import UserOut
from app.db.session import get_session
from app.core.config import settings

router = APIRouter()

def get_current_user(token: str, session: Session):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
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
    return [
        UserOut(
            id=u.id,
            email=u.email,
            role=u.role,
            is_active=u.is_active,
            two_factor_enabled=u.two_factor_enabled,
        )
        for u in users
    ]

@router.patch("/users/{user_id}/role")
def update_role(user_id: int, role: str, token: str, session: Session = Depends(get_session)):
    require_gestor(token, session)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    user.role = role
    session.add(user)
    session.commit()
    return {"msg": "Perfil atualizado"}

@router.patch("/users/{user_id}/2fa")
def toggle_2fa(user_id: int, enabled: bool, token: str, session: Session = Depends(get_session)):
    require_gestor(token, session)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    user.two_factor_enabled = enabled
    session.add(user)
    session.commit()
    return {"msg": "2FA atualizado"}

@router.delete("/users/{user_id}")
def delete_user(user_id: int, token: str, session: Session = Depends(get_session)):
    require_gestor(token, session)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    session.delete(user)
    session.commit()
    return {"msg": "Usuário excluído"}
