#!/usr/bin/env python3
"""Trusted linear-time array sum."""

import sys


def main() -> None:
    n = int(sys.stdin.readline())
    raw = sys.stdin.readline().strip()
    nums = list(map(int, raw.split())) if raw else []
    if len(nums) != n:
        raise SystemExit(f"expected {n} numbers, got {len(nums)}")
    print(sum(nums))


if __name__ == "__main__":
    main()
