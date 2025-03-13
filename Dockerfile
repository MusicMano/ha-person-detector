ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install basic dependencies first
RUN apk add --no-cache \
    python3 \
    py3-pip \
    build-base \
    python3-dev \
    nodejs \
    npm \
    jpeg-dev \
    zlib-dev

# Copy files
COPY . /app
WORKDIR /app

# Make run script executable
RUN chmod a+x /app/run.sh

# Install Python requirements
# We'll use pip instead of apk for the more complex packages
RUN pip3 install --no-cache-dir numpy opencv-python-headless pillow paho-mqtt

# Install Edge Impulse Linux CLI tools
RUN npm install edge-impulse-linux -g

# Command to run
CMD [ "/app/run.sh" ]