"""Preserve company production and procurement definitions before process mapping."""
from pathlib import Path
import json,hashlib,sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cap.production_bounds import additive_output_bounds
RAW=ROOT/'tmp/pdfs/company_process_bridge';OUT=ROOT/'data/research_v2/company_process_bridge'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    access=json.loads((RAW/'access.json').read_text());sources={Path(x['file']).stem:x for x in access}
    for r in access:assert hashlib.sha256((ROOT/r['file']).read_bytes()).hexdigest()==r['sha256']
    obs=[]
    def add(source,page,printed,company,period,entity,metric,value,unit,meaning,status='reported'):
        # The page was visually reviewed; retain a second machine-readable locator check.
        text=(RAW/(source+'.txt')).read_text().split('\f')[page-1]
        assert str(value) in text or f'{value:,}' in text or f'{value:.2f}' in text,(metric,value)
        r=sources[source]
        obs.append(dict(id=f'CPB{len(obs)+1:03}',company=company,period=period,entity=entity,metric=metric,value=value,unit=unit,
          meaning=meaning,status=status,source_url=r['url'],source_file=r['file'],source_sha256=r['sha256'],pdf_page=page,printed_page=printed,
          visually_reviewed=True,automatic_FIN_adoption=False))
    lotte='lotte_business_2024'
    for year,production,rate in [(2024,2848129,81.),(2023,3095864,87.8),(2022,3000011,85.5)]:
        for metric,value,unit in [('NC_capacity',3521000,'t/year'),('NC_production',production,'t'),('NC_utilization',rate,'%')]:
            add(lotte,34,'31','LOTTE',f'CY{year}','parent_basic_chemicals',metric,value,unit,'Native NC aggregate; ethylene-only definition not established')
    for metric,value in [('ethylene_capacity',2330),('propylene_capacity',1191)]:
        add(lotte,64,'61','LOTTE','CY2023','domestic_parent_works',metric,value,'thousand_t/year','Source column2023; carrying capacity to2024 is an additional assumption')
    for year,purchase,share,subtotal in [(2024,4786068,46.2,10362098),(2023,5549723,55.3,10035545)]:
        add(lotte,32,'29','LOTTE',f'CY{year}','parent_plus_LC_TITAN','naphtha_purchase',purchase,'million_KRW','Combined purchaser scope; no split quantity or actual unit purchase price')
        add(lotte,32,'29','LOTTE',f'CY{year}','basic_chemicals_purchase_scope','naphtha_purchase_share',share,'%','Denominator basic-chemicals purchases includes other listed entities')
        add(lotte,32,'29','LOTTE',f'CY{year}','basic_chemicals_purchase_scope','raw_material_purchase_total',subtotal,'million_KRW','Includes parent basic chemicals, LC TITAN, LOTTE INEOS and others per footnote')
    for year,price in [(2024,675),(2023,649),(2022,785)]:
        add(lotte,32,'29','LOTTE',f'CY{year}','international_market_reference','naphtha_price',price,'USD/MT','Footnote: international price basis, not company realized procurement price')
    for year,values in [(2024,[33.85,39.64,34.30,31.62]),(2023,[34.55,40.51,34.99,32.03])]:
        for metric,value,entity in zip(['pig_iron','crude_steel_consolidated','crude_steel_nonconsolidated','steel_products_shipped'],values,
               ['including_Hokkai_Iron_and_Coke','consolidated','nonconsolidated','issuer_shipment_table_scope']):
            add('nsc_results_fy2024',30,'supplement2','NSC',f'FY{year}',entity,metric,value,'million_t','Different products/entities; ratios are not automatically process conversion yields')
    add('mci_outage_20240821',1,'1','MCI','FY2024_first_half','OPC_outage_financial_effect','announced_impact_estimate',7,'billion_JPY','2024-08-21 forecast; not realized transition or abatement cost','forecast')
    pd.DataFrame(obs).to_csv(OUT/'native_observations.csv',index=False)
    comparisons=[]
    for year,q,reported in [(2024,2848129,81.),(2023,3095864,87.8),(2022,3000011,85.5)]:
        derived=q/3521000*100
        comparisons.append(dict(year=year,reported_utilization_pct=reported,simple_output_capacity_pct=derived,
                                difference_pp=reported-derived,rounds_to_reported=round(derived,1)==reported,
                                interpretation='Preserve source reported ratio; weighting/operating-capacity definition unresolved'))
    pd.DataFrame(comparisons).to_csv(OUT/'utilization_reconciliation.csv',index=False)
    bounds=[]
    for gamma in np.linspace(1,1.1,21):
        limits={'ethylene':2330000*gamma,'propylene':1191000*gamma}
        lo,hi=additive_output_bounds(2848129,limits)['ethylene']
        bounds.append(dict(assumed_capacity_multiplier=float(gamma),ethylene_lower_t=lo,ethylene_upper_t=hi,
                          lower_share_of_2023_nameplate=lo/2330000,upper_share_of_2023_nameplate=hi/2330000,
                          status='conditional_arithmetic_envelope_not_probability',
                          assumptions='NC=ethylene+propylene only;2023 capacities carried to2024;effective ceiling=gamma*nameplate;no other joint-yield constraints'))
    df=pd.DataFrame(bounds);df.to_csv(OUT/'conditional_output_bounds.csv',index=False)
    events=[dict(date='2024-08-21',company='MCI',event='OPC outage response',statement='Issuer announced Ichihara transfers and external procurement;October restart was a forecast',source_url=sources['mci_outage_20240821']['url'],adoption='Candidate mechanism evidence only; quantities, premiums and probabilities unobserved'),
            dict(date='2024-10-02',company='MCI',event='OPC restart announcement',statement='Issuer reports restart on2024-09-30',source_url=sources['mci_restart_20241002']['url'],adoption='Observed event timing; not a calibrated transition-risk shock')]
    (OUT/'operational_events.json').write_text(json.dumps(events,ensure_ascii=False,indent=2)+'\n')
    decisions=[['LOTTE','NC_production','Keep NC aggregate; ethylene output unresolved'],['LOTTE','NC_utilization','Reported percentage is not recovered by displayed aggregate output/capacity; do not substitute ethylene utilization'],['LOTTE','naphtha_price','International benchmark; separately map basis/FX/freight/contract to procurement'],['LOTTE','naphtha_purchase','Parent plus TITAN amount does not match domestic parent production denominator'],['NSC','pig_iron_to_crude','Hokkai-included pig iron and nonconsolidated crude steel cannot define a technical yield'],['MCI','alternative_supply','Introduce procurement/transfer/inventory limits and receipts/payments before evaluating flexibility']]
    pd.DataFrame(decisions,columns=['company','field','decision']).to_csv(OUT/'mapping_decisions.csv',index=False)
    font=font_manager.FontProperties(fname=str(ROOT/'tmp/pdfs/methodology/Body.ttf')).get_name()
    font_manager.fontManager.addfont(str(ROOT/'tmp/pdfs/methodology/Body.ttf'));plt.rcParams.update({'font.family':font,'axes.unicode_minus':False,'font.size':10})
    fig,axes=plt.subplots(1,2,figsize=(11,4.3))
    a=axes[0];xx=np.arange(3);diff=[x['difference_pp'] for x in comparisons]
    a.barh(xx,diff,color=['#286782' if v>=0 else '#b67540' for v in diff],height=.5)
    a.axvline(0,color='#888',linewidth=.8);a.set_yticks(xx,[str(x['year']) for x in comparisons]);a.invert_yaxis()
    a.set_xlim(-.4,.4);a.set_xlabel('공시 가동률 - 생산실적/표시 생산능력 (%p)');a.set_title('작은 차이도 정의 확인이 필요하다')
    for i,v in enumerate(diff):a.text(v+(.015 if v>=0 else -.015),i,f'{v:+.3f}',va='center',ha='left' if v>=0 else 'right',fontsize=9)
    a=axes[1];a.fill_between(df.assumed_capacity_multiplier,df.ethylene_lower_t/1e6,df.ethylene_upper_t/1e6,color='#bdd8e3',alpha=.7)
    a.plot(df.assumed_capacity_multiplier,df.ethylene_lower_t/1e6,color='#286782');a.plot(df.assumed_capacity_multiplier,df.ethylene_upper_t/1e6,color='#286782')
    a.set_xlabel('가정한 유효 생산 상한 / 2023 표시 생산능력');a.set_ylabel('에틸렌 생산량 조건부 범위 · 백만 t');a.set_title('추가 가정에 따른 조건부 범위')
    a.text(.03,.03,'NC = 에틸렌 + 프로필렌 가정\n확률구간·실측 생산량 아님',transform=a.transAxes,fontsize=8)
    fig.tight_layout();fig.savefig(OUT/'production_boundary_assumptions.png',dpi=180);plt.close(fig)
    files=[p for p in OUT.iterdir() if p.name!='manifest.json']
    manifest=dict(native_observations=len(obs),source_PDFs=4,source_pages_visually_reviewed=6,source_pages={'lotte_business_2024':[32,34,64],'nsc_results_fy2024':[30],'mci_outage_20240821':[1],'mci_restart_20241002':[1]},
      capacity_sum_identity=2330000+1191000==3521000,NC_composition_verified=False,corporate_FIN_adoption=False,conditional_output_bound_rows=len(bounds),
      input_sha256={r['file']:r['sha256'] for r in access},artifact_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
      code_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'src/cap/production_bounds.py']})
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print({k:v for k,v in manifest.items() if not k.endswith('sha256')})


if __name__=='__main__':main()
