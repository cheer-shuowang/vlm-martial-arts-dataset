#!/usr/bin/env python3
"""
Step 2: Image Pre-processing
==============================
Convert PDF scans into individual page images.

Pipeline per PDF page:
  1. Render PDF page to image at specified DPI
  2. Auto-crop: remove color calibration card and dark background
  3. Detect single vs double-page spread (by aspect ratio)
  4. Split double pages at the center binding crease
  5. Rename sequentially as {bookID}_{pageNumber}
  6. Resize to target height (default 800px), width scaled proportionally
  7. Save as PNG

Usage:
    python step2_preprocess.py input.pdf --book-id gy_mg -o output_dir/
    python step2_preprocess.py input.pdf --book-id gy_mg --height 800 --dpi 300

Dependencies:
    pip install pymupdf Pillow numpy
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional

try:
    import fitz  # pymupdf
except ImportError:
    sys.exit("[ERROR] Missing 'pymupdf'. Run: pip install pymupdf")

try:
    from PIL import Image
except ImportError:
    sys.exit("[ERROR] Missing 'Pillow'. Run: pip install Pillow")

try:
    import numpy as np
except ImportError:
    sys.exit("[ERROR] Missing 'numpy'. Run: pip install numpy")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration defaults
# ---------------------------------------------------------------------------
DEFAULT_DPI = 300
DEFAULT_HEIGHT = 800
DOUBLE_PAGE_RATIO_THRESHOLD = 1.05  # width/height > this => double page
DARK_THRESHOLD = 40                # grayscale below this = "dark background"
CONTENT_THRESHOLD = 50             # grayscale above this = "content"
SEPARATOR_SEARCH_START = 0.65      # search for color card from this % of width


# ---------------------------------------------------------------------------
# Image processing functions
# ---------------------------------------------------------------------------
def find_color_card_boundary(img_array: np.ndarray) -> Optional[int]:
    """
    Find the x-coordinate of the dark vertical separator between
    the book content and the color calibration card on the right edge.

    Scans the middle vertical band from right to left, looking for
    consistently dark columns in the rightmost ~35% of the image.

    Returns the x-coordinate to crop at, or None if not found.
    """
    gray = np.mean(img_array, axis=2)
    h, w = gray.shape

    # Use the middle 50% of height to avoid edge artifacts
    y_start = h // 4
    y_end = 3 * h // 4
    mid_band = gray[y_start:y_end, :]
    col_avg = np.mean(mid_band, axis=0)

    search_start = int(w * SEPARATOR_SEARCH_START)
    dark_cols = np.where(col_avg[search_start:] < DARK_THRESHOLD)[0]

    if len(dark_cols) > 0:
        return dark_cols[0] + search_start

    return None


def auto_crop_content(img: Image.Image, remove_card: bool = True) -> Image.Image:
    """
    Crop out the dark background and (optionally) the color calibration card.

    Steps:
      1. If remove_card: detect and remove color card from the right
      2. Find the bounding box of non-dark content on all sides
      3. Add a small padding (2px) to preserve content edges
    """
    arr = np.array(img)

    if remove_card:
        boundary = find_color_card_boundary(arr)
        if boundary is not None:
            arr = arr[:, :boundary, :]

    gray = np.mean(arr, axis=2)
    mask = gray > CONTENT_THRESHOLD

    rows_with_content = np.any(mask, axis=1)
    cols_with_content = np.any(mask, axis=0)

    if not np.any(rows_with_content) or not np.any(cols_with_content):
        log.warning("  Could not detect content area; returning uncropped")
        return img

    row_indices = np.where(rows_with_content)[0]
    col_indices = np.where(cols_with_content)[0]

    y_min = max(0, row_indices[0] - 2)
    y_max = min(arr.shape[0], row_indices[-1] + 3)
    x_min = max(0, col_indices[0] - 2)
    x_max = min(arr.shape[1], col_indices[-1] + 3)

    return Image.fromarray(arr[y_min:y_max, x_min:x_max])


def is_double_page(img: Image.Image,
                   threshold: float = DOUBLE_PAGE_RATIO_THRESHOLD) -> bool:
    """Check if an image is a double-page spread based on aspect ratio."""
    w, h = img.size
    return (w / h) > threshold


def find_split_point(img: Image.Image) -> int:
    """
    Find the optimal x-coordinate to split a double-page spread.

    Looks for the binding crease: a narrow vertical band near the center
    with lower brightness (shadow from the spine). Falls back to the
    geometric center if no crease is detected.
    """
    arr = np.array(img)
    gray = np.mean(arr, axis=2)
    h, w = gray.shape

    # Search within the central 20% of width
    center = w // 2
    search_half = int(w * 0.1)
    x_start = center - search_half
    x_end = center + search_half

    # Use the middle 60% of height to avoid margins
    y_start = int(h * 0.2)
    y_end = int(h * 0.8)

    region = gray[y_start:y_end, x_start:x_end]
    col_avg = np.mean(region, axis=0)

    # Binding crease = darkest column in the central region
    min_col = np.argmin(col_avg)
    return x_start + min_col


def split_double_page(img: Image.Image) -> tuple[Image.Image, Image.Image]:
    """
    Split a double-page spread into two individual pages.

    For traditional Chinese thread-bound books:
    - RIGHT half = first (earlier) logical page
    - LEFT half = second (later) logical page
    Chinese books are bound on the right, read right-to-left.
    """
    split_x = find_split_point(img)
    w, h = img.size

    page_right = img.crop((split_x, 0, w, h))
    page_left = img.crop((0, 0, split_x, h))

    return page_right, page_left


def resize_to_height(img: Image.Image, target_height: int) -> Image.Image:
    """Resize image to a fixed height, maintaining aspect ratio."""
    w, h = img.size
    if h == target_height:
        return img
    ratio = target_height / h
    new_w = int(w * ratio)
    return img.resize((new_w, target_height), Image.LANCZOS)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def process_pdf(pdf_path: str, book_id: str, output_dir: str,
                dpi: int = DEFAULT_DPI,
                target_height: int = DEFAULT_HEIGHT,
                force_mode: Optional[str] = None,
                remove_card: bool = True) -> dict:
    """
    Process a single PDF file through the full Step 2 pipeline.

    Args:
        pdf_path:      path to input PDF
        book_id:       book identifier (e.g. "gy_mg")
        output_dir:    directory for output images
        dpi:           rendering DPI (default 300)
        target_height: output image height in pixels (default 800)
        force_mode:    "single" or "double" to override auto-detection
        remove_card:   whether to auto-remove color calibration cards

    Returns:
        dict with processing statistics
    """
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not pdf_path.exists():
        sys.exit(f"[ERROR] PDF not found: {pdf_path}")

    log.info("Converting PDF to images at %d DPI...", dpi)
    doc = fitz.open(str(pdf_path))
    total_pdf_pages = len(doc)
    log.info("PDF has %d pages", total_pdf_pages)

    stats = {
        "pdf_pages": total_pdf_pages,
        "single_pages": 0,
        "double_pages": 0,
        "output_images": 0,
        "errors": [],
    }

    page_counter = 1

    for pdf_idx in range(total_pdf_pages):
        pdf_page_num = pdf_idx + 1
        log.info("[Page %d/%d] Processing...", pdf_page_num, total_pdf_pages)

        try:
            # Render page to image via pymupdf
            page = doc[pdf_idx]
            zoom = dpi / 72.0  # PDF default is 72 DPI
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            raw_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            # Auto-crop
            cropped = auto_crop_content(raw_img, remove_card=remove_card)
            log.info("  Cropped: %dx%d -> %dx%d",
                     raw_img.size[0], raw_img.size[1],
                     cropped.size[0], cropped.size[1])

            # Detect single/double
            if force_mode == "single":
                double = False
            elif force_mode == "double":
                double = True
            else:
                double = is_double_page(cropped)

            if double:
                stats["double_pages"] += 1
                page_a, page_b = split_double_page(cropped)
                pages_to_save = [page_a, page_b]
                log.info("  Double-page -> split at binding crease")
            else:
                stats["single_pages"] += 1
                pages_to_save = [cropped]
                log.info("  Single page")

            # Resize and save
            for page_img in pages_to_save:
                resized = resize_to_height(page_img, target_height)
                filename = f"{book_id}_{page_counter}.png"
                out_path = output_dir / filename
                resized.save(str(out_path), "PNG")
                log.info("  -> %s (%dx%d)", filename,
                         resized.size[0], resized.size[1])
                page_counter += 1
                stats["output_images"] += 1

        except Exception as e:
            log.error("  Error on PDF page %d: %s", pdf_page_num, e)
            stats["errors"].append({"pdf_page": pdf_page_num, "error": str(e)})

    doc.close()
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Step 2: Convert PDF scans to individual page images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python step2_preprocess.py book.pdf --book-id gy_mg
  python step2_preprocess.py book.pdf --book-id gy_mg -o ./images/gy_mg/
  python step2_preprocess.py book.pdf --book-id gy_mg --height 800 --dpi 300
  python step2_preprocess.py book.pdf --book-id gy_mg --force double
  python step2_preprocess.py book.pdf --book-id gy_mg --no-card-removal

Notes on page ordering for Chinese thread-bound books:
  Double-page spreads are split with the RIGHT half as the first logical
  page, since Chinese books are bound on the right and read right-to-left.
        """
    )
    parser.add_argument("pdf_file", help="Path to input PDF file")
    parser.add_argument("--book-id", required=True,
                        help="Book identifier for filenames (e.g. gy_mg)")
    parser.add_argument("-o", "--output-dir", default=None,
                        help="Output directory (default: ./output/{book_id}/)")
    parser.add_argument("--dpi", type=int, default=DEFAULT_DPI,
                        help="Rendering DPI (default: 300)")
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT,
                        help="Target height in pixels (default: 800)")
    parser.add_argument("--force", choices=["single", "double"], default=None,
                        help="Force all pages as single or double")
    parser.add_argument("--no-card-removal", action="store_true",
                        help="Disable color calibration card removal")
    parser.add_argument("--double-page-ratio", type=float,
                        default=DOUBLE_PAGE_RATIO_THRESHOLD,
                        help="Aspect ratio threshold for double-page detection "
                             "(default: 1.05)")

    args = parser.parse_args()
    output_dir = args.output_dir or f"./output/{args.book_id}/"

    log.info("=" * 60)
    log.info("Step 2: Image Pre-processing")
    log.info("=" * 60)
    log.info("Input:  %s", args.pdf_file)
    log.info("Book ID: %s", args.book_id)
    log.info("Output: %s", output_dir)
    log.info("DPI: %d | Height: %dpx | Mode: %s | Card removal: %s",
             args.dpi, args.height,
             args.force or "auto",
             "off" if args.no_card_removal else "on")
    log.info("-" * 60)

    stats = process_pdf(
        pdf_path=args.pdf_file,
        book_id=args.book_id,
        output_dir=output_dir,
        dpi=args.dpi,
        target_height=args.height,
        force_mode=args.force,
        remove_card=not args.no_card_removal,
    )

    log.info("=" * 60)
    log.info("Done.")
    log.info("  PDF pages:     %d", stats["pdf_pages"])
    log.info("  Single pages:  %d", stats["single_pages"])
    log.info("  Double pages:  %d (-> %d images)",
             stats["double_pages"], stats["double_pages"] * 2)
    log.info("  Total output:  %d images", stats["output_images"])
    if stats["errors"]:
        log.warning("  Errors: %d", len(stats["errors"]))
    log.info("  Output dir:    %s", output_dir)
    log.info("=" * 60)


if __name__ == "__main__":
    main()
