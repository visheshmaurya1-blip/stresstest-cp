from stresstest_cp.config import ProblemConfig
from stresstest_cp.generator import generate


def test_same_seed_is_reproducible() -> None:
    config = ProblemConfig(kind="array_int", n_min=3, n_max=8)
    first = generate(config, seed=42)
    second = generate(config, seed=42)
    assert first.stdin == second.stdin
    assert first.data == second.data


def test_array_length_respects_bounds() -> None:
    config = ProblemConfig(kind="array_int", n_min=4, n_max=4, value_min=0, value_max=5)
    case = generate(config, seed=7)
    assert len(case.data) == 4
    assert all(0 <= value <= 5 for value in case.data)
    lines = case.stdin.strip().splitlines()
    assert lines[0] == "4"
    assert len(lines[1].split()) == 4


def test_string_generation_uses_charset() -> None:
    config = ProblemConfig(kind="string", n_min=5, n_max=5, charset="ab")
    case = generate(config, seed=3)
    assert len(case.data) == 5
    assert set(case.data) <= {"a", "b"}


def test_two_sum_format_and_duplicate_bias() -> None:
    config = ProblemConfig(kind="two_sum", n_min=2, n_max=6)
    found_duplicate_pair = False
    for seed in range(50):
        case = generate(config, seed)
        nums = case.data["nums"]
        target = case.data["target"]
        assert len(nums) >= 2
        header, body = case.stdin.strip().splitlines()
        n_text, target_text = header.split()
        assert int(n_text) == len(nums)
        assert int(target_text) == target
        assert body.split() == [str(x) for x in nums]
        if nums.count(nums[0]) >= 2 and target == 2 * nums[0]:
            found_duplicate_pair = True
    assert found_duplicate_pair
