# Capital allocation pathways under transition uncertainty: how much, when, and in what form should heavy industry invest to meet a net-zero pathway?

**Working paper · round R1 · 2026-09-12 (KST) · target: Energy Policy**
Jinsu Park (PLANiT Institute)

> Status line (maintained every round): R0 = skeleton, allocation results from the canonical run `runs/v2_3` (r = 2.4 % real, net-trade carbon, structural hydrogen, verified price factors). Sections marked [R1]…[R7] are to be written or rewritten in that round. Every number cites its source file. Nothing here is final.

---

## Highlights (draft, [R7])

- A firm-level *capital allocation pathway* — how much, when, and in what form (equipment vs. contract) — is derived for four Korean and Japanese steel and petrochemical firms under two IEA-anchored scenarios.
- The pathway is priced with five indicators: aligned capex need, expected transition cost, transition cost at risk and its factor decomposition, policy exposure, and flexibility value.
- Under the stringent scenario the steel capex peak moves forward by 3–11 years at 11–12 % more capital; the technology set does not change.
- In the generated menu the risk-efficient allocation keeps the equipment schedule and adds a fixed-price contract on the electricity the transition adds; whether risk preference also moves equipment earlier is tested with timing-ladder variants [R3].
- Fixed-price power procurement removes 13–64 % of the plan's tail cost for a 0.7–6.2 % increase in expected cost — the cheapest item in the allocation.
- Whether early conversion itself reduces energy-cost exposure depends on the power price regime: with SMP tied to LNG, electrification moves exposure rather than removing it.

## Abstract (draft, [R7])

[R7 — rewrite last.] Firms facing a sector emission pathway must decide how much capital to commit, when, and whether to spend it on equipment or on contracts that transfer price risk. We formalise this as a capital allocation pathway problem: given an exogenous sector pathway downscaled to a firm budget, the set of feasible allocations is generated at facility level and each allocation is valued on a common set of correlated price paths. The allocation is priced with five indicators — aligned capex need, expected transition cost, transition cost at risk (TCaR) with its factor decomposition, policy exposure, and flexibility value — and the efficient allocation is the non-dominated set in (expected cost, expected shortfall). Applied to POSCO, Nippon Steel, LOTTE Chemical and Mitsui Chemicals under NZE- and STEPS-anchored scenarios, we find [R3/R4].

---

## 1. Introduction

A net-zero pathway for heavy industry is, from the firm's side, a capital allocation problem. The sector pathway says how much emission room remains; it does not say which furnace or cracker is replaced, in which year, with which technology, or whether the new energy bill is bought on the spot market or under contract. Those decisions fix the size, timing and risk of the firm's cash outlays, and they are what an investment committee approves and a lender underwrites.

This paper asks one question. **Given a sector emission pathway, what is the financially efficient allocation of capital for a single firm — how much, when, and in what form — and how does price uncertainty change that allocation?** The sector pathway is exogenous (in the final version, the KAIST GCAM pathway for Korea and Japan; in this draft, an IEA-anchored local scenario); the paper decides only how it is translated into a firm budget and how the firm's feasible allocations are generated and valued. "Efficient" is defined on two statistics of the allocation's discounted cost distribution: its mean and its expected shortfall at the 90 % level. The transition cost at risk, TCaR = P90 − P50 of the incremental cost, is reported alongside as the dispersion statistic that does not move when deterministic accounting assumptions move.

The answer is delivered as a *capital allocation pathway* with a five-line price tag: aligned capex need (how much, when), expected transition cost, TCaR and its factor decomposition, policy exposure, and flexibility value. The reader is the firm and the investor underwriting it. The paper does not rank firms, does not estimate a market price of transition risk, and does not claim that the four firms studied represent their sectors.

### 1.1 Where this sits in the literature

Five strands bear on the question; the paper combines pieces that each strand treats separately.

*Investment under climate-policy uncertainty.* The real-options literature established that policy uncertainty delays irreversible abatement investment and that the value of waiting depends on the volatility and mean reversion of the carbon price (Dixit and Pindyck, 1994; Blyth et al., 2007 [확인 필요]; Fuss et al., 2008). Those models optimise the timing of a single representative plant under a stochastic policy price. This paper keeps the policy pathway as a *condition* — two scenarios, no probabilities — and randomises input prices around it; policy stringency enters as indicator ④, the cost of holding one scenario's allocation when the other materialises. The two designs answer different questions: theirs, when to invest given an uncertain carbon price; ours, how to allocate given a pathway the firm has accepted.

*Portfolio and tail-risk methods in energy investment.* Mean–variance portfolio theory has been applied to generation fuel mixes (Roques, Newbery and Nuttall, 2008), and coherent tail measures — expected shortfall / CVaR (Artzner et al., 1999; Rockafellar and Uryasev, 2002) — to stochastic investment programmes. The frontier used here is of that family, with two differences: the "portfolio" is a discrete set of facility-level schedules and contract terms rather than divisible assets, so the frontier is a finite non-dominated set, not a curve; and both physical choices and contracts are placed on the same frontier, so the price of tail removal is read directly as Δμ/ΔES between adjacent allocations.

*Transition risk in asset pricing.* Bolton and Kacperczyk (2021) show a carbon premium in equity returns; Battiston et al. (2017) and Engle et al. (2020) treat transition risk at the portfolio and news-index level. These works price exposure across firms from market data. This paper works one level down — inside the firm, from physical volumes and cost — and produces the cash-flow object those studies would need to explain the premium: the distribution of the transition's cost under a given allocation.

*Industrial decarbonisation pathways.* Technology-level studies of hydrogen direct reduction (Vogl, Åhman and Nilsson, 2018) and the timing of blast-furnace phase-out against reinvestment cycles (Vogl, Olsson and Nykvist, 2021, *Joule*), of steam-cracker electrification (Layritz et al., 2021), and sector reviews (Rissman et al., 2020; Bataille et al., 2018 [확인 필요]) give the technology set, cost ranges and the reinvestment-window logic used in the schedule generator. They are deterministic or scenario-based; they do not price the cost distribution of a firm's schedule, and they do not include contracts.

*Emissions trading and free allocation.* Free allocation to trade-exposed industry shifts the carbon cost from a gross to a net-trade basis (Martin et al., 2014, on the EU ETS). Korea's K-ETS phase 4 and Japan's GX-ETS both allocate to steel and petrochemicals; the paper therefore prices carbon as p·(E − A) with A set by a stated rule, and reports the gross basis as a sensitivity.

### 1.2 Contributions

First, the allocation is generated at facility level over real reinvestment windows by a mixed-integer schedule and then valued — schedule and contracts together — on one set of correlated, mean-normalised price paths whose volatilities and correlations come only from verified series (KPX SMP, JEPX, KAU, World Bank coal and LNG), with hydrogen derived structurally from electricity and construction cost deterministic. Nothing in the reported tail comes from a prior.

Second, the output is the allocation itself, priced. For each firm and scenario the paper reports capex by year, technology and contract share, and the five indicators. The frontier is the instrument that selects among allocations; it is not the result.

Third, the paper states where the design cannot yet speak. The generated menu contains no timing variants for steel, so the effect of risk preference on *equipment* timing is tested only through constructed timing-ladder variants (§5.3); the contract premium is an assumption, so the price of tail removal is conditional on it (§5.2); and the sector pathway is a placeholder until the GCAM pathway is received.

## 2. The capital allocation pathway problem [R2 formalises]

### 2.1 Objects

- Sector pathway (exogenous; KAIST GCAM in the final version, IEA-anchored local scenario in this draft) → firm cumulative Scope-1 budget B_c^s over 2027–2050.
- Allocation x = (facility, technology, adoption year) schedule + contract terms (PPA share on the electricity the transition *adds*, EPC on construction).
- Feasible set A_s: allocations that respect the cumulative budget, technology availability years, reinvestment windows and fixed production.
- Cost C(x, ε): discounted cash cost over 2027–2050 on a price path ε; mean μ(x), expected shortfall ES₉₀(x), and TCaR(x) = q₀.₉ − q₀.₅ of the incremental cost.
- Reference points. The cost axis is reported *incremental* to the no-transition counterfactual x₀ (so that ② is a transition cost), while ES₉₀ is taken on the allocation's *own* absolute cost (so that it is a level of tail cash cost and is monotone in cost dominance). TCaR is shift-invariant, so its reference point is immaterial. [R2 justifies; the manuscript v2.32 §4.2 gives the properties.]

### 2.2 The five indicators (pricing the allocation)

| # | Indicator | Definition | Question it answers | Source column |
|---|---|---|---|---|
| ① | Aligned capex need | Σ_t K_t(x), peak K_t and its year | how much, when | `e5/metrics_company.csv: capex_total_bnkrw, capex_peak_bnkrw, capex_peak_year`; `e4/annual_capital_ledger.csv` |
| ② | Expected transition cost | μ(x) − μ(x₀) (incremental to no-transition counterfactual; carbon on net-trade basis) | how much on average | `mean_bnkrw` |
| ③ | TCaR and decomposition | q₀.₉ − q₀.₅; variance shares by factor | what moves it, by how much | `tcar_bnkrw`, `e5/variance_decomp.csv` |
| ④ | Policy exposure | cost of the *same* allocation revalued under the other scenario (allocation, prices and allowances of the evaluating scenario) | how much hangs on policy stringency | `e5/policy_wedge.csv` |
| ⑤ | Flexibility value | expected cost of the fixed allocation minus expected cost of re-optimising within the generated menu after prices are known (lower bound) | what optionality is worth | `e4/flex_value.csv` |

The efficient allocation is the non-dominated set of A_s in (μ, ES₉₀); a decision-maker's λ picks a point on it (μ + λ·ES₉₀). The ratio Δμ/ΔES₉₀ between two adjacent points is the price of removing one won of tail cost.

## 3. Method (pipeline summary; details in the methodology manuscript v2.32 and its v2.x changelog)

E1 constraints and central prices → E2 mixed-integer schedule generation (CBC, ε-grid on a surrogate risk term; 27 schedules, 270 contract variants) → E3 correlated annual log-price shocks (N = 10,000; mean-normalised around the scenario's central path) → E4 revaluation of every variant on the common paths (cash accounting `cash_v1`, net-trade carbon p·(E−A) with A = the firm's budget path, incremental hedge basis) → E5 statistics, frontier and indicators. Discount rate 2.4 % real (KTB-10y 4.40 % − ~2 % expected inflation, 2026-09-11). Conventions and their audit trail: `config.yaml`, `paper/methodology/TCaR_METHOD_V2_KO.md`.

## 4. Data [R3]

Four firms (POSCO, Nippon Steel, LOTTE Chemical, Mitsui Chemicals), estimated facility portfolios (not the whole company), technology DB (steel: efficiency, H₂-DRI, HyREX; petrochemicals: e-cracker, bio-feed, H₂-fuel), verified price history (KPX SMP, JEPX, KAU 2015–2025, World Bank CMO coal and LNG), IEA GEC 2025 anchors for scenario prices (NZ15 = NZE, B20 = STEPS), K-ETS phase-4 / GX-ETS allocation rules.

## 5. Results — the allocation pathways (R0 numbers; [R3] adds timing-ladder variants and figures)

### 5.1 How much and when (indicator ①)

Table 1. Mean-cost-minimising allocation, canonical run. Source: `paper/cap_pathway/data/allocation_table_v2_3.csv` (built from `runs/v2_3/run/e5/metrics_company.csv`, `e4/annual_capital_ledger.csv`).

| Firm · scenario | Technologies | First adoption | Capex total (bn KRW2025) | Capex peak (bn) | Peak year |
|---|---|---|---|---|---|
| POSCO · NZ15 | eff + H₂-DRI + HyREX | 2027 | 27,843 | 4,777 | 2032 |
| POSCO · B20 | eff + H₂-DRI + HyREX | 2027 | 24,771 | 3,852 | 2043 |
| NSC · NZ15 | eff + H₂-DRI | 2027 | 34,577 | 6,958 | 2034 |
| NSC · B20 | eff + H₂-DRI | 2027 | 31,267 | 4,950 | 2037 |
| LOTTE · NZ15 | e-cracker | 2039 | 2,465 | 708 | 2039 |
| LOTTE · B20 | e-cracker | 2038 | 2,465 | 519 | 2038 |
| MCI · NZ15 | e-cracker | 2034 | 915 | 221 | 2034 |
| MCI · B20 | e-cracker | 2040 | 1,135 | 375 | 2040 |

Reading. The stringency of the pathway does not change the steel technology set; it changes *when* the capital is spent. POSCO's capex peak moves from 2043 (B20) to 2032 (NZ15), NSC's from 2037 to 2034, with 11–12 % more total capital. In petrochemicals the budget is met by a single e-cracker conversion whose timing is set by the budget year (2034–2040); early adoption is never mean-cost-minimising under either scenario. Figure 1 (`figures/fig1_capex_pathway.png`) shows the annual construction outlays.

Capex total = construction (new transition equipment) + maintenance/renewal capex of the retained fleet (`gross_capex_k`); for POSCO · NZ15 the split is 18,626 + 9,216. Figure 1 plots construction only; Table 1 will show both columns [R3].

### 5.2 The price tag (indicators ②, ③, ④, ⑤)

Table 2. Mean-minimising allocation (λ = 0) versus the λ = 1 allocation on the (μ, ES₉₀) frontier. bn KRW2025. Source: same file; `e5/lambda_tangency.csv`, `e5/policy_wedge.csv`, `e4/flex_value.csv`.

| Firm · scen. | ② μ (λ=0) | ES₉₀ (λ=0) | λ=1 allocation | μ (λ=1) | ES₉₀ (λ=1) | Δμ % | ΔES % | Δμ/ΔES | ④ same plan under other scen. (μ incl. carbon) | ⑤ flex (mean) |
|---|---|---|---|---|---|---|---|---|---|---|
| POSCO · NZ15 | 29,409 | 705,214 | same schedule, PPA 1.0 | 30,428 | 593,922 | +3.5 | −15.8 | 0.009 | 88,276 | 0 |
| POSCO · B20 | 68,090 | 507,217 | PPA 1.0 | 68,690 | 439,290 | +0.9 | −13.4 | 0.009 | 18,616 | 0 |
| NSC · NZ15 | 73,530 | 806,947 | PPA 1.0 | 74,946 | 642,132 | +1.9 | −20.4 | 0.009 | 122,303 | 3,194 |
| NSC · B20 | 89,839 | 585,431 | PPA 1.0 | 90,506 | 484,557 | +0.7 | −17.2 | 0.007 | 42,704 | 291 |
| LOTTE · NZ15 | 2,793 | 49,490 | PPA 1.0 | 2,964 | 20,799 | +6.2 | −58.0 | 0.006 | 1,523 | 565 |
| LOTTE · B20 | 4,744 | 50,644 | PPA 1.0 | 4,918 | 22,147 | +3.7 | −56.3 | 0.006 | 979 | 570 |
| MCI · NZ15 | 2,412 | 29,304 | PPA 1.0 | 2,551 | 10,705 | +5.7 | −63.5 | 0.007 | 1,217 | 46 |
| MCI · B20 | 2,170 | 22,742 | PPA 1.0 | 2,245 | 9,976 | +3.5 | −56.1 | 0.007 | 502 | 306 |

Reading. (i) Along the frontier the risk-efficient allocation keeps the *same equipment schedule* and adds a fixed-price contract on the electricity the transition adds; the price of removing one won of ES₉₀ is 0.6–0.9 jeon. This is cheap because the contract premium is a research assumption — PPA at +8 % over the central electricity price, EPC at +10 % over central capex (`config.yaml: contracts`) — and because the hedge applies only to the electricity the transition adds; the ratio is a property of that assumption, not an observed market price of hedging [R4 must say so and vary the premium in R6]. (ii) The tail cut is 13–20 % in steel and 56–64 % in petrochemicals — the petrochemical tail is almost entirely purchased electricity, the steel tail retains coal, hydrogen and residual carbon exposure. (iii) Policy exposure ④: the NZ15 allocation evaluated under B20 prices and allowances, and vice versa; the B20 steel allocations violate the NZ15 budget by 194–242 MtCO₂ cumulative (`budget_gap_tco2`), which is the cost that cannot be bought back. (iv) Flexibility ⑤ is small except NSC · NZ15 (3,194) — the menu contains genuinely different schedules only there and in petrochemicals.

### 5.3 Does uncertainty pull capital forward? [R3 — timing ladder]

In the canonical menu every steel schedule starts in 2027 (the budget binds early) and every petrochemical schedule is a single dated conversion; the menu therefore cannot yet answer whether risk preference moves the *equipment* earlier. R3 constructs timing-ladder variants (adoption ±3, ±6 years where availability and budget allow) and revalues them.

### 5.4 Where the tail comes from (indicator ③ decomposition) [R3]

`e5/variance_decomp.csv` — electricity (including structurally derived hydrogen) and carbon dominate; coal and gas enter with negative signed shares (they are hedges of the transition, not risks). [R3: table.]

## 6. Discussion — what an investor does with this [R4]

[R4.] Funding timing (①); the contract as the cheapest line in the allocation (Δμ/ΔES); when early conversion reduces exposure and when it only relocates it (SMP–LNG linkage; horizon truncation); policy exposure as the non-hedgeable item; comparison with disclosed plans (linear declared-path benchmark, methodology v2.32 §3.5).

## 7. Robustness and limitations [R6]

Discount rate (2.4 / 3.5 / 5 %), GBM vs log-OU (ES level −32 to −38 %, POSCO NZ15 ΔES sign), factor correlation, hydrogen price, carbon accounting (gross vs net-trade), terminal value. Limitations: estimated facility portfolio; correlation from 10–15 annual observations; allocation rule for free allowances; no timing ladder in the generated menu; no CCUS.

## 8. Conclusion [R7]

## References (verified by web search in R1 unless marked)

- Artzner, P., Delbaen, F., Eber, J.-M., Heath, D., 1999. Coherent measures of risk. *Mathematical Finance* 9(3), 203–228.
- Bataille, C., et al., 2018. A review of technology and policy deep decarbonization pathway options for making energy-intensive industry production consistent with the Paris Agreement. *Journal of Cleaner Production* 187, 960–973. [확인 필요]
- Battiston, S., Mandel, A., Monasterolo, I., Schütze, F., Visentin, G., 2017. A climate stress-test of the financial system. *Nature Climate Change* 7, 283–288.
- Blyth, W., Bradley, R., Bunn, D., Clarke, C., Wilson, T., Yang, M., 2007. Investment risks under uncertain climate change policy. *Energy Policy* 35(11), 5766–5773. [확인 필요 — title/authors located, volume unverified]
- Bolton, P., Kacperczyk, M., 2021. Do investors care about carbon risk? *Journal of Financial Economics* 142(2), 517–549.
- Dixit, A.K., Pindyck, R.S., 1994. *Investment under Uncertainty*. Princeton University Press.
- Engle, R.F., Giglio, S., Kelly, B., Lee, H., Stroebel, J., 2020. Hedging climate change news. *Review of Financial Studies* 33(3), 1184–1216.
- Froot, K.A., Scharfstein, D.S., Stein, J.C., 1993. Risk management: coordinating corporate investment and financing policies. *Journal of Finance* 48(5), 1629–1658. [확인 필요 — cited in manuscript v2.32]
- Fuss, S., Szolgayova, J., Obersteiner, M., Gusti, M., 2008. Investment under market and climate policy uncertainty. *Applied Energy* 85(8), 708–721.
- Layritz, L.S., Dolganova, I., Finkbeiner, M., Luderer, G., Penteado, A.T., Ueckerdt, F., Repke, J.-U., 2021. The potential of direct steam cracker electrification and carbon capture & utilization via oxidative coupling of methane as decarbonization strategies for ethylene production. *Applied Energy* 296, 117049.
- Markowitz, H., 1952. Portfolio selection. *Journal of Finance* 7(1), 77–91.
- Martin, R., Muûls, M., de Preux, L.B., Wagner, U.J., 2014. Industry compensation under relocation risk: a firm-level analysis of the EU Emissions Trading Scheme. *American Economic Review* 104(8), 2482–2508.
- Rissman, J., et al., 2020. Technologies and policies to decarbonize global industry: review and assessment of mitigation drivers through 2070. *Applied Energy* 266, 114848.
- Rockafellar, R.T., Uryasev, S., 2002. Conditional value-at-risk for general loss distributions. *Journal of Banking & Finance* 26(7), 1443–1471.
- Roques, F.A., Newbery, D.M., Nuttall, W.J., 2008. Fuel mix diversification incentives in liberalized electricity markets: a mean–variance portfolio theory approach. *Energy Economics* 30(4), 1831–1849.
- Vogl, V., Åhman, M., Nilsson, L.J., 2018. Assessment of hydrogen direct reduction for fossil-free steelmaking. *Journal of Cleaner Production* 203, 736–745. [확인 필요 — cited in manuscript v2.32]
- Vogl, V., Olsson, O., Nykvist, B., 2021. Phasing out the blast furnace to meet global climate targets. *Joule* 5(10), 2646–2662.
- Kampmann et al., 2026; Ostrovnaya et al., 2026 — cited in manuscript v2.32; not verified this round. [확인 필요]

## Reproducibility [R6]

Repository `PLANiT-Institute/cap_finance`; canonical run `tmp/research_case_v2_3` (manifest hashes); `config.yaml`; this paper's tables are regenerated by `paper/cap_pathway/data/*.csv`.
