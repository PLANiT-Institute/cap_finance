"""Compare selected primary financial facts with legacy inputs in native units."""
from pathlib import Path
import hashlib
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/research_cycles/2026-09-05"


def main():
    facts = pd.read_csv(OUT / "verified_financial_observations.csv")
    legacy_path = ROOT / "data/prepared/D6_company_financials.csv"
    old = pd.read_csv(legacy_path)
    rows = []
    mapping = {"revenue":"revenue", "cash":"cash", "interest_bearing_debt":"total_debt",
               "reported_net_debt":"net_debt", "reported_ebitda":"ebitda", "capital_expenditure":"capex_total"}
    for r in facts.itertuples():
        field = mapping.get(r.metric)
        if not field: continue
        g = old[(old.company_id == r.company_id) & (old.year == r.fiscal_year)]
        value = float(g[field].iloc[0]) if len(g) else float("nan")
        # Legacy Japanese numbers are hundred-million yen. This is a unit
        # conversion within JPY, not a currency exchange conversion to KRW.
        value *= .1 if r.currency == "JPY" else 1
        status = ("previously_missing" if pd.isna(value) else
                  "wrong_earnings_definition" if r.metric == "reported_ebitda" else
                  "matches" if abs(value-r.value_bn_native)<1e-8 else "vintage_or_rounding_difference")
        rows.append(dict(company_id=r.company_id, fiscal_year=r.fiscal_year, legacy_field=field,
            audited_metric=r.metric, currency=r.currency, legacy_value_bn_native=value,
            audited_value_bn_native=r.value_bn_native, difference_bn_native=r.value_bn_native-value,
            status=status, source_name=r.source_name))
    result = pd.DataFrame(rows)
    result.to_csv(OUT / "financial_legacy_comparison.csv", index=False)
    oldref = old.query("company_id=='POSCO' and year>=2023").ebitda.mean()
    newref = facts.query("company_id=='POSCO' and metric=='reported_ebitda'").value_bn_native.mean()
    summary = dict(comparisons=len(result), status_counts=result.status.value_counts().to_dict(),
        posco_2023_25_legacy_ebitda_ref_bnkrw=oldref,
        posco_2023_25_reported_ebitda_ref_bnkrw=newref,
        posco_peak_ratio_multiplier_if_numerator_unchanged=oldref/newref,
        model_rerun=False, all_historical_financials_audited=False,
        sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (Path(__file__),legacy_path,OUT/"verified_financial_observations.csv")})
    (OUT / "financial_legacy_comparison_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps({k:v for k,v in summary.items() if k!='sha256'},indent=2))


if __name__ == "__main__":
    main()
