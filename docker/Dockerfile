ARG PIP_INSTALL=/pip


###############################################
# INSTALL tools for rp2paths                  #
###############################################
# Same as final stage to be sure paths are the same
FROM brsynth/rdkit:debian AS tools

RUN python -m pip install --upgrade pip
ARG PIP_INSTALL
ENV PYTHONUSERBASE=$PIP_INSTALL/pandas
RUN python -m pip install --user pandas
ENV PYTHONUSERBASE=$PIP_INSTALL/pydotplus
RUN python -m pip install --user pydotplus
ENV PYTHONUSERBASE=$PIP_INSTALL/graphviz
RUN python -m pip install --user graphviz
ENV PYTHONUSERBASE=$PIP_INSTALL/lxml
RUN python -m pip install --user lxml



FROM brsynth/rdkit:debian

# Copy tools
ARG PIP_INSTALL
COPY --from=tools ${PIP_INSTALL}/* /usr/local/

# Install needed packages
RUN apt-get update \
 && apt-get install -y \
      openjdk-11-jre-headless \
      graphviz \
      python3-graphviz

WORKDIR /home/src

# Copy source code
COPY src .

#ENTRYPOINT python3 RP2paths.py
