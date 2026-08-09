"""M8 — 경계 퇴화 진단: 기술 일정 축에 epsilon-constraint를 걸어 재확인.

문제(D3 발견): 16개 (기업×시나리오×지원) 묶음 중 14개에서 효율경계 위 점들이 **같은 기술
일정**을 공유한다. 경계를 따라 움직이는 것은 PPA 비중(과 EPC)뿐이다. 두 가설을 가른다.

  (H-thin)  E2가 만드는 기술 일정이 얇다 — 계획 생성 문제. 다른 일정을 강제하면 경계에
            올라올 만한 것이 나온다.
  (H-bound) 재투자 창(A-10 포함)이 자유도를 없앴다 — 모형 경계에 관한 발견. 다른 일정은
            존재하지 않거나, 존재해도 정본 비용·TCaR 양쪽에서 지배당한다.

방법: 누적 배출에 상한을 걸어 비용최소해를 다시 푼다. 배출은 **계약으로는 살 수 없는 축**이다
— PPA·EPC·CCfD는 배출을 1tCO2도 바꾸지 않는다(`tests/test_pipeline.py`가 강제). 얻은 일정을
E4와 동일한 정본 절차로 재산출하고(build_profile + simulate_cost, 지원 none, E5와 같은 계약
격자), 같은 묶음의 전체 후보 집합이 만드는 파레토 경계에 대해 비지배인지 판정한다.

두 번 판정한다. **헤드라인 규약**(탄소가격 결정론)과 **L2 규약**(탄소가격 확률화, D6). 감축은
노출을 탄소(결정론)에서 전력·수소·건설비(확률)로 옮기므로, 헤드라인 규약에서는 감축이 TCaR을
**올린다**. 이 판정이 두 규약에서 갈리는지가 L2-b(헤드라인 채택)의 실제 쟁점이다.

출력: out/m8/tech_epsilon.csv, out/m8/summary.csv, out/m8/plans/
"""

from __future__ import annotations

import pathlib
import shutil
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from cap import config as C                                    # noqa: E402
from cap.e1_constraints import COMPANY_REGION                  # noqa: E402
from cap.e2_milp import _prep_company, _solve_company          # noqa: E402
from cap.e3_prices import load_shocks                          # noqa: E402
from cap.e4_revalue import _central_px                         # noqa: E402
from cap.plancost import build_profile, simulate_cost, support_params  # noqa: E402
from cap.schemas import load_input                             # noqa: E402
from uncertainty_propagation import co2_shocks, co2_vol        # noqa: E402

CAP_GRID = [0.95, 0.90, 0.80, 0.70]   # 기준 비용최소해의 누적배출 대비
CONTRACT_GRID = [(ppa, epc) for ppa in (0.0, 0.25, 0.5, 0.75, 1.0) for epc in (0, 1)]
SUPPORT = "none"                       # 헤드라인 기준


def _sched_key(plan):
    return tuple(sorted((p["facility_id"], p["tech_id"], int(p["adopt_year"])) for p in plan))


def _plan_df(rows, company, scen, ppa, epc, ccfd=0):
    rows = rows or [{"facility_id": None, "tech_id": None, "adopt_year": None, "op_year": None}]
    return pd.DataFrame(rows).assign(company_id=company, scenario=scen,
                                     ppa_share=ppa, epc=epc, ccfd=ccfd)


def _points(rows, company, scen, fac, techs, px, years, cfg, shock_sets, sp):
    """계약 격자 위 (p50, tcar) 점들. shock_sets 규약별로 하나씩."""
    out = {k: [] for k in shock_sets}
    for ppa, epc in CONTRACT_GRID:
        prof = build_profile(_plan_df(rows, company, scen, ppa, epc), fac, techs, px, years, cfg)
        for name, sh in shock_sets.items():
            sims = simulate_cost(prof, px, sh, sp, cfg)
            p50 = float(np.median(sims))
            out[name].append((p50, float(np.percentile(sims, 90) - p50), ppa, epc))
    return out


def _pareto(pts):
    """(p50, tcar) 최소화 파레토 집합."""
    return [p for p in pts if not any(q[0] <= p[0] + 1e-9 and q[1] <= p[1] + 1e-9
                                      and (q[0] < p[0] - 1e-9 or q[1] < p[1] - 1e-9) for q in pts)]


def _best_nondominated(cand, front):
    """cand 중 front에 비지배인 점 하나(가장 싼 것). 없으면 (False, 최저 p50 점)."""
    nd = [p for p in cand if not any(f[0] <= p[0] + 1e-9 and f[1] <= p[1] + 1e-9 for f in front)]
    if nd:
        return True, min(nd, key=lambda p: p[0])
    return False, min(cand, key=lambda p: p[0])


def run(cfg):
    ddir = C.data_dir(cfg)
    odir = C.out_dir(cfg, "m8")
    shutil.rmtree(odir / "plans", ignore_errors=True)
    (odir / "plans").mkdir(exist_ok=True)
    fac, d3, cal = _prep_company(cfg, ddir)
    d5 = load_input(ddir, "D5_policy_support")
    prices = pd.read_csv(C.out_dir(cfg, "e1") / "price_paths_central.csv")
    constraints = pd.read_csv(C.out_dir(cfg, "e1") / "constraints.csv")
    avail = pd.read_csv(C.out_dir(cfg, "e1") / "tech_availability.csv")
    e2idx = pd.read_csv(C.out_dir(cfg, "e2") / "plan_index.csv")
    shocks = load_shocks(cfg)
    years = np.arange(cfg.years.start, cfg.years.end + 1)
    sp = support_params(d5, SUPPORT, years)
    cvol, cn, csrc = co2_vol(cfg)
    n_sims = shocks["elec"].shape[0]
    co2 = co2_shocks(cfg, len(years), n_sims, cvol)
    shock_sets = {"headline": shocks, "l2": {**shocks, "co2": co2}}
    print(f"[m8] 탄소 변동성 {cvol:.3f} (obs {cn}, {csrc}), sims {n_sims}", flush=True)

    rows, summ = [], []
    combos = [(c, s) for c in sorted(fac.company_id.unique()) for s in cfg.scenarios]
    for n, (company, scen) in enumerate(combos, 1):
        t0 = time.time()
        args = (cfg, company, scen, fac, d3, cal, prices, constraints, avail)
        px = _central_px(prices, COMPANY_REGION[company], scen, years, cfg, cal)
        techs = d3[d3.sector == fac[fac.company_id == company].sector.iloc[0]]

        # 기준 경계: 이 묶음의 기존 후보 전체 × 계약 격자 (E5와 같은 구성, 공시계획 제외)
        base_ids = e2idx[(e2idx.company_id == company) & (e2idx.scenario == scen)
                         & ~e2idx.is_disclosed].plan_id.tolist()
        front_pts = {k: [] for k in shock_sets}
        seen = set()
        for pid in base_ids:
            df = pd.read_csv(C.out_dir(cfg, "e2") / "plans" / f"plan_{pid}.csv")
            r = [{"facility_id": x.facility_id, "tech_id": x.tech_id,
                  "adopt_year": x.adopt_year, "op_year": x.op_year}
                 for x in df.itertuples() if pd.notna(x.facility_id)]
            seen.add(_sched_key(r))
            got = _points(r, company, scen, fac, techs, px, years, cfg, shock_sets, sp)
            for k in front_pts:
                front_pts[k] += got[k]
        front = {k: _pareto(v) for k, v in front_pts.items()}

        base = _solve_company(*args, objective="cost")
        if base is None:
            raise RuntimeError(f"base solve failed for {company} {scen}")
        e0 = float(base["cum_emis_tco2"])
        print(f"[m8] {n}/{len(combos)} {company} {scen} — 기준 누적배출 {e0/1e6:.1f} MtCO2, "
              f"기존 후보 {len(base_ids)}개(고유 일정 {len(seen)}), 경계 "
              f"{len(front['headline'])}/{len(front['l2'])}점", flush=True)

        n_new = {"headline": 0, "l2": 0}
        for frac in CAP_GRID:
            s = _solve_company(*args, objective="cost", emis_cap=e0 * frac)
            if s is None:
                rows.append([company, scen, frac, e0 * frac, np.nan, np.nan, "no_incumbent",
                             False] + [np.nan] * 6)
                continue
            key = _sched_key(s["plan"])
            is_new = key not in seen
            seen.add(key)
            _plan_df(s["plan"], company, scen, 0.0, 0).assign(
                plan_id=f"M8_{company}_{scen}_{int(frac*100)}").to_csv(
                odir / "plans" / f"m8_{company}_{scen}_{int(frac*100)}.csv", index=False)
            got = _points(s["plan"], company, scen, fac, techs, px, years, cfg, shock_sets, sp)
            rec = [company, scen, frac, e0 * frac, float(s["cum_emis_tco2"]),
                   float(s["npv_cost"]), s["solve_status"], is_new]
            for k in ("headline", "l2"):
                nd, p = _best_nondominated(got[k], front[k])
                n_new[k] += nd
                rec += [nd, p[0], p[1]]
            rows.append(rec)
        summ.append([company, scen, e0, len(base_ids), len(front["headline"]), len(front["l2"]),
                     len(CAP_GRID), n_new["headline"], n_new["l2"], round(time.time() - t0)])
        print(f"[m8] {n}/{len(combos)} {company} {scen} — 비지배 헤드라인 {n_new['headline']}"
              f"/{len(CAP_GRID)}, L2 {n_new['l2']}/{len(CAP_GRID)}, {time.time()-t0:.0f}s",
              flush=True)

    out = pd.DataFrame(rows, columns=[
        "company_id", "scenario", "cap_frac", "cap_tco2", "cum_emis_tco2", "surrogate_cost_bnkrw",
        "solve_status", "schedule_is_new",
        "nondominated_headline", "p50_headline", "tcar_headline",
        "nondominated_l2", "p50_l2", "tcar_l2"])
    out.to_csv(odir / "tech_epsilon.csv", index=False)
    s = pd.DataFrame(summ, columns=["company_id", "scenario", "base_cum_emis_tco2",
                                    "base_candidates", "frontier_headline", "frontier_l2",
                                    "caps_tried", "nondominated_headline", "nondominated_l2",
                                    "seconds"])
    s.to_csv(odir / "summary.csv", index=False)
    return out, s


if __name__ == "__main__":
    o, s = run(C.load())
    print(s.to_string(index=False))
    print(o.to_string(index=False))
