from typing import Any, Dict, List, Optional
from copy import deepcopy

from sqlalchemy.orm import Session

from app.models.inspection import Inspection
from app.models.declaration import Declaration
from app.models.applicability import Applicability
from app.models.compliance_finding import ComplianceFinding
from app.services.legal_version_resolver import resolve_for_inspection


# ============================================================
# RESULT STATES
# ============================================================

COMPLIANT = "COMPLIANT"
VIOLATION = "VIOLATION"
INCONCLUSIVE = "INCONCLUSIVE"


# ============================================================
# HELPERS
# ============================================================

def normalize_text(value: Optional[str]) -> str:
    """
    Normalize text for case-insensitive comparisons.
    """
    if not value:
        return ""

    return " ".join(
        str(value).strip().lower().split()
    )


def parse_evidence_fields(
    value: Optional[str],
) -> List[str]:
    """
    Convert text/list-like database values into a list.

    Supported examples:

        NET_QUANTITY

        ['NET_QUANTITY', 'MRP']

        NET_QUANTITY,MRP

    Also supports applicability provisions:

        ['RULE_6', 'RULE_7', 'RULE_8', 'RULE_9']
    """

    if not value:
        return []

    text = str(value).strip()

    # Python-list-like representation
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]

    text = text.replace("'", "")
    text = text.replace('"', "")

    fields: List[str] = []

    for item in text.split(","):
        item = item.strip()

        if item:
            fields.append(item.upper())

    return fields


def normalize_rule_number(value: Any) -> str:
    """
    Normalize rule numbers coming from the resolver.

    Supports values such as:

        6
        "6"
        "Rule 6"
        "RULE 6"
        "6(10)"
        "Rule 6(10)"
    """

    if value is None:
        return ""

    text = str(value).strip().upper()

    if not text:
        return ""

    text = text.replace("RULE", "")
    text = text.replace(" ", "")

    return text


def normalize_sub_rule(value: Any) -> str:
    """
    Normalize sub-rule identifiers.

    Examples:

        10A      -> 10A
        (10A)    -> 10A
        Rule 6(10A) -> 10A
    """

    if value is None:
        return ""

    text = str(value).strip().upper()

    if not text:
        return ""

    text = text.replace("RULE", "")
    text = text.replace(" ", "")
    text = text.replace("(", "")
    text = text.replace(")", "")

    return text


def get_requirement_rule_number(
    requirement: Dict[str, Any],
) -> str:
    """
    Resolve the rule number attached to a requirement.

    The legal-version resolver normally stores rule_number
    on the parent rule object rather than directly on each
    requirement.

    This helper supports both structures.
    """

    candidates = [
        requirement.get("rule_number"),
        requirement.get("parent_rule_number"),
        requirement.get("rule"),
        requirement.get("rule_no"),
    ]

    for value in candidates:
        normalized = normalize_rule_number(value)

        if normalized:
            return normalized

    return ""


def get_requirement_sub_rule(
    requirement: Dict[str, Any],
) -> str:
    """
    Resolve the sub-rule attached to a requirement.
    """

    candidates = [
        requirement.get("sub_rule"),
        requirement.get("parent_sub_rule"),
        requirement.get("subrule"),
    ]

    for value in candidates:
        normalized = normalize_sub_rule(value)

        if normalized:
            return normalized

    return ""


def enrich_requirement_with_rule_context(
    requirement: Dict[str, Any],
    rule: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Add parent-rule metadata to a requirement.

    This is important because the resolver stores:

        rule_number
        sub_rule
        source_reference

    on the parent rule object.

    Applicability evaluation needs this information to decide
    whether RULE_6 / RULE_7 / RULE_8 / RULE_9 applies.
    """

    enriched = deepcopy(requirement)

    if not enriched.get("rule_number"):
        enriched["rule_number"] = rule.get("rule_number")

    if not enriched.get("sub_rule"):
        enriched["sub_rule"] = rule.get("sub_rule")

    if not enriched.get("source_reference"):
        enriched["source_reference"] = rule.get(
            "source_reference"
        )

    if not enriched.get("legal_version"):
        enriched["legal_version"] = (
            rule.get("resolved_from_version")
            or {}
        ).get("version_code")

    return enriched


def get_declaration_map(
    db: Session,
    inspection_id: int,
) -> Dict[str, List[Declaration]]:
    """
    Return declarations grouped by field_name.
    """

    declarations = (
        db.query(Declaration)
        .filter(
            Declaration.inspection_id == inspection_id
        )
        .order_by(
            Declaration.id.asc()
        )
        .all()
    )

    result: Dict[str, List[Declaration]] = {}

    for declaration in declarations:
        key = (
            declaration.field_name.upper()
        )

        result.setdefault(
            key,
            []
        ).append(
            declaration
        )

    return result


def declaration_exists(
    declaration_map: Dict[str, List[Declaration]],
    field_name: str,
) -> bool:
    """
    Evidence exists only when the declaration
    extractor actually produced a declaration.
    """

    return bool(
        declaration_map.get(
            field_name.upper(),
            [],
        )
    )


def get_declaration_value(
    declaration_map: Dict[str, List[Declaration]],
    field_name: str,
) -> Optional[str]:
    """
    Return the best available declaration value.
    """

    values = declaration_map.get(
        field_name.upper(),
        [],
    )

    if not values:
        return None

    for declaration in values:

        if declaration.normalized_value:
            return declaration.normalized_value

        if declaration.value:
            return declaration.value

    return None


def get_declaration_confidence(
    declaration_map: Dict[str, List[Declaration]],
    field_name: str,
) -> Optional[float]:
    """
    Return the highest declaration confidence.
    """

    values = declaration_map.get(
        field_name.upper(),
        [],
    )

    if not values:
        return None

    confidences = [
        d.confidence
        for d in values
        if d.confidence is not None
    ]

    if not confidences:
        return None

    return max(confidences)


# ============================================================
# APPLICABILITY
# ============================================================

def is_requirement_applicable(
    requirement: Dict[str, Any],
    applicability: Optional[Applicability],
) -> bool:
    """
    Determine whether a compliance requirement applies
    to the current inspection.

    Important:
    The parent rule context is propagated into each requirement
    by enrich_requirement_with_rule_context().

    Rules:

    1. No applicability record:
       preserve legacy behavior.

    2. E-commerce-only requirements:
       only apply to ECOMMERCE inspections.

    3. EXEMPT:
       normal Rule 6/7/8/9 requirements are skipped.

    4. NOT_EXEMPT:
       only provisions established by the applicability
       service are evaluated.

    5. UNKNOWN:
       substantive compliance requirements are not evaluated.

    6. Rule 26 exemption screen:
       evaluated whenever applicability exists.
    """

    # --------------------------------------------------------
    # No applicability information
    # --------------------------------------------------------

    if not applicability:
        return True

    # --------------------------------------------------------
    # Basic requirement information
    # --------------------------------------------------------

    description = normalize_text(
        requirement.get("description")
    )

    title = normalize_text(
        requirement.get("title")
    )

    combined = (
        f"{title} {description}"
    )

    requirement_code = (
        requirement.get(
            "requirement_code"
        )
        or ""
    ).upper()

    rule_number = get_requirement_rule_number(
        requirement
    )

    sub_rule = get_requirement_sub_rule(
        requirement
    )

    inspection_type = (
        applicability.inspection_type
        or ""
    ).upper()

    # --------------------------------------------------------
    # 1. E-commerce-only requirements
    # --------------------------------------------------------

    ecommerce_requirement = (
        "online" in combined
        or "e-commerce" in combined
        or "ecommerce" in combined
        or "digital" in combined
        or "country-of-origin filter" in combined
        or "searchable and sortable" in combined
        or requirement_code.startswith("R6_10_")
        or requirement_code.startswith("R6_10A_")
    )

    if ecommerce_requirement:
        return (
            inspection_type == "ECOMMERCE"
        )

    # --------------------------------------------------------
    # 2. Rule 26 exemption screen
    # --------------------------------------------------------

    if requirement_code == (
        "R26_EXEMPTION_SCREEN"
    ):
        return True

    # --------------------------------------------------------
    # 3. Read applicability provisions
    # --------------------------------------------------------

    raw_provisions = (
        applicability.applicable_provisions
        or ""
    )

    applicable_provisions = set(
        parse_evidence_fields(
            raw_provisions
        )
    )

    # --------------------------------------------------------
    # 4. EXEMPT
    # --------------------------------------------------------

    if (
        applicability.exemption_status
        == "EXEMPT"
    ):

        # Special Rule 26(f) branch.
        if "RULE_26_F" in applicable_provisions:

            if (
                rule_number == "26"
                or requirement_code.startswith(
                    "R26_"
                )
            ):
                return True

        # Other exemptions do not require
        # normal packaged commodity checks.
        return False

    # --------------------------------------------------------
    # 5. UNKNOWN
    # --------------------------------------------------------

    if (
        applicability.exemption_status
        == "UNKNOWN"
    ):
        return False

    # --------------------------------------------------------
    # 6. NOT_EXEMPT
    # --------------------------------------------------------

    if (
        applicability.exemption_status
        == "NOT_EXEMPT"
    ):

        # If applicability engine supplied explicit
        # provisions, only those rules are evaluated.
        if applicable_provisions:

            # --------------------------------------------
            # Rule 6
            # --------------------------------------------

            if rule_number == "6":
                return (
                    "RULE_6"
                    in applicable_provisions
                )

            # --------------------------------------------
            # Rule 7
            # --------------------------------------------

            if rule_number == "7":
                return (
                    "RULE_7"
                    in applicable_provisions
                )

            # --------------------------------------------
            # Rule 8
            # --------------------------------------------

            if rule_number == "8":
                return (
                    "RULE_8"
                    in applicable_provisions
                )

            # --------------------------------------------
            # Rule 9
            # --------------------------------------------

            if rule_number == "9":
                return (
                    "RULE_9"
                    in applicable_provisions
                )

            # --------------------------------------------
            # Rule 26 screen already handled
            # --------------------------------------------

            if rule_number == "26":
                return False

            # --------------------------------------------
            # Exact generic rule provision
            # --------------------------------------------

            generic_rule_key = (
                f"RULE_{rule_number}"
            )

            if (
                generic_rule_key
                in applicable_provisions
            ):
                return True

            # --------------------------------------------
            # Exact sub-rule provision
            # --------------------------------------------

            if sub_rule:

                normalized_sub_rule = (
                    normalize_sub_rule(
                        sub_rule
                    )
                    .replace("-", "_")
                )

                exact_key = (
                    f"RULE_{rule_number}_"
                    f"{normalized_sub_rule}"
                )

                if (
                    exact_key
                    in applicable_provisions
                ):
                    return True

            return False

        # Conservative fallback when no provisions
        # were supplied.
        return True

    # --------------------------------------------------------
    # 7. Unknown status
    # --------------------------------------------------------

    return False


# ============================================================
# REQUIREMENT EVALUATION
# ============================================================

def evaluate_requirement(
    requirement: Dict[str, Any],
    declaration_map: Dict[str, List[Declaration]],
    applicability: Optional[Applicability],
) -> Dict[str, Any]:

    requirement_code = (
        requirement.get(
            "requirement_code"
        )
        or ""
    )

    title = (
        requirement.get("title")
        or requirement_code
    )

    description = (
        requirement.get("description")
        or ""
    )

    severity = (
        requirement.get("severity")
        or "MEDIUM"
    )

    # --------------------------------------------------------
    # Applicability
    # --------------------------------------------------------

    if not is_requirement_applicable(
        requirement,
        applicability,
    ):
        return {
            "result": INCONCLUSIVE,
            "confidence": 0.0,
            "observed_value": None,
            "expected_value": None,
            "reason": (
                "Requirement is not applicable "
                "to the current inspection."
            ),
            "evidence_type": requirement.get(
                "evidence_type"
            ),
            "severity": severity,
        }

    # --------------------------------------------------------
    # Evidence fields
    # --------------------------------------------------------

    evidence_fields = parse_evidence_fields(
        requirement.get(
            "evidence_fields"
        )
    )

    # --------------------------------------------------------
    # Requirement → declaration field mapping
    # --------------------------------------------------------

    requirement_field_map = {

        # ----------------------------------------------------
        # Rule 6
        # ----------------------------------------------------

        "R6_MANUFACTURER_PACKER_IMPORTER":
            [
                "MANUFACTURER",
                "PACKER",
                "IMPORTER",
            ],

        "R6_COUNTRY_OF_ORIGIN":
            [
                "COUNTRY_OF_ORIGIN"
            ],

        "R6_COMMON_GENERIC_NAME":
            [
                "GENERIC_NAME"
            ],

        "R6_GENERIC_NAME":
            [
                "GENERIC_NAME"
            ],

        "R6_NET_QUANTITY":
            [
                "NET_QUANTITY"
            ],

        "R6_MRP":
            [
                "MRP"
            ],

        "R6_UNIT_SALE_PRICE":
            [
                "UNIT_SALE_PRICE"
            ],

        "R6_MANUFACTURE_DATE":
            [
                "MANUFACTURE_DATE"
            ],

        "R6_BEST_BEFORE":
            [
                "BEST_BEFORE"
            ],

        "R6_DIMENSIONS":
            [
                "DIMENSIONS"
            ],

        "R6_CUSTOMER_CARE":
            [
                "CUSTOMER_CARE"
            ],

        # ----------------------------------------------------
        # Rule 6(10) E-commerce
        # ----------------------------------------------------

        "R6_10_MANUFACTURER_PACKER_IMPORTER":
            [
                "MANUFACTURER",
                "PACKER",
                "IMPORTER",
            ],

        "R6_10_COUNTRY_ORIGIN":
            [
                "COUNTRY_OF_ORIGIN"
            ],

        "R6_10_GENERIC_NAME":
            [
                "GENERIC_NAME"
            ],

        "R6_10_NET_QUANTITY":
            [
                "NET_QUANTITY"
            ],

        "R6_10_MRP":
            [
                "MRP"
            ],

        "R6_10_CONSUMER_CARE":
            [
                "CUSTOMER_CARE"
            ],
    }

    fields = requirement_field_map.get(
        requirement_code
    )

    if not fields:
        fields = evidence_fields

    # ========================================================
    # SPECIAL REQUIREMENTS
    # ========================================================

    # --------------------------------------------------------
    # Rule 7 - Character Height
    # --------------------------------------------------------

    if requirement_code == (
        "R7_CHARACTER_HEIGHT"
    ):

        return {
            "result": INCONCLUSIVE,
            "confidence": 0.0,
            "observed_value": None,
            "expected_value": (
                "Minimum character height must "
                "be verified from calibrated "
                "image evidence."
            ),
            "reason": (
                "Character height cannot be "
                "established reliably from OCR "
                "text alone. A calibrated physical "
                "image measurement is required."
            ),
            "evidence_type": "IMAGE_GEOMETRY",
            "severity": severity,
        }

    # --------------------------------------------------------
    # Rule 7 - Character Width
    # --------------------------------------------------------

    if requirement_code == (
        "R7_CHARACTER_WIDTH"
    ):

        return {
            "result": INCONCLUSIVE,
            "confidence": 0.0,
            "observed_value": None,
            "expected_value": (
                "Character width must be verified "
                "from calibrated image evidence."
            ),
            "reason": (
                "Character width cannot be "
                "established reliably from OCR "
                "text alone."
            ),
            "evidence_type": "IMAGE_GEOMETRY",
            "severity": severity,
        }

    # --------------------------------------------------------
    # Rule 7 - PDP
    # --------------------------------------------------------

    if requirement_code == "R7_PDP":

        return {
            "result": INCONCLUSIVE,
            "confidence": 0.0,
            "observed_value": None,
            "expected_value": (
                "Principal display panel placement "
                "requires image-based verification."
            ),
            "reason": (
                "PDP placement cannot be established "
                "from extracted text alone."
            ),
            "evidence_type": "IMAGE_GEOMETRY",
            "severity": severity,
        }

    # --------------------------------------------------------
    # Rule 8 - PDP Placement
    # --------------------------------------------------------

    if requirement_code == (
        "R8_PDP_PLACEMENT"
    ):

        return {
            "result": INCONCLUSIVE,
            "confidence": 0.0,
            "observed_value": None,
            "expected_value": (
                "Mandatory declarations should appear "
                "on the principal display panel."
            ),
            "reason": (
                "PDP placement requires image evidence "
                "and cannot be confirmed from OCR text alone."
            ),
            "evidence_type": "IMAGE_GEOMETRY",
            "severity": severity,
        }

    # --------------------------------------------------------
    # Rule 8 - Quantity Clear Space
    # --------------------------------------------------------

    if requirement_code == (
        "R8_QUANTITY_CLEAR_SPACE"
    ):

        return {
            "result": INCONCLUSIVE,
            "confidence": 0.0,
            "observed_value": None,
            "expected_value": (
                "Required clear space around quantity "
                "declaration must be verified."
            ),
            "reason": (
                "Clear-space measurement requires "
                "image geometry and calibrated dimensions."
            ),
            "evidence_type": "IMAGE_GEOMETRY",
            "severity": severity,
        }

    # --------------------------------------------------------
    # Rule 9 - Legibility / Prominence
    # --------------------------------------------------------

    if requirement_code == (
        "R9_LEGIBLE_PROMINENT"
    ):

        return {
            "result": INCONCLUSIVE,
            "confidence": 0.0,
            "observed_value": None,
            "expected_value": (
                "Declarations must be legible "
                "and prominent."
            ),
            "reason": (
                "Legibility and prominence require "
                "image quality/visual analysis beyond "
                "OCR extraction."
            ),
            "evidence_type": "IMAGE_ANALYSIS",
            "severity": severity,
        }

    # --------------------------------------------------------
    # Rule 9 - MRP / Net Quantity Contrast
    # --------------------------------------------------------

    if requirement_code == (
        "R9_MRP_NET_QUANTITY_CONTRAST"
    ):

        return {
            "result": INCONCLUSIVE,
            "confidence": 0.0,
            "observed_value": None,
            "expected_value": (
                "MRP and net quantity must satisfy "
                "the applicable contrast requirement."
            ),
            "reason": (
                "Contrast requires visual image analysis; "
                "OCR text alone is insufficient."
            ),
            "evidence_type": "IMAGE_ANALYSIS",
            "severity": severity,
        }

    # --------------------------------------------------------
    # Rule 6(10A) Country-of-origin filter
    # --------------------------------------------------------

    if requirement_code == (
        "R6_10A_COUNTRY_ORIGIN_FILTER"
    ) or requirement_code == (
        "R6_10A_COUNTRY_ORIGIN_FILTER_2027"
    ):

        return {
            "result": INCONCLUSIVE,
            "confidence": 0.0,
            "observed_value": None,
            "expected_value": (
                "E-commerce listing must provide "
                "the applicable searchable/sortable "
                "country-of-origin filter."
            ),
            "reason": (
                "Country-of-origin filter functionality "
                "requires inspection of the actual "
                "e-commerce interface."
            ),
            "evidence_type": "ECOMMERCE_INTERFACE",
            "severity": severity,
        }

    # --------------------------------------------------------
    # Rule 26 exemption screen
    # --------------------------------------------------------

    if requirement_code == (
        "R26_EXEMPTION_SCREEN"
    ):

        if not applicability:

            return {
                "result": INCONCLUSIVE,
                "confidence": 0.0,
                "observed_value": None,
                "expected_value": None,
                "reason": (
                    "Applicability information "
                    "is unavailable."
                ),
                "evidence_type": "APPLICABILITY",
                "severity": severity,
            }

        if (
            applicability.exemption_status
            == "UNKNOWN"
        ):

            return {
                "result": INCONCLUSIVE,
                "confidence": 0.0,
                "observed_value": None,
                "expected_value": (
                    "Applicability/exemption status "
                    "must be established."
                ),
                "reason": (
                    "Rule 26 exemption status has not "
                    "yet been conclusively established."
                ),
                "evidence_type": "APPLICABILITY",
                "severity": severity,
            }

        return {
            "result": COMPLIANT,
            "confidence": 1.0,
            "observed_value": (
                applicability.exemption_status
            ),
            "expected_value": None,
            "reason": (
                "Applicability service supplied "
                "an exemption determination."
            ),
            "evidence_type": "APPLICABILITY",
            "severity": severity,
        }

    # ========================================================
    # DECLARATION-BASED REQUIREMENTS
    # ========================================================

    if not fields:

        return {
            "result": INCONCLUSIVE,
            "confidence": 0.0,
            "observed_value": None,
            "expected_value": description,
            "reason": (
                "No machine-evaluable evidence field "
                "is configured for this requirement."
            ),
            "evidence_type": requirement.get(
                "evidence_type"
            ),
            "severity": severity,
        }

    # --------------------------------------------------------
    # Search for acceptable declaration evidence
    # --------------------------------------------------------

    observed = []

    for field in fields:

        value = get_declaration_value(
            declaration_map,
            field,
        )

        if value:

            observed.append(
                {
                    "field": field,
                    "value": value,
                    "confidence": (
                        get_declaration_confidence(
                            declaration_map,
                            field,
                        )
                    ),
                }
            )

    # --------------------------------------------------------
    # Declaration found
    # --------------------------------------------------------

    if observed:

        confidences = [
            item["confidence"]
            for item in observed
            if item["confidence"] is not None
        ]

        confidence = (
            min(confidences)
            if confidences
            else 0.70
        )

        return {
            "result": COMPLIANT,
            "confidence": confidence,
            "observed_value": observed,
            "expected_value": description,
            "reason": (
                f"Required declaration evidence "
                f"was detected for {title}."
            ),
            "evidence_type": (
                requirement.get(
                    "evidence_type"
                )
                or "OCR_DECLARATION"
            ),
            "severity": severity,
        }

    # --------------------------------------------------------
    # Missing evidence is NOT automatically a violation
    # --------------------------------------------------------

    return {
        "result": INCONCLUSIVE,
        "confidence": 0.0,
        "observed_value": None,
        "expected_value": description,
        "reason": (
            f"No evidence for '{title}' was detected "
            f"in the currently processed evidence. "
            f"This is not sufficient to establish a "
            f"violation because the relevant package "
            f"side/listing may not have been provided."
        ),
        "evidence_type": (
            requirement.get(
                "evidence_type"
            )
            or "OCR_DECLARATION"
        ),
        "severity": severity,
    }


# ============================================================
# MAIN EVALUATOR
# ============================================================

def evaluate_inspection(
    db: Session,
    inspection_id: int,
) -> Dict[str, Any]:

    # --------------------------------------------------------
    # 1. Load inspection
    # --------------------------------------------------------

    inspection = (
        db.query(Inspection)
        .filter(
            Inspection.id
            == inspection_id
        )
        .first()
    )

    if not inspection:
        raise ValueError(
            "Inspection not found"
        )

    # --------------------------------------------------------
    # 2. Applicability
    # --------------------------------------------------------

    applicability = (
        db.query(Applicability)
        .filter(
            Applicability.inspection_id
            == inspection_id
        )
        .first()
    )

    # Applicability must be completed before
    # compliance evaluation.
    if applicability is None:

        raise ValueError(
            "Applicability analysis has not "
            "been completed. Run applicability "
            "analysis before compliance evaluation."
        )

    # --------------------------------------------------------
    # 3. Declarations
    # --------------------------------------------------------

    declaration_map = get_declaration_map(
        db,
        inspection_id,
    )

    # --------------------------------------------------------
    # 4. Resolve legal context
    # --------------------------------------------------------

    legal_context = resolve_for_inspection(
        db,
        inspection,
    )

    # --------------------------------------------------------
    # 5. Remove previous findings
    # --------------------------------------------------------

    db.query(
        ComplianceFinding
    ).filter(
        ComplianceFinding.inspection_id
        == inspection_id
    ).delete(
        synchronize_session=False
    )

    # --------------------------------------------------------
    # 6. Evaluate applicable requirements
    # --------------------------------------------------------

    findings = []

    result_counts = {
        COMPLIANT: 0,
        VIOLATION: 0,
        INCONCLUSIVE: 0,
    }

    for rule in legal_context.get(
        "rules",
        [],
    ):

        parent_rule_number = normalize_rule_number(
            rule.get("rule_number")
        )

        parent_sub_rule = normalize_sub_rule(
            rule.get("sub_rule")
        )

        resolved_version = (
            rule.get(
                "resolved_from_version"
            )
            or {}
        )

        legal_version_code = (
            resolved_version.get(
                "version_code"
            )
        )

        legal_effective_date = (
            resolved_version.get(
                "effective_from"
            )
        )

        for raw_requirement in rule.get(
            "requirements",
            [],
        ):

            # ------------------------------------------------
            # CRITICAL FIX
            #
            # The resolver stores rule_number/sub_rule on the
            # parent rule object. Propagate them into the
            # requirement before applicability evaluation.
            # ------------------------------------------------

            requirement = (
                enrich_requirement_with_rule_context(
                    raw_requirement,
                    rule,
                )
            )

            # Explicitly guarantee the parent rule context.
            requirement["rule_number"] = (
                parent_rule_number
            )

            if parent_sub_rule:
                requirement["sub_rule"] = (
                    parent_sub_rule
                )

            # ------------------------------------------------
            # Skip non-applicable requirements completely.
            #
            # This prevents:
            #
            #   - e-commerce rules appearing in physical
            #     inspections
            #   - rules outside RULE_6/7/8/9 appearing
            #     for a normal retail package
            #   - exempt package requirements being evaluated
            # ------------------------------------------------

            if not is_requirement_applicable(
                requirement,
                applicability,
            ):
                continue

            evaluation = evaluate_requirement(
                requirement,
                declaration_map,
                applicability,
            )

            # ------------------------------------------------
            # Create database finding
            # ------------------------------------------------

            finding = ComplianceFinding(

                inspection_id=inspection.id,

                rule_requirement_id=(
                    requirement.get(
                        "id"
                    )
                ),

                legal_version_code=(
                    legal_version_code
                ),

                legal_effective_date=(
                    legal_effective_date
                ),

                rule_number=(
                    parent_rule_number
                ),

                sub_rule=(
                    parent_sub_rule
                    or requirement.get(
                        "sub_rule"
                    )
                ),

                requirement_code=(
                    requirement.get(
                        "requirement_code"
                    )
                ),

                result=(
                    evaluation[
                        "result"
                    ]
                ),

                confidence=(
                    evaluation[
                        "confidence"
                    ]
                ),

                evidence_type=(
                    evaluation[
                        "evidence_type"
                    ]
                ),

                evidence_reference=(
                    requirement.get(
                        "evidence_fields"
                    )
                ),

                observed_value=(
                    str(
                        evaluation[
                            "observed_value"
                        ]
                    )
                    if evaluation[
                        "observed_value"
                    ] is not None
                    else None
                ),

                expected_value=(
                    str(
                        evaluation[
                            "expected_value"
                        ]
                    )
                    if evaluation[
                        "expected_value"
                    ] is not None
                    else None
                ),

                reason=(
                    evaluation[
                        "reason"
                    ]
                ),

                source_reference=(
                    requirement.get(
                        "source_reference"
                    )
                    or rule.get(
                        "source_reference"
                    )
                ),
            )

            db.add(
                finding
            )

            # ------------------------------------------------
            # Response finding
            # ------------------------------------------------

            findings.append(
                {
                    "rule_number": (
                        parent_rule_number
                    ),

                    "sub_rule": (
                        parent_sub_rule
                        or requirement.get(
                            "sub_rule"
                        )
                    ),

                    "requirement_code": (
                        requirement.get(
                            "requirement_code"
                        )
                    ),

                    "title": (
                        requirement.get(
                            "title"
                        )
                    ),

                    "result": (
                        evaluation[
                            "result"
                        ]
                    ),

                    "confidence": (
                        evaluation[
                            "confidence"
                        ]
                    ),

                    "reason": (
                        evaluation[
                            "reason"
                        ]
                    ),

                    "severity": (
                        evaluation[
                            "severity"
                        ]
                    ),

                    "legal_version": (
                        legal_version_code
                    ),

                    "legal_effective_date": (
                        legal_effective_date
                    ),

                    "source_reference": (
                        requirement.get(
                            "source_reference"
                        )
                        or rule.get(
                            "source_reference"
                        )
                    ),
                }
            )

            result_counts[
                evaluation["result"]
            ] += 1

    # --------------------------------------------------------
    # 7. Determine overall result
    # --------------------------------------------------------

    if result_counts[
        VIOLATION
    ] > 0:

        overall_result = VIOLATION

    elif result_counts[
        INCONCLUSIVE
    ] > 0:

        overall_result = INCONCLUSIVE

    else:

        overall_result = COMPLIANT

    # --------------------------------------------------------
    # 8. Save findings
    # --------------------------------------------------------

    db.commit()

    # --------------------------------------------------------
    # 9. Return evaluation result
    # --------------------------------------------------------

    return {

        "message": (
            "Compliance evaluation completed"
        ),

        "inspection_id": (
            inspection.id
        ),

        "inspection_number": (
            inspection.inspection_number
        ),

        "inspection_type": (
            inspection.inspection_type
        ),

        "applicability": {

            "status": (
                applicability.exemption_status
            ),

            "applicable_provisions": (
                parse_evidence_fields(
                    applicability.applicable_provisions
                )
            ),

            "rule_version": (
                applicability.rule_version
            ),
        },

        "legal_context": {

            "inspection_date": (
                legal_context[
                    "inspection_date"
                ]
            ),

            "base_version": (
                legal_context[
                    "base_version"
                ]
            ),

            "latest_amendment": (
                legal_context[
                    "latest_amendment"
                ]
            ),

            "rule_count": (
                legal_context[
                    "rule_count"
                ]
            ),
        },

        "overall_result": (
            overall_result
        ),

        "summary": {

            "compliant": (
                result_counts[
                    COMPLIANT
                ]
            ),

            "violations": (
                result_counts[
                    VIOLATION
                ]
            ),

            "inconclusive": (
                result_counts[
                    INCONCLUSIVE
                ]
            ),

            "total_findings": (
                len(findings)
            ),
        },

        "findings": findings,
    }