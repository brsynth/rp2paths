ARG IMAGE
FROM ${IMAGE}

RUN conda install -y -c rdkit rdkit \
 && conda install -y -c conda-forge graphviz \
 && conda install -y -c cyclus java-jre

ARG PKG
COPY tests/pytest/requirements.txt requirements-test.txt
COPY extras/requirements.txt requirements-src.txt
# install requirements
RUN python3 -m pip install --upgrade pip \
 && python3 -m pip install --no-cache-dir --upgrade -r requirements-test.txt \
 && python3 -m pip install --no-cache-dir --upgrade -r requirements-src.txt

ARG HOME
WORKDIR ${HOME}/tests

ADD tests .
ADD ${PKG} ${PKG}
