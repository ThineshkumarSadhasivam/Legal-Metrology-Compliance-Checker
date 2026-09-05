from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine

# API routers
from app.api.auth import router as auth_router
from app.api.inspection import router as inspections_router
from app.api.inspection_images import router as inspection_images_router
from app.api.ocr import router as ocr_router

# Database models
from app.models.user import User
from app.models.inspection import Inspection
from app.models.inspection_image import InspectionImage
from app.models.ocr_result import OCRResult


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Legal Metrology Compliance API",
    version="1.0.0"
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routers
app.include_router(auth_router)
app.include_router(inspections_router)
app.include_router(inspection_images_router)
app.include_router(ocr_router)


@app.get("/")
def root():
    return {
        "message": "Legal Metrology Compliance API"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }