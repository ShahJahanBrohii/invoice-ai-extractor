import fitz
from pathlib import Path


def pdf_to_images(pdf_path: str, output_folder: str):
    # Convert every page of a PDF into high-resolution PNG images.


    pdf = fitz.open(pdf_path)

    output_dir = Path(output_folder)
    output_dir.mkdir(parents=True, exist_ok=True)

    image_paths = []

    for page_number in range(len(pdf)):

        page = pdf.load_page(page_number)

        # Increase resolution for better OCR
        matrix = fitz.Matrix(2, 2)

        pix = page.get_pixmap(matrix=matrix)

        image_path = output_dir / f"page_{page_number + 1}.png"

        pix.save(image_path)

        image_paths.append(str(image_path))

    pdf.close()

    return image_paths