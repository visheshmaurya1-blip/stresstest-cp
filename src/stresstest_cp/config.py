"""Problem configuration loaded from JSON or CLI flags."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
import json
from pathlib import Path
import sys
from typing import Any


VALID_KINDS = ("array_int", "string", "integer", "two_sum")


@dataclass(frozen=True)
class ProblemConfig:
    name: str = "problem"
    kind: str = "array_int"
    timeout_sec: float = 1.0
    python_executable: str = field(default_factory=lambda: sys.executable)
    n_min: int = 1
    n_max: int = 20
    value_min: int = -100
    value_max: int = 100
    charset: str = "abcdefghijklmnopqrstuvwxyz"
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.kind not in VALID_KINDS:
            raise ValueError(
                f"Unsupported kind {self.kind!r}. Choose one of {VALID_KINDS}."
            )
        if self.n_min < 0 or self.n_max < self.n_min:
            raise ValueError("Require 0 <= n_min <= n_max.")
        if self.value_max < self.value_min:
            raise ValueError("Require value_min <= value_max.")
        if self.timeout_sec <= 0:
            raise ValueError("timeout_sec must be positive.")
        if self.kind == "two_sum" and self.n_min < 2:
            object.__setattr__(self, "n_min", 2)
        if self.kind == "string" and not self.charset:
            raise ValueError("string kind requires a non-empty charset.")


def load_problem_config(path: str | Path, **overrides: Any) -> ProblemConfig:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    constraints = raw.get("constraints", {})
    data = {
        "name": raw.get("name", Path(path).parent.name),
        "kind": raw.get("kind", "array_int"),
        "timeout_sec": raw.get("timeout_sec", 1.0),
        "n_min": constraints.get("n_min", 1),
        "n_max": constraints.get("n_max", 20),
        "value_min": constraints.get("value_min", -100),
        "value_max": constraints.get("value_max", 100),
        "charset": constraints.get("charset", "abcdefghijklmnopqrstuvwxyz"),
        "extra": {k: v for k, v in raw.items() if k not in {"name", "kind", "timeout_sec", "constraints"}},
    }
    data.update({k: v for k, v in overrides.items() if v is not None})
    return ProblemConfig(**data)


def apply_cli_overrides(config: ProblemConfig, **overrides: Any) -> ProblemConfig:
    cleaned = {k: v for k, v in overrides.items() if v is not None}
    if not cleaned:
        return config
    return replace(config, **cleaned)
