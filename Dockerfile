# syntax=docker/dockerfile:1

FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends chafa xdg-utils && \
    rm -rf /var/lib/apt/lists/*
RUN ln -s /usr/bin/chafa /usr/bin/www-browser

COPY . .

RUN pip3 install --no-cache-dir -r requirements/docker.txt
RUN playwright install --with-deps webkit

CMD ["python3", "main.py"]
