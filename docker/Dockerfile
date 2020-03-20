#FROM conda/miniconda3
FROM brsynth/rdkit

#RUN conda update -n base -c defaults conda
#RUN conda install -y -c rdkit rdkit
#RUN conda install --quiet --yes python-graphviz pydotplus lxml

RUN apk update
 # \
 # && apk add \
 #      py3-graphviz \
 #      py3-lxml \
 #      libxrender \
 #      libxext

# For rp2paths
RUN apk add openjdk11-jre

WORKDIR /home

#ENTRYPOINT python3 src/RP2paths.py
