#!/bin/sh
outdir=$1

if [[ "$outdir" == "" ]]; then
  outdir="out/test-standalone"
fi


python3 ../src/RP2paths.py all in/rp2_pathways.csv --outdir $outdir --timeout 5
