from app.services.product_classification_service import classify_product


ocr_results = [
    {"text": "IODIZED"},
    {"text": "SHUBHA"},
    {"text": "SALT"},
    {"text": "IODIZED CRYSTAL SALT"},
    {"text": "NET. QUANT"},
    {"text": "1kg"},
]


declarations = [
    {
        "field_name": "NET_QUANTITY",
        "value": "1kg",
        "confidence": 0.81,
    }
]


result = classify_product(
    ocr_results,
    declarations
)


print("\nPRODUCT CLASSIFICATION")
print("======================")

print(
    "Commodity:",
    result["commodity_category"]
)

print(
    "Package:",
    result["package_type"]
)

print(
    "Imported:",
    result["is_imported"]
)

print(
    "Multi-piece:",
    result["is_multi_piece"]
)

print(
    "Combination:",
    result["is_combination"]
)

print(
    "Group package:",
    result["is_group_package"]
)

print(
    "Confidence:",
    result["confidence"]
)

print(
    "Status:",
    result["status"]
)

print(
    "\nEvidence:"
)

print(
    result["evidence"]
)