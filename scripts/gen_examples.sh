#!/bin/bash
echo "Generate cleaned example data."

if [[ $# -ne 1 ]]; then
  echo "Usage: {folder}"
  exit 1
fi

if [[ -n $1 ]]; then
  OUT=$1
fi

DIR=$(dirname -- "$0")

# Generate data.
bash "$DIR"/gen_data.sh "$OUT"
# Clean meta data.
bash "$DIR"/clean_svg.sh "$OUT"
