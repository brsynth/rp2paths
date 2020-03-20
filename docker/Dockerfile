ARG PYTHON_PACKAGES_DIR=/usr/local/lib/python3.8/site-packages


###############################################
# INSTALL tools for rp2paths                  #
###############################################
FROM brsynth/rdkit AS tools
RUN apk update \
 && apk --no-cache add \
      g++ \
      libxslt-dev
RUN pip install \
      pandas \
      pydotplus \
      graphviz \
      lxml


FROM brsynth/rdkit
# Copy tools
COPY --from=tools ${PYTHON_PACKAGES_DIR} ${PYTHON_PACKAGES_DIR}
RUN apk update \
 && apk add openjdk11-jre

WORKDIR /home

#ENTRYPOINT python3 src/RP2paths.py
