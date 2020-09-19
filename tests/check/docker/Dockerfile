ARG IMAGE
FROM ${IMAGE}

ARG PKG
COPY tests/check/requirements.txt requirements-test.txt
COPY extras/requirements.txt requirements-src.txt
# install requirements
RUN python3 -m pip install --upgrade pip \
 && python3 -m pip install --no-cache-dir --upgrade -r requirements-test.txt \
 && python3 -m pip install --no-cache-dir --upgrade -r requirements-src.txt

ARG HOME
WORKDIR ${HOME}

ADD src ${PKG}
ADD tests tests
