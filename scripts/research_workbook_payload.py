"""Prepare an integrated, portable research workbook and embedded input contract."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / 'docs/research_cycles/2026-09-05'
sys.path.insert(0, str(ROOT/'src'))
from cap.schemas import NUMERIC
from research_control_contract import CONTROLS, KEYS, get_nested


def table(path, columns=None, numeric=()):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        cols = columns or reader.fieldnames
        rows = []
        for row in reader:
            vals = []
            for col in cols:
                value = row.get(col, '')
                if value == '':
                    value = None
                elif col in numeric:
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                elif value in {'True', 'False'}:
                    value = value == 'True'
                vals.append(value)
            rows.append(vals)
    return dict(columns=cols, rows=rows)


def build(config_path, out):
    config = yaml.safe_load(config_path.read_text())
    config.setdefault('candidate_expansion_emissions_points', 0)
    data = Path(config['data_dir']); run = Path(config['out_dir'])
    manifest_path = run/'run_manifest.json'
    manifest = json.loads(manifest_path.read_text())
    if manifest['status'] != 'completed':
        raise ValueError('Only a completed run can populate result sheets')
    for group in ['source_sha256','output_sha256']:
        for name, expected in manifest[group].items():
            path = Path(name)
            path = path if path.is_absolute() else ROOT/path
            if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
                raise ValueError(f'Result provenance changed: {path}; rerun before refreshing')
    payload = dict(version=2, sheets=[], config=config,
                   run_manifest_sha256=hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                   run_finished_at_utc=manifest['finished_at_utc'])
    def add(name, title, note, path=None, columns=None, numeric=(), rows=None, **extra):
        t = table(path, columns, numeric) if path else dict(columns=columns, rows=rows)
        payload['sheets'].append(dict(name=name,title=title,note=note,**t,**extra))
    add('Case results','선택 후보의 증분 비용',f'2027–2050. {config["budget_mode"]}. 십억원, 선언된2025년 원화 기준 대용치. 선택 기준 {config["plan_selection_criterion"]}.',
        run/'e5/metrics_company.csv',
        ['company_id','scenario','selected_plan_id','p50_bnkrw','mean_bnkrw','tcar_bnkrw','es_alpha_bnkrw','capex_peak_bnkrw','capex_peak_year','selection_criterion'],
        ['p50_bnkrw','mean_bnkrw','tcar_bnkrw','es_alpha_bnkrw','capex_peak_bnkrw','capex_peak_year'])
    add('Risk measures','모든 후보의 비용과 위험','동일 가격경로의 조건부 평가. 표본 지배 후보는 선택에서 제외. 입력 수정 후 재실행해야 갱신됩니다.',
        run/'e5/frontier_points.csv',
        ['company_id','scenario','support','plan_id','mean','p50','p90','tcar','es_alpha','ppa_share','epc','decision_eligible','on_mean_tcar_frontier','on_mean_es_frontier','sampled_dominance_witness'],
        ['mean','p50','p90','tcar','es_alpha','ppa_share','epc'])
    def records(path):
        with path.open(newline='') as f:return list(csv.DictReader(f))
    selected=records(run/'e5/metrics_company.csv')
    points={r['plan_id']:r for r in records(run/'e5/frontier_points.csv')}
    assets=records(data/'D1a_facility_static.csv')
    from cap.plancost import capital_ledger_for
    years=list(range(config['years']['start'],config['years']['end']+1))
    baseline={}
    for asset in assets:
        amounts=capital_ledger_for(asset,None,None,years,config).cash_capex_k
        for year,value in zip(years,amounts):
            key=(asset['company_id'],year);baseline[key]=baseline.get(key,0.)+float(value)/1e6
    schedule_rows=[];annual_rows=[]
    ledger=records(run/'e4/annual_capital_ledger.csv')
    for chosen in selected:
        candidate=points[chosen['selected_plan_id']];base=candidate['base_plan_id']
        plan={r['facility_id']:r for r in records(run/'e2/plans'/f'plan_{base}.csv') if r['facility_id']}
        for asset in assets:
            if asset['company_id']!=chosen['company_id']:continue
            decision=plan.get(asset['facility_id'],{})
            schedule_rows.append([chosen['company_id'],chosen['scenario'],chosen['selected_plan_id'],asset['facility_id'],
                decision.get('tech_id','incumbent'),float(decision['adopt_year']) if decision else None,
                float(decision['op_year']) if decision else None,float(candidate['ppa_share']),int(candidate['epc'])])
        for row in ledger:
            if row['plan_id']!=base:continue
            year=int(row['year']);gross=float(row['gross_capex_k'])/1e6;reference=baseline[(chosen['company_id'],year)]
            annual_rows.append([chosen['company_id'],chosen['scenario'],year,gross,reference,gross-reference,
                float(row['construction_k'])/1e6,float(row['maintenance_capex_k'])/1e6,
                float(row['noncash_writeoff_k'])/1e6,float(row['terminal_value_k'])/1e6,chosen['selected_plan_id']])
    add('Selected schedules','선택한 시설·기술·착수·가동 일정','추정 자산 포트폴리오의 실제 선택 행입니다. incumbent는 전환 미선택입니다. 동률과 현장 추가 제약을 함께 확인합니다.',
        columns=['company_id','scenario','selected_plan_id','facility_id','tech_id','adopt_year','op_year','ppa_share','epc'],rows=schedule_rows)
    add('Annual capital','선택 일정과 기준선의 연간 자본 원장','십억원. 할인·계약 프리미엄·지원·가격충격 적용 전 금액입니다. 장부손실은 비현금이며 현금 총액에 합산하지 않습니다.',
        columns=['company_id','scenario','year','plan_gross_bnkrw','baseline_gross_bnkrw','incremental_gross_bnkrw',
                 'construction_bnkrw','renewal_bnkrw','noncash_writeoff_bnkrw','terminal_proxy_bnkrw','selected_plan_id'],rows=annual_rows)
    add('Attainable gaps','공시계획 비교 가능성','표현되지 않는 공시를 대체 기술로 바꾸거나 가동일을 옮겨 개선액을 산출하지 않습니다.',
        columns=['company_id','scenario','comparison','reason'],
        rows=[[co,sc,'not_represented','현재 전체 공시 커밋의 기술·설비·시점 매핑이 검증되지 않음'] for co in ['POSCO','NSC','MCI','LOTTE'] for sc in config['scenarios']])
    add('Settings','실행 설정','value 열이 수정 입력입니다. 범위는 소프트웨어 허용 범위이며 경험적 신뢰구간이 아닙니다.',
        columns=['parameter','value','unit_or_description','allowed_values'],
        rows=[[key,get_nested(config,key),spec[3],', '.join(spec[1]) if spec[0]=='choice' else ('TRUE, FALSE' if spec[0]=='boolean' else f'{spec[1]} to {spec[2]}')] for key,spec in CONTROLS.items()],editable_columns=['value'])
    payload['sheets'][-1]['rows'][-1][3]='0, or an integer from 2 to 30'
    add('Parameters','기존 모수의 증거와 가정 범위','FIN·EFF 기존 등록부415행. 새 잔존에너지39가정과 구별. 이 시트의 수정은 모형 입력에 적용되지 않습니다.',
        ROOT/'docs/parameter_inventory.csv',numeric=['value','value_low','value_high'])
    add('Primary observations','원문에서 확인한 선택 수치','원문 단위·기간·기업 또는 사업장 범위를 유지합니다. 모형 개별 설비의 실측값이라는 뜻은 아닙니다.',
        AUDIT/'selected_primary_observation_register.csv',numeric=['value'])
    add('Energy assumptions','기술별 구매 에너지 잔존 가정','모형의 D3에서 수정합니다. [0,1]은 구조적 범위이며 열수지·부산물 수지의 경험적 신뢰구간이 아닙니다.',
        data/'energy_retention_assumptions.csv',numeric=['value','structural_low','structural_high'])
    add('Sources','원자료 출처 목록','기존 출처 목록입니다. 이번에 확인한 개별 수치와 원문 위치는 Primary observations에서 확인합니다.',
        data/'source_register.csv',columns=['source_id','publisher','title','url_or_doi','location','retrieved_at','quality_note'])
    add('Literature','방법론 문헌','서지·초록·원문 확인 범위를 구별합니다.',AUDIT/'literature_register.csv')
    add('Issues','해석에 영향을 주는 검증 과제','해결된 구현 문제와 남은 데이터·외부 타당성 문제를 구별합니다.',AUDIT/'issues.csv',numeric=['priority'])
    # Attach fixed-baseline audits only when every candidate statistic matches.
    # Edited reruns must not inherit a sensitivity assessment of different inputs.
    robust=AUDIT/'robustness_verified'
    original=ROOT/'tmp/research_case_expanded/run/e5/frontier_points.csv'
    if not original.exists():
        original=ROOT/'reference_run/e5/frontier_points.csv'
    fields=['company_id','scenario','support','plan_id','mean','p50','p90','tcar','es_alpha']
    numeric=['mean','p50','p90','tcar','es_alpha']
    if robust.joinpath('validation.json').exists() and original.exists():
        current_rows=sorted(table(run/'e5/frontier_points.csv',fields,numeric)['rows'])
        audited_rows=sorted(table(original,fields,numeric)['rows'])
        if current_rows==audited_rows:
            note='기준 450개 후보의 감사입니다. 현재 결과와 전 후보 5개 통계량이 일치할 때만 첨부됩니다. 모수·선택 오차를 포함한 경험적 신뢰구간이 아닙니다.'
            add('Analytic means','분석적 기대비용과 MC 평균',note,
                robust/'selected_analytic_means.csv',numeric=['analytic_mean','monte_carlo_mean','bootstrap_low_95','bootstrap_high_95','tied_analytic_minimum_count'])
            add('Sampling intervals','고정 후보의 경로 표본오차',note,
                AUDIT/'robustness/fixed_candidate_bootstrap.csv',
                columns=['company_id','scenario','plan_id','metric','point','bootstrap_low_95','bootstrap_high_95','interval_scope'],
                numeric=['point','bootstrap_low_95','bootstrap_high_95'])
            add('Sensitivity','가정 변경에 따른 선택 변화','각 열은 8개 기업–시나리오 중 기준 후보 ID가 바뀐 수입니다. 고정 메뉴의 조건부 가정 시험이며 전역 재최적화가 아닙니다.',
                robust/'selection_changes.csv',numeric=['mean','tcar','es_alpha'])
            add('Equivalent plans','동일한 모형 비용분포의 일정','추정 설비 특성 때문에 생긴 동률입니다. 현장 시설의 교환 가능성이나 유일한 최적 일정의 증거가 아닙니다.',
                robust/'equivalent_plans.csv')
    contract = dict(version=2,config=config,input_files={},sheets={},run_manifest_sha256=payload['run_manifest_sha256'])
    for path in sorted(data.glob('*.csv')):
        raw=path.read_bytes()
        contract['input_files'][path.name]=dict(csv=raw.decode('utf-8'),sha256=hashlib.sha256(raw).hexdigest())
        if not path.name.startswith('D'):
            continue
        name=path.stem.split('_')[0]
        num=set(NUMERIC)|{'value_low','value_high'}
        t=table(path,numeric=num)
        editable=[c for c in t['columns'] if c in num and c not in KEYS[name]]
        if name=='D7':editable=[]
        contract['sheets'][name]=dict(filename=path.name,columns=t['columns'],rows=t['rows'],keys=KEYS[name],editable_columns=editable)
        add(name,path.stem,'노란 셀만 수정 입력입니다. ID·단위·출처는 유지합니다. 변경값은 사용자 가정으로 기록하며 결과 갱신에는 재실행이 필요합니다.',
            columns=t['columns'],rows=t['rows'],editable_columns=editable)
        notes={
            'D3b':'범위 기록용 입력입니다. 기본 E1–E5 계산은 이 범위에서 모수를 추출하지 않습니다. 문헌 표본 범위도 개별 기술의 신뢰구간과 다릅니다.',
            'D4':'가격 이력입니다. 요인별 사용 계열과 최소 관측 수에 따라 변동성을 추정하거나 사전값을 씁니다. 모든 행이 활성 가격요인은 아닙니다.',
            'D5':'지원 입력입니다. 현재 support_scenarios=none에서는 적용되지 않습니다. 경매비율은 현재 총 탄소의무 비용에 곱하지 않습니다.',
            'D6':'재무 참조입니다. 설비·위험 경계를 직접 최적화하지 않습니다. 숫자를 바꾸면 원문 검증 상태가 해제되어 엄격 비율이 미산출될 수 있습니다.'}
        if name in notes:payload['sheets'][-1]['note']=notes[name]
    contract['reference_tables']={s['name']:dict(columns=s['columns'],rows=s['rows'])
                                 for s in payload['sheets'] if 'editable_columns' not in s}
    raw=json.dumps(contract,ensure_ascii=False,separators=(',',':'),allow_nan=False)
    contract_sha=hashlib.sha256(raw.encode()).hexdigest()
    add('Control schema','입력 기준과 실행 연결','자동으로 저장한 기준 입력입니다. 직접 편집하지 않습니다. 외부 파일 없이 입력의 동일성과 변경을 검사합니다.',
        columns=['record','content'],rows=[['contract_version',2],['contract_sha256',contract_sha]]+
        [[f'chunk_{i//12000:04}',raw[i:i+12000]] for i in range(0,len(raw),12000)])
    payload['contract_sha256']=contract_sha
    payload['input_contract']=contract
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,ensure_ascii=False,allow_nan=False,indent=2)+'\n')
    print(f'Prepared {len(payload["sheets"])+2} sheets; contract {contract_sha}')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config',type=Path,default=ROOT/'tmp/research_case_expanded/config.yaml')
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();build(args.config,args.out)


if __name__=='__main__':main()
