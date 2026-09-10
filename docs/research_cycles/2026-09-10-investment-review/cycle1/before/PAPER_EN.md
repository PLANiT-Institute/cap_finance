# Comparing Industrial Transition Plans under Energy Price Uncertainty

## A pilot methodology for process choices contracts and investment timing

Jinsu Park | PLANiT Institute | September 2026

### Abstract

Industrial transition plans alter technology, investment timing and procurement exposure. This pilot compares feasible plans under matched production, emissions and cash accounting boundaries. Transition Cost at Risk (TCaR) shows the gap between median cost and an adverse cost quantile; expected cost and Expected Shortfall (ES) support plan selection. A four company exercise and separate process references show that risk criteria change contract choices, electricity emissions alter eligible investment dates, and procurement assumptions materially affect cost tails. The purpose is to support investment review and contract discussions while identifying evidence needed for defensible decisions. The next phase couples the framework to PLANiT’s energy modelling system and a planned public abatement technology database to improve scenario consistency and independent reproducibility. Current findings establish conditional pilot value rather than calibrated corporate risk or investment recommendations.

{{fig:tcar}}

Figure 1. Main pilot result illustrated by the naphtha cracker reference. Lines connect P50 to P95: their length is TCaR95. Diamonds show ES95. Solid and dashed lines are independent 5,000 path pools; labels give TCaR95 for both. Units are million EUR with an assumed 2019 operating price basis. The three dates qualify under the lower initial grid case in Section 8. These are conditional quantiles, not confidence intervals. Source: [D3].

**How to use the result.** In this reference, moving commissioning from 2030 to 2040 reduces TCaR95 from 744.9–839.5 to 419.8–476.4 across the two pools, alongside lower cost levels. Investment review should compare both the cost level and its adverse spread; the preferred date remains conditional on the candidate menu and emissions rule.

\pagebreak

### 1 Research question and contribution

For a given production service and emissions requirement, which feasible changes in technology, commissioning date and procurement improve the level or upper tail of transition cost? This is a within firm question. Cross company rankings are not identified by the present data.

The intended users are corporate investment teams and researchers evaluating transition finance applications. The proposed contribution is a traceable connection between process quantities, shared market shocks and actual decision alternatives. The relevant test is whether the connection changes an admissible plan or the evidence needed to select it. Running simulations and publishing a database are useful capabilities, but neither alone establishes a new economic result.

### 2 Economic interpretation and related research

Mean–risk analysis has a long history in portfolio choice, and Expected Shortfall provides an established way to evaluate large losses, including discrete distributions [1–3]. Industry studies already compare abatement technologies across input prices and provide open data and tools [4]. Process studies supply detailed reference configurations for hydrogen steelmaking and electrified ethylene production [5–6]. This paper builds on these approaches by checking how process boundaries, procurement exposures and discrete investment schedules jointly determine comparable cost distributions.

The relevant economic mechanisms differ. Changing a process can reduce or substitute physical exposure. A fixed price contract reallocates price risk and generally charges for that service. Holding liquidity changes the ability to absorb a loss. A subsidy reallocates expenditure between the firm and the public sector. These mechanisms should not all be called a reduction in aggregate economic risk.

A deterministic cost model can price a contract premium. Under fixed quantities and correctly mean-normalised linear prices, it can also calculate expected cost exactly. What expected cost alone does not determine is the value a decision maker assigns to reducing expensive tail outcomes. We therefore compare expected cost and ES without inferring an unobserved risk preference from a single chosen plan.

### The pilot hypothesis

Adding consistent process, emissions and procurement information can change feasible alternatives or their cost–risk ordering relative to a central price calculation. The existing experiments demonstrate this possibility under stated assumptions. They do not establish how often this occurs in actual investment decisions or whether the benefit exceeds the cost of collecting better data.

### Why steel and petrochemicals

Hydrogen steelmaking can replace coal exposure with electricity, hydrogen and different iron feedstocks. Onsite hydrogen production and purchased hydrogen are different system boundaries. Naphtha cracker electrification can retain feedstock demand while changing electricity purchases and internal fuel use. This contrast makes the two sectors useful for testing when feedstock costs cancel in incremental comparisons and when they remain material.

Korean and Japanese company names identify the origin of selected disclosures in the frozen exercise. The allocated assets and several common price assumptions are model constructions. National energy systems, procurement practices and corporate scope require separate calibration before country effects can be estimated.

\pagebreak

### 3 Comparable plans and cash accounting

Let x denote a fixed investment and contract plan, s a long term scenario, θ a set of process and procurement assumptions, and ω a conditional price path. Let x₀ be a reference plan delivering the same specified product and quantity. Costs increase in the adverse direction.

{{eq:loss}}

The reference may fail the transition target; it remains a valid cost counterfactual if this is explicit. It can enter the set of selectable transition plans only when it meets the same eligibility requirements.

{{eq:cash}}

K includes initial and replacement cash investment; O denotes other operating expenditure; q is external purchased quantity; Z is the stated carbon payment; H is net contract payment; S is support received; V is recoverable terminal cash. d discounts cash to the valuation date; T is the final year. Sales and internal transfers must be reconciled before forming external net purchases. Existing sunk investment is excluded from future cash expenditure; future replacement is included when required. A noncash impairment is reported separately and is not charged construction price risk or subsidised as new investment.

Both plans must provide equivalent product quality, delivery timing and output. Curtailment requires explicit lost revenue or replacement supply, including displaced emissions. The current company exercise fixes output; it does not solve restructuring or closure decisions.

Annual and cumulative emissions conditions are distinct. Satisfying the sum of annual budgets does not prove compliance in every year. Eligibility also depends on construction lead times, mutually exclusive technologies, infrastructure availability and the chosen emissions scope. Purchased electricity can move emissions outside Scope 1 without delivering an equivalent system reduction.

### Procurement and settlement

An unchanged feedstock quantity cancels only if the two plans have the same pathwise discounted cash payment for that item. Invoice dates, currency, payment dates, quality premiums or contracts can prevent cancellation. With foreign currency procurement, E[PX] = E[P]E[X] + Cov(P,X); separately normalising commodity and exchange rate multipliers does not fix the expectation of their product. Nominal exchange rates and real commodity prices require explicit inflation conversion [D1, D5].

These are private cost comparisons. Removing carbon payments does not convert them into social welfare calculations. Revenues, taxes, financing, risk premia and externalities require a consistent extension.

\pagebreak

### 4 Risk measures and attainable choices

For each eligible plan we report the mean, median, upper quantile, TCaR and ES. The frozen company exercise uses α = 0.90; process references use α = 0.95. Results at different confidence levels are not pooled.

{{eq:risk}}

{{eq:es}}

The ES expression applies to integrable losses and correctly allocates probability mass at a discrete quantile [2]. Stored quantiles and medians use linear interpolation; empirical ES integrates the inverse empirical distribution, including fractional boundary mass. These conventions must be retained in replication.

TCaR is a spread, not a cash funding requirement. Adding a certain cost shifts the mean, quantiles and ES by the same amount while leaving TCaR unchanged. It can also rank a uniformly worse loss as less risky: let X equal 0 with probability 0.8 and 100 with probability 0.2, and let Y always equal 100. At α = 0.90, TCaR(X) = 100 and TCaR(Y) = 0, although Y is never cheaper. A mean plus twice TCaR criterion chooses Y. This is why a low TCaR cannot be the sole recommendation rule [D1].

The primary frontier is the subset of evaluated eligible plans for which no alternative has both weakly lower expected cost and weakly lower ES, with at least one strict improvement. A mean–TCaR display remains a diagnostic. We also check pathwise cost dominance on the simulated sample. Such a check is a sample statement unless an algebraic argument establishes it for all admissible states.

An efficient set can contain one point, several separated points, or be empty when no plan qualifies. Connecting discrete points does not create an executable investment schedule. The search uses mixed integer scheduling and a finite contract menu; the resulting frontier is conditional on that menu, not a certificate of global optimality.

### Decision rule

A reviewer can compare plans at a predeclared ES ceiling or examine mean + λES for λ ≥ 0. The latter preserves loss monotonicity, but may miss some nondominated discrete points. An ES constrained comparison is therefore retained. Risk appetite and the cost boundary must be stated by the decision maker. For an implementable disclosed comparator, cost savings at its ES and ES savings at its mean are separate attainable comparisons, each requiring its own witness plan.

\pagebreak

### 5 Scenarios price paths and identification

Long term scenarios define conditional environments; they are not assigned occurrence probabilities in this pilot. This treatment is consistent with the NGFS scenario framework [7]. Historical price changes describe a separate assumption about fluctuations around those environments, not observed forecast errors of an energy system model.

The frozen company experiment uses local NZ15 and B20 proxy scenarios and positive geometric Brownian motion (GBM) type multipliers. It is not an NGFS or GCAM extraction. Its electricity volatility pools short, heterogeneous tariff and market series; hydrogen and construction volatilities are prior assumptions. These limitations make its tail magnitudes exploratory [D1].

Later process experiments use IEA 2025 price ratios and World Bank monthly benchmarks [8–9]. Demeaned monthly log changes are sampled in common, overlapping, noncircular 12 month blocks. The same block is applied to all six factors to preserve historical within block dependence. Price levels are obtained by exponentiation and normalised using exact finite block exponential moments, without rescaling by the simulated sample mean. Equal monthly purchases imply an arithmetic annual average.

{{fig:scenario}}

Figure 2. Reference scenario inputs, shown as ratios to 2024. The figure reproduces registered IEA nodes with linear interpolation. Applying these benchmark ratios to a plant’s purchase price remains an assumption. Source: [8], [D2].

All plans and their reference use common price paths. Independent evaluation pools test selection stability; resampling whole path indices jointly across plans measures conditional sampling variation. Neither exercise validates the assumed long horizon distribution. Repeated historical crisis blocks and the absence of mean reversion can materially enlarge the tail. Generating more paths cannot repair a misspecified price process.

\pagebreak

### 6 Assumptions that control the comparison

Table 1 separates the frozen company case from the later reference modules. Model settings are not estimates merely because they have precise numerical values.

{{table:assumptions}}

{{fig:discount_grid}}

Figure 3. Illustrative discount factors at 3%, 5% and 7%, alongside the two assumed electricity emissions paths in the timing experiment. Only the 5% case is used in the displayed reference cost results; the other discount curves show weighting, not rerun risk estimates. The electricity paths are sensitivity conditions, not national forecasts.

Specifications from different papers are kept as internally consistent packages. For example, total electricity including onsite electrolysis cannot be combined with a separate purchased hydrogen bill. Residual emissions, coproduct sales, useful steam recovery and replacement lives affect both the feasible set and cost. Technical ranges are not automatically probability distributions.

\pagebreak

### 7 What the frozen company exercise establishes

The original conditional case covers 22 allocated model assets associated with POSCO, Nippon Steel, LOTTE Chemical and Mitsui Chemicals, 45 schedules and 450 schedule–contract combinations over 2027–2050. Each schedule is evaluated at five electricity contract shares and two construction contract states. All 45 schedules satisfy the period cumulative Scope 1 cap; none satisfies every annual cap [D1].

{{table:choices}}

Table 2. Contracts selected from the same menu. Entries show electricity fixed price share and engineering, procurement and construction (EPC) contract state, where 1 indicates application. Expected cost selects no contract in all eight cases; the other criteria select electricity coverage of 75–100%. These stylised contracts carry assumed premia and are not quoted commercial power purchase agreements (PPAs). Source: [D1], criterion comparison.

The main contribution of this table is the kind of decision that changes. In three petrochemical company–scenario cases, risk criteria also change the selected physical schedule. In the four steel cases and LOTTE B20, the physical schedule is unchanged across the three criteria. This distinction is more informative for the pilot than ranking corporate monetary risk levels.

The mean based selection is stable across two additional independent 10,000 path pools. TCaR selections change in three and two of eight cases; ES selections change in one and zero. Enlarging the schedule menu from 22 to 45 reduces Mitsui B20’s minimum TCaR90 from 849.91 to 220.11 in the run’s declared billion KRW unit, without changing the minimum mean choice. Stable expected cost selection therefore does not establish adequate risk frontier exploration.

Absolute corporate amounts are deliberately secondary because asset allocation, monetary bases and procurement parameters remain incompletely matched. The company run’s negative mean increments for NZ15 steel rely on avoided deterministic carbon charges. They cannot be read as verified profits or current country specific net carbon payments. This boundary limits the external claim, while preserving the decision comparison as a computational pilot.

\pagebreak

### 8 Electrification timing requires an emissions test

The naphtha cracker (NCC) reference supplies 920,000 tonnes of ethylene annually. It compares commissioning in 2030, 2035, 2040 and 2045 against continued conventional production. Construction lasts three years. Purchased electricity rises from 0.083 to 1.942 MWh per tonne of naphtha; direct process emissions are 0.397 and assumed zero tonnes CO₂ per tonne of naphtha. Other residual emissions are tested separately [6, D3].

{{fig:ncc_eligibility}}

Figure 4. Cumulative emissions relative to continued operation under the same electricity path, with zero residual emissions. The dashed line is the assumed 75% cap. At an initial grid factor of 0.2, three schedules qualify; at 0.4, only 2040 qualifies. All also require zero terminal emissions. Source: [D3].

{{table:ncc}}

Table 3. Incremental cost conditional on the reference assumptions, in million EUR with an assumed 2019 real operating price basis. Means are analytical; TCaR95 and ES95 use two independent 5,000 path pools. Source: [D3].

At the lower initial grid factor, 2040 has the lowest mean and ES in both pools, so the evaluated frontier contains one point. This does not establish an optimal investment year outside this menu. The choice reflects the assumed replacement cycle, discounting and emissions rule. All 16 combinations of date, grid path and residual condition fail the separate annual linear cap; residual emissions of 0.05 tonnes CO₂ per tonne of naphtha also make the terminal zero condition infeasible for every date.

The 2040 TCaR95 estimates are 419.8 and 476.4. Conditional bootstrap intervals are 383.0–451.0 and 433.3–510.6. Stable choice and precise risk magnitude are different outcomes. Holding prices fixed while varying grid emissions isolates eligibility; it does not establish joint power price and emissions consistency.

\pagebreak

### 9 Procurement assumptions can dominate a reference tail

A separate steel experiment keeps the Vogl reference quantities at 3.48 MWh electricity and 1.504 tonnes pellets per tonne of liquid steel. The assumed plant produces 0.75 million tonnes annually from 2030 to 2050, following three construction years, at a 5% discount rate. Onsite electrolysis is included; purchased hydrogen is not added [5, D4].

Pellet price is represented by 100[(1 − β) + βMᵒʳᵉ], with β = 0, 0.5 or 1 and E[Mᵒʳᵉ] = 1. Electricity uses a separate 40 EUR/MWh reference with half fixed and half linked to the IEA Japan LNG ratio and shock. β is an unestimated mapping assumption, not a contract that the firm can freely choose. Real pellet prices include grade and delivery components, which also affect process performance [10].

{{fig:steel}}

Figure 5. Absolute reference cost ES95 across pellet indexation assumptions. Two independent pools each contain 5,000 paths. The common theoretical mean is 3,971.2 million source EUR. Mixed source monetary bases have not been harmonised into a verified current price year. Source: [D4].

From β = 0 to β = 1, ES rises from 5,532.6 to 9,732.4 in pool 1 and from 5,527.8 to 9,923.6 in pool 2, increases of 75.9% and 79.5%. The theoretical mean is unchanged. These points form a sensitivity comparison, not an efficient frontier: the assumptions are not priced feasible contracts, and the experiment lacks a matched incumbent subtraction and emissions qualification.

Tail contributions must be measured on the same high total cost paths. Summing each component’s separate tail mean overstates or otherwise misrepresents the total ES. In this experiment, a changing composition of total cost tail states lowers electricity’s ES minus mean contribution as pellet indexation rises. That is a conditional allocation result, not evidence that electricity itself became safer.

The economic lesson is specific: mapping a public benchmark to an actual purchase can materially affect a tail estimate. The experiment does not establish that procurement uncertainty always exceeds technology or price process uncertainty.

\pagebreak

### 9A Reading TCaR and using the results

Figure 1 introduces the main cost and risk comparison. TCaR answers a practical question: how far above the median does the specified adverse cost quantile lie? It makes transition cost uncertainty visible in the same monetary units as the plan. The reporting identity is P95 = P50 + TCaR95; ES95 then describes the mean of the worst 5% of costs. These are complementary views of the same conditional distribution, not competing names for one number.

For 2040, pool 1 has P50 = 1,945.5, P95 = 2,365.2 and TCaR95 = 419.8 million EUR; ES95 is 2,877.8. Pool 2 gives TCaR95 = 476.4. The 419.8 amount is an upper quantile increment above the median of discounted incremental cost. It is not an annual funding deficit or a required reserve. A budget based on the mean or an approved amount B needs its own comparison with P95, rather than adding TCaR to that different baseline.

**Investment review.** Present mean, P50, P95, TCaR, ES and emissions eligibility together. This distinguishes a cheaper plan from one with a narrower adverse cost spread. The NCC example supports comparison within the evaluated menu; it does not identify a universally optimal commissioning date.

**Procurement and support design.** For priced feasible contracts, report the change in expected cost alongside the change in TCaR and ES. A premium per unit of TCaR reduction is descriptive, not a universal willingness to pay. An additive certain subsidy reduces cost levels but leaves TCaR unchanged; contingent protection can alter its spread. Neither metric alone establishes social welfare gains.

**Financing discussion.** TCaR can flag plans requiring further stress analysis. Credit sizing requires a dated cash flow model with revenues, debt service, liquidity and covenants. The current discounted cost measure does not yet establish bankability.

\pagebreak

### 10 What validation does and does not establish

The stored experiments reconcile quantities, cash ledgers and risk summaries against separately written arithmetic checks. The company exercise checks 2,250 candidate statistics. The timing experiment checks 40,000 FIN cost values, and the procurement experiment checks 60,000. These are numerical checks within the specified model; counts do not measure predictive accuracy or independent empirical replication [D1, D3–D4].

{{table:validation}}

Table 4. Distinct validation questions and current evidence. Each row requires a separate judgement; passing one does not establish the next.

A constant cost reduction can be economically valuable without reducing TCaR. In the paired new plant NCC reference, changing the assumed electrified plant life from 20 to 30 years with zero terminal cash reduces mean cost from 3,963.988 to 3,636.696 million assumed EUR2019. ES95 falls by the same amount, while TCaR95 remains 857.615 [D1].

The current literature specification audits also expose unresolved plant boundaries, heat bases and source price years. Retrospective price diagnostics reject a uniform claim that a more elaborate volatility model captures every gas tail. Long horizon tail differences persist across generators after increasing the simulation size. Publication should retain these negative results because they define what the proposed integration needs to improve.

For formal plan selection, independent simulation alone is insufficient. The next analysis must report menu expansion, sensitivity to jointly coherent specifications and forecast diagnostics of procurement prices. A narrow conditional sampling interval should never be displayed as uncertainty about the full corporate transition outcome.

\pagebreak

### 11 Coupling to PLANiT energy modelling

The next phase will couple this decision framework to PLANiT’s energy modelling system. The purpose is to replace loosely connected energy price, supply and emissions assumptions with an internally consistent system context, while preserving plant specific investment and procurement accounting. Existing system capability provides a platform for this work; the coupling and its validation remain research tasks.

{{fig:integration}}

Figure 6. Proposed exchange between PLANiT’s energy modelling system, the public technology database and the plant decision module. Solid arrows denote the proposed first stage exchange; the dashed feedback is a later extension requiring system re-solving. The diagram is a research design, not a claim of completed integration.

For each identified scenario and model version, the exchange should provide carrier prices, supply limits, electricity emissions factors, technology availability and relevant sectoral constraints at consistent region, time and unit boundaries. The plant module returns energy demand by carrier, commissioning schedules and emissions profiles. Wholesale prices still need tariffs, network charges, basis differences and contract terms before they become purchase invoices.

The first stage is one way coupling: system conditions are held fixed while the plant compares a modest candidate menu. The second stage tests whether aggregated plant decisions materially alter electricity, hydrogen or other supply conditions. If they do, demands must be passed back and the energy system solved again. Neither convergence nor equilibrium consistency should be assumed after simply adding stochastic shocks to a central trajectory. GCAM illustrates this distinction between system market conditions and detailed plant decisions [11]; using GCAM is not a claim about PLANiT’s current software architecture.

A separate record must identify which uncertainties the system model already propagates. Only residual uncertainty should be added downstream to avoid double counting. Adaptive operations require decisions to depend only on information available at the decision time. The current fixed schedule comparisons do not estimate the value of such flexibility.

\pagebreak

### 12 Public technology data as a testable research asset

PLANiT plans to make an abatement technology database public as part of the research programme. Its value is that reviewers can trace each technology to a complete process specification and reproduce the consequences of changing it. The pilot does not claim that a complete public release, redistribution permissions or a permanent repository identifier are already in place.

{{table:db}}

Table 5. Minimum proposed public record. Missing values remain explicit; a source citation is not itself evidence that a parameter is applicable to a particular plant.

The release should distinguish original observations, transformed values, reference specifications and researcher assumptions. A versioned case should retain the package actually used, including excluded technologies and reasons for exclusion. Correcting one input must produce a new version with a visible change in emissions qualification or cost results, rather than silently replacing historical results.

Only material that can be redistributed should be included. Public metadata and transformation code can point to restricted source material without redistributing it. Facility level confidential inputs require a separate access boundary. An open, nonconfidential reference case should be sufficiently complete for another team to reproduce the headline tables without author local temporary files. The current full corporate reproducibility bundle does not yet meet that public release standard.

Open data alone is not a sufficient novelty claim because related industrial abatement tools already publish data and code [4]. The stronger claim to test is that boundary aware, executable technology records allow independent reviewers to identify and correct decision relevant errors. An initial release can be small if it includes a matched incumbent, a transition alternative, reconciled energy and material flows, and an end to end reproducible comparison.

\pagebreak

### 13 Is this a meaningful pilot

The pilot is worth pursuing as a study of decision validity and the value of better process and procurement information. Its existing evidence establishes that feasibility rules, accounting boundaries and the chosen risk criterion can change conclusions. A credible next claim is that PLANiT integration and a traceable database improve a specified decision comparison. A claim to have measured the true 2050 tail risk of four corporations is not supported.

{{table:next}}

Table 6. Proposed next experiment and acceptance evidence. Thresholds and risk appetite should be agreed before viewing new results; no numerical acceptance threshold is presented as an established standard.

A staged experiment should keep the production service and candidate menu fixed while replacing inputs: first the matched physical ledger, then coherent PLANiT energy conditions, then procurement and settlement evidence. An additional combined run is necessary because these changes interact. Each stage reports eligibility, mean, quantiles, TCaR and ES, selection changes, and conditional regret when a plan chosen under one assumption is evaluated under another. Assumption cases without justified probabilities remain separate rather than being averaged into a single expected regret.

Decision relevance does not require a different preferred plan. If the preference remains stable across plausible inputs and independent calculations, the pilot can show where a simpler method is adequate. If rankings remain unidentified or feasible alternatives disappear under unresolved assumptions, that finding should guide further data collection. It should not be concealed by an attractive frontier plot.

### Conclusion

A useful transition assessment links physical service, emissions qualification and procurement cash flows before interpreting a cost distribution. The current pilot demonstrates why this sequence matters and provides an executable basis for review. Coupling to PLANiT’s energy modelling system and publishing a traceable abatement technology database are the next means of testing whether these methodological improvements survive more realistic inputs. The intended output is a defensible comparison with explicit limits, capable of supporting a subsequent corporate validation study.

\pagebreak

### 14 Academic contribution and the next decisive test

This is a reviewable applied methods pilot. It does not yet establish a new risk measure, a general superiority result or empirically calibrated corporate risk. A substantive paper can emerge if the integration produces a reproducible economic finding about which investments qualify, how risk is transferred, or when additional information changes a decision.

The closest literature makes this distinction necessary. Richstein and Neuhoff [12] analyse industrial carbon contracts and financing with a CVaR based investment criterion. Gaebelein-Khanra and colleagues [13] evaluate German steel alternatives using worst-case mean and Expected Shortfall under probability ambiguity. Ahmed and colleagues [14], in a June 2026 preprint, endogenise energy procurement contracts in multistage industrial investment planning. Their abstract establishes direct overlap; it is not evidence that all implementation details have been compared. Applying risk metrics to industry or adding contracts therefore cannot be claimed as the contribution on its own.

**The question to identify.** Under the same production requirement and candidate menu, when do coherent energy system conditions and verified procurement exposures change an admissible investment decision relative to a central price assessment? TCaR communicates the change in adverse cost spread; mean, upper quantiles and ES identify its level and tail consequences.

**A comparison that could answer it.** Predefine one matched plant case and a common evaluation model. Compare a central price baseline, a stochastic case with simple benchmark exposure, a case coupled to PLANiT, and a case adding verified procurement and technology records. Keep candidate choices, output and accounting boundaries comparable, and report interactions through a combined run. Evaluate selected plans on independent paths under each defensible specification. Regret is the objective gap to that specification’s best evaluated eligible plan; infeasibility is reported separately. This is model-conditional evaluation, not evidence of realised investment performance.

**What would constitute added knowledge.** Report which mechanism changes eligibility or ranking, the premium associated with risk transfer, and where the added complexity makes no decision difference. Show whether those findings survive menu expansion, plausible process specifications and independent replication. The value of additional data should be framed as conditional decision improvement; a formal expected value of information requires a justified probability model and information costs.

PLANiT coupling and the public database are enabling research assets. Their academic contribution is demonstrated by the comparison and an executable public case, not by a promise of future integration. The current material warrants collaborator review and a focused validation study; readiness for a full journal submission depends on this evidence and a fuller comparison with the closest literature.

\pagebreak

### References

[1] Markowitz, H. (1952). Portfolio Selection. Journal of Finance, 7, 77–91. [Article](https://doi.org/10.1111/j.1540-6261.1952.tb01525.x).

[2] Rockafellar, R. T. and Uryasev, S. (2002). Conditional value-at-risk for general loss distributions. Journal of Banking & Finance, 26, 1443–1471. [Author manuscript](https://sites.math.washington.edu/~rtr/papers/rtr187-CVaR2.pdf).

[3] Rockafellar, R. T., Uryasev, S. and Zabarankin, M. (2006). Generalized deviations in risk analysis. Finance and Stochastics, 10, 51–74. [Author manuscript](https://sites.math.washington.edu/~rtr/papers/rtr192-GeneralizedDeviations.pdf).

[4] Bachorz, C., Verpoort, P. C., Luderer, G. and Ueckerdt, F. (2025). Exploring techno-economic landscapes of abatement options for hard-to-electrify sectors. Nature Communications, 16, 3984. [Article](https://doi.org/10.1038/s41467-025-59277-1).

[5] Vogl, V., Åhman, M. and Nilsson, L. J. (2018). Assessment of hydrogen direct reduction for fossil-free steelmaking. Journal of Cleaner Production, 203, 736–745. [Article](https://doi.org/10.1016/j.jclepro.2018.08.279).

[6] Tiggeloven, J. L., Faaij, A. P. C., Kramer, G. J. and Gazzani, M. (2023). Optimization of Electric Ethylene Production: Exploring the Role of Cracker Flexibility, Batteries, and Renewable Energy Integration. Industrial & Engineering Chemistry Research, 62, 16360–16382. [Publication](https://doi.org/10.1021/acs.iecr.3c02226).

[7] NGFS. Long term scenarios frequently asked questions. [Scenario interpretation](https://www.ngfs.net/ngfs-scenarios-portal/faq/).

[8] IEA (2025). Global Energy and Climate Model Documentation, Table 2.3. [Documentation](https://iea.blob.core.windows.net/assets/9155992e-962c-45f4-97c1-78fd43a94178/GlobalEnergyandClimateModelDocumentation2025.pdf).

[9] World Bank. Commodity Markets and historical monthly prices. Frozen experiment window: January 2010–December 2025. [Data source](https://www.worldbank.org/en/research/commodity-markets).

[10] Linklater, J. (2021). Adapting to Raw Materials Challenges, Part 1. Midrex. [Technical article](https://www.midrex.com/direct-from-midrex/technical-articles/adapting-to-raw-materials-challenges-part-1-operating-midrex-plants-with-lower-grade-pellets-lump-ores/).

[11] JGCRI. GCAM model overview. [Official documentation](https://jgcri.github.io/gcam-doc/overview.html).

\pagebreak

### References continued

[12] Richstein, J. C. and Neuhoff, K. (2022). Carbon contracts-for-difference: How to de-risk innovative investments for a low-carbon industry? iScience, 25, 104700. [Article](https://doi.org/10.1016/j.isci.2022.104700).

[13] Gaebelein-Khanra, M., Klobasa, M. and Patil, P. (2026). A framework for decision making under deep uncertainty in hard-to-abate industries: An application case for investment in a German steel plant. Energy Strategy Reviews, 64, 102185. [Article](https://doi.org/10.1016/j.esr.2026.102185).

[14] Ahmed, M., Zavala, V. M. and Cordiner, J. (2026). Endogenous Energy Contracts for Accelerating Industrial Decarbonisation Investment Planning under Uncertainty: an SDDP Approach. SSRN preprint, posted 5 June 2026. Abstract reviewed. [Preprint](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6882934).

\pagebreak

### Appendix A Evidence and replication map

[D1] PLANiT CAP research archive. TCaR methodology v2.32, 9 September 2026; sections 4.6, 5.2, 6.4–6.8 and 6.13. Frozen company comparisons, accounting assumptions and robustness results. Original inputs and source locations are retained in the project archive; this paper does not report a newly calibrated corporate run.

[D2] IEA scenario register: data/research_v2/iea_2025_scenarios/curves.json. Source price nodes, units and scenario identities used in Figure 2. Price history and transformations: data/research_v2/price_history/ and block_price_paths/.

[D3] Timing experiment: data/research_v2/ncc_timing_frontier/. qualification.csv supplies eligibility; risk_metrics.csv supplies Table 3; bootstrap_precision.csv supplies the conditional TCaR intervals. The manifest records assumptions and seeds 20260917 and 20260918. Seeds are arbitrary identifiers, not dates of observation or execution.

[D4] Steel procurement experiment: data/research_v2/steel_procurement_tail/. conditional_risk.csv supplies Figure 5; annual_ledger.csv and source_register.json document quantities and price mappings. Seeds 20260923 and 20260924 each generate 5,000 paths. theoretical_mean is distinguished from finite sample mean.

[D5] Settlement extension: src/cap/fx_settlement.py and invoice_fin.py; data/research_v2/invoice_fin_bridge/. These modules demonstrate invoice and payment date accounting. Their presence does not mean the frozen company exercise has been recalibrated with corporate foreign exchange exposures.

### Minimum replication sequence

Read the experiment manifest and source boundaries; reconstruct the physical and cash ledger; test production and emissions eligibility; restore the specified price generator and shared paths; calculate means, quantiles and empirical ES using the stated conventions; compare eligible candidates; repeat selection in an independent pool. Preserve the candidate menu, seeds, units and exclusions in every output.

Figures 1–5 in this paper are regenerated from registered nodes, declared assumptions and saved experiment tables. Figure 6 is a proposed integration architecture. No figure represents a new corporate simulation. Numeric tables are rounded for readability; the associated CSV files retain the stored precision.

### Questions for the reviewing team

Does the matched production and counterfactual definition support the intended economic question? Which physically linked parameters need to change together? Does the proposed PLANiT exchange preserve price, quantity and emissions consistency? Which input uncertainty could reverse a decision, and which needs actual procurement data? What is the smallest independently reproducible public case that would justify a corporate validation study?
