ARG TOOL_NAME

FROM brsynth/${TOOL_NAME}:flask

# FLASK
RUN pip install --upgrade pip
RUN pip install flask flask-restful

# REDIS
RUN pip install rq
RUN apt-get update
RUN apt-get --quiet --yes install supervisor redis-server

WORKDIR /REST

RUN export LC_ALL=C.UTF-8 \
 && export LANG=C.UTF-8

ENTRYPOINT supervisord -c /CONF/supervisor.conf & python3 /REST/Main.py redis

# Open server port
EXPOSE 8888
