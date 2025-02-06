ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.18
FROM ${BUILD_FROM}

WORKDIR /app

# Install bashio
RUN apk add --no-cache \
    bash \
    jq \
    curl

# Install Python and deps
RUN apk add --no-cache \
    python3 \
    py3-pip && \
    pip3 install --no-cache-dir \
    aiohttp \
    numpy \
    opencv-python-headless

# Install bashio
RUN curl -J -L -o /tmp/bashio.tar.gz \
    "https://github.com/hassio-addons/bashio/archive/v0.14.3.tar.gz" && \
    mkdir /tmp/bashio && \
    tar zxvf /tmp/bashio.tar.gz -C /tmp/bashio --strip 1 && \
    mv /tmp/bashio/lib /usr/lib/bashio && \
    ln -s /usr/lib/bashio/bashio /usr/bin/bashio

COPY . /app/
RUN chmod a+x /app/run.sh

CMD [ "/app/run.sh" ]