"""Delta debugging: shrink a failing input while the failure still reproduces."""

from __future__ import annotations

from collections.abc import Callable

from stresstest_cp.config import ProblemConfig
from stresstest_cp.generator import InputCase


Predicate = Callable[[InputCase], bool]


def shrink(case: InputCase, still_fails: Predicate, config: ProblemConfig) -> InputCase:
    """Reduce ``case`` while ``still_fails`` stays true.

    There is no guarantee of a globally minimal input. The result is a
    smaller counterexample that still reproduces the observed failure.
    """
    current = case
    if case.kind == "array_int":
        nums = _ddmin_list(list(case.data), config.n_min, lambda items: still_fails(case.with_data(items)))
        nums = _shrink_ints(nums, lambda items: still_fails(case.with_data(items)))
        current = case.with_data(nums)
    elif case.kind == "string":
        chars = _ddmin_list(
            list(case.data),
            config.n_min,
            lambda items: still_fails(case.with_data("".join(items))),
        )
        current = case.with_data("".join(chars))
    elif case.kind == "integer":
        current = _shrink_integer(case, still_fails, config)
    elif case.kind == "two_sum":
        current = _shrink_two_sum(case, still_fails, config)
    return current if still_fails(current) else case


def _ddmin_list(items: list, min_len: int, test: Callable[[list], bool]) -> list:
    current = list(items)
    if not test(current):
        return current
    chunk = max(1, len(current) // 2)
    while True:
        reduced = False
        start = 0
        while start < len(current):
            end = min(len(current), start + chunk)
            candidate = current[:start] + current[end:]
            if len(candidate) >= min_len and test(candidate):
                current = candidate
                reduced = True
                chunk = max(1, len(current) // 2)
                break
            start += chunk
        if reduced:
            continue
        if chunk == 1:
            break
        chunk = max(1, chunk // 2)
    return current


def _shrink_ints(values: list[int], test: Callable[[list[int]], bool]) -> list[int]:
    current = list(values)
    for i, value in enumerate(current):
        if value == 0:
            continue
        trial = list(current)
        trial[i] = 0
        if test(trial):
            current = trial
            continue
        guess = value
        while guess not in (0, 1, -1):
            nxt = guess // 2
            trial = list(current)
            trial[i] = nxt
            if test(trial):
                current = trial
                guess = nxt
            else:
                break
    return current


def _shrink_integer(case: InputCase, still_fails: Predicate, config: ProblemConfig) -> InputCase:
    value = int(case.data)
    for candidate in (0, 1, -1, config.value_min, config.value_max):
        trial = case.with_data(candidate)
        if still_fails(trial):
            return trial
    guess = value
    while abs(guess) > 1:
        nxt = guess // 2
        trial = case.with_data(nxt)
        if still_fails(trial):
            guess = nxt
        else:
            break
    return case.with_data(guess)


def _shrink_two_sum(case: InputCase, still_fails: Predicate, config: ProblemConfig) -> InputCase:
    nums = list(case.data["nums"])
    target = int(case.data["target"])
    min_len = max(2, config.n_min)

    def test_nums(items: list[int]) -> bool:
        return still_fails(case.with_data({"nums": items, "target": target}))

    nums = _ddmin_list(nums, min_len, test_nums)
    nums = _shrink_ints(nums, test_nums)

    for candidate_target in (0, 1, -1, target // 2, nums[0] + nums[1] if len(nums) >= 2 else target):
        trial = case.with_data({"nums": nums, "target": candidate_target})
        if still_fails(trial):
            target = candidate_target
            break
    return case.with_data({"nums": nums, "target": target})
