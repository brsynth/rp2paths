ARG PYTHON_PACKAGES_DIR=/usr/local/lib/python3.8/site-packages


###############################################
# BUILD pandas                                #
###############################################
FROM brsynth/rdkit AS tools
RUN apk update \
 && apk --no-cache add \
      g++
RUN pip install --upgrade pandas


FROM brsynth/rdkit
COPY --from=tools ${PYTHON_PACKAGES_DIR} ${PYTHON_PACKAGES_DIR}
COPY --from=tools ${PYTHON_PACKAGES_DIR} ${PYTHON_PACKAGES_DIR}
RUN apk update \
 && apk add openjdk11-jre

WORKDIR /home

#ENTRYPOINT python3 src/RP2paths.py
