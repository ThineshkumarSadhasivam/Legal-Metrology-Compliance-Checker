import os
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.inspection import Inspection
from app.models.inspection_image import InspectionImage


router = APIRouter(
    tags=["Inspection Images"]
)



UPLOAD_ROOT = Path("uploads/inspections")

UPLOAD_ROOT.mkdir(
    parents=True,
    exist_ok=True
)



ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}



@router.post(
    "/inspections/{inspection_id}/images"
)
async def upload_inspection_image(
    inspection_id: int,

    image_type: str = Form("OTHER"),

    file: UploadFile = File(...),

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)
):


    inspection = (
        db.query(Inspection)
        .filter(
            Inspection.id == inspection_id,
            Inspection.officer_id == current_user.id
        )
        .first()
    )

    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found"
        )



    if file.content_type not in ALLOWED_MIME_TYPES:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unsupported image format. "
                "Allowed formats: JPEG, PNG, WEBP"
            )
        )



    allowed_image_types = {
        "FRONT",
        "BACK",
        "SIDE",
        "LABEL",
        "PDP",
        "OTHER"
    }

    image_type = image_type.upper()

    if image_type not in allowed_image_types:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid image_type. "
                "Allowed values: FRONT, BACK, SIDE, "
                "LABEL, PDP, OTHER"
            )
        )



    inspection_folder = (
        UPLOAD_ROOT /
        str(inspection.inspection_number)
    )

    inspection_folder.mkdir(
        parents=True,
        exist_ok=True
    )



    extension = Path(
        file.filename or ""
    ).suffix.lower()

    if extension not in {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    }:

        extension = ".jpg"


    unique_filename = (
        f"{uuid.uuid4().hex}{extension}"
    )

    file_path = (
        inspection_folder /
        unique_filename
    )


    contents = await file.read()

    if not contents:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty"
        )


    max_size = 10 * 1024 * 1024  # 10 MB

    if len(contents) > max_size:

        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image size cannot exceed 10 MB"
        )


    with open(file_path, "wb") as buffer:

        buffer.write(contents)


    inspection_image = InspectionImage(

        inspection_id=inspection.id,

        image_type=image_type,

        file_name=file.filename or unique_filename,

        file_path=str(file_path),

        mime_type=file.content_type,

        file_size=len(contents)
    )


    db.add(inspection_image)

    db.commit()

    db.refresh(inspection_image)


    # ----------------------------------------------
    # 8. Return response
    # ----------------------------------------------

    return {

        "message": "Inspection image uploaded successfully",

        "image": {

            "id": inspection_image.id,

            "inspection_id": inspection_image.inspection_id,

            "inspection_number": (
                inspection.inspection_number
            ),

            "image_type": (
                inspection_image.image_type
            ),

            "file_name": (
                inspection_image.file_name
            ),

            "file_path": (
                inspection_image.file_path
            ),

            "mime_type": (
                inspection_image.mime_type
            ),

            "file_size": (
                inspection_image.file_size
            ),

            "uploaded_at": (
                inspection_image.uploaded_at
            )
        }
    }



@router.get(
    "/inspections/{inspection_id}/images"
)
def get_inspection_images(

    inspection_id: int,

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)
):


    inspection = (
        db.query(Inspection)
        .filter(
            Inspection.id == inspection_id,
            Inspection.officer_id == current_user.id
        )
        .first()
    )

    if not inspection:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found"
        )


    images = (
        db.query(InspectionImage)
        .filter(
            InspectionImage.inspection_id ==
            inspection_id
        )
        .order_by(
            InspectionImage.uploaded_at.desc()
        )
        .all()
    )


    return {

        "inspection_id": inspection_id,

        "inspection_number": (
            inspection.inspection_number
        ),

        "count": len(images),

        "images": [

            {
                "id": image.id,

                "image_type": image.image_type,

                "file_name": image.file_name,

                "file_path": image.file_path,

                "mime_type": image.mime_type,

                "file_size": image.file_size,

                "uploaded_at": image.uploaded_at
            }

            for image in images
        ]
    }



@router.get(
    "/inspection-images/{image_id}"
)
def get_inspection_image(

    image_id: int,

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)
):

    image = (
        db.query(InspectionImage)
        .join(
            Inspection,
            Inspection.id ==
            InspectionImage.inspection_id
        )
        .filter(
            InspectionImage.id == image_id,
            Inspection.officer_id ==
            current_user.id
        )
        .first()
    )


    if not image:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection image not found"
        )


    return {

        "id": image.id,

        "inspection_id": (
            image.inspection_id
        ),

        "image_type": (
            image.image_type
        ),

        "file_name": (
            image.file_name
        ),

        "file_path": (
            image.file_path
        ),

        "mime_type": (
            image.mime_type
        ),

        "file_size": (
            image.file_size
        ),

        "uploaded_at": (
            image.uploaded_at
        )
    }