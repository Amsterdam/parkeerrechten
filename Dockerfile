FROM amsterdam/python:3.8-buster as app
MAINTAINER datapunt@amsterdam.nl

WORKDIR /app/install
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY deploy /app/deploy

WORKDIR /app/src
COPY src .
COPY pyproject.toml /app

USER datapunt

# Build metadata
ARG BUILD_DATE
ARG BUILD_REVISION
ARG BUILD_VERSION
ENV BUILD_DATE=$BUILD_DATE
ENV BUILD_REVISION=$BUILD_REVISION
ENV BUILD_VERSION=$BUILD_VERSION

CMD ["echo", "hello world"]

# stage 2, dev
FROM app as dev

USER root
WORKDIR /app/install
ADD requirements_dev.txt requirements_dev.txt
RUN pip install -r requirements_dev.txt

WORKDIR /app/src
USER datapunt

# Any process that requires to write in the home dir
# we write to /tmp since we have no home dir
ENV HOME /tmp

CMD ["echo", "hello DEV world"]

# stage 3, tests
FROM dev as tests

USER datapunt
WORKDIR /app/tests
ADD tests .

ENV COVERAGE_FILE=/tmp/.coverage
ENV PYTHONPATH=/app/src

CMD ["pytest"]
