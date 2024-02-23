from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
from ..extensions.utils import get_all_users, get_user_by_id, jwt_decode, response, error
from ..models import User
from ..extensions.database import get_db

router = APIRouter()

# ✅ ------------------------ #

@router.get("/users", response_model=List[User])
async def get_users(db=Depends(get_db)):
    users = await get_all_users(db)
    if not users:
        error(404, "No users found")
    return response(users, 200)

# ------------------------ #

@router.get("/me", response_model=User)
async def get_current_user(request: Request, db=Depends(get_db)):
    token = request.cookies.get('token')
    if not token:
        raise HTTPException(status_code=401, detail="No token in cookies")

    decoded_token = jwt_decode(token)
    if not decoded_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_id = decoded_token.get('sub')
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return response(user, 200)
