# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

# System deps (kept minimal). If you see build errors, uncomment build tools.
# RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# Use Gunicorn to serve Flask app object `app` from app.py
CMD gunicorn -w ${WEB_CONCURRENCY:-2} -k gthread -b 0.0.0.0:${PORT} app:app
