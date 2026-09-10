import pandas as pd

from cap.financial_reference import comparable_funding_ratios, REQUIRED_METADATA


def fixture():
    metrics=pd.DataFrame([dict(company_id='A',capex_total_bnkrw=100,capex_peak_bnkrw=20)])
    row=dict(company_id='A',year=2025,ebitda=40,revenue=200,net_debt=60)
    return metrics,row


def test_missing_currency_or_mislabeled_profit_cannot_create_a_funding_ratio():
    metrics,row=fixture()
    for metadata in [{},{**REQUIRED_METADATA,'earnings_definition':'operating_profit'},
                     {**REQUIRED_METADATA,'amount_unit':'bn_JPY'}]:
        result=comparable_funding_ratios(metrics,pd.DataFrame([{**row,**metadata}])).iloc[0]
        assert pd.isna(result.capex_peak_to_ebitda)
        assert '미검증' in result.funding_verdict


def test_verified_reference_is_traceable_but_does_not_invent_future_debt():
    metrics,row=fixture()
    result=comparable_funding_ratios(metrics,pd.DataFrame([{**row,**REQUIRED_METADATA}])).iloc[0]
    assert result.capex_peak_to_ebitda==.5 and result.netdebt_to_ebitda_now==1.5
    assert result.ebitda_years=='2025' and pd.isna(result.netdebt_to_ebitda_post)
    assert '별도 검토' in result.funding_verdict


def test_negative_ebitda_is_not_a_proof_of_insolvency_or_inability_to_fund():
    metrics,row=fixture()
    result=comparable_funding_ratios(metrics,pd.DataFrame([{**row,**REQUIRED_METADATA,'ebitda':-1}])).iloc[0]
    assert pd.isna(result.capex_peak_to_ebitda)
    assert '조달 불가능 판정 아님' in result.funding_verdict
