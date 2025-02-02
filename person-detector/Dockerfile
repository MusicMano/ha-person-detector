ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.15
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install required packages
RUN \
    apk add --no-cache \
        python3 \
        py3-pip \
        nodejs \
        npm

# Install Python dependencies
RUN pip3 install --no-cache-dir \
    numpy \
    opencv-python-headless \
    aiohttp

# Copy your files
COPY rootfs /
WORKDIR /
COPY run.sh /
COPY person_detector.py /
COPY edge-impulse-standalone.* /

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]

LABEL \
    io.hass.name="Edge Impulse Person Detector" \
    io.hass.description="Person detection using Edge Impulse" \
    io.hass.type="addon" \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.arch="${BUILD_ARCH}"