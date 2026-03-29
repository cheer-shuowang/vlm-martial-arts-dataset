# A naive script to split a PDF, assuming the pages are symmetric.

# pip install pymupdf pillow
import fitz
from pathlib import Path
from PIL import Image

def pdf_to_split_pages(pdf_path, output_dir, dpi=300):
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(pdf_path))
    total = len(doc)
    stem = pdf_path.stem
    counter = 1  # global image counter

    for page_num, page in enumerate(doc, start=1):
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        mid_x = img.width // 2
        left  = img.crop((0,     0, mid_x,     img.height))
        right = img.crop((mid_x, 0, img.width, img.height))

        left.save(output_dir  / f"{stem}_{counter}.jpg", quality=95)
        counter += 1
        right.save(output_dir / f"{stem}_{counter}.jpg", quality=95)
        counter += 1

        if page_num % 50 == 0:
            print(f"⏳ {page_num}/{total} pages done...")

    doc.close()
    print(f"\nDone! {total} pages → {counter - 1} images")
    print(f"Saved to: {output_dir}")


if __name__ == "__main__":
    pdf_to_split_pages(
        pdf_path   = "../tbbb_part1.pdf",
        output_dir = "../split",
        dpi = 300
    )