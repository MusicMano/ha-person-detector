FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY person_detector.py .
COPY run.sh .
RUN chmod +x run.sh

CMD ["bash", "-c", "python3 /app/person_detector.py --camera \"${CAMERA_ENTITY}\" --confidence \"${CONFIDENCE_THRESHOLD}\" --interval \"${SCAN_INTERVAL}\" --ei-api-key \"${EDGE_IMPULSE_API_KEY}\""]