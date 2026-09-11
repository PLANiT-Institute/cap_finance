"""Build the explicit public-data / server-engine allowlist for the web tool.

Never copy a research run, facility input, local workbook, or private PDF tree.
The historical corporate snapshot is checked against its completed run manifest;
current reference calculators are byte-for-byte copies with their own fingerprint.
"""
from pathlib import Path
import csv
import hashlib
import json
import shutil
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'platform'
ENGINE = DEST / 'engine'
PUBLIC = DEST / 'public' / 'data'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_json(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')) + '\n')
def records(path):
    df = pd.read_csv(path)
    return json.loads(df.to_json(orient='records'))
def copy(relative):
    source = ROOT / relative
    dest = ENGINE / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, dest)
    return relative

def build():
    PUBLIC.mkdir(parents=True, exist_ok=True)
    files = [str(p.relative_to(ROOT)) for p in (ROOT/'src/cap').glob('*.py')]
    files += ['config.yaml']
    files += ['scripts/'+n+'.py' for n in ['ncc_joint_control','joint_workbook_control','ncc_cash_workbook_control','timing_workbook_control','research_block_price_paths','xlsx_table_reader']]
    files += ['data/research_v2/'+n for n in [
        'price_history/aligned_monthly_log_returns.csv','block_price_paths/manifest.json',
        'iea_2025_scenarios/curves.json','technology_packages/reference_process_packages.json',
        'tiggeloven_reference/source_observations.csv','tiggeloven_reference/manifest.json',
        'tiggeloven_supplement/manifest.json','ncc_emissions_context/direct_emissions_observations.csv',
        'ncc_emissions_context/manifest.json',
    ]]
    package=json.loads((ROOT/'data/research_v2/technology_packages/reference_process_packages.json').read_text())
    files += [x['path'] for x in package['source_registers']]
    supplement=json.loads((ROOT/'data/research_v2/tiggeloven_supplement/manifest.json').read_text())
    files += [p for p in supplement['sha256'] if not p.startswith('tmp/')]
    for path in sorted(set(files)): copy(path)
    write_json(ENGINE/'bundle-manifest.json',{p:sha(ROOT/p) for p in sorted(set(files))})

    def snapshot(run, cols, information_date, label, extra_meta):
        manifest=json.loads((run/'run_manifest.json').read_text())
        assert manifest['status']=='completed'
        for filename in ['e5/frontier_points.csv','e5/metrics_company.csv']:
            path=run/filename
            expected=next((v for k,v in manifest['output_sha256'].items() if k.endswith('/'+filename) or k==filename),None)
            assert expected is not None and sha(path)==expected, f'Historical result changed: {filename}'
        candidates=pd.read_csv(run/'e5/frontier_points.csv')[cols]
        selected=records(run/'e5/metrics_company.csv')
        return candidates, dict(candidates=json.loads(candidates.to_json(orient='records')),selected=selected,
            metadata=dict(information_date=information_date,finished_at=manifest['finished_at_utc'],label=label,
                horizon='2027–2050',unit='십억 KRW2025 대용치',scenario_status='NZ15·B20: 로컬 EST_v0 대용 시나리오 (다운로드한 NGFS/GCAM 아님; B20 연료가격은 IEA STEPS 앵커, NZ15 한국 탄소는 IEA NZE 선진국 경로로 교체)',
                candidate_count=len(candidates),schedule_count=int(candidates.base_plan_id.nunique()),
                result_sha256=sha(run/'e5/frontier_points.csv'),snapshot_only=True,**extra_meta))

    base_cols=['plan_id','base_plan_id','company_id','scenario','p50','p90','tcar','mean','es_alpha','alpha','n_draws','ppa_share','epc','budget_ok','sampled_statewise_dominated','decision_eligible','on_mean_tcar_frontier','on_mean_es_frontier']
    v1_run=ROOT/'tmp/research_case_expanded/run'
    _, v1=snapshot(v1_run, base_cols, '2026-09-05', 'v1 · 2026-09-05 동결 (보존)', dict(
        methodology_version='v1', price_factors='elec(추정)·h2(사전값 0.25)·capex(사전값 0.06), 상관 = 단위행렬',
        hedge_basis='total_purchase', frontier_axes=['p50','tcar'], carbon_included=True))
    v2_cols=base_cols+['p50_abs','mean_abs','tcar_abs','es_abs','es_abs_vs_baseline','on_mean_esabs_frontier','on_mean_tcarabs_frontier','carbon_delta','hedge_basis']
    def v2_meta(run, carbon, extra):
        pm=json.loads((run/'e3/price_model.json').read_text())
        return dict(methodology_version=extra.pop('mv'), price_factors='검증 계열만: elec(KPX SMP·JEPX 연간), co2(KAU 연간 2015–2025, NABO+KRX), coal·gas(World Bank CMO 연간); h2는 전력에서 구조적 파생, capex 결정론',
            innovation_sigma={k:round(v,4) for k,v in pm['innovation_sigma'].items()},
            correlation=dict(factors=pm['correlation_factors'],matrix=[[round(x,3) for x in r] for r in pm['correlation']],
                             overlap=pm.get('calibration_meta',{}).get('pairwise_overlap')),
            hedge_basis='incremental', frontier_axes=['mean','es_abs'], carbon_included=True, carbon_accounting=carbon,
            annual_budget_feasible_schedules=0, **dict(dict(e1_e2_source='2026-09-05 동결 실행의 45개 일정 재사용'), **extra))
    v2_run=ROOT/'tmp/research_case_v2_2026-09-10/run'
    _, v2=snapshot(v2_run, v2_cols, '2026-09-11', 'v2.0 · 총의무 p·E (보존)', v2_meta(v2_run,'gross_obligation_proxy: 무상할당 0, 총의무 p·E',dict(mv='v2.0-gross')))
    v21_run=ROOT/'tmp/research_case_v2_1_net/run'
    candidates, v21=snapshot(v21_run, v2_cols, '2026-09-11', 'v2.1 · 순거래 p·(E−A) (보존)', v2_meta(v21_run,
        'net_trade: A = 시나리오별 E1 기업 예산경로 — K-ETS 4기 철강·석유화학 100% 무상할당(탄소누출업종, 2차 인용)·GX-ETS §34 목표기반 무상할당(법조문 확인)에 근거한 규칙 대용치; 업체별 공표 할당량 아님',
        dict(mv='v2.1-net-allocation')))
    candidates.to_csv(PUBLIC/'company-candidates.csv',index=False)
    v22_run=ROOT/'tmp/research_case_v2_2_struct/run'
    candidates, v22=snapshot(v22_run, v2_cols, '2026-09-11', 'v2.2 · 검증 입력 정합 (보존)', v2_meta(v22_run,
        'net_trade: A = 시나리오별 E1 기업 예산경로 (v2.1과 동일 규칙)',
        dict(mv='v2.2-verified-inputs', h2_price_source='structural: 전력 중심가격×52 kWh/kg + 전해조 상각(IEA GHR 2024 앵커 2,916,000 KRW/kW, 하락률 0 — 검증 관측만 사용); D2b의 정책목표 3,500원/kg(MOTIE 2021)·JP 전략가는 v2.1에 보존',
             co2_near_term_anchor='2026 KAU 장내 거래량가중 연평균 21,073원(KRX, 1/2–9/10)을 한국 두 시나리오의 2026 앵커로 추가',
             scenario_labels={'NZ15':'NZE-anchored (IEA NZE 선진국 탄소가격·연료가격)','B20':'STEPS-anchored (IEA 공표정책 — 2°C 정합 아님; IEA WEO 2025에는 APS가 없어 2°C 앵커 부재)'})))
    v23_run=ROOT/'tmp/research_case_v2_3/run'
    v23_cols=v2_cols
    candidates, v23=snapshot(v23_run, v23_cols, '2026-09-11', 'v2.3 · E2 재생성·실질 무위험 2.4% (정본)', v2_meta(v23_run,
        'net_trade: A = 시나리오별 E1 기업 예산경로 (v2.1과 동일 규칙)',
        dict(mv='v2.3-regenerated-menu', discount_rate='2.4% 실질 (국고채 10년 4.40% − 기대물가 ~2%, 2026-09-11)',
             h2_price_source='structural (v2.2와 동일)', co2_near_term_anchor='KAU 2026 21,073원 (v2.2와 동일)',
             e1_e2_source='v2.2 가격·순거래·2.4% 할인율로 E1→E2 재생성 (27개 일정 / 270개 평가 후보; 배출 방향 확장은 미적용 — 실행 실패)',
             e2='MIP gap 실제값을 plan_index에 기록(NaN = CBC 증명 최적; 하한값은 PuLP 상수항 제외 — 단위 불일치, 참고용)',
             scenario_labels={'NZ15':'NZE-anchored (IEA NZE 선진국 탄소가격·연료가격)','B20':'STEPS-anchored (IEA 공표정책 — 2°C 정합 아님)'})))
    candidates.to_csv(PUBLIC/'company-candidates.csv',index=False)
    write_json(DEST/'src/lib/research.json',dict(version='v2.3',**v23,v22=v22,v21=v21,v2=v2,v1=v1))

    # D1 is aggregated before it enters the publication directory. No facility IDs.
    dd=ROOT/'tmp/research_case_v3/data'
    static=pd.read_csv(dd/'D1a_facility_static.csv')
    panel=pd.read_csv(dd/'D1b_facility_panel.csv').merge(static[['facility_id','company_id']],on='facility_id')
    capacity=static.groupby(['company_id','sector','capacity_unit'],dropna=False).capacity.sum().reset_index()
    totals=panel.groupby(['company_id','year'])[['production','emissions_s1','emissions_s2','energy_coal','energy_gas','energy_elec']].sum(min_count=1).reset_index()
    capacity.to_csv(PUBLIC/'D1a_company_capacity.csv',index=False)
    totals.to_csv(PUBLIC/'D1b_company_panel.csv',index=False)
    disclosures=pd.read_csv(dd/'D7_disclosed_plan.csv')
    disclosures=disclosures.groupby(['company_id','item_type','year_stated','resolution','mapping_status'],dropna=False).size().reset_index(name='record_count')
    disclosures.to_csv(PUBLIC/'D7_company_disclosures.csv',index=False)
    definitions=[
      ('D1a','설비 포트폴리오','D1a_company_capacity.csv','기업 × 업종 × 생산능력 단위','시설 입력을 기업 수준으로 집계. 추정 자산의 부분 포트폴리오이며 실제 기업 전체 생산능력과 다릅니다.','추정·집계','기업 후보',PUBLIC/'D1a_company_capacity.csv'),
      ('D1b','생산·배출·에너지','D1b_company_panel.csv','기업 × 관측 연도','생산과 Scope 1·2 및 구매 에너지. 시설 실측이 아닌 자산 배분·공정 추정값을 포함합니다.','추정·집계','기업 후보',PUBLIC/'D1b_company_panel.csv'),
      ('D2a','감축 예산','D2a_scenario_budget.csv','시나리오 × 부문 × 연도','NZ15·B20은 EST_v0 대용치. 다운로드한 NGFS/GCAM 데이터가 아닙니다. 누적 상한과 연간 상한을 구분합니다.','시나리오 가정','기업 후보',dd/'D2a_scenario_budget.csv'),
      ('D2b','중심 가격','D2b_scenario_prices.csv','시나리오 × 연도','기업 연구 사례의 중심 가격입니다. 아래 IEA 2025 참조 모형의 가격과 교체·혼합하지 않습니다.','시나리오 가정','기업 후보',dd/'D2b_scenario_prices.csv'),
      ('D3','전환 기술','D3_tech_options.csv','기술 × 업종','투자비, 공기, 수명, 에너지·배출 계수. 원문 수치와 경계 변환 가정이 섞여 있으며 기업 견적이 아닙니다.','원문 + 가정','기업 후보',dd/'D3_tech_options.csv'),
      ('D4','기업 가격 이력','D4_price_history.csv','관측 시점 × 가격 변수','v2 가격 보정 입력. KPX SMP·JEPX·KAU(NABO)·World Bank CMO 석탄·LNG 연평균(WB_CMO_* 행)만 확률 요인 추정에 쓰입니다. 수소·건설비 계열은 사전값 없이 구조 파생·결정론으로 처리합니다.','과거 가격 입력 (검증 계열)','기업 후보',ROOT/'tmp/research_case_v2_2026-09-10/data/D4_price_history.csv'),
      ('D5','정책 조건','D5_policy_support.csv','정책 × 적용 기간','정책별 보조·할당 조건의 등록부입니다. 저장된 기업 사례의 지원 조건은 support=none입니다.','정책·가정','기업 후보',dd/'D5_policy_support.csv'),
      ('D6','재무 기준','D6_company_financials.csv','기업 × 회계 연도','통화 단위, 재무 주체의 범위와 원문 확인 상태를 기록합니다. 비교 가능한 값이 없는 항목은 결측으로 표시합니다.','공시·결측','기업 후보',dd/'D6_company_financials.csv'),
      ('D7','공시 경로','D7_company_disclosures.csv','기업 × 공시 유형 × 목표 연도','시설별 매핑과 원문 인용을 제외한 집계입니다. 탄소중립 선언의 선형 배출 경로와 이를 달성하는 실제 투자 일정을 구분합니다.','공시 집계','공시 적격성',PUBLIC/'D7_company_disclosures.csv'),
      ('WB','공동 가격 변화','aligned_monthly_log_returns.csv','월 × 6개 가격','World Bank 벤치마크의 정렬된 월별 로그 변화. 동일 월의 가격을 공동 추출하며 기업 조달 잔차로 해석하지 않습니다.','벤치마크 파생','세 참조 모형',ROOT/'data/research_v2/price_history/aligned_monthly_log_returns.csv'),
      ('NCC','공정 문헌 원표','source_observations.csv','공정 × 물량·비용 항목','Tiggeloven 문헌 전사값. 원문 단위·페이지·해석 상태를 보존합니다. NCC 현금비용과 Timing에 연결됩니다.','문헌 관측','NCC cash · Timing',ROOT/'data/research_v2/tiggeloven_reference/source_observations.csv'),
      ('CO2','직접배출 경계','direct_emissions_observations.csv','공정 × 직접배출','재래식 0.397은 보고된 모형 결과, 전기식 0은 문헌 모형 가정입니다. 실측 및 전과정 배출량이 아닙니다.','문헌 모형','Timing',ROOT/'data/research_v2/ncc_emissions_context/direct_emissions_observations.csv'),
      ('EVIDENCE','기술 관측 등록부','primary_process_observations.csv','원문 관측 × 조건 × 단위','원문 URL·페이지·사용 상태를 유지합니다. 등록됐다는 이유만으로 모든 값이 계산에 채택되지는 않습니다.','원문 추적','공정 경계',ROOT/'data/research_v2/evidence/primary_process_observations.csv'),
    ]
    frames=[]
    for id,title,name,grain,note,status,used,path in definitions:
        if path!=PUBLIC/name: shutil.copyfile(path,PUBLIC/name)
        rows=records(path)
        frames.append(dict(id=id,title=title,file=name,grain=grain,note=note,status=status,used=used,
            columns=list(pd.read_csv(path,nrows=0).columns),rows=rows,sha256=sha(path)))
    curves=json.loads((ROOT/'data/research_v2/iea_2025_scenarios/curves.json').read_text())
    curve_rows=[dict(scenario=c['scenario'],commodity=c['commodity'],region=c['region'],year=y,value=v,
       unit=c['quantity_unit'],currency=c['currency'],price_year=c['price_year'],source=c['source'])
       for c in curves for y,v in zip(c['years'],c['values'])]
    pd.DataFrame(curve_rows).to_csv(PUBLIC/'iea-scenario-anchors.csv',index=False)
    frames.append(dict(id='IEA',title='IEA 중심 경로',file='iea-scenario-anchors.csv',grain='시나리오 × 가격 × 원표 연도',note='IEA GEC 2025 원표 앵커. 전력·메탄·나프타의 조달 가격으로 옮기는 비율과 기준가격은 별도 가정입니다.',status='시나리오 원표',used='세 참조 모형',columns=list(curve_rows[0]),rows=curve_rows,sha256=sha(PUBLIC/'iea-scenario-anchors.csv')))
    write_json(PUBLIC/'frames.json',frames)
    dictionary=records(ROOT/'data/package/data_dictionary.csv')
    write_json(PUBLIC/'field-dictionary.json',dictionary)
    print(f'Published {len(candidates)} company-level candidates, {len(frames)} dataframes; engine allowlist {len(set(files))} files.')

if __name__=='__main__': build()
