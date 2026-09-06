import re
from typing import List, Dict, Any


# =========================================================
# COMMODITY KEYWORDS
# =========================================================

COMMODITY_KEYWORDS = {
    "PACKAGED_FOOD": [
        "salt",
        "iodized salt",
        "crystal salt",
        "sugar",
        "rice",
        "wheat",
        "flour",
        "atta",
        "dal",
        "pulse",
        "spice",
        "masala",
        "biscuit",
        "cookie",
        "snack",
        "noodles",
        "pasta",
        "food",
        "edible",
        "tea",
        "coffee",
        "millet",
        "cereal",
    ],

    "BEVERAGE": [
        "juice",
        "drink",
        "beverage",
        "water",
        "soft drink",
        "carbonated",
        "soda",
        "energy drink",
        "fruit drink",
    ],

    "PERSONAL_CARE": [
        "shampoo",
        "conditioner",
        "soap",
        "face wash",
        "body wash",
        "toothpaste",
        "cream",
        "lotion",
        "moisturizer",
        "cosmetic",
    ],

    "HOUSEHOLD_CLEANING": [
        "detergent",
        "washing powder",
        "dishwash",
        "dish wash",
        "cleaner",
        "floor cleaner",
        "toilet cleaner",
        "liquid cleaner",
    ],

    "STATIONERY": [
        "notebook",
        "pen",
        "pencil",
        "marker",
        "eraser",
        "stationery",
    ],
}


# =========================================================
# PACKAGE INDICATORS
# =========================================================

RETAIL_PACKAGE_INDICATORS = [
    "net quantity",
    "net qty",
    "net quant",
    "net wt",
    "net weight",
    "mrp",
    "maximum retail price",
    "manufactured by",
    "manufactured & marketed by",
    "packed by",
    "packed & marketed by",
    "customer care",
    "consumer care",
    "country of origin",
    "made in",
]


MULTI_PIECE_INDICATORS = [
    "pieces",
    "piece",
    "pcs",
    "pack of",
    "units",
    "count",
]


COMBINATION_INDICATORS = [
    "combo",
    "combination",
    "kit",
    "assorted",
]


GROUP_PACKAGE_INDICATORS = [
    "group pack",
    "multipack",
    "multi pack",
    "bundle",
]


IMPORTED_INDICATORS = [
    "imported by",
    "importer",
    "country of origin",
    "made in",
]


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def collect_text(
    ocr_results: List[Dict[str, Any]]
) -> str:

    texts = []

    for item in ocr_results:
        text = item.get("text")

        if text:
            texts.append(
                normalize_text(text)
            )

    return " ".join(texts)


def keyword_matches(
    text: str,
    keywords: List[str]
) -> List[str]:

    matches = []

    for keyword in keywords:

        normalized_keyword = normalize_text(
            keyword
        )

        if normalized_keyword in text:
            matches.append(keyword)

    return matches


# =========================================================
# COMMODITY CLASSIFICATION
# =========================================================

def classify_commodity(text: str):

    best_category = None
    best_matches = []

    for category, keywords in COMMODITY_KEYWORDS.items():

        matches = keyword_matches(
            text,
            keywords
        )

        if len(matches) > len(best_matches):

            best_category = category
            best_matches = matches

    if not best_category:

        return (
            None,
            0.0,
            []
        )

    if len(best_matches) >= 3:

        confidence = 0.95

    elif len(best_matches) == 2:

        confidence = 0.88

    else:

        confidence = 0.75

    return (
        best_category,
        confidence,
        best_matches
    )


# =========================================================
# PACKAGE CLASSIFICATION
# =========================================================

def classify_package(
    text: str,
    declaration_fields: List[str]
):

    indicator_matches = keyword_matches(
        text,
        RETAIL_PACKAGE_INDICATORS
    )

    declaration_matches = []

    for field in declaration_fields:

        if field in {
            "NET_QUANTITY",
            "MRP",
            "MANUFACTURER",
            "PACKER",
            "IMPORTER",
            "COUNTRY_OF_ORIGIN",
            "CUSTOMER_CARE",
        }:

            declaration_matches.append(field)

    evidence_count = len(
        set(
            indicator_matches
            + declaration_matches
        )
    )

    if evidence_count >= 3:

        return (
            "RETAIL_PACKAGE",
            0.95,
            indicator_matches,
            declaration_matches,
        )

    if evidence_count >= 1:

        return (
            "RETAIL_PACKAGE",
            0.75,
            indicator_matches,
            declaration_matches,
        )

    return (
        None,
        0.0,
        [],
        [],
    )


# =========================================================
# SPECIAL PACKAGE FLAGS
# =========================================================

def detect_special_package_flags(
    text: str
):

    multi_matches = keyword_matches(
        text,
        MULTI_PIECE_INDICATORS
    )

    combination_matches = keyword_matches(
        text,
        COMBINATION_INDICATORS
    )

    group_matches = keyword_matches(
        text,
        GROUP_PACKAGE_INDICATORS
    )

    imported_matches = keyword_matches(
        text,
        IMPORTED_INDICATORS
    )

    return {

        "is_multi_piece":
            len(multi_matches) > 0,

        "is_combination":
            len(combination_matches) > 0,

        "is_group_package":
            len(group_matches) > 0,

        "is_imported":
            len(imported_matches) > 0,

        "multi_piece_evidence":
            multi_matches,

        "combination_evidence":
            combination_matches,

        "group_evidence":
            group_matches,

        "imported_evidence":
            imported_matches,
    }


# =========================================================
# MAIN PRODUCT CLASSIFIER
# =========================================================

def classify_product(
    ocr_results: List[Dict[str, Any]],
    declarations: List[Dict[str, Any]],
):

    # -----------------------------------------------------
    # Combine OCR text
    # -----------------------------------------------------

    text = collect_text(
        ocr_results
    )

    # -----------------------------------------------------
    # Extract declaration field names
    # -----------------------------------------------------

    declaration_fields = [

        item.get("field_name")

        for item in declarations

        if item.get("field_name")
    ]

    # -----------------------------------------------------
    # Commodity
    # -----------------------------------------------------

    (
        commodity_category,
        commodity_confidence,
        commodity_matches,
    ) = classify_commodity(text)

    # -----------------------------------------------------
    # Package
    # -----------------------------------------------------

    (
        package_type,
        package_confidence,
        package_indicator_matches,
        package_declaration_matches,
    ) = classify_package(
        text,
        declaration_fields
    )

    # -----------------------------------------------------
    # Special package flags
    # -----------------------------------------------------

    special_flags = detect_special_package_flags(
        text
    )

    # -----------------------------------------------------
    # Overall confidence
    # -----------------------------------------------------

    confidence_parts = []

    if commodity_confidence > 0:

        confidence_parts.append(
            commodity_confidence
        )

    if package_confidence > 0:

        confidence_parts.append(
            package_confidence
        )

    if confidence_parts:

        confidence = (
            sum(confidence_parts)
            / len(confidence_parts)
        )

    else:

        confidence = 0.0

    # -----------------------------------------------------
    # Classification status
    # -----------------------------------------------------

    if (
        commodity_category
        and package_type
    ):

        status = "CLASSIFIED"

    elif (
        commodity_category
        or package_type
    ):

        status = "UNCERTAIN"

    else:

        status = "INCONCLUSIVE"

    # -----------------------------------------------------
    # Evidence
    # -----------------------------------------------------

    evidence = {

        "ocr_text": text,

        "commodity_matches":
            commodity_matches,

        "package_indicator_matches":
            package_indicator_matches,

        "package_declaration_matches":
            package_declaration_matches,

        "special_package_evidence":
            special_flags,
    }

    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    return {

        "commodity_category":
            commodity_category,

        "package_type":
            package_type,

        "is_imported":
            special_flags["is_imported"],

        "is_multi_piece":
            special_flags["is_multi_piece"],

        "is_combination":
            special_flags["is_combination"],

        "is_group_package":
            special_flags["is_group_package"],

        "confidence":
            round(confidence, 4),

        "status":
            status,

        "evidence":
            evidence,
    }