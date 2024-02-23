from datetime import datetime, timedelta
import os
from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from uuid import uuid4
from .constants import SECRET_KEY, bcrypt_context
from .database import get_db, save

# ------------------------ #

def get_uuid():
    return str(uuid4())[:8]
    
# ------------------------ #

def jwt_decode(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None

# ------------------------ #
    
def jwt_encode(data: dict):
    try:
        payload = jwt.encode(data, SECRET_KEY, algorithm="HS256")
        return payload
    except JWTError:
        return None

# ------------------------ #

def get_hashed_password(password):
    return bcrypt_context.hash(password)

# ------------------------ #

def verify_password(password, hashed_password):
    return bcrypt_context.verify(password, hashed_password)

# ------------------------ #

async def create_access_token(data: dict, expires_delta: timedelta, db=None, user_id=None):
    json_payload = data.copy()
    expire = datetime.utcnow() + expires_delta
    json_payload.update({"exp": expire})
    return jwt_encode(json_payload)         

# ------------------------ #

def response(content, status_code):
    return JSONResponse(content=content, status_code=status_code)

def error(status_code, detail):
    return response({"error": detail}, status_code)

# ------------------------ #

async def get_user_by_email(db, email):
    query = "SELECT * FROM users WHERE email = %s"
    db.execute(query, (email,))
    return db.fetchone()

# ------------------------ #

async def get_user_by_id(db, user_id):
    query = "SELECT * FROM users WHERE id = %s"
    db.execute(query, (user_id,))
    return db.fetchone()

# ------------------------ #

async def get_all_users(db):
    query = "SELECT * FROM users"
    db.execute(query)
    return db.fetchall()

# ------------------------ #

async def protected_route(request: Request, db=Depends(get_db)):
    token = request.cookies.get("token")
    if token:
        scan = "SELECT * FROM blacklist WHERE token = %s"
        db.execute(scan, (token,))
        investigation = db.fetchone()
        if investigation is not None:
            error(401, "Unauthorized")
    return True