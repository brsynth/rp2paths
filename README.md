# RP2paths -- RetroPath2.0 to pathways

[![Anaconda-Server Badge](https://anaconda.org/brsynth/rp2paths/badges/latest_release_date.svg)](https://anaconda.org/brsynth/rp2paths)
[![Anaconda-Server Badge](https://anaconda.org/brsynth/rp2paths/badges/version.svg)](https://anaconda.org/brsynth/rp2paths)

RP2paths extracts the set of pathways that lies in a metabolic space file outputted by the RetroPath2.0 workflow. RetroPath2.0 is freely accessible on myExperiment.org at: https://www.myexperiment.org/workflows/4987.html.

## Installation

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
conda env create -f environment.yml -n <dev_env>
conda develop -n <dev_env> .
conda activate <dev_env>
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

### Build and deployment

The process is automated with GitHub's Action.

If you want to check the build process locally:

```bash
CONDA_BLD_PATH=<repository>/conda-bld
mkdir -p ${CONDA_BLD_PATH} 
cd <repository>

conda env create -f recipe/conda_build_env.yaml -n <build_env>
conda activate <build_env>
conda build -c conda-forge -c cyclus --output-folder ${CONDA_BLD_PATH} recipe

conda convert --platform osx-64 --platform linux-64 --platform win-64 --output-dir ${CONDA_BLD_PATH} ${CONDA_BLD_PATH}/*/rp2paths-*
```

## How to cite RP2paths?
Please cite:

Delepine B, Duigou T, Carbonell P, Faulon JL. RetroPath2.0: A retrosynthesis workflow for metabolic engineers. Metabolic Engineering, 45: 158-170, 2018. DOI: https://doi.org/10.1016/j.ymben.2017.12.002

## Licence
RP2paths is released under the MIT licence. See the LICENCE.txt file for details.
