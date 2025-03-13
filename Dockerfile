ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install essential packages only
RUN apk add --no-cache \
    python3 \
    nodejs \
    npm \
    git

# Install Edge Impulse CLI
RUN npm install -g edge-impulse-linux

# Copy files
COPY . /app
WORKDIR /app

# Make run script executable
RUN chmod a+x /app/run.sh

# Set up a custom Python environment instead of fighting with system packages
RUN python3 -m ensurepip
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir paho-mqtt

# Command to run
CMD [ "/app/run.sh" ]