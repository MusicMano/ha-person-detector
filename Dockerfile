# Start with the official Home Assistant base image
FROM ghcr.io/home-assistant/amd64-base:3.15

# Install required packages using Alpine's package manager
RUN \
    apk add --no-cache \
        python3 \
        py3-pip \
        mesa-gl \
        glib \
        curl \
        xz \
    && pip3 install --no-cache-dir wheel

# Set s6-overlay version
ENV S6_OVERLAY_VERSION=3.1.5.0

# Install s6-overlay
RUN curl -L -s https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz | tar -C / -Jxf - \
    && curl -L -s https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz | tar -C / -Jxf -

# Copy your application files
WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Make scripts executable
RUN chmod a+x /app/run.sh

# Copy s6-overlay service definitions
COPY services.d /etc/services.d/
RUN chmod a+x /etc/services.d/person_detector/run \
    && chmod a+x /etc/services.d/person_detector/finish

# Set the entrypoint
ENTRYPOINT ["/init"]