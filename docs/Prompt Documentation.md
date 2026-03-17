# VLM Prompt Documentation

## Overview
This document records the VLM models, prompts, and parameters used in each processing step, along with observations and modifications.

---

## Step 3: Page-Level Indexing

### Model
- **Model**: Qwen-VL-Plus (qwen-vl-plus)
- **Provider**: Alibaba DashScope API
- **Endpoint**: https://modelstudio.console.aliyun.com/ap-southeast-1/?tab=dashboard#/efm/model_experience_center/text
- **API format**: OpenAI-compatible

### Parameters
- temperature: 0.1
- max_tokens: 256

### Prompt (v1.0)
Used since: 2026-03-16

```
You are analyzing a scanned page from a historical Chinese martial arts text.

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
- Respond with ONLY the JSON object. No markdown, no explanation.
```

### Post-processing Rules
The script applies the following consistency checks after receiving the VLM response:
- If has_image = N, force count_of_image = 0 and img_layout = NA
- If count_of_image = 0, force has_image = N and img_layout = NA
- If count_of_image = 1 and layout is not sgl, correct to sgl
- If count_of_image > 1 and layout is sgl, default to td

### Test Results

#### Test 1: slgf_mt (132 pages, full book)
- Date: 2026-03-17
- Pages tested: 132
- Results summary:
  - Pages with illustrations: 90 (68%)
  - Text-only pages: 40 (30%)
  - API errors: 2 (1.5%)
  - Layout distribution: sgl=87, td=1, lr=2, NA=40
- Observations:
  - Majority of illustrated pages correctly identified as single-image (sgl)
  - 2 pages with left-right layout detected (slgf_mt_117, slgf_mt_118)
  - 2 API error on slgf_mt_3 (HTTP 400) -- The system is blocking the request because it suspects the input contains "inappropriate content."-probably because of ‘中华民国’ in the two pages
- Accuracy: TBD (manual verification in progress)
- Cost estimate: ~132 API calls, within free tier

### Prompt Modification Log

| Date | Version | Change | Reason |
|------|---------|--------|--------|
| 2026-03-16 | v1.0 | Initial prompt | -- |

---

## Step 4: Image-Level Data Extraction

### Model
- **Model**: TBD (testing with Qwen-VL-Plus first)

### Prompt
- TBD (to be developed after Step 3 validation is complete)

### Test Plan
- ~200 pages of handwritten text + ~200 pages of printed text
- Evaluate across multiple books before deciding on final model

---

## Notes
- Scripts are version-controlled at: https://github.com/cheer-shuowang/vlm-martial-arts-dataset

