# Installation details

### Set up a python environment using (ana)conda (tested with Linux & Mac)
```
# Python 3.5
conda create --name pyenv python=3.5
source activate pyenv
# Rdkit
conda install --channel rdkit rdkit
# pandas
conda install pandas
# graphviz
pip install graphviz
pip install pydotplus
# svg parsing
conda install lxml
# Rdkit issue with picture generation
# conda install --channel rdkit cairocffi (might be not necessary)
pip install image
```

### Install graphviz binaries

- For ubuntu:
    ```
    apt-get install graphviz
    ```
- For mac (using HomeBrew):
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
