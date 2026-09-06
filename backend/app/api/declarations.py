from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.inspection import Inspection
from app.models.ocr_result import OCRResult
from app.models.declaration import Declaration

from app.services.declaration_extractor import extract_declarations


router = APIRouter(tags=["Declarations"])


@router.post("/inspections/{inspection_id}/declarations")
def extract_inspection_declarations(
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
    # 2. Get all OCR results for this inspection
    # ---------------------------------------------------------
    ocr_results = (
        db.query(OCRResult)
        .filter(
            OCRResult.inspection_id == inspection_id
        )
        .order_by(OCRResult.id.asc())
        .all()
    )

    if not ocr_results:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No OCR results found. Run OCR before declaration extraction."
        )

    # ---------------------------------------------------------
    # 3. Convert database objects into extractor input
    # ---------------------------------------------------------
    ocr_data = []

    for result in ocr_results:

        ocr_data.append({
            "id": result.id,
            "text": result.text,
            "confidence": result.confidence,
            "bbox": result.bbox
        })

    # ---------------------------------------------------------
    # 4. Run declaration extraction
    # ---------------------------------------------------------
    extracted = extract_declarations(ocr_data)

    # ---------------------------------------------------------
    # 5. Remove previously extracted declarations
    # ---------------------------------------------------------
    db.query(Declaration).filter(
        Declaration.inspection_id == inspection_id
    ).delete(
        synchronize_session=False
    )

    # ---------------------------------------------------------
    # 6. Store new declarations
    # ---------------------------------------------------------
    stored_declarations = []

    for item in extracted:

        declaration = Declaration(
            inspection_id=inspection.id,
            field_name=item["field_name"],
            value=item["value"],
            normalized_value=item.get("normalized_value"),
            confidence=item.get("confidence"),
            source_ocr_ids=str(
                item.get("source_ocr_ids", [])
            ),
            status=item.get("status", "DETECTED")
        )

        db.add(declaration)
        db.flush()

        stored_declarations.append({
            "id": declaration.id,
            "field_name": declaration.field_name,
            "value": declaration.value,
            "normalized_value": declaration.normalized_value,
            "confidence": declaration.confidence,
            "source_ocr_ids": declaration.source_ocr_ids,
            "status": declaration.status
        })

    # ---------------------------------------------------------
    # 7. Commit
    # ---------------------------------------------------------
    db.commit()

    # ---------------------------------------------------------
    # 8. Return extraction result
    # ---------------------------------------------------------
    return {
        "message": "Declaration extraction completed",
        "inspection_id": inspection.id,
        "inspection_number": inspection.inspection_number,
        "ocr_regions_analyzed": len(ocr_results),
        "declarations_detected": len(stored_declarations),
        "declarations": stored_declarations
    }


@router.get("/inspections/{inspection_id}/declarations")
def get_inspection_declarations(
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
    # 2. Get stored declarations
    # ---------------------------------------------------------
    declarations = (
        db.query(Declaration)
        .filter(
            Declaration.inspection_id == inspection_id
        )
        .order_by(Declaration.id.asc())
        .all()
    )

    # ---------------------------------------------------------
    # 3. Return declarations
    # ---------------------------------------------------------
    return {
        "inspection_id": inspection.id,
        "inspection_number": inspection.inspection_number,
        "count": len(declarations),
        "declarations": [
            {
                "id": declaration.id,
                "field_name": declaration.field_name,
                "value": declaration.value,
                "normalized_value": declaration.normalized_value,
                "confidence": declaration.confidence,
                "source_ocr_ids": declaration.source_ocr_ids,
                "status": declaration.status,
                "created_at": declaration.created_at
            }
            for declaration in declarations
        ]
    }