from __future__ import annotations

import csv
import html
import json
from pathlib import Path
from typing import Any


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Cannot write empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def write_frontier_svg(
    path: Path,
    scenario_id: str,
    metrics: list[dict[str, object]],
    frontier_plan_ids: set[str],
) -> None:
    width, height = 840, 540
    margin_left, margin_right, margin_top, margin_bottom = 90, 35, 55, 75
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom
    xs = [float(row["expected_cost_p50_kkrw_per_tco2"]) for row in metrics]
    ys = [float(row["tcar_kkrw_per_tco2"]) for row in metrics]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    x_pad = max((x_max - x_min) * 0.12, 5.0)
    y_pad = max((y_max - y_min) * 0.15, 5.0)
    x_min, x_max = x_min - x_pad, x_max + x_pad
    y_min, y_max = max(0.0, y_min - y_pad), y_max + y_pad

    def x_coord(value: float) -> float:
        return margin_left + (value - x_min) / (x_max - x_min) * plot_width

    def y_coord(value: float) -> float:
        return margin_top + (y_max - value) / (y_max - y_min) * plot_height

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text x="{margin_left}" y="30" font-family="Arial" font-size="20" font-weight="700" fill="#17365d">Capital Allocation Frontier — {html.escape(scenario_id)}</text>',
    ]
    for tick in range(6):
        x_value = x_min + (x_max - x_min) * tick / 5
        x = x_coord(x_value)
        lines.append(f'<line x1="{x:.1f}" y1="{margin_top}" x2="{x:.1f}" y2="{margin_top + plot_height}" stroke="#e3e8ef"/>')
        lines.append(f'<text x="{x:.1f}" y="{margin_top + plot_height + 25}" text-anchor="middle" font-family="Arial" font-size="12" fill="#536273">{x_value:.0f}</text>')
        y_value = y_min + (y_max - y_min) * tick / 5
        y = y_coord(y_value)
        lines.append(f'<line x1="{margin_left}" y1="{y:.1f}" x2="{margin_left + plot_width}" y2="{y:.1f}" stroke="#e3e8ef"/>')
        lines.append(f'<text x="{margin_left - 12}" y="{y + 4:.1f}" text-anchor="end" font-family="Arial" font-size="12" fill="#536273">{y_value:.0f}</text>')
    frontier_rows = sorted(
        (row for row in metrics if str(row["plan_id"]) in frontier_plan_ids),
        key=lambda row: float(row["expected_cost_p50_kkrw_per_tco2"]),
    )
    if frontier_rows:
        points = " ".join(
            f'{x_coord(float(row["expected_cost_p50_kkrw_per_tco2"])):.1f},{y_coord(float(row["tcar_kkrw_per_tco2"])):.1f}'
            for row in frontier_rows
        )
        lines.append(f'<polyline points="{points}" fill="none" stroke="#173b6c" stroke-width="4"/>')
    for row in metrics:
        x = x_coord(float(row["expected_cost_p50_kkrw_per_tco2"]))
        y = y_coord(float(row["tcar_kkrw_per_tco2"]))
        plan_id = html.escape(str(row["plan_id"]))
        disclosed = bool(row["is_disclosed_plan"])
        if disclosed:
            points = f"{x:.1f},{y - 9:.1f} {x + 9:.1f},{y:.1f} {x:.1f},{y + 9:.1f} {x - 9:.1f},{y:.1f}"
            lines.append(f'<polygon points="{points}" fill="#8b241e"/>')
        else:
            fill = "#173b6c" if plan_id in frontier_plan_ids else "#aab4c0"
            lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{fill}"/>')
        lines.append(f'<text x="{x + 10:.1f}" y="{y - 10:.1f}" font-family="Arial" font-size="12" fill="#243447">{plan_id}</text>')
    lines.extend([
        f'<line x1="{margin_left}" y1="{margin_top + plot_height}" x2="{margin_left + plot_width}" y2="{margin_top + plot_height}" stroke="#667788" stroke-width="1.5"/>',
        f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_height}" stroke="#667788" stroke-width="1.5"/>',
        f'<text x="{margin_left + plot_width / 2:.1f}" y="{height - 20}" text-anchor="middle" font-family="Arial" font-size="14">Expected transition cost P50 (kKRW/tCO2)</text>',
        f'<text x="24" y="{margin_top + plot_height / 2:.1f}" transform="rotate(-90 24 {margin_top + plot_height / 2:.1f})" text-anchor="middle" font-family="Arial" font-size="14">TCaR P90-P50 (kKRW/tCO2)</text>',
        '</svg>',
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_markdown_report(
    path: Path,
    path_count: int,
    metrics: list[dict[str, object]],
    summary: dict[str, Any],
    candidate_robust_summary: list[dict[str, object]] | None = None,
    refined_candidate_robust_summary: list[dict[str, object]] | None = None,
    refined_candidate_metrics: list[dict[str, object]] | None = None,
    refined_candidate_facility_rows: list[dict[str, object]] | None = None,
    refined_candidate_resource_rows: list[dict[str, object]] | None = None,
    resource_benchmarks: list[dict[str, object]] | None = None,
    transition_projects: list[dict[str, object]] | None = None,
    technology_cost_evidence: list[dict[str, object]] | None = None,
) -> None:
    rows = [
        "# 한·일 철강 Capital Allocation Pathway — 실행 결과",
        "",
        f"POSCO, Nippon Steel, JFE Steel, Kobe Steel의 공식 기업 총량과 명시적 모델 추정치에 상관 가격경로 {path_count:,}개를 적용했다.",
        "",
        "## 내부 1.5°C 스트레스에서 공시경로 고정 포트폴리오 재평가",
        "",
        "| 기업 | 통합 실행가능성 | 미충족 제약 | 순현금 P50 | 탄소회피가치 | 경제적 Net P50 | TCaR | CAPEX | P90/EBITDA |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    company_order = list(summary["companies"])
    for company_id in company_order:
        current = next(
            row for row in metrics
            if row["company_id"] == company_id
            and row["scenario_id"] == "ACCELERATED_15C"
            and bool(row["is_disclosed_plan"])
        )
        constraints = []
        if not bool(current["carbon_budget_feasible"]):
            constraints.append(f"탄소예산({current['first_budget_breach_year']})")
        if not bool(current["resource_constraints_feasible"]):
            constraints.append(f"자원·계통({current['first_resource_breach_year']})")
        if not bool(current["construction_concurrency_feasible"]):
            constraints.append("동시공사")
        if not bool(current["failure_risk_constraint_feasible"]):
            constraints.append("기술실패위험")
        rows.append(
            "| {company} | {feasible} | {constraints} | {cash:,.0f} | {carbon:,.0f} | {p50:.1f} | {tcar:.1f} | {capex:,.0f} | {stress:.2f}x |".format(
                company=current["company_name"],
                feasible="PASS" if bool(current["scenario_feasible"]) else "FAIL",
                constraints="·".join(constraints) if constraints else "—",
                cash=float(current["net_cash_cost_after_support_p50_bn_krw"]),
                carbon=float(current["avoided_carbon_cost_value_p50_bn_krw"]),
                p50=float(current["expected_cost_p50_kkrw_per_tco2"]),
                tcar=float(current["tcar_kkrw_per_tco2"]),
                capex=float(current["aligned_capex_bn_krw"]),
                stress=float(current["p90_cost_to_ebitda_x"]),
            )
        )
    rows.extend([
        "",
        "단위: 순현금·탄소회피가치·CAPEX는 십억원 NPV, Net P50·TCaR은 천원/tCO₂. 탄소회피가치는 인식된 회피비용이며 현금수익이 아니다.",
        "",
        "## 생성 후보와 강건성 진단",
        "",
        f"시설 기술조합·전환연도·계약 프로필 {int(summary.get('generated_candidate_count', 0)):,}개를 두 활성 시나리오에서 결정론적으로 선별하고, 회사별 대표 {int(summary.get('stochastic_candidate_count', 0)):,}개를 seed당 {int(summary.get('candidate_path_count', 0)):,}경로로 재평가했다.",
        "",
        "| 기업 | 확률평가 후보 | 모든 활성 시나리오 적격 | 강건 경계 | λ=1 후보 | 최대후회 P50 | 최악 TCaR |",
        "|---|---:|---:|---:|---|---:|---:|",
    ])
    robust_rows = candidate_robust_summary or []
    for company_id in company_order:
        company_rows = [
            row for row in robust_rows if row["company_id"] == company_id
        ]
        lambda_choice = next(
            (row for row in company_rows if bool(row["lambda_1_optimal"])),
            None,
        )
        rows.append(
            "| {company} | {count:,} | {eligible:,} | {frontier:,} | {choice} | {regret} | {risk} |".format(
                company=summary["companies"][company_id]["company_name"],
                count=len(company_rows),
                eligible=sum(bool(row["robust_feasible"]) for row in company_rows),
                frontier=sum(bool(row["robust_frontier"]) for row in company_rows),
                choice=(lambda_choice["candidate_id"] if lambda_choice else "—"),
                regret=(
                    f"{float(lambda_choice['maximum_regret_p50_kkrw_per_tco2']):.1f}"
                    if lambda_choice else "—"
                ),
                risk=(
                    f"{float(lambda_choice['worst_case_tcar_kkrw_per_tco2']):.1f}"
                    if lambda_choice else "—"
                ),
            )
        )
    rows.extend([
        "",
        "최대후회는 각 시나리오에서 가장 낮은 적격 후보 P50 대비 비용 차이의 최댓값이다. λ=1 후보는 최대후회 + 최악 TCaR을 최소화한 강건 적격안이다. 공식 GCAM 경로가 아직 비활성이므로 현재 강건성은 공시경로와 내부 스트레스 사이의 예비 진단이다.",
        "",
        "## 상위 강건후보 고정밀 재평가",
        "",
        f"결정론 기준으로 고정한 상위 후보 {int(summary.get('refined_candidate_count', 0)):,}개를 후보당·시나리오당 {int(summary.get('refined_candidate_path_count', 0)):,}경로로 다시 평가하고 전력·수소입력·건설 CAPEX의 정확한 3요인 Shapley 분산배분을 재계산했다.",
        "",
        "| 기업 | 정밀 후보 | λ=1 후보 | 최대후회 P50 | 최악 TCaR | 최악경로 전력 | 수소입력 | 건설비 |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
    ])
    refined_robust_rows = refined_candidate_robust_summary or []
    refined_metric_rows = refined_candidate_metrics or []
    refined_facility_rows = refined_candidate_facility_rows or []
    refined_resource_rows = refined_candidate_resource_rows or []
    refined_choices: dict[str, dict[str, object]] = {}
    refined_worst_metrics: dict[str, dict[str, object]] = {}
    for company_id in company_order:
        company_refined = [
            row for row in refined_robust_rows if row["company_id"] == company_id
        ]
        choice = next(
            (row for row in company_refined if bool(row["lambda_1_optimal"])),
            None,
        )
        choice_metrics = [
            row
            for row in refined_metric_rows
            if choice is not None
            and row["company_id"] == company_id
            and row["candidate_id"] == choice["candidate_id"]
        ]
        worst_metric = (
            max(
                choice_metrics,
                key=lambda row: float(row["tcar_kkrw_per_tco2"]),
            )
            if choice_metrics else None
        )
        if choice is not None:
            refined_choices[company_id] = choice
        if worst_metric is not None:
            refined_worst_metrics[company_id] = worst_metric
        rows.append(
            "| {company} | {count:,} | {choice} | {regret} | {risk} | {power} | {hydrogen} | {capex} |".format(
                company=summary["companies"][company_id]["company_name"],
                count=len(company_refined),
                choice=(choice["candidate_id"] if choice else "—"),
                regret=(
                    f"{float(choice['maximum_regret_p50_kkrw_per_tco2']):.1f}"
                    if choice else "—"
                ),
                risk=(
                    f"{float(choice['worst_case_tcar_kkrw_per_tco2']):.1f}"
                    if choice else "—"
                ),
                power=(
                    f"{100.0 * float(worst_metric['electricity_shapley_variance_share']):.1f}%"
                    if worst_metric else "—"
                ),
                hydrogen=(
                    f"{100.0 * float(worst_metric['hydrogen_shapley_variance_share']):.1f}%"
                    if worst_metric else "—"
                ),
                capex=(
                    f"{100.0 * float(worst_metric['capex_shapley_variance_share']):.1f}%"
                    if worst_metric else "—"
                ),
            )
        )
    rows.extend([
        "",
        "요인비중은 총비용 구성비가 아니라 최악 TCaR 시나리오의 분산을 모든 8개 요인부분집합으로 재평가해 배분한 Shapley 비중이다. 같은 seed의 공통난수를 사용하며 상관·비선형 상호작용 때문에 개별 기여가 음수일 수도 있지만 합계는 전체 분산과 일치한다. 수소 제조의 전력가격 노출은 전력 요인에 포함되고, `수소입력`은 비전력 전해조 비용성분만 흔든다.",
        "",
        "### λ=1 정밀 추천의 시설·배출·공급여력",
        "",
        "아래 시설·배출·자원값은 각 기업 λ=1 추천의 **최악 TCaR 시나리오**를 선택한 뒤, 해당 시나리오 안에서 계산한다. 자원 활용률은 그 경로의 2026–2040 최댓값이며 두 활성 시나리오 전체의 보수적 최댓값은 아니다.",
        "",
        "| 기업 | 기준배출 | 2040 잔여배출 | 연간 감축 | 정렬 CAPEX | 스크랩 최대활용 | 수소 최대활용 | 증분계통 최대활용 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for company_id in company_order:
        choice = refined_choices.get(company_id)
        worst_metric = refined_worst_metrics.get(company_id)
        scenario_id = str(worst_metric["scenario_id"]) if worst_metric else ""
        facility_choice_rows = [
            row
            for row in refined_facility_rows
            if choice is not None
            and row["company_id"] == company_id
            and row["candidate_id"] == choice["candidate_id"]
            and row["scenario_id"] == scenario_id
        ]
        resource_choice_rows = [
            row
            for row in refined_resource_rows
            if choice is not None
            and row["company_id"] == company_id
            and row["candidate_id"] == choice["candidate_id"]
            and row["scenario_id"] == scenario_id
        ]
        peak = lambda field: max(
            (float(row[field]) for row in resource_choice_rows), default=0.0
        )
        rows.append(
            "| {company} | {baseline:.1f} | {residual:.1f} | {abatement:.1f} | {capex:,.0f} | {scrap:.1f}% | {hydrogen:.1f}% | {grid:.1f}% |".format(
                company=summary["companies"][company_id]["company_name"],
                baseline=sum(
                    float(row["baseline_emissions_mtco2"])
                    for row in facility_choice_rows
                ),
                residual=sum(
                    float(row["emissions_2040_mtco2"])
                    for row in facility_choice_rows
                ),
                abatement=sum(
                    float(row["annual_avoided_emissions_mtco2"])
                    for row in facility_choice_rows
                ),
                capex=sum(
                    float(row["aligned_capex_bn_krw"])
                    for row in facility_choice_rows
                ),
                scrap=peak("scrap_utilization_pct"),
                hydrogen=peak("hydrogen_utilization_pct"),
                grid=peak("incremental_grid_utilization_pct"),
            )
        )
    project_rows = transition_projects or []
    cost_evidence_rows = technology_cost_evidence or []
    evidence_by_project = {
        row["project_id"]: row for row in cost_evidence_rows
    }
    rows.extend([
        "",
        "단위: 배출·감축은 MtCO₂/년, CAPEX는 십억원. 표의 자원 최대활용은 각 기업 최악 TCaR 시나리오 내 전 기간 최댓값이다. 공급한도와 활용률은 아직 `model_estimate`이므로 계약·계통 승인 전 screening 지표다.",
        "",
        f"정밀 후보집합은 seed가 아니라 중앙가격 screening으로 고정해 반복 간 후보 변경을 막았다. 최대후회 기준점은 이 shortlist 안의 시나리오별 최저 적격안이며, 전체 {int(summary.get('generated_candidate_count', 0)):,}개 후보를 모두 {int(summary.get('refined_candidate_path_count', 0)):,}경로로 평가한 결과는 아니다.",
        "",
        "## 공식 전환 프로젝트 증거층",
        "",
        "공식 프로젝트의 총사업비·용량·지원·가동시점을 모델 입력과 분리해 보존한다. 부두·물류·전력·후공정·혼합공정 등 포함범위가 다르므로 같은 범위로 bridge하기 전에는 기술 CAPEX를 직접 치환하지 않는다.",
        "",
        "| 기업 | 프로젝트 | 단계 | 용량 | 총사업비 | 최대지원 | 가동시점 | 공시 원단위 | 모델 연결 | 출처 |",
        "|---|---|---|---:|---:|---:|---|---:|---|---|",
    ])
    for item in project_rows:
        evidence = evidence_by_project.get(item["project_id"])
        capacity = item.get("capacity_mtpa")
        capex = item.get("capex_bn_krw")
        support = item.get("government_support_pct")
        rows.append(
            "| {company} | {project} | {stage} | {capacity} | {capex} | {support} | {timing} | {unit} | {mapping} | [원문]({url}) |".format(
                company=summary["companies"][item["company_id"]]["company_name"],
                project=item["project_name"],
                stage=item["project_status"],
                capacity=(f"{float(capacity):.2f} Mtpa" if capacity is not None else "—"),
                capex=(f"{float(capex):,.0f} bn KRW" if capex is not None else "미공시"),
                support=(f"{100 * float(support):.1f}%" if support is not None else "—"),
                timing=item["operation_start_label"],
                unit=(
                    f"{float(evidence['normalized_capex_bn_krw_per_mtpa']):,.0f} bn/Mtpa"
                    if evidence else "—"
                ),
                mapping=item["model_mapping_status"],
                url=item["source_url"],
            )
        )
    benchmark_rows = resource_benchmarks or []
    rows.extend([
        "",
        "## 공식 국가 자원 벤치마크",
        "",
        "아래 값은 회사 공급한도를 대체하지 않는다. 국가 전체·서로 다른 단위의 정책 및 인프라 맥락을 별도 감사층으로 보존한 것이다.",
        "",
        "| 국가 | 자원 | 연도 | 공식 값 | 범위 | 출처 |",
        "|---|---|---:|---:|---|---|",
    ])
    for item in benchmark_rows:
        value = item.get("benchmark_value")
        formatted = (
            f"{float(value):,.2f} {item['unit']}" if value is not None else "정성 정책"
        )
        rows.append(
            "| {country} | {resource} | {year} | {value} | {scope} | [{source}]({url}) |".format(
                country=item["country_code"],
                resource=item["resource_type"],
                year=item["benchmark_year"],
                value=formatted,
                scope=item["scope"],
                source=item["source_org"],
                url=item["source_url"],
            )
        )
    rows.extend([
        "",
        "## 산출 파일",
        "",
        "- `plan_metrics.csv`: 기업 수준 ①~⑤ 지표와 스트레스 비율",
        "- `facility_schedule.csv`: 시설별 전환 기술·시점·CAPEX",
        "- `frontier_membership.csv`: 시나리오별 경계 포함 여부",
        "- `scenario_comparison.csv`: 동일 설비·기술·연도의 시나리오 간 signed ΔP50·ΔTCaR·ΔNPV·ΔCAPEX",
        "- `candidate_portfolios.csv`: 생성된 전체 후보의 시설 액션·계약 프로필·공통분모",
        "- `candidate_screening.csv`: 전체 후보의 시나리오별 탄소·자원·공사·실패 제약 진단",
        "- `candidate_scenario_metrics.csv`: 대표 후보의 P50·P90·TCaR·현금·탄소가치·정책지원",
        "- `candidate_robust_summary.csv`: 최대후회·최악 TCaR·강건 경계·λ 최적점",
        "- `candidate_scenario_comparison.csv`: 동일 생성 후보의 signed 시나리오 변화",
        "- `refined_candidate_scenario_metrics.csv`: 고정된 상위 후보의 전체 경로·요인분해 재평가",
        "- `refined_candidate_robust_summary.csv`: 정밀 shortlist의 최대후회·강건경계·λ 최적점",
        "- `refined_candidate_facility_schedule.csv`: 정밀 후보별 시설 기술·전환연도·비용·감축",
        "- `refined_candidate_resource_profile.csv`: 연도별 스크랩·수소·증분계통 수요·공급·여유",
        "- `resource_benchmarks.csv`: 공식 국가 자원·계통 맥락(회사 공급한도와 비비교)",
        "- `transition_projects.csv`: 공식 전환 프로젝트의 용량·총사업비·지원·시점과 모델 연결상태",
        "- `technology_cost_evidence.csv`: 공식 총사업비의 공통통화·용량 환산과 범위 경고",
        "- `data_gap_registry.csv`: 입력별 남은 증거격차와 P0/P1 편입 게이트",
        "- `gcam_manifest_validation.json`: GCAM release·target XML·query 매니페스트 무결성과 활성화 게이트",
        "- `run_summary.json`: gap, λ별 최적 계획, 실행 메타데이터",
        "- `frontier_*.svg`: 기업 고유 효율 경계",
        "",
        "## 해석 제한",
        "",
        "기업 생산·배출·재무 총량은 공식 원문을 사용했다. 설비 포트폴리오는 기업 공시경로에서 한 번 고정한 뒤 다른 시나리오에 그대로 재평가한다. 탄소예산 또는 스크랩·수소·전력망·동시공사·실패위험 제약을 충족하지 못한 계획은 비용을 보존하되 효율경계와 추천에서 제외한다. 생성 후보는 기업 공시안이 아니라 모델 조합이며, 설비별 배분, 재투자연도, 공통 기술비용, 환율, 계약비율, 정책지원, 내부 1.5°C 스트레스와 현실 제약 한도는 검증 전 모델 추정치다. GCAM 1.5°C/2.0°C는 공식 9.1 실행·추출·hash 검증이 끝나기 전까지 활성 시나리오가 아니다.",
        "",
    ])
    path.write_text("\n".join(rows), encoding="utf-8")
