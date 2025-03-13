#!/usr/bin/env python3
import os
import sys
import time
import json
import base64
import logging
import subprocess
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
import paho.mqtt.client as mqtt
import tempfile

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
        
        logger.info(f"Using Edge Impulse model at: {self.model_path}")
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at {self.model_path}")
            
        # Connect to MQTT
        self.setup_mqtt()
    
    def setup_mqtt(self):
        """Set up MQTT client and connection."""
        try:
            client_id = f"ha-person-detector-{int(time.time())}"
            self.mqtt_client = mqtt.Client(client_id)
            
            # Set credentials if provided
            if self.config.get('mqtt_username') and self.config.get('mqtt_password'):
                self.mqtt_client.username_pw_set(
                    self.config.get('mqtt_username'),
                    self.config.get('mqtt_password')
                )
            
            # Set callbacks
            self.mqtt_client.on_connect = self.on_connect
            self.mqtt_client.on_message = self.on_message
            self.mqtt_client.on_disconnect = self.on_disconnect
            
            # Connect to broker
            broker = self.config.get('mqtt_broker', 'localhost')
            port = int(self.config.get('mqtt_port', 1883))
            logger.info(f"Connecting to MQTT broker at {broker}:{port}")
            
            self.mqtt_client.connect(broker, port, 60)
            logger.info("MQTT connection initiated")
        except Exception as e:
            logger.error(f"Failed to set up MQTT: {e}")
            raise
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the broker."""
        connection_result = {
            0: "Connection successful",
            1: "Incorrect protocol version",
            2: "Invalid client identifier",
            3: "Server unavailable",
            4: "Bad username or password",
            5: "Not authorized"
        }
        result = connection_result.get(rc, f"Unknown error code: {rc}")
        
        if rc == 0:
            logger.info(result)
            # Subscribe to camera image topic
            client.subscribe("esp32/cam/image")
            # Subscribe to control topics
            client.subscribe("basement-ai-cam/switch/person_detection/state")
            client.subscribe("basement-ai-cam/switch/training_data_upload/state")
            logger.info("Subscribed to ESP32 camera and control topics")
        else:
            logger.error(f"Failed to connect to MQTT: {result}")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the broker."""
        if rc != 0:
            logger.warning(f"Unexpected MQTT disconnection: {rc}. Attempting to reconnect...")
            time.sleep(5)  # Wait a bit before reconnecting
            try:
                client.reconnect()
            except Exception as e:
                logger.error(f"Failed to reconnect to MQTT: {e}")
    
    def on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages."""
        try:
            topic = msg.topic
            
            # Handle control messages
            if topic == "basement-ai-cam/switch/person_detection/state":
                state = msg.payload.decode("utf-8")
                self.detection_active = (state.lower() == "on")
                logger.info(f"Person detection turned {'ON' if self.detection_active else 'OFF'}")
                return
                
            if topic == "basement-ai-cam/switch/training_data_upload/state":
                state = msg.payload.decode("utf-8")
                self.upload_active = (state.lower() == "on")
                logger.info(f"Training data upload turned {'ON' if self.upload_active else 'OFF'}")
                return
            
            # Handle image data for detection
            if topic == "esp32/cam/image" and self.detection_active:
                logger.info("Received image for processing")
                image_data = base64.b64decode(msg.payload)
                
                # Process the image for person detection
                self.process_image_for_detection(image_data)
                
            # Handle image data for training upload
            if topic == "esp32/cam/image" and self.upload_active:
                logger.info("Received image for training data upload")
                # This would be implemented to upload to Edge Impulse for training
                # For now, just log
                logger.info("Training data upload functionality not yet implemented")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def process_image_for_detection(self, image_data):
        """Process image data to detect people using Edge Impulse model."""
        try:
            # Save the image to a temporary file
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_file_path = temp_file.name
                temp_file.write(image_data)
            
            logger.info(f"Saved image to temporary file: {temp_file_path}")
            
            # Run the Edge Impulse model on the image using the Linux Runner
            cmd = [
                "edge-impulse-linux-runner", 
                "--model", self.model_path,
                "--image", temp_file_path,
                "--silent"  # Reduce console output
            ]
            
            logger.info(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Process the output to extract detection results
            if result.returncode != 0:
                logger.error(f"Model inference failed: {result.stderr}")
                return
                
            output = result.stdout
            logger.info(f"Model output: {output}")
            
            # Parse the output to find person detection results
            # This will need to be adapted based on your specific model output format
            person_detected = "person" in output.lower()
            
            # Extract confidence value - this pattern may need adjustment
            confidence = 0.0
            import re
            confidence_match = re.search(r"person.*?(\d+\.\d+)%", output, re.IGNORECASE)
            if confidence_match:
                confidence = float(confidence_match.group(1)) / 100.0
            else:
                # Try alternative format
                confidence_match = re.search(r"confidence.*?(\d+\.\d+)", output, re.IGNORECASE)
                if confidence_match:
                    confidence = float(confidence_match.group(1))
            
            logger.info(f"Detection result: {'Person detected' if person_detected else 'No person'} "
                        f"with {confidence*100:.1f}% confidence")
            
            # Publish results back to Home Assistant
            self.publish_detection_result(person_detected, confidence)
            
            # Clean up
            os.unlink(temp_file_path)
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def publish_detection_result(self, person_detected, confidence):
        """Publish detection results to MQTT."""
        try:
            # Send binary sensor state (ON/OFF for person detection)
            person_topic = self.config.get('person_detection_topic', 
                                          'homeassistant/binary_sensor/person_detection/state')
            self.mqtt_client.publish(
                person_topic,
                "ON" if person_detected else "OFF"
            )
            
            # Send confidence value as percentage
            confidence_topic = self.config.get('confidence_topic',
                                              'homeassistant/sensor/detection_confidence/state')
            self.mqtt_client.publish(
                confidence_topic,
                f"{confidence*100:.1f}"
            )
            
            logger.info(f"Published detection results to MQTT")
        except Exception as e:
            logger.error(f"Error publishing detection results: {e}")
    
    def run(self):
        """Run the main loop of the detector."""
        try:
            # Verify Edge Impulse Linux Runner is installed
            try:
                subprocess.run(["edge-impulse-linux-runner", "--version"], 
                               check=True, capture_output=True)
                logger.info("Edge Impulse Linux Runner is installed")
            except (subprocess.SubprocessError, FileNotFoundError):
                logger.error("Edge Impulse Linux Runner not found. Make sure it's installed.")
                return
            
            logger.info("Starting MQTT loop")
            self.mqtt_client.loop_forever()
        except KeyboardInterrupt:
            logger.info("Stopping person detector due to keyboard interrupt")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            if self.mqtt_client:
                self.mqtt_client.disconnect()
            logger.info("Person detector stopped")

def main():
    """Main function to start the person detector."""
    try:
        # Load configuration from file
        config_path = '/data/options.json'
        logger.info(f"Loading configuration from {config_path}")
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            # Use default configuration if file doesn't exist
            logger.warning(f"Configuration file not found, using defaults")
            config = {
                'mqtt_broker': 'localhost',
                'mqtt_port': 1883,
                'mqtt_username': '',
                'mqtt_password': '',
                'detection_threshold': 0.5,
                'person_detection_topic': 'homeassistant/binary_sensor/person_detection/state',
                'confidence_topic': 'homeassistant/sensor/detection_confidence/state'
            }
        
        # Create and run the detector
        detector = PersonDetector(config)
        detector.run()
    except Exception as e:
        logger.error(f"Failed to start person detector: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    main()