# VLM-Enhanced Martial Arts Dataset

## Project Structure
```
scripts/
  step1_metadata.py          -- Step 1: Wikidata metadata acquisition
  step2_preprocess.py        -- Step 2: PDF scan preprocessing (crop, split, resize)
  split_pdf.py               -- Step 2 alt: Simple center-split for double-page PDFs
  step3_index.py             -- Step 3: Page-level indexing (Qwen-VL-Plus, v1 prompt)
  step3_index_v2.py          -- Step 3: Page-level indexing (Qwen3-VL-Flash, v2 prompt)
  step4_extract.py           -- Step 4: Image-level data extraction
  compare_models.py          -- Step 3 model comparison (generates markdown report)
  compare_step4.py           -- Step 4 model comparison (generates markdown report)

data/
  booklist_template.csv      -- Master book list (29 entries)
  known_qids.json            -- Confirmed Wikidata QIDs
  pdf_mapping.json           -- bookID → PDF filename mapping

pdfs/
  batch2/                    -- PDF scans (batch 2)

output/                      -- Step 2 output: preprocessed page images per book
  {bookID}/                  -- e.g. gzfh_ld/, slgf_mt/, ...
  jx_mg_flat/                -- Flattened symlinks for multi-volume jx_mg
  errors_step4/              -- Batch 1 error page images
  errors_step4_batch2/       -- Batch 2 error page images

index/
  Qwen-VL-Plus/              -- Step 3 baseline results (Qwen-VL-Plus, v1 prompt)
    {bookID}_index.csv
  Qwen3-VL-Flash/
    Branch_1/                -- Step 3 batch 1 results (Qwen3-VL-Flash, v2 prompt)
      {bookID}_index_qwen3flash_v2.csv
    {bookID}_index_qwen3flash_v2.csv  -- Step 3 batch 2 results

extraction/
  Branch1/                   -- Step 4 batch 1 results
    {bookID}_step4.jsonl
  {bookID}_step4.jsonl       -- Step 4 batch 2 results

metadata/                    -- Step 1 output

docs/
  Phase1-mar10.docx          -- Task brief
  Prompt Documentation.md    -- VLM prompts, parameters, and test results
  model_comparison_report.md -- Step 3 model comparison (Qwen-VL-Plus vs Qwen3-VL-Flash)
  step4_comparison.md        -- Step 4 model comparison (summary)
  step4_comparison_full.md   -- Step 4 model comparison (full details)
```

## Processing Pipeline

### Step 1: Metadata Acquisition
Query Wikidata for bibliographic metadata of each book.
```bash
python scripts/step1_metadata.py data/booklist_template.csv --known-qids data/known_qids.json
```

### Step 2: Image Preprocessing
Convert PDF scans into individual page images (crop, split, resize to 800px height).
```bash
# Full preprocessing pipeline
python scripts/step2_preprocess.py path/to/file.pdf --book-id gy_mg

# Simple center-split for double-page scans
python scripts/split_pdf.py path/to/file.pdf --book-id zggyjf
```

### Step 3: Page-Level Indexing
Classify each page image using VLM (has_image, has_text, count_of_image, img_layout).
```bash
python scripts/step3_index_v2.py ./output/gy_mg/ --book-id gy_mg --model qwen3-vl-flash \
  -o ./index/Qwen3-VL-Flash/gy_mg_index_qwen3flash_v2.csv
```

### Step 4: Image-Level Data Extraction
Extract detailed information from pages with illustrations (original_text, count_person, count_weapon, type_weapons, posture, tactic).
```bash
python scripts/step4_extract.py ./output/gy_mg/ --book-id gy_mg \
  --index ./index/Qwen3-VL-Flash/gy_mg_index_qwen3flash_v2.csv \
  --model qwen3-vl-flash -o ./extraction/gy_mg_step4.jsonl
```

## Progress

### Batch 1 (14 books) — Completed
| # | bookID | Title | Step 3 | Step 4 |
|---|--------|-------|--------|--------|
| 01 | gzfh_ld | 工字伏虎拳 | ✅ | ✅ |
| 02 | slgf_qc | 少林棍法阐宗 (清抄) | ✅ | ✅ |
| 04 | jx_rep | 纪效新书 (民国) | ✅ | ✅ |
| 05 | jx_mg | 纪效新书 (18卷) | ✅ | ✅ |
| 06 | sec_cq | 三十二势长拳 | ✅ | ✅ |
| 07 | gy_mg | 耕余剩技 | ✅ | ✅ |
| 09 | sbl_v2 | 手臂录 (v2) | ✅ | ✅ |
| 10 | wbz_mg | 武备志 (卷85-93) | ✅ | ✅ |
| 11 | bl_mg | 兵录 | ✅ | ✅ |
| 12 | yjj_qm | 易筋经外经图说 | ✅ | ✅ |
| 13 | bdj_qm | 八段锦册 | ✅ | ✅ |
| 14 | slgf_mt | 少林棍法秘传 | ✅ | ✅ |

### Batch 2 (14 books) — Completed
| # | bookID | Title | Step 3 | Step 4 |
|---|--------|-------|--------|--------|
| 15 | hhsx_v1 | 虎鹤双形拳 | ✅ | ✅ |
| 16 | cswj_v1 | 苌氏武技书 | ✅ | ✅ |
| 17 | qigqj_m | 戚继光拳经 | ✅ | ✅ |
| 18 | syl_v3 | 手臂录 (v3) | ✅ | ✅ |
| 19 | qjqf_tyl | 拳经拳法备要 | ✅ | ✅ |
| 20 | wytp_nk | 武艺图谱通志 | ✅ | ✅ |
| 21 | jxxs_tw | 纪效新书 (台湾) | ✅ | ✅ |
| 22 | cqs_q | 长枪式图说 | ✅ | ✅ |
| 23 | mcgp_m | 麻杈棍谱 | ✅ | ✅ |
| 24 | zggyjf | 中国古佚剑法 | ✅ | ✅ |
| 25 | bjzz_q | 兵技指掌图说 | ✅ | ✅ |
| 27 | tbbb_part2 | 太白兵备统宗宝鉴 vol97-184 | ✅ | ✅ |
| 28 | cztjj_m | 剿贼图记 | ✅ | ✅ |
| 29 | clf_xmhq | 蔡李佛小梅花拳 | ✅ | ✅ |

### Skipped
| # | bookID | Reason |
|---|--------|--------|
| 03 | slgf_lres | Low-res duplicate of slgf_qc |
| 08 | sbl_v1 | Duplicate (v1 of 手臂录) |
| 26 | tbbb_part1 | Pending |

## Models Used
- **Step 3 baseline**: Qwen-VL-Plus (v1 prompt)
- **Step 3 & 4 production**: Qwen3-VL-Flash (v2 prompt)

## Dependencies
```bash
pip install requests openpyxl pymupdf Pillow numpy
```
