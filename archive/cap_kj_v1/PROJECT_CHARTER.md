# CAP-KJ Project Charter

**Project:** Capital Allocation Pathways for Steel and Petrochemicals in Korea and Japan  
**Short name:** CAP-KJ  
**Version:** 1.0 — protocol freeze candidate  
**Data cut-off for the first release:** 5 August 2026  
**Current programme position:** Stage 1 of the long-term CAP research programme

## 1. Immutable purpose

> CAP-KJ produces company-level capital-allocation pathways by translating sectoral transition pathways into facility-level transition schedules, cost gaps, uncertainty exposures, support conditions, and modelled emissions reductions, and then aggregating them transparently to the company.

The project connects three analytical levels without confusing them:

1. **System level:** GCAM and other authoritative scenarios describe the sector pathway and enabling-energy conditions.
2. **Facility level:** physical assets, technologies, production, emissions, costs, and investment windows determine whether that pathway can be implemented.
3. **Company level:** facility results are aggregated to show the company's transition pathway, cost and capital requirement, support dependence, modelled abatement, capital-allocation priorities, and residual common risk. **This is the primary reporting and decision level.**

CAP-KJ does not create a new global climate scenario. It does not value companies or securities. Its function is to make the missing middle between a sector scenario and an investor decision explicit and reproducible.

## 2. Fixed study sample

The primary sample contains four representative companies, one in each country–sector cell.

| Country | Steel | Petrochemicals |
|---|---|---|
| Korea | POSCO | LOTTE Chemical |
| Japan | Nippon Steel | Mitsui Chemicals |

The sample is fixed for the first complete release. A company may be replaced only if a documented data audit shows that a facility-level analysis is impossible and the replacement improves, rather than weakens, country–sector comparability.

## 3. Four questions that govern all work

### Q1 — Required transition

Under comparable Current Policies and Net Zero-aligned sector pathways, what transition pathway is required for each company, and which facilities must change, when, and through which technically feasible route to deliver it?

### Q2 — Economic gap

What is each company's aggregate transition cost gap, which facilities drive it, and how much more or less costly is each low-carbon route than continued incumbent production after separating resource costs from actual market and policy incentives?

### Q3 — Risk, support, and emissions

Which uncertainties—hydrogen, electricity, carbon, feedstock, technology cost, or enabling infrastructure—dominate each company's pathway? How much company-level modelled abatement is unlocked by reducing risk alone, by lowering the mean cost level, and by combining both?

### Q4 — Investor meaning

How much of each company's production, emissions, and transition capital is investable under current conditions, contract-dependent, support-dependent, or physically constrained, and which common cost exposures remain after de-risking?

No analysis, figure, metric, or report section is in scope unless it answers at least one of these questions.

## 4. Four primary outputs

The public-facing analysis is restricted to four primary outputs.

1. **Company transition pathway** — company-level production and emissions trajectory, with the contributing facility timing and technology visible as a decomposition.
2. **Company cost-gap profile** — aggregate resource and incentive-adjusted gaps, with facility contributions, break-even prices, and early-retirement exposure.
3. **Company risk-to-abatement profile** — dominant company exposures, de-risking coverage, support combinations, and modelled additional abatement, traced back to the facilities that change status.
4. **Company capital-allocation map** — transition readiness, capital and support efficiency, dependency conditions, and premium-relevant residual exposure.

Detailed intermediate tables are retained for auditability but must not become additional research objectives.

## 5. Non-negotiable analytical rules

1. **The facility is the calculation unit; the company is the reporting and decision unit.** Every company result is an aggregation of explicitly covered facilities, and every public-facing result begins with the company total before showing its facility decomposition.
2. **No ex ante corporate carbon budgets.** Sector emissions envelopes are translated to facilities; company pathways emerge ex post.
3. **One common outer framework, two sector-specific physical models.** Steel and petrochemicals share questions and outputs, not false technological equivalence.
4. **GCAM is a system benchmark, not a facility dispatch model.** GCAM technology shares inform and validate direction; CAP-KJ performs the asset translation.
5. **GCAM shadow prices are not actual carbon costs or subsidies.** Only legally or contractually realisable cash effects enter the incentive-adjusted ledger.
6. **Current Policies and Net Zero are not mixed as though they formed a new equilibrium.** Any bridge case is labelled a conditional diagnostic.
7. **Risk reduction does not directly reduce emissions.** It can unlock a facility transition, which then changes modelled emissions.
8. **Scenario uncertainty is not assigned arbitrary probability.** Historical market distributions, technology ranges, and scenario ranges remain distinguishable.
9. **No false precision.** Estimated, inferred, allocated, and reported values are separately flagged.
10. **No firm ranking from incomparable boundaries.** Cross-company comparisons use harmonised domestic operational scopes or show the boundary mismatch explicitly.
11. **Every final number must be reproducible.** It must trace to a source, transformation, model version, and output script.
12. **Primary conclusions must survive specified sensitivity tests.** Otherwise they are reported as conditional findings.

## 6. Stage 1 exclusions

The following are explicitly outside this release:

- real-options modelling;
- DSCR, debt sculpting, or project-finance structuring;
- company financial-statement forecasting;
- company valuation, credit-spread, or share-price estimation;
- a numerical security risk premium in basis points;
- endogenous contract pricing or public fiscal-tail-risk valuation;
- a causal claim that risk reduction itself produced observed emissions reductions;
- optimisation of national industrial policy or distributional fairness;
- confidential company data that cannot be audited or cited.

The final Stage 1 term is **premium-relevant transition exposure**: the company-level aggregation of the covariance and residual exposure of facility cost gaps to common transition factors. The market price of that exposure belongs to a later stage.

## 7. Decision rules and interpretation labels

Every modelled result uses one of the following labels:

- **Reported:** directly disclosed by an identified source.
- **Derived:** calculated from reported data using a documented transformation.
- **Allocated:** a reported aggregate distributed to facilities using a declared rule.
- **Estimated:** based on external engineering or cost assumptions.
- **Scenario output:** conditional result from GCAM or another named scenario.
- **Modelled:** generated by CAP-KJ under declared assumptions.

Facility status labels are fixed:

1. **No-regret:** the route closes the relevant cost gap across the principal test range and meets physical constraints.
2. **Price-conditional:** feasibility changes with observable input or carbon prices.
3. **Contract-dependent:** a specified risk-coverage level is required for robust feasibility.
4. **Level-support-dependent:** uncertainty reduction is insufficient because the central cost gap remains positive.
5. **Physically constrained:** the route fails a material or infrastructure constraint regardless of price.

These are model classifications, not forecasts of final investment decisions.

Company reporting presents the share of production, emissions, transition CAPEX, and modelled abatement associated with each facility status. A company is not assigned one opaque composite score.

## 8. Change-control rule

Changes to the purpose, four questions, sample, primary outputs, system boundary, or exclusions require all of the following:

1. a written decision record in `docs/decisions/`;
2. the reason the current design cannot answer the original question;
3. the effect on comparability and prior results;
4. a project version increment;
5. regeneration of all affected outputs.

New data, improved parameters, code fixes, and additional sensitivity tests do not change the charter unless they alter the meaning of the analysis.

## 9. Completion standard

Stage 1 is complete only when:

- all four companies have an auditable domestic facility inventory;
- sector pathways for Korea and Japan are scenario-consistent or clearly separated when consistency is impossible;
- facility production, emissions, and company totals reconcile within documented tolerances;
- steel and petrochemical transition routes pass engineering and carbon-boundary checks;
- cost gaps and uncertainty ranges are reproduced from code;
- risk-only, level-only, and combined support experiments are reported without causal overclaiming;
- the four primary outputs are produced for every company;
- unresolved data gaps are visible in the final tables;
- a clean environment can reproduce the processed data and figures from permitted source files.

This charter takes precedence over exploratory notebooks, draft figures, and report narratives.
