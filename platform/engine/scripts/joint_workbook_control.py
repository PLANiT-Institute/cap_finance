"""Read documented Excel controls and execute the paired NCC partial-cost model.

XLSX reading is read-only XML; all XLSX authoring is delegated to Artifact Tool.
Refreshing creates a rebuilt, versioned result file; it never edits the input file.
"""
from pathlib import Path
import argparse
import json
import hashlib
import subprocess
import sys
import numpy as np
from ncc_joint_control import ROOT, DEFAULTS, evaluate, validate_controls
from xlsx_table_reader import read_cells, literal, WorkbookInputError

FIELDS = [
    ('scenario','시나리오','IEA GEC 2025','시나리오에 확률을 부여하지 않음'),
    ('shock_model','월별 충격 생성법','공동 분포','같은 월의 6개 가격 변화를 함께 추출'),
    ('start_year','계산 시작 연도','년','시작 연도 현금흐름의 할인계수는 1'),
    ('end_year','계산 종료 연도','년','원자료 범위: 2024–2050'),
    ('production_t','매년 에틸렌 생산량','t/년','고정 생산량 가정. 기업 실제 생산량 아님'),
    ('power_EUR2024_MWh','기준 전력 구매가격','EUR2024/MWh','예시 가정. 고정 성분 + LNG 연동 성분'),
    ('methane_EUR2024_t','기준 메탄 판매 넷백','EUR2024/t CH4','예시 가정. 판매·처리 비용 차감 후; 음수 허용'),
    ('naphtha_EUR2024_t','기준 나프타 구매가격','EUR2024/t','예시 가정. 원유 시나리오 비율에 연동'),
    ('power_indexed_share','전력가격의 LNG 연동 비중','0–1','기준 연도 가격 중 연동 비중. PPA 계약 아님'),
    ('methane_sale_fraction','남는 메탄의 판매 비율','0–1','판매하지 않는 잔량은 이 부분 모형에서 가치 0'),
    ('KRW2024_per_EUR2024','보고 통화 환산 가정','KRW2024/EUR2024','고정 환산 가정. 환율 충격 제외'),
    ('discount_rate','실질 할인율','연율','2024년 실질가격 비용을 시작 연도로 할인'),
    ('alpha','꼬리 기준 분위수','확률','0.5 초과, 1 미만. ES는 정확한 꼬리 질량'),
    ('paths','몬테카를로 경로 수','개','2–10,000 (웹 API 상한; 로컬 실행은 50,000); 경로 수 증가는 모형 검증과 다름'),
    ('seed','난수 시드','정수','동일 입력·시드·소스 버전으로 재현'),
]
NODE=Path('/Users/jinsu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node')
DEPS=NODE.parent.parent/'node_modules'
SCRATCH=ROOT/'tmp/ncc_joint_workbook'


def reference_data():
    folder=ROOT/'data/research_v2/tiggeloven_supplement'
    manifest=json.loads((folder/'manifest.json').read_text())
    for p,sha in manifest['sha256'].items():
        if p.startswith('tmp/'):
            continue  # Private originals are not required to use the public tool.
        if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=sha:
            raise WorkbookInputError('Reference package changed; rebuild and review its provenance')
    return json.loads((folder/'workbook_reference.json').read_text())


def sources():
    from cap.scenario_prices import ScenarioPriceCurve, interpolate_curve
    curves=[ScenarioPriceCurve(**x) for x in json.loads((ROOT/'data/research_v2/iea_2025_scenarios/curves.json').read_text())]
    rows=[]
    for scenario in ('CPS','STEPS','NZE'):
        oil=next(x for x in curves if x.scenario==scenario and x.commodity=='crude_oil')
        gas=next(x for x in curves if x.scenario==scenario and x.commodity=='natural_gas' and x.region=='Japan')
        years=tuple(range(2024,2051));o=interpolate_curve(oil,years,method='linear');g=interpolate_curve(gas,years,method='linear')
        rows.extend([[f'{scenario}_{y}',scenario,y,o.values[i],g.values[i],
                      '원표' if y in oil.years and y in gas.years else '선형 보간',oil.source] for i,y in enumerate(years)])
    return rows


def read_controls(path):
    sheets=read_cells(path)
    if not {'Control','Scenario source','Technology DB'}<=set(sheets):
        raise WorkbookInputError('Required control/source sheets are missing')
    c={}
    for i,(key,label,_,_) in enumerate(FIELDS,12):
        if literal(sheets['Control'],i,1,f'Control!A{i}')!=label:
            raise WorkbookInputError(f'Control row {i} was moved or renamed')
        c[key]=literal(sheets['Control'],i,2,f'Control!B{i}')
    for r,row in enumerate(sources(),5):
        for col,value in enumerate(row[:5],1):
            actual=literal(sheets['Scenario source'],r,col,f'Scenario source row {r}')
            if isinstance(value,(int,float)):
                valid=isinstance(actual,(int,float)) and not isinstance(actual,bool) and np.isclose(actual,value,rtol=1e-12,atol=1e-12)
            else:valid=actual==value
            if not valid:raise WorkbookInputError('Scenario source changed: update the sourced model before refreshing')
    for r,value in enumerate((.21,6.99,3.58,.488),5):
        actual=literal(sheets['Technology DB'],r,2,f'Technology DB!B{r}')
        if not isinstance(actual,(int,float)) or isinstance(actual,bool) or not np.isclose(actual,value,rtol=1e-12,atol=1e-12):
            raise WorkbookInputError('Technology quantities changed: update the sourced model before refreshing')
    if 'NCC reference' in sheets:
        ref=reference_data()
        for first,records in [(10,ref['observations']),(64,ref['coproducts'])]:
            for row,record in enumerate(records,first):
                for col,value in enumerate(record,1):
                    actual=literal(sheets['NCC reference'],row,col,f'NCC reference row{row}')
                    if isinstance(value,(int,float)):
                        valid=isinstance(actual,(int,float)) and not isinstance(actual,bool) and np.isclose(actual,value,rtol=1e-12,atol=1e-12)
                    else:valid=actual==value
                    if not valid:raise WorkbookInputError('NCC reference changed; review source corrections before refreshing. This reference is not an active FIN specification.')
    return validate_controls(c)


def payload(c,directory):
    result,draws=evaluate(c)
    directory.mkdir(parents=True,exist_ok=True)
    (directory/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    np.savez_compressed(directory/'cost_draws.npz',**draws)
    data=dict(result=result,fields=FIELDS,scenarios=sources(),reference=reference_data(),
              draws=[[i+1,float(b),float(t)] for i,(b,t) in enumerate(zip(draws['baseline'],draws['transition']))])
    p=directory/'payload.json';p.write_text(json.dumps(data,ensure_ascii=False)+'\n')
    return p


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path);ap.add_argument('--controls',type=Path)
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--scratch',type=Path,default=SCRATCH/'default')
    ap.add_argument('--no-preview',action='store_true');a=ap.parse_args()
    if a.input and a.controls:ap.error('Use --input or --controls, not both')
    if a.input and a.input.resolve()==a.output.resolve():ap.error('Choose a new output path to preserve the edited input')
    c=read_controls(a.input) if a.input else validate_controls(json.loads(a.controls.read_text()) if a.controls else DEFAULTS)
    p=payload(c,a.scratch.resolve())
    SCRATCH.mkdir(parents=True,exist_ok=True);(SCRATCH/'package.json').write_text('{"type":"module"}\n')
    link=SCRATCH/'node_modules'
    if link.is_symlink() and link.resolve()!=DEPS.resolve():link.unlink()
    if not link.exists():link.symlink_to(DEPS,target_is_directory=True)
    command=[str(NODE),str(ROOT/'scripts/build_joint_control_workbook.mjs'),str(p),str(a.output.resolve())]
    if a.no_preview:command.append('--no-preview')
    subprocess.run(command,check=True,cwd=ROOT)


if __name__=='__main__':main()
