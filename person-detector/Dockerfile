ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install required packages
RUN \
    apk add --no-cache \
        python3 \
        py3-pip \
        nodejs \
        npm

# Install Python packages
RUN pip3 install --no-cache-dir \
    numpy \
    opencv-python-headless \
    aiohttp \
    pillow

# Set up work directory
WORKDIR /usr/src/app

# Copy files
COPY person_detector.py /usr/src/app/
COPY edge-impulse-standalone.* /usr/src/app/

# Copy rootfs
COPY rootfs /

ENTRYPOINT []
CMD [ "/usr/bin/with-contenv", "/usr/src/app/person_detector.py" ]