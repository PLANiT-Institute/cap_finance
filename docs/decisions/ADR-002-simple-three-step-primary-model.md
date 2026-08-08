# ADR-002 — Make the three-step G-CAP model the primary investor view

- **Date:** 2026-08-05
- **Status:** accepted
- **Supersedes for presentation:** ADR-001 and complex-model v1 outputs
- **Does not delete:** any prior model, table, figure, report or decision record

## Context

The complex v1 chain preserved useful facility, cost, pathway and support detail, but it did not make the investment flow or the investor conclusion easy to understand. In particular, physical capital need, recurring cost exposure and residual emissions risk appeared in separate views. A numerical security risk premium also cannot be estimated from the available data without inventing factor prices or financing spreads.

## Decision

The primary presentation will contain three linked steps and three figures:

1. **G-CAP allocation and capital gap.** Define G-CAP as a GCAM-aligned sector capital-envelope proxy. Calculate the sector envelope from its allocated 2050 emissions reduction and a documented low/base/high representative capital intensity. Allocate it to companies by each company's share of the sector sample's required reduction. Compare company G-CAP with route-identified capital.
2. **Level gap and transition-premium proxy.** Scale the base and high annual resource-gap sensitivities to the full allocated emissions path. The level-gap rate is base annual gap divided by G-CAP. The transition-premium proxy is high-minus-base annual gap divided by G-CAP. It is an annual hurdle-rate equivalent, not WACC, a security spread, a probability-weighted expectation or a premium in basis points.
3. **Support-to-emissions closure.** Compare level-only (BL), premium-mitigation-only (BH) and combined (BHL) screening outcomes as shares of the allocated 2050 reduction. Use representative technologies to explain the mechanism: scrap-EAF/H2-DRI for steel and NCC electrification/consolidation for petrochemicals.

The direct GCAM Korea/Japan capital extract remains a data upgrade. Until then every G-CAP value is `estimated`, low/base/high, 2025 USD, quality D and formula-traceable. `transition_risk_premium_bps` remains `NA`.

## Consequences

- The investor can see one capital requirement, one missing-capital amount, one uncertainty surcharge and one emissions-closure result per company.
- Paying the level gap is not represented as sufficient to eliminate emissions. The combined mechanism cannot close more than the route-identified physical path.
- The premium proxy can be large or exceed 100% per year because the numerator is a high-case annual resource-cost stress and the denominator is a one-time capital envelope. Such a result is a cost-risk warning, not an expected return.
- Complex v1 assets are preserved at `archive/2026-08-05-complex-v1/` for audit and potential reuse, but they are no longer the preferred public narrative.
