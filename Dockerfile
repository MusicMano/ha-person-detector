ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.15
FROM ${BUILD_FROM}

WORKDIR /app
COPY . /app/
RUN chmod a+x /app/run.sh

CMD [ "/app/run.sh" ]