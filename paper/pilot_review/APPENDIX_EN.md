\pagebreak

### Appendix C Data, variables and calculations

This appendix documents every dataset, field and stored array in the bounded evidence package supporting this review paper. It separates observations, explicit assumptions, computed quantities and diagnostic metadata. It does not claim to document every unrelated experiment in the repository.

Reading order: 1 evidence map; 2 fixed inputs and source quantities; 3 formulas with variable definitions; 4 complete field dictionary; 5 file/array catalogue and audit. Raw historical rows and Monte Carlo draws are preserved without rounding in PLANiT_Pilot_Data_Appendix.zip. The Word tables make the calculation understandable; the companion originals contain every recorded value, not merely representative samples.

Dataset IDs DSxxx identify exact files. F01–F36 identify calculations. A field with several currency contexts inherits its dataset unit; a blank source value is not zero. Input tables below display readable precision; full source precision is retained in the archive. Package presence is not evidence that an inactive option was used.

| Evidence | Use in paper | Equations / boundary |
| --- | --- | --- |
| D1 / CORP | Appendix A; contract versus physical choices | F01–18; billion declared KRW |
| D2 / PRICE | Scenario nodes, historical shocks, assumptions figures | F09–13; source units → ratios |
| D3 / NCC | Main TCaR figure, timing, emissions gates; lifetime example | F18–23; million assumed EUR |
| D4 / STEEL | Pellet loading and tail exposure | F29–31; absolute million source EUR |
| D5 / FX | Invoice accounting demonstration | F32–33; explicitly dated currencies |
| D6–7 / REVIEW | Timing decomposition, CCS physical/policy choices | F23–28; same-output comparisons |
| CCS | Source cash package plus later physical audit | F24–28; million source USD |
| FIGURE | Unrounded data behind Figures 1–5 | Figure 6 is proposed architecture, no numeric model output |

\pagebreak

### 1. Reproducibility and status

The inventory contains 222 files, 1357 file–field occurrences, 462 distinct field names, and 73 named arrays. SHA-256 is recorded for every file. The catalogue includes source observations, calculation inputs, frozen results, validation records and current implementation snapshots; their roles differ.

Historical manifests are retained verbatim. Five earlier hash declarations differ from the current referenced files: two implementation files (e5_metrics.py, plancost.py) and three manuscripts revised in later review cycles. A historical manifest is not silently rewritten. Current code snapshots are labeled current, not represented as the exact historical executable. Frozen inputs/results and independent arithmetic checks are the evidence for this paper; a bit-for-bit full historic rerun is not asserted.

The source registries can contain unused items: D3b bands are evidence/sensitivity records, D5 support is inactive with support=none, D6 finances are contextual, and D7 disclosed plans are not candidates in this frozen comparison. NCC battery, wind, PV and tank source rows are retained but not charged in the timing ledger. CCS older source-status flags are preserved; the later selected-page audit takes precedence only for the explicitly reconciled physical fields.

\pagebreak

### 2. Fixed inputs and complete source specifications

### 2.1 Company configuration

DS078 · tmp/research_case_expanded/config.yaml

| Configuration key | Frozen value |
| --- | --- |
| data_dir | /Users/jinsu/Documents/GitHub/cap_finance/tmp/research_case_v3/data |
| out_dir | /Users/jinsu/Documents/GitHub/cap_finance/tmp/research_case_expanded/run |
| seed | 20260806 |
| years.start | 2027 |
| years.end | 2050 |
| scenarios | ["NZ15", "B20"] |
| support_scenarios | ["none"] |
| discount_rate | 0.05 |
| discount_rate_sensitivity | [0.035, 0.065] |
| simulation.n_sims | 10000 |
| simulation.n_sims_flex | 1500 |
| simulation.convergence_check_n | 2000 |
| price_process | gbm |
| ou_halflife_years | 10 |
| shock_normalisation | mean |
| milp.frontier_points | 6 |
| milp.solver_time_limit_s | 30 |
| milp.mip_gap_rel | 0.02 |
| milp.solver_threads | 1 |
| milp.reinvest_window_halfwidth | 1 |
| milp.budget_violation_floor_thkrw | 300 |
| milp.retire_max_share | 0 |
| carbon_auction_share.2025 | 0.1 |
| carbon_auction_share.2030 | 0.15 |
| carbon_auction_share.2035 | 0.3 |
| carbon_auction_share.2040 | 0.5 |
| carbon_auction_share.2045 | 0.75 |
| carbon_auction_share.2050 | 1 |
| contracts.ppa_premium_pct | 0.08 |
| contracts.epc_premium_pct | 0.1 |
| contracts.ccfd_fee_pct | 0.03 |
| hydrogen.kwh_per_kg | 52 |
| hydrogen.electrolyzer_capex_amort | 0.12 |
| hydrogen.electrolyzer_kg_per_kw_yr | 150 |
| budget_scaling | intensity_ratio |
| capital_accounting | cash_v1 |
| energy_balance_mode | explicit_retention |
| carbon_accounting_mode | gross_obligation_proxy |
| transition_loss_basis | incremental_cash |
| plan_selection_criterion | mean |
| financial_boundary_mode | strict |
| scenario_base_year | 2025 |
| include_capital_renewals | True |
| terminal_value_rule | none |
| budget_mode | cumulative_hard |
| candidate_contracts | unhedged |
| information_cutoff | 2026-09-05 |
| monetary_basis | declared_KRW_2025_proxy_not_all_source_deflators_verified |
| case_scope | company_informed_modeled_legacy_asset_portfolios |
| scenario_evidence | EST_v0_illustrative_not_downloaded_GCAM_or_NGFS |
| candidate_expansion_emissions_points | 4 |

These are the complete saved configuration leaves. Solver settings concern finite candidate generation; price-process alternatives, support settings and hydrogen fallback coefficients are not all active in the baseline. Missing capex_shock_scaling resolves to the code default positive_lognormal. Annual date 2027 is deterministic; the price path has 24 columns.

\pagebreak

### 2.2 Calibration and all technology options

DS129 · tmp/research_case_expanded/run/e3/calibration_report.csv

| Parameter | Value |
| --- | --- |
| vol_elec | 0.242447 |
| vol_h2 | 0.25 |
| vol_capex | 0.06 |
| electrolyzer_decline | 0.05 |
| electrolyzer_vol | 0.1 |
| corr_elec_capex | 0 |
| sim_vol_elec | 0.242238 |
| sim_vol_h2 | 0.250225 |
| sim_vol_capex | 0.0598984 |

Correlation (electricity, H2, construction): [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]; factor volatility: {"elec": 0.24244650997167314, "h2": 0.25, "capex": 0.06, "electrolyzer": 0.1}

Electricity σ=0.24244650997167314 is a pooled short-series statistic; H2 .25 and construction .06 are fallback priors. Electrolyser trend decline .05 and residual σ .10 are separate assumptions. Central h2_price/re_price values in D2b take precedence over fallback equations. Where hydrogen fallback is needed: H2 price = electricity price ×52/1000 + electrolyser KRW/kW ×.12/150; electrolyser central level decays exponentially from its last recorded anchor.

DS139 · tmp/research_case_v3/data/D3_tech_options.csv

Cost: thousand KRW per annual capacity / annual capacity per year / actual tonne, respectively.

| tech_id | applies_to_unit | capex_unit | opex_fixed | opex_var |
| --- | --- | --- | --- | --- |
| steel_eaf | NONE | 240 | 0 | 0 |
| steel_h2dri | BF | 863 | 102 | 69 |
| steel_eff | BF | 120 | 0 | 6 |
| petchem_h2fuel | NCC | 68 | 0 | 5 |
| petchem_bio | NCC | 0 | 0 | 579 |
| petchem_eff | NCC | 60 | 0 | 0 |
| steel_h2inj | BF | 54 | 1 | 5 |
| steel_scrap | BF | 20 | 0.5 | 10 |
| steel_hbi | BF | 20 | 0.5 | 62 |
| steel_hyrex | FINEX | 863 | 102 | 39 |
| petchem_ecracker_hybrid | NCC | 270 | 8 | 10 |
| petchem_ecracker | NCC | 608 | 18 | 20 |
| petchem_hp_whr | NCC | 72 | 2 | 0 |

MWh/t product; kg purchased H2/t product; tCO2/t product.

| tech_id | elec_intensity | h2_intensity | emission_factor |
| --- | --- | --- | --- |
| steel_eaf | 0.667 | 0 | 0.05 |
| steel_h2dri | 0.85 | 51 | 0.053 |
| steel_eff | 0 | 0 | 1.6 |
| petchem_h2fuel | 0 | 83 | 0.48 |
| petchem_bio | 0 | 0 | 0.865 |
| petchem_eff | 0 | 0 | 0.92 |
| steel_h2inj | 0.05 | 28 | 1.72 |
| steel_scrap | 0.02 | 0 | 1.88 |
| steel_hbi | 0 | 0 | 1.72 |
| steel_hyrex | 0.85 | 51 | 0.05 |
| petchem_ecracker_hybrid | 1 | 0 | 0.65 |
| petchem_ecracker | 2.8 | 0 | 0.1 |
| petchem_hp_whr | 0.19 | 0 | 0.845 |

Calendar year; construction years; life years; relative uncertainty band %.

| tech_id | avail_year | build_years | lifetime | capex_uncertainty |
| --- | --- | --- | --- | --- |
| steel_eaf | 2024 | 3 | 20 | 60 |
| steel_h2dri | 2030 | 4 | 20 | 40 |
| steel_eff | 2024 | 1 | 15 | 50 |
| petchem_h2fuel | 2028 | 2 | 20 | 60 |
| petchem_bio | 2025 | 0 | 20 | 30 |
| petchem_eff | 2024 | 1 | 15 | 40 |
| steel_h2inj | 2030 | 2 | 20 | 50 |
| steel_scrap | 2025 | 1 | 15 | 30 |
| steel_hbi | 2025 | 1 | 20 | 30 |
| steel_hyrex | 2035 | 3 | 25 | 50 |
| petchem_ecracker_hybrid | 2027 | 2 | 25 | 40 |
| petchem_ecracker | 2030 | 2 | 25 | 40 |
| petchem_hp_whr | 2025 | 1 | 20 | 30 |

Flag 0/1; purchased-energy retention fractions. Source assumptions, not inferred from emissions.

| tech_id | retrofit | retained_coal_fraction | retained_gas_fraction | retained_grid_fraction |
| --- | --- | --- | --- | --- |
| steel_eaf | 0 | 0 | 0 | 0 |
| steel_h2dri | 0 | 0 | 0 | 0 |
| steel_eff | 1 | 1 | 1 | 1 |
| petchem_h2fuel | 1 | 1 | 0.5 | 1 |
| petchem_bio | 1 | 1 | 1 | 1 |
| petchem_eff | 1 | 1 | 1 | 1 |
| steel_h2inj | 1 | 1 | 1 | 1 |
| steel_scrap | 1 | 1 | 1 | 1 |
| steel_hbi | 1 | 1 | 1 | 1 |
| steel_hyrex | 0 | 0 | 0 | 0 |
| petchem_ecracker_hybrid | 1 | 1 | 0.6 | 1 |
| petchem_ecracker | 0 | 0 | 0 | 0 |
| petchem_hp_whr | 1 | 1 | 1 | 1 |

Every technology row is shown, including steel_eaf with applies_to_unit=NONE (unavailable to this asset menu). Full source_id and retention_evidence_status strings remain in the original CSV and field dictionary. Cost and energy figures are modeling inputs with mixed evidence quality, not verified quotations.

\pagebreak

### 2.3 Every model asset and its averaged operating inputs

DS135 · tmp/research_case_v3/data/D1a_facility_static.csv

DS136 · tmp/research_case_v3/data/D1b_facility_panel.csv

All 22 assets are listed. Operating columns average all three stored years; the 66 original annual records are in the package. Product-capacity unit labels and source allocation caveats are retained in D1a/D1b and are not converted to one verified product definition. Electricity is MWh/year, coal/gas GJ/year, Scope 1 tCO2/year. Capacity and production are source/model tonnes with different product scopes.

| facility_id | capacity | production | emissions_s1 |
| --- | --- | --- | --- |
| POSCO_POH_BF2 | 2.329e+06 | 2.16642e+06 | 4.55594e+06 |
| POSCO_POH_BF3 | 5.11467e+06 | 4.75763e+06 | 1.00052e+07 |
| POSCO_POH_BF4 | 5.11467e+06 | 4.75763e+06 | 1.00052e+07 |
| POSCO_GWY_BF1 | 5.48e+06 | 5.09746e+06 | 1.07199e+07 |
| POSCO_GWY_BF3 | 5.02333e+06 | 4.67267e+06 | 9.82654e+06 |
| POSCO_GWY_BF4 | 5.02333e+06 | 4.67267e+06 | 9.82654e+06 |
| POSCO_GWY_BF5 | 5.02333e+06 | 4.67267e+06 | 9.82654e+06 |
| POSCO_POH_FINEX3 | 2e+06 | 1.86039e+06 | 3.73039e+06 |
| NSC_MUR_BF2 | 2.75279e+06 | 2.14229e+06 | 3.95384e+06 |
| NSC_KAS_BF1 | 4.9046e+06 | 3.81689e+06 | 7.04451e+06 |
| NSC_KIM_BF2 | 4.11e+06 | 3.19851e+06 | 5.88037e+06 |
| NSC_KIM_BF4 | 5.07357e+06 | 3.94838e+06 | 7.25899e+06 |
| NSC_NGO_BF1 | 4.97127e+06 | 3.86877e+06 | 6.70555e+06 |
| NSC_NGO_BF3 | 4.0415e+06 | 3.1452e+06 | 5.45141e+06 |
| NSC_WAK_BF2 | 3.37933e+06 | 2.62989e+06 | 4.52765e+06 |
| NSC_TOB_BF4 | 4.56667e+06 | 3.5539e+06 | 8.32271e+06 |
| NSC_OIT_BF1 | 5.2745e+06 | 4.10475e+06 | 7.27666e+06 |
| NSC_OIT_BF2 | 5.2745e+06 | 4.10475e+06 | 7.27666e+06 |
| LOTTE_YEO_NCC | 1.23e+06 | 1.107e+06 | 1.05165e+06 |
| LOTTE_DAE_NCC | 1.1e+06 | 990,000 | 940,500 |
| MCI_ICH_CR | 553,000 | 497,700 | 472,815 |
| MCI_OSK_CR | 455,000 | 409,500 | 389,025 |

\pagebreak

### Asset inputs continued 2

| facility_id | energy_elec | energy_coal | energy_gas |
| --- | --- | --- | --- |
| POSCO_POH_BF2 | 173,314 | 2.92467e+07 | 866,568 |
| POSCO_POH_BF3 | 380,610 | 6.4228e+07 | 1.90305e+06 |
| POSCO_POH_BF4 | 380,610 | 6.4228e+07 | 1.90305e+06 |
| POSCO_GWY_BF1 | 407,797 | 6.88157e+07 | 2.03898e+06 |
| POSCO_GWY_BF3 | 373,813 | 6.3081e+07 | 1.86907e+06 |
| POSCO_GWY_BF4 | 373,813 | 6.3081e+07 | 1.86907e+06 |
| POSCO_GWY_BF5 | 373,813 | 6.3081e+07 | 1.86907e+06 |
| POSCO_POH_FINEX3 | 186,039 | 2.4185e+07 | 744,154 |
| NSC_MUR_BF2 | 171,383 | 2.89209e+07 | 856,916 |
| NSC_KAS_BF1 | 305,351 | 5.1528e+07 | 1.52675e+06 |
| NSC_KIM_BF2 | 255,881 | 4.31799e+07 | 1.2794e+06 |
| NSC_KIM_BF4 | 315,871 | 5.33032e+07 | 1.57935e+06 |
| NSC_NGO_BF1 | 309,502 | 5.22285e+07 | 1.54751e+06 |
| NSC_NGO_BF3 | 251,616 | 4.24602e+07 | 1.25808e+06 |
| NSC_WAK_BF2 | 210,391 | 3.55034e+07 | 1.05195e+06 |
| NSC_TOB_BF4 | 284,312 | 4.79776e+07 | 1.42156e+06 |
| NSC_OIT_BF1 | 328,380 | 5.54142e+07 | 1.6419e+06 |
| NSC_OIT_BF2 | 328,380 | 5.54142e+07 | 1.6419e+06 |
| LOTTE_YEO_NCC | 387,450 | 0 | 8.856e+06 |
| LOTTE_DAE_NCC | 346,500 | 0 | 7.92e+06 |
| MCI_ICH_CR | 174,195 | 0 | 3.9816e+06 |
| MCI_OSK_CR | 143,325 | 0 | 3.276e+06 |

\pagebreak

### Asset inputs continued 3

| facility_id | commissioning_year | last_reline_year | reinvest_cycle_yr | incumbent_capex_unit | margin_kthou_t |
| --- | --- | --- | --- | --- | --- |
| POSCO_POH_BF2 | 1976.0 | 2,015 | 15 | 200 | 70 |
| POSCO_POH_BF3 | 1978.0 | 2,017 | 15 | 200 | 70 |
| POSCO_POH_BF4 | 1981.0 | 2,024 | 15 | 200 | 70 |
| POSCO_GWY_BF1 | 1987.0 | 2,013 | 15 | 200 | 70 |
| POSCO_GWY_BF3 | 1990.0 | 2,020 | 15 | 200 | 70 |
| POSCO_GWY_BF4 | 1992.0 | 2,022 | 15 | 200 | 70 |
| POSCO_GWY_BF5 | 2000.0 | 2,016 | 15 | 200 | 70 |
| POSCO_POH_FINEX3 | 2014.0 | 2,014 | 20 | 300 | 70 |
| NSC_MUR_BF2 |  | 2,020 | 20 | 200 | 70 |
| NSC_KAS_BF1 |  | 2,004 | 20 | 200 | 70 |
| NSC_KIM_BF2 |  | 2,012 | 20 | 200 | 70 |
| NSC_KIM_BF4 |  | 2,003 | 20 | 200 | 70 |
| NSC_NGO_BF1 |  | 2,007 | 20 | 200 | 70 |
| NSC_NGO_BF3 |  | 2,022 | 20 | 200 | 70 |
| NSC_WAK_BF2 | 2019.0 | 2,019 | 20 | 200 | 70 |
| NSC_TOB_BF4 |  | 2,014 | 20 | 200 | 70 |
| NSC_OIT_BF1 |  | 2,009 | 20 | 200 | 70 |
| NSC_OIT_BF2 |  | 2,004 | 20 | 200 | 70 |
| LOTTE_YEO_NCC | 1992.0 | 2,026 | 4 | 150 | 290 |
| LOTTE_DAE_NCC | 1991.0 | 2,025 | 4 | 150 | 290 |
| MCI_ICH_CR | 1978.0 | 1,978 | 4 | 150 | 290 |
| MCI_OSK_CR | 1970.0 | 2,024 | 4 | 150 | 290 |

\pagebreak

### 2.4 Company scenario anchors and budgets

DS138 · tmp/research_case_v3/data/D2b_scenario_prices.csv

| Series / unit | All year:value anchors |
| --- | --- |
| B20 / Japan / co2_price / KRW/tCO2 | 2025: 27000.0; 2030: 39825.0; 2035: 52650.0; 2040: 82350.0; 2045: 112050.0; 2050: 141750.0 |
| B20 / Japan / coal_price / KRW/t | 2025: 197640.0; 2030: 166320.0; 2035: 135000.0; 2040: 127845.0; 2045: 120555.0; 2050: 113400.0 |
| B20 / Japan / elec_price / KRW/MWh | 2025: 119599.99999999999; 2030: 135240.0; 2035: 126959.99999999999; 2040: 118679.99999999999; 2045: 118679.99999999999; 2050: 118679.99999999999 |
| B20 / Japan / gas_price / KRW/t | 2025: 912600.0; 2030: 751140.0; 2035: 589680.0; 2040: 617760.0; 2045: 652860.0; 2050: 680940.0 |
| B20 / Japan / h2_price / KRW/kg | 2025: 10239.599999999999; 2030: 3532.662; 2035: 3235.7136; 2040: 2938.7652000000003; 2045: 2652.0564; 2050: 2355.1079999999997 |
| B20 / Japan / re_price / KRW/MWh | 2025: 198000.0; 2026: 198000.0; 2027: 198000.0; 2028: 198000.0; 2029: 198000.0; 2030: 198000.0; 2031: 198000.0; 2032: 198000.0; 2033: 198000.0; 2034: 198000.0; 2035: 198000.0; 2036: 198000.0; 2037: 198000.0; 2038: 198000.0; 2039: 198000.0; 2040: 198000.0; 2041: 198000.0; 2042: 198000.0; 2043: 198000.0; 2044: 198000.0; 2045: 198000.0; 2046: 198000.0; 2047: 198000.0; 2048: 198000.0; 2049: 198000.0; 2050: 198000.0 |
| B20 / Korea / co2_price / KRW/tCO2 | 2025: 9450.0; 2030: 39825.0; 2035: 70200.0; 2040: 83700.0; 2045: 92475.0; 2050: 101250.0 |
| B20 / Korea / coal_price / KRW/t | 2025: 197640.0; 2030: 166320.0; 2035: 135000.0; 2040: 127845.0; 2045: 120555.0; 2050: 113400.0 |
| B20 / Korea / elec_price / KRW/MWh | 2025: 110200.0; 2030: 117400.0; 2035: 124600.0; 2040: 131900.0; 2045: 139100.0; 2050: 146300.0 |
| B20 / Korea / gas_price / KRW/t | 2025: 912600.0; 2030: 751140.0; 2035: 589680.0; 2040: 617760.0; 2045: 652860.0; 2050: 680940.0 |
| B20 / Korea / h2_price / KRW/kg | 2025: ; 2030: 4025.0; 2035: 3737.5; 2040: 3450.0; 2045: 3162.5; 2050: 2875.0 |
| B20 / Korea / re_price / KRW/MWh | 2025: 175000.0; 2026: 175000.0; 2027: 175000.0; 2028: 175000.0; 2029: 175000.0; 2030: 175000.0; 2031: 175000.0; 2032: 175000.0; 2033: 175000.0; 2034: 175000.0; 2035: 175000.0; 2036: 175000.0; 2037: 175000.0; 2038: 175000.0; 2039: 175000.0; 2040: 175000.0; 2041: 175000.0; 2042: 175000.0; 2043: 175000.0; 2044: 175000.0; 2045: 175000.0; 2046: 175000.0; 2047: 175000.0; 2048: 175000.0; 2049: 175000.0; 2050: 175000.0 |
| NZ15 / Japan / co2_price / KRW/tCO2 | 2025: 27000.0; 2030: 135000.0; 2035: 243000.0; 2040: 276750.0; 2045: 307125.0; 2050: 337500.0 |
| NZ15 / Japan / coal_price / KRW/t | 2025: 192375.0; 2030: 134595.0; 2035: 76950.0; 2040: 73305.0; 2045: 69795.0; 2050: 66150.0 |
| NZ15 / Japan / elec_price / KRW/MWh | 2025: 119599.99999999999; 2030: 135240.0; 2035: 126959.99999999999; 2040: 118679.99999999999; 2045: 118679.99999999999; 2050: 118679.99999999999 |
| NZ15 / Japan / gas_price / KRW/t | 2025: 891540.0; 2030: 617760.0; 2035: 343980.0; 2040: 343980.0; 2045: 343980.0; 2050: 343980.0 |
| NZ15 / Japan / h2_price / KRW/kg | 2025: 10239.599999999999; 2030: 3071.88; 2035: 2815.8900000000003; 2040: 2559.8999999999996; 2045: 2303.91; 2050: 2047.92 |
| NZ15 / Japan / re_price / KRW/MWh | 2025: 198000.0; 2026: 198000.0; 2027: 198000.0; 2028: 198000.0; 2029: 198000.0; 2030: 198000.0; 2031: 198000.0; 2032: 198000.0; 2033: 198000.0; 2034: 198000.0; 2035: 198000.0; 2036: 198000.0; 2037: 198000.0; 2038: 198000.0; 2039: 198000.0; 2040: 198000.0; 2041: 198000.0; 2042: 198000.0; 2043: 198000.0; 2044: 198000.0; 2045: 198000.0; 2046: 198000.0; 2047: 198000.0; 2048: 198000.0; 2049: 198000.0; 2050: 198000.0 |
| NZ15 / Korea / co2_price / KRW/tCO2 | 2025: 9450.0; 2030: 189000.0; 2035: 243000.0; 2040: 276750.0; 2045: 306450.0; 2050: 337500.0 |
| NZ15 / Korea / coal_price / KRW/t | 2025: 192375.0; 2030: 134595.0; 2035: 76950.0; 2040: 73305.0; 2045: 69795.0; 2050: 66150.0 |
| NZ15 / Korea / elec_price / KRW/MWh | 2025: 110200.0; 2030: 123200.0; 2035: 136200.0; 2040: 149300.0; 2045: 162300.0; 2050: 175300.0 |
| NZ15 / Korea / gas_price / KRW/t | 2025: 891540.0; 2030: 617760.0; 2035: 343980.0; 2040: 343980.0; 2045: 343980.0; 2050: 343980.0 |
| NZ15 / Korea / h2_price / KRW/kg | 2025: ; 2030: 3500.0; 2035: 3250.0; 2040: 3000.0; 2045: 2750.0; 2050: 2500.0 |
| NZ15 / Korea / re_price / KRW/MWh | 2025: 175000.0; 2026: 175000.0; 2027: 175000.0; 2028: 175000.0; 2029: 175000.0; 2030: 175000.0; 2031: 175000.0; 2032: 175000.0; 2033: 175000.0; 2034: 175000.0; 2035: 175000.0; 2036: 175000.0; 2037: 175000.0; 2038: 175000.0; 2039: 175000.0; 2040: 175000.0; 2041: 175000.0; 2042: 175000.0; 2043: 175000.0; 2044: 175000.0; 2045: 175000.0; 2046: 175000.0; 2047: 175000.0; 2048: 175000.0; 2049: 175000.0; 2050: 175000.0 |

\pagebreak

### All company budget anchors

DS137 · tmp/research_case_v3/data/D2a_scenario_budget.csv

| Series / unit | All year:value anchors |
| --- | --- |
| B20 / Japan / petchem | 2025: 49.1; 2030: 43.1; 2035: 37; 2040: 30.9; 2045: 24.9; 2050: 18.8 |
| B20 / Japan / steel | 2025: 144.9; 2030: 127.5; 2035: 110.2; 2040: 92.9; 2045: 75.6; 2050: 58.3 |
| B20 / Korea / petchem | 2025: 58.6; 2030: 50.7; 2035: 42.7; 2040: 34.8; 2045: 26.8; 2050: 18.8 |
| B20 / Korea / steel | 2025: 94.5; 2030: 81.6; 2035: 68.8; 2040: 56; 2045: 43.2; 2050: 30.4 |
| NZ15 / Japan / petchem | 2025: 49.1; 2030: 42.6; 2035: 31.9; 2040: 21.3; 2045: 10.6; 2050: 0 |
| NZ15 / Japan / steel | 2025: 144.9; 2030: 127.5; 2035: 102.1; 2040: 68.1; 2045: 34; 2050: 0 |
| NZ15 / Korea / petchem | 2025: 58.6; 2030: 50.7; 2035: 42.7; 2040: 34.8; 2045: 26.6; 2050: 16.9 |
| NZ15 / Korea / steel | 2025: 94.5; 2030: 81.6; 2035: 68.4; 2040: 47.1; 2045: 25.9; 2050: 4.6 |

\pagebreak

### 2.5 IEA nodes and World Bank transformations

DS185 · data/research_v2/iea_2025_scenarios/curves.json

| Series / region / scenario | Unit | 2024 | 2035 | 2050 |
| --- | --- | --- | --- | --- |
| crude_oil / IEA_import_average / CPS | USD2024/barrel | 79 | 89 | 106 |
| crude_oil / IEA_import_average / STEPS | USD2024/barrel | 79 | 80 | 76 |
| crude_oil / IEA_import_average / NZE | USD2024/barrel | 79 | 33 | 25 |
| natural_gas / United States / CPS | USD2024/MMBtu_unspecified | 2.2 | 4.5 | 5 |
| natural_gas / United States / STEPS | USD2024/MMBtu_unspecified | 2.2 | 3.9 | 4.6 |
| natural_gas / United States / NZE | USD2024/MMBtu_unspecified | 2.2 | 2.1 | 2.2 |
| natural_gas / European Union / CPS | USD2024/MMBtu_unspecified | 10.3 | 9.1 | 10.6 |
| natural_gas / European Union / STEPS | USD2024/MMBtu_unspecified | 10.3 | 6.5 | 8.4 |
| natural_gas / European Union / NZE | USD2024/MMBtu_unspecified | 10.3 | 4.2 | 4 |
| natural_gas / China / CPS | USD2024/MMBtu_unspecified | 10.3 | 9.9 | 11.2 |
| natural_gas / China / STEPS | USD2024/MMBtu_unspecified | 10.3 | 7.5 | 9.1 |
| natural_gas / China / NZE | USD2024/MMBtu_unspecified | 10.3 | 4.9 | 4.8 |
| natural_gas / Japan / CPS | USD2024/MMBtu_unspecified | 13.5 | 11.2 | 12.9 |
| natural_gas / Japan / STEPS | USD2024/MMBtu_unspecified | 13.5 | 8.4 | 9.7 |
| natural_gas / Japan / NZE | USD2024/MMBtu_unspecified | 13.5 | 4.9 | 4.9 |
| steam_coal / United States / CPS | USD2024/t_steam_coal_6000kcal_kg | 56 | 56 | 53 |
| steam_coal / United States / STEPS | USD2024/t_steam_coal_6000kcal_kg | 56 | 41 | 41 |
| steam_coal / United States / NZE | USD2024/t_steam_coal_6000kcal_kg | 56 | 25 | 23 |
| steam_coal / European Union / CPS | USD2024/t_steam_coal_6000kcal_kg | 112 | 92 | 82 |
| steam_coal / European Union / STEPS | USD2024/t_steam_coal_6000kcal_kg | 112 | 78 | 66 |
| steam_coal / European Union / NZE | USD2024/t_steam_coal_6000kcal_kg | 112 | 47 | 39 |
| steam_coal / Japan / CPS | USD2024/t_steam_coal_6000kcal_kg | 151 | 112 | 105 |
| steam_coal / Japan / STEPS | USD2024/t_steam_coal_6000kcal_kg | 151 | 100 | 84 |
| steam_coal / Japan / NZE | USD2024/t_steam_coal_6000kcal_kg | 151 | 57 | 49 |
| steam_coal / Coastal China / CPS | USD2024/t_steam_coal_6000kcal_kg | 131 | 115 | 105 |
| steam_coal / Coastal China / STEPS | USD2024/t_steam_coal_6000kcal_kg | 131 | 99 | 84 |
| steam_coal / Coastal China / NZE | USD2024/t_steam_coal_6000kcal_kg | 131 | 59 | 49 |

All 27 saved curves are shown, including source series not selected in Figures 2 or individual process runs. Source values are 2024 USD; only within-series ratios are mapped onto the assumed plant price anchors. The World Bank full extracted table has 4,800 rows (six series through August 2026). The chosen 2010–2025 window has 192 monthly prices per series and yields 191×6 log-return inputs. Subsequent observations are excluded from calibration. Raw descriptions, missing markers and the source comparison warning are retained.

\pagebreak

### 2.6 NCC source observations and assumptions

DS182 · data/research_v2/tiggeloven_reference/source_observations.csv

| Case / source item | Value | Unit / PDF page |
| --- | --- | --- |
| conventional / cracker_methane_consumption | 1.868 | kWh/kg_naphtha / p4 |
| conventional / cracker_superheated_steam_production | 0.841 | kWh/kg_naphtha / p4 |
| conventional / compression_superheated_steam_consumption | 0.431 | kWh/kg_naphtha / p4 |
| conventional / separation_saturated_steam_consumption | 0.492 | kWh/kg_naphtha / p4 |
| conventional / separation_electricity_consumption | 0.083 | kWh/kg_naphtha / p4 |
| conventional / separation_methane_production | 2.349 | kWh/kg_naphtha / p4 |
| conventional / ethylene_yield | 0.303 | kg_ethylene/kg_naphtha / p4 |
| electric / cracker_electricity_consumption | 1.476 | kWh/kg_naphtha / p4 |
| electric / cracker_saturated_steam_production | 0.542 | kWh/kg_naphtha / p4 |
| electric / compression_electricity_consumption | 0.383 | kWh/kg_naphtha / p4 |
| electric / separation_saturated_steam_consumption | 0.492 | kWh/kg_naphtha / p4 |
| electric / separation_electricity_consumption | 0.083 | kWh/kg_naphtha / p4 |
| electric / separation_methane_production | 2.349 | kWh/kg_naphtha / p4 |
| electric / ethylene_yield | 0.303 | kg_ethylene/kg_naphtha / p4 |
| conventional / TOC_slope | 5,126 | EUR2019/(kg_ethylene/h) / p10 |
| conventional / TOC_intercept | 405 | million_EUR2019 / p10 |
| conventional / maintenance_fraction_printed | 0.04 | table_header_percent / p10 |
| electric / TOC_slope | 5,126 | EUR2019/(kg_ethylene/h) / p10 |
| electric / TOC_intercept | 405 | million_EUR2019 / p10 |
| electric / maintenance_fraction_printed | 0.02 | table_header_percent / p10 |
| gas_boiler / TOC_slope | 72.1 | EUR2019/(kW_steam) / p10 |
| gas_boiler / maintenance_fraction_printed | 0.04 | table_header_percent / p10 |
| ethylene_tank / TOC_slope | 19.5 | EUR2019/(kg_ethylene) / p10 |
| ethylene_tank / maintenance_fraction_printed | 0.02 | table_header_percent / p10 |
| Li_ion / TOC_slope | 168.9 | EUR2019/(kWh) / p10 |
| Li_ion / maintenance_fraction_printed | 0.01 | table_header_percent / p10 |
| wind_8_4MW / TOC_slope | 2.38e+07 | EUR2019/(turbine) / p10 |
| wind_8_4MW / maintenance_fraction_printed | 0.02 | table_header_percent / p10 |
| PV / TOC_slope | 188.2 | EUR2019/(m2) / p10 |
| PV / maintenance_fraction_printed | 0.01 | table_header_percent / p10 |
| gas_boiler / lifetime | 25 | years / p11 |
| PV / lifetime | 25 | years / p11 |
| wind_8_4MW / lifetime | 25 | years / p11 |
| ethylene_tank / lifetime | 15 | years / p11 |
| Li_ion / lifetime | 15 | years / p11 |
| gas_boiler / efficiency | 92 | percent / p11 |
| conventional / reported_pyrolysis_separation_SEC | 2.44 | kWh/kg_naphtha / p4 |
| electric / reported_pyrolysis_separation_SEC | 2.05 | kWh/kg_naphtha / p6 |
| both / reference_capacity | 115 | t_ethylene/h / p6 |

DS174 · data/research_v2/ncc_timing_frontier/manifest.json

| Assumption key | Complete saved value |
| --- | --- |
| scenario | IEA2025 STEPS ratios |
| historical_source | WB6monthly2010-2025demeanedlogreturns |
| shock | common overlapping noncircular block12; exact expected multiplier1 |
| price_basis | EUR2019 assumed real operating-price basis; not market quotations |
| electricity_central | 100*(0.5+0.5*JapanLNGscenarioRatio) |
| methane_central | 40*JapanLNGscenarioRatio |
| naphtha_central | 600*BrentscenarioRatio |
| discount | 0.05 |
| carbon_cost_excluded | True |
| emissions_ledger | reported direct0.397/assumed0 tCO2 per t naphtha + modeled purchased power + explicit common residual |
| grid_conditions | linear2027initial0.2or0.4 to2050zero; not national pathways; same price conditions held fixed |
| residual_per_t_naphtha | [0, 0.05] |
| cumulative_cap | 75% of same-condition continue-existing cumulative emissions |
| terminal_cap | 0 |
| annual_comparator | linear2027baseline to2050zero; separately tested, not implied by cumulative cap |
| commission_dates | [2030, 2035, 2040, 2045] |
| old_remaining_life | 8 |
| replacement_cost_scale | 1 |
| zero_downtime | True |
| common_output_t_per_year | 920000 |
| newplant_life | 20 |
| construction_years | 3 |
| terminal_cash_receipt | 0 |
| adaptation_to_observed_prices | False |
| excluded_other_costs | ["labour", "working capital", "tax", "financing", "other coproduct revenues", "closure salvage"] |
| grid_residual_probabilities_assigned | False |

DS166 · data/research_v2/ncc_reference_cash/manifest.json

| Assumption key | Complete saved value |
| --- | --- |
| years | [2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040, 2041, 2042, 2043, 2044, 2045, 2046, 2047, 2048, 2049, 2050] |
| scenario | IEA2025STEPS ratios only |
| hours | 8000 |
| capacity_t_hour | 115 |
| power_anchor_EUR2019_MWh | 100 |
| methane_netback_EUR2019_sourceMWh | 40 |
| naphtha_EUR2019_t | 600 |
| power_gas_index_share | 0.5 |
| discount | 0.05 |
| base_life | 30 |
| electric_life | [20, 30] |
| steam_usable_fraction | [0.8, 1] |
| maintenance | source annualized-capital formula; decimal and literal-percent interpretations separate |
| zero_renewal_downtime | True |
| prices_are_research_assumptions | True |
| numerical_KRW_per_EUR | 1,000 |

The lifetime illustration uses the new-plant reference, not the incumbent timing comparator: recovery=1, block=12, seed=20260913, maintenance_scale=1, life20/30, terminal none/proxy. At terminal none, analytic means are 3963.988 and 3636.696 million EUR, while the shared-pool TCaR is 857.615. The timing experiment instead has continuous output before conversion and old remaining life=8. Do not merge these counterfactuals.

\pagebreak

### 2.7 CCS source bills and physical reconciliation

DS016 · data/research_v2/ieaghg_reference/package.json

| Field | REFERENCE | EOP_L1 | EOP_L2 |
| --- | --- | --- | --- |
| initial_capex_source_USD | 4.124e+09 | 5.038e+09 | 5.321e+09 |
| reline_source_USD | 2.32e+08 | 2.32e+08 | 2.32e+08 |
| output_t_HRC | 4e+06 | 4e+06 | 4e+06 |
| direct_co2_t_per_t_HRC | 2.09014 | 1.04173 | 0.82742 |
| ng_GJ | 3.39849e+06 | 1.68625e+07 | 2.20704e+07 |
| ng_quantity_status | source_table_E35 | cost_implied_from_D15_fuel_difference_at_9.77_USD_GJ | cost_implied_from_D15_fuel_difference_at_9.77_USD_GJ |
| coal_bundle_source_USD | 4.50735e+08 | 4.50735e+08 | 4.50735e+08 |
| ore_bundle_source_USD | 4.92054e+08 | 4.92054e+08 | 4.92054e+08 |
| gross_opex_source_USD | 1.7818e+09 | 1.96623e+09 | 2.03169e+09 |
| byproduct_credit_source_USD | 5.36704e+07 | 5.36704e+07 | 5.36704e+07 |
| residual_fixed_price_opex_source_USD | 7.52133e+08 | 8.05021e+08 | 8.19608e+08 |

| Source component (USD/year) | REFERENCE | EOP_L1 | EOP_L2 |
| --- | --- | --- | --- |
| maintenance | 1.41996e+08 | 1.69903e+08 | 1.79996e+08 |
| direct_labour | 2.04581e+08 | 2.08247e+08 | 2.08623e+08 |
| indirect_labour | 7.614e+07 | 7.614e+07 | 7.614e+07 |
| energy_reductant | 4.83938e+08 | 6.15481e+08 | 6.66362e+08 |
| iron_ore | 4.92054e+08 | 4.92054e+08 | 4.92054e+08 |
| scrap_alloys | 2.18228e+08 | 2.18228e+08 | 2.18228e+08 |
| flux | 4.46499e+07 | 4.46499e+07 | 4.46499e+07 |
| consumables_utilities | 4.97808e+07 | 6.79428e+07 | 7.13261e+07 |
| miscellaneous | 6.22468e+07 | 6.22468e+07 | 6.22468e+07 |
| other_opex | 8.18134e+06 | 1.13339e+07 | 1.20686e+07 |
| coke_byproducts_credit | 2.14229e+07 | 2.14229e+07 | 2.14229e+07 |
| bf_slag_credit | 1.778e+07 | 1.778e+07 | 1.778e+07 |
| ld_slag_credit | 449,810 | 449,810 | 449,810 |
| argon_credit | 1.40177e+07 | 1.40177e+07 | 1.40177e+07 |

| Source basket | Quantity, tonnes/year |
| --- | --- |
| coal_hard | 1.25729e+06 |
| coal_soft | 838,194 |
| coal_PCI | 603,251 |
| ore_fines_Brazil | 2.92328e+06 |
| ore_fines_Australia | 352,202 |
| ore_fines_Sweden | 246,541 |
| ore_lump_Australia | 497,139 |
| ore_pellet_Brazil | 1.41772e+06 |

DS013 · data/research_v2/ieaghg_physical_reference/same_product_ledger.csv

| Field | REFERENCE | EOP_L1 | EOP_L2 |
| --- | --- | --- | --- |
| output_t_HRC_y | 4e+06 | 4e+06 | 4e+06 |
| source_ng_GJ_y | 3398486 | 16862476 | 22070357 |
| cost_implied_ng_GJ_y | 3.39849e+06 | 1.68625e+07 | 2.20704e+07 |
| ng_difference_GJ_y | 0 | 0.235415 | -0.0337769 |
| C7_emitted_t_CO2_y | 8376554 | 4182921 | 3325694 |
| avoided_t_CO2_y | 0 | 4193633 | 5050860 |
| captured_t_CO2_y | 0 | 4972525 | 6131267 |
| C7_avoided_fraction | 0 | 0.500639 | 0.602976 |
| D15_avoided_fraction | 0 | 0.501598 | 0.604132 |
| captured_over_baseline | 0 | 0.593624 | 0.731956 |
| captured_less_avoided_t_CO2_y | 0 | 778892 | 1080407 |
| capture_to_avoided_ratio |  | 1.185732037114359 | 1.213905552717755 |
| initial_capex_million_source_USD | 4,124 | 5,038 | 5,321 |
| gross_opex_million_source_USD_y | 1,781.8 | 1,966.23 | 2,031.69 |

CCS settings: 2027–2050, 5% discount, build 2027–29, operation2030–50, reline2044, terminal0; gas/ore shocks only; gas premium3%; h=0,.25,.5,.75,1; IEA CPS/STEPS/NZE; block1/12; selection 2,500 paths seed20260910, evaluation10,000 seed20260911. The same seeds are reused across model settings, so not every comparison has independent random numbers. Physical targets .50/.60/.604; λ=0,.01,.1,1. Threshold fees k=0,20,50,100; policy grid k=0,20,50 and c=0,50,100,200,500,1000. All charges are source USD per relevant CO2 tonne.

\pagebreak

### 2.8 Steel and invoice reference inputs

DS212 · data/research_v2/steel_cost_reference/vogl_main_text_package.json

| Exact input key | Source value |
| --- | --- |
| functional_unit | 1 t liquid steel; 0% scrap; continuous onsite electrolysis |
| electricity_MWh_t | 3.48 |
| hydrogen_purchase_kg_t | 0 |
| labour_EUR_t | 53.2 |
| OM_fraction_CAPEX | 0.03 |
| source_interest_rate | 0.05 |
| annualized_capital_EUR_t | 53.9412 |
| price_basis | Source2015–2018 commodity assumptions plus projected2030 equipment; no uniform price-year established |
| purchases[0].flow_id | pellets |
| purchases[0].quantity | 1.504 |
| purchases[0].quantity_unit | t/tLS |
| purchases[0].role | purchased |
| purchases[0].source_quantity | VC_pellets_quantity |
| purchases[0].source_price | VC_pellets_price |
| purchases[0].price_EUR | 100 |
| purchases[1].flow_id | lime |
| purchases[1].quantity | 0.05 |
| purchases[1].quantity_unit | t/tLS |
| purchases[1].role | purchased |
| purchases[1].source_quantity | VC_lime_quantity |
| purchases[1].source_price | VC_lime_price |
| purchases[1].price_EUR | 100 |
| purchases[2].flow_id | alloys |
| purchases[2].quantity | 0.011 |
| purchases[2].quantity_unit | t/tLS |
| purchases[2].role | purchased |
| purchases[2].source_quantity | VC_alloys_quantity |
| purchases[2].source_price | VC_alloys_price |
| purchases[2].price_EUR | 1777 |
| purchases[3].flow_id | graphite_electrodes |
| purchases[3].quantity | 0.002 |
| purchases[3].quantity_unit | t/tLS |
| purchases[3].role | purchased |
| purchases[3].source_quantity | VC_graphite_electrodes_quantity |
| purchases[3].source_price | VC_graphite_electrodes_price |
| purchases[3].price_EUR | 4000 |
| oxygen.generated_t_t | 0.411 |
| oxygen.sale_fraction | 0.6 |
| oxygen.price_EUR_t | 60.8 |
| capital_components[0].component | electrolyser |
| capital_components[0].capex_EUR_per_t_annual_capacity | 160 |
| capital_components[0].lifetime_years | 10 |
| capital_components[1].component | shaft |
| capital_components[1].capex_EUR_per_t_annual_capacity | 230 |
| capital_components[1].lifetime_years | 20 |
| capital_components[2].component | EAF |
| capital_components[2].capex_EUR_per_t_annual_capacity | 184 |
| capital_components[2].lifetime_years | 20 |

Experiment settings beyond the package: capacity1,000,000t/year, utilisation.75, construction2027–29, operation2030–50, r=.05, β=0/.5/1, oxygen sale fraction.6, nominal bridge1500KRW/EUR, seeds20260923/24, 5000 paths each, 12-month blocks, 200 permutations per seed, permutation RNG seed+1000, α=.95, terminal0. Direct emission factor0 is a cash-model placeholder, not verified zero emissions or an eligibility test. Carbon, tax, financing, working capital and incumbent costs are omitted.

\pagebreak

### Synthetic payment example

DS161 · data/research_v2/invoice_fin_bridge/timing_example_inputs.csv

| state | date | KRW_per_USD | USD_per_t | discount_factor | price_date | baseline_payment | later_payment |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | 2027-01-01 | 1000 | 10 | 1 | True | True | False |
| A | 2027-07-01 | 1200 | 15 | 0.953463 | False | False | True |
| A | 2028-01-01 | 1400 | 20 | 0.909091 | True | True | False |
| A | 2029-01-01 | 1600 | 25 | 0.826446 | False | False | True |
| B | 2027-01-01 | 1800 | 20 | 1 | True | True | False |
| B | 2027-07-01 | 1500 | 25 | 0.953463 | False | False | True |
| B | 2028-01-01 | 1200 | 10 | 0.909091 | True | True | False |
| B | 2029-01-01 | 900 | 15 | 0.826446 | False | False | True |

DS160 · data/research_v2/invoice_fin_bridge/timing_example_costs.csv

| state | baseline_npv_KRW | later_npv_KRW | incremental_npv_KRW |
| --- | --- | --- | --- |
| A | 70,909.1 | 75,775.7 | 4,866.57 |
| B | 93,818.2 | 72,083.8 | -21,734.4 |

Invoice bridge validation reuses NCC pools with constant1000KRW/EUR and unit inflation indices. The separate two-state timing illustration is synthetic; its dated values above are not observed FX forecasts. The full dataclass field definitions and settlement equations are F32–33 and the code snapshots.

\pagebreak

### 3. Complete calculation register

Each equation below defines its local variables and units. Subscripts are indices, not multiplication. The same short symbol is reused only within its explicitly labeled experiment. Expressions are editable Word math objects. Constants are traceable to section2 and file IDs in section5.

### F01 Decision, state and common comparator

$$x=(d,h);\quad L_n(x\mid s,\theta)=C_n(x\mid s,\theta)-C_n(x_0\mid s,\theta)$$

d is the physical technology and commissioning schedule; h is the procurement/EPC choice. n identifies a shared random path, s a named scenario, θ the declared structural assumptions, and x₀ the same-service reference. C is discounted cash cost and L its increment. Scenarios and θ cases have no probability weights. The pellet experiment reports C, because it has no matched incumbent.

Implementation: src/cap/plancost.py; src/cap/invoice_fin.py

### F02 Cash boundary and discounting

$$d_t=(1+r)^{-(t-t_0)}$$

$$C_n=\sum_t d_t\left[K_{nt}+O_t+\sum_j P_{njt}q_{jt}+Z_{nt}+H_{nt}-S_{nt}\right]-d_TV_T$$

t₀=2027, T=2050, r=0.05 unless the stated sensitivity changes it. K is cash investment/renewal, O other operating cash, P the external unit price, q its signed quantity, Z carbon payment, H a separately charged contract payment, S a subsidy/receipt and V terminal cash. Exports have negative q. If a contract or subsidy is already inside P or K, do not add H or subtract S again. Each stream enters once. Historical capital and noncash impairment are not new payments.

Implementation: src/cap/plancost.py:simulate_cost

\pagebreak

### F03 Units and numerical bridge

$$C\ [\mathrm{billion\ KRW}]=10^{-6}\sum_t d_t\,\mathrm{cash}_t\ [\mathrm{thousand\ KRW}]$$

$$C\ [\mathrm{million\ source\ currency}]=(1000/f)C_{\mathrm{FIN}}$$

f is a numerical KRW-per-source-currency factor: 1000 for NCC/CCS and 1500 for Vogl. Inputs are converted by f, then results converted back; these are arithmetic bridges, not observed FX. Do not compare source EUR, source USD and declared 2025 KRW as if harmonised. 1 kWh/kg = 1 MWh/t; 1000 kW = 1 MW. Costs per annual capacity and costs per actual output have different denominators.

Implementation: src/cap/plancost.py; scripts/run_steel_procurement_tail_audit.py

### F04 Mean and interpolated quantiles

$$\widehat\mu=N^{-1}\sum_n L_n;\quad h_p=(N-1)p;\quad j=\lfloor h_p\rfloor;\quad a=h_p-j$$

$$\widehat q_p=(1-a)L_{(j+1)}+aL_{(j+2)}$$

L_(i) is the ith ascending observation (one-based). At p=1 use L_(N). N is the number of paths. Quantiles use NumPy linear interpolation, equivalent to PERCENTILE.INC. Analytic/theoretical mean means expectation under the declared generator, not the finite sample mean. With deterministic quantities, affine cash prices and E[M]=1, replace M by 1 to obtain that expectation; this shortcut is invalid for nonlinear cash or stochastic quantities.

Implementation: src/cap/risk_metrics.py:loss_summary

\pagebreak

### F05 TCaR and funding questions

$$\mathrm{TCaR}_\alpha=\widehat q_\alpha(L)-\widehat q_{0.5}(L);\quad \mathrm{funding\ gap}_\alpha=\widehat q_\alpha(L)-B$$

α=0.90 in the frozen company case and 0.95 in process experiments. B is an explicitly defined budget in the same currency, discount basis and loss boundary. TCaR measures the gap above the median, not expected investment, total capital required or an annual liquidity buffer. Figure 1 shows median, upper quantile, ES and physical abatement together.

Implementation: src/cap/risk_metrics.py

### F06 Exact empirical Expected Shortfall

$$m=N(1-\alpha);\quad k=\lfloor m\rfloor;\quad f=m-k$$

$$\widehat{\mathrm{ES}}_\alpha=\frac{\sum_{i=N-k+1}^{N}L_{(i)}+fL_{(N-k)}}{m}$$

$$\mathrm{ES}_\alpha=\min_\eta\left\{\eta+\frac{\mathrm{E}[(L-\eta)^+]}{1-\alpha}\right\}$$

The sum is zero if k=0; omit the boundary term if f=0. The minimisation uses a threshold η in cost units and (z)⁺=max(z,0). ES integrates the worst 1−α probability mass, including fractional boundary weight. It is not generally the average of observations strictly above an interpolated percentile. For N=5000 and α=.95, the upper 250 observations are averaged.

Implementation: src/cap/risk_metrics.py; scripts/research_block_price_paths.py:expected_shortfall

\pagebreak

### F07 Decision rule and dominance

$$x^*\in\underset{x\in X_{\mathrm{eligible}}}{\operatorname{argmin}}\,[\mu(x)+\lambda\mathrm{ES}_\alpha(x)],\quad\lambda\geq0$$

$$y\succ x\ \Longleftrightarrow\ \mu(y)\leq\mu(x),\ \mathrm{ES}(y)\leq\mathrm{ES}(x),\ \mathrm{at\ least\ one\ strict}$$

Xeligible is the finite physically qualified menu, λ a dimensionless declared preference weight. Report all tied minima; an empty menu is infeasibility, not a zero-cost plan. Mean–ES nondominance differs from sample pathwise dominance, which requires L_n(y)≤L_n(x) for every paired n and strict inequality somewhere. TCaR alone is not a monotone cost ordering. A risk cap formulation minimises μ subject to ES≤B_ES. Neither finite-menu rule proves a global integer optimum.

Implementation: src/cap/risk_metrics.py; scripts/review_technology_investment_cycle2.py

### F08 Translation and counterexample

$$\mu(L+a)=\mu(L)+a;\quad\mathrm{ES}_\alpha(L+a)=\mathrm{ES}_\alpha(L)+a$$

$$\mathrm{TCaR}_\alpha(L+a)=\mathrm{TCaR}_\alpha(L)$$

$$\Pr(X=0)=0.8;\quad\Pr(X=100)=0.2;\quad Y=100$$

a is deterministic and measured in cost units. In the example, μ(X)=20, ES90(X)=100, TCaR90(X)=100; μ(Y)=ES90(Y)=100 and TCaR90(Y)=0. Thus μ+2TCaR wrongly selects Y, although X≤Y in every state. A shared future random cashflow also preserves pathwise differences but does not generally cancel from separate ES or TCaR levels.

Implementation: src/cap/risk_metrics.py; scripts/review_technology_investment_cycle2.py

\pagebreak

### F09 Historical observations and calibration

$$r_{mj}=\ln(P_{mj}/P_{m-1,j});\quad\widetilde r_{mj}=r_{mj}-\operatorname{mean}_m(r_{mj})$$

$$\sigma_{\mathrm{annual}}=\operatorname{sd}(r,\mathrm{ddof}=1)\sqrt\nu;\quad\nu=365.25/\operatorname{median}(\mathrm{day\ gaps})$$

m indexes calendar months and j a benchmark. World Bank January 2010–December 2025 has 192 price rows and 191 aligned return rows for six factors; no invented missing prices. D4 company calibration instead uses available named series with at least six observations, averages their annualised standard deviations within a factor, and uses priors when unavailable. Its mixed-frequency ν follows actual date gaps, not an automatic √12. Unestimable cross-factor correlation is identity.

Implementation: src/cap/calibration.py; scripts/extract_worldbank_price_history.py

### F10 Frozen Gaussian log-price factors

$$z_{nt}=\operatorname{chol}(R)\epsilon_{nt};\quad\epsilon_{nt}\sim N(0,I)$$

$$u_{nt}=\varphi u_{n,t-1}+\sigma z_{nt};\quad v_t=\varphi^2v_{t-1}+\sigma^2$$

$$M_{nt}=\exp(u_{nt}-v_t/2);\quad u_{n0}=v_0=0$$

u is the centered latent log-price state, v its analytic variance, z a correlated standard-normal innovation and ε an independent standard-normal vector. R is the factor correlation matrix, φ=1 for GBM and exp(−ln2/H) for the OU sensitivity with half-life H=10 years. The first annual column is fixed at multiplier one; innovations begin in 2028. E[M]=1. Electricity, hydrogen and construction have separate σ; both electricity channels share one power shock. Electrolyser residual is an independent GBM factor. Initial-forecast uncertainty is a separate robustness variant, not present in the baseline.

Implementation: src/cap/e3_prices.py; src/cap/price_process.py

\pagebreak

### F11 Technology capital dispersion

$$a_k=\mathrm{uncertainty\_band}_k/40$$

$$M_k=\exp\left[a_k\ln(M_{\mathrm{cap}})+\tfrac12a_k(1-a_k)v\right]$$

The D3 band is a percentage used as a relative amplitude, not a confidence interval. This formula changes log dispersion while retaining positivity and E[M_k]=1. An EPC contract replaces eligible construction shocks by a deterministic 1+10% premium. Future renewals retain their own shock and are outside project EPC/subsidy coverage. Process references freeze capital; their stored uncertainty placeholders are inactive.

Implementation: src/cap/price_process.py:scale_lognormal_multiplier; src/cap/plancost.py

### F12 Joint overlapping blocks

$$S=H-b+1;\quad U_k\sim\operatorname{Uniform}\{0,\ldots,S-1\}$$

$$A_{\ell j}=\log\left[S^{-1}\sum_{i=0}^{S-1}\exp\left(\sum_{v=0}^{\ell}\widetilde r_{i+v,j}\right)\right]$$

$$M_{nmj}=\exp\left[\sum_{v=0}^{m}\widetilde r_{nvj}-\lfloor m/b\rfloor A_{b-1,j}-A_{m\bmod b,j}\right]$$

H=191 historical returns, b=12 months normally (CCS also tests b=1). Indices m,l,v start at zero. Each independent block draw U selects the same historical start for all six factors; no circular wrapping. A_l is the log exponential moment of a partial block. A final partial block uses the full-block start support. The deterministic anchor gives exact expectation one under this finite resampling law; samples are not divided by their sample mean. This is an assumed future generator, not an estimated long-run forecast-error law.

Implementation: scripts/research_block_price_paths.py:block_paths

\pagebreak

### F13 Scenario interpolation and annual purchases

$$\overline P_t=P_{y_0}+(P_{y_1}-P_{y_0})(t-y_0)/(y_1-y_0)$$

$$R_{sjt}=\overline P_{sjt}/P_{sj,2024};\quad\overline M_{njt}=\frac1{12}\sum_{m\in\mathrm{year}\ t}M_{nmj}$$

y₀,y₁ bracket the requested year. IEA nodes are 2024,2035,2050; ratios are unitless and preserve source scenario/region. Constant monthly purchases imply arithmetic annual price averages. An annual endpoint or geometric average gives a different bill. Source historical benchmarks are not delivered plant prices; grade, freight, FX and contract basis require additional records. The company NZ15/B20 inputs are separate illustrative proxies, not an IEA/NGFS mapping.

Implementation: src/cap/scenario_prices.py; scripts/research_block_price_paths.py

### F14 Company physical quantities

$$\overline q_i=\operatorname{mean}_{2022:2024}(q_{iy});\quad e_i=\overline E_i/\overline q_i$$

$$a_{\mathrm{elec},i}=\overline{\mathrm{MWh}}_i/\overline q_i;\quad a_{\mathrm{coal},i}=\overline{\mathrm{GJ}}_{\mathrm{coal},i}/(28\overline q_i)$$

$$a_{\mathrm{gas},i}=\overline{\mathrm{GJ}}_{\mathrm{gas},i}/(54\overline q_i)$$

i is a model facility. The last three available panel years are averaged (2022–2024 in this snapshot). Annual production is fixed thereafter. Post-adoption purchased incumbent energy equals its original intensity times output times the technology-specific retained fraction; transition electricity/hydrogen are additional explicit streams. Retained fractions are not inferred from the direct emission factor. Emission factor × output gives annual Scope 1. The 22 assets are model allocations, not verified corporate coverage.

Implementation: src/cap/e2_milp.py:_prep_company; src/cap/plancost.py:build_profile

\pagebreak

### F15 Company budget and candidate construction

$$B_{ct}=\overline E_c\,\mathrm{sector\_budget}_{srt}/\mathrm{sector\_budget}_{sr,2025}$$

$$\sum_t E_{ct}(x)\leq\sum_t B_{ct};\quad\mathrm{annual\ diagnostic}:\ E_{ct}(x)\leq B_{ct}\ \forall t$$

c is company, r region and s scenario. Ebar is the recent panel average of the model portfolio’s Scope 1 total. The sector-budget ratio scales this total; it is not a corporate legal allocation. Technology/unit compatibility, availability, build time, fixed production and at-most-one facility conversion define the finite search. The expansion preserves 22 schedules and adds 23 from minimum-emissions and emissions-cap cost searches; 45×5 electricity shares×2 EPC states=450. The accepted constraint is cumulative; an annual failure must remain visible.

Implementation: src/cap/e1_constraints.py; scripts/expand_research_candidates.py

### F16 Electricity and capital contract billing

$$P^h_{nt}=(1-h)\overline P_tM_{nt}+h\overline P_t(1+\pi)$$

$$K_{\mathrm{contract},t}=K_{\mathrm{construction},t}(1-\mathrm{subsidy}_t)(1+\pi_{\mathrm{EPC}})$$

h∈{0,.25,.5,.75,1}; company power premium π=.08 and EPC premium .10. Power coverage applies to both electricity channels, never to externally purchased hydrogen. Fixed price means an annual central-price schedule plus premium, not one constant price for 24 years. Support=none in the reviewed company menu, so subsidy=0 and CCfD inactive. Basis/default/volume risk is absent. Do not label these assumed payoffs quoted PPAs.

Implementation: src/cap/plancost.py:simulate_cost

\pagebreak

### F17 Carbon payment and source unit conversion

$$Z_t=P_{\mathrm{CO}_2,t}(E_t-A_t);\quad Z_{\mathrm{purchase},t}=P_{\mathrm{CO}_2,t}\max(E_t-A_t,0)$$

A is free allowance quantity in tonnes, not an auction percentage. The frozen company gross-obligation proxy has A=0 and deterministic carbon prices; its avoided carbon bill may dominate incremental means. Other net-trade/purchase-only modes require actual allocation data and are not this result. Carbon price is zero in the process cash experiments until the explicitly hypothetical CCS charge sensitivity. All emissions still enter physical eligibility regardless of free allocation.

Implementation: src/cap/carbon_accounting.py; src/cap/plancost.py

### F18 Dated capital and renewal

$$K_{\mathrm{build},t}=I/b\ \mathrm{for}\ t=a,\ldots,a+b-1;\quad \tau=a+b$$

$$K_{\mathrm{renew},t}=I\,\mathbf1_{\{t=\tau+\ell,\,\tau+2\ell,\ldots\}}$$

$$V_{\mathrm{proxy}}=I\max[1-(T-\mathrm{last\_origin}+1)/\ell,0]$$

I is installed capital, a construction start, b build years, ℓ component life. Renewals occur at the start of the due year with zero downtime in the references. With b=0, the company implementation pays immediately at adoption. Incumbent renewal continues only before retirement; a replacement on the due date avoids that old renewal. Vproxy is a sensitivity accounting credit, not demonstrated liquidation cash. Main cases use V=0. Distinct component lives must not be replaced by one average life.

Implementation: src/cap/capital_ledger.py; src/cap/component_capital.py

\pagebreak

### F19 NCC output and steam closure

$$Y=115\times8000=920{,}000\ \mathrm{t\ ethylene/year};\quad F=Y/0.303$$

$$H_{\mathrm{conv}}=u\max(0.841-0.431,0);\quad H_{\mathrm{elec}}=u\times0.542$$

$$H_{\mathrm{boiler}}=\max(0.492-H_{\mathrm{recovered}},0);\quad G_{\mathrm{boiler}}=H_{\mathrm{boiler}}/0.92$$

F is annual naphtha feed. All specific energy terms here are MWh/t naphtha. u is the useful-steam recovery fraction (1 in timing; .8/1 in the separate new-plant sensitivity). Steam grades are collapsed as an explicit approximation. Conventional cracker methane demand=1.868, electric=0; electricity is .083 conventional and 1.476+.383+.083=1.942 electric. Zero boiler heat does not imply full engineering validation.

Implementation: src/cap/reference_ncc.py

### F20 NCC methane and capital

$$G_{\mathrm{buy}}=\max(G_{\mathrm{cracker}}+G_{\mathrm{boiler}}-2.349,0)$$

$$G_{\mathrm{sell}}=v\max(2.349-G_{\mathrm{cracker}}-G_{\mathrm{boiler}},0)$$

$$I_{\mathrm{plant}}=5126\times115\times1000+405\times10^6$$

$$I_{\mathrm{boiler}}=72.1\times H_{\mathrm{boiler}}\times115/0.303\times1000$$

v=1 is the assumed sale fraction of surplus methane. Unsold surplus would be a separately recorded transfer, not zero-emission flaring. Signed net methane quantity is F(Gbuy−Gsell). Plant cost is 994.49 million EUR2019; auxiliary boiler cost is added explicitly. Each cost curve’s capacity denominator is retained; methane export is priced at the assumed netback, not a verified contract. Naphtha quantity and price are identical in the paired alternatives and cancel exactly in their increment.

Implementation: src/cap/reference_ncc.py

\pagebreak

### F21 NCC maintenance and prices

$$\operatorname{CRF}(r,\ell)=\frac{r}{1-(1+r)^{-\ell}};\quad\operatorname{CRF}(0,\ell)=1/\ell$$

$$\mathrm{OM}=\psi I_{\mathrm{plant}}\operatorname{CRF}(.05,\ell_{\mathrm{plant}})+.04I_{\mathrm{boiler}}\operatorname{CRF}(.05,25)$$

$$P_e=100(.5+.5R_{\mathrm{gas}}\overline M_{\mathrm{gas}});\quad P_g=40R_{\mathrm{gas}}\overline M_{\mathrm{gas}}$$

$$P_{\mathrm{naphtha}}=600R_{\mathrm{oil}}\overline M_{\mathrm{oil}};\quad P_e=50+1.25P_g$$

ψ=.04 conventional and .02 electric in timing; lives are 30 and 20. Maintenance is the source annualised-capital proxy, not ψ times installed capital. Annualised capital itself is not added to cash investment. The source percentage-label ambiguity is tested separately in the new-plant experiment (ψ=.0004/.0002 alternative). Operating price bases are assumed EUR2019: power/methane per MWh, naphtha per tonne. The affine electricity–gas identity is imposed; it drives the ordering proof and is not market evidence.

Implementation: src/cap/reference_ncc.py; scripts/run_ncc_timing_frontier.py

### F22 NCC emissions gates

$$g_t=g_{2027}(2050-t)/23$$

$$E_t=F[e_t+a_{\mathrm{elec},t}g_t+\rho]$$

$$\sum_t E_t\leq\kappa\sum_t E^0_t;\quad E_T\leq0;\quad\mathrm{diagnostic}: E_t\leq E^0_{2027}(2050-t)/23$$

g2027∈{.2,.4} tCO2/MWh, residual ρ∈{0,.05} tCO2/t naphtha, direct e=.397 before electric operation and assumed zero after. κ=.75 in the main menu; cycle 1 tests .45,.50,…,.85. The reported reduction is 1−ΣE/ΣE0. E0 uses the same grid/residual condition. Annual, cumulative and terminal gates are separate; quantities are not discounted. A 0.05 residual fails terminal zero. Numerical feasibility tolerance=1e−7 tonnes.

Implementation: src/cap/reference_timing.py:emission_qualification

\pagebreak

### F23 Continuation and timing proof

$$\operatorname{Tail}(\tau)=\frac{I(1+r)^{-(\operatorname{next}(\tau)-2027)}}{1-(1+r)^{-20}}$$

$$\Delta C_{\mathrm{early,late}}\geq\sum_t d_t[\Delta\mathrm{fixed}_t+50\Delta\mathrm{MWh}_t]+\Delta\operatorname{Tail}$$

I=994.49 million EUR, next(τ) is the first renewal after 2050 (2070/2055/2060/2065 for commissioning 2030/35/40/45). The second inequality requires nonnegative Pg and 1.25ΔMWh+Δnetmethane≥0 each year. Future same-technology operating cash cancels pathwise in differences. Positive lower bounds prove cost ordering under these assumptions. They do not produce full-horizon individual ES/TCaR levels. The continuation is stationary deterministic capital, not an estimated terminal value.

Implementation: scripts/review_technology_investment_cycle2.py

### F24 CCS source cash ledger

$$\mathrm{Fixed}_i=\mathrm{GrossOM}_i-\mathrm{GasBill}_i-\mathrm{OreBill}_i-\mathrm{CoalBill}_i-\mathrm{Credits}_i$$

$$\mathrm{Gas}_i=\mathrm{Gas}_0+(\mathrm{EnergyBill}_i-\mathrm{EnergyBill}_0)/9.77$$

$$C_i=\sum_t d_t[K_{it}+\mathrm{Fixed}_{it}+\mathrm{CoalBill}_t+\mathrm{OreBill}_t\overline M_{\mathrm{ore}}+\mathrm{GasBill}_{it}]$$

i∈{REFERENCE,L1,L2}. Bills are annual source USD; gas quantities are GJ/year. Gross operating costs exclude byproduct credits; the subtraction retains net fixed cash after removing separately billed energy/material components. Frozen L1/L2 gas volumes are cost-implied; the later physical-source values are rounded and reconciled, not substituted into saved costs. Initial capital is paid in equal thirds 2027–29; common 232 million USD reline occurs in 2044. Operation is 2030–50 at 4 million t HRC/year.

Implementation: scripts/run_ieaghg_paired_reference.py; data/research_v2/ieaghg_reference/package.json

\pagebreak

### F25 CCS incremental gas procurement

$$\overline P_{\mathrm{gas},t}=9.77R_{\mathrm{IEA\ Europe\ gas},t}$$

$$\mathrm{GasBill}_i^h=\mathrm{Gas}_0\overline P_{\mathrm{gas}}\overline M_{\mathrm{gas}}+\Delta\mathrm{Gas}_i\overline P_{\mathrm{gas}}[(1-h)\overline M_{\mathrm{gas}}+h(1+.03)]$$

ΔGas_i=Gas_i−Gas0. The common baseline gas remains exposed; only additional capture gas can be fixed. h has five values 0,.25,.5,.75,1. All routes share ore and coal cash, so those terms cancel in paired increments. Under the specified two-factor model and deterministic capital, h=1 makes incremental TCaR zero algebraically, while absolute project cost remains exposed to common gas/ore. No volume, basis or default risk is modeled.

Implementation: scripts/run_ieaghg_paired_reference.py

### F26 Avoided versus captured CO₂

$$A_i=E_0-E_i;\quad\mathrm{reduction}_i=A_i/E_0$$

$$\mathrm{net\_reduction}_i=(A_i-uQ_i)/E_0$$

$$u_{\max}=(A_i-\mathrm{target}\times E_0)/Q_i$$

E0=8,376,554 tCO2/year on the audited C7 boundary; E_i is emitted and Q_i captured CO2. Q is not A because capture energy and other emissions remain. u is net additional downstream emissions relative to the comparator per captured tonne, not an estimated leakage rate. Targets .50/.60/.604 gate physical choice; downstream stress uses 0, u_max, .005 and .01. C7 and older D15 fractions remain distinct. C7 column identity is an inferred reconciliation, not an official erratum.

Implementation: scripts/audit_ieaghg_physical_reference.py; scripts/review_technology_investment_cycle2.py

\pagebreak

### F27 Hypothetical carbon/transport cash

$$W=\sum_{t=2030}^{2050}(1.05)^{-(t-2027)}$$

$$L_i(c,k)=L_i(0,0)+W(kQ_i-cA_i)$$

c is a constant real source-USD charge per emitted tonne on the reported boundary; relative to baseline it credits avoided tonnes. k is a fee per captured tonne, not avoided tonne. Costs in million USD require dividing the added term by 1e6. These are hypothetical schedules, not actual ETS net payments or calibrated transport/storage tariffs. μ and ES both shift by this amount; TCaR does not change.

Implementation: scripts/review_technology_investment_cycle2.py

### F28 Physical switching thresholds

$$c_\mu^*=[\Delta\mu/W+k\Delta Q]/\Delta A$$

$$c_{\mathrm{ES}}^*=[\Delta\mathrm{ES}/W+k\Delta Q]/\Delta A$$

$$c_{\mu+\lambda\mathrm{ES}}^*=\left[\frac{\Delta\mu+\lambda\Delta\mathrm{ES}}{(1+\lambda)W}+k\Delta Q\right]/\Delta A$$

Δ denotes L2 minus L1 at the same h, scenario and evaluation pool; costs here are USD, not million USD. ΔA>0. Equal scores occur at c*, and increasing c favors L2. The weighted formula follows translation of BOTH μ and ES and includes (1+λ). If h is jointly selectable, compare every qualified plan; one same-h threshold is not the envelope over all contracts. λ∈{0,.01,.1,1} is a sensitivity, not an estimated preference.

Implementation: scripts/review_technology_investment_cycle2.py; algebraic extension of F27

\pagebreak

### F29 Vogl plant quantities and fixed cash

$$Y_t=\mathrm{capacity}\times\mathrm{utilisation}\times\mathbf1_{\{t\geq2030\}}=750{,}000\,\mathbf1_{\{t\geq2030\}}$$

$$q_{\mathrm{power}}=3.48Y;\quad q_{\mathrm{pellet}}=1.504Y;\quad q_{\mathrm{oxygen}}=-.411\times.6Y$$

$$\mathrm{Fixed}_t=K_t+Y_t(.05\times100+.011\times1777+.002\times4000+53.2-.411\times.6\times60.8)$$

$$\mathrm{Fixed}_t\leftarrow\mathrm{Fixed}_t+\mathbf1_{\{t\geq2030\}}\times10^6\times574\times.03$$

Installed capacity is 1,000,000 t liquid steel/year, utilisation=.75. Power is MWh, other flows tonnes. Source capital per annual tonne is electrolyser160 (life10), shaft230 (life20), EAF184 (life20) EUR. Initial 574 million is split across 2027–29; renewals are 160 million in 2040 and 574 million in 2050. Maintenance uses installed capacity, labour actual output. Onsite hydrogen is already in electricity; do not bill purchased hydrogen or upstream pellet production energy again. Oxygen price is an assumed sale value with unresolved conditioning cost.

Implementation: src/cap/reference_steel.py; scripts/run_steel_procurement_tail_audit.py

### F30 Pellet loading and equal means

$$P_{\mathrm{pellet}}=100[(1-\beta)+\beta\overline M_{\mathrm{ore}}];\quad P_e=40(.5+.5R_{\mathrm{JapanLNG}}\overline M_{\mathrm{gas}})$$

$$C_\beta=C_{\mathrm{fixed}}+C_{\mathrm{power}}+(1-\beta)C_{\mathrm{pellet,central}}+\beta C_{\mathrm{pellet,random}}$$

β∈{0,.5,1} is an unestimated mapping assumption, not an available financial contract. E[M]=1 implies the same theoretical mean, 3971.2314147902393 million source EUR, across β. Finite sample means can differ. Joint paths preserve the block relation; whole-trajectory permutations change pairing while preserving every marginal path. The 200 permutations per seed are a dependence diagnostic, not a forecast confidence interval.

Implementation: scripts/run_steel_procurement_tail_audit.py

\pagebreak

### F31 Tail contributions and uncertainty summaries

$$C_n=\sum_j C_{nj};\quad\mathrm{ES\ contribution}_j=\sum_n w_nC_{nj};\quad\sum_n w_n=1$$

$$\mathrm{Excess\ contribution}_j=\mathrm{ES\ contribution}_j-\operatorname{mean}_n(C_{nj})$$

$$\operatorname{MCSE}(\widehat\mu)=\operatorname{sd}(L,\mathrm{ddof}=1)/\sqrt N$$

w ranks TOTAL cost and allocates the worst-tail mass from F06; it is common across components. Contributions sum to total ES; standalone component ES values generally do not. Paired bootstrap draws the same path indices across candidates, recalculates the statistic, and uses 2.5/97.5 percentiles of 500 replicates (NCC). Frontier frequency is count/500, not probability of true efficiency. Corporate fixed-candidate bootstrap uses 400 replicates. These cover sampling conditional on the specified model, not structural or parameter uncertainty.

Implementation: src/cap/tail_attribution.py; scripts/run_ncc_timing_frontier.py

### F32 Invoice currency and settlement

$$\mathrm{FX}_{a\to b,nt}=\mathrm{quote}_{b,nt}/\mathrm{quote}_{a,nt}$$

$$\mathrm{Cash}_{n,\mathrm{paid}}=\frac{\mathrm{sign}\times q\times P^{\mathrm{real}}_{n,\mathrm{priced}}\times I_{a,n,\mathrm{priced}}\times\mathrm{FX}_{a\to b,n,\mathrm{paid}}}{I_{b,n,\mathrm{paid}}}$$

$$\mathrm{NPV}_n=\sum_{\mathrm{paid}}d_{n,\mathrm{paid}}\mathrm{Cash}_{n,\mathrm{paid}}$$

Quotes are nominal currency units per common anchor; its own quote=1. a is invoice currency, b evaluation currency. q≥0; sign=+1 purchase or −1 export. I_a inflates a real invoice price to nominal at pricing; I_b deflates nominal evaluation cash at payment. Use one for the relevant nominal leg. Indices must match explicit base years; discount factors must match nominal/real output. price_date and settlement_date differ; post-2050 payments are retained. Sample ID, ordered path IDs, currency, quantity unit and calendar must align.

Implementation: src/cap/fx_settlement.py:settle_invoices

\pagebreak

### F33 Invoice integration and covariance

$$C_{\mathrm{combined}}=C_{\mathrm{FIN\ without\ additional\ flows}}+\mathrm{NPV}_{\mathrm{invoice}}/10^9$$

$$\mathrm{E}[PX]=\mathrm{E}[P]\mathrm{E}[X]+\operatorname{Cov}(P,X)$$

$$\operatorname{mean}_m(P_mX_m)=\operatorname{mean}_m(P_m)\operatorname{mean}_m(X_m)+\operatorname{Cov}_m(P_m,X_m)$$

The first result is billion KRW, with invoice NPV in KRW. Replace the old additional-commodity ledger completely, then add each invoice once; never add an FX surcharge to a bill already converted. The last covariance uses denominator M (population covariance over the M months), not M−1. Annual averages of price and FX cannot generally be multiplied independently. Invoice integration is an opt-in extension; the frozen company results do not include estimated corporate FX exposures.

Implementation: src/cap/invoice_fin.py

### F34 Reference evaluation and regret

$$\operatorname{Regret}(\widehat x\mid s,\theta)=J_{\mathrm{reference}}(\widehat x\mid s,\theta)-\min_{x\in X_{\mathrm{eligible}}}J_{\mathrm{reference}}(x\mid s,\theta)$$

Jreference is one predeclared common evaluation rule, for example μ+λES. xhat is the plan chosen by a competing information/model configuration. Infeasibility is reported separately and never assigned zero regret. PLANiT-linked prices, quantities, supply caps and emission factors must share scenario, region, year and system boundary; a changed industrial demand response requires a system re-solve. This is the proposed validation design, not a completed numerical value-of-information estimate.

Implementation: paper/pilot_review/PAPER_EN.md:sections 13–16

\pagebreak

### F35 Finite candidate generation surrogate

$$x_{ika}\in\{0,1\};\quad\sum_{ka}x_{ika}\leq1;\quad\tau_k=a+\mathrm{build\_years}_k$$

$$R_{\mathrm{proxy}}=\sum_t d_t[\sigma_e\mathrm{ElectricityBill}_t+\sigma_h\mathrm{H2Bill}_t+\sigma_K\mathrm{CapitalCash}_t+.30\mathrm{CarbonBill}_t]$$

$$\min C_{\mathrm{central}}\ \mathrm{subject\ to}\ R_{\mathrm{proxy}}\leq\varepsilon;\quad\mathrm{or}\ \min R_{\mathrm{proxy}};\quad\mathrm{or}\ \min\sum_t E_t$$

x_ika selects technology k at facility i with construction start a. Allowed starts satisfy a≥max(2027,technology availability,scenario availability) and a+build_years≤2050; incompatible units have no variable. Retirement share is fixed at zero; candidate generation is unhedged (power/EPC/CCfD=0). Rproxy is a linear search device, not simulated TCaR/ES: its .30 carbon exposure coefficient is a search assumption even though company carbon cash is deterministic in Monte Carlo. All bills in the expression use one monetary scale. Original six risk-bound search points and emissions expansion points generate schedules that are subsequently revalued. Expansion uses four equally spaced caps between the minimum total emissions and the cumulative budget, adds a 1e−9 relative feasibility allowance (capped at the budget), and removes duplicate facility/technology/start tuples. No annual slack penalty applies in cumulative_hard mode; annual slack only records failures.

Implementation: src/cap/e2_milp.py; scripts/expand_research_candidates.py

### F36 Historical descriptive statistics

$$m_k=H^{-1}\sum_m(r_m-\overline r)^k;\quad\mathrm{skew}=m_3/m_2^{3/2};\quad\mathrm{excess\ kurtosis}=m_4/m_2^2-3$$

$$\operatorname{Corr}(X,Y)=\frac{\sum(X-\overline X)(Y-\overline Y)}{\sqrt{\sum(X-\overline X)^2\sum(Y-\overline Y)^2}}$$

H is the number of retained returns, rbar their arithmetic mean, m_k a central moment. Lag-one autocorrelation correlates consecutive returns; squared-return autocorrelation applies the same operation to squared returns. These statistics and historical quantiles describe the input sample. They are not a fitted future risk distribution or independent validation. The stored six-factor correlation matrix and source diagnostics are auxiliary to the common-block construction, which samples the joint history directly.

Implementation: scripts/extract_worldbank_price_history.py

\pagebreak

### 4. Complete field dictionary

Every distinct field name from every registered CSV/Parquet is included below. Full per-file occurrence, datatype, observed range, missing count, example and meaning are in field_dictionary.csv. This avoids silently giving one name the wrong unit when multiple experiments reuse it. Calendar and categorical metadata have no physical unit; source unit fields override generic labels.

| Exact field / dataset group | Meaning and unit rule |
| --- | --- |
| C7_avoided_fraction<br>CCS | Named emissions ratio; C7 vs D15 boundaries differ; capture is not avoidance<br>Unit: ratio |
| C7_eligible<br>CCS | Boolean flag: C7 eligible; this is a test outcome, not probability<br>Unit: boolean |
| C7_emitted_t_CO2_y<br>CCS | Emitted, avoided, captured, or captured-minus-avoided CO2 on audited C7 boundary (F26)<br>Unit: tCO2/year |
| D15_avoided_fraction<br>CCS | Named emissions ratio; C7 vs D15 boundaries differ; capture is not avoidance<br>Unit: ratio |
| D15_eligible<br>CCS | Boolean flag: D15 eligible; this is a test outcome, not probability<br>Unit: boolean |
| ES_contribution<br>STEEL | Contribution using total-cost tail weights; excess subtracts component mean (F31)<br>Unit: million source EUR |
| KRW_per_USD<br>FX | Nominal KRW per USD in the synthetic settlement example<br>Unit: KRW/USD |
| USD_per_t<br>FX | Nominal invoice price in the synthetic settlement example<br>Unit: USD/t |
| abated_tco2_disc<br>CORP | Discounted avoided emissions in legacy cost-per-tonne diagnostic; eligibility uses undiscounted emissions<br>Unit: discounted tCO2 |
| absolute_es95<br>CCS | Mean/ES of whole-project cost before reference subtraction<br>Unit: million source USD |
| absolute_mean<br>CCS | Mean/ES of whole-project cost before reference subtraction<br>Unit: million source USD |
| accessed_at_utc<br>CORP | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| acf1<br>PRICE | Lag-one sample correlation of returns or squared returns<br>Unit: coefficient |
| adopt_year<br>CORP | Calendar year for the event named in the field; adopt=start, op=commissioning; 9999 denotes unavailable<br>Unit: year |
| aggregate_annual_exposure_arrays_equal<br>CORP | Boolean flag: aggregate annual exposure arrays equal; this is a test outcome, not probability<br>Unit: boolean |
| alpha<br>CORP,FIGURE,FX,NCC,STEEL | Upper-tail confidence level; .90 company, .95 process<br>Unit: fraction |
| amount_unit<br>CORP | Unit/currency/price-year declaration; blanks are unresolved, not zero<br>Unit: metadata |
| analytic_mean<br>CCS,CORP,FIGURE,NCC,REVIEW | Expectation under the declared generator; analytic rather than sampled when named analytic/theoretical<br>Unit: dataset currency |
| analytic_mean_in_interval<br>CORP | Boolean flag: analytic mean in interval; this is a test outcome, not probability<br>Unit: boolean |
| annual_budget_compliant<br>CORP | Boolean flag: annual budget compliant; this is a test outcome, not probability<br>Unit: boolean |
| annual_excess_tco2<br>CORP | Emissions-budget slack or annual excess with sign documented by column<br>Unit: tCO2 |
| annual_feasible<br>FIGURE,NCC | Boolean flag: annual feasible; this is a test outcome, not probability<br>Unit: boolean |
| annual_linear_cap<br>NCC | Company-scaled or NCC diagnostic annual emissions cap<br>Unit: tCO2/year |
| annual_linear_cap_enforced<br>REVIEW | Boolean flag: annual linear cap enforced; this is a test outcome, not probability<br>Unit: boolean |
| annual_log_vol<br>CORP | Standard deviation of log returns at the named frequency<br>Unit: log-return SD |
| annual_net_emissions_margin<br>REVIEW | Avoided tonnes minus target times reference emissions<br>Unit: tCO2/year |
| applies_to_unit<br>CORP | Facility/site/sector/region/compatibility label; not an extra numeric assumption<br>Unit: category |
| avail_year<br>CORP | Calendar year for the event named in the field; adopt=start, op=commissioning; 9999 denotes unavailable<br>Unit: year |
| avail_year_scenario<br>CORP | Calendar year for the event named in the field; adopt=start, op=commissioning; 9999 denotes unavailable<br>Unit: year |
| avoided_t_CO2_y<br>CCS | Emitted, avoided, captured, or captured-minus-avoided CO2 on audited C7 boundary (F26)<br>Unit: tCO2/year |
| base_eligible<br>CORP | Boolean flag: base eligible; this is a test outcome, not probability<br>Unit: boolean |
| base_menu_size<br>CORP | Base menu size<br>Unit: count |
| base_plan<br>CORP | Selected/reference/equivalent plan ID; semicolon separates multiple IDs<br>Unit: identifier |
| base_plan_id<br>CORP | Named company/facility/technology/plan/reference/component identifier; joins are exact<br>Unit: identifier |
| base_value<br>CORP | Numeric or categorical value of the named item; unit inherited from its row/dataset<br>Unit: row unit |
| baseline_cumulative<br>FIGURE,NCC | Undiscounted total candidate or baseline emissions<br>Unit: tCO2 |
| baseline_emissions<br>NCC | Annual emissions component/total/reference or terminal quantity/cap named in field<br>Unit: tCO2/year |
| baseline_gross_capex_k<br>CORP | Gross baseline/plan/incremental or renewal capital cash named by field<br>Unit: thousand KRW |
| baseline_mean<br>NCC | Sample absolute mean of new conventional/electric plant in lifetime experiment<br>Unit: million EUR |
| baseline_npv_KRW<br>FX | Discounted invoice cash for baseline/later payment or their difference<br>Unit: KRW |
| baseline_payment<br>FX | Boolean flag indicating whether this row date is a pricing, baseline settlement or later settlement date in the synthetic example<br>Unit: boolean |
| baseline_scope1_tco2<br>CORP | Annual direct Scope 1 emissions in company boundary<br>Unit: tCO2/year |
| baseline_selected_plan_id<br>CORP | Selected/reference/equivalent plan ID; semicolon separates multiple IDs<br>Unit: identifier |
| beta<br>FIGURE,STEEL | Pellet-to-ore benchmark loading; 0,.5,1 (F30)<br>Unit: fraction |
| block<br>NCC | Historical block length in months<br>Unit: months |
| bootstrap_high_95<br>CORP | Empirical bootstrap 2.5/97.5 percentile limits (F31)<br>Unit: dataset currency |
| bootstrap_low_95<br>CORP | Empirical bootstrap 2.5/97.5 percentile limits (F31)<br>Unit: dataset currency |
| bootstrap_replicates<br>NCC | Count of observations, paths, or replications named by field<br>Unit: count |
| boundary<br>PRICE | Literal explanatory evidence or boundary statement; read alongside numeric fields<br>Unit: text |
| boundary_limit<br>PRICE | Literal explanatory evidence or boundary statement; read alongside numeric fields<br>Unit: text |
| boundary_status<br>CORP | Evidence, extraction, mapping or accounting status; not a model probability<br>Unit: category |
| brent<br>PRICE | Aligned historical monthly benchmark log return; raw price units in source series register<br>Unit: log return |
| budget_mode<br>CORP | Accounting/qualification/statistical convention defining the result<br>Unit: category |
| budget_ok<br>CORP | Boolean flag: budget ok; this is a test outcome, not probability<br>Unit: boolean |
| budget_slack_tco2<br>CORP | Emissions-budget slack or annual excess with sign documented by column<br>Unit: tCO2 |
| build_years<br>CORP | Construction duration, technology life or incumbent renewal interval<br>Unit: years |
| candidate<br>FIGURE,FX,NCC,REVIEW | Named company/facility/technology/plan/reference/component identifier; joins are exact<br>Unit: identifier |
| capacity<br>CORP | Installed annual production capacity; monetary denominator uses this, not output<br>Unit: capacity_unit |
| capacity_unit<br>CORP | Unit/currency/price-year declaration; blanks are unresolved, not zero<br>Unit: metadata |
| capex_EUR<br>NCC | Dated capital/maintenance/terminal credit cash named by field<br>Unit: EUR/year |
| capex_peak<br>CORP | Peak annual or cumulative gross capital cash; not discounted total project cost<br>Unit: billion KRW |
| capex_peak_bnkrw<br>CORP | Peak annual or cumulative gross capital cash; not discounted total project cost<br>Unit: billion KRW |
| capex_peak_year<br>CORP | Calendar year for the event named in the field; adopt=start, op=commissioning; 9999 denotes unavailable<br>Unit: year |
| capex_source_USD<br>CCS | Annual capital/reline/fixed-price cash component<br>Unit: source USD/year |
| capex_total<br>CORP | Peak annual or cumulative gross capital cash; not discounted total project cost<br>Unit: billion KRW |
| capex_total_bnkrw<br>CORP | Peak annual or cumulative gross capital cash; not discounted total project cost<br>Unit: billion KRW |
| capex_uncertainty<br>CORP | D3 percentage band used relative to 40 to scale log dispersion (F11)<br>Unit: percent; not CI |
| capex_unit<br>CORP | New technology / incumbent replacement cost per annual capacity<br>Unit: thousand KRW/(t/year) |
| capital_accounting<br>CORP | Accounting/qualification/statistical convention defining the result<br>Unit: category |
| capital_delta_npv<br>NCC | Electric minus conventional discounted component cash<br>Unit: million EUR |
| capture_to_avoided_ratio<br>CCS | Named emissions ratio; C7 vs D15 boundaries differ; capture is not avoidance<br>Unit: ratio |
| captured_less_avoided_t_CO2_y<br>CCS | Emitted, avoided, captured, or captured-minus-avoided CO2 on audited C7 boundary (F26)<br>Unit: tCO2/year |
| captured_over_baseline<br>CCS | Named emissions ratio; C7 vs D15 boundaries differ; capture is not avoidance<br>Unit: ratio |
| captured_t_CO2_y<br>CCS | Emitted, avoided, captured, or captured-minus-avoided CO2 on audited C7 boundary (F26)<br>Unit: tCO2/year |
| carbon_accounting<br>CORP | Accounting/qualification/statistical convention defining the result<br>Unit: category |
| carbon_budget<br>CORP | Scenario sector emissions limit before company scaling<br>Unit: MtCO2/year |
| carbon_charge<br>REVIEW | Hypothetical emitted-tonne charge or equal-score threshold; incremental benefit uses avoided tonnes (F28)<br>Unit: source USD/tCO2 |
| carbon_delta<br>CORP | Named corporate discounted cost/carbon/policy/perfect-information diagnostic; auxiliary, not a new pilot decision result<br>Unit: billion KRW |
| carbon_delta_bnkrw<br>CORP | Named corporate discounted cost/carbon/policy/perfect-information diagnostic; auxiliary, not a new pilot decision result<br>Unit: billion KRW |
| case<br>CCS,NCC,REVIEW | Named company/facility/technology/plan/reference/component identifier; joins are exact<br>Unit: identifier |
| case_boundary_status<br>CORP | Evidence, extraction, mapping or accounting status; not a model probability<br>Unit: category |
| cash<br>CORP | Corporate financial observation or historical proxy; not facility energy cost; retain currency and reporting scope<br>Unit: row currency/unit |
| ccfd<br>CORP | Binary contract state; EPC active menu, CCfD inactive in reviewed company run<br>Unit: 0/1 |
| central_cost_reconciliation_error<br>CORP | Central FIN cost minus independent reconstruction<br>Unit: billion KRW |
| central_gas_source_USD_GJ<br>CCS | 9.77 times IEA EU-gas ratio<br>Unit: source USD/GJ |
| central_power<br>STEEL | Central assumed power price in Vogl experiment<br>Unit: source EUR/MWh |
| changed<br>CORP | Boolean flag: changed; this is a test outcome, not probability<br>Unit: boolean |
| check<br>CCS | Name of measured parameter, source item, statistic or diagnostic<br>Unit: identifier |
| commission_year<br>FIGURE,NCC | Calendar year for the event named in the field; adopt=start, op=commissioning; 9999 denotes unavailable<br>Unit: year |
| commissioning_year<br>CORP | Calendar year for the event named in the field; adopt=start, op=commissioning; 9999 denotes unavailable<br>Unit: year |
| commodity<br>FIGURE,PRICE | Commodity identity; prices and flows must use matching denominator<br>Unit: category |
| common_contract_fraction<br>REVIEW | Fixed-price coverage fraction; power in company, incremental gas in CCS (F16,F25)<br>Unit: fraction |
| company_budget_tco2<br>CORP | Company-scaled or NCC diagnostic annual emissions cap<br>Unit: tCO2/year |
| company_delivered_input<br>PRICE | Boolean flag: company delivered input; this is a test outcome, not probability<br>Unit: boolean |
| company_id<br>CORP | Named company/facility/technology/plan/reference/component identifier; joins are exact<br>Unit: identifier |
| company_scenario_alignment_verified<br>PRICE | Boolean flag: company scenario alignment verified; this is a test outcome, not probability<br>Unit: boolean |
| comparison<br>FX | Name of paired comparison or verification experiment<br>Unit: identifier |
| comparison_basis<br>CORP | Literal explanatory evidence or boundary statement; read alongside numeric fields<br>Unit: text |
| component<br>REVIEW,STEEL | Named company/facility/technology/plan/reference/component identifier; joins are exact<br>Unit: identifier |
| computed<br>CCS | Numeric or categorical value of the named item; unit inherited from its row/dataset<br>Unit: row unit |
| condition<br>FIGURE,NCC | Combined grid/residual condition for NCC qualification<br>Unit: category |
| condition_id<br>NCC | Combined parameter-case identifier in new-plant experiment<br>Unit: identifier |
| construction_EUR<br>NCC | Annual construction/new renewal/old renewal cash named in field<br>Unit: EUR/year |
| continuation_capex_PV<br>REVIEW | Post-2050 capital PV or candidate minus 2040 difference; continued mean includes window difference<br>Unit: million EUR |
| continuation_difference_vs2040<br>REVIEW | Post-2050 capital PV or candidate minus 2040 difference; continued mean includes window difference<br>Unit: million EUR |
| continued_mean_difference_vs2040<br>REVIEW | Post-2050 capital PV or candidate minus 2040 difference; continued mean includes window difference<br>Unit: million EUR |
| contracted_ng_GJ<br>CCS | Incremental fixed gas / remaining market-priced gas quantity<br>Unit: GJ/year |
| cost_implied_ng_GJ_y<br>CCS | Published gas quantity / frozen cash-implied quantity / published minus implied<br>Unit: GJ/year |
| cost_per_tco2_thkrw<br>CORP | Incremental discounted cost divided by discounted avoided tonnes; auxiliary diagnostic<br>Unit: thousand KRW/tCO2 |
| coverage_pct<br>CORP | Declared observation coverage percentage; does not prove model asset completeness<br>Unit: percent |
| criterion<br>CORP,REVIEW | Selection statistic or mean definition; preserve sample vs analytic distinction<br>Unit: category |
| cum_emis_tco2<br>CORP | Undiscounted total candidate or baseline emissions<br>Unit: tCO2 |
| cumulative_budget<br>CORP | Undiscounted sum emissions allowance over modeled years<br>Unit: tCO2 |
| cumulative_budget_tco2<br>CORP | Undiscounted sum emissions allowance over modeled years<br>Unit: tCO2 |
| cumulative_cap<br>FIGURE,NCC | Undiscounted sum emissions allowance over modeled years<br>Unit: tCO2 |
| cumulative_emissions<br>CORP,FIGURE,NCC | Undiscounted total candidate or baseline emissions<br>Unit: tCO2 |
| cumulative_feasible<br>FIGURE,NCC | Boolean flag: cumulative feasible; this is a test outcome, not probability<br>Unit: boolean |
| cumulative_ratio<br>FIGURE,NCC | Candidate/reference cumulative emissions ratio or allowed maximum<br>Unit: ratio |
| currency<br>CORP,PRICE | Unit/currency/price-year declaration; blanks are unresolved, not zero<br>Unit: metadata |
| date<br>CORP,FX | Observation, pricing or settlement date explicitly named in field<br>Unit: calendar |
| decision_eligible<br>CORP | Boolean flag: decision eligible; this is a test outcome, not probability<br>Unit: boolean |
| derivation<br>CORP | Literal explanatory evidence or boundary statement; read alongside numeric fields<br>Unit: text |
| difference<br>PRICE | Source comparison or arithmetic residual in named unit; not a model input unless marked<br>Unit: row unit |
| direct_co2<br>CCS | Frozen D15 direct annual CO2; later C7 boundary separately audited<br>Unit: tCO2/year |
| direct_emissions<br>NCC | Annual emissions component/total/reference or terminal quantity/cap named in field<br>Unit: tCO2/year |
| discount<br>STEEL | Present-value weight (1+r)^−(t−2027), or explicit dated weight<br>Unit: ratio |
| discount_factor<br>FIGURE,FX | Present-value weight (1+r)^−(t−2027), or explicit dated weight<br>Unit: ratio |
| discount_rate<br>FIGURE | Annual real or nominal rate consistent with stated price basis<br>Unit: fraction/year |
| discounted_power_ore_correlation<br>STEEL | Sample correlation of discounted power and ore cost components<br>Unit: coefficient |
| dominance_witness<br>CORP | Candidate with weakly lower paired loss in every sampled state and strict somewhere<br>Unit: identifier |
| downstream_fee<br>REVIEW | Hypothetical fee per captured CO2 tonne<br>Unit: source USD/tCO2 captured |
| downstream_fee_per_captured_t<br>REVIEW | Hypothetical fee per captured CO2 tonne<br>Unit: source USD/tCO2 captured |
| earlier<br>REVIEW | Commissioning year in paired timing dominance proof<br>Unit: year |
| earnings_definition<br>CORP | Financial reporting period or earnings definition<br>Unit: metadata/calendar |
| ebitda<br>CORP | Corporate financial observation or historical proxy; not facility energy cost; retain currency and reporting scope<br>Unit: row currency/unit |
| elec_intensity<br>CORP | Additional transition electricity per product tonne<br>Unit: MWh/t |
| electric_life<br>NCC | Electric plant component lifetime in sensitivity<br>Unit: years |
| electric_mean<br>NCC | Sample absolute mean of new conventional/electric plant in lifetime experiment<br>Unit: million EUR |
| electric_operating_years<br>FIGURE,REVIEW | Count of years with electric technology active inside 2027–2050<br>Unit: years |
| electricity_MWh_per_t_ethylene<br>NCC | Total purchased electricity per ethylene output<br>Unit: MWh/t ethylene |
| eligible<br>REVIEW | Boolean flag: eligible; this is a test outcome, not probability<br>Unit: boolean |
| eligible_for_cumulative_terminal_menu<br>FIGURE,NCC | Boolean flag: eligible for cumulative terminal menu; this is a test outcome, not probability<br>Unit: boolean |
| emission_factor<br>CORP | Technology direct-emissions intensity at operating output<br>Unit: tCO2/t product |
| emissions_s1<br>CORP | Annual direct Scope 1 emissions in company boundary<br>Unit: tCO2/year |
| emissions_s1_basis<br>CORP | Evidence, extraction, mapping or accounting status; not a model probability<br>Unit: category |
| emissions_s2<br>CORP | Reported/model allocated indirect Scope 2 emissions; not the company Scope 1 gate<br>Unit: tCO2/year |
| emissions_s2_basis<br>CORP | Evidence, extraction, mapping or accounting status; not a model probability<br>Unit: category |
| end<br>CORP,PRICE | First/last date or index in the named source range<br>Unit: calendar/index |
| energy_coal<br>CORP | Annual coal/gas energy; tonnes reconstructed using 28/54 GJ per tonne<br>Unit: GJ/year |
| energy_elec<br>CORP | Annual purchased electricity<br>Unit: MWh/year |
| energy_gas<br>CORP | Annual coal/gas energy; tonnes reconstructed using 28/54 GJ per tonne<br>Unit: GJ/year |
| energy_naphtha<br>CORP | Recorded naphtha energy field; not a separate additional corporate fuel bill<br>Unit: source declared GJ/year |
| epc<br>CORP | Binary contract state; EPC active menu, CCfD inactive in reviewed company run<br>Unit: 0/1 |
| equivalent_plan_id<br>CORP | Selected/reference/equivalent plan ID; semicolon separates multiple IDs<br>Unit: identifier |
| es95<br>CCS,FIGURE,NCC,REVIEW | Mean of exact worst-tail probability mass (F06)<br>Unit: dataset currency |
| es_alpha<br>CORP,FIGURE,FX,NCC,STEEL | Mean of exact worst-tail probability mass (F06)<br>Unit: dataset currency |
| es_alpha_bnkrw<br>CORP | Mean of exact worst-tail probability mass (F06)<br>Unit: dataset currency |
| es_p025<br>NCC | Empirical bootstrap 2.5/97.5 percentile limits (F31)<br>Unit: dataset currency |
| es_p975<br>NCC | Empirical bootstrap 2.5/97.5 percentile limits (F31)<br>Unit: dataset currency |
| europe_gas<br>PRICE | Aligned historical monthly benchmark log return; raw price units in source series register<br>Unit: log return |
| evidence_status<br>CORP | Evidence, extraction, mapping or accounting status; not a model probability<br>Unit: category |
| evidence_tier<br>CORP | Evidence, extraction, mapping or accounting status; not a model probability<br>Unit: category |
| excess_ES<br>FIGURE,STEEL | ES minus the sample mean<br>Unit: dataset currency |
| excess_ES_contribution<br>STEEL | Contribution using total-cost tail weights; excess subtracts component mean (F31)<br>Unit: million source EUR |
| excess_kurtosis_moment<br>PRICE | Standardised third moment / fourth moment minus three<br>Unit: dimensionless |
| exchange_basis<br>PRICE | Declared currency conversion or calorific convention; retain source statement<br>Unit: metadata |
| expanded_eligible<br>CORP | Boolean flag: expanded eligible; this is a test outcome, not probability<br>Unit: boolean |
| expanded_menu_size<br>CORP | Expanded menu size<br>Unit: count |
| expanded_plan<br>CORP | Selected/reference/equivalent plan ID; semicolon separates multiple IDs<br>Unit: identifier |
| expanded_value<br>CORP | Numeric or categorical value of the named item; unit inherited from its row/dataset<br>Unit: row unit |
| extraction<br>PRICE | Evidence, extraction, mapping or accounting status; not a model probability<br>Unit: category |
| extraction_method<br>CORP | Evidence, extraction, mapping or accounting status; not a model probability<br>Unit: category |
| facility_id<br>CORP | Named company/facility/technology/plan/reference/component identifier; joins are exact<br>Unit: identifier |
| factor<br>CORP | Price factor/benchmark series identity; preserve ordering for shared paths<br>Unit: identifier |
| fee_slope<br>REVIEW | Δcaptured/Δavoided, slope of switching charge with fee<br>Unit: ratio |
| feedstock_t<br>NCC | Annual naphtha feed / pellet purchase as named<br>Unit: t/year |
| field<br>CORP | Name of measured parameter, source item, statistic or diagnostic<br>Unit: identifier |
| file_name<br>CORP | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| fiscal_period_end<br>CORP | Financial reporting period or earnings definition<br>Unit: metadata/calendar |
| fiscal_year<br>CORP | Financial reporting period or earnings definition<br>Unit: metadata/calendar |
| fixed_cash_EUR<br>NCC,STEEL | Dated deterministic cash incl. capital and other fixed-price components; dataset-specific boundary<br>Unit: EUR/year |
| fixed_price_cash_source_USD<br>CCS | Annual capital/reline/fixed-price cash component<br>Unit: source USD/year |
| flex_value_bnkrw<br>CORP | Named corporate discounted cost/carbon/policy/perfect-information diagnostic; auxiliary, not a new pilot decision result<br>Unit: billion KRW |
| frequency<br>NCC | Bootstrap frontier membership count divided by replicates<br>Unit: fraction |
| frontier_count<br>NCC | Count of observations, paths, or replications named by field<br>Unit: count |
| gcam_version<br>CORP | Legacy scenario provenance label; current proxies not verified GCAM output<br>Unit: metadata |
| grid_MWh<br>STEEL | Annual purchased power quantity<br>Unit: MWh/year |
| grid_factor<br>NCC | Purchased-power emissions coefficient; initial value or dated value (F22)<br>Unit: tCO2/MWh |
| grid_initial<br>FIGURE,NCC,REVIEW | Purchased-power emissions coefficient; initial value or dated value (F22)<br>Unit: tCO2/MWh |
| grid_mwh<br>NCC | Annual purchased power quantity<br>Unit: MWh/year |
| gross_opex_million_source_USD_y<br>CCS | Gross operating cost before byproduct credits<br>Unit: million source USD/year |
| h2_intensity<br>CORP | Externally purchased hydrogen per product tonne<br>Unit: kg/t |
| heat_basis<br>PRICE | Declared currency conversion or calorific convention; retain source statement<br>Unit: metadata |
| henry_hub<br>PRICE | Aligned historical monthly benchmark log return; raw price units in source series register<br>Unit: log return |
| incorrect_capture_as_avoidance_eligible<br>CCS | Boolean flag: incorrect capture as avoidance eligible; this is a test outcome, not probability<br>Unit: boolean |
| incremental_gas_contract_fraction<br>CCS,REVIEW | Fixed-price coverage fraction; power in company, incremental gas in CCS (F16,F25)<br>Unit: fraction |
| incremental_gross_capex_k<br>CORP | Gross baseline/plan/incremental or renewal capital cash named by field<br>Unit: thousand KRW |
| incremental_npv_KRW<br>FX | Discounted invoice cash for baseline/later payment or their difference<br>Unit: KRW |
| incumbent_capex_unit<br>CORP | New technology / incumbent replacement cost per annual capacity<br>Unit: thousand KRW/(t/year) |
| incumbent_renewal_EUR<br>NCC | Annual construction/new renewal/old renewal cash named in field<br>Unit: EUR/year |
| initial_capex_million_source_USD<br>CCS | Initial installed capital; paid in thirds<br>Unit: million source USD |
| instrument<br>CORP | Support scenario, instrument or validity window; none is used for company review<br>Unit: metadata/calendar |
| interest_expense<br>CORP | Corporate financial observation or historical proxy; not facility energy cost; retain currency and reporting scope<br>Unit: row currency/unit |
| interpretation<br>CORP,NCC,REVIEW | Literal explanatory evidence or boundary statement; read alongside numeric fields<br>Unit: text |
| interval_scope<br>CORP | Accounting/qualification/statistical convention defining the result<br>Unit: category |
| iron_ore<br>PRICE | Aligned historical monthly benchmark log return; raw price units in source series register<br>Unit: log return |
| is_disclosed<br>CORP | Boolean flag: is disclosed; this is a test outcome, not probability<br>Unit: boolean |
| is_missing<br>PRICE | Boolean flag: is missing; this is a test outcome, not probability<br>Unit: boolean |
| item<br>CCS,NCC | Name of measured parameter, source item, statistic or diagnostic<br>Unit: identifier |
| item_type<br>CORP | Name of measured parameter, source item, statistic or diagnostic<br>Unit: identifier |
| japan_lng<br>PRICE | Aligned historical monthly benchmark log return; raw price units in source series register<br>Unit: log return |
| last_reline_year<br>CORP | Calendar year for the event named in the field; adopt=start, op=commissioning; 9999 denotes unavailable<br>Unit: year |
| later<br>REVIEW | Commissioning year in paired timing dominance proof<br>Unit: year |
| later_npv_KRW<br>FX | Discounted invoice cash for baseline/later payment or their difference<br>Unit: KRW |
| later_payment<br>FX | Boolean flag indicating whether this row date is a pricing, baseline settlement or later settlement date in the synthetic example<br>Unit: boolean |
| legacy_conversion_factor<br>PRICE | Recorded unit conversion for legacy comparison; not estimated current FX<br>Unit: conversion ratio |
| legacy_source_id<br>PRICE | Legacy source ID or type of evidence<br>Unit: metadata |
| legacy_value<br>PRICE | Source comparison or arithmetic residual in named unit; not a model input unless marked<br>Unit: row unit |
| licence<br>CORP | Recorded licence/reuse status; bundling locally is not publication clearance<br>Unit: metadata |
| lifetime<br>CORP | Construction duration, technology life or incumbent renewal interval<br>Unit: years |
| limit<br>CORP | Declared diagnostic/feasibility limit<br>Unit: row unit |
| local_scenario<br>PRICE | Conditional scenario label; no scenario probability is implied<br>Unit: category |
| location<br>CCS,CORP,NCC | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| loss_basis<br>CORP | Accounting/qualification/statistical convention defining the result<br>Unit: category |
| maintenance_EUR<br>NCC | Dated capital/maintenance/terminal credit cash named by field<br>Unit: EUR/year |
| maintenance_capex_k<br>CORP | Gross baseline/plan/incremental or renewal capital cash named by field<br>Unit: thousand KRW |
| maintenance_delta_npv<br>NCC | Electric minus conventional discounted component cash<br>Unit: million EUR |
| maintenance_scale<br>NCC | Scale used to distinguish source percentage interpretations<br>Unit: ratio |
| mapping_status<br>CORP | Evidence, extraction, mapping or accounting status; not a model probability<br>Unit: category |
| margin_kthou_t<br>CORP | Operating cost or forgone-margin proxy per actual product tonne<br>Unit: thousand KRW/t |
| market_ng_GJ<br>CCS | Incremental fixed gas / remaining market-priced gas quantity<br>Unit: GJ/year |
| matched_source_scenario<br>PRICE | Conditional scenario label; no scenario probability is implied<br>Unit: category |
| max_common_naphtha_cash_error_KRW<br>FX | Numerical check: max common naphtha cash error KRW; not a statistical uncertainty estimate<br>Unit: named check unit |
| max_error_vs_frozen_cost_KRW_billion<br>FX | Numerical check: max error vs frozen cost KRW billion; not a statistical uncertainty estimate<br>Unit: named check unit |
| max_error_vs_original_FIN_KRW_billion<br>FX | Numerical check: max error vs original FIN KRW billion; not a statistical uncertainty estimate<br>Unit: named check unit |
| max_scaled_constraint_violation<br>CORP | Numerical check: max scaled constraint violation; not a statistical uncertainty estimate<br>Unit: named check unit |
| maximum_baseline_emissions_ratio<br>REVIEW | Candidate/reference cumulative emissions ratio or allowed maximum<br>Unit: ratio |
| maximum_fraction<br>REVIEW | Net additional downstream emissions per captured tonne, or maximum preserving target (F26)<br>Unit: tCO2/tCO2 captured |
| maximum_statistic_error<br>CORP | Numerical check: maximum statistic error; not a statistical uncertainty estimate<br>Unit: named check unit |
| maximum_tcar_change<br>CORP | Numerical check: maximum tcar change; not a statistical uncertainty estimate<br>Unit: named check unit |
| maximum_translation_error<br>CORP | Numerical check: maximum translation error; not a statistical uncertainty estimate<br>Unit: named check unit |
| mean<br>CCS,CORP,FIGURE,FX,NCC,STEEL | Arithmetic sample mean of the named cost/loss variable<br>Unit: dataset currency |
| mean_ES_frontier<br>REVIEW | List of nondominated eligible candidate identifiers; empty means none<br>Unit: identifier list |
| mean_axis<br>NCC | Selection statistic or mean definition; preserve sample vs analytic distinction<br>Unit: category |
| mean_bnkrw<br>CORP | Arithmetic sample mean of the named cost/loss variable<br>Unit: dataset currency |
| mean_mc_se<br>CCS | Monte Carlo mean standard error or explicitly labeled observed mean error; see field context<br>Unit: dataset currency |
| mean_million_EUR<br>REVIEW | Expectation under the declared generator; analytic rather than sampled when named analytic/theoretical<br>Unit: dataset currency |
| mean_monthly_log_return<br>PRICE | Arithmetic mean of historical monthly log returns<br>Unit: log return/month |
| methane_export_signed_MWh<br>NCC | Signed methane exports (negative) or purchased methane (positive)<br>Unit: MWh/year |
| methane_purchased_MWh<br>NCC | Signed methane exports (negative) or purchased methane (positive)<br>Unit: MWh/year |
| metric<br>CORP | Name of measured parameter, source item, statistic or diagnostic<br>Unit: identifier |
| minimum_gas_coefficient<br>REVIEW | Minimum annual coefficient 1.25Δpower+Δmethane in ordering proof<br>Unit: MWh/year |
| minimum_pathwise_difference_million_EUR<br>REVIEW | Analytic lower bound on early minus late cost under affine prices<br>Unit: million EUR |
| minimum_value<br>CORP | Numeric or categorical value of the named item; unit inherited from its row/dataset<br>Unit: row unit |
| model<br>CCS,PRICE,REVIEW | Price generator or source model identity; block_12/1 differ in block length<br>Unit: category |
| monte_carlo_error<br>CORP | Monte Carlo mean standard error or explicitly labeled observed mean error; see field context<br>Unit: dataset currency |
| monte_carlo_mean<br>CORP | Arithmetic sample mean of the named cost/loss variable<br>Unit: dataset currency |
| mult<br>CORP | Positive price multiplier around central path<br>Unit: ratio |
| n_draws<br>CORP,FIGURE,FX,NCC,STEEL | Count of observations, paths, or replications named by field<br>Unit: count |
| n_monthly_returns<br>PRICE | Count of observations, paths, or replications named by field<br>Unit: count |
| naphtha_t<br>NCC | Annual naphtha feed quantity<br>Unit: t/year |
| naphtha_t_per_t_ethylene<br>NCC | Naphtha feed per ethylene output = 1/yield<br>Unit: t/t ethylene |
| net_additional_downstream_fraction_of_capture<br>REVIEW | Net additional downstream emissions per captured tonne, or maximum preserving target (F26)<br>Unit: tCO2/tCO2 captured |
| net_debt<br>CORP | Corporate financial observation or historical proxy; not facility energy cost; retain currency and reporting scope<br>Unit: row currency/unit |
| net_methane_MWh<br>NCC | Purchased minus sold methane; a negative value is a receipt exposure<br>Unit: MWh/year |
| net_reduction<br>REVIEW | Avoided fraction after explicit downstream stress<br>Unit: fraction |
| new_renewal_EUR<br>NCC | Annual construction/new renewal/old renewal cash named in field<br>Unit: EUR/year |
| next_reinvest_year<br>CORP | Calendar year for the event named in the field; adopt=start, op=commissioning; 9999 denotes unavailable<br>Unit: year |
| ng_difference_GJ_y<br>CCS | Published gas quantity / frozen cash-implied quantity / published minus implied<br>Unit: GJ/year |
| nominal_or_real<br>PRICE | Unit/currency/price-year declaration; blanks are unresolved, not zero<br>Unit: metadata |
| non_dominated<br>NCC | Boolean flag: non dominated; this is a test outcome, not probability<br>Unit: boolean |
| noncash_writeoff_k<br>CORP | Remaining-value accounting proxy; excluded from cash investment<br>Unit: thousand KRW |
| note<br>PRICE | Literal explanatory evidence or boundary statement; read alongside numeric fields<br>Unit: text |
| notes<br>CORP | Literal explanatory evidence or boundary statement; read alongside numeric fields<br>Unit: text |
| npv_cost_bnkrw<br>CORP | Named corporate discounted cost/carbon/policy/perfect-information diagnostic; auxiliary, not a new pilot decision result<br>Unit: billion KRW |
| numeric_match<br>PRICE | Boolean flag: numeric match; this is a test outcome, not probability<br>Unit: boolean |
| observation_id<br>PRICE | Unique source observation key<br>Unit: identifier |
| observation_kind<br>CORP | Evidence, extraction, mapping or accounting status; not a model probability<br>Unit: category |
| observations<br>CORP | Count of observations, paths, or replications named by field<br>Unit: count |
| on_analytic_mean_sample_ES_frontier<br>CCS | Boolean flag: on analytic mean sample ES frontier; this is a test outcome, not probability<br>Unit: boolean |
| on_frontier<br>CORP | Boolean flag: on frontier; this is a test outcome, not probability<br>Unit: boolean |
| on_mean_es_frontier<br>CORP | Boolean flag: on mean es frontier; this is a test outcome, not probability<br>Unit: boolean |
| on_mean_tcar_frontier<br>CORP | Boolean flag: on mean tcar frontier; this is a test outcome, not probability<br>Unit: boolean |
| on_sampled_mean_ES_frontier<br>CCS | Boolean flag: on sampled mean ES frontier; this is a test outcome, not probability<br>Unit: boolean |
| op_year<br>CORP | Calendar year for the event named in the field; adopt=start, op=commissioning; 9999 denotes unavailable<br>Unit: year |
| opex_fixed<br>CORP | Annual operating cost per installed annual capacity<br>Unit: thousand KRW/(t/year)/year |
| opex_var<br>CORP | Operating cost or forgone-margin proxy per actual product tonne<br>Unit: thousand KRW/t |
| ore_bundle_count<br>CCS | Number of annual source ore baskets charged; zero before operation, one while active<br>Unit: basket/year |
| original_choice_eligible<br>CORP | Boolean flag: original choice eligible; this is a test outcome, not probability<br>Unit: boolean |
| original_choice_value<br>CORP | Numeric or categorical value of the named item; unit inherited from its row/dataset<br>Unit: row unit |
| output_t<br>NCC,STEEL | Annual product output; ethylene, liquid steel or HRC as named by dataset<br>Unit: t/year |
| output_t_HRC<br>CCS | Annual product output; ethylene, liquid steel or HRC as named by dataset<br>Unit: t/year |
| output_t_HRC_y<br>CCS | Annual product output; ethylene, liquid steel or HRC as named by dataset<br>Unit: t/year |
| p50<br>CCS,CORP,FIGURE,FX,NCC,REVIEW,STEEL | Median using linear interpolation (F04)<br>Unit: dataset currency |
| p50_bnkrw<br>CORP | Median using linear interpolation (F04)<br>Unit: dataset currency |
| p50_incl_carbon<br>CORP | Named corporate discounted cost/carbon/policy/perfect-information diagnostic; auxiliary, not a new pilot decision result<br>Unit: billion KRW |
| p50_incl_carbon_bnkrw<br>CORP | Named corporate discounted cost/carbon/policy/perfect-information diagnostic; auxiliary, not a new pilot decision result<br>Unit: billion KRW |
| p90<br>CORP | Upper quantile: suffix is probability; q_alpha uses recorded alpha (F04)<br>Unit: dataset unit |
| p95<br>FIGURE,REVIEW | Upper quantile: suffix is probability; q_alpha uses recorded alpha (F04)<br>Unit: dataset unit |
| pairing<br>FIGURE,STEEL | joint = common block pairing; permuted = whole ore trajectory reassignment<br>Unit: category |
| param<br>CORP | Name of measured parameter, source item, statistic or diagnostic<br>Unit: identifier |
| param_type<br>CORP | Name of measured parameter, source item, statistic or diagnostic<br>Unit: identifier |
| passed<br>CCS | Boolean flag: passed; this is a test outcome, not probability<br>Unit: boolean |
| paths<br>CCS,FIGURE,FX,NCC,STEEL | Count of observations, paths, or replications named by field<br>Unit: count |
| pathwise_dominance_witness<br>CCS | Candidate with weakly lower paired loss in every sampled state and strict somewhere<br>Unit: identifier |
| pdf_page<br>CCS,NCC,PRICE | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| pellet_t<br>STEEL | Annual naphtha feed / pellet purchase as named<br>Unit: t/year |
| period<br>PRICE | Observation, pricing or settlement date explicitly named in field<br>Unit: calendar |
| permutation<br>STEEL | Random-generator seed or zero-based path/permutation identifier; not observation date<br>Unit: identifier |
| plan_gross_capex_k<br>CORP | Gross baseline/plan/incremental or renewal capital cash named by field<br>Unit: thousand KRW |
| plan_id<br>CCS,CORP | Named company/facility/technology/plan/reference/component identifier; joins are exact<br>Unit: identifier |
| plan_scope1_tco2<br>CORP | Annual direct Scope 1 emissions in company boundary<br>Unit: tCO2/year |
| point<br>CORP | Numeric or categorical value of the named item; unit inherited from its row/dataset<br>Unit: row unit |
| policy_exposure_bnkrw<br>CORP | Named corporate discounted cost/carbon/policy/perfect-information diagnostic; auxiliary, not a new pilot decision result<br>Unit: billion KRW |
| power_MWh<br>NCC | Annual external electricity quantity<br>Unit: MWh/year |
| power_emissions<br>NCC | Annual emissions component/total/reference or terminal quantity/cap named in field<br>Unit: tCO2/year |
| ppa_share<br>CORP | Fixed-price coverage fraction; power in company, incremental gas in CCS (F16,F25)<br>Unit: fraction |
| price_basis<br>CORP | Unit/currency/price-year declaration; blanks are unresolved, not zero<br>Unit: metadata |
| price_date<br>FX | Boolean flag indicating whether this row date is a pricing, baseline settlement or later settlement date in the synthetic example<br>Unit: boolean |
| price_year<br>PRICE | Unit/currency/price-year declaration; blanks are unresolved, not zero<br>Unit: metadata |
| primal_feasible<br>CORP | Boolean flag: primal feasible; this is a test outcome, not probability<br>Unit: boolean |
| procurement_mode<br>REVIEW | Common unhedged physical comparison or joint priced contract menu<br>Unit: category |
| production<br>CORP | Annual facility production, allocated in the frozen portfolio<br>Unit: t/year |
| production_basis<br>CORP | Evidence, extraction, mapping or accounting status; not a model probability<br>Unit: category |
| publication_date<br>CORP | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| publisher<br>CORP | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| q01<br>PRICE | Historical-return percentile at 1%,5%,99%; distinguish from monetary cost quantiles<br>Unit: log return |
| q05<br>PRICE | Historical-return percentile at 1%,5%,99%; distinguish from monetary cost quantiles<br>Unit: log return |
| q95<br>CCS,NCC,PRICE,REVIEW | Upper quantile: suffix is probability; q_alpha uses recorded alpha (F04)<br>Unit: dataset unit |
| q99<br>PRICE | Historical-return percentile at 1%,5%,99%; distinguish from monetary cost quantiles<br>Unit: log return |
| q_alpha<br>FIGURE,FX,NCC,STEEL | Upper quantile: suffix is probability; q_alpha uses recorded alpha (F04)<br>Unit: dataset unit |
| quality_note<br>CORP | Literal explanatory evidence or boundary statement; read alongside numeric fields<br>Unit: text |
| quantity_unit<br>PRICE | Unit/currency/price-year declaration; blanks are unresolved, not zero<br>Unit: metadata |
| quote<br>CORP | Literal explanatory evidence or boundary statement; read alongside numeric fields<br>Unit: text |
| ratio_2024<br>FIGURE | IEA price divided by its own 2024 node<br>Unit: ratio |
| reason<br>CORP | Literal explanatory evidence or boundary statement; read alongside numeric fields<br>Unit: text |
| recent_estimate<br>PRICE | World Bank marker for a recent estimated observation<br>Unit: boolean/category |
| reconstructed_value<br>PRICE | Source comparison or arithmetic residual in named unit; not a model input unless marked<br>Unit: row unit |
| recovery<br>NCC | Useful steam recovery fraction<br>Unit: fraction |
| redistributable<br>CORP | Recorded licence/reuse status; bundling locally is not publication clearance<br>Unit: metadata |
| reduction<br>CORP | Named abatement reduction quantity; retain source unit<br>Unit: row unit |
| region<br>CORP,PRICE | Facility/site/sector/region/compatibility label; not an extra numeric assumption<br>Unit: category |
| reinvest_cycle_yr<br>CORP | Construction duration, technology life or incumbent renewal interval<br>Unit: years |
| reline_source_USD<br>CCS | Annual capital/reline/fixed-price cash component<br>Unit: source USD/year |
| reported<br>CCS | Numeric or categorical value of the named item; unit inherited from its row/dataset<br>Unit: row unit |
| reported_direct_reduction<br>CCS | Source-package direct reduction; older boundary retained for reconciliation<br>Unit: fraction |
| reporting_end<br>CORP | Financial reporting period or earnings definition<br>Unit: metadata/calendar |
| reporting_scope<br>CORP | Literal explanatory evidence or boundary statement; read alongside numeric fields<br>Unit: text |
| reporting_start<br>CORP | Financial reporting period or earnings definition<br>Unit: metadata/calendar |
| representative<br>CORP | Selected/reference/equivalent plan ID; semicolon separates multiple IDs<br>Unit: identifier |
| residual<br>CORP | Source comparison or arithmetic residual in named unit; not a model input unless marked<br>Unit: row unit |
| residual_emissions<br>NCC | Annual emissions component/total/reference or terminal quantity/cap named in field<br>Unit: tCO2/year |
| residual_per_t_naphtha<br>FIGURE,NCC | Common unresolved residual-emissions sensitivity<br>Unit: tCO2/t naphtha |
| resolution<br>CORP | Source time resolution or issue resolution status; retain file context<br>Unit: metadata |
| retained_coal_fraction<br>CORP | Share of incumbent purchased energy retained after adoption (F14)<br>Unit: fraction |
| retained_gas_fraction<br>CORP | Share of incumbent purchased energy retained after adoption (F14)<br>Unit: fraction |
| retained_grid_fraction<br>CORP | Share of incumbent purchased energy retained after adoption (F14)<br>Unit: fraction |
| retention_evidence_status<br>CORP | Evidence, extraction, mapping or accounting status; not a model probability<br>Unit: category |
| retrieved_at<br>CORP | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| retrofit<br>CORP | Source technology compatibility flag; does not determine retention automatically<br>Unit: 0/1 |
| revenue<br>CORP | Corporate financial observation or historical proxy; not facility energy cost; retain currency and reporting scope<br>Unit: row currency/unit |
| risk_proxy<br>CORP | Linear candidate-search surrogate; not reported Monte Carlo TCaR/ES<br>Unit: surrogate units |
| role<br>CCS,REVIEW | Sampling role selection/validation, or external flow purchase/export; dataset context controls<br>Unit: category |
| sample_excess_of_original_choice<br>CORP | Original choice score minus new menu minimum under the same stress<br>Unit: dataset currency |
| sampled_dominance_witness<br>CORP | Candidate with weakly lower paired loss in every sampled state and strict somewhere<br>Unit: identifier |
| sampled_dominated<br>CORP | Boolean flag: sampled dominated; this is a test outcome, not probability<br>Unit: boolean |
| sampled_dominated_candidates<br>CORP | Sampled dominated candidates<br>Unit: count |
| sampled_statewise_dominated<br>CORP | Boolean flag: sampled statewise dominated; this is a test outcome, not probability<br>Unit: boolean |
| scenario<br>CCS,CORP,FIGURE,PRICE,REVIEW | Conditional scenario label; no scenario probability is implied<br>Unit: category |
| scope<br>NCC,PRICE,REVIEW | Literal explanatory evidence or boundary statement; read alongside numeric fields<br>Unit: text |
| sd_monthly_log_return<br>PRICE | Standard deviation of log returns at the named frequency<br>Unit: log-return SD |
| section_SEC_kWh_per_kg_naphtha<br>NCC | Source section energy intensity; not net plant purchase<br>Unit: kWh/kg naphtha |
| sector<br>CORP | Facility/site/sector/region/compatibility label; not an extra numeric assumption<br>Unit: category |
| sector_budget_mt<br>CORP | Scenario sector emissions limit before company scaling<br>Unit: MtCO2/year |
| seed<br>CCS,FIGURE,FX,NCC,REVIEW,STEEL | Random-generator seed or zero-based path/permutation identifier; not observation date<br>Unit: identifier |
| selected_physical_cases<br>REVIEW | Selected physical configurations, with contracts removed from identity<br>Unit: identifier list |
| selected_plan_id<br>CORP | Selected/reference/equivalent plan ID; semicolon separates multiple IDs<br>Unit: identifier |
| selected_plans<br>REVIEW | Selected/reference/equivalent plan ID; semicolon separates multiple IDs<br>Unit: identifier |
| selection_changed<br>CORP | Boolean flag: selection changed; this is a test outcome, not probability<br>Unit: boolean |
| selection_criterion<br>CORP | Selection statistic or mean definition; preserve sample vs analytic distinction<br>Unit: category |
| sensitivity_weight<br>REVIEW | Lambda in mean + lambda ES; a declared preference sensitivity<br>Unit: dimensionless |
| series_id<br>CORP,PRICE | Price factor/benchmark series identity; preserve ordering for shared paths<br>Unit: identifier |
| sha256<br>CORP | SHA-256 fingerprint of source bytes; does not certify economic validity<br>Unit: hash |
| shared_anchor<br>PRICE | Common benchmark/FX anchor identifier in source comparison<br>Unit: metadata |
| sheet<br>PRICE | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| sim<br>CORP | Random-generator seed or zero-based path/permutation identifier; not observation date<br>Unit: identifier |
| site<br>CORP | Facility/site/sector/region/compatibility label; not an extra numeric assumption<br>Unit: category |
| skew_moment<br>PRICE | Standardised third moment / fourth moment minus three<br>Unit: dimensionless |
| solution_status<br>CORP | Solver termination status; distinguish feasibility from optimality<br>Unit: category |
| solve_status<br>CORP | Solver termination status; distinguish feasibility from optimality<br>Unit: category |
| source_column<br>PRICE | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| source_context<br>CORP | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| source_id<br>CORP | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| source_label<br>CORP | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| source_locator<br>CORP | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| source_name<br>CORP,PRICE | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| source_ng_GJ_y<br>CCS | Published gas quantity / frozen cash-implied quantity / published minus implied<br>Unit: GJ/year |
| source_node<br>PRICE | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| source_or_linear_value<br>PRICE | Source comparison or arithmetic residual in named unit; not a model input unless marked<br>Unit: row unit |
| source_price<br>FIGURE | IEA source price node, before ratio conversion<br>Unit: 2024 USD/source unit |
| source_region<br>PRICE | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| source_row<br>PRICE | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| source_sha256<br>CORP,PRICE | SHA-256 fingerprint of source bytes; does not certify economic validity<br>Unit: hash |
| source_table<br>PRICE | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| source_token<br>CCS | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| source_type<br>CORP | Legacy source ID or type of evidence<br>Unit: metadata |
| source_url<br>CCS,CORP,NCC,PRICE | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| squared_return_acf1<br>PRICE | Lag-one sample correlation of returns or squared returns<br>Unit: coefficient |
| start<br>CORP,PRICE | First/last date or index in the named source range<br>Unit: calendar/index |
| state<br>FX | Synthetic scenario state label in settlement example<br>Unit: identifier |
| status<br>CCS,CORP,PRICE | Evidence, extraction, mapping or accounting status; not a model probability<br>Unit: category |
| structural_high<br>CORP | Declared lower/upper sensitivity bound; not automatically a statistical interval<br>Unit: row unit |
| structural_low<br>CORP | Declared lower/upper sensitivity bound; not automatically a statistical interval<br>Unit: row unit |
| support<br>CORP | Support scenario, instrument or validity window; none is used for company review<br>Unit: metadata/calendar |
| support_scenario<br>CORP | Support scenario, instrument or validity window; none is used for company review<br>Unit: metadata/calendar |
| switching_carbon_charge_per_avoided_t<br>REVIEW | Hypothetical emitted-tonne charge or equal-score threshold; incremental benefit uses avoided tonnes (F28)<br>Unit: source USD/tCO2 |
| table<br>PRICE | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| target<br>CCS,REVIEW | Required avoided/reference emissions fraction<br>Unit: fraction |
| target_onsite_reduction<br>CCS | Required avoided/reference emissions fraction<br>Unit: fraction |
| tcar<br>CORP,FIGURE,FX,NCC,STEEL | Upper quantile minus median (F05), not capital budget<br>Unit: dataset currency |
| tcar95<br>CCS,FIGURE,NCC,REVIEW | Upper quantile minus median (F05), not capital budget<br>Unit: dataset currency |
| tcar_bnkrw<br>CORP | Upper quantile minus median (F05), not capital budget<br>Unit: dataset currency |
| tcar_p025<br>NCC | Empirical bootstrap 2.5/97.5 percentile limits (F31)<br>Unit: dataset currency |
| tcar_p975<br>NCC | Empirical bootstrap 2.5/97.5 percentile limits (F31)<br>Unit: dataset currency |
| tech_id<br>CORP | Named company/facility/technology/plan/reference/component identifier; joins are exact<br>Unit: identifier |
| terminal<br>NCC | Terminal-value rule in new-plant sensitivity; none or proxy<br>Unit: category |
| terminal_EUR<br>NCC | Dated capital/maintenance/terminal credit cash named by field<br>Unit: EUR/year |
| terminal_cap<br>FIGURE,NCC | Annual emissions component/total/reference or terminal quantity/cap named in field<br>Unit: tCO2/year |
| terminal_emissions<br>FIGURE,NCC | Annual emissions component/total/reference or terminal quantity/cap named in field<br>Unit: tCO2/year |
| terminal_feasible<br>FIGURE,NCC | Boolean flag: terminal feasible; this is a test outcome, not probability<br>Unit: boolean |
| terminal_proxy_shift<br>FIGURE,REVIEW | Deterministic PV change from symmetric residual-value proxy<br>Unit: million EUR |
| terminal_rule<br>FIGURE,REVIEW | Accounting/qualification/statistical convention defining the result<br>Unit: category |
| text<br>PRICE | Literal explanatory evidence or boundary statement; read alongside numeric fields<br>Unit: text |
| theoretical_mean<br>FIGURE,STEEL | Expectation under the declared generator; analytic rather than sampled when named analytic/theoretical<br>Unit: dataset currency |
| thermal_coal_au<br>PRICE | Aligned historical monthly benchmark log return; raw price units in source series register<br>Unit: log return |
| tied_analytic_minimum_count<br>CORP | Tied analytic minimum count<br>Unit: count |
| title<br>CORP | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| token_found<br>CCS | Boolean flag: token found; this is a test outcome, not probability<br>Unit: boolean |
| tolerance<br>CCS | Numerical check: tolerance; not a statistical uncertainty estimate<br>Unit: named check unit |
| tolerance_source_USD<br>CCS | Numerical check: tolerance source USD; not a statistical uncertainty estimate<br>Unit: named check unit |
| total_debt<br>CORP | Corporate financial observation or historical proxy; not facility energy cost; retain currency and reporting scope<br>Unit: row currency/unit |
| total_emissions<br>NCC | Annual emissions component/total/reference or terminal quantity/cap named in field<br>Unit: tCO2/year |
| total_plant_TOC_at_115t_h_million_EUR2019<br>NCC | Installed plant curve at 115 t ethylene/hour<br>Unit: million EUR2019 |
| transcription<br>NCC | Evidence, extraction, mapping or accounting status; not a model probability<br>Unit: category |
| unit<br>CCS,CORP,NCC,PRICE,REVIEW | Unit/currency/price-year declaration; blanks are unresolved, not zero<br>Unit: metadata |
| unit_name<br>CORP | Facility/site/sector/region/compatibility label; not an extra numeric assumption<br>Unit: category |
| unit_type<br>CORP | Facility/site/sector/region/compatibility label; not an extra numeric assumption<br>Unit: category |
| url_or_doi<br>CORP | Evidence identity, citation, source location or retrieval metadata as named<br>Unit: metadata |
| used<br>CORP | Boolean flag: used; this is a test outcome, not probability<br>Unit: boolean |
| valid_from<br>CORP | Support scenario, instrument or validity window; none is used for company review<br>Unit: metadata/calendar |
| valid_to<br>CORP | Support scenario, instrument or validity window; none is used for company review<br>Unit: metadata/calendar |
| value<br>CCS,CORP,NCC,PRICE | Numeric or categorical value of the named item; unit inherited from its row/dataset<br>Unit: row unit |
| value_bn_native<br>CORP | Corporate financial observation or historical proxy; not facility energy cost; retain currency and reporting scope<br>Unit: row currency/unit |
| value_high<br>CORP | Declared lower/upper sensitivity bound; not automatically a statistical interval<br>Unit: row unit |
| value_low<br>CORP | Declared lower/upper sensitivity bound; not automatically a statistical interval<br>Unit: row unit |
| variable<br>CORP,PRICE | Name of measured parameter, source item, statistic or diagnostic<br>Unit: identifier |
| variant<br>CORP | Baseline, independent-seed or declared structural stress case<br>Unit: category |
| verification_status<br>CORP | Evidence, extraction, mapping or accounting status; not a model probability<br>Unit: category |
| window_ES_difference_with_capital_extension<br>REVIEW | Capital-only extended-window diagnostic; NOT full-horizon ES/TCaR (F23)<br>Unit: million EUR |
| window_TCaR_with_capital_extension<br>REVIEW | Capital-only extended-window diagnostic; NOT full-horizon ES/TCaR (F23)<br>Unit: million EUR |
| year<br>CCS,CORP,FIGURE,NCC,PRICE,STEEL | Calendar year for the event named in the field; adopt=start, op=commissioning; 9999 denotes unavailable<br>Unit: year |
| year_stated<br>CORP | Calendar year for the event named in the field; adopt=start, op=commissioning; 9999 denotes unavailable<br>Unit: year |

### 5. Every file and stored array

The following catalogue lists every package file. CSV rows×columns describe saved records, not necessarily the active analysis subset. Repeated plan files use the same schema, but all45 schedules are retained. Code files are current implementation snapshots. JSON/YAML nested keys and every leaf value are exhaustively listed in metadata_leaf_inventory.csv. Original files retain all values and metadata; no precision is discarded.

### CORP files

docs/research_cycles/2026-09-05/research_case_expanded

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS060 | candidate_expansion_comparison.csv | 24 × 14 |
| DS061 | candidate_expansion_validation.json | 854 bytes |
| DS062 | independent_candidate_risk.csv | 450 × 10 |
| DS063 | paired_annual_capital_and_emissions.csv | 1080 × 11 |
| DS064 | plan_feasibility_and_cost.csv | 45 × 8 |
| DS065 | validation.json | 834 bytes |

docs/research_cycles/2026-09-05/robustness

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS066 | fixed_candidate_bootstrap.csv | 105 × 9 |
| DS067 | manifest.json | 2,487 bytes |

docs/research_cycles/2026-09-05/robustness_initial_forecast

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS068 | manifest.json | 1,334 bytes |

docs/research_cycles/2026-09-05/robustness_verified

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS069 | analytic_means.csv | 450 × 8 |
| DS070 | calibration_series.csv | 6 × 8 |
| DS071 | candidate_statistics.csv | 7650 × 14 |
| DS072 | criterion_choices.csv | 408 × 20 |
| DS073 | equivalent_plans.csv | 2 × 6 |
| DS074 | selected_analytic_means.csv | 8 × 9 |
| DS075 | selection_changes.csv | 17 × 4 |
| DS076 | translation_invariance.csv | 3 × 3 |
| DS077 | validation.json | 1,523 bytes |

tmp/research_case_expanded

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS078 | config.yaml | 1,580 bytes |

tmp/research_case_expanded/run/e1

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS079 | constraints.csv | 192 × 7 |
| DS080 | e1_check.csv | 8 × 4 |
| DS081 | price_paths_central.csv | 576 × 6 |
| DS082 | tech_availability.csv | 0 × 4 |

tmp/research_case_expanded/run/e2

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS083 | plan_index.csv | 45 × 18 |

tmp/research_case_expanded/run/e2/plans

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS084 | plan_P0001.csv | 2 × 10 |
| DS085 | plan_P0002.csv | 2 × 10 |
| DS086 | plan_P0003.csv | 2 × 10 |
| DS087 | plan_P0004.csv | 2 × 10 |
| DS088 | plan_P0005.csv | 2 × 10 |
| DS089 | plan_P0006.csv | 2 × 10 |
| DS090 | plan_P0007.csv | 2 × 10 |
| DS091 | plan_P0008.csv | 10 × 10 |
| DS092 | plan_P0009.csv | 10 × 10 |
| DS093 | plan_P0010.csv | 10 × 10 |
| DS094 | plan_P0011.csv | 10 × 10 |
| DS095 | plan_P0012.csv | 10 × 10 |
| DS096 | plan_P0013.csv | 10 × 10 |
| DS097 | plan_P0014.csv | 10 × 10 |
| DS098 | plan_P0015.csv | 8 × 10 |
| DS099 | plan_P0016.csv | 8 × 10 |
| DS100 | plan_P0017.csv | 8 × 10 |
| DS101 | plan_P0018.csv | 8 × 10 |
| DS102 | plan_P0019.csv | 8 × 10 |
| DS103 | plan_P0020.csv | 8 × 10 |
| DS104 | plan_P0021.csv | 8 × 10 |
| DS105 | plan_P0022.csv | 8 × 10 |
| DS106 | plan_P0023.csv | 2 × 10 |
| DS107 | plan_P0024.csv | 2 × 10 |
| DS108 | plan_P0025.csv | 2 × 10 |
| DS109 | plan_P0026.csv | 2 × 10 |
| DS110 | plan_P0027.csv | 2 × 10 |
| DS111 | plan_P0028.csv | 2 × 10 |
| DS112 | plan_P0029.csv | 2 × 10 |
| DS113 | plan_P0030.csv | 2 × 10 |
| DS114 | plan_P0031.csv | 2 × 10 |
| DS115 | plan_P0032.csv | 2 × 10 |
| DS116 | plan_P0033.csv | 2 × 10 |
| DS117 | plan_P0034.csv | 2 × 10 |
| DS118 | plan_P0035.csv | 10 × 10 |
| DS119 | plan_P0036.csv | 10 × 10 |
| DS120 | plan_P0037.csv | 10 × 10 |
| DS121 | plan_P0038.csv | 10 × 10 |
| DS122 | plan_P0039.csv | 10 × 10 |
| DS123 | plan_P0040.csv | 8 × 10 |
| DS124 | plan_P0041.csv | 8 × 10 |
| DS125 | plan_P0042.csv | 8 × 10 |
| DS126 | plan_P0043.csv | 8 × 10 |
| DS127 | plan_P0044.csv | 8 × 10 |
| DS128 | plan_P0045.csv | 8 × 10 |

tmp/research_case_expanded/run/e3

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS129 | calibration_report.csv | 9 × 2 |
| DS130 | price_model.json | 3,120 bytes |
| DS131 | price_sims.parquet | 960000 × 4 |

tmp/research_case_expanded/run/e5

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS132 | frontier_points.csv | 450 × 34 |
| DS133 | metrics_company.csv | 8 × 21 |

tmp/research_case_expanded/run

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS134 | run_manifest.json | 14,274 bytes |

tmp/research_case_v3/data

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS135 | D1a_facility_static.csv | 22 × 17 |
| DS136 | D1b_facility_panel.csv | 66 × 11 |
| DS137 | D2a_scenario_budget.csv | 48 × 7 |
| DS138 | D2b_scenario_prices.csv | 224 × 7 |
| DS139 | D3_tech_options.csv | 13 × 19 |
| DS140 | D3b_tech_bands.csv | 3 × 8 |
| DS141 | D4_price_history.csv | 99 × 5 |
| DS142 | D5_policy_support.csv | 7 × 9 |
| DS143 | D6_company_financials.csv | 4 × 14 |
| DS144 | D7_disclosed_plan.csv | 12 × 10 |
| DS145 | company_observation_reconciliation.csv | 12 × 9 |
| DS146 | energy_retention_assumptions.csv | 39 × 9 |
| DS147 | excluded_assets.csv | 1 × 17 |
| DS148 | legacy_financials_unverified.csv | 22 × 10 |
| DS149 | modeled_portfolio_totals.csv | 12 × 6 |
| DS150 | source_register.csv | 82 × 16 |
| DS151 | verified_financial_native_units.csv | 50 × 16 |

### PRICE files

data/research_v2/block_price_paths

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS183 | manifest.json | 1,631 bytes |

data/research_v2/iea_2025_scenarios

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS184 | annual_reference_curves.csv | 729 × 13 |
| DS185 | curves.json | 16,210 bytes |
| DS186 | legacy_alignment_audit.csv | 36 × 17 |
| DS187 | legacy_alignment_manifest.json | 895 bytes |
| DS188 | manifest.json | 1,778 bytes |
| DS189 | native_observations.csv | 63 × 16 |
| DS190 | scenario_nodes.csv | 81 × 11 |

data/research_v2/price_history

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS191 | aligned_monthly_log_returns.csv | 191 × 7 |
| DS192 | manifest.json | 1,203 bytes |
| DS193 | monthly_log_return_correlation.csv | 6 × 7 |
| DS194 | monthly_log_return_diagnostics.csv | 6 × 15 |
| DS195 | native_monthly_prices.csv | 4800 × 15 |
| DS196 | source_comparison_notes.json | 22,377 bytes |
| DS197 | source_series_descriptions.csv | 104 × 2 |

### NCC files

data/research_v2/ncc_reference_cash

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS163 | annual_cash.csv | 768 × 11 |
| DS164 | conditional_metrics.csv | 64 × 18 |
| DS165 | incremental_cost_draws.npz | 593,847 bytes |
| DS166 | manifest.json | 2,937 bytes |
| DS167 | translation_checks.json | 1,171 bytes |

data/research_v2/ncc_timing_frontier

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS168 | annual_cash.csv | 96 × 10 |
| DS169 | annual_emissions.csv | 384 × 11 |
| DS170 | annual_prices.npz | 5,354,156 bytes |
| DS171 | bootstrap_precision.csv | 8 × 9 |
| DS172 | cost_draws.npz | 292,562 bytes |
| DS173 | frontier_membership.csv | 16 × 5 |
| DS174 | manifest.json | 4,841 bytes |
| DS175 | paired_bootstrap_membership.csv | 8 × 7 |
| DS176 | qualification.csv | 16 × 15 |
| DS177 | risk_metrics.csv | 6 × 10 |

data/research_v2/tiggeloven_reference

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS178 | boundary_checks.json | 471 bytes |
| DS179 | derived_quantities.csv | 2 × 5 |
| DS180 | manifest.json | 1,165 bytes |
| DS181 | package.json | 1,684 bytes |
| DS182 | source_observations.csv | 39 × 9 |

### CCS files

data/research_v2/ieaghg_paired

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS001 | STEPS_validation_absolute_costs.npz | 822,796 bytes |
| DS002 | STEPS_validation_incremental_costs.npz | 591,382 bytes |
| DS003 | annual_cash_quantities.csv | 240 × 11 |
| DS004 | conditional_cost_metrics.csv | 120 × 18 |
| DS005 | finite_frontier.csv | 180 × 8 |
| DS006 | independent_selection.json | 7,949 bytes |
| DS007 | manifest.json | 4,132 bytes |

data/research_v2/ieaghg_physical_reference

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS008 | arithmetic_checks.csv | 12 × 6 |
| DS009 | emissions_qualification.csv | 15 × 5 |
| DS010 | legacy_transcription_checks.csv | 75 × 5 |
| DS011 | manifest.json | 2,732 bytes |
| DS012 | physical_source_observations.csv | 23 × 7 |
| DS013 | same_product_ledger.csv | 3 × 15 |

data/research_v2/ieaghg_reference

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS014 | account_checks.csv | 10 × 6 |
| DS015 | manifest.json | 824 bytes |
| DS016 | package.json | 5,928 bytes |
| DS017 | source_observations.csv | 75 × 8 |

### STEEL files

data/research_v2/steel_cost_reference

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS212 | vogl_main_text_package.json | 3,403 bytes |

data/research_v2/steel_procurement_tail

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS213 | annual_ledger.csv | 24 × 7 |
| DS214 | conditional_risk.csv | 12 × 13 |
| DS215 | dependence.csv | 4 × 3 |
| DS216 | independent_verification.json | 591 bytes |
| DS217 | manifest.json | 3,839 bytes |
| DS218 | manuscript_verification.json | 286 bytes |
| DS219 | pairing_randomization.csv | 800 × 6 |
| DS220 | paths.npz | 4,447,680 bytes |
| DS221 | source_register.json | 2,387 bytes |
| DS222 | tail_allocation.csv | 36 × 7 |

### FX files

data/research_v2/invoice_fin_bridge

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS158 | frozen_FIN_comparison.csv | 8 × 7 |
| DS159 | paired_risk_metrics.csv | 6 × 9 |
| DS160 | timing_example_costs.csv | 2 × 4 |
| DS161 | timing_example_inputs.csv | 8 × 8 |
| DS162 | verification.json | 2,078 bytes |

### REVIEW files

docs/research_cycles/2026-09-10-investment-review/cycle1

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS198 | cost_decomposition.csv | 24 × 3 |
| DS199 | editorial_verification.json | 860 bytes |
| DS200 | emissions_budget_sweep.csv | 36 × 6 |
| DS201 | terminal_sensitivity.csv | 16 × 10 |
| DS202 | verification.json | 1,750 bytes |

docs/research_cycles/2026-09-10-investment-review/cycle2

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS203 | carbon_charge_switching_thresholds.csv | 192 × 9 |
| DS204 | downstream_emissions_margins.csv | 8 × 8 |
| DS205 | editorial_verification.json | 558 bytes |
| DS206 | ncc_continuation_dominance_bounds.csv | 3 × 5 |
| DS207 | ncc_matched_continuation.csv | 8 × 7 |
| DS208 | physical_and_contract_choices.csv | 288 × 8 |
| DS209 | policy_and_procurement_choices.csv | 576 × 8 |
| DS210 | reference_risk_comparison.csv | 10 × 7 |
| DS211 | verification.json | 2,199 bytes |

### FIGURE files

output/pilot_review/figure_data

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS152 | discount_weights.csv | 72 × 3 |
| DS153 | ncc_qualification.csv | 16 × 15 |
| DS154 | ncc_risk_metrics.csv | 6 × 10 |
| DS155 | ncc_tcar_quantiles.csv | 8 × 10 |
| DS156 | scenario_nodes.csv | 18 × 5 |
| DS157 | steel_risk_metrics.csv | 6 × 13 |

### CODE files

scripts

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS018 | audit_ieaghg_physical_reference.py | 7,917 bytes |
| DS019 | audit_investment_timing_review.py | 8,678 bytes |
| DS020 | audit_research_robustness.py | 13,280 bytes |
| DS021 | expand_research_candidates.py | 7,066 bytes |
| DS022 | extract_iea_scenario_reference.py | 7,128 bytes |
| DS023 | extract_worldbank_price_history.py | 6,252 bytes |
| DS024 | prepare_research_case.py | 7,269 bytes |
| DS025 | research_block_price_paths.py | 7,170 bytes |
| DS026 | review_technology_investment_cycle2.py | 14,848 bytes |
| DS027 | run_ieaghg_paired_reference.py | 16,463 bytes |
| DS028 | run_ncc_reference_cash.py | 10,435 bytes |
| DS029 | run_ncc_timing_frontier.py | 13,253 bytes |
| DS030 | run_steel_procurement_tail_audit.py | 12,091 bytes |
| DS031 | verify_invoice_fin_bridge.py | 8,199 bytes |
| DS032 | verify_research_robustness.py | 9,210 bytes |

src/cap

| ID | Filename | Size / shape |
| --- | --- | --- |
| DS033 | block_moments.py | 3,007 bytes |
| DS034 | calibration.py | 6,573 bytes |
| DS035 | capital_ledger.py | 6,342 bytes |
| DS036 | carbon_accounting.py | 3,057 bytes |
| DS037 | commodity_ledger.py | 3,848 bytes |
| DS038 | component_capital.py | 5,190 bytes |
| DS039 | config.py | 1,195 bytes |
| DS040 | e1_constraints.py | 7,276 bytes |
| DS041 | e2_milp.py | 30,514 bytes |
| DS042 | e3_prices.py | 8,996 bytes |
| DS043 | e4_revalue.py | 8,142 bytes |
| DS044 | e5_metrics.py | 28,701 bytes |
| DS045 | energy_balance.py | 1,554 bytes |
| DS046 | financial_reference.py | 2,694 bytes |
| DS047 | fx_settlement.py | 11,001 bytes |
| DS048 | input_boundaries.py | 2,229 bytes |
| DS049 | invoice_fin.py | 7,499 bytes |
| DS050 | plancost.py | 22,254 bytes |
| DS051 | price_process.py | 6,787 bytes |
| DS052 | reference_incumbent.py | 6,049 bytes |
| DS053 | reference_ncc.py | 6,849 bytes |
| DS054 | reference_steel.py | 5,835 bytes |
| DS055 | reference_timing.py | 4,694 bytes |
| DS056 | risk_metrics.py | 4,640 bytes |
| DS057 | scenario_prices.py | 8,907 bytes |
| DS058 | schemas.py | 4,123 bytes |
| DS059 | tail_attribution.py | 2,121 bytes |

\pagebreak

### 5.1 Array names, dimensions and interpretation

Array axes are always read with the generating script: cost vectors [path], annual price/multiplier arrays [path, year], block_starts [path, block], log_anchors [month, factor], and permutation [path] as a zero-based reassignment. Years are 2027–2050 where length24; NCC fixed source pools have5000 paths; CCS saved validation vectors have10000. Shared prefix/seed matches paired paths. Minimum/maximum, dtype and element count are recorded for every array in array_inventory.csv.

| Dataset ID | Exact array name | Shape / dtype |
| --- | --- | --- |
| DS001 | REFERENCE | [10000] / float64 |
| DS001 | EOP_L1_h0.00 | [10000] / float64 |
| DS001 | EOP_L1_h0.25 | [10000] / float64 |
| DS001 | EOP_L1_h0.50 | [10000] / float64 |
| DS001 | EOP_L1_h0.75 | [10000] / float64 |
| DS001 | EOP_L1_h1.00 | [10000] / float64 |
| DS001 | EOP_L2_h0.00 | [10000] / float64 |
| DS001 | EOP_L2_h0.25 | [10000] / float64 |
| DS001 | EOP_L2_h0.50 | [10000] / float64 |
| DS001 | EOP_L2_h0.75 | [10000] / float64 |
| DS001 | EOP_L2_h1.00 | [10000] / float64 |
| DS002 | EOP_L1_h0.00 | [10000] / float64 |
| DS002 | EOP_L1_h0.25 | [10000] / float64 |
| DS002 | EOP_L1_h0.50 | [10000] / float64 |
| DS002 | EOP_L1_h0.75 | [10000] / float64 |
| DS002 | EOP_L1_h1.00 | [10000] / float64 |
| DS002 | EOP_L2_h0.00 | [10000] / float64 |
| DS002 | EOP_L2_h0.25 | [10000] / float64 |
| DS002 | EOP_L2_h0.50 | [10000] / float64 |
| DS002 | EOP_L2_h0.75 | [10000] / float64 |
| DS002 | EOP_L2_h1.00 | [10000] / float64 |
| DS165 | r0.8_life20_psi0.01_none | [5000] / float64 |
| DS165 | r0.8_life20_psi0.01_straight_line_proxy | [5000] / float64 |
| DS165 | r0.8_life20_psi1.0_none | [5000] / float64 |
| DS165 | r0.8_life20_psi1.0_straight_line_proxy | [5000] / float64 |
| DS165 | r0.8_life30_psi0.01_none | [5000] / float64 |
| DS165 | r0.8_life30_psi0.01_straight_line_proxy | [5000] / float64 |
| DS165 | r0.8_life30_psi1.0_none | [5000] / float64 |
| DS165 | r0.8_life30_psi1.0_straight_line_proxy | [5000] / float64 |
| DS165 | r1.0_life20_psi0.01_none | [5000] / float64 |
| DS165 | r1.0_life20_psi0.01_straight_line_proxy | [5000] / float64 |
| DS165 | r1.0_life20_psi1.0_none | [5000] / float64 |
| DS165 | r1.0_life20_psi1.0_straight_line_proxy | [5000] / float64 |
| DS165 | r1.0_life30_psi0.01_none | [5000] / float64 |
| DS165 | r1.0_life30_psi0.01_straight_line_proxy | [5000] / float64 |
| DS165 | r1.0_life30_psi1.0_none | [5000] / float64 |
| DS165 | r1.0_life30_psi1.0_straight_line_proxy | [5000] / float64 |
| DS170 | 20260917_power | [5000, 24] / float64 |
| DS170 | 20260917_methane | [5000, 24] / float64 |
| DS170 | 20260917_naphtha | [5000, 24] / float64 |
| DS170 | 20260918_power | [5000, 24] / float64 |
| DS170 | 20260918_methane | [5000, 24] / float64 |
| DS170 | 20260918_naphtha | [5000, 24] / float64 |
| DS172 | 20260917_baseline | [5000] / float64 |
| DS172 | 20260917_replace_2030 | [5000] / float64 |
| DS172 | 20260917_replace_2035 | [5000] / float64 |
| DS172 | 20260917_replace_2040 | [5000] / float64 |
| DS172 | 20260918_baseline | [5000] / float64 |
| DS172 | 20260918_replace_2030 | [5000] / float64 |
| DS172 | 20260918_replace_2035 | [5000] / float64 |
| DS172 | 20260918_replace_2040 | [5000] / float64 |
| DS220 | power_20260923 | [5000, 24] / float64 |
| DS220 | ore_20260923 | [5000, 24] / float64 |
| DS220 | permutation_20260923 | [5000] / int64 |
| DS220 | block_starts_20260923 | [5000, 24] / int64 |
| DS220 | log_anchors_20260923 | [288, 6] / float64 |
| DS220 | cost_20260923_joint_0.0 | [5000] / float64 |
| DS220 | cost_20260923_joint_0.5 | [5000] / float64 |
| DS220 | cost_20260923_joint_1.0 | [5000] / float64 |
| DS220 | cost_20260923_permuted_0.0 | [5000] / float64 |
| DS220 | cost_20260923_permuted_0.5 | [5000] / float64 |
| DS220 | cost_20260923_permuted_1.0 | [5000] / float64 |
| DS220 | power_20260924 | [5000, 24] / float64 |
| DS220 | ore_20260924 | [5000, 24] / float64 |
| DS220 | permutation_20260924 | [5000] / int64 |
| DS220 | block_starts_20260924 | [5000, 24] / int64 |
| DS220 | log_anchors_20260924 | [288, 6] / float64 |
| DS220 | cost_20260924_joint_0.0 | [5000] / float64 |
| DS220 | cost_20260924_joint_0.5 | [5000] / float64 |
| DS220 | cost_20260924_joint_1.0 | [5000] / float64 |
| DS220 | cost_20260924_permuted_0.0 | [5000] / float64 |
| DS220 | cost_20260924_permuted_0.5 | [5000] / float64 |
| DS220 | cost_20260924_permuted_1.0 | [5000] / float64 |

### 5.2 Coverage checklist and interpretation limits

| Check | Requirement |
| --- | --- |
| Data | Every registered file exists and its copied bytes match SHA-256. |
| Variables | Every CSV/Parquet field occurs in both dictionaries; every NPZ key appears in array inventory. |
| Parameters | Every JSON/YAML leaf is retained; raw input rows preserved without rounding. |
| Equations | 36 numbered formula groups cover cash, quantities, gates, prices, statistics and decision use. |
| Body | Original main text, six figures and nine tables preserved; appended OOXML checked. |
| Claims | No new corporate calibration, validated full-chain CCS, completed system coupling or released public DB is asserted. |

Coverage is exhaustive against the declared package and paper calculation register, not a claim that every omitted real-world process has been measured. In particular, tax, financing, working capital, actual procurement basis/default/volume risks, closure proceeds and full-chain CO2 accounting still need matched evidence. Their absence is an explicit modeling limitation, not a zero-valued observation. PLANiT integration and the public mitigation-technology database should make these boundaries and transformations versioned and reviewable.
