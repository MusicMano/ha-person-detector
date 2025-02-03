ARG BUILD_FROM=ghcr.io/hassio-addons/base:14.0.2
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
        npm

# Set workdir
WORKDIR /usr/src/app

# Copy files
COPY rootfs /
COPY run.sh /usr/src/app/
COPY person_detector.py /usr/src/app/
COPY edge-impulse-standalone.* /usr/src/app/

# Make scripts executable
RUN chmod a+x /usr/src/app/run.sh

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