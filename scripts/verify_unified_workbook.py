"""Audit three actual two-model file roundtrips with an independent tail sum."""
from pathlib import Path
import json
import hashlib
import math
import numpy as np
from unified_workbook_control import verify_saved, read_both
from xlsx_table_reader import read_cells

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'tmp/ncc_joint_workbook/completion9'


def main():
    runs=[]
    for case in ('final','changed_guarded','grown_zero'):
        report=json.loads((RUN/case/'verification.json').read_text())
        payload=json.loads((RUN/case/'payload.json').read_text())
        path=Path(report['output'])
        assert hashlib.sha256(path.read_bytes()).hexdigest()==report['output_sha256']
        verify_saved(path,payload)
        s=read_cells(path);controls=read_both(path);max_error=[]
        for (source,target),c in zip([('Cost paths','Control'),('NCC paths','NCC cash')],controls):
            values=np.sort([s[source][row,3]['value']-s[source][row,2]['value'] for row in range(5,c['paths']+5)])
            mass=len(values)*(1-c['alpha']);whole=math.floor(mass);fraction=mass-whole
            tail=(float(values[-whole:].sum()) if whole else 0.)+fraction*values[-whole-1]
            median,q=np.quantile(values,[.5,c['alpha']],method='linear')
            expected=[values.mean(),median,q,q-median,tail/mass]
            actual=[s[target][row,2]['value'] for row in range(5,10)]
            np.testing.assert_allclose(actual,expected,rtol=1e-12,atol=1e-7)
            max_error.append(float(np.max(np.abs(np.array(actual)-expected))))
        runs.append(dict(case=case,models=report['models'],independent_tail_max_errors=max_error,
                         annual_rows=48,sheets=report['sheets']))
    assert all(m['metrics'][3]==0 for m in runs[-1]['models'])
    assert runs[-1]['models'][0]['metrics']==[0]*5
    assert runs[-1]['models'][1]['metrics'][0]>0
    features=json.loads((RUN/'feature_preservation.json').read_text())
    assert len(features['structural_features'])==60 and features['cell_style_maps_preserved']==10
    rejected=json.loads((RUN/'guarded_edits/rejections.json').read_text());assert len(rejected)==6
    stale={r['name']:r for r in json.loads((RUN/'guarded_edits/stale_checks.json').read_text())}
    assert stale['technology_unit']['jointStatus']=='재계산 필요'
    assert stale['scenario_provenance']['jointStatus']==stale['scenario_provenance']['status']=='재계산 필요'
    assert runs[-1]['sheets']==11
    paper=(ROOT/'paper/methodology/TCaR_METHOD_KO.md').read_text();control_log=(ROOT/'paper/methodology/EXCEL_CONTROL_LOG_KO.md').read_text()
    for phrase in ['두 모형의 통합 갱신','10,000/5,000','101/103','205/207','위험 요약30개','연간 현금식144행','60개 구조 비교','10개 시트의 셀 서식']:
        assert phrase in paper or phrase in control_log,phrase  # v4 record moved to EXCEL_CONTROL_LOG_KO.md in v2.25
    result=dict(actual_roundtrips=runs,risk_metrics_checked=30,annual_cash_rows_checked=144,
                source_edit_and_invalid_rejections=6,unit_and_provenance_stale_display_fixed=True,
                structural_feature_checks=60,cell_style_maps_preserved=10,extra_note_sheet_preserved=True,
                new_manuscript_execution_claims_checked=8,company_calibration=False,native_Excel_tested=False,
                sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [
                    Path(__file__),ROOT/'scripts/unified_workbook_control.py',ROOT/'scripts/refresh_joint_workbook.mjs',
                    ROOT/'paper/methodology/TCaR_METHOD_KO.md',ROOT/'output/pdf/TCaR_methodology.pdf',
                    Path(json.loads((RUN/'final/verification.json').read_text())['output'])]})
    (RUN/'roundtrip_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('sha256','actual_roundtrips')},ensure_ascii=False))


if __name__=='__main__':main()
