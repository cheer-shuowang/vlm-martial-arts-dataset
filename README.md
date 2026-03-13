# VLM-Enhanced Martial Arts Dataset



## Project Structure
```
scripts/
  step1/step1_metadata.py     -- Wikidata metadata acquisition
  step2/step2_preprocess.py   -- PDF scan preprocessing
data/
  booklist_template.csv        -- book list 
  known_qids.json              -- confirmed Wikidata QIDs
  pdf_mapping.json             -- bookID to PDF filename mapping
```

## Dependencies
```bash
pip install requests openpyxl pymupdf Pillow numpy
```

## Step 1: Metadata Acquisition
```bash
python scripts/step1/step1_metadata.py data/booklist_template.csv --known-qids data/known_qids.json
```

## Step 2: Image Preprocessing
```bash
python scripts/step2/step2_preprocess.py path/to/file.pdf --book-id gy_mg
```
