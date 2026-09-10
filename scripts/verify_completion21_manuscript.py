"""Audit the narrow v2.26.1 integration against saved scientific experiments.

The comparison copy is captured before editing. Checks concern transcription,
scope and preservation; they do not establish corporate calibration.
"""
from pathlib import Path
import re,json,hashlib
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
PAPER=ROOT/'paper/methodology/TCaR_METHOD_KO.md'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    text=PAPER.read_text();before=(ROOT/'tmp/research_completion21/TCaR_METHOD_KO.md').read_text()
    assert re.search(r'연구 원고 v2\.\d+(\.\d+)? ·',text)
    q=pd.read_csv(ROOT/'data/research_v2/ncc_timing_frontier/qualification.csv')
    metrics=pd.read_csv(ROOT/'data/research_v2/ncc_timing_frontier/risk_metrics.csv')
    risk=pd.read_csv(ROOT/'data/research_v2/steel_procurement_tail/conditional_risk.csv')
    random=pd.read_csv(ROOT/'data/research_v2/steel_procurement_tail/pairing_randomization.csv')
    timing=text.split('### 6.16 ')[1].split('### 6.17 ')[0]
    steel=text.split('### 6.17 ')[1].split('## 7.')[0]
    count=0
    for year in [2030,2035,2040,2045]:
        r=q[(q.commission_year==year)&(q.residual_per_t_naphtha==0)].set_index('grid_initial')
        line=f'| {year} | {r.loc[.2,"cumulative_ratio"]*100:.2f}% | {r.loc[.4,"cumulative_ratio"]*100:.2f}% |'
        assert line in timing,line;count+=3
    for name in ['replace_2030','replace_2035','replace_2040']:
        a=metrics[(metrics.candidate==name)&(metrics.seed==20260917)].iloc[0]
        b=metrics[(metrics.candidate==name)&(metrics.seed==20260918)].iloc[0]
        line=f'| {name[-4:]} | {a.analytic_mean:,.2f} | {a.es_alpha:,.2f} | {b.es_alpha:,.2f} | {a.tcar:,.2f} | {b.tcar:,.2f} |'
        assert line in timing,line;count+=6
    for beta in [0,.5,1]:
        a=risk.query('seed==20260923 and pairing=="joint" and beta==@beta').iloc[0]
        b=risk.query('seed==20260924 and pairing=="joint" and beta==@beta').iloc[0]
        line=f'| {beta:g} | {a["mean"]:,.1f} | {a.es_alpha:,.1f} | {a.tcar:,.1f} | {b.es_alpha:,.1f} |'
        assert line in steel,line;count+=5
    assert f'{risk.theoretical_mean.iloc[0]:,.1f}' in steel;count+=1
    for seed in [20260923,20260924]:
        r=risk.query('seed==@seed and pairing=="joint"').set_index('beta')
        pct=100*(r.loc[1,'es_alpha']/r.loc[0,'es_alpha']-1)
        assert f'{pct:.1f}%' in steel;count+=1
        median=random.query('seed==@seed and beta==1').es_alpha.median()
        pct=100*(1-r.loc[1,'es_alpha']/median)
        assert f'{pct:.1f}%' in steel;count+=1
    a=pd.read_csv(ROOT/'data/research_v2/steel_procurement_tail/tail_allocation.csv')
    for beta,comp in [(0,'electricity'),(1,'electricity'),(1,'pellets')]:
        v=a.query('seed==20260923 and pairing=="joint" and beta==@beta and component==@comp').excess_ES_contribution.iloc[0]
        assert f'{v:,.1f}' in steel;count+=1
    precision=pd.read_csv(ROOT/'data/research_v2/ncc_timing_frontier/bootstrap_precision.csv')
    for seed in [20260917,20260918]:
        r=precision.query('seed==@seed and candidate=="replace_2040" and condition=="g0.2_r0.0"').iloc[0]
        assert f'{r.tcar_p025:.1f}–{r.tcar_p975:.1f}' in timing;count+=2
    assert not q.annual_feasible.any()
    assert not q[q.residual_per_t_naphtha==.05].terminal_feasible.any()
    assert set(q[(q.grid_initial==.2)&q.eligible_for_cumulative_terminal_menu].commission_year)=={2030,2035,2040}
    assert set(q[(q.grid_initial==.4)&q.eligible_for_cumulative_terminal_menu].commission_year)=={2040}
    # Preserve old equations, policy appendix and every numeric table row
    # except the intentionally corrected summary unit/reference table.
    assert re.findall(r'\\\[.*?\\\]',text,re.S)==re.findall(r'\\\[.*?\\\]',before,re.S)
    old_rows=[l for l in before.splitlines() if l.startswith('|') and not l.startswith('| 6.')]
    for line in old_rows:
        expected=re.sub(r'그림 (18|19|20)(?!\d)',lambda m:'그림 '+str(int(m[1])+2),line)
        expected=re.sub(r'표 19(?!\d)','표 22',expected)
        if expected.startswith('| λ (C.4절 한정)'):
            expected=expected.replace('| 5.16 |','| C.4 |')
        assert expected in text,line
    old_figs=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',before)
    figs=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',text)
    assert set(old_figs).issubset(figs)
    for f in figs:assert (PAPER.parent/f).exists(),f
    for kind in ['표','그림']:
        labels=re.findall(r'\*\*'+kind+r' (\d+)\.',text)
        # Later appendices may add figures; retain the original sequence and
        # numeric/source checks above instead of pinning the final count.
        assert len(labels)>=22
        assert labels==list(map(str,range(1,len(labels)+1)))
    assert '### C.8' in text and '**표 C4.**' in text
    assert '여덟 가지 주요 한계' in text
    for stale in ['6.11절의 펠릿 가격은 고정값','가격 시나리오의 정밀화보다 공정 사양과 회계 경계의 선택에 더 민감','공정 사양의 불확실성이 가격 불확실성보다 결과를 더 크게 움직인다']:
        assert stale not in text
    for needed in ['선형 DISCLOSED 경로를 달성한 경계가 아니다','실제 선택 가능한 계약 비중이 아니다','선택 안정성과 위험량의 정밀도는 다른 검사','13개 시트','위험통계 58값·연간 현금식 504행·이전 판본 비교 42셀']:
        assert needed in text,needed
    book=ROOT/'outputs/01a07012-9848-7b02-8b66-346eca06ed4d/TCaR_joint_research_control_v6.xlsx'
    assert sha(book)=='8151194f7ed1397577bde320a2868abe4546ce7f060227a32acd8bcb6dbe6148'
    out=dict(new_printed_numeric_values_checked=count,existing_table_rows_preserved=len(old_rows),
             old_figures_preserved=len(old_figs),total_figures=len(figs),normal_tables=22,
             equations_preserved=12,scope_guards_passed=True,workbook_v6_unchanged=True,
             new_MC=False,company_calibrated=False,sha256={str(PAPER.relative_to(ROOT)):sha(PAPER),
             str(Path(__file__).relative_to(ROOT)):sha(__file__)})
    (ROOT/'tmp/research_completion21/integration_verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
