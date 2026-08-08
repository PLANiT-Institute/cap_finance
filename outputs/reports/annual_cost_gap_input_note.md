# Annual cost-gap proxy input note

## Decision use

This input layer makes the existing facility transition-CAPEX screen annual. It is designed to answer how much annual economic gap each route creates before transfers, and how much of that gap would remain under an explicitly selected support stress. It does **not** claim a verified net cost gap.

## MVP calculation

For each modelled facility and low/base/high resource case:

`annual resource gap proxy = transition CAPEX × (CRF + incremental fixed-OPEX share) + modelled operational abatement × variable-resource gap proxy`

The resource case combines 3%/5%/7% real analytical discount rates with route lives, fixed OPEX and variable-resource ranges. The analytical rate is not a company WACC. The proxy is incremental: incumbent CAPEX and operating costs are not yet reconstructed, while early-retirement exposure remains outside the gap.

The independently selected support stress is:

`stress-adjusted gap = annual resource gap proxy − max(annual resource gap proxy, 0) × support-stress share`

The support axis must not be mechanically paired with the same-named resource case. It is a sensitivity, not observed cash support. A resource-saving negative gap is retained and receives no artificial subsidy.

## What can and cannot be published next

The next company output can publish annual resource-gap proxy, facility contributions, USD/tCO2 of modelled operational abatement, and the support amount required to close a chosen share of that proxy. It can also show how rankings change across resource and support axes.

It cannot yet publish an actual incentive-adjusted or realised net gap. Facility-level avoided compliance cost, realised green premium and verified support remain `NA`, never zero. The western-Japan subsidy application is only a multi-company project ceiling and is used to anchor a petrochemical stress case, not as realised Mitsui support.

## Quality and interpretation

- All new numeric route inputs are `Estimated`, quality D, with low/base/high values, units, price-year treatment, formula, rationale and source context.
- Verified market-policy fields are `Not_available` and carry the unresolved acquisition target.
- Variable-resource values are analyst screening proxies per operational tCO2 reduced; they are not published technology costs or system-abatement costs.
- Production leakage, replacement output, physical feasibility and system abatement remain outside this cost layer.

The generated route summary is `outputs/tables/route_annual_cost_gap_inputs_mvp.csv`. Facility and company aggregation is deliberately left to the next bounded model run.
