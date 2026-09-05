from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.inspection import Inspection

from app.schemas.inspection import (
    InspectionCreate,
    InspectionResponse
)


router = APIRouter(
    prefix="/inspections",
    tags=["Inspections"]
)


@router.post(
    "/",
    response_model=InspectionResponse
)
def create_inspection(
    payload: InspectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Validate inspection type
    allowed_types = {
        "PHYSICAL",
        "ECOMMERCE"
    }

    inspection_type = payload.inspection_type.upper()

    if inspection_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="inspection_type must be PHYSICAL or ECOMMERCE"
        )

    # E-commerce inspection requires URL
    if (
        inspection_type == "ECOMMERCE"
        and not payload.source_url
    ):
        raise HTTPException(
            status_code=400,
            detail="source_url is required for ECOMMERCE inspection"
        )

    # Physical inspection should not require URL
    source_url = (
        payload.source_url
        if inspection_type == "ECOMMERCE"
        else None
    )

    # Generate inspection number
    count = db.query(Inspection).count() + 1

    inspection_number = f"LM-{count:05d}"

    inspection = Inspection(
        inspection_number=inspection_number,

        officer_id=current_user.id,

        inspection_type=inspection_type,

        source_url=source_url,

        # These will be populated after OCR + NER
        product_name=None,
        brand_name=None,
        manufacturer_name=None,

        status="CREATED",

        overall_result="INCONCLUSIVE"
    )

    db.add(inspection)
    db.commit()
    db.refresh(inspection)

    return inspection



@router.get(
    "/",
    response_model=list[InspectionResponse]
)
def get_inspections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    inspections = (
        db.query(Inspection)
        .filter(
            Inspection.officer_id == current_user.id
        )
        .order_by(
            Inspection.created_at.desc()
        )
        .all()
    )

    return inspections


@router.get(
    "/{inspection_id}",
    response_model=InspectionResponse
)
def get_inspection(
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
            status_code=404,
            detail="Inspection not found"
        )

    return inspection