"""시나리오 분석 러너 — 명명된 가정 묶음마다 결과를 다시 낸다.

"이 답은 어떤 가정에서 나온 답인가"를 실행 가능한 형태로 만든다. E1(제약)·E2(계획
탐색)은 공유하고 E3(가격 시뮬)–E5(지표)만 묶음마다 다시 돌린다. 묶음당 10초 안쪽.

**공유하는 것과 다시 하는 것**
  - E1·E2는 심볼릭 링크로 공유한다. 즉 **계획 메뉴는 고정**이고, 묶음이 바꾸는 것은
    "같은 메뉴를 다른 세계에서 평가했을 때의 값"이다. 할인율처럼 계획 선택 자체를
    바꿀 수 있는 축은 `--replan`으로 E2까지 다시 풀어야 정확하다 (묶음당 `REPLAN_MINUTES`분).
  - E3부터는 전부 다시 계산하므로 변동성·가격경로 변경이 제대로 반영된다.

    .venv/bin/python scripts/run_scenarios.py            # 전 묶음
    .venv/bin/python scripts/run_scenarios.py disc65 h2_expensive
    .venv/bin/python scripts/run_scenarios.py --replan disc65

산출: out/scenarios/<묶음>/e5/*.csv + out/scenarios/summary.csv
"""

from __future__ import annotations

import argparse
import pathlib
import shutil
import sys
import time

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cap import config as C  # noqa: E402

SCEN_ROOT = ROOT / "out" / "scenarios"


def _ramp(pairs) -> dict:
    return {int(y): float(v) for y, v in pairs}


# 각 묶음은 기업이 실제로 묻는 질문 하나에 대응한다.
BUNDLES: dict[str, tuple[str, dict]] = {
    "base": ("기준 — 할인율 5%, 확정 유상할당(2026–30 15%) + 추정 램프", {}),

    "disc35": ("할인율 3.5% — 자본비용이 낮으면(정책금융·장기채) 결론이 유지되는가",
               {"discount_rate": 0.035}),
    "disc65": ("할인율 6.5% — 자본비용이 높으면 조기 투자가 더 불리해지는가",
               {"discount_rate": 0.065}),

    "carbon_slow": ("유상할당 완화 — 2050년까지 60%에 그침 (무상할당 존속 시나리오)",
                    {"carbon_auction_share": _ramp([(2025, .10), (2030, .15), (2035, .22),
                                                    (2040, .32), (2045, .45), (2050, .60)])}),
    "carbon_fast": ("유상할당 가속 — 2040년 전량 유상 (EU CBAM 정합 압력 시나리오)",
                    {"carbon_auction_share": _ramp([(2025, .10), (2030, .15), (2035, .60),
                                                    (2040, 1.0), (2045, 1.0), (2050, 1.0)])}),

    "h2_cheap": ("수소 −30% — 대규모 수입 수소가 값싸게 들어오면", {"_px": {"h2_price": 0.7}}),
    "h2_expensive": ("수소 +30% — 청정수소 프리미엄이 유지되면", {"_px": {"h2_price": 1.3}}),
    "elec_high": ("전력 +30% — 계통요금 상승이 기존 설비를 먼저 때린다", {"_px": {"elec_price": 1.3, "re_price": 1.3}}),

    "ppa_costly": ("재생 PPA 프리미엄 2배 — 전환 설비의 전력 조달이 비싸지면",
                   {"contracts": "ppa_premium_pct*2"}),
    "retire_free": ("폐쇄 상한 40% — 시장지위 방어 제약을 절반으로 풀면",
                    {"milp": "retire_max_share=0.4"}),
    "reline_cheap": ("개수 재조달가 ×0.235 — 공시된 실제 개수(47천원/t, 고베 3고로)에 맞추면. "
                     "좌초비용이 줄어 조기 전환의 벌점이 작아진다 (H3 §1-1)",
                     {"incumbent_capex_scale": 0.235}),
    "penalty_none": ("예산 초과 벌칙 바닥 300 → 0 — 초과에 별도 제재 없이 탄소요금 2배만 무는 제도. "
                     "§5.3.1의 손익분기(36.5–39.4천원/tCO2)가 이 바닥 아래이므로, 바닥을 치우면 "
                     "조기 전환이 모형 안에서도 지는지 본다 (한계 13)",
                     {"milp": "budget_violation_floor_thkrw=0"}),
}

# E2에서만 읽히는 축 — E2를 공유한 채 돌리면 base와 **한 자리도 다르지 않은** 결과가 나온다.
# D14까지 carbon_slow·carbon_fast·ppa_costly·retire_free가 그 상태로 요약표에 실려 있었고,
# 읽는 사람에게는 "흔들어 봤는데 안 변했다"로 보였다. 흔든 적이 없다. 아래 묶음은 --replan
# 없이 도는 것을 막는다.
REPLAN_REQUIRED = {"carbon_slow", "carbon_fast", "ppa_costly", "retire_free", "penalty_none"}

# 재계획 1묶음의 실측 벽시계(분). 문서 넷이 "약 10분"을 적고 있었다. F26에서 여섯 묶음을
# 실제로 돌려 쟀다: penalty_none 12 · carbon_fast 14 · ppa_costly 21 · disc35 26 ·
# retire_free 32 · disc65 29 (2~3개 동시 실행, 10코어). 중앙값 근처인 20을 쓴다. **묶음마다
# 크게 다르고, 제약을 푸는 묶음(retire_free)이 가장 비싸다** — 상한을 40%로 올리면 탐색
# 공간이 넓어지니 당연하지만, 미루는 판단은 그 사실 없이 "약 10분"에 기대고 있었다
# (F20 이래 7사이클). 여기가 정본이고, 가이드 §4.3과 논문 §6.2는 이 상수를 인용한다.
REPLAN_MINUTES = 20


def build_cfg(name: str) -> C.Config:
    _, over = BUNDLES[name]
    cfg = C.load()
    for k, v in over.items():
        if k.startswith("_"):
            continue
        if k == "contracts" and v == "ppa_premium_pct*2":
            cfg["contracts"] = dict(cfg["contracts"],
                                    ppa_premium_pct=cfg["contracts"]["ppa_premium_pct"] * 2)
        elif k == "milp":
            key, val = v.split("=")
            cfg["milp"] = dict(cfg["milp"], **{key: float(val)})
        else:
            cfg[k] = v
    return cfg


STAGES = ["e1", "e2", "e3", "e4", "e5", "render"]


def _link_shared(dst: pathlib.Path, stages: list[str]) -> None:
    """공유할 단계는 링크하고, 묶음이 직접 쓸 단계의 낡은 링크는 **반드시 지운다**.

    지우지 않으면 재앙이 난다: 이전 실행이 남긴 `<bundle>/e2 -> out/e2` 링크가 살아 있는
    상태에서 `--replan`을 걸면 E2가 링크를 따라가 **실산출물 out/e2를 덮어쓴다**.
    실제로 한 번 그렇게 파괴됐다(2026-08-09). 공유 목록에 없는 단계는 전부 제거한다.
    """
    dst.mkdir(parents=True, exist_ok=True)
    for s in STAGES:
        tgt = dst / s
        if s in stages:
            src = ROOT / "out" / s
            if not src.exists():
                raise SystemExit(f"{src.relative_to(ROOT)} 없음 — `python -m cap all` 먼저 실행")
            if tgt.is_symlink() or tgt.exists():
                (tgt.unlink() if tgt.is_symlink() else shutil.rmtree(tgt))
            tgt.symlink_to(src.resolve(), target_is_directory=True)
        elif tgt.is_symlink():
            # 이 단계는 묶음이 직접 쓴다 — 링크를 남겨두면 원본에 쓰게 된다
            tgt.unlink()


def run_bundle(name: str, replan: bool) -> pd.DataFrame:
    label, over = BUNDLES[name]
    cfg = build_cfg(name)
    dst = SCEN_ROOT / name
    shared = ["e1"] if replan else ["e1", "e2"]
    _link_shared(dst, shared)
    cfg["out_dir"] = str(dst)

    # 가격 수준 이동은 E1 중앙경로에 걸리므로 E1 산출을 그 묶음 전용으로 다시 쓴다
    px = over.get("_px")
    if px:
        e1 = dst / "e1_local"
        if e1.exists():
            shutil.rmtree(e1)
        shutil.copytree((ROOT / "out" / "e1").resolve(), e1)
        p = pd.read_csv(e1 / "price_paths_central.csv")
        for var, f in px.items():
            # D2b names the series h2_price / elec_price / re_price — matching the
            # bare factor name silently scaled nothing and every price bundle
            # returned the base answer
            mask = p.variable == var
            if not mask.any():
                raise SystemExit(f"{name}: 가격 변수 '{var}' 없음. "
                                 f"있는 것: {sorted(p.variable.unique())}")
            p.loc[mask, "value"] *= f
        p.to_csv(e1 / "price_paths_central.csv", index=False)
        (dst / "e1").unlink()
        (dst / "e1").symlink_to(e1.resolve(), target_is_directory=True)

    from cap import e2_milp, e3_prices, e4_revalue, e5_metrics
    if replan:
        e2_milp.run(cfg)
    e3_prices.run(cfg)
    e4_revalue.run(cfg)
    e5_metrics.run(cfg)

    m = pd.read_csv(dst / "e5" / "metrics_company.csv")
    a = pd.read_csv(dst / "e5" / "affordability.csv")
    out = m.merge(a[["company_id", "scenario", "support", "capex_peak_bnkrw",
                     "capex_peak_to_ebitda", "netdebt_to_ebitda_post", "funding_verdict"]],
                  on=["company_id", "scenario", "support"], how="left")
    out.insert(0, "bundle", name)
    out.insert(1, "bundle_label", label)
    out.insert(2, "replanned", replan)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("bundles", nargs="*", default=None,
                    help=f"기본 전체. 선택지: {', '.join(BUNDLES)}")
    ap.add_argument("--force", action="store_true",
                    help="재계획본을 평가 전용 결과로 덮어쓴다 (기본은 보존)")
    ap.add_argument("--replan", action="store_true",
                    help=f"E2 MILP까지 다시 푼다 (계획 선택 채널 포함, 묶음당 ~{REPLAN_MINUTES}분)")
    a = ap.parse_args()
    names = a.bundles or list(BUNDLES)
    bad = [n for n in names if n not in BUNDLES]
    if bad:
        raise SystemExit(f"모르는 묶음: {bad}. 선택지: {list(BUNDLES)}")
    inert = sorted(set(names) & REPLAN_REQUIRED) if not a.replan else []
    if inert:
        if a.bundles:                    # 이름을 찍어 부른 것 — 침묵하면 가짜 결과가 남는다
            raise SystemExit(f"{inert}: E2에서만 읽히는 축이다. --replan 없이 돌리면 base와 "
                             f"같은 수가 나오고 그것이 요약표에 '검증됨'으로 남는다. "
                             f"--replan을 붙여라 (묶음당 ~{REPLAN_MINUTES}분).")
        print(f"[scenario] --replan 없음 — E2 전용 축 {inert} 건너뜀", flush=True)
        names = [n for n in names if n not in inert]

    SCEN_ROOT.mkdir(parents=True, exist_ok=True)
    path = SCEN_ROOT / "summary.csv"
    # 재계획(--replan) 결과는 20분씩 든 계산이다. 평가 전용 실행이 그것을 조용히 덮어쓰면
    # I1 강건성 결과가 산출물에서 사라진다 — 실제로 한 번 그렇게 잃었다(2026-08-09).
    if path.exists() and not a.replan:
        prev = pd.read_csv(path)
        keep = set(prev[prev.replanned].bundle) & set(names)
        if keep:
            print(f"[scenario] 재계획본 보존: {sorted(keep)} 건너뜀 "
                  f"(덮어쓰려면 --force 또는 --replan)", flush=True)
            names = [n for n in names if n not in keep] if not a.force else names

    frames = []
    for n in names:
        t0 = time.time()
        print(f"[scenario] {n} — {BUNDLES[n][0]}", flush=True)
        frames.append(run_bundle(n, a.replan))
        print(f"[scenario] {n} done in {time.time() - t0:.1f}s", flush=True)

    if not frames:
        print("[scenario] 새로 계산한 묶음이 없다 — 기존 요약 유지"); return 0
    df = pd.concat(frames, ignore_index=True)
    if path.exists():                               # 부분 실행은 기존 표를 갱신
        old = pd.read_csv(path)
        df = pd.concat([old[~old.bundle.isin(names)], df], ignore_index=True)
    df.sort_values(["bundle", "company_id", "scenario", "support"]).to_csv(path, index=False)

    v = df[(df.scenario == "NZ15") & (df.support == "none")]
    for label, col, unit in [("② 감축단가", "cost_per_tco2_thkrw", "천원/tCO₂"),
                             ("③ TCaR", "tcar_bnkrw", "십억원"),
                             ("탄소 포함 P50", "p50_incl_carbon_bnkrw", "십억원")]:
        print(f"\n=== {label} ({unit}, NZ15 · support=none)")
        print(v.pivot_table(index="bundle", columns="company_id", values=col).round(0).to_string())
    print(f"\n-> {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
