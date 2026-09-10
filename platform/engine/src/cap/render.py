"""Rendering — 3-layer outputs (REDESIGN_SPEC §3 렌더링).

Company layer (public): frontier + disclosed-plan gap, TCaR factor decomposition,
CAPEX timing, cost distribution — 설계서 그림 1·2·3·4 유형.
Facility layer (out/render/facility_confidential/): adoption schedules per plan.
비공개 — .gitignore로 커밋 차단.

Usage: python -m cap render
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import config as C


def _company_figs(cfg, odir):
    e5 = C.out_dir(cfg, "e5")
    for f in [e5 / "frontier_points.csv", C.out_dir(cfg, "e4") / "summary.csv"]:
        if not f.exists():
            raise RuntimeError(f"missing {f} — run earlier stages first (python -m cap all)")
    frontier = pd.read_csv(e5 / "frontier_points.csv")
    decomp = pd.read_csv(e5 / "variance_decomp.csv")
    summary = pd.read_csv(C.out_dir(cfg, "e4") / "summary.csv")
    dist = pd.read_parquet(C.out_dir(cfg, "e4") / "cost_dist.parquet")

    for (company, scen, supp), g in frontier.groupby(["company_id", "scenario", "support"]):
        # 그림 4 type: frontier + disclosed point
        fig, ax = plt.subplots(figsize=(7, 5))
        fr = g[g.on_frontier].sort_values("tcar")
        ax.plot(fr.tcar, fr.p50, "o-", color="#1F3864", label="frontier")
        other = g[~g.on_frontier & ~g.is_disclosed]
        ax.scatter(other.tcar, other.p50, color="#9DB2CC", s=25, label="dominated plans")
        d = g[g.is_disclosed]
        if len(d):
            ax.scatter(d.tcar, d.p50, color="#C00000", marker="*", s=180, label="disclosed plan")
        ax.set_xlabel("TCaR (P90−P50, bn KRW)")
        ax.set_ylabel("Expected incremental cost (P50, bn KRW)")
        ax.set_title(f"{company} — {scen}, support={supp}")
        ax.legend()
        fig.tight_layout()
        fig.savefig(odir / f"frontier_{company}_{scen}_{supp}.png", dpi=150)
        plt.close(fig)

    # 그림 3 type: TCaR factor decomposition (frontier plans only)
    front_ids = frontier[frontier.on_frontier | frontier.is_disclosed].plan_id.unique()
    dsub = decomp[decomp.plan_id.isin(front_ids)]
    for (company, scen, supp), g in dsub.groupby(["company_id", "scenario", "support"]):
        piv = g.pivot_table(index="plan_id", columns="factor", values="variance_share")
        if piv.empty:
            continue
        fig, ax = plt.subplots(figsize=(8, 4))
        piv.plot.bar(stacked=True, ax=ax, color={"elec": "#1F3864", "h2": "#4472C4", "capex": "#9DB2CC"})
        ax.set_ylabel("variance share")
        ax.set_title(f"TCaR decomposition — {company} {scen} {supp}")
        fig.tight_layout()
        fig.savefig(odir / f"decomp_{company}_{scen}_{supp}.png", dpi=150)
        plt.close(fig)

    # 그림 2 type: cost distribution of the cost-min plan per company
    # (first scenario, last support scenario — config-driven, not hardcoded)
    scen0 = cfg.scenarios[0]
    supp0 = cfg.support_scenarios[-1]
    for company, g in summary[(summary.support == supp0) & (summary.scenario == scen0)].groupby("company_id"):
        pid = g.loc[g.p50.idxmin()].plan_id
        s = dist[(dist.plan_id == pid) & (dist.support == supp0)].npv_cost_bnkrw
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.hist(s, bins=60, color="#4472C4", alpha=0.85)
        for q, c, lb in [(50, "#1F3864", "P50"), (90, "#C00000", "P90")]:
            v = np.percentile(s, q)
            ax.axvline(v, color=c, ls="--", label=f"{lb}={v:,.0f}")
        ax.set_xlabel("NPV cost (bn KRW)")
        ax.set_title(f"Cost distribution — {company} {pid} {scen0}/{supp0}")
        ax.legend()
        fig.tight_layout()
        fig.savefig(odir / f"dist_{company}.png", dpi=150)
        plt.close(fig)


def _facility_layer(cfg):
    """CONFIDENTIAL: per-facility adoption schedule tables. Never committed."""
    fdir = C.out_dir(cfg, "render") / "facility_confidential"
    fdir.mkdir(exist_ok=True)
    e2 = C.out_dir(cfg, "e2")
    idx = pd.read_csv(e2 / "plan_index.csv")
    plans = pd.concat([pd.read_csv(e2 / "plans" / f"plan_{p}.csv") for p in idx.plan_id])
    plans.to_csv(fdir / "facility_schedules_ALL_PLANS.csv", index=False)
    (fdir / "README.txt").write_text(
        "시설 단위 산출 — 비공개 (설계서 §8-2). engagement·정책 협의용 부속서 전용.\n"
        "GitHub 커밋 금지: .gitignore에 등록되어 있음.\n")


def run(cfg: C.Config):
    odir = C.out_dir(cfg, "render")
    _company_figs(cfg, odir)
    _facility_layer(cfg)
    # 그림 1 type: CAPEX timing of cost-min plans (per company, NZ15)
    e5 = C.out_dir(cfg, "e5")
    metrics = pd.read_csv(e5 / "metrics_company.csv")
    metrics.to_csv(odir / "metrics_company_public.csv", index=False)
    return odir


if __name__ == "__main__":
    print(run(C.load()))
