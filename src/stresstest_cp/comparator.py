"""Compare candidate and reference runs and classify failures."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from stresstest_cp.runner import RunResult


class FailureKind(str, Enum):
    PASS = "pass"
    WRONG_ANSWER = "wrong_answer"
    CRASH = "crash"
    TIMEOUT = "timeout"
    REFERENCE_CRASH = "reference_crash"
    REFERENCE_TIMEOUT = "reference_timeout"


@dataclass(frozen=True)
class Comparison:
    kind: FailureKind
    expected: str
    actual: str
    message: str

    @property
    def failed(self) -> bool:
        return self.kind is not FailureKind.PASS


def normalize_output(text: str) -> str:
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def compare_runs(candidate: RunResult, reference: RunResult) -> Comparison:
    expected = normalize_output(reference.stdout)
    actual = normalize_output(candidate.stdout)

    if reference.timed_out:
        return Comparison(
            kind=FailureKind.REFERENCE_TIMEOUT,
            expected=expected,
            actual=actual,
            message="Reference solution timed out.",
        )
    if reference.crashed:
        return Comparison(
            kind=FailureKind.REFERENCE_CRASH,
            expected=expected,
            actual=actual,
            message=_crash_message("Reference", reference),
        )
    if candidate.timed_out:
        return Comparison(
            kind=FailureKind.TIMEOUT,
            expected=expected,
            actual=actual,
            message="Candidate solution timed out.",
        )
    if candidate.crashed:
        return Comparison(
            kind=FailureKind.CRASH,
            expected=expected,
            actual=actual,
            message=_crash_message("Candidate", candidate),
        )
    if actual != expected:
        return Comparison(
            kind=FailureKind.WRONG_ANSWER,
            expected=expected,
            actual=actual,
            message="Candidate output differs from the reference.",
        )
    return Comparison(
        kind=FailureKind.PASS,
        expected=expected,
        actual=actual,
        message="Outputs match.",
    )


def _crash_message(label: str, result: RunResult) -> str:
    detail = normalize_output(result.stderr)
    suffix = f"\n{detail}" if detail else ""
    return f"{label} exited with code {result.exit_code}.{suffix}"
