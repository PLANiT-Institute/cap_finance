# 01. Literature background (EN) — with positioning

> 2026-08-22 04:55 KST, iteration 1; updated 16:55 (iteration 12: the reference list now lives in 03_DRAFT_EN.md §References, 28 entries, 21 marked † for the register). Citations were checked against Crossref / publisher pages by a research sub-agent on 2026-08-21; items marked [unverified] must be confirmed before submission. The repo's own literature map (`docs/literature_map.md`) cites only `source_id`s from `data/raw/source_register.csv`; the references below that are NOT yet in the register are flagged **[REG]** and should be added before the manuscript cites them.

## 0. One-paragraph version (for §2 of the paper)

Three literatures each hold one piece of what this paper assembles, and none holds all three. Transition-plan assessment (CA100+ benchmark, TPI, and the asset-based planning approach of Kampmann et al. 2026) locates disclosed plans in *emissions* space against a carbon budget and explicitly leaves cost unmodelled. Investment-under-uncertainty and risk-efficient portfolio work (Dixit–Pindyck; Fuss et al. 2008; Roques et al. 2008; Ehrenmann & Smeers 2011) supplies the risk axis and the correlated Monte-Carlo machinery, but for generic investors or power systems and never with a disclosed plan as the reference point. Steel and petrochemical cost modelling (Vogl et al. 2018, 2021; IEA 2020; DIW DP 2082) supplies deterministic point costs and the reinvestment-window logic. Our contribution is the combination: one industrial firm's budget-feasible plan set placed in a (expected cost, tail cost-at-risk) plane, with the disclosed plan's distance to the frontier as the diagnostic. The literature is ahead of us in one place — it makes the carbon price stochastic, we make it a scenario — and we measure what that choice costs.

## 1. Corporate transition-plan assessment and credibility

- **Kampmann, Rekker, Ruan, Shrimali et al. (2026)**, "Assessing corporate transition plans using a production asset-based planning approach", *Nature Communications* 17:6410, doi 10.1038/s41467-026-72703-2. — register id `NATCOMM_APA_2026`. Open-source APA: GEM asset data → ownership → firm BAU vs stated-plan trajectories 2020–2050 vs NGFS budgets; 10 utilities + 10 steelmakers incl. POSCO; 3/20 Paris-compatible; 42% of steel assets need reinvestment before 2030. Cost mentioned (BF reline €48/t, H2-DRI-EAF €574/t) but not modelled.
- **Saleh, Battiston, Monasterolo, Barreau, Tankov (2026)**, "Estimating firms' emissions from asset level data helps revealing (mis)alignment to net zero targets", *Nature Communications*, doi 10.1038/s41467-026-70481-5. **[REG]** >950 steel plants; 2030 sector emissions exceed IEA NZE by 10–22% and firms' own targets by 15–28%.
- **Kampmann, Rose, Shrimali (2023)**, *Assessing the Credibility of Climate Transition Plans in the Steel Sector*, Oxford SSEE Discussion Paper. **[REG]** Three-level credibility framework; 30–75% of BF-BOF assets face relining before 2030.
- **AbdulRafiu (2026)**, "Stranded futures? Quantifying the asset risks of industrial decarbonisation in developed economies", *ERSS* 133:104621, doi 10.1016/j.erss.2026.104621. **[REG]** Content [unverified] — full text still blocked (see `docs/data_gap_registry.md`).
- **Bachorz et al. (2026)**, "The window to avoid locking in decades of steel emissions is closing fast", *Nature Climate Change*, doi 10.1038/s41558-026-02634-9. **[REG]** >1,000 plants; committed emissions ≈60 GtCO2 to 2070.
- **CA100+ Net Zero Company Benchmark** (`CA100_BENCHMARK_V22`) and **TPI** methodology v5.0 (2023) **[REG]**: indicator scoring; capital-allocation-alignment indicator exists but does not price the plan.
- **ACCR (2025)** *Steelmakers face crunch-time on coal* (`ACCR_BF_RELINE_2025`): ≈62 BF reline decisions by 2035, 70% in 2026–35, $300m–$1bn per reline.

*Gap:* this strand asks whether a plan is aligned, not what it costs the firm, how dispersed that cost is, or whether the same budget could be met more cheaply or more safely. Petrochemicals are absent at firm level.

## 2. Steel / petrochemical decarbonisation cost modelling

- **Vogl, Åhman, Nilsson (2018)**, *J. Cleaner Production* 203:736–745, doi 10.1016/j.jclepro.2018.08.279 — `VOGL_2018`. H-DR/EAF techno-economics; ≈3.5 MWh/t; competitiveness hinges on electricity and carbon price.
- **Vogl, Olsson, Nykvist (2021)**, "Phasing out the blast furnace to meet global climate targets", *Joule* 5:2646–2662, doi 10.1016/j.joule.2021.09.007. **[REG]** Reinvestment-cycle logic (15–20-yr relines) — our facility windows operationalise this.
- **Hüttel & Lehner (2024)**, *Revisiting Investment Costs for Green Steel*, DIW DP 2082. (Used in `data/raw/tech_bands.csv`; check register id.) Literature ≈€592/t vs announced ≈€751/t; right-skewed capex.
- **Xu, Wang, Jiang, Yu, Wei (2024)**, *J. Environmental Management* 356:120484, doi 10.1016/j.jenvman.2024.120484. **[REG]** Single H2-DRI project timing under multiple uncertainties — closest "steel + uncertainties" valuation.
- **Algers, Åhman, Nilsson (2025)**, *Annual Review of Environment and Resources* 50:433–454. **[REG]** Survey.
- **Fitriasari et al. (2025)**, "Decarbonization Strategies in Naphtha Cracking: … South Korea", *ACS Sustainable Chem. Eng.* 13:9913–9926, doi 10.1021/acssuschemeng.4c09854. **[REG]** Korea-specific cracker options — cross-check LOTTE technology menu.
- Grey: IEA (2020) *Iron and Steel Technology Roadmap*; Material Economics (2019); MPP (2022); Agora Industry (2024). [page details unverified]

*Gap:* point LCOS/CAPEX and sector pathways; no firm-level, facility-level optimisation under a firm budget with correlated uncertainty, and nothing on contract structure as the risk lever.

## 3. Investment under uncertainty / real options with carbon-price uncertainty

- Dixit & Pindyck (1994), *Investment under Uncertainty*, Princeton. **[REG]**
- Laurikka & Koljonen (2006), *Energy Policy* 34:1063–1074. **[REG]**
- Fuss, Szolgayova, Obersteiner, Gusti (2008), *Applied Energy* 85:708–721. **[REG]** Policy uncertainty delays low-carbon investment more than price volatility.
- Zhou et al. (2010), *Applied Energy* 87:2392–2400. **[REG]** CCS timing under stochastic carbon price.
- Heydari, Ovenden, Siddiqui (2010), *Computational Management Science* 9:109–138. **[REG]**

*Gap:* carbon price is a stochastic process and the object is single-project timing. We treat carbon price as a policy-regime scenario and the inputs as correlated draws, for a facility portfolio under a hard budget. The "wait" result reappears in our regret tables — but only when budget overrun is unsanctioned.

## 4. Risk measures in energy / capacity investment

- Awerbuch (2006), *Mitig. Adapt. Strateg. Glob. Change* 11:693–710. **[REG]**
- **Roques, Newbery, Nuttall (2008)**, *Energy Economics* 30:1831–1849, doi 10.1016/j.eneco.2007.11.008. **[REG]** Monte-Carlo NPVs with correlated fuel/electricity/CO2 prices; efficient frontiers; gas–electricity correlation as natural hedge — the conceptual twin of our PPA-share result.
- **Ehrenmann & Smeers (2011)**, *Operations Research* 59:1332–1346. **[REG]** CVaR-based risk-averse capacity expansion.
- Conejo, Carrión, Morales (2010), Springer. **[REG]**
- **Mavrotas (2009)**, AUGMECON ε-constraint, *Appl. Math. Comput.* 213:455–465. **[REG]**

*Gap:* ex-ante portfolios for a generic investor; no disclosed-plan benchmark; no funding-shortfall risk axis; no cross-industry comparison of the frontier slope.

## 5. MACC and its critique

- Kesicki & Strachan (2011), *Environ. Sci. Policy* 14:1195–1204; **Kesicki & Ekins (2012)**, *Climate Policy* 12:219–236, doi 10.1080/14693062.2011.582347. **[REG]** MACCs hide interactions, path dependence and — for us — uncertainty.

*Gap:* no study replaces the MACC with a cost–risk frontier in which risk is a *choice variable* (contracts), not an error band. Our hedge price of risk is the slope of that frontier.

## 6. Transition finance / investor perspective

- Bolton & Kacperczyk (2021), *JFE* 142:517–549; NBER 28510. **[REG]**
- Seltzer, Starks, Zhu (2022), NBER 29994. **[REG]**
- **Dietz, Bowen, Dixon, Gradwell (2016)**, "Climate value at risk of global financial assets", *Nature Climate Change* 6:676–679. **[REG]**
- Battiston, Mandel, Monasterolo, Roncoroni (2023), SSRN 4124002. **[REG]**
- **Fukuda & Ino (2026)**, "Fiscal sustainability of transition finance: … GX economy transition bonds in Japan", *Japan and the World Economy* 79:101368. **[REG]**
- Park (2026), "Carbon Pricing and Industrial Decarbonization: Can Korea's ETS Drive Low-Carbon Investment in Steel?", SSRN 6339967 [unverified content]. **[REG]**

*Gap:* transition risk is priced from market data or top-down scenarios; no bottom-up, plan-specific funding-need-at-risk a lender or GX-bond allocator could underwrite.

## 7. Robust decision making / regret

- Lempert, Popper, Bankes (2003) RAND; Lempert et al. (2006) *Management Science* 52:514–528. **[REG]**
- Hallegatte et al. (2012), World Bank PRWP 6193. **[REG]**
- Rezai & van der Ploeg (2017), *Energy Economics* 68:4–16. **[REG]**

*Gap:* RDM is applied to public policy; our min-max regret is a private firm's disclosed plan vs frontier alternatives across carbon scenarios, and the sign flips on one institutional variable.

## 8. Positioning

| Contribution | Nearest prior work | What we add |
|---|---|---|
| C1 disclosed plan in (P50, TCaR) plane; frontier gap | Kampmann et al. 2026; Saleh et al. 2026 (emissions space); Roques et al. 2008; Ehrenmann & Smeers 2011 (ex-ante risk portfolios) | ex-post benchmark of an actual plan under its own budget; gap split into cost and risk; frontier traced by contracts |
| C2 TCaR as funding language | Dietz et al. 2016; Battiston et al. 2023; CVaR planners; DIW 2082 | tail as *additional funding need* vs the plan's own central case |
| C3 hedge-price asymmetry | Awerbuch/Roques natural hedges; Kesicki & Ekins | frontier slope as sector-specific marginal cost of de-risking (10×); stricter budget lowers tail |

## 9. Referee risks (closest prior work they will cite) and our reply

1. Kampmann et al. 2026 — "APA already covers POSCO." → emissions-only, deterministic; we add cost, uncertainty, frontier, contracts.
2. Roques et al. 2008 — "MV frontier with correlated MC is old." → generic investor, power only, no budget, no disclosed plan, no funding metric.
3. Ehrenmann & Smeers / Conejo — "why P90−P50 not CVaR?" → treasury unit; report CVaR as robustness [TBD].
4. Xu et al. 2024 — "real options for H2-DRI exists." → single project, timing only.
5. Fuss et al. 2008 — "carbon price should be stochastic." → we measured the cost of the scenario choice: +3,064/+2,159 bn KRW in steel, negative in petrochemicals.
6. Hüttel & Lehner 2024 — capex distributions will be checked → our EAF capex sits below the DIW band (§4.6 of working paper); say so.
7. Dietz et al. 2016 — "climate VaR exists." → asset-value top-down vs plan-cost bottom-up.
8. Kesicki & Ekins — "MACC with error bars?" → risk is a choice variable.
9. Vogl 2021 / Bachorz 2026 / ACCR 2025 — reline windows must match their plant data for POSCO and NSC.
10. AbdulRafiu 2026 — obtain and cite.
11. Fukuda & Ino 2026 — map TCaR to GX-ETS compliance.

## 9a. Added in later iterations

- King & Wood Mallesons (2025), Korean PPA regime (third-party 2021-06, direct 2022-09, fee stack, 2025-07 capacity-floor removal) — grey; replace with Electricity Business Act Art. 16-5 and MOTIE notice before submission. **[REG]**
- Japan corporate PPA primary sources (REI 2025; Bird & Bird 2026; Japan Energy Hub 2025) — fetch blocked (robots/403); still `[verify]` in the draft.

## 10. Korean summary / 한국어 요약

문헌은 세 갈래이고 각 갈래가 한 조각씩만 갖고 있다. 전환계획 평가(CA100+, TPI, Kampmann et al. 2026의 APA)는 공시계획을 **배출** 공간에서 탄소예산과 대조하고 비용은 모형화하지 않는다고 적는다. 불확실성 하 투자·위험효율 포트폴리오(Dixit–Pindyck; Fuss 2008; Roques 2008; Ehrenmann & Smeers 2011)는 위험 축과 상관 몬테카를로를 갖지만 대상이 일반 투자자·전력계통이고 공시계획을 참조점으로 쓰지 않는다. 철강·석화 비용모형(Vogl 2018·2021; IEA 2020; DIW 2082)은 결정론적 점 추정과 재투자 창 논리를 준다. 우리 몫은 조합이다. 문헌이 우리보다 앞선 자리는 탄소가격을 확률로 둔다는 점이며, 우리는 그 선택의 비용(철강 TCaR +3,064/+2,159십억원, 석화 음수)을 쟀다. 제출 전 **[REG]** 표시 문헌을 `source_register.csv`에 등록해야 한다.
