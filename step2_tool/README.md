# Step 2: Image Pre-processing

## Overview
Convert PDF scans of historical texts into standardised individual page
images, ready for VLM analysis in Steps 3 and 4.

## Pipeline
1. **PDF to image** -- render each PDF page at a configurable DPI
2. **Crop calibration bar** -- auto-detect and remove the Tiffen colour
   strip (right edge) and dark background (left edge)
3. **Double-page split** -- detect the binding line and split two-page
   spreads into individual pages (right page first, matching traditional
   Chinese reading order)
4. **Sequential naming** -- `{bookID}_{pageNumber}.png`
5. **Resize** -- fixed height (default 800px), width scaled proportionally

## Files
```
step2_tool/
  step2_preprocess.py   -- core pipeline (single PDF)
  step2_batch.py        -- batch runner (multiple PDFs via CSV)
  README.md             -- this file
```

## Dependencies
```bash
pip install Pillow numpy
```
System requirement: `poppler-utils` (provides `pdftoppm`).
- macOS: `brew install poppler`
- Ubuntu/Debian: `sudo apt install poppler-utils`
- Windows: download from https://github.com/oschwartz10612/poppler-windows

Optional fallback: `pip install pdf2image`

## Usage

### Single PDF
```bash
# Split double pages, output at 800px height
python step2_preprocess.py input.pdf --book-id gy_mg

# No splitting (already single-page scans)
python step2_preprocess.py input.pdf --book-id jx_mg --no-split

# Custom height and DPI
python step2_preprocess.py input.pdf --book-id wbz_mg --height 1000 --dpi 400

# Start numbering from a specific page (for multi-volume books)
python step2_preprocess.py vol2.pdf --book-id syl_v2 --start-page 150
```

### Batch processing
```bash
python step2_batch.py booklist.csv --pdf-dir ./pdfs/
python step2_batch.py booklist.csv --pdf-dir ./pdfs/ --mapping pdf_mapping.json
```

If PDF filenames do not match bookIDs, create `pdf_mapping.json`:
```json
{
    "gy_mg": "GengYu_ShengJi_full.pdf",
    "jx_mg": "JiXiao_XinShu_18juan.pdf"
}
```

## Output structure
```
output/
  gy_mg/
    gy_mg_1.png
    gy_mg_2.png
    ...
  jx_mg/
    jx_mg_1.png
    ...
```

## Notes
- Double pages detected by aspect ratio (width > 1.1x height).
- Binding line found via darkest vertical column in the centre region.
- If binding detection fails, the image is split at the geometric centre.
- Use `--no-split` for single-page PDFs.
- The colour-bar cropping is tuned for Tiffen-style strips. Other setups
  may need threshold adjustments in `detect_right_bar()`.
- The script does not de-skew rotated pages. Pre-process with ImageMagick
  if needed: `convert -deskew 40% input.png output.png`
