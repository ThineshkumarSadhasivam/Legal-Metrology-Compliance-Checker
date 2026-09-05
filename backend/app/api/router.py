from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.inspection import router as inspection_router
from app.api.inspection_images import router as inspection_images_router
from app.api.ocr import router as ocr_router


api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(inspection_router)
api_router.include_router(inspection_images_router)
api_router.include_router(ocr_router)