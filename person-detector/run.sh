#!/usr/bin/with-contenv bashio
# ==============================================================================
# Start the person detector service
# ==============================================================================

# Get config values
declare camera

# Get the camera entity
camera=$(bashio::config 'camera_entity')
confidence=$(bashio::config 'confidence_threshold')
interval=$(bashio::config 'scan_interval')

cd /app

# Run person detector
python3 person_detector.py \
    --camera "${camera}" \
    --confidence "${confidence}" \
    --interval "${interval}"
