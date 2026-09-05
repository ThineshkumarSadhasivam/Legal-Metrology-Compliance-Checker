from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)

from app.core.database import Base


class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    inspection_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    officer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    inspection_type = Column(
        String(30),
        nullable=False
    )

    product_name = Column(
        String(255),
        nullable=True
    )

    brand_name = Column(
        String(255),
        nullable=True
    )

    manufacturer_name = Column(
        String(255),
        nullable=True
    )

    source_url = Column(
        Text,
        nullable=True
    )

    status = Column(
        String(30),
        nullable=False,
        default="CREATED"
    )

    overall_result = Column(
        String(30),
        nullable=False,
        default="INCONCLUSIVE"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )