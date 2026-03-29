# Step 4 Model Comparison Report

**Baseline**: Qwen-VL-Plus
**Candidate**: Qwen3-VL-Flash
**Comparable pages**: 10

---

## Agreement Summary

| Metric | Score |
|--------|-------|
| Image count agreement | 9/10 (90.0%) |
| count_person agreement | 9/10 (90.0%) |
| count_weapon agreement | 10/10 (100.0%) |
| type_weapons Jaccard (avg) | 0.700 |
| Both have original_text | 10/10 (100.0%) |
| Both have translation | 10/10 (100.0%) |

## Disagreements (1 total)

| Page | Field | Qwen-VL-Plus | Qwen3-VL-Flash |
|------|-------|--------|-----------|
| slgf_mt_13 | count_person | 1 | 0 |

---

*Generated from: ./extraction/slgf_mt_step4_plus.jsonl vs ./extraction/slgf_mt_step4_flash.jsonl*