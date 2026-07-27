"""Command-line interface for lightweight verification and examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import __version__
from .repo_audit import audit_repository


def _demo() -> int:
    from .cosmology import CPLCosmology
    from .datasets import DESI_DR2_BAO

    cosmology = CPLCosmology(omega_m=0.2973, h=0.68)
    chi2 = DESI_DR2_BAO.chi2(cosmology, sound_horizon=101.55 / 0.68)
    print(
        json.dumps(
            {
                "package_version": __version__,
                "dataset": DESI_DR2_BAO.name,
                "model": "flat LambdaCDM",
                "omega_m": cosmology.omega_m,
                "h": cosmology.h,
                "h_times_rd_mpc": 101.55,
                "bao_chi2": chi2,
            },
            indent=2,
        )
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="destress")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("demo", help="evaluate the bundled DESI DR2 BAO example")
    verify = commands.add_parser("verify-ledger", help="verify a frozen JSON ledger")
    verify.add_argument("path", type=Path)
    audit = commands.add_parser(
        "audit-repo", help="score a repository's reproducibility readiness"
    )
    audit.add_argument("path", nargs="?", type=Path, default=Path("."))
    audit.add_argument("--json-output", type=Path)
    audit.add_argument("--markdown-output", type=Path)
    audit.add_argument("--minimum-score", type=int, default=0)
    audit.add_argument("--github-output", type=Path)
    audit.add_argument("--github-summary", type=Path)
    audit.add_argument("--github-repository")
    audit.add_argument(
        "--workflow-file", default="reproducibility-audit.yml"
    )
    args = parser.parse_args(argv)
    if args.command == "demo":
        return _demo()
    if args.command == "audit-repo":
        if not 0 <= args.minimum_score <= 100:
            parser.error("--minimum-score must be between 0 and 100")
        report = audit_repository(args.path)
        rendered_json = report.to_json()
        rendered_markdown = report.to_markdown()
        if args.json_output:
            args.json_output.write_text(rendered_json, encoding="utf-8")
        if args.markdown_output:
            args.markdown_output.write_text(rendered_markdown, encoding="utf-8")
        if args.github_summary:
            with args.github_summary.open("a", encoding="utf-8") as handle:
                handle.write(rendered_markdown)
        badge_url = report.score_badge_url()
        status_badge = ""
        if args.github_repository:
            workflow_url = (
                f"https://github.com/{args.github_repository}/actions/workflows/"
                f"{args.workflow_file}"
            )
            status_badge = (
                f"[![Reproducibility audit]({workflow_url}/badge.svg)]"
                f"({workflow_url})"
            )
        if args.github_output:
            with args.github_output.open("a", encoding="utf-8") as handle:
                handle.write(f"score={report.score}\n")
                handle.write(f"grade={report.grade}\n")
                handle.write(f"score_badge_url={badge_url}\n")
                handle.write(f"status_badge_markdown={status_badge}\n")
        print(rendered_markdown, end="")
        if report.score < args.minimum_score:
            print(
                f"readiness score {report.score} is below required "
                f"{args.minimum_score}"
            )
            return 1
        return 0
    from .stress import verify_frozen_json

    digest = verify_frozen_json(args.path)
    print(f"verified {args.path}: sha256:{digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
