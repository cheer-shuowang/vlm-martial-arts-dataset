#!/usr/bin/env python3
"""
Simple PDF Splitter: Split double-page PDF scans into individual pages.
========================================================================
Assumes pages are symmetric double-page spreads, splits at the center.

Usage:
    python split_pdf.py ./scans/中國古佚劍法.pdf --book-id zggyjf
    python split_pdf.py ./scans/book.pdf --book-id gy_mg -o ./output/gy_mg/
    python split_pdf.py ./scans/book.pdf --book-id test --dpi 200

Dependencies:
    pip install pymupdf Pillow
"""

import argparse
import sys
from pathlib import Path

try:
    import fitz
except ImportError:
    sys.exit("[ERROR] Missing 'pymupdf'. Run: pip install pymupdf")

try:
    from PIL import Image
except ImportError:
    sys.exit("[ERROR] Missing 'Pillow'. Run: pip install Pillow")


def pdf_to_split_pages(pdf_path, output_dir, book_id, dpi=300):
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not pdf_path.exists():
        sys.exit(f"[ERROR] PDF not found: {pdf_path}")

    doc = fitz.open(str(pdf_path))
    total = len(doc)
    print(f"PDF has {total} pages, splitting at center...")
    counter = 1

    for page_num, page in enumerate(doc, start=1):
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        mid_x = img.width // 2
        left = img.crop((0, 0, mid_x, img.height))
        right = img.crop((mid_x, 0, img.width, img.height))

        left.save(output_dir / f"{book_id}_{counter}.jpg", quality=95)
        counter += 1
        right.save(output_dir / f"{book_id}_{counter}.jpg", quality=95)
        counter += 1

        if page_num % 50 == 0:
            print(f"  {page_num}/{total} pages done...")

    doc.close()
    print(f"\nDone! {total} PDF pages -> {counter - 1} images")
    print(f"Saved to: {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Split double-page PDF scans into individual page images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python split_pdf.py ./scans/book.pdf --book-id zggyjf
  python split_pdf.py ./scans/book.pdf --book-id zggyjf -o ./output/zggyjf/
  python split_pdf.py ./scans/book.pdf --book-id zggyjf --dpi 200
        """
    )
    parser.add_argument("pdf_file", help="Path to input PDF file")
    parser.add_argument("--book-id", required=True,
                        help="Book identifier for filenames (e.g. zggyjf)")
    parser.add_argument("-o", "--output-dir", default=None,
                        help="Output directory (default: ./output/{book_id}/)")
    parser.add_argument("--dpi", type=int, default=300,
                        help="Rendering DPI (default: 300)")

    args = parser.parse_args()
    output_dir = args.output_dir or f"./output/{args.book_id}/"

    print("=" * 60)
    print("PDF Splitter")
    print("=" * 60)
    print(f"Input:   {args.pdf_file}")
    print(f"Book ID: {args.book_id}")
    print(f"Output:  {output_dir}")
    print(f"DPI:     {args.dpi}")
    print("-" * 60)

    pdf_to_split_pages(args.pdf_file, output_dir, args.book_id, args.dpi)


if __name__ == "__main__":
    main()
