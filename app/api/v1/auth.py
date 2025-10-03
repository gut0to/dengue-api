from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from app.db.session import get_session
from app.models.user import User
from app.schemas.user import (
    UserCreate, UserLogin, Token, ConfirmAccount,
    ResetPasswordRequest, ResetPasswordConfirm, TwoFactorVerify
)
from app.core.security import verify_password, get_password_hash, create_access_token, generate_token
from app.core.config import settings
from app.utils.email import email_sender

router = APIRouter()

two_factor_codes: dict[str, dict] = {}

@router.post("/register")
def register(user_in: UserCreate, background: BackgroundTasks, session: Session = Depends(get_session)):
    exists = session.exec(select(User).where(User.email == user_in.email)).first()
    if exists:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role or "usuario",
        is_active=False,
        two_factor_enabled=False,
        confirmation_token=generate_token(),
        reset_token=None,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    token = user.confirmation_token
    background.add_task(
        email_sender.send_email,
        to=user.email,
        subject="Confirme sua conta",
        html_body=f'<p>Confirme sua conta: <a href="http://localhost:8000/api/v1/auth/confirm?token={token}">Confirmar</a></p>',
        text_body=f"Token de confirmação: {token}",
    )
    return {"msg": "Usuário criado. Verifique seu e-mail."}

@router.post("/confirm")
def confirm(data: ConfirmAccount, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.confirmation_token == data.token)).first()
    if not user:
        raise HTTPException(status_code=400, detail="Token inválido")
    user.is_active = True
    user.confirmation_token = None
    session.add(user)
    session.commit()
    return {"msg": "Conta confirmada"}

@router.post("/login", response_model=Token)
def login(data: UserLogin, background: BackgroundTasks, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == data.email)).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Credenciais inválidas")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Confirme seu e-mail")
    if user.two_factor_enabled:
        code = f"{generate_token()[:6]}"
        two_factor_codes[user.email] = {"code": code, "exp": datetime.utcnow() + timedelta(minutes=10)}
        background.add_task(
            email_sender.send_email,
            to=user.email,
            subject="Código 2FA",
            html_body=f"<p>Seu código 2FA: <b>{code}</b></p>",
            text_body=f"Código 2FA: {code}",
        )
        return {"access_token": "", "token_type": "2fa_pending"}
    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/two-factor/verify", response_model=Token)
def two_factor_verify(data: TwoFactorVerify, session: Session = Depends(get_session)):
    entry = two_factor_codes.get(data.email)
    if not entry or entry["code"] != data.code or entry["exp"] < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Código inválido ou expirado")
    user = session.exec(select(User).where(User.email == data.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    two_factor_codes.pop(data.email, None)
    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password")
def forgot_password(data: ResetPasswordRequest, background: BackgroundTasks, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == data.email)).first()
    if not user:
        return {"msg": "Se existir, enviaremos instruções de recuperação"}
    user.reset_token = generate_token()
    session.add(user)
    session.commit()
    token = user.reset_token
    background.add_task(
        email_sender.send_email,
        to=user.email,
        subject="Redefinição de Senha",
        html_body=f'<p>Redefina sua senha: <a href="http://localhost:8000/api/v1/auth/reset-password?token={token}">Redefinir</a></p>',
        text_body=f"Token de redefinição: {token}",
    )
    return {"msg": "Se existir, enviaremos instruções de recuperação"}

@router.post("/reset-password")
def reset_password(data: ResetPasswordConfirm, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.reset_token == data.token)).first()
    if not user:
        raise HTTPException(status_code=400, detail="Token inválido")
    user.hashed_password = get_password_hash(data.new_password)
    user.reset_token = None
    session.add(user)
    session.commit()
    return {"msg": "Senha redefinida"}
