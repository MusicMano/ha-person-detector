#!/usr/bin/env python3
import os
import time
import json
import base64
import logging
import subprocess
import paho.mqtt.client as mqtt

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class PersonDetector:
    def __init__(self, config):
        """Initialize the person detector with configuration settings."""
        self.config = config
        self.mqtt_client = None
        self.detection_active = True
        self.upload_active = False
        self.model_path = os.path.join(os.path.dirname(__file__), 'model', 'model.eim')
        
        # Connect to MQTT
        self.setup_mqtt()
    
    # MQTT setup and other functions remain the same...
    
    def process_image_for_detection(self, image_data):
        """Process image data to detect people using Edge Impulse CLI."""
        try:
            # Save the image to a file
            with open('/tmp/image.jpg', 'wb') as f:
                f.write(image_data)
                
            logger.info("Saved image to temporary file")
            
            # Run Edge Impulse CLI on the image
            cmd = ["edge-impulse-linux-runner", "--model", self.model_path, "--image", "/tmp/image.jpg"]
            logger.info(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            output = result.stdout
            logger.info(f"Model output: {output}")
            
            # Very simple parsing of output
            person_detected = "person" in output.lower()
            confidence = 0.5  # Default value
            
            # Publish results
            self.publish_detection_result(person_detected, confidence)
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")