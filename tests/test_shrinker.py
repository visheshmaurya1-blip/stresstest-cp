from stresstest_cp.config import ProblemConfig
from stresstest_cp.generator import InputCase
from stresstest_cp.shrinker import shrink


def test_shrinks_array_to_offending_value() -> None:
    case = InputCase(
        kind="array_int",
        seed=1,
        stdin="6\n1 2 7 3 4 5\n",
        data=[1, 2, 7, 3, 4, 5],
    )
    config = ProblemConfig(kind="array_int", n_min=1, n_max=10)

    def still_fails(trial: InputCase) -> bool:
        return 7 in trial.data

    reduced = shrink(case, still_fails, config)
    assert reduced.data == [7]


def test_shrinks_string_by_removing_chars() -> None:
    case = InputCase(kind="string", seed=1, stdin="6\nabczzz\n", data="abczzz")
    config = ProblemConfig(kind="string", n_min=1, n_max=10)

    def still_fails(trial: InputCase) -> bool:
        return "z" in trial.data

    reduced = shrink(case, still_fails, config)
    assert reduced.data == "z"


def test_shrinks_two_sum_array() -> None:
    case = InputCase(
        kind="two_sum",
        seed=1,
        stdin="5 6\n1 2 3 3 9\n",
        data={"nums": [1, 2, 3, 3, 9], "target": 6},
    )
    config = ProblemConfig(kind="two_sum", n_min=2, n_max=10)

    def still_fails(trial: InputCase) -> bool:
        nums = trial.data["nums"]
        target = trial.data["target"]
        return nums.count(3) >= 2 and target == 6

    reduced = shrink(case, still_fails, config)
    assert reduced.data["nums"] == [3, 3]
    assert reduced.data["target"] == 6
