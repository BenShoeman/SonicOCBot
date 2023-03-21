# syntax=docker/dockerfile:1

FROM python:3.9-slim

ENV CHROME_ARGS=--no-sandbox

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends chromium chafa xorg && \
    rm -rf /var/lib/apt/lists/*
RUN ln -s /usr/bin/chafa /usr/bin/www-browser

COPY . .

RUN pip3 install --no-cache-dir -r requirements/minimal.txt

CMD ["python3", "main.py"]
