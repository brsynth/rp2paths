#! /bin/bash
#
# Copyright (C) 2017 JL Faulon's research group, INRA
#

if [ ! $# -eq 2 ]; then
    echo "Usage: $0 basename outname"
    exit 1
fi

in=$1
out=$2

set -e

script_dir=`dirname $0`
elemodes="$script_dir/elemodes.jar"

java -jar $elemodes -kind stoichiometry -stoich ${in}_mat -rev ${in}_rever -meta ${in}_comp -reac ${in}_react -arithmetic double -zero 1e-10  -compression default -log console -level INFO -maxthreads -1 -normalize min -adjacency-method pattern-tree-minzero -rowordering MostZerosOrAbsLexMin -out text-boolean ${out}_efm
