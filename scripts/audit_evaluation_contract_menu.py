"""Rerun final evaluation without assumed contracts; preserve the legacy run.

Candidate-generation 'unhedged' historically constrained E2 only. Compare the
explicit E5 unhedged menu with the recorded idealized PPA/EPC expansion.
"""
from pathlib import Path
import hashlib
import json
import sys
import yaml

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from cap import config as C,e5_metrics


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    config=ROOT/'tmp/research_case_expanded/config.yaml'
    cfg=C.load(config);source=Path(cfg.out_dir)
    source_manifest=json.loads((source/'run_manifest.json').read_text())
    # Preserve all source input/config data. Current code differences are
    # deliberate and separately recorded, as in the previous regression audit.
    for name,digest in source_manifest['source_sha256'].items():
        p=Path(name);p=p if p.is_absolute() else ROOT/p
        if not p.resolve().is_relative_to((ROOT/'src/cap').resolve()):
            assert sha(p)==digest,p
    original=source/'e5/frontier_points.csv';original_hash=sha(original)
    before=pd.read_csv(original)
    destination=ROOT/'tmp/research_unhedged_evaluation/run'
    destination.mkdir(parents=True,exist_ok=True)
    for stage in ('e1','e2','e3','e4'):
        target=destination/stage
        if target.is_symlink():assert target.resolve()==(source/stage).resolve()
        elif target.exists():raise ValueError(f'Refusing to replace existing directory: {target}')
        else:target.symlink_to(source/stage,target_is_directory=True)
    cfg['out_dir']=str(destination);cfg['evaluation_contracts']='unhedged'
    local_config=destination.parent/'config.yaml'
    local_config.write_text(yaml.safe_dump(dict(cfg),allow_unicode=True,sort_keys=False))
    e5_metrics.run(cfg)
    assert sha(original)==original_hash
    after=pd.read_csv(destination/'e5/frontier_points.csv')
    assert len(after)==45 and (after.ppa_share==0).all() and (after.epc==0).all() and (after.ccfd==0).all()
    unchanged=before[(before.ppa_share==0)&(before.epc==0)&(before.ccfd==0)]
    a,b=[x.set_index('plan_id').sort_index() for x in (after,unchanged)]
    assert a.index.equals(b.index)
    metrics=['mean','p50','p90','tcar','es_alpha']
    error=float(np.max(np.abs(a[metrics].to_numpy()-b[metrics].to_numpy())))
    assert error<1e-8
    rows=[]
    for keys,old in before.groupby(['company_id','scenario','support']):
        new=after[(after.company_id==keys[0])&(after.scenario==keys[1])&(after.support==keys[2])]
        for criterion in ('mean','tcar','es_alpha'):
            # A risk-spread minimum is a diagnostic; do not silently call it a
            # cost-efficient plan. Compare all budget-feasible candidates here.
            o=old.sort_values([criterion,'mean','plan_id']).iloc[0]
            n=new.sort_values([criterion,'mean','plan_id']).iloc[0]
            rows.append(dict(company_id=keys[0],scenario=keys[1],support=keys[2],criterion=criterion,
                legacy_candidate_count=len(old),unhedged_candidate_count=len(new),
                legacy_plan=o.plan_id,unhedged_plan=n.plan_id,
                legacy_ppa=float(o.ppa_share),legacy_epc=int(o.epc),
                legacy_value=float(o[criterion]),unhedged_value=float(n[criterion]),
                reduction_from_assumed_contract_menu=float(n[criterion]-o[criterion]),
                technology_schedule_changed=bool(o.base_plan_id!=n.base_plan_id),
                status='legacy estimated-facility/price-prior comparison; not sourced joint-price case'))
    out=ROOT/'data/research_v2/contract_menu_audit';out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(out/'menu_comparison.csv',index=False)
    after.to_csv(out/'unhedged_frontier_points.csv',index=False)
    sources=[config,source/'run_manifest.json',original,local_config,Path(__file__),
             ROOT/'src/cap/e5_metrics.py',ROOT/'src/cap/plancost.py']
    m=dict(source_files=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in sources],
        original_candidate_count=len(before),new_candidate_count=len(after),
        maximum_common_candidate_metric_error_bnKRW=error,original_run_unchanged=True,
        E2_reoptimized=False,E5_rerun=True,new_joint_price_case=False,
        candidate_contracts_scope='E2 surrogate only; this setting historically did not constrain E5',
        evaluation_contracts_scope='E5 final comparison menu; now explicit unhedged/legacy_grid/explicit_grid',
        source_inputs='Legacy22estimatedfacilities andold FIN price/H2/CAPEX priors; not newly validated corporate observations',
        default_policy='legacy_grid retained for backwards compatibility; use explicit policies in new research cases',
        caveat='A wider feasible menu cannot worsen the best objective; idealized contractual risk reduction is not empirical PPA superiority')
    (out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    print(json.dumps(dict(comparisons=len(rows),candidates=len(after),max_error=error),indent=2))


if __name__=='__main__':main()
