ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.15
FROM ${BUILD_FROM}

WORKDIR /app

RUN apk add --no-cache \
    python3=3.9.18-r0 \
    py3-pip=20.3.4-r1

RUN pip3 install --no-cache-dir \
    aiohttp \
    numpy \
    opencv-python-headless

COPY . /app/
RUN chmod a+x /app/run.sh

CMD [ "/app/run.sh" ]