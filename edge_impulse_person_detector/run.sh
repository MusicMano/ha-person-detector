#!/bin/bash
# Load config
CONFIG_PATH=/data/options.json

# Parse config
CAMERA_ENTITY="$(jq --raw-output '.camera_entity // empty' $CONFIG_PATH)"
CONFIDENCE_THRESHOLD="$(jq --raw-output '.confidence_threshold // empty' $CONFIG_PATH)"
SCAN_INTERVAL="$(jq --raw-output '.scan_interval // empty' $CONFIG_PATH)"
EDGE_IMPULSE_API_KEY="$(jq --raw-output '.edge_impulse_api_key // empty' $CONFIG_PATH)"

# Export as environment variables
export CAMERA_ENTITY=$CAMERA_ENTITY
export CONFIDENCE_THRESHOLD=$CONFIDENCE_THRESHOLD
export SCAN_INTERVAL=$SCAN_INTERVAL
export EDGE_IMPULSE_API_KEY=$EDGE_IMPULSE_API_KEY

# Run the Python script
python3 /person_detector.py