from datetime import datetime, timezone
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, PasswordResetToken
from app.schemas import RegisterIn, LoginIn, UserOut, TokenOut, ForgotIn, ResetIn, ProfileUpdateIn
from app.auth import utils
from app.auth.deps import get_current_user
from app import email_service
from app.config import FRONTEND_RESET_URL

log = logging.getLogger('fnds')
router = APIRouter(prefix='/api/auth', tags=['auth'])

def _user_out(u: User, db: Session):
    from app.models import Prediction
    n = db.query(Prediction).filter(Prediction.user_id == u.id).count()
    return UserOut(id=u.id, full_name=u.full_name, email=u.email,
                   created_at=u.created_at.isoformat() if u.created_at else '', analyses=n)

@router.post('/register', response_model=UserOut)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    email = utils.normalize_email(body.email)
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail='An account with this email already exists. Please log in instead.')
    u = User(full_name=body.full_name.strip(), email=email,
             password_hash=utils.hash_password(body.password))
    db.add(u); db.commit(); db.refresh(u)
    return _user_out(u, db)

@router.post('/login', response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    email = utils.normalize_email(body.email)
    u = db.query(User).filter(User.email == email).first()
    if not u or not utils.verify_password(body.password, u.password_hash):
        raise HTTPException(status_code=401, detail='Incorrect email or password.')
    return TokenOut(access_token=utils.create_access_token(u.id))

@router.get('/me', response_model=UserOut)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _user_out(user, db)

@router.put('/profile', response_model=UserOut)
def update_profile(body: ProfileUpdateIn, user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    if not body.full_name.strip():
        raise HTTPException(status_code=400, detail='Please enter your full name.')
    user.full_name = body.full_name.strip()
    db.commit(); db.refresh(user)
    return _user_out(user, db)

@router.post('/forgot-password')
def forgot(body: ForgotIn, db: Session = Depends(get_db)):
    # Fail uniformly (no account enumeration) if the mail service is down/misconfigured.
    if not email_service.smtp_configured():
        log.error('Forgot-password requested but SMTP is not configured.')
        raise HTTPException(status_code=503,
                            detail='Password reset email service is currently unavailable. Please try again later.')
    email = utils.normalize_email(body.email)
    u = db.query(User).filter(User.email == email).first()
    if u:
        tok, th = utils.make_reset_token()
        db.add(PasswordResetToken(user_id=u.id, token_hash=th,
                                  expires_at=utils.reset_token_expiry()))
        db.commit()
        link = f'{FRONTEND_RESET_URL}?token={tok}'
        try:
            email_service.send_password_reset_email(email, link)
        except Exception:
            log.error('Failed to send password reset email (SMTP error).')
            raise HTTPException(status_code=503,
                                detail='Password reset email service is currently unavailable. Please try again later.')
    return {'message': 'If an account exists for this email, a reset link has been sent.'}

@router.post('/reset-password')
def reset(body: ResetIn, db: Session = Depends(get_db)):
    th = utils.hash_reset_token(body.token)
    row = db.query(PasswordResetToken).filter(PasswordResetToken.token_hash == th).first()
    now = datetime.now(timezone.utc)
    if not row:
        raise HTTPException(status_code=400, detail='Invalid reset token.')
    if row.used_at is not None:
        raise HTTPException(status_code=400, detail='This reset link has already been used.')
    exp = row.expires_at
    if exp is not None and exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if exp is None or exp < now:
        raise HTTPException(status_code=400, detail='This reset link has expired.')
    u = db.query(User).filter(User.id == row.user_id).first()
    if not u:
        raise HTTPException(status_code=400, detail='Invalid reset token.')
    u.password_hash = utils.hash_password(body.new_password)
    row.used_at = now
    db.commit()
    return {'message': 'Password updated. You can now log in.'}
