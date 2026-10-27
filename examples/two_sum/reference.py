#!/usr/bin/env python3
"""Trusted O(n^2) two-sum. Returns the lexicographically smallest index pair."""

import sys


def two_sum(nums: list[int], target: int) -> tuple[int, int]:
    for i, left in enumerate(nums):
        for j in range(i + 1, len(nums)):
            if left + nums[j] == target:
                return i, j
    return -1, -1


def main() -> None:
    header = sys.stdin.readline().split()
    n, target = int(header[0]), int(header[1])
    raw = sys.stdin.readline().strip()
    nums = list(map(int, raw.split())) if raw else []
    if len(nums) != n:
        raise SystemExit(f"expected {n} numbers, got {len(nums)}")
    i, j = two_sum(nums, target)
    print(i, j)


if __name__ == "__main__":
    main()
