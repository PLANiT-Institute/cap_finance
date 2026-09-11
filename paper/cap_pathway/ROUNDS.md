# CAP paper loop — round log (2026-09-12 KST)

Rule: each round opens with a critique of the previous round (wrong / overstated / missing), then the fix, then what the round added. Numbers only from `runs/v2_3` unless a new computation is documented here.

## R0 · 01:10 KST · skeleton and allocation numbers

Purpose restated (user, 2026-09-11 evening): the deliverable is a per-firm capital allocation pathway (how much, when, in what form) with its five-indicator price tag; TCaR and the frontier are instruments. Not a firm ranking; not a paper about a risk measure.

What R0 did.
- Built `data/allocation_table_v2_3.csv` from the canonical run: ① capex total/peak/year, ② μ, ③ ES₉₀ and the λ = 1 point, ④ same-plan-other-scenario cost and budget gap, ⑤ flex value.
- Figure 1: annual construction outlays of the mean-minimising allocation, both scenarios, four firms.
- Wrote the skeleton with sections assigned to R1–R7.

Findings worth carrying (to be challenged in R1+).
- Stringency changes *timing*, not the steel technology set: POSCO peak 2043 → 2032, NSC 2037 → 2034, +11–12 % capital.
- Risk-efficient allocation = same equipment + fixed-price contract on added electricity; price of tail removal 0.6–0.9 jeon per won of ES₉₀.
- Petrochemical tail is ~60 % removable by contract; steel only 13–20 % (coal, hydrogen, residual carbon remain).
- Policy exposure: B20 steel allocations miss the NZ15 budget by 194–242 MtCO₂ cumulative — not purchasable.

Open problems R0 leaves (must be resolved, not hidden).
1. RESOLVED in R0: capex_total = construction + maintenance/renewal (`gross_capex_k`); POSCO NZ15 = 18,626 + 9,216. Paper text updated.
2. No timing ladder in the menu → §5.3 empty. R3 must construct ±3/±6-year variants and revalue.
3. RESOLVED (partly) in R0: PPA premium 8 %, EPC 10 % are research assumptions in `config.yaml`; the paper now says so. R6 must vary the premium (e.g. 8/15/25 %) and report where the contract stops being efficient.
4. ④ policy exposure is asymmetric (NZ15 plan under B20 is cheap; B20 plan under NZ15 infeasible). The paper must present both directions and the budget gap, never one number.
5. Flex ⑤ = 0 for POSCO because the menu has one distinct schedule (P0024–26 are permutations). State it; do not present 0 as "no option value".
6. Literature and theory sections are placeholders.

## R1 · 02:12 KST · literature and positioning

Critique of R0 (what was wrong, overstated, missing).
- Overstated: "the risk-efficient allocation adds contracts rather than earlier equipment" was presented as a finding. It is a property of the menu: no timing variants exist, so the frontier *cannot* move equipment earlier. Until R3 builds the timing ladder this sentence is a statement about the menu, not about firms. Highlights amended.
- Overstated: "Under the stringent scenario the steel capex peak moves forward by 8–11 years." Correct for POSCO (2043→2032, 11 y) but NSC is 2037→2034 (3 y). Corrected to "3–11 years".
- Wrong framing: ② was defined as incremental to the no-transition counterfactual while ES₉₀ is on the plan's own absolute cost. The paper must say explicitly that the two axes have different reference points and why (shift-invariance of TCaR vs. level meaning of ES). Added to §2.1.
- Missing: the introduction had no literature; no statement of what is exogenous (sector pathway from KAIST GCAM) vs. what the paper decides (downscaling rule, menu, valuation). Added.
- Missing: the paper never said who the reader is. Added a paragraph: the firm's investment committee and the lender/investor underwriting it; not a regulator, not a ranking.
- Missing: the manuscript v2.32 cites Kampmann et al. (2026) and Ostrovnaya et al. (2026) for transition-plan/finance links; I could not verify them by search this round → marked [확인 필요] and not relied on.

What R1 added.
- §1 rewritten; §1.1 positions the paper in five strands, each with citations verified by web search this round (Vogl, Olsson & Nykvist 2021 is in *Joule*, not One Earth as first assumed; corrected). §1.2 states three contributions and what is *not* claimed. References section started with verified entries only.
- Bataille et al. (2018) and Blyth et al. (2007) are cited from memory of the field with [확인 필요] until R5 re-checks.

Open problems carried to R2+.
1. The theory must justify using ES on absolute cost but μ on incremental cost (§2.1 note) — R2.
2. Timing ladder — R3.
3. Kampmann/Ostrovnaya/Bataille/Blyth verification — R5.
