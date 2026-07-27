#!/usr/bin/env python3
"""Prepare the non-customer delivery metadata for a paid static audit."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def repository_commit(target: Path) -> str:
    """Return the frozen target commit without executing target code."""
    try:
        return subprocess.check_output(
            ["git", "-C", str(target), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def prepare_delivery(
    output: Path,
    target: Path,
    repository: str,
    order_reference: str,
) -> None:
    """Write bounded scope, execution, and manifest records."""
    output.mkdir(parents=True, exist_ok=True)
    commit = repository_commit(target)

    scope = f"""# Audit scope

- Order reference: `{order_reference}`
- Repository: {repository}
- Audited commit: `{commit}`
- Execution: not attempted

This automated stage performs structural inspection only. It does not execute
customer code, numerically reproduce a claim, or certify scientific validity.
"""
    (output / "scope.md").write_text(scope, encoding="utf-8")

    execution = """# Execution record

Customer code was not executed automatically. Installation and test smoke
checks remain behind the published safety gate and require isolated review.
"""
    (output / "execution.md").write_text(execution, encoding="utf-8")

    manifest = {
        "schema_version": 1,
        "order_reference": order_reference,
        "repository": repository,
        "commit": commit,
        "static_audit": (output / "audit.json").exists(),
        "customer_code_executed": False,
    }
    (output / "delivery-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--order-reference", required=True)
    args = parser.parse_args()
    prepare_delivery(
        args.output,
        args.target,
        args.repository,
        args.order_reference,
    )


if __name__ == "__main__":
    main()
