# Start with a base Python image that includes Python 3
FROM python:3.9-slim

# Install system dependencies needed for OpenCV and s6-overlay
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install s6-overlay
ENV S6_OVERLAY_VERSION=3.1.5.0
RUN curl -L -s https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz | tar -C / -Jxf - \
    && curl -L -s https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz | tar -C / -Jxf -

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy your application files
COPY person_detector.py /app/
COPY run.sh /app/
RUN chmod +x /app/run.sh

# Copy the s6-overlay service definitions
COPY services.d /etc/services.d

# Set the entry point to use s6-overlay
ENTRYPOINT ["/init"]