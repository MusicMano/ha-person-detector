ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.15
FROM ${BUILD_FROM}

ENV LANG C.UTF-8

# Install required packages
RUN \
    apk update && \
    apk add --no-cache \
        python3 \
        py3-pip \
        py3-numpy \
        py3-pillow \
        nodejs \
        npm \
        make \
        g++ \
        jpeg-dev \
        zlib-dev \
        gcc \
        musl-dev \
        python3-dev

# Install Python dependencies
RUN pip3 install --no-cache-dir \
    aiohttp \
    pillow

# Set up workspace
WORKDIR /usr/src/app

# Copy files
COPY run.sh /
COPY person_detector.py /
COPY edge-impulse-standalone.* /

# Make scripts executable
RUN chmod a+x /run.sh

# Label
LABEL \
    io.hass.name="Edge Impulse Person Detector" \
    io.hass.description="Person detection using Edge Impulse" \
    io.hass.type="addon" \
    io.hass.arch="amd64"

CMD [ "/run.sh" ]