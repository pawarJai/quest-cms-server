from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from app.repository.user_repository import UserRepository
from app.config.config import settings
from jose import JWTError
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:

    @staticmethod
    def hash_password(password: str):
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_token(token: str):
        """
        Verify and decode a JWT token. Returns the payload (dict) on success,
        or None on failure.
        """
        if not token:
            return None

        # If token has "Bearer " prefix, strip it (your client sets "Bearer <token>")
        if token.startswith("Bearer "):
            token = token.split(" ", 1)[1]

        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            # Optionally you can verify exp etc. jose will raise if exp expired.
            return payload
        except JWTError as e:
            # log if you want: print("Token verification failed:", e)
            return None

    @staticmethod
    def verify_password(password: str, hashed: str):
        return pwd_context.verify(password, hashed)

    @staticmethod
    def create_token(data: dict):
        payload = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        payload.update({"exp": expire})
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    async def signup(user_data: dict):
        try:
            existing_user = await UserRepository.get_user_by_email(user_data["email"])
            if existing_user:
                return None

            user_data["hashed_password"] = AuthService.hash_password(user_data.pop("password"))
            user_data["created_at"] = datetime.utcnow()

            await UserRepository.create_user(user_data)
            return user_data

        except Exception as e:
            print("SIGNUP ERROR:", e)
            raise

    @staticmethod
    async def login(email: str, password: str):
        user = await UserRepository.get_user_by_email(email)
        if not user:
            return None

        if not AuthService.verify_password(password, user["hashed_password"]):
            return None

        await UserRepository.update_login(email, datetime.utcnow())
        token = AuthService.create_token({"sub": email})

        return token
