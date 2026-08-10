# CAP — Capital Allocation Pathway: Technical Guide

**What this document is.** A technical reader's entry point to the CAP model: what question it
answers, what data it runs on, what it assumes, and what it cannot yet claim. It is written for
someone who intends to interrogate the model, not to be reassured by it.

Every quantitative claim below is either generated from the live repository (blocks marked
*generated*) or carries a pointer to the file that produces it. Where the evidence is weak, this
document says so in the same sentence as the number.

**Companion documents.** [`METHODOLOGY.md`](../METHODOLOGY.md) states the model in equations and
holds the assumption ledger (`A-01` … `A-24`). [`REDESIGN_SPEC.md`](../REDESIGN_SPEC.md) is the
design narrative. [`docs/data_gap_registry.md`](data_gap_registry.md) records what we tried to
collect and where we were blocked. `paper/working_paper.md` is the manuscript.

<!-- GEN:stamp -->
> **Repository state.** Last commit to code, inputs or results: `bdb8b5f` (2026-08-10). Results in this document come from the pipeline run finished `2026-08-10T10:00:24`. Regenerate the generated blocks with `python3 scripts/build_tech_guide.py`.
<!-- /GEN:stamp -->

---

## 1. The question

Steel and petrochemical firms in Korea and Japan have each published a transition plan. Existing
assessment tools (Climate Action 100+ Net Zero Benchmark, the Nature Communications alignment
literature) answer **"is this plan aligned or not?"** The firm that receives that verdict then asks
a different question — **"how much, when, and what does it cost me if prices move?"** — and no
public tool answers it.

CAP answers it in three parts:

1. **Where is the efficient frontier** between expected transition cost and tail risk, across the
   full set of plans a firm could choose?
2. **How far from that frontier is the plan the firm actually disclosed?**
3. **Is that distance a capital shortfall or a risk-management failure?**

The unit of analysis is the **firm's own opportunity set**, not a ranking against peers. A firm is
compared to the best version of itself.

### Falsifiable claims

The model is built so that each of these can be shown false. Current status is stated plainly.

| ID | Claim | Status |
|---|---|---|
| **P1** | A plan that is cheap in expectation is expensive in the tail — the frontier slopes, it does not collapse to a point. | Holds, but **weakly**: only 4 of 32 forced technology schedules survive as non-dominated under the headline risk convention. See §6.3. |
| **P2** | Contract instruments (renewable PPA, fixed-price EPC, CCfD) raise expected cost and lower tail risk. | Not rejected for steel. **In petrochemicals an even hedge covers 0% of the variance** — the instrument set has no hydrogen hedge. That is a gap in the instrument set, not a counterexample. |
| **P3** | Underspending is itself an energy-price risk position, i.e. the disclosed plan has `gap_risk > 0`. | Holds where a disclosed coordinate can be computed. It cannot be computed for 2 of 4 firms — see §6.4, and note the reason is a model boundary, not corporate disclosure failure. |
| **P4** | The ranking by abatement cost and the ranking by financing burden do not coincide. | Holds. This is why metric ⑥ exists. |

---

## 2. Approach

Five stages. The important structural fact is in stage E2/E4: **the optimiser's objective is a
surrogate used to enumerate candidate plans; it is not the cost we report.**

```
data/raw ──prepare_raw──▶ data/prepared ──▶ E1 ──▶ E2 ──▶ E3 ──▶ E4 ──▶ E5 ──▶ out/
                                        constraints  plans  prices  revalue  metrics
```

| Stage | What it does | Output |
|---|---|---|
| **E1** | Extracts firm-level carbon budgets and central price paths. Budgets take their **shape** from the sector scenario and their **level** from the firm's own realised emissions. | `out/e1/` |
| **E2** | Facility-level MILP. Enumerates candidate transition plans by sweeping an ε-constraint over a linear risk surrogate. Decisions: which facility adopts which technology in which year, closure, PPA share, EPC and CCfD. | `out/e2/plan_index.csv`, `out/e2/plans/` |
| **E3** | Calibrates volatility from price history and simulates stochastic price paths (GBM by default) for electricity, hydrogen and construction cost. | `out/e3/` |
| **E4** | **Authoritative revaluation.** Every candidate plan is re-priced along every simulated path, with contracts applied non-linearly. This is where reported cost and risk come from. | `out/e4/` |
| **E5** | Metrics ①–⑥, the efficient frontier, the disclosed-plan gap, variance decomposition, λ tangency, policy wedge. | `out/e5/` |

### Why the surrogate/authoritative split matters

E2's objective linearises risk and contracts, so it orders plans imperfectly. We measured how
imperfectly: the rank correlation between surrogate cost and authoritative P50 is **−0.05 to 0.00 in
steel and 0.20 to 0.73 in petrochemicals**, and the surrogate's cheapest plan is the authoritative
cheapest in **0 of 8** (firm × scenario) bundles.

The consequence is a design rule, not a caveat: E2 is allowed to stop at a 2% relative MIP gap and a
60-second time limit, because proving optimality of the *surrogate* to the last basis point buys
nothing. Each plan's `solve_status` is recorded in `plan_index.csv`, so solve quality is auditable
from the outputs rather than asserted here.

### Metrics

| Metric | Definition |
|---|---|
| ① Capital scale and timing | Σ CAPEX; the year of peak CAPEX |
| ② Expected transition cost | P50 of the incremental NPV vs. the incumbent plan, **net of carbon expenditure** (see A-19), and per tonne abated |
| ③ **TCaR** (Transition Cost at Risk) | P90 − P50 of that same distribution |
| ④ Policy exposure | P50 under NZ15 − P50 under B20 |
| ⑤ Flexibility value | Lower bound on the value of re-optimising per path |
| ⑥ Financing burden | Peak CAPEX ÷ 3-year mean EBITDA; total CAPEX ÷ EBITDA; post-hoc net-debt multiple |

**Efficient frontier** = the Pareto non-dominated set in the (P50, TCaR) plane.
**Frontier gap** = horizontal and vertical distance from the disclosed plan's coordinate to that
frontier. `gap_cost` is how much more the firm could have spent at the same risk; `gap_risk` is how
much tail risk it could have removed at the same cost.

---

## 3. Datasets

Seven input datasets, `D1`–`D7`, mirroring the sheets of the collection workbook. Schemas are
enforced in code at load time (`src/cap/schemas.py`); a missing column or a non-numeric value in a
numeric column stops the run rather than propagating.

<!-- GEN:dataset_inventory -->
| ID | Dataset | Grain | Rows | Years | Domains |
|---|---|---|---|---|---|
| **D1a** | Facility register | one row per production unit | 23 | — | 4 firms, 23 facilities |
| **D1b** | Facility panel | one row per facility-year | 69 | 2022–2024 | 23 facilities |
| **D2a** | Scenario carbon budgets | scenario x region x sector x year | 48 | 2025–2050 | 2 scenarios |
| **D2b** | Scenario price paths | scenario x region x variable x year | 224 | 2025–2050 | 6 variables, 2 scenarios |
| **D3** | Technology options | one row per abatement measure | 13 | — | 13 techs |
| **D4** | Price history | one row per series-date | 99 | — | 18 series |
| **D5** | Policy support | one row per instrument-window | 7 | — | 4 instruments |
| **D6** | Company financials | one row per company-year | 22 | 2020–2025 | 4 firms |
| **D7** | Disclosed plan | one row per commitment | 12 | 2023–2050 | 4 firms, 7 facilities, 4 techs |

9 files across 7 dataset families, 85 schema-required columns in total. Extra columns are permitted and preserved; required ones are not optional.
<!-- /GEN:dataset_inventory -->

The field tables below mark each column **[req]** if `SCHEMAS` in `src/cap/schemas.py` requires
it and **[extra]** if it is an additional column the loader preserves and some stage reads. An
extra column can disappear without the schema check noticing, so the ones that carry model
behaviour are called out where they appear.

### 3.0 Controlled vocabularies

<!-- GEN:vocab -->
| Field | Distinct | Values (count) |
|---|---|---|
| `D1a.sector` | 2 | `steel` (19), `petchem` (4) |
| `D1a.unit_type` | 4 | `BF` (17), `NCC` (4), `FINEX` (1), `EAF` (1) |
| `D1a.capacity_unit` | 4 | `t용선/yr (내용적 추정)` (16), `t에틸렌/yr` (4), `t용선/yr` (2), `t조강/yr` (1) |
| `D1a.status` | 6 | `가동` (18), `휴지예정(전기로 전환)` (1), `가동(여천NCC 통합법인 이관 예정)` (1), `가동중단 계획(롯데대산석화 재편)` (1), `가동(2027.7 지바 집약 거점)` (1), `가동(2030년도 서일본 집약 거점)` (1) |
| `D2a.scenario` | 2 | `NZ15` (24), `B20` (24) |
| `D2a.region` | 2 | `Korea` (24), `Japan` (24) |
| `D2b.variable` | 6 | `re_price` (104), `elec_price` (24), `h2_price` (24), `co2_price` (24), `coal_price` (24), `gas_price` (24) |
| `D2b.unit` | 4 | `KRW/MWh` (128), `KRW/t` (48), `KRW/kg` (24), `KRW/tCO2` (24) |
| `D3.applies_to_unit` | 4 | `NCC` (6), `BF` (5), `NONE` (1), `FINEX` (1) |
| `D3.retrofit` | 2 | `1` (9), `0` (4) |
| `D5.support_scenario` | 1 | `current` (7) |
| `D5.instrument` | 4 | `auction_share_power` (2), `price_cap` (2), `price_floor` (2), `auction_share` (1) |
| `D7.item_type` | 3 | `tech_commit` (7), `target` (3), `timing` (2) |
| `D7.resolution` | 2 | `high` (7), `mid` (5) |

These are the values that **occur**, not the values the schema permits — `load_input` checks that a column exists and is numeric where required, never what it contains. Three of these fields are documentation rather than input and no stage branches on them: `D1a.status`, `D1a.capacity_unit` and `D7.resolution`. Nor is any `D5` row read — see §3.6. The rest decide behaviour.
<!-- /GEN:vocab -->

### 3.1 D1a — facility register (static)

One row per production unit. This is the model's spine: every technology decision is attached to a
row here.

| Field | Definition | Unit | Notes |
|---|---|---|---|
| `facility_id` **[req]** | Stable key, `COMPANY_SITE_UNIT` (e.g. `NSC_OIT_BF1`) | — | Never reused |
| `company_id` **[req]** | `POSCO`, `NSC`, `LOTTE`, `MCI` | — | |
| `sector` **[req]** | `steel` or `petchem` | — | Determines which technology set applies |
| `site` **[req]** | Works / plant name | — | Site is the grain at which Japanese emissions are disclosed |
| `unit_type` **[req]** | Process type — values in §3.0 | — | Matched against `D3.applies_to_unit`, so it governs technology applicability (A-10) |
| `unit_name` **[req]** | Unit label as published, free text | — | Read by no stage; it is what makes a row checkable against its source |
| `capacity` **[req]** | Nameplate annual capacity | **see `capacity_unit`** | Published capacity where available; otherwise inner volume × 913 t/m³·yr (**A-01**) |
| `capacity_unit` **[req]** | The basis `capacity` is stated on | — | **Three bases occur in this one column** — hot metal, crude steel, ethylene (§3.0). See the caution below |
| `commissioning_year` **[req]** | First operation | year | |
| `last_reline_year` **[req]** | Most recent campaign renewal | year | Blast furnaces only |
| `reinvest_cycle_yr` **[req]** | Campaign length | yr | Sets the reinvestment window |
| `next_reinvest_year` **[req]** | Next campaign anchor | year | Early conversion before this anchor writes off residual book value (**A-13**) |
| `status` **[req]** | Operating state, free Korean text as published (§3.0) | — | Not parsed and not branched on: **no row is excluded on `status`**, including the two units whose text says closure or transfer is planned |
| `source_id` **[req]** | Foreign key into `source_register` | — | Mandatory |
| `incumbent_capex_unit` **[extra]** | Replacement cost of the incumbent asset | thousand KRW/t | Used only for the stranding write-off. One value per `unit_type`, not per asset: BF 200, EAF 250, FINEX 300, NCC 150. The BF figure is the one A-13 fails external validation on, at 4.2× |
| `margin_kthou_t` **[extra]** | Operating margin per tonne of output | thousand KRW/t | Closure forfeits it (**A-04**). Also one value per sector, not per asset: steel 70, petchem 290. E2 enables the retirement decision **only if every facility of that firm has a positive value** — one blank switches closure off for the whole firm rather than making closure free. All 23 rows are currently populated, so retirement is live for all four firms |

**Unit caution.** `capacity` is not commensurate across rows: a blast furnace is stated in tonnes of
hot metal, an NCC in tonnes of ethylene, and one unit in tonnes of crude steel. Nothing in the model
converts between them — `D3` costs and intensities are applied per tonne of whatever basis the row
carries, so a technology's `capex_unit` is only comparable within a `unit_type`.

**Grain caution.** Emissions are disclosed by *site* in Japan and only by *legal entity* in Korea,
while decisions are made per *unit*. That mismatch is where the model's largest assumption lives —
see A-02 in §4.

### 3.2 D1b — facility panel (time-varying)

One row per facility-year. Production and energy define the incumbent baseline that every plan is
measured against.

All nine columns are schema-required.

| Field | Definition | Unit |
|---|---|---|
| `facility_id`, `year` | Composite key | — |
| `production` | Physical output — on the same basis as `D1a.capacity_unit` for that facility | t/yr |
| `emissions_s1` | Scope 1 | tCO₂/yr |
| `emissions_s2` | Scope 2 (purchased electricity) | tCO₂/yr |
| `energy_coal` | Coal / coke input | t/yr |
| `energy_gas` | Gas input | t/yr |
| `energy_elec` | Electricity input | MWh/yr |
| `energy_naphtha` | Naphtha feedstock | t/yr |
| `source_id` | Foreign key into `source_register` | — |

Derived quantities: incumbent output `Q_f` is the 3-year mean of `production`; incumbent emission
intensity `e_f = emissions_s1 / Q_f`; energy intensities likewise. The panel holds exactly
2022–2024, so "3-year mean" is the whole panel, not a trailing window — a fourth year would change
the baseline of every result.

**Known hole:** `energy_naphtha` is empty for all 69 rows — the column is blank, not zero.
Petrochemical feedstock exposure is therefore understated. Because margin is taken on an
operating-profit basis there is no double-count, but the naphtha price channel is absent.

**Emission boundary:** Scope 1 only (**A-21**). `emissions_s2` is non-zero in 63 of 69 rows and is
preserved but never charged, because budgets are anchored to the firm's own base and the choice is
level-neutral.

### 3.3 D2a / D2b — scenarios

`D2a` carries sector carbon budgets, `D2b` carries price paths. Both are stated on 5-year anchors
(2025, 2030 … 2050) that E1 interpolates annually — **with one exception**: `re_price` is already
annual, and flat. It is a single procurement price held constant to 2050 (Korea 175,000 KRW/MWh),
so the renewable-PPA channel has a level but no path, while every other price does.

| Field | Definition |
|---|---|
| `scenario` | `NZ15` (1.5 °C-consistent) or `B20` (below 2 °C) |
| `region` | `Korea` or `Japan` — Korean budgets are direct-emission based and on calendar years, Japanese include purchased power and are on fiscal years |
| `sector` (D2a) | `steel` / `petchem` |
| `carbon_budget` (D2a) | Sector emissions allowance for that year |
| `gcam_version` (D2a) | Provenance tag of the pathway — see the caveat below |
| `variable` (D2b) | `elec_price`, `re_price`, `h2_price`, `coal_price`, `gas_price`, `co2_price` |
| `value`, `unit` (D2b) | The price and its unit (`KRW/MWh`, `KRW/kg`, `KRW/t`, `KRW/tCO₂`) |
| `source_id` | Foreign key into `source_register`, per row |

Only the **ratio** to the base year is used (**A-06**), so the Korea/Japan boundary difference
survives only in path shape, not level. Electricity is deliberately split in two: incumbent
consumption is priced at grid tariff, transition technologies at a renewable PPA price (`re_price`).

**Provenance caveat — these are not GCAM output.** They are provisional in-house pathways built to
exercise the structure until the GCAM-KAIST solved output arrives; the `gcam_version` column says so
in the data (`EST_v0 (비GCAM 잠정)`). The construction is documented anchor by anchor in
[`data/manifests/estimation_notes_D2_v0.md`](../data/manifests/estimation_notes_D2_v0.md): budgets
are piecewise-linear between government targets, carbon prices interpolate central-bank and IEA
anchors, electricity comes from an LCOE study rather than a wholesale market. Provenance is
**mixed at row level**, not uniform — rows carrying an anchor keep the real `source_id`
(`IEA_GECM_DOC_2025`, `MOTIE_H2_PLAN_2021`, `KETS_P4_CONFIRM_2025` …) and only the interpolated
rows are labelled `EST_D2A_V0` / `EST_D2B_V0`, which are the rows to be replaced wholesale on
receipt.

Three consequences a reader should carry:

- **`coal_price` is thermal coal**, not the coking coal a blast furnace consumes. A coking-coal
  scenario path has not been obtained (§6.5).
- **Korean `h2_price` for 2025 is blank** — no verified current price was found — so the hydrogen
  path starts from the 2030 target anchor.
- The central paths do not state whether they are means or medians, which is the whole reason A-24
  exists (§4). Series definitions are also mixed across scenarios: Korean NZ15 carbon price is a
  central-bank shadow price, Japanese NZ15 is IEA NZE, B20 is IEA STEPS.

### 3.4 D3 — technology options

One row per abatement measure available to a sector, 13 rows in total.

**Adoption is all-or-nothing per facility.** There is no coverage fraction: E2's decision variable
is binary over (facility, technology, adoption year), and at most one technology or one closure may
be taken per facility over the whole horizon. Partial abatement is therefore expressed in two other
places — in `emission_factor`, which is the post-measure intensity rather than a reduction rate, and
in `retrofit`, which decides whether the measure's energy intensities are **added to** the
incumbent process or **replace** it.

| Field | Definition | Unit |
|---|---|---|
| `tech_id` **[req]** | e.g. `steel_h2dri`, `petchem_ecracker` | — |
| `sector` **[req]** | `steel` (7 rows) or `petchem` (6) — the measure is only offered to firms in that sector | — |
| `applies_to_unit` **[req]** | Which single `unit_type` it can be applied to; `NONE` marks a greenfield measure applicable to no existing unit (`steel_eaf`) | — |
| `capex_unit` **[req]** | Unit capital cost | thousand KRW / t capacity |
| `opex_fixed` / `opex_var` **[req]** | Fixed / variable operating cost — fixed is charged on `capacity`, variable on `production` | thousand KRW per t capacity·yr / per t |
| `elec_intensity` **[req]** | Electricity requirement, priced at `re_price` | MWh/t |
| `h2_intensity` **[req]** | Hydrogen requirement | kg/t |
| `emission_factor` **[req]** | Post-conversion intensity, **not** a reduction rate | tCO₂/t |
| `avail_year` **[req]** | Earliest adoption year | year |
| `build_years` **[req]** | Construction duration — CAPEX is spread evenly across it (**A-18**) | yr |
| `lifetime` **[req]** | Economic life | yr |
| `capex_uncertainty` **[req]** | Relative CAPEX dispersion, used as a **relative** multiplier only (**A-22**) | **percent, 30–60 across our set** — not a fraction |
| `source_id` **[req]** | Foreign key into `source_register` | — |
| `retrofit` **[extra]** | 1 = keeps the incumbent process running and adds the measure's intensities on top; 0 = swaps the process energy out. 9 of 13 rows are retrofits | 0/1 |

`D3b_tech_bands.csv` carries `[value_low, value_high]` evidence bands per (tech, field) from the
literature. The bands are **asymmetric**, and at least one D3 point value sits outside its own band —
that is deliberate and tested, because it is the evidence that the central values were not quietly
snapped to the band.

**Hydrogen is an externally procured commodity**, not an electrolyser built inside the model
(**A-05**). The earlier structural formulation was discarded.

### 3.5 D4 — price history

Five columns, all required: `date`, `series_id`, `value`, `unit`, `source_id` — one observation per
row. Used for one purpose: estimating annualised volatility per stochastic factor. This is the
thinnest dataset in the project and it directly sets the level of metric ③. Note that `unit` is
free text carrying the definitional caveat for the series (basis, coverage, whether a value is
estimated), so it is worth reading in the table below rather than skipping as a label.

<!-- GEN:price_series -->
| Series | Obs | From | To | Volatility | Unit |
|---|---|---|---|---|---|
| `smp_monthly` | 19 | 2025-01 | 2026-07 | estimated | 원/kWh (육지 월별) |
| `usdkrw` | 11 | 2015-01 | 2025-01 | estimated | 원/USD (연평균) |
| `smp_krw_mwh` | 11 | 2015-01 | 2025-01 | estimated | 원/kWh (육지, 연평균) |
| `indus_tariff` | 10 | 2015-01 | 2024-01 | estimated | 원/kWh (산업용 전체 평균판매단가, 연평균) |
| `kau_krw` | 9 | 2015-01 | 2023-01 | estimated | 원/tCO2 (연평균) |
| `ethylene_naphtha_spread` | 7 | 2019-12 | 2025-12 | estimated | USD/t (CFR NEA - C+F Japan; 19-21 추정) |
| `jepx_spot` | 7 | 2019-03 | 2025-03 | estimated | JPY/kWh (FY 시스템프라이스) |
| `steel_margin_krw_t` | 7 | 2019-12 | 2025-12 | estimated | 원/t (포스코 별도 영업이익/조강톤, 추정 혼재) |
| `cpi` | 4 | 2020-01 | 2024-01 | **prior** | 지수(2020=100, 연평균) |
| `constr_cost_idx` | 3 | 2020-01 | 2025-01 | **prior** | 지수(2020=100, 11월값) |
| `lng_import` | 2 | 2022-01 | 2023-01 | **prior** | USD/t (국가평균 도입단가, 연평균) |
| `electrolyzer_capex` | 2 | 2022-01 | 2023-01 | **prior** | KRW/kW |
| `coal_import` | 2 | 2022-01 | 2023-01 | **prior** | USD/t (유연탄 전체 — 원료탄 아님) |
| `h2_contract_krw_kg` | 1 | 2024-12 | 2024-12 | **prior** | KRW/kg (한국 청정수소 현 공급비 ~1만원) |
| `h2_target_krw_kg` | 1 | 2030-12 | 2030-12 | **prior** | KRW/kg (수소 로드맵 목표) |
| `re_ppa_jp_krw_mwh` | 1 | 2024-12 | 2024-12 | **prior** | KRW/MWh (일본 물리 PPA HV 총비용 21.5JPY×9.2) |
| `re_ppa_krw_mwh` | 1 | 2026-01 | 2026-01 | **prior** | KRW/MWh (한국 태양광 PPA 170원대 중반) |
| `re_ppa_wind_krw_mwh` | 1 | 2026-01 | 2026-01 | **prior** | KRW/MWh (한국 육상풍력 PPA 180원 중반) |

**18 series, 99 observations total. 10 of 18 series have fewer than 6 observations** and therefore contribute a prior rather than an estimate. This is the binding constraint on metric ③.
<!-- /GEN:price_series -->

Any factor with fewer than 6 observations falls back to a prior volatility, and the run **warns
every time** (**A-17**). Currently hydrogen uses a prior of 0.25 and construction cost 0.06, with an
identity correlation matrix.

### 3.6 D5 — policy support

Instruments that change the economics: auction share, price collar, capital subsidy, CCfD. Seven
rows.

| Field | Definition |
|---|---|
| `support_scenario` | Which support world the row belongs to. **Every row in the file is `current`** — `none` is the absence of rows, not a value: `support_params` returns an empty object without reading the file |
| `instrument` | Instrument key — values in §3.0. `subsidy_capex` and `ccfd` are the two the code reads and neither occurs |
| `tech_id` | Which technology the instrument attaches to; `all` for economy-wide instruments |
| `param_type`, `value`, `unit` | The parameter and its value; `param_type` is a Korean label and is not parsed |
| `valid_from`, `valid_to` | Applicability window; a blank end extends to the horizon |
| `source_id` | Foreign key into `source_register` |

**The `support` axis is currently empty of information, and the manuscript says so.** The only
instruments `plancost.support_params` reads are `subsidy_capex` and `ccfd`, and D5 contains no rows
of either type — the seven rows present are K-ETS auction shares and a Japanese price collar, and
no stage reads them; the auction ramp the model actually applies is the one in `config.yaml` (§5).
So `current` returns the same object as `none`. The
results table has a column where there is no signal. A test asserts this correspondence, so the day
a subsidy row arrives the test fails and the prose must be corrected with it.

### 3.7 D6 — company financials

One row per company-year: revenue, EBITDA, total CAPEX, total and net debt, interest expense, cash,
plus `source_id`. Feeds metric ⑥ only. Coverage is 2020–2025 for POSCO and Nippon Steel, 2021–2025
for LOTTE, 2020–2024 for Mitsui.

Reference earnings for ⑥ is the **3-year mean EBITDA** (**A-20**) — petrochemicals are at a cyclical
trough and a single-year denominator flips the conclusion. Firms with non-positive reference earnings
get **no ratio and a stated verdict** rather than a misleading number. The post-hoc net-debt
multiple is an **upper bound under full debt financing**, not a forecast of financing mix.

Three definitional caveats sit inside this table, and all three are live:

- **The column called `ebitda` is not EBITDA for every firm.** For Nippon Steel it is 営業利益
  (operating profit) and for Mitsui コア営業利益 (core operating profit) — depreciation is not added
  back. Metric ⑥ therefore understates Japanese capacity to fund relative to Korean.
- **Reporting boundaries differ.** POSCO is 별도 (parent-only), LOTTE consolidated, and the two
  Japanese firms consolidated on an April–March fiscal year. Nippon Steel's FY2025 additionally
  consolidates U.S. Steel, which breaks the series rather than continuing it.
- **The currency unit is mixed and nothing converts it.** Korean rows are in billion KRW and
  Japanese rows in 億円 as published, and no stage applies an exchange rate — `e5_metrics` reads the
  column straight into `ebitda_ref_bnkrw`. At the project's own rate (9.2 KRW/JPY) 1 億円 is 0.92
  billion KRW, so Japanese denominators in ⑥ are overstated by about 8% and the ratios understated
  by the same. It is a small error and a real one; it is registered in
  [`docs/data_gap_registry.md`](data_gap_registry.md) rather than silently carried.

### 3.8 D7 — disclosed plan

The firm's own published commitments, decomposed so they can be forced into the MILP.

| Field | Definition |
|---|---|
| `company_id` | Who committed |
| `item_type` | `target` (3 rows), `tech_commit` (7), `timing` (2) |
| `facility_id`, `tech_id`, `year_stated` | What was committed, where, when. `facility_id` and `tech_id` are blank where the disclosure names neither |
| `coverage_pct` | Share of the unit covered. **Blank in all 12 rows** — no firm quantifies it, so no partial commitment can be forced |
| `resolution` | How enforceable the statement is, as judged when the row was written. Two values occur, `high` (7) and `mid` (5). **Read by no stage** — it is an interpretive grade for the skip report, not a filter |
| `quote` | The disclosure text the row was derived from, verbatim |
| `source_id` | Foreign key into `source_register` |

What actually becomes a fixed decision is narrower than the table suggests: a row is enforced only
if `item_type == tech_commit`, its `facility_id` is one of that firm's units, `year_stated` is
present, its `tech_id` exists in D3, and that technology applies to that unit's type. Start year is
back-computed as `year_stated − build_years` and clamped into the feasible range, so a commitment
that predates the technology's availability is enforced at the earliest feasible year rather than
disappearing. `target` and `timing` rows are context, not constraints.

**If no commitment is enforceable, we do not produce a disclosed coordinate** (**A-16**). An empty
set of fixed decisions would just be a second unconstrained optimisation, and the resulting "gap"
would be fabricated. Skips and their reasons are written to `out/e2/disclosed_skipped.csv`.

### 3.9 Provenance and licensing

Every data row carries a `source_id` into `source_register.csv`, which records publisher, title,
URL/DOI, publication and retrieval dates, reporting period, licence, and whether the source is
redistributable. Citations in prose use `source_id`; URLs are never written inline.

`data/raw/` is not committed (licence-restricted sources). The redistributable subset plus derived
results ships in `data/package/` with a `manifest.json` carrying SHA256 per file, a merged data
dictionary, and the configuration the results were produced under. Facility-level results are
confidential by design and are excluded from the package.

---

## 4. Key assumptions

The full ledger with equations lives in [`METHODOLOGY.md`](../METHODOLOGY.md) §8. Reproduced here are
the assumptions that **move the conclusions**, ordered by how much they move them.

### 4.1 The ones that decide the answer

| ID | Assumption | Why it is assumed | Impact | How it is checked |
|---|---|---|---|---|
| **A-02** | Facility emissions = firm-reported total, distributed by capacity × route emission factor (steel); bottom-up (petchem) | Per-facility measured emissions are not publicly issued in Korea | **Largest single parameter — rank 1 in sensitivity screening, evidence tier T5.** Moves abatement cost by up to 86% | Back-test; for Japan, replaced by T1 site disclosure (EEGS) — see §5.1 |
| **A-17** | Factors with too few observations use prior volatility (h₂ 0.25, capex 0.06, identity correlation) | D4 has 1–19 observations per series | **Large — sets the level of metric ③.** Mean-reversion instead of GBM cuts TCaR by 41–48% | `docs/process_alternative.md`; D4 is too short to discriminate statistically, and we say so rather than reporting a test we have no power for |
| **A-24** | Price shocks normalised so **E[shock] = 1** | D2b does not state whether its central path is a mean or a median | **Large — petrochemical metric ② moves +71–73% under the median convention.** Log-normal skew drags the median down: at σ=0.25 over 25 years the 2050 median is 0.47× the central path | `docs/process_alternative.md` §3 |
| **A-07** | Auction share follows the confirmed K-ETS Phase 4 allocation plan (15% non-power, 2026–2030), then an assumed ramp to 100% by 2050 | Post-2030 allocation is not decided | **Large.** At 100% auctioning, carbon cost reaches ~10× product margin and full closure becomes "optimal" | `test_auction_share_follows_confirmed_allocation_plan`; the `carbon_fast` bundle measures it — **+19.7% on ② and +61.5% on ③, the largest of any axis tested** |
| **A-05** | Hydrogen is procured externally at a market price | Design decision (spec §5-1); the electrolyser formulation was discarded | Large — 30–42% of TCaR | `test_hydrogen_priced_from_data_not_structural_fallback` |
| **A-19** | Metric ② is a **resource cost**: carbon expenditure delta is subtracted | If carbon avoidance dominates, "transition is free" and the capital-allocation question disappears | Large on ②, none on ③ | `test_resource_cost_is_total_minus_carbon` |
| **A-13** | Stranding cost = residual straight-line book value of the campaign asset; ±1 year grace around a relining anchor | Spec §2 | Large on investment timing | **Fails external validation: the injected blast-furnace replacement cost is 4.2× a disclosed actual (Kobe, 47 thousand KRW/t).** Over-penalises early conversion. The `reline_cheap` bundle bounds the effect |

### 4.2 Structural choices that are visible, not hidden

| ID | Assumption | Note |
|---|---|---|
| **A-06** | Firm budget = own base emissions × sector path ratio | Level from the firm, shape from the scenario. No inter-firm allocation of abatement — who abates when is E2's decision |
| **A-10** | Blast-furnace conversion is hydrogen-DRI only; CCUS and efficiency are retrofits; wholesale BF→EAF conversion is disallowed | User-confirmed scope decision. **This is why POSCO has no disclosed coordinate** — its Gwangyang EAF cannot be represented (§6.4) |
| **A-09** | At most 20% of firm production may be retired early | Demand / market-position proxy. Without it, NZ15 carbon prices dwarf margins and full closure wins |
| **A-11** | Budget-violation penalty floored at 300 thousand KRW/tCO₂ | Without a floor the optimiser buys violations instead of transitions — demonstrated in the first run |
| **A-14** | E2 is an ordering surrogate at a 2% relative gap | Cheap because E4 is authoritative — **but see §2: had we trusted the surrogate we would have been wrong in 8 of 8 bundles** |
| **A-15** | Hedges enter the surrogate as a plan-independent linear deduction at the median | Avoids bilinearity. Conservative; E4 applies contracts non-linearly |
| **A-18** | CAPEX spread evenly across `build_years` | Charging it at adoption overstated peak funding need by up to `build_years`× |
| **A-01** | Capacity = published, else inner volume × 913 t/m³·yr | Sensitivity rank 8. A 12% discrepancy against the independent implementation is open (workstream G3) |
| **A-21** | Emission boundary = Scope 1 | Level-neutral given A-06; Scope 2 preserved but not charged |

### 4.3 Evidence grading

Every parameter carries an evidence tier. T5 (our own estimate) additionally requires a
`[low, high]` range.

| Tier | Definition |
|---|---|
| **T1** | Regulatory, verified, or statutory disclosure (statutory GHG filings, audited accounts, official gazette) |
| **T2** | Company primary disclosure (IR databook, press release, sustainability report) |
| **T3** | Peer-reviewed or public-institution (journal articles, IEA, IEAGHG, DIW, NEDO) |
| **T4** | Trade press, consultancy, secondary citation |
| **T5** | Our own model estimate — **requires a derivation and a `[low, central, high]` range** |

<!-- GEN:tier_distribution -->
| Group | T1 | T2 | T3 | T4 | T5 | Total |
|---|---|---|---|---|---|---|
| `budget` | 0 | 0 | 0 | 0 | 8 | 8 |
| `cost_evidence` | 0 | 7 | 0 | 0 | 0 | 7 |
| `facility` | 0 | 70 | 0 | 45 | 68 | 183 |
| `model_choice` | 0 | 0 | 0 | 0 | 8 | 8 |
| `policy_assumption` | 2 | 0 | 0 | 0 | 4 | 6 |
| `prep_injection` | 0 | 0 | 0 | 0 | 4 | 4 |
| `price_path` | 1 | 0 | 1 | 4 | 18 | 24 |
| `price_process` | 0 | 0 | 0 | 0 | 9 | 9 |
| `technology` | 0 | 60 | 40 | 30 | 36 | 166 |
| **415 parameters** | 3 | 137 | 41 | 79 | 155 | 415 |

T5 accounts for 155 of 415 parameters; 139 of those are still flagged as lacking a range. Models: FIN 295, EFF 120.
<!-- /GEN:tier_distribution -->

The distribution is itself a finding: **the parameters with the best sources are the ones without
ranges.** A T2 company disclosure gives a point value and no uncertainty, while a T5 estimate is
required to carry a band — so evidence quality and stated uncertainty run in opposite directions.

---

## 5. Configuration

<!-- GEN:config -->
| Setting | Value | Note |
|---|---|---|
| Horizon | 2025–2050 | annual steps |
| Scenarios | NZ15, B20 | D2 pathways |
| Support scenarios | none, current | `none` = gross |
| Discount rate | 5.0% real | sensitivity 3.5%, 6.5% |
| Monte Carlo paths | 10,000 | convergence checked at 2,000 |
| Flexibility subsample | 1,500 | metric ⑤ re-optimisation |
| Price process | gbm | alternative: mean reversion, half-life 10 yr |
| Shock normalisation | mean | A-24 — see §4.1 |
| Frontier grid | 10 points | ε-constraint sweep |
| MIP relative gap | 2% | surrogate objective (A-14) |
| Solver time limit | 60 s | feasible solutions accepted |
| Solver threads | 1 | **1 is a reproducibility requirement**, not a performance setting |
| Early-retirement cap | 20% of production | A-09 |
| Violation price floor | 300 thousand KRW/tCO₂ | A-11 |
| Seed | 20260806 | pinned in `config.yaml` |

**Auction share ramp (A-07):** 2025 10% → 2030 15% → 2035 30% → 2040 50% → 2045 75% → 2050 100%. Anchored on the confirmed K-ETS Phase 4 non-power share; everything after 2030 is an assumption.

**Contract premia:** renewable PPA +8% over the central electricity price, fixed-price EPC +10% over central CAPEX, CCfD fee 3% of covered carbon cost.
<!-- /GEN:config -->

---

## 6. Current results and what they rest on

<!-- GEN:headline -->
| Firm | ② Abatement cost (thousand KRW/tCO₂) | ③ TCaR (bn KRW) | ① Total CAPEX (bn KRW) | Peak CAPEX year |
|---|---|---|---|---|
| POSCO | 115.0 | 26,753 | 20,565 | 2041 |
| Nippon Steel | 155.6 | 32,961 | 32,617 | 2035 |
| Mitsui Chemicals | 241.7 | 864 | 69 | 2041 |
| LOTTE Chemical | 279.2 | 2,242 | 158 | 2041 |

Scenario NZ15, `support=none`. Read TCaR to two significant figures (§6.1).

A frontier gap is computed for **2 of 4 firms**; §6.4 explains why the other two are not a disclosure failure. 12 assumption bundles have been evaluated.
<!-- /GEN:headline -->

### 6.1 How precisely these should be read

Five-seed repetition of E3–E5 gives the sampling error:

| Metric | Coefficient of variation | Read to |
|---|---|---|
| ② P50 / abatement cost | 0.3–0.8% | The digits as printed |
| ③ TCaR | 1.1–1.8% | **Two significant figures** — "33 trillion KRW", not "32,961 bn" |
| ⑤ Flexibility | 3–9% | **One significant figure**; it is a lower bound, so more simulation buys nothing |

Seed stability is precision, not accuracy. Every seed uses the same prior volatility (A-17); if that
prior is wrong, all seeds are consistently wrong.

### 6.2 What is robust and what is not

**Ranking is robust.** It survives discount rates of 3.5/5/6.5%, GBM vs. mean reversion, both shock
normalisations, and all scenario bundles tested — zero rank reversals.

**Levels are not.** TCaR moves 41–48% on the price-process choice alone, and petrochemical ② moves
71–73% on the shock-normalisation choice. Any use of these numbers as absolute magnitudes needs the
sensitivity annexe alongside.

### 6.3 The frontier is thinner than it looks

Forcing technology schedules with an ε-constraint on cumulative emissions — an axis contracts cannot
buy — shows that **all 32 caps are feasible and every one yields a new schedule**: the degrees of
freedom exist. But under the headline risk convention only **4** remain non-dominated in
(P50, TCaR).

The mechanism is that abatement moves exposure *out of* carbon, which is deterministic, and *into*
electricity, hydrogen and construction cost, which are stochastic. So **abating increases TCaR**.
Under the alternative convention where carbon price is itself stochastic, 25 of the same 32 become
non-dominated and the technology axis returns in 7 of 8 bundles. The frontier's thinness is a
property of the risk convention, not of the candidate generator.

Separately, of 51 enumerated plans only **43** are distinct under authoritative evaluation. In each
bundle exactly one pair differs only in whether a CCfD is signed, and under `support=none` the CCfD
strike is undefined — so the two plans are numerically identical downstream while the surrogate
charges a premium and prices them apart.

### 6.4 Where the gap cannot be computed, and why

Two of four firms have no disclosed coordinate, and the reason is **our model boundary, not their
disclosure quality**:

- **POSCO** discloses at `high` resolution. Its Gwangyang EAF is nevertheless unrepresentable because
  A-10 disallows wholesale BF→EAF conversion.
- **LOTTE** commits to CCUS, which is excluded from D3.

Earlier iterations of this project recorded these as "resolution too low". That was wrong and is
corrected here and in the board memo. Reasons are attached per row in
`out/e2/disclosed_skipped.csv`.

### 6.5 Open data gaps

| Gap | Status |
|---|---|
| Korean per-site emissions | **Blocked.** Statutory filings contain site-level emissions but are not publicly issued; the public data portal and the KIER analysis both stop at the legal entity. Untried alternative: formal information-disclosure request |
| Japanese per-site emissions | **Closed at T1.** EEGS discloses by site from FY2021. Nippon Steel 27 sites and Mitsui Chemicals 8 sites obtained for FY2023; site totals reconcile to −2.6% and −1.9% against firm disclosure |
| Monthly price series | Partly closed. Volatility still rests on 1–19 annual observations for most factors |
| Petrochemical naphtha feedstock | Open — `D1b.energy_naphtha` is 0/69 |
| Petrochemical production volumes | **Not disclosed by either firm.** Emission intensity level is confirmed by one primary source (Mitsui's Mizushima closure implies 1.020 tCO₂/t-ethylene against our 0.95, −6.9%) but the utilisation time series cannot be checked |

Full record with attempted access paths: [`docs/data_gap_registry.md`](data_gap_registry.md).

---

## 7. Verification

Three layers, all runnable.

**Internal consistency.** Accounting identities (total = sum of components), mass and energy balance
(output × intensity = energy consumed), emission consistency (EF × output = emissions), unit
round-trips. Plus an allocation identity — facility emissions must sum to the firm's disclosed total
in every year — which was added after a fallback branch silently zeroed one firm's emissions and
nothing caught it until the last stage.

**External comparison.** Model CAPEX against disclosed actual project costs (Gwangyang EAF, Nippon
Steel Yawata, JFE Kurashiki); metric ② against published LCOA/MAC ranges (Vogl, Agora, IEA ISTR,
Material Economics, MPP). This is the layer that found A-13's 4.2× over-estimate.

**Back-test.** 2020–2024 actual production and energy prices fed in, and the reproduction error on
actual emissions and energy cost reported.

**Independent reimplementation.** A second model (`cap-efficient/`, stdlib only) computes overlapping
quantities from the same data through different code. Differences are decomposed by structural cause
— boundary definition, margin treatment, carbon treatment, facility resolution. The two trees are
forbidden from importing each other, enforced by `tests/test_independence.py`; without that, the
cross-check would be circular.

### One command

```bash
.venv/bin/python scripts/gate.py
```

Eight checks: test suite, implementation independence, data audit (no synthetic leakage, no unused or
unsourced columns), MCP `tools/list`, CLI wiring, output freshness against inputs **and model code**,
run provenance against `config.yaml`, and git state. Non-zero exit on any hard failure.

The freshness and provenance checks exist because of specific failures: outputs four days older than
the code they were attributed to, and a results ledger validated against a reduced-simulation run.
Both passed every hand check before they were automated.

### Reproducing from scratch

```bash
.venv/bin/python scripts/prepare_raw.py     # data/raw -> data/prepared, every conversion logged
.venv/bin/python scripts/audit_data.py      # synthetic / unused / unsourced gate
.venv/bin/python -m cap all                 # E1 -> render (~20 min, MILP)
.venv/bin/python scripts/run_scenarios.py   # assumption bundles
.venv/bin/python -m pytest tests/ -q
```

Seed is pinned in `config.yaml`. `milp.solver_threads: 1` is a **reproducibility requirement, not a
performance setting** — parallel CBC changes which of several tied optima is returned within the 2%
gap, and two runs of the same commit and seed once produced different plan counts.

### Programmatic access

An MCP server exposes the results for query: firm list, plan metrics, affordability, frontier,
disclosed gap, parameter lookup with tier and source, sensitivity ranking, data audit, validation
summary, package manifest. Facility-level detail is refused by default. See
[`docs/mcp_server.md`](mcp_server.md).

---

## 8. What we do not claim

1. Facility-level absolute values should be treated as **ordering information only** until per-site
   measured emissions are obtained. For Japan they now are; for Korea they are not.
2. Petrochemical emission intensity is confirmed at the level of one primary source and is otherwise
   **unverified** — neither firm discloses production volume.
3. **TCaR levels depend on an untestable choice.** D4 is too short to discriminate GBM from mean
   reversion. Rankings are robust to the choice; levels are not.
4. Metric ② for petrochemicals depends on the shock-normalisation convention to the tune of 71–73%.
5. The `support` axis carries no information at present (§3.6).
6. Sensitivity of the **plan-selection** channel is only partly verified. The scenario runner
   re-evaluates a fixed plan menu; whether an assumption changes the optimal plan itself requires
   `--replan`, which has been run for some bundles and not others.
7. Where a disclosed coordinate is absent, that is a **measurement-impossible verdict**, not a
   missing value, and not evidence about the firm.
8. **Metric ⑥ is not comparable across countries as it stands.** The `ebitda` column mixes billion
   KRW with 億円 and no exchange rate is applied, and for the two Japanese firms it holds operating
   profit rather than EBITDA (§3.7). The cross-country ⑥ comparison is therefore off by roughly 8%
   from the currency alone, in a known direction, before the profit-definition difference is
   counted. Found 2026-08-11 while checking this document against the data; not yet fixed, because
   the fix is a re-run rather than an edit.

---

*Corrections to this document are welcome and should be sent as issues against the repository. Where
this document and the code disagree, the code is authoritative and this document is defective.*
