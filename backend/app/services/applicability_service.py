from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.applicability import Applicability
from app.models.inspection import Inspection
from app.models.product_classification import ProductClassification
from app.services.legal_version_resolver import resolve_for_inspection


# =========================================================
# DECISION MODEL
# =========================================================

@dataclass
class ApplicabilityDecision:
    status: str
    reason: str
    applicable_provisions: list[str]
    confidence: float
    exemption_code: Optional[str] = None


# =========================================================
# APPLICABILITY SERVICE
# =========================================================

class ApplicabilityService:
    """
    Determines whether the Legal Metrology (Packaged Commodities)
    Rules, 2011 should be applied to the current inspection.

    Applicability states:

        EXEMPT
        NOT_EXEMPT
        UNKNOWN

    Important:
    - This service determines legal/applicability context.
    - It does NOT make the final enforcement decision.
    - UNKNOWN is preserved when evidence is insufficient.
    - Exemptions are returned only when a recognizable
      exemption condition has been established.
    - The legal version is resolved from the inspection date.
    """

    # Rule 26(a) prototype thresholds
    SMALL_PACK_MAX_GRAMS = 10.0
    SMALL_PACK_MAX_ML = 10.0

    # Pan masala small-pack exemption exclusion
    PAN_MASALA_EXCLUSION_DATE = date(2026, 2, 1)

    def __init__(self, db: Session):
        self.db = db

    # =========================================================
    # PUBLIC API
    # =========================================================

    def evaluate(
        self,
        inspection: Inspection,
        classification: Optional[ProductClassification] = None,
    ) -> ApplicabilityDecision:
        """
        Determine applicability/exemption for an inspection.
        """

        # -----------------------------------------------------
        # 1. Load product classification
        # -----------------------------------------------------

        if classification is None:
            classification = (
                self.db.query(ProductClassification)
                .filter(
                    ProductClassification.inspection_id == inspection.id
                )
                .first()
            )

        if classification is None:
            return ApplicabilityDecision(
                status="UNKNOWN",
                reason=(
                    "Product classification is not available. "
                    "Applicability cannot be determined reliably."
                ),
                applicable_provisions=[],
                confidence=0.0,
            )

        category = self._normalize(
            classification.commodity_category
        )

        package_type = self._normalize(
            classification.package_type
        )

        # -----------------------------------------------------
        # 2. Classification uncertainty
        # -----------------------------------------------------

        if classification.status in {
            "INCONCLUSIVE",
            "UNCERTAIN",
            "UNKNOWN",
        }:
            return ApplicabilityDecision(
                status="UNKNOWN",
                reason=(
                    "Product classification is uncertain. "
                    "Rule applicability cannot be determined "
                    "reliably from the available evidence."
                ),
                applicable_provisions=[],
                confidence=classification.confidence or 0.0,
            )

        # -----------------------------------------------------
        # 3. Medical-device branch
        # -----------------------------------------------------

        if category == "MEDICAL_DEVICE":
            return ApplicabilityDecision(
                status="EXEMPT",
                reason=(
                    "Product is classified as a medical device. "
                    "The relevant Packaged Commodities PDP/font "
                    "provisions are not applied through this branch."
                ),
                applicable_provisions=[],
                confidence=classification.confidence or 0.0,
                exemption_code="MEDICAL_DEVICE",
            )

        # -----------------------------------------------------
        # 4. Industrial / institutional package
        # -----------------------------------------------------

        if package_type in {
            "INDUSTRIAL",
            "INSTITUTIONAL",
            "INDUSTRIAL_CONSUMER",
            "INSTITUTIONAL_CONSUMER",
        }:
            return ApplicabilityDecision(
                status="EXEMPT",
                reason=(
                    "Package is classified as intended for "
                    "industrial/institutional consumers."
                ),
                applicable_provisions=[],
                confidence=classification.confidence or 0.0,
                exemption_code="INDUSTRIAL_INSTITUTIONAL",
            )

        # -----------------------------------------------------
        # 5. Extract net quantity
        # -----------------------------------------------------

        quantity_result = (
            self._extract_quantity_from_inspection(
                inspection
            )
        )

        # -----------------------------------------------------
        # 6. Rule 26(a) small-package branch
        # -----------------------------------------------------

        if quantity_result is not None:
            quantity, unit = quantity_result

            inspection_date = (
                inspection.created_at.date()
                if inspection.created_at
                else date.today()
            )

            # Pan masala is excluded from the small-pack
            # exemption from 1 February 2026.
            is_pan_masala_excluded = (
                self._is_pan_masala(
                    category,
                    inspection,
                )
                and inspection_date
                >= self.PAN_MASALA_EXCLUSION_DATE
            )

            if not is_pan_masala_excluded:

                if self._supports_small_pack_branch(
                    category
                ):
                    if self._is_small_pack(
                        quantity,
                        unit,
                    ):
                        return ApplicabilityDecision(
                            status="EXEMPT",
                            reason=(
                                f"Net quantity {quantity:g} {unit} "
                                "falls within the Rule 26(a) "
                                "small-package threshold."
                            ),
                            applicable_provisions=[],
                            confidence=0.95,
                            exemption_code=(
                                "RULE_26_A_SMALL_PACK"
                            ),
                        )

        # -----------------------------------------------------
        # 7. Fast-food branch
        # -----------------------------------------------------

        if self._is_fast_food(
            category,
            inspection,
        ):
            return ApplicabilityDecision(
                status="EXEMPT",
                reason=(
                    "Product is classified as fast food packed "
                    "by a restaurant/hotel or similar establishment."
                ),
                applicable_provisions=[],
                confidence=0.90,
                exemption_code="RULE_26_B_FAST_FOOD",
            )

        # -----------------------------------------------------
        # 8. Drug formulation branch
        # -----------------------------------------------------

        if self._is_drug_formulation(
            category,
            inspection,
        ):
            return ApplicabilityDecision(
                status="EXEMPT",
                reason=(
                    "Product is classified as a drug formulation "
                    "covered by the applicable drug-price-control "
                    "framework."
                ),
                applicable_provisions=[],
                confidence=0.90,
                exemption_code="RULE_26_C_DRUG_FORMULATION",
            )

        # -----------------------------------------------------
        # 9. Agricultural produce > 50 kg
        # -----------------------------------------------------

        if (
            self._is_agricultural_produce(
                category,
                inspection,
            )
            and quantity_result is not None
        ):
            quantity, unit = quantity_result

            if unit == "kg" and quantity > 50:
                return ApplicabilityDecision(
                    status="EXEMPT",
                    reason=(
                        f"Agricultural farm produce package "
                        f"is {quantity:g} kg, exceeding the "
                        "50 kg threshold."
                    ),
                    applicable_provisions=[],
                    confidence=0.95,
                    exemption_code=(
                        "RULE_26_D_AGRICULTURAL_PRODUCE"
                    ),
                )

        # -----------------------------------------------------
        # 10. Thread / handloom branch
        # -----------------------------------------------------

        if self._is_handloom_thread(
            category,
            inspection,
        ):
            return ApplicabilityDecision(
                status="EXEMPT",
                reason=(
                    "Thread is classified as being sold in coils "
                    "to handloom weavers."
                ),
                applicable_provisions=[],
                confidence=0.90,
                exemption_code="RULE_26_E_HANDLOOM_THREAD",
            )

        # -----------------------------------------------------
        # 11. Garment / hosiery branch
        # -----------------------------------------------------

        if self._is_loose_garment(
            category,
            package_type,
            inspection,
        ):
            return ApplicabilityDecision(
                status="EXEMPT",
                reason=(
                    "Garment/hosiery is classified as being sold "
                    "loose/open under the special Rule 26(f) branch."
                ),
                applicable_provisions=[
                    "RULE_26_F"
                ],
                confidence=0.90,
                exemption_code=(
                    "RULE_26_F_GARMENT_HOSIERY"
                ),
            )

        # -----------------------------------------------------
        # 12. Normal retail package
        # -----------------------------------------------------

        if self._is_retail_package(
            package_type
        ):
            return ApplicabilityDecision(
                status="NOT_EXEMPT",
                reason=(
                    "The product is classified as a normal "
                    "retail/pre-packaged commodity and no verified "
                    "Rule 26 exemption condition was established."
                ),
                applicable_provisions=[
                    "RULE_6",
                    "RULE_7",
                    "RULE_8",
                    "RULE_9",
                ],
                confidence=0.85,
            )

        # -----------------------------------------------------
        # 13. Insufficient evidence
        # -----------------------------------------------------

        return ApplicabilityDecision(
            status="UNKNOWN",
            reason=(
                "Available product, package and declaration "
                "evidence is insufficient to establish either "
                "a Rule 26 exemption or a normal retail-package "
                "applicability decision."
            ),
            applicable_provisions=[],
            confidence=classification.confidence or 0.0,
        )

    # =========================================================
    # DATABASE UPDATE
    # =========================================================

    def evaluate_and_store(
        self,
        inspection: Inspection,
        classification: Optional[ProductClassification] = None,
    ) -> Applicability:
        """
        Evaluate applicability and persist the result.

        Also resolves the legal version applicable on the
        inspection date and stores it in Applicability.rule_version.
        """

        # -----------------------------------------------------
        # 1. Evaluate applicability
        # -----------------------------------------------------

        decision = self.evaluate(
            inspection=inspection,
            classification=classification,
        )

        # -----------------------------------------------------
        # 2. Resolve legal version
        # -----------------------------------------------------

        rule_version = self._resolve_rule_version(
            inspection
        )

        # -----------------------------------------------------
        # 3. Find existing applicability record
        # -----------------------------------------------------

        record = (
            self.db.query(Applicability)
            .filter(
                Applicability.inspection_id
                == inspection.id
            )
            .first()
        )

        # -----------------------------------------------------
        # 4. Create if necessary
        # -----------------------------------------------------

        if record is None:
            record = Applicability(
                inspection_id=inspection.id,
                inspection_type=inspection.inspection_type,
            )

            self.db.add(record)

        # -----------------------------------------------------
        # 5. Classification information
        # -----------------------------------------------------

        if classification is None:
            classification = (
                self.db.query(ProductClassification)
                .filter(
                    ProductClassification.inspection_id
                    == inspection.id
                )
                .first()
            )

        if classification:
            record.commodity_category = (
                classification.commodity_category
            )

            record.package_type = (
                classification.package_type
            )

            record.is_imported = (
                classification.is_imported
            )

            record.is_multi_piece = (
                classification.is_multi_piece
            )

            record.is_combination = (
                classification.is_combination
            )

            record.is_group_package = (
                classification.is_group_package
            )

            record.classification_confidence = (
                classification.confidence
            )

            record.classification_status = (
                classification.status
            )

        # -----------------------------------------------------
        # 6. Applicability decision
        # -----------------------------------------------------

        record.exemption_status = decision.status

        record.exemption_reason = decision.reason

        record.applicable_provisions = str(
            decision.applicable_provisions
        )

        # -----------------------------------------------------
        # 7. LEGAL VERSION
        # -----------------------------------------------------

        record.rule_version = rule_version

        # -----------------------------------------------------
        # 8. Save
        # -----------------------------------------------------

        self.db.commit()
        self.db.refresh(record)

        return record

    # =========================================================
    # LEGAL VERSION RESOLUTION
    # =========================================================

    def _resolve_rule_version(
        self,
        inspection: Inspection,
    ) -> Optional[str]:
        """
        Resolve the operative Legal Metrology rule version
        for the inspection date.

        Priority:
        1. Latest operative amendment
        2. Base rules version
        3. None if resolver cannot determine a version
        """

        try:
            legal_context = resolve_for_inspection(
                self.db,
                inspection,
            )
        except Exception:
            # Applicability should still be usable if the
            # version resolver encounters an unexpected issue.
            return None

        if not legal_context:
            return None

        # -----------------------------------------------------
        # Latest operative amendment
        # -----------------------------------------------------

        latest_amendment = legal_context.get(
            "latest_amendment"
        )

        if latest_amendment:
            version_code = latest_amendment.get(
                "version_code"
            )

            if version_code:
                return version_code

        # -----------------------------------------------------
        # Base rules fallback
        # -----------------------------------------------------

        base_version = legal_context.get(
            "base_version"
        )

        if base_version:
            version_code = base_version.get(
                "version_code"
            )

            if version_code:
                return version_code

        return None

    # =========================================================
    # QUANTITY EXTRACTION
    # =========================================================

    def _extract_quantity_from_inspection(
        self,
        inspection: Inspection,
    ) -> Optional[tuple[float, str]]:
        """
        Extract NET_QUANTITY from the declaration table.
        """

        try:
            from app.models.declaration import Declaration

            declaration = (
                self.db.query(Declaration)
                .filter(
                    Declaration.inspection_id
                    == inspection.id,
                    Declaration.field_name
                    == "NET_QUANTITY",
                )
                .order_by(
                    Declaration.confidence.desc()
                )
                .first()
            )

            if declaration is None:
                return None

            value = (
                declaration.normalized_value
                or declaration.value
                or ""
            )

            return self._parse_quantity(value)

        except Exception:
            return None

    # =========================================================
    # QUANTITY PARSER
    # =========================================================

    @staticmethod
    def _parse_quantity(
        value: str,
    ) -> Optional[tuple[float, str]]:
        """
        Parse common weight/volume declarations.

        Examples:
            1kg
            500 g
            250ml
            1 litre
        """

        if not value:
            return None

        text = (
            value
            .lower()
            .replace(",", "")
            .strip()
        )

        match = re.search(
            r"(\d+(?:\.\d+)?)\s*"
            r"(kg|g|mg|l|ml|litre|liter|litres|liters)\b",
            text,
        )

        if not match:
            return None

        quantity = float(
            match.group(1)
        )

        unit = match.group(2)

        conversions = {
            "mg": (
                "g",
                quantity / 1000,
            ),
            "g": (
                "g",
                quantity,
            ),
            "kg": (
                "kg",
                quantity,
            ),
            "ml": (
                "ml",
                quantity,
            ),
            "l": (
                "l",
                quantity,
            ),
            "litre": (
                "l",
                quantity,
            ),
            "liter": (
                "l",
                quantity,
            ),
            "litres": (
                "l",
                quantity,
            ),
            "liters": (
                "l",
                quantity,
            ),
        }

        return conversions.get(unit)

    # =========================================================
    # SMALL PACKAGE CHECK
    # =========================================================

    @classmethod
    def _is_small_pack(
        cls,
        quantity: float,
        unit: str,
    ) -> bool:

        if unit == "g":
            return (
                quantity
                <= cls.SMALL_PACK_MAX_GRAMS
            )

        if unit == "kg":
            return (
                quantity
                <= cls.SMALL_PACK_MAX_GRAMS / 1000
            )

        if unit == "ml":
            return (
                quantity
                <= cls.SMALL_PACK_MAX_ML
            )

        if unit == "l":
            return (
                quantity
                <= cls.SMALL_PACK_MAX_ML / 1000
            )

        return False

    # =========================================================
    # SMALL-PACK BRANCH ELIGIBILITY
    # =========================================================

    @staticmethod
    def _supports_small_pack_branch(
        category: str,
    ) -> bool:
        """
        Only use the small-pack branch when a recognizable
        commodity category is available.

        This prevents an unknown product from being declared
        exempt solely because OCR detected a small quantity.
        """

        if not category:
            return False

        return category not in {
            "MEDICAL_DEVICE",
            "DRUG",
            "PHARMACEUTICAL",
            "INDUSTRIAL",
            "INSTITUTIONAL",
        }

    # =========================================================
    # NORMALIZATION
    # =========================================================

    @staticmethod
    def _normalize(
        value: Optional[str],
    ) -> str:

        if not value:
            return ""

        return (
            value
            .strip()
            .upper()
            .replace("-", "_")
            .replace(" ", "_")
        )

    # =========================================================
    # PAN MASALA
    # =========================================================

    @classmethod
    def _is_pan_masala(
        cls,
        category: str,
        inspection: Inspection,
    ) -> bool:

        text = " ".join(
            [
                category,
                inspection.product_name or "",
                inspection.source_url or "",
            ]
        ).lower()

        return (
            "pan masala" in text
            or "pan_masala" in text
        )

    # =========================================================
    # FAST FOOD
    # =========================================================

    @classmethod
    def _is_fast_food(
        cls,
        category: str,
        inspection: Inspection,
    ) -> bool:

        text = " ".join(
            [
                category,
                inspection.product_name or "",
            ]
        ).lower()

        return any(
            phrase in text
            for phrase in [
                "fast food",
                "restaurant packed",
                "hotel packed",
            ]
        )

    # =========================================================
    # DRUG FORMULATION
    # =========================================================

    @classmethod
    def _is_drug_formulation(
        cls,
        category: str,
        inspection: Inspection,
    ) -> bool:

        text = " ".join(
            [
                category,
                inspection.product_name or "",
            ]
        ).lower()

        return (
            "drug" in text
            or "pharmaceutical" in text
            or "formulation" in text
        )

    # =========================================================
    # AGRICULTURAL PRODUCE
    # =========================================================

    @classmethod
    def _is_agricultural_produce(
        cls,
        category: str,
        inspection: Inspection,
    ) -> bool:

        text = " ".join(
            [
                category,
                inspection.product_name or "",
            ]
        ).lower()

        return any(
            term in text
            for term in [
                "agricultural",
                "farm produce",
                "farm_produce",
            ]
        )

    # =========================================================
    # HANDLOOM THREAD
    # =========================================================

    @classmethod
    def _is_handloom_thread(
        cls,
        category: str,
        inspection: Inspection,
    ) -> bool:

        text = " ".join(
            [
                category,
                inspection.product_name or "",
            ]
        ).lower()

        return (
            "thread" in text
            and (
                "handloom" in text
                or "weaver" in text
            )
        )

    # =========================================================
    # GARMENT / HOSIERY
    # =========================================================

    @classmethod
    def _is_loose_garment(
        cls,
        category: str,
        package_type: str,
        inspection: Inspection,
    ) -> bool:

        text = " ".join(
            [
                category,
                package_type,
                inspection.product_name or "",
            ]
        ).lower()

        garment = any(
            term in text
            for term in [
                "garment",
                "hosiery",
                "clothing",
            ]
        )

        loose = any(
            term in text
            for term in [
                "loose",
                "open",
            ]
        )

        return garment and loose

    # =========================================================
    # NORMAL RETAIL PACKAGE
    # =========================================================

    @classmethod
    def _is_retail_package(
        cls,
        package_type: str,
    ) -> bool:

        return package_type in {
            "RETAIL_PACKAGE",
            "SINGLE",
            "STANDARD",
            "PRE_PACKAGED",
        }