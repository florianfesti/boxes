#!/bin/bash
echo "Clean data by removing metadata."

if [[ $# -ne 1 ]]; then
  echo "Usage: {folder}"
  exit 1
fi

if [[ -n $1 ]]; then
  FILES=$1
fi
if ! [[ -d $FILES ]]; then
  echo "This folder does not exists: $FILES"
  exit 1
fi

echo "Start cleaning folder: $FILES"
for f in "$FILES"/*
do
	echo "Clean: $f"
	## Remove changing lines.
	grep -v -E "(<dc:date>|<dc:source>|Creation date|Command line)" "$f" > "$f.tmp" && mv -f "$f.tmp" "$f"
done
echo "Finished cleaning folder."
