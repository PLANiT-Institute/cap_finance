"""Keep declaration-derived paths and certify limitations of the current menu.

Uses the legacy estimated facility portfolio as an explicitly scoped proxy.
This is not a test of whether a company's actual net-zero declaration is viable.
"""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from cap import config as C
from cap.e2_milp import _prep_company
from cap.e1_constraints import COMPANY_REGION
from cap.disclosed_path import linear_disclosed_path
from cap.disclosed_feasibility import emission_floor


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    config=ROOT/'tmp/research_case_expanded/config.yaml'
    cfg=C.load(config)
    if cfg.milp.get('retire_max_share',0.2)!=0:
        raise ValueError('This fixed-output certificate requires retirement to be disabled')
    fac,tech,_=_prep_company(cfg,C.data_dir(cfg))
    declarations_path=ROOT/'data/research_v2/disclosed_linear_reference/declarations.csv'
    declarations=pd.read_csv(declarations_path).set_index('company_id')
    availability_path=Path(cfg.out_dir)/'e1/tech_availability.csv'
    av=pd.read_csv(availability_path)
    panel_path=C.data_dir(cfg)/'D1b_facility_panel.csv'
    panel=pd.read_csv(panel_path)
    base_year=int(panel.year.max()) #2024, linked to the2022–2024mean proxy, not actual2024emissions
    years=np.arange(cfg.years.start,cfg.years.end+1)
    lines=[];details=[];summaries=[]
    for company,cf in fac.groupby('company_id'):
        base=float((cf.production*cf.ef_inc).sum())
        dec=declarations.loc[company]
        line=linear_disclosed_path(company_id=company,base_year=base_year,
            target_year=int(dec.target_year),base_emissions=base,years=years,
            declaration_source=dec.source_url,
            baseline_source=f'Estimated covered facilities: mean2022–2024; source{panel_path.relative_to(ROOT)}; sha256={sha(panel_path)}',
            scope='covered estimated facilities Scope1 proxy, not corporate declaration boundary',
            accounting_basis='gross_zero_offset_assumption',unit='tCO2/year')
        for scenario in cfg.scenarios:
            a=av[(av.scenario==scenario)&(av.region==COMPANY_REGION[company])]
            amap=dict(zip(a.tech_id,a.avail_year_scenario))
            for start in (base_year,int(years[0])):
                floor,detail=emission_floor(cf,tech,years,earliest_start_year=start,availability=amap)
                joined=line.merge(floor,on=['company_id','year'],validate='one_to_one')
                joined['scenario']=scenario;joined['earliest_start_year']=start
                joined['floor_relative_to_baseline']=joined.floor_emissions_tco2/base
                joined['minimum_missing_abatement_tco2']=np.maximum(0,joined.floor_emissions_tco2-joined.emissions)
                joined['infeasible_under_declared_menu']=joined.minimum_missing_abatement_tco2>max(1e-6,base*1e-10)
                joined['corporate_scope_harmonized']=False
                joined['cost_status']='not_costed_when_optimistic_physical_bound_exceeds_path'
                failed=joined[joined.infeasible_under_declared_menu]
                terminal=joined.iloc[-1]
                summaries.append(dict(company_id=company,scenario=scenario,earliest_start_year=start,
                    declaration_target_year=int(dec.target_year),linear_base_year=base_year,
                    base_scope1_proxy_tco2=base,base_status='estimated2022–2024mean_assigned_to2024',
                    covered_facilities=len(cf),first_bound_violation_year=int(failed.year.min()) if len(failed) else None,
                    violating_years=len(failed),terminal_floor_tco2=terminal.floor_emissions_tco2,
                    terminal_floor_percent_of_proxy_baseline=100*terminal.floor_relative_to_baseline,
                    cumulative_missing_abatement_lower_bound_tco2=joined.minimum_missing_abatement_tco2.sum(),
                    linear_path_accepted=True,corporate_scope_harmonized=False,
                    conditional_gross_path_infeasible=bool(len(failed)),
                    cost_evaluated=False,solver_called=False,
                    reason='Optimistic physical lower bound certificate; no zero-emission route/removal/retirement in this fixed-output menu'))
                lines.append(joined)
                details.append(detail.assign(scenario=scenario,earliest_start_year=start))
    out=ROOT/'data/research_v2/disclosed_feasibility';out.mkdir(parents=True,exist_ok=True)
    pd.concat(lines,ignore_index=True).to_csv(out/'linear_paths_and_bounds.csv',index=False)
    pd.concat(details,ignore_index=True).to_csv(out/'facility_floor_witnesses.csv',index=False)
    result=pd.DataFrame(summaries);result.to_csv(out/'case_summary.csv',index=False)
    sources=[config,declarations_path,panel_path,C.data_dir(cfg)/'D1a_facility_static.csv',
        C.data_dir(cfg)/'D3_tech_options.csv',availability_path,Path(__file__),
        ROOT/'src/cap/disclosed_path.py',ROOT/'src/cap/disclosed_feasibility.py',
        ROOT/'src/cap/e2_milp.py',ROOT/'src/cap/e1_constraints.py']
    m=dict(source_files=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in sources],
        scenarios=list(cfg.scenarios),cases=len(result),years=years.tolist(),linear_paths_admitted=True,
        base_year=base_year,base_year_emissions_are_reported_measurements=False,
        input_facility_status='22estimatedfacility portfolio, full corporate scope not verified',
        declared_scope_aligned=False,net_zero_to_gross_zero_is_an_assumption=True,
        retirement_cap_verified_zero=True,
        earliest_start_cases=[base_year,int(years[0])],
        bound_definition='Annual independent minimum emission factor among compatible routes after availability+construction; fixed output; no retirement or removals',
        interpretation='A positive lower-bound excess proves infeasibility only under this scoped menu and no-offset assumption',
        not_concluded=['Corporate declaration infeasible','Actual corporate emissions baseline verified',
            'A relaxed lower-bound sequence is an executable investment schedule','A cost/TCaR for an infeasible reference',
            'NZE/STEPS source prices and existing B20/NZ15 technology availability are harmonized'],
        solver_calls=0,reason_no_solver='All cases have a positive physical lower-bound certificate; do not manufacture an optimal cost')
    assert result.conditional_gross_path_infeasible.all()
    (out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    print(result[['company_id','scenario','earliest_start_year','first_bound_violation_year',
                  'terminal_floor_percent_of_proxy_baseline']].to_string(index=False))


if __name__=='__main__':main()
