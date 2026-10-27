from pathlib import Path

from stresstest_cp.cli import main
from stresstest_cp.comparator import FailureKind
from stresstest_cp.config import load_problem_config
from stresstest_cp.engine import replay_input, stress_test
from stresstest_cp.reporter import load_report

ROOT = Path(__file__).resolve().parents[1]
TWO_SUM = ROOT / "examples" / "two_sum"
ARRAY_SUM = ROOT / "examples" / "array_sum"


def test_finds_two_sum_duplicate_bug(tmp_path: Path) -> None:
    config = load_problem_config(TWO_SUM / "problem.json")
    result = stress_test(
        candidate=TWO_SUM / "candidate.py",
        reference=TWO_SUM / "reference.py",
        config=config,
        seed=42,
        count=200,
        reports_dir=tmp_path,
        stop_on_failure=True,
        do_shrink=True,
    )
    assert result.failed == 1
    assert result.report is not None
    assert result.last_comparison is not None
    assert result.last_comparison.kind is FailureKind.WRONG_ANSWER
    assert result.report.shrunk is True
    nums = result.last_case.data["nums"]
    assert len(nums) <= 4
    report_path = Path(result.report.report_dir) / "report.json"
    payload = load_report(report_path)
    assert payload["failure"] == "wrong_answer"
    replayed = replay_input(
        candidate=TWO_SUM / "candidate.py",
        reference=TWO_SUM / "reference.py",
        stdin=payload["input"],
        config=config,
        kind=payload["kind"],
        case_seed=payload["case_seed"],
    )
    assert replayed[3].kind is FailureKind.WRONG_ANSWER


def test_finds_array_sum_negative_bug(tmp_path: Path) -> None:
    config = load_problem_config(ARRAY_SUM / "problem.json")
    result = stress_test(
        candidate=ARRAY_SUM / "candidate.py",
        reference=ARRAY_SUM / "reference.py",
        config=config,
        seed=1,
        count=100,
        reports_dir=tmp_path,
    )
    assert result.failed == 1
    assert result.last_comparison is not None
    assert result.last_comparison.kind is FailureKind.WRONG_ANSWER


def test_cli_run_and_replay(tmp_path: Path) -> None:
    reports = tmp_path / "reports"
    code = main(
        [
            "run",
            "--candidate",
            str(TWO_SUM / "candidate.py"),
            "--reference",
            str(TWO_SUM / "reference.py"),
            "--problem",
            str(TWO_SUM / "problem.json"),
            "--seed",
            "42",
            "--count",
            "200",
            "--reports-dir",
            str(reports),
        ]
    )
    assert code == 1
    report_dirs = [path for path in reports.iterdir() if path.is_dir()]
    assert len(report_dirs) == 1
    replay_code = main(
        [
            "replay",
            "--candidate",
            str(TWO_SUM / "candidate.py"),
            "--reference",
            str(TWO_SUM / "reference.py"),
            "--report",
            str(report_dirs[0]),
        ]
    )
    assert replay_code == 1
