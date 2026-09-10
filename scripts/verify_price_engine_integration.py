"""Rerun E3/E4/E5 on the saved candidate menu and compare to independent repricing."""
from pathlib import Path
import hashlib,json,shutil,sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from cap import config as C
from cap import e3_prices,e4_revalue,e5_metrics


def main():
    output=ROOT/'docs/research_cycles/2026-09-05/positive_prices/engine_integration'
    output.mkdir(parents=True,exist_ok=True)
    run_dir=ROOT/'tmp/price_engine_v2/run'
    run_dir.mkdir(parents=True,exist_ok=True)
    for stage in ('e1','e2'):
        shutil.copytree(ROOT/'out'/stage,run_dir/stage,dirs_exist_ok=True)
    cfg=C.load(out_dir=str(run_dir),capex_shock_scaling='positive_lognormal',capital_accounting='legacy_mixed',energy_balance_mode='legacy_retrofit_all',carbon_accounting_mode='legacy_auction_discount',transition_loss_basis='incremental_ex_carbon',plan_selection_criterion='p50')
    e3_prices.run(cfg);e4_revalue.run(cfg);e5_metrics.run(cfg)
    actual=pd.read_csv(run_dir/'e5/frontier_points.csv')
    expected=pd.read_csv(output.parent/'risk_comparison.csv')
    keys=['company_id','scenario','support','plan_id']
    joined=actual.merge(expected,on=keys,suffixes=('_engine','_independent'),validate='one_to_one')
    assert len(joined)==len(expected)==268
    rows=[]
    for metric in ('p50','tcar'):
        diff=np.abs(joined[metric+'_engine']-joined[metric+'_independent'])
        assert diff.max()<1e-7,(metric,diff.max())
        rows.append({'metric':metric,'max_absolute_error_bnkrw':float(diff.max())})
    joined.to_csv(output/'candidate_comparison.csv',index=False)
    new=e3_prices.load_shocks(cfg)
    old=e3_prices.load_shocks(C.load(allow_legacy_price_paths=True))
    path_errors={k:float(np.max(np.abs(v-old[k]))) for k,v in new.items()}
    assert max(path_errors.values())<1e-10
    result={'evaluated_candidates':len(joined),'risk_cells_compared':len(joined)*2,
            'comparison':rows,'base_price_path_max_abs_errors':path_errors,
            'pricing_engine_version':'positive_lognormal_v2','independent_reference':'positive_prices/risk_comparison.csv',
            'scope':'Existing GBM mean-normalized candidate menu only; no new E2 optimization; other accounting and data defects remain',
            'run_dir':str(run_dir.relative_to(ROOT)),
            'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'src/cap/e3_prices.py',ROOT/'src/cap/price_process.py',ROOT/'src/cap/plancost.py',output.parent/'risk_comparison.csv']}}
    (output/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
