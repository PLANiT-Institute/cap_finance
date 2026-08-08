# ADR-001: Capital-flow and risk-premium boundary

**Status:** Accepted  
**Date:** 2026-08-05  
**Decision owner:** CAP-KJ  
**Affected project version:** 1.0 output interpretation; no charter version change

## Context

The first pathway figures connected emissions reductions to estimated CAPEX, but they did not show the investor decision chain: how much capital is required, how much is screen-investable under current conditions, which portion is blocked by a central cost gap versus uncertainty, which policy or contract instrument changes that status, and how much emissions reduction becomes investable. Calling required CAPEX a capital flow overstated what the data established.

The user also requested a risk-premium concept that is meaningful to investors. A priced security or project risk premium requires both a measured exposure and an observable or estimated market price of that risk. Stage 1 currently has screening exposure and deterministic support experiments, but not defensible factor prices, project cash flows, hurdle rates, or comparable financing spreads.

## Current rule

`PROJECT_CHARTER.md` Q4 requires the investable, contract-dependent, support-dependent and physically constrained shares of transition capital. Section 6 excludes a numerical security risk premium in basis points. Section 14.3 permits premium-relevant cost exposure but states that the market price belongs to a later stage.

## Decision

1. Public-facing capital outputs will distinguish:
   - total physical pathway capital need;
   - capital attached to an identified facility route;
   - capital with no identified facility route;
   - screening-investable identified capital under B0, BH, BL and BHL;
   - risk-covered capital and level-support-equivalent amounts;
   - modelled operational abatement unlocked by each mechanism.
2. `Capital flow` means the screening amount that changes to investable status under a declared mechanism. It is not observed financing, committed company expenditure or transaction volume.
3. `Risk premium` will be presented as a two-part identity:

   `transition risk premium = cost exposure beta × market price of transition risk`.

   Stage 1 reports the premium-relevant exposure and its reduction after de-risking. The market price and basis-point premium remain `NA`, not zero.
4. The current B0/BH/BL/BHL experiment may be used to demonstrate the mechanism only. Exact financing claims remain gated by project-specific cash flows, contract terms, market covariance and the known Mitsui boundary mismatch.

## Reason

The original investor question cannot be answered by a physical CAPEX schedule alone. Investors need to see the difference between capital required and capital likely to cross an investability threshold, why that difference exists, which actor bears each risk, and what emissions result follows. At the same time, inventing a risk premium from deterministic low/base/high ranges would violate the scenario-probability and false-precision rules.

## Alternatives considered

- **Label the existing high/base cost difference a risk premium:** rejected because it is a stress loss, not compensation for priced systematic risk.
- **Use an arbitrary probability distribution to produce basis points:** rejected because the charter prohibits arbitrary scenario probabilities and the necessary market/cash-flow data are absent.
- **Remove the term risk premium entirely:** rejected because premium relevance is central to investor interpretation; separating exposure from its market price is both accurate and decision-useful.

## Consequences

- Korea–Japan and steel–petrochemical comparisons retain the same company and facility boundaries.
- Prior CAPEX and emissions-pathway outputs remain valid as physical screens but must not be called capital flows.
- The support experiment is reframed as an investability mechanism, not observed policy effectiveness.
- A numerical risk premium requires a later evidence gate: covariance-aware market data, facility cash-flow sensitivities, observable financing spreads or hurdle rates, and actual contract/policy allocation.
- New figures must show capital, policy condition and emissions effect together.

## Validation

The new output passes only if:

- B0/BH/BL/BHL investable capital reconciles to the declared mechanism shares;
- no mechanism unlocks more than identified route CAPEX or modelled pathway abatement;
- steel is unlocked by risk-only coverage and chemicals only by combined risk and level support under the current rule set;
- risk-premium basis points remain `NA` while residual exposure is numeric;
- every capital-flow amount is labelled screening/modelled rather than observed financing.
