import json
import google.generativeai as genai

from app.config import GEMINI_API_KEY
from app.schemas import InvoiceSchema
from app.logger import logger


class InvoiceExtractor:
    """
    Uses Google's Gemini model to extract structured invoice
    information from OCR text.
    """

    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)

        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash"
        )

    def extract(self, ocr_text: str) -> InvoiceSchema:
        """
        Extract structured invoice data.

        Args:
            ocr_text (str): Raw OCR text.

        Returns:
            InvoiceSchema: Validated invoice data.
        """

        prompt = f"""
You are an expert AI Invoice Extraction System.

Your task is to extract invoice information from OCR text.

Rules:

1. Return ONLY valid JSON.
2. Do NOT include markdown.
3. Do NOT explain anything.
4. If a value is missing, use null.
5. Preserve dates exactly as written.
6. Preserve currency exactly as written.
7. Extract all invoice items.

Required JSON format:

{{
    "invoice_number": "",
    "invoice_date": "",
    "supplier_name": "",
    "customer_name": "",
    "vat_number": "",
    "subtotal": "",
    "vat": "",
    "grand_total": "",
    "currency": "",
    "items": [
        {{
            "description": "",
            "quantity": "",
            "unit_price": "",
            "total": ""
        }}
    ]
}}

OCR TEXT:

{ocr_text}
"""

        response = self.model.generate_content(prompt)

        output = response.text.strip()

        # Remove Markdown JSON fences if the model adds them
        if output.startswith("```json"):
            output = output.replace("```json", "").replace("```", "").strip()
        elif output.startswith("```"):
            output = output.replace("```", "").strip()

        # Parse and validate — runs in ALL cases now, not just the elif branch
        try:
            data = json.loads(output)

        except json.JSONDecodeError as e:
            logger.error(f"Gemini returned invalid JSON: {output}")
            raise ValueError(
                f"Failed to parse Gemini response as JSON: {e}"
            )

        try:
            validated_invoice = InvoiceSchema(**data)

        except Exception as e:
            logger.error(f"Invoice validation failed. Raw data: {data}")
            raise ValueError(
                f"Failed to validate invoice data against schema: {e}"
            )

        return validated_invoice