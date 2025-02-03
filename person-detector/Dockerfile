ARG BUILD_FROM=ghcr.io/hassio-addons/base:14.0.2
FROM ${BUILD_FROM}

# Install dependencies
RUN \
    apk add --no-cache \
        python3 \
        py3-pip \
        py3-numpy \
        py3-pillow \
        py3-aiohttp \
        nodejs \
        npm

WORKDIR /app

# Copy app files
COPY run.sh /app/
COPY person_detector.py /app/
COPY edge-impulse-standalone.* /app/

RUN chmod a+x /app/run.sh

# Copy root filesystem
COPY rootfs /

ENTRYPOINT ["/init"]