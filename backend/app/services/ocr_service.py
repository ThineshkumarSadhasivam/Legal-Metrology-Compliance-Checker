from pathlib import Path
from paddleocr import PaddleOCR


# Initialize OCR engine once when the backend starts
ocr_engine = PaddleOCR(
    lang="en",
    device="cpu",
    enable_mkldnn=False,
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)


def run_ocr(image_path: str):
    """
    Run PaddleOCR on an image and return:
    - recognized text
    - confidence score
    - bounding polygon
    """

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    # PaddleOCR 3.x API
    results = ocr_engine.predict(str(path))

    extracted = []

    for result in results:

        # PaddleOCR result object
        result_data = result.json

        # Depending on PaddleOCR version, json may be
        # a string or dictionary.
        if isinstance(result_data, str):
            import json
            result_data = json.loads(result_data)

        # Usually the OCR data is inside "res"
        data = result_data.get("res", result_data)

        texts = data.get("rec_texts", [])
        scores = data.get("rec_scores", [])
        boxes = data.get("rec_polys", [])

        for text, score, bbox in zip(
            texts,
            scores,
            boxes
        ):

            if not text:
                continue

            extracted.append({
                "text": str(text),
                "confidence": float(score),
                "bbox": bbox.tolist()
                    if hasattr(bbox, "tolist")
                    else bbox
            })

    return extracted