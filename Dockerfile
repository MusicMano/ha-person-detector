ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install system dependencies first
RUN apk add --no-cache \
    python3 \
    py3-pip \
    nodejs \
    npm \
    git \
    build-base \
    python3-dev \
    jpeg-dev \
    zlib-dev \
    openblas-dev \
    libffi-dev \
    freetype-dev \
    libjpeg \
    libpng-dev \
    libstdc++

# Set up Python environment
ENV PYTHONUNBUFFERED=1

# We'll install packages one at a time with specific error handling
RUN pip3 install --upgrade pip setuptools

# Try installing wheel with verbose output for debugging
RUN pip3 install --verbose wheel || echo "Wheel installation failed, continuing anyway"

# Install basic dependencies first
RUN pip3 install --no-cache-dir paho-mqtt

# Try installing more complex packages with fallbacks
RUN pip3 install --no-cache-dir pillow || pip3 install --no-cache-dir --no-binary :all: pillow

# For numpy and OpenCV, we'll use specific versions with fewer dependencies
RUN pip3 install --no-cache-dir numpy==1.21.6 || pip3 install --no-cache-dir --no-binary :all: numpy==1.21.6
RUN pip3 install --no-cache-dir opencv-python-headless==4.5.1.48 || echo "OpenCV installation failed, will handle in code"

# Install Edge Impulse Linux CLI tools
RUN npm install edge-impulse-linux@1.14.7 -g

# Copy files
COPY . /app
WORKDIR /app

# Make run script executable
RUN chmod a+x /app/run.sh

# Command to run
CMD [ "/app/run.sh" ]