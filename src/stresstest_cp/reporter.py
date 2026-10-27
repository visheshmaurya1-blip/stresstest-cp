"""Save reproducible failure reports that can be committed to git."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from stresstest_cp.comparator import Comparison, FailureKind
from stresstest_cp.generator import InputCase
from stresstest_cp.runner import RunResult


@dataclass(frozen=True)
class FailureReport:
    problem: str
    kind: str
    failure: str
    seed: int
    case_seed: int
    tests_run: int
    input: str
    expected: str
    actual: str
    candidate: str
    reference: str
    shrunk: bool
    original_input: str | None
    candidate_stderr: str
    reference_stderr: str
    message: str
    created_at: str
    report_dir: str
    extra: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def write_report(
    *,
    reports_dir: str | Path,
    problem: str,
    case: InputCase,
    comparison: Comparison,
    candidate: str | Path,
    reference: str | Path,
    seed: int,
    tests_run: int,
    candidate_run: RunResult,
    reference_run: RunResult,
    shrunk: bool,
    original_input: str | None = None,
    extra: dict[str, Any] | None = None,
) -> FailureReport:
    root = Path(reports_dir)
    root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = f"{_safe(problem)}_{case.seed}_{stamp}"
    case_dir = root / slug
    case_dir.mkdir(parents=True, exist_ok=True)

    (case_dir / "input.txt").write_text(case.stdin, encoding="utf-8")
    (case_dir / "expected.txt").write_text(comparison.expected + "\n", encoding="utf-8")
    (case_dir / "actual.txt").write_text(comparison.actual + "\n", encoding="utf-8")

    report = FailureReport(
        problem=problem,
        kind=case.kind,
        failure=comparison.kind.value if isinstance(comparison.kind, FailureKind) else str(comparison.kind),
        seed=seed,
        case_seed=case.seed,
        tests_run=tests_run,
        input=case.stdin,
        expected=comparison.expected,
        actual=comparison.actual,
        candidate=str(Path(candidate)),
        reference=str(Path(reference)),
        shrunk=shrunk,
        original_input=original_input,
        candidate_stderr=candidate_run.stderr,
        reference_stderr=reference_run.stderr,
        message=comparison.message,
        created_at=stamp,
        report_dir=str(case_dir),
        extra=extra or {},
    )
    (case_dir / "report.json").write_text(
        json.dumps(report.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def load_report(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    if target.is_dir():
        target = target / "report.json"
    return json.loads(target.read_text(encoding="utf-8"))


def _safe(name: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in name)
    return cleaned.strip("-") or "problem"
