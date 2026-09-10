"""Verify source-bound numerical claims and deterministic consolidation evidence."""
from pathlib import Path
import json,hashlib,re,subprocess
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def main():
 out=ROOT/'data/research_v2/supply_continuity';m=json.loads((out/'manifest.json').read_text())
 for group in ['source_sha256','artifact_sha256','code_sha256']:
  for p,h in m[group].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 obs=pd.read_csv(out/'mci_impact_observations.csv');assert len(obs)==4 and not obs.automatic_FIN_adoption.any()
 assert obs.value.iloc[1:].sum()==obs.value.iloc[0]
 paper=(ROOT/'paper/methodology/TCaR_METHOD_KO.md').read_text();control_log=(ROOT/'paper/methodology/EXCEL_CONTROL_LOG_KO.md').read_text();section=paper.split('### C.5')[1].split('## 참고문헌')[0]
 pdftext=subprocess.check_output(['pdftotext','-layout',str(ROOT/'output/pdf/TCaR_methodology.pdf'),'-'],text=True)
 for r in obs.itertuples():assert f'| {r.value*10:.0f} |' in section
 for term in ['85','20','40','25']:assert term in pdftext
 assert '새 물량·상계 검사 29개' in section
 records=pd.read_csv(out/'internal_settlement_invariance.csv');assert len(records)==16
 for _,g in records.groupby(['draw','period']):assert g.group_external_cash.nunique()==1
 assert not m['corporate_MC'] and not m['adaptive_policy_implemented']
 prior=['두 모형의 통합 갱신','10,000/5,000','101/103','205/207','위험 요약30개','연간 현금식144행','60개 구조 비교','10개 시트의 셀 서식']
 assert all(x in paper or x in control_log for x in prior)  # v4 record moved to EXCEL_CONTROL_LOG_KO.md in v2.25
 version=re.search(r'연구 원고 (v[\d.]+)',paper).group(1).replace('.','')
 result=dict(source_observations=4,source_pages_visually_reviewed=1,component_sum_check=True,new_printed_numeric_claims=4,new_execution_claim=1,previous_Excel_execution_claims_preserved=8,synthetic_accounting_cells=16,company_MC=False,adaptive_policy=False,
 sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),out/'manifest.json',ROOT/'paper/methodology/TCaR_METHOD_KO.md',ROOT/'output/pdf/TCaR_methodology.pdf']})
 (ROOT/f'docs/research_cycles/2026-09-07-hourly/supply_continuity_{version}_verification.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='sha256'})
if __name__=='__main__':main()
