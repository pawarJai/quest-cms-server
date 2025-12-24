from fastapi import APIRouter
from app.controllers.upload_controller import router as upload_controller

router = APIRouter()
router.include_router(upload_controller, tags=["Uploads"])
