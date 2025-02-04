ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.18
FROM ${BUILD_FROM}

# Install required packages
RUN \
    apk add --no-cache \
        python3 \
        py3-pip \
        py3-numpy \
        py3-pillow \
        py3-aiohttp \
        nodejs \
        npm \
        gcc \
        musl-dev \
        python3-dev \
        linux-headers

# Install OpenCV
RUN pip3 install --no-cache-dir opencv-python-headless

# Copy root filesystem
COPY rootfs /

# Copy app files
WORKDIR /app
COPY person_detector.py .
COPY edge-impulse-standalone.* .

# Labels
LABEL \
    io.hass.type="addon"