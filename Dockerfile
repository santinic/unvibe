# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11.6
FROM python:${PYTHON_VERSION}-slim as base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . app
WORKDIR /app

RUN python -m pip install poetry
RUN python -m poetry install
RUN poetry run unvibe --help
RUN python -m pip install gunicorn

# Expose the port that the application listens on.
EXPOSE 8000

#CMD gunicorn '' --bind=0.0.0.0:8000
CMD poetry run unvibe-server
