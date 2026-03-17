#!/usr/bin/env python3
"""
Step 3: Page-Level Indexing using VLM (Qwen-VL via DashScope)
==============================================================
For each page image from Step 2, use a Vision Language Model to classify:
  - has_image (Y/N)
  - has_text (Y/N)
  - count_of_image (integer)
  - img_layout (NA / sgl / td / lr)

Outputs a CSV file with one row per page.

Usage:
    python step3_index.py ../step2_tool/output/gy_mg/ --book-id gy_mg
    python step3_index.py ../step2_tool/output/gy_mg/ --book-id gy_mg --limit 10
    python step3_index.py ../step2_tool/output/gy_mg/ --book-id gy_mg --resume

Dependencies:
    pip install requests Pillow
"""

import argparse
import base64
import csv
import json
import logging
import os
import sys
import time
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("[ERROR] Missing 'Pillow'. Run: pip install Pillow")

try:
    import requests
except ImportError:
    sys.exit("[ERROR] Missing 'requests'. Run: pip install requests")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DASHSCOPE_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
DEFAULT_MODEL = "qwen-vl-plus"
DEFAULT_DELAY = 1.0
MAX_RETRIES = 3

CLASSIFICATION_PROMPT = """You are analyzing a scanned page from a historical Chinese martial arts text.

Look at this image carefully and answer the following questions.
Respond ONLY with a JSON object, no other text.

{
  "has_image": "Y or N -- does this page contain any illustration or drawing (not text)?",
  "has_text": "Y or N -- does this page contain any readable text (printed or handwritten)?",
  "count_of_image": "integer -- how many distinct illustrations/drawings are on this page? (0 if none)",
  "img_layout": "one of: NA, sgl, td, lr -- NA if no image; sgl if single image; td if multiple images arranged top-to-bottom; lr if multiple images arranged left-to-right"
}

Important rules:
- Decorative borders, seals, stamps, and page numbers do NOT count as illustrations.
- Only count actual drawings/illustrations depicting people, weapons, objects, or diagrams.
- A blank or nearly blank page should have has_image=N, has_text=N, count_of_image=0, img_layout=NA.
- Respond with ONLY the JSON object. No markdown, no explanation."""


# ---------------------------------------------------------------------------
# API interaction
# ---------------------------------------------------------------------------
def load_api_key() -> str:
    """Load the DashScope API key from environment variable or .env file."""
    key = os.environ.get("DASHSCOPE_API_KEY")
    if key:
        return key

    for env_path in [Path(".env"), Path("../.env")]:
        if env_path.exists():
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("DASHSCOPE_API_KEY="):
                        return line.split("=", 1)[1].strip().strip("'\"")

    sys.exit(
        "[ERROR] DASHSCOPE_API_KEY not found.\n"
        "Either set it as an environment variable:\n"
        "  export DASHSCOPE_API_KEY=your_key_here\n"
        "Or create a .env file with:\n"
        "  DASHSCOPE_API_KEY=your_key_here"
    )


def encode_image(image_path: str) -> str:
    """Read an image file and return its base64-encoded content."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def classify_page(image_path: str, api_key: str, model: str = DEFAULT_MODEL) -> dict:
    """
    Send an image to Qwen-VL via DashScope API and get page classification.
    Uses the OpenAI-compatible endpoint format.
    """
    img_base64 = encode_image(image_path)

    suffix = Path(image_path).suffix.lower()
    mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
    mime_type = mime_map.get(suffix, "image/png")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": CLASSIFICATION_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{img_base64}"
                        },
                    },
                ],
            }
        ],
        "temperature": 0.1,
        "max_tokens": 256,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(
                DASHSCOPE_API_URL, headers=headers, json=payload, timeout=60
            )

            if resp.status_code == 429:
                wait = 10 * attempt
                log.warning("  Rate limited. Waiting %ds...", wait)
                time.sleep(wait)
                continue

            if resp.status_code != 200:
                log.error("  API error %d: %s", resp.status_code, resp.text[:300])
                if attempt < MAX_RETRIES:
                    time.sleep(5)
                    continue
                return _error_result(f"API error {resp.status_code}")

            data = resp.json()
            text = _extract_text(data)
            return _parse_response(text)

        except requests.RequestException as e:
            log.warning("  Request failed (attempt %d/%d): %s", attempt, MAX_RETRIES, e)
            if attempt < MAX_RETRIES:
                time.sleep(5)
            else:
                return _error_result(str(e))

    return _error_result("Max retries exceeded")


def _extract_text(api_response: dict) -> str:
    """Extract the text content from a DashScope/OpenAI-format response."""
    try:
        choices = api_response.get("choices", [])
        if not choices:
            return ""
        message = choices[0].get("message", {})
        return message.get("content", "")
    except (KeyError, IndexError):
        return ""


def _parse_response(text: str) -> dict:
    """Parse the VLM text response into a structured dict."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    text = text.strip()

    try:
        result = json.loads(text)

        has_image = str(result.get("has_image", "N")).strip().upper()
        has_text = str(result.get("has_text", "N")).strip().upper()
        count = int(result.get("count_of_image", 0))

        layout = str(result.get("img_layout", "NA")).strip().lower()
        valid_layouts = {"na", "sgl", "td", "lr"}
        if layout not in valid_layouts:
            layout = "na"

        # Consistency checks
        if has_image == "N":
            count = 0
            layout = "na"
        if count == 0:
            has_image = "N"
            layout = "na"
        if count == 1 and layout not in ("sgl", "na"):
            layout = "sgl"
        if count > 1 and layout == "sgl":
            layout = "td"

        return {
            "has_image": has_image,
            "has_text": has_text,
            "count_of_image": count,
            "img_layout": layout.upper() if layout == "na" else layout,
            "raw_response": text,
            "error": "",
        }

    except (json.JSONDecodeError, ValueError, TypeError) as e:
        log.warning("  Failed to parse response: %s", text[:100])
        return _error_result(f"Parse error: {e}")


def _error_result(error_msg: str) -> dict:
    """Return a result dict indicating an error."""
    return {
        "has_image": "",
        "has_text": "",
        "count_of_image": "",
        "img_layout": "",
        "raw_response": "",
        "error": error_msg,
    }


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def get_image_files(image_dir: str, book_id: str) -> list[Path]:
    """Get sorted list of page images for a given book."""
    image_dir = Path(image_dir)
    files = sorted(
        image_dir.glob(f"{book_id}_*.png"),
        key=lambda p: int(p.stem.split("_")[-1])
    )
    if not files:
        files = sorted(
            image_dir.glob(f"{book_id}_*.jpg"),
            key=lambda p: int(p.stem.split("_")[-1])
        )
    return files


def load_existing_results(csv_path: str) -> set:
    """Load already-processed pageIDs from an existing CSV (for resume)."""
    done = set()
    path = Path(csv_path)
    if not path.exists():
        return done
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("pageID") and not row.get("error"):
                done.add(row["pageID"])
    return done


def process_book(image_dir: str, book_id: str, output_csv: str,
                 api_key: str, model: str = DEFAULT_MODEL,
                 limit: int = 0, resume: bool = False,
                 delay: float = DEFAULT_DELAY):
    """
    Process all page images for one book through the VLM classification pipeline.
    """
    files = get_image_files(image_dir, book_id)
    if not files:
        sys.exit(f"[ERROR] No images found for {book_id} in {image_dir}")

    log.info("Found %d page images for %s", len(files), book_id)

    done_pages = set()
    if resume:
        done_pages = load_existing_results(output_csv)
        log.info("Resume mode: %d pages already processed", len(done_pages))

    csv_path = Path(output_csv)
    file_exists = csv_path.exists() and resume
    mode = "a" if file_exists else "w"

    fieldnames = ["pageID", "has_image", "has_text", "count_of_image",
                  "img_layout", "error"]

    processed = 0
    errors = 0

    with open(output_csv, mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if mode == "w":
            writer.writeheader()

        for i, img_file in enumerate(files):
            page_id = img_file.stem

            if page_id in done_pages:
                continue

            if limit > 0 and processed >= limit:
                log.info("Reached limit of %d pages", limit)
                break

            log.info("[%d/%d] Classifying: %s", i + 1, len(files), page_id)

            result = classify_page(str(img_file), api_key, model)

            row = {
                "pageID": page_id,
                "has_image": result["has_image"],
                "has_text": result["has_text"],
                "count_of_image": result["count_of_image"],
                "img_layout": result["img_layout"],
                "error": result["error"],
            }
            writer.writerow(row)
            f.flush()

            if result["error"]:
                errors += 1
                log.warning("  ERROR: %s", result["error"])
            else:
                log.info("  -> has_image=%s has_text=%s count=%s layout=%s",
                         result["has_image"], result["has_text"],
                         result["count_of_image"], result["img_layout"])

            processed += 1
            time.sleep(delay)

    log.info("=" * 60)
    log.info("Done. Processed: %d | Errors: %d", processed, errors)
    log.info("Output CSV: %s", output_csv)
    log.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Step 3: Page-level indexing using Qwen-VL (DashScope)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python step3_index.py ../step2_tool/output/gy_mg/ --book-id gy_mg
  python step3_index.py ../step2_tool/output/gy_mg/ --book-id gy_mg --limit 10
  python step3_index.py ../step2_tool/output/gy_mg/ --book-id gy_mg --resume
  python step3_index.py ../step2_tool/output/gy_mg/ --book-id gy_mg -o results/gy_mg.csv

The script reads DASHSCOPE_API_KEY from:
  1. Environment variable DASHSCOPE_API_KEY
  2. A .env file in the current or parent directory
        """
    )
    parser.add_argument("image_dir",
                        help="Directory containing page images from Step 2")
    parser.add_argument("--book-id", required=True,
                        help="Book identifier (e.g. gy_mg)")
    parser.add_argument("-o", "--output", default=None,
                        help="Output CSV path (default: ./index/{book_id}_index.csv)")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help="Model name (default: qwen-vl-plus)")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max pages to process, 0=all (default: 0)")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from where we left off")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY,
                        help="Seconds between API requests (default: 1.0)")

    args = parser.parse_args()
    output_csv = args.output or f"./index/{args.book_id}_index.csv"

    Path(output_csv).parent.mkdir(parents=True, exist_ok=True)

    api_key = load_api_key()

    log.info("=" * 60)
    log.info("Step 3: Page-Level Indexing (Qwen-VL)")
    log.info("=" * 60)
    log.info("Image dir:  %s", args.image_dir)
    log.info("Book ID:    %s", args.book_id)
    log.info("Model:      %s", args.model)
    log.info("Output CSV: %s", output_csv)
    log.info("Limit:      %s", args.limit or "all")
    log.info("Resume:     %s", args.resume)
    log.info("-" * 60)

    process_book(
        image_dir=args.image_dir,
        book_id=args.book_id,
        output_csv=output_csv,
        api_key=api_key,
        model=args.model,
        limit=args.limit,
        resume=args.resume,
        delay=args.delay,
    )


if __name__ == "__main__":
    main()
