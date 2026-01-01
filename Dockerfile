FROM docker.arvancloud.ir/python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY production.txt.txt /app/requirements/production.txt
RUN pip install --no-cache-dir -r /app/requirements/production.txt

COPY . /app

EXPOSE 8000
