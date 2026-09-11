# Capital allocation pathways under transition uncertainty: how much, when, and in what form should heavy industry invest to meet a net-zero pathway?

**Working paper · round R3 · 2026-09-12 (KST) · target: Energy Policy**
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

*Investment under climate-policy uncertainty.* The real-options literature established that uncertainty about the carbon price can delay irreversible abatement investment, with the sign and size of the effect depending on the drift, volatility and mean reversion of the policy price (Dixit and Pindyck, 1994; Blyth et al., 2007 [확인 필요]; Fuss et al., 2008). Those models optimise the timing of a single representative plant under a stochastic policy price. This paper keeps the policy pathway as a *condition* — two scenarios, no probabilities — and randomises input prices around it; policy stringency enters as indicator ④, the cost of holding one scenario's allocation when the other materialises. The two designs answer different questions: theirs, when to invest given an uncertain carbon price; ours, how to allocate given a pathway the firm has accepted.

*Portfolio and tail-risk methods in energy investment.* Mean–variance portfolio theory has been applied to generation fuel mixes (Roques, Newbery and Nuttall, 2008), and coherent tail measures — expected shortfall / CVaR (Artzner et al., 1999; Rockafellar and Uryasev, 2002) — to stochastic investment programmes. The frontier used here is of that family, with two differences: the "portfolio" is a discrete set of facility-level schedules and contract terms rather than divisible assets, so the frontier is a finite non-dominated set, not a curve; and both physical choices and contracts are placed on the same frontier, so the price of tail removal is read directly as Δμ/ΔES between adjacent allocations.

*Transition risk in asset pricing.* Bolton and Kacperczyk (2021) show a carbon premium in equity returns; Battiston et al. (2017) and Engle et al. (2020) treat transition risk at the portfolio and news-index level. These works price exposure across firms from market data. This paper works one level down — inside the firm, from physical volumes and cost — and produces the cash-flow object those studies would need to explain the premium: the distribution of the transition's cost under a given allocation.

*Industrial decarbonisation pathways.* Technology-level studies of hydrogen direct reduction (Vogl, Åhman and Nilsson, 2018) and the timing of blast-furnace phase-out against reinvestment cycles (Vogl, Olsson and Nykvist, 2021, *Joule*), of steam-cracker electrification (Layritz et al., 2021), and sector reviews (Rissman et al., 2020; Bataille et al., 2018 [확인 필요]) give the technology set, cost ranges and the reinvestment-window logic used in the schedule generator. They are deterministic or scenario-based; they do not price the cost distribution of a firm's schedule, and they do not include contracts.

*Emissions trading and free allocation.* Free allocation to trade-exposed industry shifts the carbon cost from a gross to a net-trade basis (Martin et al., 2014, on the EU ETS). Korea's K-ETS phase 4 and Japan's GX-ETS both allocate to steel and petrochemicals; the paper therefore prices carbon as p·(E − A) with A set by a stated rule, and reports the gross basis as a sensitivity.

### 1.2 Contributions

First, the allocation is generated at facility level over real reinvestment windows by a mixed-integer schedule and then valued — schedule and contracts together — on one set of correlated, mean-normalised price paths whose volatilities and correlations come only from verified series (KPX SMP, JEPX, KAU, World Bank coal and LNG), with hydrogen derived structurally from electricity and construction cost deterministic. Nothing in the reported tail comes from a prior.

Second, the output is the allocation itself, priced. For each firm and scenario the paper reports capex by year, technology and contract share, and the five indicators. The frontier is the instrument that selects among allocations; it is not the result.

Third, the paper states where the design cannot yet speak. The generated menu contains no timing variants for steel, so the effect of risk preference on *equipment* timing is tested only through constructed timing-ladder variants (§5.3); the contract premium is an assumption, so the price of tail removal is conditional on it (§5.2); and the sector pathway is a placeholder until the GCAM pathway is received.

## 2. The capital allocation pathway problem

### 2.1 Setting

A firm c operates facilities f ∈ F_c (blast furnaces, crackers) over years t ∈ T = {2027, …, 2050}. A scenario s supplies, exogenously, (i) a central price path p^s_t for electricity, renewable-procured electricity, coal, gas and carbon, with the hydrogen price derived structurally from electricity (p^H_t = 52 kWh/kg · p^E_t + electrolyser amortisation); (ii) technology availability years; and (iii) a sector emission pathway that is downscaled to a firm cumulative Scope-1 budget B^s_c = Σ_t B^s_{c,t}. In this draft the downscaling is the emission-share rule of the local scenario; in the final version it is the KAIST GCAM pathway. The paper takes B^s_c as given and does not optimise across firms.

An **allocation** is a pair x = (z, h): a schedule z = {z_{f,k,τ}} ∈ {0,1} of technology k adopted at facility f in year τ, subject to reinvestment windows and build times, and a contract vector h = (h^{PPA}, h^{EPC}) where h^{PPA} ∈ [0,1] is the share of the electricity the transition *adds* that is bought at a fixed price, and h^{EPC} ∈ {0,1} fixes construction cost. Contracts change neither emissions nor budget feasibility, so the feasible set factorises,

A_s = Z_s × H,   Z_s = { z : Σ_t E_t(z) ≤ B^s_c, availability, windows, fixed production },

and the frontier can be traced schedule by schedule. This factorisation is what lets the paper put equipment and contracts on the same frontier without a joint stochastic programme.

The discounted cash cost of an allocation on a price path ε is

C(x, ε) = Σ_t d_t [ K_t(z)(1 + h^{EPC}π_K) + Σ_j Q_{j,t}(z) · p^s_{j,t} · ε_{j,t}^{(h)} + p^{CO₂,s}_t ε^{CO₂}_t (E_t(z) − A^s_t) + O_t(z) ] − d_T V_T(z),   d_t = (1 + r)^{−(t − t₀)},

where Q_{j,t} are purchased volumes of input j, ε_{j,t} are multiplicative price shocks with E[ε_{j,t}] = 1 and correlated log-innovations, ε^{(h)} denotes that the hedged share of added electricity carries a fixed price (1 + π_E) instead of the shock, A^s_t is free allocation under the stated rule, O_t other operating cost, V_T a terminal proxy, and r a real risk-free rate. Because the shocks are mean-normalised and enter linearly, **E[C(x, ε)] = C(x, 1)**: the expected cost equals the central-price cost (methodology manuscript v2.32, Proposition 7). The mean therefore carries the scenario; the shocks carry only dispersion around it.

### 2.2 Three statistics and their reference points

Let L(x) = C(x) − C(x₀) be the cost incremental to the no-transition counterfactual x₀ (which does not meet the budget; it is a reference, not an option). The paper reports

- μ(x) = E[L(x)] — expected transition cost (indicator ②);
- TCaR(x) = q₀.₉(L) − q₀.₅(L) — the upper dispersion of the incremental cost (indicator ③);
- ES₉₀(x) = E[C(x) | C(x) ≥ q₀.₉(C(x))] — expected shortfall of the allocation's *own* absolute cost.

The reference points differ deliberately. TCaR is invariant to adding any constant (v2.32, Proposition 1), so it is the same whether computed on L or on C; it isolates dispersion from level and is unchanged by deterministic accounting choices (terminal value, book write-offs, contract premia). ES is not shift-invariant, and computing it on L would subtract a *random* baseline: since x₀ is exposed to coal and carbon, an allocation that removes that exposure moves *away* from x₀ in every state, and ES(L) would read the removal of exposure as risk — the defect that motivated the current convention (audit finding A1, 2026-09-10). ES on C(x) has the two properties the allocation problem needs: it is monotone (C(x) ≤ C(y) statewise ⇒ ES(x) ≤ ES(y)) and it is coherent (Artzner et al., 1999), so "the allocation lowers tail cash cost" is a well-defined statement, ES₉₀(x) < ES₉₀(x₀), and the sum of firm-level ES bounds the tail of a portfolio that shares the same price paths (subadditivity; methodology v2.x, Proposition 8). Because ES(x) − ES(x₀) mixes a level shift with a dispersion change, the deviation form ES₉₀(x) − E[C(x)] is reported alongside when the question is dispersion rather than level.

### 2.3 Efficient allocation and the price of tail removal

The efficient set is the non-dominated subset of the evaluated allocations,

F_s = { x ∈ A_s : ∄ y ∈ A_s with μ(y) ≤ μ(x), ES₉₀(y) ≤ ES₉₀(x), (μ(y), ES₉₀(y)) ≠ (μ(x), ES₉₀(x)) },

computed after removing allocations that are dominated state by state on the sampled paths (a sampled-dominance filter). A decision-maker with risk weight λ ≥ 0 selects argmin_{x∈F_s} μ(x) + λ·ES₉₀(x). Because ES is monotone, this rule never selects an allocation that is worse in every state; the same rule on TCaR can (v2.32, Proposition 6), which is why TCaR is reported but not used for selection.

Between two adjacent points a, b on F_s with μ(b) > μ(a) and ES(b) < ES(a), the ratio

π(a → b) = [μ(b) − μ(a)] / [ES₉₀(a) − ES₉₀(b)]

is the price of removing one won of tail cost by moving from a to b. It is the object an investor compares with its own λ, or with the cost of hedging the same exposure in a market. In the results the moves along the frontier are of two kinds — a contract added to the same schedule, or a different schedule — and π is reported for each.

### 2.4 When does uncertainty change the allocation?

Two levers move an allocation along the frontier.

*Contracts.* Fixing the price of a share h of added electricity Q^+_t raises the mean by the premium, Δμ = Σ_t d_t h Q^+_t p^E_t π_E, and lowers ES by removing the hedged share's contribution to the upper tail. Because the hedged share replaces a fraction h of one common shock by a constant, both the premium and the tail reduction are *linear* in h on the evaluated grid (§5.2, Fig. 3), so the price of tail removal π is constant in h and the efficient contract is bang-bang: fully contracted if π < λ, uncontracted otherwise. With the research premium used here (π_E = 8 %), π is below 1 jeon per won for every firm (§5.2), so the λ = 1 allocation is fully contracted; the result is conditional on π_E, and §7 reports the premium at which the contract leaves the frontier.

*Timing.* Advancing adoption of technology k by Δτ years changes the mean by the discounted capex brought forward, less the central-price operating difference over the advanced years, and changes the tail by exchanging the incumbent's exposure for the new technology's exposure over those years. Writing σ² for the variance of a year's energy-plus-carbon bill under the two configurations,

earlier adoption lowers ES only if  Var[ bill_new ] < Var[ bill_old ] on the advanced years, i.e. (Q^E σ_E)² + cross terms  <  (Q^{coal} σ_coal)² + (E − A)² σ²_{CO₂} + cross terms.

This is an empirical condition, not a theorem. In Korea the system marginal price is tied to LNG (electricity–LNG log-return correlation 0.905 in the verified series), so σ_E is the largest volatility in the factor set; electrification can therefore *relocate* exposure from coal and carbon to electricity rather than reduce it, unless the added electricity is contracted. The hypothesis "faster transition prepares the firm against energy cost" is thus, within this model, the hypothesis that *transition plus fixed-price procurement* lowers ES, and it is tested on constructed timing variants in §5.3.

### 2.5 The five indicators, formally

| # | Indicator | Definition | Notes |
|---|---|---|---|
| ① | Aligned capex need | K(x) = Σ_t K_t(z); peak max_t K_t and its year; construction vs. renewal split | `e5/metrics_company.csv`, `e4/annual_capital_ledger.csv` |
| ② | Expected transition cost | μ(x) = E[L(x)] = L(x, 1) | equals central-price incremental cost |
| ③ | TCaR and decomposition | q₀.₉(L) − q₀.₅(L); variance shares from freezing one factor at its central path (hydrogen folded into electricity) | `e5/variance_decomp.csv` |
| ④ | Policy exposure | W(x; s→s′) = μ_{s′}(x) − min_{y∈A_{s′}} μ_{s′}(y), the regret of holding x when s′ materialises, evaluated with s′'s prices, allowances and hedge reference; plus the budget gap G(x; s′) = Σ_t max(E_t(z) − B^{s′}_{c,t}, 0) | asymmetric by construction; both directions reported |
| ⑤ | Flexibility value | Φ = μ(x*) − E[ min_{y∈Z_s} L(y, ε) ], the gain from re-optimising within the generated menu after prices are known | perfect-information over a finite menu: a lower bound on option value, not a real-options value (v2.32 §5.4) |

### 2.6 Discounting and the separation of level and risk

The rate r is a real risk-free rate (2.4 %: KTB-10y 4.40 % less ≈ 2 % expected inflation, 2026-09-11). Discounting at a WACC and then penalising the tail with λ·ES would count systematic risk twice; here the mean is the expected cash cost under the physical measure and risk enters once, through ES. The choice moves the level of every number (§7 reports 3.5 % and 5 %) but not the ranking of allocations in the canonical run.

## 3. Method (pipeline summary; details in the methodology manuscript v2.32 and its v2.x changelog)

E1 constraints and central prices → E2 mixed-integer schedule generation (CBC, ε-grid on a surrogate risk term; 27 schedules, 270 contract variants) → E3 correlated annual log-price shocks (N = 10,000; mean-normalised around the scenario's central path) → E4 revaluation of every variant on the common paths (cash accounting `cash_v1`, net-trade carbon p·(E−A) with A = the firm's budget path, incremental hedge basis) → E5 statistics, frontier and indicators. Discount rate 2.4 % real (KTB-10y 4.40 % − ~2 % expected inflation, 2026-09-11). Conventions and their audit trail: `config.yaml`, `paper/methodology/TCaR_METHOD_V2_KO.md`.

## 4. Data

**Firms and facilities (D1).** POSCO and Nippon Steel (steel), LOTTE Chemical and Mitsui Chemicals (petrochemicals). Facility portfolios are *estimated* from public capacity, production and emission disclosures allocated to units; they are not the whole company and not measured unit data (methodology v2.32 §6.2–6.3; the facility-level inputs are confidential and are not part of the public repository). Production is held fixed over the horizon.

**Technology options (D3).** Steel: efficiency retrofit, hydrogen direct reduction (H₂-DRI), HyREX; petrochemicals: e-cracker, bio-feed, hydrogen fuel. CCUS is excluded by design decision (2026-08-06). Cost bands and availability years are from the technology register with evidence tiers; the register's known weaknesses (a heat double-count in `petchem_h2fuel`, tier labels assigned per source row) are carried as limitations (§7).

**Scenario anchors (D2).** Two scenarios: NZ15, anchored on IEA GEC 2025 NZE advanced-economy carbon and fuel prices; B20, anchored on IEA STEPS. Electricity central paths and the firm budgets are local EST_v0 interpolations pending the KAIST GCAM pathway. The 2026 Korean carbon anchor is the KAU volume-weighted average traded on KRX, 21,073 KRW/t (2 Jan–10 Sep 2026). Hydrogen is not a scenario input: p^H_t = 52 kWh/kg × p^E_t + electrolyser amortisation (IEA Global Hydrogen Review 2024 anchor, 2,916,000 KRW/kW, no decline assumed).

**Price history for calibration (D4).** Annual log-returns of KPX SMP (Korea) and JEPX system price (Japan) for electricity; KAU annual averages 2015–2025 (NABO; KRX) for carbon; World Bank Commodity Price Data (Australian coal, Japan LNG) for fuels. Innovation standard deviations and the pairwise correlation matrix are estimated from these series only (electricity–LNG 0.905, electricity–coal 0.843, 10–15 overlapping years). Construction cost is deterministic. Source: `runs/v2_3/run/e3/price_model.json`.

**Carbon accounting (D5).** Net-trade basis p·(E − A). A follows a stated rule — the firm's scenario budget path — as a proxy for K-ETS phase-4 free allocation to trade-exposed sectors and GX-ETS target-based allocation; it is not a published firm-level allocation. Gross p·E is reported as a sensitivity (§7).

**Contracts.** PPA on the electricity the transition adds, at central price + 8 %; EPC on construction at central capex + 10 %. Both premia are research assumptions (`config.yaml: contracts`), varied in §7.

**Simulation.** N = 10,000 paths, seed fixed, common paths for all allocations of a firm and scenario; α = 0.9 for TCaR and ES; r = 2.4 % real. Canonical run manifest: `tmp/research_case_v2_3/run/run_manifest.json`.

## 5. Results — the allocation pathways

### 5.1 How much and when (indicator ①)

Table 1. Mean-cost-minimising allocation, canonical run. Source: `paper/cap_pathway/data/allocation_table_v2_3.csv` (built from `runs/v2_3/run/e5/metrics_company.csv`, `e4/annual_capital_ledger.csv`).

| Firm · scenario | Technologies | First adoption | Capex total (bn KRW2025) | of which construction | Capex peak (bn) | Peak year |
|---|---|---|---|---|---|---|
| POSCO · NZ15 | eff + H₂-DRI + HyREX | 2027 | 27,843 | 18,626 | 4,777 | 2032 |
| POSCO · B20 | eff + H₂-DRI + HyREX | 2027 | 24,771 | [R6] | 3,852 | 2043 |
| NSC · NZ15 | eff + H₂-DRI | 2027 | 34,577 | 28,182 | 6,958 | 2034 |
| NSC · B20 | eff + H₂-DRI | 2027 | 31,267 | [R6] | 4,950 | 2037 |
| LOTTE · NZ15 | e-cracker | 2039 | 2,465 | 1,417 | 708 | 2039 |
| LOTTE · B20 | e-cracker | 2038 | 2,465 | [R6] | 519 | 2038 |
| MCI · NZ15 | e-cracker | 2034 | 915 | 613 | 221 | 2034 |
| MCI · B20 | e-cracker | 2040 | 1,135 | [R6] | 375 | 2040 |

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

### 5.3 Does uncertainty pull capital forward? — the timing ladder

The generated menu has no timing variants for steel (every schedule starts in 2027 because the budget binds early) and a single dated conversion for each petrochemical firm, so the frontier in §5.2 cannot by itself say whether risk preference moves *equipment* earlier. To test the §2.4 condition directly, each mean-minimising schedule was shifted by −6, −3, +3 and +6 years (all adoption years moved together, clipped at technology availability and the horizon) and revalued on the same 10,000 paths with the same contract grid. Source: `paper/cap_pathway/data/timing_ladder_results.csv` (run `runs/v2_3_ladder`, E5 only; 32 variants P0028–P0059).

Table 3. Effect of shifting the canonical schedule, spot power (PPA 0). ES₉₀ and μ in bn KRW2025; "dev" = ES₉₀ − E[C], the dispersion part.

| Firm · scen. | shift | budget | Δμ | ES₉₀ (canonical → shifted) | dev (canonical → shifted) |
|---|---|---|---|---|---|
| POSCO · NZ15 | −6 | ok | +17,553 | 705,214 → 756,197 | 479,497 → 512,927 |
| POSCO · NZ15 | +6 | **violated** | −15,224 | 705,214 → 624,057 | 479,497 → 413,564 |
| NSC · NZ15 | −6 | ok | +44,639 | 806,947 → 911,031 | 542,338 → 601,782 |
| NSC · NZ15 | +6 | **violated** | −34,665 | 806,947 → 672,843 | 542,338 → 442,899 |
| LOTTE · NZ15 | −6 | ok | +2,058 | 49,490 → 63,598 | 37,034 → 49,083 |
| LOTTE · NZ15 | +6 | **violated** | −1,303 | 49,490 → 33,525 | 37,034 → 22,372 |
| MCI · NZ15 | −6 | ok | +1,406 | 29,304 → 34,567 | 22,279 → 26,137 |
| MCI · NZ15 | +6 | **violated** | −1,014 | 29,304 → 21,440 | 22,279 → 15,430 |

(B20 rows and the ±3 steps are in the data file; every cell has the same sign pattern.)

Three facts, all eight cells. (i) Earlier adoption raises expected cost *and* raises the tail, in both the absolute and the dispersion form — the §2.4 variance condition fails: the new bill (electricity, and hydrogen made from it) is more dispersed than the bill it replaces (coal, gas, and a carbon bill that is small on the net-trade basis). (ii) Later adoption lowers both statistics but violates the cumulative budget; the canonical schedule is therefore not a compromise on the frontier, it is the *earliest feasible point at which the budget binds*, and no evaluated earlier variant is non-dominated. (iii) Under full contracting (PPA 1.0) the pattern is the same in sign but roughly one third the size in the dispersion part (data file, `ppa = 1`), i.e. the contract removes most of what earlier adoption adds.

Within this model, then, uncertainty does not pull equipment forward. What it does is make the *contract* on the added electricity the efficient complement of any schedule (Fig. 3). The result depends on two things the paper cannot change and must state: the verified volatility ordering (σ_E is the largest in the factor set because Korean SMP is tied to LNG), and the 2027–2050 horizon, under which earlier electrification means more exposure-years inside the window and later electrification means fewer (§7 treats a terminal-value correction).

### 5.4 Where the tail comes from (indicator ③ decomposition)

Table 4. Signed variance shares of the mean-minimising allocation (spot power). Freezing one factor at its central path; hydrogen is folded into electricity because it is derived from it. Negative shares are factors that move against the plan's other costs (hedges by construction). Source: `paper/cap_pathway/data/variance_decomp_selected.csv` from `runs/v2_3/run/e5/variance_decomp.csv`.

| Firm · scen. | electricity (+H₂) | carbon | coal | gas |
|---|---|---|---|---|
| POSCO · NZ15 | 0.28 | 0.58 | −0.06 | 0.00 |
| POSCO · B20 | 0.64 | 0.15 | −0.25 | −0.01 |
| NSC · NZ15 | 0.36 | 0.48 | −0.09 | 0.00 |
| NSC · B20 | 0.68 | 0.11 | −0.27 | −0.01 |
| LOTTE · NZ15 | 0.83 | 0.10 | 0.00 | −0.10 |
| LOTTE · B20 | 0.97 | −0.01 | 0.00 | −0.21 |
| MCI · NZ15 | 0.88 | 0.05 | 0.00 | −0.08 |
| MCI · B20 | 0.97 | 0.00 | 0.00 | −0.18 |

Petrochemical tails are electricity; that is why the contract removes 56–64 % of ES there (Table 2). Steel tails are electricity under B20 and *carbon* under NZ15 — the residual blast-furnace emissions priced at NZE carbon prices net of a shrinking allocation — which no power contract touches; that is why the contract removes only 13–20 % of steel ES, and why the steel tail under the stringent scenario is a policy exposure as much as a market one.

### 5.5 Contract grid

ES₉₀ falls linearly in the hedged share h for every schedule (Fig. 3, `figures/fig3_contract_grid.png`): for LOTTE · B20, 50,644 → 43,396 → 36,184 → 29,049 → 22,147 at h = 0, 0.25, 0.5, 0.75, 1. The premium is linear in h by construction, so the price of tail removal π is constant along the contract axis and the efficient contract is all-or-nothing (§2.4). The frontier's contract points are therefore the two ends, h = 0 (λ below π) and h = 1 (λ above π); intermediate shares appear only as ties.

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
