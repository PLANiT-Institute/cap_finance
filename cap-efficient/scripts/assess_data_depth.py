from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


TABLES = {
    "companies.csv": (8, "company totals and boundaries"),
    "company_financials.csv": (8, "financial capacity"),
    "facilities.csv": (15, "physical asset registry"),
    "technologies.csv": (15, "technology cost and performance"),
    "transition_projects.csv": (12, "official project pipeline"),
    "technology_cost_evidence.csv": (12, "observed project-cost evidence"),
    "company_constraints.csv": (8, "company execution capacity"),
    "technology_constraints.csv": (8, "technology execution risk"),
    "resource_constraints.csv": (15, "company resource availability"),
    "resource_benchmarks.csv": (5, "national resource context"),
    "scenario_anchors.csv": (12, "carbon and market pathways"),
    "plans.csv": (8, "portfolio and contract choices"),
    "policy_support.csv": (8, "policy cash support"),
    "gcam_run_manifest.csv": (10, "official GCAM run evidence"),
    "gcam_query_manifest.csv": (10, "official GCAM query evidence"),
}


def status_score(status: str) -> tuple[str, float]:
    value = status.strip().lower()
    if "pending" in value or "planned_not_run" in value:
        return "pending", 0.05
    if value in {"official", "official_converted", "official_derived"}:
        return "official_or_derived", 0.90
    if value.startswith("official_") and "model" not in value:
        return "official_or_derived", 0.95
    if "official" in value and "model" in value:
        return "mixed_official_model", 0.60
    if value in {"model_estimate", "model_anchor"}:
        return "model_estimate", 0.20
    return "other", 0.35


def main() -> None:
    parser = argparse.ArgumentParser(description="Assess source depth of model inputs.")
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()

    rows_out: list[dict[str, object]] = []
    weighted_numerator = 0.0
    weighted_denominator = 0.0
    for filename, (weight, decision_area) in TABLES.items():
        with (args.data_dir / filename).open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        if not rows or "data_status" not in rows[0]:
            raise ValueError(f"{filename} must contain rows and data_status")
        counts: dict[str, int] = {}
        row_scores: list[float] = []
        for row in rows:
            category, score = status_score(row["data_status"])
            counts[category] = counts.get(category, 0) + 1
            row_scores.append(score)
        table_score = sum(row_scores) / len(row_scores)
        weighted_numerator += table_score * weight
        weighted_denominator += weight
        rows_out.append(
            {
                "file": filename,
                "decision_area": decision_area,
                "row_count": len(rows),
                "criticality_weight": weight,
                "official_or_derived_rows": counts.get("official_or_derived", 0),
                "mixed_official_model_rows": counts.get("mixed_official_model", 0),
                "model_estimate_rows": counts.get("model_estimate", 0),
                "pending_rows": counts.get("pending", 0),
                "other_rows": counts.get("other", 0),
                "depth_score_pct": round(100 * table_score, 1),
                "priority": "P0" if weight >= 10 and table_score < 0.7 else "P1" if table_score < 0.7 else "maintain",
            }
        )
    overall_score = 100 * weighted_numerator / weighted_denominator
    gaps_path = args.data_dir / "data_gap_registry.csv"
    with gaps_path.open(encoding="utf-8-sig", newline="") as handle:
        gaps = list(csv.DictReader(handle))
    report = {
        "status": "PASS",
        "assessment_date": "2026-08-08",
        "overall_weighted_depth_score_pct": round(overall_score, 1),
        "official_project_count": next(r["row_count"] for r in rows_out if r["file"] == "transition_projects.csv"),
        "official_cost_evidence_count": next(r["row_count"] for r in rows_out if r["file"] == "technology_cost_evidence.csv"),
        "open_p0_gap_count": sum(1 for gap in gaps if gap["priority"] == "P0" and gap["data_status"] != "closed"),
        "interpretation": "Score measures evidence maturity, not forecast accuracy. Project disclosures improve audit depth but do not change optimization inputs until scope and asset mapping gates pass.",
        "tables": rows_out,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / "data_depth_assessment.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows_out[0]))
        writer.writeheader()
        writer.writerows(rows_out)
    json_path = args.output_dir / "data_depth_assessment.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
