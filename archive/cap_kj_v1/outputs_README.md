# Generated outputs

Tables, figures, and diagnostics in this directory are generated from the versioned pipeline. They must not be edited manually.

Release outputs may be committed only after the corresponding source manifest, configuration, code version, and validation report are fixed.

## Primary simple three-step outputs

- `tables/company_simple_three_step_mvp.csv` — one company row linking allocated G-CAP, route-identified capital, capital gap, annual base cost gap, transition-premium proxy and support-conditioned emissions closure.
- `figures/13_gcap_company_capital_gap.png` — company G-CAP split into route-identified capital and the capital still missing, with low/high intensity ranges and representative technologies.
- `figures/14_level_gap_and_premium_proxy.png` — annual base resource-cost gap and high-minus-base uncertainty buffer as percentages of G-CAP.
- `figures/15_support_to_emissions_closure.png` — level-only, premium-mitigation-only and combined operational-reduction closure, plus the emissions gap that remains.
- `reports/simple_three_step_investor_model.md` — the three equations, four-company decision table, main conclusions and evidence boundary.

G-CAP and the transition-premium metric are quality-D screening proxies. G-CAP is not yet a direct solved GCAM capital output; the premium proxy is not WACC or a market-priced spread. The earlier v1 outputs below remain available for audit, and a snapshot is preserved at `archive/2026-08-05-complex-v1/`.

## Earlier pathway and capital-flow outputs

- `tables/company_emissions_pathway_mvp.csv` — official baseline, current-policies proxy, net-zero envelope, identified facility path, unclosed gap, identified CAPEX, low/base/high implied residual capital and annual resource gap for 2025/2030/2040/2050.
- `tables/facility_gap_to_capital_pathway_mvp.csv` — facility-level physical availability, assigned reduction, CAPEX and annual gap feeding the company pathway.
- `tables/company_pathway_uncertainty_mvp.csv` — capital-annualisation, variable-resource and combined low/base/high funding-gap sensitivities on fixed pathway scope.
- `figures/07_company_emissions_pathway.png` through `10_capital_timing_vs_gap_closed.png` — the four investor-facing pathway views.
- `reports/emissions_pathway_v1.md` — interpretation, boundaries and next evidence gates.
- `tables/company_capital_flow_bridge_mvp.csv` — physical capital need, B0/BH/BL/BHL screening-investable capital, risk coverage, level-support equivalent, unlocked operational reduction and premium-relevant residual exposure.
- `figures/11_capital_flow_policy_bridge.png` — shows when identified capital crosses the provisional investability threshold and the operational reduction associated with it.
- `figures/12_premium_relevant_exposure.png` — shows the common-cost exposure quantity before and after the enabling policy bundle; risk-premium basis points remain NA.
- `reports/capital_flow_investor_note.md` — capital-gap decomposition, policy closure logic and the risk-premium data gate.
