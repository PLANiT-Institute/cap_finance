# Four-company capital-allocation screening memo

> Run 4 screening snapshot. The current annual cost-gap and risk-to-abatement view is `outputs/reports/investor_cost_gap_update.md`; this earlier memo is retained for audit history.

**Decision status:** first-pass output for prioritising diligence; not company guidance, committed capital, or an investment recommendation.  
**Boundary:** covered domestic facility-seed operational Scope 1+2 emissions. Production coverage is not yet available.  
**Evidence status:** company anchors and selected facility/project facts are official or reported; the transition CAPEX and operational-abatement outputs below are `Modelled`, use estimated/allocated inputs, and carry quality flag D.

## Decision snapshot

| Company | Base CAPEX | Low–high | By 2030 | Operational abatement | Emissions coverage | Main dependency | Largest facility share |
|---|---:|---:|---:|---:|---:|---|---:|
| POSCO | $18.15bn | $9.51–31.12bn | $5.71bn | 52.38 MtCO2e/yr | 100.0% | Contract 68.6%; price 31.4% | 68.6% (Pohang) |
| Nippon Steel | $26.97bn | $16.85–40.48bn | $0.06bn | 57.42 MtCO2e/yr | 100.0% | Contract 99.8% | 24.8% (Oita) |
| LOTTE Chemical | $0.75bn | $0.30–1.74bn | $0.00bn | 2.49 MtCO2e/yr | 92.7% | Level support 100% | 52.1% (Yeosu Basic) |
| Mitsui Chemicals | $0.49bn | $0.15–1.52bn | $0.00bn | 1.64 MtCO2e/yr | 85.0% | Level support 100% | 37.6% (Ichihara) |

## Capital-allocation pathway

1. **The only material 2030 capital block in this screen is POSCO Gwangyang.** POSCO has $5.71bn in the by-2030 bucket, while its remaining $12.45bn falls in 2031–2040. The near-term diligence question is therefore whether Gwangyang's EAF-linked power and scrap conditions can move from price-conditional screening to an executable package.
2. **Nippon Steel is a later, contract-heavy portfolio problem.** 99.8% of base CAPEX falls in 2031–2040 and 99.8% is provisionally contract-dependent. Oita is the largest site but only 24.8% of company CAPEX, implying a multi-site procurement and infrastructure programme rather than a single-asset solution.
3. **POSCO has greater single-project concentration.** Pohang represents 68.6% of base transition CAPEX. That makes hydrogen, clean-power and commercial-scale HyREX readiness a concentrated execution gate, even though total modelled operational abatement is large.
4. **Petrochemical totals are smaller but less decision-ready.** LOTTE and Mitsui are both screened as 100% level-support-dependent for their modelled assets. Their uncovered emissions are 0.394 and 0.580 MtCO2e/year respectively, so the current figures are not full-company transition plans.

## What the ranges say

- Steel CAPEX uncertainty is material: POSCO's high case is 3.27x its low case and Nippon Steel's is 2.40x.
- Petrochemical uncertainty is wider: LOTTE spans 5.83x and Mitsui 10.21x. The result reflects a coarse annual-abatement CAPEX proxy and, for Mitsui, allocated site emissions; it should direct data collection, not support relative valuation.
- Base operational-abatement efficiency is 2.89 MtCO2e/year per USD bn for POSCO and 2.13 for Nippon Steel. The 3.33 value shared by both petrochemical companies is mechanically imposed by the same proxy and is not an independently observed advantage.

## Required next evidence before an allocation decision

- Build resource-cost and market-policy ledgers; current status labels are screening placeholders, not passed economic-feasibility tests.
- Run B0/BH/BL/BHL cases to separate reduced input-price exposure from a lower mean cost level and to trace any additional modelled abatement to changed facility decisions.
- Add official facility emissions, actual policy treatment, production coverage, route energy/material balances, and ownership/equity sensitivities.
- Model replacement production and leakage before calling operational reductions system abatement.

## Figure guide

1. `01_company_capex_range.png` — capital magnitude and low/base/high uncertainty by sector.
2. `02_capital_timing_and_dependency.png` — decision windows and provisional dependency classification.
3. `03_abatement_efficiency_and_coverage.png` — operational reduction, capital efficiency and boundary coverage.
4. `04_capital_concentration_and_uncertainty.png` — largest-facility execution concentration and assumption span.

## Reproducibility

Generated from `outputs/tables/company_capital_allocation_mvp.csv` and `outputs/tables/facility_capital_allocation_mvp.csv` by `python -m cap_kj.investor_outputs`. Every source and estimation method traces through the input tables to `data/manifests/source_register.csv`; no result is manually edited.
