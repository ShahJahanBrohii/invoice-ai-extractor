from pathlib import Path
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException

from app.parser import InvoiceParser

app = FastAPI(
    title="Invoice AI Extractor",
    description="AI-powered Invoice Extraction API",
    version="1.0.0"
)

parser = InvoiceParser()


@app.get("/")
def root():
    return {
        "message": "Invoice AI Extractor API is running."
    }


@app.post("/extract")
async def extract_invoice(
    file: UploadFile = File(...)
):
    """
    Upload an invoice PDF and receive structured JSON.
    """

    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    input_folder = Path("data/input")
    input_folder.mkdir(parents=True, exist_ok=True)

    pdf_path = input_folder / file.filename

    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    invoice = parser.parse_invoice(
        pdf_path=str(pdf_path),
        image_output_folder="data/images",
        json_output_path="data/output/result.json"
    )

    return invoice.model_dump()