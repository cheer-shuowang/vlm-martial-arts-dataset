# Step 3 Model Comparison Report

**Baseline**: Qwen-VL-Plus (v1 prompt)
**Candidate**: Qwen3-VL-Flash (v2 prompt)

---

## Summary across all books

| Book | Pages | Full agreement | has_image | has_text | count_of_image | img_layout |
|------|-------|----------------|-----------|----------|----------------|------------|
| gzfh_ld | 198 | 92.4% | 92.4% | 100.0% | 92.4% | 92.9% |
| jx_rep | 470 | 92.1% | 96.0% | 100.0% | 92.3% | 92.3% |
| sec_cq | 158 | 89.2% | 91.1% | 99.4% | 89.9% | 89.9% |
| slgf_mt | 130 | 96.2% | 97.7% | 100.0% | 96.2% | 96.2% |
| slgf_qc | 104 | 96.2% | 99.0% | 99.0% | 97.1% | 98.1% |
| **TOTAL** | **1060** | **92.6%** | **95.1%** | **99.8%** | **92.9%** | **93.1%** |

---

## Per-book details

### gzfh_ld
- Comparable pages: 198
- Full row agreement: 183/198 (92.4%)
- Errors: Qwen-VL-Plus (v1 prompt)=0, Qwen3-VL-Flash (v2 prompt)=0

| Field | Agreement |
|-------|-----------|
| has_image | 183/198 (92.4%) |
| has_text | 198/198 (100.0%) |
| count_of_image | 183/198 (92.4%) |
| img_layout | 184/198 (92.9%) |

**Disagreements (44)**:

| Page | Field | Qwen-VL-Plus (v1 prompt) | Qwen3-VL-Flash (v2 prompt) |
|------|-------|--------|-----------|
| gzfh_ld_12 | has_image | Y | N |
| gzfh_ld_12 | count_of_image | 1 | 0 |
| gzfh_ld_12 | img_layout | SGL | NA |
| gzfh_ld_24 | has_image | Y | N |
| gzfh_ld_24 | count_of_image | 1 | 0 |
| gzfh_ld_24 | img_layout | SGL | NA |
| gzfh_ld_28 | has_image | Y | N |
| gzfh_ld_28 | count_of_image | 1 | 0 |
| gzfh_ld_28 | img_layout | SGL | NA |
| gzfh_ld_46 | has_image | Y | N |
| gzfh_ld_46 | count_of_image | 1 | 0 |
| gzfh_ld_46 | img_layout | SGL | NA |
| gzfh_ld_54 | has_image | Y | N |
| gzfh_ld_54 | count_of_image | 1 | 0 |
| gzfh_ld_54 | img_layout | SGL | NA |
| gzfh_ld_62 | has_image | Y | N |
| gzfh_ld_62 | count_of_image | 1 | 0 |
| gzfh_ld_62 | img_layout | SGL | NA |
| gzfh_ld_90 | has_image | N | Y |
| gzfh_ld_90 | count_of_image | 0 | 1 |
| gzfh_ld_90 | img_layout | NA | SGL |
| gzfh_ld_110 | has_image | Y | N |
| gzfh_ld_110 | count_of_image | 1 | 0 |
| gzfh_ld_110 | img_layout | SGL | NA |
| gzfh_ld_118 | has_image | N | Y |
| gzfh_ld_118 | count_of_image | 0 | 1 |
| gzfh_ld_118 | img_layout | NA | SGL |
| gzfh_ld_120 | has_image | Y | N |
| gzfh_ld_120 | count_of_image | 1 | 0 |
| gzfh_ld_120 | img_layout | SGL | NA |
| gzfh_ld_140 | has_image | Y | N |
| gzfh_ld_140 | count_of_image | 1 | 0 |
| gzfh_ld_140 | img_layout | SGL | NA |
| gzfh_ld_148 | has_image | N | Y |
| gzfh_ld_148 | count_of_image | 0 | 1 |
| gzfh_ld_158 | has_image | Y | N |
| gzfh_ld_158 | count_of_image | 1 | 0 |
| gzfh_ld_158 | img_layout | SGL | NA |
| gzfh_ld_182 | has_image | Y | N |
| gzfh_ld_182 | count_of_image | 1 | 0 |
| gzfh_ld_182 | img_layout | SGL | NA |
| gzfh_ld_190 | has_image | N | Y |
| gzfh_ld_190 | count_of_image | 0 | 1 |
| gzfh_ld_190 | img_layout | NA | SGL |

### jx_rep
- Comparable pages: 470
- Full row agreement: 433/470 (92.1%)
- Errors: Qwen-VL-Plus (v1 prompt)=0, Qwen3-VL-Flash (v2 prompt)=0

| Field | Agreement |
|-------|-----------|
| has_image | 451/470 (96.0%) |
| has_text | 470/470 (100.0%) |
| count_of_image | 434/470 (92.3%) |
| img_layout | 434/470 (92.3%) |

**Disagreements (91)**:

| Page | Field | Qwen-VL-Plus (v1 prompt) | Qwen3-VL-Flash (v2 prompt) |
|------|-------|--------|-----------|
| jx_rep_1 | has_image | N | Y |
| jx_rep_1 | count_of_image | 0 | 1 |
| jx_rep_1 | img_layout | NA | SGL |
| jx_rep_60 | count_of_image | 1 | 2 |
| jx_rep_60 | img_layout | SGL | TD |
| jx_rep_107 | has_image | N | Y |
| jx_rep_107 | count_of_image | 0 | 1 |
| jx_rep_107 | img_layout | NA | SGL |
| jx_rep_108 | has_image | N | Y |
| jx_rep_108 | count_of_image | 0 | 1 |
| jx_rep_108 | img_layout | NA | SGL |
| jx_rep_129 | has_image | N | Y |
| jx_rep_129 | count_of_image | 0 | 1 |
| jx_rep_129 | img_layout | NA | SGL |
| jx_rep_134 | has_image | N | Y |
| jx_rep_134 | count_of_image | 0 | 1 |
| jx_rep_134 | img_layout | NA | SGL |
| jx_rep_136 | count_of_image | 1 | 3 |
| jx_rep_136 | img_layout | SGL | TD |
| jx_rep_151 | has_image | N | Y |
| jx_rep_151 | count_of_image | 0 | 1 |
| jx_rep_151 | img_layout | NA | SGL |
| jx_rep_156 | count_of_image | 1 | 3 |
| jx_rep_156 | img_layout | SGL | TD |
| jx_rep_157 | count_of_image | 2 | 1 |
| jx_rep_157 | img_layout | TD | SGL |
| jx_rep_160 | count_of_image | 2 | 1 |
| jx_rep_160 | img_layout | TD | SGL |
| jx_rep_165 | has_image | N | Y |
| jx_rep_165 | count_of_image | 0 | 1 |
| jx_rep_165 | img_layout | NA | SGL |
| jx_rep_166 | has_image | N | Y |
| jx_rep_166 | count_of_image | 0 | 1 |
| jx_rep_166 | img_layout | NA | SGL |
| jx_rep_174 | count_of_image | 2 | 1 |
| jx_rep_174 | img_layout | TD | SGL |
| jx_rep_176 | count_of_image | 1 | 4 |
| jx_rep_176 | img_layout | SGL | TD |
| jx_rep_186 | count_of_image | 2 | 3 |
| jx_rep_186 | img_layout | LR | TD |
| jx_rep_191 | has_image | N | Y |
| jx_rep_191 | count_of_image | 0 | 1 |
| jx_rep_191 | img_layout | NA | SGL |
| jx_rep_192 | has_image | N | Y |
| jx_rep_192 | count_of_image | 0 | 1 |
| jx_rep_192 | img_layout | NA | SGL |
| jx_rep_193 | has_image | N | Y |
| jx_rep_193 | count_of_image | 0 | 1 |
| jx_rep_193 | img_layout | NA | SGL |
| jx_rep_195 | has_image | N | Y |
| jx_rep_195 | count_of_image | 0 | 1 |
| jx_rep_195 | img_layout | NA | SGL |
| jx_rep_196 | has_image | N | Y |
| jx_rep_196 | count_of_image | 0 | 1 |
| jx_rep_196 | img_layout | NA | SGL |
| jx_rep_290 | count_of_image | 1 | 2 |
| jx_rep_290 | img_layout | SGL | LR |
| jx_rep_294 | count_of_image | 1 | 2 |
| jx_rep_294 | img_layout | SGL | TD |
| jx_rep_298 | has_image | N | Y |
| jx_rep_298 | count_of_image | 0 | 1 |
| jx_rep_298 | img_layout | NA | SGL |
| jx_rep_299 | has_image | N | Y |
| jx_rep_299 | count_of_image | 0 | 1 |
| jx_rep_299 | img_layout | NA | SGL |
| jx_rep_308 | count_of_image | 2 | 1 |
| jx_rep_308 | img_layout | TD | SGL |
| jx_rep_309 | count_of_image | 1 | 2 |
| jx_rep_309 | img_layout | SGL | TD |
| jx_rep_311 | img_layout | LR | TD |
| jx_rep_313 | count_of_image | 3 | 2 |
| jx_rep_321 | count_of_image | 1 | 2 |
| jx_rep_321 | img_layout | SGL | LR |
| jx_rep_400 | has_image | Y | N |
| jx_rep_400 | count_of_image | 1 | 0 |
| jx_rep_400 | img_layout | SGL | NA |
| jx_rep_401 | has_image | N | Y |
| jx_rep_401 | count_of_image | 0 | 5 |
| jx_rep_401 | img_layout | NA | TD |
| jx_rep_411 | count_of_image | 1 | 4 |
| jx_rep_411 | img_layout | SGL | LR |
| jx_rep_415 | has_image | N | Y |
| jx_rep_415 | count_of_image | 0 | 3 |
| jx_rep_415 | img_layout | NA | TD |
| jx_rep_435 | count_of_image | 1 | 2 |
| jx_rep_435 | img_layout | SGL | TD |
| jx_rep_459 | has_image | N | Y |
| jx_rep_459 | count_of_image | 0 | 1 |
| jx_rep_459 | img_layout | NA | SGL |
| jx_rep_462 | count_of_image | 1 | 2 |
| jx_rep_462 | img_layout | SGL | TD |

### sec_cq
- Comparable pages: 158
- Full row agreement: 141/158 (89.2%)
- Errors: Qwen-VL-Plus (v1 prompt)=2, Qwen3-VL-Flash (v2 prompt)=2

| Field | Agreement |
|-------|-----------|
| has_image | 144/158 (91.1%) |
| has_text | 157/158 (99.4%) |
| count_of_image | 142/158 (89.9%) |
| img_layout | 142/158 (89.9%) |

**Disagreements (47)**:

| Page | Field | Qwen-VL-Plus (v1 prompt) | Qwen3-VL-Flash (v2 prompt) |
|------|-------|--------|-----------|
| sec_cq_1 | has_image | N | Y |
| sec_cq_1 | count_of_image | 0 | 1 |
| sec_cq_1 | img_layout | NA | SGL |
| sec_cq_4 | has_image | N | Y |
| sec_cq_4 | count_of_image | 0 | 1 |
| sec_cq_4 | img_layout | NA | SGL |
| sec_cq_6 | has_image | N | Y |
| sec_cq_6 | count_of_image | 0 | 1 |
| sec_cq_6 | img_layout | NA | SGL |
| sec_cq_15 | has_image | N | Y |
| sec_cq_15 | count_of_image | 0 | 1 |
| sec_cq_15 | img_layout | NA | SGL |
| sec_cq_16 | has_image | N | Y |
| sec_cq_16 | count_of_image | 0 | 1 |
| sec_cq_16 | img_layout | NA | SGL |
| sec_cq_21 | has_image | N | Y |
| sec_cq_21 | count_of_image | 0 | 1 |
| sec_cq_21 | img_layout | NA | SGL |
| sec_cq_35 | has_image | N | Y |
| sec_cq_35 | count_of_image | 0 | 1 |
| sec_cq_35 | img_layout | NA | SGL |
| sec_cq_42 | has_image | N | Y |
| sec_cq_42 | count_of_image | 0 | 1 |
| sec_cq_42 | img_layout | NA | SGL |
| sec_cq_43 | has_image | N | Y |
| sec_cq_43 | count_of_image | 0 | 1 |
| sec_cq_43 | img_layout | NA | SGL |
| sec_cq_44 | has_image | N | Y |
| sec_cq_44 | count_of_image | 0 | 1 |
| sec_cq_44 | img_layout | NA | SGL |
| sec_cq_45 | has_image | N | Y |
| sec_cq_45 | count_of_image | 0 | 1 |
| sec_cq_45 | img_layout | NA | SGL |
| sec_cq_46 | has_image | N | Y |
| sec_cq_46 | count_of_image | 0 | 1 |
| sec_cq_46 | img_layout | NA | SGL |
| sec_cq_47 | has_image | N | Y |
| sec_cq_47 | count_of_image | 0 | 1 |
| sec_cq_47 | img_layout | NA | SGL |
| sec_cq_48 | has_image | N | Y |
| sec_cq_48 | count_of_image | 0 | 1 |
| sec_cq_48 | img_layout | NA | SGL |
| sec_cq_139 | count_of_image | 2 | 1 |
| sec_cq_139 | img_layout | TD | SGL |
| sec_cq_159 | count_of_image | 2 | 1 |
| sec_cq_159 | img_layout | TD | SGL |
| sec_cq_160 | has_text | N | Y |

### slgf_mt
- Comparable pages: 130
- Full row agreement: 125/130 (96.2%)
- Errors: Qwen-VL-Plus (v1 prompt)=2, Qwen3-VL-Flash (v2 prompt)=2

| Field | Agreement |
|-------|-----------|
| has_image | 127/130 (97.7%) |
| has_text | 130/130 (100.0%) |
| count_of_image | 125/130 (96.2%) |
| img_layout | 125/130 (96.2%) |

**Disagreements (13)**:

| Page | Field | Qwen-VL-Plus (v1 prompt) | Qwen3-VL-Flash (v2 prompt) |
|------|-------|--------|-----------|
| slgf_mt_5 | has_image | N | Y |
| slgf_mt_5 | count_of_image | 0 | 2 |
| slgf_mt_5 | img_layout | NA | TD |
| slgf_mt_55 | count_of_image | 1 | 2 |
| slgf_mt_55 | img_layout | SGL | LR |
| slgf_mt_69 | count_of_image | 1 | 2 |
| slgf_mt_69 | img_layout | SGL | TD |
| slgf_mt_127 | has_image | N | Y |
| slgf_mt_127 | count_of_image | 0 | 2 |
| slgf_mt_127 | img_layout | NA | TD |
| slgf_mt_131 | has_image | N | Y |
| slgf_mt_131 | count_of_image | 0 | 1 |
| slgf_mt_131 | img_layout | NA | SGL |

### slgf_qc
- Comparable pages: 104
- Full row agreement: 100/104 (96.2%)
- Errors: Qwen-VL-Plus (v1 prompt)=0, Qwen3-VL-Flash (v2 prompt)=0

| Field | Agreement |
|-------|-----------|
| has_image | 103/104 (99.0%) |
| has_text | 103/104 (99.0%) |
| count_of_image | 101/104 (97.1%) |
| img_layout | 102/104 (98.1%) |

**Disagreements (7)**:

| Page | Field | Qwen-VL-Plus (v1 prompt) | Qwen3-VL-Flash (v2 prompt) |
|------|-------|--------|-----------|
| slgf_qc_6 | has_text | N | Y |
| slgf_qc_11 | has_image | N | Y |
| slgf_qc_11 | count_of_image | 0 | 2 |
| slgf_qc_11 | img_layout | NA | TD |
| slgf_qc_25 | count_of_image | 1 | 3 |
| slgf_qc_25 | img_layout | SGL | TD |
| slgf_qc_51 | count_of_image | 3 | 4 |
