# app/services/rules_seed.py

from datetime import date

from app.core.database import SessionLocal

from app.models.rule_version import RuleVersion
from app.models.compliance_rule import ComplianceRule
from app.models.rule_requirement import RuleRequirement


# ============================================================
# OFFICIAL SOURCE REFERENCES
# ============================================================

DCA_RULES_PAGE = (
    "Department of Consumer Affairs - Legal Metrology Rules"
)

BASE_SOURCE = (
    "Legal Metrology (Packaged Commodities) Rules, 2011, "
    "G.S.R. 202(E), dated 07-03-2011"
)

SOURCE_2017 = (
    "Legal Metrology (Packaged Commodities) Amendment Rules, 2017, "
    "G.S.R. 629(E), dated 23-06-2017"
)

SOURCE_2021 = (
    "Legal Metrology (Packaged Commodities) Amendment Rules, 2021, "
    "G.S.R. 779(E), dated 02-11-2021"
)

SOURCE_2022 = (
    "Legal Metrology (Packaged Commodities) Amendment Rules, 2022, "
    "G.S.R. 226(E), dated 28-03-2022"
)

SOURCE_2023 = (
    "Legal Metrology (Packaged Commodities) Amendment Rules, 2023, "
    "G.S.R. 722(E), dated 06-10-2023"
)

SOURCE_2025_1 = (
    "Legal Metrology (Packaged Commodities) Amendment Rules, 2025, "
    "G.S.R. 778(E), dated 23-10-2025"
)

SOURCE_2025_2 = (
    "Legal Metrology (Packaged Commodities) Second Amendment Rules, "
    "2025, G.S.R. 881(E), dated 02-12-2025"
)

SOURCE_2026_1 = (
    "Legal Metrology (Packaged Commodities) Amendment Rules, 2026, "
    "G.S.R. 128(E), dated 13-02-2026"
)

SOURCE_2026_2 = (
    "Legal Metrology (Packaged Commodities) Second Amendment Rules, "
    "2026, dated 27-04-2026"
)


# ============================================================
# RULE VERSION DATA
# ============================================================

RULE_VERSIONS = [
    {
        "version_code": "PCR_2011_BASE",
        "title": "Packaged Commodities Rules 2011 - Base",
        "amendment_year": 2011,
        "notification_number": "G.S.R. 202(E)",
        "notification_date": date(2011, 3, 7),
        "effective_from": date(2011, 4, 1),
        "effective_to": None,
        "is_base_version": True,
        "is_active": True,
        "source_name": DCA_RULES_PAGE,
        "source_reference": BASE_SOURCE,
        "notes": (
            "Principal rules. Subsequent amendments are stored "
            "as separate versioned amendment events."
        ),
    },

    {
        "version_code": "PCR_2017_AMENDMENT",
        "title": "Packaged Commodities Amendment Rules 2017",
        "amendment_year": 2017,
        "notification_number": "G.S.R. 629(E)",
        "notification_date": date(2017, 6, 23),
        "effective_from": date(2018, 1, 1),
        "effective_to": None,
        "is_base_version": False,
        "is_active": True,
        "source_name": DCA_RULES_PAGE,
        "source_reference": SOURCE_2017,
        "notes": (
            "Amendment event. Affected provisions are represented "
            "through versioned rule records."
        ),
    },

    {
        "version_code": "PCR_2021_AMENDMENT",
        "title": "Packaged Commodities Amendment Rules 2021",
        "amendment_year": 2021,
        "notification_number": "G.S.R. 779(E)",
        "notification_date": date(2021, 11, 2),
        "effective_from": date(2022, 4, 1),
        "effective_to": None,
        "is_base_version": False,
        "is_active": True,
        "source_name": DCA_RULES_PAGE,
        "source_reference": SOURCE_2021,
        "notes": (
            "Amendment affecting declarations and related "
            "packaged-commodity requirements."
        ),
    },

    {
        "version_code": "PCR_2022_AMENDMENT",
        "title": "Packaged Commodities Amendment Rules 2022",
        "amendment_year": 2022,
        "notification_number": "G.S.R. 226(E)",
        "notification_date": date(2022, 3, 28),
        "effective_from": date(2022, 10, 1),
        "effective_to": None,
        "is_base_version": False,
        "is_active": True,
        "source_name": DCA_RULES_PAGE,
        "source_reference": SOURCE_2022,
        "notes": (
            "Amendment affecting implementation and declaration "
            "requirements."
        ),
    },

    {
        "version_code": "PCR_2023_AMENDMENT",
        "title": "Packaged Commodities Amendment Rules 2023",
        "amendment_year": 2023,
        "notification_number": "G.S.R. 722(E)",
        "notification_date": date(2023, 10, 6),
        "effective_from": date(2024, 1, 1),
        "effective_to": None,
        "is_base_version": False,
        "is_active": True,
        "source_name": DCA_RULES_PAGE,
        "source_reference": SOURCE_2023,
        "notes": (
            "Amendment event affecting definitions and other "
            "packaged-commodity provisions."
        ),
    },

    {
        "version_code": "PCR_2025_AMENDMENT",
        "title": "Packaged Commodities Amendment Rules 2025",
        "amendment_year": 2025,
        "notification_number": "G.S.R. 778(E)",
        "notification_date": date(2025, 10, 23),
        "effective_from": date(2025, 10, 23),
        "effective_to": None,
        "is_base_version": False,
        "is_active": True,
        "source_name": DCA_RULES_PAGE,
        "source_reference": SOURCE_2025_1,
        "notes": (
            "Amendment containing medical-device related changes "
            "to specified provisions."
        ),
    },

    {
        "version_code": "PCR_2025_SECOND_AMENDMENT",
        "title": "Packaged Commodities Second Amendment Rules 2025",
        "amendment_year": 2025,
        "notification_number": "G.S.R. 881(E)",
        "notification_date": date(2025, 12, 2),
        "effective_from": date(2026, 2, 1),
        "effective_to": None,
        "is_base_version": False,
        "is_active": True,
        "source_name": DCA_RULES_PAGE,
        "source_reference": SOURCE_2025_2,
        "notes": (
            "Rule 26 amendment concerning the specified pan-masala "
            "exemption."
        ),
    },

    {
        "version_code": "PCR_2026_AMENDMENT",
        "title": "Packaged Commodities Amendment Rules 2026",
        "amendment_year": 2026,
        "notification_number": "G.S.R. 128(E)",
        "notification_date": date(2026, 2, 13),
        "effective_from": date(2026, 7, 1),
        "effective_to": date(2027, 6, 30),
        "is_base_version": False,
        "is_active": True,
        "source_name": DCA_RULES_PAGE,
        "source_reference": SOURCE_2026_1,
        "notes": (
            "Rule 6(10A) amendment concerning the searchable and "
            "sortable country-of-origin filter for applicable "
            "imported products on e-commerce listings."
        ),
    },

    {
        "version_code": "PCR_2026_SECOND_AMENDMENT",
        "title": "Packaged Commodities Second Amendment Rules 2026",
        "amendment_year": 2026,
        "notification_number": None,
        "notification_date": date(2026, 4, 27),
        "effective_from": date(2027, 7, 1),
        "effective_to": None,
        "is_base_version": False,
        "is_active": True,
        "source_name": DCA_RULES_PAGE,
        "source_reference": SOURCE_2026_2,
        "notes": (
            "Substitutes Rule 6(10A) and moves the applicable "
            "searchable/sortable country-of-origin filter requirement "
            "to 01-07-2027."
        ),
    },
]


# ============================================================
# CORE RULE DATA
# ============================================================

CORE_RULES = [
    {
        "version_code": "PCR_2011_BASE",
        "rule_number": "2",
        "sub_rule": None,
        "title": "Definitions",
        "requirement_summary": (
            "Definitions used to determine scope, classification "
            "and applicability of the Rules."
        ),
        "legal_text": None,
        "inspection_type": "BOTH",
        "commodity_category": None,
        "applicability_condition": (
            "Used as a classification and applicability dependency."
        ),
        "evidence_required": (
            "Product classification, package characteristics "
            "and relevant declaration evidence."
        ),
        "evaluation_method": "CLASSIFICATION",
        "severity": "INFO",
        "source_reference": BASE_SOURCE,
    },

    {
        "version_code": "PCR_2011_BASE",
        "rule_number": "6",
        "sub_rule": None,
        "title": "Mandatory declarations",
        "requirement_summary": (
            "Mandatory declarations required on applicable "
            "pre-packaged commodities."
        ),
        "legal_text": None,
        "inspection_type": "BOTH",
        "commodity_category": None,
        "applicability_condition": (
            "Subject to applicable exemptions, commodity/package "
            "classification and amendments."
        ),
        "evidence_required": (
            "OCR text, declaration fields, source images, "
            "bounding boxes and package context."
        ),
        "evaluation_method": "DECLARATION_VALIDATION",
        "severity": "HIGH",
        "source_reference": BASE_SOURCE,
    },

    {
        "version_code": "PCR_2011_BASE",
        "rule_number": "7",
        "sub_rule": None,
        "title": "Principal display panel",
        "requirement_summary": (
            "Requirements concerning principal display panel, "
            "character height and related presentation."
        ),
        "legal_text": None,
        "inspection_type": "PHYSICAL",
        "commodity_category": None,
        "applicability_condition": (
            "Requires physical package/image evidence."
        ),
        "evidence_required": (
            "PDP location, image geometry, OCR bounding boxes, "
            "physical scale/calibration evidence and measurements."
        ),
        "evaluation_method": "PHYSICAL_MEASUREMENT",
        "severity": "HIGH",
        "source_reference": BASE_SOURCE,
    },

    {
        "version_code": "PCR_2011_BASE",
        "rule_number": "8",
        "sub_rule": None,
        "title": "Manner of declaration",
        "requirement_summary": (
            "Requirements concerning the manner and presentation "
            "of declarations."
        ),
        "legal_text": None,
        "inspection_type": "PHYSICAL",
        "commodity_category": None,
        "applicability_condition": (
            "Requires adequate physical package evidence."
        ),
        "evidence_required": (
            "OCR text, bounding boxes, package images and "
            "placement/presentation evidence."
        ),
        "evaluation_method": "PLACEMENT_VALIDATION",
        "severity": "MEDIUM",
        "source_reference": BASE_SOURCE,
    },

    {
        "version_code": "PCR_2011_BASE",
        "rule_number": "26",
        "sub_rule": None,
        "title": "Exemptions",
        "requirement_summary": (
            "Exemptions applicable to specified packages "
            "or commodities."
        ),
        "legal_text": None,
        "inspection_type": "BOTH",
        "commodity_category": None,
        "applicability_condition": (
            "Must be evaluated before treating a missing "
            "declaration as a violation."
        ),
        "evidence_required": (
            "Commodity category, package characteristics, "
            "intended use and relevant exemption evidence."
        ),
        "evaluation_method": "EXEMPTION_CHECK",
        "severity": "CRITICAL",
        "source_reference": BASE_SOURCE,
    },
]


# ============================================================
# RULE 6 REQUIREMENTS
# ============================================================

RULE_6_REQUIREMENTS = [
    {
        "requirement_code": "R6_MANUFACTURER_PACKER_IMPORTER",
        "requirement_title": "Manufacturer / packer / importer declaration",
        "requirement_description": (
            "Applicable package must contain the prescribed "
            "manufacturer, packer or importer identification."
        ),
        "evidence_type": "OCR_DECLARATION",
        "evidence_fields": "MANUFACTURER,PACKER,IMPORTER",
        "evaluation_method": "DECLARATION_PRESENCE",
        "violation_condition": (
            "Reliable evidence demonstrates that the applicable "
            "declaration is absent or non-compliant."
        ),
        "inconclusive_condition": (
            "Required package surfaces are not sufficiently visible "
            "or OCR evidence is inadequate."
        ),
        "severity": "HIGH",
        "source_reference": BASE_SOURCE,
    },
    {
        "requirement_code": "R6_COMMON_GENERIC_NAME",
        "requirement_title": "Common or generic name",
        "requirement_description": (
            "The common or generic name of the commodity must "
            "be declared where required."
        ),
        "evidence_type": "OCR_DECLARATION",
        "evidence_fields": "PRODUCT_NAME",
        "evaluation_method": "DECLARATION_PRESENCE",
        "violation_condition": (
            "Reliable evidence demonstrates absence of the "
            "required common/generic name."
        ),
        "inconclusive_condition": (
            "Available images do not adequately expose the "
            "relevant declaration area."
        ),
        "severity": "HIGH",
        "source_reference": BASE_SOURCE,
    },
    {
        "requirement_code": "R6_NET_QUANTITY",
        "requirement_title": "Net quantity",
        "requirement_description": (
            "Net quantity must be declared in the prescribed "
            "standard unit or number, as applicable."
        ),
        "evidence_type": "OCR_DECLARATION",
        "evidence_fields": "NET_QUANTITY",
        "evaluation_method": "QUANTITY_VALIDATION",
        "violation_condition": (
            "Reliable evidence demonstrates that the required "
            "net quantity declaration is absent or non-compliant."
        ),
        "inconclusive_condition": (
            "Quantity declaration cannot be reliably located or read."
        ),
        "severity": "HIGH",
        "source_reference": BASE_SOURCE,
    },
    {
        "requirement_code": "R6_MRP",
        "requirement_title": "Maximum retail price",
        "requirement_description": (
            "Maximum retail price must be declared in the "
            "prescribed form where applicable."
        ),
        "evidence_type": "OCR_DECLARATION",
        "evidence_fields": "MRP",
        "evaluation_method": "PRICE_VALIDATION",
        "violation_condition": (
            "Reliable evidence demonstrates that the required "
            "MRP declaration is absent or non-compliant."
        ),
        "inconclusive_condition": (
            "Relevant package surface is unavailable or the "
            "price cannot be reliably read."
        ),
        "severity": "HIGH",
        "source_reference": BASE_SOURCE,
    },
    {
        "requirement_code": "R6_CUSTOMER_CARE",
        "requirement_title": "Consumer care details",
        "requirement_description": (
            "Required consumer/customer care contact information "
            "must be declared."
        ),
        "evidence_type": "OCR_DECLARATION",
        "evidence_fields": "CUSTOMER_CARE",
        "evaluation_method": "CONTACT_VALIDATION",
        "violation_condition": (
            "Reliable evidence demonstrates absence or "
            "non-compliance of required consumer care details."
        ),
        "inconclusive_condition": (
            "Contact declaration is not visible or cannot "
            "be reliably read."
        ),
        "severity": "MEDIUM",
        "source_reference": BASE_SOURCE,
    },
    {
        "requirement_code": "R6_COUNTRY_OF_ORIGIN",
        "requirement_title": "Country of origin",
        "requirement_description": (
            "Country of origin declaration applies to imported "
            "products subject to the applicable rule version."
        ),
        "evidence_type": "OCR_DECLARATION",
        "evidence_fields": "COUNTRY_OF_ORIGIN",
        "evaluation_method": "ORIGIN_VALIDATION",
        "violation_condition": (
            "Imported-product evidence exists and the applicable "
            "country-of-origin declaration is demonstrably absent "
            "or non-compliant."
        ),
        "inconclusive_condition": (
            "Imported status or relevant package evidence cannot "
            "be reliably established."
        ),
        "severity": "HIGH",
        "source_reference": BASE_SOURCE,
    },
    {
        "requirement_code": "R6_UNIT_SALE_PRICE",
        "requirement_title": "Unit sale price",
        "requirement_description": (
            "Where applicable, unit sale price must be declared "
            "according to the applicable unit and quantity rules."
        ),
        "evidence_type": "OCR_DECLARATION",
        "evidence_fields": "UNIT_SALE_PRICE",
        "evaluation_method": "UNIT_PRICE_VALIDATION",
        "violation_condition": (
            "Reliable evidence demonstrates absence or "
            "non-compliance of a required unit sale price."
        ),
        "inconclusive_condition": (
            "Commodity, quantity or price evidence is insufficient "
            "to establish the applicable unit sale price requirement."
        ),
        "severity": "HIGH",
        "source_reference": (
            SOURCE_2021 + "; " + SOURCE_2022
        ),
    },
]


# ============================================================
# RULE 7 REQUIREMENTS
# ============================================================

RULE_7_REQUIREMENTS = [
    {
        "requirement_code": "R7_PDP",
        "requirement_title": "Principal display panel",
        "requirement_description": (
            "Required declarations must be evaluated in the "
            "principal display panel context."
        ),
        "evidence_type": "IMAGE_GEOMETRY",
        "evidence_fields": "PDP_BOUNDING_BOX",
        "evaluation_method": "PDP_DETECTION",
        "violation_condition": (
            "Reliable physical evidence demonstrates "
            "non-compliance with the applicable PDP requirement."
        ),
        "inconclusive_condition": (
            "PDP cannot be reliably identified from the "
            "available images."
        ),
        "severity": "HIGH",
        "source_reference": BASE_SOURCE,
    },
    {
        "requirement_code": "R7_CHARACTER_HEIGHT",
        "requirement_title": "Character height",
        "requirement_description": (
            "Numerals/letters subject to Rule 7 must satisfy "
            "the applicable minimum character-height requirement."
        ),
        "evidence_type": "PHYSICAL_MEASUREMENT",
        "evidence_fields": (
            "OCR_BBOX,PHYSICAL_SCALE,PDP_AREA"
        ),
        "evaluation_method": "FONT_HEIGHT_MEASUREMENT",
        "violation_condition": (
            "Validated physical measurement is below the "
            "applicable minimum threshold."
        ),
        "inconclusive_condition": (
            "No reliable physical scale, distorted image geometry, "
            "insufficient resolution or borderline measurement."
        ),
        "severity": "HIGH",
        "source_reference": BASE_SOURCE,
    },
    {
        "requirement_code": "R7_CHARACTER_WIDTH",
        "requirement_title": "Character width",
        "requirement_description": (
            "Applicable character-width requirement must be "
            "evaluated with the prescribed exceptions."
        ),
        "evidence_type": "PHYSICAL_MEASUREMENT",
        "evidence_fields": (
            "OCR_BBOX,PHYSICAL_SCALE"
        ),
        "evaluation_method": "FONT_WIDTH_MEASUREMENT",
        "violation_condition": (
            "Validated physical measurement demonstrates "
            "non-compliance with the applicable width requirement."
        ),
        "inconclusive_condition": (
            "Physical scale or character geometry is insufficient "
            "for a reliable measurement."
        ),
        "severity": "HIGH",
        "source_reference": BASE_SOURCE,
    },
]


# ============================================================
# RULE 8 REQUIREMENTS
# ============================================================

RULE_8_REQUIREMENTS = [
    {
        "requirement_code": "R8_DECLARATION_PLACEMENT",
        "requirement_title": "Declaration placement",
        "requirement_description": (
            "The manner and placement of declarations must "
            "satisfy the applicable requirements."
        ),
        "evidence_type": "IMAGE_GEOMETRY",
        "evidence_fields": (
            "OCR_BBOX,PDP_BOUNDING_BOX"
        ),
        "evaluation_method": "PLACEMENT_ANALYSIS",
        "violation_condition": (
            "Reliable image evidence demonstrates "
            "non-compliant placement or presentation."
        ),
        "inconclusive_condition": (
            "Available images do not permit reliable "
            "determination of placement."
        ),
        "severity": "MEDIUM",
        "source_reference": BASE_SOURCE,
    },
]


# ============================================================
# 2026 RULE 6(10A)
# ============================================================

RULE_6_10A_2026 = {
    "requirement_code": "R6_10A_COUNTRY_ORIGIN_FILTER",
    "requirement_title": "E-commerce country-of-origin filter",
    "requirement_description": (
        "For applicable imported products offered through "
        "an e-commerce entity, the product listing must satisfy "
        "the applicable searchable and sortable country-of-origin "
        "filter requirement."
    ),
    "evidence_type": "ECOMMERCE_PAGE",
    "evidence_fields": (
        "SOURCE_URL,LISTING_TEXT,STRUCTURED_DATA,FILTER_UI"
    ),
    "evaluation_method": "ECOMMERCE_FILTER_VALIDATION",
    "violation_condition": (
        "The product is established as imported and the applicable "
        "e-commerce listing lacks the required searchable and "
        "sortable country-of-origin filter."
    ),
    "inconclusive_condition": (
        "The listing is inaccessible, dynamically rendered content "
        "cannot be inspected, imported status is uncertain, or "
        "filter functionality cannot be reliably verified."
    ),
    "severity": "HIGH",
    "source_reference": SOURCE_2026_1,
}


RULE_6_10A_2027 = {
    "requirement_code": "R6_10A_COUNTRY_ORIGIN_FILTER_2027",
    "requirement_title": (
        "E-commerce country-of-origin filter - 2027 version"
    ),
    "requirement_description": (
        "The substituted Rule 6(10A) requirement applies "
        "from 1 July 2027."
    ),
    "evidence_type": "ECOMMERCE_PAGE",
    "evidence_fields": (
        "SOURCE_URL,LISTING_TEXT,STRUCTURED_DATA,FILTER_UI"
    ),
    "evaluation_method": "ECOMMERCE_FILTER_VALIDATION",
    "violation_condition": (
        "The applicable imported-product listing does not "
        "provide the required searchable and sortable "
        "country-of-origin filter."
    ),
    "inconclusive_condition": (
        "Listing or filter functionality cannot be reliably inspected."
    ),
    "severity": "HIGH",
    "source_reference": SOURCE_2026_2,
}


# ============================================================
# DATABASE HELPERS
# ============================================================

def get_or_create_version(db, data):
    """
    Creates a RuleVersion if it does not already exist.

    Existing versions are reused so the seed is idempotent.
    """

    version = (
        db.query(RuleVersion)
        .filter(
            RuleVersion.version_code
            == data["version_code"]
        )
        .first()
    )

    if version:
        return version

    version = RuleVersion(
        version_code=data["version_code"],
        title=data["title"],
        amendment_year=data.get("amendment_year"),
        notification_number=data.get("notification_number"),
        notification_date=data.get("notification_date"),
        effective_from=data["effective_from"],
        effective_to=data.get("effective_to"),
        is_base_version=data.get(
            "is_base_version",
            False,
        ),
        is_active=data.get(
            "is_active",
            True,
        ),
        source_name=data.get("source_name"),
        source_reference=data.get(
            "source_reference"
        ),
        notes=data.get("notes"),
    )

    db.add(version)
    db.flush()

    return version


def get_or_create_rule(
    db,
    version,
    data,
):
    """
    Creates a ComplianceRule linked to a RuleVersion.

    IMPORTANT:
    Only ComplianceRule fields are passed here.
    """

    rule = (
        db.query(ComplianceRule)
        .filter(
            ComplianceRule.rule_version_id
            == version.id,

            ComplianceRule.rule_number
            == data["rule_number"],

            ComplianceRule.sub_rule
            == data.get("sub_rule"),
        )
        .first()
    )

    if rule:
        return rule

    rule = ComplianceRule(
        rule_version_id=version.id,
        rule_number=data["rule_number"],
        sub_rule=data.get("sub_rule"),
        title=data["title"],
        requirement_summary=data[
            "requirement_summary"
        ],
        legal_text=data.get("legal_text"),
        inspection_type=data.get(
            "inspection_type"
        ),
        commodity_category=data.get(
            "commodity_category"
        ),
        applicability_condition=data.get(
            "applicability_condition"
        ),
        evidence_required=data.get(
            "evidence_required"
        ),
        evaluation_method=data.get(
            "evaluation_method"
        ),
        severity=data.get(
            "severity"
        ),
        is_active=data.get(
            "is_active",
            True,
        ),
        source_reference=data.get(
            "source_reference"
        ),
    )

    db.add(rule)
    db.flush()

    return rule


def get_or_create_requirement(
    db,
    rule,
    data,
):
    """
    Creates a RuleRequirement.

    IMPORTANT:
    RuleRequirement does NOT have rule_number.
    The relationship to the rule is represented by
    compliance_rule_id.
    """

    requirement = (
        db.query(RuleRequirement)
        .filter(
            RuleRequirement.compliance_rule_id
            == rule.id,

            RuleRequirement.requirement_code
            == data["requirement_code"],
        )
        .first()
    )

    if requirement:
        return requirement

    requirement = RuleRequirement(
        compliance_rule_id=rule.id,
        requirement_code=data[
            "requirement_code"
        ],
        requirement_title=data[
            "requirement_title"
        ],
        requirement_description=data[
            "requirement_description"
        ],
        evidence_type=data.get(
            "evidence_type"
        ),
        evidence_fields=data.get(
            "evidence_fields"
        ),
        evaluation_method=data.get(
            "evaluation_method"
        ),
        violation_condition=data.get(
            "violation_condition"
        ),
        inconclusive_condition=data.get(
            "inconclusive_condition"
        ),
        severity=data.get(
            "severity"
        ),
        is_mandatory=data.get(
            "is_mandatory",
            True,
        ),
        is_active=data.get(
            "is_active",
            True,
        ),
        source_reference=data.get(
            "source_reference"
        ),
    )

    db.add(requirement)
    db.flush()

    return requirement


# ============================================================
# FIND RULE
# ============================================================

def find_rule(
    db,
    version_id,
    rule_number,
    sub_rule=None,
):
    """
    Finds a ComplianceRule for a specific version.
    """

    return (
        db.query(ComplianceRule)
        .filter(
            ComplianceRule.rule_version_id
            == version_id,

            ComplianceRule.rule_number
            == rule_number,

            ComplianceRule.sub_rule
            == sub_rule,
        )
        .first()
    )


# ============================================================
# SEED BASE REQUIREMENTS
# ============================================================

def seed_base_requirements(
    db,
    version,
):
    """
    Seeds Rule 6, Rule 7 and Rule 8 requirements
    against the corresponding base rules.
    """

    requirement_groups = [
        (
            "6",
            RULE_6_REQUIREMENTS,
        ),
        (
            "7",
            RULE_7_REQUIREMENTS,
        ),
        (
            "8",
            RULE_8_REQUIREMENTS,
        ),
    ]

    for rule_number, requirements in (
        requirement_groups
    ):

        rule = find_rule(
            db,
            version.id,
            rule_number,
            None,
        )

        if not rule:
            print(
                f"WARNING: Rule {rule_number} "
                f"not found for {version.version_code}"
            )
            continue

        for requirement_data in requirements:

            get_or_create_requirement(
                db,
                rule,
                requirement_data,
            )


# ============================================================
# SEED 2026 RULE 6(10A)
# ============================================================

def seed_2026_10a(
    db,
    version,
    requirement_data,
):
    """
    Creates Rule 6(10A) and its requirement for
    the appropriate version.
    """

    rule = find_rule(
        db,
        version.id,
        "6",
        "10A",
    )

    if not rule:

        rule = get_or_create_rule(
            db,
            version,
            {
                "rule_number": "6",
                "sub_rule": "10A",
                "title": (
                    "E-commerce imported-product "
                    "country-of-origin filter"
                ),
                "requirement_summary": (
                    requirement_data[
                        "requirement_description"
                    ]
                ),
                "legal_text": None,
                "inspection_type": "ECOMMERCE",
                "commodity_category": None,
                "applicability_condition": (
                    "Imported product offered for sale "
                    "through an applicable e-commerce entity."
                ),
                "evidence_required": (
                    requirement_data[
                        "evidence_fields"
                    ]
                ),
                "evaluation_method": (
                    requirement_data[
                        "evaluation_method"
                    ]
                ),
                "severity": (
                    requirement_data[
                        "severity"
                    ]
                ),
                "source_reference": (
                    requirement_data[
                        "source_reference"
                    ]
                ),
            },
        )

    get_or_create_requirement(
        db,
        rule,
        requirement_data,
    )


# ============================================================
# MAIN SEED FUNCTION
# ============================================================

def seed_rules():

    db = SessionLocal()

    try:

        print(
            "\n=========================================="
        )
        print(
            "LEGAL METROLOGY RULE SEED"
        )
        print(
            "=========================================="
        )

        # ----------------------------------------------------
        # 1. RULE VERSIONS
        # ----------------------------------------------------

        versions = {}

        print(
            "\n[1/4] Seeding rule versions..."
        )

        for version_data in RULE_VERSIONS:

            version = get_or_create_version(
                db,
                version_data,
            )

            versions[
                version_data["version_code"]
            ] = version

            print(
                f"  ✓ {version.version_code}"
            )

        # ----------------------------------------------------
        # 2. BASE RULES
        # ----------------------------------------------------

        print(
            "\n[2/4] Seeding core rules..."
        )

        base_version = versions[
            "PCR_2011_BASE"
        ]

        for rule_data in CORE_RULES:

            rule = get_or_create_rule(
                db,
                base_version,
                rule_data,
            )

            print(
                f"  ✓ Rule {rule.rule_number}"
            )

        # ----------------------------------------------------
        # 3. BASE REQUIREMENTS
        # ----------------------------------------------------

        print(
            "\n[3/4] Seeding rule requirements..."
        )

        seed_base_requirements(
            db,
            base_version,
        )

        print(
            "  ✓ Rule 6 requirements"
        )

        print(
            "  ✓ Rule 7 requirements"
        )

        print(
            "  ✓ Rule 8 requirements"
        )

        # ----------------------------------------------------
        # 4. 2026 RULE 6(10A)
        # ----------------------------------------------------

        print(
            "\n[4/4] Seeding 2026 Rule 6(10A)..."
        )

        version_2026 = versions[
            "PCR_2026_AMENDMENT"
        ]

        seed_2026_10a(
            db,
            version_2026,
            RULE_6_10A_2026,
        )

        print(
            "  ✓ Rule 6(10A) - 2026"
        )

        version_2026_second = versions[
            "PCR_2026_SECOND_AMENDMENT"
        ]

        seed_2026_10a(
            db,
            version_2026_second,
            RULE_6_10A_2027,
        )

        print(
            "  ✓ Rule 6(10A) - 2027 version"
        )

        # ----------------------------------------------------
        # COMMIT
        # ----------------------------------------------------

        db.commit()

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        version_count = (
            db.query(RuleVersion)
            .count()
        )

        rule_count = (
            db.query(ComplianceRule)
            .count()
        )

        requirement_count = (
            db.query(RuleRequirement)
            .count()
        )

        print(
            "\n=========================================="
        )
        print(
            "SEED COMPLETED SUCCESSFULLY"
        )
        print(
            "=========================================="
        )

        print(
            f"Rule versions : {version_count}"
        )

        print(
            f"Compliance rules : {rule_count}"
        )

        print(
            f"Rule requirements : {requirement_count}"
        )

        print(
            "==========================================\n"
        )

    except Exception as exc:

        db.rollback()

        print(
            "\n=========================================="
        )
        print(
            "SEED FAILED"
        )
        print(
            "=========================================="
        )

        print(
            f"Error: {exc}"
        )

        print(
            "Database transaction rolled back."
        )

        print(
            "==========================================\n"
        )

        raise

    finally:

        db.close()


# ============================================================
# SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":
    seed_rules()