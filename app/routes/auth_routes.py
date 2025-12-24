from fastapi import APIRouter
from app.schemas.user_schema import UserSignupSchema, UserLoginSchema
from app.controllers.auth_controller import AuthController

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup")
async def signup(data: UserSignupSchema):
    return await AuthController.signup(data.dict())


@router.post("/login")
async def login(data: UserLoginSchema):
    return await AuthController.login(data.email, data.password)
