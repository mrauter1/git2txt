#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
Usage: run_git2text.sh [--dry-run] [--require-output <path>] <source> [git2text options...]

Options:
  --dry-run                Print composed command without executing git2text.
  --require-output <path>  Validate output file exists and is non-empty after execution.
USAGE
}

is_remote_source() {
  case "$1" in
    http://*|https://*|ssh://*|git@*|*.git)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

DRY_RUN=0
REQUIRE_OUTPUT=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --require-output)
      if [ "$#" -lt 2 ]; then
        echo "Error: --require-output requires a path argument." >&2
        usage
        exit 2
      fi
      REQUIRE_OUTPUT="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -*)
      break
      ;;
    *)
      break
      ;;
  esac
done

if [ "$#" -lt 1 ]; then
  usage
  exit 2
fi

SOURCE="$1"
shift

if ! is_remote_source "$SOURCE" && [ ! -e "$SOURCE" ]; then
  echo "Error: source does not exist: $SOURCE" >&2
  exit 2
fi

if command -v git2text >/dev/null 2>&1; then
  CMD=(git2text "$SOURCE" "$@")
elif command -v python >/dev/null 2>&1; then
  CMD=(python -m src.git2text "$SOURCE" "$@")
elif command -v python3 >/dev/null 2>&1; then
  CMD=(python3 -m src.git2text "$SOURCE" "$@")
else
  echo "Error: could not find 'git2text', 'python', or 'python3' to execute git2text." >&2
  exit 127
fi

echo "Running: ${CMD[*]}"

if [ "$DRY_RUN" -eq 1 ]; then
  exit 0
fi

"${CMD[@]}"

if [ -n "$REQUIRE_OUTPUT" ]; then
  if [ ! -s "$REQUIRE_OUTPUT" ]; then
    echo "Error: required output is missing or empty: $REQUIRE_OUTPUT" >&2
    exit 1
  fi
  echo "Validated output: $REQUIRE_OUTPUT"
fi
