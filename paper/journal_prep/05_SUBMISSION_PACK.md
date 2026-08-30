# 05. Energy Policy 투고 패키지 초안

> 2026-08-22 21:00 KST (반복 16). Energy Policy(Elsevier) 투고 시 요구 항목: Highlights(3–5개, 각 ≤85자 공백 포함), Abstract(≤250단어 권장), Keywords(≤6), Cover letter, Declaration of interests, Data availability statement, CRediT. 본 파일은 원고 밖 부속물의 초안이며 `[TBD]`는 저자 정보.

## Highlights (각 85자 이내, 공백 포함)

1. Disclosed transition plans are placed on an intra-firm cost–tail-risk frontier. (79)
2. The frontier is traced by PPA share and EPC contracts, not by technology choice. (80)
3. Removing one won of tail risk costs 0.3–0.4 won in steel, 4–5 won in petrochemicals. (84)
4. Stricter carbon budgets lower tail funding risk for every firm studied. (71)
5. Early transition pays only if carbon-budget overshoot is sanctioned, not on price. (82)

## Keywords (Energy Policy ≤6)
transition plans; capital allocation; efficiency frontier; tail risk; power purchase agreements; carbon budget

## Cover letter (초안)

Dear Editor,

We submit "Where do disclosed transition plans sit in the cost–risk plane? An intra-firm efficiency frontier for four Korean and Japanese steel and petrochemical firms" for consideration as a full-length article in *Energy Policy*.

Corporate transition plans are now assessed by several public benchmarks, all of which ask whether a plan is aligned with a carbon budget. None asks what the plan costs the firm, how dispersed that cost is, or whether the same budget could be met more cheaply or more safely. We build the missing axis. For POSCO, Nippon Steel, Mitsui Chemicals and LOTTE Chemical we enumerate budget-feasible facility-level transition plans, revalue each on 10,000 correlated price paths, and trace the efficient frontier in expected cost and tail cost-at-risk (P90 − P50, the additional funding a treasury must pre-arrange). The disclosed plan's distance to that frontier is reported in local currency.

Three findings are of direct policy relevance. First, along the frontier only procurement contracts vary — renewable PPA share and fixed-price EPC — while the technology schedule is pinned at the cost minimum, so corporate PPA access is transition-risk policy. Second, the price of hedging tail risk differs by an order of magnitude between steel and petrochemicals, because the petrochemical tail is a hydrogen tail that no electricity contract can reach. Third, on money alone delay wins for three of four firms; early transition is rational only where carbon-budget overshoot is sanctioned in quantity. We believe these results speak to the journal's readership on electricity-market design, transition finance and carbon-budget governance.

The paper is built for scrutiny: every number is registered in a machine-checked ledger reconciled against model outputs, the falsifiable claims and their refuting observations are listed, and the limitations that could reverse the conclusions are stated in a table. Code, configuration and a reproducibility package are deposited `[TBD: Zenodo DOI]`. Facility-level outputs are withheld; firm-level aggregates are public.

The manuscript is approximately 7,100 words of main text excluding tables, with three figures, nine tables (one of them the five-stage method summary) and a supplementary document (S1–S8). It has not been published or submitted elsewhere. We suggest the following reviewers `[TBD]` and declare no competing interests.

Yours sincerely,
`[TBD: corresponding author, affiliation, contact]`

## Declaration of interests
The authors declare no competing financial or personal interests. `[TBD: funding statement — PLANiT / grant]`

## Data availability statement
The full pipeline, configuration, seeds, parameter inventory (415 rows with source identifiers) and a reproducibility package with SHA-256 manifests are available at `[TBD: Zenodo DOI]`. Facility-level outputs are withheld under the project's disclosure policy; firm-level aggregates and all figures are reproducible from the package.

## CRediT
`[TBD]` Conceptualization, Methodology, Software, Validation, Formal analysis, Data curation, Writing – original draft, Writing – review & editing, Visualization.

## Supplementary Information — 목차 초안

- S1 MILP formulation and assumption register A-01–A-23 (from `METHODOLOGY.md` §8)
- S2 Price processes: GBM specification, calibration, ADF/Hurst tests and power analysis (from `docs/price_process_test.md`, `docs/process_alternative.md`)
- S3 Parameter inventory (415 rows), confidence grades T1–T5, evidence bands (from `docs/parameter_inventory.csv`, `data/raw/tech_bands.csv`)
- S4 Scenario bundles: definitions, re-planning protocol, per-firm results incl. resource-cost regret (from `scripts/run_scenarios.py`, `out/scenarios/summary.csv`, `out/m4/regret.csv`)
- S5 Full frontier ladders (24 rungs), variance decomposition by rung, ppa_costly ladders (from `out/m4/frontier_ladder.csv`, `out/e5/variance_decomp.csv`, `out/scenarios/ppa_costly/e5/frontier_points.csv`)
- S6 Surrogate-vs-canonical diagnostics (from `out/e4/summary.csv`)
- S7 Cross-implementation check and affordability indicators (from `docs/cross_model_check.md`, `out/e5/affordability.csv`)
- S8 Falsifiable claims FC1–FC5: statement, refuting observation, code path, status
