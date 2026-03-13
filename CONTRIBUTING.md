# Contributing

## Development Setup

Install dependencies and register the kernelspec:

```shell
just install
```

## Running Tests

```shell
just test                          # pytest suite
just test-kernel                   # legacy unittest + diagnostics
just test-notebook                 # notebook execution test
just cover                         # tests with coverage report
```

## Code Quality

```shell
just pre-commit                    # run all pre-commit hooks
just typing                        # mypy strict type checking
```

## Benchmarks

Performance is tracked using [ASV](https://asv.readthedocs.io). The benchmark
suite exercises `OctaveEngine` across startup time, eval round-trip latency,
matrix operations, output handling, completions, and peak memory usage.

**Run benchmarks for the current commit:**

```shell
just benchmark
```

This runs `asv run HEAD^!` — all 10 benchmarks against the current HEAD.
Expect a runtime of roughly 5 minutes.

**Compare against `origin/main`:**

```shell
just benchmark-compare
```

This runs `asv continuous <merge-base> HEAD --split`, comparing your branch
against the point where it diverged from `origin/main`. Results are printed
in a split table showing improvements, regressions, and unchanged benchmarks.
A change must exceed the default 10% factor to be reported.

**CI:** The `benchmark` job in `test.yml` runs `just benchmark-compare`
automatically on every pull request.
