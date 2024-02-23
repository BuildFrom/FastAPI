from fastapi import FastAPI
from .routes import auth, user

def router(app: FastAPI) -> None:
    v1 = "/api/v1"
    app.include_router(auth.router, prefix=v1, tags=["auth"])
    app.include_router(user.router, prefix=v1, tags=["user"])
