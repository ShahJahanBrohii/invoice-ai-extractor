import json
from pathlib import Path
from app.pdf_utils import pdf_to_images
from app.ocr import OCRProcessor
from app.extractor import InvoiceExtractor
from app.logger import logger


class InvoiceParser:
    """
    Main pipeline for invoice processing.

    Pipeline:
    PDF
        ↓
    Convert PDF → Images
        ↓
    OCR
        ↓
    Gemini Extraction
        ↓
    Pydantic Validation
        ↓
    Save JSON
    """

    def __init__(self):
        logger.info("Initializing Invoice Parser...")

        self.ocr = OCRProcessor()
        self.extractor = InvoiceExtractor()

        logger.info("Invoice Parser initialized successfully.")

    def parse_invoice(
        self,
        pdf_path: str,
        image_output_folder: str,
        json_output_path: str,
    ):
        

        try:

            # --------------------------------------------------
            # STEP 1 : PDF -> Images
            # --------------------------------------------------
            logger.info("STEP 1/5 - Converting PDF into images...")

            image_paths = pdf_to_images(
                pdf_path=pdf_path,
                output_folder=image_output_folder
            )

            logger.info(f"{len(image_paths)} page(s) generated successfully.")

            # --------------------------------------------------
            # STEP 2 : OCR
            # --------------------------------------------------
            logger.info("STEP 2/5 - Starting OCR...")

            full_text = ""

            for index, image in enumerate(image_paths, start=1):

                logger.info(
                    f"Processing page {index}/{len(image_paths)} : {image}"
                )

                text = self.ocr.extract_text(image)

                full_text += text
                full_text += "\n\n"

            logger.info("OCR completed successfully.")

            # Save OCR text for debugging
            ocr_output = Path("data/output/ocr_text.txt")
            ocr_output.parent.mkdir(parents=True, exist_ok=True)

            with open(ocr_output, "w", encoding="utf-8") as f:
                f.write(full_text)

            logger.info(f"OCR text saved to {ocr_output}")

            # --------------------------------------------------
            # STEP 3 : Gemini Extraction
            # --------------------------------------------------
            logger.info("STEP 3/5 - Extracting structured data using Gemini...")

            invoice = self.extractor.extract(full_text)

            logger.info("Invoice information extracted successfully.")

            # --------------------------------------------------
            # STEP 4 : Save JSON
            # --------------------------------------------------
            logger.info("STEP 4/5 - Saving JSON output...")

            output_path = Path(json_output_path)

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            with open(output_path, "w", encoding="utf-8") as f:

                json.dump(
                    invoice.model_dump(),
                    f,
                    indent=4,
                    ensure_ascii=False
                )

            logger.info(f"JSON saved successfully at {output_path}")

            # --------------------------------------------------
            # STEP 5 : Completed
            # --------------------------------------------------
            logger.info("STEP 5/5 - Invoice processing completed successfully.")

            return invoice

        except Exception as e:

            logger.exception("Invoice processing failed.")

            raise RuntimeError(
                f"Invoice parsing failed: {e}"
            )