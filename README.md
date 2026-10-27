# StressTest CP 🧪

**Find bugs in competitive programming solutions using randomized differential testing.**

StressTest CP is a Python command-line tool that compares an optimized solution against a trusted reference implementation, generates randomized test cases, detects incorrect outputs, and helps minimize failing inputs.

When you do not know whether an optimized solution is correct, generate thousands of small tests and compare it with a brute-force implementation. If the optimized two-sum misses duplicate values, this tool should find the mismatch, save the failing input, and shrink it to a small reproducible example.

## ✨ Features

- **Random test generation:** Generate reproducible test cases using configurable random seeds.
- **Differential testing:** Compare a candidate solution against a trusted reference.
- **Failure detection:** Identify output mismatches, crashes, and timeouts.
- **Test-case shrinking:** Reduce failing inputs to simpler counterexamples.
- **Reproducible reports:** Save failing inputs, expected outputs, actual outputs, and seeds.
- **Regression testing:** Replay previously discovered bugs with `stresstest replay`.
- **Extensible design:** Add generators for arrays, strings, trees, graphs, and other problem types.

## 🧠 How It Works

1. Provide an optimized candidate and a trusted reference solution.
2. Generate a random input using a reproducible seed.
3. Execute both programs with the same input.
4. Compare their results and detect failures.
5. Minimize the failing input when possible.
6. Save a report so the bug can be reproduced later.

## 🛠️ Tech Stack

- Python 3.11+
- Python standard library
- pytest for automated tests
- GitHub Actions for continuous integration

## 🚀 Installation

```bash
git clone https://github.com/visheshmaurya1-blip/stresstest-cp.git
cd stresstest-cp

python -m venv .venv
```

Activate the environment and install the project:

```bash
python -m pip install -e ".[dev]"
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`.

## 💻 Usage

Solutions read from stdin and write to stdout. Generator kinds:

| Kind        | Stdin format                         |
|-------------|--------------------------------------|
| `array_int` | `n` then a line of `n` integers      |
| `string`    | `n` then a line with `n` characters  |
| `integer`   | a single integer                     |
| `two_sum`   | `n target` then a line of `n` integers |

```bash
stresstest run \
  --candidate examples/two_sum/candidate.py \
  --reference examples/two_sum/reference.py \
  --problem examples/two_sum/problem.json \
  --seed 42 \
  --count 1000
```

The command stops on the first failure, shrinks the input, and writes a JSON report under `reports/`.

Replay a saved bug:

```bash
stresstest replay \
  --candidate examples/two_sum/candidate.py \
  --reference examples/two_sum/reference.py \
  --report reports/<report-directory>
```

You can also run the module directly: `python -m stresstest_cp run ...`.

## 📂 Project Structure

```text
src/stresstest_cp/  # Core testing engine (independent of the CLI)
examples/           # Candidate and reference solutions
tests/              # Unit and integration tests
reports/            # Reproducible failure reports
docs/               # Algorithm explanations
```

The engine in `engine.py` does not import `cli.py`, so each component can be unit-tested and later reused from a GUI or another language runner.

## 📚 Algorithms and Concepts

See [docs/algorithms.md](docs/algorithms.md) for costs and design notes.

- Randomized testing
- Differential testing
- Brute-force reference solutions
- Delta debugging and test-case shrinking
- Process timeouts and failure classification
- Deterministic random number generation
- Algorithmic complexity analysis

## 🧪 Run Tests

```bash
python -m pytest -q
```

## 🔬 Example Use Case

The bundled `examples/two_sum/candidate.py` refuses pairs of equal numbers. StressTest CP generates an input with duplicates (for example `3 3` with target `6`), compares it with the brute-force reference, shrinks the array, and stores the counterexample.

The same workflow applies to sorting, binary search, dynamic programming, and later to trees and graphs.

## 🔐 Safety

The initial version is intended for local use with trusted programs. A subprocess timeout is not a security sandbox. Do not run arbitrary untrusted submissions without operating-system-level isolation and resource restrictions.

## 🗺️ Roadmap

- [x] Define modular project architecture
- [x] Implement deterministic input generation
- [x] Implement candidate and reference runners
- [x] Implement output comparison
- [x] Build the differential-testing engine
- [x] Add array-based test-case shrinking
- [x] Add JSON failure reports
- [x] Add replay and regression testing
- [ ] Add tree and graph generators
- [ ] Add optional C++ execution support
- [ ] Publish a demo and first release

## 🤝 Contributing

Contributions are welcome. Useful additions include new input generators, shrinkers, comparison strategies, tests, and documentation.

## 📄 License

Released under the MIT License.

---

**Built to make competitive programming debugging more systematic, reproducible, and efficient.**
