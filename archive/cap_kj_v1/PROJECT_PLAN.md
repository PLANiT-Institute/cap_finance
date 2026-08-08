# CAP-KJ: Comprehensive Project Plan

## Company-Level Capital Allocation Pathways Built from Facility-Level Evidence

**Version:** 1.0 — analysis protocol  
**Prepared:** 5 August 2026  
**Data cut-off:** 5 August 2026  
**Project stage:** CAP Stage 1 — physical pathway, cost gap, uncertainty, and investor exposure  
**Governing document:** [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md)

---

## 1. Executive statement

CAP-KJ will use actual public data to analyse four representative industrial companies:

- **POSCO** and **Nippon Steel** in steel;
- **LOTTE Chemical** and **Mitsui Chemicals** in petrochemicals.

For each company, the project will identify the domestic production facilities that drive emissions, translate comparable sector transition pathways into facility-specific technology and timing choices, estimate the incremental cost of those choices, test how energy, carbon, feedstock, and technology uncertainty affects feasibility, and show what an investor can infer about capital-allocation priority and residual transition exposure.

**Facilities are the calculation units; companies are the primary reporting and decision units.** The model first calculates physical and economic outcomes facility by facility, then reports the transition pathway, cost gap, risk dependence, modelled abatement, and capital-allocation implications for POSCO, Nippon Steel, LOTTE Chemical, and Mitsui Chemicals. Facility results remain visible as the explanation of each company result.

The project has one fixed analytical chain:

> **Sector pathway → facility transition → cost gap → uncertainty and support conditions → modelled abatement → company-level capital-allocation exposure**

This chain must not be reversed or bypassed. Company conclusions cannot be produced directly from corporate emissions targets, ESG scores, or financial ratios.

## 2. Research objective

The objective is to answer a practical allocation question:

> Under sector pathways consistent with Current Policies and Net Zero, what transition pathway and capital-allocation exposure does each company face, which facilities drive that result, and what conditions would make the associated capital expenditure and emissions reduction credible to an investor?

The project is not designed to identify the “greenest” company. It is designed to identify:

- each company's physical transition pathway and its facility drivers;
- each company's resource and market-policy cost gap and facility contributions;
- the variable or infrastructure constraint that dominates that gap;
- the amount of modelled abatement unlocked by risk reduction, cost support, or both;
- the risk that remains common and non-diversifiable at the company level.

### 2.1 Analytical and reporting units

| Layer | Function | Public presentation |
|---|---|---|
| Sector | defines production, emissions, energy, and policy conditions | benchmark for the four companies |
| Facility | calculates route, timing, cost, uncertainty, and abatement | drill-down and explanation |
| Company | aggregates covered facilities | **headline result and investor decision view** |

No company value may be calculated without its facility components, and no facility table may replace the required company-level result.

## 3. Why these four companies

The sample creates a balanced two-country, two-sector design while retaining enough public information for asset-level reconstruction.

| Company | Country and sector | Latest verified public emissions anchor | Facility evidence available for the study | Primary reason for inclusion |
|---|---|---:|---|---|
| **POSCO** | Korea, steel | 2025 reported Scope 1+2: **69.846 MtCO₂e**; reported intensity: **2.02 tCO₂e/t steel** | Pohang and Gwangyang integrated works; company energy data; Korean installation-level disclosure; equipment and project announcements | Korea's principal integrated steel producer and a direct test of BF–BOF transition choices |
| **Nippon Steel** | Japan, steel | FY2024 non-consolidated GHG total: **79.013 MtCO₂e**; energy-derived CO₂: **75.349 Mt** | official works list, facility production and blast-furnace information; Japan's facility-level SHK disclosure | Japan's principal integrated steel producer with unusually strong works-level public data |
| **LOTTE Chemical** | Korea, petrochemicals | 2025 parent Scope 1+2: **5.371 MtCO₂e**; selected consolidated boundary: **6.118 MtCO₂e** | Yeosu, Daesan, and Ulsan process and capacity data; Korean installation disclosure; announced Daesan and Yeosu restructuring | a large Korean basic-chemicals producer already undergoing asset rationalisation |
| **Mitsui Chemicals** | Japan, petrochemicals | FY2024 parent Scope 1+2: approximately **3.869 MtCO₂e**; group: **4.428 MtCO₂e** | Ichihara, Osaka, Iwakuni-Ohtake and other works; Japanese facility disclosure; disclosed cracker consolidation projects | a data-rich Japanese chemicals producer with observable transition and consolidation decisions |

### Boundary warning

The figures above demonstrate scale and data feasibility; they are not directly comparable company rankings. Their reporting periods and consolidation boundaries differ. CAP-KJ will reconstruct a harmonised **domestic operational-control facility boundary** and separately reconcile it to each public corporate total.

### Current transition events to preserve in the baseline

- LOTTE Chemical announced that its Daesan assets were to be spun off and combined with HD Hyundai Chemical, with a targeted 50:50 ownership structure, while Yeosu rationalisation was also under review. The analysis will preserve both the pre-transaction asset baseline and the announced restructuring case until completion is verified.
- Mitsui Chemicals and its partners have announced consolidation of Chiba ethylene capacity and a western-Japan consolidation centred on Osaka Petrochemical. The latter disclosed an expected **506,000 tCO₂/year** Scope 1+2 reduction. These are observable validation cases, not assumptions to be silently embedded in the model.

## 4. Scope and boundaries

### 4.1 Geographic boundary

The primary analysis covers **domestic production facilities in Korea and Japan** that are operationally controlled by, or materially attributable to, the four companies.

- Overseas subsidiaries are excluded from the primary comparison.
- Joint ventures are shown separately under operational-control and equity-share views.
- Imports and displaced production are tracked to prevent a domestic closure from being mislabelled as global abatement.

### 4.2 Organisational boundary

The primary boundary is operational control. A secondary equity-share result is produced where joint ownership is material, especially for petrochemical crackers and post-restructuring entities.

Every facility record must contain:

- legal owner;
- operator;
- company ownership share;
- operational-control flag;
- reporting-boundary inclusion flag;
- treatment in the primary and sensitivity cases.

### 4.3 Emissions boundary

The common headline boundary is production-related **Scope 1 plus location- or market-appropriate Scope 2** emissions.

Additional boundaries are kept separate:

- upstream fuel and electricity emissions;
- captured and stored CO₂;
- embodied feedstock carbon in petrochemicals;
- end-of-life emissions and recycling credits;
- broader corporate Scope 3.

Steel and petrochemical results are not combined until the emissions boundary is identical. Petrochemical feedstock and end-of-life carbon are reported as a secondary lifecycle extension, not silently added to operational emissions.

### 4.4 Time boundary

- Historical reconstruction: target **2015–2025**, subject to source availability.
- Base year: the latest fully reconcilable facility year, expected to be 2024 or 2025.
- Projection years: **2025–2050**, at annual or five-year scenario intervals.
- Investment decisions occur only at declared construction, relining, major-turnaround, or retirement windows.

### 4.5 Economic boundary

Stage 1 uses a techno-economic, not corporate-finance, perspective.

- Primary values are real 2025 local currency and real 2025 USD.
- Tradable inputs use market exchange rates; a purchasing-power sensitivity is allowed for domestic non-tradable costs.
- A common real analytical discount rate of **5%** is used, with **3% and 7%** sensitivities.
- The discount rate is not described as company WACC or investor required return.
- No debt, tax shield, DSCR, accounting impairment, or security valuation is modelled.

### 4.6 Unit of calculation and unit of reporting

- The **facility** is the lowest calculation unit for physical route, timing, cost, risk, and emissions.
- The **company** is the primary unit for figures, comparison, interpretation, and report conclusions.
- Every headline company value must reconcile to the covered facilities and state the coverage ratio.
- Facility detail is retained to explain concentration, bottlenecks, and outliers; it is not the final presentation endpoint.

## 5. Fixed research questions and pre-specified tests

### Q1 — Required transition

**Test:** Can a feasible combination of facility routes and investment windows satisfy the national sector emissions envelope while meeting production and resource constraints?

Company-level results, supported by a facility decomposition:

- company production and emissions pathway;
- company transition milestones and required technologies;
- technology and timing by contributing facility;
- production and emissions by route and company;
- residual sector production and emissions;
- difference between CAP-KJ facility allocation and GCAM technology shares.

### Q2 — Economic gap

**Test:** At the facility's eligible investment window, is the low-carbon route's annualised unit cost above or below the incumbent route before and after realisable market-policy incentives?

Company-level results, supported by a facility decomposition:

- aggregate resource cost gap and facility contributions;
- aggregate incentive-adjusted gap and facility contributions;
- break-even hydrogen, electricity, feedstock, and carbon prices;
- required level support;
- early-retirement exposure, explicitly separated from accounting impairment.

### Q3 — Risk, support, and emissions

**Test:** Holding the central input-price path approximately constant, does reduced price exposure make the transition robust? If not, how much cost-level support must accompany it?

Company-level results, supported by a facility decomposition:

- aggregate cost sensitivities and market-price covariance, with facility drivers;
- empirical downside ranges where defensible;
- scenario and technology ranges shown separately;
- risk-only, level-only, and combined support experiments;
- company-level modelled additional abatement attributable to changes in facility feasibility.

### Q4 — Investor meaning

**Test:** What share of covered company production, emissions, and transition capital is no-regret, price-conditional, contract-dependent, level-support-dependent, or physically constrained?

Results:

- company capital-allocation map, with facility contributions shown as the explanatory drill-down;
- near-term transition capital and emissions exposure;
- abatement per unit of CAPEX and support;
- risk concentration by common factor;
- premium-relevant residual exposure, without estimating a security premium.

## 6. Scenario architecture

### 6.1 Core scenarios

Only two scenarios are required for the main narrative.

1. **Current Policies (CP):** enacted or credibly implemented policy and currently expected energy-system development.
2. **Net Zero-aligned (NZ):** the closest internally consistent GCAM pathway to economy-wide net zero around 2050.

### 6.2 Bridge diagnostic

The central decision diagnostic is:

> What facility transition is required by the Net Zero emissions envelope, and what cost gap remains if that transition faces Current Policies market and incentive conditions?

This is labelled **NZ pathway under CP incentives**. It is not reported as a new market equilibrium.

### 6.3 Stress cases

Stress cases do not become separate narratives. They diagnose failure points:

- clean hydrogen expensive or supply-constrained;
- clean electricity expensive, carbon-intensive, or grid-constrained;
- CCS transport or storage unavailable;
- scrap or DRI-grade iron input constrained;
- petrochemical feedstock substitution constrained;
- lower industrial demand and capacity rationalisation;
- delayed technology commercialisation;
- accelerated or delayed carbon-pricing implementation.

### 6.4 Korea–Japan scenario consistency rule

The preferred pathway source is one GCAM version and one scenario design covering both Korea and Japan.

Priority order:

1. KAIST supplies solved Korea and Japan regional outputs from the same GCAM run, including iron and steel and chemicals detail.
2. CAP-KJ reproduces a common open-source GCAM release for both regions and uses GCAM-KAIST/ROK results as a Korea calibration and sensitivity benchmark.
3. If chemicals detail is insufficient, CAP-KJ derives a petrochemical envelope from national inventories, primary-chemicals pathways, and production statistics. This envelope is labelled **CAP-derived**, never presented as direct GCAM output.

Korea and Japan pathways from unrelated models may be shown side by side but cannot be used for a numerical country ranking unless differences in model structure are isolated.

## 7. Facility inventory

### 7.1 Steel assets

#### POSCO

Primary works:

- Pohang Works;
- Gwangyang Works.

Minimum equipment resolution:

- blast furnace;
- coke oven where material;
- basic oxygen furnace;
- FINEX or other smelting-reduction unit where applicable;
- electric arc furnace;
- major power and by-product gas systems;
- announced hydrogen, DRI, EAF, and CCUS projects.

#### Nippon Steel

Primary scope includes domestic ironmaking and crude-steelmaking areas identified in the official data book. Equipment is represented at the lowest public level that can be linked reliably to production, relining, and emissions.

The facility master must distinguish works from areas and prevent double-counting where multiple areas are reported under one works name.

### 7.2 Petrochemical assets

#### LOTTE Chemical

Primary basic-chemicals scope:

- Yeosu Basic Chemicals complex;
- Daesan complex;
- Ulsan complex where it produces in-scope primary petrochemicals;
- shared utilities and material joint ventures where attributable.

Advanced-material and downstream plants enter only if their emissions and production can be separated from the primary-chemicals system.

#### Mitsui Chemicals

Primary scope:

- Ichihara Works and linked Chiba cracker arrangements;
- Osaka Works and Osaka Petrochemical's Senboku cracker;
- other domestic works with material in-scope operational emissions;
- joint operations and announced consolidation projects as separate ownership cases.

### 7.3 Required facility fields

The canonical facility table contains:

- stable `facility_id` and source aliases;
- latitude, longitude, country, and industrial cluster;
- owner, operator, ownership share, and boundary status;
- process route and equipment units;
- commissioning and latest major refurbishment year;
- nameplate capacity, reported production, and utilisation;
- products and co-products;
- reported Scope 1 and 2 emissions where available;
- energy and feedstock consumption;
- announced closure, conversion, or expansion;
- data-quality and estimation flags;
- source identifier and retrieval date for every material field.

## 8. Sector-specific physical models

The outer decision framework is identical, but steel and petrochemicals use separate engineering representations.

### 8.1 Steel routes

At minimum, each eligible integrated facility is tested against:

1. **BF–BOF continuation with best-available efficiency**;
2. **hydrogen injection or other transitional BF improvement**;
3. **BF–BOF or smelting-reduction with CCUS**;
4. **scrap-EAF**;
5. **domestic H₂-DRI-EAF**;
6. **imported DRI/HBI plus EAF**, where physically and commercially plausible;
7. **retirement or capacity reduction**, with displaced production explicitly accounted for.

Physical constraints include:

- blast-furnace relining and replacement windows;
- crude-steel demand and product-quality requirements;
- domestic scrap quantity and quality;
- DRI-grade ore or HBI availability;
- low-carbon hydrogen quantity and carbon intensity;
- clean-power connection, quantity, and carbon intensity;
- CCUS capture rate, transport, storage, and residual emissions;
- technology readiness and construction lead time;
- minimum efficient scale and utilisation.

### 8.2 Petrochemical routes

For steam crackers and associated primary-chemical units, the route set includes:

1. **continued naphtha cracking with efficiency and furnace upgrades**;
2. **electrified cracking or electrified process heat**;
3. **clean-hydrogen or low-carbon fuel substitution where technically material**;
4. **CCUS on process furnaces, CHP, or concentrated process streams**;
5. **bio-naphtha, recycled pyrolysis oil, or other lower-carbon feedstock substitution**;
6. **alternative primary-chemical pathways**, such as low-carbon alcohol-to-olefins, only after technology and feedstock validation;
7. **cracker consolidation, closure, or product-mix shift**, with production displacement and import leakage accounted for.

Physical and market constraints include:

- cracker and furnace turnaround windows;
- co-product yields and multi-product allocation;
- feedstock availability, quality, and chain-of-custody;
- renewable electricity and clean-fuel supply;
- hydrogen use as fuel versus feedstock;
- CCS infrastructure and capture-point suitability;
- recycled-feedstock collection and conversion capacity;
- downstream derivative demand and integrated site balances;
- technology readiness and joint-venture decision rights.

### 8.3 Closure and leakage rule

A facility closure is not counted automatically as global abatement.

The model must identify whether output is:

- eliminated by lower demand;
- shifted to another covered domestic facility;
- imported from an external producer;
- replaced by a genuinely lower-carbon route.

Only the emissions difference after replacement production is included in the modelled abatement result. Company operational-emissions reduction and system emissions reduction are shown separately.

## 9. Translating sector pathways to facilities

### 9.1 Primary method

The translation is a transparent, constrained facility-scheduling problem.

For each eligible investment window, the model:

1. identifies technically feasible routes;
2. calculates production, emissions, resource use, and annualised cost;
3. selects a route consistent with the sector production and emissions envelope;
4. preserves material, energy, infrastructure, and technology constraints;
5. records why unselected routes failed.

A deterministic rule-based allocation is implemented first. If multiple feasible combinations remain materially different, a small linear or mixed-integer cost-minimisation model may choose among them. This is not a real-options model and does not optimise against future stochastic information.

### 9.2 Objective and constraints

The base optimisation minimises discounted resource cost subject to:

- annual sector production demand;
- annual sector emissions envelope;
- facility capacity and utilisation;
- construction and retirement windows;
- route-specific material and energy demand;
- resource and infrastructure availability;
- minimum technology-readiness year;
- no double-counting of shared equipment or emissions.

### 9.3 Residual sector

If the four companies do not cover the entire national sector, a calibrated `residual_sector` preserves national production, energy, and emissions totals. Company conclusions are based only on covered facilities; the residual sector exists to maintain system consistency.

## 10. Cost model

### 10.1 Two ledgers

| Ledger | Included | Question answered |
|---|---|---|
| **Resource-cost ledger** | annualised CAPEX, energy, feedstock, O&M, transport, storage, decommissioning, early-retirement exposure | What is the real economic cost difference before policy transfers? |
| **Market-policy ledger** | actual carbon compliance effect, free allocation, verified subsidy, contract cash effect, and realisable green premium | What cost gap remains for the facility under observable incentives? |

Transfers are not counted as resource costs. GCAM shadow prices are excluded from the market-policy ledger.

### 10.2 Annualised facility cost

For facility `i`, route `k`, year `t`, and scenario `s`:

\[
C_{ikts}^{resource}
= \frac{CRF(r,n_k)\,CAPEX_{ikt}}{Q_{ikt}}
+ Feedstock_{ikts}
+ Energy_{ikts}
+ O\&M_{ikt}
+ TransportStorage_{ikts}
+ EarlyRetirement_{ikt}
\]

The resource gap is:

\[
\Delta C_{ikts}^{resource}
=C_{ikts}^{low\ carbon}-C_{its}^{incumbent}
\]

The incentive-adjusted gap is:

\[
\Delta C_{ikts}^{net}
=\Delta C_{ikts}^{resource}
-AvoidedActualCarbonCost_{ikts}
-RealisedGreenPremium_{ikts}
-VerifiedSupport_{ikts}
\]

### 10.3 Units

Steel outputs:

- local currency and USD per tonne of crude steel;
- currency per tonne of CO₂ abated;
- annual and cumulative total cost.

Petrochemical outputs:

- local currency and USD per tonne of primary output or high-value chemicals;
- currency per tonne of CO₂ abated;
- annual and cumulative total cost.

Cross-sector comparison uses only commensurable measures such as cost per tonne of CO₂ abated, abatement per unit of capital, and support per unit of abatement.

### 10.4 Multi-product chemical allocation

Steam-cracker cost and emissions are allocated to products using a documented primary method and sensitivity:

- primary: mass or process-causality allocation where engineering data support it;
- sensitivity: energy or economic allocation;
- no allocation when the decision concerns the entire cracker as one investment unit.

### 10.5 Early-retirement exposure

Early-retirement exposure is an engineering estimate of uncompleted useful service:

\[
ERE_{it}=ReplacementCost_i \times
\frac{RemainingTechnicalLife_{it}}{ExpectedTechnicalLife_i}
\times RetiredShare_{it}
\]

It is never described as book-value impairment or investor loss.

## 11. Price and policy variables

### 11.1 Electricity

Historical market anchors:

- Korea Power Exchange EPSIS hourly and weighted-average SMP;
- Japan Electric Power Exchange day-ahead and area prices;
- regulated or contracted industrial tariffs where market prices do not represent facility procurement.

Forward values come from the common GCAM scenario and authoritative national power assumptions. Wholesale prices, network charges, taxes, and clean-power contracting costs remain distinct.

### 11.2 Carbon

- Korea: KAU allowance history, Korean ETS allocation and compliance rules, and facility exposure.
- Japan: the GX ETS rules effective from FY2026, observed allowance data when a usable market history exists, and official reference price limits where relevant.

Actual compliance costs reflect free allocation and legal coverage. A carbon price is not multiplied by all emissions without applying the relevant allocation and boundary rules.

### 11.3 Hydrogen

Because neither country has a sufficiently deep industrial clean-hydrogen spot series, hydrogen prices are constructed from components:

\[
P_{H_2}=AnnualisedElectrolyserCost
+q_E P_E
+Water+O\&M+Compression+Storage+Transport
\]

Imported hydrogen or derivatives add production, conversion, shipping, reconversion, terminal, exchange-rate, and carbon-intensity terms.

Power and hydrogen prices are not sampled independently when hydrogen is electricity-derived. Their covariance is inherited from the component model.

### 11.4 Feedstocks and fuels

Steel inputs include iron ore, metallurgical coal, scrap, DRI/HBI, natural gas, and oxygen. Petrochemical inputs include naphtha, LPG, natural gas, electricity, hydrogen, recycled feedstock, and qualifying biogenic inputs.

Prices use official customs, energy-statistics, or exchange data where possible. Commercial price assessments may be used only when licensing permits reproducible use; otherwise the data are referenced but not redistributed.

### 11.5 Technology costs

Technology cost and performance assumptions are assembled from:

- company project disclosures;
- IEA technology roadmaps and the 2026 ETP Clean Energy Technology Guide;
- national demonstration programmes;
- peer-reviewed techno-economic studies;
- engineering benchmarks with explicit currency year, scale, and location adjustments.

Each value records whether it is a point estimate, range, or project-specific observation.

## 12. Uncertainty architecture

### 12.1 Three blocks that remain separate

| Block | Evidence | Treatment |
|---|---|---|
| Market | observed power, carbon, fuel, feedstock, and FX series | empirical distribution, covariance, regime and block-bootstrap tests |
| Technology | published CAPEX, efficiency, utilisation, lifetime, and readiness ranges | low/base/high and justified parameter distributions |
| Scenario | GCAM policy, demand, technology, and energy-system pathways | conditional range and stress cases, not assigned probability |

The project does not report one total variance unless all components belong to a defensible common probability model.

### 12.2 Market-risk estimation

The preferred frequency is monthly. The model will:

1. deflate nominal prices;
2. align currencies and periods;
3. retain joint observations for correlated inputs;
4. identify structural breaks and major energy-price regimes;
5. use rolling windows and a block bootstrap to preserve serial dependence;
6. report results with and without crisis periods;
7. avoid treating a short new-market history as a stable long-run distribution.

### 12.3 Risk attribution

Every facility receives:

- local cost elasticity to each input;
- break-even input prices;
- one-at-a-time range contribution;
- covariance-aware market contribution;
- interaction terms where material.

Variance shares such as Sobol or Shapley effects are used only inside a defined probabilistic block. Scenario spread is not forced into those shares.

## 13. Risk reduction, level support, and modelled abatement

### 13.1 Four mechanism cases

| Case | Mean cost level | Residual input-price exposure | Meaning |
|---|---|---|---|
| **B0** | unchanged | unchanged | baseline conditions |
| **BH** | approximately unchanged | reduced | risk-only mechanism experiment |
| **BL** | reduced | unchanged | level-only support experiment |
| **BHL** | reduced | reduced | combined support experiment |

For a covered input price:

\[
P^{effective}(\theta)=\theta K+(1-\theta)P^{market}
\]

`θ` is the covered share and `K` is set to preserve the declared central price path in the risk-only experiment. Stage 1 does not price the contract premium or public tail risk.

### 13.2 Hydrogen-specific experiment

Hydrogen-risk reduction is tested wherever hydrogen is a material cost input.

- In steel, the main application is H₂-DRI-EAF and transitional hydrogen use.
- In petrochemicals, the test applies only to routes using clean hydrogen materially as fuel or feedstock.
- A zero petrochemical effect is a valid result; hydrogen is not forced to be the dominant risk.

### 13.3 Feasibility and robustness

A route is physically feasible only if all material and timing constraints pass. Economic feasibility is then reported as:

- central cost-gap sign;
- share of empirical market draws in which the gap closes;
- robustness across technology ranges;
- robustness across named scenarios, reported descriptively rather than probabilistically.

The primary risk-dependent classification uses a pre-registered 90% market-draw closure test where a probability model is defensible, with 75% and 95% sensitivities. Where it is not defensible, the project reports the entire closure curve rather than a binary status.

### 13.4 Modelled additional abatement

For each support case `x`:

\[
ModelledAbatement_x=E_{B0}-E_x
\]

The result is decomposed into:

- earlier transition;
- additional transitioned capacity;
- route substitution;
- avoided or displaced production;
- leakage or replacement-production adjustment.

The report must use the phrase **modelled additional abatement under stated decision rules**. It must not call this a causal policy effect.

## 14. Investor translation

### 14.1 Facility calculation fields

For each facility the supporting dataset reports:

- required route and earliest credible transition year;
- transition CAPEX and resource cost gap;
- incentive-adjusted gap;
- annual and cumulative modelled abatement;
- break-even hydrogen, electricity, feedstock, and carbon prices;
- dominant physical and economic constraints;
- risk coverage and level support needed;
- status classification;
- residual common risk after the mechanism experiment;
- data-quality and scope flags.

### 14.2 Company-level primary results

Company results are capacity-, emissions-, capital-, and abatement-weighted aggregations of covered facilities. These are the headline outputs used in all figures, comparisons, executive summaries, and investor conclusions. The analysis reports the covered share and never assumes that uncovered assets have the same characteristics.

Core company metrics:

- production and emissions coverage;
- transition CAPEX by 2030, 2040, and 2050;
- annualised resource and incentive-adjusted gaps;
- share of capacity in each status class;
- modelled abatement per unit of CAPEX;
- modelled abatement per unit of required support;
- modelled abatement per unit of contracted hydrogen or electricity exposure;
- concentration of transition capital in the largest facilities;
- residual factor exposure after de-risking.

No composite ESG score is created.

Each company result must also identify the facilities responsible for the largest shares of transition CAPEX, cost gap, modelled abatement, and residual risk. This preserves explanation without turning the report into a collection of standalone plant studies.

### 14.3 Premium-relevant exposure

For observable common factor `F_k`, facility cost exposure is:

\[
\beta^{cost}_{ik}=\frac{Cov(\Delta C_i,F_k)}{Var(F_k)}
\]

The company result aggregates facility cost betas and shows how much common exposure remains after the risk-reduction case.

This is a **cost beta**, not a stock beta. Stage 1 does not estimate factor prices `λ_k` or convert the exposure into basis points.

## 15. Data acquisition plan

The detailed source matrix is maintained in [`DATA_CATALOG.md`](DATA_CATALOG.md). The source hierarchy is:

1. official government and regulatory data;
2. assured company reports and statutory disclosures;
3. official company facility and project disclosures;
4. GCAM databases, inputs, and query outputs;
5. peer-reviewed engineering and economic research;
6. reputable open facility trackers for cross-checking only;
7. transparent estimation when no direct source exists.

### Minimum data gate

Modelling may begin only after the following exist for each covered facility or a declared estimation rule has been approved:

- identity, ownership, route, age or refurbishment window, and capacity;
- production or defensible utilisation estimate;
- emissions or defensible facility allocation;
- incumbent energy and material intensity;
- feasible transition routes and technology availability;
- route-specific CAPEX, OPEX, energy, material, and emissions parameters;
- national pathway and enabling-energy price paths;
- actual carbon-policy treatment.

## 16. Data engineering and reproducibility

### 16.1 Source ledger

Every source receives a stable `source_id` with:

- publisher and title;
- URL or DOI;
- publication and retrieval dates;
- reporting period;
- table, page, or field location;
- licence and redistribution rule;
- file checksum;
- extraction method;
- quality note.

### 16.2 Raw-data rule

- Raw files are immutable and date-stamped.
- Licensed files that cannot be redistributed are excluded from Git and represented by acquisition instructions and checksums.
- Manual transcription is allowed only with double-entry verification and a page-level citation.
- A revised source creates a new version; it never overwrites the prior raw file.

### 16.3 Transformation rule

All cleaning, unit conversion, facility matching, allocation, and imputation occur in code. Processed tables contain source and transformation fields so that a result can be traced backwards.

### 16.4 Reporting-period harmonisation

The data model stores exact `period_start` and `period_end` values. Calendar-year and Japanese fiscal-year values are not labelled as identical. Annualisation is allowed only when justified and flagged.

### 16.5 Currency and price-year harmonisation

Every monetary record stores:

- nominal or real status;
- original currency;
- original price year;
- deflator source;
- exchange-rate source;
- converted currency and price year.

## 17. Quality assurance and validation

### 17.1 Reconciliation tests

For every company and year:

- facility production must reconcile to the covered company production total;
- facility emissions must reconcile to the relevant reported or registry boundary;
- Scope 1, Scope 2, captured CO₂, and avoided emissions must not be mixed;
- route production must sum to sector production including the residual sector;
- energy and material balances must close within declared tolerances.

Target tolerances:

- reported production aggregation: **±2%**;
- reported emissions aggregation: **±5%**;
- allocated facility emissions: **±10%**, with the allocation residual shown;
- monetary unit conversions: exact apart from documented rounding.

Failure does not disappear into an adjustment factor. It creates a visible QA exception.

### 17.2 Engineering validation

- steel energy, hydrogen, scrap, DRI, and emissions intensities are benchmarked against IEA and project evidence;
- petrochemical yields, furnace energy, feedstock carbon, and co-product allocation are benchmarked against process literature;
- electricity and hydrogen carbon intensity are checked against the same generation assumptions used in the pathway;
- CCS routes include capture energy and residual emissions;
- early-retirement results are checked against alternative lifetime assumptions.

### 17.3 External-event validation

Announced real decisions are used as out-of-sample plausibility checks where possible:

- LOTTE Chemical's Daesan and Yeosu restructuring;
- Mitsui Chemicals' Chiba and western-Japan cracker consolidation;
- disclosed steel demonstration and replacement projects.

The model is not calibrated to reproduce these decisions automatically. Differences must be explained by data, constraints, or factors outside Stage 1.

### 17.4 Robustness tests

Required tests include:

- 3%, 5%, and 7% real discount rates;
- alternative facility lifetime and utilisation;
- alternative power and hydrogen carbon intensity;
- carbon-policy allocation sensitivity;
- high and low clean-energy infrastructure availability;
- technology-cost and readiness ranges;
- exclusion of crisis price periods;
- operational-control versus equity-share ownership;
- petrochemical allocation method;
- output leakage and import-emissions assumptions.

## 18. Execution phases and gates

### Phase 0 — Protocol and repository freeze

Actions:

- approve the charter, sample, boundaries, and four outputs;
- assign stable company and facility identifiers;
- establish source, unit, scenario, and decision-record schemas;
- create the reproducible repository structure.

**Gate 0:** no analytical code begins until the charter and data cut-off are versioned.

### Phase 1 — Source acquisition and facility inventory

Actions:

- download and register government, company, and model sources;
- build the four company facility inventories;
- map legal entities, JVs, and operational control;
- identify missing data and estimation routes.

**Gate 1:** every facility has an identity, ownership treatment, process route, capacity, and source trail.

### Phase 2 — Historical baseline and reconciliation

Actions:

- construct production, emissions, energy, and price histories;
- harmonise periods, units, currencies, and scopes;
- reconcile facilities to company and national totals;
- freeze the baseline-year dataset.

**Gate 2:** reconciliation passes or all residuals are documented and approved.

### Phase 3 — Scenario and technology library

Actions:

- acquire or reproduce the common GCAM scenarios;
- create steel and petrochemical technology parameter libraries;
- define physical resource and infrastructure constraints;
- validate country pathways against official statistics and external roadmaps.

**Gate 3:** each route has a complete mass, energy, emissions, cost, lifetime, and availability record.

### Phase 4 — Facility pathway and cost-gap model

Actions:

- translate sector envelopes to facility investment windows;
- calculate route choices, production, emissions, and resource gaps;
- apply actual policy and market incentives separately;
- produce break-even and early-retirement results.

**Gate 4:** the model reproduces all baseline totals and has no infeasible hidden residuals.

### Phase 5 — Uncertainty and support experiments

Actions:

- estimate market distributions and covariance;
- run technology and scenario ranges separately;
- execute B0, BH, BL, and BHL cases;
- calculate modelled additional abatement and leakage adjustments.

**Gate 5:** risk-only results preserve the declared central price path, and every abatement change traces to a changed facility decision.

### Phase 6 — Investor aggregation

Actions:

- classify facilities;
- aggregate capital, cost, abatement, dependency, and residual risk;
- calculate cost-factor exposure;
- generate the four company capital-allocation maps.

**Gate 6:** company results reproduce the covered facility totals and state coverage explicitly.

### Phase 7 — Release and report package

Actions:

- regenerate all tables and figures from a clean environment;
- produce methodology, data, limitation, and result documentation;
- archive permitted data and source manifests;
- tag the reproducible release for the later report.

**Gate 7:** an independent clean run recreates the released processed datasets and figures.

### Indicative duration

A credible first full release is approximately **18–22 weeks** of focused work, driven by data-access gates rather than calendar deadlines. Facility-emissions reconciliation and GCAM output access are expected to be the critical path.

## 19. Repository design

```text
cap-rebuild/
├── README.md
├── PROJECT_CHARTER.md
├── PROJECT_PLAN.md
├── DATA_CATALOG.md
├── DATA_REQUEST_KAIST.md
├── CHANGELOG.md
├── pyproject.toml
├── uv.lock
├── config/
│   ├── project.yaml
│   ├── companies.yaml
│   ├── scenarios.yaml
│   └── units.yaml
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── manifests/
├── docs/
│   ├── decisions/
│   ├── methodology/
│   └── data-dictionary/
├── src/cap_kj/
│   ├── ingest/
│   ├── harmonise/
│   ├── pathways/
│   ├── steel/
│   ├── petrochemicals/
│   ├── costs/
│   ├── uncertainty/
│   ├── investors/
│   └── reporting/
├── tests/
├── notebooks/
├── outputs/
│   ├── tables/
│   ├── figures/
│   └── diagnostics/
└── reports/
```

Rules:

- notebooks are exploratory and never the source of a final number;
- final outputs are generated by versioned pipeline commands;
- source data and outputs are not edited manually;
- tests cover units, joins, balances, ownership, emissions, and scenario aggregation;
- large or restricted raw files are handled through manifests, not silently committed.

## 20. GitHub and release protocol

### Branch and review discipline

- `main` contains only reproducible, passing work;
- feature branches contain one bounded data or model change;
- every pull request identifies affected sources, assumptions, outputs, and tests;
- purpose or boundary changes require a decision record under the charter.

### Version milestones

- **v0.1 — Protocol freeze:** charter, plan, schemas, and source catalogue;
- **v0.2 — Baseline data:** reconciled facilities, production, emissions, and prices;
- **v0.3 — Physical pathways:** scenario and facility transition results;
- **v0.4 — Cost and uncertainty:** cost gaps and support experiments;
- **v0.5 — Investor exposure:** company aggregation and premium bridge;
- **v1.0 — Report dataset:** validated, documented, and reproducible release.

### Public-data rule

The repository will publish only data that can legally be redistributed. Restricted sources will have:

- exact acquisition instructions;
- file name and checksum;
- expected schema;
- transformation code;
- a clear licence note.

## 21. Final analytical products

### 21.1 Canonical datasets

- `facility_master.csv`
- `facility_production_emissions.csv`
- `sector_pathways.csv`
- `technology_parameters.csv`
- `market_prices.csv`
- `policy_incentives.csv`
- `facility_transition_results.csv`
- `facility_cost_gaps.csv`
- `uncertainty_results.csv`
- `support_experiments.csv`
- `company_transition_results.csv`
- `company_cost_gaps.csv`
- `company_risk_abatement.csv`
- `company_capital_allocation.csv`
- `source_register.csv`

### 21.2 Four primary figures

1. **Company transition pathways:** the four company production and emissions trajectories, with facility transition milestones as the decomposition.
2. **Company cost-gap profiles:** aggregate resource and incentive-adjusted gaps, with the facilities and break-even prices that drive them.
3. **Company risk-to-abatement profiles:** company exposure, support combinations, and modelled additional abatement, with the affected facilities identified.
4. **Company capital-allocation map:** company transition readiness, capital and support efficiency, and premium-relevant residual exposure.

### 21.3 Report-ready company dossiers

Each dossier will use the same structure:

1. company boundary, coverage, and observed baseline;
2. company transition pathway and milestones;
3. company transition CAPEX and aggregate cost gap;
4. company risk concentration and support dependence;
5. company modelled abatement under B0/BH/BL/BHL;
6. company capital-allocation and premium-relevant exposure;
7. facility decomposition explaining the company result;
8. limitations and data-quality statement.

## 22. Main risks and mitigations

| Risk | Consequence | Mitigation |
|---|---|---|
| GCAM-KAIST output lacks Japan or chemicals detail | inconsistent country or sector comparison | reproduce common GCAM; label CAP-derived petrochemical envelope |
| facility emissions are unavailable or use different boundaries | false asset precision | registry matching, transparent allocation, reconciliation residual, quality flag |
| petrochemical JVs change during the project | ownership double-counting | date-stamped ownership graph and operational/equity sensitivities |
| closures shift production abroad | overstated abatement | replacement-production and leakage accounting |
| hydrogen has no liquid spot history | invented volatility | bottom-up component price with covariance and stress ranges |
| Japan's new GX ETS has short price history | unstable carbon variance | use rules and official price bands; do not extrapolate a mature distribution |
| technology cost ranges are inconsistent | misleading precision | common price year, scale adjustment, source hierarchy, range validation |
| project expands into valuation or financing | loss of clarity | charter exclusions and change control |
| results depend on one robustness threshold | brittle classification | publish closure curve and 75/90/95% sensitivities |
| company public totals do not match domestic assets | misleading ranking | disclose covered share and keep reconciliation bridge |

## 23. Success criteria

The project succeeds if an investor, policymaker, or company can answer the following without reading the model code:

1. What transition pathway and milestones does each company face?
2. What is each company's real resource gap, and how much remains under actual policy and market conditions?
3. Which facilities and constraints drive each company's result?
4. Does risk reduction alone unlock company-level abatement, or is cost-level support also required?
5. How much company and system abatement follows after production displacement is considered?
6. Which company exposures are concentrated in specific facilities and which remain common across the portfolio?
7. Which findings are reported, derived, allocated, estimated, scenario-based, or modelled?

If the project cannot answer these seven questions transparently, additional sophistication does not count as progress.

## 24. Authoritative starting sources

### Models and pathways

- [JGCRI, GCAM core repository](https://github.com/JGCRI/gcam-core)
- [GCAM 8.2 documentation](https://jgcri.github.io/gcam-doc/)
- [GCAM-KAIST 1.0 input files and database](https://zenodo.org/records/14171830)
- [GCAM input files for Korea industrial decarbonisation](https://zenodo.org/records/13920489)
- [IEA Iron and Steel Technology Roadmap](https://www.iea.org/reports/iron-and-steel-technology-roadmap)
- [IEA Primary Chemicals tracking analysis](https://www.iea.org/reports/primary-chemicals)
- [IEA ETP Clean Energy Technology Guide](https://www.iea.org/data-and-statistics/data-tools/etp-clean-energy-technology-guide)

### Company evidence

- [POSCO 2025 sustainability data](https://sustainability.posco.com/S91/S91F10/eng/cmspage.do?mmcd=2682093497003371)
- [Nippon Steel Integrated Report and Data Book 2025](https://www.nipponsteel.com/en/ir/library/annual_report.html)
- [LOTTE Chemical ESG reports](https://www.lottechem.com/en/esg/management_report.do)
- [Mitsui Chemicals ESG Report 2025 performance data](https://jp.mitsuichemicals.com/content/dam/mitsuichemicals/sites/mci/documents/sustainability/report/esg2025web_e_part06.pdf.coredownload.pdf)

### Facility emissions and markets

- [Korea public data: regulated-company emissions statements](https://www.data.go.kr/dataset/3072361/fileData.do)
- [Japan SHK facility emissions disclosure](https://eegs.env.go.jp/ghg-santeikohyo-result/search)
- [Korea Power Exchange EPSIS weighted SMP](https://epsis.kpx.or.kr/epsisnew/selectEkmaSmpSmpChart.do?menuId=040201)
- [Japan Electric Power Exchange](https://www.jepx.jp/en/electricpower/outline/)
- [Japan METI GX emissions trading system](https://www.meti.go.jp/policy/energy_environment/global_warming/ets.html)

These sources begin the evidence base. They do not replace the source register, page-level citations, licence review, or data-quality audit required before analysis.
