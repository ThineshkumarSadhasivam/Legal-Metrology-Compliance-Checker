import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.inspection import Inspection
from app.models.ocr_result import OCRResult
from app.models.declaration import Declaration
from app.models.product_classification import ProductClassification

from app.services.product_classification_service import classify_product


router = APIRouter(tags=["Product Classification"])


# =========================================================
# POST - Automatically classify product
# =========================================================

@router.post("/inspections/{inspection_id}/classification")
def classify_inspection_product(
    inspection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # -----------------------------------------------------
    # 1. Verify inspection belongs to logged-in officer
    # -----------------------------------------------------

    inspection = (
        db.query(Inspection)
        .filter(
            Inspection.id == inspection_id,
            Inspection.officer_id == current_user.id,
        )
        .first()
    )

    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found",
        )

    # -----------------------------------------------------
    # 2. Get OCR results
    # -----------------------------------------------------

    ocr_rows = (
        db.query(OCRResult)
        .filter(
            OCRResult.inspection_id == inspection_id
        )
        .order_by(OCRResult.id.asc())
        .all()
    )

    if not ocr_rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "OCR results not found. "
                "Run OCR before product classification."
            ),
        )

    ocr_results = [
        {
            "id": row.id,
            "text": row.text,
            "confidence": row.confidence,
            "bbox": row.bbox,
        }
        for row in ocr_rows
    ]

    # -----------------------------------------------------
    # 3. Get extracted declarations
    # -----------------------------------------------------

    declaration_rows = (
        db.query(Declaration)
        .filter(
            Declaration.inspection_id == inspection_id
        )
        .order_by(Declaration.id.asc())
        .all()
    )

    declarations = [
        {
            "id": row.id,
            "field_name": row.field_name,
            "value": row.value,
            "normalized_value": row.normalized_value,
            "confidence": row.confidence,
            "status": row.status,
        }
        for row in declaration_rows
    ]

    # -----------------------------------------------------
    # 4. Run product classification
    # -----------------------------------------------------

    result = classify_product(
        ocr_results=ocr_results,
        declarations=declarations,
    )

    # -----------------------------------------------------
    # 5. Check whether classification already exists
    # -----------------------------------------------------

    existing = (
        db.query(ProductClassification)
        .filter(
            ProductClassification.inspection_id == inspection_id
        )
        .first()
    )

    # -----------------------------------------------------
    # 6. Update existing classification
    # -----------------------------------------------------

    if existing:

        existing.commodity_category = (
            result["commodity_category"]
        )

        existing.package_type = (
            result["package_type"]
        )

        existing.is_imported = (
            result["is_imported"]
        )

        existing.is_multi_piece = (
            result["is_multi_piece"]
        )

        existing.is_combination = (
            result["is_combination"]
        )

        existing.is_group_package = (
            result["is_group_package"]
        )

        existing.confidence = (
            result["confidence"]
        )

        existing.status = (
            result["status"]
        )

        existing.evidence = json.dumps(
            result["evidence"],
            ensure_ascii=False,
        )

        db.commit()
        db.refresh(existing)

        classification = existing

    # -----------------------------------------------------
    # 7. Create new classification
    # -----------------------------------------------------

    else:

        classification = ProductClassification(
            inspection_id=inspection_id,

            commodity_category=(
                result["commodity_category"]
            ),

            package_type=(
                result["package_type"]
            ),

            is_imported=(
                result["is_imported"]
            ),

            is_multi_piece=(
                result["is_multi_piece"]
            ),

            is_combination=(
                result["is_combination"]
            ),

            is_group_package=(
                result["is_group_package"]
            ),

            confidence=(
                result["confidence"]
            ),

            status=(
                result["status"]
            ),

            evidence=json.dumps(
                result["evidence"],
                ensure_ascii=False,
            ),
        )

        db.add(classification)

        db.commit()
        db.refresh(classification)

    # -----------------------------------------------------
    # 8. Return classification
    # -----------------------------------------------------

    return {
        "message": "Product classification completed",

        "inspection_id": inspection.id,

        "inspection_number": (
            inspection.inspection_number
        ),

        "classification": {
            "id": classification.id,

            "commodity_category": (
                classification.commodity_category
            ),

            "package_type": (
                classification.package_type
            ),

            "is_imported": (
                classification.is_imported
            ),

            "is_multi_piece": (
                classification.is_multi_piece
            ),

            "is_combination": (
                classification.is_combination
            ),

            "is_group_package": (
                classification.is_group_package
            ),

            "confidence": (
                classification.confidence
            ),

            "status": (
                classification.status
            ),

            "evidence": result["evidence"],
        },
    }


# =========================================================
# GET - Retrieve classification
# =========================================================

@router.get("/inspections/{inspection_id}/classification")
def get_product_classification(
    inspection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # -----------------------------------------------------
    # 1. Verify inspection
    # -----------------------------------------------------

    inspection = (
        db.query(Inspection)
        .filter(
            Inspection.id == inspection_id,
            Inspection.officer_id == current_user.id,
        )
        .first()
    )

    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found",
        )

    # -----------------------------------------------------
    # 2. Get classification
    # -----------------------------------------------------

    classification = (
        db.query(ProductClassification)
        .filter(
            ProductClassification.inspection_id
            == inspection_id
        )
        .first()
    )

    if not classification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product classification not found",
        )

    # -----------------------------------------------------
    # 3. Parse evidence
    # -----------------------------------------------------

    try:

        evidence = (
            json.loads(classification.evidence)
            if classification.evidence
            else {}
        )

    except json.JSONDecodeError:

        evidence = {}

    # -----------------------------------------------------
    # 4. Return stored classification
    # -----------------------------------------------------

    return {
        "inspection_id": inspection.id,

        "inspection_number": (
            inspection.inspection_number
        ),

        "classification": {
            "id": classification.id,

            "commodity_category": (
                classification.commodity_category
            ),

            "package_type": (
                classification.package_type
            ),

            "is_imported": (
                classification.is_imported
            ),

            "is_multi_piece": (
                classification.is_multi_piece
            ),

            "is_combination": (
                classification.is_combination
            ),

            "is_group_package": (
                classification.is_group_package
            ),

            "confidence": (
                classification.confidence
            ),

            "status": (
                classification.status
            ),

            "evidence": evidence,
        },
    }