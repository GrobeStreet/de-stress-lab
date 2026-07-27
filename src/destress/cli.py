"""Command-line interface for lightweight verification and examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import __version__
from .cosmology import CPLCosmology
from .datasets import DESI_DR2_BAO
from .stress import verify_frozen_json


def _demo() -> int:
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
    args = parser.parse_args(argv)
    if args.command == "demo":
        return _demo()
    digest = verify_frozen_json(args.path)
    print(f"verified {args.path}: sha256:{digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

