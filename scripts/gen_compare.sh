#!/bin/bash
echo "Compares files in two folders."

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
if ! [[ -d $FILES2 ]]; then
  echo "This folder does not exists: $FILES2"
  exit 1
fi

echo "Start comparing folders."
echo "Reference: $FILES1"
echo "Comparison: $FILES2"

ERROR=false

for f in "$FILES1"/*; do
  FILENAME="$(basename -- "$f")"
  echo "Compare: $FILENAME"
  f2="$FILES2"/"$FILENAME"
  if ! [[ -f $f ]]; then
    echo "This file does not exists: $f"
    exit 1
  fi
  if ! [[ -f $f2 ]]; then
    echo "This file does not exists: $f2"
    exit 1
  fi
  # if cmp --silent -- "$f" "$f2"; then # Problems with line endings.
  if diff -q --strip-trailing-cr -- "$f" "$f2"; then
    echo "[OK] files equal."
  else
    echo "[ERROR] files differ."
    diff --strip-trailing-cr -- "$f" "$f2"
    ERROR=true
  fi
done

if [ "$ERROR" == true ]; then
  echo "[ERROR] At least one error has occurred."
  exit 1
fi
