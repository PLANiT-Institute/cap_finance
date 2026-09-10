import numpy as np
import pandas as pd
import pytest
from cap.input_boundaries import company_observations, COMPANY_COMPONENTS


def sites():
    return pd.DataFrame([dict(facility_id=f,year=2024,production=np.nan,emissions_s1=i+10,emissions_s2=i+1)
                         for i,f in enumerate(COMPANY_COMPONENTS['LOTTE'])])


def test_declared_complete_sites_recover_company_total_without_inventing_production():
    result=company_observations(sites(),'LOTTE',[2024]).iloc[0]
    assert result.emissions_s1==60 and result.emissions_s2==15 and pd.isna(result.production)
    assert result.emissions_s2_basis=='sum_of_declared_whole_site_components'


def test_reported_total_has_priority_without_double_counting_or_forcing_rounding_equality():
    p=pd.concat([sites(),pd.DataFrame([dict(facility_id='LOTTE_TOTAL',year=2024,production=np.nan,emissions_s1=61,emissions_s2=np.nan)])])
    result=company_observations(p,'LOTTE',[2024]).iloc[0]
    assert result.emissions_s1==61 and result.emissions_s2==15
    assert result.emissions_s1_basis=='reported_company_total'


def test_partial_boundary_and_missing_value_remain_unknown_and_duplicates_fail():
    p=sites()
    assert pd.isna(company_observations(p.iloc[:-1],'LOTTE',[2024]).emissions_s2.iloc[0])
    p.loc[0,'emissions_s2']=np.nan
    assert pd.isna(company_observations(p,'LOTTE',[2024]).emissions_s2.iloc[0])
    with pytest.raises(ValueError,match='Duplicate'):company_observations(pd.concat([p,p.iloc[:1]]),'LOTTE',[2024])
    with pytest.raises(ValueError,match='not declared'):company_observations(p,'OTHER',[2024])
