"""Command-line interface. The testing engine does not depend on this module."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from stresstest_cp import __version__
from stresstest_cp.config import ProblemConfig, apply_cli_overrides, load_problem_config
from stresstest_cp.engine import replay_input, stress_test
from stresstest_cp.reporter import load_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stresstest",
        description="Find bugs in competitive programming solutions with differential testing.",
    )
    parser.add_argument("--version", action="version", version=f"stresstest-cp {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Generate tests and compare candidate vs reference.")
    _add_program_args(run)
    run.add_argument("--problem", help="Path to problem.json with generator constraints.")
    run.add_argument("--kind", choices=["array_int", "string", "integer", "two_sum"])
    run.add_argument("--seed", type=int, default=42)
    run.add_argument("--count", type=int, default=1000)
    run.add_argument("--timeout", type=float, default=None, help="Seconds per solution run.")
    run.add_argument("--n-min", type=int, dest="n_min")
    run.add_argument("--n-max", type=int, dest="n_max")
    run.add_argument("--value-min", type=int, dest="value_min")
    run.add_argument("--value-max", type=int, dest="value_max")
    run.add_argument("--reports-dir", default="reports")
    run.add_argument("--no-shrink", action="store_true")
    run.add_argument(
        "--keep-going",
        action="store_true",
        help="Continue after the first failure (still writes a report).",
    )
    run.add_argument("--name", help="Problem name used in report filenames.")

    replay = sub.add_parser("replay", help="Re-run a saved failing input.")
    _add_program_args(replay)
    replay.add_argument("--report", required=True, help="Path to report.json or a report directory.")
    replay.add_argument("--timeout", type=float, default=None)
    return parser


def _add_program_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--candidate", required=True, help="Path to the candidate Python solution.")
    parser.add_argument("--reference", required=True, help="Path to the trusted reference solution.")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "run":
        return _cmd_run(args)
    if args.command == "replay":
        return _cmd_replay(args)
    parser.error(f"Unknown command {args.command}")
    return 2


def _cmd_run(args: argparse.Namespace) -> int:
    _require_files(args.candidate, args.reference)
    if args.problem:
        config = load_problem_config(
            args.problem,
            name=args.name,
            kind=args.kind,
            timeout_sec=args.timeout,
            n_min=args.n_min,
            n_max=args.n_max,
            value_min=args.value_min,
            value_max=args.value_max,
        )
    else:
        config = ProblemConfig(
            name=args.name or Path(args.candidate).parent.name,
            kind=args.kind or "array_int",
            timeout_sec=args.timeout or 1.0,
            n_min=args.n_min if args.n_min is not None else 1,
            n_max=args.n_max if args.n_max is not None else 20,
            value_min=args.value_min if args.value_min is not None else -100,
            value_max=args.value_max if args.value_max is not None else 100,
        )
        config = apply_cli_overrides(
            config,
            timeout_sec=args.timeout,
            n_min=args.n_min,
            n_max=args.n_max,
            value_min=args.value_min,
            value_max=args.value_max,
            name=args.name,
        )

    result = stress_test(
        candidate=args.candidate,
        reference=args.reference,
        config=config,
        seed=args.seed,
        count=args.count,
        reports_dir=args.reports_dir,
        stop_on_failure=not args.keep_going,
        do_shrink=not args.no_shrink,
    )
    if result.failed:
        report = result.report
        print(f"FAIL after {result.passed + result.failed} test(s); {result.passed} passed.")
        if report is not None:
            print(f"  failure: {report.failure}")
            print(f"  case seed: {report.case_seed}")
            print(f"  report: {report.report_dir}")
            print("  input:")
            print(report.input.rstrip())
            print("  expected:")
            print(report.expected)
            print("  actual:")
            print(report.actual)
        return 1
    print(f"PASS {result.passed} test(s) with seed {args.seed}.")
    return 0


def _cmd_replay(args: argparse.Namespace) -> int:
    _require_files(args.candidate, args.reference)
    payload = load_report(args.report)
    config = ProblemConfig(
        name=payload.get("problem", "replay"),
        kind=payload.get("kind", "array_int"),
        timeout_sec=args.timeout or 1.0,
    )
    _, _, _, comparison = replay_input(
        candidate=args.candidate,
        reference=args.reference,
        stdin=payload["input"],
        config=config,
        kind=payload.get("kind"),
        case_seed=int(payload.get("case_seed", 0)),
    )
    print(f"replay: {comparison.kind.value}")
    print(comparison.message)
    if comparison.failed:
        print("  expected:")
        print(comparison.expected)
        print("  actual:")
        print(comparison.actual)
        return 1
    return 0


def _require_files(*paths: str) -> None:
    missing = [path for path in paths if not Path(path).is_file()]
    if missing:
        raise SystemExit("Missing file(s): " + ", ".join(missing))


if __name__ == "__main__":
    sys.exit(main())
