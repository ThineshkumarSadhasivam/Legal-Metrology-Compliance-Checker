import json


def classify_applicability(
    inspection_type: str,
    commodity_category: str | None = None,
    package_type: str | None = None,
    is_imported: bool = False,
    is_multi_piece: bool = False,
    is_combination: bool = False,
    is_group_package: bool = False,
):
    """
    Initial applicability classification.

    IMPORTANT:
    This service does NOT make the final compliance decision.

    It identifies the information needed by the
    versioned Legal Metrology rules engine.
    """

    inspection_type = inspection_type.upper()

    # ---------------------------------------------------------
    # Validate inspection type
    # ---------------------------------------------------------

    if inspection_type not in {"PHYSICAL", "ECOMMERCE"}:
        raise ValueError(
            "inspection_type must be PHYSICAL or ECOMMERCE"
        )

    # ---------------------------------------------------------
    # Determine classification confidence
    # ---------------------------------------------------------

    classification_confidence = 0.0

    if commodity_category:
        classification_confidence += 0.30

    if package_type:
        classification_confidence += 0.20

    # Inspection channel is always known from the inspection
    classification_confidence += 0.20

    # Special classification information
    classification_confidence += 0.10

    # Cap confidence
    classification_confidence = min(
        classification_confidence,
        1.0
    )

    # ---------------------------------------------------------
    # Determine classification status
    # ---------------------------------------------------------

    if not commodity_category:
        classification_status = "INCONCLUSIVE"

    elif not package_type:
        classification_status = "UNCERTAIN"

    else:
        classification_status = "CLASSIFIED"

    # ---------------------------------------------------------
    # Initial exemption status
    # ---------------------------------------------------------
    #
    # IMPORTANT:
    # We do NOT assume exemption merely because a field
    # is missing.
    #
    # The actual exemption decision will be made by the
    # versioned rules engine using the applicable provisions.
    # ---------------------------------------------------------

    exemption_status = "UNKNOWN"
    exemption_reason = None

    # ---------------------------------------------------------
    # Initial applicable provisions
    # ---------------------------------------------------------
    #
    # These are candidate provisions only.
    #
    # The final rules engine will determine the exact
    # provisions applicable to the commodity/package.
    # ---------------------------------------------------------

    applicable_provisions = []

    # Packaged commodity inspection
    if commodity_category:

        applicable_provisions.append("RULE_6")
        applicable_provisions.append("RULE_7")
        applicable_provisions.append("RULE_8")

    # E-commerce specific processing
    if inspection_type == "ECOMMERCE":
        applicable_provisions.append("RULE_6_10")

    # Unit sale price candidate
    applicable_provisions.append("RULE_6_11")

    # Imported package
    if is_imported:
        applicable_provisions.append("IMPORTED_PACKAGE")

    # Multi-piece package
    if is_multi_piece:
        applicable_provisions.append("MULTI_PIECE")

    # Combination package
    if is_combination:
        applicable_provisions.append("COMBINATION_PACKAGE")

    # Group package
    if is_group_package:
        applicable_provisions.append("GROUP_PACKAGE")

    # Remove duplicates while preserving order
    applicable_provisions = list(
        dict.fromkeys(applicable_provisions)
    )

    return {
        "inspection_type": inspection_type,
        "commodity_category": commodity_category,
        "package_type": package_type,
        "is_imported": is_imported,
        "is_multi_piece": is_multi_piece,
        "is_combination": is_combination,
        "is_group_package": is_group_package,
        "exemption_status": exemption_status,
        "exemption_reason": exemption_reason,
        "rule_version": None,
        "applicable_provisions": applicable_provisions,
        "classification_confidence": round(
            classification_confidence,
            2
        ),
        "classification_status": classification_status,
    }