# (가제) 공시된 전환계획은 비용·위험 평면에서 어디에 있는가
### 철강·석유화학 4사의 기업 내 자본배분 효율경계

> **상태: 골격 (M1, 2026-08-10 D3).** 본문은 아직 없다. 이 문서가 정하는 것은
> **무엇을 주장하고, 그 주장이 어떻게 틀릴 수 있는가**다. M2–M7이 절을 채운다.
>
> 규칙: 본문 수치는 전부 `out/`에서 온다. §0의 대장에 등록된 값만 인용하고,
> `tests/test_paper_numbers.py`가 대장과 `out/`의 일치를 강제한다. 문헌 인용은
> `data/raw/source_register.csv`의 `source_id`로만 한다.

---

## 0. 수치 대장 (자동 검증)

기준 실행: `NZ15` 시나리오 · 지원 `none` · N=20,000. 화폐 단위 십억원, ②는 천원/tCO₂.

| key | value | 출처 |
|---|---|---|
| m2_posco | 115.0 | out/e5/metrics_company.csv |
| m2_nsc | 155.8 | out/e5/metrics_company.csv |
| m2_mci | 241.7 | out/e5/metrics_company.csv |
| m2_lotte | 279.2 | out/e5/metrics_company.csv |
| tcar_posco | 26752.6 | out/e5/metrics_company.csv |
| tcar_nsc | 32973.1 | out/e5/metrics_company.csv |
| tcar_mci | 864.1 | out/e5/metrics_company.csv |
| tcar_lotte | 2242.2 | out/e5/metrics_company.csv |
| gap_cost_nsc | 1164.4 | out/e5/gap.csv |
| gap_risk_nsc | 4364.3 | out/e5/gap.csv |
| gap_cost_mci | 712.5 | out/e5/gap.csv |
| gap_risk_mci | 969.5 | out/e5/gap.csv |
| hedge_rate_posco | 2.44 | out/e5/frontier_points.csv |
| hedge_rate_nsc | 3.27 | out/e5/frontier_points.csv |
| hedge_rate_mci | 0.21 | out/e5/frontier_points.csv |
| hedge_rate_lotte | 0.24 | out/e5/frontier_points.csv |
| frontier_single_schedule_groups | 14 | out/e5/frontier_points.csv |
| frontier_groups_total | 16 | out/e5/frontier_points.csv |
| gap_companies | 2 | out/e5/gap.csv |
| tcar_param30_posco | 11664.9 | out/uncertainty/decomposition.csv |
| tcar_param30_nsc | 15578.0 | out/uncertainty/decomposition.csv |
| tcar_param30_mci | 229.1 | out/uncertainty/decomposition.csv |
| tcar_param30_lotte | 590.9 | out/uncertainty/decomposition.csv |
| param_share30_posco | 40.6 | out/uncertainty/decomposition.csv |
| param_share30_nsc | 43.9 | out/uncertainty/decomposition.csv |
| param_share30_mci | 26.6 | out/uncertainty/decomposition.csv |
| param_share30_lotte | 26.4 | out/uncertainty/decomposition.csv |
| tcar_co2only_posco | 16510.3 | out/uncertainty/decomposition.csv |
| co2_increment_posco | 2444.0 | out/uncertainty/decomposition.csv |
| tcar_co2only_nsc | 15464.5 | out/uncertainty/decomposition.csv |
| co2_increment_nsc | 1223.0 | out/uncertainty/decomposition.csv |
| tcar_co2only_mci | 75.0 | out/uncertainty/decomposition.csv |
| co2_increment_mci | -37.2 | out/uncertainty/decomposition.csv |
| tcar_co2only_lotte | 162.7 | out/uncertainty/decomposition.csv |
| co2_increment_lotte | -100.3 | out/uncertainty/decomposition.csv |

`hedge_rate` = (최소비용 계획 → 최소위험 계획으로 옮길 때 줄어드는 TCaR) ÷ (늘어나는 P50).
단위 없는 교환비이며 1보다 크면 "위험 1원을 1원 미만으로 산다"는 뜻이다.

---

## 1. 연구질문 (한 문장)

> **공시된 기업 전환계획을, 같은 탄소예산 제약 아래 그 기업이 선택할 수 있었던 계획 전체와
> 같은 (기대비용, 꼬리위험) 평면에 놓았을 때, 그 거리는 얼마이며 무엇이 그 거리를 만드는가.**

답의 형태: 기업×시나리오마다 원화 두 숫자 — 비용 거리(`gap_cost`)와 위험 거리(`gap_risk`).
검증 가능성: 같은 데이터·같은 제약으로 제3자가 재실행하면 같은 두 숫자가 나와야 한다
(시드 고정 + 데이터 패키지, `docs/seed_stability.md`).

## 2. 기여 3개

L1 문헌 지도(`docs/literature_map.md`)의 판정을 그대로 쓴다. 기여 진술은 그 판정보다 넓으면 안 된다.

**C1. 공시계획을 비용·위험 평면에 좌표화한다.**
`NATCOMM_APA_2026`이 같은 대상(CA100+ 우선기업의 공시 전환계획)을 **배출 축**에서 다루면서
비용은 모형에 넣지 않는다고 스스로 밝힌다. 우리는 그들이 비워 둔 축을 채운다. 따라서 기여는
"아무도 안 한 것"이 아니라 **"그들이 안 한다고 적은 것"** 이고, 그 편이 방어하기 쉽다.

**C2. 꼬리위험을 조달 언어로 옮긴다.** TCaR = P90 − P50을 원화로 표기해, 위험을 "분산"이 아니라
**"이 계획을 실행하려면 추가로 확보해야 하는 자금"** 으로 읽게 한다. CVaR보다 꼬리 정보를 덜
쓰지만 재무담당자가 그대로 쓸 수 있는 단위다.

**C3. 위험 축의 가격표를 계산한다.** 효율경계 위에서 위험 1원을 줄이는 데 드는 기대비용을
기업별로 잰다(`hedge_rate`). 철강 2사는 2.4–3.3, 석유화학 2사는 0.21–0.24 — **같은 헤지 수단이
철강에서 10배 이상 잘 듣는다.** 이 비대칭은 지금까지 어디에도 보고된 것을 확인하지 못했다.

## 3. 반증가능 주장

각 주장은 "이런 관측이 나오면 우리가 틀린 것"과 그 관측을 만드는 코드 경로를 함께 적는다.
M5(강건성·한계 절)가 이 표를 그대로 이어받는다.

| # | 주장 | 현재 증거 | 이렇게 나오면 틀린 것 | 검사 경로 |
|---|---|---|---|---|
| **FC1** | 공시계획은 효율경계 위에 있지 않고, 그 거리는 무시할 수 없다 | NSC `gap_cost` 1,164 / `gap_risk` 4,364, MCI 713 / 969 (십억원) | 같은 예산·제약 아래 공시계획보다 P50과 TCaR이 **동시에** 낮은 계획이 존재하지 않으면(=gap≈0) 무너진다 | `src/cap/e5_metrics.py::_gap`, `out/e5/gap.csv` |
| **FC2** | 기대값에서 싼 계획이 꼬리에서 비싸다 | NZ15·none에서 최소비용→최소위험 이동이 NSC P50 +8.7% / TCaR −45.9%, POSCO +9.3% / −35.1% | 경계가 사실상 한 점이거나(교환비 ≈ 0) 최소비용 계획이 최소위험 계획과 같으면 무너진다 | `out/e5/frontier_points.csv` |
| **FC3** | 위험 헤지의 가격은 업종별로 다르고, 철강이 유리하다 | `hedge_rate` 철강 2.44·3.27 대 석화 0.21·0.24 | 전력집약도·계약 가능량을 통제했을 때 차이가 사라지면 업종 효과가 아니라 규모 효과다 | 미작성 — **M5에서 통제 필요** |
| **FC4** | 우리 TCaR은 정책 위험을 **빼고** 잰 값이다 | **검사 완료 (L2, D6) — 업종별로 답이 갈렸다.** 탄소가격을 확률 축(K-ETS 실측 연변동성 36.3%)으로 옮기면 TCaR 증분은 철강 +2,444 / +1,223, 석화 **−100 / −37** (십억원, 시드 3개 평균) | 철강에서는 반증되지 않았다 — 정책 축만으로도 TCaR 16,510 / 15,465로 파라미터분(11,665 / 15,578)과 같은 자릿수다. 석화에서는 **반증됐다**: 증분이 음수이므로 이 한계는 그쪽에서 실무적으로 무해하다 | `scripts/uncertainty_propagation.py` §4, `out/uncertainty/decomposition.csv` |
| **FC5** | 두 독립 구현이 같은 수준을 본다 | FIN ② POSCO 115가 EFF 실행가능 후보 범위 26.6–155.9 안에 든다 | FIN 값이 EFF 실행가능 범위 **밖**으로 나가면 수준 자체가 의심된다 | `docs/cross_model_check.md`, `tests/test_independence.py` |

## 4. 이 골격이 드러낸 문제 — 경계가 기술 선택이 아니라 계약으로 그려진다

M1을 쓰면서 처음 확인한 것이고, C1의 범위를 좁힌다.

16개 (기업×시나리오×지원) 묶음 중 **14개에서 효율경계 위 점들이 전부 같은 기술 일정**을
공유한다. 즉 경계를 따라 움직이는 것은 무엇을 언제 짓느냐가 아니라 **PPA 비중 0→100%** 뿐이다.
LOTTE는 후보 기술 일정 자체가 1개라 선택집합이 없다.

이것을 지금 적어 두는 이유는 심사자가 반드시 여기를 친다는 것이다 — *"자본배분 효율경계라고
부르지만 실제로는 PPA 헤지비율 곡선 아닌가."* 가능한 답은 둘이고, 둘 중 무엇인지 아직 모른다.

1. **계획 생성이 얇다** — E2 MILP가 만드는 서로 다른 기술 일정이 기업당 1–5개뿐이다.
   (`out/e2/plan_index.csv` 기준 NZ15·none: LOTTE 1, MCI 3, NSC 3, POSCO 2)
2. **진짜로 한 일정이 지배한다** — 재투자 창과 기술 집합(A-10: BF→EAF 전면 전환 불허)이
   자유도를 없앤다. 그렇다면 결과가 아니라 **모형 경계에 관한 발견**이고 그렇게 써야 한다.

→ 백로그 **M8** 신설: ε-constraint를 기술 일정 축에서도 걸어 계획 다양성을 강제한 뒤
경계가 여전히 계약 축으로만 움직이는지 본다. 답이 (2)로 확정되면 논문 제목의 "자본배분"을
"계약·자본 혼합 배분"으로 바꾸는 것이 정직하다.

## 5. 절 구조와 각 절의 재료

| 절 | 사이클 | 재료 (이미 존재) |
|---|---|---|
| 1 서론 | M6 (D15) | `docs/literature_map.md` §0 판정 요약 |
| 2 선행연구 | M6 (D15) | 같은 문서 §1–3, `NATCOMM_APA_2026`·`CA100_BENCHMARK_V22`·`ACCR_BF_RELINE_2025` |
| 3 방법 | M2 (D7) | `METHODOLOGY.md` 수식. **E2 대리목적함수와 E4 정본의 관계를 정면 기술** |
| 4 데이터 | M3 (D9) | `docs/parameter_inventory.csv`, `docs/data_audit.md`, `docs/data_gap_registry.md` (공백 4건) |
| 5 결과 | M4 (D11) | §0 대장 + `out/e5/*` 그림(경계·λ 접점·정책 wedge) |
| 6 강건성 | M5 (D14) | `docs/robustness_structural.md`, `docs/seed_stability.md`, `docs/validation_backtest.md`, `docs/validation_external.md`, F3(D5) |
| 7 한계·반증 | M5 (D14) | §3 표 + §4 + 아래 §6 |
| 8 결론 | M7 | — |

## 6. 미리 적어 두는 한계 (심사자가 먼저 찾을 것들)

각 항목은 이미 저장소에 근거가 있다. 숨기지 않고 본문에 싣는다.

1. **표본이 4사다.** 통계적 일반화를 주장하지 않는다. 주장의 형태는 "이 방법으로 재면 이런
   값이 나온다"이지 "산업 전체가 이렇다"가 아니다.
2. **gap이 4사 중 2사만 계산된다.** POSCO는 모형 규칙(A-10)이 공시된 EAF를 허용하지 않고,
   LOTTE는 공시된 CCUS가 기술집합 D3에 없다 (`out/e2/disclosed_skipped.csv`). **공시 해상도
   문제가 아니라 모형 경계 문제**이며, 이대로 쓰면 "gap이 큰 기업만 골랐다"는 선택편의로 읽힌다.
3. **NSC 후향 검증이 기준을 넘는다.** 배출강도 재현 오차 평균 +15.7%, 최대 17.5% (기준 ±10%).
   회사 총량 재척도 뒤에는 −0.6%로 맞지만, 재척도 전 능력가중 표준값은 맞지 않는다.
4. **석유화학 2사는 원단위 대조가 불가능하다.** 생산량 공시가 없어 0.95 tCO₂/t는 검증되지 않은
   주입값이다.
5. **정책 위험이 헤드라인에서 빠져 있다** (FC4). L2(D6)에서 크기를 쟀다 — 철강은 정책 축
   하나로 TCaR 16.5조·15.5조가 나오고 이는 파라미터 불확실성과 같은 자릿수다. 헤드라인 ③은
   여전히 탄소가격 결정론 위에 있으므로 **철강 TCaR은 하한으로 읽어야 한다**. 석화는 증분이
   음수라 이 유보가 필요 없다. 방향도 통념과 다르다 — 전환계획은 배출이 적어 탄소가격 상승 시
   상대적으로 싸지므로, 정책 위험은 '규제 강화'가 아니라 **탄소가격 붕괴에 따른 좌초**로 들어온다.
6. **개수 단가 200 천원/t의 외부 앵커가 [47, 269]로 5배 폭이다.** 점 추정이 아니라 폭을 전파해야
   한다 (`docs/validation_external.md` §1-1).
7. **§4의 경계 퇴화.**
8. **TCaR의 절대값은 확률과정 선택 위에 서 있고, 그 선택은 검정으로 정해지지 않는다.**
   GBM 대신 반감기 10년 OU를 쓰면 TCaR이 40~48% 줄어든다(`docs/process_alternative.md`).
   ADF로 그 대안을 80% 검정력에서 배제하려면 월별 관측 **약 4,740개(≈395년)**가 필요하다
   (`docs/price_process_test.md`). 따라서 이것은 데이터로 메울 공백이 아니라 **명시적 선택**이며,
   방법 절(M2)에 그렇게 적는다 — 보수적(위험을 크게 잡는) 쪽인 GBM을 고르고 대안의 크기를
   함께 보고한다. 독립 구현 EFF가 반감기 2년 OU를 쓰고 있다는 사실도 같이 적는다(G8).
9. **③ TCaR은 파라미터를 다 안다고 가정한 세계의 위험이었다** (F3, D5). 상위 10개 파라미터를
   ±30%로 동시에 추첨해 전파하면 파라미터가 만드는 몫이 결합 TCaR의 **철강 41~44%,
   석유화학 26~27%**다(`docs/uncertainty_propagation.md`). 그 크기는 추첨 폭에 거의 정확히
   비례하고(폭 2배 → ×2.08~2.14), 폭 자체는 근거가 아니라 규약이다 —
   `docs/parameter_inventory.csv` 415행 중 [low, high]를 가진 것이 18행뿐이기 때문이다.
   따라서 본문은 파라미터분을 **절대값이 아니라 "±30%를 가정했을 때의 몫"으로만** 인용한다.
   더 중요한 것은 그 옆칸이다: 확률과정 선택이 만드는 폭(한계 8)이 파라미터분과 **같은
   자릿수이거나 더 크고**, 이쪽은 데이터로 줄일 수 없다.

## 7. 타깃 저널 후보

| 후보 | 왜 | 왜 아닐 수 있나 |
|---|---|---|
| **Energy Policy** (1순위) | 기업 단위 사례 + 정책 함의 조합을 받는다. 최적화 모형과 정책 서사를 같이 실을 수 있는 몇 안 되는 곳 | 방법 기여만으로는 약함 — 정책 함의 절이 실해야 한다 |
| **Energy Economics** (2순위) | 비용·위험 최적화가 중심 기여인 점이 맞는다 | 인과 식별을 기대하는 심사자를 만나면 4사 사례로는 버티기 어렵다 |
| **Climate Policy** | 공시–계획 gap 서사가 정확히 이 저널의 관심 | 최적화 상세를 실을 지면이 부족 |
| **Nature Communications / Joule** | `NATCOMM_APA_2026`과 직접 대화 가능 | 4사 표본과 §4 경계 퇴화가 해결되기 전에는 무리 |

**결정**: M6 서론을 Energy Policy 독자 기준으로 쓴다. §4가 (2)로 정리되면 Energy Economics로
상향 검토.
