import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from ncc_cash_workbook_control import DEFAULTS,validate,evaluate
from xlsx_table_reader import WorkbookInputError

@pytest.mark.parametrize('change',[{'hours':None},{'hours':0},{'paths':10.5},{'paths':True},{'alpha':1},{'discount':-1},{'block':2},{'base_life':0},{'sale':1.1},{'power':-1},{'scenario':'unknown'},{'maintenance_scale':.5},{'seed':float('nan')}])
def test_bad_controls(change):
 with pytest.raises(WorkbookInputError):validate(dict(DEFAULTS,**change))

def test_zero_market_prices_have_no_cost_dispersion():
 r=evaluate(dict(DEFAULTS,paths=101,power=0,methane=0,naphtha=0,alpha=.95327))
 assert r['metrics']['tcar']==0
 assert r['metrics']['es_alpha']==pytest.approx(r['analytic_mean'])
 assert r['max_FIN_error']<1e-7

def test_common_feedstock_changes_absolute_cost_only():
 a=evaluate(dict(DEFAULTS,paths=101,naphtha=0))
 b=evaluate(dict(DEFAULTS,paths=101,naphtha=700))
 for k in ('mean','tcar','es_alpha'):assert a['metrics'][k]==pytest.approx(b['metrics'][k],abs=1e-8)
 aa=np.array(a['draws']);bb=np.array(b['draws'])
 assert np.all(bb[:,1]>aa[:,1])
 np.testing.assert_allclose(bb[:,1]-aa[:,1],bb[:,2]-aa[:,2],atol=1e-8)

def test_zero_sale_changes_gas_price_exposure():
 a=evaluate(dict(DEFAULTS,paths=101,sale=0))
 b=evaluate(dict(DEFAULTS,paths=101,sale=1))
 assert a['analytic_mean']>b['analytic_mean']
 assert a['metrics']['tcar']!=pytest.approx(b['metrics']['tcar'])

def test_integer_zero_discount_and_annuity_are_valid():
 r=evaluate(dict(DEFAULTS,paths=101,discount=0,annuity_rate=0,scenario='NZE',base_life=25,electric_life=30,terminal='straight_line_proxy'))
 assert all(row[13]==1 for row in r['annual'])
 assert r['max_FIN_error']<1e-7
