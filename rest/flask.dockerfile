ARG TOOL_NAME

FROM brsynth/${TOOL_NAME}

# FLASK
RUN pip install --upgrade pip
RUN pip install flask flask-restful

WORKDIR /REST

RUN export LC_ALL=C.UTF-8 \
 && export LANG=C.UTF-8

ENTRYPOINT python3 /REST/Main.py flask

# Open server port
EXPOSE 8888
