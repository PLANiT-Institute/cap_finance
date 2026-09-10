"""Isolate noncash write-off exposure without changing the production model.

Paired synthetic facilities differ only in incumbent book value. This diagnoses
current behavior; its assertions are evidence of the defect, not approval of it.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cap import config as C
from cap.plancost import build_profile, simulate_cost


def main():
    cfg = C.load(capex_shock_scaling="legacy_linear", allow_legacy_price_paths=True, capital_accounting="legacy_mixed", energy_balance_mode="legacy_retrofit_all", carbon_accounting_mode="legacy_auction_discount", transition_loss_basis="incremental_ex_carbon", plan_selection_criterion="p50")
    cfg["years"] = {"start": 2025, "end": 2026}
    cfg["discount_rate"] = 0.0
    cfg["incumbent_capex_scale"] = 1.0
    cfg["milp"] = dict(cfg["milp"], reinvest_window_halfwidth=1)
    cfg["contracts"] = dict(cfg["contracts"], epc_premium_pct=.1)
    years = np.arange(2025, 2027)
    prices = {k: np.zeros(2) for k in ("elec", "re", "h2", "coal", "gas", "co2")}
    facilities = pd.DataFrame([dict(facility_id="AUDIT_1", company_id="AUDIT",
        capacity=100., production=100., reinvest_cycle_yr=20., last_reline_year=2020,
        incumbent_capex_unit=200., margin_kthou_t=0., elec_int_inc=0.,
        coal_int_inc=0., gas_int_inc=0., ef_inc=0.)]).set_index("facility_id")
    techs = pd.DataFrame([dict(tech_id="AUDIT_TECH", capex_unit=100.,
        capex_uncertainty=40., build_years=1, lifetime=20., retrofit=0,
        elec_intensity=0., h2_intensity=0., emission_factor=0., opex_var=0., opex_fixed=0.)])
    # Book value: 100 t capacity * 200 thousand KRW/t * (2040-2025-1)/20.
    expected_book_bn = 100. * 200. * 14./20. * 1e-6
    rows = []
    for mode, epc, subsidy, multipliers in (
        ("unhedged_construction_shock", 0, 0., [.5, 2.]),
        ("fixed_epc_10pct_premium", 1, 0., [.5, 2.]),
        ("construction_subsidy_50pct", 0, .5, [1., 1.]),
        ("retirement_control", 0, 0., [.5, 2.]),
    ):
        plan = pd.DataFrame([dict(plan_id="AUDIT", company_id="AUDIT",
            facility_id="AUDIT_1", tech_id="retire" if mode=="retirement_control" else "AUDIT_TECH",
            adopt_year=2025, op_year=2025, ppa_share=0., epc=epc, ccfd=0)])
        shocks = {k: np.ones((2, 2)) for k in ("elec", "h2", "capex")}
        shocks["capex"] = np.repeat(np.array(multipliers)[:, None], 2, axis=1)
        support = {"subsidy": {"AUDIT_TECH": np.full(2, subsidy)}, "ccfd_strike": None}
        costs = []
        for book_unit in (0., 200.):
            fac = facilities.copy()
            fac["incumbent_capex_unit"] = book_unit
            profile = build_profile(plan, fac, techs, prices, years, cfg)
            costs.append(simulate_cost(profile, prices, shocks, support, cfg))
        delta = costs[1] - costs[0]
        multiplier = np.ones(2) if mode=="retirement_control" else (
            np.full(2, 1.1) if epc else np.array(multipliers)) * (1-subsidy)
        np.testing.assert_allclose(delta, expected_book_bn * multiplier, atol=1e-14, rtol=0)
        for i, value in enumerate(delta):
            rows.append(dict(case=mode, path=i, construction_shock=multipliers[i],
                book_writeoff_bn=expected_book_bn, observed_paired_cost_difference_bn=value,
                difference_from_deterministic_book_bn=value-expected_book_bn,
                expected_cash_difference_bn=0.))
    result = pd.DataFrame(rows)
    out = ROOT / "docs/research_cycles/2026-09-05"
    result.to_csv(out / "writeoff_accounting_audit.csv", index=False)
    manifest = dict(scope="Synthetic paired facilities; isolates book amount from equal construction and salvage",
        cases=4, paired_path_comparisons=8, model_fixed=False,
        finding="Conversion book amount receives construction shocks, EPC premium and construction subsidy; retirement control stays deterministic",
        cash_interpretation="Changing only historical book value has no current cash effect",
        sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (Path(__file__),ROOT/"src/cap/plancost.py",ROOT/"config.yaml")})
    (out/"writeoff_accounting_audit_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
