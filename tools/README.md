# Tools

Small helper scripts for working with the repository.

## PERF extraction

PERF output is enabled with `pytest --perf` and printed as a consolidated report at the end of the test session.

Pytest may still prefix or interleave output in some configurations; use the extractor to keep only the PERF records.

Example:

- `pytest -v -s --perf tests/yappla | tools/perf_extract.sh | tee perf.log`
- `grep '^PERF ' perf.log`
