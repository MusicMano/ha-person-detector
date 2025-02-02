ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install required packages
RUN \
    apk add --no-cache \
        python3 \
        py3-pip \
        nodejs \
        npm

# Install Python dependencies
RUN pip3 install \
    numpy \
    opencv-python-headless \
    aiohttp

# Copy your files
COPY run.sh /
COPY person_detector.py /
COPY edge-impulse-standalone.* /

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]