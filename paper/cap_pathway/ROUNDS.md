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
