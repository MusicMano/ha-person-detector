FROM python:3.9-alpine

# Install dependencies
RUN apk add --no-cache \
    python3 \
    py3-numpy \
    py3-pillow \
    py3-aiohttp \
    nodejs \
    npm

WORKDIR /app

# Copy files
COPY . .

CMD ["python3", "person_detector.py"]