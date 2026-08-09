#!/usr/bin/env python3
"""Build and validate the minimal arXiv source archive without submitting it."""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "preprint" / "manuscript.tex"
OUTDIR = ROOT / "submission" / "arxiv"
ARCHIVE = OUTDIR / "arxiv-source.zip"
CHECKSUMS = OUTDIR / "SHA256SUMS"
ALLOWED_NAME = re.compile(r"^[A-Za-z0-9_+.,=-]+$")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if not SOURCE.exists():
        raise FileNotFoundError("preprint/manuscript.tex is missing; run build_preprint.py first")
    if not ALLOWED_NAME.fullmatch(SOURCE.name):
        raise ValueError(f"arXiv-incompatible source filename: {SOURCE.name}")

    text = SOURCE.read_text(encoding="utf-8")
    if "\\documentclass" not in text or "\\end{document}" not in text:
        raise ValueError("source is not a complete top-level TeX document")
    if re.search(r"\\(?:input|include|includegraphics|bibliography)\s*\{", text):
        raise ValueError("source references external files; package them explicitly")

    with tempfile.TemporaryDirectory(prefix="desi-arxiv-") as tmp_name:
        tmp = Path(tmp_name)
        isolated = tmp / SOURCE.name
        shutil.copy2(SOURCE, isolated)
        subprocess.run(
            ["tectonic", "--keep-logs", "--outdir", str(tmp), str(isolated)],
            check=True,
            capture_output=True,
            text=True,
        )
        rendered = tmp / "manuscript.pdf"
        if not rendered.exists() or rendered.stat().st_size == 0:
            raise RuntimeError("isolated arXiv source did not compile")
        log = (tmp / "manuscript.log").read_text(encoding="utf-8", errors="replace")
        bad = [line for line in log.splitlines() if "Missing character" in line or "Overfull" in line]
        if bad:
            raise RuntimeError("TeX diagnostics failed:\n" + "\n".join(bad))

    OUTDIR.mkdir(parents=True, exist_ok=True)
    info = zipfile.ZipInfo(SOURCE.name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    with zipfile.ZipFile(ARCHIVE, "w") as bundle:
        bundle.writestr(info, SOURCE.read_bytes())

    with zipfile.ZipFile(ARCHIVE) as bundle:
        names = bundle.namelist()
        if names != ["manuscript.tex"] or bundle.testzip() is not None:
            raise RuntimeError(f"unexpected archive contents: {names}")

    CHECKSUMS.write_text(
        f"{digest(SOURCE)}  preprint/manuscript.tex\n"
        f"{digest(ARCHIVE)}  submission/arxiv/arxiv-source.zip\n",
        encoding="utf-8",
    )
    print(f"validated isolated source: {SOURCE.relative_to(ROOT)}")
    print(f"built {ARCHIVE.relative_to(ROOT)}")
    print(f"wrote {CHECKSUMS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
