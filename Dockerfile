ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install system dependencies (using apt for Debian/Ubuntu-based containers)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-dev \
    python3-pip \
    build-essential \
    libatlas-base-dev \
    libopencv-dev \
    nodejs \
    npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Edge Impulse Linux CLI tools
RUN npm install edge-impulse-linux -g --unsafe-perm

# Copy files
COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip wheel setuptools
RUN pip3 install --no-cache-dir -r requirements.txt

# Make run script executable
RUN chmod a+x /app/run.sh

# Command to run
CMD [ "/app/run.sh" ]