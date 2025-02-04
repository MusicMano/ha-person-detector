ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.18
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install system dependencies
RUN \
    apk add --no-cache \
        python3 \
        py3-pip \
        gcc \
        python3-dev \
        musl-dev \
        linux-headers

# Install python packages
RUN pip3 install --no-cache-dir \
    numpy \
    opencv-python-headless \
    aiohttp \
    pillow

# Copy root filesystem
COPY rootfs /

WORKDIR /app

# Copy app files
COPY person_detector.py /app/
COPY edge-impulse-standalone.* /app/

# Build arguments
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_DESCRIPTION
ARG BUILD_NAME
ARG BUILD_REF
ARG BUILD_REPOSITORY
ARG BUILD_VERSION

# Labels
LABEL \
    io.hass.name="${BUILD_NAME}" \
    io.hass.description="${BUILD_DESCRIPTION}" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION}