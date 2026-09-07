# app/services/verified_core_rules_seed.py

import json

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.rule_version import RuleVersion
from app.models.compliance_rule import ComplianceRule
from app.models.rule_requirement import RuleRequirement


# ============================================================
# VERSION
# ============================================================

def get_version(
    db: Session,
    version_code: str,
):
    version = (
        db.query(RuleVersion)
        .filter(
            RuleVersion.version_code == version_code
        )
        .first()
    )

    if not version:
        raise RuntimeError(
            f"Rule version not found: {version_code}"
        )

    return version


# ============================================================
# RULE
# ============================================================

def upsert_rule(
    db: Session,
    *,
    version_code: str,
    rule_number: str,
    sub_rule: str | None,
    title: str,
    requirement_summary: str,
    legal_text: str,
    inspection_type: str,
    applicability_condition: str,
    evidence_required: str,
    evaluation_method: str,
    severity: str,
    source_reference: str,
):
    version = get_version(
        db,
        version_code,
    )

    rule = (
        db.query(ComplianceRule)
        .filter(
            ComplianceRule.rule_version_id
            == version.id,

            ComplianceRule.rule_number
            == rule_number,

            ComplianceRule.sub_rule
            == sub_rule,
        )
        .first()
    )

    if not rule:

        rule = ComplianceRule(
            rule_version_id=version.id,
            rule_number=rule_number,
            sub_rule=sub_rule,
        )

        db.add(rule)

    rule.title = title
    rule.requirement_summary = requirement_summary
    rule.legal_text = legal_text
    rule.inspection_type = inspection_type
    rule.applicability_condition = (
        applicability_condition
    )
    rule.evidence_required = (
        evidence_required
    )
    rule.evaluation_method = (
        evaluation_method
    )
    rule.severity = severity
    rule.source_reference = (
        source_reference
    )
    rule.is_active = True

    db.flush()

    return rule


# ============================================================
# REQUIREMENT
# ============================================================

def upsert_requirement(
    db: Session,
    *,
    rule,
    requirement_code: str,
    requirement_title: str,
    requirement_description: str,
    evidence_type: str,
    evidence_fields: list[str],
    evaluation_method: str,
    violation_condition: str,
    inconclusive_condition: str,
    severity: str,
    source_reference: str,
):
    requirement = (
        db.query(RuleRequirement)
        .filter(
            RuleRequirement.compliance_rule_id
            == rule.id,

            RuleRequirement.requirement_code
            == requirement_code,
        )
        .first()
    )

    if not requirement:

        requirement = RuleRequirement(
            compliance_rule_id=rule.id,
            requirement_code=requirement_code,
        )

        db.add(requirement)

    requirement.requirement_title = (
        requirement_title
    )

    requirement.requirement_description = (
        requirement_description
    )

    requirement.evidence_type = (
        evidence_type
    )

    requirement.evidence_fields = json.dumps(
        evidence_fields
    )

    requirement.evaluation_method = (
        evaluation_method
    )

    requirement.violation_condition = (
        violation_condition
    )

    requirement.inconclusive_condition = (
        inconclusive_condition
    )

    requirement.severity = severity

    requirement.source_reference = (
        source_reference
    )

    requirement.is_mandatory = True
    requirement.is_active = True

    return requirement


# ============================================================
# RULE 6 — CURRENT DECLARATION FAMILY
# ============================================================

def seed_rule_6(
    db: Session,
):
    """
    Current core Rule 6 requirements.

    These are evidence requirements rather than a verbatim
    reproduction of the statutory text.
    """

    rule = upsert_rule(
        db,
        version_code="PCR_2022_AMENDMENT",
        rule_number="6",
        sub_rule=None,
        title="Mandatory declarations",
        requirement_summary=(
            "Retail packages must carry the declarations "
            "required by Rule 6, subject to applicability "
            "conditions and exemptions."
        ),
        legal_text=(
            "Verified Rule 6 declaration framework "
            "including manufacturer/packer/importer, "
            "country of origin where applicable, generic "
            "name, net quantity, retail sale price, "
            "unit sale price where applicable, date "
            "information, best-before/use-by where "
            "applicable, dimensions where relevant, "
            "and consumer-care information."
        ),
        inspection_type="BOTH",
        applicability_condition=(
            "Applies to packages within Chapter II unless "
            "an applicable exemption or special provision "
            "removes or modifies the requirement."
        ),
        evidence_required=(
            "OCR declarations, image evidence, package "
            "classification and applicability result."
        ),
        evaluation_method="DECLARATION_VALIDATION",
        severity="HIGH",
        source_reference=(
            "Legal Metrology (Packaged Commodities) "
            "Rules, 2011, Rule 6; consolidated Rules "
            "and applicable amendments."
        ),
    )

    requirements = [

        (
            "R6_MANUFACTURER_PACKER_IMPORTER",
            "Manufacturer / packer / importer declaration",
            "Verify the responsible entity declaration "
            "and address information applicable to the package.",
            [
                "MANUFACTURER",
                "PACKER",
                "IMPORTER",
            ],
        ),

        (
            "R6_COUNTRY_OF_ORIGIN",
            "Country of origin",
            "Verify country-of-origin information for "
            "imported packages.",
            [
                "COUNTRY_OF_ORIGIN",
                "IS_IMPORTED",
            ],
        ),

        (
            "R6_GENERIC_NAME",
            "Common or generic name",
            "Verify that the commodity is identified "
            "using the required common or generic name.",
            [
                "PRODUCT_NAME",
                "COMMODITY_CATEGORY",
            ],
        ),

        (
            "R6_NET_QUANTITY",
            "Net quantity",
            "Verify net quantity in the applicable "
            "standard unit of weight, measure or number.",
            [
                "NET_QUANTITY",
                "NORMALIZED_NET_QUANTITY",
            ],
        ),

        (
            "R6_MRP",
            "Retail sale price",
            "Verify the declared retail sale price "
            "and applicable inclusive-tax requirement.",
            [
                "MRP",
                "MRP_VALUE",
                "CURRENCY",
            ],
        ),

        (
            "R6_UNIT_SALE_PRICE",
            "Unit sale price",
            "Verify unit sale price where Rule 6(11) "
            "makes the declaration applicable.",
            [
                "UNIT_SALE_PRICE",
                "NET_QUANTITY",
                "PACKAGE_TYPE",
            ],
        ),

        (
            "R6_MANUFACTURE_DATE",
            "Manufacture date",
            "Verify month and year manufacture information "
            "where applicable.",
            [
                "MANUFACTURE_DATE",
            ],
        ),

        (
            "R6_BEST_BEFORE",
            "Best before / use by",
            "Verify the applicable date declaration where "
            "the commodity may become unfit over time.",
            [
                "BEST_BEFORE",
                "USE_BY",
                "EXPIRY_DATE",
            ],
        ),

        (
            "R6_DIMENSIONS",
            "Dimensions",
            "Verify dimensions where the dimensions of "
            "the commodity are relevant to sale or use.",
            [
                "DIMENSIONS",
            ],
        ),

        (
            "R6_CONSUMER_CARE",
            "Consumer care information",
            "Verify consumer-care contact information.",
            [
                "CUSTOMER_CARE",
                "PHONE",
                "EMAIL",
                "ADDRESS",
            ],
        ),
    ]

    for (
        code,
        title,
        description,
        fields,
    ) in requirements:

        upsert_requirement(
            db,
            rule=rule,
            requirement_code=code,
            requirement_title=title,
            requirement_description=description,
            evidence_type="OCR_DECLARATION",
            evidence_fields=fields,
            evaluation_method=(
                "DECLARATION_PRESENCE_AND_NORMALIZATION"
            ),
            violation_condition=(
                "Required declaration is reliably "
                "observed to be absent or materially "
                "non-conforming after applicability "
                "has been established."
            ),
            inconclusive_condition=(
                "Required declaration cannot be reliably "
                "observed because submitted evidence is "
                "incomplete, unreadable or insufficient."
            ),
            severity="HIGH",
            source_reference=(
                "PCR 2011 Rule 6 and applicable amendments."
            ),
        )


# ============================================================
# RULE 6(10) — E-COMMERCE
# ============================================================

def seed_rule_6_10(
    db: Session,
):
    rule = upsert_rule(
        db,
        version_code="PCR_2017_AMENDMENT",
        rule_number="6",
        sub_rule="10",
        title="E-commerce declarations",
        requirement_summary=(
            "Mandatory Rule 6(1) declarations, except "
            "the month and year of manufacture or packing, "
            "must be displayed on the digital/electronic "
            "network used for e-commerce transactions."
        ),
        legal_text=(
            "E-commerce entity declaration framework "
            "introduced by the 2017 amendment."
        ),
        inspection_type="ECOMMERCE",
        applicability_condition=(
            "Applies when the inspection concerns an "
            "e-commerce transaction/listing."
        ),
        evidence_required=(
            "Listing text, structured product data, "
            "visible product information and screenshots."
        ),
        evaluation_method="ECOMMERCE_DECLARATION_VALIDATION",
        severity="HIGH",
        source_reference=(
            "G.S.R. 629(E), dated 23-06-2017; "
            "Rule 6(10), effective 01-01-2018."
        ),
    )

    requirements = [

        (
            "R6_10_MANUFACTURER_PACKER_IMPORTER",
            "Online manufacturer / packer / importer",
            "Verify applicable responsible-entity information "
            "is displayed on the e-commerce listing.",
            [
                "MANUFACTURER",
                "PACKER",
                "IMPORTER",
            ],
        ),

        (
            "R6_10_COUNTRY_ORIGIN",
            "Online country of origin",
            "Verify country-of-origin information where "
            "the product is imported.",
            [
                "COUNTRY_OF_ORIGIN",
                "IS_IMPORTED",
            ],
        ),

        (
            "R6_10_GENERIC_NAME",
            "Online generic name",
            "Verify the commodity's common or generic name "
            "is displayed.",
            [
                "PRODUCT_NAME",
                "COMMODITY_CATEGORY",
            ],
        ),

        (
            "R6_10_NET_QUANTITY",
            "Online net quantity",
            "Verify the net quantity is displayed.",
            [
                "NET_QUANTITY",
                "NORMALIZED_NET_QUANTITY",
            ],
        ),

        (
            "R6_10_MRP",
            "Online MRP",
            "Verify applicable retail sale price information "
            "is displayed.",
            [
                "MRP",
                "MRP_VALUE",
            ],
        ),

        (
            "R6_10_CONSUMER_CARE",
            "Online consumer care",
            "Verify consumer-care information is displayed.",
            [
                "CUSTOMER_CARE",
                "PHONE",
                "EMAIL",
                "ADDRESS",
            ],
        ),
    ]

    for (
        code,
        title,
        description,
        fields,
    ) in requirements:

        upsert_requirement(
            db,
            rule=rule,
            requirement_code=code,
            requirement_title=title,
            requirement_description=description,
            evidence_type="ECOMMERCE_LISTING",
            evidence_fields=fields,
            evaluation_method=(
                "LISTING_FIELD_VALIDATION"
            ),
            violation_condition=(
                "Required online declaration is reliably "
                "absent from the accessible listing."
            ),
            inconclusive_condition=(
                "Listing content is inaccessible, dynamically "
                "hidden, blocked or insufficient to establish "
                "the presence/absence of the declaration."
            ),
            severity="HIGH",
            source_reference=(
                "G.S.R. 629(E), Rule 6(10)."
            ),
        )


# ============================================================
# RULE 6(10A) — 2026
# ============================================================

def seed_rule_6_10a(
    db: Session,
):
    rule = upsert_rule(
        db,
        version_code="PCR_2026_AMENDMENT",
        rule_number="6",
        sub_rule="10A",
        title=(
            "E-commerce imported-product "
            "country-of-origin filter"
        ),
        requirement_summary=(
            "For imported products sold through e-commerce, "
            "the platform must provide the specified "
            "country-of-origin searchable/sortable filter."
        ),
        legal_text=(
            "2026 amendment provision for searchable and "
            "sortable country-of-origin filtering."
        ),
        inspection_type="ECOMMERCE",
        applicability_condition=(
            "Applies to an e-commerce entity selling "
            "imported products."
        ),
        evidence_required=(
            "Accessible listing/catalogue interface showing "
            "country-of-origin filter functionality."
        ),
        evaluation_method="ECOMMERCE_FILTER_VALIDATION",
        severity="HIGH",
        source_reference=(
            "G.S.R. 128(E), dated 13-02-2026; "
            "effective 01-07-2026."
        ),
    )

    upsert_requirement(
        db,
        rule=rule,
        requirement_code=(
            "R6_10A_COUNTRY_ORIGIN_FILTER"
        ),
        requirement_title=(
            "Searchable and sortable country-of-origin filter"
        ),
        requirement_description=(
            "Verify that imported-product listings can be "
            "searched/sorted using the country-of-origin "
            "filter required by the applicable version."
        ),
        evidence_type="ECOMMERCE_FUNCTIONAL",
        evidence_fields=[
            "IS_IMPORTED",
            "COUNTRY_OF_ORIGIN_FILTER_PRESENT",
            "FILTER_SEARCHABLE",
            "FILTER_SORTABLE",
            "FILTER_SCREENSHOT",
        ],
        evaluation_method=(
            "FUNCTIONAL_FILTER_TEST"
        ),
        violation_condition=(
            "Imported products are offered for sale and "
            "the required country-of-origin filter is "
            "reliably observed to be absent or non-functional."
        ),
        inconclusive_condition=(
            "The platform is inaccessible or the available "
            "evidence does not permit reliable functional "
            "verification."
        ),
        severity="HIGH",
        source_reference=(
            "G.S.R. 128(E), Rule 6(10A)."
        ),
    )


# ============================================================
# RULE 7
# ============================================================

def seed_rule_7(
    db: Session,
):
    rule = upsert_rule(
        db,
        version_code="PCR_2017_AMENDMENT",
        rule_number="7",
        sub_rule=None,
        title="Principal display panel",
        requirement_summary=(
            "The height of numerals and letters must meet "
            "the applicable Rule 7 table and width must be "
            "at least one-third of height, subject to the "
            "specified exceptions."
        ),
        legal_text=(
            "Rule 7 controls principal display panel "
            "measurement and minimum character dimensions."
        ),
        inspection_type="PHYSICAL",
        applicability_condition=(
            "Applies to physical package declarations "
            "subject to applicable exemptions and other-law "
            "exceptions."
        ),
        evidence_required=(
            "PDP boundary/area, character bounding boxes, "
            "calibrated physical scale and package surface type."
        ),
        evaluation_method="PHYSICAL_MEASUREMENT",
        severity="HIGH",
        source_reference=(
            "G.S.R. 629(E), Rule 7, effective 01-01-2018; "
            "current consolidated Rule 7."
        ),
    )

    # Important: values below are the Rule 7 table
    # used by the current compliance measurement layer.

    table = {
        "A_LE_50": {
            "normal_mm": 1.0,
            "formed_mm": 2.0,
        },
        "A_50_100": {
            "normal_mm": 1.5,
            "formed_mm": 3.0,
        },
        "A_100_500": {
            "normal_mm": 2.5,
            "formed_mm": 4.0,
        },
        "A_500_2500": {
            "normal_mm": 4.0,
            "formed_mm": 6.0,
        },
        "A_GT_2500": {
            "normal_mm": 6.0,
            "formed_mm": 6.0,
        },
    }

    upsert_requirement(
        db,
        rule=rule,
        requirement_code="R7_CHARACTER_HEIGHT",
        requirement_title="Minimum character height",
        requirement_description=json.dumps(
            table
        ),
        evidence_type="PHYSICAL_IMAGE_MEASUREMENT",
        evidence_fields=[
            "PDP_AREA_CM2",
            "CHARACTER_HEIGHT_MM",
            "CHARACTER_BBOX",
            "SURFACE_TYPE",
            "CALIBRATION_REFERENCE",
        ],
        evaluation_method=(
            "PDP_AREA_AND_CHARACTER_HEIGHT"
        ),
        violation_condition=(
            "Measured character height is below the "
            "applicable minimum after reliable calibration."
        ),
        inconclusive_condition=(
            "PDP area, character boundary, scale calibration "
            "or surface geometry cannot be reliably determined."
        ),
        severity="HIGH",
        source_reference=(
            "PCR Rule 7(2) and Table-I."
        ),
    )

    upsert_requirement(
        db,
        rule=rule,
        requirement_code="R7_CHARACTER_WIDTH",
        requirement_title="Minimum character width",
        requirement_description=(
            "Character width must be at least one-third "
            "of character height, subject to the stated "
            "exceptions."
        ),
        evidence_type="PHYSICAL_IMAGE_MEASUREMENT",
        evidence_fields=[
            "CHARACTER_HEIGHT_MM",
            "CHARACTER_WIDTH_MM",
            "CHARACTER_BBOX",
        ],
        evaluation_method=(
            "CHARACTER_WIDTH_HEIGHT_RATIO"
        ),
        violation_condition=(
            "Measured width is less than one-third of "
            "height for a character to which the rule applies."
        ),
        inconclusive_condition=(
            "Character segmentation or measurement is "
            "not sufficiently reliable."
        ),
        severity="MEDIUM",
        source_reference=(
            "PCR Rule 7(3)."
        ),
    )


# ============================================================
# RULE 8
# ============================================================

def seed_rule_8(
    db: Session,
):
    rule = upsert_rule(
        db,
        version_code="PCR_2011_BASE",
        rule_number="8",
        sub_rule=None,
        title="Declaration where to appear",
        requirement_summary=(
            "Required declarations must appear on the "
            "principal display panel and the prescribed "
            "clear area must be maintained around the "
            "quantity declaration."
        ),
        legal_text=(
            "Rule 8 governs placement of declarations "
            "on the principal display panel."
        ),
        inspection_type="PHYSICAL",
        applicability_condition=(
            "Applies to physical packages subject to "
            "applicable exemptions."
        ),
        evidence_required=(
            "PDP location, quantity declaration bounding box "
            "and surrounding printed-information geometry."
        ),
        evaluation_method="PLACEMENT_VALIDATION",
        severity="HIGH",
        source_reference=(
            "PCR Rule 8."
        ),
    )

    upsert_requirement(
        db,
        rule=rule,
        requirement_code="R8_PDP_PLACEMENT",
        requirement_title="Declarations on PDP",
        requirement_description=(
            "Verify that required declarations appear on "
            "the principal display panel."
        ),
        evidence_type="PHYSICAL_LAYOUT",
        evidence_fields=[
            "PDP_BOUNDARY",
            "DECLARATION_BBOX",
            "DECLARATION_FIELD",
        ],
        evaluation_method="DECLARATION_PDP_INTERSECTION",
        violation_condition=(
            "A required declaration is reliably located "
            "outside the principal display panel."
        ),
        inconclusive_condition=(
            "PDP boundaries or declaration location cannot "
            "be reliably determined."
        ),
        severity="HIGH",
        source_reference="PCR Rule 8(1).",
    )

    upsert_requirement(
        db,
        rule=rule,
        requirement_code="R8_QUANTITY_CLEAR_SPACE",
        requirement_title="Clear space around quantity",
        requirement_description=(
            "Verify the prescribed clear space around "
            "the quantity declaration."
        ),
        evidence_type="PHYSICAL_LAYOUT",
        evidence_fields=[
            "QUANTITY_BBOX",
            "CHARACTER_HEIGHT_MM",
            "NEIGHBOURING_TEXT_BBOXES",
        ],
        evaluation_method="QUANTITY_CLEAR_SPACE",
        violation_condition=(
            "Printed information intrudes into the "
            "prescribed surrounding quantity-declaration area."
        ),
        inconclusive_condition=(
            "The quantity bounding box or surrounding "
            "printed-information geometry cannot be reliably measured."
        ),
        severity="HIGH",
        source_reference="PCR Rule 8(1).",
    )


# ============================================================
# RULE 9
# ============================================================

def seed_rule_9(
    db: Session,
):
    rule = upsert_rule(
        db,
        version_code="PCR_2011_BASE",
        rule_number="9",
        sub_rule=None,
        title="Manner in which declaration shall be made",
        requirement_summary=(
            "Declarations must be legible and prominent; "
            "MRP and net quantity numerals must have the "
            "required contrast, subject to the stated exceptions."
        ),
        legal_text=(
            "Rule 9 governs legibility, prominence, contrast "
            "and related presentation requirements."
        ),
        inspection_type="PHYSICAL",
        applicability_condition=(
            "Applies to physical package declarations."
        ),
        evidence_required=(
            "OCR confidence, image quality, text/background "
            "contrast and package presentation evidence."
        ),
        evaluation_method="PRESENTATION_VALIDATION",
        severity="MEDIUM",
        source_reference="PCR Rule 9.",
    )

    upsert_requirement(
        db,
        rule=rule,
        requirement_code="R9_LEGIBLE_PROMINENT",
        requirement_title="Legible and prominent",
        requirement_description=(
            "Verify that required declarations are "
            "legible and prominent."
        ),
        evidence_type="OCR_AND_IMAGE",
        evidence_fields=[
            "OCR_CONFIDENCE",
            "CHARACTER_BBOX",
            "IMAGE_QUALITY",
            "DECLARATION_TEXT",
        ],
        evaluation_method="LEGIBILITY_VALIDATION",
        violation_condition=(
            "Declaration is reliably shown to be illegible "
            "or insufficiently prominent."
        ),
        inconclusive_condition=(
            "Image quality or OCR/visual evidence is "
            "insufficient to establish legibility."
        ),
        severity="MEDIUM",
        source_reference="PCR Rule 9(1)(a).",
    )

    upsert_requirement(
        db,
        rule=rule,
        requirement_code="R9_MRP_NET_QUANTITY_CONTRAST",
        requirement_title="MRP and net quantity contrast",
        requirement_description=(
            "Verify the required contrast of MRP and "
            "net-quantity numerals against the label background, "
            "subject to applicable exceptions."
        ),
        evidence_type="IMAGE_ANALYSIS",
        evidence_fields=[
            "MRP_BBOX",
            "NET_QUANTITY_BBOX",
            "FOREGROUND_COLOR",
            "BACKGROUND_COLOR",
            "CONTRAST_SCORE",
            "SURFACE_TYPE",
        ],
        evaluation_method="CONTRAST_ANALYSIS",
        violation_condition=(
            "Applicable MRP or net-quantity numerals "
            "lack the required conspicuous contrast."
        ),
        inconclusive_condition=(
            "Lighting, glare, image compression, surface "
            "geometry or color segmentation prevents reliable assessment."
        ),
        severity="MEDIUM",
        source_reference="PCR Rule 9(1)(b).",
    )


# ============================================================
# RULE 26
# ============================================================

def seed_rule_26(
    db: Session,
):
    rule = upsert_rule(
        db,
        version_code="PCR_2011_BASE",
        rule_number="26",
        sub_rule=None,
        title="Exemption in respect of certain packages",
        requirement_summary=(
            "Applicability must be checked against the "
            "exemption provisions of Rule 26 before declaring "
            "a package non-compliant with a normally applicable "
            "requirement."
        ),
        legal_text=(
            "Rule 26 contains specified package exemptions "
            "and exceptions; applicability is provision-specific."
        ),
        inspection_type="BOTH",
        applicability_condition=(
            "Evaluate package type, commodity, quantity, "
            "channel and relevant special conditions."
        ),
        evidence_required=(
            "Commodity classification, net quantity, package "
            "type, intended consumer/channel and relevant "
            "special-category evidence."
        ),
        evaluation_method="EXEMPTION_CHECK",
        severity="CRITICAL",
        source_reference=(
            "PCR Rule 26 and applicable amendments."
        ),
    )

    upsert_requirement(
        db,
        rule=rule,
        requirement_code="R26_EXEMPTION_SCREEN",
        requirement_title="Rule 26 exemption screen",
        requirement_description=(
            "Determine whether a Rule 26 exemption applies "
            "before evaluating the affected declarations."
        ),
        evidence_type="CLASSIFICATION_AND_CONTEXT",
        evidence_fields=[
            "COMMODITY_CATEGORY",
            "NET_QUANTITY",
            "PACKAGE_TYPE",
            "IS_IMPORTED",
            "IS_MULTI_PIECE",
            "IS_COMBINATION",
            "IS_GROUP_PACKAGE",
            "INTENDED_CONSUMER",
        ],
        evaluation_method="RULE_26_APPLICABILITY",
        violation_condition=(
            "A requirement is treated as exempt even though "
            "the available evidence establishes that the "
            "Rule 26 exemption does not apply."
        ),
        inconclusive_condition=(
            "Required classification or contextual evidence "
            "is insufficient to determine exemption applicability."
        ),
        severity="CRITICAL",
        source_reference="PCR Rule 26.",
    )


# ============================================================
# MAIN
# ============================================================

def seed():
    db = SessionLocal()

    try:

        print(
            "\n=========================================="
        )
        print(
            "VERIFIED CORE PCR RULE SEED"
        )
        print(
            "=========================================="
        )

        seed_rule_6(db)
        print("  ✓ Rule 6")

        seed_rule_6_10(db)
        print("  ✓ Rule 6(10)")

        seed_rule_6_10a(db)
        print("  ✓ Rule 6(10A)")

        seed_rule_7(db)
        print("  ✓ Rule 7")

        seed_rule_8(db)
        print("  ✓ Rule 8")

        seed_rule_9(db)
        print("  ✓ Rule 9")

        seed_rule_26(db)
        print("  ✓ Rule 26")

        db.commit()

        rule_count = (
            db.query(ComplianceRule)
            .filter(
                ComplianceRule.is_active.is_(True)
            )
            .count()
        )

        requirement_count = (
            db.query(RuleRequirement)
            .filter(
                RuleRequirement.is_active.is_(True)
            )
            .count()
        )

        print(
            "\n------------------------------------------"
        )

        print(
            f"Active compliance rules : "
            f"{rule_count}"
        )

        print(
            f"Active requirements     : "
            f"{requirement_count}"
        )

        print(
            "Seed completed successfully."
        )

        print(
            "==========================================\n"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()