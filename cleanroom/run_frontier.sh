#!/bin/sh
set -eu

MOCKS="${1:-5000}"
WORKERS="${2:-1}"
OUTPUT_DIR="${3:-cleanroom/frontier-output}"

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PYTHON="$PROJECT_DIR/.venv-cleanroom/bin/python"

if [ ! -x "$PYTHON" ]; then
  echo "Missing .venv-cleanroom. Follow cleanroom/README.md first." >&2
  exit 2
fi

cd "$PROJECT_DIR"
mkdir -p "$OUTPUT_DIR"

"$PYTHON" -m unittest discover -s tests -v
"$PYTHON" scripts/time_variation_mocks.py \
  --mocks "$MOCKS" \
  --workers "$WORKERS" \
  --chunk-size 25 \
  --output "$OUTPUT_DIR/time-variation.json" \
  --fresh
"$PYTHON" scripts/time_variation_mocks.py \
  --mocks "$MOCKS" \
  --workers "$WORKERS" \
  --chunk-size 25 \
  --drop-index 2 \
  --output "$OUTPUT_DIR/time-variation-no-lrg2.json" \
  --fresh
"$PYTHON" scripts/lrg2_posterior_predictive.py \
  --mocks "$MOCKS" \
  --workers "$WORKERS" \
  --chunk-size 100 \
  --output "$OUTPUT_DIR/lrg2-posterior-predictive.json" \
  --fresh
