from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOFTWARE_DOI = "10.5281/zenodo.21633731"
SCIENTIFIC_DOI = "10.5281/zenodo.21632602"
VERSION = "0.1.1"
JOSS_REQUIRED_SECTIONS = (
    "# Summary",
    "# Statement of need",
    "# State of the field",
    "# Software design",
    "# Research impact statement",
    "# AI usage disclosure",
    "# Acknowledgements",
    "# References",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_package_version_is_consistent() -> None:
    pyproject = read("pyproject.toml")
    citation = read("CITATION.cff")
    package_init = read("src/destress/__init__.py")
    zenodo = json.loads(read(".zenodo.json"))
    release = json.loads(read("archive/SOFTWARE_RELEASE_0.1.1.json"))

    assert re.search(r'^version = "0\.1\.1"$', pyproject, re.MULTILINE)
    assert re.search(r'^version: 0\.1\.1$', citation, re.MULTILINE)
    assert f'__version__ = "{VERSION}"' in package_init
    assert zenodo["version"] == VERSION
    assert release["version"] == VERSION


def test_reusable_software_doi_is_canonical_for_package() -> None:
    # .zenodo.json describes a future deposition and intentionally does not
    # hard-code a DOI minted by the repository service. The already-minted DOI
    # belongs in citation, documentation, package URLs, and preservation records.
    paths = [
        "README.md",
        "CITATION.cff",
        "pyproject.toml",
        "paper/paper.md",
        "paper/paper.bib",
        "paper/JOSS-READINESS.md",
        "paper/SUBMISSION_ROADMAP.md",
        "archive/SOFTWARE_RELEASE_0.1.1.json",
    ]
    for path in paths:
        assert SOFTWARE_DOI in read(path), f"software DOI missing from {path}"


def test_scientific_archive_remains_separate_and_citable() -> None:
    release = json.loads(read("archive/SOFTWARE_RELEASE_0.1.1.json"))
    canonical = json.loads(read("archive/CANONICAL_RELEASE.json"))

    assert release["doi"] == SOFTWARE_DOI
    assert release["related_scientific_archive"]["version_doi"] == SCIENTIFIC_DOI
    assert canonical["doi"]["version_doi"] == SCIENTIFIC_DOI
    assert SOFTWARE_DOI != SCIENTIFIC_DOI
    assert SCIENTIFIC_DOI in read("README.md")
    assert SCIENTIFIC_DOI in read("CITATION.cff")


def test_zenodo_metadata_targets_reusable_release() -> None:
    zenodo = json.loads(read(".zenodo.json"))
    assert zenodo["upload_type"] == "software"
    assert zenodo["publication_date"] == "2026-07-29"
    assert "reusable scientific likelihood stress-testing toolkit" in zenodo["title"]
    related = {item["identifier"] for item in zenodo["related_identifiers"]}
    assert SCIENTIFIC_DOI in related


def test_joss_submission_bundle_tracks_current_required_sections() -> None:
    paper = read("paper/paper.md")
    for section in JOSS_REQUIRED_SECTIONS:
        assert section in paper, f"JOSS paper is missing {section}"
    assert "OpenAI ChatGPT" in paper
    assert "human author reviewed" in paper


def test_joss_readiness_does_not_overstate_eligibility() -> None:
    readiness = read("paper/JOSS-READINESS.md")
    normalized = " ".join(readiness.split())
    assert "not yet eligible for JOSS screening" in normalized
    assert "2027-01-22" in readiness
    assert "independent installation by another researcher" in readiness
    assert "evidence of use beyond the original flagship analysis" in readiness


def test_open_source_maintenance_documents_are_present() -> None:
    for path in (
        "CHANGELOG.md",
        "GOVERNANCE.md",
        "CONTRIBUTING.md",
        "SUPPORT.md",
        "CODE_OF_CONDUCT.md",
        "paper/REVIEW_CHECKLIST.md",
    ):
        assert (ROOT / path).is_file(), f"missing maintenance document: {path}"
