from fastapi import HTTPException
from app.services.auth_service import AuthService


class AuthController:

    @staticmethod
    async def signup(data: dict):
        user = await AuthService.signup(data)
        if not user:
            raise HTTPException(status_code=400, detail="User already exists")
        return {"message": "User registered successfully"}

    @staticmethod
    async def login(email: str, password: str):
        token = await AuthService.login(email, password)
        if not token:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {"access_token": token, "token_type": "bearer"}
