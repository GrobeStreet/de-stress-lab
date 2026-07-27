#!/bin/sh
set -eu

MOCKS="${1:-5000}"
WORKERS="${2:-1}"
OUTPUT="${3:-cleanroom/verification-output.json}"

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PYTHON="$PROJECT_DIR/.venv-cleanroom/bin/python"

if [ ! -x "$PYTHON" ]; then
  echo "Missing .venv-cleanroom. Follow cleanroom/README.md first." >&2
  exit 2
fi

cd "$PROJECT_DIR"
"$PYTHON" scripts/max_influence_mocks.py \
  --mocks "$MOCKS" \
  --workers "$WORKERS" \
  --chunk-size 100 \
  --output "$OUTPUT" \
  --fresh
