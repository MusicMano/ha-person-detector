FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-opencv \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install numpy pillow aiohttp

WORKDIR /app

# Copy application files
COPY person_detector.py .
COPY edge-impulse-standalone.* .

# Copy service files
COPY rootfs/ /

# Make service executable
RUN chmod a+x /etc/services.d/person-detector/run

CMD ["/etc/services.d/person-detector/run"]