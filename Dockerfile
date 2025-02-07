# Start with Python 3.9 slim image
FROM python:3.9-slim

# Install required packages including xz-utils
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    xz-utils \  # Added this package
    && rm -rf /var/lib/apt/lists/*

# Set s6-overlay version
ENV S6_OVERLAY_VERSION=3.1.5.0

# Install s6-overlay
RUN curl -L -s https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz | tar -C / -Jxf - \
    && curl -L -s https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz | tar -C / -Jxf -