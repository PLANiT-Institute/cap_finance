# CAP-KJ Data Catalogue and Acquisition Protocol

**Version:** 1.0  
**Data cut-off:** 5 August 2026  
**Purpose:** define the actual data required to execute `PROJECT_PLAN.md`, the authoritative source hierarchy, and the first-pass availability status.

## 1. Data principles

1. Use a reported or regulatory value before an estimate.
2. Preserve the original reporting boundary, period, unit, and currency.
3. Do not compare company totals until the domestic facility boundary is reconstructed.
4. Do not infer facility precision from a corporate total without an explicit allocation rule.
5. Keep Scope 1, Scope 2, feedstock carbon, captured CO₂, avoided emissions, and offsets in separate fields.
6. Store exact source location and retrieval date for every material value.
7. Never overwrite a raw source.
8. Publish only data allowed by the source licence.

## 2. Source-register schema

Every source must be represented in `source_register.csv`.

| Field | Definition |
|---|---|
| `source_id` | stable project identifier |
| `publisher` | issuing organisation |
| `title` | source title |
| `source_type` | regulation, registry, statistics, company report, model, paper, market data |
| `url_or_doi` | persistent URL or DOI |
| `publication_date` | date issued |
| `retrieved_at` | date and time retrieved |
| `reporting_start` / `reporting_end` | period represented |
| `location` | page, table, sheet, row, API field, or query |
| `licence` | reuse terms |
| `redistributable` | yes, no, or conditional |
| `file_name` | local raw-file name where permitted |
| `sha256` | raw-file checksum |
| `extraction_method` | API, CSV, PDF table, OCR, manual transcription |
| `quality_note` | scope, revision, assurance, or known issue |

## 3. Initial verified company anchors

These anchors confirm that the sample is quantitatively material. They do not replace facility reconciliation.

| Source ID | Company | Period and boundary | Verified anchor | Source |
|---|---|---|---:|---|
| `POSCO_ESG_2025` | POSCO | 2025 steel reporting boundary | Scope 1+2 **69,846,050 tCO₂e**; intensity **2.02 tCO₂e/t steel** | [POSCO environmental data](https://sustainability.posco.com/S91/S91F10/eng/cmspage.do?mmcd=2682093497003371) |
| `NSC_DB_2025` | Nippon Steel | FY2024 non-consolidated | GHG total **79,013 ktCO₂e**; energy-derived CO₂ **75,349 kt** | [Nippon Steel Data Book 2025](https://www-zam.nipponsteel.com/en/ir/library/pdf/nsc_en_ir_2025_databook.pdf) |
| `LOTTE_ESG_2025` | LOTTE Chemical | 2025 parent | Scope 1+2 **5,370,773 tCO₂e** | [LOTTE Chemical ESG report library](https://www.lottechem.com/en/esg/management_report.do) |
| `LOTTE_ESG_2025` | LOTTE Chemical | 2025 parent plus named consolidated companies | Scope 1+2 **6,117,646 tCO₂e** | same report |
| `MCI_ESG_2025` | Mitsui Chemicals | FY2024 parent | Scope 1 **3,383 kt**; Scope 2 **486 kt** | [Mitsui ESG performance data](https://jp.mitsuichemicals.com/content/dam/mitsuichemicals/sites/mci/documents/sustainability/report/esg2025web_e_part06.pdf.coredownload.pdf) |
| `MCI_ESG_2025` | Mitsui Chemicals | FY2024 group | Scope 1+2 **4,428 ktCO₂e** | same report |

Required follow-up fields:

- assurance status and exact organisational boundary;
- production denominator and product definition;
- domestic versus overseas contribution;
- treatment of purchased coke, oxygen, steam, and self-generation;
- registry-to-corporate reconciliation.

## 4. Company and facility sources

### 4.1 POSCO

| Dataset | Variables | Preferred source | Status |
|---|---|---|---|
| Corporate emissions and energy | Scope 1, Scope 2, Scope 3, intensity, fuel, electricity | POSCO Sustainability Report and ESG data tables | verified at aggregate level |
| Facility list | Pohang and Gwangyang units, capacities, routes | POSCO reports, business reports, official project releases | works identities verified; unit/capacity reconciliation required |
| Installation emissions | direct and indirect emissions by site and year | Korea GIR/NGMS public data and Korea public-data portal | acquisition required |
| Blast-furnace data | commissioning, relining, inner volume, status | official POSCO releases and facility histories | Pohang No. 4 BF 2024 relining verified; remaining units required |
| Production | crude steel and products by works | company reports; Korea Iron & Steel Association where available | gap: works allocation may be required |
| Transition projects | EAF, HyREX, hydrogen, CCUS, efficiency | official POSCO project releases | acquisition required |
| Actual policy treatment | Korean ETS verified emissions, allocation, surrender | GIR, Ministry, KRX and company disclosure | acquisition required |

### 4.2 Nippon Steel

| Dataset | Variables | Preferred source | Status |
|---|---|---|---|
| Corporate emissions and energy | non-consolidated and covered-group emissions, energy | Nippon Steel Data Book 2025 | verified |
| Domestic works | site, area, products, capacity and equipment | Nippon Steel Data Book 2025 | verified |
| Production by site | crude steel by works/area | Nippon Steel Data Book 2025 | verified for FY2024 at published resolution |
| Installation emissions | facility emissions from 2021 onward | Japan MOE EEGS/SHK disclosure | available; extraction required |
| Furnace and relining | furnace size, relining and operation | Nippon Steel Data Book and official works releases | available; normalisation required |
| Transition projects | COURSE50, Super COURSE50, hydrogen, EAF, CCUS | official Nippon Steel and NEDO releases | acquisition required |
| Actual policy treatment | GX ETS eligibility, allocation, price rules | METI GX ETS | rules available; price history immature |

### 4.3 LOTTE Chemical

| Dataset | Variables | Preferred source | Status |
|---|---|---|---|
| Corporate emissions and targets | parent and selected consolidated Scope 1+2, energy, 2030/2050 targets | LOTTE Chemical ESG Report 2025 | verified |
| Domestic complexes | Yeosu Basic, Yeosu Advanced, Daesan, Ulsan | official ESG report and product technology guides | verified |
| Unit capacities and processes | NCC, ethylene, propylene, PE, PP, EG, BTX and other primary products | LOTTE product technology guide | available; extraction required |
| Installation emissions | site-year Scope 1 and 2 | company ESG report; Korea GIR/NGMS or public-data portal | CY2025 company facility rows verified; regulator cross-check required |
| Restructuring | Daesan spin-off/merger; Yeosu rationalisation | official 2025–2026 releases and filings | announced; completion must be checked at each release |
| Transition projects | efficiency, fuel shift, renewable power, hydrogen, CCUS, circular feedstock | ESG report and official project releases | available |
| Product carbon | product-specific LCA where public | official LCA announcements and verified product declarations | limited public numeric data |

Verified facility example: LOTTE reports a naphtha cracker with annual capacity of **1.0 Mt ethylene** and **0.52 Mt propylene** in its official process guide. The exact plant and current operating boundary must be recorded during extraction rather than inferred from the search result alone.

### 4.4 Mitsui Chemicals

| Dataset | Variables | Preferred source | Status |
|---|---|---|---|
| Corporate emissions and energy | parent, domestic affiliates, overseas, group | Mitsui Chemicals ESG Report 2025 | verified |
| Domestic works | Ichihara, Osaka, Iwakuni-Ohtake, Omuta and other sites | [official domestic sites](https://jp.mitsuichemicals.com/en/corporate/ds/works/index.htm) | verified |
| Installation emissions | facility-year emissions | Japan MOE EEGS/SHK disclosure | FY2023 Mitsui block extracted: 12 reported records in `mci_shk_facility_emissions_2023.csv`; period-matched bridge pending model adoption |
| Cracker capacity and ownership | Chiba LLP and Osaka Petrochemical | official corporate releases and filings | available |
| Chiba consolidation | timing, capacity, ownership, closure | official Idemitsu–Mitsui releases | announced; FY2027 target |
| Western-Japan consolidation | capacity, CAPEX support, expected CO₂ reduction | official January 2026 joint release | verified announcement |
| Process and feedstock transition | biomass feedstock, circular feedstock, low-carbon fuels | official project releases and ESG report | available |

Verified project example: the disclosed western-Japan project indicates **¥21.2 billion** investment, maximum subsidy application of **¥10.4 billion**, and expected Scope 1+2 reduction of **506,000 tCO₂/year**. The values provide a valuable validation case but are not general technology-cost assumptions.

FY2023 SHK upgrade: the official Mitsui corporate disclosure is **3,571,026 tCO₂**. The 12 listed facility records total **3,560,757 tCO₂**, leaving an explicit **10,269 tCO₂** corporate residual. `mci_shk_to_fy2024_bridge.csv` aggregates repeated registry site labels and applies their FY2023 shares to the separately reported FY2024 parent Scope 1+2 anchor with a ±10% allocation range. These allocated FY2024 values are quality C and must not be described as reported FY2024 facility emissions.

## 5. National production and emissions sources

| Domain | Korea | Japan | Use |
|---|---|---|---|
| Steel production | Korea Iron & Steel Association / KOSIS steel statistics; company reports | [Japan Iron and Steel Federation annual and monthly statistics](https://www.jisf.or.jp/en/statistics/production/index.html); METI production statistics | national production envelope and residual sector |
| Petrochemical production | MOTIE, KOSIS, Korea Petrochemical Industry Association where accessible | [METI Current Survey of Production](https://www.meti.go.jp/english/statistics/tyo/seidou/), including chemical-industry commodity tables | ethylene and primary-chemical baseline |
| National GHG inventory | Korea GIR national inventory | [Japan MOE national GHG inventory](https://www.env.go.jp/earth/ondanka/ghg-mrv/emissions/index.html) | sector-emissions reconciliation |
| Facility GHG | [Korea public-data portal regulated-company statements](https://www.data.go.kr/dataset/3072361/fileData.do) | [Japan EEGS/SHK operator and facility data](https://eegs.env.go.jp/ghg-santeikohyo-result/search) | asset emissions and reconciliation |
| Industrial energy | KESIS, KEA, KOSIS | METI Energy Balance and Current Survey | fuel and electricity intensity checks |
| Trade | Korea Customs Service and UN Comtrade validation | Japan Customs and UN Comtrade validation | leakage and replacement-production cases |

## 6. Scenario and model data

| Source ID | Required variables | Status | Rule |
|---|---|---|---|
| `GCAM_CORE_8_2` | Korea/Japan production, emissions, energy, prices, technology and policy markets | open code and documentation available | pin commit and model configuration |
| `GCAM_KAIST_1_0` | Korea inputs and database | public input package available | not treated as solved output |
| `GCAM_KAIST_INDUSTRY` | Korea industrial pathway inputs | public Zenodo package available | acquire paper figure data if possible |
| `KAIST_LATEST_OUTPUT` | solved CP/NZ output for Korea and Japan, steel and chemicals, prices and assumptions | request required | preferred common scenario backbone |
| `IEA_STEEL_ROADMAP` | route energy, emissions, maturity and global pathway | public CC BY 4.0 | engineering and pathway validation |
| `IEA_PRIMARY_CHEM` | primary-chemicals pathway and technology milestones | public | chemicals validation |
| `IEA_ETP_GUIDE_2026` | readiness, project and performance data | public CC BY 4.0 | technology library |

The exact KAIST request is specified in [`DATA_REQUEST_KAIST.md`](DATA_REQUEST_KAIST.md).

## 7. Market prices and policy data

### 7.1 Electricity

| Country | Source | Variables | Frequency | Treatment |
|---|---|---|---|---|
| Korea | [KPX EPSIS weighted SMP](https://epsis.kpx.or.kr/epsisnew/selectEkmaSmpSmpChart.do?menuId=040201) and hourly SMP | KRW/kWh, date/time, region where available | hourly/monthly | market anchor; add industrial tariff and network effects separately |
| Korea | KEPCO tariff schedules and company contract disclosure | industrial tariff components | revision period | procurement sensitivity, not a substitute for SMP history |
| Japan | JEPX spot-market data | JPY/kWh by 30-minute product and area | half-hourly/daily | market anchor; distinguish area and baseload products |
| Japan | METI electricity statistics and tariff data | industrial price and fuel-adjustment components | monthly/annual | end-user reconciliation |

### 7.2 Carbon

| Country | Source | Variables | Treatment |
|---|---|---|---|
| Korea | KRX ETS/KAU market and GIR/MOE rules | daily allowance price, volume, compliance year, allocation | deflate and match allowance vintage; apply free allocation |
| Japan | [METI GX ETS](https://www.meti.go.jp/policy/energy_environment/global_warming/ets.html) | eligibility, allocation rules, reference price limits, trades when available | no long-run variance until sufficient history exists |
| Both | GCAM policy market | fixed price, shadow price, emissions constraint | scenario diagnostic only; never actual compliance cost |

### 7.3 Hydrogen

No primary spot series is accepted as representative of large industrial clean-hydrogen procurement. Build separate domestic and import-parity series from:

- electrolyser CAPEX, efficiency, lifetime and utilisation;
- electricity price and clean-power constraint;
- water and O&M;
- compression, storage, pipeline or trucking;
- carrier conversion and reconversion where applicable;
- shipping and terminal cost;
- exchange rate;
- lifecycle carbon intensity.

The component model must retain power–hydrogen covariance.

### 7.4 Feedstock and fuel

| Variable | Korea source | Japan source | Fallback |
|---|---|---|---|
| naphtha and oil products | Korea National Oil Corporation Petronet and customs | METI energy statistics and Japan Customs | IMF/World Bank commodity series for validation only |
| LNG and natural gas | KESIS, customs, company reports | METI energy statistics, Japan Customs | IEA or World Bank benchmark with delivery adjustment |
| coal and iron ore | Korea Customs and company disclosures | Japan Customs and company disclosures | World Bank benchmark |
| scrap | national steel statistics and customs | JISF/METI and customs | industry reports with licence review |
| DRI/HBI | customs and company project disclosure | customs and company project disclosure | international trade data |
| recycled/biogenic chemical feedstock | government project data and company disclosure | METI project data and company disclosure | technology stress range |

## 8. Technology-parameter schema

Each `technology_parameters` record requires:

| Field group | Required fields |
|---|---|
| Identity | sector, route, technology, country, scale, source ID |
| Timing | base year, earliest availability, lead time, lifetime, refurbishment interval |
| Cost | CAPEX, fixed O&M, variable O&M, decommissioning, currency, price year |
| Operation | capacity, utilisation, yield, availability |
| Energy | electricity, hydrogen, gas, coal, steam and other fuel per output |
| Material | ore, scrap, DRI/HBI, naphtha, recycled and biogenic feedstock per output |
| Carbon | direct, indirect, upstream, captured and residual emissions per output |
| Infrastructure | grid, hydrogen, CO₂ transport/storage and logistics requirement |
| Uncertainty | low, central, high; distribution only where justified |
| Quality | project-specific, national benchmark, global benchmark, estimated |

The current output-first implementation is `data/processed/technology_assumptions_mvp.csv`: 27 low/base/high parameter rows across seven route or project archetypes. It preserves the original source price year and marks rows as `screening_only`, direct model proxies, or project-specific validation metrics. The western-Japan ethylene case is an actual multi-company project observation; the electrified-cracker retrofit values are quality-D placeholders and must not be presented as published IEA costs.

The annual cost layer is staged in `data/processed/annual_cost_gap_assumptions_mvp.csv`: 32 audited rows for the four routes currently selected in the facility screen. It separates estimated resource-proxy inputs (analytical life, 3%/5%/7% real discount rate, incremental fixed OPEX and variable-resource gap) from an independent support-stress axis. Facility-level avoided compliance cost, realised green premium and verified support remain `Not_available`/`NA`, not zero. Therefore `outputs/tables/route_annual_cost_gap_inputs_mvp.csv` supports annual resource-gap and stress-adjusted screening, but not a verified incentive-adjusted net-gap claim.

The facility-to-company implementation is `outputs/tables/facility_annual_cost_gap_mvp.csv` and `outputs/tables/company_annual_cost_gap_mvp.csv`. The company table has 12 primary low/base/high rows plus three Mitsui legacy-allocation sensitivity rows. Mitsui's primary view uses the quality-C SHK-to-FY2024 bridge for the four costed facilities; the judgement-based 85% allocation remains a named sensitivity. Emissions coverage is fixed to the base facility boundary rather than allowed to vary with low/high cost cases. Negative resource gaps are retained as savings and receive no artificial support. Verified incentive-adjusted gaps remain `NA`.

Production coverage is published separately in `outputs/tables/company_production_coverage_status_mvp.csv`. Nippon Steel is the first company with a like-for-like reported denominator: its 11 FY2024 works/area observations total 34.88 Mt crude steel versus the separate official company statement of 34.30 Mt. The raw 101.69% reconciliation and 0.58 Mt excess remain visible, while published coverage is capped at 100% because the difference falls within the protocol's pre-specified ±2% tolerance. POSCO, LOTTE Chemical and Mitsui Chemicals remain `NA`, not zero, until a comparable reported production denominator and facility boundary are acquired.

The first project-to-pathway physical screen is `outputs/tables/facility_physical_constraint_mvp.csv`. POSCO's completed Gwangyang EAF has 2.5 Mt/year official capacity and approximately KRW 600bn disclosed investment. Against the allocated 19.02 Mt/year base Gwangyang steel-product proxy, that is 13.15% coverage (12.05%–14.46%) and a 7.61x full-route capacity multiple. The Green Bond project's 80% planned scrap mix implies 2.0 Mt/year scrap demand, or 97.5% of POSCO's reported 2024 purchased scrap use. Capacity, investment and material mix are reported facts; the full-works denominator and resulting ratios are quality-D screening allocations. The existing full-Gwangyang CAPEX and operational-abatement screen is therefore a potential pathway requirement, not a project-backed allocation.

The emissions-pathway v1 anchor table is `data/processed/sector_emissions_pathway_anchors_mvp.csv`. It contains 16 steel/petrochemical × current-policies/net-zero-proxy × 2025/2030/2040/2050 records, each with low/base/high, unit, common reference year, formula, official source ID, quality flag and boundary note. NGFS Phase V supplies scenario definitions; SBTi Steel Guidance and official IEA steel/primary-chemicals pathways supply numerical direction. Interpolations and company scaling are `value_type=estimated`; the table is not a solved GCAM extract, national pathway or company carbon budget.

The calculation outputs are `outputs/tables/facility_gap_to_capital_pathway_mvp.csv`, `outputs/tables/company_emissions_pathway_mvp.csv` and `outputs/tables/company_pathway_uncertainty_mvp.csv`. Facility assignment is capped by physical availability, ordered by decision year and annual resource-gap efficiency, and capped again by the 2050 reduction requirement. The company table keeps current-policy, net-zero-envelope and conditional facility paths separate. It attaches an explicit low/base/high implied-capital estimate to the still-unclosed gap by extrapolating the identified pathway's capital per annual tCO2 and scaling it with the minimum/maximum company model-case intensity; this stays separate from identified projects. The uncertainty table holds the base physical pathway fixed for capital-annualisation and variable-resource one-factor cases, and also reports the existing combined low/base/high model case. All three are quality-D screens; operational reduction is not system abatement.

`outputs/tables/company_capital_flow_bridge_mvp.csv` is the Stage 1 investor bridge. It distinguishes total physical pathway need, route-identified capital, route-missing implied capital, and the identified capital that becomes screening-investable under B0/BH/BL/BHL. It scales the mechanism experiment's contract-coverage and level-support shares to the updated pathway boundary and reports the corresponding operational reduction unlocked. These are model status transitions, not observed investment transactions or company commitments. The table reports residual premium-relevant common-cost exposure but keeps `transition_risk_premium_bps=NA`, because a priced premium requires market factor prices, facility cash-flow sensitivities and observable financing/hurdle data. The interpretation is governed by `docs/decisions/ADR-001-capital-flow-and-risk-premium-boundary.md`.

The primary simplified investor table is `outputs/tables/company_simple_three_step_mvp.csv`, governed by `docs/decisions/ADR-002-simple-three-step-primary-model.md`. Its two sector assumptions are stored in `data/processed/simple_three_step_assumptions.csv` with low/base/high capital intensity, 2025 price basis, source IDs, formula, quality D and `value_type=estimated`. Sector G-CAP equals the GCAM-aligned 2050 required-reduction proxy times the representative capital intensity; company G-CAP is allocated by each company's share of the sector sample's required reduction. The base cost-gap rate and high-minus-base transition-premium proxy scale the fixed-scope annual resource-gap sensitivities to the full allocated path and divide by base G-CAP. The premium proxy is a deterministic cost-stress rate, not WACC, a probability-weighted expectation, a security spread or a market-priced premium; `transition_risk_premium_bps` remains `NA`. BL/BH/BHL closure ratios remain provisional operational-reduction screens, not causal policy effects or system abatement.

The evidence gate for a later priced-premium and FID-timing project is fixed in `docs/decisions/ADR-003-stage-2-risk-premium-pricing-gate.md`. Historical and forward factor-price distributions, covariance, facility cash-flow elasticities, actual contract and policy risk allocation, observed hurdle/spread/FID evidence, and any accounting inputs for stranded-asset analysis are deliberately deferred. Stage 1 retains numeric factor exposure and residual premium relevance but keeps the market price of risk, transition-risk-premium basis points, probability-weighted FID timing, expected NPV and impairment loss as `NA`.

## 9. Macro and conversion data

| Data | Preferred source | Use |
|---|---|---|
| Korea CPI/PPI and GDP deflator | Bank of Korea / KOSIS | KRW price-year conversion |
| Japan CPI/PPI and GDP deflator | Bank of Japan / Statistics Bureau / Cabinet Office | JPY price-year conversion |
| KRW and JPY exchange rates | Bank of Korea and Bank of Japan; IMF validation | real 2025 USD conversion |
| Purchasing-power parities | OECD | non-tradable-cost sensitivity only |
| Grid emissions factors | national environment and energy authorities | historical Scope 2 and hydrogen carbon intensity |
| Forward grid intensity | common GCAM scenario | scenario electricity and hydrogen emissions |

## 10. Canonical processed tables

### `facility_seed.csv`

MVP staging inventory with one row per facility/area. It keeps reported activity and emissions distinct from allocated values, records low/base/high ranges and allocation formulas, and must not be mistaken for the final normalised facility tables below.

### `facility_master.csv`

One row per stable facility or equipment unit, with ownership and boundary fields.

### `facility_activity.csv`

One row per facility-year-product, with capacity, production, utilisation, energy, material, and source fields.

### `facility_emissions.csv`

One row per facility-year-scope-gas, preserving reported and allocated values separately.

### `market_prices.csv`

One row per date-country-market-stage-product, with nominal/real and source metadata.

### `technology_parameters.csv`

One row per country-route-year-parameter-value case.

### `sector_pathways.csv`

One row per model-region-sector-route-year-scenario, with production, energy, emissions, and price linkage.

### `policy_incentives.csv`

One row per country-policy-facility-year, including eligibility, free allocation, support and realised cash treatment.

## 11. Initial data-gap register

| Gap | Effect | Resolution before modelling |
|---|---|---|
| GCAM solved output for Japan and chemicals is not yet confirmed | may break scenario comparability | execute KAIST request; prepare common GCAM reproduction |
| POSCO works-level production and emissions may not be reported on the same boundary | weak facility reconciliation | combine GIR installation data, works production, and energy allocation with residual |
| Nippon Steel works and SHK facility names may not match directly | join and double-count risk | create audited alias table using corporate numbers and addresses |
| LOTTE Chemical 2025 boundary includes selected consolidated companies | domestic parent comparison may be distorted | use parent 5.371 Mt anchor and reconcile complexes separately |
| LOTTE Daesan ownership is changing | inconsistent asset attribution | maintain time-stamped pre-transaction and announced post-transaction cases |
| Mitsui cracker JVs span multiple owners | emissions and CAPEX attribution risk | publish operational-control and equity-share sensitivities |
| clean-hydrogen market history is inadequate | false volatility estimate | bottom-up component model with covariance |
| Japan GX allowance history is short | unstable risk estimate | use observed data only descriptively; use rule-based official bands for stress |
| petrochemical product yields and unit-level energy may be confidential | model allocation uncertainty | use engineering ranges, full-site investment unit, and explicit quality flag |
| closure-related import substitution is uncertain | overstated modelled abatement | report zero, low, and high leakage cases |

## 12. Data acceptance tests

A dataset is accepted only if:

- the publisher and reporting period are known;
- the unit and price year are known;
- the organisational and emissions boundary are known or explicitly flagged;
- revisions can be identified;
- the licence is recorded;
- numeric fields pass type and range checks;
- facility identifiers resolve without silent many-to-many joins;
- totals reconcile or a residual is retained;
- the extraction can be rerun or independently checked.

## 13. Licensing and GitHub publication

Each raw source receives one of three treatments:

1. **Redistributable:** store the file with citation and licence.
2. **Acquirable but restricted:** store acquisition code/instructions, schema, checksum, and citation; exclude raw file from Git.
3. **Manual-access only:** store a source record and reproducible transformation template; never publish the underlying content.

No source is copied into the public repository merely because it can be downloaded.
