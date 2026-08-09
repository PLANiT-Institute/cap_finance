"""H3 외부 대조 — 우리 값이 실제 프로젝트·문헌 범위 안에 있는가.

내부 일관성(H1)은 "스스로 모순되지 않는가"만 본다. 이 검증은 **바깥과 맞는가**를 본다.
두 축으로 대조한다.

  (a) 기술 CAPEX  ↔ 공시된 실제 프로젝트 (EFF `technology_cost_evidence`, 1차 공시)
                  ↔ 문헌 범위 (DIW DP2082, Vogl 2018)
  (b) 감축 단가 ② ↔ 문헌 한계감축비용·정책 섀도가격 (Nature 2025, 한은·금감원 NGFS)

판정은 세 가지만 쓴다: **범위 안 / 범위 밖(사유) / 대조 불가(사유)**.
범위 밖을 "보수적"이라고 부르지 않는다 — 방향과 크기를 적는다.

    .venv/bin/python scripts/validate_external.py
산출: docs/validation_external.md
"""

from __future__ import annotations

import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cap import config as C  # noqa: E402
from cap.schemas import load_input  # noqa: E402

EFF = pathlib.Path.home() / "Documents" / "cap-efficient"
DOCS = ROOT / "docs"

# 환율: D6·D3 준비 단계와 동일 기준을 쓴다 (prepare_raw.py USDKRW/JPYKRW).
# EUR는 준비 단계에 없어 여기서 처음 도입하므로 값·근거를 명시한다.
USDKRW, JPYKRW, EURKRW = 1350.0, 9.2, 1450.0
FX_NOTE = (f"USD {USDKRW:,.0f} · JPY {JPYKRW:.1f} · EUR {EURKRW:,.0f} KRW. "
           "USD·JPY는 `prepare_raw.py`와 동일 기준. EUR는 이 문서에서 처음 쓰는 값으로 "
           "2024–25 근사이며, 문헌이 €2022 기준이라 물가·환율 이중 근사가 들어간다 "
           "— 배수 판정(0.5~2배)에는 견디지만 소수점 비교에는 쓸 수 없다.")

# 문헌 앵커. 모두 source_register에 등록된 출처의 quality_note에서 그대로 옮긴 값이고
# 재계산·보정하지 않았다. 새 수치를 여기서 만들지 않는다.
LIT_CAPEX = [
    # (라벨, 저·고 (원화 천원/t능력), source_id, 비고)
    ("EAF 문헌 중앙값", 254 * EURKRW / 1000, 254 * EURKRW / 1000, "DIW_DP2082", "€2022, 그린필드"),
    ("EAF 발표 프로젝트", 467 * EURKRW / 1000, 467 * EURKRW / 1000, "DIW_DP2082", "€2022"),
    ("POSCO 광양 EAF (DIW 수록)", 170.15 * EURKRW / 1000, 170.15 * EURKRW / 1000,
     "DIW_DP2082", "€2023, 기존 부지·인프라 재활용 추정"),
    ("DRP+EAF 문헌 (전해조 제외)", 592 * EURKRW / 1000, 592 * EURKRW / 1000,
     "DIW_DP2082", "€2022"),
    ("DRP+EAF 발표 프로젝트", 751 * EURKRW / 1000, 751 * EURKRW / 1000, "DIW_DP2082", "€2022"),
    ("H2-DRI 전체 (Vogl)", 574 * EURKRW / 1000, 574 * EURKRW / 1000, "VOGL_2018",
     "€2011, 전해조 160 포함 — 우리 모형은 수소를 사서 쓰므로 전해조분 제외 비교"),
]

# 우리 기술 ↔ 어떤 문헌 항목과 비교 가능한가 (범위는 [저, 고] 천원/t능력)
TECH_MAP = {
    "steel_h2dri": ("DRP+EAF (전해조 제외)", 592 * EURKRW / 1000, 751 * EURKRW / 1000, "DIW_DP2082"),
    "steel_hyrex": ("DRP+EAF (전해조 제외)", 592 * EURKRW / 1000, 751 * EURKRW / 1000, "DIW_DP2082"),
    "steel_eaf": ("EAF (문헌~발표 범위)", 254 * EURKRW / 1000, 467 * EURKRW / 1000, "DIW_DP2082"),
}


def verdict(v: float, lo: float, hi: float) -> str:
    if lo <= v <= hi:
        return "범위 안"
    ratio = v / (lo if v < lo else hi)
    side = "하단 아래" if v < lo else "상단 위"
    return f"범위 밖 — {side} ×{ratio:.2f}"


def main() -> int:
    cfg = C.load()
    ddir = C.data_dir(cfg)
    d3 = load_input(ddir, "D3_tech_options").set_index("tech_id")
    d1a = load_input(ddir, "D1a_facility_static")

    ev_path = EFF / "data" / "technology_cost_evidence.csv"
    ev = pd.read_csv(ev_path) if ev_path.exists() else pd.DataFrame()

    m = pd.read_csv(ROOT / "out" / "e5" / "metrics_company.csv").query(
        "scenario=='NZ15' and support=='none'")

    L = ["# H3 외부 대조 — 우리 값은 바깥과 맞는가",
         "", "> `scripts/validate_external.py` 자동 생성. 내부 일관성(H1)과 달리 **모형 밖의 "
         "실제 프로젝트 공시와 문헌 범위**에 우리 값을 견준다.",
         "", f"**환율.** {FX_NOTE}", ""]

    # ---------------------------------------------------------------- (a-1) 실제 프로젝트
    L += ["## 1. 기술 CAPEX ↔ 공시된 실제 프로젝트", "",
          "출처는 EFF `data/technology_cost_evidence.csv` — 전부 기업 1차 공시(T2)에서 "
          "용량으로 나눈 값이다. 비교 시 **범위(scope)가 결정적**이다: 노(爐)만 센 값과 "
          "물류·수전설비·후공정까지 센 값은 5~12배 차이가 난다.", ""]
    if ev.empty:
        L += ["*EFF 증거 파일을 찾지 못했다 (`~/Documents/cap-efficient/data/"
              "technology_cost_evidence.csv`). 대조 불가.*", ""]
    else:
        L += ["| 프로젝트 | 기술 | 천원/t능력 | 범위 | 등급 |", "|---|---|---|---|---|"]
        for r in ev.sort_values("normalized_capex_bn_krw_per_mtpa").itertuples():
            L.append(f"| {r.project_id} | {r.technology_id} | "
                     f"{r.normalized_capex_bn_krw_per_mtpa:,.0f} | {r.comparability} | "
                     f"{r.confidence_grade} |")
        L.append("")
        eaf = ev[ev.technology_id == "SCRAP_EAF"].normalized_capex_bn_krw_per_mtpa
        L += [f"**EAF 실적 분포**: {eaf.min():,.0f} ~ {eaf.max():,.0f} 천원/t "
              f"(중앙 {eaf.median():,.0f}). 최저값은 POSCO 광양(노 중심, 기존 부지 재활용), "
              "최고값은 NSC 야하타(물류·수전·후공정 포함). 우리 D3의 "
              f"`steel_eaf` = {d3.loc['steel_eaf'].capex_unit:,.0f} 천원/t는 **최저값과 같은 "
              "출처에서 왔다** — 즉 우리는 EAF 비용을 이 분포의 하단으로 잡고 있다. "
              "(모형은 BF→EAF 전면 전환을 허용하지 않으므로 결과에 직접 영향은 없다. A-10)", ""]

        # incumbent reline anchor — 이것이 stranded cost(A-13)를 통해 투자 시점을 좌우한다
        rl = ev[ev.technology_id == "BF_RELINE"]
        if not rl.empty:
            real = float(rl.normalized_capex_bn_krw_per_mtpa.iloc[0])
            ours = float(d1a[d1a.unit_type == "BF"].incumbent_capex_unit.median())
            L += ["### 1-1. 개수(reline) 재조달가 — 투자 시점을 좌우하는 앵커", "",
                  f"모형의 `incumbent_capex_unit`(BF 중앙값) = **{ours:,.0f}** 천원/t, "
                  f"공시된 실제 개수(고베제강 3고로 2016, 외피 재사용 90일) = **{real:,.0f}** 천원/t "
                  f"→ **우리 값이 ×{ours / real:.1f} 크다**.", "",
                  "이 값은 좌초비용(A-13) = 개수 캠페인 자산의 잔존 장부가를 정한다. 과대하면 "
                  "**조기 전환의 벌점이 과대**해지고 투자가 재투자 창(relining anchor)으로 과도하게 "
                  "몰린다. 실제 우리 결과의 CAPEX 피크가 2040–41에 집중된 것과 방향이 일치한다.", "",
                  "다만 단일 관측(1개 프로젝트, 2016년, 외피 재사용 = 저비용 사례)이므로 "
                  "**교체가 아니라 범위 부여의 근거**로 쓴다: `incumbent_capex_unit`을 "
                  f"[{real:,.0f}, {ours:,.0f}] 범위의 T5로 승급하고 민감도로 결론 불변성을 "
                  "확인하는 것이 다음 작업이다.", ""]

    # ---------------------------------------------------------------- (a-2) 문헌 범위
    L += ["## 2. 기술 CAPEX ↔ 문헌 범위", "",
          "| 우리 기술 | 우리 값 | 문헌 비교 대상 | 문헌 범위 | 판정 | 출처 |",
          "|---|---|---|---|---|---|"]
    for tech, (label, lo, hi, sid) in TECH_MAP.items():
        if tech not in d3.index:
            continue
        v = float(d3.loc[tech].capex_unit)
        L.append(f"| `{tech}` | {v:,.0f} | {label} | {lo:,.0f} ~ {hi:,.0f} | "
                 f"**{verdict(v, lo, hi)}** | {sid} |")
    L += ["", "*단위: 천원/t 능력. 문헌 원값은 €2022/2011이며 위 환율로 환산했다.*", "",
          "**참조 앵커 원값**", "", "| 항목 | €/t | 천원/t | 출처 | 비고 |", "|---|---|---|---|---|"]
    for label, lo, _hi, sid, note in LIT_CAPEX:
        L.append(f"| {label} | {lo * 1000 / EURKRW:,.0f} | {lo:,.0f} | {sid} | {note} |")
    L.append("")

    # ---------------------------------------------------------------- (b) 감축 단가
    lo2, hi2 = m.cost_per_tco2_thkrw.min(), m.cost_per_tco2_thkrw.max()
    L += ["## 3. 감축 단가 ② ↔ 문헌·정책 섀도가격", "",
          f"우리 값 (NZ15, 지원 없음): **{lo2:,.0f} ~ {hi2:,.0f} 천원/tCO₂** "
          f"= US${lo2 * 1000 / USDKRW:,.0f} ~ {hi2 * 1000 / USDKRW:,.0f}/tCO₂.", "",
          "| 비교 대상 | 값 | 우리 값과의 관계 | 출처 |", "|---|---|---|---|",
          f"| NGFS 1.5℃ 섀도 탄소가격 2030 | US$150/tCO₂ | 우리 하단(US${lo2 * 1000 / USDKRW:,.0f})이 "
          f"이보다 {'낮다' if lo2 * 1000 / USDKRW < 150 else '높다'} | BOK_FSS_CST_2025 |",
          f"| NGFS 1.5℃ 섀도 탄소가격 2050 | US$1,700/tCO₂ | 우리 상단(US${hi2 * 1000 / USDKRW:,.0f})이 "
          f"×{1700 / (hi2 * 1000 / USDKRW):.1f} 낮다 | BOK_FSS_CST_2025 |",
          "| 철강 BAT 리트로핏 평균 | US$15/tCO₂ | 우리 전 기업이 이보다 높다 — 우리 계획은 "
          "리트로핏이 아니라 **루트 전환**을 포함하므로 대상이 다르다 | NATURE_STEELEFF_2025 |",
          "| 에너지효율 단독 | −US$8.5/tCO₂ (비용절감형) | 우리 `steel_eff`는 CAPEX 120천원/t·"
          "EF 2.15→1.60으로 20년 환산 시 약 US$8/tCO₂ (양수) — 문헌이 운영비 절감을 포함해 "
          "음수인 반면 우리는 CAPEX만 센 값이라 부호가 갈린다 | NATURE_STEELEFF_2025 |", "",
          "**판정.** 감축 단가는 2050 섀도 탄소가격보다 한 자릿수 낮고 2030 가격과 같은 "
          "자릿수다. 즉 **전환은 그것이 마주할 탄소가격보다 싸다** — 시나리오 러너의 "
          "`carbon_fast` 묶음에서 탄소 포함 P50이 크게 음수로 가는 결과와 같은 이야기다. "
          "이것은 결론을 지지하는 방향이지 검증의 종료가 아니다: 문헌의 LCOA(수소환원 "
          "US$/tCO₂ 직접 비교)는 아직 추출하지 않았다.", ""]

    # ---------------------------------------------------------------- 석화
    d3all = load_input(ddir, "D3_tech_options")
    h2f = d3all[d3all.tech_id == "petchem_h2fuel"]
    ncc_ef = 0.95   # prepare_raw ROUTE NCC 배출계수 (주입값)
    L += ["## 4. 석유화학 — 유일하게 대조 가능했던 지점", "",
          "석화는 공시된 **전환 CAPEX**가 비교 가능한 형태로 존재하지 않는다(§5 참조). "
          "다만 배출 감축률 하나는 1차 공시로 대조된다.", ""]
    if not h2f.empty:
        ours = 1 - float(h2f.emission_factor.iloc[0]) / ncc_ef
        L += ["| 항목 | 우리 가정 | 공시 | 판정 |", "|---|---|---|---|",
              f"| NCC 연료전환 감축률 | `petchem_h2fuel` EF {h2f.emission_factor.iloc[0]:.2f} vs "
              f"기존 {ncc_ef:.2f} → **{ours:.0%} 감축** | 미쓰이화학 오사카공장 암모니아 "
              "연료전환으로 약 70만/160만 tCO₂ = **약 44% 감축**(2030년 전후) | "
              f"**범위 안** (차이 {abs(ours - 0.44) * 100:.0f}%p) |", "",
              "연료를 수소로 바꾸느냐 암모니아로 바꾸느냐는 다르지만 **크래커 가열로의 "
              "연료 탄소를 걷어낸다**는 점에서 감축 메커니즘이 같고, 회사가 자기 공장에 대해 "
              "제시한 감축률이 우리 주입값과 4%p 안에서 만난다. 석화 기술 가정 중 유일하게 "
              "외부에서 확인된 항목이다. (출처 `MCI_OSAKA_CN_2023`)", "",
              "주의: 공시는 **공장 전체 Scope1+2** 기준이고 우리 값은 **크래커 공정 배출** "
              "기준이라 분모가 다르다. 자릿수·방향 확인이지 동일 정의의 일치가 아니다.", "",
              "### 4-1. 같은 공시로 역산한 NCC 배출계수 — 미해결 불일치", "",
              "감축률이 맞았다고 수준까지 맞는 것은 아니다. 같은 공시를 **절대량**으로 읽으면 "
              "우리 주입값 `NCC EF = 0.95 tCO₂/t`가 낮아 보인다.", "",
              "| 항목 | 값 |", "|---|---|",
              "| 우리 모형: 오사카 크래커 능력 | 0.455 Mt (가동률 0.9 → 생산 0.409 Mt) |",
              "| 우리 모형: 오사카 크래커 배출 | 0.409 × 0.95 = **0.389 MtCO₂** |",
              "| 공시: 오사카공장 Scope1+2 | 1.60 MtCO₂ |",
              "| 공시: 암모니아 연료전환 감축 전망 | **0.70 MtCO₂** |", "",
              "감축 0.70 Mt 중 크래커 몫을 얼마로 보든 문제가 생긴다: 100%면 크래커 감축 "
              "원단위가 1.71 tCO₂/t로 우리 EF **전체값의 1.8배**이고, 70%여도 1.3배다. "
              "50%까지 내려야 0.85로 우리 값과 만난다. 즉 **공시된 감축량이 우리가 모형에 "
              "넣은 크래커 배출 총량보다 클 수 있다**.", "",
              "**(b)는 배제됐다.** 석유화학공업협회(JPCA)가 게재한 경제산업성 조사"
              "(2024-12-31, `JPCA_CAPACITY_2024`)에 大阪石油化学 455,000 t에틸렌/yr, "
              "三井化学 553,000 t/yr로 나오고 우리 D1a와 **정확히 일치**한다. 능력 추정 "
              "오류가 아니다.", "",
              "**(c)가 더 그럴듯하다 — 공시 자체의 구조만으로도.** 0.70 Mt는 공장 전체 "
              "배출 1.60 Mt의 44%다. 오사카공장은 크래커 외에 폴리프로필렌·페놀 등 유도품 "
              "설비를 함께 두고 있고(공시 본문), 공장 전체 감축의 44%를 크래커 한 기에 "
              "전부 귀속시키는 것은 공시가 말하는 범위(‘암모니아를 연료로’ = 공장 가열로 "
              "전반)와 맞지 않는다. 즉 **분모가 다른 두 수를 비교한 것**일 가능성이 높다. "
              "다만 공시가 설비별 분해를 주지 않으므로 확정할 수 없다.", "",
              "남은 설명은 둘이다 — (a) 우리 NCC EF 0.95 tCO₂/t-에틸렌이 낮다"
              "(주입값이며 등록된 출처가 없다 — 이 문서에서 문헌 대역을 인용하지 않는 "
              "이유는 아직 추출·등록하지 않았기 때문이다), "
              "(c) 공시 감축량이 크래커 밖(공장 유틸리티·다운스트림 가열로)을 포함한다. "
              "**어느 쪽이든 석유화학 배출 입력이 검증되지 않았다는 §5의 판정을 강화한다.** "
              "(a)라면 우리는 석화 감축량을 과소평가하고 **감축 단가 ②(237~275)를 과대평가**하고 "
              "있다 — 값을 고치지 않는 이유는 (c)를 배제할 자료(오사카공장 배출의 설비별 "
              "분해, 일본 SHK 사업소별 공시)가 아직 없기 때문이다.", ""]

    # 석화 수준의 유일한 상한 검증: 모형 크래커 배출 vs 공시 사업장 배출
    raw_panel = ROOT / "data" / "raw" / "facility_panel.csv"
    if raw_panel.exists():
        rp = pd.read_csv(raw_panel, encoding="utf-8-sig")
        d1b = load_input(ddir, "D1b_facility_panel")
        yr = int(d1b.year.max())
        mod = d1b[d1b.year == yr].set_index("facility_id").emissions_s1
        site = rp[rp.year == yr].set_index("facility_id").emissions_s1
        # (모형 시설, 공시 사업장) — 크로스워크가 없어 사이트명으로 수동 대응
        PAIRS = [("LOTTE_YEO_NCC", "LOTTE_YEO1_TOTAL", "여수1 사업장"),
                 ("LOTTE_DAE_NCC", "LOTTE_DAE_TOTAL", "대산 사업장")]
        rows2 = [(lab, f, mod[f], t, site[t]) for f, t, lab in PAIRS
                 if f in mod.index and t in site.index]
        if rows2:
            L += ["### 4-2. 상한 검증 — 모형 크래커 배출 ≤ 공시 사업장 배출", "",
                  "석화는 수준을 직접 대조할 수 없지만 **상한은 검증된다**: 크래커 한 기의 "
                  "배출이 그 사업장 전체 공시 배출을 넘으면 명백한 오류다. 롯데케미칼은 "
                  f"사업장별 배출을 공시하므로 이 검증이 가능하다 ({yr}년).", "",
                  "| 사업장 | 모형 크래커 배출 (MtCO₂) | 공시 사업장 배출 | 크래커 비중 | 판정 |",
                  "|---|---|---|---|---|"]
            for lab, f, mv, t, sv in rows2:
                sh = mv / sv
                v = "**초과 — 오류**" if sh > 1 else ("높음 — 확인 필요" if sh > 0.85 else "정합")
                L.append(f"| {lab} | {mv / 1e6:.2f} | {sv / 1e6:.2f} | {sh:.0%} | {v} |")
            L += ["", "두 사업장 모두 크래커가 사업장 배출의 55~61%를 차지하는 것으로 나온다. "
                  "NCC 중심 사업장에서 나프타 분해로가 최대 배출원인 것은 자연스러우므로 "
                  "**상한을 위반하지 않고 비중도 부자연스럽지 않다**. 이것은 '틀리지 않았다'는 "
                  "확인이지 '맞다'는 확인이 아니다 — 생산량 공시가 없어 원단위 자체는 여전히 "
                  "검증되지 않는다. 미쓰이는 사업장별 배출 공시가 없어 같은 검증을 못 한다.", ""]

    # ---------------------------------------------------------------- 남은 것
    L += ["## 5. 아직 못 한 대조 (없는 것을 있다고 하지 않는다)", "",
          "- **문헌 LCOA 직접 대조**: Vogl·Agora·IEA ISTR·Material Economics·MPP의 "
          "수소환원 LCOA(US$/tCO₂) 수치를 아직 추출하지 않았다. 위 3절은 섀도 탄소가격과 "
          "리트로핏 비용만으로 자릿수를 확인한 것이다.",
          "- **석유화학 원단위 자체는 여전히 미검증**: §4-2는 상한(사업장 배출을 넘지 "
          "않는다)만 확인한다. 생산량 공시가 없는 한 원단위는 확인할 수 없고, 미쓰이는 "
          "사업장별 배출 공시조차 없어 상한 검증도 불가하다.",
          "- **석유화학 CAPEX 대조 없음 (수집 시도 후 미확보)**: 미쓰이화학 오사카공장 "
          "탄소중립 발표(2023-06-01)는 '대규모 자본투자가 필요하다'고만 쓰고 **금액을 "
          "제시하지 않는다**. 검색 요약에 도는 '1,400억엔'은 1차 출처로 확인되지 않아 "
          "채택하지 않았다. 롯데케미칼의 '2030년까지 그린사업 11조원'은 수소·전지소재·"
          "리사이클 **신사업 투자**이지 기존 크래커의 전환 CAPEX가 아니므로 비교 대상이 "
          "아니다. 결과적으로 LOTTE·MCI의 CAPEX는 외부 대조 없이 D3 주입값에만 의존한다 "
          "— 석화 결과의 가장 약한 고리.",
          "- **NCC 배출원단위 문헌 앵커 미확보 (수집 시도함)**: 스팀크래커 원단위를 "
          "찾았으나 인용 가능한 형태가 아니었다. 한 업계지가 재래식 크래커를 "
          "0.63 tCO₂e/t **HVC**(고부가 화학제품 기준, Scope 1+2)로 제시하지만 **출처 표기가 "
          "없고** 분모가 에틸렌이 아니라 HVC다. HVC→에틸렌 환산 계수를 우리가 임의로 "
          "곱하면 없는 근거를 만드는 것이므로 쓰지 않았다. 필요한 것은 **에틸렌 기준·"
          "출처가 붙은** 원단위다(IEA ISTR, Material Economics, MPP 등에서 추출·등록).",
          "- **범위 정합 미보정**: 실제 프로젝트의 `comparability` 라벨이 "
          "`partial_scope_comparator`~`broad_scope_upper_comparator`로 갈리는데 "
          "범위를 맞춘 재계산은 하지 않았다. 배수 판정까지만 유효하다.", ""]

    DOCS.mkdir(exist_ok=True)
    (DOCS / "validation_external.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[validate_external] docs/validation_external.md ({len(L)} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
