"""Build an explicit conditional research case without replacing historical inputs.

This is a company-informed modeled asset portfolio. Estimated facility allocation
and commercial technology parameters remain assumptions, not plant observations.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

import numpy as np
import pandas as pd
import yaml

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'docs/research_cycles/2026-09-05'
DEST=ROOT/'tmp/research_case_v3/data'


def main():
    DEST.mkdir(parents=True,exist_ok=True)
    subprocess.run([sys.executable,str(ROOT/'scripts/prepare_raw.py'),'--out-dir',str(DEST)],check=True,cwd=ROOT)
    static=pd.read_csv(DEST/'D1a_facility_static.csv')
    panel=pd.read_csv(DEST/'D1b_facility_panel.csv')
    # Historical allocation cannot stand in for production before commissioning.
    excluded=static[static.commissioning_year>panel.year.max()].copy()
    static=static[~static.facility_id.isin(excluded.facility_id)].copy()
    panel=panel[panel.facility_id.isin(static.facility_id)].copy()
    excluded['reason']='Outside this legacy-asset portfolio: no valid pre-commission historical allocation; do not redistribute its assigned history'
    excluded.to_csv(DEST/'excluded_assets.csv',index=False)
    static['case_boundary_status']='modeled_legacy_asset_subset_not_verified_company_coverage'
    panel['observation_kind']='estimated_asset_allocation_or_route_model_not_facility_measurement'
    static.to_csv(DEST/'D1a_facility_static.csv',index=False)
    panel.to_csv(DEST/'D1b_facility_panel.csv',index=False)
    # Source phrases inform hypotheses only. These fractions do not claim a
    # measured naphtha heat/coproduct balance or an engineering confidence interval.
    tech=pd.read_csv(DEST/'D3_tech_options.csv')
    rows=[]
    for i,row in tech.iterrows():
        fractions=[float(row.retrofit)]*3
        if row.tech_id=='petchem_h2fuel': fractions[1]=.5
        if row.tech_id=='petchem_ecracker_hybrid': fractions[1]=.6
        for field,value in zip(['retained_coal_fraction','retained_gas_fraction','retained_grid_fraction'],fractions):
            tech.loc[i,field]=value
            rows.append(dict(tech_id=row.tech_id,field=field,value=value,
                structural_low=0.,structural_high=1.,evidence_status='explicit_model_assumption',
                interpretation='Purchased incumbent energy retained; not total process heat or feedstock',
                source_context=row.source_id,
                limit='Bounds are physical fraction domain, not verified statistical or engineering uncertainty bounds'))
    tech['retention_evidence_status']='assumption_not_verified_heat_and_coproduct_balance'
    tech.to_csv(DEST/'D3_tech_options.csv',index=False)
    pd.DataFrame(rows).to_csv(DEST/'energy_retention_assumptions.csv',index=False)
    # Source financial values in native units remain outside the normalized model
    # table. A single comparable KRW/2025 operating-company reference is populated.
    observed=pd.read_csv(AUDIT/'verified_financial_observations.csv')
    legacy=pd.read_csv(DEST/'D6_company_financials.csv')
    legacy.to_csv(DEST/'legacy_financials_unverified.csv',index=False)
    financial=[]
    for company in ['POSCO','NSC','LOTTE','MCI']:
        r=dict(company_id=company,year=2025,source_id='UNAVAILABLE_COMPARABLE_FINANCIAL_REFERENCE')
        for key in ['revenue','ebitda','capex_total','total_debt','net_debt','interest_expense','cash']:
            r[key]=np.nan
        r.update(amount_unit='unavailable',earnings_definition='unavailable',
                 boundary_status='unverified',verification_status='unverified')
        if company=='POSCO':
            g=observed[(observed.company_id==company)&(observed.fiscal_year==2025)].set_index('metric')
            for key,metric in [('revenue','revenue'),('ebitda','reported_ebitda'),('total_debt','interest_bearing_debt'),('net_debt','reported_net_debt'),('cash','cash')]:
                if metric in g.index:r[key]=float(g.loc[metric,'value_bn_native'])
            r.update(source_id='POSCO_OFFICIAL_IR_SEPARATE_2025',amount_unit='bn_KRW_2025',
                     earnings_definition='reported_ebitda',boundary_status='financing_entity_covers_modeled_assets',
                     verification_status='primary_verified')
        financial.append(r)
    pd.DataFrame(financial).to_csv(DEST/'D6_company_financials.csv',index=False)
    observed.to_csv(DEST/'verified_financial_native_units.csv',index=False)
    cfg=yaml.safe_load((ROOT/'config.yaml').read_text())
    cfg.update(data_dir=str(DEST),out_dir=str(ROOT/'tmp/research_case_v3/run'),
        years=dict(start=2027,end=2050),scenario_base_year=2025,
        capital_accounting='cash_v1',include_capital_renewals=True,terminal_value_rule='none',
        energy_balance_mode='explicit_retention',carbon_accounting_mode='gross_obligation_proxy',
        transition_loss_basis='incremental_cash',plan_selection_criterion='mean',
        financial_boundary_mode='strict',budget_mode='cumulative_hard',candidate_contracts='unhedged',
        information_cutoff='2026-09-05',monetary_basis='declared_KRW_2025_proxy_not_all_source_deflators_verified',
        case_scope='company_informed_modeled_legacy_asset_portfolios',
        scenario_evidence='EST_v0_illustrative_not_downloaded_GCAM_or_NGFS',
        support_scenarios=['none'])
    cfg['milp']=dict(cfg['milp'],frontier_points=6,retire_max_share=0,solver_time_limit_s=30)
    cfg['simulation']=dict(cfg['simulation'],n_sims=10000,n_sims_flex=1500)
    config_path=ROOT/'tmp/research_case_v3/config.yaml'
    config_path.write_text(yaml.safe_dump(cfg,sort_keys=False,allow_unicode=True))
    reconciled=panel.merge(static[['facility_id','company_id']],on='facility_id').groupby(['company_id','year'])[['production','emissions_s1','emissions_s2']].sum().reset_index()
    reconciled['interpretation']='Modeled portfolio totals; company emission observations have different boundaries and are not forced to match'
    reconciled.to_csv(DEST/'modeled_portfolio_totals.csv',index=False)
    files=list(DEST.glob('*.csv'))+[config_path,Path(__file__).resolve()]
    manifest=dict(facilities=len(static),facility_years=len(panel),excluded_future_assets=len(excluded),
                  retained_energy_assumptions=len(rows),start_year=2027,information_cutoff='2026-09-05',
                  actual_company_coverage_verified=False,all_price_base_years_verified=False,
                  heat_and_coproduct_balances_verified=False,
                  scope='Conditional methodology cases; verified company disclosures plus explicitly estimated asset and technology inputs',
                  source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    out=AUDIT/'research_case_v3';out.mkdir(exist_ok=True)
    (out/'input_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    for name in ['energy_retention_assumptions.csv','modeled_portfolio_totals.csv','excluded_assets.csv']:
        shutil.copyfile(DEST/name,out/name)
    print(json.dumps({k:v for k,v in manifest.items() if k!='source_sha256'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
