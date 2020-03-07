#!/usr/bin/env bash

BOXES=../scripts/boxes

set -x
$BOXES closedbox --x=50 --y=50 --h=70 --output=closedbox.svg
$BOXES hingebox --x=50 --y=50 --h=70 --output=hingebox.svg
$BOXES castle --output=castle.svg
$BOXES drillbox --output=drillbox.svg
$BOXES flexbox --x=70 --y=100 --h=50 --radius=20 --output=flexbox.svg
$BOXES flexbox2 --x=70 --y=100 --h=50 --radius=20 --output=flexbox2.svg
$BOXES flexbox3 --x=70 --y=100 --z=50 --h=8 --radius=30 --output=flexbox3.svg
$BOXES folder --x=165 --y=240 --h=20 --r=10 --output=folder.svg
#$BOXES lamp --x=50 --y=50  --r=10 --output=lamp.svg
$BOXES magazinfile --output=magazinefile.svg
#$BOXES printer --output=printer.svg
#$BOXES Silverwaree --output=silverwarebox.svg
#$BOXES traylayout --x=4 --y=4 --output=traylayout.txt
$BOXES traylayout2 --input=traylayout.txt --h=50 --hi=40 --output=traylayout.svg
$BOXES trayinsert --sx=70:100:70 --sy=100*3 --h=50 --output=trayinsert.svg
$BOXES typetray --sx=70:100:70 --sy=100*3 --h=60 --hi=50 --output=typetray.svg
