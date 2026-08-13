#!/usr/bin/env python3
"""Build the evidence-reconciled manuscript as a self-contained REVTeX source."""

from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "whitepaper.md"
OUTDIR = ROOT / "preprint"
TEX = OUTDIR / "manuscript.tex"
PDF = OUTDIR / "manuscript.pdf"


def normalize_scientific_tex(markdown: str) -> str:
    replacements = (
        ("3×10⁻⁷", r"$3\times 10^{-7}$"),
        ("Δχ²_MAP", r"$\Delta\chi^2_{\mathrm{MAP}}$"),
        ("Δχ²", r"$\Delta\chi^2$"),
        ("χ²_min", r"$\chi^2_{\min}$"),
        ("χ²", r"$\chi^2$"),
        ("w₀–wₐ", r"$w_0$--$w_a$"),
        ("w₀+wₐ", r"$w_0+w_a$"),
        ("w₀wₐCDM", r"$w_0w_a$CDM"),
        ("w₀", r"$w_0$"),
        ("wₐ", r"$w_a$"),
        ("fσ₈", r"$f\sigma_8$"),
        ("Ωm", r"$\Omega_m$"),
        ("θ*", r"$\theta_*$"),
        ("ΛCDM", r"$\Lambda$CDM"),
        ("S₈", r"$S_8$"),
        ("ℓ", r"$\ell$"),
        ("σ", r"$\sigma$"),
        ("α", r"$\alpha$"),
        ("≈", "approximately"),
        ("≤", r"$\leq$"),
        ("≡", r"$\equiv$"),
        ("∈", r"$\in$"),
        ("±", r"$\pm$"),
        ("→", r"$\rightarrow$"),
        ("×", r"$\times$"),
        ("−", "-"),
    )
    for old, new in replacements:
        markdown = markdown.replace(old, new)
    return markdown


def tables_to_lists(markdown: str) -> str:
    lines = markdown.splitlines()
    output: list[str] = []
    index = 0
    while index < len(lines):
        if not lines[index].lstrip().startswith("|"):
            output.append(lines[index])
            index += 1
            continue
        block: list[str] = []
        while index < len(lines) and lines[index].lstrip().startswith("|"):
            block.append(lines[index].strip())
            index += 1
        rows = [
            [cell.strip() for cell in row.strip("|").split("|")]
            for row in block
            if not all(set(cell.strip()) <= {"-", ":"} for cell in row.strip("|").split("|"))
        ]
        if len(rows) < 2:
            output.extend(block)
            continue
        headers = rows[0]
        for row in rows[1:]:
            details = []
            for column, cell in enumerate(row[1:], start=1):
                label = headers[column] if column < len(headers) else f"Column {column + 1}"
                details.append(f"**{label}:** {cell}")
            output.append(f"- **{row[0]}:** " + "; ".join(details))
        output.append("")
    return "\n".join(output)


def pandoc_fragment(markdown: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8") as handle:
        handle.write(markdown)
        handle.flush()
        return subprocess.run(
            ["pandoc", handle.name, "--from=gfm", "--to=latex", "--shift-heading-level-by=-1", "--ascii"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    marker = "## 1. Motivation and scope"
    start = text.index("## Abstract") + len("## Abstract")
    split = text.index(marker)
    abstract = (OUTDIR / "ABSTRACT.md").read_text(encoding="utf-8").strip()
    body = text[split:].strip()
    appendix = body.find("## Appendix A.")
    if appendix != -1:
        body = body[:appendix].rstrip()
    reproduction_start = body.index("Everything runs from the released directory.")
    reproduction_end = body.index("\n\n## Acknowledgments", reproduction_start)
    body = (
        body[:reproduction_start]
        + "The blind reproduction protocol and one-command runners are documented in "
        + "cleanroom/README.md. Released outputs are in results/; canonical values, "
        + "completion states, and checksums are in RESULTS_MANIFEST.json."
        + body[reproduction_end:]
    )
    body = re.sub(r"(?m)^## \d+[a-z]?\.\s+", "## ", body)
    abstract = normalize_scientific_tex(abstract)
    body = normalize_scientific_tex(tables_to_lists(body))
    abstract_tex = pandoc_fragment(abstract)
    body_tex = pandoc_fragment(body)

    preamble = r"""\documentclass[aps,prd,preprint,superscriptaddress,nofootinbib]{revtex4-2}
\usepackage{amsmath,amssymb}
\usepackage{booktabs,array}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage{xurl}
\usepackage{textcomp}
\usepackage{etoolbox}
\setlength{\emergencystretch}{3em}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\hypersetup{hidelinks,pdftitle={Anatomy of a 2--3 Sigma Hint},pdfauthor={Robert Morong}}
\begin{document}
\title{Anatomy of a 2--3$\sigma$ Hint}
\author{Robert Morong}
\affiliation{Independent researcher, San Diego, California, USA}
\date{August 2026}
\begin{abstract}
"""
    ending = r"""
\section*{Data Availability}
The released code, download instructions, result files, chains, and registered hypothesis records are available at \url{https://github.com/GrobeStreet/de-stress-lab}. The immutable flagship scientific archive is \href{https://doi.org/10.5281/zenodo.21632602}{doi:10.5281/zenodo.21632602}. The canonical completion states and checksums are recorded in \texttt{RESULTS\_MANIFEST.json}. A human clean-room execution remains pending.

\section*{Conflict of Interest}
The author declares no competing financial interests.

\end{document}
"""
    OUTDIR.mkdir(parents=True, exist_ok=True)
    TEX.write_text(preamble + abstract_tex + "\\end{abstract}\n\\maketitle\n\\sloppy\n\n" + body_tex + ending, encoding="utf-8")
    subprocess.run(["tectonic", "--keep-logs", "--outdir", str(OUTDIR), str(TEX)], check=True)
    if not PDF.exists() or PDF.stat().st_size == 0:
        raise RuntimeError("preprint PDF was not produced")
    print(f"built {TEX.relative_to(ROOT)}")
    print(f"built {PDF.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
