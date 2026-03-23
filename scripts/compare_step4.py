#!/usr/bin/env python3
"""
Step 4 Model Comparison: Compare extraction results between two models.
========================================================================
Compares JSONL outputs from step4_extract.py run with different models.

Metrics:
  - count_person agreement
  - count_weapon agreement
  - type_weapons overlap (Jaccard similarity)
  - Text presence (did both produce original_text and translation?)

Usage:
    python compare_step4.py \
      --baseline ./extraction/slgf_mt_step4_plus.jsonl \
      --candidate ./extraction/slgf_mt_step4_flash.jsonl \
      -o ./docs/step4_comparison.md
"""

import argparse
import json
import sys
from pathlib import Path


def load_jsonl(path: str) -> dict:
    """Load JSONL file, keyed by pageID."""
    records = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                pid = obj.get("pageID", "")
                if pid:
                    records[pid] = obj
            except json.JSONDecodeError:
                continue
    return records


def jaccard(list_a: list, list_b: list) -> float:
    """Jaccard similarity between two lists (case-insensitive)."""
    set_a = set(s.lower().strip() for s in list_a)
    set_b = set(s.lower().strip() for s in list_b)
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def compare(baseline_path: str, candidate_path: str,
            baseline_label: str, candidate_label: str) -> str:
    baseline = load_jsonl(baseline_path)
    candidate = load_jsonl(candidate_path)

    common_pages = sorted(set(baseline.keys()) & set(candidate.keys()),
                          key=lambda x: int(x.split("_")[-1]))

    total = 0
    person_agree = 0
    weapon_agree = 0
    weapon_jaccard_sum = 0.0
    both_have_text = 0
    both_have_translation = 0
    img_count_agree = 0
    disagreements = []

    for pid in common_pages:
        b = baseline[pid]
        c = candidate[pid]

        # Skip errors
        if b.get("error") or c.get("error"):
            continue

        b_imgs = b.get("images", [])
        c_imgs = c.get("images", [])

        if not b_imgs and not c_imgs:
            continue

        total += 1

        # Image count agreement
        if len(b_imgs) == len(c_imgs):
            img_count_agree += 1

        # Compare first image (primary comparison)
        b0 = b_imgs[0] if b_imgs else {}
        c0 = c_imgs[0] if c_imgs else {}

        # count_person
        bp = b0.get("count_person", 0)
        cp = c0.get("count_person", 0)
        if bp == cp:
            person_agree += 1
        else:
            disagreements.append((pid, "count_person", str(bp), str(cp)))

        # count_weapon
        bw = b0.get("count_weapon", 0)
        cw = c0.get("count_weapon", 0)
        if bw == cw:
            weapon_agree += 1
        else:
            disagreements.append((pid, "count_weapon", str(bw), str(cw)))

        # type_weapons jaccard
        b_types = b0.get("type_weapons", [])
        c_types = c0.get("type_weapons", [])
        weapon_jaccard_sum += jaccard(b_types, c_types)

        # Text presence
        if b0.get("original_text") and c0.get("original_text"):
            both_have_text += 1
        if b0.get("text_to_EN") and c0.get("text_to_EN"):
            both_have_translation += 1

    if total == 0:
        return "No comparable pages found.\n"

    # Build report
    lines = [
        "# Step 4 Model Comparison Report",
        "",
        f"**Baseline**: {baseline_label}",
        f"**Candidate**: {candidate_label}",
        f"**Comparable pages**: {total}",
        "",
        "---",
        "",
        "## Agreement Summary",
        "",
        "| Metric | Score |",
        "|--------|-------|",
        f"| Image count agreement | {img_count_agree}/{total} ({img_count_agree/total*100:.1f}%) |",
        f"| count_person agreement | {person_agree}/{total} ({person_agree/total*100:.1f}%) |",
        f"| count_weapon agreement | {weapon_agree}/{total} ({weapon_agree/total*100:.1f}%) |",
        f"| type_weapons Jaccard (avg) | {weapon_jaccard_sum/total:.3f} |",
        f"| Both have original_text | {both_have_text}/{total} ({both_have_text/total*100:.1f}%) |",
        f"| Both have translation | {both_have_translation}/{total} ({both_have_translation/total*100:.1f}%) |",
        "",
    ]

    if disagreements:
        lines.append(f"## Disagreements ({len(disagreements)} total)")
        lines.append("")
        lines.append(f"| Page | Field | {baseline_label} | {candidate_label} |")
        lines.append("|------|-------|--------|-----------|")
        for pid, field, bv, cv in disagreements[:50]:
            lines.append(f"| {pid} | {field} | {bv} | {cv} |")
        if len(disagreements) > 50:
            lines.append(f"\n*... and {len(disagreements) - 50} more*")
        lines.append("")

    lines.append("---")
    lines.append(f"\n*Generated from: {baseline_path} vs {candidate_path}*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Compare Step 4 extraction results between two models")
    parser.add_argument("--baseline", required=True,
                        help="Baseline JSONL file")
    parser.add_argument("--candidate", required=True,
                        help="Candidate JSONL file")
    parser.add_argument("--baseline-label", default="Qwen-VL-Plus",
                        help="Label for baseline model")
    parser.add_argument("--candidate-label", default="Qwen3-VL-Flash",
                        help="Label for candidate model")
    parser.add_argument("-o", "--output", default=None,
                        help="Output markdown file (default: stdout)")

    args = parser.parse_args()

    report = compare(
        args.baseline, args.candidate,
        args.baseline_label, args.candidate_label
    )

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report saved to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
