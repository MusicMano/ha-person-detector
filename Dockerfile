ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.18
FROM ${BUILD_FROM}

WORKDIR /app

RUN apk update && \
    apk add --no-cache \
    python3 \
    py3-pip

RUN pip3 install --no-cache-dir aiohttp numpy opencv-python-headless

COPY . /app/
RUN chmod a+x /app/run.sh

CMD [ "/app/run.sh" ]