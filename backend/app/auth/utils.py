import hashlib, secrets
from datetime import datetime, timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from app.config import JWT_SECRET, JWT_EXPIRE_MINUTES

ph = PasswordHasher()

def normalize_email(email: str) -> str:
    return email.strip().lower()

def hash_password(pw: str) -> str:
    return ph.hash(pw)

def verify_password(pw: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, pw)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False

def create_access_token(user_id: int) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    return jwt.encode({'sub': str(user_id), 'exp': exp}, JWT_SECRET, algorithm='HS256')

def decode_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return int(payload['sub'])
    except Exception:
        return None

def make_reset_token() -> tuple[str, str]:
    tok = secrets.token_urlsafe(32)
    return tok, hashlib.sha256(tok.encode()).hexdigest()

def hash_reset_token(tok: str) -> str:
    return hashlib.sha256(tok.encode()).hexdigest()

def reset_token_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=1)
