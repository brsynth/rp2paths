ARG PIP_INSTALL=/pip


###############################################
# INSTALL tools for rp2paths                  #
###############################################
FROM brsynth/rdkit AS tools
RUN apk update \
 && apk --no-cache add \
      g++ \
      libxslt-dev
ARG PIP_INSTALL
ENV PYTHONUSERBASE=$PIP_INSTALL/pandas
RUN pip install --user pandas
ENV PYTHONUSERBASE=$PIP_INSTALL/pydotplus
RUN pip install --user pydotplus
ENV PYTHONUSERBASE=$PIP_INSTALL/graphviz
RUN pip install --user graphviz
ENV PYTHONUSERBASE=$PIP_INSTALL/lxml
RUN pip install --user lxml


FROM brsynth/rdkit

# Copy tools
ARG PIP_INSTALL
COPY --from=tools ${PIP_INSTALL}/* /usr/local/

# Install needed packages
RUN apk update \
 && apk add \
      openjdk11-jre \
      graphviz \
      libxslt \
      bash

WORKDIR /home/src

# Copy source code
COPY src .

ENTRYPOINT python3 RP2paths.py
