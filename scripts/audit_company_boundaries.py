"""Visually reviewed corporate and works observations, kept outside FIN adoption."""
from pathlib import Path
import csv,hashlib,json,sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt,font_manager
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cap.company_boundary import coverage_requirement,process_intensity
SOURCES={
 'POSCO':('tmp/pdfs/tcar_steel_sources/posco_factbook_2024.pdf','https://sustainability.posco.co.kr/assets/file/2024_POSCO_ESG_Factbook.pdf','CY2024','2024-01-01','2024-12-31'),
 'NSC':('tmp/pdfs/tcar_steel_sources/nsc_databook_2025.pdf','https://www.nipponsteel.com/en/ir/library/pdf/nsc_en_ir_2025_databook_print.pdf','FY2024','2024-04-01','2025-03-31'),
 'LOTTE':('tmp/pdfs/tcar_petchem_sources/lotte_esg_2025.pdf','https://www.lottechem.com/pdfRead.do?fileId=FILE_260803112356995','CY2024','2024-01-01','2024-12-31'),
 'MCI':('tmp/pdfs/tcar_petchem_sources/mci_esg_2025_part6.pdf','https://jp.mitsuichemicals.com/content/dam/mitsuichemicals/sites/mci/documents/sustainability/report/esg2025web_e_part06.pdf.coredownload.pdf','FY2024','2024-04-01','2025-03-31')}
# company, entity, PDF page, printed page, measure, original numeric cell, original unit.
OBS=[
 ('POSCO','domestic_company',4,'4','crude_steel',35048,'thousand_t'),
 ('POSCO','domestic_company',4,'4','bof_steel',33893,'thousand_t'),
 ('POSCO','domestic_company',4,'4','eaf_steel',1154,'thousand_t'),
 ('POSCO','domestic_company',5,'5','ghg_total',71065170,'tCO2e'),
 ('POSCO','domestic_company',5,'5','scope1',69665353,'tCO2e'),
 ('POSCO','domestic_company',5,'5','scope2',1399825,'tCO2e'),
 ('POSCO','domestic_company',6,'6','electricity_reported_energy',10963428,'reported_GJ'),
 ('NSC','nonconsolidated',19,'18','crude_steel',3430,'ten_thousand_t'),
 ('NSC','nonconsolidated',23,'22','ghg_total',79013,'ktCO2e'),
 ('NSC','nonconsolidated',23,'22','energy_CO2',75349,'ktCO2e'),
 ('NSC','nonconsolidated',23,'22','nonenergy_CO2',3389,'ktCO2e'),
 ('NSC','nonconsolidated',23,'22','CH4',114,'ktCO2e'),
 ('NSC','nonconsolidated',23,'22','N2O',139,'ktCO2e'),
 ('LOTTE','parent',117,'117','ghg_total',5902878,'tCO2e'),
 ('LOTTE','parent',117,'117','scope1',3808439,'tCO2e'),
 ('LOTTE','parent',117,'117','scope2',2094447,'tCO2e'),
 ('LOTTE','yeosu_basic_works',117,'117','scope1',1886740,'tCO2e'),
 ('LOTTE','yeosu_basic_works',117,'117','scope2',900833,'tCO2e'),
 ('LOTTE','daesan_works',117,'117','scope1',1534019,'tCO2e'),
 ('LOTTE','daesan_works',117,'117','scope2',650497,'tCO2e'),
 ('MCI','parent',6,'284','ghg_total',3869,'ktCO2e'),
 ('MCI','parent',6,'284','scope1',3383,'ktCO2e'),
 ('MCI','parent',6,'284','scope2',486,'ktCO2e'),
 ('MCI','parent',6,'284','energy',64.6,'PJ'),
 ('MCI','parent',6,'284','products_shipped',2069,'thousand_t_mixed_products'),
 ('MCI','ichihara_works',7,'285','ghg_total',1421,'ktCO2e'),
 ('MCI','ichihara_works',7,'285','scope1',1379,'ktCO2e'),
 ('MCI','ichihara_works',7,'285','scope2',42,'ktCO2e'),
 ('MCI','ichihara_works',7,'285','energy',26.5,'PJ'),
 ('MCI','ichihara_works',7,'285','products_shipped',1506,'thousand_t_mixed_products'),
 ('MCI','osaka_works',7,'285','ghg_total',1451,'ktCO2e'),
 ('MCI','osaka_works',7,'285','scope1',1305,'ktCO2e'),
 ('MCI','osaka_works',7,'285','scope2',146,'ktCO2e'),
 ('MCI','osaka_works',7,'285','energy',23.8,'PJ'),
 ('MCI','osaka_works',7,'285','products_shipped',84,'thousand_t_mixed_products')]

def main():
 out=ROOT/'data/research_v2/company_boundary';out.mkdir(parents=True,exist_ok=True)
 rows=[]
 for i,(company,entity,page,printed,item,value,unit) in enumerate(OBS,1):
  local,url,period,start,end=SOURCES[company]
  rows.append(dict(observation_id=f'CB{i:03}',company=company,entity=entity,period=period,start_date=start,end_date=end,item=item,value=value,unit=unit,pdf_page=page,printed_page=printed,source_url=url,source_sha256=hashlib.sha256((ROOT/local).read_bytes()).hexdigest(),visual_review=True,automatic_FIN_adoption=False))
 df=pd.DataFrame(rows);df.to_csv(out/'observations.csv',index=False)
 def get(c,e,item):return float(df[(df.company==c)&(df.entity==e)&(df.item==item)].value.iloc[0])
 reconciliation=[]
 for c,e in [('POSCO','domestic_company'),('LOTTE','parent'),('MCI','parent')]:
  difference=get(c,e,'ghg_total')-get(c,e,'scope1')-get(c,e,'scope2')
  reconciliation.append(dict(company=c,item='reported total minus displayed Scope1+2',difference=difference,unit='ktCO2e' if c=='MCI' else 'tCO2e',interpretation='preserve reported total; source notes site truncation' if difference else 'displayed components reconcile'))
 reconciliation.append(dict(company='NSC',item='reported GHG minus four displayed gas categories',difference=get('NSC','nonconsolidated','ghg_total')-sum(get('NSC','nonconsolidated',k) for k in ['energy_CO2','nonenergy_CO2','CH4','N2O']),unit='ktCO2e',interpretation='unreconciled22kt; do not force into a process or rounding bucket'))
 reconciliation.append(dict(company='POSCO',item='reported crude steel minus BOF and EAF components',difference=get('POSCO','domestic_company','crude_steel')-get('POSCO','domestic_company','bof_steel')-get('POSCO','domestic_company','eaf_steel'),unit='thousand_t',interpretation='compatible with displayed precision; preserve independently reported quantities'))
 pd.DataFrame(reconciliation).to_csv(out/'reconciliation.csv',index=False)
 coverage=[]
 for company,entity,works,scale in [('LOTTE','parent',['yeosu_basic_works','daesan_works'],1.),('MCI','parent',['ichihara_works','osaka_works'],1000.)]:
  total=get(company,entity,'ghg_total')*scale
  covered=sum((get(company,w,'scope1')+get(company,w,'scope2'))*scale for w in works)
  r=coverage_requirement(total,covered,covered_residual_fraction=0,target_fraction=0)
  coverage.append(dict(company=company,period=SOURCES[company][2],total_tCO2e=total,selected_whole_works_tCO2e=covered,outside_tCO2e=r['outside_baseline'],outside_percent=100*r['outside_baseline']/total,interpretation='Only selected whole works hypothetically reach zero; all outside activity unchanged. Not NCC-only abatement or a company prediction.'))
 pd.DataFrame(coverage).to_csv(out/'selected_works_coverage.csv',index=False)
 gates=[]
 for c in SOURCES:
  gates.append(dict(company=c,period=SOURCES[c][2],company_observation_available=True,process_output_matched=False,purchased_energy_boundary_matched=False,incumbent_capital_matched=False,remaining_emissions_costed=False,ready_for_new_corporate_frontier=False,
   reason={'POSCO':'Crude steel versus furnace hot metal; report-specific electricity conversion unknown; furnace allocation and residual scope needed',
   'NSC':'Purchased coke/oxygen upstream boundary differs from conventional Scope1+2; hot-metal and crude-steel basis must match;22kt component gap unresolved',
   'LOTTE':'Whole works versus NCC; nameplate versus actual ethylene output; downstream/shared utilities and residual sites',
   'MCI':'Mixed-products shipments versus ethylene production; parent works versus legacy cracker legal entity; shared energy and residual sites'}[c]))
 pd.DataFrame(gates).to_csv(out/'company_mapping_status.csv',index=False)
 sensitivity=[]
 for fraction in [.25,.5,.75]:
  for u in np.linspace(.5,1,51):sensitivity.append(dict(utilization=u,process_energy_fraction=fraction,normalized_intensity=process_intensity(1,1,utilization=float(u),process_energy_fraction=fraction)))
 pd.DataFrame(sensitivity).to_csv(out/'denominator_sensitivity.csv',index=False)
 font=ROOT/'tmp/pdfs/methodology/Heading.ttf';font_manager.fontManager.addfont(str(font));plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),'font.size':10,'axes.unicode_minus':False})
 fig,ax=plt.subplots(1,2,figsize=(10,4),layout='constrained')
 for f0 in [.25,.5,.75]:
  d=[r for r in sensitivity if r['process_energy_fraction']==f0];ax[0].plot([r['utilization'] for r in d],[r['normalized_intensity'] for r in d],label=f'공정 에너지 비중 λ={f0:.2f}')
 ax[0].axhline(1,color='#777777',linestyle='--');ax[0].set(xlabel='실제 생산량 / 생산능력 (u, 가정)',ylabel='공정 원단위 / (사업장 에너지 ÷ 생산능력)',title='분모가 다르면 상한 관계도 달라진다');ax[0].legend(fontsize=8)
 for i,r in enumerate(coverage):
  rest=r['outside_percent'];ax[1].barh(i,100-rest,color='#276887');ax[1].barh(i,rest,left=100-rest,color='#b67542');ax[1].text(100-rest/2,i,f'{rest:.1f}%',ha='center',va='center',color='white')
 ax[1].set(yticks=[0,1],yticklabels=['LOTTE CY2024','MCI FY2024'],xlim=(0,100),xlabel='공시 회사 총배출 대비 비중 (%)',title='선택한 전체 사업장 밖의 배출도 남는다')
 ax[1].text(.01,-.27,'파랑: 선택한 두 사업장 전체 / 갈색: 나머지 범위\n크래커만의 배출 비중 또는 위험 순위가 아님',transform=ax[1].transAxes,fontsize=9)
 fig.savefig(out/'company_boundary_assumptions.png',dpi=180);plt.close(fig)
 corrections=[dict(item='POSCO purchased electricity intensity',old_value=.0869,new_value=None,reason='Source accounting conversion coefficient not specified;3.6 inversion withdrawn'),dict(item='LOTTE energy per ethylene capacity',old_claim='upper bound on NCC intensity',new_claim='capacity-normalized whole-site statistic',reason='Actual intensity equals statistic times process share/utilization; no unconditional ordering'),dict(item='NSC production locator',old='page19 ambiguous; line0',new='PDFpage19/printedpage18/textline1223',reason='Visually verified source table')]
 (out/'corrections.json').write_text(json.dumps(corrections,indent=2)+'\n')
 inputs=[ROOT/p[0] for p in SOURCES.values()]+[Path(__file__),ROOT/'src/cap/company_boundary.py',ROOT/'data/research_v2/evidence/company_energy_intensities.csv']
 manifest=dict(observations=len(df),companies=4,source_PDFs=4,source_pages_visually_reviewed={'POSCO':[4,5,6],'NSC':[19,23],'LOTTE':[117],'MCI':[2,6,7]},periods_not_identical=True,source_checks=len(reconciliation),unresolved_NSC_gap_kt=22,corporate_FIN_adoption=False,
  legacy_reference_workbook_status='Historical TCaR_research_v2_registers.xlsx contains superseded electricity/capacity interpretations; use corrected CSV and this audit. Current joint_control_v3 does not consume these company ratios.',
  input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},artifact_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.name!='manifest.json'})
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'observations':len(df),'coverage':coverage,'reconciliation':reconciliation}))

if __name__=='__main__':main()
