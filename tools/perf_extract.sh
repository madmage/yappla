#!/usr/bin/env bash
set -euo pipefail

# Extract grep-friendly PERF lines from mixed pytest output.
#
# Usage:
#   pytest -v -s --perf tests/yappla | tools/perf_extract.sh | tee perf.log
#   tools/perf_extract.sh pytest_output.log
#
# Output:
#   Prints only the substring starting at "PERF " for each line that contains it.

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  sed -n '1,200p' "$0"
  exit 0
fi

if [[ $# -gt 1 ]]; then
  echo "Usage: $0 [path-to-log-file]" >&2
  exit 2
fi

input="${1:-/dev/stdin}"

# Print from the first occurrence of 'PERF ' to end-of-line.
# This handles cases where pytest prefixes output (e.g., 'tests/foo.py PERF ...').
awk '
  {
    pos = index($0, "PERF ")
    if (pos > 0) {
      print substr($0, pos)
    }
  }
' "$input"
