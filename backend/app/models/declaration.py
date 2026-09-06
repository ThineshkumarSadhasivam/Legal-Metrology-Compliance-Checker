from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey
)

from app.core.database import Base


class Declaration(Base):
    __tablename__ = "declarations"

    id = Column(Integer, primary_key=True, index=True)

    # Inspection to which this declaration belongs
    inspection_id = Column(
        Integer,
        ForeignKey("inspections.id"),
        nullable=False,
        index=True
    )

    # Type of declaration detected
    # Examples:
    # BRAND_NAME
    # PRODUCT_NAME
    # NET_QUANTITY
    # MRP
    # MANUFACTURER
    # PACKER
    # IMPORTER
    # COUNTRY_OF_ORIGIN
    # UNIT_SALE_PRICE
    # CUSTOMER_CARE
    # OTHER
    field_name = Column(
        String(100),
        nullable=False,
        index=True
    )

    # Exact/near-exact value obtained from OCR
    value = Column(
        Text,
        nullable=False
    )

    # Normalized interpretation of the value
    # Example:
    # "1kg" -> "1 kg"
    # "MRP Rs.120" -> "₹120"
    normalized_value = Column(
        Text,
        nullable=True
    )

    # Confidence of the extraction layer
    confidence = Column(
        Float,
        nullable=True
    )

    # OCR result IDs which support this declaration
    # Example: "[6, 7]"
    source_ocr_ids = Column(
        Text,
        nullable=True
    )

    # Status of extraction
    # DETECTED / UNCERTAIN / NOT_DETECTED
    status = Column(
        String(30),
        nullable=False,
        default="DETECTED"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )