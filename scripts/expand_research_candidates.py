"""Expand a verified menu along physical emissions, preserving all prior plans."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import shutil
import sys
import time
import traceback

import numpy as np
import pandas as pd
import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from cap import config as C,e4_revalue,e5_metrics
from cap.e2_milp import _prep_company,_solve_company
from run_research_case import digest


def signature(plan):
    return tuple(sorted((r.facility_id,r.tech_id,int(r.adopt_year))
                        for r in plan.itertuples() if pd.notna(r.tech_id)))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base-config',type=Path,required=True)
    ap.add_argument('--out-root',type=Path,required=True)
    ap.add_argument('--emissions-points',type=int,default=4)
    args=ap.parse_args()
    if args.emissions_points<2:raise ValueError('At least two emissions points required')
    base=C.load(args.base_config);parent=Path(base.out_dir)
    parent_manifest=json.loads((parent/'run_manifest.json').read_text())
    assert parent_manifest['status']=='completed'
    for name,value in parent_manifest['source_sha256'].items():
        p=Path(name);p=p if p.is_absolute() else ROOT/p
        assert hashlib.sha256(p.read_bytes()).hexdigest()==value,name
    root=args.out_root.resolve();root.mkdir(parents=True,exist_ok=True)
    output=root/'run'
    if (output/'run_manifest.json').exists():
        raise FileExistsError('Use a new output root; existing run manifests are preserved')
    for stage in ['e1','e2','e3']:shutil.copytree(parent/stage,output/stage)
    cfg=C.load(args.base_config,out_dir=str(output))
    cfg['candidate_expansion_emissions_points']=args.emissions_points
    config_path=root/'config.yaml'
    config_path.write_text(yaml.safe_dump({k:v for k,v in cfg.items() if k!='root'},sort_keys=False,allow_unicode=True))
    files=list(C.data_dir(cfg).glob('*.csv'))+list((ROOT/'src/cap').glob('*.py'))+[config_path,Path(__file__).resolve()]
    before=digest(files)
    record=dict(status='running',started_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        config_path=str(config_path),source_sha256=before,stages=[],
        parent_run_manifest_sha256=hashlib.sha256((parent/'run_manifest.json').read_bytes()).hexdigest(),
        method='Preserve verified parent menu and add minimum-emissions plus emission-cap cost minimizers')
    manifest_path=output/'run_manifest.json'
    def save():manifest_path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    save()
    try:
        fac,tech,cal=_prep_company(cfg,C.data_dir(cfg))
        prices=pd.read_csv(output/'e1/price_paths_central.csv')
        constraints=pd.read_csv(output/'e1/constraints.csv')
        availability=pd.read_csv(output/'e1/tech_availability.csv')
        idx=pd.read_csv(output/'e2/plan_index.csv');base_rows=len(idx)
        next_id=max(int(x[1:]) for x in idx.plan_id)+1
        additions=[];attempts=[]
        start=time.monotonic()
        for (company,scenario),group in idx.groupby(['company_id','scenario']):
            print('EXPAND',company,scenario,flush=True)
            signatures={signature(pd.read_csv(output/'e2/plans'/f'plan_{pid}.csv')) for pid in group.plan_id}
            arguments=(cfg,company,scenario,fac,tech,cal,prices,constraints,availability)
            minimum=_solve_company(*arguments,objective='emissions')
            solutions=[]
            if minimum is not None:
                solutions.append(('minimum_emissions',None,minimum))
                low=minimum['cum_emis_tco2'];high=minimum['cumulative_budget_tco2']
                for cap in np.linspace(low,high,args.emissions_points):
                    bound=min(high,float(cap)+max(1.,abs(cap))*1e-9)
                    result=_solve_company(*arguments,objective='cost',emis_cap=bound)
                    solutions.append(('cost_at_emissions_cap',bound,result))
            for objective,cap,result in solutions:
                if result is None:
                    attempts.append(dict(company_id=company,scenario=scenario,objective=objective,emissions_cap=cap,status='no_verified_solution'))
                    continue
                plan=pd.DataFrame(result['plan'] or [dict(facility_id=None,tech_id=None,adopt_year=None,op_year=None)])
                key=signature(plan)
                duplicate=key in signatures
                attempts.append(dict(company_id=company,scenario=scenario,objective=objective,emissions_cap=cap,
                                     status='duplicate' if duplicate else 'new_schedule',cum_emissions=result['cum_emis_tco2']))
                if duplicate:continue
                signatures.add(key);pid=f'P{next_id:04d}';next_id+=1
                plan.assign(plan_id=pid,company_id=company,scenario=scenario,ppa_share=result['ppa'],
                            epc=result['epc'],ccfd=result['ccfd']).to_csv(output/'e2/plans'/f'plan_{pid}.csv',index=False)
                feasible=result['primal_feasibility']
                additions.append(dict(plan_id=pid,company_id=company,scenario=scenario,
                    npv_cost_bnkrw=result['npv_cost'],risk_proxy=result['risk'],ppa_share=result['ppa'],
                    epc=result['epc'],ccfd=result['ccfd'],budget_slack_tco2=result['budget_slack'],
                    is_disclosed=False,solve_status=result['solve_status'],comparison_basis='optimized_candidate',
                    cum_emis_tco2=result['cum_emis_tco2'],cumulative_budget_tco2=result['cumulative_budget_tco2'],
                    budget_mode=result['budget_mode'],primal_feasible=feasible['valid'],
                    solution_status=feasible['solution_status'],max_scaled_constraint_violation=feasible['max_scaled_constraint_violation']))
        pd.concat([idx,pd.DataFrame(additions)],ignore_index=True).to_csv(output/'e2/plan_index.csv',index=False)
        pd.DataFrame(attempts).to_csv(output/'e2/expansion_attempts.csv',index=False)
        record['stages'].append(dict(stage='E2_emissions_expansion',status='completed',elapsed_seconds=time.monotonic()-start,
                                     preserved_schedules=base_rows,added_schedules=len(additions)))
        save()
        for name,module in [('E4',e4_revalue),('E5',e5_metrics)]:
            start=time.monotonic();module.run(cfg)
            record['stages'].append(dict(stage=name,status='completed',elapsed_seconds=time.monotonic()-start));save()
        assert digest(files)==before,'Source or input changed during run'
        record.update(status='completed',finished_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      output_sha256=digest([p for p in output.rglob('*') if p.is_file() and p!=manifest_path]))
    except Exception:
        record.update(status='failed',error=traceback.format_exc());save();raise
    save()
    print('ADDED',len(additions),'TO',base_rows,flush=True)


if __name__=='__main__':main()
