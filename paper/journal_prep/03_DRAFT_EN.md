# Where do disclosed transition plans sit in the cost–risk plane? An intra-firm efficiency frontier for four Korean and Japanese steel and petrochemical firms

**Working draft — 23 August 2026. Prepared for submission to *Energy Policy* as a full-length article (≤8,000 words of main text).**
Unless stated otherwise, all values are for the base run: the net-zero scenario, no support policy, 10,000 simulated paths, fixed seed. Money is in KRW billion; abatement cost in thousand KRW per tCO₂ (1,000 KRW ≈ USD 0.72 at the exchange rate stated in the supplementary material). Throughout, the *price of risk* is ΔP50 ÷ ΔTCaR, the expected cost of removing one won of tail risk, so a smaller number means cheaper risk reduction.

---

## Abstract

Transition-plan assessments tell investors whether a corporate plan is aligned with a carbon budget, not what it costs, how uncertain that cost is, or whether the budget could be met more cheaply or safely. We give disclosed plans coordinates. For POSCO, Nippon Steel, Mitsui Chemicals and LOTTE Chemical we enumerate budget-feasible facility-level transition plans with a mixed-integer programme, revalue each on 10,000 correlated electricity, hydrogen and capital-cost paths, and trace the efficient frontier in the plane of expected incremental cost (P50) and tail cost-at-risk (TCaR = P90 − P50, the additional funding a treasury must pre-arrange). The disclosed plan's distance to the frontier is a two-number diagnostic — 1.3 trillion KRW on cost and 4.7 trillion on risk for Nippon Steel, 0.7 and 1.0 trillion for Mitsui Chemicals. Along the frontier only contract choices vary — renewable PPA share and fixed-price EPC — while the technology schedule stays fixed, a consequence of treating the carbon price as a scenario, not a stochastic factor. Removing one won of tail risk costs 0.3–0.4 won in the two steelmakers and 4–5 won in the two petrochemical firms: the same PPA is a hedge in one industry and expensive electricity in the other. The stricter carbon scenario carries the smaller tail for every firm. On money alone delay wins for three of four firms; early action wins only if budget overshoot is sanctioned above 5–39 thousand KRW/tCO₂. The case for early transition rests on whether carbon budgets bind in quantity, not on price forecasts.

**Keywords:** transition plans; capital allocation; efficiency frontier; tail risk; power purchase agreements; steel; petrochemicals; carbon budget

---

## 1. Introduction

Over the past five years most large steel and petrochemical producers have disclosed transition plans to 2050, and the tools that grade those plans have multiplied with them. The Climate Action 100+ Net Zero Company Benchmark scores whether disclosed capital expenditure is consistent with a pathway, and asset-level methods reconstruct emission trajectories from disclosed facility schedules and compare them with a carbon budget. The most recent of these, the asset-based planning approach of Kampmann et al. (2026), applies that test to ten steelmakers and ten utilities among the CA100+ focus companies and finds only three of twenty plans broadly Paris-compatible.

Each of these tools answers one question: *is the plan aligned or not?* A firm that has received the answer asks a second one. *What does it cost, and how much more must we be able to raise if prices move against us?* A verdict is not a prescription, and a verdict that omits cost can attach the same label, "misaligned", to two firms in entirely different positions: one that can close the gap cheaply and one that cannot.

Kampmann et al. (2026) record the omission themselves. They mention blast-furnace relining at €48/t and hydrogen direct reduction at €574/t, note that cost affects abatement choices only indirectly, and leave it out of the model. Uncertainty is treated as a narrative limitation rather than a distribution. This paper fills the axis they state they do not model.

### 1.1 The question

> Placed in the same (expected cost, tail risk) plane as every plan the firm could have chosen under the same carbon budget, how far is the disclosed plan from the efficient frontier, and what creates that distance?

The question concerns a firm's *internal* coordinates, not a league table across firms. Our sample is four companies: POSCO and Nippon Steel in steel, Mitsui Chemicals and LOTTE Chemical in petrochemicals. It is small by design. The measurement is internal to each firm, so the sample need not be representative of an industry, and each firm requires a hand-assembled record of its facilities, their vintages and their reinvestment windows, which is what bounds the number. Section 7.2 states what that forecloses. For each of them we enumerate the set of facility-level transition plans that satisfy a firm-specific carbon budget derived from NGFS–GCAM sector pathways, price each plan on correlated stochastic paths for electricity, hydrogen and capital cost, draw the Pareto frontier in the plane of expected incremental cost and tail cost-at-risk, and measure the disclosed plan's distance to it along each axis. The answer for each firm and scenario is two numbers in won: a cost gap and a risk gap.

We define tail risk as TCaR = P90 − P50 of the plan's incremental cost distribution, in currency, rather than as a variance or a conditional value-at-risk. We chose the measure for the people who have to act on it. P90 − P50 is the amount a treasury must be able to raise *beyond* the base-case budget if the plan is to survive an adverse decade. It is a financing quantity that a CFO, a lender or an allocator of transition bonds can use without translation. It uses less of the tail than CVaR, and Section 3.2 reports how much less.

### 1.2 What we find

We report three results, ordered by how much weight each can bear.

*(a) The ranking of abatement cost is the paper's most robust result.* Under the net-zero scenario with no support, the resource-cost abatement unit cost is 115.0 thousand KRW/tCO₂ for POSCO, 155.6 for Nippon Steel, 241.7 for Mitsui Chemicals and 279.2 for LOTTE Chemical. The order survives every robustness axis that can test it (decision criterion, random seed, price-process choice) as well as all twelve scenario bundles, with zero rank reversals.

*(b) The price of hedging differs by an order of magnitude between the two industries in our sample.* Along the frontier, the expected cost of removing one won of tail risk is 0.31 and 0.41 won for the two steelmakers and 4.2 and 4.8 won for the two petrochemical firms. The same instrument, a renewable PPA, is a hedge in steel, where electricity is half to two-thirds of cost variance, and merely expensive electricity in petrochemicals, whose tail is almost entirely hydrogen. We have not found this asymmetry reported elsewhere; with two firms per industry we cannot yet separate an industry effect from a scale effect (Section 7.2).

*(c) What moves along the frontier is contracts, not technology.* In all sixteen (firm × scenario × support) groups, every point on the frontier shares the same technology schedule, and the only thing that varies is the PPA share from 0 to 100 per cent, with fixed-price EPC appearing in the petrochemical ladders. This is at once a result and a finding about the model's boundary, and a referee will rightly ask whether a "capital-allocation frontier" is in fact a PPA-hedge-ratio curve. Section 5.2 shows that the degeneracy is a consequence of holding the carbon price deterministic within a scenario: when the carbon price is made stochastic, technology schedules return to the frontier in seven of eight groups.

### 1.3 What this paper cannot say

The paper is silent in three places a policy reader would most want to quote, and we would rather say so here than bury it in the results. The paper does not measure support policy, because the support dataset contains no subsidy or contract-for-difference rows. It does not pin down the *level* of tail risk, which moves by nearly half on the choice of price process, so TCaR is quoted by order and magnitude only. And it does not show that early transition pays on price alone. On total cost, delay wins for three of four firms unless overshooting the carbon budget is sanctioned, and whether it is sanctioned turns out to differ between our two jurisdictions in a way that reverses the answer (Section 6.3).

### 1.4 Contributions and structure

We claim three contributions, none broader than the literature review supports. **C1**: we place disclosed plans in the cost–risk plane, the axis the emissions-space literature leaves open. **C2**: we translate tail risk into a funding quantity, TCaR. **C3**: we compute the price of the risk axis firm by firm and find a ten-fold cross-industry asymmetry. Section 2 positions these claims; Section 3 describes the five-stage method and its one deliberate division of labour; Section 4 describes the data and its confidence grades; Section 5 reports results; Section 6 measures what they hang on; Section 7 draws policy implications and lists the limitations that could change the conclusions; Section 8 concludes. Every value in the text is registered and reconciled against the model outputs before publication.

---

## 2. Literature and positioning

Three literatures each hold one piece of what this paper assembles, and none holds all three. For each claim we say what exists, what does not, and which observation would reduce the claim.

### 2.1 Plan comparison with a risk axis: the pieces exist, the combination does not

Marginal abatement cost curves order measures by unit cost and select below a budget. They are single-objective and deterministic, and their critics have listed what they omit: interactions, path dependence and uncertainty (Kesicki and Strachan, 2011; Kesicki and Ekins, 2012). A MACC has no risk axis.

Mean–variance analysis has a risk axis, but its object is a securities portfolio or, in the energy application opened by Awerbuch (2006) and developed by Roques et al. (2008), a generation mix. Roques et al. simulate correlated fuel, electricity and CO₂ prices, obtain NPV distributions for each technology and trace efficient frontiers for a private investor, showing that the correlation between gas and electricity prices acts as a natural hedge. That paper is the closest conceptual relative of our PPA result. Multistage stochastic programming with CVaR (Ehrenmann and Smeers, 2011; Conejo et al., 2010) adds the multi-period structure and a formal risk measure. Its object is again power investment, and a disclosed plan is never the reference point. Capital-alignment assessments do use the disclosed plan as their reference point. The CA100+ Net Zero Company Benchmark (Climate Action 100+, 2024) and the Transition Pathway Initiative (2023) grade alignment as an indicator score, however, rather than measuring its degree as a distance in a cost–risk plane.

A second body of work has grown up around the plans themselves. Nicolajsen et al. (2025) translate more than 1,400 disclosure requests across fourteen frameworks into thirteen components and show that the frameworks increasingly demand that firms link decarbonisation strategy to financial planning, which is the requirement this paper tries to make computable. Rose et al. (2025) name the missing quantity from the other side: a transition plan carries *dependencies* on prices, technologies and policies outside the firm's control, and they ask for those dependencies to be measured. The stochastic factors priced here are three such dependencies. Klein et al. (2026) supply the large-sample counterpart, assessing 411 hard-to-abate firms and finding that commitments are often not embedded in financial planning at all, and Chan et al. (2024) argue for an economic rather than an accounting test of credibility.

The closest published work to ours is Ostrovnaya et al. (2026), who model the effect of carbon pricing and abatement cost on operating margin and capital expenditure for six steel and cement firms and conclude that decarbonisation depends on raising new capital. We reach a compatible conclusion by a different route and add three things their design does not provide: a distribution rather than a set of discrete scenarios, a tail quantile expressed as a funding requirement, and a frontier that locates the disclosed plan relative to the alternatives the firm had. Where they ask what a carbon price does to a firm, we ask what the firm's own plan costs relative to its feasible set.

Our contribution is the combination: cost minimisation, a risk axis and a disclosed-plan reference point built together on one industrial firm's plan set. The claim is falsifiable. A prior study that places a steel or petrochemical firm's plan set in a (cost, risk) plane and locates the disclosed plan in it would reduce ours to a replication, and we have not found one.

The portfolio literature also points to a constraint we must own. A frontier traced by ε-constraint (Mavrotas, 2009) is only as rich as the candidate set, and portfolio studies assume thousands of asset combinations. For an industrial firm the reinvestment windows and the admissible technology set narrow the choice set before any optimisation: our enumerator produced 48 plans, 40 distinct after canonical valuation. Finding (c) of the introduction is a consequence of that narrowness as much as of the data.

### 2.2 What is made stochastic: the literature randomises policy, we randomise inputs

The central result of the real-options literature is that carbon-price and policy uncertainty moves investment timing (Dixit and Pindyck, 1994; Laurikka and Koljonen, 2006; Fuss et al., 2008; Zhou et al., 2010). The closest steel application values a single hydrogen-DRI project under several stochastic drivers (Xu et al., 2024). Our base design is the reverse: the carbon price is fixed by scenario and only electricity, hydrogen and capital cost are stochastic, so our TCaR is tail risk *net of* policy risk. Here the literature was ahead of us, and rather than leave the point as a caveat we measured it. Carbon-price volatility estimated from K-ETS allowance prices with the same estimator as the inputs is 36.3 per cent a year, 1.5 times electricity (24.2 per cent) and the largest of our factors. Adding it as a fourth stochastic factor raises TCaR by 3,064 for POSCO and 2,159 for Nippon Steel but *lowers* it by 44 for Mitsui Chemicals and 94 for LOTTE Chemical. The objection is right in steel, where the policy axis alone is of the same order as total parametric uncertainty, and practically harmless in petrochemicals.

The sign deserves comment. Transition plans emit less than inaction, so they become relatively cheaper as the carbon price rises. In a funding-need metric the bad tail is therefore a carbon-price *collapse* rather than a spike: the firm invests and then watches policy retreat. Policy risk enters as stranding risk, which is the mechanism the real-options literature describes, seen from the other side.

### 2.3 The disclosed-plan gap: the emissions axis exists, the cost axis does not

Kampmann et al. (2026) reconstruct the disclosed plans of CA100+ steelmakers and utilities from Global Energy Monitor asset data and compare cumulative emissions with NGFS budgets. Saleh et al. (2026) do the same for more than 950 steel plants and find 2030 sector emissions 10–22 per cent above the IEA net-zero path. Bachorz et al. (2026), Vogl et al. (2021) and ACCR (2025) turn the same asset data into a relining-window argument, and AbdulRafiu (2026) into a stranded-asset quantification. All are emissions- or asset-space. None computes what a plan costs or how dispersed the cost is, even though the point costs they would need exist (Vogl et al., 2018; Hüttel and Lehner, 2024). Three cells could be filled: disclosed plan to emission path to budget overshoot, disclosed plan to cost in currency to distance from the frontier, and disclosed plan to cost distribution to funding need. Only the first is populated.

We are behind on one axis. Kampmann et al. use an open asset database, whereas our blast-furnace specifications and relining histories are individually collected, and Korean facility-level emissions are not publicly released. Their reinvestment-window statistic (42 per cent of steel assets before 2030) is consistent with our sample (48.9 per cent of capacity across 17 furnaces), the first external check our window assumption has received.

### 2.4 Procurement contracts as risk instruments

Our result that the frontier is traced by contracts rather than technologies rests on a literature that has studied those contracts in isolation. Tranberg et al. (2020) model the joint distribution of wind output and spot price and show that the residual volumetric exposure of a long-term power purchase agreement is large enough to change a value-at-risk estimate, which is the general form of the point that a fixed-price contract substitutes one exposure for another rather than removing risk. Pombo-Romero et al. (2024) price the options embedded in a renewable PPA from the offtaker's side and identify volatility reduction, not price level, as the main source of value, and they compute the collateral a counterparty must post against it. Gabrielli et al. (2022) come closest to our construction: they optimise a portfolio of corporate PPAs against expected performance and conditional value-at-risk and obtain a frontier in which single contracts earn more and portfolios carry less risk. Mittler et al. (2025) give the taxonomy of contract structures that a firm chooses among.

The hydrogen side of the ladder has no equivalent. Palmer et al. (2025) study the mirror image of our problem, a green hydrogen producer contracting with an industrial customer, and find that ignoring uncertainty raises cost by about 30 per cent under stress testing; the hedging instruments available in their setting are power purchase agreements and electricity futures, not hydrogen contracts. That asymmetry is structural rather than accidental. Odenweller and Ueckerdt (2025) document the gap between announced and realised green hydrogen supply, and where physical supply is unrealised there is no forward market in which an offtaker could lay off price risk. The instrument our petrochemical firms would need is the one the market has not yet built.

### 2.5 Tail risk in finance and transition finance

Climate value-at-risk (Dietz et al., 2016) and scenario-based climate credit risk (Battiston et al., 2023) define tails of asset-value distributions from the top down, and Acharya et al. (2023) survey how that tradition has been institutionalised in supervisory stress testing. Fliegel (2026) shows that the choice of transition-risk metric changes the answer, which is why the substitution of a funding quantity for an asset-value quantile is a change of object and not a change of label. The carbon-premium literature (Bolton and Kacperczyk, 2021; Seltzer et al., 2022) prices transition risk from returns and spreads. Neither produces a bottom-up, plan-specific funding need. That the quantity matters to firms is not only our conjecture: Tran et al. (2025) find that firms with greater climate-change exposure hold larger precautionary cash reserves, which is the behaviour a pre-arranged funding requirement predicts. In the two jurisdictions we study, the instruments that would absorb such a need are being designed without one: Japan's GX Economy Transition Bonds (Fukuda and Ino, 2026) and the auction revenue of K-ETS Phase 4. Section 7.1 returns to what underwriting it would cost. On the instrument side, Hoogsteyn et al. (2025) and Richstein et al. (2024) analyse carbon contracts for difference as a way of reallocating carbon-price risk between firm and state, which is the closest existing design to the contingent instrument our results imply.

---

## 3. Method

### 3.1 Five stages and one division of labour

The object of measurement is the distance between the plan a firm chose and the set of plans it could have chosen under the same carbon budget. The model is therefore not a device for finding one optimal plan but one for valuing comparable plans on the same ruler. Five stages do this in order (formulation in S1).

| Stage | Task | What it decides |
|---|---|---|
| 1. Budget | Firm-level annual carbon budget and central price paths from the scenario | the constraint |
| 2. Enumeration | Facility-level transition programme swept with ε-constraints to **enumerate candidate plans** | what is compared |
| 3. Simulation | Correlated stochastic paths for the price factors | what moves |
| 4. Valuation | **Revaluation** of every plan on every path | what each plan costs |
| 5. Frontier | Pareto set in the (P50, TCaR) plane and the disclosed plan's distance to it | the answer |

*The enumeration stage generates candidates; the valuation stage prices them.* Section 3.3 reports what goes wrong when that division is ignored.

*The budget stage.* Firm *c*'s annual cap scales the sector pathway's ratio to the firm's base-year emissions, $B_{c,t}=E^{base}_c\,\text{SectorBudget}_{s(c),\sigma,t}/\text{SectorBudget}_{s(c),\sigma,t_0}$. Korean sector budgets are direct-emission and Japanese ones include purchased electricity, so levels are not comparable, and taking ratios leaves the difference only in the slope. Abatement is not apportioned across firms; who abates when is an output of the model, not an input. Two NGFS–GCAM scenarios are used: net-zero 1.5 °C (NZ15) and below-2 °C (B20).

*The enumeration stage.* Decision variables are binary technology adoptions per facility and year, retirements, a firm-level renewable PPA share $\pi\in[0,1]$, fixed-price EPC and carbon-contract-for-difference indicators, and budget-overrun slack. Constraints are one decision per facility, the carbon budget with slack, a 20 per cent retirement cap as a proxy for demand and market position, technology availability, and the tracing ε-constraint. The objective sums discounted operating and energy cost, capex and stranding write-offs, carbon expenditure, a budget-violation penalty with a floor of 300 thousand KRW/tCO₂, retirement margin loss and residual value, and contract premia. Risk enters the enumeration stage only as a *linear* surrogate, a hedge deduction at median prices, because multiplying unhedged exposure by $(1-\pi)$ would make the programme bilinear. The disclosed plan is solved separately with its enforceable commitments fixed; if a disclosure contains none, no disclosed coordinate is produced, because an empty fixing is a second unconstrained optimisation and calling its distance a "gap" would manufacture one.

### 3.2 What is stochastic, and what is declared

Price factors follow geometric Brownian motion with drift implied by the central path and volatilities estimated from history (S2), and capex shocks are scaled by technology-specific uncertainty. Factors with fewer than six observations use priors and are flagged on every run. The base run is four factors × 10,000 paths × 26 years. The process is a *declaration, not an inference*: rejecting a ten-year-half-life mean-reverting alternative at 80 per cent power would require roughly 4,740 monthly observations, about 395 years, so available data cannot decide the question. We choose the risk-magnifying GBM explicitly and report that the mean-reverting alternative cuts TCaR by 41–48 per cent. The carbon price is a scenario axis rather than a stochastic one, for the reason given in Section 2.2: the policy path *is* the scenario's definition. The steel TCaR below is accordingly a lower bound.

*The valuation stage.* For each plan and path, quantity profiles are multiplied by path prices to obtain an NPV. Contracts apply *non-linearly* here. A signed EPC fixes capex at the median times a premium and removes it from market shocks, while the PPA share fixes that share of electricity at the contract price. A PPA is therefore an exposure swap rather than risk removal. Market-price variance on the contracted share is exchanged for a fixed payment that is itself above or below the market path on every draw, which is why the contracted share can reappear as a variance source at high PPA shares (Section 5.2). Capex is spread over the construction period rather than booked at adoption, which would overstate peak funding need. Stranding write-offs are booked at adoption and not shocked. The abatement unit cost is on a *resource-cost* basis, with the carbon-expenditure delta subtracted from the total-cost difference. Otherwise avoided carbon payments dominate and "transition is free", at which point the capital-allocation question disappears. TCaR is unaffected.

*The frontier stage.* The frontier is the Pareto set in the (P50, TCaR) plane on a canonical candidate set: enumerated plans de-duplicated by technology schedule and re-assigned a fixed contract grid (five PPA levels × two EPC states, no CCfD). The ε-sweep therefore *enumerates*; the reported frontier is the lower-left envelope of the re-gridded set. The frontier gap is the disclosed plan's distance to the frontier along the cost axis (cost that could have been saved at the same risk) and along the risk axis (risk that could have been removed at the same cost). The price of risk along the frontier is ΔP50 ÷ ΔTCaR between adjacent rungs, or over the whole ladder from the minimum-cost to the minimum-risk point. For readers who prefer a conditional tail measure: on the simulated distributions the expected cost beyond P90 exceeds P50 by 1.9 times TCaR in steel and 2.2 times in petrochemicals, so CVaR-type figures can be recovered by scaling.

### 3.3 The surrogate and the canonical value: the most easily misread part of the paper

The enumeration objective is an ordering device: its risk term is linear, its contracts linearised, its prices central. A 2 per cent MIP gap and a 60-second limit are therefore consistent settings rather than approximations, because optimality for a surrogate contributes nothing to the conclusion. All 51 solves in the base run terminated optimal in any case. Because this departs from the common practice of reporting the MILP optimum as *the* firm's optimal plan, we measured the difference. The rank correlation between the surrogate cost used for enumeration and the canonical P50 across a firm's candidates is 0.00 (POSCO), −0.56 (Nippon Steel), 0.20 (Mitsui) and 0.72 (LOTTE); in all eight firm × scenario groups the plan the surrogate called cheapest was *not* the cheapest under canonical valuation. This is a property of the surrogate itself rather than Monte-Carlo noise: the deterministic central-path cost correlates 0.94–1.00 with canonical P50 in seven of eight groups. Had we reported those solutions as the firms' optimal plans we would have reported the wrong plan eight times out of eight. No surrogate objective value appears anywhere in this paper (diagnostics in S6).

The same comparison showed that of 48 enumerated plans only 40 are distinct after canonical valuation, since the duplicates differ only in a CCfD that does nothing under a no-support scenario. The candidate set is thinner than the raw count suggests, a fact to carry into Section 5.2.

### 3.4 Numerical conventions

Seeds are fixed and the whole analysis re-runs end to end; the solver is restricted to a single thread, because near-tied optima within the optimality gap otherwise depend on thread scheduling. Five-seed coefficients of variation are 0.3–0.8 per cent for abatement cost and 1.1–1.8 per cent for TCaR, so TCaR is reported to two significant figures. Seed stability is precision, not accuracy.

---

## 4. Data

### 4.1 What was collected

Ten raw files: facility static specifications (28 facilities), a facility panel (9 facilities, 2020–2025), Japanese site-level measured emissions (23 sites, FY2023), scenario budgets and price paths (2 scenarios, 2025–2050), technology options (17), price history (18 series, 2015–2030), policy support (6 instruments), company financials (4 firms, 2020–2025) and disclosed plans (12 rows). Every row is keyed to a register of 80 sources, and the manuscript draws only on registered sources, so that citation integrity can be checked automatically.

The sample is not hidden. The disclosed-plan file has twelve rows: itemised, the four firms' transition plans are twelve lines long. The thinness is in the object being measured, not in the collection.

### 4.2 Confidence grades — what we cite and what we made

The parameter inventory (S3) has 415 rows graded T1 (statutory) to T5 (our estimate). Only 21 rows carry a [low, high] band, and at the start of this work the bands belonged to two T1 and sixteen T5 rows: *every one* of the 257 rows in the evidentiary grades T2–T4 was a point estimate. Confidence and dispersion were unrelated: the better the source, the less likely it was to carry a band at all. The literature reports ranges; we had transcribed medians. This is the direct cause of the parameter-uncertainty convention used in Section 6 (symmetric ±30 per cent draws) being a rule rather than evidence.

Of the ten parameters to which the conclusions are most sensitive, four meet the T3-or-better rule. The rest fail for different reasons that call for different remedies: the facility emission factor (rank 1) is a gap the Korean disclosure regime sets — site-level statements exist in the national registry but are not published, whereas Japanese site data are; the discount rate (rank 4) is a choice, handled by re-running the analysis at 3.5, 5.0 and 6.5 per cent; and hydrogen price and volatility are T5 because the series are short, a gap that Section 3.2 shows data cannot close.

### 4.3 Evidence bands — three cells filled, and what they showed

Filling three cells with literature bands (Hüttel and Lehner, 2024; IEA, 2020) found the current value at the edge of or outside the band in all three: H2-DRI capex at the lower end, EAF capex *below* the band (the POSCO Gwangyang project cost, which DIW itself lists at €170/t against a literature band of €254–573/t — 65 per cent of the lower bound; our 240 thousand KRW/t is that project figure), EAF emission factor at the upper end. Bands are converted from €2022 at 1,457.8 KRW/€ (USD/KRW 1,350 × EUR/USD 1.08). Each time we had taken the lowest cited value without checking where it sat in the distribution. We did not change the values — changing them without checking boundary definitions would turn data into taste — but carry the bands into Section 6, where they move the steel parameter share of TCaR from 22 to 36 per cent.

### 4.4 Four genuine gaps

The data audit flags four partially missing columns: the Korean 2025 hydrogen contract price, LOTTE 2021 revenue, and capex and net debt for POSCO and LOTTE, the last two a boundary problem (steel-only separate accounts versus holding-company consolidated). The financial gaps affect only the funding-burden indicators (peak capex and net debt relative to EBITDA), not the headline numbers, but those indicators are where the question "can this firm carry this plan" is answered, and the net-debt part of it is unanswered for two firms. Blocked collections are listed with attempted routes and blocking reasons rather than filled.

---

## 5. Results

### 5.1 Two numbers per firm

| Firm | Abatement cost NZ15 (th. KRW/tCO₂) | B20 | TCaR NZ15 (KRW bn) | Cost gap | Risk gap |
|---|---|---|---|---|---|
| POSCO | 115.0 | 43.8 | 26,752.6 | — (disclosed EAF route not admissible) | — |
| Nippon Steel | 155.6 | 86.2 | 32,961.3 | 1,254.5 | 4,651.2 |
| Mitsui Chemicals | 241.7 | 160.4 | 864.1 | 712.5 | 969.5 |
| LOTTE Chemical | 279.2 | 170.4 | 2,242.2 | — (disclosed CCUS not in technology set) | — |

Three readings. *(a) The ranking does not depend on the scenario.* The ascending order of abatement cost is the same under NZ15 and B20. Steel abates more cheaply per tonne than petrochemicals because there is more to abate (blast furnaces) and a technology exists to abate it. The petrochemical unit cost is high not because the technology is dear but because the denominator is small. *(b) Unit cost and total risk measure different things.* LOTTE has the highest unit cost but a TCaR only 2.6 times Mitsui's; scale pulls both indicators toward steel, and the two diverge only between the two petrochemical firms. *(c) The gap is computed for two of four firms.* POSCO's disclosed EAF route is excluded by the model's technology-availability rule, and LOTTE's disclosed CCUS is absent from the technology set. Those cells are blank because the model cannot represent the plan, not because the disclosure is poor. The distinction matters: read carelessly, the table can look like a sample selected for its large gaps.

Nippon Steel's disclosed plan sits 1,254.5 bn KRW from the frontier along the cost axis at its own risk level, and 4,651.2 bn along the risk axis at its own cost; Mitsui's sits 712.5 and 969.5 away. In both cases the risk gap exceeds the cost gap, so the disclosed plans are closer to efficient on expected cost than on tail exposure (Fig. 1).

> **Figure 1.** Intra-firm efficiency frontiers under NZ15 with no support, one panel per firm: expected incremental cost (P50) against tail cost-at-risk (TCaR = P90 − P50), both in KRW bn. Dark points and line: non-dominated frontier; light points: dominated candidate plans after canonical re-gridding; star: disclosed plan (Nippon Steel and Mitsui Chemicals only). Frontier points are labelled by PPA share; open markers are rungs with fixed-price EPC. Nippon Steel's disclosed plan sits to the right of and above its frontier, Mitsui's far to the right of a frontier that is nearly vertical. Source: model output for the base run; plotting code is in the replication package.

The funding-burden indicator translates these numbers into balance-sheet terms. Peak-year capex of the minimum-cost NZ15 plan is 1.9 times POSCO's three-year average EBITDA and 0.6 times Nippon Steel's, 0.03 times Mitsui's; LOTTE's reference EBITDA is negative over 2023–2025 and no ratio is produced, which is a verdict in itself. (full indicators in S7) Peak capex is identical along each firm's frontier ladder, since the contract rungs change prices and not the build schedule, so the ratio characterises the firm rather than one plan. (Net debt, the other half of the indicator, is not collected for POSCO and LOTTE, as Section 4.4 explains, so the verdicts below rest on the capex ratio alone.) The question "can this firm carry this plan" therefore has four different answers in the sample, and we quote the pipeline's own verdict labels. Peak capex sits within half a year's EBITDA for Mitsui and within one year's for Nippon Steel. It exceeds peak-year EBITDA for POSCO, so external funding is required under any plan on the frontier, and LOTTE's EBITDA is negative, so self-funding is impossible and no ratio is reported. TCaR itself is a present value over 26 years and is not divided by annual EBITDA here. The relevant comparison is with contingent debt capacity, which Section 7.1 takes up.

### 5.2 What moves along the frontier is contracts, not technology

Under NZ15 with no support there are 24 non-dominated frontier points across the four firms.

| Firm | Rung | PPA share | EPC | P50 (KRW bn) | TCaR (KRW bn) | Price of risk (ΔP50/ΔTCaR) |
|---|---|---|---|---|---|---|
| Nippon Steel | min-cost | 0.00 | 0 | 53,305.2 | 32,961.3 | — |
| | first rung | 0.25 | 0 | 54,958.5 | 27,247.7 | 0.289 |
| | min-risk | 1.00 | 0 | 57,961.6 | 17,788.8 | 1.126 |
| POSCO | min-cost | 0.00 | 0 | 41,569.0 | 26,752.6 | — |
| | first rung | 0.25 | 0 | 42,537.7 | 23,004.7 | 0.258 |
| | min-risk | 1.00 | 0 | 45,418.0 | 17,363.6 | 9.550 |
| Mitsui Chemicals | min-cost → min-risk | 0.00 → 1.00 | 0/1 | 310.9 → 484.0 | 864.1 → 828.2 | 0.228 – 12.950 |
| LOTTE Chemical | min-cost → min-risk | 0.00 → 1.00 | 0/1 | 775.9 → 1,239.0 | 2,242.2 → 2,129.1 | 0.567 – 4.486 |

(All 24 rungs in Table S5; the price of risk is between adjacent rungs and is blank where the TCaR reduction is below reporting precision.)

In all sixteen groups every frontier point uses the same base technology schedule. The frontier is not a trajectory of what to build when. It is a *ladder* of contract choices, PPA share and fixed-price EPC, laid on one technology schedule. The only instrument that buys down risk is procurement, and the technology schedule is pinned at the cost minimum.

We checked that this is not an artefact of a thin candidate set by forcing diversity: ε-constraints on the technology-schedule axis produced 32 forced caps, all feasible and all new schedules. Under the headline convention only four of them are non-dominated; under the convention in which the carbon price is stochastic, 25 are, and the technology axis returns in seven of eight groups. *The contract-traced frontier is a consequence of the risk convention, not of the data.* With a deterministic carbon price within a scenario, abatement moves exposure from carbon to electricity, hydrogen and construction cost, all of which are stochastic, so deeper abatement raises tail risk and the cost-minimal schedule dominates. Under the current convention the frontier is honestly described as a *contract-and-capital* allocation frontier.

The price of risk differs by an order of magnitude between the two industries. Over the full ladder, removing one won of TCaR costs 0.31 won of P50 for Nippon Steel and 0.41 for POSCO, against 4.8 for Mitsui and 4.2 for LOTTE (equivalently, 3.27, 2.44, 0.21 and 0.24 won of tail risk removed per won of expected cost). Rung by rung the contrast is sharper: steel buys its first three rungs at 0.22–0.29 won per won of risk removed, petrochemicals pay 2.7–13.0. A PPA is a hedge in steel and merely expensive electricity in petrochemicals.

The mechanism is visible in the variance decomposition of each plan's cost distribution. At the minimum-cost point, electricity accounts for 64 per cent of Nippon Steel's cost variance and 47 per cent of POSCO's, hydrogen for most of the rest; for Mitsui and LOTTE electricity accounts for essentially none of it and hydrogen for all. A renewable PPA fixes the electricity price and nothing else. In steel it therefore removes the largest single source of variance. In petrochemicals it removes a source that was not there, while the contract premium is paid regardless, and as the PPA share rises the electricity share of *remaining* variance rises (to 23–25 per cent at full PPA) because the PPA itself introduces a fixed-price-versus-market exposure. The petrochemical tail is a hydrogen tail, and the instrument that would hedge it, a fixed-price hydrogen offtake, is not in the contract set (Fig. 3).

Whether the steel–petrochemical contrast is an industry effect or a scale effect cannot be separated with two firms per industry (Section 7.2); what can be said is that it is an *exposure* effect, and that the model's contract menu is the binding constraint on the petrochemical frontier.

> **Figure 3.** Variance decomposition of plan cost (electricity, hydrogen, capex shares) along each firm's frontier ladder from PPA share 0 to 1, one panel per firm. In steel the electricity share falls from 47–64 per cent to under 10 per cent by the 0.75 rung; in petrochemicals it never exceeds 25 per cent and hydrogen dominates at every rung. The electricity share rises again at full PPA because the contract itself introduces a fixed-price-versus-market exposure. Source: variance decomposition of the simulated cost distributions along each frontier ladder.

### 5.3 Policy wedge: the stricter scenario has the smaller tail

Revaluing the same plan under both scenarios, NZ15 TCaR is lower than B20 TCaR for all four firms.

| Firm | NZ15 P50 | B20 P50 | NZ15 TCaR | B20 TCaR | B20-optimal P50 |
|---|---|---|---|---|---|
| POSCO | 41,569.0 | 40,665.5 | 26,752.6 | 29,240.1 | 12,029.1 |
| Nippon Steel | 53,305.2 | 52,017.8 | 32,961.3 | 35,024.3 | 20,388.7 |
| Mitsui Chemicals | 310.9 | 352.9 | 864.1 | 993.5 | 57.9 |
| LOTTE Chemical | 775.9 | 879.8 | 2,242.2 | 2,576.7 | 117.2 |

The mechanism is simple. These plans have abated most of their emissions, and the remaining risk comes from the dispersion of the carbon price faced by residual emissions. NZ15 has a high price level but a path tied to a budget and therefore less dispersed, while B20 has a lower level and a wider spread. The statement of Section 2.2, that policy risk enters as price collapse and discretion rather than as regulatory tightening, appears here as a number. Note what is held fixed: this is the *same plan* revalued under two price regimes. When firms are instead allowed to *re-plan* for a lenient regime, they abate less and the tail shrinks for a different reason, namely that the transition itself shrinks (Section 6.2). The two results are not in tension. One measures regime risk for a committed plan, the other the plan a firm would choose if the regime were known.

Regret at the median is, however, large. By regret we mean the cost of a committed plan relative to the plan that would have been optimal had the scenario been known, the quantity robust-decision analysis minimises (Lempert et al., 2006). On a total-cost basis, since the resource-cost basis of the tables above subtracts carbon expenditure and so flatters the less-abating plan, holding the NZ15 plan when B20 materialises costs POSCO 22.1 tn and Nippon Steel 23.3 tn KRW more than that scenario's optimal plan, one and a half to two and a half times the tail risk the full contract ladder removes (Table 5.2: 15.2 and 9.4 tn).

#### 5.3.1 Adding the reverse direction changes the basis of the conclusion

When the reverse direction, holding the B20 plan when NZ15 arrives, is computed on the same total-cost basis, the regret is *negative* for three of four firms.

| Firm | Forward regret (total cost) | **Reverse regret (total cost)** | Reverse budget overshoot (MtCO₂) | Break-even sanction (th. KRW/tCO₂) |
|---|---|---|---|---|
| POSCO | 22,100.1 | **−7,766.5** | 213.0 | 36.5 |
| Nippon Steel | 23,315.2 | **−9,918.8** | 251.9 | 39.4 |
| Mitsui Chemicals | 184.4 | **+33.3** | 2.9 | — |
| LOTTE Chemical | 573.1 | **−31.2** | 6.5 | 4.8 |

(Forward = holding the NZ15 plan when B20 materialises; reverse = holding the B20 plan when NZ15 materialises; both relative to the realised scenario's optimal plan. Resource-cost-basis values in Table S4.)

On money alone, delay wins. Holding the lenient plan when the strict scenario arrives, POSCO spends 7.8 tn KRW *less*, by overshooting the budget and paying the carbon price on the excess. What differs in the reverse direction is not money but tonnes: 213 Mt for POSCO and 252 Mt for Nippon Steel, an order of magnitude above the forward case. The conclusion therefore rests on different ground. The sanction per tonne of overshoot at which reverse regret is zero is 36.5 thousand KRW for POSCO and 39.4 for Nippon Steel. The enumerator penalises overshoot at max(2 × carbon price, 300 thousand KRW/tCO₂), so inside the model early action wins by a factor of eight. The 300 is a modelling assumption, however, not an observed penalty. What supports early transition in this paper is not a price forecast but whether the carbon budget is *enforced in quantity*. In a regime where allowance prices stay below 40 thousand KRW/tCO₂ and overshoot carries no separate sanction, the signs in the table are the firm's incentives. Section 6.3 shows that Korea and Japan sit on opposite sides of that condition.

### 5.4 The support axis is empty

Every result is computed twice, once with no support policy and once with current support, and in all eight firm × scenario cells the two settings give identical headline values. The reason is data, not model: the support dataset contains zero rows of capex subsidy or CCfD, and the instruments it does contain, the K-ETS Phase 4 auction share and the GX-ETS price collar, apply regardless of the support state. We report this as a result because a reader who sees both settings will assume support policy was examined. It was not, and the finding will change the day subsidy rows enter the data.

---

## 6. Robustness

### 6.1 Eight axes shaken; the ranking never reversed

| Check | What moved | Rank preserved | Headline change |
|---|---|---|---|
| Decision criterion P50 → P90 | risk preference | yes | abatement cost ×1.4–3.9 |
| Five seeds | randomness | yes | CV ≤0.81% (cost), ≤1.75% (TCaR) |
| Parameter propagation, ±30% convention | top-10 parameters | — | parameter share of TCaR 26–44% |
| Parameter propagation, literature bands | top-10 parameters | — | 26–54% |
| Price process GBM → OU | stochastic process | yes | TCaR ×0.52–0.59 |
| Forced candidate diversity (Section 5.2) | technology-schedule caps | — | 4 of 32 non-dominated (headline), 25 (stochastic carbon) |
| Back-cast 2020–24 | — | — | emission-intensity error up to 17.5% (Nippon Steel) |
| Budget-overshoot penalty floor | sanction level | — | reverse-regret sign flips at 4.8–39.4 th. KRW/tCO₂ |

("—" in the rank column means the check does not re-rank firms: it propagates uncertainty, forces candidates, back-casts, or sweeps a post-hoc valuation parameter rather than re-computing the four abatement costs.)

On every axis that can test it, the abatement-cost order POSCO < Nippon Steel < Mitsui < LOTTE holds, and twelve scenario bundles add zero reversals. Not reversing is not the same as not moving: the absolute TCaR moves by nearly half on the process choice alone, a quantity of the same order as or larger than the parametric share, and one that data cannot reduce. *TCaR is to be quoted by order and magnitude, not by level.*

### 6.2 Opening every channel: no "flat" axis was flat

Twelve scenario bundles map one corporate question each to a parameter change. Five of them act on plan *choice* and are read only by the enumeration stage: auction-share acceleration and relaxation, PPA premium, retirement cap, penalty floor. An earlier version of this work reused one enumeration across bundles to save computation and reported those five as "flat". They were not flat. They had no channel. Re-planning each:

| Bundle | Re-planned | Max \|Δ\| abatement cost | Max \|Δ\| TCaR | Direction | Rank |
|---|---|---|---|---|---|
| Retirement cap 20 → 40% | yes | **41.2%** | **51.9%** | both fall (steel) | kept |
| Slower auctioning (≤60% auctioned by 2050) | yes | **39.0%** | **99.7%** | both fall (all firms) | kept |
| Hydrogen price ±30% | no | 27.0% / 26.9% | 30.4% / 29.9% | petrochemicals ∓27–30%; steel only ∓5–17% | kept |
| Faster auctioning (100% by 2040) | yes | 19.7% | **61.5%** | both rise (all firms) | kept |
| Electricity price +30% | no | 5.8% | 19.5% | steel rises; petrochemicals unmoved | kept |
| Discount rate 3.5% / 6.5% | yes | 5.4% / 1.2% | 34.4% / 26.4% | TCaR rises at 3.5% / falls at 6.5% | kept |
| Relining cost ×0.235 | no | 2.0% | 0.1% | steel cost falls slightly | kept |
| Overshoot penalty floor 300 → 0 | yes | 1.6% | 5.9% | steel only, mixed signs | kept |
| PPA premium ×2 | yes | 1.4% | 8.1% | LOTTE only (re-plan); others unmoved | kept |

(Percentages are the largest absolute change across the four firms; per-firm values in Table S4.)

The two auction bundles are mirror images, and the mechanism is the same in both directions. With faster auctioning, re-planning lets firms buy more expensive abatement earlier to avoid the auction bill, and unit cost and funding burden rise *together* (POSCO TCaR 26,752.6 → 40,811.3). With slower auctioning, where free allocation persists so that the auctioned share reaches only 60 per cent by 2050, the opposite happens and it is the largest movement in the table: firms re-plan toward *less* abatement, capex falls (POSCO 20,565 → 13,019; Nippon Steel 32,617 → 28,307), and TCaR falls with it (POSCO 26,753 → 15,964) — in petrochemicals almost to zero (LOTTE 2,242 → 17; Mitsui 864 → 3), because the re-planned petrochemical plans are close to the lenient-scenario plans of Section 5.3 and carry almost no stochastic exposure. The 99.7 per cent is therefore not a blow-up but a collapse: under persistent free allocation the tail disappears because the transition does.

Raising the retirement cap works through a third channel. Steelmakers retire capacity instead of converting it, so abatement cost falls 41 per cent for POSCO (115.0 → 67.6) and TCaR halves. That makes the 20 per cent cap, a demand-and-market-position proxy, one of the most consequential assumptions in the model. The ranking holds in all three.

The bundle that doubles the PPA premium, the first thing a referee will question given Section 5.2, leaves the headline numbers of three firms untouched and moves LOTTE's by 1.4 and 8.1 per cent through re-planning. That is the expected null, not a robustness result: the headline is read at the minimum-cost rung, where the PPA share is zero, so the premium cannot reach it. What the premium does move is the *slope* of the ladder, and the re-planned frontiers show exactly that: with the premium doubled, every TCaR rung is unchanged (a PPA fixes the electricity price whatever it costs) while the P50 rungs rise, so the full-ladder price of risk goes from 0.31 to 0.41 won per won for Nippon Steel, 0.41 to 0.60 for POSCO, 4.8 to 6.2 for Mitsui and 4.1 to 6.4 for LOTTE. The ladders stay monotone in PPA share and the steel–petrochemical ratio stays between ten and fifteen to one, as in the base case. Full ladders are in Table S5. The hydrogen and electricity bundles repeat the exposure pattern of Fig. 3: ±30 per cent on hydrogen moves petrochemical cost and tail by 27–30 per cent and steel by 5–17, while +30 per cent on electricity moves only steel.

Re-planning costs 12–32 minutes of computation per bundle, and we no longer report a bundle that has not been re-planned.

### 6.3 The conclusion of Section 5.3 hangs on one configuration line — so we made it an axis

The canonical cost deliberately excludes the enumerator's overshoot penalty (a search device, not a cost), so the sanction φ per tonne of overshoot can be swept after the fact.

| φ (th. KRW/tCO₂) | POSCO | Nippon Steel | Mitsui | LOTTE | Early wins |
|---|---|---|---|---|---|
| 0 (no separate sanction) | −7,766.5 | −9,918.8 | +33.3 | −31.2 | 1 / 4 |
| 50 | +2,883.3 | +2,674.6 | +180.7 | +295.0 | 4 / 4 |
| 150 (inventory low) | +24,182.8 | +27,861.5 | +475.5 | +947.5 | 4 / 4 |
| 300 (configuration) | +56,132.1 | +65,641.8 | +917.6 | +1,926.2 | 4 / 4 |
| 600 (inventory high) | +120,030.7 | +141,202.3 | +1,801.9 | +3,883.6 | 4 / 4 |

Read as a parameter, the conclusion is robust: the latest sign change is at 39.4, and the lower edge of the inventory band is 3.8 times that. Read as an institution, it is not. φ = 0 is not a value outside the band but a *different regime*, a voluntary corporate budget whose overshoot carries nothing beyond the allowance price. Band robustness therefore does not defend the conclusion; the statutes do, and they do not say the same thing in the two countries (Fig. 2).

Korea's emissions trading act penalises a shortfall at up to three times the average market price of the compliance year, subject to a ceiling of 100 thousand KRW per tCO₂ (ICAP, 2026a; ADB, 2018). That ceiling is about two and a half times the largest break-even sanction in our sample, so under the statutory maximum early action wins for the Korean firms on money alone. Japan's GX-ETS, whose mandatory phase began in April 2026, works the other way: a firm that cannot surrender enough allowances pays the shortfall multiplied by the ceiling price and a factor of 1.1, with the ceiling set at 4,300 JPY per tCO₂ for FY2027 (ICAP, 2026b; METI, 2026). That is a buy-out option, not a punishment, and it caps rather than escalates the cost of overshooting. The sign of our regret result is thus a function of which regime a firm sits in, which is a sharper statement than the one we set out to make and one we could not have reached from the model alone.

Two qualifications. Statutory severity is not enforcement: Calel et al. (2025) find that observed non-compliance in the EU ETS should have produced about €13 billion in fines against roughly €2.1 billion apparently collected, and that variation in fine probability and severity explains only about a tenth of the variation in compliance. A treasury pricing overshoot at the statutory rate would therefore overstate its exposure, and a modeller assuming the statutory rate binds would overstate the case for early action. Kim and Yu (2018) show for Korea that the penalty ceiling propagates into the allowance price itself, so the sanction and the price are not independent axes.

> **Figure 2.** Reverse regret (holding the B20 plan when NZ15 materialises, total-cost basis, KRW bn) as a function of the sanction φ per tonne of budget overshoot, one line per firm, with the sign-change points (4.8, 36.5, 39.4 thousand KRW/tCO₂) and the inventory band [150, 600] marked. One panel per industry because the vertical scales differ by a factor of about forty; the inset in each panel enlarges the sign-change region φ ≤ 50. Mitsui alone has no sign change: its reverse regret is already positive at φ = 0. Below the marked break-even, delay wins on money for three of four firms. Source: the post-hoc sanction sweep described in Section 6.3.

### 6.4 What this section does not claim

All axes were shaken on the same candidate set, whose thinness is addressed separately by the forced-diversity check. The support axis and the five once-"flat" bundles are evidence of nothing until re-planned. Seed CVs measure sampling error only.

---

## 7. Policy implications and limitations

### 7.1 Implications

*For transition-plan assessment.* An alignment verdict without a cost–risk coordinate cannot distinguish a firm that can close its gap cheaply from one that cannot. Nippon Steel's disclosed plan is closer to efficient on cost than on risk. An alignment score cannot carry that, and it is what an investor needs in order to decide whether engagement should target technology choice or procurement.

*For electricity-market design.* If the frontier is traced by the PPA share, then corporate PPA access is transition-risk policy. In Korea, corporate procurement runs through two channels created only recently: the KEPCO-intermediated third-party PPA (June 2021) and the bilateral direct PPA under Article 16-5 of the Electricity Business Act (September 2022). Both still carry network-usage fees, KPX settlement charges and a fund levy on top of the contract price. A 2024 complaint over double-charged network fees is unresolved, and on-site capacity floors were removed only in July 2025 (King & Wood Mallesons, 2025). In Japan, off-site physical and virtual corporate PPAs have grown under the FIP regime since 2022.

Whether the cheapest rung of the steel ladder, at 0.22–0.29 won per won of risk removed, exists in practice therefore depends on fee design and contractable volume, neither of which the model's PPA premium yet encodes. A steelmaker contracting 100 per cent of several TWh a year is far outside the current Korean market's deal sizes. The ten-fold asymmetry says this lever is worth building for steel and nearly worthless for petrochemicals, whose tail is a hydrogen tail and would need a fixed-price hydrogen offtake, an instrument that the model's contract set, and for now the market, does not contain.

*For transition finance.* TCaR is a contingent quantity, funding the firm needs only in the adverse decile, and a contingent need is matched by a contingent instrument rather than a grant. The natural forms are a state guarantee or first-loss tranche on transition debt sized to TCaR (a present value, so the guarantee caps cumulative calls rather than setting an annual line), or a contract-for-difference whose payout is triggered by the same price paths that generate the tail. Both let the GX bonds or K-ETS auction revenue of Section 2.4 *de-risk* a plan at an expected fiscal cost far below TCaR itself.

On the simulated cost distributions, a guarantee covering calls between P50 and P90 is drawn on in half of the paths and drawn in full in one path in ten, so its actuarial (risk-neutral) expected payout is 23–24 per cent of TCaR for all four firms. That is the fiscal cost to a state that can diversify the risk across firms and years, not the price a risk-averse guarantor would charge. The residual beyond P90, which such a guarantee does not cover, has an expected size of a further 9–12 per cent of TCaR. For the two steelmakers the quantity to be stood behind is 27–33 tn KRW under NZ15, a lower bound; the policy-risk increment alone adds 2–3 tn, and Section 5.1 shows POSCO cannot carry the base plan from operating cash flow at all.

*For the design of carbon budgets.* The case for early transition is institutional. Unless overshooting a firm's budget carries a sanction above roughly 40 thousand KRW/tCO₂, delay wins on money for three of four firms. The two jurisdictions in our sample have made opposite choices about this. Korea's penalty ceiling sits above the threshold and Japan's buy-out price sits below it, so the same firm-level arithmetic recommends different timing on either side of the strait. A disclosure regime that asks for plans while capping the cost of missing them is asking firms to act against their own arithmetic.

This also locates our result relative to the sector literature. Bachorz et al. (2026) find that most steel lock-in is avoidable at moderate abatement cost and conclude that early action is cheap. That is a statement about resource cost per tonne abated; ours is a statement about a firm's cash flow including what it pays, or does not pay, for exceeding a budget. The two are consistent, and their difference is the wedge that policy design either opens or closes.

### 7.2 Limitations that could change the direction of the conclusions

| Limitation | What is known | Direction |
|---|---|---|
| Overshoot sanction is unsourced | sign flips at 4.8–39.4 th. KRW/tCO₂ | a sanction-free regime reverses §5.3 |
| Support axis empty | 8 cells identical | support would shrink gap and TCaR together |
| Frontier traced by contracts; candidate set thin | 4 of 32 forced schedules non-dominated | title's "capital allocation" becomes "contract-and-capital" |
| TCaR level rests on the process choice | OU gives ×0.52–0.59 | level uncitable; order survives |
| Fixed-price EPC premium has no sensitivity bundle | EPC appears only on the petrochemical ladders (Table 5.2); its premium was not varied | the petrochemical price of risk could move; steel results unaffected |
| Retirement cap of 20% is a proxy, not evidence | raising it to 40% cuts steel abatement cost 41% and TCaR by half (§6.2) | steel results shift toward closure rather than conversion; ranking holds |
| Four firms; gap for two | model-boundary exclusions | no statistical generalisation claimed |

The first two are data gaps with documented attempted routes. The other five are choices or omissions, and the most we can do is declare them and report the alternative's size. One falsifiable claim remains untested: that the hedge-price asymmetry is an industry effect rather than a scale effect. With four firms the controls (electricity intensity, contractable volume) may not identify it, in which case the claim must be lowered to "an observed asymmetry".

### 7.3 Falsifiable claims

The paper makes five falsifiable claims, each with the observation that would refute it and the code path that produces that observation (Table S8). Two are not refuted, one is untested (the industry-versus-scale question above), and one, that TCaR excludes policy risk, is refuted for the petrochemical firms and not for the steelmakers (Section 2.2). The fifth, that an independently built implementation sees the same level, holds for POSCO's abatement cost (115 inside the independent range 26.6–155.9; S7).

---

## 8. Conclusion

A firm's disclosed transition plan can be given coordinates. Under the same carbon budget the firm could have chosen from a set of plans, and that set has an efficient frontier in the plane of expected cost and tail funding need. For the two firms whose disclosures the model can represent, the disclosed plan lies 1.3 and 0.7 tn KRW from the frontier on cost and 4.7 and 1.0 tn on risk. What traces the frontier is the choice of contracts rather than the choice of technology. What the contracts buy differs ten-fold between steel and petrochemicals, and the stricter carbon scenario carries the smaller tail. None of these depends on the level of tail risk, which this paper cannot pin down. Their signs and the firms' ranking survive every assumption we were able to move, while their magnitudes do not — a persistent free-allocation regime or a looser retirement cap shrinks the transition and its tail together. What does not survive the arithmetic is the case for early action on price alone. That case rests on a single institutional condition — that a carbon budget, once disclosed, binds in quantity — and the measurement tool built here is only as useful as the regimes that make it so.

---

## Data and code availability
The model code, configuration, seeds, parameter inventory and a reproducibility package with checksum manifests are deposited in a public archive [DOI to be added on acceptance]. Facility-level outputs are withheld under the project's disclosure policy; firm-level aggregates and all figures are reproducible from the package.

## References

*(Elsevier Harvard style. DOIs were verified against Crossref on 21 August 2026 unless marked [unverified]; entries marked † are not yet in the project's source register.)*

AbdulRafiu, A., 2026. Stranded futures? Quantifying the asset risks of industrial decarbonisation in developed economies. Energy Research & Social Science 133, 104621. https://doi.org/10.1016/j.erss.2026.104621 † [content unverified]

ACCR, 2025. Steelmakers face crunch-time on coal: critical risks in blast furnace relining decisions. Australasian Centre for Corporate Responsibility, 19 May 2025.

Acharya, V.V., Berner, R., Engle, R., Jung, H., Stroebel, J., Zeng, X., Zhao, Y., 2023. Climate stress testing. Annual Review of Financial Economics 15, 291–326. https://doi.org/10.1146/annurev-financial-110921-101555 †

ADB, 2018. The Korea Emissions Trading Scheme: Challenges and Emerging Opportunities. Asian Development Bank, Manila. †

Awerbuch, S., 2006. Portfolio-based electricity generation planning: policy implications for renewables and energy security. Mitigation and Adaptation Strategies for Global Change 11, 693–710. https://doi.org/10.1007/s11027-006-4754-4 †

Bachorz, C., Dürrwächter, J., Gong, C.C., Odenweller, A., Pehl, M., Schreyer, F., Verpoort, P.C., Luderer, G., Ueckerdt, F., 2026. The window to avoid locking in decades of steel emissions is closing fast. Nature Climate Change 16, 681–689. https://doi.org/10.1038/s41558-026-02634-9 †

Battiston, S., Mandel, A., Monasterolo, I., Roncoroni, A., 2023. Climate credit risk and corporate valuation. SSRN Working Paper 4124002. https://doi.org/10.2139/ssrn.4124002 †

Bolton, P., Kacperczyk, M., 2021. Do investors care about carbon risk? Journal of Financial Economics 142, 517–549. https://doi.org/10.1016/j.jfineco.2021.05.008 †

Calel, R., Dechezleprêtre, A., Venmans, F., 2025. Policing carbon markets. Climate Policy 25, 1489–1507. https://doi.org/10.1080/14693062.2025.2464699 †

Chan, K.J.D., Cheung, B., Shen, L.Y., 2024. An economic foundation for assessing the credibility of corporate net zero transition pathways. Business Strategy and the Environment 33, 8868–8881. https://doi.org/10.1002/bse.3951 †

Climate Action 100+, 2024. Net Zero Company Benchmark, v2.2.

Conejo, A.J., Carrión, M., Morales, J.M., 2010. Decision Making Under Uncertainty in Electricity Markets. Springer, New York. https://doi.org/10.1007/978-1-4419-7421-1 †

Dietz, S., Bowen, A., Dixon, C., Gradwell, P., 2016. 'Climate value at risk' of global financial assets. Nature Climate Change 6, 676–679. https://doi.org/10.1038/nclimate2972 †

Dixit, A.K., Pindyck, R.S., 1994. Investment under Uncertainty. Princeton University Press, Princeton. †

Ehrenmann, A., Smeers, Y., 2011. Generation capacity expansion in a risky environment: a stochastic equilibrium analysis. Operations Research 59, 1332–1346. https://doi.org/10.1287/opre.1110.0992 †

Fliegel, P., 2026. How you measure transition risk matters: comparing and evaluating climate transition risk metrics. Journal of Corporate Finance 98, 102939. https://doi.org/10.1016/j.jcorpfin.2025.102939 †

Fukuda, S., Ino, A., 2026. Fiscal sustainability of transition finance: implications for the GX economy transition bonds in Japan. Japan and the World Economy 79, 101368. https://doi.org/10.1016/j.japwor.2026.101368 †

Fuss, S., Szolgayova, J., Obersteiner, M., Gusti, M., 2008. Investment under market and climate policy uncertainty. Applied Energy 85, 708–721. https://doi.org/10.1016/j.apenergy.2008.01.005 †

Gabrielli, P., Aboutalebi, R., Sansavini, G., 2022. Mitigating financial risk of corporate power purchase agreements via portfolio optimization. Energy Economics 109, 105980. https://doi.org/10.1016/j.eneco.2022.105980 †

Hoogsteyn, A., Bruninx, K., Delarue, E., 2025. Carbon contracts for difference design: managing carbon price risk in a low-carbon industry. Joule 9, 101921. https://doi.org/10.1016/j.joule.2025.101921 †

Hüttel, A., Lehner, J., 2024. Revisiting investment costs for green steel: capital expenditures, firm level impacts, and policy implications. DIW Discussion Paper 2082, Berlin.

ICAP, 2026a. Korea Emissions Trading System. ETS factsheet, International Carbon Action Partnership, Berlin. †

ICAP, 2026b. Japan GX-ETS. ETS factsheet, International Carbon Action Partnership, Berlin. †

IEA, 2020. Iron and Steel Technology Roadmap. International Energy Agency, Paris.

Kampmann, D., Rekker, S., Ruan, M., Shrimali, G., et al., 2026. Assessing corporate transition plans using a production asset-based planning approach. Nature Communications 17, 6410. https://doi.org/10.1038/s41467-026-72703-2

Kesicki, F., Ekins, P., 2012. Marginal abatement cost curves: a call for caution. Climate Policy 12, 219–236. https://doi.org/10.1080/14693062.2011.582347 †

Kesicki, F., Strachan, N., 2011. Marginal abatement cost (MAC) curves: confronting theory and practice. Environmental Science & Policy 14, 1195–1204. https://doi.org/10.1016/j.envsci.2011.08.004 †

Kim, W., Yu, J., 2018. The effect of the penalty system on market prices in the Korea ETS. Carbon Management 9, 145–154. https://doi.org/10.1080/17583004.2018.1440852 †

King & Wood Mallesons, 2025. Powering data centres in South Korea: understanding and using PPAs. Client insight, Seoul. https://www.kingandwood.com/global/en/insights/latest-thinking/powering-data-centres-in-south-korea-understanding-and-using-ppas.html † [grey literature; replace with the Electricity Business Act Art. 16-5 and MOTIE notice citations before submission]

Klein, S.M.A., Polzin, F., Urbach, X., 2026. Planning to fail? Credibility and financing of corporate transition plans in hard-to-abate sectors. iScience 29, 116282. https://doi.org/10.1016/j.isci.2026.116282 †

Laurikka, H., Koljonen, T., 2006. Emissions trading and investment decisions in the power sector — a case study in Finland. Energy Policy 34, 1063–1074. https://doi.org/10.1016/j.enpol.2004.09.004 †

Lempert, R.J., Groves, D.G., Popper, S.W., Bankes, S.C., 2006. A general, analytic method for generating robust strategies and narrative scenarios. Management Science 52, 514–528. †

Mavrotas, G., 2009. Effective implementation of the ε-constraint method in multi-objective mathematical programming problems. Applied Mathematics and Computation 213, 455–465. https://doi.org/10.1016/j.amc.2009.03.037 †

METI, 2026. Overview of Japan's GX policy and carbon pricing. Ministry of Economy, Trade and Industry, Tokyo. †

Mittler, C., Bucksteeg, M., Staudt, P., 2025. Review and morphological analysis of renewable power purchasing agreement types. Renewable and Sustainable Energy Reviews 211, 115293. https://doi.org/10.1016/j.rser.2024.115293 †

Nicolajsen, A.B., Bjørn, A., McAloone, T.C., Pigosso, D.C.A., 2025. Decoding corporate climate transition plans: a comparative analysis of 14 frameworks. Journal of Environmental Management 393, 127062. https://doi.org/10.1016/j.jenvman.2025.127062 †

Odenweller, A., Ueckerdt, F., 2025. The green hydrogen ambition and implementation gap. Nature Energy 10, 110–123. https://doi.org/10.1038/s41560-024-01684-7 †

Ostrovnaya, A., Ahrens, J., Smart, J., Theocharidou, A., Buhr, B., 2026. Carbon cost pass-through and access to capital shape firms' carbon strategies. Communications Earth & Environment 7, 524. https://doi.org/10.1038/s43247-026-03495-y †

Palmer, O., Radet, H., Camal, S., Kazempour, J., Girard, R., 2025. Hedging hydrogen: planning and contracting under uncertainty for a green hydrogen producer. Energy Economics 152, 108981. https://doi.org/10.1016/j.eneco.2025.108981 †

Pombo-Romero, J., Rúas-Barrosa, O., Vázquez, C., 2024. Assessing the value and risk of renewable PPAs. Energy Economics 139, 107861. https://doi.org/10.1016/j.eneco.2024.107861 †

Richstein, J.C., Anatolitis, V., Blömer, R., et al., 2024. Catalyzing the transition to a climate-neutral industry with carbon contracts for difference. Joule 8, 3233–3238. https://doi.org/10.1016/j.joule.2024.11.003 †

Roques, F.A., Newbery, D.M., Nuttall, W.J., 2008. Fuel mix diversification incentives in liberalized electricity markets: a mean–variance portfolio theory approach. Energy Economics 30, 1831–1849. https://doi.org/10.1016/j.eneco.2007.11.008 †

Rose, A., Shrimali, G., Halttunen, K., 2025. A framework for assessing and managing dependencies in corporate transition plans. iScience 28, 112811. https://doi.org/10.1016/j.isci.2025.112811 †

Saleh, H., Battiston, S., Monasterolo, I., Barreau, T., Tankov, P., 2026. Estimating firms' emissions from asset level data helps revealing (mis)alignment to net zero targets. Nature Communications. https://doi.org/10.1038/s41467-026-70481-5 †

Seltzer, L., Starks, L., Zhu, Q., 2022. Climate regulatory risk and corporate bonds. NBER Working Paper 29994. https://doi.org/10.3386/w29994 †

Tran, L.T.H., Trinh, V.Q., Le, V.T.P., Tu, T.T.K., 2025. Carbon emissions, firm-level climate change exposure, and corporate cash reserves. Business Strategy and the Environment 34, 5158–5180. https://doi.org/10.1002/bse.4188 †

Tranberg, B., Hansen, R.T., Catania, L., 2020. Managing volumetric risk of long-term power purchase agreements. Energy Economics 85, 104567. https://doi.org/10.1016/j.eneco.2019.104567 †

Transition Pathway Initiative, 2023. Methodology and indicators report, v5.0. †

Vogl, V., Olsson, O., Nykvist, B., 2021. Phasing out the blast furnace to meet global climate targets. Joule 5, 2646–2662. https://doi.org/10.1016/j.joule.2021.09.007 †

Vogl, V., Åhman, M., Nilsson, L.J., 2018. Assessment of hydrogen direct reduction for fossil-free steelmaking. Journal of Cleaner Production 203, 736–745. https://doi.org/10.1016/j.jclepro.2018.08.279

Xu, S., Wang, X., Jiang, Y., Yu, B., Wei, Y.-M., 2024. Optimum investment strategy for hydrogen-based steelmaking project coupled with multiple uncertainties. Journal of Environmental Management 356, 120484. https://doi.org/10.1016/j.jenvman.2024.120484 †

Zhou, W., Zhu, B., Fuss, S., Szolgayová, J., Obersteiner, M., Liu, W., 2010. Uncertainty modeling of CCS investment strategy in China's power sector. Applied Energy 87, 2392–2400. https://doi.org/10.1016/j.apenergy.2010.01.013 †

## Supplementary Information (outline)
S1 MILP formulation and assumption register A-01–A-23 · S2 Correlated price process, calibration, and process tests · S3 Parameter inventory (415 rows) and evidence bands · S4 Scenario bundles and re-planning protocol · S5 Full frontier ladders (24 rungs), variance decomposition by rung, and the ladders re-planned under a doubled PPA premium · S6 Surrogate-vs-canonical diagnostics · S7 Cross-implementation check; affordability indicators · S8 Falsifiable claims FC1–FC5: statement, refuting observation, code path, status.
