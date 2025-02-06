ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.15
FROM ${BUILD_FROM}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-pillow \
    nodejs \
    npm \
    opencv

RUN pip3 install --no-cache-dir \
    aiohttp \
    numpy \
    opencv-python-headless

WORKDIR /app

COPY rootfs /
COPY person_detector.py /app/
COPY edge-impulse-standalone.* /app/
COPY run.sh /app/

RUN chmod a+x /app/run.sh

CMD [ "/app/run.sh" ]
