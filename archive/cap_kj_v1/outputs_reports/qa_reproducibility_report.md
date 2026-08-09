# Post-upgrade reconciliation and release-gap audit

**Internal consistency:** PASS  
**Public-release gate:** GATED  
**Overall diagnostic:** PASS WITH WARNINGS  
**Checks:** 22 pass, 7 warning, 0 fail  
**Scope:** isolated regeneration, cross-output boundary consistency and publication readiness of the current MVP; not external validation of engineering costs, contracts, policy eligibility or system abatement.

## Check results

| Check | Status | Detail |
|---|---|---|
| `required_files` | PASS | All declared MVP inputs and eight canonical tables exist. |
| `isolated_table_regeneration` | PASS | Eight tables rebuilt in a temporary directory match canonical outputs byte-for-byte. |
| `isolated_figure_regeneration` | PASS | All four investor figures regenerated from rebuilt tables and passed minimum file-size checks. |
| `screening_grain` | PASS | Screening outputs contain 25 facilities x 3 cases and four companies x 3 cases. |
| `screening_unique_keys` | PASS | Facility/case and company/case keys are unique. |
| `screening_reconciliation` | PASS | Six CAPEX and operational-emissions measures reconcile exactly from facilities to companies. |
| `screening_sensitivity_order` | PASS | Company CAPEX and operational abatement are monotonic across low/base/high cases. |
| `support_grain` | PASS | Support outputs contain 25 facilities x 3 assumptions x 4 mechanisms and four companies at the same cases. |
| `support_unique_keys` | PASS | Facility and company support keys are unique. |
| `support_reconciliation` | PASS | Six capital, support and abatement measures reconcile exactly from facilities to companies. |
| `abatement_status_trace` | PASS | Every positive additional operational-abatement row names a facility status change. |
| `support_sensitivity_order` | PASS | Support totals rise and residual common exposure falls monotonically across low/base/high mechanism assumptions. |
| `cost_gap_grain` | PASS | Cost-gap outputs contain 87 facility-variant-case rows and 15 company-variant-case rows. |
| `cost_gap_unique_keys` | PASS | Facility and company cost-gap keys are unique. |
| `cost_gap_reconciliation` | PASS | Six CAPEX, abatement, annual resource-gap and support-stress measures reconcile exactly from facilities to companies. |
| `cross_output_company_set` | PASS | Screening, support, cost and production tables all contain the fixed four-company sample. |
| `production_coverage_policy` | PASS | Nippon publishes 100% production coverage within the 2% tolerance; the other three companies remain NA and none is zero-filled. |
| `physical_constraint_reconciliation` | PASS | Gwangyang capacity coverage, full-route multiple and implied scrap demand reproduce from the disclosed capacity and allocated activity. |
| `boundary_guardrails` | PASS | System abatement remains not modelled and legacy pathway/support tables do not silently backfill production coverage. |
| `assumption_metadata` | PASS | All mechanism assumptions retain estimate label, range, unit, price-year treatment, formula, rationale and quality D. |
| `source_referential_integrity` | PASS | All external source IDs in processed inputs resolve to the source register. |
| `non_mitsui_cost_support_boundaries` | PASS | POSCO, Nippon and LOTTE primary cost/support emissions boundaries align within 0.1%. |
| `mitsui_support_boundary` | WARN | Mitsui primary cost coverage is 97.46% versus 85.00% in the legacy support experiment, a 12.46 percentage-point difference; exact combined support/cost claims are gated. |
| `production_coverage_completeness` | WARN | Production coverage is publishable for 1/4 companies; POSCO, LOTTE and Mitsui remain NA rather than zero. |
| `production_coverage_integration` | WARN | Nippon's new 100% production coverage is not yet propagated into the capital-allocation and support tables, which retain the older NA field. |
| `gwangyang_full_route_capacity` | WARN | The completed Gwangyang EAF covers only 13.15% of allocated base works activity; full-route project-backed CAPEX and abatement are gated. |
| `verified_net_gap_availability` | WARN | Verified incentive-adjusted cost gaps remain NA for all company cost rows; support amounts are sensitivities, not realised cash. |
| `system_abatement_availability` | WARN | System abatement remains unavailable because leakage and replacement production are not modelled. |
| `version_control_coverage` | WARN | 13 top-level status entries are untracked; reproducible files exist but are not yet protected by version history. |

## Sensitivity audit

| Company | CAPEX low/base/high | High ÷ low | BHL level support low/base/high | BHL residual exposure low/base/high |
|---|---:|---:|---:|---:|
| POSCO | $9.51/$18.15/$31.12bn | 3.27x | $0.000/$0.000/$0.000bn | 43.1%/23.1%/6.6% |
| Nippon Steel Corporation | $16.85/$26.97/$40.48bn | 2.40x | $0.000/$0.000/$0.000bn | 40.0%/20.0%/5.0% |
| LOTTE Chemical Corporation | $0.30/$0.75/$1.74bn | 5.83x | $0.224/$0.367/$0.523bn | 40.0%/20.0%/5.0% |
| Mitsui Chemicals, Inc. | $0.15/$0.49/$1.52bn | 10.21x | $0.148/$0.242/$0.345bn | 40.0%/20.0%/5.0% |

The CAPEX range is especially wide for LOTTE and Mitsui because the petrochemical screen uses a common annual-abatement CAPEX proxy. Their identical support-efficiency result is therefore mechanical, not evidence of equal project economics. Higher coverage assumptions reduce residual exposure monotonically, while level-support totals rise monotonically with the declared support-share range.

## Cross-output boundary matrix

| Company | Primary cost emissions coverage | Support-experiment coverage | Difference | Production coverage | Release use |
|---|---:|---:|---:|---:|---|
| POSCO | 100.00% | 100.00% | +0.00% | NA | aligned within 0.1% |
| Nippon Steel Corporation | 100.00% | 100.00% | -0.00% | 1 | aligned within 0.1% |
| LOTTE Chemical Corporation | 92.67% | 92.67% | +0.00% | NA | aligned within 0.1% |
| Mitsui Chemicals, Inc. | 97.46% | 85.00% | +12.46% | NA | do not combine exact support and cost amounts |

Mitsui's cost layer uses the official-registry bridge at 97.46% emissions coverage, while its support experiment still uses the 85.00% legacy allocation. The 12.46 percentage-point difference is a publication blocker for any exact combined Mitsui support/cost statement; the two panels may remain visible only as explicitly separated boundary views.

## Physical-pathway gate

The completed Gwangyang EAF covers 13.15% of the allocated base works activity, requiring 7.61x disclosed capacity for the current full-route screen. Its implied 2.0 Mt/year scrap demand is 97.5% of reported 2024 purchased scrap. Full-Gwangyang CAPEX and operational abatement remain potential pathway requirements, not project-backed allocations.

## Open release gaps

- `mitsui_support_boundary`: Mitsui primary cost coverage is 97.46% versus 85.00% in the legacy support experiment, a 12.46 percentage-point difference; exact combined support/cost claims are gated.
- `production_coverage_completeness`: Production coverage is publishable for 1/4 companies; POSCO, LOTTE and Mitsui remain NA rather than zero.
- `production_coverage_integration`: Nippon's new 100% production coverage is not yet propagated into the capital-allocation and support tables, which retain the older NA field.
- `gwangyang_full_route_capacity`: The completed Gwangyang EAF covers only 13.15% of allocated base works activity; full-route project-backed CAPEX and abatement are gated.
- `verified_net_gap_availability`: Verified incentive-adjusted cost gaps remain NA for all company cost rows; support amounts are sensitivities, not realised cash.
- `system_abatement_availability`: System abatement remains unavailable because leakage and replacement production are not modelled.
- `version_control_coverage`: 13 top-level status entries are untracked; reproducible files exist but are not yet protected by version history.

Facility calculations reconcile to company totals for capital, emissions, mechanism and annual resource-gap measures. Eight core tables regenerate byte-for-byte in an isolated directory. These internal passes do not override the open boundary and evidence gaps above.

## Canonical output hashes

- `company_annual_cost_gap_mvp.csv`: `bbf644acc8182e76cc3d2a149b053bed6cb75e54d239df919d9610691d0070ca`
- `company_capital_allocation_mvp.csv`: `3495a37df2545fd8a119242a9b28208aa344fc90fe06d53cfb1304f9de73b17b`
- `company_production_coverage_status_mvp.csv`: `639acc7d0e951e8151029cfc4c43ce3e5064726997f9db671f95000afec7ce86`
- `company_support_experiment_mvp.csv`: `bdb6ab5f180eeddb8b39cbb1345ca645a1c57e366c92316159bcde2594689224`
- `facility_annual_cost_gap_mvp.csv`: `06b3a043d17db175981223326034c5268ed98d494007b6ca48c8de23352a8e8b`
- `facility_capital_allocation_mvp.csv`: `326fe1f5cfea6e97f9baa340e1fd89919953b98ad0806b8a8b2a8bebc8432da8`
- `facility_physical_constraint_mvp.csv`: `c0f335fb1725fbcb13ae741150a3797bd27cfcb0158af819e2c100dcf32df72b`
- `facility_support_experiment_mvp.csv`: `0e0778a9586ef8646fc10c002f3d0501a423bfebfd1dadc3aa1e1e88a6a1d9f9`

## Reproduction

Run `PYTHONPATH=src python3 -m cap_kj.qa --root .`. The command rebuilds eight screening, support, cost-gap, production and constraint tables in a temporary directory, compares them to canonical CSV outputs, regenerates the four original investor figures, and rewrites this report and `outputs/diagnostics/qa_checks.csv`.
