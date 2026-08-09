"""F3 — 파라미터 불확실성을 가격 불확실성과 **함께** 전파한다 (AUTOPILOT v2 §4-F3).

지금까지 TCaR(=P90−P50)은 **가격 충격 하나만**의 산물이었다. 파라미터는 F2에서 한 번에
하나씩(OAT) 흔들어 보기만 했고, 그 폭이 TCaR 안에 들어온 적이 없다. 그래서 보고서의
"③ TCaR"은 사실 "**파라미터를 다 안다고 가정했을 때의** 위험"이다.

여기서는 상위 파라미터를 동시에 추첨해 두 축을 분해한다.

    TCaR_price  : 파라미터 중앙값 고정, 가격만 확률적   (= 지금까지 보고한 값)
    TCaR_param  : 가격 중심경로 고정, 파라미터만 확률적
    TCaR_joint  : 둘 다 확률적 (D × N 풀링)
    interaction : joint − price − param  (분위수는 가법적이지 않다 — 잔차를 숨기지 않는다)

**계획은 고정한다.** 추첨마다 MILP를 다시 풀면 사이클에 들어오지 않는다(F2와 같은 한계).
따라서 이 수치는 "메뉴가 정해진 뒤 남는 불확실성"이고, 계획 선택 경로는 I1/I2가 덮는다.

**추첨 폭은 근거가 아니라 규약이다.** `docs/parameter_inventory.csv` 415행 중 [low, high]가
있는 것은 18행뿐이다. 그래서 F2와 같은 ±30% 균등분포를 쓰고, 폭 의존성을 드러내기 위해
±15%도 함께 돌려 보고한다(선형이면 두 배).

    .venv/bin/python scripts/uncertainty_propagation.py [--draws 200] [--sims 2000]
산출: out/uncertainty/decomposition.csv, docs/uncertainty_propagation.md
"""

from __future__ import annotations

import argparse
import pathlib
import sys
from dataclasses import replace

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cap import config as C  # noqa: E402
from cap.e1_constraints import COMPANY_REGION  # noqa: E402
from cap.e2_milp import _prep_company  # noqa: E402
from cap.e3_prices import load_shocks  # noqa: E402
from cap.e4_revalue import _central_px  # noqa: E402
from cap.plancost import (auction_share, build_profile, simulate_cost,  # noqa: E402
                          support_params)
from cap.schemas import load_input  # noqa: E402

SCEN = "NZ15"
SUPPORT = "none"
CONTRACTS = [(0.0, 0), (0.5, 0), (1.0, 0), (1.0, 1)]
CONAME = {"POSCO": "POSCO", "NSC": "Nippon Steel",
          "LOTTE": "LOTTE Chemical", "MCI": "Mitsui Chemicals"}

# F2 랭킹의 base_param → 이 모형에서 그 파라미터를 흔드는 방법.
# 랭킹에 있어도 여기 없는 항목은 추첨에서 빠지고 그 사실을 보고한다.
SPEC = {
    "cfg.discount": ("cfg", "discount_rate"),
    "price.elec": ("px", "elec"),
    "price.re": ("px", "re"),
    "price.h2": ("px", "h2"),
    "price.co2": ("px", "co2"),
    "price.coal": ("px", "coal"),
    "price.gas": ("px", "gas"),
    "tech.capex": ("d3", "capex_unit"),
    "tech.opex_fixed": ("d3", "opex_fixed"),
    "tech.opex_var": ("d3", "opex_var"),
    "tech.elec_intensity": ("d3", "elec_intensity"),
    "tech.h2_intensity": ("d3", "h2_intensity"),
    "tech.emission_factor": ("d3", "emission_factor"),
    "fac.capacity": ("fac", "capacity"),
    "fac.ef_inc": ("fac", "ef_inc"),
    "fac.elec_int_inc": ("fac", "elec_int_inc"),
    "fac.coal_int_inc": ("fac", "coal_int_inc"),
    "fac.margin": ("fac", "margin_kthou_t"),
    "vol.elec": ("vol", "elec"),
    "vol.h2": ("vol", "h2"),
    "vol.capex": ("vol", "capex"),
}


def _scale(df: pd.DataFrame, col: str, f: float) -> pd.DataFrame:
    d = df.copy()
    d[col] = d[col] * f
    return d


def _empty(company: str) -> pd.DataFrame:
    return pd.DataFrame([{"facility_id": None, "tech_id": None, "adopt_year": None,
                          "op_year": None, "company_id": company, "scenario": "-",
                          "ppa_share": 0.0, "epc": 0, "ccfd": 0}])


def perturb(cfg, fac, d3, shocks, mult: dict[str, float]):
    """Apply a draw of multipliers. Returns (cfg, fac, d3, px_scale, shocks).

    `vol` multipliers act on the log of the shock array, so a deterministic
    (all-ones) shock array stays all-ones — volatility uncertainty is a
    price-channel parameter by construction and cannot show up in the
    parameter-only pass. That is a property of the decomposition, not a bug.
    """
    c2, f2, d32, sh2, pxs = cfg, fac, d3, shocks, {}
    for name, m in mult.items():
        kind, tgt = SPEC[name]
        if kind == "px":
            pxs[tgt] = m
        elif kind == "d3":
            d32 = _scale(d32, tgt, m)
        elif kind == "fac":
            f2 = _scale(f2, tgt, m)
        elif kind == "cfg":
            c2 = C.Config({**c2, tgt: c2[tgt] * m})
        elif kind == "vol":
            sh2 = {k: (np.exp(np.log(v) * m) if k == tgt else v) for k, v in sh2.items()}
    return c2, f2, d32, pxs, sh2


def increment(cfg, fac, d3, d5, prices, company, plan_df, ppa, epc, shocks,
              px_scale=None) -> np.ndarray:
    """NPV cost increment over do-nothing, net of the deterministic carbon-cost
    delta — the same quantity E5 takes P50/P90 of. Returns (N,) KRW billions."""
    years = np.arange(cfg.years.start, cfg.years.end + 1)
    disc = (1 + cfg.discount_rate) ** -(years - years[0])
    px = _central_px(prices, COMPANY_REGION[company], SCEN, years, cfg, None)
    if px_scale:
        px = {k: v * px_scale.get(k, 1.0) for k, v in px.items()}
    sp = support_params(d5, SUPPORT, years)
    auc = auction_share(years, cfg)

    base = build_profile(_empty(company), fac, d3, px, years, cfg)
    bs = simulate_cost(base, px, shocks, sp, cfg)
    cb = float((base.emissions * px["co2"] * auc / 1000.0 * disc).sum() * 1e-6)

    prof = build_profile(plan_df, fac, d3, px, years, cfg)
    dc = float((prof.emissions * px["co2"] * auc / 1000.0 * disc).sum() * 1e-6) - cb
    s = simulate_cost(replace(prof, ppa=ppa, epc=epc), px, shocks, sp, cfg)
    return s - bs - dc


def tcar(x: np.ndarray) -> float:
    return float(np.percentile(x, 90) - np.median(x))


def decompose(inc_price: np.ndarray, inc_param: np.ndarray,
              inc_joint: np.ndarray) -> dict[str, float]:
    """TCaR by source. Quantiles are not additive, so the interaction term is
    reported rather than assumed away."""
    tp, ta, tj = tcar(inc_price), tcar(inc_param), tcar(inc_joint)
    return {"tcar_price": tp, "tcar_param": ta, "tcar_joint": tj,
            "interaction": tj - tp - ta,
            "param_share_pct": 100.0 * ta / tj if tj else np.nan,
            "p50_joint": float(np.median(inc_joint)),
            "p50_price": float(np.median(inc_price))}


def pick_params(k: int) -> list[str]:
    rank = pd.read_csv(ROOT / "out" / "sensitivity" / "ranking.csv")
    keep = [p for p in rank.base_param if p in SPEC]
    return keep[:k], [p for p in rank.base_param[:k] if p not in SPEC]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=200)
    ap.add_argument("--sims", type=int, default=2000)
    ap.add_argument("--params", type=int, default=10)
    ap.add_argument("--widths", type=float, nargs="+", default=[0.15, 0.30])
    a = ap.parse_args()

    cfg = C.load(data_dir="data/prepared")
    cfg["simulation"] = dict(cfg["simulation"], n_sims=a.sims)
    ddir = C.data_dir(cfg)
    fac, d3, _cal = _prep_company(cfg, ddir)
    d5 = load_input(ddir, "D5_policy_support")
    prices = pd.read_csv(C.out_dir(cfg, "e1") / "price_paths_central.csv")
    shocks = {k: v[:a.sims] for k, v in load_shocks(cfg).items()}
    T = shocks["elec"].shape[1]
    ones = {k: np.ones((1, T)) for k in shocks}

    idx = pd.read_csv(C.out_dir(cfg, "e2") / "plan_index.csv")
    idx = idx[(idx.scenario == SCEN) & (~idx.is_disclosed)]
    plans: dict[str, list[pd.DataFrame]] = {}
    for co, g in idx.groupby("company_id"):
        seen, lst = set(), []
        for pid in g.plan_id:
            pdf = pd.read_csv(C.out_dir(cfg, "e2") / "plans" / f"plan_{pid}.csv")
            key = tuple(sorted((r.facility_id, r.tech_id, int(r.adopt_year))
                               for r in pdf.itertuples() if pd.notna(r.tech_id)))
            if key not in seen:
                seen.add(key)
                lst.append(pdf)
        plans[co] = lst

    params, skipped = pick_params(a.params)
    print(f"[F3] 추첨 파라미터 {len(params)}: {', '.join(params)}")
    if skipped:
        print(f"[F3] 상위 {a.params} 중 미구현 제외: {', '.join(skipped)}")

    # --- base point: cost-min plan × contract at central parameters (F2와 동일 규칙)
    base_pt = {}
    for co, plist in plans.items():
        best = None
        for pdf in plist:
            for ppa, epc in CONTRACTS:
                inc = increment(cfg, fac, d3, d5, prices, co, pdf, ppa, epc, shocks)
                p50 = float(np.median(inc))
                if best is None or p50 < best[0]:
                    best = (p50, pdf, ppa, epc, inc)
        base_pt[co] = best
        print(f"  {co:6} 기준점 P50 {best[0]:9,.0f}bn  TCaR(price) {tcar(best[4]):9,.0f}bn")

    rows = []
    for width in a.widths:
        rng = np.random.default_rng(cfg.seed)
        draws = [{p: float(rng.uniform(1 - width, 1 + width)) for p in params}
                 for _ in range(a.draws)]
        for co, (_p50, pdf, ppa, epc, inc_price) in base_pt.items():
            joint, param_only = [], []
            for mult in draws:
                c2, f2, d32, pxs, sh2 = perturb(cfg, fac, d3, shocks, mult)
                joint.append(increment(c2, f2, d32, d5, prices, co, pdf, ppa, epc, sh2, pxs))
                c2, f2, d32, pxs, sh1 = perturb(cfg, fac, d3, ones, mult)
                param_only.append(increment(c2, f2, d32, d5, prices, co, pdf, ppa, epc,
                                            sh1, pxs))
            d = decompose(inc_price, np.concatenate(param_only), np.concatenate(joint))
            rows.append(dict(company_id=co, scenario=SCEN, support=SUPPORT,
                             width=width, draws=a.draws, sims=a.sims, **d))
            print(f"  [{width:.0%}] {co:6} price {d['tcar_price']:9,.0f} "
                  f"param {d['tcar_param']:9,.0f} joint {d['tcar_joint']:9,.0f} "
                  f"(param {d['param_share_pct']:.0f}%)", flush=True)

    df = pd.DataFrame(rows)
    odir = ROOT / "out" / "uncertainty"
    odir.mkdir(parents=True, exist_ok=True)
    df.to_csv(odir / "decomposition.csv", index=False)
    _write_report(df, params, skipped, a)
    print(f"[F3] wrote {odir/'decomposition.csv'} + docs/uncertainty_propagation.md")
    return 0


def _write_report(df: pd.DataFrame, params, skipped, a) -> None:
    proc = _process_column()
    L = ["# F3 파라미터 불확실성 전파 — ③ TCaR은 무엇의 위험인가", "",
         "> `scripts/uncertainty_propagation.py` 자동 생성.", "",
         "지금까지 보고한 ③ TCaR은 **가격 충격만**의 산물이다. 파라미터는 F2에서 한 번에 하나씩",
         "흔들어 보기만 했고 그 폭이 위험 지표 안에 들어온 적이 없다. 즉 우리는 **파라미터를",
         "다 안다고 가정한 세계의 위험**을 조원 단위로 적어 왔다. 여기서 그 가정을 뗀다.", "",
         f"추첨 파라미터 {len(params)}개(F2 랭킹 상위): `" + "`, `".join(params) + "`.",
         (f"상위 {a.params} 중 이 모형에서 흔들 수단이 없어 제외: `"
          + "`, `".join(skipped) + "`.") if skipped else "",
         f"추첨 {a.draws}회 × 가격 경로 {a.sims}개, 시드 고정.", "",
         "## 1. 분해", "",
         "| 기업 | 폭 | TCaR 가격분 | TCaR 파라미터분 | TCaR 결합 | 상호작용 | 파라미터 몫 |",
         "|---|---|---|---|---|---|---|"]
    for r in df.itertuples():
        L.append(f"| {CONAME[r.company_id]} | ±{r.width:.0%} | {r.tcar_price:,.0f} | "
                 f"{r.tcar_param:,.0f} | {r.tcar_joint:,.0f} | {r.interaction:+,.0f} | "
                 f"**{r.param_share_pct:.0f}%** |")
    L += ["", "단위 십억원, NZ15·지원 none, 비용최소 계획 고정. **분위수는 가법적이지 않으므로**",
          "가격분+파라미터분≠결합이고 그 잔차를 상호작용 열에 그대로 둔다.", ""]

    wide = df.pivot_table(index="company_id", columns="width", values="tcar_param")
    if wide.shape[1] >= 2:
        w = sorted(wide.columns)
        L += ["## 2. 이 크기는 얼마나 우리가 고른 폭에 달려 있나", "",
              "추첨 폭은 근거가 아니라 규약이다 — `docs/parameter_inventory.csv` 415행 중",
              "[low, high]가 있는 것은 18행뿐이다. 폭을 절반으로 줄이면:", "",
              f"| 기업 | ±{w[0]:.0%} | ±{w[-1]:.0%} | 배율 |", "|---|---|---|---|"]
        for co in wide.index:
            lo, hi = wide.loc[co, w[0]], wide.loc[co, w[-1]]
            L.append(f"| {CONAME[co]} | {lo:,.0f} | {hi:,.0f} | ×{hi/lo:.2f} |"
                     if lo else f"| {CONAME[co]} | {lo:,.0f} | {hi:,.0f} | — |")
        L += ["", "배율이 2에 가까우면 파라미터분은 폭에 **선형**이다 — 즉 이 열의 숫자는",
              "'우리가 모르는 정도'를 그대로 되돌려 줄 뿐이고, 읽는 사람은 ±30%라는 규약을",
              "함께 읽어야 한다. 이 표를 근거 밴드로 바꾸는 것이 G2·G3의 목적이다.", ""]

    L += ["## 3. 세 번째 칸 — 확률과정 선택분", "",
          "가격분·파라미터분과 나란히 놓아야 할 것이 하나 더 있다. **어떤 확률과정을 쓰는가**는",
          "파라미터가 아니라 모형 선택이고, D4에서 우리 표본으로는 원리적으로 가를 수 없음이",
          "확인됐다(검정력 ≈ 유의수준). 크기는 I3이 이미 쟀다 — 재계산하지 않고 옮긴다.", ""]
    if proc:
        wmax = df.width.max()
        pm = df[df.width == wmax].set_index("company_id").tcar_param
        L += [f"| 기업 | TCaR GBM | TCaR OU(반감기 10년) | 과정 선택분(절대값) | "
              f"파라미터분 (±{wmax:.0%}) | 어느 쪽이 큰가 |",
              "|---|---|---|---|---|---|"]
        inv = {v: k for k, v in CONAME.items()}
        for name, gbm, ou, gap in proc:
            p = float(pm.get(inv[name], np.nan))
            L.append(f"| {name} | {gbm:,.0f} | {ou:,.0f} | {abs(ou - gbm):,.0f} | {p:,.0f} | "
                     f"**{'과정 선택' if abs(ou - gbm) > p else '파라미터'}** |")
        stale = _cited_vs_current(proc)
        if stale:
            L += ["", "**인용값 정합 경고**: I3 표의 GBM 열이 현재 `out/e5/metrics_company.csv`와 "
                  "어긋난다 — " + ", ".join(stale) + ". I3 문서가 그 이후의 파이프라인 변경 "
                  "전에 생성됐다는 뜻이므로, 위 '과정 선택분'은 그만큼의 오차를 안고 있다. "
                  "`scripts/process_alternative.py` 재실행이 필요하다."]
        L += ["", "GBM·OU 값은 `docs/process_alternative.md` §2에서 인용(재계산 없음), 차이는",
              "절대값(십억원)으로 환산했다. **두 열의 크기가 같은 자릿수다** — ③의 불확실성은",
              "'무엇을 모르는가'만큼이나 '무엇을 골랐는가'에 달려 있고, 후자는 D4에서 확인했듯",
              "데이터로 줄일 수 없다. 파라미터 승급(G2·G3)이 줄일 수 있는 것은 앞 칸뿐이다.", ""]
    L += ["## 4. 한계", "",
          "- **계획 고정.** 추첨마다 MILP를 다시 풀지 않는다. 파라미터가 바뀌면 최적 계획도",
          "  바뀌므로 여기 파라미터분은 **하한**이다(계획 재선택은 손실을 흡수한다).",
          "- **균등·독립 추첨.** 상관을 넣지 않았다. 원단위와 배출계수처럼 물리적으로 얽힌",
          "  파라미터를 독립으로 뽑으면 결합 분산이 과대·과소 어느 쪽으로도 갈 수 있다.",
          "- **폭이 규약.** §2 참조.", ""]
    (ROOT / "docs" / "uncertainty_propagation.md").write_text("\n".join(L) + "\n")


def _cited_vs_current(proc, tol: float = 0.01) -> list[str]:
    """I3이 인용한 GBM TCaR이 지금의 E5 헤드라인과 같은가. 손으로 옮긴 수치가 파이프라인
    변경 뒤 조용히 낡는 것이 이 저장소의 반복 실패 방식이라 자동으로 대조한다."""
    f = ROOT / "out" / "e5" / "metrics_company.csv"
    if not f.exists():
        return []
    cur = (pd.read_csv(f).query("scenario=='NZ15' and support=='none'")
           .set_index("company_id").tcar_bnkrw)
    inv = {v: k for k, v in CONAME.items()}
    out = []
    for name, gbm, _ou, _d in proc:
        c = float(cur.get(inv[name], np.nan))
        if np.isfinite(c) and c and abs(gbm - c) / c > tol:
            out.append(f"{name} 인용 {gbm:,.0f} 대 현재 {c:,.0f} ({100*(gbm-c)/c:+.1f}%)")
    return out


def _process_column() -> list[tuple[str, float, float, str]]:
    """I3 표(GBM vs OU)의 TCaR 열을 그대로 읽는다 — 재계산하지 않는다."""
    p = ROOT / "docs" / "process_alternative.md"
    if not p.exists():
        return []
    out = []
    for ln in p.read_text().splitlines():
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) == 7 and c[0] in CONAME.values():
            out.append((c[0], float(c[4].replace(",", "")),
                        float(c[5].replace(",", "")), c[6]))
    return out


if __name__ == "__main__":
    raise SystemExit(main())
