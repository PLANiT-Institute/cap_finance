# Simple three-step investor model

## The whole model in three equations

1. **Company G-CAP** = sector GCAM-aligned capital envelope proxy × company share of sector 2050 required reduction.
2. **Transition premium proxy** = full-path annual high-minus-base resource-gap buffer ÷ company G-CAP.
3. **Emissions closure** = operational reduction unlocked under level-only, premium-mitigation-only or combined support ÷ allocated 2050 required reduction.

The four-company base G-CAP is **USD 69.5bn**: steel USD 66.9bn and petrochemicals/NCC USD 2.6bn. Route-identified projects leave a **USD 28.0bn** capital level gap.

| Company | Sector allocation key | Representative technology | G-CAP | Capital gap | Base cost-gap rate | Premium proxy | Combined emissions closure |
|---|---:|---|---:|---:|---:|---:|---:|
| POSCO | 46.9% | Scrap-EAF + H2-DRI / HyREX | USD 31.4bn | USD 18.2bn | 20.9%/yr | +33.8%/yr | 41.4% |
| Nippon Steel Corporation | 53.1% | H2-DRI / EAF + EAF efficiency | USD 35.5bn | USD 8.6bn | 22.1%/yr | +34.6%/yr | 76.8% |
| LOTTE Chemical Corporation | 58.1% | NCC electrification | USD 1.5bn | USD 0.8bn | 37.5%/yr | +70.8%/yr | 49.8% |
| Mitsui Chemicals, Inc. | 41.9% | NCC electrification + cracker consolidation | USD 1.1bn | USD 0.5bn | 37.5%/yr | +81.7%/yr | 52.4% |

## Concrete investor conclusions

- The missing investment has two different components. The one-time capital level gap is distinct from the recurring cost uncertainty that can raise the required hurdle after the asset is built.
- Under the current provisional mechanism rule, level support by itself unlocks none of the identified route. Premium mitigation through contracts, guarantees or other common-risk coverage unlocks the identified steel pathway, while the NCC pathways need both level and risk treatment.
- Even combined support closes only the identified physical pathway. It does not eliminate the residual emissions gap, so finance policy cannot substitute for missing technology capacity, clean power, hydrogen, feedstock and project timing.
- The premium proxy is deliberately comparable across companies as an annual percentage of G-CAP, but it is not a market-observed WACC increment or security risk premium. `transition_risk_premium_bps` remains `NA`.

## Evidence boundary

G-CAP currently uses transparent sector capital-intensity proxies around a GCAM-aligned emissions requirement. It is not yet a direct GCAM Korea/Japan capital output. Low/base/high values, source IDs, formulae, 2025 price basis and quality-D flags are retained in the generated company table. BL/BH/BHL results are deterministic screening rules and model operational reduction, not probability-weighted investment response, causal policy impact or system abatement.

## Primary outputs

- `outputs/figures/13_gcap_company_capital_gap.png`
- `outputs/figures/14_level_gap_and_premium_proxy.png`
- `outputs/figures/15_support_to_emissions_closure.png`
- `outputs/tables/company_simple_three_step_mvp.csv`
