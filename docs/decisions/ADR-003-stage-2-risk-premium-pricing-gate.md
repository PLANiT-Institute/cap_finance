# ADR-003 — Preserve priced transition risk premium for the next project

- **Date:** 2026-08-05
- **Status:** accepted
- **Decision owner:** CAP-KJ
- **Affected scope:** Stage 1 interpretation and Stage 2 evidence roadmap
- **Charter effect:** none; Stage 1 exclusions remain in force

## Context

The simplified capital-allocation pathway needs an investor interpretation of electricity, hydrogen and other transition uncertainty without converting deterministic cost ranges into an invented security premium. Stage 1 can estimate the quantity of factor exposure and show how contracts or policy conditions change facility investability and modelled operational abatement. It cannot yet estimate the market price of that exposure.

The 2050 pathway milestone is not an analytical terminal date. Industrial assets, investment windows and transition liabilities may continue beyond 2050. Any later pricing model will use the relevant facility life and declared investment, relining, turnaround and retirement windows, including post-2050 years where required.

## Decision

1. Stage 1 keeps the following investor identity:

   `additional transition risk premium = sum(factor exposure beta_k × market price of risk lambda_k)`

2. `factor exposure beta_k` means the sensitivity or covariance of facility/project incremental cash flow or value to factor `k`, including electricity, hydrogen, carbon, feedstock and enabling-infrastructure risks. A high price range or volatility alone is not a beta.
3. `market price of risk lambda_k` means the compensation required for bearing one unit of systematic, non-diversifiable factor risk. It must be estimated from auditable market or financing evidence rather than chosen to force a target premium.
4. Stage 1 reports only:
   - low/base/high resource-cost exposure;
   - transition capital subject to each factor;
   - contract-, support- and physical-constraint status;
   - residual premium-relevant exposure after de-risking;
   - modelled operational abatement unlocked under stated decision rules.
5. Stage 1 keeps `transition_risk_premium_bps=NA`. The current deterministic high-minus-base buffer may be called an `uncertainty buffer` or `premium-relevant cost exposure`, but not a priced premium, WACC increment, expected return or security spread.
6. Contracts and policy instruments are represented by the channel they change:
   - PPA, hydrogen offtake, indexation and hedging reduce or transfer factor exposure beta;
   - grants, tax credits, carbon contracts for difference and price floors may reduce the central level gap and/or downside exposure;
   - an intervention does not automatically change the market price of risk lambda.
7. A numerical real-options FID delay, priced premium, expected NPV, impairment loss or stranded-asset loss is a later-project result and does not enter the Stage 1 headline figures.

## Next-project evidence gate

The next project may estimate a priced premium and FID timing only after collecting and reconciling:

1. historical and forward electricity, hydrogen, carbon and feedstock price distributions, including covariance and regime treatment;
2. facility- or route-level incremental cash-flow sensitivities, CAPEX schedules, operating margins, asset lives and decision windows;
3. actual PPA, hydrogen offtake, indexation, guarantee, subsidy and carbon-contract terms, including which party retains each risk;
4. observed project hurdle rates, financing spreads, comparable issuer/project returns and realised FID, delay or cancellation evidence;
5. for any stranded-asset extension, carrying amount, recoverable amount, reuse/salvage value, closure cost and decommissioning timing.

Each dataset must preserve source, date, currency, price year, unit, boundary, value type and quality grade. Probability distributions must be estimated from evidence or presented as named stress scenarios; they may not be assigned arbitrarily.

## Required next-project outputs

Subject to the evidence gate, the next project may report:

- factor betas for electricity, hydrogen, carbon and feedstock;
- market prices of systematic transition risk;
- an additional transition risk premium range in basis points;
- FID timing and Delay-at-Risk across the full relevant asset horizon, including post-2050;
- contract- and policy-conditioned changes in beta, investability and premium;
- expected project NPV and stranded/closure loss only where accounting and cash-flow evidence support them.

## Interpretation rule

The Stage 1 causal chain remains:

`emissions pathway → required physical capital → identified route and capital gap → factor exposure and support condition → screening-investable capital → modelled operational abatement and residual gap`

The later priced-premium module is an extension of this chain, not a substitute for the physical pathway.
