from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db.session import get_session
from app.api.deps import require_roles
from app.models.user import User
from app.schemas.user import UserOut, UserUpdateRole, UserToggle2FA

router = APIRouter()

@router.get("/users", response_model=list[UserOut])
def list_users(_: User = Depends(require_roles("gestor")),
               session: Session = Depends(get_session)):
    return session.exec(select(User)).all()

@router.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, _: User = Depends(require_roles("gestor")),
             session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@router.patch("/users/{user_id}/role")
def update_role(user_id: int, body: UserUpdateRole,
                _: User = Depends(require_roles("gestor")),
                session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if body.role not in {"usuario", "gestor"}:
        raise HTTPException(status_code=400, detail="Role inválida")
    user.role = body.role
    session.add(user)
    session.commit()
    return {"msg": f"Role atualizada", "email": user.email, "role": user.role}

@router.patch("/users/{user_id}/2fa")
def toggle_2fa(user_id: int, body: UserToggle2FA,
               _: User = Depends(require_roles("gestor")),
               session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    user.two_factor_enabled = body.two_factor_enabled
    session.add(user)
    session.commit()
    return {"msg": "2FA atualizado", "two_factor_enabled": user.two_factor_enabled}

@router.delete("/users/{user_id}")
def delete_user(user_id: int, _: User = Depends(require_roles("gestor")),
                session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    session.delete(user)
    session.commit()
    return {"msg": "Usuário excluído"}
