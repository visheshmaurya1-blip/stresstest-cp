from stresstest_cp.comparator import FailureKind, compare_runs, normalize_output
from stresstest_cp.runner import RunResult


def _run(stdout: str = "", stderr: str = "", exit_code: int | None = 0, timed_out: bool = False) -> RunResult:
    return RunResult(
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        timed_out=timed_out,
        duration_sec=0.01,
        command=["python", "x.py"],
    )


def test_normalize_trailing_whitespace() -> None:
    assert normalize_output("1 2  \r\n3\n\n") == "1 2\n3"


def test_pass_when_outputs_match() -> None:
    comparison = compare_runs(_run("7\n"), _run("7\n"))
    assert comparison.kind is FailureKind.PASS
    assert comparison.failed is False


def test_wrong_answer() -> None:
    comparison = compare_runs(_run("1 2\n"), _run("0 1\n"))
    assert comparison.kind is FailureKind.WRONG_ANSWER
    assert comparison.expected == "0 1"
    assert comparison.actual == "1 2"


def test_candidate_crash_and_timeout() -> None:
    crash = compare_runs(_run(stderr="boom", exit_code=1), _run("ok\n"))
    assert crash.kind is FailureKind.CRASH
    timeout = compare_runs(_run(timed_out=True, exit_code=None), _run("ok\n"))
    assert timeout.kind is FailureKind.TIMEOUT


def test_reference_failures_are_classified() -> None:
    crash = compare_runs(_run("x"), _run(stderr="ref", exit_code=2))
    assert crash.kind is FailureKind.REFERENCE_CRASH
    timeout = compare_runs(_run("x"), _run(timed_out=True, exit_code=None))
    assert timeout.kind is FailureKind.REFERENCE_TIMEOUT
