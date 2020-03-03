FROM brsynth/rest:flask-conda

RUN conda update -n base -c defaults conda

RUN conda install -y -c rdkit rdkit
RUN conda install --quiet --yes python-graphviz pydotplus lxml

RUN apt-get update
# For rdkit
RUN apt-get install -y \
  libxrender1 \
  libxext6
# For rp2paths
RUN apt-get install -y openjdk-8-jre

WORKDIR /home
