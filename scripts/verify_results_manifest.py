#!/usr/bin/env python3
"""Verify canonical result hashes and flagship fields in RESULTS_MANIFEST.json."""

import hashlib
import json
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
manifest = json.load(open(PROJECT / "RESULTS_MANIFEST.json"))
errors = []

for relative, expected in manifest["sha256"].items():
    path = PROJECT / relative
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        errors.append(f"hash mismatch: {relative}: expected {expected}, got {actual}")

result = json.load(open(PROJECT / "results" / "max_influence_mocks.json"))
canonical = manifest["canonical_results"]["selection_calibrated_maximum_influence"]
checks = {
    "observed_selected_tracer": result["observed"]["selected_tracer"],
    "observed_max_influence": result["observed"]["max_influence"],
    "observed_dchi2_without_selected_tracer": result["observed"]["dchi2_deleted"][2],
    "n_mocks": result["summary"]["n_mocks"],
}
for key, actual in checks.items():
    if canonical[key] != actual:
        errors.append(f"field mismatch: {key}: manifest {canonical[key]!r}, result {actual!r}")

if errors:
    raise SystemExit("\n".join(errors))
print(f"PASS: {len(manifest['sha256'])} hashes and {len(checks)} flagship fields verified")
