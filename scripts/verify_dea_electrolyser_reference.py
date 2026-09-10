"""Check frozen source locators, independently reconstruct printed diagnostics."""
from pathlib import Path
import csv, hashlib, json, math
import openpyxl

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/research_v2/dea_electrolyser_reference'
RAW=ROOT/'tmp/pdfs/tcar_research_v2/steel_upstream'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    m=json.loads((OUT/'manifest.json').read_text())
    for p,h in m['source_sha256'].items(): assert sha(RAW/p)==h,p
    for p,h in m['output_sha256'].items(): assert sha(OUT/p)==h,p
    wb=openpyxl.load_workbook(RAW/'dea_aug2026.xlsx',data_only=True)
    native=json.loads((OUT/'selected_native_cells.json').read_text())
    for r in native: assert wb[r['sheet']][r['cell']].value==r['cached_value'],r
    s=wb['80 AEC 100 MW']
    note=(ROOT/'paper/methodology/ELECTROLYSER_SOURCE_ALIGNMENT_KO.md').read_text()
    printed=[]
    with (OUT/'specification_comparison.csv').open() as f: comps=list(csv.DictReader(f))
    old_etas=[.587,.6994]
    for r,c,eta in zip(comps,['C','G'],old_etas):
        old=33.33/eta; new=s[f'{c}12'].value
        for key,value in [('Langhorst_source_kWh_per_kg_H2',old),
                          ('DEA_AEC100_reference_kWh_per_kg_H2',new),
                          ('Langhorst_electrolysis_MWh_per_t_DRI',old*.058),
                          ('DEA_electrolysis_MWh_per_t_DRI',new*.058)]:
            assert math.isclose(float(r[key]),value,rel_tol=1e-12)
            assert f'{value:.3f}' in note
            printed.append(f'{value:.3f}')
        pct=(new-old)/old*100
        assert f'{abs(pct):.3f}%' in note
        printed.append(f'{abs(pct):.3f}%')
    # Symmetric log quantiles imply this median, regardless of log-variance.
    qlo=s['J27'].value; qhi=s['K27'].value
    mu=(math.log(qlo)+math.log(qhi))/2
    median=math.exp(mu)
    deviation=(1-median/s['G27'].value)*100
    for v in [qlo,qhi,median,s['G27'].value,deviation]:
        assert f'{v:.3f}' in note
        printed.append(f'{v:.3f}')
    # H and I must retain source order, which is reversed for consumption.
    assert s['H12'].value>s['I12'].value
    assert s['H15'].value<s['I15'].value
    assert wb['Intro']['D7'].value==2025
    v6=ROOT/'outputs/01a07012-9848-7b02-8b66-346eca06ed4d/TCaR_joint_research_control_v6.xlsx'
    assert sha(v6)=='8151194f7ed1397577bde320a2868abe4546ce7f060227a32acd8bcb6dbe6148'
    result=dict(source_hashes_checked=len(m['source_sha256']),output_hashes_checked=len(m['output_sha256']),
                native_source_cells_checked=len(native),independent_printed_diagnostics=len(printed),
                source_arithmetic_checks=m['arithmetic_checks'],source_arithmetic_passed=m['all_passed'],
                interval_direction_checks=2,currency_exception_checked=True,
                integrated_Excel_v6_unchanged=True,new_MC_runs=0,corporate_calibration=False,all_passed=True)
    target=ROOT/'docs/research_cycles/2026-09-07-hourly/completion_23_verification.json'
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
