#!/usr/bin/with-contenv bashio

# Get config values
CAMERA_ENTITY=$(bashio::config 'camera_entity')
CONFIDENCE_THRESHOLD=$(bashio::config 'confidence_threshold')
SCAN_INTERVAL=$(bashio::config 'scan_interval')

# Run the person detector
python3 /person_detector.py \
    --camera "${CAMERA_ENTITY}" \
    --confidence "${CONFIDENCE_THRESHOLD}" \
    --interval "${SCAN_INTERVAL}"