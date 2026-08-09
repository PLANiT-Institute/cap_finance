#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cap_efficient.gcam_manifest import write_validation_report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate GCAM release, target, query, extraction, and hash manifests."
    )
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument(
        "--output", type=Path, default=Path("outputs/gcam_manifest_validation.json")
    )
    args = parser.parse_args()
    report = write_validation_report(args.data_dir, args.output)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
