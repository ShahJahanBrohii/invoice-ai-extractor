# Invoice AI Extractor

An AI-powered invoice processing system that extracts structured information
from PDF invoices using OCR (EasyOCR) and Google's Gemini LLM, validates the
extracted data with Pydantic, and exposes the functionality through a FastAPI
REST API.

## How it works

```
PDF Invoice
     │
     ▼
Convert PDF → Images        (app/pdf_utils.py)
     │
     ▼
OCR (EasyOCR)                (app/ocr.py)
     │
     ▼
Structured Extraction (Gemini)   (app/extractor.py)
     │
     ▼
Validation (Pydantic)        (app/schemas.py)
     │
     ▼
JSON Output
```

1. **PDF → Images** — each page of the invoice PDF is rendered to a PNG.
2. **OCR** — EasyOCR extracts raw text from each page image.
3. **LLM Extraction** — the combined OCR text is sent to Gemini
   (`gemini-2.5-flash`) with a structured-output prompt.
4. **Validation** — Gemini's JSON response is parsed and validated against a
   Pydantic schema (`InvoiceSchema`), normalizing currency-formatted numbers
   (e.g. `"SR 7,260.00"` → `7260.0`) along the way.
5. **Output** — the validated result is saved as JSON and returned to the
   caller.

## Project structure

```
INVOICE-AI-EXTRACTOR/
│
├── app/
│   ├── __init__.py
│   ├── config.py        # Loads environment variables (e.g. GEMINI_API_KEY)
│   ├── extractor.py      # Gemini-based structured extraction
│   ├── logger.py         # Logging setup (console + file, UTF-8 safe)
│   ├── main.py           # FastAPI application
│   ├── ocr.py             # EasyOCR text extraction
│   ├── parser.py         # End-to-end orchestration pipeline
│   ├── pdf_utils.py      # PDF → image conversion
│   └── schemas.py         # Pydantic models for invoice data
│
├── data/
│   ├── images/            # Generated page images (gitignored)
│   ├── input/              # Source PDF invoices
│   └── output/             # Extracted JSON + OCR debug text (gitignored)
│
├── logs/                   # Application logs (gitignored)
├── run.py                  # CLI entry point for local testing
├── requirements.txt
├── .env.example
└── .gitignore
```

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <your-repo-url>
cd invoice-ai-extractor
python -m venv .venv
```

Activate it:

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `easyocr` and `torch` are large downloads (~1–2 GB total). The
> first run will also download EasyOCR's detection/recognition models.

### 3. Configure environment variables

```bash
cp .env.example .env
```

Then edit `.env` and add your Gemini API key (get one at
[aistudio.google.com/apikey](https://aistudio.google.com/apikey)):

```
GEMINI_API_KEY=your_actual_key_here
```

### 4. Run the CLI pipeline

Place a PDF invoice in `data/input/`, then:

```bash
python run.py
```

This runs the full pipeline (PDF → images → OCR → Gemini → validation → JSON)
and writes the result to `data/output/result.json`.

### 5. Run the API server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`, with interactive docs
at `http://127.0.0.1:8000/docs`.

## API Reference

### `GET /`

Health check.

**Response**
```json
{
    "message": "Invoice AI Extractor API is running."
}
```

### `POST /extract`

Upload an invoice PDF and receive structured, validated JSON in return.

**Request:** `multipart/form-data` with a single field `file` (must be a
`.pdf`).

```bash
curl -X POST "http://127.0.0.1:8000/extract" \
  -F "file=@data/input/invoice.pdf"
```

**Response:** `200 OK`
```json
{
    "invoice_number": "ANC/25-26/03/087",
    "invoice_date": "31 March 2026",
    "supplier_name": "AFAQ ALNAMA CO.",
    "customer_name": "BRC Industrial Saudia Co.",
    "vat_number": "300188758500003",
    "subtotal": 7260.0,
    "vat": 1089.0,
    "grand_total": 8349.0,
    "currency": "SR",
    "items": [
        {
            "description": "Shipment Jeddah - Al Henakiyah",
            "quantity": 1.0,
            "unit_price": 1815.0,
            "total": 1815.0
        }
    ]
}
```

**Error responses:**
- `400 Bad Request` — uploaded file is not a `.pdf`
- `500 Internal Server Error` — OCR, Gemini extraction, or validation failure

> **Note:** each request currently overwrites `data/output/result.json` and
> reuses a single `data/images/` folder, since the pipeline was originally
> designed for one-invoice-at-a-time CLI use. For concurrent multi-user API
> traffic, consider namespacing these paths per-request (e.g. by a generated
> request ID) to avoid race conditions.

## Known limitations

- **OCR accuracy on bilingual documents**: invoices with mixed Arabic/English
  text can produce misread characters (e.g. Arabic-Indic digits substituted
  for Latin digits, or similar-looking Latin letters swapped). Gemini
  currently preserves the OCR text as-is rather than cross-referencing
  duplicate Arabic/English fields, so occasional field-level noise is
  possible on lower-quality scans.
- **CPU-only OCR** is significantly slower than GPU-accelerated OCR
  (~2–4 minutes per page observed locally). A CUDA-enabled environment is
  recommended for production use.

## Tech stack

- **FastAPI** — REST API layer
- **EasyOCR** — OCR text extraction
- **Google Gemini** (`gemini-2.5-flash`) — structured data extraction
- **Pydantic** — schema validation
- **PyMuPDF (fitz)** — PDF-to-image conversion
