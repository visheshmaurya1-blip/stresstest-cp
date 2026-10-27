# Algorithms in StressTest CP

This project is a developer tool, but the interesting part is the computer science behind it. The engine is a small composition of four techniques used constantly in competitive programming and compiler testing.

## 1. Random test generation

A pseudorandom number generator with a **fixed seed** produces arrays, strings, integers, and two-sum instances. The same seed always yields the same input, so a failure can be replayed and committed.

Cost is \(O(n)\) to build an array or string of length \(n\). Each trial `i` uses case seed `base_seed + i`, which avoids storing the entire random stream.

The generator also injects structured edge cases (all-equal values, monotonic sequences, extremes, duplicate pairs) because uniform random data often misses the inputs that actually break solutions.

## 2. Differential testing

The candidate (optimized, possibly wrong) and the reference (slow, trusted) receive the same stdin. Their stdout is normalized and compared.

Cost is \(O(T_c + T_r + O_c)\): candidate runtime, reference runtime, and output comparison. For the MVP, comparison is line-oriented string equality after trailing-whitespace normalization. Solutions that may return any valid answer (not a unique one) should agree on a canonical form, such as the lexicographically smallest index pair.

This is the same idea as compiling a program with two compilers and comparing outputs, applied to contest solutions.

## 3. Execution limits

Each program runs in a subprocess with a wall-clock timeout. The runner captures stdout, stderr, and the exit code, then classifies:

- **wrong_answer** — both exited 0, outputs differ
- **crash** — candidate nonzero exit
- **timeout** — candidate exceeded the limit
- **reference_crash / reference_timeout** — the trusted program is broken or too slow

A timeout is **not** a proof that the algorithm is asymptotically too slow. It is a practical bound so a hanging loop cannot stall the tester. Subprocess isolation is also **not** a security sandbox; only run trusted local files.

## 4. Delta debugging (shrinking)

When a failure appears, the shrinker tries to delete chunks of the input (then individual elements) while the same failure still reproduces. Integer values are then walked toward zero.

This is a simplified [delta debugging](https://www.st.cs.uni-saarland.de/dd/) loop (`ddmin`-style). Worst-case cost depends on input size, the shrink steps, and how many times the pair of solutions must be re-executed. There is no general guarantee of a globally minimal counterexample — only a smaller one that is easier to inspect.

For two-sum, shrinking preserves a minimum length of 2 and keeps the target unless a simpler target still fails.

## Putting it together

```text
for i in 0 .. count-1:
    input = generate(seed + i)          # O(n)
    cand  = run(candidate, input)       # timeout + capture
    ref   = run(reference, input)
    if classify(cand, ref) is failure:
        input = shrink(input)           # extra re-executions
        write report and stop
```

That loop is the whole product: randomized search for a counterexample, plus reduction so the bug is small enough to debug by hand.
