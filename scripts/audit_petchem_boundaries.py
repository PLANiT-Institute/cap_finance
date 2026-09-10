"""Trace petrochemical source boundaries and actual E4 fuel accounting."""
from pathlib import Path
import json
import sys
import hashlib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from cap import config as C
from cap.e2_milp import _prep_company
from cap.e4_revalue import _central_px
from cap.e1_constraints import COMPANY_REGION
from cap.plancost import build_profile, GJ_PER_T_GAS

OUT = ROOT / 'docs/research_cycles/2026-09-05/petchem_data'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    static = pd.read_csv(ROOT / 'data/prepared/D1a_facility_static.csv')
    panel = pd.read_csv(ROOT / 'data/prepared/D1b_facility_panel.csv').merge(static[['facility_id','company_id']], on='facility_id')
    raw = pd.read_csv(ROOT / 'data/raw/facility_panel.csv')
    observations = pd.read_csv(OUT / 'verified_primary_observations.csv')
    rows = []
    for year in [2022, 2023, 2024]:
        sites = raw[(raw.facility_id.str.startswith('LOTTE_')) & (raw.facility_id != 'LOTTE_TOTAL') & (raw.year == year)]
        assert len(sites) == 5
        for metric, field in [('scope1','emissions_s1'), ('scope2','emissions_s2')]:
            value = sites[field].sum()
            primary = observations[(observations.boundary == 'LOTTE_TOTAL') & (observations.year == year) & (observations.metric == metric)]
            model = panel[(panel.company_id == 'LOTTE') & (panel.year == year)][field].sum()
            rows.append(dict(company_id='LOTTE',year=year,metric=metric,raw_five_site_sum=value,
                             primary_company_table=primary.value.iloc[0] if len(primary) else np.nan,
                             prepared_cracker_sum=model,
                             raw_sum_minus_primary=value-primary.value.iloc[0] if len(primary) else np.nan,
                             comparison_scope='Whole domestic company/site observations versus modeled cracker estimates; different boundaries'))
    pd.DataFrame(rows).to_csv(OUT/'lotte_scope2_omission_trace.csv',index=False)
    assert all(r['prepared_cracker_sum'] == 0 for r in rows if r['metric'] == 'scope2')
    assert all(r['raw_five_site_sum'] > 0 for r in rows if r['metric'] == 'scope2')

    cfg = C.load(); fac, techs, _ = _prep_company(cfg, C.data_dir(cfg))
    years = np.arange(cfg.years.start, cfg.years.end + 1)
    prices = pd.read_csv(C.out_dir(cfg,'e1')/'price_paths_central.csv')
    px = _central_px(prices, COMPANY_REGION['LOTTE'], 'NZ15', years, cfg, None)
    fid = 'LOTTE_YEO_NCC';one = fac.loc[[fid]];quantity = one.production.iloc[0]
    zero = {**px,'gas':np.zeros_like(px['gas'])}
    i = int(np.flatnonzero(years == 2035)[0]);fuel = []
    for tk in techs[techs.sector == 'petchem'].itertuples():
        plan = pd.DataFrame([dict(company_id='LOTTE',facility_id=fid,tech_id=tk.tech_id,
                                 adopt_year=2030,op_year=2032,ppa_share=0.,epc=0,ccfd=0)])
        a=build_profile(plan,one,techs,px,years,cfg);b=build_profile(plan,one,techs,zero,years,cfg)
        # Same profile with gas price zero isolates purchases; capex, opex and all
        # other channels cancel. No argument about actual fuel efficiency is imposed.
        implied=(a.other_cost_k[i]-b.other_cost_k[i])*1000/px['gas'][i]/quantity*GJ_PER_T_GAS
        fuel.append(dict(tech_id=tk.tech_id,retrofit=int(tk.retrofit),baseline_purchased_gas_gj_per_t=one.gas_int_inc.iloc[0]*GJ_PER_T_GAS,
                         modeled_purchased_gas_gj_per_t=implied,added_hydrogen_kg_per_t=a.h2_kg[i]/quantity,
                         added_renewable_mwh_per_t=a.re_mwh[i]/quantity,incumbent_grid_mwh_per_t=a.grid_mwh[i]/quantity,
                         direct_emissions_tco2_per_t=a.emissions[i]/quantity,
                         inference='Fuel displacement and useful heat balance are not explicitly represented; cannot infer a verified engineering saving'))
    trace=pd.DataFrame(fuel);trace.to_csv(OUT/'actual_retrofit_energy_trace.csv',index=False)
    assert np.allclose(trace[trace.retrofit == 1].modeled_purchased_gas_gj_per_t,8.)
    index=pd.read_csv(C.out_dir(cfg,'e2')/'plan_index.csv');invalid=[]
    for r in index[(index.company_id.isin(['MCI','LOTTE'])) & index.is_disclosed].itertuples():
        plan=pd.read_csv(C.out_dir(cfg,'e2')/'plans'/f'plan_{r.plan_id}.csv')
        if r.company_id == 'MCI':
            wrong=((plan.facility_id == 'MCI_OSK_CR') & (plan.tech_id == 'petchem_h2fuel')).any()
            reason='Ammonia concept represented as purchased-hydrogen conversion' if wrong else 'Requires primary mapping review'
        else:
            wrong=True;reason='Announced CCU tech absent from D3; regional closures/JV boundary not represented; target-only comparator'
        invalid.append(dict(plan_id=r.plan_id,company_id=r.company_id,scenario=r.scenario,
                            valid_as_actual_disclosed_plan=not wrong,reason=reason))
    pd.DataFrame(invalid).to_csv(OUT/'disclosed_comparator_validity.csv',index=False)
    result={'lotte_years_with_scope2_default_zero':3,'lotte_site_scope2_cells_already_present':15,
            'technology_energy_traces':len(trace),'retrofits_preserving_all_incumbent_gas':int(trace.retrofit.sum()),
            'disclosed_comparators_reviewed':len(invalid),'invalid_actual_disclosed_comparators':sum(not r['valid_as_actual_disclosed_plan'] for r in invalid),
            'production_inputs_modified':False,
            'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'src/cap/plancost.py',ROOT/'scripts/prepare_raw.py',ROOT/'data/prepared/D1b_facility_panel.csv',ROOT/'data/prepared/D3_tech_options.csv']}}
    (OUT/'boundary_trace_manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
