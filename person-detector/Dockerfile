ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.11-alpine3.18
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install dependencies
RUN \
    apk add --no-cache \
        python3 \
        py3-numpy \
        py3-pillow \
        py3-aiohttp \
        bash \
        nodejs \
        npm

# Create working directory
WORKDIR /app

# Copy files
COPY run.sh /app/
COPY person_detector.py /app/
COPY edge-impulse-standalone.* /app/

RUN chmod a+x /app/run.sh

CMD [ "/app/run.sh" ]