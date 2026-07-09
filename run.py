from app.parser import InvoiceParser
from app.logger import logger


def main():
    logger.info("=" * 60)
    logger.info("Invoice AI Extractor Started")
    logger.info("=" * 60)

    parser = InvoiceParser()

    invoice = parser.parse_invoice(
        pdf_path="data/input/invoice.pdf",
        image_output_folder="data/images",
        json_output_path="data/output/result.json",
    )

    logger.info("=" * 60)
    logger.info("FINAL OUTPUT")
    logger.info("=" * 60)

    print(invoice.model_dump_json(indent=4))


if __name__ == "__main__":
    main()