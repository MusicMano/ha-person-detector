ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.18
FROM ${BUILD_FROM}

# Install required packages
RUN \
    apk add --no-cache \
        python3 \
        py3-pip \
        py3-numpy \
        py3-pillow \
        py3-opencv \
        py3-aiohttp \
        nodejs \
        npm

# Copy root filesystem
COPY rootfs /

# Copy app files
WORKDIR /app
COPY person_detector.py .
COPY edge-impulse-standalone.* .

# Labels
LABEL \
    io.hass.type="addon"