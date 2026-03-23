# Step 4 Model Comparison Report

**Baseline**: Qwen-VL-Plus
**Candidate**: Qwen3-VL-Flash
**Comparable pages**: 86

---

## Agreement Summary

| Metric | Score |
|--------|-------|
| Image count agreement | 84/86 (97.7%) |
| count_person agreement | 85/86 (98.8%) |
| count_weapon agreement | 80/86 (93.0%) |
| type_weapons Jaccard (avg) | 0.750 |
| Both have original_text | 86/86 (100.0%) |
| Both have translation | 86/86 (100.0%) |

## Disagreements (7 total)

| Page | Field | Qwen-VL-Plus | Qwen3-VL-Flash |
|------|-------|--------|-----------|
| slgf_mt_16 | count_weapon | 1 | 2 |
| slgf_mt_29 | count_weapon | 1 | 2 |
| slgf_mt_43 | count_weapon | 1 | 2 |
| slgf_mt_76 | count_weapon | 0 | 1 |
| slgf_mt_115 | count_weapon | 2 | 3 |
| slgf_mt_119 | count_weapon | 3 | 2 |
| slgf_mt_132 | count_person | 2 | 0 |

---

*Generated from: ./extraction/slgf_mt_step4_plus.jsonl vs ./extraction/slgf_mt_step4_flash.jsonl*