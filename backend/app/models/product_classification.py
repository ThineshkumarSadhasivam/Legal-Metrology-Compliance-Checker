from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
)

from app.core.database import Base


class ProductClassification(Base):
    __tablename__ = "product_classifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    inspection_id = Column(
        Integer,
        ForeignKey("inspections.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    commodity_category = Column(
        String(100),
        nullable=True,
    )

    package_type = Column(
        String(100),
        nullable=True,
    )

    is_imported = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    is_multi_piece = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    is_combination = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    is_group_package = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    confidence = Column(
        Float,
        nullable=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default="INCONCLUSIVE",
    )

    evidence = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )