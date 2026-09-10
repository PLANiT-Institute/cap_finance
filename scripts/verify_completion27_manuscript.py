"""Verify joint-FX manuscript integration against frozen source artifacts."""
from collections import Counter
from fractions import Fraction
import csv
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / 'paper/methodology/TCaR_METHOD_KO.md'
OUT = ROOT / 'docs/research_cycles/2026-09-07-hourly'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    old = json.loads((OUT/'completion27_evidence/before.json').read_text())
    text = PAPER.read_text()
    assert '연구 원고 v2.31' in text
    prior_rows = Counter(old['table_rows'])
    rows = Counter(l for l in text.splitlines() if l.startswith('|'))
    assert not (prior_rows - rows)
    assert sum(prior_rows.values()) == 215
    figures = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', text)
    oldfigs = old['figures']
    assert figures[:len(oldfigs)] == oldfigs and len(oldfigs)==24 and len(figures)==25
    assert re.findall(r'\*\*그림 (\d+)\.', text) == [str(i) for i in range(1,26)]
    assert re.findall(r'\*\*표 (\d+)\.', text) == [str(i) for i in range(1,23)]
    assert re.findall(r'\*\*표 C(\d+)\.', text) == [str(i) for i in range(1,8)]
    assert re.findall(r'\\tag\{(\d+)\}', text) == old['equation_tags']
    eqs = re.findall(r'\\\[(.*?)\\\]', text, re.S)
    assert eqs == old['equations'] and len(eqs)==12
    refs = text.split('## 참고문헌 및 재현 자료', 1)[1]
    assert re.findall(r'^(\d+)\. ', refs, re.M)==[str(i) for i in range(1,64)]
    for line in old['references']:
        assert line in refs
    evidence = json.loads((OUT/'completion_26_verification.json').read_text())
    checked_hashes = 0
    for rel, digest in evidence['artifact_sha256'].items():
        assert sha(ROOT/rel)==digest, rel
        checked_hashes += 1
    experiment = json.loads((ROOT/'data/research_v2/ecb_fx_reference/experiment_manifest.json').read_text())
    for section in ('source_sha256','artifact_sha256'):
        for rel,digest in experiment[section].items():
            assert sha(ROOT/rel)==digest, rel
            checked_hashes += 1
    assert sha(ROOT/'paper/methodology/figures/fx_joint_conversion.png') == sha(ROOT/'data/research_v2/ecb_fx_reference/fx_joint_conversion.png')
    metrics=list(csv.DictReader((ROOT/'data/research_v2/ecb_fx_reference/exact_block_conversion_metrics.csv').open()))
    lookup={(r['commodity'], r['currency'], r['method']):r for r in metrics}
    count=0
    for commodity,label in [('brent','원유'),('japan_lng','일본 LNG'),('iron_ore','철광석')]:
        for currency,korean in [('KRW','원화'),('JPY','엔화')]:
            joint=lookup[commodity,currency,'same_historical_block']
            independent=lookup[commodity,currency,'independent_block_pairs']
            vals=[float(joint['mean']),float(independent['mean']),float(joint['es95']),float(independent['es95'])]
            line='| '+label+'·'+korean+' | '+' | '.join(f'{v:.6f}' for v in vals)+' |'
            assert line in text, line
            count+=4
    for value in ('1,421.522493','149.655408','1,605.452275'):
        assert value in text
    # Exact two-state example: inverse-CDF integrated ES95 equals largest loss.
    f=Fraction
    a,b,fx=(f(0),f(4)),(f(2),f(2)),(f(4),f(1))
    def point(x): return sum(x)/2,max(x)
    def dominates(x,y): return all(i<=j for i,j in zip(x,y)) and any(i<j for i,j in zip(x,y))
    foreign_a,foreign_b=point(a),point(b)
    domestic_a,domestic_b=point(tuple(x*y for x,y in zip(a,fx))),point(tuple(x*y for x,y in zip(b,fx)))
    assert foreign_a==(2,4) and foreign_b==(2,2) and dominates(foreign_b,foreign_a)
    assert domestic_a==(2,4) and domestic_b==(5,8) and dominates(domestic_a,domestic_b)
    # This is a distributional reversal, not a change of the physical feasible set.
    for scale in (f(1,100),f(3),f(1500)):
        assert dominates(point(tuple(scale*x for x in b)),point(tuple(scale*x for x in a)))
    inverse_mean=(1/f(1,2)+1/f(3,2))/2
    assert inverse_mean==f(4,3)
    assert [x*(1/x)/inverse_mean for x in (f(1,2),f(3,2))]==[f(3,4)]*2
    workbook=ROOT/'outputs/01a07012-9848-7b02-8b66-346eca06ed4d/TCaR_joint_research_control_v6.xlsx'
    assert sha(workbook)=='8151194f7ed1397577bde320a2868abe4546ce7f060227a32acd8bcb6dbe6148'
    report=dict(all_passed=True,iteration=27,manuscript_version='v2.31',prior_table_rows_preserved=215,
                old_figures_preserved=24,figures=25,numbered_equations_unchanged=12,references=63,
                new_table_values_checked=count,annual_FX_values_preserved=3,
                frozen_source_hashes_checked=checked_hashes,numeraire_reversal_exact=True,
                constant_conversion_preservation_examples=3,inverse_mean_counterexample='4/3',
                Excel_v6_unchanged=True,new_MC_draws=0,company_calibration=False,goal_complete=False)
    paths=[PAPER,ROOT/'output/pdf/TCaR_methodology.pdf',ROOT/'paper/methodology/figures/fx_joint_conversion.png',Path(__file__)]
    report['artifact_sha256']={str(p.relative_to(ROOT)):sha(p) for p in paths}
    (OUT/'completion_27_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
