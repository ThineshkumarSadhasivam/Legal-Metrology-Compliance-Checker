from app.core.database import SessionLocal

from app.models.rule_version import RuleVersion
from app.models.compliance_rule import ComplianceRule
from app.models.rule_requirement import RuleRequirement


# ============================================================
# RULE DEFINITIONS
# ============================================================

RULES = [

    # --------------------------------------------------------
    # RULE 2 - DEFINITIONS
    # --------------------------------------------------------

    {
        "rule_number": "2",
        "sub_rule": "DEFINITIONS",
        "title": "Definitions",
        "summary": (
            "Definitions used to determine whether a package, "
            "commodity, transaction or entity falls within "
            "particular provisions of the Rules."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "CLASSIFICATION",
        "severity": "INFO",
        "applicability": (
            "Used as an upstream dependency for applicability."
        ),
    },

    # --------------------------------------------------------
    # RULE 3 - APPLICATION
    # --------------------------------------------------------

    {
        "rule_number": "3",
        "sub_rule": None,
        "title": "Application of Chapter",
        "summary": (
            "Determines packages and commodities to which "
            "the applicable chapter provisions apply or do not apply."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "APPLICABILITY_CHECK",
        "severity": "CRITICAL",
        "applicability": (
            "Evaluated before applying declaration requirements."
        ),
    },

    # --------------------------------------------------------
    # RULE 4
    # --------------------------------------------------------

    {
        "rule_number": "4",
        "sub_rule": None,
        "title": "Specific requirements for packages",
        "summary": (
            "Requirements concerning packages and declarations "
            "under the Rules."
        ),
        "inspection_type": "PHYSICAL",
        "evaluation_method": "PACKAGE_VALIDATION",
        "severity": "HIGH",
        "applicability": (
            "Applicable where the package falls within the "
            "relevant packaged-commodity provisions."
        ),
    },

    # --------------------------------------------------------
    # RULE 5
    # --------------------------------------------------------

    {
        "rule_number": "5",
        "sub_rule": None,
        "title": "Provisions relating to declarations",
        "summary": (
            "General requirements associated with declarations "
            "on applicable packaged commodities."
        ),
        "inspection_type": "PHYSICAL",
        "evaluation_method": "DECLARATION_VALIDATION",
        "severity": "HIGH",
        "applicability": (
            "Applicable where the corresponding declaration "
            "provisions are triggered."
        ),
    },

    # --------------------------------------------------------
    # RULE 6
    # --------------------------------------------------------

    {
        "rule_number": "6",
        "sub_rule": None,
        "title": "Declarations to be made on every package",
        "summary": (
            "Mandatory declarations applicable to pre-packaged "
            "commodities."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "DECLARATION_VALIDATION",
        "severity": "HIGH",
        "applicability": (
            "Subject to Rule 3, Rule 26 and other applicable "
            "commodity/package-specific provisions."
        ),
    },

    # --------------------------------------------------------
    # RULE 6(10)
    # --------------------------------------------------------

    {
        "rule_number": "6",
        "sub_rule": "10",
        "title": "E-commerce declarations",
        "summary": (
            "Requirements applicable to declarations made "
            "through e-commerce platforms/listings."
        ),
        "inspection_type": "ECOMMERCE",
        "evaluation_method": "ECOMMERCE_DECLARATION_VALIDATION",
        "severity": "HIGH",
        "applicability": (
            "Applicable to relevant e-commerce listings."
        ),
    },

    # --------------------------------------------------------
    # RULE 6(10A)
    # --------------------------------------------------------

    {
        "rule_number": "6",
        "sub_rule": "10A",
        "title": "Country-of-origin filter",
        "summary": (
            "Country-of-origin filtering requirement for "
            "applicable imported products offered through "
            "e-commerce."
        ),
        "inspection_type": "ECOMMERCE",
        "evaluation_method": "ECOMMERCE_FILTER_VALIDATION",
        "severity": "HIGH",
        "applicability": (
            "Applicable according to the effective date and "
            "import/e-commerce conditions."
        ),
    },

    # --------------------------------------------------------
    # RULE 7
    # --------------------------------------------------------

    {
        "rule_number": "7",
        "sub_rule": None,
        "title": "Principal display panel",
        "summary": (
            "Requirements concerning principal display panel, "
            "character height and character width."
        ),
        "inspection_type": "PHYSICAL",
        "evaluation_method": "PHYSICAL_MEASUREMENT",
        "severity": "HIGH",
        "applicability": (
            "Applicable to physical packages subject to the Rules, "
            "with specific exemptions or alternative regimes where applicable."
        ),
    },

    # --------------------------------------------------------
    # RULE 8
    # --------------------------------------------------------

    {
        "rule_number": "8",
        "sub_rule": None,
        "title": "Manner of declaration",
        "summary": (
            "Requirements concerning the manner and presentation "
            "of declarations."
        ),
        "inspection_type": "PHYSICAL",
        "evaluation_method": "PLACEMENT_VALIDATION",
        "severity": "HIGH",
        "applicability": (
            "Applicable to declarations required on applicable packages."
        ),
    },

    # --------------------------------------------------------
    # RULE 9
    # --------------------------------------------------------

    {
        "rule_number": "9",
        "sub_rule": None,
        "title": "Declaration of quantity",
        "summary": (
            "Requirements concerning declaration of quantity "
            "and prescribed units."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "QUANTITY_VALIDATION",
        "severity": "HIGH",
        "applicability": (
            "Applicable where the commodity is sold by weight, "
            "measure, length, area or number as relevant."
        ),
    },

    # --------------------------------------------------------
    # RULE 10
    # --------------------------------------------------------

    {
        "rule_number": "10",
        "sub_rule": None,
        "title": "Sale of commodities by number",
        "summary": (
            "Requirements associated with commodities sold "
            "by number or count."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "QUANTITY_VALIDATION",
        "severity": "HIGH",
        "applicability": (
            "Applicable where the commodity is sold by number/count."
        ),
    },

    # --------------------------------------------------------
    # RULE 11
    # --------------------------------------------------------

    {
        "rule_number": "11",
        "sub_rule": None,
        "title": "Declaration of unit sale price",
        "summary": (
            "Requirements concerning declaration of unit sale price "
            "for applicable packaged commodities."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "UNIT_PRICE_VALIDATION",
        "severity": "HIGH",
        "applicability": (
            "Applicable according to commodity, quantity and "
            "effective amendment provisions."
        ),
    },

    # --------------------------------------------------------
    # RULE 12
    # --------------------------------------------------------

    {
        "rule_number": "12",
        "sub_rule": None,
        "title": "Declaration of dimensions",
        "summary": (
            "Requirements relating to dimensions where the "
            "Rules require such declaration."
        ),
        "inspection_type": "PHYSICAL",
        "evaluation_method": "DIMENSION_VALIDATION",
        "severity": "MEDIUM",
        "applicability": (
            "Applicable to commodities/packages for which "
            "dimension declaration is prescribed."
        ),
    },

    # --------------------------------------------------------
    # RULE 13
    # --------------------------------------------------------

    {
        "rule_number": "13",
        "sub_rule": None,
        "title": "Declaration of retail sale price",
        "summary": (
            "Requirements concerning maximum retail price "
            "and its declaration."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "PRICE_VALIDATION",
        "severity": "HIGH",
        "applicability": (
            "Applicable to relevant retail packaged commodities."
        ),
    },

    # --------------------------------------------------------
    # RULE 14
    # --------------------------------------------------------

    {
        "rule_number": "14",
        "sub_rule": None,
        "title": "Declaration of date information",
        "summary": (
            "Requirements concerning applicable date-related "
            "declarations."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "DATE_DECLARATION_VALIDATION",
        "severity": "HIGH",
        "applicability": (
            "Applicable to commodities where date declarations "
            "are prescribed."
        ),
    },

    # --------------------------------------------------------
    # RULE 15
    # --------------------------------------------------------

    {
        "rule_number": "15",
        "sub_rule": None,
        "title": "Consumer care information",
        "summary": (
            "Requirements concerning consumer care information "
            "where applicable."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "CONTACT_VALIDATION",
        "severity": "MEDIUM",
        "applicability": (
            "Applicable where prescribed by the Rules."
        ),
    },

    # --------------------------------------------------------
    # RULE 16
    # --------------------------------------------------------

    {
        "rule_number": "16",
        "sub_rule": None,
        "title": "Imported packages",
        "summary": (
            "Requirements relevant to imported packaged commodities."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "IMPORT_VALIDATION",
        "severity": "HIGH",
        "applicability": (
            "Applicable where imported status is established."
        ),
    },

    # --------------------------------------------------------
    # RULE 17
    # --------------------------------------------------------

    {
        "rule_number": "17",
        "sub_rule": None,
        "title": "Wholesale packages",
        "summary": (
            "Requirements applicable to wholesale packages."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "PACKAGE_TYPE_VALIDATION",
        "severity": "HIGH",
        "applicability": (
            "Applicable where the package qualifies as a "
            "wholesale package."
        ),
    },

    # --------------------------------------------------------
    # RULE 18
    # --------------------------------------------------------

    {
        "rule_number": "18",
        "sub_rule": None,
        "title": "Institutional / industrial consumers",
        "summary": (
            "Requirements and exclusions concerning institutional "
            "or industrial consumers."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "APPLICABILITY_CHECK",
        "severity": "CRITICAL",
        "applicability": (
            "Determined using consumer/package classification."
        ),
    },

    # --------------------------------------------------------
    # RULE 19
    # --------------------------------------------------------

    {
        "rule_number": "19",
        "sub_rule": None,
        "title": "Combination packages",
        "summary": (
            "Requirements applicable to combination packages."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "PACKAGE_CLASSIFICATION",
        "severity": "HIGH",
        "applicability": (
            "Applicable when a package contains multiple "
            "commodities forming a combination package."
        ),
    },

    # --------------------------------------------------------
    # RULE 20
    # --------------------------------------------------------

    {
        "rule_number": "20",
        "sub_rule": None,
        "title": "Multi-piece packages",
        "summary": (
            "Requirements applicable to multi-piece packages."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "PACKAGE_CLASSIFICATION",
        "severity": "HIGH",
        "applicability": (
            "Applicable where multiple pieces/items are packaged "
            "and sold as a package."
        ),
    },

    # --------------------------------------------------------
    # RULE 21
    # --------------------------------------------------------

    {
        "rule_number": "21",
        "sub_rule": None,
        "title": "Group packages",
        "summary": (
            "Requirements applicable to group packages."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "PACKAGE_CLASSIFICATION",
        "severity": "HIGH",
        "applicability": (
            "Applicable where the package qualifies as a group package."
        ),
    },

    # --------------------------------------------------------
    # RULE 22
    # --------------------------------------------------------

    {
        "rule_number": "22",
        "sub_rule": None,
        "title": "Specific package declarations",
        "summary": (
            "Additional declaration requirements applicable "
            "to specified package categories."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "DECLARATION_VALIDATION",
        "severity": "HIGH",
        "applicability": (
            "Triggered according to package classification."
        ),
    },

    # --------------------------------------------------------
    # RULE 23
    # --------------------------------------------------------

    {
        "rule_number": "23",
        "sub_rule": None,
        "title": "Special commodity/package requirements",
        "summary": (
            "Additional requirements applying to specified "
            "commodities or package forms."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "SPECIAL_RULE_VALIDATION",
        "severity": "HIGH",
        "applicability": (
            "Requires commodity-specific classification."
        ),
    },

    # --------------------------------------------------------
    # RULE 24
    # --------------------------------------------------------

    {
        "rule_number": "24",
        "sub_rule": None,
        "title": "Special provisions",
        "summary": (
            "Additional provisions applicable to specified "
            "commodities or circumstances."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "SPECIAL_RULE_VALIDATION",
        "severity": "HIGH",
        "applicability": (
            "Triggered only where the relevant condition is established."
        ),
    },

    # --------------------------------------------------------
    # RULE 25
    # --------------------------------------------------------

    {
        "rule_number": "25",
        "sub_rule": None,
        "title": "Exemption-related provisions",
        "summary": (
            "Specific exemption or special treatment provisions "
            "where applicable."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "EXEMPTION_CHECK",
        "severity": "CRITICAL",
        "applicability": (
            "Evaluated during applicability resolution."
        ),
    },

    # --------------------------------------------------------
    # RULE 26
    # --------------------------------------------------------

    {
        "rule_number": "26",
        "sub_rule": None,
        "title": "Exemptions",
        "summary": (
            "Specified packages and commodities may be exempt "
            "from particular provisions subject to the applicable "
            "conditions."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "EXEMPTION_CHECK",
        "severity": "CRITICAL",
        "applicability": (
            "Must be evaluated before concluding that a missing "
            "declaration constitutes a violation."
        ),
    },

    # --------------------------------------------------------
    # RULE 27
    # --------------------------------------------------------

    {
        "rule_number": "27",
        "sub_rule": None,
        "title": "Registration requirements",
        "summary": (
            "Registration-related requirements for applicable "
            "manufacturers, packers or importers."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "REGISTRATION_VALIDATION",
        "severity": "HIGH",
        "applicability": (
            "Applicable where the inspected entity falls within "
            "the registration provisions."
        ),
    },

    # --------------------------------------------------------
    # RULE 28
    # --------------------------------------------------------

    {
        "rule_number": "28",
        "sub_rule": None,
        "title": "Registration particulars",
        "summary": (
            "Requirements relating to particulars maintained "
            "under registration provisions."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "REGISTRATION_VALIDATION",
        "severity": "MEDIUM",
        "applicability": (
            "Applicable to entities subject to registration."
        ),
    },

    # --------------------------------------------------------
    # RULE 29
    # --------------------------------------------------------

    {
        "rule_number": "29",
        "sub_rule": None,
        "title": "Verification of declarations",
        "summary": (
            "Verification-related requirements associated with "
            "declared package information."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "DECLARATION_VERIFICATION",
        "severity": "HIGH",
        "applicability": (
            "Triggered where verification evidence is available."
        ),
    },

    # --------------------------------------------------------
    # RULE 30
    # --------------------------------------------------------

    {
        "rule_number": "30",
        "sub_rule": None,
        "title": "Records and related requirements",
        "summary": (
            "Record-related requirements under applicable provisions."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "RECORD_VALIDATION",
        "severity": "MEDIUM",
        "applicability": (
            "Applicable where the inspected entity is required "
            "to maintain the relevant records."
        ),
    },

    # --------------------------------------------------------
    # RULE 31
    # --------------------------------------------------------

    {
        "rule_number": "31",
        "sub_rule": None,
        "title": "Offences / compliance-related provisions",
        "summary": (
            "Compliance provisions associated with contraventions "
            "and enforcement."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "ENFORCEMENT_REFERENCE",
        "severity": "CRITICAL",
        "applicability": (
            "Used for enforcement reference rather than OCR-only "
            "product assessment."
        ),
    },

    # --------------------------------------------------------
    # RULE 32
    # --------------------------------------------------------

    {
        "rule_number": "32",
        "sub_rule": None,
        "title": "General provisions",
        "summary": (
            "General provisions under the Rules."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "GENERAL_VALIDATION",
        "severity": "MEDIUM",
        "applicability": (
            "Applied only when the relevant condition is established."
        ),
    },

    # --------------------------------------------------------
    # RULE 33
    # --------------------------------------------------------

    {
        "rule_number": "33",
        "sub_rule": None,
        "title": "Relaxation / related provision",
        "summary": (
            "Provision allowing specified treatment subject to "
            "the conditions prescribed by the Rules."
        ),
        "inspection_type": "BOTH",
        "evaluation_method": "SPECIAL_CONDITION_CHECK",
        "severity": "HIGH",
        "applicability": (
            "Must be considered where a specified special regime applies."
        ),
    },
]


# ============================================================
# REQUIREMENTS
# ============================================================

REQUIREMENTS = [

    {
        "rule_number": "3",
        "code": "R3_SCOPE",
        "title": "Scope applicability",
        "description": (
            "Determine whether the package falls within the "
            "applicable chapter based on package quantity, "
            "commodity and consumer classification."
        ),
        "evidence_type": "CLASSIFICATION",
        "evidence_fields": (
            "COMMODITY_CATEGORY,PACKAGE_TYPE,NET_QUANTITY,"
            "CONSUMER_TYPE"
        ),
        "method": "APPLICABILITY_CHECK",
        "severity": "CRITICAL",
    },

    {
        "rule_number": "6",
        "code": "R6_PRODUCT_NAME",
        "title": "Common or generic name",
        "description": (
            "Detect and validate the applicable common or generic "
            "name declaration."
        ),
        "evidence_type": "OCR_DECLARATION",
        "evidence_fields": "PRODUCT_NAME",
        "method": "DECLARATION_PRESENCE",
        "severity": "HIGH",
    },

    {
        "rule_number": "6",
        "code": "R6_MANUFACTURER",
        "title": "Manufacturer / packer / importer",
        "description": (
            "Detect the applicable manufacturer, packer or importer "
            "identification."
        ),
        "evidence_type": "OCR_DECLARATION",
        "evidence_fields": (
            "MANUFACTURER,PACKER,IMPORTER"
        ),
        "method": "DECLARATION_PRESENCE",
        "severity": "HIGH",
    },

    {
        "rule_number": "6",
        "code": "R6_NET_QUANTITY",
        "title": "Net quantity",
        "description": (
            "Detect and validate the applicable net quantity "
            "declaration."
        ),
        "evidence_type": "OCR_DECLARATION",
        "evidence_fields": "NET_QUANTITY",
        "method": "QUANTITY_VALIDATION",
        "severity": "HIGH",
    },

    {
        "rule_number": "6",
        "code": "R6_MRP",
        "title": "Maximum retail price",
        "description": (
            "Detect and validate the applicable maximum retail "
            "price declaration."
        ),
        "evidence_type": "OCR_DECLARATION",
        "evidence_fields": "MRP",
        "method": "PRICE_VALIDATION",
        "severity": "HIGH",
    },

    {
        "rule_number": "6",
        "code": "R6_CUSTOMER_CARE",
        "title": "Consumer care",
        "description": (
            "Detect applicable consumer care contact information."
        ),
        "evidence_type": "OCR_DECLARATION",
        "evidence_fields": "CUSTOMER_CARE",
        "method": "CONTACT_VALIDATION",
        "severity": "MEDIUM",
    },

    {
        "rule_number": "6",
        "code": "R6_COUNTRY_ORIGIN",
        "title": "Country of origin",
        "description": (
            "Validate country-of-origin declaration where "
            "the package is an imported product."
        ),
        "evidence_type": "OCR_DECLARATION",
        "evidence_fields": "COUNTRY_OF_ORIGIN",
        "method": "ORIGIN_VALIDATION",
        "severity": "HIGH",
    },

    {
        "rule_number": "6",
        "code": "R6_UNIT_SALE_PRICE",
        "title": "Unit sale price",
        "description": (
            "Validate unit sale price according to the applicable "
            "quantity/unit and amendment provisions."
        ),
        "evidence_type": "OCR_DECLARATION",
        "evidence_fields": (
            "UNIT_SALE_PRICE,NET_QUANTITY,MRP"
        ),
        "method": "UNIT_PRICE_VALIDATION",
        "severity": "HIGH",
    },

    {
        "rule_number": "6(10)",
        "code": "R6_10_ECOMMERCE_DECLARATIONS",
        "title": "E-commerce declarations",
        "description": (
            "Validate declarations required to be made available "
            "through the applicable e-commerce listing."
        ),
        "evidence_type": "ECOMMERCE_PAGE",
        "evidence_fields": (
            "SOURCE_URL,LISTING_TEXT,STRUCTURED_DATA"
        ),
        "method": "ECOMMERCE_DECLARATION_VALIDATION",
        "severity": "HIGH",
    },

    {
        "rule_number": "6(10A)",
        "code": "R6_10A_ORIGIN_FILTER",
        "title": "Country-of-origin filter",
        "description": (
            "Validate the applicable searchable and sortable "
            "country-of-origin filter requirement."
        ),
        "evidence_type": "ECOMMERCE_PAGE",
        "evidence_fields": (
            "SOURCE_URL,FILTER_UI,LISTING_TEXT"
        ),
        "method": "ECOMMERCE_FILTER_VALIDATION",
        "severity": "HIGH",
    },

    {
        "rule_number": "7",
        "code": "R7_PDP",
        "title": "Principal display panel",
        "description": (
            "Identify the principal display panel and determine "
            "whether required declarations are presented in the "
            "applicable location."
        ),
        "evidence_type": "IMAGE_GEOMETRY",
        "evidence_fields": (
            "PDP_BOUNDING_BOX,OCR_BBOX"
        ),
        "method": "PDP_DETECTION",
        "severity": "HIGH",
    },

    {
        "rule_number": "7",
        "code": "R7_CHARACTER_HEIGHT",
        "title": "Character height",
        "description": (
            "Measure character height using validated physical "
            "scale and compare with the applicable threshold."
        ),
        "evidence_type": "PHYSICAL_MEASUREMENT",
        "evidence_fields": (
            "OCR_BBOX,PHYSICAL_SCALE,PDP_AREA"
        ),
        "method": "FONT_HEIGHT_MEASUREMENT",
        "severity": "HIGH",
    },

    {
        "rule_number": "7",
        "code": "R7_CHARACTER_WIDTH",
        "title": "Character width",
        "description": (
            "Measure character width and compare against the "
            "applicable requirement."
        ),
        "evidence_type": "PHYSICAL_MEASUREMENT",
        "evidence_fields": (
            "OCR_BBOX,PHYSICAL_SCALE"
        ),
        "method": "FONT_WIDTH_MEASUREMENT",
        "severity": "HIGH",
    },

    {
        "rule_number": "8",
        "code": "R8_PLACEMENT",
        "title": "Declaration placement",
        "description": (
            "Evaluate placement and presentation of applicable "
            "declarations."
        ),
        "evidence_type": "IMAGE_GEOMETRY",
        "evidence_fields": (
            "OCR_BBOX,PDP_BOUNDING_BOX"
        ),
        "method": "PLACEMENT_ANALYSIS",
        "severity": "MEDIUM",
    },

    {
        "rule_number": "9",
        "code": "R9_QUANTITY",
        "title": "Quantity declaration",
        "description": (
            "Validate quantity against the applicable measurement "
            "basis and standard unit."
        ),
        "evidence_type": "OCR_DECLARATION",
        "evidence_fields": (
            "NET_QUANTITY"
        ),
        "method": "QUANTITY_VALIDATION",
        "severity": "HIGH",
    },

    {
        "rule_number": "11",
        "code": "R11_UNIT_PRICE",
        "title": "Unit sale price",
        "description": (
            "Validate unit sale price using quantity, unit and "
            "price evidence."
        ),
        "evidence_type": "OCR_DECLARATION",
        "evidence_fields": (
            "UNIT_SALE_PRICE,NET_QUANTITY,MRP"
        ),
        "method": "UNIT_PRICE_VALIDATION",
        "severity": "HIGH",
    },

    {
        "rule_number": "12",
        "code": "R12_DIMENSIONS",
        "title": "Dimensions",
        "description": (
            "Validate dimensions where the applicable commodity "
            "requires dimension declarations."
        ),
        "evidence_type": "OCR_DECLARATION",
        "evidence_fields": (
            "DIMENSIONS"
        ),
        "method": "DIMENSION_VALIDATION",
        "severity": "MEDIUM",
    },

    {
        "rule_number": "13",
        "code": "R13_RETAIL_PRICE",
        "title": "Retail sale price",
        "description": (
            "Validate applicable maximum retail price information."
        ),
        "evidence_type": "OCR_DECLARATION",
        "evidence_fields": "MRP",
        "method": "PRICE_VALIDATION",
        "severity": "HIGH",
    },

    {
        "rule_number": "14",
        "code": "R14_DATE",
        "title": "Date information",
        "description": (
            "Validate applicable manufacture, packing, expiry, "
            "best-before or use-by information."
        ),
        "evidence_type": "OCR_DECLARATION",
        "evidence_fields": (
            "MANUFACTURE_DATE,PACK_DATE,"
            "BEST_BEFORE,USE_BY,EXPIRY_DATE"
        ),
        "method": "DATE_DECLARATION_VALIDATION",
        "severity": "HIGH",
    },

    {
        "rule_number": "15",
        "code": "R15_CUSTOMER_CARE",
        "title": "Consumer care information",
        "description": (
            "Validate required consumer care information."
        ),
        "evidence_type": "OCR_DECLARATION",
        "evidence_fields": (
            "CUSTOMER_CARE"
        ),
        "method": "CONTACT_VALIDATION",
        "severity": "MEDIUM",
    },

    {
        "rule_number": "16",
        "code": "R16_IMPORTED_PACKAGE",
        "title": "Imported package",
        "description": (
            "Apply imported-package requirements when imported "
            "status is established."
        ),
        "evidence_type": "CLASSIFICATION",
        "evidence_fields": (
            "IS_IMPORTED,COUNTRY_OF_ORIGIN,IMPORTER"
        ),
        "method": "IMPORT_VALIDATION",
        "severity": "HIGH",
    },

    {
        "rule_number": "17",
        "code": "R17_WHOLESALE_PACKAGE",
        "title": "Wholesale package",
        "description": (
            "Apply wholesale-package requirements when the "
            "package is classified as wholesale."
        ),
        "evidence_type": "CLASSIFICATION",
        "evidence_fields": (
            "PACKAGE_TYPE,NET_QUANTITY"
        ),
        "method": "PACKAGE_TYPE_VALIDATION",
        "severity": "HIGH",
    },

    {
        "rule_number": "19",
        "code": "R19_COMBINATION",
        "title": "Combination package",
        "description": (
            "Apply combination-package requirements when the "
            "package contains a qualifying combination."
        ),
        "evidence_type": "CLASSIFICATION",
        "evidence_fields": (
            "IS_COMBINATION,PACKAGE_CONTENTS"
        ),
        "method": "PACKAGE_CLASSIFICATION",
        "severity": "HIGH",
    },

    {
        "rule_number": "20",
        "code": "R20_MULTI_PIECE",
        "title": "Multi-piece package",
        "description": (
            "Apply multi-piece requirements when the package "
            "contains multiple pieces."
        ),
        "evidence_type": "CLASSIFICATION",
        "evidence_fields": (
            "IS_MULTI_PIECE,PIECE_COUNT"
        ),
        "method": "PACKAGE_CLASSIFICATION",
        "severity": "HIGH",
    },

    {
        "rule_number": "21",
        "code": "R21_GROUP_PACKAGE",
        "title": "Group package",
        "description": (
            "Apply group-package requirements when the package "
            "is classified as a group package."
        ),
        "evidence_type": "CLASSIFICATION",
        "evidence_fields": (
            "IS_GROUP_PACKAGE"
        ),
        "method": "PACKAGE_CLASSIFICATION",
        "severity": "HIGH",
    },

    {
        "rule_number": "26",
        "code": "R26_EXEMPTION",
        "title": "Exemption determination",
        "description": (
            "Determine whether an applicable exemption removes "
            "or modifies a declaration requirement."
        ),
        "evidence_type": "CLASSIFICATION",
        "evidence_fields": (
            "COMMODITY_CATEGORY,PACKAGE_TYPE,"
            "IS_IMPORTED,CONSUMER_TYPE"
        ),
        "method": "EXEMPTION_CHECK",
        "severity": "CRITICAL",
    },

    {
        "rule_number": "27",
        "code": "R27_REGISTRATION",
        "title": "Registration",
        "description": (
            "Validate applicable registration information "
            "for manufacturers, packers or importers."
        ),
        "evidence_type": "OFFICER_RECORD",
        "evidence_fields": (
            "MANUFACTURER,PACKER,IMPORTER,REGISTRATION"
        ),
        "method": "REGISTRATION_VALIDATION",
        "severity": "HIGH",
    },

    {
        "rule_number": "30",
        "code": "R30_RECORDS",
        "title": "Records",
        "description": (
            "Validate applicable records where required "
            "for an enforcement inspection."
        ),
        "evidence_type": "OFFICER_RECORD",
        "evidence_fields": (
            "INSPECTION_RECORDS"
        ),
        "method": "RECORD_VALIDATION",
        "severity": "MEDIUM",
    },

    {
        "rule_number": "33",
        "code": "R33_SPECIAL_RELAXATION",
        "title": "Special relaxation",
        "description": (
            "Determine whether a specified relaxation or special "
            "condition is applicable."
        ),
        "evidence_type": "CLASSIFICATION",
        "evidence_fields": (
            "COMMODITY_CATEGORY,SPECIAL_STATUS"
        ),
        "method": "SPECIAL_CONDITION_CHECK",
        "severity": "HIGH",
    },
]


# ============================================================
# VERSION HELPERS
# ============================================================

def get_version(db, version_code):
    return (
        db.query(RuleVersion)
        .filter(
            RuleVersion.version_code
            == version_code
        )
        .first()
    )


# ============================================================
# RULE UPSERT
# ============================================================

def get_or_create_rule(
    db,
    version,
    data,
):
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
        requirement_summary=data["summary"],
        legal_text=None,
        inspection_type=data.get(
            "inspection_type"
        ),
        commodity_category=None,
        applicability_condition=data.get(
            "applicability"
        ),
        evidence_required=None,
        evaluation_method=data.get(
            "evaluation_method"
        ),
        severity=data.get(
            "severity"
        ),
        is_active=True,
        source_reference=version.source_reference,
    )

    db.add(rule)
    db.flush()

    return rule


# ============================================================
# REQUIREMENT UPSERT
# ============================================================

def get_or_create_requirement(
    db,
    rule,
    data,
):
    requirement = (
        db.query(RuleRequirement)
        .filter(
            RuleRequirement.compliance_rule_id
            == rule.id,

            RuleRequirement.requirement_code
            == data["code"],
        )
        .first()
    )

    if requirement:
        return requirement

    requirement = RuleRequirement(
        compliance_rule_id=rule.id,
        requirement_code=data["code"],
        requirement_title=data["title"],
        requirement_description=data["description"],
        evidence_type=data.get(
            "evidence_type"
        ),
        evidence_fields=data.get(
            "evidence_fields"
        ),
        evaluation_method=data.get(
            "method"
        ),
        violation_condition=(
            "Reliable evidence demonstrates "
            "that the applicable requirement "
            "is not satisfied."
        ),
        inconclusive_condition=(
            "Required evidence is unavailable, "
            "insufficient or unreliable."
        ),
        severity=data.get(
            "severity"
        ),
        is_mandatory=True,
        is_active=True,
        source_reference=(
            rule.source_reference
        ),
    )

    db.add(requirement)
    db.flush()

    return requirement


# ============================================================
# MAIN
# ============================================================

def seed_full_rule_repository():

    db = SessionLocal()

    try:

        print(
            "\n=========================================="
        )
        print(
            "FULL PCR RULE REPOSITORY EXPANSION"
        )
        print(
            "=========================================="
        )

        # ----------------------------------------------------
        # IMPORTANT
        # ----------------------------------------------------
        #
        # At this stage we attach the structural rule catalogue
        # to the base PCR version.
        #
        # Amendment-specific overrides remain versioned and
        # should NOT be copied blindly into every amendment.
        #
        # ----------------------------------------------------

        base_version = get_version(
            db,
            "PCR_2011_BASE",
        )

        if not base_version:

            raise RuntimeError(
                "PCR_2011_BASE was not found. "
                "Run rules_seed.py first."
            )

        rule_count = 0
        requirement_count = 0

        # ----------------------------------------------------
        # CREATE RULES
        # ----------------------------------------------------

        for rule_data in RULES:

            rule = get_or_create_rule(
                db,
                base_version,
                rule_data,
            )

            rule_count += 1

        # ----------------------------------------------------
        # CREATE REQUIREMENTS
        # ----------------------------------------------------

        for requirement_data in REQUIREMENTS:

            rule = (
                db.query(ComplianceRule)
                .filter(
                    ComplianceRule.rule_version_id
                    == base_version.id,

                    ComplianceRule.rule_number
                    == requirement_data[
                        "rule_number"
                    ],
                )
                .first()
            )

            if not rule:
                continue

            requirement = (
                get_or_create_requirement(
                    db,
                    rule,
                    requirement_data,
                )
            )

            requirement_count += 1

        db.commit()

        total_rules = (
            db.query(ComplianceRule)
            .count()
        )

        total_requirements = (
            db.query(RuleRequirement)
            .count()
        )

        print(
            "\nSeed completed successfully."
        )

        print(
            f"Rules processed       : {rule_count}"
        )

        print(
            f"Requirements processed: {requirement_count}"
        )

        print(
            f"Total rules in DB     : {total_rules}"
        )

        print(
            f"Total requirements    : {total_requirements}"
        )

        print(
            "\n=========================================="
        )

    except Exception as exc:

        db.rollback()

        print(
            "\nFULL RULE REPOSITORY SEED FAILED"
        )

        print(
            f"Error: {exc}"
        )

        raise

    finally:

        db.close()


if __name__ == "__main__":
    seed_full_rule_repository()