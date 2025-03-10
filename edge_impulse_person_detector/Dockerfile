FROM python:3.9-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install dependencies for image processing
RUN apt-get update && apt-get install -y \
    jq \
    python3-pillow \
    && apt-get clean

# Install Python dependencies
RUN pip install aiohttp pillow

# Copy code
COPY person_detector.py /app/
COPY run.sh /app/
RUN chmod +x /app/run.sh

# Use absolute path in CMD
CMD ["python3", "/app/person_detector.py"]