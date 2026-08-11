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
from cap.calibration import _annual_vol  # noqa: E402
from cap.e1_constraints import COMPANY_REGION  # noqa: E402
from cap.e2_milp import _prep_company  # noqa: E402
from cap.e3_prices import load_shocks  # noqa: E402
from cap.e4_revalue import _central_px  # noqa: E402
from cap.plancost import (auction_share, build_profile, simulate_cost,  # noqa: E402
                          support_params)
from cap.schemas import load_input  # noqa: E402

SCEN = "NZ15"
SUPPORT = "none"
KAU = "kau_krw"  # L2: 탄소가격 확률화의 유일한 관측 계열 (D4)
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


def co2_vol(cfg) -> tuple[float, int, str]:
    """L2 — 탄소가격 변동성을 D4 `kau_krw`(K-ETS 연평균)에서 그대로 추정한다.
    투입가 변동성과 **같은 추정기**(`calibration._annual_vol`)를 쓴다 — 두 축의 크기를
    비교하는 것이 이 사이클의 목적이므로 추정 규약이 다르면 비교가 성립하지 않는다."""
    d4 = load_input(C.data_dir(cfg), "D4_price_history").copy()
    d4["date"] = pd.to_datetime(d4.date.astype(str), format="mixed")
    s = d4[d4.series_id == KAU].set_index("date").value.sort_index().dropna()
    if len(s) < 6:
        raise RuntimeError(f"D4 {KAU}: {len(s)} obs — 6+ 필요(계산 규약: calibration.py)")
    v, _ = _annual_vol(s)
    src = str(d4[d4.series_id == KAU].source_id.iloc[0])
    return float(v), len(s), src


def co2_shocks(cfg, T: int, n: int, vol: float, seed_offset: int = 0) -> np.ndarray:
    """탄소가격 충격 (n,T). 입력가 충격과 같은 규약 — GBM 로그공간 랜덤워크, 평균 1,
    0년차는 '오늘'이라 분산 없음. **상관은 넣지 않는다**(§4 한계): 탄소가격과 전력가는
    물리적으로 얽혀 있지만 D4에서 두 계열의 관측 연도가 겹치지 않아 추정할 수 없다."""
    rng = np.random.default_rng(cfg.seed + 1 + seed_offset)
    drift = -0.5 * vol**2 if str(cfg.get("shock_normalisation", "mean")) == "mean" else 0.0
    inc = rng.standard_normal((n, T)) * vol + drift
    inc[:, 0] = 0.0
    return np.exp(np.cumsum(inc, axis=1))


def evidence_bands(cfg) -> dict[str, tuple[float, float]]:
    """G2(D10) — 문헌 밴드를 base_param의 **승수 구간**으로 옮긴다.

    F3의 추첨은 base_param 하나에 승수 하나를 곱해 D3 열 전체를 스케일한다. 밴드는
    기술별로 붙으므로 그대로 대응하지 않는다. 여기서는 밴드가 붙은 기술들의 상대편차
    [low/value, high/value]의 **포락**을 쓴다 — 즉 "증거가 허용하는 최대 오설정"이고,
    좁히는 방향이 아니라 넓히는 방향의 보수적 선택이다. 어느 기술이 포락을 만드는지는
    보고서에 그대로 적는다(경계 불일치가 섞일 수 있다).
    """
    p = C.data_dir(cfg) / "D3b_tech_bands.csv"
    if not p.exists():
        return {}
    tb = pd.read_csv(p)
    d3 = pd.read_csv(C.data_dir(cfg) / "D3_tech_options.csv")
    out: dict[str, tuple[float, float]] = {}
    for r in tb.itertuples():
        base = {"capex_unit": "tech.capex", "opex_fixed": "tech.opex_fixed",
                "opex_var": "tech.opex_var", "elec_intensity": "tech.elec_intensity",
                "h2_intensity": "tech.h2_intensity",
                "emission_factor": "tech.emission_factor"}.get(r.field)
        m = d3.tech_id == r.tech_id
        if base is None or not m.any():
            continue
        v = float(d3.loc[m, r.field].iloc[0])
        if v == 0:
            continue
        lo, hi = r.value_low / v, r.value_high / v
        p0, p1 = out.get(base, (lo, hi))
        out[base] = (min(p0, lo), max(p1, hi))
    return out


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
    ap.add_argument("--co2-seeds", type=int, default=3, dest="co2_seeds")
    ap.add_argument("--bands", action="store_true",
                    help="G2: 문헌 밴드가 있는 파라미터는 ±width 대신 밴드에서 추첨")
    a = ap.parse_args()

    cfg = C.load(data_dir="data/prepared")
    cfg["simulation"] = dict(cfg["simulation"], n_sims=a.sims)
    ddir = C.data_dir(cfg)
    fac, d3, _cal = _prep_company(cfg, ddir)
    d5 = load_input(ddir, "D5_policy_support")
    prices = pd.read_csv(C.out_dir(cfg, "e1") / "price_paths_central.csv")
    shocks = {k: v[:a.sims] for k, v in load_shocks(cfg).items()}
    # e3가 저장한 경로 수가 --sims보다 적을 수 있다(config n_sims). 실제 N을 쓴다 —
    # co2 충격을 요청값으로 만들면 조용히 브로드캐스트가 깨진다.
    a.sims = int(shocks["elec"].shape[0])
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

    # --- L2 (FC4): 탄소가격을 시나리오 축(결정론)에서 확률 축으로 옮긴다.
    # increment()는 **결정론적** 탄소비용 델타(dc)를 빼므로, 확률화된 탄소가격은
    # (계획 배출 − 무대응 배출) × (충격 − 1)만큼만 남는다 — 정확히 정책 위험의 몫이다.
    cvol, cn, csrc = co2_vol(cfg)
    print(f"[L2] 탄소가격 연변동성 {cvol:.3f} ({KAU} {cn}obs, {csrc}) — 전력 대비 비교는 보고서")
    # 증분의 **부호**가 결론이 되므로(석화가 음수면 FC4는 그쪽에서 무해하다) 시드를
    # 여러 개 돌려 몬테카를로 잡음보다 큰지 확인한다. 한 시드로 부호를 주장하지 않는다.
    sets = [co2_shocks(cfg, T, a.sims, cvol, s) for s in range(a.co2_seeds)]
    pol = {}
    for co, (_p50, pdf, ppa, epc, inc_price) in base_pt.items():
        onlys, boths = [], []
        for co2 in sets:
            onlys.append(tcar(increment(cfg, fac, d3, d5, prices, co, pdf, ppa, epc,
                                        {**ones, "co2": co2})))
            boths.append(tcar(increment(cfg, fac, d3, d5, prices, co, pdf, ppa, epc,
                                        {**shocks, "co2": co2})))
        incs = [b - tcar(inc_price) for b in boths]
        pol[co] = {"tcar_co2_only": float(np.mean(onlys)),
                   "tcar_price_co2": float(np.mean(boths)),
                   "co2_increment": float(np.mean(incs)),
                   "co2_increment_lo": float(np.min(incs)),
                   "co2_increment_hi": float(np.max(incs)),
                   "co2_seeds": a.co2_seeds, "co2_vol": cvol}
        print(f"  {co:6} co2만 {pol[co]['tcar_co2_only']:9,.0f}  가격+co2 "
              f"{pol[co]['tcar_price_co2']:9,.0f}  증분 {pol[co]['co2_increment']:+9,.0f}"
              f" [{pol[co]['co2_increment_lo']:+,.0f}, {pol[co]['co2_increment_hi']:+,.0f}]bn",
              flush=True)

    bands = evidence_bands(cfg) if a.bands else {}
    used = {p: b for p, b in bands.items() if p in params}
    if a.bands:
        print("[G2] 증거 밴드 적용 " + (", ".join(f"{p} [{lo:.3f}, {hi:.3f}]"
              for p, (lo, hi) in used.items()) or "없음")
              + f" — 나머지 {len(params) - len(used)}개는 ±width 규약")

    rows = []
    for width in a.widths:
        rng = np.random.default_rng(cfg.seed)
        draws = [{p: float(rng.uniform(*used.get(p, (1 - width, 1 + width))))
                  for p in params} for _ in range(a.draws)]
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
                             width=width, draws=a.draws, sims=a.sims,
                             bands=bool(a.bands), n_banded=len(used),
                             # F26: 어느 파라미터를 뽑았는지가 결과의 일부다. 밴드 비교가
                             # "아무것도 안 움직인다"로 나올 때, 그것이 밴드가 무해해서인지
                             # 밴드가 붙은 파라미터가 추첨에서 빠져서인지를 이 열이 가른다.
                             params="|".join(params),
                             **d, **pol[co]))
            print(f"  [{width:.0%}] {co:6} price {d['tcar_price']:9,.0f} "
                  f"param {d['tcar_param']:9,.0f} joint {d['tcar_joint']:9,.0f} "
                  f"(param {d['param_share_pct']:.0f}%)", flush=True)

    df = pd.DataFrame(rows)
    odir = ROOT / "out" / "uncertainty"
    odir.mkdir(parents=True, exist_ok=True)
    # --bands는 **별도 파일**로 쓴다. 정본(±규약)을 덮으면 페이퍼 대장의 F3 key가
    # 조용히 다른 규약의 값으로 바뀐다 — G2는 정본을 교체하는 작업이 아니다.
    tag = "_bands" if a.bands else ""
    df.to_csv(odir / f"decomposition{tag}.csv", index=False)
    if not a.bands:
        _write_report(df, params, skipped, a)
    print(f"[F3] wrote {odir/f'decomposition{tag}.csv'}"
          + ("" if a.bands else " + docs/uncertainty_propagation.md"))
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
    L += _l2_section(df)
    L += ["## 5. 한계", "",
          "- **계획 고정.** 추첨마다 MILP를 다시 풀지 않는다. 파라미터가 바뀌면 최적 계획도",
          "  바뀌므로 여기 파라미터분은 **하한**이다(계획 재선택은 손실을 흡수한다).",
          "- **균등·독립 추첨.** 상관을 넣지 않았다. 원단위와 배출계수처럼 물리적으로 얽힌",
          "  파라미터를 독립으로 뽑으면 결합 분산이 과대·과소 어느 쪽으로도 갈 수 있다.",
          "- **탄소가격 충격도 독립이다**(§4). 탄소가격과 전력가는 물리적으로 얽혀 있으나",
          "  D4에서 `kau_krw`(연, 2015–2023)와 `smp_monthly`(월, 2025–)의 관측 구간이 겹치지",
          "  않아 상관을 추정할 수 없다. 양의 상관이 실제라면 §4의 증분은 **과소**다.",
          "- **폭이 규약.** §2 참조.", ""]
    (ROOT / "docs" / "uncertainty_propagation.md").write_text("\n".join(L) + "\n")


def _l2_section(df: pd.DataFrame) -> list[str]:
    """L2/FC4 — 문헌이 우리보다 앞선 축(정책·탄소가격 확률화)을 이식한 결과."""
    g = df.drop_duplicates("company_id").set_index("company_id")
    if "tcar_co2_only" not in g:
        return []
    v = float(g.co2_vol.iloc[0])
    L = ["## 4. 네 번째 칸 — 정책(탄소가격) 확률화 [L2/FC4]", "",
         "L1이 찾아낸 것 중 **문헌이 우리보다 나은 항목**은 하나였다: 그들은 탄소가격·정책을",
         "확률변수로 두고 우리는 시나리오로 고정한 채 투입가만 흔든다. 즉 우리가 보고해 온",
         "③ TCaR은 **정책 위험을 빼고 잰 위험**이다(FC4). 여기서 그 축을 켠다.", "",
         f"탄소가격 변동성은 D4 `{KAU}`(K-ETS 연평균 2015–2023, 9obs)에서 투입가와 **같은",
         f"추정기**로 뽑았다 — **연 {v:.1%}**. 전력(0.242)의 1.5배이고 우리 위험인자 중 가장 크다.",
         "충격은 GBM·평균1로 입력가와 같은 규약을 쓴다.", "",
         "| 기업 | TCaR 가격분 | TCaR 탄소만 | TCaR 가격+탄소 | 정책 증분 (시드 범위) | 증분/가격분 |",
         "|---|---|---|---|---|---|"]
    for co in g.index:
        r, base = g.loc[co], float(g.loc[co, "tcar_price"])
        L.append(f"| {CONAME[co]} | {base:,.0f} | {r.tcar_co2_only:,.0f} | "
                 f"{r.tcar_price_co2:,.0f} | {r.co2_increment:+,.0f} "
                 f"[{r.co2_increment_lo:+,.0f}, {r.co2_increment_hi:+,.0f}] | "
                 f"**{100*r.co2_increment/base:+.0f}%** |")
    L += ["", f"증분은 탄소충격 시드 {int(g.co2_seeds.iloc[0])}개의 평균이고 대괄호는 그 범위다 —",
          "**부호가 결론이 되므로 한 시드로 주장하지 않는다.**", "",
          "단위 십억원. `increment()`가 **결정론적** 탄소비용 델타를 빼므로, 확률화된 탄소가격은",
          "(계획 배출 − 무대응 배출) × (충격 − 1)만큼만 남는다 — 그 잔차가 정책 위험이다.", "",
          "**부호를 읽는 법이 중요하다.** 전환계획은 무대응보다 배출이 적으므로 탄소가격이",
          "**오를 때** 상대적으로 싸진다. 따라서 이 축의 나쁜 꼬리(P90)는 고탄소가격이 아니라",
          "**탄소가격 붕괴**다 — 투자해 놓고 정책이 물러서는 경우. TCaR을 '추가 조달 여력'으로",
          "읽는 우리 정의에서 정책 위험은 '규제 강화 위험'이 아니라 **좌초 위험**으로 들어온다.",
          "이것은 실물옵션 문헌(탄소세 상승이 투자를 앞당긴다)과 반대 방향이 아니라, 같은",
          "메커니즘을 조달 관점에서 본 것이다.", ""]
    return L


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
