import time
import easyocr

from app.logger import logger


class OCRProcessor:
    """
    OCR Processor using EasyOCR.

    Supports:
    - English
    - Arabic

    Returns extracted text from invoice images.
    """

    def __init__(self):
        try:
            logger.info("Loading EasyOCR model...")

            self.reader = easyocr.Reader(
                ['en', 'ar'],
                gpu=False
            )

            logger.info("EasyOCR model loaded successfully.")

        except Exception as e:
            logger.exception("Failed to initialize EasyOCR.")
            raise RuntimeError(f"EasyOCR initialization failed: {e}")

    def extract_text(self, image_path: str) -> str:
        """
        Extract text from an image.

        Args:
            image_path (str): Path to the image.

        Returns:
            str: Extracted text.
        """

        try:
            logger.info(f"Starting OCR for: {image_path}")

            start_time = time.time()

            results = self.reader.readtext(
                image_path,
                detail=1,
                paragraph=False
            )

            elapsed = time.time() - start_time

            logger.info(
                f"OCR completed for {image_path} in {elapsed:.2f} seconds."
            )

            extracted_lines = []

            for result in results:
                extracted_lines.append(result[1])

            extracted_text = "\n".join(extracted_lines)

            logger.info(
                f"Extracted {len(extracted_lines)} text lines from {image_path}"
            )

            return extracted_text

        except Exception as e:
            logger.exception(f"OCR failed for {image_path}")
            raise RuntimeError(f"OCR failed: {e}")