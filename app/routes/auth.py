from fastapi import APIRouter, Depends, Request
from datetime import timedelta, datetime

from fastapi.responses import JSONResponse
from ..models import User
from ..extensions.database import get_db, save
from ..extensions.constants import ACCESS_TOKEN_EXPIRE_MINUTES, bcrypt_context
from ..extensions.utils import create_access_token, get_uuid, get_hashed_password, jwt_decode, protected_route, response, error, get_user_by_email

router = APIRouter()

# ✅ ------------------------ #

@router.post("/register")
async def register_user(request: Request, db=Depends(get_db)):
    data = await request.json()
    form_data = User(**data)
    hashed_password = get_hashed_password(form_data.password)
    existing_user = await get_user_by_email(db, form_data.email)

    if existing_user:
        return response({"error": "User already exists"}, status_code=400)

    user_id = get_uuid()
    query = "INSERT INTO users (id, name, username, email, password, phone_number) VALUES (%s, %s, %s, %s, %s, %s)"

    if db is not None:
        db.execute(query, (user_id, form_data.name, form_data.username, form_data.email, hashed_password, form_data.phone_number))
        save.commit()

    registered_user = await get_user_by_email(db, form_data.email)
    access_token_data = {"sub": form_data.id}
    access_token = await create_access_token(access_token_data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) , user_id=user_id, db=db)

    return response({"Register User": registered_user, "access_token": access_token}, 200)

# ✅ ------------------------ #

@router.post("/login")
async def login_user(request: Request, db=Depends(get_db)):
    data = await request.json()
    form_data = User(**data)
    
    result = await get_user_by_email(db, form_data.email)

    user = User(**result)

    if not user:
        error(404, "User not found")

    if not bcrypt_context.verify(form_data.password, user.password):
        error(401, "Unauthorized")

    access_token_data = {"sub": user.id}
    access_token = await create_access_token(access_token_data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), user_id=user.id, db=db)

    if access_token is None:
        return JSONResponse(content={"error": "Unauthorized"}, status_code=401)

    response_data = {"Login User": result, "access_token": access_token}

    response = JSONResponse(content=response_data, status_code=200)
    response.set_cookie(key="token", value=access_token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    return response



# ------------------------ #

@router.post("/logout")
async def logout_user(request: Request, db=Depends(get_db), secure=Depends(protected_route)):
    try:
        token = request.cookies.get("token")

        await protected_route(request, db)

        if not token:
            return {"error": "Token is missing"}

        decoded_token = jwt_decode(token)
        print(decoded_token)

        if not decoded_token:
            return {"error": "Invalid token"}

        query_check = "SELECT * FROM blacklist WHERE token = %s"
        db.execute(query_check, (token,))
        existing_token = db.fetchone()

        if existing_token is not None:
            return {"message": "User has already logged out"}
        
        user_id = decoded_token.get('sub')
        
        query_insert = "INSERT INTO blacklist (token, expiration_time, user_id) VALUES (%s, %s, %s)"
        if db is not None:
            db.execute(query_insert, (token, datetime.utcnow(), user_id))
            save.commit()

        return {"message": "User logged out successfully"}

    except Exception as e:
        return {"error": str(e)}
