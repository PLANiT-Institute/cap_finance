"""Audit saved boundary arithmetic and its explicitly selected manuscript values."""
from pathlib import Path
import json,hashlib,re,sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def main():
 out=ROOT/'data/research_v2/company_boundary';m=json.loads((out/'manifest.json').read_text())
 for p,h in (m['input_sha256']|m['artifact_sha256']).items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 df=pd.read_csv(out/'observations.csv');coverage=pd.read_csv(out/'selected_works_coverage.csv');paper=(ROOT/'paper/methodology/TCaR_METHOD_KO.md').read_text()
 assert len(df)==35 and not df.duplicated(['company','entity','item','period']).any()
 values=df.set_index(['company','entity','item']).value.to_dict()
 totals={'POSCO':'domestic_company','NSC':'nonconsolidated','LOTTE':'parent','MCI':'parent'}
 printed_table=0
 for c,e in totals.items():
  assert f'| {int(values[c,e,"ghg_total"]):,} |' in paper;printed_table+=1
 cases=[('LOTTE','parent',['yeosu_basic_works','daesan_works'],1),('MCI','parent',['ichihara_works','osaka_works'],1000)]
 for c,e,works,scale in cases:
  v=coverage[coverage.company==c].iloc[0];total=values[c,e,'ghg_total']*scale
  covered=sum((values[c,w,'scope1']+values[c,w,'scope2'])*scale for w in works)
  np.testing.assert_allclose([total,covered,total-covered,100*(total-covered)/total],[v.total_tCO2e,v.selected_whole_works_tCO2e,v.outside_tCO2e,v.outside_percent],rtol=1e-12)
  assert f'{int(covered/scale):,}' in paper and f'{int((total-covered)/scale):,}' in paper and f'{v.outside_percent:.1f}%' in paper
 assert values['POSCO','domestic_company','electricity_reported_energy']==10963428
 assert '10,963,428GJ' in paper
 gap=values['NSC','nonconsolidated','ghg_total']-sum(values['NSC','nonconsolidated',k] for k in ['energy_CO2','nonenergy_CO2','CH4','N2O'])
 assert gap==22 and '22kt 차이' in paper
 sensitivity=pd.read_csv(out/'denominator_sensitivity.csv')
 np.testing.assert_allclose(sensitivity.normalized_intensity,sensitivity.process_energy_fraction/sensitivity.utilization,rtol=1e-12)
 e=pd.read_csv(ROOT/'data/research_v2/evidence/company_energy_intensities.csv')
 electricity=e[(e.company=='POSCO')&(e.quantity=='purchased_electricity')].iloc[0]
 assert pd.isna(electricity.value) and electricity.use_status=='withheld_missing_conversion'
 for _,r in e[e.company=='LOTTE'].iterrows():assert 'upper bound on NCC' not in r.comparison_note
 assert not pd.read_csv(out/'company_mapping_status.csv').ready_for_new_corporate_frontier.any()
 version=re.search(r'연구 원고 (v[\d.]+)',paper).group(1).replace('.','')
 report=dict(source_observations_visually_reviewed=35,source_PDFs=4,new_table_values_checked=printed_table,new_prose_values_checked=8,coverage_identity_values_checked=8,sensitivity_values_checked=len(sensitivity),withdrawn_electricity_conversion=True,corporate_FIN_adoption=False,
  sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),out/'manifest.json',ROOT/'paper/methodology/TCaR_METHOD_KO.md',ROOT/'output/pdf/TCaR_methodology.pdf']})
 (ROOT/f'docs/research_cycles/2026-09-07-hourly/company_boundary_{version}_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='sha256'}))

if __name__=='__main__':main()
