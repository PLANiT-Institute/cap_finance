# GCAM-KAIST Data Request for CAP-KJ

**Project:** Company-Level Capital Allocation Pathways Built from Facility-Level Evidence in Korea and Japan  
**Requested use:** academic, reproducible, non-commercial analysis  
**Preferred data cut:** latest validated model version available as of August 2026

## 1. Purpose of the request

CAP-KJ will translate internally consistent sector transition pathways into facility-level calculations and aggregate them into company transition pathways, cost gaps, uncertainty exposures, support conditions, and modelled emissions reductions for:

- POSCO and Nippon Steel;
- LOTTE Chemical and Mitsui Chemicals.

GCAM is used as the system-level scenario backbone. It is not used to assign an exact technology to an individual facility. CAP-KJ needs sector production, emissions, energy, price, technology, and policy outputs for Korea and Japan from the same model and scenario design wherever possible.

The public GCAM-KAIST 1.0 Zenodo package appears to contain mainly model inputs rather than a complete solved output database and extraction queries. The project therefore requests solved and documented output.

## 2. Priority request

The preferred delivery is:

1. a solved database from the latest GCAM-KAIST/GCAM-ROK run;
2. Korea and Japan results from the same global run;
3. Current Policies and 2050 Net Zero-aligned scenarios;
4. explicit iron-and-steel and chemicals/petrochemicals output where the model permits;
5. electricity, hydrogen, fuel, feedstock, carbon-policy, and technology assumptions;
6. the queries and scripts used to extract the results.

If Japan or petrochemicals are not represented at the same detail as Korea or steel, please provide the closest native GCAM outputs and explain the aggregation. CAP-KJ will not present a derived value as a native model output.

## 3. Scenario set

### Required

1. **Current Policies / Reference**
2. **2050 Net Zero / Carbon-Neutrality pathway**

### Requested sensitivity runs, if already available

3. low-cost/high-availability clean hydrogen;
4. high-cost/limited clean hydrogen;
5. clean-power expansion constrained;
6. CCS transport or storage constrained;
7. scrap, DRI/HBI, or material circularity constrained;
8. alternative industrial-demand pathway;
9. alternative nuclear, renewable-power, hydrogen-import, or fuel-price assumptions;
10. delayed or accelerated industrial technology availability.

No scenario probability is requested unless the modelling team has explicitly assigned and justified it. CAP-KJ will otherwise treat scenarios as conditional cases.

## 4. Required metadata

### `scenario_metadata.csv`

| Field | Description |
|---|---|
| `scenario_id` | unique stable identifier |
| `scenario_name` | model or paper name |
| `model_name` | GCAM, GCAM-KAIST, GCAM-ROK, or other |
| `model_version` | release and commit identifier |
| `database_version` | solved database identifier |
| `configuration_file` | run configuration |
| `calibration_year` | last calibrated year |
| `time_step` | output frequency |
| `climate_target` | temperature, emissions, or net-zero target |
| `policy_definition` | tax, emissions constraint, technology policy, or combination |
| `demand_assumption` | industrial demand and production assumption |
| `hydrogen_assumption` | technology, cost, import and availability |
| `electricity_assumption` | generation, grid and delivery assumptions |
| `ccs_assumption` | capture, transport, storage and availability |
| `trade_assumption` | industrial products, fuels, hydrogen and feedstocks |
| `notes` | material caveats |

## 5. Regional and sector pathways

### `sector_pathways.csv`

| Field | Description |
|---|---|
| `scenario_id` | scenario |
| `region` | Korea or Japan, using native model name |
| `sector` | industry, iron and steel, chemicals, or native sector |
| `subsector` | process or product where available |
| `year` | model year |
| `production` | physical output |
| `production_unit` | native and, if available, converted unit |
| `gross_emissions` | pre-capture emissions |
| `captured_emissions` | captured CO₂ |
| `net_emissions` | post-capture emissions |
| `emissions_gas` | CO₂ or GHG species |
| `emissions_unit` | native unit |
| `final_energy` | energy demand |
| `energy_unit` | native unit |
| `electricity_use` | sector electricity |
| `hydrogen_use` | sector hydrogen |
| `notes` | boundary definition |

Please distinguish:

- CO₂ from CO₂e;
- energy from process emissions;
- gross from net emissions;
- direct industrial emissions from indirect power-sector emissions;
- production from service output if the native GCAM sector uses a service unit.

## 6. Technology pathways

### `technology_pathways.csv`

| Field | Description |
|---|---|
| `scenario_id` | scenario |
| `region` | Korea or Japan |
| `sector` | iron and steel, chemicals, or native name |
| `subsector` | technology nest or process |
| `technology` | native GCAM technology name |
| `technology_mapping` | engineering interpretation if different from native name |
| `year` | model year |
| `output` | technology output |
| `share` | technology output share |
| `capacity` | if represented |
| `capacity_addition` | if represented |
| `retirement` | if represented |
| `utilisation` | if represented |
| `emissions_intensity` | direct emissions per output |
| `electricity_intensity` | electricity per output |
| `hydrogen_intensity` | hydrogen per output |
| `fuel_intensity` | other fuel per output |
| `feedstock_intensity` | material input per output where represented |
| `captured_fraction` | CCS capture rate |

### Steel mapping requested

Please identify whether and how the model represents:

- conventional BF–BOF;
- efficient or hydrogen-enriched BF–BOF;
- smelting reduction;
- scrap-EAF;
- gas-DRI-EAF;
- H₂-DRI-EAF;
- DRI/HBI trade;
- BF, DRI, or smelting routes with CCUS.

### Chemicals mapping requested

Please identify whether and how the model represents:

- primary chemicals or high-value chemicals;
- naphtha or other steam-cracker routes;
- electrified process heat or electrified cracking;
- hydrogen used as fuel or feedstock;
- process or combustion CCUS;
- bio-based, recycled, or synthetic-carbon feedstock;
- material recycling or demand reduction;
- ammonia, methanol, olefins and aromatics separately, if available.

If the model has only an aggregate `chemicals` sector, please provide the full technology and fuel detail under that aggregate and the calibration source used for Korea and Japan.

## 7. Market and delivered prices

### `market_prices.csv`

| Field | Description |
|---|---|
| `scenario_id` | scenario |
| `region` | model region |
| `market` | electricity, hydrogen, gas, coal, liquids, biomass, scrap or other |
| `market_level` | primary, wholesale, delivered, industrial end use, or other |
| `year` | model year |
| `price_native` | native model value |
| `native_unit` | model unit and currency year |
| `price_converted` | research-team conversion if available |
| `converted_unit` | conversion unit and currency year |
| `conversion_method` | deflator, exchange rate, energy conversion |
| `included_components` | generation, grid, delivery, storage, transport, taxes |

For electricity and hydrogen, please state whether the price is the producer-market price, industrial delivered price, or another model-market price. CAP-KJ will not interpret a wholesale equilibrium price as a facility procurement price without the missing components.

## 8. Carbon-policy prices and constraints

### `policy_prices.csv`

| Field | Description |
|---|---|
| `scenario_id` | scenario |
| `region_or_market` | region or linked policy market |
| `policy_market` | CO₂, GHG, or other |
| `year` | model year |
| `policy_type` | fixed tax, emissions constraint, standard, or other |
| `fixed_price` | exogenous price if applicable |
| `shadow_price` | endogenous constraint price if applicable |
| `emissions_constraint` | cap if applicable |
| `native_unit` | original model unit |
| `converted_unit` | requested 2025 USD/tCO₂ if available |
| `conversion_method` | tC/tCO₂ and currency conversion |

Fixed prices and shadow prices must be separate. CAP-KJ will use both as system diagnostics but will use actual Korean and Japanese carbon-policy cash effects in the facility market-policy ledger.

## 9. Technology cost and performance inputs

### `technology_costs.csv`

| Field | Description |
|---|---|
| `scenario_id` | if the parameter varies by scenario |
| `region` | Korea, Japan, global or other |
| `sector` | sector |
| `technology` | native technology |
| `year` | model year |
| `capital_cost` | capital-cost assumption |
| `fixed_om` | fixed O&M |
| `variable_om` | variable O&M |
| `efficiency` | conversion efficiency |
| `capacity_factor` | utilisation assumption |
| `lifetime` | technical lifetime |
| `lead_time` | if represented |
| `retirement_rule` | model retirement behaviour |
| `cost_unit` | native unit |
| `currency_year` | price basis |
| `source` | source citation |
| `uncertainty_case` | low, central, high, if available |

Please flag which values are input assumptions rather than solved outputs.

## 10. Energy, material, and carbon coefficients

### `technology_inputs.csv`

| Field | Description |
|---|---|
| `scenario_id` | scenario if applicable |
| `region` | region |
| `sector` | sector |
| `technology` | technology |
| `year` | model year |
| `input_name` | electricity, hydrogen, coal, gas, liquids, scrap, ore or other |
| `input_coefficient` | input per unit of output |
| `unit` | native unit |
| `emissions_factor` | associated direct or upstream factor |
| `carbon_boundary` | direct, upstream, electricity or lifecycle |

For hydrogen, please provide or identify the pathway-specific carbon intensity and whether conversion, transport, storage, and reconversion are included.

## 11. Resource, infrastructure, and trade constraints

### `resource_constraints.csv`

| Field | Description |
|---|---|
| `scenario_id` | scenario |
| `region` | region |
| `year` | model year |
| `resource` | scrap, DRI/HBI, low-carbon H₂, clean power, CO₂ storage, bio-feedstock, recycled feedstock |
| `available_quantity` | available quantity or upper bound |
| `unit` | unit |
| `price_or_supply_curve` | price or supply-curve identifier |
| `carbon_intensity` | where relevant |
| `trade_allowed` | yes/no and direction |
| `source` | source citation |

### `trade_flows.csv`

Requested trade flows include:

- steel and, where possible, crude versus finished steel;
- chemicals or primary-chemical proxies;
- coal, gas, liquids, electricity and hydrogen;
- DRI/HBI and scrap;
- CO₂ transport or storage across regions if represented.

The trade output is necessary to distinguish domestic facility closure from system-wide emissions reduction.

## 12. Reproduction package

Please provide, where permitted:

- solved BaseX/output database;
- query XML used for the requested variables;
- run configuration XML;
- scenario-component list;
- GCAM release and commit hash;
- Korea-specific extension version;
- data-processing or figure-generation scripts;
- data dictionary or model diagram;
- underlying data for relevant paper figures;
- known model or output caveats;
- licence and preferred citation wording.

## 13. Quality-assurance questions

1. Are Korea and Japan represented as separate model regions in the delivered run?
2. Do the two regions use the same global scenario and technology assumptions?
3. Is iron and steel represented with explicit production technologies in each region?
4. Is H₂-DRI-EAF explicit, proxied, or absent?
5. Is the chemicals sector calibrated in physical product units or energy-service units?
6. Can primary chemicals be separated from the broader chemicals sector?
7. Are electricity and hydrogen prices producer, wholesale, or delivered prices?
8. What does the hydrogen price include?
9. Is the Net Zero carbon value a fixed tax or a shadow price from an emissions constraint?
10. How are process emissions, indirect electricity emissions, captured CO₂, and residual emissions represented?
11. Are technology costs exogenous inputs, and are sensitivity values available?
12. How does the logit technology-choice formulation affect interpretation of technology shares?
13. How are premature retirement, vintage, lifetime, and capacity utilisation represented?
14. How are industrial products and enabling-energy carriers traded between Korea, Japan, and other regions?
15. Do technology outputs sum to sector production, energy, and emissions totals?
16. Which data can be publicly redistributed in a GitHub repository?

## 14. Delivery format

Preferred order:

1. CSV or Parquet tables plus data dictionary;
2. solved database plus query XML;
3. paper-figure source data;
4. native input XML where no processed table exists.

Each file should include or be accompanied by:

- model and scenario version;
- generation date;
- variable definitions;
- units and currency price year;
- conversion method;
- scope and boundary;
- licence and citation.

## 15. Minimum acceptance criteria

CAP-KJ can use the delivery as its primary scenario backbone only if it includes:

1. comparable Korea and Japan production and emissions paths from the same run;
2. iron-and-steel and chemicals/industry outputs at the greatest native detail available;
3. scenario electricity, hydrogen, fuel, and carbon-policy prices with unambiguous units and market level;
4. technology energy, emissions, cost, efficiency, and lifetime assumptions;
5. enough metadata to reproduce or audit the extraction.

If any criterion is not met, CAP-KJ will use a documented alternative or surrogate. Every surrogate will be labelled as CAP-derived rather than GCAM output.
