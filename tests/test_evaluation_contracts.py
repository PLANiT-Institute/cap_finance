"""Final evaluation must obey its explicit menu instead of assuming a PPA."""
import pytest
from cap.e5_metrics import evaluation_contract_grid


def test_historical_menu_is_preserved_and_unhedged_menu_is_explicit():
    old=[(p,e) for p in (0.,.25,.5,.75,1.) for e in (0,1)]
    assert evaluation_contract_grid({})==old
    # E2-only setting never purported to constrain the historical E5 menu.
    assert evaluation_contract_grid({'candidate_contracts':'unhedged'})==old
    assert evaluation_contract_grid({'evaluation_contracts':'unhedged'})==[(0.,0)]


def test_explicit_menu_preserves_declared_order_and_does_not_add_contracts():
    cfg={'evaluation_contracts':'explicit_grid','evaluation_contract_grid':[
        {'ppa_share':0.,'epc':0},{'ppa_share':.4,'epc':1}]}
    assert evaluation_contract_grid(cfg)==[(0.,0),(.4,1)]


@pytest.mark.parametrize('rows',[[],[{}],[{'ppa_share':1.1,'epc':0}],
    [{'ppa_share':float('nan'),'epc':0}],[{'ppa_share':True,'epc':0}],
    [{'ppa_share':.5,'epc':True}],[{'ppa_share':.5,'epc':2}],
    [{'ppa_share':.5,'epc':1,'ccfd':0}],
    [{'ppa_share':0.,'epc':0},{'ppa_share':0.,'epc':0}]])
def test_invalid_or_duplicate_menu_is_rejected(rows):
    with pytest.raises(ValueError):evaluation_contract_grid({
        'evaluation_contracts':'explicit_grid','evaluation_contract_grid':rows})


def test_unknown_policy_is_not_silently_treated_as_legacy():
    with pytest.raises(ValueError):evaluation_contract_grid({'evaluation_contracts':'unknown'})
