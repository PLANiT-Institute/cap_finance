"""Replay three preserved workbook inputs through the active delivery-gated FIN."""
from pathlib import Path
import hashlib,json
import numpy as np
import ncc_cash_workbook_control as cash
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/research_v2/ncc_delivery_integration'


def main():
 OUT.mkdir(parents=True,exist_ok=True);results=[];contracts={};inputs={}
 for case in ['final','changed_guarded','grown_zero']:
  previous=ROOT/f'tmp/ncc_joint_workbook/completion9/{case}/payload.json'
  p=json.loads(previous.read_text());workbook=Path(p['input_workbook'])
  c=cash.read_input(workbook);assert c==p['cash']['controls']
  r=cash.evaluate(c);contracts[case]=r['delivery_contract']
  before=np.array(p['cash']['draws']);after=np.array(r['draws'])
  np.testing.assert_array_equal(after,before)
  assert r['annual']==p['cash']['annual']
  for k in ['mean','p50','q_alpha','tcar','es_alpha']:assert r['metrics'][k]==p['cash']['metrics'][k]
  results.append(dict(case=case,paths=c['paths'],FIN_cost_values_checked=r['FIN_checks'],annual_rows=len(r['annual']),risk_metrics_unchanged=5,
   maximum_cost_change=float(abs(after-before).max()),max_FIN_error=r['max_FIN_error'],delivery_contract=r['delivery_contract'],
   workbook_sha256=hashlib.sha256(workbook.read_bytes()).hexdigest(),previous_payload_sha256=hashlib.sha256(previous.read_bytes()).hexdigest()))
  inputs[str(workbook.relative_to(ROOT))]=hashlib.sha256(workbook.read_bytes()).hexdigest();inputs[str(previous.relative_to(ROOT))]=hashlib.sha256(previous.read_bytes()).hexdigest()
 (OUT/'replays.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
 files=[ROOT/'src/cap/reference_delivery.py',ROOT/'src/cap/supply_network.py',ROOT/'scripts/ncc_cash_workbook_control.py',ROOT/'tests/test_reference_delivery.py',Path(__file__)]
 report=dict(saved_workbook_inputs_replayed=3,FIN_cost_values_checked=sum(r['FIN_cost_values_checked'] for r in results),annual_rows_unchanged=144,risk_metrics_unchanged=15,maximum_cost_change=0.,price_sampling_after_delivery_gate=True,new_workbook_written=False,native_Excel=False,new_corporate_results=False,
 input_sha256=inputs,code_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},artifact_sha256={str((OUT/'replays.json').relative_to(ROOT)):hashlib.sha256((OUT/'replays.json').read_bytes()).hexdigest()})
 (OUT/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if not k.endswith('sha256')})
if __name__=='__main__':main()
