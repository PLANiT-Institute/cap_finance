from pathlib import Path
import sys
import pytest
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import timing_workbook_control as t

@pytest.mark.parametrize('key,value',[('paths',None),('seed',True),('block',5),('alpha',1),('grid_start',-1),('cum_fraction',1.1),('remaining_years',2.5),('replacement_scale',float('nan')),('scenario','unknown'),('constraint','terminal_only')])
def test_reject_invalid_controls(key,value):
 with pytest.raises(t.WorkbookInputError):t.validate(dict(t.DEFAULTS,**{key:value}))

def test_empty_set_skips_MC(monkeypatch):
 def unexpected(*args):raise AssertionError('No price generation is allowed')
 monkeypatch.setattr(t,'block_paths',unexpected)
 p=t.evaluate(dict(t.DEFAULTS,residual=.05))
 assert not p['MC_executed'] and p['FIN_checks']==0 and p['draws']==[] and p['metrics']=={}
 assert not any(q['eligible'] for q in p['qualification'])

def test_annual_linear_is_a_different_constraint(monkeypatch):
 monkeypatch.setattr(t,'block_paths',lambda *args:pytest.fail('No eligible annual path'))
 p=t.evaluate(dict(t.DEFAULTS,constraint='annual_linear'))
 assert not p['MC_executed']
 assert any(q['cumulative_feasible'] for q in p['qualification'])
 assert not any(q['annual_feasible'] for q in p['qualification'])

def test_four_candidates_fractional_tail_and_zero_discount():
 p=t.evaluate(dict(t.DEFAULTS,paths=103,alpha=.93,cum_fraction=1.,discount=0.,remaining_years=3,replacement_scale=1.2))
 assert p['FIN_checks']==515 and len(p['metrics'])==4 and len(p['draws'])==103
 for j,name in enumerate(['replace_2030','replace_2035','replace_2040','replace_2045'],2):
  x=np.sort(np.array(p['draws'])[:,j]);mass=103*(1-.93);k=int(mass)
  expected=(x[-k:].sum()+(mass-k)*x[-k-1])/mass
  np.testing.assert_allclose(p['metrics'][name]['es_alpha'],expected,rtol=1e-12)
