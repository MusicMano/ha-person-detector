ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.15
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Setup base
RUN \
    apk add --no-cache \
        python3 \
        py3-pip \
        py3-pillow \
        nodejs \
        npm 

# Install Python dependencies
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Create working directory
WORKDIR /app

# Copy files
COPY run.sh /app/
COPY person_detector.py /app/
COPY edge-impulse-standalone.* /app/

RUN chmod a+x /app/run.sh

CMD ["/app/run.sh"]