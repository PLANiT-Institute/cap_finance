#!/usr/bin/env python3
"""Compare deterministic model artifacts from canonical and Excel-exported CSV inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


DEFAULT_FILES = (
    "plan_metrics.csv",
    "facility_schedule.csv",
    "frontier_membership.csv",
    "scenario_comparison.csv",
    "candidate_portfolios.csv",
    "candidate_screening.csv",
    "candidate_scenario_metrics.csv",
    "candidate_robust_summary.csv",
    "candidate_scenario_comparison.csv",
    "refined_candidate_scenario_metrics.csv",
    "refined_candidate_robust_summary.csv",
    "refined_candidate_scenario_comparison.csv",
    "refined_candidate_facility_schedule.csv",
    "refined_candidate_resource_profile.csv",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-dir", type=Path, required=True)
    parser.add_argument("--roundtrip-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--paths", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    files: dict[str, object] = {}
    overall = "PASS"
    for filename in DEFAULT_FILES:
        reference = args.reference_dir / filename
        roundtrip = args.roundtrip_dir / filename
        ref_bytes = reference.read_bytes()
        test_bytes = roundtrip.read_bytes()
        status = "PASS" if ref_bytes == test_bytes else "FAIL"
        if status == "FAIL":
            overall = "FAIL"
        files[filename] = {
            "status": status,
            "reference_sha256": sha256(reference),
            "roundtrip_sha256": sha256(roundtrip),
            "bytes": len(ref_bytes),
        }

    payload = {
        "status": overall,
        "paths": args.paths,
        "seed": args.seed,
        "reference_dir": str(args.reference_dir.resolve()),
        "roundtrip_dir": str(args.roundtrip_dir.resolve()),
        "files": files,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
