ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install system dependencies using apk (Alpine's package manager)
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-numpy \
    py3-opencv \
    py3-pillow \
    build-base \
    python3-dev \
    npm \
    nodejs

# Install Edge Impulse Linux CLI tools
RUN npm install edge-impulse-linux -g

# Copy files
COPY . /app
WORKDIR /app

# Make run script executable
RUN chmod a+x /app/run.sh

# Install Python requirements
RUN pip3 install --no-cache-dir -r requirements.txt

# Command to run
CMD [ "/app/run.sh" ]