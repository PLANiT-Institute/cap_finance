# CAP — Capital Allocation Pathway (v2)

기업의 탈탄소 전환비용이 "얼마인가"가 아니라 **"무엇에 얼마나 흔들리며, 기업은 그 흔들림을 줄일 수단을 확보했는가"**를 측정하는 도구.

대상 4사: POSCO · Nippon Steel (철강), LOTTE Chemical · Mitsui Chemicals (석유화학).

기준 문서: [`REDESIGN_SPEC.md`](REDESIGN_SPEC.md) — 데이터셋(D1–D7)·엔진(E1–E5)·지표(①–⑤) 정의.
기존 v1(cost-gap 설계)은 `archive/cap_kj_v1/`.

## 방법 요약

1. **제약만 내려받기** — NGFS-GCAM 시나리오에서 섹터 탄소예산·가격 경로만 추출 (감축량 안분 금지). 누가 언제 감축할지는 시설 단위 MILP가 결정하며, 설비 재투자 창이 투자 타이밍을 내생적으로 결정.
2. **불확실성을 원화로** — 전력·수소·CAPEX 상관 몬테카를로(N=5,000)로 비용 분포 산출. P50 = 기대비용, **TCaR = P90−P50**. 수소가격은 수소 = f(전력, 전해조 CAPEX) 구조식으로 파생.
3. **기업 내 효율 경계** — 선택 가능한 계획 전체를 (기대비용, TCaR) 평면에 놓고 ε-constraint로 frontier 추적. 공시 계획과 경계의 거리(**frontier gap**)가 진단 결과. 기업 간 순위표 없음.

## 실행

```bash
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"

# 합성 샘플 데이터로 전 파이프라인 검증
.venv/bin/python scripts/make_sample_data.py
.venv/bin/python -m cap all --data data/sample --sims 1000

# 실데이터 (data/raw/*.csv — 엑셀 템플릿에서 변환)
.venv/bin/python -m cap e1
.venv/bin/python -m cap e2      # 단계별 실행, 각 out/<stage>/ 확인 후 다음
.venv/bin/python -m cap e3
.venv/bin/python -m cap e4
.venv/bin/python -m cap e5
.venv/bin/python -m cap render

.venv/bin/pytest tests/ -q      # 전체 테스트 (~4분)
```

## 파이프라인

| 단계 | 모듈 | 입력 | 출력 |
|---|---|---|---|
| E1 제약 추출 | `e1_constraints.py` | D2 | `out/e1/constraints.csv`, 중심 가격 경로 |
| E2 시설 MILP + 경계 추적 | `e2_milp.py` | D1, D3, D7, E1 | `out/e2/plan_index.csv`, 계획별 스케줄 |
| E3 확률 가격 | `e3_prices.py` | D4 | `out/e3/price_sims.parquet`, 캘리브레이션 리포트 |
| E4 경로별 재평가 | `e4_revalue.py` | E2, E3, D5 | `out/e4/cost_dist.parquet`, ⑤ 유연성 가치 |
| E5 지표·경계·gap | `e5_metrics.py` | E4, D7 | `out/e5/metrics_company.csv`, frontier, gap |
| 렌더링 | `render.py` | E5 | `out/render/` 그림·공개 지표표 |

## 데이터

- 수집 템플릿: `data/CAP_data_collection_template.xlsx` (작성 지침: [`DATA_COLLECTION_GUIDE.md`](DATA_COLLECTION_GUIDE.md))
- 완성된 시트를 `data/raw/<시트명>.csv`로 저장하면 파이프라인이 스키마 검증 후 사용
- `data/sample/` — 합성 검증용 (전부 허구값, 실분석 사용 금지)

## 공개 범위

시설 단위 산출은 **비공개** (`out/render/facility_confidential/`, gitignore 처리) — 설계서 §8-2. 공개물은 기업 집계 지표 ①–⑤와 frontier/gap 차트로 한정.
