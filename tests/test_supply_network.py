from dataclasses import replace
import numpy as np
import pytest
from cap.supply_network import SiteSupply,Transfer,delivery_balance,consolidate_cash


def example():
    sites={'A':SiteSupply([10,8],[0,0],[6,6],[1,0],0,[10,10],[0,0],[1,1]),
           'B':SiteSupply([0,0],[1,1],[4,4],[0,0],0,[0,0],[1,1],[0,0])}
    t=Transfer('AB','A','B',[3,3],[3,3])
    kw=dict(years=[2030,2031],product_specification='Test-only same ethylene grade',required_delivery={'A':[6,6],'B':[4,4]},inventory_boundary={'A':[0,0],'B':[0,0]})
    return sites,[t],kw


def test_same_delivery_with_inventory_and_internal_supply():
    s,t,k=example();r=delivery_balance(s,t,**k)
    np.testing.assert_array_equal(r['delivery'],[10,10]);np.testing.assert_array_equal(r['inventory_change'],[1,-1])
    np.testing.assert_array_equal(r['consolidated_residual'],[0,0])


def test_external_replacement_preserves_customer_output():
    s,t,k=example();s['A']=replace(s['A'],production=[6,6],closing_inventory=[0,0]);s['B']=replace(s['B'],external_purchase=[4,4],purchase_limit=[4,4])
    r=delivery_balance(s,[],**k)
    np.testing.assert_array_equal(r['external_purchase'],[4,4]);np.testing.assert_array_equal(r['delivery'],[10,10])


def test_group_balance_cannot_hide_local_shortage():
    s,t,k=example();s['A']=replace(s['A'],production=[9,8]);s['B']=replace(s['B'],production=[1,0],production_limit=[1,1])
    with pytest.raises(ValueError,match='Local material'):delivery_balance(s,t,**k)


@pytest.mark.parametrize('field,value,message',[
 ('production',[11,8],'capacity'),('external_purchase',[1,0],'capacity'),
 ('closing_inventory',[2,0],'capacity'),('initial_inventory',2,'capacity'),
 ('production',[-1,8],'Finite'),('production',[[10,8],[10,8]],'Finite'),
 ('production',[float('nan'),8],'Finite'),('production',[True,False],'numeric'),
 ('delivery',[5,6],'Customer')])
def test_bad_site_rejected(field,value,message):
    s,t,k=example();s['A']=replace(s['A'],**{field:value})
    with pytest.raises(ValueError,match=message):delivery_balance(s,t,**k)


@pytest.mark.parametrize('edit',[dict(destination='outside'),dict(destination='A'),dict(capacity=[2,3]),dict(identifier='')])
def test_invalid_transfer(edit):
    s,t,k=example()
    with pytest.raises(ValueError):delivery_balance(s,[replace(t[0],**edit)],**k)


def test_duplicate_transfer_and_missing_customer_constraint():
    s,t,k=example()
    with pytest.raises(ValueError):delivery_balance(s,t+t,**k)
    k['required_delivery'].pop('B')
    with pytest.raises(ValueError):delivery_balance(s,t,**k)


@pytest.mark.parametrize('markup',[0.,2.,1e20,-3.])
def test_internal_pricing_cannot_change_consolidated_cash(markup):
    _,t,_=example();a=np.array([[1.,2.],[3.,4.]]);b=a*2;freight=np.ones((2,2))*.5
    r=consolidate_cash({'A':a,'B':b},t,{'AB':np.full((2,2),markup)},{'AB':freight},shape=(2,2))
    np.testing.assert_array_equal(r['consolidated_cash'],a+b+freight)
    if abs(markup)<100:np.testing.assert_allclose(sum(r['site_posted_cash'].values()),r['consolidated_cash'])


@pytest.mark.parametrize('kind',['missing_site','missing_freight','missing_settlement','wrong_shape','nan'])
def test_incomplete_cash_rejected(kind):
    _,t,_=example();a=np.ones((2,2));sites={'A':a,'B':a};settle={'AB':a};freight={'AB':a}
    if kind=='missing_site':sites.pop('B')
    if kind=='missing_freight':freight.clear()
    if kind=='missing_settlement':settle.clear()
    if kind=='wrong_shape':settle['AB']=np.ones((2,1))
    if kind=='nan':freight['AB']=a*np.nan
    with pytest.raises(ValueError):consolidate_cash(sites,t,settle,freight,shape=(2,2))


def test_free_initial_stock_and_terminal_depletion_rejected():
    s,t,k=example()
    s['A']=replace(s['A'],initial_inventory=1,production=[9,8])
    with pytest.raises(ValueError,match='inventory differs'):delivery_balance(s,t,**k)
    s,t,k=example();k['inventory_boundary']['A']=[0,1]
    with pytest.raises(ValueError,match='inventory differs'):delivery_balance(s,t,**k)


def test_skipped_year_does_not_silently_carry_inventory():
    s,t,k=example();k['years']=[2030,2032]
    with pytest.raises(ValueError,match='Consecutive'):delivery_balance(s,t,**k)


def test_opening_stock_must_fit_current_period_capacity():
    s,t,k=example();s['A']=replace(s['A'],inventory_limit=[1,0])
    with pytest.raises(ValueError,match='capacity'):delivery_balance(s,t,**k)
