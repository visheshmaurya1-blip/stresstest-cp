from pathlib import Path

from stresstest_cp.runner import run_solution


def test_captures_stdout(tmp_path: Path) -> None:
    program = tmp_path / "echo.py"
    program.write_text("import sys; print(sys.stdin.read().strip()[::-1])\n", encoding="utf-8")
    result = run_solution(program, "abc\n", timeout_sec=1.0)
    assert result.exit_code == 0
    assert result.timed_out is False
    assert result.stdout.strip() == "cba"


def test_classifies_crash(tmp_path: Path) -> None:
    program = tmp_path / "crash.py"
    program.write_text("raise RuntimeError('boom')\n", encoding="utf-8")
    result = run_solution(program, "", timeout_sec=1.0)
    assert result.crashed
    assert result.exit_code != 0
    assert "boom" in result.stderr


def test_timeout(tmp_path: Path) -> None:
    program = tmp_path / "hang.py"
    program.write_text("import time; time.sleep(5)\n", encoding="utf-8")
    result = run_solution(program, "", timeout_sec=0.2)
    assert result.timed_out
    assert result.exit_code is None
