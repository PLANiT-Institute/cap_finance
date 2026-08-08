# CAP-KJ MVP Output Specification

**Status:** MVP reporting contract  
**Applies to:** POSCO, Nippon Steel, LOTTE Chemical, and Mitsui Chemicals  
**Primary audience:** investors, corporate strategy and capital-planning teams  
**Governing documents:** `PROJECT_CHARTER.md` and `PROJECT_PLAN.md`

## 1. Purpose and decision standard

The MVP must answer one practical question:

> Which capital must be allocated by 2030, 2040, and 2050; to which facilities and transition routes; under what economic, support, and physical conditions; for how much modelled abatement; and with what common exposure still remaining?

The facility is the calculation unit and the company is the headline reporting unit. Every company result must reconcile to named covered facilities. The four outputs below are the only primary public outputs. Intermediate tables exist to support them, not to create additional research objectives.

The **capital-allocation pathway is not an emissions pathway, a project pipeline, or a marginal abatement cost curve (MACC)**. A MACC can rank a static cost per tonne. The CAP-KJ pathway must additionally show the timing and amount of capital, the annual and cumulative net cost gap, the support or contract condition required, physical deliverability, abatement per unit of capital, and the common cost exposure left after de-risking. A project with attractive abatement economics but no eligible investment window or enabling infrastructure is not investable in the same sense as a physically deliverable project.

No composite ESG, readiness, or investability score is permitted. The decision dimensions remain visible.

## 2. Common output contract

### 2.1 Boundaries and scenarios

Every chart, headline metric, and downloadable row must identify:

- `company_id`, `country`, `sector`, and `company_boundary`;
- `ownership_case` and `ownership_as_of`;
- `base_year`, `reporting_year`, and `decision_horizon`;
- `scenario` (`CP`, `NZ`, or explicitly labelled diagnostic);
- `emissions_boundary` and `production_boundary`;
- real-price currency and `price_year`;
- operational-control or equity-share attribution;
- production and emissions coverage ratios.

Company comparisons are permitted only on harmonised boundaries. CP and NZ must never be averaged or presented as probabilities.

### 2.2 Evidence labels

Every material number must carry both a public display basis and an audit class. Labels attach to the value, not merely to the table or chart.

| `display_basis` | Public meaning | Required `evidence_class` mapping |
|---|---|---|
| `actual` | observed historical value on a named reporting boundary | `reported`, or `derived` when only a deterministic unit/currency conversion is applied |
| `allocated` | observed aggregate distributed to facilities by a declared rule | `allocated` |
| `estimated` | engineering, market, or other transparent assumption used because an observation is unavailable | `estimated` |
| `scenario` | conditional exogenous pathway or price from GCAM or another named scenario | `scenario_output` |
| `modelled` | CAP-KJ result produced from labelled inputs and declared decision rules | `modelled` |

The downloadable data must also include `source_id`, `transformation_method`, `assumption_case`, and `quality_note`. An `actual` value derived from a reported observation must still display `evidence_class=derived`; it cannot be described as directly reported. Allocated or estimated values must never inherit an `actual` label after aggregation.

Charts use a consistent visual grammar:

- solid mark: `actual`;
- hatched mark: `allocated`;
- outlined mark or band: `estimated`;
- dashed line: `scenario`;
- filled model-result mark: `modelled`.

Accessible text labels or tooltips must repeat the basis; colour alone is insufficient.

### 2.3 Coverage ratios

Every company headline displays both:

\[
ProductionCoverage=\frac{\sum \text{covered base-year facility production}}{\text{boundary-matched company production}}
\]

\[
EmissionsCoverage=\frac{\sum \text{covered base-year facility Scope 1+2}}{\text{boundary-matched company Scope 1+2}}
\]

The numerator and denominator must share the year, organisational boundary, scope, and ownership basis. If a denominator is unavailable, coverage is `NA`, never assumed to be 100%.

Projected CAPEX, cost gaps, and abatement inherit these two baseline coverage ratios and add `modelled_facility_share`: the share of identified in-boundary facility capacity for which a transition route has been modelled. Uncovered assets remain an explicit residual and are not scaled as though they resemble covered facilities.

Each figure subtitle must follow this minimum pattern:

> Boundary: [definition] | Scenario: [CP/NZ] | Production coverage: [x%] | Emissions coverage: [y%] | Actual/allocated/estimated share: [x/y/z]

### 2.4 Common metric rules

- CAPEX is shown as real 2025 local currency and real 2025 USD, both by decade and cumulative through 2030, 2040, and 2050.
- `resource_cost_gap` excludes policy transfers and realisable incentives.
- `net_cost_gap` is the incentive-adjusted gap after only legally or contractually realisable cash effects. A GCAM shadow price is never such an effect.
- Annualised cost gaps and cumulative present values are shown separately.
- `abatement_per_capex` is cumulative system modelled abatement divided by incremental transition CAPEX. Company operational-emissions reduction is also reported, but is not substituted for system abatement.
- Closure or production displacement is not system abatement unless replacement production and leakage are included.
- Early-retirement exposure is separate from transition CAPEX and is not called an accounting impairment.
- Monetary outputs include central and transparent low/high cases in the MVP; ranges from market history, engineering assumptions, and scenarios are never blended into one probability distribution.

## 3. Primary output 1 — Company transition pathway

### 3.1 Decision questions

**Investor:** What production and operational-emissions trajectory is implied under CP and NZ, which facility decisions create the divergence, and when do they become capital-relevant?

**Company:** Which route, capacity change, construction window, turnaround, relining, or retirement decision is required at each facility to remain consistent with the sector pathway?

### 3.2 Company headline metric

`2030/2040/2050 transition milestone`: company production and Scope 1+2 emissions in each horizon, percentage change from the actual base year, and the share of production that has moved from the incumbent to a transition route. The headline is accompanied by production and emissions coverage.

### 3.3 Facility drill-down

List the named facilities responsible for at least 80% of the covered company's change in production or emissions, plus every facility whose route or status changes. Show incumbent route, selected transition route, eligible decision window, construction period, operating start, capacity affected, and emissions change. The remainder may be grouped only as a labelled residual.

### 3.4 Required columns

`company_id`, `facility_id`, `facility_name`, `country`, `sector`, `ownership_case`, `ownership_share`, `operational_control_flag`, `company_boundary`, `scenario`, `base_year`, `year`, `decision_window_start`, `decision_window_end`, `transition_start_year`, `incumbent_route`, `selected_route`, `route_status`, `capacity`, `production`, `utilisation`, `scope1_emissions`, `scope2_emissions`, `company_operational_emissions_change`, `system_emissions_change`, `leakage_case`, `display_basis`, `evidence_class`, `source_id`, `production_coverage`, `emissions_coverage`, `modelled_facility_share`, `quality_note`.

### 3.5 Graph form

One company small-multiple with aligned x-axes:

1. stacked production by route, with actual history and CP/NZ scenario-modelled paths;
2. Scope 1+2 emissions trajectory, with CP and NZ as separate lines;
3. a facility milestone strip showing decision windows, construction, commissioning, consolidation, and retirement.

Facility events must be visually connected to the change in the company path. A corporate target may be overlaid as a reference marker only; it cannot define the modelled pathway.

### 3.6 Prohibited interpretations

- Do not call a domestic closure global abatement without replacement-production accounting.
- Do not treat an announced project, target, or route as a committed investment.
- Do not infer that a smooth sector trajectory implies smooth facility dispatch.
- Do not compare company emissions paths when coverage or boundaries differ without an explicit warning.
- Do not interpret CP-to-NZ spread as a probability or forecast error band.

## 4. Primary output 2 — Company cost-gap profile

### 4.1 Decision questions

**Investor:** How large is the economic gap attached to the required pathway, which facilities and inputs dominate it, and how much is closed by currently realisable market and policy conditions?

**Company:** At each eligible investment window, what resource gap remains versus incumbent production, what net gap remains after actual incentives, and which input or carbon price would close it?

### 4.2 Company headline metric

`annualised net cost gap at 2030/2040/2050`: total covered-company resource cost gap and net cost gap, in real local currency and USD, with the largest facility and common-factor contribution identified. Also show the unit gap per tonne of sector output and per tonne of system CO2 abated where commensurable.

### 4.3 Facility drill-down

Rank facilities by contribution to the company net cost gap, not by standalone unit cost. For each, show incremental CAPEX, annualised capital charge, fixed and variable operating gap, actual incentives, early-retirement exposure, break-even prices, production weight, and uncertainty range. A high unit gap at an immaterial facility must not dominate the company headline.

### 4.4 Required columns

`company_id`, `facility_id`, `facility_name`, `scenario`, `decision_year`, `decision_horizon`, `incumbent_route`, `transition_route`, `production_weight`, `incremental_capex_local_2025`, `incremental_capex_usd_2025`, `annualised_capital_gap`, `fixed_opex_gap`, `variable_opex_gap`, `resource_cost_gap`, `realisable_incentive`, `net_cost_gap`, `net_cost_gap_per_output`, `net_cost_gap_per_tco2_system_abated`, `early_retirement_exposure`, `break_even_electricity_price`, `break_even_hydrogen_price`, `break_even_feedstock_price`, `break_even_carbon_price`, `dominant_cost_factor`, `low_case`, `central_case`, `high_case`, `display_basis`, `evidence_class`, `source_id`, `production_coverage`, `emissions_coverage`, `quality_note`.

### 4.5 Graph form

Use a company-level waterfall from resource gap to net gap, with facility contributions nested or linked beneath it. Pair it with a break-even dot-and-range panel for the material input prices. A secondary facility contribution bar is allowed; a standalone MACC is not the primary graph.

### 4.6 Prohibited interpretations

- Do not describe a GCAM shadow price as a tax, subsidy, or company cash flow.
- Do not net subsidies against resource cost without also showing the unadjusted resource gap.
- Do not treat a negative gap as proof that a project will be built; physical, timing, and governance constraints remain.
- Do not mix early-retirement exposure into route unit cost or call it an impairment.
- Do not compare steel and petrochemical cost per tonne of product; cross-sector comparison uses abatement-based measures only.

## 5. Primary output 3 — Company risk-to-abatement profile

### 5.1 Decision questions

**Investor:** Which observable common factors make the pathway fragile, and does reducing exposure alone unlock credible additional abatement or is a lower mean cost level also required?

**Company:** What contract coverage or support level changes a facility decision, how much abatement follows from that status change, and which risks remain after intervention?

### 5.2 Company headline metric

`additional system abatement under BH/BL/BHL versus B0`: cumulative modelled abatement through 2030, 2040, and 2050, paired with the share of transition CAPEX whose facility status changes and the number/name of facilities causing the change. Zero is a valid and decision-relevant result.

### 5.3 Facility drill-down

For every facility, show the B0, BH, BL, and BHL status; the risk-coverage fraction `theta`; level support; emissions under each case; status-change trigger; and residual exposure to electricity, hydrogen, carbon, feedstock, and technology cost. Only facilities whose transition state changes may contribute additional abatement.

### 5.4 Required columns

`company_id`, `facility_id`, `facility_name`, `scenario`, `year`, `mechanism_case` (`B0`, `BH`, `BL`, `BHL`), `mean_cost_treatment`, `risk_exposure_treatment`, `coverage_theta`, `contract_strike_or_reference`, `level_support_per_output`, `level_support_total`, `status_before`, `status_after`, `status_change_flag`, `trigger_factor`, `company_operational_emissions`, `system_emissions`, `additional_system_abatement_vs_b0`, `capex_status_changed`, `residual_electricity_exposure`, `residual_hydrogen_exposure`, `residual_carbon_exposure`, `residual_feedstock_exposure`, `residual_technology_exposure`, `robustness_test`, `display_basis`, `evidence_class`, `source_id`, `production_coverage`, `emissions_coverage`, `quality_note`.

### 5.5 Graph form

Use a four-case company waterfall or grouped bar for B0/BH/BL/BHL cumulative system abatement, with an adjacent facility state-transition strip. Where a defensible probability model is unavailable, show the full coverage-closure curve (`theta` against net gap/status) instead of a binary robustness result. A factor-exposure panel shows exposure before and after de-risking.

### 5.6 Prohibited interpretations

- Do not claim that risk reduction directly causes emissions reduction; it may change a modelled facility decision, which changes modelled emissions.
- Do not call BH a subsidy when its central mean cost is held approximately constant.
- Do not combine historical price variation, engineering uncertainty, and scenario spread into one probability distribution.
- Do not claim statistical confidence where only low/central/high stress cases exist.
- Do not report additional abatement without naming the facilities whose status changed.

## 6. Primary output 4 — Company capital-allocation pathway

### 6.1 Decision questions

**Investor:** How much transition capital is required in each decision horizon, what portion is presently actionable or conditional, what abatement does it buy, and which portfolio-wide factor exposures remain after feasible de-risking?

**Company:** Which facility decisions should enter near-term capital planning, which require contracts or level support, which require enabling infrastructure first, and which must wait for a physical decision window or route change?

### 6.2 Company headline metric

The headline is a **six-part allocation block**, not one score:

1. incremental transition CAPEX by decade and cumulative through 2030/2040/2050;
2. annual and cumulative net cost gap for that capital;
3. cumulative system abatement and `abatement_per_capex`;
4. CAPEX share by fixed facility status (`no-regret`, `price-conditional`, `contract-dependent`, `level-support-dependent`, `physically-constrained`);
5. required contract coverage and level support attached to conditional CAPEX;
6. residual common-factor exposure after the relevant risk-reduction case.

The headline sentence uses this form:

> By [horizon], [company] has [CAPEX] of covered transition capital, of which [x%] is no-regret/price-conditional, [y%] contract-dependent, [z%] level-support-dependent, and [w%] physically constrained; it delivers [abatement] at [abatement/CAPEX], leaves a [net gap], and retains material exposure to [factor(s)]. Coverage: production [p%], emissions [e%].

### 6.3 Capital-allocation decision flow

Every facility-route-decision-window record passes through the following ordered gates. The output is a time-phased decision ledger, not an optimisation claim.

| Gate | Required test | Output used in allocation | If test fails |
|---|---|---|---|
| 1. Boundary and timing | Facility is in scope and has an eligible construction, relining, turnaround, or retirement window | assign CAPEX to 2030, 2040, or 2050 decision horizon | retain as uncovered or future-window residual; do not pull capital forward |
| 2. Physical deliverability | Capacity, material, power, hydrogen, CO2 transport/storage, logistics, technology readiness, and JV decision rights are feasible | physically deliverable flag and binding constraint | classify `physically-constrained`; no claim of investability regardless of MACC position |
| 3. Capital requirement | Incremental transition CAPEX and early-retirement exposure are separately quantified | decade CAPEX and cumulative CAPEX stock | retain estimate range and evidence label; never hide missing capital in unit cost |
| 4. Economic gap | Resource and net cost gaps are tested at the eligible window | annual/cumulative net gap and break-even input prices | classify as price-, contract-, or level-support-dependent according to the declared rule |
| 5. Abatement efficiency | System abatement after leakage is divided by incremental CAPEX | cumulative abatement and abatement/CAPEX | do not count closure-only operational reduction as system abatement |
| 6. Dependency condition | B0/BH/BL/BHL establishes needed `theta`, contract/reference price, and level support | conditional CAPEX, support total, and abatement/support | disclose the missing contract or support condition; do not label committed |
| 7. Residual common risk | Factor exposure is recalculated after the applicable de-risking case | residual cost exposure by common factor and facility concentration | keep exposure visible; do not convert it into a security premium |
| 8. Company aggregation | Facility records are aggregated without extrapolating uncovered assets | company allocation block by 2030/2040/2050 and fixed status | display coverage and unexplained residual |

The pathway therefore connects, for every horizon:

> **eligible facility decision → physical constraint → required CAPEX → net cost gap → abatement/CAPEX → support dependence → residual common risk → company capital bucket**

The project may use the following action views without replacing the fixed status labels:

- **allocate/prepare now:** eligible-window, physically feasible `no-regret` or disclosed `price-conditional` capital;
- **contract before commitment:** `contract-dependent` capital with the required `theta` and reference/strike stated;
- **secure level support before commitment:** `level-support-dependent` capital with required support stated;
- **resolve enabling constraint:** `physically-constrained` capital, shown separately from economically conditional capital;
- **future decision window:** potentially feasible route whose capital is not yet eligible for the current horizon.

These are analytical capital-planning buckets, not predictions of board approval or investment advice.

### 6.4 Facility drill-down

For each horizon, display every facility contributing at least 10% of company transition CAPEX or abatement, every physically constrained facility, and every facility with a status change across B0/BH/BL/BHL. Show the complete gate result, capital timing, abatement, net gap, dependency condition, and residual exposure. Smaller facilities may be grouped as `other covered facilities` only if the downloadable table retains them individually.

### 6.5 Required columns

`company_id`, `facility_id`, `facility_name`, `country`, `sector`, `ownership_case`, `scenario`, `decision_window`, `decision_horizon`, `capex_start_year`, `commissioning_year`, `incumbent_route`, `transition_route`, `physical_feasibility_flag`, `binding_physical_constraint`, `technology_readiness`, `incremental_capex_local_2025`, `incremental_capex_usd_2025`, `capex_by_2030`, `capex_2031_2040`, `capex_2041_2050`, `cumulative_capex_2030`, `cumulative_capex_2040`, `cumulative_capex_2050`, `early_retirement_exposure`, `resource_cost_gap_annual`, `net_cost_gap_annual`, `net_cost_gap_cumulative`, `company_operational_emissions_reduction`, `system_abatement_cumulative`, `abatement_per_capex`, `facility_status`, `action_view`, `mechanism_case`, `coverage_theta_required`, `contract_reference_price`, `level_support_required`, `support_total`, `abatement_per_support`, `dominant_common_factor`, `residual_common_factor_exposure`, `capex_concentration_share`, `display_basis`, `evidence_class`, `source_id`, `production_coverage`, `emissions_coverage`, `modelled_facility_share`, `uncovered_residual`, `quality_note`.

### 6.6 Graph form

The primary figure is a **time-phased company capital-allocation map**:

- x-axis: 2030, 2040, and 2050 decision horizons;
- y-axis: incremental CAPEX, stacked by fixed facility status;
- facility/route labels: the material contributors within each stack;
- annotation: cumulative net cost gap and cumulative system abatement for each horizon;
- linked efficiency panel: system abatement/CAPEX by facility, with bubble size equal to CAPEX;
- dependency glyph: none, price, contract (`theta`), level support, or physical constraint;
- residual-risk panel: company exposure to the material common factors after the selected mechanism case.

A static MACC may appear only as a diagnostic appendix. It cannot replace the time, support, physical-constraint, and residual-risk panels.

### 6.7 Prohibited interpretations

- Do not call the pathway a recommended portfolio, investment advice, capital commitment, forecast, or optimised corporate plan.
- Do not rank capital solely by cost per tonne or abatement/CAPEX.
- Do not move a project into 2030 because it has attractive economics if its physical decision window is later.
- Do not treat contract-dependent or level-support-dependent CAPEX as presently funded or investable.
- Do not combine physical constraint with economic unattractiveness; the remedies differ.
- Do not convert residual cost exposure into a stock beta, spread, valuation, or numerical risk premium.
- Do not produce a company league table when scope or coverage is not comparable.

## 7. Minimum first MVP

The first MVP prioritises a complete decision chain over false precision. It must produce the four primary outputs for all four companies using the best available actual data and transparent allocation or estimation where needed.

Minimum viable content:

1. one actual base year (2024 or 2025, boundary matched where possible);
2. CP and NZ central cases at 2030, 2040, and 2050;
3. named major domestic facilities, with all uncovered assets shown as a residual;
4. one central feasible transition route per facility and one incumbent comparator;
5. central incremental CAPEX, resource cost gap, net cost gap, and low/high assumption cases;
6. B0/BH/BL/BHL mechanism results, allowing rule-based stress ranges where empirical distributions are unavailable;
7. company and system emissions changes shown separately;
8. the fixed facility status, binding constraint, required `theta` or level support, and dominant residual common factor;
9. all value-basis labels, source IDs, quality notes, and production/emissions/modelled-facility coverage;
10. one four-output company dossier and downloadable facility rows per company.

Estimation is acceptable in the MVP when the estimation rule, range, and evidence label are visible. Missing data are `NA` or an explicit residual; they are never silently set to zero. The MVP may be published below a desired coverage threshold, but the result header must say `partial coverage`, and no cross-company rank is allowed when either production or emissions coverage is below 70% or boundaries are not harmonised.

### 7.1 MVP acceptance test

An investor or company reader must be able to answer, without reading model code:

- What capital is required by 2030, 2040, and 2050?
- Which named facilities and routes account for it?
- What net economic gap remains and what closes it?
- What physical constraint can block the capital regardless of cost?
- What system abatement is associated with that capital after leakage treatment?
- Does risk reduction alone change the decision, or is level support required?
- Which common cost exposure remains?
- How much of the company's production and emissions is actually represented, and which values are actual, allocated, estimated, scenario, or modelled?

If any answer cannot be traced from the company headline to facility rows, the MVP output is incomplete.

## 8. Subsequent data and model enhancements

The following improve confidence and granularity but do not block the first MVP:

- extend actual reconstruction from one base year to 2015–2025;
- replace facility allocations with registry-level actuals and improve company reconciliation;
- replace global engineering estimates with country-, route-, scale-, and project-specific parameters;
- add annual paths and exact refurbishment/construction schedules between milestone years;
- improve tariff, policy eligibility, free-allocation, contract, and subsidy cash-flow treatment;
- estimate defensible market covariance and closure curves from longer electricity, carbon, feedstock, and hydrogen-component histories;
- add technology and scenario ranges without conflating them with market probability;
- strengthen import substitution, production relocation, and lifecycle leakage cases;
- refine JV operational-control and equity-share attribution as transactions complete;
- validate transition routes against disclosed projects and realised CAPEX;
- add audited cost-beta aggregation and residual common-factor decomposition;
- raise facility coverage and disaggregate the `other covered facilities` and uncovered residuals.

Enhancements may change values and ranges. They must not change the four-output structure, the facility-to-company trace, the time-phased capital-allocation decision flow, or the mandatory evidence and coverage disclosures without formal change control.

## 9. Publication checklist

Before any primary output is shown, confirm:

- company headline precedes facility drill-down;
- 2030/2040/2050 CAPEX is visible in the capital-allocation pathway;
- resource and net gaps are both visible;
- abatement/CAPEX uses system abatement and reports leakage treatment;
- fixed status and dependency condition are visible;
- physical constraints are separate from economic dependence;
- residual common risk is visible and is not monetised as a security premium;
- actual/allocated/estimated/scenario/modelled bases and charter evidence classes are attached to values;
- production, emissions, and modelled-facility coverage are stated;
- uncovered assets remain a residual rather than an extrapolation;
- every company number reconciles to downloadable facility rows;
- all prohibited-interpretation notes relevant to the figure appear in its caption or methodology note.
