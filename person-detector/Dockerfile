FROM python:3.9-alpine

# Install dependencies
RUN apk add --no-cache \
    python3 \
    py3-numpy \
    py3-pillow \
    py3-aiohttp \
    nodejs \
    npm

# Set workdir
WORKDIR /app

# Copy files
COPY run.sh /app/
COPY person_detector.py /app/
COPY edge-impulse-standalone.* /app/

# Make script executable
RUN chmod +x /app/run.sh

# Run script
CMD ["/app/run.sh"]