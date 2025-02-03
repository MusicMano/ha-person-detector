ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.11-alpine3.18
FROM ${BUILD_FROM}

# Copy root filesystem
COPY rootfs /

# Install dependencies
RUN \
    apk add --no-cache \
        python3 \
        py3-numpy \
        py3-pillow \
        py3-aiohttp \
        bash \
        nodejs \
        npm \
        jq

# Create app directory
WORKDIR /app

# Copy app files
COPY run.sh /app/
COPY person_detector.py /app/
COPY edge-impulse-standalone.* /app/

RUN chmod a+x /app/run.sh

# Set workdir
WORKDIR /app

# Labels
LABEL \
    io.hass.version="1.0.0" \
    io.hass.type="addon" \
    io.hass.arch="aarch64|amd64|armhf|armv7|i386"

# Entrypoint
ENTRYPOINT ["/init"]