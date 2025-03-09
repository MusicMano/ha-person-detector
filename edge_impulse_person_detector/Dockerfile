FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
RUN pip install aiohttp

# Copy code
COPY config.yaml /etc/config.yaml

CMD ["python3", "/app/person_detector.py"]