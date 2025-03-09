#!/bin/bash

# Print working directory and list files to debug
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la

# Check if configuration file exists
CONFIG_PATH="/data/options.json"
if [ -f "$CONFIG_PATH" ]; then
  echo "Found configuration file at $CONFIG_PATH"
  cat "$CONFIG_PATH"
else
  echo "No configuration file at $CONFIG_PATH"
fi

# Directly run the Python script
python3 /app/person_detector.py