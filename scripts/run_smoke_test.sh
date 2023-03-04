#!/bin/bash
echo "Generate current data and compare against reference data."

if [[ $# -ne 2 ]]; then
  echo "Usage: {folder_reference} {folder_comparison}"
  exit 1
fi

if [[ -n $1 ]]; then
  FILES1=$1
fi
if [[ -n $2 ]]; then
  FILES2=$2
fi
if ! [[ -d $FILES1 ]]; then
  echo "This folder does not exists: $FILES1"
  exit 1
fi

DIR=$(dirname -- "$0")

# Generate current data.
bash "$DIR"/gen_examples.sh "$FILES2"
# For sanity clean reference data.
bash "$DIR"/clean_svg.sh "$FILES1"
# Do the test.
bash "$DIR"/gen_compare.sh "$FILES1" "$FILES2"
