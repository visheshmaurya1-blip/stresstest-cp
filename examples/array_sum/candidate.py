#!/usr/bin/env python3
"""Buggy array sum: ignores negative numbers."""

import sys


def main() -> None:
    n = int(sys.stdin.readline())
    raw = sys.stdin.readline().strip()
    nums = list(map(int, raw.split())) if raw else []
    if len(nums) != n:
        raise SystemExit(f"expected {n} numbers, got {len(nums)}")
    print(sum(value for value in nums if value >= 0))


if __name__ == "__main__":
    main()
