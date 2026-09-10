"""Read selected primary steel facts and audit the existing FIN case boundary.

This creates evidence and validation tables; it does not rescale company emissions
into unmatched facilities or pretend a demonstration is a full conversion.
"""
from pathlib import Path
from functools import lru_cache
import hashlib,json,re,subprocess,sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/research_cycles/2026-09-05/steel_data'
REG=ROOT/'docs/research_cycles/2026-09-05/steel_source_access_audit.json'
SOURCES={r['source_id']:r for r in json.loads(REG.read_text()) if r['status']=='downloaded'}
OBS=[]

@lru_cache(None)
def page(sid,number):
    record=SOURCES[sid];p=ROOT/record['local_path']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256'],sid
    return subprocess.check_output(['/opt/homebrew/bin/pdftotext','-f',str(number),'-l',str(number),'-layout',str(p),'-'],text=True)


def add(sid,pageno,company,entity,metric,year,value,unit,boundary,status='reported',note=''):
    source=SOURCES[sid]
    OBS.append(dict(company_id=company,entity=entity,metric=metric,year=year,value=value,unit=unit,
                    boundary=boundary,value_status=status,note=note,source_id=sid,
                    source_url=source['url'],source_pdf_page=pageno,source_sha256=source['sha256']))


def row_values(sid,pageno,label,n):
    matches=[]
    for line in page(sid,pageno).splitlines():
        if label not in line:continue
        if label in ('고로/전로 ','전기로 ') and '천ton' not in line:continue
        if sid=='POSCO_FACTBOOK_2024_PRIMARY' and pageno==5 and 'tCO2e' not in line:continue
        line=re.sub(r'\*\d','',line)
        values=re.findall(r'(?<![\w.])\d[\d,]*(?:\.\d+)?',line)
        if len(values)>=n:matches.append(values[-n:])
    assert len(matches)==1,(sid,pageno,label,matches)
    return [float(x.replace(',','')) for x in matches[0]]


def build_observations():
    sid='POSCO_FACTBOOK_2024_PRIMARY'
    specs=[(4,'조강 생산량','crude_steel_production',1000,'t_crude_steel'),
           (4,'고로/전로 ','bof_crude_steel_production',1000,'t_crude_steel'),
           (4,'전기로 ','eaf_crude_steel_production',1000,'t_crude_steel'),
           (5,'직/간접 배출량(Scope 1&2)','scope1_plus_scope2',1,'tCO2e'),
           (5,'직접 배출(Scope 1)','scope1',1,'tCO2e'),
           (5,'간접 배출(Scope 2)','scope2',1,'tCO2e')]
    for p,label,metric,scale,unit in specs:
        vals=row_values(sid,p,label,3)
        for y,v in zip((2022,2023,2024),vals):add(sid,p,'POSCO','POSCO_DOMESTIC',metric,y,v*scale,unit,'POSCO domestic operations')
    sid='NSC_DATABOOK_2025_PRIMARY'
    for label,metric in [('Non-Consol.*','crude_steel_production'),('  Consol.','consolidated_crude_steel_production')]:
        vals=row_values(sid,19,label,10)[-3:]
        for y,v in zip((2022,2023,2024),vals):add(sid,19,'NSC','NSC_PRODUCTION',metric,y,v*10000,'t_crude_steel','nonconsolidated' if 'Non-' in label else 'consolidated',note='Fiscal year ends March 31 of following calendar year')
    # The extracted first line includes the Scope digit before the five values.
    for label,metric in [('Scope 1','scope1'),('Scope 2','scope2')]:
        vals=row_values(sid,24,label,5)[-3:]
        for y,v in zip((2022,2023,2024),vals):add(sid,24,'NSC','NSC_CNAP_GHG',metric,y,v*1000,'tCO2','Nippon Steel plus ten EAF subsidiaries; IPP excluded','preliminary' if y==2024 else 'reported_revised',note='FY2024 purchased-power coefficients assumed equal FY2023; not parent-only emissions')
    # Typed equipment map checked against the two original table pages. Values
    # are contents and relining dates, not observed annual hot-metal capacities.
    equipment=[('NSC_MUR_BF2',3014,2020,14),('NSC_KAS_BF1',5370,2004,14),
       ('NSC_KIM_BF2',4500,2012,14),('NSC_KIM_BF4',5555,2003,14),
       ('NSC_NGO_BF1',5443,2007,14),('NSC_NGO_BF3',4425,2022,14),
       ('NSC_WAK_BF2',3700,2019,14),('NSC_TOB_BF4',5000,2014,15),
       ('NSC_OIT_BF1',5775,2009,15),('NSC_OIT_BF2',5775,2004,15)]
    for entity,volume,year,p in equipment:
        text=page(sid,p);assert f'{volume:,}' in text and str(year) in text
        add(sid,p,'NSC',entity,'blast_furnace_inner_volume',2025,volume,'m3','equipment as of 2025-07-01')
        add(sid,p,'NSC',entity,'last_reline_year',2025,year,'year','equipment as of 2025-07-01')
    works=[('MUR',1.24,14),('KAS',6.09,14),('KIM',6.60,14),('NGO',5.47,14),('WAK',2.18,14),
           ('OSAKA',.03,14),('HIR',.61,15),('HIKARI',.41,15),('YAMAGUCHI',.20,15),('TOB',3.70,15),('OIT',8.35,15)]
    for entity,prod,p in works:
        text=page(sid,p)
        assert ('30,000 tons' if entity=='OSAKA' else f'{prod:g} million tons') in text or f'{prod:.2f} million tons' in text
        add(sid,p,'NSC',entity,'works_crude_steel_production',2024,prod*1e6,'t_crude_steel','reported works/area; reconciliation to parent total unresolved')
    sid='NSC_EAF_20250530_PRIMARY';text=page(sid,1)
    for entity,capex,grant,capacity,fy in [('NSC_YAW_EAF1',6302,1799,2_000_000,2029),('NSC_HIR_EAF2',1400,428,500_000,2029),('NSC_YAM_EAF',985,287,400_000,2028)]:
        assert f'{capex:,}' in text and f'{grant:,}' in text
        add(sid,1,'NSC',entity,'project_capex',2025,capex*.1,'bn_JPY_nominal','gross project including ancillary and related equipment','announced')
        add(sid,1,'NSC',entity,'government_support_ceiling',2025,grant*.1,'bn_JPY_nominal','project-specific upper limit, not cash received','announced_ceiling')
        add(sid,1,'NSC',entity,'new_or_restarted_capacity',2025,capacity,'t_steel_per_year','incremental project capacity','announced')
        add(sid,1,'NSC',entity,'operation_fiscal_year',2025,fy,'Japanese_FY','second half: October of stated FY to March of following year','announced')
    return pd.DataFrame(OBS)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obs=build_observations()
    assert len(obs)==73 and not obs.duplicated(['company_id','entity','metric','year']).any()
    assert obs[(obs.company_id=='NSC')&(obs.metric=='scope1')&(obs.year==2024)].value.item()==63_672_000
    obs.to_csv(OUT/'verified_steel_observations.csv',index=False)
    raw=pd.read_csv(ROOT/'data/raw/facility_static.csv');rawpanel=pd.read_csv(ROOT/'data/raw/facility_panel.csv')
    static=pd.read_csv(ROOT/'data/prepared/D1a_facility_static.csv');panel=pd.read_csv(ROOT/'data/prepared/D1b_facility_panel.csv')
    st=static[static.sector=='steel'];joined=panel.merge(st[['facility_id','company_id','commissioning_year','unit_type']],on='facility_id')
    temporal=joined[(joined.year<joined.commissioning_year)&(joined.production>0)]
    temporal.to_csv(OUT/'precommissioning_allocations.csv',index=False)
    excluded=raw[raw.company_id.isin(['POSCO','NSC'])&~raw.facility_id.isin(st.facility_id)].copy()
    excluded.to_csv(OUT/'excluded_raw_steel_facilities.csv',index=False)
    comparisons=[]
    for r in obs[obs.metric.isin(['crude_steel_production','scope1','scope2'])].itertuples():
        field={'crude_steel_production':'production','scope1':'emissions_s1','scope2':'emissions_s2'}[r.metric]
        rr=rawpanel[(rawpanel.facility_id==r.company_id+'_TOTAL')&(rawpanel.year==r.year)]
        legacy=float(rr[field].iloc[0]);allocated=float(joined[(joined.company_id==r.company_id)&(joined.year==r.year)][field].sum())
        comparisons.append(dict(company_id=r.company_id,year=r.year,metric=r.metric,primary_value=r.value,raw_value=legacy,prepared_sum=allocated,
                                raw_difference=legacy-r.value,prepared_difference=allocated-r.value,unit=r.unit,
                                matched_numeric=bool(np.isclose(legacy,r.value,rtol=0,atol=.01)),
                                facility_boundary_verified=False,reason='Allocated company total; '+r.boundary))
    pd.DataFrame(comparisons).to_csv(OUT/'company_total_reconciliation.csv',index=False)
    capacities=[]
    for r in st.itertuples():
        inferred='추정' in r.capacity_unit
        volume=re.search(r'([\d,]+)\s*m³',r.unit_name)
        v=float(volume.group(1).replace(',','')) if volume else None
        if inferred:assert np.isclose(r.capacity,v*5_480_000/6000)
        capacities.append(dict(facility_id=r.facility_id,capacity=r.capacity,capacity_unit=r.capacity_unit,
                               value_type='estimated_single_anchor_scaling' if inferred else 'reported_input_pending_full_scope_audit',
                               volume_m3=v,conversion_t_per_m3_year=5_480_000/6000 if inferred else None,
                               source_id=r.source_id,observation_equivalent=False if inferred else None))
    pd.DataFrame(capacities).to_csv(OUT/'capacity_derivation_audit.csv',index=False)
    # Exact current evidence classification, preserving the previous inventory.
    from build_parameter_inventory import field_provenance
    inventory_path=ROOT/'docs/parameter_inventory.csv';inventory=pd.read_csv(inventory_path).fillna('')
    original=OUT/'parameter_inventory_before_field_audit.csv'
    if not original.exists():inventory.to_csv(original,index=False)
    before=pd.read_csv(original).fillna('');changes=[];byid=static.set_index('facility_id')
    for i,r in inventory.iterrows():
        if r.model=='FIN' and r.group=='facility':
            row=byid.loc[r.entity];tier,source=field_provenance(row,'FIN','facility',r.field)
            old=before.loc[before.param_id==r.param_id].iloc[0]
            if old.evidence_tier!=tier:changes.append(dict(param_id=r.param_id,old_tier=old.evidence_tier,new_tier=tier,source_id=source))
            inventory.loc[i,['evidence_tier','source_id']]=[tier,source]
            if r.field=='capacity':inventory.loc[i,'unit']=row.capacity_unit
    inventory['needs_range']=(inventory.evidence_tier=='T5')&((inventory.value_low=='')|(inventory.value_high==''))
    inventory.to_csv(inventory_path,index=False);pd.DataFrame(changes).to_csv(OUT/'parameter_tier_corrections.csv',index=False)
    mappings=[
      ['POSCO_GWY_EAF1','steel_eaf','Completed EAF June 2026; construction began February 2024','existing asset at current information cutoff; excluded by NONE applies_to rule','POSCO_EAF_20260622_PRIMARY'],
      ['POSCO_UNASSIGNED_HYREX','steel_h2dri','300000 t/year HyREX demonstration, commercialization validation target2030','demo scale and fluidized-bed route not mapped; no full-furnace commercial commitment','POSCO_EAF_20260622_PRIMARY'],
      ['NSC_YAW_EAF1','steel_eaf','New2Mt/year EAF; second-half FY2029','not in prepared D1a; not represented in disclosed comparator','NSC_EAF_20250530_PRIMARY'],
      ['NSC_HIR_EAF2','steel_eaf','Additional0.5Mt/year EAF; second-half FY2029','not in prepared D1a; not represented in disclosed comparator','NSC_EAF_20250530_PRIMARY'],
      ['NSC_KIM_BF2','steel_h2dri','Hydrogen-rich gas injection in operating BF; demonstration target January2026','WRONG_ROUTE: current comparator forces full H2-DRI operational2034','NSC_H2INJ_20230209_PRIMARY']]
    pd.DataFrame(mappings,columns=['facility_id','legacy_tech_id','verified_disclosure','mapping_assessment','source_id']).to_csv(OUT/'disclosed_plan_mapping_audit.csv',index=False)
    plans=pd.read_csv(ROOT/'out/e2/plan_index.csv');forced=[]
    for r in plans[(plans.company_id=='NSC')&plans.is_disclosed].itertuples():
        p=pd.read_csv(ROOT/f'out/e2/plans/plan_{r.plan_id}.csv');f=p[(p.facility_id=='NSC_KIM_BF2')&(p.tech_id=='steel_h2dri')]
        for x in f.itertuples():forced.append(dict(plan_id=r.plan_id,scenario=r.scenario,facility_id=x.facility_id,adopt_year=x.adopt_year,operation_year=x.op_year,source_demonstration_target_year=2026,comparator_valid=False))
    pd.DataFrame(forced).to_csv(OUT/'invalid_disclosed_comparators.csv',index=False)
    summary=dict(primary_numeric_observations=len(obs),steel_prepared_facilities=len(st),estimated_steel_capacities=sum(x['value_type'].startswith('estimated') for x in capacities),
      excluded_raw_steel_facilities=len(excluded),precommissioning_positive_rows=len(temporal),
      precommissioning_production_t=float(temporal.production.sum()),company_total_cells_compared=len(comparisons),
      company_total_cells_matching=sum(x['matched_numeric'] for x in comparisons),field_evidence_tiers_corrected=len(changes),
      current_tier_counts=inventory.evidence_tier.value_counts().to_dict(),t5_without_both_bounds=int(inventory.needs_range.sum()),
      nsc_reported_works_production_t=float(obs[obs.metric=='works_crude_steel_production'].value.sum()),
      nsc_parent_production_t=34_300_000,nsc_production_boundary_reconciled=False,
      invalid_nsc_disclosed_comparators=len(forced),case_claim_release_ready=False,
      production_model_changed=False,inventory_provenance_corrected=True)
    summary['source_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [REG,Path(__file__),ROOT/'data/prepared/D1a_facility_static.csv',ROOT/'data/prepared/D1b_facility_panel.csv',ROOT/'data/prepared/D7_disclosed_plan.csv']}
    (OUT/'manifest.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='source_sha256'},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
