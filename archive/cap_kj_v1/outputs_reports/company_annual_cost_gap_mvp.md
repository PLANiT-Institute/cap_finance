# Company annual resource cost-gap MVP

## Company-first result

The base case produces the following incremental annual resource-gap proxies. Dollar amounts are real 2025 USD screening values, not company guidance or committed spending.

| Company | Base emissions coverage | Transition CAPEX | Annual resource-gap proxy | Proxy per operational tCO2 reduced | Base support stress | Gap after base support stress | Largest facility contribution |
|---|---:|---:|---:|---:|---:|---:|---:|
| POSCO | 100.0% | $18.153bn | $3.416bn/year | $65.2/tCO2 | $0.733bn/year | $2.683bn/year | Pohang 76.4% |
| Nippon Steel | 100.0% | $26.967bn | $6.017bn/year | $104.8/tCO2 | $1.503bn/year | $4.515bn/year | Oita 24.8% |
| LOTTE Chemical | 92.67% | $0.747bn | $0.280bn/year | $112.5/tCO2 | $0.137bn/year | $0.143bn/year | Yeosu Basic 52.1% |
| Mitsui Chemicals | 97.46% | $0.566bn | $0.212bn/year | $112.5/tCO2 | $0.104bn/year | $0.108bn/year | Osaka 43.8% |

Mitsui uses the FY2023 official SHK site-share bridge to the FY2024 parent anchor as the primary cost view. The retained judgement-allocation sensitivity has 85.0% coverage and a $0.185bn/year base resource gap. The registry bridge therefore raises the covered base gap by $27.1m/year, or 14.7%, while reducing the base unmodelled residual from 0.580 MtCO2 to 0.098 MtCO2.

## Capital-allocation interpretation

- Nippon Steel has the largest absolute base annual resource-gap proxy at $6.017bn/year, followed by POSCO at $3.416bn/year. This follows their much larger transition-capital blocks and does not establish relative investability.
- POSCO's Pohang share rises from 68.6% of base transition CAPEX in the earlier screen to 76.4% of annual resource gap because the H2-DRI route carries a larger variable-resource proxy than the Gwangyang scrap-EAF route. Contracting clean hydrogen and power for Pohang is therefore more consequential to annual economics than its CAPEX share alone suggests.
- LOTTE and Mitsui show the same $112.5/tCO2 base proxy because the current petrochemical screen mechanically applies one electrified-cracker CAPEX-per-abatement and variable-cost assumption. This equality is an assumption artifact, not evidence of equal project economics.
- The low POSCO case includes a $51.3m/year resource saving at Gwangyang under the negative scrap-EAF variable-cost sensitivity; the company total remains a positive $0.685bn/year gap. No support is assigned to that negative facility gap.
- Primary low/base/high annual resource gaps span $0.685bn/$3.416bn/$9.317bn for POSCO, $1.758bn/$6.017bn/$15.441bn for Nippon Steel, $0.067bn/$0.280bn/$0.809bn for LOTTE, and $0.046bn/$0.212bn/$0.674bn for Mitsui. The width is parameter uncertainty, not forecast volatility.

## Boundary and publication guardrails

The resource proxy equals transition CAPEX times the annual capital-plus-fixed-OPEX factor, plus modelled operational abatement times the route variable-resource proxy. It does not yet subtract a reconstructed incumbent cost and excludes early-retirement exposure.

The support figures are independent stress amounts applied only to positive gaps. They are not realised subsidy, contract cash flow, avoided compliance cost, or verified green premium. Those three market-policy fields remain `NA`, so a verified incentive-adjusted net gap is not published.

All cost outputs are `Modelled_from_estimated_inputs`, quality D. Operational reductions are not system abatement because production replacement and leakage remain unmodelled. Production coverage also remains unavailable.

Auditable source tables: `outputs/tables/facility_annual_cost_gap_mvp.csv` and `outputs/tables/company_annual_cost_gap_mvp.csv`.
