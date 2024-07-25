FROM python:3.11-slim AS base

ARG POETRY_HOME=/etc/poetry
RUN apt-get update && \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get install -y libyaml-dev curl tini && \
    curl -sSL https://install.python-poetry.org | POETRY_HOME=${POETRY_HOME} python - --version 1.7.1 && \
    apt-get remove -y curl && \
    apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="${PATH}:${POETRY_HOME}/bin"

COPY poetry.lock pyproject.toml ./

FROM base as development

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-cache

ENV PYTHONPATH=/
COPY ./manage.py /manage.py
COPY ./config/ /config
COPY ./deploy/gunicorn /deploy/gunicorn
COPY regbot /regbot

RUN poetry run python ./manage.py collectstatic