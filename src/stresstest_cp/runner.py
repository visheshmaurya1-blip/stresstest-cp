"""Execute candidate and reference solutions with timeouts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys
import time


@dataclass(frozen=True)
class RunResult:
    stdout: str
    stderr: str
    exit_code: int | None
    timed_out: bool
    duration_sec: float
    command: list[str]

    @property
    def crashed(self) -> bool:
        return (not self.timed_out) and self.exit_code not in (0, None)


def run_solution(
    program: str | Path,
    stdin: str,
    timeout_sec: float,
    python_executable: str | None = None,
) -> RunResult:
    """Run a local Python program on ``stdin`` and capture its result.

    Isolation is process-level only. A timeout is not a proof of an
    asymptotic complexity violation, and this is not a security sandbox.
    """
    python = python_executable or sys.executable
    command = [python, str(Path(program))]
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            input=stdin,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        duration = time.perf_counter() - started
        stdout = _as_text(exc.stdout)
        stderr = _as_text(exc.stderr)
        return RunResult(
            stdout=stdout,
            stderr=stderr or f"TIMEOUT after {timeout_sec}s",
            exit_code=None,
            timed_out=True,
            duration_sec=duration,
            command=command,
        )
    duration = time.perf_counter() - started
    return RunResult(
        stdout=completed.stdout,
        stderr=completed.stderr,
        exit_code=completed.returncode,
        timed_out=False,
        duration_sec=duration,
        command=command,
    )


def _as_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value
