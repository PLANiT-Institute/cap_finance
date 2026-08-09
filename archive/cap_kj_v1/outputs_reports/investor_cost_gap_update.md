# Investor cost-gap and risk-to-abatement update

**Decision status:** auditable quality-D screening for capital-priority diligence; not company guidance, an investment recommendation, or a verified net-cost forecast.  
**Boundary:** domestic operational Scope 1+2 facility screen. Production coverage, replacement production and system abatement remain unresolved.  
**Market-policy rule:** actual avoided compliance cost, realised green premium and verified support are unavailable; the incentive-adjusted gap remains `NA`, not zero.

## Decision table

| Company | Base annual resource gap | Low–high | Gap per operational tCO2 | Base support stress | Gap after stress | Base coverage | Largest gap facility |
|---|---:|---:|---:|---:|---:|---:|---:|
| POSCO | $3.416bn/yr | $0.685–9.317bn | $65.2/tCO2 | $0.733bn/yr | $2.683bn/yr | 100.00% | 76.4% (Pohang) |
| Nippon Steel | $6.017bn/yr | $1.758–15.441bn | $104.8/tCO2 | $1.503bn/yr | $4.515bn/yr | 100.00% | 24.8% (Oita) |
| LOTTE Chemical | $0.280bn/yr | $0.067–0.809bn | $112.5/tCO2 | $0.137bn/yr | $0.143bn/yr | 92.67% | 52.1% (Yeosu Basic) |
| Mitsui Chemicals | $0.212bn/yr | $0.046–0.674bn | $112.5/tCO2 | $0.104bn/yr | $0.108bn/yr | 97.46% | 43.8% (Osaka) |

## What changes the capital-allocation view

1. **Nippon Steel carries the largest absolute annual gap.** Its base resource proxy is $6.017bn/year across eleven costed facilities. Oita contributes 24.8%, so the economic burden is material but distributed rather than a single-asset bet.
2. **Pohang dominates POSCO more on annual economics than on CAPEX.** Pohang contributes 76.4% of the base annual gap, versus 68.6% of the earlier CAPEX screen, because its H2 and clean-power proxy is more expensive than Gwangyang's scrap-EAF case.
3. **The mechanism test separates the steel and chemical problems.** Under the rule experiment, BH alone unlocks 52.38 MtCO2/year for POSCO and 57.42 MtCO2/year for Nippon. For LOTTE and Mitsui, BH reduces residual exposure but unlocks no operational abatement; only BHL changes the rule-based facility status to no-regret.
4. **Official Mitsui facility evidence materially raises covered exposure.** The SHK bridge moves base emissions coverage from 85.0% to 97.46% and raises the covered annual resource gap by $27.1m/year. The separate mechanism chart still uses the legacy 85% boundary and must be recalibrated before exact support totals are combined with the SHK cost view.
5. **Chemical equality is mechanical, not comparative evidence.** LOTTE and Mitsui both show the same base dollars per operational tCO2 because one electrified-cracker proxy is applied to both. It cannot support a company ranking.

## Diligence priorities

- For POSCO, test Pohang clean-hydrogen and clean-power contractability before treating the large abatement block as investable.
- For Nippon Steel, test portfolio-wide procurement and infrastructure coverage; no single facility closes the company gap.
- For LOTTE and Mitsui, replace the common electrified-cracker proxy with site production, energy balance and ownership-specific project economics, then rerun BHL on the same boundary.
- Acquire verified facility policy cash effects before publishing an incentive-adjusted net gap; support stresses are decision sensitivities only.

## Figure guide

1. `05_company_annual_resource_gap.png` — low/base/high annual resource gap, base support stress and Mitsui boundary sensitivity.
2. `06_risk_to_abatement_pathway.png` — whether risk coverage, level support or both unlocks operational abatement under the rule experiment.

## Reproducibility

Generated from `outputs/tables/company_annual_cost_gap_mvp.csv` and `outputs/tables/company_support_experiment_mvp.csv` by `python -m cap_kj.investor_cost_gap_outputs`. No displayed number is manually edited.
