from __future__ import annotations

import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


REQUIRED_SCENARIOS = {"GCAM_15C": 1.5, "GCAM_2C": 2.0}
REQUIRED_OUTPUTS = {
    "global_mean_temperature",
    "total_climate_forcing",
    "co2_price",
    "iron_steel_production_by_tech",
    "iron_steel_inputs_by_tech",
    "iron_steel_co2_emissions",
    "electricity_price",
    "hydrogen_price",
    "company_carbon_budget",
    "electrolyzer_capex_index",
}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Required GCAM manifest is missing: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require_sha(value: str, label: str) -> None:
    if not SHA256_PATTERN.fullmatch(value):
        raise ValueError(f"{label} must be a lowercase SHA256 digest")


def validate_gcam_manifests(data_dir: Path | str) -> dict[str, object]:
    root = Path(data_dir)
    run_rows = _rows(root / "gcam_run_manifest.csv")
    query_rows = _rows(root / "gcam_query_manifest.csv")
    definition_rows = _rows(root / "scenario_definitions.csv")
    definitions = {row["scenario_id"]: row for row in definition_rows}
    runs = {row["scenario_id"]: row for row in run_rows}
    if len(runs) != len(run_rows):
        raise ValueError("Duplicate scenario_id in gcam_run_manifest.csv")
    if set(runs) != set(REQUIRED_SCENARIOS):
        raise ValueError(
            f"GCAM run manifest scenarios must be {sorted(REQUIRED_SCENARIOS)}"
        )

    grouped_queries: dict[str, list[dict[str, str]]] = {}
    seen_query_keys: set[tuple[str, str]] = set()
    for row in query_rows:
        key = (row["scenario_id"], row["required_output_id"])
        if key in seen_query_keys:
            raise ValueError(f"Duplicate GCAM query manifest row: {key}")
        seen_query_keys.add(key)
        grouped_queries.setdefault(row["scenario_id"], []).append(row)

    scenarios: dict[str, object] = {}
    for scenario_id, expected_target in REQUIRED_SCENARIOS.items():
        run = runs[scenario_id]
        definition = definitions.get(scenario_id)
        if definition is None or definition["scenario_family"] != "gcam_climate":
            raise ValueError(f"{scenario_id} must be registered as gcam_climate")
        if run["model_name"] != "GCAM + Hector":
            raise ValueError(f"{scenario_id} model_name must be GCAM + Hector")
        if run["target_type"] != "temperature":
            raise ValueError(f"{scenario_id} must use an explicit temperature target")
        if abs(float(run["target_value"]) - expected_target) > 1e-9:
            raise ValueError(f"{scenario_id} target must equal {expected_target}")
        if not run["release_url"].startswith(
            "https://github.com/JGCRI/gcam-core/releases/tag/"
        ):
            raise ValueError(f"{scenario_id} release_url must point to JGCRI/gcam-core")
        for field in (
            "release_asset_sha256",
            "configuration_origin_sha256",
            "policy_target_sha256",
            "query_file_sha256",
        ):
            _require_sha(run[field], f"{scenario_id}.{field}")

        policy_path = root / run["policy_target_file"]
        if not policy_path.is_file():
            raise FileNotFoundError(f"GCAM target file is missing: {policy_path}")
        if _sha256(policy_path) != run["policy_target_sha256"]:
            raise ValueError(f"{scenario_id} policy target SHA256 mismatch")
        xml = ET.parse(policy_path).getroot()
        target_type = (xml.findtext("target-type") or "").strip()
        target_value = float(xml.findtext("target-value") or "nan")
        if target_type != "temperature" or abs(target_value - expected_target) > 1e-9:
            raise ValueError(f"{scenario_id} target XML does not match the manifest")

        outputs = {row["required_output_id"] for row in grouped_queries.get(scenario_id, [])}
        if outputs != REQUIRED_OUTPUTS:
            raise ValueError(
                f"{scenario_id} query coverage mismatch: missing={sorted(REQUIRED_OUTPUTS - outputs)}, "
                f"extra={sorted(outputs - REQUIRED_OUTPUTS)}"
            )
        for row in grouped_queries[scenario_id]:
            output_id = row["required_output_id"]
            if not row["source_url"].startswith("https://"):
                raise ValueError(f"{scenario_id}/{output_id} needs a source URL")
            if row["extraction_status"] == "pending":
                if row["output_file"] or row["output_sha256"]:
                    raise ValueError(
                        f"Pending output {scenario_id}/{output_id} must not claim a file/hash"
                    )
            else:
                if row["extraction_status"] not in {"extracted_verified", "external_verified"}:
                    raise ValueError(f"Invalid extraction status for {scenario_id}/{output_id}")
                output_path = root / row["output_file"]
                _require_sha(row["output_sha256"], f"{scenario_id}.{output_id}")
                if not output_path.is_file() or _sha256(output_path) != row["output_sha256"]:
                    raise ValueError(f"Output/hash mismatch for {scenario_id}/{output_id}")

        run_verified = run["run_status"] == "extracted_verified"
        active = definition["is_active"].strip().lower() == "true"
        if active and not run_verified:
            raise ValueError(f"Active {scenario_id} requires run_status=extracted_verified")
        if run_verified:
            for field in ("database_file", "database_sha256", "extraction_date"):
                if not run[field]:
                    raise ValueError(f"Verified {scenario_id} requires {field}")
            _require_sha(run["database_sha256"], f"{scenario_id}.database_sha256")
            database_path = root / run["database_file"]
            if not database_path.is_file() or _sha256(database_path) != run["database_sha256"]:
                raise ValueError(f"{scenario_id} database file/hash mismatch")
        elif any(run[field] for field in ("database_file", "database_sha256", "extraction_date")):
            raise ValueError(f"Pending {scenario_id} must not claim database/extraction metadata")

        all_outputs_verified = all(
            row["extraction_status"] in {"extracted_verified", "external_verified"}
            for row in grouped_queries[scenario_id]
        )
        ready = run_verified and all_outputs_verified
        if active and not ready:
            raise ValueError(f"Active {scenario_id} has incomplete query outputs")
        scenarios[scenario_id] = {
            "model_version": run["model_version"],
            "release_tag": run["release_tag"],
            "release_asset_sha256": run["release_asset_sha256"],
            "target_type": run["target_type"],
            "target_value": float(run["target_value"]),
            "run_status": run["run_status"],
            "query_outputs_verified": sum(
                row["extraction_status"] in {"extracted_verified", "external_verified"}
                for row in grouped_queries[scenario_id]
            ),
            "query_outputs_required": len(REQUIRED_OUTPUTS),
            "ready_to_activate": ready,
            "blocking_requirements": [] if ready else [
                "successful official-model target-finder run",
                "temperature target/baseline verification",
                "query export with raw-unit metadata",
                "company disaggregation and electrolyzer-index audit",
                "database/output SHA256 pinning",
            ],
        }

    return {
        "status": "PASS",
        "validation_scope": "manifest integrity; not GCAM numerical-result validation",
        "run_rows": len(run_rows),
        "query_rows": len(query_rows),
        "scenarios": scenarios,
    }


def write_validation_report(data_dir: Path | str, output: Path | str) -> dict[str, object]:
    report = validate_gcam_manifests(data_dir)
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report
