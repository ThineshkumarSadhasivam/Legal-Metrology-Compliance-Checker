from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    Text,
    DateTime,
    ForeignKey
)

from app.core.database import Base


class Applicability(Base):
    __tablename__ = "applicability"

    id = Column(Integer, primary_key=True, index=True)

    # Inspection this classification belongs to
    inspection_id = Column(
        Integer,
        ForeignKey("inspections.id"),
        nullable=False,
        unique=True,
        index=True
    )

    # -----------------------------------------------------
    # Inspection / channel
    # -----------------------------------------------------

    inspection_type = Column(
        String(30),
        nullable=False
    )
    # PHYSICAL / ECOMMERCE

    # -----------------------------------------------------
    # Commodity / package classification
    # -----------------------------------------------------

    commodity_category = Column(
        String(100),
        nullable=True
    )

    package_type = Column(
        String(100),
        nullable=True
    )

    # -----------------------------------------------------
    # Special package classifications
    # -----------------------------------------------------

    is_imported = Column(
        Boolean,
        nullable=False,
        default=False
    )

    is_multi_piece = Column(
        Boolean,
        nullable=False,
        default=False
    )

    is_combination = Column(
        Boolean,
        nullable=False,
        default=False
    )

    is_group_package = Column(
        Boolean,
        nullable=False,
        default=False
    )

    # -----------------------------------------------------
    # Exemption / applicability
    # -----------------------------------------------------

    exemption_status = Column(
        String(30),
        nullable=False,
        default="UNKNOWN"
    )
    # APPLICABLE / EXEMPT / UNKNOWN

    exemption_reason = Column(
        Text,
        nullable=True
    )

    # -----------------------------------------------------
    # Rule version
    # -----------------------------------------------------

    rule_version = Column(
        String(30),
        nullable=True
    )

    # -----------------------------------------------------
    # Applicable provisions
    # -----------------------------------------------------
    #
    # Example:
    #
    # [
    #   "RULE_6",
    #   "RULE_6_11",
    #   "RULE_7",
    #   "RULE_8"
    # ]
    #
    # Stored as JSON text for the prototype.
    # We can normalize this into a separate relationship
    # table when the rules engine becomes larger.
    # -----------------------------------------------------

    applicable_provisions = Column(
        Text,
        nullable=True
    )

    # -----------------------------------------------------
    # Classification confidence
    # -----------------------------------------------------

    classification_confidence = Column(
        Float,
        nullable=True
    )

    classification_status = Column(
        String(30),
        nullable=False,
        default="UNCERTAIN"
    )
    # CLASSIFIED / UNCERTAIN / INCONCLUSIVE

    # -----------------------------------------------------
    # Audit
    # -----------------------------------------------------

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