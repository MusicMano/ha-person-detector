#!/usr/bin/with-contenv bashio

# Print Home Assistant add-on info
bashio::log.info "Starting Person Detector add-on with Edge Impulse model..."

# Verify Edge Impulse Linux tools are installed
if ! command -v edge-impulse-linux-runner &> /dev/null; then
    bashio::log.warning "Edge Impulse Linux Runner not found, installing..."
    npm install edge-impulse-linux -g --unsafe-perm
fi

# Run the Python script
python3 /app/person_detector.py