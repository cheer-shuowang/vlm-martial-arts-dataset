#!/usr/bin/env python3
"""
Step 4: Image-Level Data Extraction using VLM
===============================================
For each page where has_image=Y and has_text=Y (from Step 3 index),
extract detailed information about illustrations and accompanying text.

Outputs:
  - imgID: {pageID}_1, {pageID}_2, etc.
  - original_text: source language text on the page
  - text_to_EN: English translation
  - count_person: number of people in illustration
  - count_weapon: number of weapons
  - type_weapons: list of weapon types
  - persons: per-person description (identifier, posture, tactic)

Output format: JSON Lines (.jsonl), one JSON object per image.

Usage:
    python step4_extract.py ./output/slgf_mt/ --book-id slgf_mt --index ./index/slgf_mt_index.csv
    python step4_extract.py ./output/slgf_mt/ --book-id slgf_mt --index ./index/slgf_mt_index.csv --limit 10
    python step4_extract.py ./output/slgf_mt/ --book-id slgf_mt --index ./index/slgf_mt_index.csv --resume
    python step4_extract.py ./output/slgf_mt/ --book-id slgf_mt --index ./index/slgf_mt_index.csv --model qwen3-vl-flash

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
DASHSCOPE_API_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
DEFAULT_MODEL = "qwen-vl-plus"
DEFAULT_DELAY = 2.0  # longer delay -- step4 responses are heavier
MAX_RETRIES = 3


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------
def build_extraction_prompt(page_id: str, count_of_image: int, img_layout: str) -> str:
    """
    Build the extraction prompt based on page metadata from Step 3.
    """
    if count_of_image <= 1:
        image_instruction = (
            "This page contains ONE illustration with accompanying text.\n"
            "Analyze the single illustration and extract all fields below."
        )
        id_instruction = f'Use imgID: "{page_id}_1"'
    else:
        if img_layout == "td":
            order_desc = "top-to-bottom"
        elif img_layout == "lr":
            order_desc = "left-to-right"
        else:
            order_desc = "top-to-bottom"

        image_instruction = (
            f"This page contains {count_of_image} illustrations arranged {order_desc}.\n"
            f"Process each illustration separately in {order_desc} order."
        )
        id_instruction = (
            f'Number them sequentially: "{page_id}_1", "{page_id}_2", etc. '
            f"in {order_desc} order."
        )

    prompt = f"""You are analyzing a scanned page from a historical Chinese martial arts text.

{image_instruction}
{id_instruction}

For EACH illustration on this page, extract the following and respond with a JSON array.
Each element in the array represents one illustration.

```json
[
  {{
    "imgID": "{page_id}_1",
    "original_text": "The original text on this page in its source language (Classical Chinese). Transcribe the text that accompanies or describes THIS illustration. If text is shared across illustrations, include it with the first one.",
    "text_to_EN": "English translation of original_text.",
    "count_person": 0,
    "count_weapon": 0,
    "type_weapons": [],
    "persons": [
      {{
        "identifier": "e.g. Person Left, Person Right, Person One",
        "posture": "Detailed description: stance, hand position, foot position, body angle, weight distribution",
        "tactic": "Interpretation of the combat movement, technique name if visible, martial application"
      }}
    ]
  }}
]
```

Rules:
- original_text: Transcribe the Classical Chinese text as accurately as possible. Include title/heading text if present.
- text_to_EN: Provide a faithful English translation. Keep martial arts terminology where appropriate.
- count_person: Count the number of distinct human figures in the illustration. 0 if the illustration shows only weapons/diagrams.
- count_weapon: Count visible weapons (staffs, swords, spears, etc.). Hands/fists do not count as weapons.
- type_weapons: List each weapon type in spatial order ({order_desc if count_of_image > 1 else "left to right"}). Use English terms (e.g. "staff", "sword", "spear", "halberd", "shield", "bow").
- persons: For EACH person, describe their posture in detail and interpret the martial technique being performed.
- If an illustration contains no people (e.g. weapon diagram only), set count_person=0 and persons=[].

Respond with ONLY the JSON array. No markdown fences, no explanation."""

    return prompt


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


def call_vlm(image_path: str, prompt: str, api_key: str,
             model: str = DEFAULT_MODEL) -> dict:
    """
    Send an image + prompt to the VLM and return the parsed response.
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
                    {"type": "text", "text": prompt},
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
        "max_tokens": 4096,  # step4 needs much longer output
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(
                DASHSCOPE_API_URL, headers=headers, json=payload, timeout=120
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
                return {"error": f"API error {resp.status_code}"}

            data = resp.json()
            text = _extract_text(data)
            return _parse_extraction(text)

        except requests.RequestException as e:
            log.warning("  Request failed (attempt %d/%d): %s",
                        attempt, MAX_RETRIES, e)
            if attempt < MAX_RETRIES:
                time.sleep(5)
            else:
                return {"error": str(e)}

    return {"error": "Max retries exceeded"}


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


def _parse_extraction(text: str) -> dict:
    """Parse the VLM response into structured extraction data."""
    text = text.strip()

    # Strip markdown fences
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    text = text.strip()

    try:
        result = json.loads(text)

        # Ensure it's a list
        if isinstance(result, dict):
            result = [result]

        if not isinstance(result, list):
            return {"error": f"Unexpected response type: {type(result).__name__}",
                    "raw_response": text}

        # Validate and clean each image entry
        cleaned = []
        for item in result:
            entry = {
                "imgID": str(item.get("imgID", "")),
                "original_text": str(item.get("original_text", "")),
                "text_to_EN": str(item.get("text_to_EN", "")),
                "count_person": _safe_int(item.get("count_person", 0)),
                "count_weapon": _safe_int(item.get("count_weapon", 0)),
                "type_weapons": item.get("type_weapons", []),
                "persons": item.get("persons", []),
            }

            # Ensure type_weapons is a list
            if not isinstance(entry["type_weapons"], list):
                entry["type_weapons"] = [str(entry["type_weapons"])]

            # Ensure persons is a list of dicts
            if not isinstance(entry["persons"], list):
                entry["persons"] = []

            cleaned_persons = []
            for p in entry["persons"]:
                if isinstance(p, dict):
                    cleaned_persons.append({
                        "identifier": str(p.get("identifier", "")),
                        "posture": str(p.get("posture", "")),
                        "tactic": str(p.get("tactic", "")),
                    })
            entry["persons"] = cleaned_persons

            cleaned.append(entry)

        return {"images": cleaned, "error": ""}

    except (json.JSONDecodeError, ValueError, TypeError) as e:
        log.warning("  Failed to parse response: %s", text[:200])
        return {"error": f"Parse error: {e}", "raw_response": text}


def _safe_int(val) -> int:
    """Safely convert a value to int."""
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0


# ---------------------------------------------------------------------------
# Index loading
# ---------------------------------------------------------------------------
def load_step3_index(index_path: str) -> list[dict]:
    """
    Load Step 3 index CSV and return pages where has_image=Y AND has_text=Y.
    """
    qualifying = []
    with open(index_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if (row.get("has_image", "").strip().upper() == "Y"
                    and row.get("has_text", "").strip().upper() == "Y"
                    and not row.get("error")):
                qualifying.append({
                    "pageID": row["pageID"],
                    "count_of_image": int(row.get("count_of_image", 1)),
                    "img_layout": row.get("img_layout", "sgl").strip().lower(),
                })
    return qualifying


def load_existing_results(jsonl_path: str) -> set:
    """Load already-processed pageIDs from an existing JSONL (for resume)."""
    done = set()
    path = Path(jsonl_path)
    if not path.exists():
        return done
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if obj.get("pageID") and not obj.get("error"):
                    done.add(obj["pageID"])
            except json.JSONDecodeError:
                continue
    return done


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def process_book(image_dir: str, book_id: str, index_path: str,
                 output_path: str, api_key: str,
                 model: str = DEFAULT_MODEL,
                 limit: int = 0, resume: bool = False,
                 delay: float = DEFAULT_DELAY):
    """
    Process all qualifying pages for one book through Step 4 extraction.
    """
    # Load qualifying pages from Step 3 index
    pages = load_step3_index(index_path)
    if not pages:
        sys.exit(f"[ERROR] No qualifying pages (has_image=Y, has_text=Y) "
                 f"found in {index_path}")

    log.info("Found %d qualifying pages for %s", len(pages), book_id)

    # Resume support
    done_pages = set()
    if resume:
        done_pages = load_existing_results(output_path)
        log.info("Resume mode: %d pages already processed", len(done_pages))

    # Find image files
    image_dir = Path(image_dir)

    # Output
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if (out_path.exists() and resume) else "w"

    processed = 0
    errors = 0
    total_images = 0

    with open(output_path, mode, encoding="utf-8") as f:
        for i, page in enumerate(pages):
            page_id = page["pageID"]

            if page_id in done_pages:
                continue

            if limit > 0 and processed >= limit:
                log.info("Reached limit of %d pages", limit)
                break

            # Find image file
            img_file = image_dir / f"{page_id}.png"
            if not img_file.exists():
                img_file = image_dir / f"{page_id}.jpg"
            if not img_file.exists():
                log.warning("  Image not found: %s", page_id)
                errors += 1
                continue

            log.info("[%d/%d] Extracting: %s (images=%d, layout=%s)",
                     i + 1, len(pages), page_id,
                     page["count_of_image"], page["img_layout"])

            # Build prompt
            prompt = build_extraction_prompt(
                page_id, page["count_of_image"], page["img_layout"]
            )

            # Call VLM
            result = call_vlm(str(img_file), prompt, api_key, model)

            # Write output
            output_record = {
                "pageID": page_id,
                "book_id": book_id,
                "model": model,
                "count_of_image": page["count_of_image"],
                "img_layout": page["img_layout"],
            }

            if result.get("error"):
                output_record["error"] = result["error"]
                if "raw_response" in result:
                    output_record["raw_response"] = result["raw_response"]
                errors += 1
                log.warning("  ERROR: %s", result["error"])
            else:
                output_record["images"] = result["images"]
                output_record["error"] = ""
                n_imgs = len(result["images"])
                total_images += n_imgs
                log.info("  -> Extracted %d image(s)", n_imgs)

                # Log summary for each image
                for img in result["images"]:
                    log.info("     %s: %d person(s), %d weapon(s), types=%s",
                             img["imgID"],
                             img["count_person"],
                             img["count_weapon"],
                             img["type_weapons"])

            f.write(json.dumps(output_record, ensure_ascii=False) + "\n")
            f.flush()

            processed += 1
            time.sleep(delay)

    log.info("=" * 60)
    log.info("Done.")
    log.info("  Pages processed:  %d", processed)
    log.info("  Images extracted: %d", total_images)
    log.info("  Errors:           %d", errors)
    log.info("  Output:           %s", output_path)
    log.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Step 4: Image-level data extraction using VLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python step4_extract.py ./output/slgf_mt/ --book-id slgf_mt --index ./index/slgf_mt_index.csv
  python step4_extract.py ./output/slgf_mt/ --book-id slgf_mt --index ./index/slgf_mt_index.csv --limit 10
  python step4_extract.py ./output/slgf_mt/ --book-id slgf_mt --index ./index/slgf_mt_index.csv --resume
  python step4_extract.py ./output/slgf_mt/ --book-id slgf_mt --index ./index/slgf_mt_index.csv --model qwen3-vl-flash

The script reads DASHSCOPE_API_KEY from:
  1. Environment variable DASHSCOPE_API_KEY
  2. A .env file in the current or parent directory
        """
    )
    parser.add_argument("image_dir",
                        help="Directory containing page images from Step 2")
    parser.add_argument("--book-id", required=True,
                        help="Book identifier (e.g. slgf_mt)")
    parser.add_argument("--index", required=True,
                        help="Path to Step 3 index CSV")
    parser.add_argument("-o", "--output", default=None,
                        help="Output JSONL path (default: ./extraction/{book_id}_step4.jsonl)")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"Model name (default: {DEFAULT_MODEL})")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max pages to process, 0=all (default: 0)")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from where we left off")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY,
                        help=f"Seconds between API requests (default: {DEFAULT_DELAY})")

    args = parser.parse_args()
    output_path = args.output or f"./extraction/{args.book_id}_step4.jsonl"

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    api_key = load_api_key()

    log.info("=" * 60)
    log.info("Step 4: Image-Level Data Extraction")
    log.info("=" * 60)
    log.info("Image dir:  %s", args.image_dir)
    log.info("Book ID:    %s", args.book_id)
    log.info("Index:      %s", args.index)
    log.info("Model:      %s", args.model)
    log.info("Output:     %s", output_path)
    log.info("Limit:      %s", args.limit or "all")
    log.info("Resume:     %s", args.resume)
    log.info("-" * 60)

    process_book(
        image_dir=args.image_dir,
        book_id=args.book_id,
        index_path=args.index,
        output_path=output_path,
        api_key=api_key,
        model=args.model,
        limit=args.limit,
        resume=args.resume,
        delay=args.delay,
    )


if __name__ == "__main__":
    main()
