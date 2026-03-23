#!/usr/bin/env python3
"""
Model Comparison: Compare Step 3 index results across different models/prompts.
================================================================================
Generates a detailed comparison report in Markdown format.

Usage:
    python compare_models.py --baseline ./index/slgf_mt_index.csv \
                             --candidate ./index/slgf_mt_index_qwen3flash_v2.csv \
                             --baseline-label "VL-Plus (v1 prompt)" \
                             --candidate-label "VL3-Flash (v2 prompt)"

    # Batch compare all books:
    python compare_models.py --batch --baseline-dir ./index/ --candidate-dir ./index_flash_v2/ \
                             --baseline-suffix "_index.csv" --candidate-suffix "_index_qwen3flash_v2.csv"

Dependencies:
    (none beyond stdlib)
"""

import argparse
import csv
import sys
from pathlib import Path

FIELDS = ['has_image', 'has_text', 'count_of_image', 'img_layout']


def load_index(path: str) -> dict:
    rows = {}
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows[row['pageID']] = row
    return rows


def compare_two(baseline_path: str, candidate_path: str,
                baseline_label: str, candidate_label: str) -> dict:
    baseline = load_index(baseline_path)
    candidate = load_index(candidate_path)

    total = 0
    agree = {f: 0 for f in FIELDS}
    all_agree_count = 0
    disagree_details = []

    b_errors = sum(1 for r in baseline.values() if r.get('error'))
    c_errors = sum(1 for r in candidate.values() if r.get('error'))

    for pid in sorted(baseline.keys(), key=lambda x: int(x.split('_')[-1])):
        b = baseline[pid]
        c = candidate.get(pid)
        if not c:
            continue
        if b.get('error') or c.get('error'):
            continue
        total += 1

        row_match = True
        for field in FIELDS:
            bv = str(b.get(field, '')).strip().upper()
            cv = str(c.get(field, '')).strip().upper()
            if bv == cv:
                agree[field] += 1
            else:
                row_match = False
                disagree_details.append((pid, field, bv, cv))

        if row_match:
            all_agree_count += 1

    return {
        'total': total,
        'agree': agree,
        'all_agree': all_agree_count,
        'disagree': disagree_details,
        'b_errors': b_errors,
        'c_errors': c_errors,
        'baseline_label': baseline_label,
        'candidate_label': candidate_label,
        'baseline_pages': len(baseline),
        'candidate_pages': len(candidate),
    }


def format_report_single(result: dict, book_id: str) -> str:
    t = result['total']
    if t == 0:
        return f"### {book_id}\nNo comparable pages.\n"

    lines = [f"### {book_id}"]
    lines.append(f"- Comparable pages: {t}")
    lines.append(f"- Full row agreement: {result['all_agree']}/{t} "
                 f"({result['all_agree']/t*100:.1f}%)")
    lines.append(f"- Errors: {result['baseline_label']}={result['b_errors']}, "
                 f"{result['candidate_label']}={result['c_errors']}")
    lines.append("")
    lines.append("| Field | Agreement |")
    lines.append("|-------|-----------|")
    for f in FIELDS:
        pct = result['agree'][f] / t * 100
        lines.append(f"| {f} | {result['agree'][f]}/{t} ({pct:.1f}%) |")

    if result['disagree']:
        lines.append("")
        lines.append(f"**Disagreements ({len(result['disagree'])})**:")
        lines.append("")
        lines.append(f"| Page | Field | {result['baseline_label']} | {result['candidate_label']} |")
        lines.append("|------|-------|--------|-----------|")
        for pid, field, bv, cv in result['disagree']:
            lines.append(f"| {pid} | {field} | {bv} | {cv} |")

    lines.append("")
    return "\n".join(lines)


def format_summary(all_results: list) -> str:
    lines = ["## Summary across all books", ""]
    lines.append(f"| Book | Pages | Full agreement | has_image | has_text | count_of_image | img_layout |")
    lines.append("|------|-------|----------------|-----------|----------|----------------|------------|")

    total_pages = 0
    total_agree = 0
    total_field = {f: [0, 0] for f in FIELDS}

    for book_id, result in all_results:
        t = result['total']
        if t == 0:
            continue
        total_pages += t
        total_agree += result['all_agree']
        full_pct = result['all_agree'] / t * 100

        field_pcts = []
        for f in FIELDS:
            pct = result['agree'][f] / t * 100
            field_pcts.append(f"{pct:.1f}%")
            total_field[f][0] += result['agree'][f]
            total_field[f][1] += t

        lines.append(f"| {book_id} | {t} | {full_pct:.1f}% | "
                     f"{' | '.join(field_pcts)} |")

    if total_pages > 0:
        overall_pct = total_agree / total_pages * 100
        field_overall = []
        for f in FIELDS:
            pct = total_field[f][0] / total_field[f][1] * 100 if total_field[f][1] > 0 else 0
            field_overall.append(f"{pct:.1f}%")
        lines.append(f"| **TOTAL** | **{total_pages}** | **{overall_pct:.1f}%** | "
                     f"**{'** | **'.join(field_overall)}** |")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Compare Step 3 index results between two models/prompts")
    parser.add_argument("--baseline", help="Baseline CSV file (single mode)")
    parser.add_argument("--candidate", help="Candidate CSV file (single mode)")
    parser.add_argument("--baseline-label", default="Baseline",
                        help="Label for baseline model")
    parser.add_argument("--candidate-label", default="Candidate",
                        help="Label for candidate model")
    parser.add_argument("--batch", action="store_true",
                        help="Batch mode: compare all matching books")
    parser.add_argument("--baseline-dir", default="./index/",
                        help="Directory with baseline CSVs (batch mode)")
    parser.add_argument("--candidate-dir", default="./index/",
                        help="Directory with candidate CSVs (batch mode)")
    parser.add_argument("--baseline-suffix", default="_index.csv",
                        help="Filename suffix for baseline CSVs")
    parser.add_argument("--candidate-suffix", default="_index_qwen3flash_v2.csv",
                        help="Filename suffix for candidate CSVs")
    parser.add_argument("-o", "--output", default=None,
                        help="Output markdown file (default: stdout)")

    args = parser.parse_args()

    report_lines = [
        "# Step 3 Model Comparison Report",
        "",
        f"**Baseline**: {args.baseline_label}",
        f"**Candidate**: {args.candidate_label}",
        "",
        "---",
        "",
    ]

    if args.batch:
        baseline_dir = Path(args.baseline_dir)
        candidate_dir = Path(args.candidate_dir)
        all_results = []

        for bf in sorted(baseline_dir.glob(f"*{args.baseline_suffix}")):
            book_id = bf.stem.replace(args.baseline_suffix.replace('.csv', ''), '')
            cf = candidate_dir / f"{book_id}{args.candidate_suffix}"
            if not cf.exists():
                continue
            result = compare_two(str(bf), str(cf),
                                 args.baseline_label, args.candidate_label)
            all_results.append((book_id, result))
            report_lines.append(format_report_single(result, book_id))

        if all_results:
            report_lines.insert(7, format_summary(all_results))
            report_lines.insert(8, "---\n")
            report_lines.insert(9, "## Per-book details\n")

    else:
        if not args.baseline or not args.candidate:
            sys.exit("Provide --baseline and --candidate, or use --batch")
        result = compare_two(args.baseline, args.candidate,
                             args.baseline_label, args.candidate_label)
        book_id = Path(args.baseline).stem.replace('_index', '')
        report_lines.append(format_report_single(result, book_id))

    report = "\n".join(report_lines)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report saved to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
