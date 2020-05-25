#!/bin/bash

printf "\n"

tput bold
printf "Test normal case\n"
tput sgr0
python3 ../src/RP2paths.py all in/rp2_pathways.csv --outdir out --timeout 5
printf "\n"

tput bold
printf "Test no scope matrix produced"
tput sgr0
python3 ../src/RP2paths.py all in/rp2_pathways_nomatrix.csv --outdir out --timeout 5
