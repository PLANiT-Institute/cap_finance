from __future__ import annotations

import csv
import json
import shutil
import tempfile
import unittest
from itertools import combinations
from pathlib import Path

from cap_efficient.loader import load_data
from cap_efficient.dashboard import run_repeated_analysis
from cap_efficient.math_utils import pareto_frontier, quantile
from cap_efficient.pipeline import _shapley_variance_allocation, run_pipeline
from cap_efficient.schedule import (
    optimize_schedule,
    physical_constraint_diagnostics,
    portfolio_id,
    rebase_fixed_schedule,
    schedule_budget_diagnostics,
)


ROOT = Path(__file__).resolve().parents[1]


class DataAndMathTests(unittest.TestCase):
    def test_data_load_and_schedule_feasibility(self) -> None:
        bundle = load_data(ROOT / "data")
        self.assertEqual(len(bundle.companies), 4)
        self.assertEqual(len(bundle.facilities), 17)
        self.assertEqual(len(bundle.scenarios), 8)
        self.assertEqual(len(bundle.scenario_definitions), 4)
        self.assertEqual(len(bundle.technology_constraints), 6)
        self.assertEqual(len(bundle.company_constraints), 4)
        self.assertEqual(len(bundle.resource_constraints), 8)
        self.assertEqual(len(bundle.resource_benchmarks), 11)
        self.assertEqual(len(bundle.transition_projects), 9)
        self.assertEqual(len(bundle.technology_cost_evidence), 7)
        self.assertTrue(all(row.source_url.startswith("https://") for row in bundle.transition_projects))
        self.assertTrue(all("not_company" in row.comparability for row in bundle.resource_benchmarks))
        self.assertTrue(bundle.scenario_definitions["ACCELERATED_15C"].is_active)
        self.assertFalse(bundle.scenario_definitions["GCAM_2C"].is_active)
        schedule = optimize_schedule(bundle, "POSCO_KR", "ACCELERATED_15C", "P4")
        self.assertGreater(schedule.cumulative_avoided_emissions_mtco2, 0)
        self.assertEqual(
            len(schedule.actions),
            sum(f.company_id == "POSCO_KR" for f in bundle.facilities.values()),
        )
        disclosed = optimize_schedule(bundle, "POSCO_KR", "DISCLOSED_PATH", "CURRENT")
        strict = rebase_fixed_schedule(bundle, disclosed, "ACCELERATED_15C")
        self.assertEqual(disclosed.actions, strict.actions)
        self.assertEqual(portfolio_id(disclosed), portfolio_id(strict))
        diagnostics = schedule_budget_diagnostics(bundle, strict)
        self.assertFalse(diagnostics["scenario_feasible"])
        self.assertEqual(diagnostics["first_budget_breach_year"], 2030)
        physical = physical_constraint_diagnostics(bundle, strict)
        self.assertIn("portfolio_failure_probability", physical)
        self.assertGreaterEqual(physical["max_concurrent_construction_projects"], 1)

    def test_quantile_and_frontier(self) -> None:
        self.assertEqual(quantile([1.0, 2.0, 3.0], 0.5), 2.0)
        frontier = pareto_frontier([
            {"plan_id": "A", "p50": 10.0, "tcar": 20.0},
            {"plan_id": "B", "p50": 12.0, "tcar": 12.0},
            {"plan_id": "C", "p50": 15.0, "tcar": 25.0},
        ])
        self.assertEqual([row["plan_id"] for row in frontier], ["A", "B"])

    def test_shapley_variance_allocation_reconciles(self) -> None:
        factors = ("electricity", "hydrogen_input", "construction_capex")
        weights = {"electricity": 1.0, "hydrogen_input": 2.0, "construction_capex": 3.0}
        game = {
            frozenset(subset): sum(weights[item] for item in subset)
            for size in range(4)
            for subset in combinations(factors, size)
        }
        contributions, shares, delta = _shapley_variance_allocation(game)
        self.assertEqual(contributions, weights)
        self.assertAlmostEqual(sum(shares.values()), 1.0, places=12)
        self.assertAlmostEqual(shares["hydrogen_input"], 1.0 / 3.0, places=12)
        self.assertAlmostEqual(delta, 0.0, places=12)


class PipelineSmokeTest(unittest.TestCase):
    def test_pipeline_writes_complete_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_pipeline(
                data_dir=ROOT / "data",
                output_dir=Path(temp_dir),
                path_count=30,
                seed=7,
            )
            self.assertEqual(result["company_count"], 4)
            self.assertEqual(result["plan_count"], 32)
            expected = {
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
                "gcam_manifest_validation.json",
                "scenario_registry.json",
                "run_summary.json",
                "report.md",
                "frontier_POSCO_KR_ACCELERATED_15C.svg",
                "frontier_JFE_STEEL_JP_DISCLOSED_PATH.svg",
            }
            self.assertTrue(expected.issubset({path.name for path in Path(temp_dir).iterdir()}))
            report_text = (Path(temp_dir) / "report.md").read_text(encoding="utf-8")
            self.assertIn("각 기업 λ=1 추천의 **최악 TCaR 시나리오**", report_text)
            registry = json.loads(
                (Path(temp_dir) / "scenario_registry.json").read_text(encoding="utf-8")
            )
            self.assertEqual(len(registry["definitions"]), 4)
            self.assertEqual(
                {
                    row["scenario_id"]
                    for row in registry["definitions"]
                    if not row["is_active"]
                },
                {"GCAM_15C", "GCAM_2C"},
            )
            with (Path(temp_dir) / "plan_metrics.csv").open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 64)
            for row in rows:
                factor_sum = sum(float(row[key]) for key in (
                    "electricity_variance_share",
                    "hydrogen_variance_share",
                    "capex_variance_share",
                ))
                self.assertAlmostEqual(factor_sum, 1.0, places=5)
                self.assertGreaterEqual(float(row["tcar_kkrw_per_tco2"]), 0.0)
                self.assertGreaterEqual(
                    float(row["gross_cost_p50_kkrw_per_tco2"]),
                    float(row["expected_cost_p50_kkrw_per_tco2"]),
                )
                component_total = sum(float(row[key]) for key in (
                    "capex_cost_p50_bn_krw",
                    "fixed_opex_cost_p50_bn_krw",
                    "electricity_cost_p50_bn_krw",
                    "hydrogen_cost_p50_bn_krw",
                    "contract_premium_p50_bn_krw",
                    "carbon_value_p50_bn_krw",
                    "policy_support_p50_bn_krw",
                    "component_reconciliation_p50_bn_krw",
                ))
                self.assertAlmostEqual(
                    component_total,
                    float(row["expected_cost_p50_bn_krw"]),
                    places=2,
                )
                self.assertAlmostEqual(
                    float(row["absolute_npv_p50_bn_krw"])
                    / float(row["common_avoided_emissions_mtco2"]),
                    float(row[
                        "net_economic_cost_p50_kkrw_per_tco2_common_denominator"
                    ]),
                    places=5,
                )
                self.assertAlmostEqual(
                    float(row["net_cash_cost_after_support_p50_bn_krw"])
                    - float(row["avoided_carbon_cost_value_p50_bn_krw"]),
                    float(row["absolute_npv_p50_bn_krw"]),
                    places=2,
                )
                self.assertAlmostEqual(
                    float(row["economic_cost_p50_identity_delta_bn_krw"]),
                    0.0,
                    places=2,
                )
                self.assertGreaterEqual(
                    float(row["avoided_carbon_cost_value_p50_bn_krw"]), 0.0
                )
                self.assertGreaterEqual(
                    float(row["policy_support_value_p50_bn_krw"]), 0.0
                )
                self.assertEqual(
                    row["scenario_feasible"] == "True",
                    row["carbon_budget_feasible"] == "True"
                    and row["physical_constraints_feasible"] == "True",
                )
            with (Path(temp_dir) / "facility_schedule.csv").open(
                encoding="utf-8"
            ) as handle:
                facility_rows = list(csv.DictReader(handle))
            self.assertIn("baseline_emissions_mtco2", facility_rows[0])
            self.assertIn("base_case_net_cost_bn_krw", facility_rows[0])
            self.assertIn(
                "base_case_net_cash_cost_after_support_bn_krw",
                facility_rows[0],
            )
            posco_current = [
                row
                for row in facility_rows
                if row["company_id"] == "POSCO_KR"
                and row["scenario_id"] == "ACCELERATED_15C"
                and row["plan_id"] == "CURRENT"
            ]
            self.assertAlmostEqual(
                sum(float(row["baseline_emissions_mtco2"]) for row in posco_current),
                69.84605,
                places=4,
            )
            action_sets: dict[tuple[str, str, str], set[tuple[str, str, str]]] = {}
            for row in facility_rows:
                key = (row["company_id"], row["plan_id"], row["facility_id"])
                action_sets.setdefault(key, set()).add((
                    row["technology_id"],
                    row["transition_year"],
                    row["portfolio_id"],
                ))
            self.assertTrue(all(len(actions) == 1 for actions in action_sets.values()))
            with (Path(temp_dir) / "scenario_comparison.csv").open(
                encoding="utf-8"
            ) as handle:
                comparisons = list(csv.DictReader(handle))
            self.assertEqual(len(comparisons), 32)
            self.assertTrue(all(row["same_physical_portfolio"] == "True" for row in comparisons))
            self.assertTrue(all(float(row["delta_aligned_capex_bn_krw"]) == 0.0 for row in comparisons))
            with (Path(temp_dir) / "frontier_membership.csv").open(
                encoding="utf-8"
            ) as handle:
                memberships = list(csv.DictReader(handle))
            self.assertFalse(any(
                row["is_frontier"] == "True"
                and row["is_scenario_feasible"] == "False"
                for row in memberships
            ))
            with (Path(temp_dir) / "candidate_portfolios.csv").open(
                encoding="utf-8"
            ) as handle:
                candidate_catalog = list(csv.DictReader(handle))
            self.assertGreaterEqual(len(candidate_catalog), 800)
            self.assertEqual(
                len({row["candidate_id"] for row in candidate_catalog}),
                len(candidate_catalog),
            )
            with (Path(temp_dir) / "candidate_robust_summary.csv").open(
                encoding="utf-8"
            ) as handle:
                robust_rows = list(csv.DictReader(handle))
            for company_id in {row["company_id"] for row in robust_rows}:
                company_rows = [
                    row for row in robust_rows if row["company_id"] == company_id
                ]
                self.assertTrue(any(row["robust_feasible"] == "True" for row in company_rows))
                self.assertEqual(
                    sum(row["lambda_1_optimal"] == "True" for row in company_rows),
                    1,
                )
            with (Path(temp_dir) / "candidate_scenario_comparison.csv").open(
                encoding="utf-8"
            ) as handle:
                candidate_comparisons = list(csv.DictReader(handle))
            self.assertEqual(len(candidate_comparisons), len(robust_rows))
            self.assertTrue(all(
                row["same_physical_portfolio"] == "True"
                and float(row["delta_aligned_capex_bn_krw"]) == 0.0
                for row in candidate_comparisons
            ))
            with (Path(temp_dir) / "refined_candidate_scenario_metrics.csv").open(
                encoding="utf-8"
            ) as handle:
                refined_metrics = list(csv.DictReader(handle))
            with (Path(temp_dir) / "refined_candidate_robust_summary.csv").open(
                encoding="utf-8"
            ) as handle:
                refined_robust = list(csv.DictReader(handle))
            self.assertGreaterEqual(len(refined_robust), 30)
            self.assertEqual(len(refined_metrics), 2 * len(refined_robust))
            self.assertTrue(all(
                int(row["candidate_path_count"]) == 30
                and row["refinement_tier"]
                == "deterministic_robust_shortlist_full_paths"
                for row in refined_metrics
            ))
            for row in refined_metrics:
                self.assertAlmostEqual(
                    sum(float(row[key]) for key in (
                        "electricity_variance_share",
                        "hydrogen_variance_share",
                        "capex_variance_share",
                    )),
                    1.0,
                    places=5,
                )
                self.assertEqual(
                    row["risk_decomposition_method"],
                    "variance_game_shapley_common_random_numbers",
                )
                self.assertAlmostEqual(
                    sum(float(row[key]) for key in (
                        "electricity_shapley_variance_share",
                        "hydrogen_shapley_variance_share",
                        "capex_shapley_variance_share",
                    )),
                    1.0,
                    places=5,
                )
                self.assertAlmostEqual(
                    float(row["shapley_reconciliation_delta"]), 0.0, places=8
                )
            for company_id in {row["company_id"] for row in refined_robust}:
                company_rows = [
                    row for row in refined_robust if row["company_id"] == company_id
                ]
                self.assertEqual(
                    sum(row["lambda_1_optimal"] == "True" for row in company_rows),
                    1,
                )
            refined_ids = {row["candidate_id"] for row in refined_robust}
            with (Path(temp_dir) / "refined_candidate_facility_schedule.csv").open(
                encoding="utf-8"
            ) as handle:
                refined_facilities = list(csv.DictReader(handle))
            self.assertEqual(
                {row["candidate_id"] for row in refined_facilities}, refined_ids
            )
            with (Path(temp_dir) / "refined_candidate_resource_profile.csv").open(
                encoding="utf-8"
            ) as handle:
                refined_resources = list(csv.DictReader(handle))
            self.assertEqual(
                {row["candidate_id"] for row in refined_resources}, refined_ids
            )
            for row in refined_resources:
                self.assertAlmostEqual(
                    float(row["scrap_supply_mt"])
                    - float(row["scrap_demand_mt"]),
                    float(row["scrap_headroom_mt"]),
                    places=5,
                )

    def test_repeated_dashboard_is_standalone(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_repeated_analysis(
                data_dir=ROOT / "data",
                output_dir=Path(temp_dir),
                path_count=12,
                seeds=[1, 2],
            )
            dashboard = Path(result["dashboard_path"])
            html = dashboard.read_text(encoding="utf-8")
            self.assertIn("<!doctype html>", html.lower())
            self.assertIn("POSCO와 일본 3사의 공시경로", html)
            self.assertIn("설비별 전환 실행지도", html)
            self.assertIn("P50 경제적 순비용 브리지", html)
            self.assertIn("동일 포트폴리오 시나리오 변화", html)
            self.assertIn("강건 후보 지도", html)
            self.assertIn("λ 추천 강건후보 · 시설과 공급여력", html)
            self.assertIn("maximum_regret_p50", html)
            self.assertIn("내부 1.5°C 스트레스 (비-GCAM)", html)
            self.assertIn("GCAM_2C", html)
            self.assertIn("공식 국가 벤치마크", html)
            self.assertIn("variance_game_shapley_common_random_numbers", html)
            self.assertNotIn("__DASHBOARD_DATA__", html)
            self.assertEqual(result["effective_paths_per_plan"], 24)
            self.assertTrue((Path(temp_dir) / "repeat_plan_summary.csv").exists())
            self.assertTrue((Path(temp_dir) / "repeat_scenario_comparison.csv").exists())
            self.assertTrue((Path(temp_dir) / "repeat_candidate_robust_summary.csv").exists())
            self.assertTrue((Path(temp_dir) / "repeat_candidate_scenario_comparison.csv").exists())
            self.assertTrue((Path(temp_dir) / "repeat_refined_candidate_scenario_metrics.csv").exists())
            self.assertTrue((Path(temp_dir) / "repeat_refined_candidate_robust_summary.csv").exists())
            self.assertTrue((Path(temp_dir) / "refined_candidate_facility_schedule.csv").exists())
            self.assertTrue((Path(temp_dir) / "refined_candidate_resource_profile.csv").exists())
            self.assertEqual(len(result["scenario_comparisons"]), 32)
            self.assertGreaterEqual(len(result["candidate_robust_summary"]), 200)
            self.assertGreaterEqual(len(result["refined_candidate_robust_summary"]), 30)
            self.assertTrue(all(
                int(row["candidate_path_count"]) == 12
                for row in result["refined_candidate_metrics"]
            ))
            self.assertIn("현재 선택 시나리오의 시설 액션", html)
            self.assertIn("자원 최대 활용률은 현재 선택 시나리오", html)
            self.assertIn("공식 전환 프로젝트 증거층", html)
            self.assertIn("Gwangyang 2.5 Mt large-scale EAF", html)
            self.assertIn("technology_cost_evidence", html)
            english_dashboard = Path(result["english_dashboard_path"])
            english_html = english_dashboard.read_text(encoding="utf-8")
            self.assertTrue(english_dashboard.exists())
            self.assertIn('<html lang="en">', english_html)
            self.assertIn("From assets to the boardroom:", english_html)
            self.assertIn("Asset-level transition execution map", english_html)
            self.assertIn("Same portfolio across scenarios", english_html)
            self.assertIn("Official transition-project evidence layer", english_html)
            self.assertIn("Internal 1.5°C stress test (non-GCAM)", english_html)
            self.assertIn('href="dashboard.html">Korean</a>', english_html)
            self.assertNotRegex(english_html, r"[가-힣]")

    def test_incomplete_official_gcam_scenario_cannot_be_activated(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "data"
            shutil.copytree(ROOT / "data", target)
            registry_path = target / "scenario_definitions.csv"
            text = registry_path.read_text(encoding="utf-8")
            registry_path.write_text(
                text.replace(
                    "GCAM_2C,GCAM 2.0°C 공식 추출 대기,gcam_climate,2.0,false,",
                    "GCAM_2C,GCAM 2.0°C 공식 추출 대기,gcam_climate,2.0,true,",
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "Active scenario definitions"):
                load_data(target)

    def test_gcam_target_hash_tampering_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "data"
            shutil.copytree(ROOT / "data", target)
            policy = target / "gcam" / "policy_target_temperature_2p0.xml"
            policy.write_text(
                policy.read_text(encoding="utf-8").replace(
                    "<target-value>2.0</target-value>",
                    "<target-value>2.1</target-value>",
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "policy target SHA256 mismatch"):
                load_data(target)


if __name__ == "__main__":
    unittest.main()
