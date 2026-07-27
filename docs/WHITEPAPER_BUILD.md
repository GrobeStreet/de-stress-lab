# Canonical whitepaper build

`whitepaper.md` is the editable source. `whitepaper.docx` and `whitepaper.pdf`
are generated artifacts.

## Dependencies

```bash
cd docs
npm install
cd ..
```

LibreOffice is required for the final DOCX-to-PDF conversion.

## Build

```bash
NODE_PATH=docs/node_modules node scripts/build_whitepaper_docx.js
python /path/to/soffice.py --headless --convert-to pdf --outdir . whitepaper.docx
```

Validate the DOCX before conversion and inspect every rendered PDF page before
release. The repository manifest records the canonical hashes.
