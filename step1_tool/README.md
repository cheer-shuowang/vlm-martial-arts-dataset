# Step 1 Automation Tool: Book-level Metadata Acquisition

## Overview
This script reads a CSV book list, batch-queries the Wikidata API, and produces
a standardised Excel spreadsheet with all metadata fields required by the task brief.

## Files
```
step1_tool/
  step1_metadata.py      -- main script
  booklist_template.csv   -- CSV template (pre-filled with the 14-book list)
  known_qids.json         -- pre-confirmed Wikidata QIDs (editable)
  README.md               -- this file
```

## Quick Start

### 1. Install dependencies
```bash
pip install requests openpyxl
```

### 2. Prepare the CSV book list
Format (UTF-8 encoding):
```csv
Sequence,bookID,Reference_Title,Edition_Source
01,jx_mg,纪效新书 (18卷),明·戚继光撰
02,wbz_mg,武备志 (卷85-93),明·茅元仪辑
```
The provided `booklist_template.csv` already contains the 14 books from the
Annex 1 screenshot. Edit or extend it as needed.

### 3. Run the script
```bash
# Recommended: use --known-qids to skip searching for already-confirmed entries
python step1_metadata.py booklist_template.csv --known-qids known_qids.json

# Minimal usage
python step1_metadata.py booklist_template.csv

# Custom output path
python step1_metadata.py booklist_template.csv -o my_output.xlsx

# Increase API delay if rate-limited
python step1_metadata.py booklist_template.csv --delay 1.0
```

### 4. Review the output
The generated Excel file contains two sheets:

- **Step1_Book_Metadata** -- main data table with all required fields
- **Summary** -- statistics and next-step instructions

Status column values:
- `AUTO_MATCHED (Qxxxxx)` (green) -- Wikidata match found automatically
- `MANUAL_REQUIRED` (yellow) -- no match; manual verification needed

## Adding new books
1. Append new rows to the CSV
2. If you already know a book's Wikidata QID, add it to `known_qids.json`
3. Re-run the script

## Known limitations
- `cnt_volumes` (volume count) must be filled in manually; Wikidata rarely has it
- Some texts have no Wikidata entry (e.g. Shoubi Lu, Bing Lu)
- String-based matching may occasionally return false positives; always review
- Wikidata API is rate-limited; use `--delay 1.0` or higher for large batches
