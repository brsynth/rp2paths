# RP2paths -- RetroPath2.0 to pathways

[![Anaconda-Server Badge](https://anaconda.org/brsynth/rp2paths/badges/latest_release_date.svg)](https://anaconda.org/brsynth/rp2paths)
[![Anaconda-Server Badge](https://anaconda.org/brsynth/rp2paths/badges/version.svg)](https://anaconda.org/brsynth/rp2paths)

RP2paths extracts the set of pathways that lies in a metabolic space file outputed by the RetroPath2.0 workflow. RetroPath2.0 is freely accessible on myExperiment.org at: https://www.myexperiment.org/workflows/4987.html.

## Installation

### Prerequisites

rp2paths relies on several packages (rdkit, cairo) and binaries (java, graphviz) that can't be installed directly with pip. Please install them before pursuing the rp2paths set up:

```bash
# from a new <myenv> conda environment
conda create --name <myenv> python=3
conda install --yes --channel rdkit rdkit cairo
conda install --yes --channel cyclus java-jre
conda install --yes --channel conda-forge graphviz
```


### From pip
```bash
# installation in an already existing <myenv> environment (see prerequisites)
conda activate <myenv>
python -m pip install rp2paths
```

### From conda
```bash
# installation in an already existing <myenv> environment (see prerequisites)
conda activate <myenv>
conda install -c brsynth rp2paths
```

## Usage

### From CLI

Once a scope has been produced by RetroPath2.0, a typical command line for extracting the pathways from the results is

```bash
python -m rp2paths all <retropath2_scope> [--outdir <outdir>]
```

where:
- `all` specify that all the tasks needed for retrieving pathways will be executed at once.
- `<retropath2_scope>` is the metabolic space outputted by the RetroPath2.0 workflow.
- `--outdir <outdir>` specify the directory in which all files will be outputted.

In the `<outdir>` folder, the complete set of pathways enumerated will be written in the `out_paths.csv` file. In addition, for each pathway there will be a .dot file (.dot representation of the graph) and a .svg file (.svg depiction of the pathway).

### Available options

Additional options are described in the embedded help:
```
# List of possible modes
python -m rp2paths -h

# List of options for the all-in-one mode
python -m rp2paths all -h
```

### Examples

Precomputed results (outputted by RetroPath2.0) are provided in the `examples` folder for few compounds (carotene, naringenin, pinocembrin, violacein).

Below are the command lines for generating pathways that lie in `naringenin` result file:

```bash
source activate <myenv>
python -m rp2paths all examples/naringenin/rp2-results.csv --outdir examples/naringenin/outdir
````


## For developers

### Development installation

After a git clone:
```bash
cd <repository>
conda create --name <dev_env> python=3
conda install --name <dev_env> --yes --channel rdkit rdkit cairo
conda install --name <dev_env> --yes --channel cyclus java-jre
conda install --name <dev_env> --yes --channel conda-forge graphviz flake8
conda install --name <dev_env> --yes pytest
conda develop --name <dev_env> .
```

### Tests

Using Docker containers with:
```
cd tests
./test-in-docker.sh [file_to_test]
```

Without using Docker containers:
```
cd tests
conda activate <dev_env>
pytest [file_to_test]
```


## How to cite RP2paths?
Please cite:

Delepine B, Duigou T, Carbonell P, Faulon JL. RetroPath2.0: A retrosynthesis workflow for metabolic engineers. Metabolic Engineering, 45: 158-170, 2018. DOI: https://doi.org/10.1016/j.ymben.2017.12.002

## Licence
RP2paths is released under the MIT licence. See the LICENCE.txt file for details.
