"""Contextual funding ratios only after unit, earnings and entity checks."""
import numpy as np
import pandas as pd


REQUIRED_METADATA = {
    'amount_unit': 'bn_KRW_2025',
    'earnings_definition': 'reported_ebitda',
    'boundary_status': 'financing_entity_covers_modeled_assets',
    'verification_status': 'primary_verified',
}


def comparable_funding_ratios(metrics, financials):
    """Latest comparable annual reference; no invented future financing path.

    A positive earnings denominator is not proof that cash or borrowing capacity
    is sufficient. Cumulative project expenditure is not added instantaneously
    to current debt. Unverified rows remain available in the source data but are
    not treated as normalized KRW EBITDA observations.
    """
    rows=[]
    for _,metric in metrics.iterrows():
        row=metric.to_dict()
        group=financials[financials.company_id==metric.company_id].copy()
        for column,expected in REQUIRED_METADATA.items():
            if column not in group:
                group=group.iloc[:0]
                break
            group=group[group[column].eq(expected)]
        valid=group.dropna(subset=['ebitda']).sort_values('year')
        for field in ['ebitda_ref_bnkrw','revenue_latest_bnkrw','net_debt_bnkrw',
                      'capex_peak_to_ebitda','capex_total_to_ebitda','capex_total_to_revenue_pct',
                      'netdebt_to_ebitda_now','netdebt_to_ebitda_post']:
            row[field]=np.nan
        row['ebitda_years']=''
        row['financial_reference_status']='unverified_unit_earnings_or_entity_boundary'
        row['funding_verdict']='비교 기준 미검증 — 비율 미산출'
        if len(valid):
            ref=valid.iloc[-1]
            e=float(ref.ebitda)
            row.update(ebitda_ref_bnkrw=e,ebitda_years=str(int(ref.year)),
                       revenue_latest_bnkrw=ref.revenue,net_debt_bnkrw=ref.net_debt,
                       financial_reference_status='latest_verified_comparable_annual_reference',
                       funding_verdict='참고 비율 — 현금흐름·차입·배당 경로를 별도 검토')
            if e>0:
                row['capex_peak_to_ebitda']=metric.capex_peak_bnkrw/e
                row['capex_total_to_ebitda']=metric.capex_total_bnkrw/e
                row['netdebt_to_ebitda_now']=ref.net_debt/e
            else:
                row['funding_verdict']='EBITDA 비양수 — EBITDA 배수 미산출; 조달 불가능 판정 아님'
            if pd.notna(ref.revenue) and ref.revenue>0:
                row['capex_total_to_revenue_pct']=100*metric.capex_total_bnkrw/ref.revenue
        rows.append(row)
    return pd.DataFrame(rows)
