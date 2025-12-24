from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer
from app.services.auth_service import AuthService

security = HTTPBearer()

async def verify_user(request: Request, credentials = Depends(security)):
    token = credentials.credentials
    payload = AuthService.verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    request.state.user = payload["sub"]  # email of logged-in user
    return payload
