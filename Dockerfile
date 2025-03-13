ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install dependencies
RUN \
    apk add --no-cache \
        python3 \
        py3-pip \
        nodejs \
        npm \
        git \
        build-base \
        python3-dev \
        jpeg-dev \
        zlib-dev

# Install Edge Impulse Linux CLI tools
RUN npm install edge-impulse-linux -g

# Copy files
COPY . /app
WORKDIR /app

# Make run script executable
RUN chmod a+x /app/run.sh

# Install Python requirements - specify versions that work with Alpine
RUN pip3 install --no-cache-dir wheel
RUN pip3 install --no-cache-dir paho-mqtt pillow
RUN pip3 install --no-cache-dir numpy==1.23.5
RUN pip3 install --no-cache-dir opencv-python-headless==4.5.5.64

# Command to run
CMD [ "/app/run.sh" ]