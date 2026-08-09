# Emissions pathway → capital allocation: investor view v1

## What this output answers

The model starts from each company's official operational Scope 1+2 baseline, applies a common sector emissions-envelope proxy, subtracts physically available modelled facility reductions by decision year, and attaches the corresponding transition CAPEX and annual resource-gap proxy. The residual stays visible and receives a separately labelled low/base/high implied-capital extrapolation rather than being presented as an identified project.

## 2050 decision screen

| Company | Identified reduction / requirement | Unclosed gap | Identified CAPEX | Implied residual CAPEX | Implied total CAPEX | Annual resource gap | Combined high/low |
|---|---:|---:|---:|---:|---:|---:|---:|
| POSCO | 41% | 38.76 MtCO₂e/yr | $13.20bn | $18.70bn ($14.69bn–$25.99bn) | $31.90bn | $2.71bn/yr | 9.7× |
| Nippon Steel | 77% | 17.38 MtCO₂e/yr | $26.97bn | $8.16bn ($8.16bn–$9.01bn) | $35.13bn | $6.02bn/yr | 8.8× |
| LOTTE Chemical | 50% | 2.51 MtCO₂e/yr | $0.75bn | $0.75bn ($0.50bn–$1.25bn) | $1.50bn | $0.28bn/yr | 12.0× |
| Mitsui Chemicals | 52% | 1.71 MtCO₂e/yr | $0.57bn | $0.51bn ($0.34bn–$0.86bn) | $1.08bn | $0.21bn/yr | 14.6× |

## Investor interpretation

- **Pathway credibility:** Nippon Steel has the highest identified 2050 gap closure (77%) but also the largest identified capital requirement and annual funding gap. Its route capacities remain modelled rather than project-verified.
- **Physical bottleneck:** POSCO closes only 41% of its 2050 required reduction in this screen. The disclosed 2.5 Mt/year Gwangyang EAF is applied at 13.15% of the allocated works activity rather than treating the earlier full-route screen as a committed project.
- **Missing capital is analytically important:** LOTTE and Mitsui each identify roughly half of the 2050 reduction requirement. The model now gives the residual an explicit low/base/high capital extrapolation while keeping it separate from identified projects.
- **Cost uncertainty dominates:** combined annual-resource-gap cases span 8.8×–14.6×. This is a deterministic sensitivity driven by screening assumptions, not a probability distribution. Variable-resource prices contribute more spread than capital annualisation alone.
- **Milestone risk:** a company can appear aligned in 2040 and fall behind by 2050 if its identified facility sequence stops while the reference envelope continues to tighten. Nippon Steel illustrates this pattern.

## Boundaries and next evidence gates

1. The sector envelopes are global proxies scaled to company baselines, not company-specific carbon budgets or official NGFS company trajectories.
2. Except for the disclosed POSCO Gwangyang EAF block, selected route capacity is not project-verified. Implied residual CAPEX extrapolates the identified pathway's base USD per annual tCO2 and scales low/high with company model-case capital intensity; it is not an identified project or financing requirement.
3. Reductions are operational Scope 1+2, not system abatement. Replacement production, leakage, product demand, Scope 3 and trade effects remain outside the calculation.
4. Annual resource gaps exclude verified incentives, incumbent-cost offsets, green premia and financing structure; they must not be read as EBITDA or cash-flow forecasts.
5. The next highest-value data work is project-specific route capacity and decision timing, followed by verified electricity/hydrogen/feedstock price and policy/contract coverage.

## Source anchors

- Official company disclosures supply the four operational emissions baselines already recorded in the source register.
- SBTi Steel Guidance Table 9 supplies the ore-based 2020/2030/2040/2050 intensity benchmark used to construct the steel net-zero proxy.
- IEA steel and primary-chemicals pathways provide the current-policy and net-zero directional anchors; the project stores all interpolations and ranges in `data/processed/sector_emissions_pathway_anchors_mvp.csv`.
- NGFS Phase V scenario definitions establish the `Current Policies` and `Net Zero 2050` framing; the current v1 does not claim to contain solved NGFS company-level outputs.
