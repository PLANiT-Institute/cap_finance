\pagebreak

### 부록 D 데이터·변수·산식 전체 설명

이 부록은 이 리뷰 페이퍼를 뒷받침하는 범위를 지정한 근거 묶음의 모든 데이터셋·필드·저장 배열을 설명한다. 관측값·명시적 가정·계산 물량·진단 메타데이터를 구분한다. 저장소의 무관한 실험까지 전부 설명한다는 주장은 하지 않는다.

읽는 순서: 1 근거 연결 → 2 고정 입력·원문 물량 → 3 변수 정의가 붙은 산식 → 4 전체 필드 사전 → 5 파일·배열 목록과 감사. 역사자료의 모든 행과 몬테카를로 경로는 PLANiT_Pilot_Data_Appendix.zip에 반올림 없이 보존했다. Word 표는 계산을 이해하기 위한 것이며 동봉 원본은 대표값만이 아니라 기록된 모든 값을 포함한다.

DSxxx는 정확한 파일 ID, F01–F36는 계산 ID다. 여러 화폐 맥락에 쓰이는 필드는 해당 데이터셋 단위를 따른다. 원천 공란을 0으로 해석하지 않는다. 아래 입력 표는 읽기 위한 정밀도로 표시하고 원본에는 전체 정밀도를 유지한다. 파일에 포함됐다는 이유로 비활성 옵션이 실제 사용됐다고 보지 않는다.

| 근거 | 본문 용도 | 산식 / 범위 |
| --- | --- | --- |
| D1 / CORP | 부록 A; 계약·실물 선택 구분 | F01–18; billion declared KRW |
| D2 / PRICE | 시나리오·과거 충격·가정 그림 | F09–13; source units → ratios |
| D3 / NCC | 메인 TCaR·투자시점·배출자격·수명 예시 | F18–23; million assumed EUR |
| D4 / STEEL | 펠릿 연동·꼬리 노출 | F29–31; absolute million source EUR |
| D5 / FX | 청구·결제 회계 시연 | F32–33; explicitly dated currencies |
| D6–7 / REVIEW | 시점 분해·CCS 기술·정책 선택 | F23–28; same-output comparisons |
| CCS | 원문 현금 패키지·후속 물리 감사 | F24–28; million source USD |
| FIGURE | 그림 1–5의 반올림 전 데이터 | 그림 6은 제안 구조; 수치 결과 없음 |

\pagebreak

### 1. 재현 범위와 상태

목록에는 파일 222개, 파일별 필드 1357개, 중복을 제거한 필드명 462개, 이름 있는 배열 73개가 있다. 모든 파일의 SHA-256을 기록했다. 관측·입력·동결 결과·검증 기록·현행 구현 사본의 역할을 구분한다.

과거 manifest는 그대로 보존했다. 과거 해시 선언 5건은 현재 참조 파일과 다르다. 구현 2개(e5_metrics.py, plancost.py) 및 후속 검토에서 수정된 원고 3개다. 과거 기록을 덮어쓰지 않았고 현행 코드를 과거 실행본과 동일하다고 주장하지 않는다. 이 페이퍼의 근거는 동결 입력·결과와 독립 산술 대조이며 과거 전체 실행의 비트 단위 재현은 주장하지 않는다.

출처 등록부에는 사용하지 않은 항목도 있다. D3b는 근거·민감도 기록, D5는 지원 없음으로 비활성, D6 재무는 배경자료, D7 공시계획은 동결 비교 후보에서 제외됐다. NCC 배터리·풍력·태양광·탱크 원문 행은 보존하되 시점 원장에는 청구하지 않는다. CCS의 과거 출처상태 표지는 보존하고 후속 선택 페이지 감사는 명시적으로 대조한 물리 필드에만 우선한다.

\pagebreak

### 2. 고정 입력과 원문 사양

### 2.1 기업 실행 설정

DS078 · tmp/research_case_expanded/config.yaml

| 설정 키 | 동결 값 |
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

저장된 설정의 모든 말단 값을 나열했다. 최적화 설정은 유한 후보 생성에 쓰이고 가격 대안·지원 설정·수소 대체식 계수가 전부 기준 실행에 활성인 것은 아니다. capex_shock_scaling 생략 시 현행 기본은 positive_lognormal이다. 2027 가격은 확정이고 연간 경로는 24열이다.

\pagebreak

### 2.2 추정값과 전체 기술 옵션

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

전력 σ=0.24244650997167314는 짧은 계열의 평균 통계이고 H2 .25·건설 .06은 대체 가정값이다. 전해조 추세감소 .05·잔차 σ .10은 별도 가정이다. D2b에 h2_price/re_price가 있으면 대체식보다 우선한다. 수소 대체식이 필요하면 전력단가×52/1000+전해조 KRW/kW×.12/150이며 전해조 중심가격은 마지막 앵커에서 지수적으로 감소한다.

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

steel_eaf의 applies_to_unit=NONE(현 자산 메뉴에 미적용)을 포함해 모든 기술 행을 표시했다. 출처 ID·잔존비율 근거상태 원문은 CSV와 사전에 남겼다. 비용·에너지 숫자는 근거 품질이 다른 모형 입력이며 검증 견적이 아니다.

\pagebreak

### 2.3 전체 모형 자산과 평균 운영 입력

DS135 · tmp/research_case_v3/data/D1a_facility_static.csv

DS136 · tmp/research_case_v3/data/D1b_facility_panel.csv

22개 자산을 모두 표시했다. 운영 열은 저장된 3개 연도를 평균했고 원래 연도별 66행은 동봉했다. 제품 능력 단위와 배분 한계는 D1a/D1b에 보존하며 하나의 검증된 제품 정의로 합치지 않는다. 전력은 MWh/년, 석탄·가스 GJ/년, Scope 1은 tCO2/년이다. 생산능력·생산량의 제품 범위 차이를 유지한다.

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

### 자산 입력 계속 2

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

### 자산 입력 계속 3

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

### 2.4 기업 시나리오 앵커와 예산

DS138 · tmp/research_case_v3/data/D2b_scenario_prices.csv

| 계열 / 단위 | 모든 연도:값 앵커 |
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

### 기업 예산 전체 앵커

DS137 · tmp/research_case_v3/data/D2a_scenario_budget.csv

| 계열 / 단위 | 모든 연도:값 앵커 |
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

### 2.5 IEA 노드·세계은행 변환

DS185 · data/research_v2/iea_2025_scenarios/curves.json

| 계열 / 지역 / 시나리오 | 단위 | 2024 | 2035 | 2050 |
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

저장된 27곡선을 전부 표시했으며 그림·공정 실행에 선택되지 않은 계열도 포함된다. 원문은 2024 USD이며 계열 내 비율만 공장 가정 앵커에 연결한다. 세계은행 전체 추출표는 6계열·2026.8까지 4800행이다. 선택한 2010–2025 구간은 계열당 가격 192개에서 191×6 로그수익률을 만든다. 이후 관측값은 추정에서 제외한다. 원문 정의·결측 표지·출처 대조 주의도 보존한다.

\pagebreak

### 2.6 NCC 원문 관측과 가정

DS182 · data/research_v2/tiggeloven_reference/source_observations.csv

| 공정 / 원문 항목 | 값 | 단위 / PDF쪽 |
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

| 가정 키 | 저장된 전체 값 |
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

| 가정 키 | 저장된 전체 값 |
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

수명 예시는 기존 설비 시점 비교가 아닌 신규공장 비교다: 회수율1, 블록12, 시드20260913, 유지비배율1, 수명20/30, 종료없음/대용치. 종료없음의 해석적 평균은 3963.988·3636.696백만 EUR, 공통표본 TCaR는 857.615다. 시점 실험은 전환 전에도 계속 생산하고 기존 잔여수명이8년이다. 기준안을 합치지 않는다.

\pagebreak

### 2.7 CCS 원문 청구액·물리 대조

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

| 원문 바스켓 | 물량, 톤/년 |
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

CCS 설정: 2027–2050·할인5%·건설2027–29·가동2030–50·개수2044·종료0; 가스/광석 충격만, 가스 프리미엄3%; h=0,.25,.5,.75,1; IEA CPS/STEPS/NZE·블록1/12; 선택2500경로 시드20260910·평가10000경로 시드20260911. 모형 사양 간 시드를 재사용하므로 모든 비교가 독립 난수는 아니다. 목표 .50/.60/.604, λ=0,.01,.1,1이다. 문턱분석 k=0,20,50,100; 정책 격자는 k=0,20,50 및 c=0,50,100,200,500,1000이다. 금액은 해당 CO2톤당 원문 USD다.

\pagebreak

### 2.8 철강·청구 참조 입력

DS212 · data/research_v2/steel_cost_reference/vogl_main_text_package.json

| 정확한 입력 키 | 원문 값 |
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

패키지 외 실험 설정: 설치능력100만톤/년·이용률.75·건설2027–29·가동2030–50·r=.05·β=0/.5/1·산소판매.6·계산환산1500KRW/EUR·시드20260923/24·각5000경로·12개월블록·시드당200순열·순열난수시드+1000·α=.95·종료0이다. 직접배출계수0은 현금모형 자리표시자이지 무배출 검증이나 적격성 검사가 아니다. 탄소·세금·금융·운전자본·기존 설비 비용은 제외됐다.

\pagebreak

### 합성 결제 예시

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

청구 연계 검증은 NCC 표본에 확정1000KRW/EUR·물가지수1을 쓴다. 별도 두 상태 결제 예시는 합성값으로 위 날짜별 값은 실제 환율 예측이 아니다. 자료 구조의 정의·결제식은 F32–33과 코드 사본에 있다.

\pagebreak

### 3. 전체 계산 등록부

각 산식마다 해당 변수·단위를 설명했다. 아래첨자는 곱셈이 아닌 인덱스다. 같은 짧은 기호를 다른 실험에서 쓰면 해당 절의 정의를 따른다. 식은 Word에서 편집 가능한 수식 개체다. 상수는 2절 입력과 5절 파일 ID로 추적한다.

### F01 의사결정·상태·공통 기준안

$$x=(d,h);\quad L_n(x\mid s,\theta)=C_n(x\mid s,\theta)-C_n(x_0\mid s,\theta)$$

d는 기술과 가동 일정, h는 구매·EPC 계약이다. n은 두 대안에 공통인 확률경로, s는 시나리오, θ는 구조적 가정, x₀는 같은 생산 서비스를 제공하는 기준안이다. C는 할인 현금비용, L은 기준안 대비 증분비용이다. 시나리오·가정에는 확률을 부여하지 않았다. 펠릿 실험은 일치하는 기준안이 없어 C를 보고한다.

구현: src/cap/plancost.py; src/cap/invoice_fin.py

### F02 현금 범위와 할인

$$d_t=(1+r)^{-(t-t_0)}$$

$$C_n=\sum_t d_t\left[K_{nt}+O_t+\sum_j P_{njt}q_{jt}+Z_{nt}+H_{nt}-S_{nt}\right]-d_TV_T$$

기준시점 t₀=2027, 종료 T=2050, 기본 할인율 r=0.05다. K는 건설·갱신 현금, O는 기타 운영 현금, P는 외부 단가, q는 부호를 갖는 물량, Z는 탄소 지급액, H는 별도 계약 지급액, S는 보조금·수입, V는 종료 현금이다. 판매 물량은 음수다. 계약·보조금이 이미 P 또는 K에 반영됐다면 H·S로 다시 계상하지 않는다. 과거 투자와 비현금 손상은 신규 지급액이 아니다.

구현: src/cap/plancost.py:simulate_cost

\pagebreak

### F03 단위 및 계산 검사용 환산

$$C\ [\mathrm{billion\ KRW}]=10^{-6}\sum_t d_t\,\mathrm{cash}_t\ [\mathrm{thousand\ KRW}]$$

$$C\ [\mathrm{million\ source\ currency}]=(1000/f)C_{\mathrm{FIN}}$$

f는 계산 검사용 원화/원문통화 환산값이며 NCC·CCS는 1000, Vogl은 1500이다. 입력에 f를 곱하고 결과에서 다시 되돌리므로 실제 환율 추정이 아니다. 원문 EUR·USD와 선언된 2025 KRW를 통일된 화폐로 비교하지 않는다. 1 kWh/kg=1 MWh/t이고 1000 kW=1 MW다. 설비능력당 투자비와 실제 생산량당 비용은 분모가 다르다.

구현: src/cap/plancost.py; scripts/run_steel_procurement_tail_audit.py

### F04 평균과 보간 분위수

$$\widehat\mu=N^{-1}\sum_n L_n;\quad h_p=(N-1)p;\quad j=\lfloor h_p\rfloor;\quad a=h_p-j$$

$$\widehat q_p=(1-a)L_{(j+1)}+aL_{(j+2)}$$

L_(i)는 오름차순 i번째 값(1부터)이다. p=1이면 최댓값 L_(N)을 쓴다. N은 경로 수다. 분위수는 NumPy 선형보간, 즉 PERCENTILE.INC 규약이다. 해석적·이론 평균은 표본평균과 다르다. 물량이 확정되고 현금이 가격의 아핀함수이며 E[M]=1일 때 M을 1로 놓아 기대값을 계산한다. 비선형 현금이나 확률적 물량에는 그대로 적용할 수 없다.

구현: src/cap/risk_metrics.py:loss_summary

\pagebreak

### F05 TCaR와 예산 질문

$$\mathrm{TCaR}_\alpha=\widehat q_\alpha(L)-\widehat q_{0.5}(L);\quad \mathrm{funding\ gap}_\alpha=\widehat q_\alpha(L)-B$$

기업 사례의 α는 0.90, 공정 실험은 0.95다. B는 같은 통화·할인·손실 범위의 명시적 예산이다. TCaR는 중앙값 위 간격으로, 기대 투자비·총 조달자금·연간 유동성 예비비와 다르다. 첫 그림은 중앙값·상위 분위수·ES·실물 감축률을 함께 보여준다.

구현: src/cap/risk_metrics.py

### F06 정확한 경험적 ES

$$m=N(1-\alpha);\quad k=\lfloor m\rfloor;\quad f=m-k$$

$$\widehat{\mathrm{ES}}_\alpha=\frac{\sum_{i=N-k+1}^{N}L_{(i)}+fL_{(N-k)}}{m}$$

$$\mathrm{ES}_\alpha=\min_\eta\left\{\eta+\frac{\mathrm{E}[(L-\eta)^+]}{1-\alpha}\right\}$$

k=0이면 합은 0이고 f=0이면 경계 항을 생략한다. η는 비용 단위의 문턱값, (z)⁺=max(z,0)이다. ES는 최악의 1−α 확률질량을 분할 경계 가중치까지 포함해 적분한다. 보간 분위수를 엄격히 넘는 관측값의 평균과 일반적으로 같지 않다. N=5000, α=.95에서는 최상위 250개 평균이다.

구현: src/cap/risk_metrics.py; scripts/research_block_price_paths.py:expected_shortfall

\pagebreak

### F07 선택 규칙과 지배

$$x^*\in\underset{x\in X_{\mathrm{eligible}}}{\operatorname{argmin}}\,[\mu(x)+\lambda\mathrm{ES}_\alpha(x)],\quad\lambda\geq0$$

$$y\succ x\ \Longleftrightarrow\ \mu(y)\leq\mu(x),\ \mathrm{ES}(y)\leq\mathrm{ES}(x),\ \mathrm{at\ least\ one\ strict}$$

Xeligible은 물리적으로 적격인 유한 후보집합, λ는 무차원의 가정된 선호 가중치다. 동률을 모두 기록하고 빈 집합은 실행 불가능으로 처리한다. 평균–ES 지배와 모든 공통 표본경로에서 비용이 작거나 같은 경로별 지배는 다르다. TCaR 단독은 비용의 단조적 순위를 주지 않는다. 별도로 ES≤B_ES 아래 평균 최소화를 쓸 수 있다. 유한 후보의 선택은 전체 정수해집합의 최적성 증명이 아니다.

구현: src/cap/risk_metrics.py; scripts/review_technology_investment_cycle2.py

### F08 확정 비용 이동과 반례

$$\mu(L+a)=\mu(L)+a;\quad\mathrm{ES}_\alpha(L+a)=\mathrm{ES}_\alpha(L)+a$$

$$\mathrm{TCaR}_\alpha(L+a)=\mathrm{TCaR}_\alpha(L)$$

$$\Pr(X=0)=0.8;\quad\Pr(X=100)=0.2;\quad Y=100$$

a는 비용 단위의 확정값이다. 반례에서 X의 평균은 20, ES90은 100, TCaR90은 100이다. Y의 평균·ES90은 100, TCaR90은 0이다. 따라서 평균+2TCaR는 모든 상태에서 X보다 비용이 낮지 않은 Y를 선택한다. 공통 미래 확률 현금은 경로별 차이에서는 없어지지만 개별 ES·TCaR 수준에서는 일반적으로 없어지지 않는다.

구현: src/cap/risk_metrics.py; scripts/review_technology_investment_cycle2.py

\pagebreak

### F09 가격 관측값과 추정

$$r_{mj}=\ln(P_{mj}/P_{m-1,j});\quad\widetilde r_{mj}=r_{mj}-\operatorname{mean}_m(r_{mj})$$

$$\sigma_{\mathrm{annual}}=\operatorname{sd}(r,\mathrm{ddof}=1)\sqrt\nu;\quad\nu=365.25/\operatorname{median}(\mathrm{day\ gaps})$$

m은 월, j는 벤치마크다. 세계은행 2010.1–2025.12 자료는 가격 192행, 6요인의 정렬 로그수익률 191행이다. 기업 D4는 이와 별개로 6개 이상 관측값을 가진 지정 계열별 연율화 표준편차를 요인 내 평균하고, 자료가 없으면 가정값을 쓴다. 혼합빈도 ν는 날짜 간격으로 계산하며 무조건 √12를 곱하지 않는다. 요인 상관을 추정할 수 없으면 단위행렬을 쓴다.

구현: src/cap/calibration.py; scripts/extract_worldbank_price_history.py

### F10 기업 로그가격 요인

$$z_{nt}=\operatorname{chol}(R)\epsilon_{nt};\quad\epsilon_{nt}\sim N(0,I)$$

$$u_{nt}=\varphi u_{n,t-1}+\sigma z_{nt};\quad v_t=\varphi^2v_{t-1}+\sigma^2$$

$$M_{nt}=\exp(u_{nt}-v_t/2);\quad u_{n0}=v_0=0$$

u는 중심화한 잠재 로그가격 상태, v는 그 해석적 분산, z는 상관된 표준정규 혁신, ε는 독립 표준정규 벡터다. R은 요인 상관행렬이다. GBM은 φ=1, OU 민감도는 반감기 H=10년으로 φ=exp(−ln2/H)다. 첫 연도 배수는 1로 고정하고 혁신은 2028년부터 적용한다. E[M]=1이며 전력·외부수소·건설의 σ를 구분한다. 두 전력 구매 경로는 같은 전력 충격을 쓴다. 전해조 잔차는 독립 GBM 요인이다. 초기 예측오차는 별도 강건성 실험이다.

구현: src/cap/e3_prices.py; src/cap/price_process.py

\pagebreak

### F11 기술별 건설비 산포

$$a_k=\mathrm{uncertainty\_band}_k/40$$

$$M_k=\exp\left[a_k\ln(M_{\mathrm{cap}})+\tfrac12a_k(1-a_k)v\right]$$

D3의 % 밴드는 상대 산포 배율이며 신뢰구간이 아니다. 이 식은 양수와 기대 배수 1을 유지한다. EPC를 적용하면 해당 건설비 충격을 확정 10% 프리미엄으로 대체한다. 이후 갱신투자는 EPC·건설보조금 적용 밖이며 별도 충격을 유지한다. 공정 참조 실험은 자본비를 고정하므로 저장된 불확실성 자리표시자는 비활성이다.

구현: src/cap/price_process.py:scale_lognormal_multiplier; src/cap/plancost.py

### F12 공동 중첩 블록

$$S=H-b+1;\quad U_k\sim\operatorname{Uniform}\{0,\ldots,S-1\}$$

$$A_{\ell j}=\log\left[S^{-1}\sum_{i=0}^{S-1}\exp\left(\sum_{v=0}^{\ell}\widetilde r_{i+v,j}\right)\right]$$

$$M_{nmj}=\exp\left[\sum_{v=0}^{m}\widetilde r_{nvj}-\lfloor m/b\rfloor A_{b-1,j}-A_{m\bmod b,j}\right]$$

H=191개 과거 수익률, 기본 b=12개월이며 CCS는 b=1도 시험한다. m,l,v는 0부터 센다. 독립 블록 U마다 6요인에 같은 과거 시작점을 쓰고 끝에서 처음으로 감지 않는다. A_l은 부분 블록의 지수 모멘트 로그다. 마지막 부분 블록도 완전 블록의 시작점 집합을 사용한다. 확정 보정항은 이 재표본화 법칙 아래 기대 배수를 정확히 1로 만들며 표본평균으로 나누지 않는다. 미래 생성법의 가정이지 장기 예측오차의 실증 법칙은 아니다.

구현: scripts/research_block_price_paths.py:block_paths

\pagebreak

### F13 시나리오 보간과 연간 구매

$$\overline P_t=P_{y_0}+(P_{y_1}-P_{y_0})(t-y_0)/(y_1-y_0)$$

$$R_{sjt}=\overline P_{sjt}/P_{sj,2024};\quad\overline M_{njt}=\frac1{12}\sum_{m\in\mathrm{year}\ t}M_{nmj}$$

y₀,y₁는 해당 연도를 감싸는 원천 연도다. IEA 노드는 2024·2035·2050이고 비율은 무차원이며 시나리오·지역을 유지한다. 월별 구매량이 일정하므로 연간 가격은 산술평균이다. 연말값·기하평균은 다른 청구액을 만든다. 과거 벤치마크는 공장 인도 단가가 아니며 품질·운임·환율·계약 차이는 별도 자료가 필요하다. 기업 NZ15/B20은 별도 예시 대용치다.

구현: src/cap/scenario_prices.py; scripts/research_block_price_paths.py

### F14 기업 물량과 원단위

$$\overline q_i=\operatorname{mean}_{2022:2024}(q_{iy});\quad e_i=\overline E_i/\overline q_i$$

$$a_{\mathrm{elec},i}=\overline{\mathrm{MWh}}_i/\overline q_i;\quad a_{\mathrm{coal},i}=\overline{\mathrm{GJ}}_{\mathrm{coal},i}/(28\overline q_i)$$

$$a_{\mathrm{gas},i}=\overline{\mathrm{GJ}}_{\mathrm{gas},i}/(54\overline q_i)$$

i는 모형 설비다. 이 판본의 최근 3개 연도인 2022–2024년 패널을 평균하고 이후 생산량을 고정한다. 전환 뒤 기존 에너지 구매는 기존 원단위×생산량×기술별 잔존 구매비율이며 전환용 전력·수소는 별도 물량이다. 잔존비율을 직접배출계수에서 추론하지 않는다. 배출계수×생산량이 연간 Scope 1이다. 22개 자산은 모형 배분값이며 기업 전체 범위 검증값이 아니다.

구현: src/cap/e2_milp.py:_prep_company; src/cap/plancost.py:build_profile

\pagebreak

### F15 기업 배출예산과 후보 생성

$$B_{ct}=\overline E_c\,\mathrm{sector\_budget}_{srt}/\mathrm{sector\_budget}_{sr,2025}$$

$$\sum_t E_{ct}(x)\leq\sum_t B_{ct};\quad\mathrm{annual\ diagnostic}:\ E_{ct}(x)\leq B_{ct}\ \forall t$$

c는 기업, r은 지역, s는 시나리오다. Ebar는 모형 포트폴리오의 최근 패널 Scope 1 합계 평균이다. 부문 예산 비율을 곱한 값은 기업의 법적 할당량이 아니다. 기술·설비 적합성, 가용연도, 건설기간, 고정생산 및 설비당 최대 1회 전환을 적용한다. 기존 22일정에 최소배출·배출상한 비용탐색의 23일정을 더해 45개가 됐고, 전력비중 5개·EPC 2개와 결합해 450개다. 누적 제약과 연간 실패를 구분한다.

구현: src/cap/e1_constraints.py; scripts/expand_research_candidates.py

### F16 전력·건설 계약 청구

$$P^h_{nt}=(1-h)\overline P_tM_{nt}+h\overline P_t(1+\pi)$$

$$K_{\mathrm{contract},t}=K_{\mathrm{construction},t}(1-\mathrm{subsidy}_t)(1+\pi_{\mathrm{EPC}})$$

h∈{0,.25,.5,.75,1}, 기업 전력 프리미엄은 .08, EPC는 .10이다. 전력 계약은 두 전력 경로에 적용되며 외부구매 수소에는 적용되지 않는다. 고정 단가는 연도별 중심가격에 프리미엄을 더한 일정이지 24년 내내 같은 숫자가 아니다. 기업 검토 메뉴는 지원 없음으로 보조금 0·CCfD 비활성이다. 베이시스·부도·물량 위험은 없다.

구현: src/cap/plancost.py:simulate_cost

\pagebreak

### F17 탄소 지급 및 원천 단위 변환

$$Z_t=P_{\mathrm{CO}_2,t}(E_t-A_t);\quad Z_{\mathrm{purchase},t}=P_{\mathrm{CO}_2,t}\max(E_t-A_t,0)$$

A는 톤 단위 무상할당량이며 유상할당 비율이 아니다. 동결 기업의 총 의무량 대용 모드는 A=0과 확정 탄소가격을 사용한다. 회피 탄소비용이 증분 평균을 좌우할 수 있다. 순거래·구매전용 모드는 실제 할당 자료가 필요하며 현재 기업 결과와 다르다. 공정 현금 실험은 CCS 가상 부과금 민감도 전까지 탄소가격 0이다. 물리적 배출 자격에는 무상할당과 무관하게 모든 해당 배출을 넣는다.

구현: src/cap/carbon_accounting.py; src/cap/plancost.py

### F18 투자 지급과 갱신

$$K_{\mathrm{build},t}=I/b\ \mathrm{for}\ t=a,\ldots,a+b-1;\quad \tau=a+b$$

$$K_{\mathrm{renew},t}=I\,\mathbf1_{\{t=\tau+\ell,\,\tau+2\ell,\ldots\}}$$

$$V_{\mathrm{proxy}}=I\max[1-(T-\mathrm{last\_origin}+1)/\ell,0]$$

I는 설비 투자액, a는 건설 시작, b는 건설 연수, ℓ은 구성요소 수명이다. 참조 실험은 갱신 기한 연도 시작에 지급하고 가동중단을 0으로 둔다. 기업 구현의 b=0은 도입 시점 일시 지급이다. 기존 설비 갱신은 퇴역 전까지만 유지하며 기한 당일 교체하면 기존 갱신을 피한다. Vproxy는 회계 민감도 대용치로 실제 처분 현금이 아니다. 본 계산은 V=0이다.

구현: src/cap/capital_ledger.py; src/cap/component_capital.py

\pagebreak

### F19 NCC 생산·증기 수지

$$Y=115\times8000=920{,}000\ \mathrm{t\ ethylene/year};\quad F=Y/0.303$$

$$H_{\mathrm{conv}}=u\max(0.841-0.431,0);\quad H_{\mathrm{elec}}=u\times0.542$$

$$H_{\mathrm{boiler}}=\max(0.492-H_{\mathrm{recovered}},0);\quad G_{\mathrm{boiler}}=H_{\mathrm{boiler}}/0.92$$

F는 연간 나프타 투입이다. 이 식의 비에너지는 MWh/t 나프타다. u는 유효 증기 이용률로 시점 실험은 1, 별도 신규공장 민감도는 .8/1이다. 서로 다른 증기 등급을 합친 명시적 근사다. 기존 분해로 메탄은 1.868, 전기화는 0이고 전력은 기존 .083, 전기화 1.476+.383+.083=1.942다. 보일러 열수요 0이 전체 공정 검증을 뜻하지 않는다.

구현: src/cap/reference_ncc.py

### F20 NCC 메탄·투자비

$$G_{\mathrm{buy}}=\max(G_{\mathrm{cracker}}+G_{\mathrm{boiler}}-2.349,0)$$

$$G_{\mathrm{sell}}=v\max(2.349-G_{\mathrm{cracker}}-G_{\mathrm{boiler}},0)$$

$$I_{\mathrm{plant}}=5126\times115\times1000+405\times10^6$$

$$I_{\mathrm{boiler}}=72.1\times H_{\mathrm{boiler}}\times115/0.303\times1000$$

v=1은 잉여 메탄 판매 가정이다. 미판매 잉여는 별도 이전이며 무배출 소각으로 간주하지 않는다. 순메탄 물량은 F(Gbuy−Gsell)이다. 플랜트는 994.49백만 EUR2019이며 보일러는 별도다. 투자 곡선의 생산능력 분모를 유지한다. 메탄 판매가는 가정된 순수취 단가다. 두 대안의 나프타 물량·단가가 같아 증분에서 정확히 상쇄된다.

구현: src/cap/reference_ncc.py

\pagebreak

### F21 NCC 유지비·가격

$$\operatorname{CRF}(r,\ell)=\frac{r}{1-(1+r)^{-\ell}};\quad\operatorname{CRF}(0,\ell)=1/\ell$$

$$\mathrm{OM}=\psi I_{\mathrm{plant}}\operatorname{CRF}(.05,\ell_{\mathrm{plant}})+.04I_{\mathrm{boiler}}\operatorname{CRF}(.05,25)$$

$$P_e=100(.5+.5R_{\mathrm{gas}}\overline M_{\mathrm{gas}});\quad P_g=40R_{\mathrm{gas}}\overline M_{\mathrm{gas}}$$

$$P_{\mathrm{naphtha}}=600R_{\mathrm{oil}}\overline M_{\mathrm{oil}};\quad P_e=50+1.25P_g$$

시점 실험에서 ψ는 기존 .04, 전기화 .02, 수명은 30·20년이다. 유지비는 원문의 연금화 자본 기준 대용치이며 단순 ψ×설치비가 아니다. 연금화 투자비 자체를 현금투자에 중복 가산하지 않는다. 원문 % 표기 모호성은 신규공장 실험에서 .0004/.0002 해석도 별도 시험했다. 운영 단가는 EUR2019 가정으로 전력·메탄은 MWh당, 나프타는 톤당이다. 전력–가스 아핀관계는 모형에 부여한 조건이다.

구현: src/cap/reference_ncc.py; scripts/run_ncc_timing_frontier.py

### F22 NCC 배출 적격성

$$g_t=g_{2027}(2050-t)/23$$

$$E_t=F[e_t+a_{\mathrm{elec},t}g_t+\rho]$$

$$\sum_t E_t\leq\kappa\sum_t E^0_t;\quad E_T\leq0;\quad\mathrm{diagnostic}: E_t\leq E^0_{2027}(2050-t)/23$$

초기 g는 .2/.4 tCO2/MWh, 잔여 ρ는 0/.05 tCO2/t 나프타다. 직접 e는 전기화 전 .397, 이후 0 가정이다. 본 κ는 .75이며 1차 검토에서 .45부터 .85까지 .05 간격으로 시험했다. 감축률은 1−ΣE/ΣE0이다. E0에도 같은 전력·잔여 조건을 쓴다. 연간·누적·말기 검사를 구분하고 배출량은 할인하지 않는다. 잔여 .05이면 말기 0을 위반한다. 수치 허용오차는 1e−7톤이다.

구현: src/cap/reference_timing.py:emission_qualification

\pagebreak

### F23 종료 이후 갱신과 시점 지배 증명

$$\operatorname{Tail}(\tau)=\frac{I(1+r)^{-(\operatorname{next}(\tau)-2027)}}{1-(1+r)^{-20}}$$

$$\Delta C_{\mathrm{early,late}}\geq\sum_t d_t[\Delta\mathrm{fixed}_t+50\Delta\mathrm{MWh}_t]+\Delta\operatorname{Tail}$$

I=994.49백만 EUR이며 next(τ)는 2050년 이후 첫 갱신이다(가동 2030/35/40/45 → 2070/2055/2060/2065). 두 번째 식은 매년 Pg≥0 및 1.25Δ전력물량+Δ순메탄물량≥0을 요구한다. 동일 기술의 미래 운영 현금은 경로별 차이에서 상쇄된다. 양의 하한은 이 조건 아래 비용 순위를 증명하지만 무한기간 개별 ES·TCaR 수준을 계산하지 않는다. 정태적 확정 갱신 가정이며 추정 종료가치가 아니다.

구현: scripts/review_technology_investment_cycle2.py

### F24 CCS 원문 현금 원장

$$\mathrm{Fixed}_i=\mathrm{GrossOM}_i-\mathrm{GasBill}_i-\mathrm{OreBill}_i-\mathrm{CoalBill}_i-\mathrm{Credits}_i$$

$$\mathrm{Gas}_i=\mathrm{Gas}_0+(\mathrm{EnergyBill}_i-\mathrm{EnergyBill}_0)/9.77$$

$$C_i=\sum_t d_t[K_{it}+\mathrm{Fixed}_{it}+\mathrm{CoalBill}_t+\mathrm{OreBill}_t\overline M_{\mathrm{ore}}+\mathrm{GasBill}_{it}]$$

i는 기준·L1·L2다. 청구액은 원문 USD/년, 가스는 GJ/년이다. 총 운영비에서 부산물 수입과 별도 청구 에너지·원료를 차감해 순고정 현금을 만든다. 동결 L1·L2 가스는 비용 역산값이며 후속 물리 원문의 반올림 물량과 대조만 하고 저장 비용을 다시 바꾸지 않았다. 최초 투자는 2027–29년 3등분, 공통 232백만 USD 개수는 2044년이다. 2030–50년 연 400만 톤 HRC를 생산한다.

구현: scripts/run_ieaghg_paired_reference.py; data/research_v2/ieaghg_reference/package.json

\pagebreak

### F25 CCS 증분 가스 조달

$$\overline P_{\mathrm{gas},t}=9.77R_{\mathrm{IEA\ Europe\ gas},t}$$

$$\mathrm{GasBill}_i^h=\mathrm{Gas}_0\overline P_{\mathrm{gas}}\overline M_{\mathrm{gas}}+\Delta\mathrm{Gas}_i\overline P_{\mathrm{gas}}[(1-h)\overline M_{\mathrm{gas}}+h(1+.03)]$$

ΔGas_i는 기준 대비 추가 가스다. 공통 기준 가스는 시장 노출을 유지하고 포집 추가 가스만 고정할 수 있다. h는 0,.25,.5,.75,1이다. 원료·석탄 공통 비용은 증분에서 상쇄된다. 현재 2요인·확정 자본 모형의 h=1에서는 증분 TCaR가 대수적으로 0이지만 절대 사업비에는 공통 가스·철광석 위험이 남는다. 물량·베이시스·부도 위험은 모형 밖이다.

구현: scripts/run_ieaghg_paired_reference.py

### F26 회피량과 포집량

$$A_i=E_0-E_i;\quad\mathrm{reduction}_i=A_i/E_0$$

$$\mathrm{net\_reduction}_i=(A_i-uQ_i)/E_0$$

$$u_{\max}=(A_i-\mathrm{target}\times E_0)/Q_i$$

감사한 C7 범위의 E0는 연 8,376,554 tCO2다. Ei는 배출, Qi는 포집량이다. 포집 에너지 등이 남으므로 Q와 회피량 A는 다르다. u는 기준안 대비 추가 하류 배출/포집톤이며 추정 누출률이 아니다. 목표 .50/.60/.604로 기술을 거르고 하류 스트레스는 0,u_max,.005,.01이다. C7과 기존 D15 감축률을 구분한다. C7 열의 식별은 대조에 의한 추론이지 공식 정오표가 아니다.

구현: scripts/audit_ieaghg_physical_reference.py; scripts/review_technology_investment_cycle2.py

\pagebreak

### F27 가상 탄소·수송저장 현금

$$W=\sum_{t=2030}^{2050}(1.05)^{-(t-2027)}$$

$$L_i(c,k)=L_i(0,0)+W(kQ_i-cA_i)$$

c는 보고 배출범위의 배출톤당 원문 USD 확정 실질 부과금이며 증분에서는 회피톤에 따른 절감이다. k는 회피톤이 아닌 포집톤당 요금이다. 백만 USD 결과에는 추가 항을 1e6으로 나눈다. 실제 ETS 순지급액이나 검증된 수송·저장 요금이 아니다. 평균과 ES는 모두 같은 금액만큼 이동하고 TCaR는 유지된다.

구현: scripts/review_technology_investment_cycle2.py

### F28 실물 기술 전환 문턱

$$c_\mu^*=[\Delta\mu/W+k\Delta Q]/\Delta A$$

$$c_{\mathrm{ES}}^*=[\Delta\mathrm{ES}/W+k\Delta Q]/\Delta A$$

$$c_{\mu+\lambda\mathrm{ES}}^*=\left[\frac{\Delta\mu+\lambda\Delta\mathrm{ES}}{(1+\lambda)W}+k\Delta Q\right]/\Delta A$$

Δ는 같은 h·시나리오·표본에서 L2−L1이다. 여기 비용은 백만 USD가 아닌 USD이고 ΔA>0이다. c*에서 동률, 더 높은 c에서 L2가 유리하다. 가중 식은 평균과 ES가 모두 이동하므로 (1+λ)가 필요하다. h도 선택하면 모든 적격 계획을 비교해야 하며 같은 h의 문턱 하나로 계약 전체의 최저비용 경계를 대신할 수 없다. λ는 0,.01,.1,1의 민감도 가정이다.

구현: scripts/review_technology_investment_cycle2.py; algebraic extension of F27

\pagebreak

### F29 Vogl 공장 물량·고정 현금

$$Y_t=\mathrm{capacity}\times\mathrm{utilisation}\times\mathbf1_{\{t\geq2030\}}=750{,}000\,\mathbf1_{\{t\geq2030\}}$$

$$q_{\mathrm{power}}=3.48Y;\quad q_{\mathrm{pellet}}=1.504Y;\quad q_{\mathrm{oxygen}}=-.411\times.6Y$$

$$\mathrm{Fixed}_t=K_t+Y_t(.05\times100+.011\times1777+.002\times4000+53.2-.411\times.6\times60.8)$$

$$\mathrm{Fixed}_t\leftarrow\mathrm{Fixed}_t+\mathbf1_{\{t\geq2030\}}\times10^6\times574\times.03$$

설치능력은 액강 연 100만 톤, 이용률 .75다. 전력은 MWh, 나머지는 톤이다. 연산톤당 자본은 전해조160(수명10), 샤프트230(20), EAF184(20) EUR다. 최초 574백만은 2027–29년 분할, 2040년 160백만·2050년 574백만 갱신이다. 유지비는 설치능력, 인건비는 생산량 기준이다. 현장 수소는 이미 전력에 포함되므로 외부수소나 상류 펠릿 생산 에너지를 다시 청구하지 않는다. 산소 판매가의 정제·취급 비용은 미해결이다.

구현: src/cap/reference_steel.py; scripts/run_steel_procurement_tail_audit.py

### F30 펠릿 연동과 동일 평균

$$P_{\mathrm{pellet}}=100[(1-\beta)+\beta\overline M_{\mathrm{ore}}];\quad P_e=40(.5+.5R_{\mathrm{JapanLNG}}\overline M_{\mathrm{gas}})$$

$$C_\beta=C_{\mathrm{fixed}}+C_{\mathrm{power}}+(1-\beta)C_{\mathrm{pellet,central}}+\beta C_{\mathrm{pellet,random}}$$

β=0,.5,1은 추정되지 않은 매핑 가정이며 실제 선택 가능한 금융계약이 아니다. E[M]=1이므로 이론 평균은 모든 β에서 3971.2314147902393백만 원문 EUR로 같다. 표본평균은 달라질 수 있다. 공동경로는 블록 관계를 유지하고 전체 궤적 순열은 각 주변경로를 보존하며 짝만 바꾼다. 시드당 200순열은 의존성 진단이며 미래 예측 신뢰구간이 아니다.

구현: scripts/run_steel_procurement_tail_audit.py

\pagebreak

### F31 꼬리 기여와 불확실성 요약

$$C_n=\sum_j C_{nj};\quad\mathrm{ES\ contribution}_j=\sum_n w_nC_{nj};\quad\sum_n w_n=1$$

$$\mathrm{Excess\ contribution}_j=\mathrm{ES\ contribution}_j-\operatorname{mean}_n(C_{nj})$$

$$\operatorname{MCSE}(\widehat\mu)=\operatorname{sd}(L,\mathrm{ddof}=1)/\sqrt N$$

w는 총비용 순위로 F06의 꼬리 질량을 배분하며 모든 구성요소에 공통이다. 기여 합은 총 ES지만 구성요소별 독립 ES의 합은 일반적으로 다르다. NCC 짝지은 부트스트랩은 후보마다 같은 경로 인덱스를 뽑아 500회 재계산하고 2.5/97.5 분위수를 쓴다. 경계 포함빈도는 횟수/500이며 진짜 효율적일 확률이 아니다. 기업 고정후보 부트스트랩은 400회다. 모두 조건부 표본오차이며 구조·모수 불확실성은 아니다.

구현: src/cap/tail_attribution.py; scripts/run_ncc_timing_frontier.py

### F32 청구 통화와 결제

$$\mathrm{FX}_{a\to b,nt}=\mathrm{quote}_{b,nt}/\mathrm{quote}_{a,nt}$$

$$\mathrm{Cash}_{n,\mathrm{paid}}=\frac{\mathrm{sign}\times q\times P^{\mathrm{real}}_{n,\mathrm{priced}}\times I_{a,n,\mathrm{priced}}\times\mathrm{FX}_{a\to b,n,\mathrm{paid}}}{I_{b,n,\mathrm{paid}}}$$

$$\mathrm{NPV}_n=\sum_{\mathrm{paid}}d_{n,\mathrm{paid}}\mathrm{Cash}_{n,\mathrm{paid}}$$

호가는 공통 기준통화 1단위당 명목 통화량이며 기준통화 호가는 1이다. a는 청구통화, b는 평가통화다. q≥0, 구매 부호 +1·판매 −1이다. Ia는 가격결정 시 실질 청구가격을 명목으로 바꾸고 Ib는 결제 시 평가통화 현금을 실질화한다. 명목인 해당 단계는 지수 1이다. 기준연도와 할인 규약을 맞추고 2050년 이후 지급도 남긴다. 표본·경로순서·통화·물량단위·달력이 일치해야 한다.

구현: src/cap/fx_settlement.py:settle_invoices

\pagebreak

### F33 청구 통합과 공분산

$$C_{\mathrm{combined}}=C_{\mathrm{FIN\ without\ additional\ flows}}+\mathrm{NPV}_{\mathrm{invoice}}/10^9$$

$$\mathrm{E}[PX]=\mathrm{E}[P]\mathrm{E}[X]+\operatorname{Cov}(P,X)$$

$$\operatorname{mean}_m(P_mX_m)=\operatorname{mean}_m(P_m)\operatorname{mean}_m(X_m)+\operatorname{Cov}_m(P_m,X_m)$$

첫 식 결과는 십억 KRW이며 청구 NPV는 KRW다. 기존 추가 원료 원장을 완전히 제거한 뒤 청구를 한 번씩 더한다. 이미 환산된 청구액에 환율 할증을 다시 더하지 않는다. 마지막 월별 공분산은 M−1이 아닌 M으로 나눈다. 연간 가격평균과 환율평균을 따로 곱하면 일반적으로 같은 현금이 아니다. 청구 통합은 선택적 확장이며 동결 기업 결과에 추정 기업 환노출이 포함됐다는 뜻은 아니다.

구현: src/cap/invoice_fin.py

### F34 공통 평가와 후회비용

$$\operatorname{Regret}(\widehat x\mid s,\theta)=J_{\mathrm{reference}}(\widehat x\mid s,\theta)-\min_{x\in X_{\mathrm{eligible}}}J_{\mathrm{reference}}(x\mid s,\theta)$$

Jreference는 사전에 정한 공통 평가함수(예: 평균+λES), xhat은 비교할 정보·모형 사양으로 선택한 계획이다. 부적격은 별도로 보고하며 후회비용 0으로 처리하지 않는다. 플랜잇 연계의 가격·물량·공급상한·배출계수는 시나리오·지역·연도·범위를 공유해야 하며 산업수요가 바뀌면 시스템을 다시 풀어야 한다. 이 식은 제안된 검증 설계이며 완료된 정보가치 추정이 아니다.

구현: paper/pilot_review/PAPER_EN.md:sections 13–16

\pagebreak

### F35 유한 후보 생성 대용 목적함수

$$x_{ika}\in\{0,1\};\quad\sum_{ka}x_{ika}\leq1;\quad\tau_k=a+\mathrm{build\_years}_k$$

$$R_{\mathrm{proxy}}=\sum_t d_t[\sigma_e\mathrm{ElectricityBill}_t+\sigma_h\mathrm{H2Bill}_t+\sigma_K\mathrm{CapitalCash}_t+.30\mathrm{CarbonBill}_t]$$

$$\min C_{\mathrm{central}}\ \mathrm{subject\ to}\ R_{\mathrm{proxy}}\leq\varepsilon;\quad\mathrm{or}\ \min R_{\mathrm{proxy}};\quad\mathrm{or}\ \min\sum_t E_t$$

x_ika는 설비 i에 기술 k를 착공 a년에 적용하는 이진변수다. 시작은 max(2027,기술·시나리오 가용연도) 이상, 가동은2050년 이내이며 부적합 설비에는 변수가 없다. 퇴역비중0·후보생성 계약0이다. Rproxy는 탐색용 선형 대용치로 MC TCaR·ES가 아니다. .30 탄소 노출계수는 후보탐색 가정이며 기업 MC의 탄소 현금은 확정이다. 식의 청구액은 같은 화폐 규모를 쓴다. 원래 위험상한6지점과 배출 확장지점으로 일정을 만든 뒤 재평가한다. 확장은 최소 누적배출과 누적예산 사이4개 등간격 상한에 상대1e−9 허용량(예산 이내)을 더하고 설비·기술·착공 조합 중복을 제거한다. cumulative_hard에서는 연간 슬랙 벌금이0이고 연간 실패만 기록한다.

구현: src/cap/e2_milp.py; scripts/expand_research_candidates.py

### F36 과거 자료 기술통계

$$m_k=H^{-1}\sum_m(r_m-\overline r)^k;\quad\mathrm{skew}=m_3/m_2^{3/2};\quad\mathrm{excess\ kurtosis}=m_4/m_2^2-3$$

$$\operatorname{Corr}(X,Y)=\frac{\sum(X-\overline X)(Y-\overline Y)}{\sqrt{\sum(X-\overline X)^2\sum(Y-\overline Y)^2}}$$

H는 보존한 수익률 수, rbar는 산술평균, m_k는 중심모멘트다. 1시차 자기상관은 연속 수익률의 상관이며 제곱수익률 자기상관은 제곱값에 같은 연산을 적용한다. 이 통계와 과거 분위수는 입력 표본의 설명으로 미래 위험분포 추정·독립검증이 아니다. 저장된6요인 상관행렬·기술통계는 보조자료이고 공동 블록은 다변량 과거행을 직접 뽑는다.

구현: scripts/extract_worldbank_price_history.py

\pagebreak

### 4. 전체 필드 사전

등록한 모든 CSV·Parquet의 서로 다른 필드명을 빠짐없이 아래에 포함했다. 파일별 등장 위치·자료형·관측범위·결측 수·예시·뜻은 field_dictionary.csv에 있다. 여러 실험에서 이름을 재사용할 때 잘못된 단위를 붙이지 않도록 했다. 달력·범주 메타데이터에는 물리단위가 없으며 원문 단위 필드가 일반적 표기보다 우선한다.

| 정확한 필드 / 데이터 그룹 | 뜻과 단위 규약 |
| --- | --- |
| C7_avoided_fraction<br>CCS | 명시된 배출 비율; C7·D15 범위 구분; 포집은 회피와 다름<br>단위: ratio |
| C7_eligible<br>CCS | 검사 표지: C7 eligible; 확률값이 아님<br>단위: boolean |
| C7_emitted_t_CO2_y<br>CCS | 감사한 C7 범위 배출·회피·포집·포집−회피량(F26)<br>단위: tCO2/year |
| D15_avoided_fraction<br>CCS | 명시된 배출 비율; C7·D15 범위 구분; 포집은 회피와 다름<br>단위: ratio |
| D15_eligible<br>CCS | 검사 표지: D15 eligible; 확률값이 아님<br>단위: boolean |
| ES_contribution<br>STEEL | 총비용 꼬리 가중치 기여; excess는 구성요소 평균 차감(F31)<br>단위: million source EUR |
| KRW_per_USD<br>FX | 합성 결제 예시의 명목 원/달러<br>단위: KRW/USD |
| USD_per_t<br>FX | 합성 결제 예시의 명목 청구 단가<br>단위: USD/t |
| abated_tco2_disc<br>CORP | 기존 톤당 비용 진단의 할인 감축량; 적격성은 비할인 배출 사용<br>단위: discounted tCO2 |
| absolute_es95<br>CCS | 기준안 차감 전 전체 사업비 평균/ES<br>단위: million source USD |
| absolute_mean<br>CCS | 기준안 차감 전 전체 사업비 평균/ES<br>단위: million source USD |
| accessed_at_utc<br>CORP | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| acf1<br>PRICE | 수익률 또는 제곱수익률의 1시차 표본상관<br>단위: coefficient |
| adopt_year<br>CORP | 해당 사건의 달력연도; adopt=착공, op=가동; 9999는 미가용<br>단위: year |
| aggregate_annual_exposure_arrays_equal<br>CORP | 검사 표지: aggregate annual exposure arrays equal; 확률값이 아님<br>단위: boolean |
| alpha<br>CORP,FIGURE,FX,NCC,STEEL | 꼬리 확률수준; 기업 .90, 공정 .95<br>단위: fraction |
| amount_unit<br>CORP | 단위·통화·가격연도 선언; 공란은 미해결이며 0이 아님<br>단위: metadata |
| analytic_mean<br>CCS,CORP,FIGURE,NCC,REVIEW | 지정 생성법 아래 기대값; analytic/theoretical은 표본평균과 구별<br>단위: dataset currency |
| analytic_mean_in_interval<br>CORP | 검사 표지: analytic mean in interval; 확률값이 아님<br>단위: boolean |
| annual_budget_compliant<br>CORP | 검사 표지: annual budget compliant; 확률값이 아님<br>단위: boolean |
| annual_excess_tco2<br>CORP | 배출예산 여유 또는 연간 초과; 필드별 부호 유지<br>단위: tCO2 |
| annual_feasible<br>FIGURE,NCC | 검사 표지: annual feasible; 확률값이 아님<br>단위: boolean |
| annual_linear_cap<br>NCC | 기업 비례배분 또는 NCC 진단 연간 배출상한<br>단위: tCO2/year |
| annual_linear_cap_enforced<br>REVIEW | 검사 표지: annual linear cap enforced; 확률값이 아님<br>단위: boolean |
| annual_log_vol<br>CORP | 명시된 빈도의 로그수익률 표준편차<br>단위: log-return SD |
| annual_net_emissions_margin<br>REVIEW | 회피량−목표비율×기준 배출량<br>단위: tCO2/year |
| applies_to_unit<br>CORP | 설비·사업장·부문·지역·적합성 이름<br>단위: category |
| avail_year<br>CORP | 해당 사건의 달력연도; adopt=착공, op=가동; 9999는 미가용<br>단위: year |
| avail_year_scenario<br>CORP | 해당 사건의 달력연도; adopt=착공, op=가동; 9999는 미가용<br>단위: year |
| avoided_t_CO2_y<br>CCS | 감사한 C7 범위 배출·회피·포집·포집−회피량(F26)<br>단위: tCO2/year |
| base_eligible<br>CORP | 검사 표지: base eligible; 확률값이 아님<br>단위: boolean |
| base_menu_size<br>CORP | 명시된 후보·동률·지배 후보 개수<br>단위: count |
| base_plan<br>CORP | 선택·기준·동등 계획 ID; 세미콜론은 복수 ID 구분<br>단위: identifier |
| base_plan_id<br>CORP | 기업·설비·기술·계획·기준·구성요소 식별자; 정확한 키로 결합<br>단위: identifier |
| base_value<br>CORP | 명시 항목의 수치·범주 값; 단위는 해당 행·파일에서 상속<br>단위: row unit |
| baseline_cumulative<br>FIGURE,NCC | 후보 또는 기준안의 비할인 누적배출<br>단위: tCO2 |
| baseline_emissions<br>NCC | 필드명에 명시한 연간 배출 구성·총량·기준·말기량·상한<br>단위: tCO2/year |
| baseline_gross_capex_k<br>CORP | 필드명에 명시한 기준·계획·증분·갱신 투자 현금<br>단위: thousand KRW |
| baseline_mean<br>NCC | 수명 실험의 신규 기존형·전기화 플랜트 절대 표본평균<br>단위: million EUR |
| baseline_npv_KRW<br>FX | 기준·후기 결제의 청구 현재가치 또는 차이<br>단위: KRW |
| baseline_payment<br>FX | 합성 예시의 해당 행 날짜가 가격결정·기준결제·후기결제일인지 표시<br>단위: boolean |
| baseline_scope1_tco2<br>CORP | 기업 범위 연간 직접 Scope 1 배출<br>단위: tCO2/year |
| baseline_selected_plan_id<br>CORP | 선택·기준·동등 계획 ID; 세미콜론은 복수 ID 구분<br>단위: identifier |
| beta<br>FIGURE,STEEL | 펠릿–철광석 벤치마크 연동 가정 0,.5,1(F30)<br>단위: fraction |
| block<br>NCC | 과거 블록 길이<br>단위: months |
| bootstrap_high_95<br>CORP | 경험적 부트스트랩 2.5/97.5 분위수 경계(F31)<br>단위: dataset currency |
| bootstrap_low_95<br>CORP | 경험적 부트스트랩 2.5/97.5 분위수 경계(F31)<br>단위: dataset currency |
| bootstrap_replicates<br>NCC | 필드명에 명시한 관측·경로·반복·포함 횟수<br>단위: count |
| boundary<br>PRICE | 수치 필드와 함께 읽는 설명·근거·범위 원문<br>단위: text |
| boundary_limit<br>PRICE | 수치 필드와 함께 읽는 설명·근거·범위 원문<br>단위: text |
| boundary_status<br>CORP | 근거·추출·매핑·회계 상태; 모형 확률 아님<br>단위: category |
| brent<br>PRICE | 정렬된 월별 벤치마크 로그수익률; 원가격 단위는 계열 등록부 참조<br>단위: log return |
| budget_mode<br>CORP | 결과를 정의하는 회계·적격성·통계 규약<br>단위: category |
| budget_ok<br>CORP | 검사 표지: budget ok; 확률값이 아님<br>단위: boolean |
| budget_slack_tco2<br>CORP | 배출예산 여유 또는 연간 초과; 필드별 부호 유지<br>단위: tCO2 |
| build_years<br>CORP | 건설기간·기술수명·기존 설비 갱신주기<br>단위: years |
| candidate<br>FIGURE,FX,NCC,REVIEW | 기업·설비·기술·계획·기준·구성요소 식별자; 정확한 키로 결합<br>단위: identifier |
| capacity<br>CORP | 설치 연간 생산능력; 투자비 분모이며 실제 생산과 구별<br>단위: capacity_unit |
| capacity_unit<br>CORP | 단위·통화·가격연도 선언; 공란은 미해결이며 0이 아님<br>단위: metadata |
| capex_EUR<br>NCC | 날짜별 자본·유지비·종료 대용치 현금<br>단위: EUR/year |
| capex_peak<br>CORP | 연간 최고 또는 누적 총 투자 현금; 할인 총사업비와 구별<br>단위: billion KRW |
| capex_peak_bnkrw<br>CORP | 연간 최고 또는 누적 총 투자 현금; 할인 총사업비와 구별<br>단위: billion KRW |
| capex_peak_year<br>CORP | 해당 사건의 달력연도; adopt=착공, op=가동; 9999는 미가용<br>단위: year |
| capex_source_USD<br>CCS | 연간 자본·개수·고정가격 현금 구성<br>단위: source USD/year |
| capex_total<br>CORP | 연간 최고 또는 누적 총 투자 현금; 할인 총사업비와 구별<br>단위: billion KRW |
| capex_total_bnkrw<br>CORP | 연간 최고 또는 누적 총 투자 현금; 할인 총사업비와 구별<br>단위: billion KRW |
| capex_uncertainty<br>CORP | 40 대비 배율로 로그 산포를 조절하는 D3 % 밴드(F11)<br>단위: percent; not CI |
| capex_unit<br>CORP | 신기술·기존 갱신의 연산능력당 비용<br>단위: thousand KRW/(t/year) |
| capital_accounting<br>CORP | 결과를 정의하는 회계·적격성·통계 규약<br>단위: category |
| capital_delta_npv<br>NCC | 전기화−기존형 할인 구성요소 현금<br>단위: million EUR |
| capture_to_avoided_ratio<br>CCS | 명시된 배출 비율; C7·D15 범위 구분; 포집은 회피와 다름<br>단위: ratio |
| captured_less_avoided_t_CO2_y<br>CCS | 감사한 C7 범위 배출·회피·포집·포집−회피량(F26)<br>단위: tCO2/year |
| captured_over_baseline<br>CCS | 명시된 배출 비율; C7·D15 범위 구분; 포집은 회피와 다름<br>단위: ratio |
| captured_t_CO2_y<br>CCS | 감사한 C7 범위 배출·회피·포집·포집−회피량(F26)<br>단위: tCO2/year |
| carbon_accounting<br>CORP | 결과를 정의하는 회계·적격성·통계 규약<br>단위: category |
| carbon_budget<br>CORP | 기업 비례배분 전 부문 배출 상한<br>단위: MtCO2/year |
| carbon_charge<br>REVIEW | 가상 배출톤 부과금·동률 문턱; 증분 절감은 회피톤 적용(F28)<br>단위: source USD/tCO2 |
| carbon_delta<br>CORP | 기업 할인비용·탄소·정책·완전정보 보조 진단; 신규 파일럿 선택 결과 아님<br>단위: billion KRW |
| carbon_delta_bnkrw<br>CORP | 기업 할인비용·탄소·정책·완전정보 보조 진단; 신규 파일럿 선택 결과 아님<br>단위: billion KRW |
| case<br>CCS,NCC,REVIEW | 기업·설비·기술·계획·기준·구성요소 식별자; 정확한 키로 결합<br>단위: identifier |
| case_boundary_status<br>CORP | 근거·추출·매핑·회계 상태; 모형 확률 아님<br>단위: category |
| cash<br>CORP | 기업 재무 관측·과거 대용값; 설비 에너지 비용 아님; 통화·보고범위 유지<br>단위: row currency/unit |
| ccfd<br>CORP | 계약 적용 0/1; 기업 검토에서는 EPC 메뉴, CCfD 비활성<br>단위: 0/1 |
| central_cost_reconciliation_error<br>CORP | 중심가격 FIN 비용−독립 재구성<br>단위: billion KRW |
| central_gas_source_USD_GJ<br>CCS | 9.77×IEA 유럽 가스비율<br>단위: source USD/GJ |
| central_power<br>STEEL | Vogl 실험의 가정 중심 전력 단가<br>단위: source EUR/MWh |
| changed<br>CORP | 검사 표지: changed; 확률값이 아님<br>단위: boolean |
| check<br>CCS | 측정 모수·원문 항목·통계·진단 이름<br>단위: identifier |
| commission_year<br>FIGURE,NCC | 해당 사건의 달력연도; adopt=착공, op=가동; 9999는 미가용<br>단위: year |
| commissioning_year<br>CORP | 해당 사건의 달력연도; adopt=착공, op=가동; 9999는 미가용<br>단위: year |
| commodity<br>FIGURE,PRICE | 원료·상품 식별자; 가격과 물량 분모 일치 필요<br>단위: category |
| common_contract_fraction<br>REVIEW | 고정가 비중; 기업은 전력, CCS는 증분 가스(F16,F25)<br>단위: fraction |
| company_budget_tco2<br>CORP | 기업 비례배분 또는 NCC 진단 연간 배출상한<br>단위: tCO2/year |
| company_delivered_input<br>PRICE | 검사 표지: company delivered input; 확률값이 아님<br>단위: boolean |
| company_id<br>CORP | 기업·설비·기술·계획·기준·구성요소 식별자; 정확한 키로 결합<br>단위: identifier |
| company_scenario_alignment_verified<br>PRICE | 검사 표지: company scenario alignment verified; 확률값이 아님<br>단위: boolean |
| comparison<br>FX | 짝지은 비교·검증 실험 이름<br>단위: identifier |
| comparison_basis<br>CORP | 수치 필드와 함께 읽는 설명·근거·범위 원문<br>단위: text |
| component<br>REVIEW,STEEL | 기업·설비·기술·계획·기준·구성요소 식별자; 정확한 키로 결합<br>단위: identifier |
| computed<br>CCS | 명시 항목의 수치·범주 값; 단위는 해당 행·파일에서 상속<br>단위: row unit |
| condition<br>FIGURE,NCC | NCC 전력계수·잔여배출 조합<br>단위: category |
| condition_id<br>NCC | 신규공장 실험의 가정 조합 식별자<br>단위: identifier |
| construction_EUR<br>NCC | 필드명에 명시한 연간 건설·신규 갱신·기존 갱신 현금<br>단위: EUR/year |
| continuation_capex_PV<br>REVIEW | 2050년 이후 자본 PV 또는 2040 대비 차이; continued mean은 기간 내 차이 포함<br>단위: million EUR |
| continuation_difference_vs2040<br>REVIEW | 2050년 이후 자본 PV 또는 2040 대비 차이; continued mean은 기간 내 차이 포함<br>단위: million EUR |
| continued_mean_difference_vs2040<br>REVIEW | 2050년 이후 자본 PV 또는 2040 대비 차이; continued mean은 기간 내 차이 포함<br>단위: million EUR |
| contracted_ng_GJ<br>CCS | 증분 고정계약 가스·나머지 시장가격 가스<br>단위: GJ/year |
| cost_implied_ng_GJ_y<br>CCS | 원문 가스물량·동결 비용역산 물량·원문−역산 차이<br>단위: GJ/year |
| cost_per_tco2_thkrw<br>CORP | 할인 증분비용/할인 회피톤; 보조 진단<br>단위: thousand KRW/tCO2 |
| coverage_pct<br>CORP | 선언된 관측 범위 비율; 모형 자산 완전성 증명 아님<br>단위: percent |
| criterion<br>CORP,REVIEW | 선택 통계·평균 정의; 표본/해석적 평균 구분<br>단위: category |
| cum_emis_tco2<br>CORP | 후보 또는 기준안의 비할인 누적배출<br>단위: tCO2 |
| cumulative_budget<br>CORP | 모형기간 배출예산의 비할인 합<br>단위: tCO2 |
| cumulative_budget_tco2<br>CORP | 모형기간 배출예산의 비할인 합<br>단위: tCO2 |
| cumulative_cap<br>FIGURE,NCC | 모형기간 배출예산의 비할인 합<br>단위: tCO2 |
| cumulative_emissions<br>CORP,FIGURE,NCC | 후보 또는 기준안의 비할인 누적배출<br>단위: tCO2 |
| cumulative_feasible<br>FIGURE,NCC | 검사 표지: cumulative feasible; 확률값이 아님<br>단위: boolean |
| cumulative_ratio<br>FIGURE,NCC | 기준안 대비 후보 누적배출 비율 또는 허용 최대비율<br>단위: ratio |
| currency<br>CORP,PRICE | 단위·통화·가격연도 선언; 공란은 미해결이며 0이 아님<br>단위: metadata |
| date<br>CORP,FX | 명시한 관측·가격결정·결제 날짜<br>단위: calendar |
| decision_eligible<br>CORP | 검사 표지: decision eligible; 확률값이 아님<br>단위: boolean |
| derivation<br>CORP | 수치 필드와 함께 읽는 설명·근거·범위 원문<br>단위: text |
| difference<br>PRICE | 명시 단위의 원천 대조값·산술 잔차; 별도 표시 없으면 입력 아님<br>단위: row unit |
| direct_co2<br>CCS | 동결 D15 연간 직접 CO2; 후속 C7 범위 별도 감사<br>단위: tCO2/year |
| direct_emissions<br>NCC | 필드명에 명시한 연간 배출 구성·총량·기준·말기량·상한<br>단위: tCO2/year |
| discount<br>STEEL | 현재가치 가중치 (1+r)^−(t−2027) 또는 명시적 결제일 가중치<br>단위: ratio |
| discount_factor<br>FIGURE,FX | 현재가치 가중치 (1+r)^−(t−2027) 또는 명시적 결제일 가중치<br>단위: ratio |
| discount_rate<br>FIGURE | 가격 기준과 일치하는 연간 실질·명목 할인율<br>단위: fraction/year |
| discounted_power_ore_correlation<br>STEEL | 할인 전력·광석 비용 간 표본상관<br>단위: coefficient |
| dominance_witness<br>CORP | 모든 짝지은 표본상태에서 비용이 작거나 같고 일부 엄격히 작은 후보<br>단위: identifier |
| downstream_fee<br>REVIEW | 포집 CO2 톤당 가상 하류 요금<br>단위: source USD/tCO2 captured |
| downstream_fee_per_captured_t<br>REVIEW | 포집 CO2 톤당 가상 하류 요금<br>단위: source USD/tCO2 captured |
| earlier<br>REVIEW | 짝지은 시점 지배 증명의 가동 연도<br>단위: year |
| earnings_definition<br>CORP | 재무 보고기간·이익 정의<br>단위: metadata/calendar |
| ebitda<br>CORP | 기업 재무 관측·과거 대용값; 설비 에너지 비용 아님; 통화·보고범위 유지<br>단위: row currency/unit |
| elec_intensity<br>CORP | 생산톤당 추가 전환용 전력<br>단위: MWh/t |
| electric_life<br>NCC | 민감도의 전기화 플랜트 수명<br>단위: years |
| electric_mean<br>NCC | 수명 실험의 신규 기존형·전기화 플랜트 절대 표본평균<br>단위: million EUR |
| electric_operating_years<br>FIGURE,REVIEW | 2027–2050년 내 전기화 기술 가동 연수<br>단위: years |
| electricity_MWh_per_t_ethylene<br>NCC | 에틸렌 생산량당 구입전력<br>단위: MWh/t ethylene |
| eligible<br>REVIEW | 검사 표지: eligible; 확률값이 아님<br>단위: boolean |
| eligible_for_cumulative_terminal_menu<br>FIGURE,NCC | 검사 표지: eligible for cumulative terminal menu; 확률값이 아님<br>단위: boolean |
| emission_factor<br>CORP | 기술 가동 시 생산량당 직접배출<br>단위: tCO2/t product |
| emissions_s1<br>CORP | 기업 범위 연간 직접 Scope 1 배출<br>단위: tCO2/year |
| emissions_s1_basis<br>CORP | 근거·추출·매핑·회계 상태; 모형 확률 아님<br>단위: category |
| emissions_s2<br>CORP | 보고·모형 배분 간접 Scope 2 배출; 기업 Scope 1 제약과 구별<br>단위: tCO2/year |
| emissions_s2_basis<br>CORP | 근거·추출·매핑·회계 상태; 모형 확률 아님<br>단위: category |
| end<br>CORP,PRICE | 명시한 자료 범위의 시작·끝 날짜 또는 인덱스<br>단위: calendar/index |
| energy_coal<br>CORP | 연간 석탄·가스 에너지; 28/54 GJ/톤으로 질량 변환<br>단위: GJ/year |
| energy_elec<br>CORP | 연간 구입 전력<br>단위: MWh/year |
| energy_gas<br>CORP | 연간 석탄·가스 에너지; 28/54 GJ/톤으로 질량 변환<br>단위: GJ/year |
| energy_naphtha<br>CORP | 기록된 나프타 에너지 필드; 기업 연료비에 별도 중복 가산하지 않음<br>단위: source declared GJ/year |
| epc<br>CORP | 계약 적용 0/1; 기업 검토에서는 EPC 메뉴, CCfD 비활성<br>단위: 0/1 |
| equivalent_plan_id<br>CORP | 선택·기준·동등 계획 ID; 세미콜론은 복수 ID 구분<br>단위: identifier |
| es95<br>CCS,FIGURE,NCC,REVIEW | 정확한 최악 꼬리 확률질량 평균(F06)<br>단위: dataset currency |
| es_alpha<br>CORP,FIGURE,FX,NCC,STEEL | 정확한 최악 꼬리 확률질량 평균(F06)<br>단위: dataset currency |
| es_alpha_bnkrw<br>CORP | 정확한 최악 꼬리 확률질량 평균(F06)<br>단위: dataset currency |
| es_p025<br>NCC | 경험적 부트스트랩 2.5/97.5 분위수 경계(F31)<br>단위: dataset currency |
| es_p975<br>NCC | 경험적 부트스트랩 2.5/97.5 분위수 경계(F31)<br>단위: dataset currency |
| europe_gas<br>PRICE | 정렬된 월별 벤치마크 로그수익률; 원가격 단위는 계열 등록부 참조<br>단위: log return |
| evidence_status<br>CORP | 근거·추출·매핑·회계 상태; 모형 확률 아님<br>단위: category |
| evidence_tier<br>CORP | 근거·추출·매핑·회계 상태; 모형 확률 아님<br>단위: category |
| excess_ES<br>FIGURE,STEEL | ES−표본평균<br>단위: dataset currency |
| excess_ES_contribution<br>STEEL | 총비용 꼬리 가중치 기여; excess는 구성요소 평균 차감(F31)<br>단위: million source EUR |
| excess_kurtosis_moment<br>PRICE | 표준화 3차 모멘트 / 4차 모멘트−3<br>단위: dimensionless |
| exchange_basis<br>PRICE | 환산·발열량 규약; 원문 선언 유지<br>단위: metadata |
| expanded_eligible<br>CORP | 검사 표지: expanded eligible; 확률값이 아님<br>단위: boolean |
| expanded_menu_size<br>CORP | 명시된 후보·동률·지배 후보 개수<br>단위: count |
| expanded_plan<br>CORP | 선택·기준·동등 계획 ID; 세미콜론은 복수 ID 구분<br>단위: identifier |
| expanded_value<br>CORP | 명시 항목의 수치·범주 값; 단위는 해당 행·파일에서 상속<br>단위: row unit |
| extraction<br>PRICE | 근거·추출·매핑·회계 상태; 모형 확률 아님<br>단위: category |
| extraction_method<br>CORP | 근거·추출·매핑·회계 상태; 모형 확률 아님<br>단위: category |
| facility_id<br>CORP | 기업·설비·기술·계획·기준·구성요소 식별자; 정확한 키로 결합<br>단위: identifier |
| factor<br>CORP | 가격 요인·벤치마크 계열 식별자; 공동경로 순서 보존<br>단위: identifier |
| fee_slope<br>REVIEW | Δ포집/Δ회피; 요금 변화에 대한 전환 부과금 기울기<br>단위: ratio |
| feedstock_t<br>NCC | 연간 나프타 투입·펠릿 구매량<br>단위: t/year |
| field<br>CORP | 측정 모수·원문 항목·통계·진단 이름<br>단위: identifier |
| file_name<br>CORP | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| fiscal_period_end<br>CORP | 재무 보고기간·이익 정의<br>단위: metadata/calendar |
| fiscal_year<br>CORP | 재무 보고기간·이익 정의<br>단위: metadata/calendar |
| fixed_cash_EUR<br>NCC,STEEL | 자본·고정가격 항목을 포함한 날짜별 확정 현금; 파일별 범위 유지<br>단위: EUR/year |
| fixed_price_cash_source_USD<br>CCS | 연간 자본·개수·고정가격 현금 구성<br>단위: source USD/year |
| flex_value_bnkrw<br>CORP | 기업 할인비용·탄소·정책·완전정보 보조 진단; 신규 파일럿 선택 결과 아님<br>단위: billion KRW |
| frequency<br>NCC | 부트스트랩 경계 포함 횟수/반복수<br>단위: fraction |
| frontier_count<br>NCC | 필드명에 명시한 관측·경로·반복·포함 횟수<br>단위: count |
| gcam_version<br>CORP | 기존 시나리오 출처 표지; 현재 대용치는 검증 GCAM 결과 아님<br>단위: metadata |
| grid_MWh<br>STEEL | 연간 구입 전력량<br>단위: MWh/year |
| grid_factor<br>NCC | 구입전력 배출계수의 초기값·연도값(F22)<br>단위: tCO2/MWh |
| grid_initial<br>FIGURE,NCC,REVIEW | 구입전력 배출계수의 초기값·연도값(F22)<br>단위: tCO2/MWh |
| grid_mwh<br>NCC | 연간 구입 전력량<br>단위: MWh/year |
| gross_opex_million_source_USD_y<br>CCS | 부산물 수입 전 총 운영비<br>단위: million source USD/year |
| h2_intensity<br>CORP | 생산톤당 외부구매 수소<br>단위: kg/t |
| heat_basis<br>PRICE | 환산·발열량 규약; 원문 선언 유지<br>단위: metadata |
| henry_hub<br>PRICE | 정렬된 월별 벤치마크 로그수익률; 원가격 단위는 계열 등록부 참조<br>단위: log return |
| incorrect_capture_as_avoidance_eligible<br>CCS | 검사 표지: incorrect capture as avoidance eligible; 확률값이 아님<br>단위: boolean |
| incremental_gas_contract_fraction<br>CCS,REVIEW | 고정가 비중; 기업은 전력, CCS는 증분 가스(F16,F25)<br>단위: fraction |
| incremental_gross_capex_k<br>CORP | 필드명에 명시한 기준·계획·증분·갱신 투자 현금<br>단위: thousand KRW |
| incremental_npv_KRW<br>FX | 기준·후기 결제의 청구 현재가치 또는 차이<br>단위: KRW |
| incumbent_capex_unit<br>CORP | 신기술·기존 갱신의 연산능력당 비용<br>단위: thousand KRW/(t/year) |
| incumbent_renewal_EUR<br>NCC | 필드명에 명시한 연간 건설·신규 갱신·기존 갱신 현금<br>단위: EUR/year |
| initial_capex_million_source_USD<br>CCS | 최초 설치비; 3등분 지급<br>단위: million source USD |
| instrument<br>CORP | 지원 사양·수단·유효기간; 기업 검토는 none 사용<br>단위: metadata/calendar |
| interest_expense<br>CORP | 기업 재무 관측·과거 대용값; 설비 에너지 비용 아님; 통화·보고범위 유지<br>단위: row currency/unit |
| interpretation<br>CORP,NCC,REVIEW | 수치 필드와 함께 읽는 설명·근거·범위 원문<br>단위: text |
| interval_scope<br>CORP | 결과를 정의하는 회계·적격성·통계 규약<br>단위: category |
| iron_ore<br>PRICE | 정렬된 월별 벤치마크 로그수익률; 원가격 단위는 계열 등록부 참조<br>단위: log return |
| is_disclosed<br>CORP | 검사 표지: is disclosed; 확률값이 아님<br>단위: boolean |
| is_missing<br>PRICE | 검사 표지: is missing; 확률값이 아님<br>단위: boolean |
| item<br>CCS,NCC | 측정 모수·원문 항목·통계·진단 이름<br>단위: identifier |
| item_type<br>CORP | 측정 모수·원문 항목·통계·진단 이름<br>단위: identifier |
| japan_lng<br>PRICE | 정렬된 월별 벤치마크 로그수익률; 원가격 단위는 계열 등록부 참조<br>단위: log return |
| last_reline_year<br>CORP | 해당 사건의 달력연도; adopt=착공, op=가동; 9999는 미가용<br>단위: year |
| later<br>REVIEW | 짝지은 시점 지배 증명의 가동 연도<br>단위: year |
| later_npv_KRW<br>FX | 기준·후기 결제의 청구 현재가치 또는 차이<br>단위: KRW |
| later_payment<br>FX | 합성 예시의 해당 행 날짜가 가격결정·기준결제·후기결제일인지 표시<br>단위: boolean |
| legacy_conversion_factor<br>PRICE | 과거 대조용 기록 환산계수; 현행 환율 추정 아님<br>단위: conversion ratio |
| legacy_source_id<br>PRICE | 과거 출처 ID 또는 근거 유형<br>단위: metadata |
| legacy_value<br>PRICE | 명시 단위의 원천 대조값·산술 잔차; 별도 표시 없으면 입력 아님<br>단위: row unit |
| licence<br>CORP | 기록된 라이선스·재사용 상태; 로컬 묶음은 공개 허가 아님<br>단위: metadata |
| lifetime<br>CORP | 건설기간·기술수명·기존 설비 갱신주기<br>단위: years |
| limit<br>CORP | 명시된 진단·적격성 한계값<br>단위: row unit |
| local_scenario<br>PRICE | 조건부 시나리오 이름; 확률을 뜻하지 않음<br>단위: category |
| location<br>CCS,CORP,NCC | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| loss_basis<br>CORP | 결과를 정의하는 회계·적격성·통계 규약<br>단위: category |
| maintenance_EUR<br>NCC | 날짜별 자본·유지비·종료 대용치 현금<br>단위: EUR/year |
| maintenance_capex_k<br>CORP | 필드명에 명시한 기준·계획·증분·갱신 투자 현금<br>단위: thousand KRW |
| maintenance_delta_npv<br>NCC | 전기화−기존형 할인 구성요소 현금<br>단위: million EUR |
| maintenance_scale<br>NCC | 원문 % 해석을 구분하는 유지비 배율<br>단위: ratio |
| mapping_status<br>CORP | 근거·추출·매핑·회계 상태; 모형 확률 아님<br>단위: category |
| margin_kthou_t<br>CORP | 실제 생산톤당 운영비 또는 상실 마진 대용치<br>단위: thousand KRW/t |
| market_ng_GJ<br>CCS | 증분 고정계약 가스·나머지 시장가격 가스<br>단위: GJ/year |
| matched_source_scenario<br>PRICE | 조건부 시나리오 이름; 확률을 뜻하지 않음<br>단위: category |
| max_common_naphtha_cash_error_KRW<br>FX | 수치 대조: max common naphtha cash error KRW; 통계적 불확실성 추정 아님<br>단위: named check unit |
| max_error_vs_frozen_cost_KRW_billion<br>FX | 수치 대조: max error vs frozen cost KRW billion; 통계적 불확실성 추정 아님<br>단위: named check unit |
| max_error_vs_original_FIN_KRW_billion<br>FX | 수치 대조: max error vs original FIN KRW billion; 통계적 불확실성 추정 아님<br>단위: named check unit |
| max_scaled_constraint_violation<br>CORP | 수치 대조: max scaled constraint violation; 통계적 불확실성 추정 아님<br>단위: named check unit |
| maximum_baseline_emissions_ratio<br>REVIEW | 기준안 대비 후보 누적배출 비율 또는 허용 최대비율<br>단위: ratio |
| maximum_fraction<br>REVIEW | 포집톤당 추가 하류배출 또는 목표 유지 최대치(F26)<br>단위: tCO2/tCO2 captured |
| maximum_statistic_error<br>CORP | 수치 대조: maximum statistic error; 통계적 불확실성 추정 아님<br>단위: named check unit |
| maximum_tcar_change<br>CORP | 수치 대조: maximum tcar change; 통계적 불확실성 추정 아님<br>단위: named check unit |
| maximum_translation_error<br>CORP | 수치 대조: maximum translation error; 통계적 불확실성 추정 아님<br>단위: named check unit |
| mean<br>CCS,CORP,FIGURE,FX,NCC,STEEL | 해당 비용·손실의 산술 표본평균<br>단위: dataset currency |
| mean_ES_frontier<br>REVIEW | 평균–ES 비지배 적격 후보 목록; 빈값은 후보 없음<br>단위: identifier list |
| mean_axis<br>NCC | 선택 통계·평균 정의; 표본/해석적 평균 구분<br>단위: category |
| mean_bnkrw<br>CORP | 해당 비용·손실의 산술 표본평균<br>단위: dataset currency |
| mean_mc_se<br>CCS | 평균의 몬테카를로 표준오차 또는 명시된 실제 평균 오차; 파일 문맥 참조<br>단위: dataset currency |
| mean_million_EUR<br>REVIEW | 지정 생성법 아래 기대값; analytic/theoretical은 표본평균과 구별<br>단위: dataset currency |
| mean_monthly_log_return<br>PRICE | 과거 월별 로그수익률 산술평균<br>단위: log return/month |
| methane_export_signed_MWh<br>NCC | 부호 있는 메탄 판매(음수)·구매(양수)<br>단위: MWh/year |
| methane_purchased_MWh<br>NCC | 부호 있는 메탄 판매(음수)·구매(양수)<br>단위: MWh/year |
| metric<br>CORP | 측정 모수·원문 항목·통계·진단 이름<br>단위: identifier |
| minimum_gas_coefficient<br>REVIEW | 순위 증명에서 연간 1.25Δ전력+Δ메탄 계수 최솟값<br>단위: MWh/year |
| minimum_pathwise_difference_million_EUR<br>REVIEW | 아핀 가격 아래 조기−후기 비용의 해석적 하한<br>단위: million EUR |
| minimum_value<br>CORP | 명시 항목의 수치·범주 값; 단위는 해당 행·파일에서 상속<br>단위: row unit |
| model<br>CCS,PRICE,REVIEW | 가격 생성법·출처 모형; block_12/1은 블록 길이 구분<br>단위: category |
| monte_carlo_error<br>CORP | 평균의 몬테카를로 표준오차 또는 명시된 실제 평균 오차; 파일 문맥 참조<br>단위: dataset currency |
| monte_carlo_mean<br>CORP | 해당 비용·손실의 산술 표본평균<br>단위: dataset currency |
| mult<br>CORP | 중심경로 주변 양의 가격 배수<br>단위: ratio |
| n_draws<br>CORP,FIGURE,FX,NCC,STEEL | 필드명에 명시한 관측·경로·반복·포함 횟수<br>단위: count |
| n_monthly_returns<br>PRICE | 필드명에 명시한 관측·경로·반복·포함 횟수<br>단위: count |
| naphtha_t<br>NCC | 연간 나프타 투입량<br>단위: t/year |
| naphtha_t_per_t_ethylene<br>NCC | 에틸렌 생산량당 나프타 = 1/수율<br>단위: t/t ethylene |
| net_additional_downstream_fraction_of_capture<br>REVIEW | 포집톤당 추가 하류배출 또는 목표 유지 최대치(F26)<br>단위: tCO2/tCO2 captured |
| net_debt<br>CORP | 기업 재무 관측·과거 대용값; 설비 에너지 비용 아님; 통화·보고범위 유지<br>단위: row currency/unit |
| net_methane_MWh<br>NCC | 메탄 구매−판매; 음수는 판매 수입 노출<br>단위: MWh/year |
| net_reduction<br>REVIEW | 명시적 하류 스트레스 적용 후 순감축률<br>단위: fraction |
| new_renewal_EUR<br>NCC | 필드명에 명시한 연간 건설·신규 갱신·기존 갱신 현금<br>단위: EUR/year |
| next_reinvest_year<br>CORP | 해당 사건의 달력연도; adopt=착공, op=가동; 9999는 미가용<br>단위: year |
| ng_difference_GJ_y<br>CCS | 원문 가스물량·동결 비용역산 물량·원문−역산 차이<br>단위: GJ/year |
| nominal_or_real<br>PRICE | 단위·통화·가격연도 선언; 공란은 미해결이며 0이 아님<br>단위: metadata |
| non_dominated<br>NCC | 검사 표지: non dominated; 확률값이 아님<br>단위: boolean |
| noncash_writeoff_k<br>CORP | 잔여가치 회계 대용치; 현금투자에서 제외<br>단위: thousand KRW |
| note<br>PRICE | 수치 필드와 함께 읽는 설명·근거·범위 원문<br>단위: text |
| notes<br>CORP | 수치 필드와 함께 읽는 설명·근거·범위 원문<br>단위: text |
| npv_cost_bnkrw<br>CORP | 기업 할인비용·탄소·정책·완전정보 보조 진단; 신규 파일럿 선택 결과 아님<br>단위: billion KRW |
| numeric_match<br>PRICE | 검사 표지: numeric match; 확률값이 아님<br>단위: boolean |
| observation_id<br>PRICE | 원천 관측 고유키<br>단위: identifier |
| observation_kind<br>CORP | 근거·추출·매핑·회계 상태; 모형 확률 아님<br>단위: category |
| observations<br>CORP | 필드명에 명시한 관측·경로·반복·포함 횟수<br>단위: count |
| on_analytic_mean_sample_ES_frontier<br>CCS | 검사 표지: on analytic mean sample ES frontier; 확률값이 아님<br>단위: boolean |
| on_frontier<br>CORP | 검사 표지: on frontier; 확률값이 아님<br>단위: boolean |
| on_mean_es_frontier<br>CORP | 검사 표지: on mean es frontier; 확률값이 아님<br>단위: boolean |
| on_mean_tcar_frontier<br>CORP | 검사 표지: on mean tcar frontier; 확률값이 아님<br>단위: boolean |
| on_sampled_mean_ES_frontier<br>CCS | 검사 표지: on sampled mean ES frontier; 확률값이 아님<br>단위: boolean |
| op_year<br>CORP | 해당 사건의 달력연도; adopt=착공, op=가동; 9999는 미가용<br>단위: year |
| opex_fixed<br>CORP | 설치 연산능력당 연간 운영비<br>단위: thousand KRW/(t/year)/year |
| opex_var<br>CORP | 실제 생산톤당 운영비 또는 상실 마진 대용치<br>단위: thousand KRW/t |
| ore_bundle_count<br>CCS | 청구하는 연간 원문 광석 바스켓 수; 가동 전0·가동 중1<br>단위: basket/year |
| original_choice_eligible<br>CORP | 검사 표지: original choice eligible; 확률값이 아님<br>단위: boolean |
| original_choice_value<br>CORP | 명시 항목의 수치·범주 값; 단위는 해당 행·파일에서 상속<br>단위: row unit |
| output_t<br>NCC,STEEL | 연간 제품 생산; 파일별 에틸렌·액강·HRC 구별<br>단위: t/year |
| output_t_HRC<br>CCS | 연간 제품 생산; 파일별 에틸렌·액강·HRC 구별<br>단위: t/year |
| output_t_HRC_y<br>CCS | 연간 제품 생산; 파일별 에틸렌·액강·HRC 구별<br>단위: t/year |
| p50<br>CCS,CORP,FIGURE,FX,NCC,REVIEW,STEEL | 선형보간 중앙값(F04)<br>단위: dataset currency |
| p50_bnkrw<br>CORP | 선형보간 중앙값(F04)<br>단위: dataset currency |
| p50_incl_carbon<br>CORP | 기업 할인비용·탄소·정책·완전정보 보조 진단; 신규 파일럿 선택 결과 아님<br>단위: billion KRW |
| p50_incl_carbon_bnkrw<br>CORP | 기업 할인비용·탄소·정책·완전정보 보조 진단; 신규 파일럿 선택 결과 아님<br>단위: billion KRW |
| p90<br>CORP | 상위 분위수: 숫자가 확률, q_alpha는 기록된 alpha 사용(F04)<br>단위: dataset unit |
| p95<br>FIGURE,REVIEW | 상위 분위수: 숫자가 확률, q_alpha는 기록된 alpha 사용(F04)<br>단위: dataset unit |
| pairing<br>FIGURE,STEEL | joint=공동 블록, permuted=철광석 전체 궤적 짝 변경<br>단위: category |
| param<br>CORP | 측정 모수·원문 항목·통계·진단 이름<br>단위: identifier |
| param_type<br>CORP | 측정 모수·원문 항목·통계·진단 이름<br>단위: identifier |
| passed<br>CCS | 검사 표지: passed; 확률값이 아님<br>단위: boolean |
| paths<br>CCS,FIGURE,FX,NCC,STEEL | 필드명에 명시한 관측·경로·반복·포함 횟수<br>단위: count |
| pathwise_dominance_witness<br>CCS | 모든 짝지은 표본상태에서 비용이 작거나 같고 일부 엄격히 작은 후보<br>단위: identifier |
| pdf_page<br>CCS,NCC,PRICE | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| pellet_t<br>STEEL | 연간 나프타 투입·펠릿 구매량<br>단위: t/year |
| period<br>PRICE | 명시한 관측·가격결정·결제 날짜<br>단위: calendar |
| permutation<br>STEEL | 난수 시드 또는 0부터 센 경로·순열 식별자; 관측 날짜 아님<br>단위: identifier |
| plan_gross_capex_k<br>CORP | 필드명에 명시한 기준·계획·증분·갱신 투자 현금<br>단위: thousand KRW |
| plan_id<br>CCS,CORP | 기업·설비·기술·계획·기준·구성요소 식별자; 정확한 키로 결합<br>단위: identifier |
| plan_scope1_tco2<br>CORP | 기업 범위 연간 직접 Scope 1 배출<br>단위: tCO2/year |
| point<br>CORP | 명시 항목의 수치·범주 값; 단위는 해당 행·파일에서 상속<br>단위: row unit |
| policy_exposure_bnkrw<br>CORP | 기업 할인비용·탄소·정책·완전정보 보조 진단; 신규 파일럿 선택 결과 아님<br>단위: billion KRW |
| power_MWh<br>NCC | 연간 외부 전력량<br>단위: MWh/year |
| power_emissions<br>NCC | 필드명에 명시한 연간 배출 구성·총량·기준·말기량·상한<br>단위: tCO2/year |
| ppa_share<br>CORP | 고정가 비중; 기업은 전력, CCS는 증분 가스(F16,F25)<br>단위: fraction |
| price_basis<br>CORP | 단위·통화·가격연도 선언; 공란은 미해결이며 0이 아님<br>단위: metadata |
| price_date<br>FX | 합성 예시의 해당 행 날짜가 가격결정·기준결제·후기결제일인지 표시<br>단위: boolean |
| price_year<br>PRICE | 단위·통화·가격연도 선언; 공란은 미해결이며 0이 아님<br>단위: metadata |
| primal_feasible<br>CORP | 검사 표지: primal feasible; 확률값이 아님<br>단위: boolean |
| procurement_mode<br>REVIEW | 공통 무계약 기술 비교 또는 유료 계약 동시 선택<br>단위: category |
| production<br>CORP | 연간 설비 생산량; 기업 동결 포트폴리오는 배분값<br>단위: t/year |
| production_basis<br>CORP | 근거·추출·매핑·회계 상태; 모형 확률 아님<br>단위: category |
| publication_date<br>CORP | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| publisher<br>CORP | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| q01<br>PRICE | 과거 수익률 1·5·99% 분위수; 비용 분위수와 구별<br>단위: log return |
| q05<br>PRICE | 과거 수익률 1·5·99% 분위수; 비용 분위수와 구별<br>단위: log return |
| q95<br>CCS,NCC,PRICE,REVIEW | 상위 분위수: 숫자가 확률, q_alpha는 기록된 alpha 사용(F04)<br>단위: dataset unit |
| q99<br>PRICE | 과거 수익률 1·5·99% 분위수; 비용 분위수와 구별<br>단위: log return |
| q_alpha<br>FIGURE,FX,NCC,STEEL | 상위 분위수: 숫자가 확률, q_alpha는 기록된 alpha 사용(F04)<br>단위: dataset unit |
| quality_note<br>CORP | 수치 필드와 함께 읽는 설명·근거·범위 원문<br>단위: text |
| quantity_unit<br>PRICE | 단위·통화·가격연도 선언; 공란은 미해결이며 0이 아님<br>단위: metadata |
| quote<br>CORP | 수치 필드와 함께 읽는 설명·근거·범위 원문<br>단위: text |
| ratio_2024<br>FIGURE | IEA 가격/동일 계열 2024 노드<br>단위: ratio |
| reason<br>CORP | 수치 필드와 함께 읽는 설명·근거·범위 원문<br>단위: text |
| recent_estimate<br>PRICE | 세계은행 최근 추정 관측값 표지<br>단위: boolean/category |
| reconstructed_value<br>PRICE | 명시 단위의 원천 대조값·산술 잔차; 별도 표시 없으면 입력 아님<br>단위: row unit |
| recovery<br>NCC | 유효 증기 회수 비중<br>단위: fraction |
| redistributable<br>CORP | 기록된 라이선스·재사용 상태; 로컬 묶음은 공개 허가 아님<br>단위: metadata |
| reduction<br>CORP | 명시된 감축량·감축률; 원문 단위 유지<br>단위: row unit |
| region<br>CORP,PRICE | 설비·사업장·부문·지역·적합성 이름<br>단위: category |
| reinvest_cycle_yr<br>CORP | 건설기간·기술수명·기존 설비 갱신주기<br>단위: years |
| reline_source_USD<br>CCS | 연간 자본·개수·고정가격 현금 구성<br>단위: source USD/year |
| reported<br>CCS | 명시 항목의 수치·범주 값; 단위는 해당 행·파일에서 상속<br>단위: row unit |
| reported_direct_reduction<br>CCS | 원문 패키지 직접 감축률; 옛 범위 대조용<br>단위: fraction |
| reporting_end<br>CORP | 재무 보고기간·이익 정의<br>단위: metadata/calendar |
| reporting_scope<br>CORP | 수치 필드와 함께 읽는 설명·근거·범위 원문<br>단위: text |
| reporting_start<br>CORP | 재무 보고기간·이익 정의<br>단위: metadata/calendar |
| representative<br>CORP | 선택·기준·동등 계획 ID; 세미콜론은 복수 ID 구분<br>단위: identifier |
| residual<br>CORP | 명시 단위의 원천 대조값·산술 잔차; 별도 표시 없으면 입력 아님<br>단위: row unit |
| residual_emissions<br>NCC | 필드명에 명시한 연간 배출 구성·총량·기준·말기량·상한<br>단위: tCO2/year |
| residual_per_t_naphtha<br>FIGURE,NCC | 미해결 공통 잔여배출 민감도<br>단위: tCO2/t naphtha |
| resolution<br>CORP | 원천 시간 해상도 또는 문제 해결 상태; 파일 문맥 유지<br>단위: metadata |
| retained_coal_fraction<br>CORP | 전환 후 유지하는 기존 에너지 구매 비중(F14)<br>단위: fraction |
| retained_gas_fraction<br>CORP | 전환 후 유지하는 기존 에너지 구매 비중(F14)<br>단위: fraction |
| retained_grid_fraction<br>CORP | 전환 후 유지하는 기존 에너지 구매 비중(F14)<br>단위: fraction |
| retention_evidence_status<br>CORP | 근거·추출·매핑·회계 상태; 모형 확률 아님<br>단위: category |
| retrieved_at<br>CORP | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| retrofit<br>CORP | 기술 보완설비 여부 표지; 잔존 구매비중 자동 결정 아님<br>단위: 0/1 |
| revenue<br>CORP | 기업 재무 관측·과거 대용값; 설비 에너지 비용 아님; 통화·보고범위 유지<br>단위: row currency/unit |
| risk_proxy<br>CORP | 후보탐색 선형 대용치; 보고된 MC TCaR·ES와 다름<br>단위: surrogate units |
| role<br>CCS,REVIEW | 선택/평가 표본 역할 또는 구매/판매 물량 역할; 파일 문맥으로 구별<br>단위: category |
| sample_excess_of_original_choice<br>CORP | 동일 스트레스에서 기존 선택 점수−새 최솟값<br>단위: dataset currency |
| sampled_dominance_witness<br>CORP | 모든 짝지은 표본상태에서 비용이 작거나 같고 일부 엄격히 작은 후보<br>단위: identifier |
| sampled_dominated<br>CORP | 검사 표지: sampled dominated; 확률값이 아님<br>단위: boolean |
| sampled_dominated_candidates<br>CORP | 명시된 후보·동률·지배 후보 개수<br>단위: count |
| sampled_statewise_dominated<br>CORP | 검사 표지: sampled statewise dominated; 확률값이 아님<br>단위: boolean |
| scenario<br>CCS,CORP,FIGURE,PRICE,REVIEW | 조건부 시나리오 이름; 확률을 뜻하지 않음<br>단위: category |
| scope<br>NCC,PRICE,REVIEW | 수치 필드와 함께 읽는 설명·근거·범위 원문<br>단위: text |
| sd_monthly_log_return<br>PRICE | 명시된 빈도의 로그수익률 표준편차<br>단위: log-return SD |
| section_SEC_kWh_per_kg_naphtha<br>NCC | 원문 공정구간 에너지; 공장 순구매와 구별<br>단위: kWh/kg naphtha |
| sector<br>CORP | 설비·사업장·부문·지역·적합성 이름<br>단위: category |
| sector_budget_mt<br>CORP | 기업 비례배분 전 부문 배출 상한<br>단위: MtCO2/year |
| seed<br>CCS,FIGURE,FX,NCC,REVIEW,STEEL | 난수 시드 또는 0부터 센 경로·순열 식별자; 관측 날짜 아님<br>단위: identifier |
| selected_physical_cases<br>REVIEW | 계약을 제외한 선택 실물 구성<br>단위: identifier list |
| selected_plan_id<br>CORP | 선택·기준·동등 계획 ID; 세미콜론은 복수 ID 구분<br>단위: identifier |
| selected_plans<br>REVIEW | 선택·기준·동등 계획 ID; 세미콜론은 복수 ID 구분<br>단위: identifier |
| selection_changed<br>CORP | 검사 표지: selection changed; 확률값이 아님<br>단위: boolean |
| selection_criterion<br>CORP | 선택 통계·평균 정의; 표본/해석적 평균 구분<br>단위: category |
| sensitivity_weight<br>REVIEW | 평균+λES의 λ; 선호 민감도 가정<br>단위: dimensionless |
| series_id<br>CORP,PRICE | 가격 요인·벤치마크 계열 식별자; 공동경로 순서 보존<br>단위: identifier |
| sha256<br>CORP | 원천 바이트 SHA-256 지문; 경제적 타당성 인증 아님<br>단위: hash |
| shared_anchor<br>PRICE | 원천 비교의 공통 벤치마크·환율 기준<br>단위: metadata |
| sheet<br>PRICE | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| sim<br>CORP | 난수 시드 또는 0부터 센 경로·순열 식별자; 관측 날짜 아님<br>단위: identifier |
| site<br>CORP | 설비·사업장·부문·지역·적합성 이름<br>단위: category |
| skew_moment<br>PRICE | 표준화 3차 모멘트 / 4차 모멘트−3<br>단위: dimensionless |
| solution_status<br>CORP | 최적화 종료 상태; 실행가능성과 최적성 구분<br>단위: category |
| solve_status<br>CORP | 최적화 종료 상태; 실행가능성과 최적성 구분<br>단위: category |
| source_column<br>PRICE | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| source_context<br>CORP | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| source_id<br>CORP | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| source_label<br>CORP | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| source_locator<br>CORP | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| source_name<br>CORP,PRICE | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| source_ng_GJ_y<br>CCS | 원문 가스물량·동결 비용역산 물량·원문−역산 차이<br>단위: GJ/year |
| source_node<br>PRICE | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| source_or_linear_value<br>PRICE | 명시 단위의 원천 대조값·산술 잔차; 별도 표시 없으면 입력 아님<br>단위: row unit |
| source_price<br>FIGURE | 비율 변환 전 IEA 원문 가격 노드<br>단위: 2024 USD/source unit |
| source_region<br>PRICE | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| source_row<br>PRICE | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| source_sha256<br>CORP,PRICE | 원천 바이트 SHA-256 지문; 경제적 타당성 인증 아님<br>단위: hash |
| source_table<br>PRICE | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| source_token<br>CCS | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| source_type<br>CORP | 과거 출처 ID 또는 근거 유형<br>단위: metadata |
| source_url<br>CCS,CORP,NCC,PRICE | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| squared_return_acf1<br>PRICE | 수익률 또는 제곱수익률의 1시차 표본상관<br>단위: coefficient |
| start<br>CORP,PRICE | 명시한 자료 범위의 시작·끝 날짜 또는 인덱스<br>단위: calendar/index |
| state<br>FX | 결제 예시의 합성 상태 이름<br>단위: identifier |
| status<br>CCS,CORP,PRICE | 근거·추출·매핑·회계 상태; 모형 확률 아님<br>단위: category |
| structural_high<br>CORP | 가정된 하·상 민감도 범위; 자동으로 통계구간이 아님<br>단위: row unit |
| structural_low<br>CORP | 가정된 하·상 민감도 범위; 자동으로 통계구간이 아님<br>단위: row unit |
| support<br>CORP | 지원 사양·수단·유효기간; 기업 검토는 none 사용<br>단위: metadata/calendar |
| support_scenario<br>CORP | 지원 사양·수단·유효기간; 기업 검토는 none 사용<br>단위: metadata/calendar |
| switching_carbon_charge_per_avoided_t<br>REVIEW | 가상 배출톤 부과금·동률 문턱; 증분 절감은 회피톤 적용(F28)<br>단위: source USD/tCO2 |
| table<br>PRICE | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| target<br>CCS,REVIEW | 요구 회피량/기준 배출량 비중<br>단위: fraction |
| target_onsite_reduction<br>CCS | 요구 회피량/기준 배출량 비중<br>단위: fraction |
| tcar<br>CORP,FIGURE,FX,NCC,STEEL | 상위 분위수−중앙값(F05); 투자예산 아님<br>단위: dataset currency |
| tcar95<br>CCS,FIGURE,NCC,REVIEW | 상위 분위수−중앙값(F05); 투자예산 아님<br>단위: dataset currency |
| tcar_bnkrw<br>CORP | 상위 분위수−중앙값(F05); 투자예산 아님<br>단위: dataset currency |
| tcar_p025<br>NCC | 경험적 부트스트랩 2.5/97.5 분위수 경계(F31)<br>단위: dataset currency |
| tcar_p975<br>NCC | 경험적 부트스트랩 2.5/97.5 분위수 경계(F31)<br>단위: dataset currency |
| tech_id<br>CORP | 기업·설비·기술·계획·기준·구성요소 식별자; 정확한 키로 결합<br>단위: identifier |
| terminal<br>NCC | 신규공장 종료가치 규약; 없음 또는 대용치<br>단위: category |
| terminal_EUR<br>NCC | 날짜별 자본·유지비·종료 대용치 현금<br>단위: EUR/year |
| terminal_cap<br>FIGURE,NCC | 필드명에 명시한 연간 배출 구성·총량·기준·말기량·상한<br>단위: tCO2/year |
| terminal_emissions<br>FIGURE,NCC | 필드명에 명시한 연간 배출 구성·총량·기준·말기량·상한<br>단위: tCO2/year |
| terminal_feasible<br>FIGURE,NCC | 검사 표지: terminal feasible; 확률값이 아님<br>단위: boolean |
| terminal_proxy_shift<br>FIGURE,REVIEW | 양쪽 잔존가치 대용치로 인한 확정 현재가치 변화<br>단위: million EUR |
| terminal_rule<br>FIGURE,REVIEW | 결과를 정의하는 회계·적격성·통계 규약<br>단위: category |
| text<br>PRICE | 수치 필드와 함께 읽는 설명·근거·범위 원문<br>단위: text |
| theoretical_mean<br>FIGURE,STEEL | 지정 생성법 아래 기대값; analytic/theoretical은 표본평균과 구별<br>단위: dataset currency |
| thermal_coal_au<br>PRICE | 정렬된 월별 벤치마크 로그수익률; 원가격 단위는 계열 등록부 참조<br>단위: log return |
| tied_analytic_minimum_count<br>CORP | 명시된 후보·동률·지배 후보 개수<br>단위: count |
| title<br>CORP | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| token_found<br>CCS | 검사 표지: token found; 확률값이 아님<br>단위: boolean |
| tolerance<br>CCS | 수치 대조: tolerance; 통계적 불확실성 추정 아님<br>단위: named check unit |
| tolerance_source_USD<br>CCS | 수치 대조: tolerance source USD; 통계적 불확실성 추정 아님<br>단위: named check unit |
| total_debt<br>CORP | 기업 재무 관측·과거 대용값; 설비 에너지 비용 아님; 통화·보고범위 유지<br>단위: row currency/unit |
| total_emissions<br>NCC | 필드명에 명시한 연간 배출 구성·총량·기준·말기량·상한<br>단위: tCO2/year |
| total_plant_TOC_at_115t_h_million_EUR2019<br>NCC | 시간당 에틸렌 115톤에서 플랜트 투자 곡선값<br>단위: million EUR2019 |
| transcription<br>NCC | 근거·추출·매핑·회계 상태; 모형 확률 아님<br>단위: category |
| unit<br>CCS,CORP,NCC,PRICE,REVIEW | 단위·통화·가격연도 선언; 공란은 미해결이며 0이 아님<br>단위: metadata |
| unit_name<br>CORP | 설비·사업장·부문·지역·적합성 이름<br>단위: category |
| unit_type<br>CORP | 설비·사업장·부문·지역·적합성 이름<br>단위: category |
| url_or_doi<br>CORP | 명시한 출처 식별·인용·원문 위치·접근 메타데이터<br>단위: metadata |
| used<br>CORP | 검사 표지: used; 확률값이 아님<br>단위: boolean |
| valid_from<br>CORP | 지원 사양·수단·유효기간; 기업 검토는 none 사용<br>단위: metadata/calendar |
| valid_to<br>CORP | 지원 사양·수단·유효기간; 기업 검토는 none 사용<br>단위: metadata/calendar |
| value<br>CCS,CORP,NCC,PRICE | 명시 항목의 수치·범주 값; 단위는 해당 행·파일에서 상속<br>단위: row unit |
| value_bn_native<br>CORP | 기업 재무 관측·과거 대용값; 설비 에너지 비용 아님; 통화·보고범위 유지<br>단위: row currency/unit |
| value_high<br>CORP | 가정된 하·상 민감도 범위; 자동으로 통계구간이 아님<br>단위: row unit |
| value_low<br>CORP | 가정된 하·상 민감도 범위; 자동으로 통계구간이 아님<br>단위: row unit |
| variable<br>CORP,PRICE | 측정 모수·원문 항목·통계·진단 이름<br>단위: identifier |
| variant<br>CORP | 기준·독립시드·구조적 스트레스 사양<br>단위: category |
| verification_status<br>CORP | 근거·추출·매핑·회계 상태; 모형 확률 아님<br>단위: category |
| window_ES_difference_with_capital_extension<br>REVIEW | 자본만 연장한 진단값; 전체기간 ES·TCaR 아님(F23)<br>단위: million EUR |
| window_TCaR_with_capital_extension<br>REVIEW | 자본만 연장한 진단값; 전체기간 ES·TCaR 아님(F23)<br>단위: million EUR |
| year<br>CCS,CORP,FIGURE,NCC,PRICE,STEEL | 해당 사건의 달력연도; adopt=착공, op=가동; 9999는 미가용<br>단위: year |
| year_stated<br>CORP | 해당 사건의 달력연도; adopt=착공, op=가동; 9999는 미가용<br>단위: year |

### 5. 전체 파일·저장 배열 목록

아래 목록은 묶음의 모든 파일이다. CSV 행×열은 저장 레코드 크기로 실제 분석 부분집합과 다를 수 있다. 계획 파일은 같은 스키마지만 45일정을 모두 보존했다. 코드는 현행 구현 사본이다. JSON·YAML의 중첩키와 모든 말단값은 metadata_leaf_inventory.csv에 전수 기록했다. 원본의 값·메타데이터·정밀도는 모두 유지한다.

### CORP 파일

docs/research_cycles/2026-09-05/research_case_expanded

| ID | 파일명 | 크기 / 구조 |
| --- | --- | --- |
| DS060 | candidate_expansion_comparison.csv | 24 × 14 |
| DS061 | candidate_expansion_validation.json | 854 bytes |
| DS062 | independent_candidate_risk.csv | 450 × 10 |
| DS063 | paired_annual_capital_and_emissions.csv | 1080 × 11 |
| DS064 | plan_feasibility_and_cost.csv | 45 × 8 |
| DS065 | validation.json | 834 bytes |

docs/research_cycles/2026-09-05/robustness

| ID | 파일명 | 크기 / 구조 |
| --- | --- | --- |
| DS066 | fixed_candidate_bootstrap.csv | 105 × 9 |
| DS067 | manifest.json | 2,487 bytes |

docs/research_cycles/2026-09-05/robustness_initial_forecast

| ID | 파일명 | 크기 / 구조 |
| --- | --- | --- |
| DS068 | manifest.json | 1,334 bytes |

docs/research_cycles/2026-09-05/robustness_verified

| ID | 파일명 | 크기 / 구조 |
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

| ID | 파일명 | 크기 / 구조 |
| --- | --- | --- |
| DS078 | config.yaml | 1,580 bytes |

tmp/research_case_expanded/run/e1

| ID | 파일명 | 크기 / 구조 |
| --- | --- | --- |
| DS079 | constraints.csv | 192 × 7 |
| DS080 | e1_check.csv | 8 × 4 |
| DS081 | price_paths_central.csv | 576 × 6 |
| DS082 | tech_availability.csv | 0 × 4 |

tmp/research_case_expanded/run/e2

| ID | 파일명 | 크기 / 구조 |
| --- | --- | --- |
| DS083 | plan_index.csv | 45 × 18 |

tmp/research_case_expanded/run/e2/plans

| ID | 파일명 | 크기 / 구조 |
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

| ID | 파일명 | 크기 / 구조 |
| --- | --- | --- |
| DS129 | calibration_report.csv | 9 × 2 |
| DS130 | price_model.json | 3,120 bytes |
| DS131 | price_sims.parquet | 960000 × 4 |

tmp/research_case_expanded/run/e5

| ID | 파일명 | 크기 / 구조 |
| --- | --- | --- |
| DS132 | frontier_points.csv | 450 × 34 |
| DS133 | metrics_company.csv | 8 × 21 |

tmp/research_case_expanded/run

| ID | 파일명 | 크기 / 구조 |
| --- | --- | --- |
| DS134 | run_manifest.json | 14,274 bytes |

tmp/research_case_v3/data

| ID | 파일명 | 크기 / 구조 |
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

### PRICE 파일

data/research_v2/block_price_paths

| ID | 파일명 | 크기 / 구조 |
| --- | --- | --- |
| DS183 | manifest.json | 1,631 bytes |

data/research_v2/iea_2025_scenarios

| ID | 파일명 | 크기 / 구조 |
| --- | --- | --- |
| DS184 | annual_reference_curves.csv | 729 × 13 |
| DS185 | curves.json | 16,210 bytes |
| DS186 | legacy_alignment_audit.csv | 36 × 17 |
| DS187 | legacy_alignment_manifest.json | 895 bytes |
| DS188 | manifest.json | 1,778 bytes |
| DS189 | native_observations.csv | 63 × 16 |
| DS190 | scenario_nodes.csv | 81 × 11 |

data/research_v2/price_history

| ID | 파일명 | 크기 / 구조 |
| --- | --- | --- |
| DS191 | aligned_monthly_log_returns.csv | 191 × 7 |
| DS192 | manifest.json | 1,203 bytes |
| DS193 | monthly_log_return_correlation.csv | 6 × 7 |
| DS194 | monthly_log_return_diagnostics.csv | 6 × 15 |
| DS195 | native_monthly_prices.csv | 4800 × 15 |
| DS196 | source_comparison_notes.json | 22,377 bytes |
| DS197 | source_series_descriptions.csv | 104 × 2 |

### NCC 파일

data/research_v2/ncc_reference_cash

| ID | 파일명 | 크기 / 구조 |
| --- | --- | --- |
| DS163 | annual_cash.csv | 768 × 11 |
| DS164 | conditional_metrics.csv | 64 × 18 |
| DS165 | incremental_cost_draws.npz | 593,847 bytes |
| DS166 | manifest.json | 2,937 bytes |
| DS167 | translation_checks.json | 1,171 bytes |

data/research_v2/ncc_timing_frontier

| ID | 파일명 | 크기 / 구조 |
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

| ID | 파일명 | 크기 / 구조 |
| --- | --- | --- |
| DS178 | boundary_checks.json | 471 bytes |
| DS179 | derived_quantities.csv | 2 × 5 |
| DS180 | manifest.json | 1,165 bytes |
| DS181 | package.json | 1,684 bytes |
| DS182 | source_observations.csv | 39 × 9 |

### CCS 파일

data/research_v2/ieaghg_paired

| ID | 파일명 | 크기 / 구조 |
| --- | --- | --- |
| DS001 | STEPS_validation_absolute_costs.npz | 822,796 bytes |
| DS002 | STEPS_validation_incremental_costs.npz | 591,382 bytes |
| DS003 | annual_cash_quantities.csv | 240 × 11 |
| DS004 | conditional_cost_metrics.csv | 120 × 18 |
| DS005 | finite_frontier.csv | 180 × 8 |
| DS006 | independent_selection.json | 7,949 bytes |
| DS007 | manifest.json | 4,132 bytes |

data/research_v2/ieaghg_physical_reference

| ID | 파일명 | 크기 / 구조 |
| --- | --- | --- |
| DS008 | arithmetic_checks.csv | 12 × 6 |
| DS009 | emissions_qualification.csv | 15 × 5 |
| DS010 | legacy_transcription_checks.csv | 75 × 5 |
| DS011 | manifest.json | 2,732 bytes |
| DS012 | physical_source_observations.csv | 23 × 7 |
| DS013 | same_product_ledger.csv | 3 × 15 |

data/research_v2/ieaghg_reference

| ID | 파일명 | 크기 / 구조 |
| --- | --- | --- |
| DS014 | account_checks.csv | 10 × 6 |
| DS015 | manifest.json | 824 bytes |
| DS016 | package.json | 5,928 bytes |
| DS017 | source_observations.csv | 75 × 8 |

### STEEL 파일

data/research_v2/steel_cost_reference

| ID | 파일명 | 크기 / 구조 |
| --- | --- | --- |
| DS212 | vogl_main_text_package.json | 3,403 bytes |

data/research_v2/steel_procurement_tail

| ID | 파일명 | 크기 / 구조 |
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

### FX 파일

data/research_v2/invoice_fin_bridge

| ID | 파일명 | 크기 / 구조 |
| --- | --- | --- |
| DS158 | frozen_FIN_comparison.csv | 8 × 7 |
| DS159 | paired_risk_metrics.csv | 6 × 9 |
| DS160 | timing_example_costs.csv | 2 × 4 |
| DS161 | timing_example_inputs.csv | 8 × 8 |
| DS162 | verification.json | 2,078 bytes |

### REVIEW 파일

docs/research_cycles/2026-09-10-investment-review/cycle1

| ID | 파일명 | 크기 / 구조 |
| --- | --- | --- |
| DS198 | cost_decomposition.csv | 24 × 3 |
| DS199 | editorial_verification.json | 860 bytes |
| DS200 | emissions_budget_sweep.csv | 36 × 6 |
| DS201 | terminal_sensitivity.csv | 16 × 10 |
| DS202 | verification.json | 1,750 bytes |

docs/research_cycles/2026-09-10-investment-review/cycle2

| ID | 파일명 | 크기 / 구조 |
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

### FIGURE 파일

output/pilot_review/figure_data

| ID | 파일명 | 크기 / 구조 |
| --- | --- | --- |
| DS152 | discount_weights.csv | 72 × 3 |
| DS153 | ncc_qualification.csv | 16 × 15 |
| DS154 | ncc_risk_metrics.csv | 6 × 10 |
| DS155 | ncc_tcar_quantiles.csv | 8 × 10 |
| DS156 | scenario_nodes.csv | 18 × 5 |
| DS157 | steel_risk_metrics.csv | 6 × 13 |

### CODE 파일

scripts

| ID | 파일명 | 크기 / 구조 |
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

| ID | 파일명 | 크기 / 구조 |
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

### 5.1 배열명·차원·해석

배열 축은 생성 스크립트와 함께 읽는다. 비용벡터는 [경로], 연간 가격·배수는 [경로,연도], block_starts는 [경로,블록], log_anchors는 [월,요인], permutation은 0부터 센 [경로] 재배치다. 길이24 연도는 2027–2050, NCC 고정 표본은5000경로, CCS 평가벡터는10000경로다. 같은 접두·시드는 짝지은 경로다. 모든 배열의 최솟값·최댓값·자료형·원소 수는 array_inventory.csv에 있다.

| 데이터셋 ID | 정확한 배열명 | 구조 / 자료형 |
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

### 5.2 누락 검사와 해석 한계

| 검사 | 기준 |
| --- | --- |
| Data | 모든 등록 파일 존재·사본 SHA-256 일치. |
| Variables | 모든 CSV·Parquet 필드를 양언어 사전에 포함; 모든 NPZ키 목록화. |
| Parameters | JSON·YAML 모든 말단값 보존; 원본 입력행 무반올림 보존. |
| Equations | 36개 산식 묶음으로 현금·물량·적격성·가격·통계·선택 용도 연결. |
| Body | 기존 본문·그림6·표9 보존; OOXML 요소 대조. |
| Claims | 신규 기업추정·CCS 전과정 검증·시스템 연계 완료·공개 DB 출시를 주장하지 않음. |

전수성은 명시한 자료 묶음과 페이퍼 계산 등록부를 대상으로 하며 현실의 모든 공정을 측정했다는 뜻은 아니다. 세금·금융·운전자본·실제 조달 베이시스/부도/물량 위험·폐쇄 수입·CO2 전과정은 여전히 일치하는 근거가 필요하다. 누락은 0 관측값이 아니라 명시적 모형 한계다. 플랜잇 연계와 공개 감축기술 DB는 이런 범위·변환을 판본별로 검토 가능하게 만드는 방향이다.
