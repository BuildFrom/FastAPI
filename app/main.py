from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse 
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .blueprint import router

load_dotenv()

origins = ["*"]

def create_app():
    app = FastAPI()    
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    router(app)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )

    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={"message": "Not Found"},
        )
    
    return app

if __name__ == '__main__':
    create_app()
