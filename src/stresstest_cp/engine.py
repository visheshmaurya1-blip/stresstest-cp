"""Coordinate generation, execution, comparison, shrinking, and reporting."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from stresstest_cp.comparator import Comparison, FailureKind, compare_runs
from stresstest_cp.config import ProblemConfig
from stresstest_cp.generator import InputCase, generate
from stresstest_cp.reporter import FailureReport, write_report
from stresstest_cp.runner import RunResult, run_solution
from stresstest_cp.shrinker import shrink


@dataclass(frozen=True)
class StressResult:
    passed: int
    failed: int
    stopped_on_failure: bool
    report: FailureReport | None
    last_comparison: Comparison | None
    last_case: InputCase | None


def run_pair(
    candidate: str | Path,
    reference: str | Path,
    case: InputCase,
    config: ProblemConfig,
) -> tuple[RunResult, RunResult, Comparison]:
    candidate_run = run_solution(candidate, case.stdin, config.timeout_sec, config.python_executable)
    reference_run = run_solution(reference, case.stdin, config.timeout_sec, config.python_executable)
    comparison = compare_runs(candidate_run, reference_run)
    return candidate_run, reference_run, comparison


def stress_test(
    *,
    candidate: str | Path,
    reference: str | Path,
    config: ProblemConfig,
    seed: int,
    count: int,
    reports_dir: str | Path = "reports",
    stop_on_failure: bool = True,
    do_shrink: bool = True,
) -> StressResult:
    """Run ``count`` deterministic trials starting from ``seed``.

    Trial ``i`` uses case seed ``seed + i`` so a failure can be replayed
    without storing the full random stream.
    """
    if count <= 0:
        raise ValueError("count must be positive.")

    passed = 0
    failed = 0
    last_comparison: Comparison | None = None
    last_case: InputCase | None = None
    report: FailureReport | None = None

    for i in range(count):
        case = generate(config, seed + i)
        candidate_run, reference_run, comparison = run_pair(candidate, reference, case, config)
        last_comparison = comparison
        last_case = case
        if not comparison.failed:
            passed += 1
            continue

        failed += 1
        original_input = case.stdin
        shrunk = False
        if do_shrink and comparison.kind in {
            FailureKind.WRONG_ANSWER,
            FailureKind.CRASH,
            FailureKind.TIMEOUT,
        }:
            failure_kind = comparison.kind

            def still_fails(trial: InputCase, expected_kind: FailureKind = failure_kind) -> bool:
                _, _, cmp = run_pair(candidate, reference, trial, config)
                return cmp.kind is expected_kind

            reduced = shrink(case, still_fails, config)
            if reduced.stdin != case.stdin and still_fails(reduced):
                case = reduced
                candidate_run, reference_run, comparison = run_pair(
                    candidate, reference, case, config
                )
                shrunk = True

        report = write_report(
            reports_dir=reports_dir,
            problem=config.name,
            case=case,
            comparison=comparison,
            candidate=candidate,
            reference=reference,
            seed=seed,
            tests_run=passed + failed,
            candidate_run=candidate_run,
            reference_run=reference_run,
            shrunk=shrunk,
            original_input=original_input if shrunk else None,
            extra={"trial_index": i},
        )
        last_case = case
        last_comparison = comparison
        if stop_on_failure:
            break

    return StressResult(
        passed=passed,
        failed=failed,
        stopped_on_failure=stop_on_failure and failed > 0,
        report=report,
        last_comparison=last_comparison,
        last_case=last_case,
    )


def replay_input(
    *,
    candidate: str | Path,
    reference: str | Path,
    stdin: str,
    config: ProblemConfig,
    kind: str | None = None,
    case_seed: int = 0,
    data: Any = None,
) -> tuple[InputCase, RunResult, RunResult, Comparison]:
    case = InputCase(kind=kind or config.kind, seed=case_seed, stdin=stdin, data=data)
    candidate_run, reference_run, comparison = run_pair(candidate, reference, case, config)
    return case, candidate_run, reference_run, comparison
