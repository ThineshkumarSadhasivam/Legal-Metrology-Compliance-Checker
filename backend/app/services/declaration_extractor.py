import re
from typing import Optional


# =========================================================
# DECLARATION LABEL PATTERNS
# =========================================================

PATTERNS = {
    "NET_QUANTITY": [
        r"\bnet\.?\s*(quantity|quant|qty)\b",
        r"\bnet\s*(wt|weight)\b",
        r"\bnetweight\b",
    ],

    "MRP": [
        r"\bm\.?\s*r\.?\s*p\.?\b",
        r"\bmaximum\s*retail\s*price\b",
        r"\bretail\s*price\b",
    ],

    "MANUFACTURER": [
        r"\bmanufactured\s+by\b",
        r"\bmanufactured\s*&\s*marketed\s+by\b",
        r"\bmanufacturer\b",
    ],

    "PACKER": [
        r"\bpacked\s+by\b",
        r"\bpacker\b",
        r"\bpacked\s*&\s*marketed\s+by\b",
    ],

    "IMPORTER": [
        r"\bimported\s+by\b",
        r"\bimporter\b",
    ],

    "COUNTRY_OF_ORIGIN": [
        r"\bcountry\s+of\s+origin\b",
        r"\bmade\s+in\b",
        r"\bproduct\s+of\b",
        r"\bcountry\s+of\s+origin\s*:\b",
    ],

    "UNIT_SALE_PRICE": [
        r"\bunit\s+sale\s+price\b",
        r"\bsale\s+price\s+per\b",
        r"\bprice\s+per\b",
    ],

    "CUSTOMER_CARE": [
        r"\bcustomer\s+care\b",
        r"\bconsumer\s+care\b",
        r"\bcustomer\s+service\b",
        r"\bconsumer\s+complaint\b",
    ],
}


# =========================================================
# GENERAL UTILITIES
# =========================================================

def normalize_text(text: str) -> str:
    """
    Basic OCR text normalization.

    The original OCR text is never modified in the database.
    This normalization is only used for extraction.
    """

    if not text:
        return ""

    text = text.strip()
    text = re.sub(r"\s+", " ", text)

    return text


def detect_field(text: str) -> Optional[str]:
    """
    Determine whether an OCR region contains a declaration label.
    """

    text_lower = normalize_text(text).lower()

    if not text_lower:
        return None

    for field_name, patterns in PATTERNS.items():

        for pattern in patterns:

            if re.search(pattern, text_lower):
                return field_name

    return None


# =========================================================
# QUANTITY NORMALIZATION
# =========================================================

def normalize_quantity(text: str) -> Optional[str]:
    """
    Normalize common quantity formats.

    Examples:
        1kg      -> 1 kg
        500g     -> 500 g
        250 ml   -> 250 ml
        1L       -> 1 L
    """

    if not text:
        return None

    text = normalize_text(text)

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*"
        r"(kg|kgs|g|gm|mg|ml|l|litre|liter|litres|liters)\b",
        text,
        re.IGNORECASE
    )

    if not match:
        return None

    value = match.group(1)
    unit = match.group(2).lower()

    unit_map = {
        "kg": "kg",
        "kgs": "kg",
        "g": "g",
        "gm": "g",
        "mg": "mg",
        "ml": "ml",
        "l": "L",
        "litre": "L",
        "liter": "L",
        "litres": "L",
        "liters": "L",
    }

    return f"{value} {unit_map[unit]}"


# =========================================================
# PRICE NORMALIZATION
# =========================================================

def normalize_price(text: str) -> Optional[str]:
    """
    Normalize common price formats.

    Examples:
        ₹120       -> ₹120
        Rs. 120    -> ₹120
        INR 120    -> ₹120
        120        -> ₹120
    """

    if not text:
        return None

    text = normalize_text(text)

    match = re.search(
        r"(?:₹|rs\.?|inr)?\s*"
        r"(\d+(?:\.\d{1,2})?)",
        text,
        re.IGNORECASE
    )

    if not match:
        return None

    return f"₹{match.group(1)}"


# =========================================================
# TEXT CLEANING
# =========================================================

def clean_extracted_value(text: str) -> str:
    """
    Clean an extracted declaration value without attempting
    to invent missing information.
    """

    text = normalize_text(text)

    # Remove common separators at beginning/end
    text = re.sub(r"^[\s:;,\-]+", "", text)
    text = re.sub(r"[\s:;,\-]+$", "", text)

    return text.strip()


# =========================================================
# DUPLICATE DETECTION
# =========================================================

def is_duplicate(
    declarations,
    field_name: str,
    normalized_value: str
) -> bool:

    for declaration in declarations:

        if declaration["field_name"] != field_name:
            continue

        existing_value = declaration.get(
            "normalized_value"
        )

        if (
            existing_value
            and normalized_value
            and existing_value.lower() == normalized_value.lower()
        ):
            return True

    return False


# =========================================================
# VALUE EXTRACTION
# =========================================================

def find_nearby_value(
    results,
    current_index,
    field_name
):
    """
    Search nearby OCR regions for the value associated
    with a declaration label.

    We intentionally keep this conservative.

    Example:

        NET. QUANT
        1kg

    becomes:

        NET_QUANTITY -> 1 kg
    """

    current = results[current_index]

    current_bbox = current.get("bbox")

    candidates = []

    # Only inspect the next few OCR regions.
    # This avoids accidentally associating unrelated
    # declarations with each other.
    for offset in range(1, 4):

        next_index = current_index + offset

        if next_index >= len(results):
            break

        candidate = results[next_index]

        candidate_text = candidate["text"]

        # Another declaration label means this candidate
        # should not be used as the current field's value.
        if detect_field(candidate_text):
            continue

        # -------------------------------------------------
        # Field-specific validation
        # -------------------------------------------------

        if field_name == "NET_QUANTITY":

            normalized = normalize_quantity(candidate_text)

            if normalized:
                candidates.append(
                    (
                        candidate,
                        normalized
                    )
                )

        elif field_name in {
            "MRP",
            "UNIT_SALE_PRICE"
        }:

            normalized = normalize_price(candidate_text)

            if normalized:
                candidates.append(
                    (
                        candidate,
                        normalized
                    )
                )

        else:

            cleaned = clean_extracted_value(
                candidate_text
            )

            if cleaned:
                candidates.append(
                    (
                        candidate,
                        cleaned
                    )
                )

    if not candidates:
        return None

    # Return closest valid candidate
    return candidates[0]


# =========================================================
# MAIN EXTRACTION FUNCTION
# =========================================================

def extract_declarations(ocr_results):
    """
    Extract structured Legal Metrology declarations
    from OCR evidence.

    Input:
        OCR result dictionaries.

    Output:
        Declaration dictionaries.

    Important:
        This function DOES NOT decide compliance.

        It only extracts declarations from evidence.
    """

    declarations = []

    # -----------------------------------------------------
    # Prepare OCR results
    # -----------------------------------------------------

    results = []

    for result in ocr_results:

        text = normalize_text(
            result.get("text", "")
        )

        if not text:
            continue

        results.append({
            "id": result["id"],
            "text": text,
            "confidence": float(
                result.get("confidence", 0)
            ),
            "bbox": result.get("bbox")
        })

    # -----------------------------------------------------
    # Process every OCR region
    # -----------------------------------------------------

    for index, result in enumerate(results):

        field_name = detect_field(
            result["text"]
        )

        if not field_name:
            continue

        # -------------------------------------------------
        # Find the corresponding value
        # -------------------------------------------------

        nearby = find_nearby_value(
            results,
            index,
            field_name
        )

        # -------------------------------------------------
        # Value not confidently found
        # -------------------------------------------------

        if nearby is None:

            declarations.append({
                "field_name": field_name,
                "value": "",
                "normalized_value": "",
                "confidence": result["confidence"],
                "source_ocr_ids": [
                    result["id"]
                ],
                "status": "UNCERTAIN"
            })

            continue

        value_result, normalized_value = nearby

        value = clean_extracted_value(
            value_result["text"]
        )

        confidence = min(
            result["confidence"],
            value_result["confidence"]
        )

        # -------------------------------------------------
        # Prevent duplicate declarations
        # -------------------------------------------------

        if is_duplicate(
            declarations,
            field_name,
            normalized_value
        ):
            continue

        # -------------------------------------------------
        # Store declaration
        # -------------------------------------------------

        declarations.append({
            "field_name": field_name,
            "value": value,
            "normalized_value": normalized_value,
            "confidence": confidence,
            "source_ocr_ids": [
                result["id"],
                value_result["id"]
            ],
            "status": (
                "DETECTED"
                if confidence >= 0.80
                else "UNCERTAIN"
            )
        })

    return declarations