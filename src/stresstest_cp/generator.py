"""Deterministic random test-case generation (O(n) for arrays of length n)."""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Any

from stresstest_cp.config import ProblemConfig


@dataclass(frozen=True)
class InputCase:
    kind: str
    seed: int
    stdin: str
    data: Any

    def with_data(self, data: Any) -> InputCase:
        return InputCase(
            kind=self.kind,
            seed=self.seed,
            stdin=format_stdin(self.kind, data),
            data=data,
        )


def generate(config: ProblemConfig, seed: int) -> InputCase:
    rng = random.Random(seed)
    if config.kind == "array_int":
        data = _generate_array(config, rng)
    elif config.kind == "string":
        data = _generate_string(config, rng)
    elif config.kind == "integer":
        data = rng.randint(config.value_min, config.value_max)
    elif config.kind == "two_sum":
        data = _generate_two_sum(config, rng)
    else:
        raise ValueError(f"Unsupported kind {config.kind!r}")
    return InputCase(
        kind=config.kind,
        seed=seed,
        stdin=format_stdin(config.kind, data),
        data=data,
    )


def format_stdin(kind: str, data: Any) -> str:
    if kind == "array_int":
        nums = list(data)
        body = " ".join(str(x) for x in nums)
        return f"{len(nums)}\n{body}\n"
    if kind == "string":
        text = str(data)
        return f"{len(text)}\n{text}\n"
    if kind == "integer":
        return f"{int(data)}\n"
    if kind == "two_sum":
        nums = list(data["nums"])
        target = int(data["target"])
        body = " ".join(str(x) for x in nums)
        return f"{len(nums)} {target}\n{body}\n"
    raise ValueError(f"Unsupported kind {kind!r}")


def _generate_array(config: ProblemConfig, rng: random.Random) -> list[int]:
    n = rng.randint(config.n_min, config.n_max)
    mode = rng.randrange(10)
    if mode == 0:
        value = rng.randint(config.value_min, config.value_max)
        return [value] * n
    if mode == 1:
        start = rng.randint(config.value_min, config.value_max)
        return [_clamp(start + i, config) for i in range(n)]
    if mode == 2:
        start = rng.randint(config.value_min, config.value_max)
        return [_clamp(start - i, config) for i in range(n)]
    if mode == 3 and n:
        extreme = config.value_min if rng.random() < 0.5 else config.value_max
        arr = [rng.randint(config.value_min, config.value_max) for _ in range(n)]
        arr[rng.randrange(n)] = extreme
        return arr
    return [rng.randint(config.value_min, config.value_max) for _ in range(n)]


def _generate_string(config: ProblemConfig, rng: random.Random) -> str:
    n = rng.randint(config.n_min, config.n_max)
    if n == 0:
        return ""
    mode = rng.randrange(6)
    if mode == 0:
        ch = rng.choice(config.charset)
        return ch * n
    if mode == 1:
        ch = rng.choice(config.charset)
        return "".join(ch if rng.random() < 0.7 else rng.choice(config.charset) for _ in range(n))
    return "".join(rng.choice(config.charset) for _ in range(n))


def _generate_two_sum(config: ProblemConfig, rng: random.Random) -> dict[str, Any]:
    n = max(2, rng.randint(config.n_min, config.n_max))
    mode = rng.randrange(10)
    if mode <= 3:
        value = rng.randint(config.value_min, config.value_max)
        nums = [rng.randint(config.value_min, config.value_max) for _ in range(n)]
        i, j = 0, 1
        if n > 2:
            i, j = rng.sample(range(n), 2)
        nums[i] = value
        nums[j] = value
        return {"nums": nums, "target": value + value}
    nums = [rng.randint(config.value_min, config.value_max) for _ in range(n)]
    if mode <= 7:
        i, j = rng.sample(range(n), 2)
        target = nums[i] + nums[j]
    else:
        target = rng.randint(config.value_min * 2, config.value_max * 2)
    return {"nums": nums, "target": target}


def _clamp(value: int, config: ProblemConfig) -> int:
    return max(config.value_min, min(config.value_max, value))
