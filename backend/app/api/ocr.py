from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.inspection import Inspection
from app.models.inspection_image import InspectionImage
from app.models.ocr_result import OCRResult

from app.services.ocr_service import run_ocr


router = APIRouter(tags=["OCR"])


@router.post("/inspections/{inspection_id}/ocr")
def run_inspection_ocr(
    inspection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # ---------------------------------------------------------
    # 1. Verify that the inspection belongs to the logged-in officer
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # 2. Get all images uploaded for this inspection
    # ---------------------------------------------------------
    images = (
        db.query(InspectionImage)
        .filter(
            InspectionImage.inspection_id == inspection_id
        )
        .order_by(InspectionImage.id.asc())
        .all()
    )

    if not images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No images uploaded for this inspection"
        )

    total_text_regions = 0
    processed_images = 0
    failed_images = []

    # ---------------------------------------------------------
    # 3. Run OCR on every uploaded image
    # ---------------------------------------------------------
    for image in images:

        try:
            # Run PaddleOCR
            extracted_text = run_ocr(image.file_path)

            # Remove previous OCR results for this image
            db.query(OCRResult).filter(
                OCRResult.image_id == image.id
            ).delete(
                synchronize_session=False
            )

            # Store new OCR results
            for item in extracted_text:

                ocr_result = OCRResult(
                    image_id=image.id,
                    inspection_id=inspection.id,
                    text=item["text"],
                    confidence=item["confidence"],
                    bbox=str(item["bbox"])
                )

                db.add(ocr_result)

                total_text_regions += 1

            processed_images += 1

        except Exception as e:
            failed_images.append({
                "image_id": image.id,
                "file_name": image.file_name,
                "error": str(e)
            })

    # ---------------------------------------------------------
    # 4. Save everything
    # ---------------------------------------------------------
    db.commit()

    # ---------------------------------------------------------
    # 5. Return OCR processing summary
    # ---------------------------------------------------------
    return {
        "message": "OCR processing completed",
        "inspection_id": inspection.id,
        "inspection_number": inspection.inspection_number,
        "total_images": len(images),
        "processed_images": processed_images,
        "total_text_regions": total_text_regions,
        "failed_images": failed_images
    }


@router.get("/inspections/{inspection_id}/ocr")
def get_inspection_ocr(
    inspection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # ---------------------------------------------------------
    # 1. Verify inspection ownership
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # 2. Get OCR results
    # ---------------------------------------------------------
    results = (
        db.query(OCRResult, InspectionImage)
        .join(
            InspectionImage,
            InspectionImage.id == OCRResult.image_id
        )
        .filter(
            OCRResult.inspection_id == inspection_id
        )
        .order_by(
            InspectionImage.id.asc(),
            OCRResult.id.asc()
        )
        .all()
    )

    # ---------------------------------------------------------
    # 3. Format response
    # ---------------------------------------------------------
    ocr_results = []

    for ocr_result, image in results:

        ocr_results.append({
            "id": ocr_result.id,
            "image_id": image.id,
            "image_type": image.image_type,
            "file_name": image.file_name,
            "text": ocr_result.text,
            "confidence": ocr_result.confidence,
            "bbox": ocr_result.bbox,
            "created_at": ocr_result.created_at
        })

    return {
        "inspection_id": inspection.id,
        "inspection_number": inspection.inspection_number,
        "count": len(ocr_results),
        "results": ocr_results
    }