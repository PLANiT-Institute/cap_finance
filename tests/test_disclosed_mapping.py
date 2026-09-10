import numpy as np
import pandas as pd
from cap.e2_milp import _disclosed_fixed


def inputs():
    cf=pd.DataFrame([dict(facility_id='A',company_id='C',unit_type='NCC')]).set_index('facility_id')
    tech=pd.DataFrame([dict(tech_id='T',applies_to_unit='NCC',build_years=3,avail_year=2030)])
    row=dict(company_id='C',item_type='tech_commit',facility_id='A',tech_id='T',year_stated=2033,
             coverage_pct=np.nan,source_id='PRIMARY',mapping_status='validated_exact')
    return cf,tech,row


def check(rows):
    cf,tech,_=inputs()
    return _disclosed_fixed(pd.DataFrame(rows),cf,tech,np.arange(2025,2051),{})


def test_exact_reviewed_mapping_preserves_operation_date_and_labels_completion():
    _,_,row=inputs();result=check([row])
    assert result['valid'] and result['x']=={('A','T',2030):1}
    assert result['comparison_basis']=='commitment_constrained_model_completion'


def test_unreviewed_and_partial_and_missing_asset_mappings_are_rejected():
    _,_,row=inputs()
    for change in [dict(mapping_status='unreviewed'),dict(coverage_pct=30),dict(facility_id='missing')]:
        result=check([{**row,**change}]);assert not result['valid'] and result['dropped'] and not result['x']


def test_impossible_disclosed_date_is_not_shifted_to_available_date():
    _,_,row=inputs();result=check([{**row,'year_stated':2032}])
    assert not result['valid'] and not result['x']
    assert 'shifting dates' in result['dropped'][0]


def test_one_unrepresented_commitment_invalidates_whole_comparator():
    _,_,row=inputs();result=check([row,{**row,'tech_id':'OTHER'}])
    assert result['x'] and not result['valid']
    future=check([row,{**row,'item_type':'ppa','year_stated':2030,'coverage_pct':40}])
    assert not future['valid'] and any('future contract' in r for r in future['dropped'])
