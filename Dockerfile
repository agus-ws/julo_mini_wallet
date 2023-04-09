# syntax=docker/dockerfile:1
FROM python:3.10-slim-bullseye

ARG APP_HOME=/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  # psycopg2 dependencies
  libpq-dev

WORKDIR ${APP_HOME}

COPY requirements.txt ${APP_HOME}
RUN pip install -r requirements.txt

COPY . ${APP_HOME}
