# RP2paths -- RetroPath2.0 to pathways

[![Anaconda-Server Badge](https://anaconda.org/brsynth/rp2paths/badges/latest_release_date.svg)](https://anaconda.org/brsynth/rp2paths) [![Anaconda-Server Badge](https://anaconda.org/brsynth/rp2paths/badges/version.svg)](https://anaconda.org/brsynth/rp2paths)

RP2paths extracts the set of pathways that lies in a metabolic space file outputed by the RetroPath2.0 workflow. RetroPath2.0 is freely accessible on myExperiment.org at: https://www.myexperiment.org/workflows/4987.html.

## Input

Required:
* **rp2_pathways**: (string) Path to the RetroPath2.0 pathways file

Advanced options:
* **outdir**: (string) Path to the folder where result files are written


## Prerequisites

* Python 3


## Install
### From pip
```sh
[sudo] python -m pip install rp2paths
```
### From Conda
```sh
[sudo] conda install -c brsynth rp2paths
```

## Run

### From CLI
The main code is `src/RP2paths.py`. Once a scope has been produced by RetroPath2.0, a typical command line for extracting the pathways from the results is:
```sh
python -m rp2paths all rp2_pathways.csv [--outdir <outdir>]
```
where:
- `all` specify that all the tasks needed for retreiving pathways will be executed at once.
- `rp2_pathways.csv` is the metabolic space outputted by the RetroPath2.0 workflow.
- `--outdir pathways` specify the directory in which all files will be outputted (here in `pathways` subfolder).

Additional options are described in the embedded help
```
python -m rp2paths -h
python -m rp2paths all -h
```

In the output folder (here `pathways`), the complete set of pathways enumerated will be written in the `out_paths.csv` file. In addition, for each pathway there will be a .dot file (.dot representation of the graph) and a .svg file (.svg depiction of the pathway).

### Examples
Precomputed result files (i.e. outputted by RetroPath2.0) are provided in the `examples` folder for few compounds (carotene, naringenin, pinocembrin, violacein).

Below are the command lines for generating pathways that lie in `naringenin` result file:

1. If needed, activate the python environment (here named `pyenv`) that provides all the mandatory python library (see the installation section for details):
```
source activate pyenv
```

2. Retrieve pathways:
```
python -m rp2paths all examples/naringenin/rp2-results.csv --outdir examples/naringenin/pathways
```


## Test
All modes can be tested with:
```
cd tests
./test-in-docker.sh
```



## How to cite RP2paths?
Please cite:

Delépine B, Duigou T, Carbonell P, Faulon JL. RetroPath2.0: A retrosynthesis workflow for metabolic engineers. Metabolic Engineering, 45: 158-170, 2018. DOI: https://doi.org/10.1016/j.ymben.2017.12.002

## Licence
RP2paths is released under the MIT licence. See the LICENCE.txt file for details.
