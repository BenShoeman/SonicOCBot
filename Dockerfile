# syntax=docker/dockerfile:1

FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && \
apt-get install -y --no-install-recommends curl chafa xdg-utils && \
rm -rf /var/lib/apt/lists/*
RUN ln -s /usr/bin/chafa /usr/bin/www-browser

COPY . .

RUN pip3 install --no-cache-dir -r requirements/docker.txt
RUN playwright install --with-deps webkit

RUN curl -fsSL https://ollama.com/install.sh | sh
RUN bash -c "ollama serve &" && sleep 5 && ollama pull qwen2:1.5b

CMD ["bash", "docker_run.sh"]
