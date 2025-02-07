#!/usr/bin/with-contenv bashio
# ==============================================================================
# Initialize the person detector service
# ==============================================================================

# Log the startup
bashio::log.info "Initializing person detector service..."

# Get config values and export them as environment variables so our service can use them
export CAMERA_ENTITY=$(bashio::config 'camera_entity')
export CONFIDENCE_THRESHOLD=$(bashio::config 'confidence_threshold')
export SCAN_INTERVAL=$(bashio::config 'scan_interval')

# Log the configuration for debugging purposes
bashio::log.info "Configuration loaded:"
bashio::log.info "Camera Entity: ${CAMERA_ENTITY}"
bashio::log.info "Confidence Threshold: ${CONFIDENCE_THRESHOLD}"
bashio::log.info "Scan Interval: ${SCAN_INTERVAL}"

# Create necessary directories if they don't exist
mkdir -p /var/log/person_detector

# Note: We don't run the Python script here anymore since s6 will handle that