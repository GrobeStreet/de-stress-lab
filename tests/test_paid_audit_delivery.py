from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "send_paid_audit_delivery.py"
SPEC = importlib.util.spec_from_file_location("send_paid_audit_delivery", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_builds_only_the_bounded_delivery_package(tmp_path: Path) -> None:
    for name in (
        "audit.md",
        "delivery-manifest.json",
        "execution.md",
        "scope.md",
    ):
        (tmp_path / name).write_text("evidence", encoding="utf-8")
    (tmp_path / "unrelated-secret.txt").write_text("private", encoding="utf-8")

    payload = MODULE.build_payload(
        tmp_path,
        "https://github.com/example/research-code",
        "0123456789abcdefabcd",
    )

    names = {file["name"] for file in payload["files"]}
    assert names == {
        "audit.md",
        "delivery-manifest.json",
        "execution.md",
        "scope.md",
    }
    assert "unrelated-secret.txt" not in names


def test_rejects_an_incomplete_delivery_package(tmp_path: Path) -> None:
    (tmp_path / "scope.md").write_text("scope", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required records"):
        MODULE.build_payload(
            tmp_path,
            "https://github.com/example/research-code",
            "0123456789abcdefabcd",
        )
