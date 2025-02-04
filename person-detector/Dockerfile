FROM python:3.9-alpine

# Install system dependencies
RUN apk add --no-cache \
    nodejs \
    npm \
    gcc \
    musl-dev \
    python3-dev

# Install Python packages
RUN pip3 install --no-cache-dir \
    numpy \
    pillow \
    aiohttp

WORKDIR /app

# Copy files
COPY . .

CMD ["python3", "person_detector.py"]