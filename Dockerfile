ARG BUILD_FROM
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-dev \
    python3-pip \
    build-essential \
    libatlas-base-dev \
    libopencv-dev \
    nodejs \
    npm \
    git \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy files
COPY . /app
WORKDIR /app

# Install Edge Impulse Linux CLI tools
RUN npm install edge-impulse-linux -g

# Install Python requirements
RUN pip3 install --no-cache-dir --upgrade pip wheel setuptools
RUN pip3 install --no-cache-dir numpy opencv-python-headless pillow paho-mqtt

# Make run script executable
RUN chmod a+x /app/run.sh

# Command to run
CMD [ "/app/run.sh" ]