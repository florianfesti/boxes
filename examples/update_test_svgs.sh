#!/bin/sh

cd "$(dirname "$0")" || exit
for i in *.svg; do cp "../tests/data/$i" . ; done
