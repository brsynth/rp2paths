# RP2paths -- RetroPath2.0 to pathways

RP2paths extracts the set of pathways that lies in a metabolic space file outputed by the RetroPath2.0 workflow. RetroPath2.0 is freely accessible on myExperiment.org at: https://www.myexperiment.org/workflows/4987.html.

### Installation
Installation steps are described in the INSTALL file.

### Quick start
The main code is `src/RP2paths.py`. Once a scope has been produced by RetroPath2.0, a typical command line for extracting the pathways from the results is:
```
python src/RP2paths.py all <path_to_rp2-results.csv> --outdir <path_to_pathways>
```
where:
- `all` specify that all the tasks needed for retreiving pathways will be executed at once.
- `results.csv` is the metabolic space outputted by the RetroPath2.0 workflow.
- `--outdir pathways` specify the directory in which all files will be outputted (here in `pathways` subfolder).

Additional options are described in the embedded help
```
python src/RP2paths.py -h
python src/RP2paths.py all -h
```

In the output folder (here `pathways`), the complete set of pathways enumerated will be written in the `out_paths.csv` file. In addition, for each pathway there will be a .dot file (.dot representation of the graph) and a .svg file (.svg depiction of the pathway).


### Installation with Docker
You can use this tool into a Docker container. For this, the Docker image has to be built with:
```
cd docker
docker-compose build
```

### Quick start with Docker
Then, the tool is runnable by:
```
cd docker
./RP2paths-in-docker.sh all <path_to_rp2-results.csv> --outdir <path_to_out_pathways>
```



### Examples
Pregenerated result files (i.e. outputed by RetroPath2.0) are provided in the `examples` folder for few compounds (carotene, naringenin, pinocembrin, violacein).

Below are the command lines for generating pathways that lie in `naringenin` result file:
1. If needed, activate the python environment (here named `py35`) that provides all the mandatory python library (see the installation section for details):
```
source activate py35
```

2. Create the parent folder if it does not exist yet:
```
mkdir pathways
```

3. Retreive pathways:
```
python src/RP2paths.py all examples/naringenin/rp2-results.csv --outdir examples/naringenin/pathways
```

### How to cite RP2paths?
Please cite:

Delépine B, Duigou T, Carbonell P, Faulon JL. RetroPath2.0: A retrosynthesis workflow for metabolic engineers. Metabolic Engineering, 45: 158-170, 2018. DOI: https://doi.org/10.1016/j.ymben.2017.12.002

### Licence
RP2paths is released under the MIT licence. See the LICENCE.txt file for details.
