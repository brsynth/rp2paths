# Installation details

### Set up a python environment using (ana)conda (tested with Linux & Mac)
```
# Build a dedicated python 3.6 environment
conda create --name pyenv python=3.6

# Activate the newly created environment
source activate pyenv  # For Linux and Mac OSs

# Install needed mandatory libraries
conda install --yes --channel rdkit rdkit
conda install --yes --channel anaconda graphviz
conda install --yes pandas lxml cairo  # cairo for compound depictions
yes | pip install graphviz pydotplus image

# Rdkit issue with picture generation
# conda install --channel rdkit cairocffi (might be not necessary)
```

### Install graphviz binaries

- For ubuntu:
    ```
    apt-get install graphviz
    ```
- For Mac OS (using HomeBrew):
    ```
    brew install graphviz
    ```
    ```
    # Or one can try (not tested)
    # brew install graphviz --with-bindings --with-freetype --with-librsvg --with-pangocairo
    ```
    Reconfigure graphviz if needed:
    ```
    sudo dot -c
    ```
