FROM python:3.11-slim AS builder

WORKDIR /app

RUN python -m pip install --no-cache-dir poetry==1.4.2

COPY poetry.lock pyproject.toml ./

RUN poetry install --no-root

COPY . .