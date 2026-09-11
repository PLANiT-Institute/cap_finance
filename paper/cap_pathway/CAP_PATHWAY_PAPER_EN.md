# Capital allocation pathways under transition uncertainty: how much, when, and in what form should heavy industry invest to meet a net-zero pathway?

**Working paper v0.7 · 2026-09-12 · prepared for submission to Energy Policy**
Jinsu Park (PLANiT Institute, Seoul)

> Results are from the canonical run `runs/v2_3` (r = 2.4 % real, net-trade carbon, structural hydrogen, verified price factors) unless a table states otherwise; every number cites its source file. Eight review rounds (2026-09-12, `ROUNDS.md`) including three adversarial referee reports shaped this draft; open items are listed in §7.4 and §8.

---

## Highlights

- A firm-level capital allocation pathway — how much, when, and in what form (equipment or contract) — is derived for four Korean and Japanese steel and petrochemical firms under NZE- and STEPS-anchored scenarios, and priced with five indicators.
- The emission budget, not risk preference, fixes the equipment schedule: under the stringent scenario the steel capex peak moves 3–11 years earlier at 11–12 % more capital, and no earlier-adoption variant is non-dominated.
- On the allocation's own cost the tail is electricity in every case (85–100 % of variance); a fixed-price contract on the electricity the transition adds removes 56–64 % of ES₉₀ in petrochemicals and 13–20 % in steel, at 0.4–2.0 % of expected cost under an assumed 8 % premium.
- Under the stringent scenario the contracted allocation has a lower tail than standing still (ES ratio 0.79–0.87; dispersion ratio 0.42–0.69) — but the level result is entirely the carbon price on the counterfactual; with STEPS carbon prices in the same fuel world the ratios exceed one for all four firms.
- The case for transition is the carbon price and the compliance budget; energy-cost insurance comes from procurement contracts, not from earlier capex, and for steel the contract does not bring the tail below the unconverted furnace's unless carbon is expensive.

## Abstract

Meeting a sector emission pathway is, for a firm, a capital allocation problem: how much to commit, when, and whether to spend it on equipment or on contracts that transfer price risk. We formalise this as a capital allocation pathway. Given an exogenous pathway downscaled to a firm's cumulative Scope-1 budget, feasible allocations are generated at facility level by a mixed-integer schedule over reinvestment windows; because contracts do not change emissions, the feasible set factorises into schedules and contract terms and both can be placed on one frontier. Every allocation is valued on a common set of 10,000 correlated, mean-normalised price paths whose volatilities and correlations come only from verified series (KPX SMP, JEPX, KAU, World Bank coal and LNG), with hydrogen derived from electricity. The allocation is priced with five indicators — aligned capex need, expected transition cost, transition cost at risk with its factor decomposition, policy exposure, and flexibility value — and the efficient allocation is the non-dominated set in (expected incremental cost, expected shortfall of the allocation's own cost). Applied to POSCO, Nippon Steel, LOTTE Chemical and Mitsui Chemicals, we find that the budget fixes the schedule and stringency changes its timing rather than the technology set; that earlier adoption raises both expected cost and tail cost within the horizon; that the tail of every allocation's own cost is electricity, so a fixed-price contract on the added load is the only lever that reduces dispersion; and that the contracted allocation has a lower tail than the no-transition counterfactual under the stringent scenario only because of the carbon price on the counterfactual. The case for transition is the carbon price and the compliance budget; energy-cost insurance is a procurement decision. We state where the design cannot yet speak: wholesale rather than tariff electricity volatility, a proxy free-allocation rule, an assumed contract premium, and a 2027–2050 window.

**Keywords:** capital allocation; transition risk; expected shortfall; transition cost at risk; corporate PPA; steel; petrochemicals; K-ETS; GX-ETS.

## 1. Introduction

A net-zero pathway for heavy industry is, from the firm's side, a capital allocation problem. The sector pathway says how much emission room remains; it does not say which furnace or cracker is replaced, in which year, with which technology, or whether the new energy bill is bought on the spot market or under contract. Those decisions fix the size, timing and risk of the firm's cash outlays, and they are what an investment committee approves and a lender underwrites.

This paper asks one question. **Given a sector emission pathway, what is the financially efficient allocation of capital for a single firm — how much, when, and in what form — and how does price uncertainty change that allocation?** The sector pathway is exogenous (in the final version, the KAIST GCAM pathway for Korea and Japan; in this draft, an IEA-anchored local scenario); the paper decides only how it is translated into a firm budget and how the firm's feasible allocations are generated and valued. "Efficient" is defined on two statistics of the allocation's discounted cost distribution: its mean and its expected shortfall at the 90 % level. The transition cost at risk, TCaR = P90 − P50 of the allocation's own cost, is reported alongside as the dispersion statistic that does not move when deterministic accounting assumptions move.

The answer is delivered as a *capital allocation pathway* with a five-line price tag: aligned capex need (how much, when), expected transition cost, TCaR and its factor decomposition, policy exposure, and flexibility value. The reader is the firm and the investor underwriting it. The paper does not rank firms, does not estimate a market price of transition risk, and does not claim that the four firms studied represent their sectors.

### 1.1 Where this sits in the literature

Five strands bear on the question; the paper combines pieces that each strand treats separately.

*Investment under climate-policy uncertainty.* The real-options literature established that uncertainty about the carbon price can delay irreversible abatement investment, with the sign and size of the effect depending on the drift, volatility and mean reversion of the policy price (Dixit and Pindyck, 1994; Blyth et al., 2007 [확인 필요]; Fuss et al., 2008). Those models optimise the timing of a single representative plant under a stochastic policy price. This paper keeps the policy pathway as a *condition* — two scenarios, no probabilities — and randomises input prices around it; policy stringency enters as indicator ④, the cost of holding one scenario's allocation when the other materialises. The two designs answer different questions: theirs, when to invest given an uncertain carbon price; ours, how to allocate given a pathway the firm has accepted.

*Portfolio and tail-risk methods in energy investment.* Mean–variance portfolio theory has been applied to generation fuel mixes (Roques, Newbery and Nuttall, 2008), and coherent tail measures — expected shortfall / CVaR (Artzner et al., 1999; Rockafellar and Uryasev, 2002) — to stochastic investment programmes. The frontier used here is of that family, with two differences: the "portfolio" is a discrete set of facility-level schedules and contract terms rather than divisible assets, so the frontier is a finite non-dominated set, not a curve; and both physical choices and contracts are placed on the same frontier, so the price of tail removal is read directly as Δμ/ΔES between adjacent allocations.

*Transition risk in asset pricing.* Bolton and Kacperczyk (2021) show a carbon premium in equity returns; Battiston et al. (2017) and Engle et al. (2020) treat transition risk at the portfolio and news-index level. These works price exposure across firms from market data. This paper works one level down — inside the firm, from physical volumes and cost — and produces the cash-flow object those studies would need to explain the premium: the distribution of the transition's cost under a given allocation.

*Industrial decarbonisation pathways.* Technology-level studies of hydrogen direct reduction (Vogl, Åhman and Nilsson, 2018) and the timing of blast-furnace phase-out against reinvestment cycles (Vogl, Olsson and Nykvist, 2021, *Joule*), of steam-cracker electrification (Layritz et al., 2021), and sector reviews (Rissman et al., 2020; Bataille, 2020) give the technology set, cost ranges and the reinvestment-window logic used in the schedule generator. They are deterministic or scenario-based; they do not price the cost distribution of a firm's schedule, and they do not include contracts.

*Emissions trading and free allocation.* Free allocation to trade-exposed industry shifts the carbon cost from a gross to a net-trade basis (Martin et al., 2014, on the EU ETS). Korea's K-ETS phase 4 and Japan's GX-ETS both allocate to steel and petrochemicals; the paper therefore prices carbon as p·(E − A) with A set by a stated rule, and reports the gross basis as a sensitivity.

### 1.2 Contributions and what is not claimed

The contribution is threefold, and narrower than the five-indicator apparatus might suggest. First, a joint frontier: facility-level equipment schedules and procurement contracts are valued on the same physical volumes, price paths and accounting boundary, so the price of removing one won of tail cost is read directly as Δμ/ΔES between adjacent allocations, and the factorisation of the feasible set (contracts do not change emissions) is what makes this tractable without a joint stochastic programme. Second, an exposure-relocation result: on verified price series the transition replaces a coal-and-carbon bill with an electricity bill whose volatility is the largest in the factor set, so earlier equipment does not reduce the tail and only procurement does. Third, a decomposition of the case for transition: separating the carbon path from the fuel path within one scenario shows that the tail advantage of the transition over standing still is the carbon price, not energy-cost insurance.

The indicators themselves are reporting conventions, not inventions: ① is a capex path; ② is a central-price NPV (the mean-normalised shocks leave it unchanged); ③ is a Monte-Carlo dispersion statistic with a leave-one-out decomposition; ④ is scenario regret (Loulou and Kanudia, 1999); ⑤ is an expected value of perfect information over a finite menu. The paper does not rank firms — the four cases are cases, and each table is to be read within a firm; it does not estimate a market price of transition risk (it assumes a contract premium and says so); and it does not claim that the generated menu is the firm's full feasible set.

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

- μ(x) = E[L(x)] — expected transition cost (indicator ②), i.e. the *level* of the transition's cost relative to standing still;
- ES₉₀(x) = E[C(x) | C(x) ≥ q₀.₉(C(x))] — expected shortfall of the allocation's *own* absolute cost, the tail level a treasury has to be able to fund;
- TCaR(x) = q₀.₉(C(x)) − q₀.₅(C(x)) — the upper dispersion of the same absolute cost (indicator ③), reported alongside ES because it is invariant to constant shifts (deterministic accounting choices: terminal value, book write-offs, contract premia) while ES is not.

Two bases are therefore in use and must not be confused. The *level* statistic ② is incremental because "how much does the transition cost" is a question about a difference. The *risk* statistics ES and TCaR are computed on C(x), not on L, for a reason that is not cosmetic: x₀ is itself random (it is exposed to coal, gas and carbon), so any statistic of L inherits the dispersion of x₀. Constant-shift invariance (manuscript v2.32, Proposition 1) says nothing about subtracting a random variable, and the paper does not claim it does — TCaR(L) and TCaR(C) differ (for POSCO · NZ15, 166,558 vs 234,216 bn KRW). An ES on L would read the removal of x₀'s coal-and-carbon exposure as *risk added*, which is the defect that motivated the current convention (audit finding A1, 2026-09-10). ES on C(x) has the two properties the allocation problem needs: it is monotone (C(x) ≤ C(y) statewise ⇒ ES(x) ≤ ES(y)) and coherent (Artzner et al., 1999), so "the allocation lowers tail cash cost" is a well-defined comparison of levels, ES₉₀(x) < ES₉₀(x₀), and the sum of firm-level ES bounds the tail of a portfolio on the same price paths (subadditivity; methodology v2.x, Proposition 8 — near equality here, since the four firms load on the same electricity and LNG paths, so the bound is tight rather than informative).

Because ES(x) − ES(x₀) mixes a level shift with a dispersion change, the paper also reports the deviation form D(x) = ES₉₀(C(x)) − E[C(x)] wherever the question is dispersion rather than level (Tables 3, 6). D is a deviation measure in the sense of Rockafellar, Uryasev and Zabarankin (2006): shift-invariant and positively homogeneous, but neither monotone nor coherent, so it is a descriptive companion, not a selection criterion. The variance decomposition (indicator ③) is likewise reported on both bases, because they answer different questions (§5.4).

### 2.3 Efficient allocation and the price of tail removal

The efficient set is the non-dominated subset of the evaluated allocations,

F_s = { x ∈ A_s : ∄ y ∈ A_s with μ(y) ≤ μ(x), ES₉₀(y) ≤ ES₉₀(x), (μ(y), ES₉₀(y)) ≠ (μ(x), ES₉₀(x)) },

computed after removing allocations that are dominated state by state on the sampled paths (a sampled-dominance filter). A decision-maker with risk weight λ ≥ 0 selects argmin_{x∈F_s} μ(x) + λ·ES₉₀(x). Because ES is monotone, this rule never selects an allocation that is worse in every state; the same rule on TCaR can (v2.32, Proposition 6), which is why TCaR is reported but not used for selection.

Between two adjacent points a, b on F_s with μ(b) > μ(a) and ES(b) < ES(a), the ratio

π(a → b) = [μ(b) − μ(a)] / [ES₉₀(a) − ES₉₀(b)]

is the price of removing one won of tail cost by moving from a to b. It is the object an investor compares with its own λ, or with the cost of hedging the same exposure in a market. In the results the moves along the frontier are of two kinds — a contract added to the same schedule, or a different schedule — and π is reported for each.

### 2.4 When does uncertainty change the allocation?

Two levers move an allocation along the frontier.

*Contracts.* Fixing the price of a share h of added electricity Q⁺_t raises the mean by the premium, Δμ = Σ_t d_t h Q⁺_t p^E_t π_E, which is exactly linear in h, and lowers ES by removing the hedged share's contribution to the upper tail. For a coherent measure ES(C_h) is convex in h (positive homogeneity and subadditivity), with equality — exact linearity — only when the set of tail paths does not change with h. On the evaluated grid the ES steps shrink by less than 5 % from h = 0 to h = 1 (§5.5), so the curve is convex but nearly linear, the price of tail removal π(h) rises only slightly along the contract axis, and the λ-selection is effectively a threshold rule: contract fully if λ exceeds π, not at all otherwise, with interior shares selected only for λ inside a band a few percent wide. All grid points are non-dominated (μ rises and ES falls monotonically in h); the interior ones are simply unsupported by most linear scalarisations. Two consequences must be stated plainly. The premium π_E is a research assumption (8 %), so π is proportional to it by construction and the reported values are not evidence about hedging markets; the decision-relevant object is the *break-even premium* at which the contract leaves the frontier for a stated λ (§7). And the EPC contract, at a +10 % premium on a construction cost the model treats as deterministic, adds the same amount in every state and is dominated by construction; the 135 EPC variants in the menu are inert and are not discussed further.

*Timing.* Advancing adoption of technology k by Δτ years changes the mean by the discounted capex brought forward, less the central-price operating difference over the advanced years, and changes the tail by exchanging the incumbent's exposure for the new technology's exposure over those years. Writing σ² for the variance of a year's energy-plus-carbon bill under the two configurations,

earlier adoption lowers ES only if  Var[ bill_new ] < Var[ bill_old ] on the advanced years, i.e. (Q^E σ_E)² + cross terms  <  (Q^{coal} σ_coal)² + (E − A)² σ²_{CO₂} + cross terms.

This is an empirical condition, not a theorem. In Korea the system marginal price is tied to LNG (electricity–LNG log-return correlation 0.905 in the verified series), so σ_E is the largest volatility in the factor set; electrification can therefore *relocate* exposure from coal and carbon to electricity rather than reduce it, unless the added electricity is contracted. The hypothesis "faster transition prepares the firm against energy cost" is thus, within this model, the hypothesis that *transition plus fixed-price procurement* lowers ES, and it is tested on constructed timing variants in §5.3.

### 2.5 The five indicators, formally

| # | Indicator | Definition | Notes |
|---|---|---|---|
| ① | Aligned capex need | K(x) = Σ_t K_t(z); peak max_t K_t and its year; construction vs. renewal split | `e5/metrics_company.csv`, `e4/annual_capital_ledger.csv` |
| ② | Expected transition cost | μ(x) = E[L(x)] = L(x, 1) | equals central-price incremental cost |
| ③ | TCaR and decomposition | q₀.₉(C(x)) − q₀.₅(C(x)); variance shares from freezing one factor at its central path (hydrogen folded into electricity) | `e5/variance_decomp.csv` |
| ④ | Policy exposure | W(x; s→s′) = μ_{s′}(x) − μ_{s′}(x*_{s′}), the cost of holding x when s′ materialises relative to s′'s own mean-minimising allocation x*_{s′}, evaluated with s′'s prices, allowances and hedge reference (a scenario-regret construction in the sense of Loulou and Kanudia, 1999); W can be negative when x ∉ A_{s′}, which is why it is always paired with the emission gap G(x; s′) = Σ_t max(E_t(z) − B^{s′}_{c,t}, 0) | two numbers by construction; both directions reported |
| ⑤ | Flexibility value | Φ = μ(x*) − E[ min_{y∈Z_s} L(y, ε) ], the expected value of perfect information over the generated menu | an EVPI: an *upper* bound on the value of any sequential-learning strategy over the same menu, and a *lower* bound only with respect to enriching the menu; not a real-options value (v2.32 §5.4) |

### 2.6 Discounting and the separation of level and risk

The rate r is a real risk-free rate (2.4 %: KTB-10y 4.40 % less ≈ 2 % expected inflation, 2026-09-11). Discounting at a WACC and then penalising the tail with λ·ES would count systematic risk twice; here the mean is the expected cash cost under the physical measure and risk enters once, through ES. The choice moves the level of every number (§7 reports 3.5 % and 5 %) but not the ranking of allocations in the canonical run.

## 3. Method (pipeline summary)

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

All tables list the four firms side by side for compactness. They are to be read *within* a firm and scenario: the portfolios are estimated, partial and of different sizes, and nothing in this section supports a cross-firm comparison of levels.

### 5.1 How much and when (indicator ①)

Table 1. Mean-cost-minimising allocation, canonical run. Source: `paper/cap_pathway/data/allocation_table_v2_3.csv` (built from `runs/v2_3/run/e5/metrics_company.csv`, `e4/annual_capital_ledger.csv`).

| Firm · scenario | Technologies | First adoption | Capex total (bn KRW2025) | of which construction | Capex peak (bn) | Peak year |
|---|---|---|---|---|---|---|
| POSCO · NZ15 | eff + H₂-DRI + HyREX | 2027 | 27,843 | 18,626 | 4,777 | 2032 |
| POSCO · B20 | eff + H₂-DRI + HyREX | 2027 | 24,771 | 13,232 | 3,852 | 2043 |
| NSC · NZ15 | eff + H₂-DRI | 2027 | 34,577 | 28,182 | 6,958 | 2034 |
| NSC · B20 | eff + H₂-DRI | 2027 | 31,267 | 22,367 | 4,950 | 2037 |
| LOTTE · NZ15 | e-cracker | 2039 | 2,465 | 1,417 | 708 | 2039 |
| LOTTE · B20 | e-cracker | 2038 | 2,465 | 1,417 | 519 | 2038 |
| MCI · NZ15 | e-cracker | 2034 | 915 | 613 | 221 | 2034 |
| MCI · B20 | e-cracker | 2040 | 1,135 | 613 | 375 | 2040 |

Reading. The stringency of the pathway does not change the steel technology set; it changes *when* the capital is spent. POSCO's capex peak moves from 2043 (B20) to 2032 (NZ15), NSC's from 2037 to 2034, with 11–12 % more total capital. In petrochemicals the budget is met by a single e-cracker conversion whose timing is set by the budget year (2034–2040); early adoption is never mean-cost-minimising under either scenario. Figure 1 (`figures/fig1_capex_pathway.png`) shows the annual construction outlays.

Capex total = construction (new transition equipment) + maintenance/renewal capex of the retained fleet (`gross_capex_k`); for POSCO · NZ15 the split is 18,626 + 9,216. Figure 1 plots construction only; Table 1 shows both.

### 5.2 The price tag (indicators ②, ③, ④, ⑤)

Table 2. Mean-minimising allocation (λ = 0) versus the λ = 1 allocation on the (μ, ES₉₀) frontier. bn KRW2025. Source: same file; `e5/lambda_tangency.csv`, `e5/policy_wedge.csv`, `e4/flex_value.csv`.

| Firm · scen. | ② μ (λ=0) | ES₉₀ (λ=0) | λ=1 allocation | μ (λ=1) | ES₉₀ (λ=1) | Δμ % of μ(L) | Δμ % of E[C] | ΔES % | Δμ/ΔES | ④ same plan under other scen. (μ incl. carbon) | ⑤ flex (mean) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| POSCO · NZ15 | 29,409 | 705,214 | same schedule, PPA 1.0 | 30,428 | 593,922 | +3.5 | +0.45 | −15.8 | 0.009 | 88,276 | 0 |
| POSCO · B20 | 68,090 | 507,217 | PPA 1.0 | 68,690 | 439,290 | +0.9 | +0.37 | −13.4 | 0.009 | 18,616 | 0 |
| NSC · NZ15 | 73,530 | 806,947 | PPA 1.0 | 74,946 | 642,132 | +1.9 | +0.53 | −20.4 | 0.009 | 122,303 | 3,194 |
| NSC · B20 | 89,839 | 585,431 | PPA 1.0 | 90,506 | 484,557 | +0.7 | +0.36 | −17.2 | 0.007 | 42,704 | 291 |
| LOTTE · NZ15 | 2,793 | 49,490 | PPA 1.0 | 2,964 | 20,799 | +6.2 | +1.4 | −58.0 | 0.006 | 1,523 | 565 |
| LOTTE · B20 | 4,744 | 50,644 | PPA 1.0 | 4,918 | 22,147 | +3.7 | +1.3 | −56.3 | 0.006 | 979 | 570 |
| MCI · NZ15 | 2,412 | 29,304 | PPA 1.0 | 2,551 | 10,705 | +5.7 | +2.0 | −63.5 | 0.007 | 1,217 | 46 |
| MCI · B20 | 2,170 | 22,742 | PPA 1.0 | 2,245 | 9,976 | +3.5 | +1.3 | −56.1 | 0.007 | 502 | 306 |

Reading. (i) Along the frontier the risk-efficient allocation keeps the *same equipment schedule* and adds a fixed-price contract on the electricity the transition adds; the price of removing one won of ES₉₀ is 0.6–0.9 jeon. The premium is 0.4–2.0 % of the allocation's absolute expected cost E[C] (the same base as ES); the larger "% of μ(L)" figures divide by the incremental cost and are shown only because ② is reported on that base. The EPC variants are dominated (deterministic construction cost) and do not appear on any frontier. This is cheap because the contract premium is a research assumption — PPA at +8 % over the central electricity price, EPC at +10 % over central capex (`config.yaml: contracts`) — and because the hedge applies only to the electricity the transition adds; the ratio is a property of that assumption, not an observed market price of hedging (§7.1 row e scales it). (ii) The tail cut is 13–20 % in steel and 56–64 % in petrochemicals — the petrochemical tail is almost entirely purchased electricity, the steel tail retains coal (Table 4). (iii) Policy exposure ④ is reported in both directions in Table 5 (§6.1); the B20 steel allocations overshoot the NZ15 annual path by 194–242 MtCO₂ in total (`budget_gap_tco2`, annual overshoot sum), against 105–106 Mt for the NZ15 plans themselves. (iv) Flexibility ⑤ is small except NSC · NZ15 (3,194) — the menu contains genuinely different schedules only there and in petrochemicals.

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

(B20 rows and the ±3 steps are in the data file and in Fig. 2, `figures/fig2_timing_ladder.png`; every cell has the same sign pattern.)

Three facts, all eight cells. (i) Earlier adoption raises expected cost *and* raises the tail, in both the absolute and the dispersion form — the §2.4 variance condition fails: the new bill (electricity, and hydrogen made from it) is more dispersed than the bill it replaces (coal, gas, and a carbon bill that is small on the net-trade basis). (ii) Later adoption lowers both statistics but violates the cumulative budget; the canonical schedule is therefore not a compromise on the frontier, it is the *earliest feasible point at which the budget binds*, and no evaluated earlier variant is non-dominated. (iii) Under full contracting (PPA 1.0) the pattern is the same in sign but roughly one third the size in the dispersion part (data file, `ppa = 1`), i.e. the contract removes most of what earlier adoption adds.

Within this model, then, uncertainty does not pull equipment forward. What it does is make the *contract* on the added electricity the efficient complement of any schedule (Fig. 3). The result depends on two things the paper cannot change and must state: the verified volatility ordering (σ_E is the largest in the factor set because Korean SMP is tied to LNG), and the 2027–2050 horizon, under which earlier electrification means more exposure-years inside the window and later electrification means fewer (§7.4 records this as a limitation; no terminal-value correction is applied).

### 5.4 Where the tail comes from (indicator ③ decomposition, two bases)

The decomposition freezes one factor at its central path and reports 1 − Var(frozen)/Var(full). Hydrogen is folded into electricity because it is derived from it; shares do not sum to one under correlated factors and can be negative when a factor moves against the plan's other costs. Table 4 reports it on the *absolute* cost C(x) — what drives the tail the treasury funds — and on the *incremental* cost L(x) — what drives the dispersion of the transition's cost relative to standing still. Sources: `paper/cap_pathway/data/abs_basis_stats_v2_3.csv` (absolute, computed from the canonical shocks and profiles) and `runs/v2_3/run/e5/variance_decomp.csv` (incremental).

Table 4. Signed variance shares of the mean-minimising allocation (spot power).

| Firm · scen. | absolute C(x): electricity (+H₂) | coal | carbon | incremental L(x): electricity (+H₂) | coal | carbon |
|---|---|---|---|---|---|---|
| POSCO · NZ15 | 0.97 | 0.16 | 0.02 | 0.28 | −0.06 | 0.58 |
| POSCO · B20 | 0.85 | 0.48 | 0.00 | 0.64 | −0.25 | 0.15 |
| NSC · NZ15 | 0.98 | 0.11 | 0.01 | 0.36 | −0.09 | 0.48 |
| NSC · B20 | 0.91 | 0.38 | 0.00 | 0.68 | −0.27 | 0.11 |
| LOTTE · NZ15 | 0.99 | 0.00 | 0.00 | 0.83 | 0.00 | 0.10 |
| LOTTE · B20 | 1.00 | 0.00 | 0.00 | 0.97 | 0.00 | −0.01 |
| MCI · NZ15 | 1.00 | 0.00 | −0.01 | 0.88 | 0.00 | 0.05 |
| MCI · B20 | 0.99 | 0.00 | 0.00 | 0.97 | 0.00 | 0.00 |

The two bases say different, complementary things. On the absolute basis the tail of every allocation's own cost is electricity (and the hydrogen made from it): 85–100 % in all eight cells, with coal a secondary factor in steel (11–48 %) and carbon essentially absent, because a budget-compliant allocation on the net-trade basis has E ≈ A and pays almost no net carbon. This is the tail a contract on added electricity addresses, and it is why the contract removes 56–64 % of ES in petrochemicals but only 13–20 % in steel — the residual steel tail is coal, not carbon, and the hedge menu contains no coal contract. On the incremental basis the picture inverts for steel under NZ15: 48–58 % of the dispersion of the *transition's* cost is carbon. That is not a carbon bill the plan pays; it is the risk that the carbon price falls and the avoided-carbon value of the abatement evaporates — the bad tail of L is a low carbon price, a stranding-of-abatement risk. Both readings hold and must be kept apart.

### 5.5 Contract grid

ES₉₀ falls almost linearly in the hedged share h for every schedule (Fig. 3, `figures/fig3_contract_grid.png`): for LOTTE · B20, 50,644 → 43,396 → 36,184 → 29,049 → 22,147 at h = 0, 0.25, 0.5, 0.75, 1, steps of 7,248 / 7,212 / 7,135 / 6,902 — mildly convex, as coherence requires. The premium is exactly linear in h, so π rises from 0.0060 to 0.0063 along the axis; all five points are non-dominated, and a linear scalarisation selects an interior share only for λ within that band. In practice the selection is a threshold rule (§2.4): h = 0 for λ below π, h = 1 above.

## 6. Discussion — what the allocation pathway is for

### 6.1 Reading the price tag as an investor

*① How much, when — the funding question.* The allocation fixes the maturity structure of the financing need. For POSCO the construction outlay peaks at 4,777 bn KRW in 2032 under NZ15 and at 3,852 bn in 2043 under B20 (Table 1, Fig. 1); against the latest verified annual EBITDA of 4,230 bn (2025), the peak-year outlay is 0.9–1.1 × EBITDA and the total over the horizon 5.9–6.6 × EBITDA, 71–80 % of one year's revenue (`e5/affordability.csv`; only POSCO has a verified, entity-consistent earnings reference — the other three firms' ratios are deliberately not computed). The stringent pathway does not change *what* POSCO builds; it moves 25 tn KRW of construction eleven years earlier. That is the number a lender prices: the same technology, a decade shorter runway.

*② Expected cost per tonne.* The mean-minimising allocation abates at 85–196 thousand KRW per discounted tCO₂ (`cost_per_tco2_thkrw`): 85–90 for the steel and petrochemical NZ15 cases where the carbon price does most of the work, 120–196 under B20 where it does not. These are conditional on the scenario's central prices and on the net-trade carbon basis.

*③ What the tail is made of — which instrument.* Table 4 tells the treasurer which exposure to hedge, on the base that matters for funding: the allocation's own cost. Petrochemical tails are electricity, so a fixed-price procurement contract on the added load removes 56–64 % of ES₉₀ (Table 2). Steel tails are electricity and coal; the contract removes the first (13–20 % of ES) and the menu offers nothing for the second — coking-coal term contracts and index swaps, which steelmakers actually use, are absent from this study and would be the next instrument to add. The incremental-basis column of Table 4 adds a different warning for steel under a stringent pathway: the dispersion of the transition's value is dominated by the carbon price, on the downside — if the carbon price collapses, the abatement that justified 25–35 tn KRW of capital loses its value. That is not hedgeable with a power contract; it is the exposure indicator ④ is for.

*The price of tail removal.* On the evaluated grid π = 0.6–0.9 jeon per won of ES₉₀ (Table 2). Two things follow. First, at the research premium of 8 % the contract is efficient for any risk weight λ above about 0.01, i.e. for any decision-maker who weighs the 90 % tail at all. Second, the number is a property of the premium, not a finding about markets: π scales with the premium, so the reader should replace 8 % with the PPA premium actually offered (in Korea, direct PPAs carry network charges and levies on top of the contract price; in Japan, corporate PPAs are traded in a liberalised retail market) and re-read Table 2. §7 gives π at 15 % and 25 %.

*④ Policy exposure — both directions.* Table 5. Holding one scenario's allocation when the other materialises. Source: `runs/v2_3/run/e5/policy_wedge.csv` (`.c00` variants; cost incl. carbon, evaluated with the realised scenario's prices, allowances and hedge reference; the emission gap is the sum of *annual* overshoots against the realised scenario's path, so it is positive even for the own-scenario plan when the cumulative budget is met by a non-monotone path).

| Firm | Holding the NZ15 allocation in a B20 world: regret (bn) | Holding the B20 allocation in an NZ15 world: cost saving (bn) | … but annual overshoot vs NZ15 path (Mt, vs own-plan overshoot) |
|---|---|---|---|
| POSCO | 88,276 − 52,147 = +36,129 | 18,616 − 48,336 = −29,720 | 193.6 vs 105.6 |
| NSC | 122,303 − 66,621 = +55,682 | 42,704 − 80,602 = −37,898 | 241.6 vs 104.6 |
| LOTTE | 1,523 − 1,524 = 0 | 978 − 980 = 0 | 5.6 vs 6.4 |
| MCI | 1,231 − 678 = +553 | 502 − 800 = −298 | 4.2 vs 1.6 |

Read carefully, this table is asymmetric in kind, not just in size. Over-investing (holding the NZ15 allocation when B20 arrives) costs POSCO 36 tn and NSC 56 tn KRW in expected terms — real money, and the reason firms hesitate. Under-investing (holding the B20 allocation when NZ15 arrives) *saves* expected cost, because the NZE-anchored scenario has low fossil prices and the B20 plan burns more fuel; but it leaves an emission overshoot of 88–137 Mt above the firm's own NZ15 plan that no contract can buy back at the modelled carbon prices without violating the cumulative budget. The policy exposure is therefore not one number but a pair: an expected-cost regret in one direction and a compliance gap in the other. For petrochemicals both are small: the conversion is a single dated decision and the two scenarios date it within two years of each other.

*⑤ Flexibility.* The value of re-optimising within the generated menu after prices are known is 46–570 bn for petrochemicals and 291–3,194 bn for NSC (Table 2), an expected value of perfect information over the menu (§2.5). It is exactly zero for POSCO because the menu contains one distinct schedule; that is a statement about the menu, not about POSCO's optionality, and it is why the timing ladder was built.

### 6.2 The case for transition, stated conditionally

The paper was asked whether a firm that transitions early is "prepared" against energy cost. The honest answer has three parts, each visible in the tables.

First, *within the price model, earlier equipment does not reduce the tail* (§5.3). Every earlier variant is dominated; the canonical schedule is the earliest budget-binding point. The reason is structural: the transition replaces a coal-and-carbon bill with an electricity-and-hydrogen bill, and in the verified series Korean electricity is the most volatile input because the system marginal price is set by LNG. Electrification relocates exposure; it does not remove it.

Table 6. Tail of the allocation relative to the no-transition counterfactual x₀ on the same paths: level form ES₉₀(x)/ES₉₀(x₀) and dispersion form D(x)/D(x₀), D = ES₉₀ − E[C]. Source: `paper/cap_pathway/data/abs_basis_stats_v2_3.csv`.

| Firm · scen. | ES₉₀(x₀) | D(x₀) | spot: ES ratio | spot: D ratio | contracted: ES ratio | contracted: D ratio |
|---|---|---|---|---|---|---|
| POSCO · NZ15 | 750,469 | 554,161 | 0.94 | 0.87 | **0.79** | **0.66** |
| NSC · NZ15 | 734,443 | 543,363 | 1.10 | 1.00 | **0.87** | **0.69** |
| LOTTE · NZ15 | 26,247 | 16,583 | 1.89 | 2.23 | **0.79** | **0.49** |
| MCI · NZ15 | 13,141 | 8,529 | 2.23 | 2.61 | **0.81** | **0.42** |
| POSCO · B20 | 317,582 | 221,752 | 1.60 | 1.55 | 1.38 | 1.24 |
| NSC · B20 | 319,849 | 225,038 | 1.83 | 1.78 | 1.51 | 1.33 |
| LOTTE · B20 | 21,305 | 12,973 | 2.38 | 2.90 | 1.04 | **0.69** |
| MCI · B20 | 9,055 | 5,458 | 2.51 | 3.11 | 1.10 | **0.76** |

Second, *the transition plus fixed-price procurement is the lower-tail position under the stringent scenario, for every firm, in both level and dispersion*: ES₉₀ falls to 79–87 % and D to 42–69 % of the counterfactual. Under B20 the level ratio stays above one for all four firms (the incumbent's tail is small when carbon is cheap and allocation does not shrink), but the dispersion ratio falls below one for the two petrochemical firms once the added load is contracted (0.69, 0.76): the transition raises the *level* of their tail cost and lowers its *dispersion*. For steel under B20 both ratios exceed one — coal exposure is replaced by a larger, uncontracted-coal-plus-electricity exposure.

Third, therefore, *the case for transition is a case about the policy world, and the case for procurement is a case about the price world.* If the stringent pathway is the world the firm plans for — and the cumulative budget makes it the world the firm must comply with — then the allocation that meets it *and* contracts its added electricity has a lower tail cash cost than standing still, in every firm studied. If the lax world is the planning basis, the transition is a compliance cost with a higher tail, and the only thing that limits the damage is again the contract. In neither world is early equipment by itself a hedge. "Prepared", in this model, means: on the budget-binding schedule, with the added electricity contracted, and with the steel carbon residual recognised as an unhedgeable policy exposure.

Three caveats bound this reading. The no-transition counterfactual violates the budget, so Table 6 compares a compliant allocation with a non-compliant one; it is a statement about cash-cost tails, not a menu of choices. The counterfactual's NZ15 tail is large partly because the allocation rule gives x₀ a shrinking allowance path against unchanged emissions, so its net carbon bill widens mechanically; §7 reports the gross basis and a benchmark-style allocation as co-equal cases. And the NZE anchor lowers fossil prices as it raises carbon prices; §7.3 separates the two by holding NZ15 fuel and electricity paths and replacing the carbon path, and finds that the entire NZ15 level result is the carbon price: with B20 carbon prices in an NZ15 fuel world the counterfactual's tail collapses and every contracted allocation sits above it again. The case for transition in this model is therefore the carbon price and the compliance budget — not energy-cost insurance.

### 6.3 What a disclosed plan would be measured against

The methodology manuscript (v2.32, §3.5, §4.4) defines a model benchmark for a firm's declared net-zero path: the minimum-central-cost schedule that achieves the declared linear emission path with the same technology menu, and the two gaps between the disclosed coordinate and the evaluated set. The canonical run contains no evaluated disclosed plan (`e5/gap.csv` is empty), because no firm's disclosed investment schedule could be mapped to the technology menu with verified resolution, and the linear-path benchmark generator was not run for v2.3. The paper therefore does not report gaps. When it does, the reading of §6.1–6.2 supplies the interpretation: a disclosed plan that lies above the frontier at the same expected cost is, in the words of the original design specification, "energy-price risk the firm is carrying for free" — the risk-gap G_R, positive whenever a cheaper-to-hedge allocation exists at no higher expected cost.

### 6.4 Implications

*For firms.* The allocation decision separates into a schedule decision, which the budget largely dictates, and a procurement decision, which the price model dictates: contract the added electricity if the premium is below the firm's price of tail cost. Treasury should track π, not the PPA share.

*For investors and lenders.* Underwrite the timing (①) and the policy exposure (④), not the electricity volatility: that is cheap to remove and the analysis shows by how much. For steel under a stringent pathway the residual absolute tail is coal, for which the menu has no instrument, and the dispersion of the transition's *value* is the carbon price on the downside — which argues for carbon contracts for difference or a credible price floor rather than for power hedges.

*For policy.* Two levers appear directly in the tables. The electricity price regime: while the system marginal price is LNG-indexed, electrification carries LNG risk into industry and the burden of removing it falls on bilateral contracts; a market design that decouples industrial power prices from the marginal gas plant lowers ES₉₀ for every electrifying firm without a single won of subsidy. And carbon-price credibility: under NZ15 the dispersion of the steel transition's value is dominated by the carbon price on the downside (Table 4, incremental basis) — the risk is not that the carbon bill rises but that it collapses after 25–35 tn KRW has been committed against it. A credible price floor, or a carbon contract for difference on the abated tonnes, addresses an exposure that no market instrument in the firm's reach can.

## 7. Robustness and limitations

### 7.1 What was varied and what moved

Table 7. Sensitivities. Rows a–d are from the v2.2 sensitivity runs (same menu and inputs as v2.2, r = 5 % base; `tmp/research_case_v2_2_sensitivity`); rows e–g are recomputed on the canonical v2.3 profiles and shocks (`paper/cap_pathway/data/carbon_fuel_split_nz15.csv`, `abs_basis_stats_v2_3.csv`). "Selection" = does the mean-minimising schedule or the λ = 1 contract choice change in any of the eight cells.

| | Variation | Level effect | Selection | Sign changes |
|---|---|---|---|---|
| a | Discount rate 5 % → 3.5 % → 2.4 % (v2.2 base) | μ and ES rise as r falls (POSCO NZ15 μ 22,610 → 26,399 → 29,725) | none | none |
| b | Price process: annual GBM → log-OU, 10-year half-life (v2.2 base) | ES₉₀ falls 32–38 % (POSCO NZ15 485,124 → 324,079) | none | ES(x) − ES(x₀) for POSCO NZ15 flips from −15,328 to +8,351 |
| c | Carbon accounting: gross p·E → net p·(E − A) (v2.0 → v2.1, same menu) | ES₉₀ falls 40–50 % for steel; μ unchanged (allocation is a level shift on the incremental basis only through x₀) | none | none |
| d | Hydrogen price: policy target → structural (v2.1 → v2.2b) | POSCO NZ15 μ −30,284 → +22,610; NSC NZ15 −38 → +54,071 | petrochemical schedules change (H₂-fuel drops out) | steel NZ15 μ changes sign |
| e | Contract premium 8 % → 15 % → 25 % (linear scaling of Δμ) | π 0.006–0.009 → 0.011–0.017 → 0.019–0.028 | none for any λ ≥ 0.03 | none |
| f | Carbon price inside NZ15: NZE path → B20 path → zero (fuel and electricity paths held) | see Table 8 | none | **Table 6 NZ15 ratios flip above 1 for every firm** |
| g | Timing ladder ±3/±6 y (§5.3) | earlier: μ and ES up; later: down but infeasible | none | none |

### 7.2 Discount rate, price process, accounting

Rows a–d confirm that the canonical selections do not depend on the discount rate, the accounting basis or the hydrogen convention, but that the *levels* — and one sign — do. The OU result (row b) matters for how the tail is read: annual GBM shocks compounded over 24 years put the 2050 median electricity multiplier near 0.24 of the central path and carry the mean in a lognormal right tail, so absolute ES levels are roughly a third lower under mean reversion. The paper reports GBM levels because the verified annual series do not reject a unit root at n = 10–15; a reader who believes SMP is mean-reverting should scale ES down by about a third and treat the POSCO NZ15 level comparison with x₀ as undetermined in sign. The dispersion ratios in Table 6 are less sensitive than the levels because both numerator and denominator scale.

### 7.3 Separating the carbon price from the fuel price

Table 8. NZ15 allocation vs. no-transition counterfactual when the NZ15 carbon path is replaced while fuel and electricity paths are kept. Contracted allocation (PPA 1.0). Source: `carbon_fuel_split_nz15.csv`.

| Firm | carbon path | μ(L) | ES₉₀(x) | ES₉₀(x₀) | ES ratio | D ratio |
|---|---|---|---|---|---|---|
| POSCO | NZE (canonical) | 30,428 | 593,922 | 750,469 | 0.79 | 0.66 |
| POSCO | B20 path | 136,473 | 587,857 | 300,285 | 1.96 | 1.72 |
| POSCO | zero | 181,110 | 587,191 | 151,057 | 3.89 | 3.45 |
| NSC | NZE | 74,946 | 642,132 | 734,443 | 0.87 | 0.69 |
| NSC | B20 path | 173,019 | 642,901 | 329,762 | 1.95 | 1.60 |
| LOTTE | NZE | 2,964 | 20,799 | 26,247 | 0.79 | 0.49 |
| LOTTE | B20 path | 5,463 | 20,676 | 18,099 | 1.14 | 0.74 |
| MCI | NZE | 2,551 | 10,705 | 13,141 | 0.81 | 0.42 |
| MCI | B20 path | 3,973 | 10,774 | 8,075 | 1.33 | 0.74 |

The allocation's own tail barely moves when the carbon path changes (a compliant plan on the net-trade basis pays almost no carbon); the counterfactual's tail collapses. Every Table 6 level ratio below one under NZ15 is therefore the NZE carbon price applied to the counterfactual's residual emissions net of a shrinking allocation, and the expected transition cost rises four- to six-fold for steel when that price is removed. Two conclusions follow and the paper states both. The case for the transition is a case about the carbon price and the budget it enforces; it is not a case about energy-cost insurance, and the paper's earlier framing of "preparedness against energy cost" is not supported on the level basis. And the contract's effect on *dispersion* survives for petrochemicals whatever the carbon path (D ratio 0.74 with B20 carbon) but not for steel (1.6–1.7), because the contracted steel allocation still carries more coal-plus-electricity dispersion than an unconverted blast furnace.

### 7.4 Limitations

*Inputs.* Facility portfolios are estimated from public disclosures, not measured; they are partial portfolios, confidential, and not reproducible outside the research team. Production is held fixed to 2050 while both petrochemical firms are in announced restructuring (MOTIE's December 2025 NCC restructuring; the Mitsui–Idemitsu Chiba integration) — for them the first capital decision in 2026 is consolidation, which this menu does not contain. The technology set excludes CCUS by design, which removes Nippon Steel's disclosed route; POSCO is assigned both H₂-DRI and HyREX on a timetable earlier than its demonstration schedule; reinvestment windows are used in the schedule generator but cannot be shown because the campaign dates are confidential.

*Prices.* Electricity volatility is calibrated on wholesale series (KPX SMP, JEPX). Korean industrial customers buy under KEPCO's regulated tariff and Japanese ones under retail contracts with lagged fuel-cost adjustment, both smoother than the wholesale price; the electricity tail reported here is an upper bound for a tariff customer, and the "relocation of exposure" result is correspondingly an upper bound. Volatilities and correlations rest on 10–15 annual observations that span the 2022 gas shock and, for KAU, a market launch, collapse and recovery; no confidence intervals are reported. Hydrogen is priced structurally (52 kWh/kg, a fixed electrolyser cost with no decline and an implicit capacity factor), whereas both governments plan on imported hydrogen; the constant's provenance is not documented in the register. Construction cost is deterministic, so the first-of-a-kind overrun risk practitioners weigh most is absent, and the EPC contract is inert.

*Carbon.* The free-allocation rule A = firm budget path is a proxy; K-ETS phase 4 allocates by product benchmark with a rising auction share and GX-ETS by target with a price corridor. The rule makes a compliant firm a net seller in years it beats its path, gives the counterfactual a widening net obligation, and drives Table 6 (§7.3). K-ETS also covers indirect emissions from purchased electricity [확인 필요 — phase-4 treatment], which the Scope-1 budget used here does not; grid-based electrolysis would add an obligation the model does not book, and a renewable PPA would then change feasibility, not only cost, weakening the factorisation A = Z × H for Korean cases.

*Contracts.* A fixed-price contract on 100 % of added load for 24 years does not exist in either market; Korean direct and third-party PPAs are pay-as-produced renewable contracts with network charges and levies, of roughly 20-year tenor, and firming a baseload DRI or e-cracker load requires several times the nameplate plus residual spot purchases. The premium is an assumption; π scales with it (row e). The hedge menu contains no coal or LNG instruments, so "contract the electricity" is efficient partly because it is the only contract offered.

*Method.* The generated menu contains one distinct steel schedule per firm; the timing ladder (§5.3) perturbs it by moving all adoption years together, which ignores campaign life, and compares within a 2027–2050 window without a terminal treatment of post-2050 exposure, so "earlier raises the tail" is a within-window statement. The λ-selection over a discrete set is a threshold rule; λ is not grounded in a cost of external finance. ⑤ is an EVPI over a finite menu. The frontier is the frontier of evaluated allocations; the ε-grid on the surrogate risk term in E2 did not induce timing variation, and the paper does not claim the true frontier of Z_s.

*Scenarios.* NZ15 and B20 are local interpolations anchored on IEA GEC 2025; the sector pathway is a placeholder for the KAIST GCAM pathway. The NZE anchor lowers fossil prices as it raises carbon prices, so the policy-exposure indicator ④ mixes the two; Table 8 isolates the carbon price for the NZ15 level results but ④ itself is not decomposed.

## 8. Conclusion

A firm that has accepted a sector emission pathway still has to decide how much capital to commit, when, and in what form. This paper turned that decision into an object that can be computed, priced and audited: a capital allocation pathway with a five-line price tag, selected on a frontier in expected incremental cost and expected shortfall of the allocation's own cost. Four things came out of applying it to two steel and two petrochemical firms.

The budget fixes the schedule. Stringency moves the steel capex peak earlier by three to eleven years and adds about a tenth to the capital, but it does not change what is built, and within the 2027–2050 window no earlier-adoption variant is non-dominated: earlier equipment costs more in expectation and carries more tail. The tail of every allocation's own cost is electricity. That is the consequence of transitioning in a power market whose marginal price is set by gas, and it makes the fixed-price contract on the added load the one lever in the menu that reduces dispersion — by roughly three-fifths in petrochemicals and a fifth in steel, at a fraction of a percent of expected cost under the assumed premium. The transition's advantage over standing still under a stringent pathway is the carbon price. Holding the fuel world fixed and replacing the carbon path removes it entirely; the case for transition is therefore a case about policy credibility and the compliance budget, and the case for procurement is a case about the price world. And for steel the two do not add up to insurance: even contracted, the converted fleet carries more coal-plus-electricity dispersion than the furnace it replaces unless carbon is expensive.

What the paper cannot yet say is set out in §7.4 and bounds every one of these statements: the electricity volatility is wholesale, not the tariff the firms pay; the allocation rule is a proxy for two schemes that allocate by benchmark and by target; the contract premium is assumed; the hedge menu has no coal or gas instruments; the facility portfolios are estimated; and the sector pathway is a placeholder for the KAIST GCAM pathway. The next version of this work should, in that order, recalibrate electricity on the tariff basis, replace the allocation rule with a benchmark rule and include indirect emissions for Korea, ground the premium in observed corporate-PPA terms, and regenerate the menu with per-facility timing so that the frontier of schedules is the frontier of the feasible set rather than of one point and its perturbations. None of those changes the object the paper proposes; each changes the numbers on its price tag, and the paper has tried to say by how much.

## References

- Artzner, P., Delbaen, F., Eber, J.-M., Heath, D., 1999. Coherent measures of risk. *Mathematical Finance* 9(3), 203–228.
- Bataille, C., 2020. Physical and policy pathways to net-zero emissions industry. *WIREs Climate Change* 11(2), e633.
- Battiston, S., Mandel, A., Monasterolo, I., Schütze, F., Visentin, G., 2017. A climate stress-test of the financial system. *Nature Climate Change* 7, 283–288.
- Blyth, W., Bradley, R., Bunn, D., Clarke, C., Wilson, T., Yang, M., 2007. Investment risks under uncertain climate change policy. *Energy Policy* 35(11), 5766–5773. [title/authors verified; volume 확인 필요]
- Bolton, P., Kacperczyk, M., 2021. Do investors care about carbon risk? *Journal of Financial Economics* 142(2), 517–549.
- Dixit, A.K., Pindyck, R.S., 1994. *Investment under Uncertainty*. Princeton University Press.
- Engle, R.F., Giglio, S., Kelly, B., Lee, H., Stroebel, J., 2020. Hedging climate change news. *Review of Financial Studies* 33(3), 1184–1216.
- Froot, K.A., Scharfstein, D.S., Stein, J.C., 1993. Risk management: coordinating corporate investment and financing policies. *Journal of Finance* 48(5), 1629–1658.
- Fuss, S., Szolgayova, J., Obersteiner, M., Gusti, M., 2008. Investment under market and climate policy uncertainty. *Applied Energy* 85(8), 708–721.
- Layritz, L.S., Dolganova, I., Finkbeiner, M., Luderer, G., Penteado, A.T., Ueckerdt, F., Repke, J.-U., 2021. The potential of direct steam cracker electrification and carbon capture & utilization via oxidative coupling of methane as decarbonization strategies for ethylene production. *Applied Energy* 296, 117049.
- Loulou, R., Kanudia, A., 1999. Minimax regret strategies for greenhouse gas abatement: methodology and application. *Operations Research Letters* 25(5), 219–230.
- Markowitz, H., 1952. Portfolio selection. *Journal of Finance* 7(1), 77–91.
- Martin, R., Muûls, M., de Preux, L.B., Wagner, U.J., 2014. Industry compensation under relocation risk: a firm-level analysis of the EU Emissions Trading Scheme. *American Economic Review* 104(8), 2482–2508.
- Rissman, J., et al., 2020. Technologies and policies to decarbonize global industry: review and assessment of mitigation drivers through 2070. *Applied Energy* 266, 114848.
- Rockafellar, R.T., Uryasev, S., Zabarankin, M., 2006. Generalized deviations in risk analysis. *Finance and Stochastics* 10(1), 51–74. [확인 필요 — cited in manuscript v2.32]
- Rockafellar, R.T., Uryasev, S., 2002. Conditional value-at-risk for general loss distributions. *Journal of Banking & Finance* 26(7), 1443–1471.
- Roques, F.A., Newbery, D.M., Nuttall, W.J., 2008. Fuel mix diversification incentives in liberalized electricity markets: a mean–variance portfolio theory approach. *Energy Economics* 30(4), 1831–1849.
- Vogl, V., Åhman, M., Nilsson, L.J., 2018. Assessment of hydrogen direct reduction for fossil-free steelmaking. *Journal of Cleaner Production* 203, 736–745.
- Vogl, V., Olsson, O., Nykvist, B., 2021. Phasing out the blast furnace to meet global climate targets. *Joule* 5(10), 2646–2662.

## Reproducibility

Repository `PLANiT-Institute/cap_finance` (public; facility-level inputs excluded). Canonical run: `tmp/research_case_v2_3/run`, configuration `config.yaml` (price_factor_set v2, hedge_basis incremental, frontier_axes [mean, es_abs], carbon net_trade, h2_price_source structural, discount 0.024), seed 20260806, N = 10,000. Manifest `run_manifest.json` records SHA-256 of every stage output; the ones this paper's tables rest on: `e2/plan_index.csv` 97157a4f…, `e3/price_sims.parquet` 2267e521…, `e5/frontier_points.csv` 16f660de…, `e5/metrics_company.csv` 43b1c1a8… (E2 finished 2026-09-11 00:22 UTC; E5 re-run 03:01 UTC after the policy-wedge and decomposition fixes). Derived tables in `paper/cap_pathway/data/`: `allocation_table_v2_3.csv` ccedd55f…, `timing_ladder_results.csv` 60721e50…, `abs_basis_stats_v2_3.csv` 74fd77b5…, `carbon_fuel_split_nz15.csv` 500f0581…, `preparedness_v2_3.csv` 4aab2d16…. The timing ladder is an E5-only re-evaluation of 32 constructed plan files in a copy of the canonical run (`runs/v2_3_ladder`); the absolute-basis decomposition and the carbon split are direct `simulate_cost` evaluations on the canonical shocks. Sensitivity rows a–d of Table 7 come from `tmp/research_case_v2_2_sensitivity/{v2_2_ou, v2_2_r035, v2_2_rf24}` and the v2.0/v2.1/v2.2 runs listed in the methodology changelog.
