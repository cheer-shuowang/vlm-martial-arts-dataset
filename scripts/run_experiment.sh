#!/bin/bash
# ═══════════════════════════════════════════════════════════
# Experiment: Qwen3-VL-Flash + Enhanced Prompt (v2) vs Qwen-VL-Plus (v1)
# ═══════════════════════════════════════════════════════════
# Prerequisites:
#   1. .env file with DASHSCOPE_API_KEY (international key)
#   2. step3_index_v2.py in scripts/
#   3. compare_models.py in scripts/
#   4. Existing baseline indexes in ./index/

# ── Step A: Run Flash v2 on all books that have baseline results ──

BOOKS=(
  "slgf_mt"
  "gy_mg"
  "gzfh_ld"
  "slgf_qc"
  "jx_rep"
  "sec_cq"
  "sbl_v2"
)

for BOOK in "${BOOKS[@]}"; do
  echo "========================================"
  echo "Processing: $BOOK"
  echo "========================================"
  python3.12 scripts/step3_index_v2.py "./output/$BOOK/" \
    --book-id "$BOOK" \
    -o "./index/${BOOK}_index_qwen3flash_v2.csv"
done

# jx_mg volumes (separate dirs)
for VOL_DIR in ./output/jx_mg/jx_mg_vol*; do
  VID=$(basename "$VOL_DIR")
  echo "========================================"
  echo "Processing: $VID"
  echo "========================================"
  python3.12 scripts/step3_index_v2.py "$VOL_DIR" \
    --book-id "$VID" \
    -o "./index/${VID}_index_qwen3flash_v2.csv"
done

# ── Step B: Generate comparison report ──

echo "========================================"
echo "Generating comparison report..."
echo "========================================"
python3.12 scripts/compare_models.py \
  --batch \
  --baseline-dir ./index/ \
  --candidate-dir ./index/ \
  --baseline-suffix "_index.csv" \
  --candidate-suffix "_index_qwen3flash_v2.csv" \
  --baseline-label "Qwen-VL-Plus (v1 prompt)" \
  --candidate-label "Qwen3-VL-Flash (v2 prompt)" \
  -o ./docs/model_comparison_report.md

echo "========================================"
echo "Done! Report saved to ./docs/model_comparison_report.md"
echo "========================================"
