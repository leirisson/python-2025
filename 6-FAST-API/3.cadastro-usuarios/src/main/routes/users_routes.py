from fastapi import APIRouter
from fastapi.responses import JSONResponse



users_routes = APIRouter(tags=["Usaários"])

@users_routes.post("/users")
async def create_user():
    return JSONResponse(
        content={
            "Olá":"Mundo"
        },
        status_code=200
    )