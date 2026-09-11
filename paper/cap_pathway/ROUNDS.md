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

## R2 · 03:12 KST · model section

Critique of R1.
- The literature paragraph on real options said policy uncertainty "delays" investment as if settled; Fuss et al. (2008) find delay under price uncertainty but earlier investment can arise under expected tightening. Softened to "can delay … depending on the drift and volatility of the policy price".  [applied in §1.1 wording check — see below]
- §1.2 claimed "nothing in the reported tail comes from a prior" — true for volatilities/correlations, but the hydrogen structural constant (52 kWh/kg) and electrolyser amortisation *are* assumptions. Sentence kept, qualified in §2.1 by stating the structural formula explicitly.
- §2.1 (R0) listed objects but never wrote the cost function; the definition of "added electricity" for the hedge was implicit; ④ and ⑤ had no formulas. All now written.
- R1 left the reference-point issue (μ on L, ES on C) as a note. R2 resolves it in §2.2 with the monotonicity/shift-invariance argument, citing manuscript v2.32 Propositions 1, 6, 7 and v2.x Proposition 8 rather than restating them as new propositions (no numbering collision; this paper states no new propositions).

What R2 added.
- §2.1 setting with the factorisation A = Z × H (contracts do not change feasibility) — the structural reason equipment and contracts sit on one frontier.
- §2.2 statistics and reference points; §2.3 frontier, λ-selection, price of tail removal π; §2.4 the two levers and the explicit empirical condition under which earlier adoption lowers ES (variance of the new bill < variance of the old bill on the advanced years) — this is the hypothesis §5.3 must test; §2.5 formal indicator table incl. regret form of ④ and menu-bound form of ⑤; §2.6 discounting.

Open for R3.
1. Build the timing-ladder variants and test the §2.4 condition directly (compare per-year bill variance pre/post conversion).
2. §2.4's contract statement "concave in h" is asserted; R3 should verify on the contract grid (ES vs h at 0, 0.25, 0.5, 0.75, 1).
3. Fill §4 data with sources and the allocation rule for A.

## R3 · 04:12 KST · data and results (timing ladder)

Critique of R2.
- WRONG: §2.4 asserted that the tail reduction is concave in the hedged share h. The contract grid shows it is *linear* (LOTTE B20: 50,644 → 43,396 → 36,184 → 29,049 → 22,147 — equal steps). Reason: the hedge replaces a fraction of one common shock by a constant, and ES of a linear combination with a fixed mixing weight is linear in that weight when the ranking of paths is unchanged. Consequence: π is constant in h and the efficient contract is bang-bang. §2.4 rewritten; §5.5 added with the evidence.
- R2's §2.4 timing condition was stated but the paper had no way to test it. R3 built the ladder (32 variants, run `runs/v2_3_ladder`, E5 only, canonical E1–E3 untouched).
- R2 §2.5 gave ⑤ as "perfect information over a finite menu" — correct, but the paper must also say the menu is 1 schedule for POSCO, hence Φ = 0 there (carried; now in §5.2 reading).
- Missing in R0–R2: the Data section had no sources. Written.

What R3 found (this is the round's substantive result).
- Earlier adoption (−3, −6 y) raises μ AND raises ES₉₀ AND raises the dispersion part ES − μ in all 8 cells, spot and contracted. Later adoption (+3, +6) lowers all three but violates the cumulative budget in all 8 cells. The canonical schedule is the earliest feasible budget-binding point; no earlier variant is non-dominated.
- Therefore, within this model, uncertainty does NOT pull equipment forward; the efficient response to uncertainty is the contract on added electricity, not earlier capex. This contradicts the working hypothesis "빠른 전환 = 에너지비용 대비" in its naive form and supports the refined form "전환 + 고정가 조달". The paper says so plainly.
- Decomposition: petrochemical tails are ~85–97 % electricity; steel NZ15 tails are 48–58 % carbon (residual BF emissions at NZE prices net of shrinking allocation) — a policy exposure a power contract cannot touch.

Open for R4–R6.
1. Horizon truncation confounds the ladder (earlier = more exposure-years in-window). R6 should add a terminal-value or per-year-normalised comparison (e.g. ES of the annual bill in a common post-conversion year).
2. Table 1 construction column for B20 rows [R6].
3. The ladder shifted *all* adoption years together; a per-facility ladder (only the H₂-DRI unit moved) would be the sharper test. Note as limitation unless time permits in R6.
4. Contract linearity means the λ-selection is a threshold rule; R4 must present π vs plausible λ ranges and market hedge costs, not "the frontier chooses PPA 1.0".

## R4 · 05:12 KST · investor meaning and the case for transition

Critique of R3.
- R3 wrote "the contract removes most of what earlier adoption adds" from the ppa=1 rows; correct in direction but the text implied a general law. Kept, with "roughly one third the size" as the measured statement.
- R3's ladder shifted all adoption years; that includes the efficiency retrofits, which are cheap and early anyway. The steel result is therefore driven by moving the H₂-DRI unit. Fine for the claim, but the limitation is now stated in §7 [R6 to write].
- R3 Table 3 reported budget "violated" for +3/+6 but did not say by how much; the data file has cum_emis vs budget — R6 should add the overshoot %.
- The wedge table in R0–R3 used one number per direction. The `budget_gap_tco2` column is the *annual* overshoot sum, so it is positive even for the own-scenario plan (cumulative met, annual not). R4 discovered this and now reports own-plan overshoot alongside; the paper text says what the column is.
- New finding surfaced while writing 6.2: the B20 allocation evaluated under NZ15 is *cheaper* than under B20 because the NZE anchor lowers fossil prices. So ④ mixes carbon stringency with fossil-price collapse. Stated as a caveat; R6 must run the NZ15-with-B20-carbon-price split.

What R4 added.
- §6.1 investor reading of ①–⑤ with the POSCO affordability ratios (only firm with a verified reference), cost per tonne, the tail composition → instrument mapping, π's dependence on the premium, and the two-sided policy exposure table (Table 5).
- §6.2 the conditional case for transition, with Table 6 (preparedness): contracted allocation ES₉₀ = 0.79–0.87 × no-transition counterfactual under NZ15 for all four firms; > 1 under B20. "Prepared" defined operationally.
- §6.3 disclosed-plan benchmark: honestly reported as not computed (gap.csv empty; linear-path generator not run for v2.3), with the interpretation that would apply.
- §6.4 implications for firms, investors, policy (SMP–LNG decoupling; allocation certainty).

Open for R5–R7.
1. Run NZ15 with B20 carbon path (or carbon = 0) to separate fuel-price from carbon-price effects in Table 6 — R6 (sensitivity run exists in tmp/research_case_v2_2_sensitivity? check; else E5-only rerun with carbon price scaled).
2. π at premium 15 %/25 % — R6.
3. Verify PPA-market statements (Korean direct PPA network charges/levies; Japanese corporate PPA market) with sources — R5.
4. Consider running the linear disclosed-path benchmark (`src/cap/disclosed_path.py`) for one firm if time allows — R6; else keep §6.3 as is.

## R5 · 06:12 KST · adversarial review (three referee reports) and response

Three reports were obtained from independent reviewer agents: R1 Energy Policy empiricist, R2 finance theorist (risk measures / real options), R3 industry practitioner (steel, petchem, K-ETS/GX-ETS, PPAs). Full texts are in this session's log; the substantive points and their disposition:

| # | Finding (referee) | Disposition | Where |
|---|---|---|---|
| 1 | **Proposition 1 misapplied**: TCaR(L) ≠ TCaR(C) because x₀ is random; §2.2 contradicted itself (R2) | FIXED. §2.2 rewritten: all risk statistics on C(x), level ② on L, bases declared; TCaR(L)=166,558 vs TCaR(C)=234,216 shown | §2.2 |
| 2 | **Table 4 basis undeclared**; "steel carbon tail" reading inverted — decomposition was on L, not C (R2) | FIXED, and it changed the narrative. Absolute-basis decomposition computed (`abs_basis_stats_v2_3.csv`): tails are 85–100 % electricity everywhere, coal 11–48 % in steel, carbon ≈ 0. Incremental-basis carbon share (48–58 % steel NZ15) is *carbon-price-collapse risk on the abatement's value*. §5.4, §6.1, §6.4 rewritten | §5.4, §6 |
| 3 | Δμ % on incremental base vs ΔES % on absolute base — not like-for-like (R2) | FIXED. Table 2 adds Δμ as % of E[C] (0.4–2.0 %); Table 6 adds dispersion-form ratios D(x)/D(x₀) (0.42–0.69 NZ15 contracted; petchem B20 contracted < 1 in dispersion though > 1 in level) | §5.2, §6.2 |
| 4 | ES is convex, not linear, in h; interior grid points are non-dominated (R2) | FIXED. Steps 7,248/7,212/7,135/6,902; π 0.0060→0.0063; threshold rule stated as approximation | §2.4, §5.5 |
| 5 | EPC at +10 % on deterministic capex is statewise dominated (R2, R3) | CONFIRMED numerically (d_mean = d_ES in all 8 cells); EPC declared inert, 135 variants removed from discussion | §2.4, §5.2 |
| 6 | λ-selection degenerate / dimensionally loose; π has no decision-theoretic content without λ grounding; π ∝ π_E (R1, R2) | PARTLY. Threshold rule stated; break-even premium to be reported (R6). λ grounding via costly external finance (Froot–Scharfstein–Stein) to be added to §2.3 in R6 | §2.4, §7 |
| 7 | Regret definition inconsistent with negative values (R2); ④ confounds carbon stringency with NZE fossil-price collapse (R1, R3) | PARTLY. Definition fixed (relative to x*_{s′}, paired with G). Carbon/fuel split run scheduled for R6; until then §6.1 keeps the caveat | §2.5, §6.1 |
| 8 | ⑤ is EVPI: an *upper* bound on information value, lower bound only w.r.t. menu (R2) | FIXED wording | §2.5 |
| 9 | Allocation rule A = budget path is not K-ETS/GX-ETS; manufactures x₀'s NZ15 tail; compliant firm becomes net seller (R1, R3) | ACKNOWLEDGED, not fixable this round. §6.2 caveat added; gross basis + benchmark-style A to be co-equal cases in §7 (R6: gross-basis run exists in v2.0 outputs; benchmark A requires new E1 rule — flagged as future) | §6.2, §7 |
| 10 | σ_E from SMP/JEPX overstates what tariff/retail customers pay; K-ETS covers indirect (electricity) emissions so grid-electrolysis H₂ adds obligation and breaks A = Z × H (R3) | ACKNOWLEDGED as the most serious practitioner objection. Cannot be re-run tonight. Goes to §7 limitations with explicit statement that the electricity tail is an upper bound for tariff customers and that indirect emissions are outside the Scope-1 budget used [확인 필요: K-ETS phase-4 indirect-emission coverage] | §7 |
| 11 | 24-year fixed-price PPA on 100 % of added load does not exist; premium unknown; no coal/LNG hedges in menu; FOAK EPC not obtainable (R3) | ACKNOWLEDGED. Hedge-menu gap stated in §6.1; break-even premium (R6); tenor/volume realism to §7 | §6.1, §7 |
| 12 | Technology routes vs firms' disclosed routes (NSC CCUS, POSCO HyREX timing); relining windows not shown; hydrogen supply (imports, DR pellets); production fixed despite 2025-12 restructuring (R3) | ACKNOWLEDGED → §7 limitations; the paper's claim is conditional on the menu, and §1.2 already says so. Data-confidentiality prevents showing campaign dates | §7 |
| 13 | Calibration on 10–15 annual obs, KAU regime shifts, no CIs (R1) | ACKNOWLEDGED → §7; correlation bounds sensitivity if time (R6) | §7 |
| 14 | Horizon truncation drives the ladder; variance condition not actually reported (R1, R2) | PARTLY. §5.3 already qualified; R6 to add per-year bill variance pre/post and an annualised comparison | §5.3, §7 |
| 15 | Five indicators are repackaged (capex path, deterministic NPV, MC P90–P50, minimax regret, EVPI) (R1) | ACCEPTED in spirit: §2.5 now cites Loulou & Kanudia for ④ and calls ⑤ EVPI; §1.2 to be re-pointed in R7 so the claimed contribution is the joint frontier and the exposure-relocation result, not the indicator set | §2.5, §1.2 (R7) |
| 16 | Results read as a firm ranking; named firms with 3-sig-fig numbers (R1) | DISAGREE in part: the firms are the cases and their disclosures are public; but R7 will add a sentence per table forbidding cross-firm reading and consider a sector-level summary table | §5 (R7) |
| 17 | GBM mean-normalisation manufactures the tail; OU should be co-equal; POSCO NZ15 ΔES sign flips under OU (R2) | ACKNOWLEDGED; OU run exists (v2.2 sensitivity) — R6 to tabulate; making OU the base case is beyond tonight | §7 |
| 18 | Discount rate 2.4 % not a corporate hurdle; reconcile ES levels with actual energy spend (R3) | R6: 3.5 %/5 % rows exist; add a "share of C(x) that is energy" line | §7 |

Citations re-verified this round: Loulou & Kanudia (1999, ORL 25) ✔; Froot–Scharfstein–Stein (1993, JF) ✔; Vogl–Åhman–Nilsson (2018, JCP 203) ✔; Bataille 2018 replaced by Bataille (2020, WIREs Climate Change) ✔; Blyth et al. 2007 title/authors ✔ (volume unverified); Rockafellar–Uryasev–Zabarankin 2006 added [확인 필요]; Kampmann/Ostrovnaya 2026 still unverified and not cited in this paper.

Net effect of R5 on the paper's claims. The headline "steel tail is carbon" is withdrawn and replaced by two correct statements (absolute tail = electricity + coal; incremental dispersion = carbon-price-collapse risk). The contract result survives with the caveat that π is proportional to an assumed premium. The timing-ladder result survives as a within-window statement. The preparedness table now shows level and dispersion; the NZ15 conclusion strengthens (dispersion ratios 0.42–0.69), the B20 conclusion becomes two-sided.
