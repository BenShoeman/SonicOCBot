# syntax=docker/dockerfile:1

FROM python:3.9-slim

ENV CHROME_ARGS=--no-sandbox

WORKDIR /app

RUN apt update
RUN apt install -y --no-install-recommends wget
RUN wget -q -O /app/chromium.deb https://github.com/berkley4/ungoogled-chromium-debian/releases/download/110.0.5481.177-1/ungoogled-chromium_110.0.5481.177_amd64.deb
RUN apt install -y /app/chromium.deb && rm -rf /app/chromium.deb
RUN apt install -y --no-install-recommends chafa && \
    rm -rf /var/lib/apt/lists/*
RUN ln -s /usr/bin/chafa /usr/bin/www-browser

COPY . .

RUN pip3 install --no-cache-dir -r requirements/minimal.txt

CMD ["python3", "main.py"]
