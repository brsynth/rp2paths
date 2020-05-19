#!/bin/bash
infile=$1
if [[ "$infile" == "" ]]; then
  echo
  echo "*** Usage is:"
  echo
  echo "     $0 <infile> [outdir]"
  echo
  echo
  exit 1
fi

outdir=$2
if [[ "$outdir" == "" ]]; then
  outdir="out/test"
fi


python3 ../src/RP2paths.py all $infile --outdir $outdir --timeout 5
