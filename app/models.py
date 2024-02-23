from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    id: Optional[str]
    email: str
    password: str
    name: Optional[str]
    username: Optional[str]
    phone_number: Optional[str]
    roles: str = "2001"

class Token(BaseModel):
    id: str
    token: str
    expiration_time: datetime
    user_id: str