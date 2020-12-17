# CI toolkit

This Continuous Integration toolkit provides tools to build and publish Conda packages. It is also possible to run fast tests in order to debug code.

## Requirements

### Packages
* [conda](https://docs.conda.io)
* [make](https://www.gnu.org/software/make)

### Files
This CI toolkit is designed to provide full development chain for a conda package. Thus, some files and folders are required in the package's root directory:
* `<package_name>/` folder which contains package source code
* `tests/` folder which contains test source code
* `recipe/` folder with:
  * `meta.yaml`: recipe file
  * `conda_build_config.yaml`: variants file for `conda-build` process
  * `conda_build_env.yaml`: environment file for `conda-build` processes
  * `conda_channels.txt`: file with channels needed to install the current package (one channel per line)

Requirements can be provided by a docker container by running the following commands (at package root folder):
```bash
docker run -it --rm -v $PWD:$PWD -w $PWD continuumio/miniconda3 bash
conda update --all -y
conda install -y make
cd ci
```

## Conda workflow

### Build
The building stage of conda package can be performed by:
```bash
make conda-build [variants=<variants>]
```
Equivalent to `conda build --build-only`. Only run the build, without  any  post  processing  or  testing. For tests, please see section about Test stage.

If `variants` option is set according to `--variants` `conda-build` option format, then this stage is performed all combinations of `variants`, otherwise combinations are deducted from `recipe/conda_build_config.yaml` file.

Also, `recipe/conda_build_config.yaml` file can be edited to target specific variant(s).

### Test
The testing stage of conda package can be performed by:
```bash
make conda-test [env=<conda_env_name>]
```
Equivalent to `conda build --test`.

If `env` option is set, then the `conda-build --test` command will run inside `env` conda environment. By default, `env` is set to `<package_name>_build`.

### Convert
The converting stage of conda package can be performed by:
```bash
make conda-convert [env=<conda_env_name>]
```
Equivalent to `conda convert`, the conversion is performed for all plaforms (`linux-64`, `osx-64` and `win-64`).

If `env` option is set, then the `conda convert` command will run inside `env` conda environment. By default, `env` is set to `<package_name>_build`.

### Publish
The publishing stage of conda package can be performed by:
```bash
make conda-publish [env=<conda_env_name>]
```
Equivalent to `anaconda upload`.

If `env` option is set, then the `anaconda upload` command will run inside `env` conda environment. By default, `env` is set to `<package_name>_build`.

Credentials have to be stored in `ci/.secrets` file with the following syntax:
```
ANACONDA_USER=<username>
ANACONDA_TOKEN=<token>
```

## Development tools
Conda workflow is heavy and long to perform. For development or debugging purposes, fast testing process is possible by:
```bash
make test [env=<conda_env_name>] args=[PATH_1, PATH_2...]
```
Equivalent to `pytest`, this stage is achieved within a conda environment. Then, `PATH_1, PATH2...` are paths to folders or filenames, just like in `pytest` command.

If `env` option is set then this stage is performed in `<conda_env_name>` (default: `test`) conda environment.

For environment automatic building, tests can be processed within conda environment:
```bash
make test-inconda [env=<conda_env_name>]  args=[PATH_1, PATH_2...]
```

### Run in interactive mode
To run the code in a debug process, it can be done with the following commands at the root of the repository:
```bash
conda activate {PACKAGE}_test
```
#### Run from command-line
```bash
python -m {PACKAGE} --help
```
#### Run from Python command-line
```bash
python
from brs_libs import rpSBML
```

## Workflows
The user will find into `workflows/` folder, several workflows for different CI/CD platform. These worfklows have to be copied into the right folder. For instance, GitHub needs to find workflows into `.github/workflows` to trigger actions.

## Authors

* **Joan Hérisson**

## Acknowledgments

* Thomas Duigou


## Licence
CI toolkit is released under the MIT licence. See the LICENCE file for details.
