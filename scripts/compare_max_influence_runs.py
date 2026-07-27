#!/usr/bin/env python3
"""Compare two matched-seed max_influence_mocks.py JSON outputs."""

import json
import sys

import numpy as np


if len(sys.argv) != 3:
    raise SystemExit(f"usage: {sys.argv[0]} RUN_A.json RUN_B.json")

a = json.load(open(sys.argv[1]))
b = json.load(open(sys.argv[2]))
a_records = {int(record["seed"]): record for record in a["mocks"]}
b_records = {int(record["seed"]): record for record in b["mocks"]}
seeds = sorted(set(a_records) & set(b_records))
if not seeds:
    raise SystemExit("no matched seeds")

full = np.array(
    [abs(a_records[seed]["dchi2_full"] - b_records[seed]["dchi2_full"]) for seed in seeds]
)
maximum = np.array(
    [
        abs(a_records[seed]["max_influence"] - b_records[seed]["max_influence"])
        for seed in seeds
    ]
)
selected_mismatches = sum(
    a_records[seed]["selected_index"] != b_records[seed]["selected_index"] for seed in seeds
)

summary = {
    "matched_mocks": len(seeds),
    "solvers": [a.get("solver", "unspecified"), b.get("solver", "unspecified")],
    "observed_max_influence_absolute_difference": abs(
        a["observed"]["max_influence"] - b["observed"]["max_influence"]
    ),
    "dchi2_full_absolute_difference": {
        "maximum": float(full.max()),
        "median": float(np.median(full)),
        "count_over_1e-3": int(np.count_nonzero(full > 1e-3)),
    },
    "max_influence_absolute_difference": {
        "maximum": float(maximum.max()),
        "median": float(np.median(maximum)),
        "count_over_1e-3": int(np.count_nonzero(maximum > 1e-3)),
    },
    "selected_tracer_mismatches": int(selected_mismatches),
    "tail_exceedances_ge_observed": [
        int(a["summary"]["exceedances_ge_observed"]),
        int(b["summary"]["exceedances_ge_observed"]),
    ],
}
print(json.dumps(summary, indent=2))
