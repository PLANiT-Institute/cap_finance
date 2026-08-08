from __future__ import annotations

import argparse
from pathlib import Path

from .dashboard import run_repeated_analysis
from .loader import load_data
from .pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cap-efficient",
        description="Run the illustrative Capital Allocation Pathway model.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="run schedules, simulation, and frontier analysis")
    run.add_argument("--data-dir", type=Path, default=Path("data"))
    run.add_argument("--output-dir", type=Path, default=Path("outputs"))
    run.add_argument("--paths", type=int, default=None, help="override Monte Carlo path count")
    run.add_argument("--seed", type=int, default=None, help="override random seed")

    dashboard = subparsers.add_parser(
        "dashboard",
        help="repeat the model across seeds and build a standalone HTML dashboard",
    )
    dashboard.add_argument("--data-dir", type=Path, default=Path("data"))
    dashboard.add_argument("--output-dir", type=Path, default=Path("outputs"))
    dashboard.add_argument("--paths", type=int, default=1000)
    dashboard.add_argument(
        "--seeds",
        default="40,41,42",
        help="comma-separated integer seeds",
    )

    validate = subparsers.add_parser("validate-data", help="validate all input data files")
    validate.add_argument("--data-dir", type=Path, default=Path("data"))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "validate-data":
        bundle = load_data(args.data_dir)
        print(
            "Validated "
            f"{len(bundle.companies)} companies, "
            f"{len(bundle.facilities)} facilities, "
            f"{len(bundle.technologies)} technologies, "
            f"{len(bundle.transition_projects)} disclosed projects, "
            f"{len(bundle.scenarios)} company-scenarios, and "
            f"{len(bundle.plans)} company-plans."
        )
        return

    if args.command == "dashboard":
        try:
            seeds = [int(value.strip()) for value in args.seeds.split(",") if value.strip()]
        except ValueError as error:
            raise SystemExit("--seeds must be a comma-separated list of integers") from error
        result = run_repeated_analysis(
            data_dir=args.data_dir,
            output_dir=args.output_dir,
            path_count=args.paths,
            seeds=seeds,
        )
        print(f"Dashboard complete: {result['dashboard_path']}")
        print(f"English dashboard: {result['english_dashboard_path']}")
        print(
            f"Aggregated {result['run_count']} runs × {result['path_count']} paths "
            f"({result['effective_paths_per_plan']:,} paths per plan/scenario)."
        )
        return

    result = run_pipeline(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        path_count=args.paths,
        seed=args.seed,
    )
    print(f"Run complete: {result['report_path']}")
    print(
        f"Evaluated {result['company_count']} companies, {result['plan_count']} company-plans, "
        f"and {result['scenario_count']} company-scenarios using {result['path_count']} paths."
    )


if __name__ == "__main__":
    main()
