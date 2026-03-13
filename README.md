# VLM-Enhanced Martial Arts Dataset

Digital humanities research project: structured data extraction from
historical Chinese martial arts texts using Vision Language Models.

## Project Structure
```
scripts/
  step1/step1_metadata.py     -- Wikidata metadata acquisition
  step2/step2_preprocess.py   -- PDF scan preprocessing
data/
  booklist_template.csv        -- book list (14 texts)
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
