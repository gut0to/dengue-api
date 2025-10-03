from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from datetime import datetime, timedelta
from app.schemas.user import (
    UserCreate, UserLogin, Token, ConfirmAccount,
    ResetPasswordRequest, ResetPasswordConfirm, TwoFactorVerify
)
from app.models.user import User
from app.db.session import get_session
from app.core.security import create_access_token, verify_password, get_password_hash, generate_token
from app.utils.email import email_sender

router = APIRouter()

two_factor_codes = {}

@router.post("/register", status_code=201)
async def register(user_data: UserCreate, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    if user_data.role not in ["usuario", "gestor"]:
        user_data.role = "usuario"
    
    confirmation_token = generate_token()
    hashed_pw = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_pw,
        role=user_data.role,
        is_active=False,
        confirmation_token=confirmation_token
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    await email_sender.send_email(
        to=user_data.email,
        subject="Confirme sua conta",
        html_body=f'<p>Clique para confirmar: <a href="http://localhost:8000/api/v1/auth/confirm?token={confirmation_token}">Confirmar conta</a></p>'
    )
    return {"msg": "Conta criada. Verifique seu e-mail para confirmar."}

@router.get("/confirm")
def confirm_account(token: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.confirmation_token == token)).first()
    if not user:
        raise HTTPException(status_code=400, detail="Token inválido")
    user.is_active = True
    user.confirmation_token = None
    session.add(user)
    session.commit()
    return {"msg": "Conta confirmada com sucesso!"}

@router.post("/login")
async def login(user: UserLogin, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.email == user.email)).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Credenciais inválidas")
    if not db_user.is_active:
        raise HTTPException(status_code=400, detail="Conta não confirmada")

    if db_user.two_factor_enabled:
        import secrets
        code = secrets.token_hex(3)[:6].upper()
        two_factor_codes[user.email] = {
            "code": code,
            "expires": datetime.utcnow() + timedelta(minutes=10)
        }
        await email_sender.send_email(
            to=user.email,
            subject="Código de Verificação (2FA)",
            html_body=f"<h2>Seu código: {code}</h2><p>Válido por 10 minutos.</p>"
        )
        return {"msg": "Código 2FA enviado para seu e-mail"}

    access_token = create_access_token(
        data={"sub": db_user.email, "role": db_user.role},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/verify-2fa")
def verify_2fa(data: TwoFactorVerify, session: Session = Depends(get_session)):
    stored = two_factor_codes.get(data.email)
    if not stored or stored["code"] != data.code or datetime.utcnow() > stored["expires"]:
        raise HTTPException(status_code=400, detail="Código inválido ou expirado")
    db_user = session.exec(select(User).where(User.email == data.email)).first()
    access_token = create_access_token(
        data={"sub": db_user.email, "role": db_user.role}
    )
    del two_factor_codes[data.email]
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/request-reset-password")
async def request_reset_password(request: ResetPasswordRequest, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == request.email)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    token = generate_token()
    user.reset_token = token
    session.add(user)
    session.commit()

    await email_sender.send_email(
        to=request.email,
        subject="Redefinição de Senha",
        html_body=f'<p>Clique para redefinir: <a href="http://localhost:8000/api/v1/auth/reset-password?token={token}">Redefinir senha</a></p>'
    )
    return {"msg": "E-mail de recuperação enviado"}

@router.post("/reset-password")
def reset_password(data: ResetPasswordConfirm, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.reset_token == data.token)).first()
    if not user:
        raise HTTPException(status_code=400, detail="Token inválido")
    user.hashed_password = get_password_hash(data.new_password)
    user.reset_token = None
    session.add(user)
    session.commit()
    return {"msg": "Senha redefinida com sucesso"}