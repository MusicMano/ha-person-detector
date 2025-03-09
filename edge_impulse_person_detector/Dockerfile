FROM python:3.9-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install dependencies
RUN pip install aiohttp

# Copy code
COPY person_detector.py /app/
COPY run.sh /app/
RUN chmod +x /app/run.sh

# Use absolute path in CMD
CMD ["python3", "/app/person_detector.py"]