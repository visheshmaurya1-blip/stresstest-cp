# StressTest CP

StressTest CP compares a candidate competitive-programming solution with a trusted reference solution. It generates reproducible inputs, reports mismatches, crashes, and timeouts, and can shrink a failing input into a smaller counterexample.

## Requirements

- Python 3.11 or newer
- `pip` (included with standard Python installations)

The candidate and reference programs must be local Python files that read from standard input and write their answer to standard output. Run only trusted programs: subprocess timeouts are not a security sandbox.

## 1. Get the project

```shell
git clone https://github.com/visheshmaurya1-blip/stresstest-cp.git
cd stresstest-cp
```

If you already have the project, open a terminal in its root directory instead.

## 2. Create an environment and install

Using a virtual environment keeps the project dependencies separate from other Python projects.

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

These commands use the virtual environment's Python directly, so activation is not required. In the remaining PowerShell examples, use `.\.venv\Scripts\python.exe` in place of `python`.

**macOS / Linux**

```shell
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## 3. Check the installation

Run these commands from the project root.

**Windows PowerShell**

```powershell
.\.venv\Scripts\python.exe -m stresstest_cp --version
.\.venv\Scripts\python.exe -m pytest -q
```

**macOS / Linux**

```shell
python -m stresstest_cp --version
python -m pytest -q
```

The first command prints the installed version. The second runs the test suite. You can also use the installed `stresstest` command instead of `python -m stresstest_cp`.

## 4. Run a stress test

The bundled `two_sum` candidate intentionally contains a bug, while its reference is correct. Run this example to see StressTest CP find and shrink a failure:

**Windows PowerShell**

```powershell
.\.venv\Scripts\python.exe -m stresstest_cp run --candidate examples/two_sum/candidate.py --reference examples/two_sum/reference.py --problem examples/two_sum/problem.json --seed 42 --count 1000
```

**macOS / Linux**

```shell
python -m stresstest_cp run \
  --candidate examples/two_sum/candidate.py \
  --reference examples/two_sum/reference.py \
  --problem examples/two_sum/problem.json \
  --seed 42 \
  --count 1000
```

The command runs up to 1,000 cases, starting with seed `42`, and stops at the first failure by default. This bundled example is expected to print `FAIL`, show the minimized input, and save a report under `reports/`. A `FAIL` here means a bug was successfully detected; it is not an installation or execution error.

For your own solution, replace `--candidate` and `--reference` with your file paths. A correct candidate should print `PASS` after all cases match. The command exits with status `0` when all cases pass and `1` when a failure is found.

### Input formats

The `--kind` or problem JSON `kind` selects the generated input format:

| Kind | Generated standard input |
| --- | --- |
| `array_int` | Number of values on the first line, followed by the integer values |
| `string` | String length on the first line, followed by the string |
| `integer` | One integer |
| `two_sum` | `n target` on the first line, followed by `n` integers |

Use the same input format in both programs. For example, the bundled two-sum solutions read `n target` and then the numbers.

### Configure generated cases

Pass `--problem` with a JSON file to set a problem name, generator kind, timeout, and constraints. For example:

```json
{
  "name": "two_sum",
  "kind": "two_sum",
  "timeout_sec": 1.0,
  "constraints": {
    "n_min": 2,
    "n_max": 12,
    "value_min": -20,
    "value_max": 20
  }
}
```

The `n_min` and `n_max` values control generated input sizes; `value_min` and `value_max` control generated integer values. String problems may also set `charset`. For options and command defaults, run `python -m stresstest_cp run --help`.

If you omit `--problem`, specify the generator using `--kind`; the default kind is `array_int`. CLI flags such as `--count`, `--seed`, `--timeout`, and `--reports-dir` let you adjust a run. Use `--no-shrink` to skip minimization or `--keep-going` to continue testing after failures.

## 5. Inspect and replay a failure

Each detected failure gets its own directory under `reports/`, containing:

- `report.json` — metadata, seed, failure type, and program paths
- `input.txt` — the minimized reproducing input
- `expected.txt` — reference output
- `actual.txt` — candidate output

The CLI prints the report directory. Pass that directory (or its `report.json`) to `replay` to execute the saved input again:

```shell
python -m stresstest_cp replay \
  --candidate examples/two_sum/candidate.py \
  --reference examples/two_sum/reference.py \
  --report reports/REPLACE_WITH_THE_PRINTED_REPORT_DIRECTORY
```

In PowerShell, use:

```powershell
.\.venv\Scripts\python.exe -m stresstest_cp replay --candidate examples/two_sum/candidate.py --reference examples/two_sum/reference.py --report reports\REPLACE_WITH_THE_PRINTED_REPORT_DIRECTORY
```

Replay returns `1` while the failure still reproduces and `0` when the outputs match. After fixing a bug, run `replay` again to confirm the saved case passes, then run `run` to test fresh generated cases.

## Project layout

```text
src/stresstest_cp/   Core package and command-line interface
examples/            Candidate/reference pairs and problem configurations
tests/               Automated tests
reports/             Generated failure reports
docs/algorithms.md   Design and algorithm notes
```

For implementation details, see [docs/algorithms.md](docs/algorithms.md).

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
