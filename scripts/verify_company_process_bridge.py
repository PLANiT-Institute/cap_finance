"""Independently check saved observations, bounds and selected manuscript claims."""
from pathlib import Path
import hashlib,json,re,subprocess
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def main():
 out=ROOT/'data/research_v2/company_process_bridge';m=json.loads((out/'manifest.json').read_text())
 for group in ('input_sha256','artifact_sha256','code_sha256'):
  for p,h in m[group].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 obs=pd.read_csv(out/'native_observations.csv')
 assert len(obs)==29 and obs.id.is_unique and obs.visually_reviewed.all() and not obs.automatic_FIN_adoption.any()
 v=obs.set_index(['company','period','metric']).value.to_dict()
 d=pd.read_csv(out/'utilization_reconciliation.csv')
 for r in d.itertuples():
  q=v['LOTTE',f'CY{r.year}','NC_production'];k=v['LOTTE',f'CY{r.year}','NC_capacity'];u=v['LOTTE',f'CY{r.year}','NC_utilization']
  np.testing.assert_allclose([r.simple_output_capacity_pct,r.difference_pp],[100*q/k,u-100*q/k],atol=1e-12)
  assert not r.rounds_to_reported
 b=pd.read_csv(out/'conditional_output_bounds.csv');assert len(b)==21
 for r in b.itertuples():
  # Endpoint feasibility and extremality without calling the production helper.
  q=2848129;ke=2330000*r.assumed_capacity_multiplier;kp=1191000*r.assumed_capacity_multiplier
  for e in (r.ethylene_lower_t,r.ethylene_upper_t):assert -1e-8<=e<=ke+1e-8 and -1e-8<=q-e<=kp+1e-8
  assert abs(r.ethylene_lower_t-max(0,q-kp))<1e-8 and abs(r.ethylene_upper_t-min(q,ke))<1e-8
 paper=(ROOT/'paper/methodology/TCaR_METHOD_KO.md').read_text();section=paper.split('### C.4')[1].split('## 참고문헌')[0]
 claims=[f"{v['LOTTE','CY2024','NC_capacity']:,.0f}",f"{v['LOTTE','CY2024','NC_production']:,.0f}",f"{v['LOTTE','CY2024','NC_utilization']:.1f}%",f'{d.iloc[0].simple_output_capacity_pct:.3f}%',
  f"{v['LOTTE','CY2023','ethylene_capacity']*1000:,.0f}",f"{v['LOTTE','CY2023','propylene_capacity']*1000:,.0f}",
  *[f'{x:,.0f}' for i in [0,-1] for x in [b.iloc[i].ethylene_lower_t,b.iloc[i].ethylene_upper_t]],
  f"{v['LOTTE','CY2024','naphtha_price']:.0f}USD/MT",f"{v['LOTTE','CY2024','naphtha_purchase']:,.0f}백만원",
  *[f"{v['NSC','FY2024',k]:.2f}백만t" for k in ['pig_iron','crude_steel_nonconsolidated','steel_products_shipped']],f"{v['MCI','FY2024_first_half','announced_impact_estimate']*10:.0f}억엔"]
 assert len(claims)==16
 pdftext=subprocess.check_output(['pdftotext','-layout',str(ROOT/'output/pdf/TCaR_methodology.pdf'),'-'],text=True)
 for s in claims:assert s in section and s in re.sub(r'\s+','',pdftext),s
 assert not m['NC_composition_verified'] and not m['corporate_FIN_adoption']
 assert len(re.findall(r'\*\*그림 \d+\.',paper))==len(re.findall(r'^!\[',paper,re.M))
 version=re.search(r'연구 원고 (v[\d.]+)',paper).group(1).replace('.','')
 report=dict(native_observations=29,source_PDFs=4,source_pages_visually_reviewed=6,reconciliation_rows=3,conditional_bounds_checked=21,selected_numeric_claims_checked=16,NC_definition_verified=False,corporate_FIN_adoption=False,
   sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),out/'manifest.json',ROOT/'paper/methodology/TCaR_METHOD_KO.md',ROOT/'output/pdf/TCaR_methodology.pdf']})
 (ROOT/f'docs/research_cycles/2026-09-07-hourly/company_process_bridge_{version}_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='sha256'}))
if __name__=='__main__':main()
