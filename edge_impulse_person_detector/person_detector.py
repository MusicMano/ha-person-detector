import os
import json
import time
import asyncio
import aiohttp
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("person_detector")

# Try to read configuration from options.json
def read_options():
    options_path = "/data/options.json"
    try:
        if os.path.exists(options_path):
            with open(options_path, 'r') as f:
                options = json.load(f)
                logger.info(f"Loaded configuration from {options_path}: {options}")
                return options
        else:
            logger.warning(f"No configuration file found at {options_path}")
            return {}
    except Exception as e:
        logger.error(f"Error reading options file: {str(e)}")
        return {}

# Log current directory and files to help debug
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Files in current directory: {os.listdir('.')}")
logger.info(f"Environment variables: {dict(os.environ)}")

# Read configuration from multiple possible sources
config = read_options()

# First try options.json, then environment variables, then defaults
CAMERA_ENTITY = config.get('camera_entity', os.environ.get('CAMERA_ENTITY', 'camera.front_door'))
CONFIDENCE_THRESHOLD = float(config.get('confidence_threshold', os.environ.get('CONFIDENCE_THRESHOLD', 0.7)))
SCAN_INTERVAL = int(config.get('scan_interval', os.environ.get('SCAN_INTERVAL', 1)))
EDGE_IMPULSE_API_KEY = config.get('edge_impulse_api_key', os.environ.get('EDGE_IMPULSE_API_KEY', ''))

# Log the configuration being used
logger.info(f"Using configuration: camera={CAMERA_ENTITY}, confidence={CONFIDENCE_THRESHOLD}, interval={SCAN_INTERVAL}")
            f"confidence_threshold={CONFIDENCE_THRESHOLD}, " +
            f"scan_interval={SCAN_INTERVAL}")

# Check all environment variables to debug
logger.info("All environment variables:")
for key, value in os.environ.items():
    if 'TOKEN' not in key.upper():  # Don't log tokens/secrets
        logger.info(f"  {key}={value}")

class PersonDetector:
    def __init__(self, camera_entity, confidence_threshold, scan_interval, ei_api_key=None):
        self.camera_entity = camera_entity
        self.confidence_threshold = confidence_threshold
        self.scan_interval = scan_interval
        self.ei_api_key = ei_api_key
        
        # Get supervisor token from environment
        self.supervisor_token = os.environ.get('SUPERVISOR_TOKEN')
        if not self.supervisor_token:
            logger.warning("SUPERVISOR_TOKEN not available - will not be able to access HA API")
            # Try alternate location
            self.supervisor_token = os.environ.get('HASSIO_TOKEN')
            if self.supervisor_token:
                logger.info("Found token as HASSIO_TOKEN instead of SUPERVISOR_TOKEN")
                
        # Keep track of last detection state
        self.last_state = None

    async def get_camera_image(self):
        """Get image from Home Assistant camera."""
        url = f"http://supervisor/core/api/camera_proxy/{self.camera_entity}"
        headers = {
            "Authorization": f"Bearer {self.supervisor_token}",
            "content-type": "application/json",
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        logger.info(f"Successfully captured image from {self.camera_entity}")
                        return await response.read()
                    else:
                        logger.error(f"Failed to get camera image: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error getting camera image: {str(e)}")
            return None

    async def publish_state(self, is_person_detected, confidence=0.0):
        """Publish state to Home Assistant via API."""
        # Only proceed if we have a supervisor token
        if not self.supervisor_token:
            logger.warning("Cannot publish state: No SUPERVISOR_TOKEN available")
            return
            
        # Update binary sensor
        url = "http://supervisor/core/api/states/binary_sensor.person_detector"
        headers = {
            "Authorization": f"Bearer {self.supervisor_token}",
            "content-type": "application/json",
        }
        
        payload = {
            "state": "on" if is_person_detected else "off",
            "attributes": {
                "device_class": "occupancy",
                "friendly_name": "Person Detector",
                "confidence": round(confidence * 100, 1)
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200 or response.status == 201:
                        logger.info(f"Successfully updated person_detector state to {is_person_detected}")
                    else:
                        logger.error(f"Failed to update binary sensor: {response.status}")
        except Exception as e:
            logger.error(f"Error updating binary sensor: {str(e)}")
            
        # Also update a sensor for the confidence value
        url = "http://supervisor/core/api/states/sensor.person_detector_confidence"
        confidence_payload = {
            "state": round(confidence * 100, 1),
            "attributes": {
                "unit_of_measurement": "%",
                "friendly_name": "Person Detector Confidence",
                "icon": "mdi:percent"
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=confidence_payload) as response:
                    if response.status == 200 or response.status == 201:
                        logger.info(f"Successfully updated confidence to {confidence*100:.1f}%")
                    else:
                        logger.error(f"Failed to update confidence sensor: {response.status}")
        except Exception as e:
            logger.error(f"Error updating confidence sensor: {str(e)}")

    async def simulate_detection(self, image_data):
        """Simulate person detection."""
        # Implement a simple simulation based on the image data
        # Here we're just using a hash of the first bytes for consistency
        if image_data is None:
            return False, 0.0
            
        hash_value = 0
        for i in range(min(20, len(image_data))):
            hash_value = (hash_value * 31 + image_data[i]) % 100
            
        # Simulate a person detection about 30% of the time
        person_detected = hash_value < 30
        confidence = 0.0
        
        if person_detected:
            confidence = 0.5 + (hash_value / 100.0) * 0.5  # 50-100% confidence
            
        return person_detected, confidence

    async def run_detection(self):
        """Main detection loop."""
        logger.info(f"Starting person detection with camera: {self.camera_entity}")
        logger.info(f"Confidence threshold: {self.confidence_threshold}")
        logger.info(f"Scan interval: {self.scan_interval} seconds")
        
        while True:
            try:
                # Get image from camera
                image_data = await self.get_camera_image()
                
                if image_data is not None:
                    # For now, use simulated detection
                    person_detected, confidence = await self.simulate_detection(image_data)
                    
                    # Only update state if it changed or on first run
                    if self.last_state is None or self.last_state != person_detected:
                        await self.publish_state(person_detected, confidence)
                        self.last_state = person_detected
                        
                        # Log detection
                        if person_detected:
                            logger.info(f"Person DETECTED with {confidence*100:.1f}% confidence")
                        else:
                            logger.info(f"No person detected")
                else:
                    logger.warning("Failed to get camera image, will retry")
            except Exception as e:
                logger.error(f"Error in detection loop: {str(e)}")
                
            # Wait before next detection
            await asyncio.sleep(self.scan_interval)

async def main():
    # Create and run detector
    detector = PersonDetector(
        CAMERA_ENTITY,
        CONFIDENCE_THRESHOLD,
        SCAN_INTERVAL,
        EDGE_IMPULSE_API_KEY
    )
    
    await detector.run_detection()

if __name__ == "__main__":
    logger.info("Person Detector starting up")
    logger.info(f"Environment: CAMERA_ENTITY={CAMERA_ENTITY}, CONFIDENCE={CONFIDENCE_THRESHOLD}, INTERVAL={SCAN_INTERVAL}")
    
    # Run the async main function
    asyncio.run(main())