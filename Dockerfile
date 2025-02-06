ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.15
FROM ${BUILD_FROM}

WORKDIR /app

RUN \
    apk add --no-cache \
        python3 \
        py3-pip \
        py3-aiohttp \
        py3-numpy \
        py3-opencv

COPY . /app/
RUN chmod a+x /app/run.sh

CMD [ "/app/run.sh" ]