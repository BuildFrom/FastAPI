import os
from passlib.context import CryptContext

SECRET_KEY: str = os.getenv("SECRET_KEY") or ""
ALGORITHM: str = os.getenv("ALGORITHM") or ""
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 7 * 24 * 60))
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
