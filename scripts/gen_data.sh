#!/bin/bash
echo "Generate data."

if [[ $# -ne 1 ]]; then
  echo "Usage: {folder}"
  exit 1
fi

if [[ -n $1 ]]; then
  OUT=$1
fi

echo "Target folder: ${OUT}"
if ! [[ -d $OUT ]]; then
  echo "This folder does not exists! Create folder."
  mkdir "$OUT"
fi

DIR=$(dirname -- "$0")
BOXES="$DIR"/boxes

set -x
$BOXES castle --output="${OUT}"/castle.svg
$BOXES closedbox --x=50 --y=50 --h=70 --output="${OUT}"/closedbox.svg
$BOXES drillbox --output="${OUT}"/drillbox.svg
$BOXES flexbox --x=70 --y=100 --h=50 --radius=20 --output="${OUT}"/flexbox.svg
$BOXES flexbox2 --x=70 --y=100 --h=50 --radius=20 --output="${OUT}"/flexbox2.svg
$BOXES flexbox3 --x=70 --y=100 --z=50 --h=8 --radius=30 --output="${OUT}"/flexbox3.svg
$BOXES folder --x=165 --y=240 --h=20 --output="${OUT}"/folder.svg
$BOXES hingebox --x=50 --y=50 --h=70 --output="${OUT}"/hingebox.svg
$BOXES lamp --x=50 --y=50 --radius=10 --output="${OUT}"/lamp.svg
$BOXES magazinefile --output="${OUT}"/magazinefile.svg
$BOXES silverware --output="${OUT}"/silverware.svg
$BOXES trayinsert --sx=70:100:70 --sy=100*3 --h=50 --output="${OUT}"/trayinsert.svg
$BOXES traylayout --sx=10*5 --sy=10*5 --output="${OUT}"/traylayout.txt
$BOXES traylayout2 --input="${OUT}"/traylayout.txt --h=50 --hi=40 --output="${OUT}"/traylayout2.svg
$BOXES typetray --sx=70:100:70 --sy=100*3 --h=60 --hi=50 --output="${OUT}"/typetray.svg
