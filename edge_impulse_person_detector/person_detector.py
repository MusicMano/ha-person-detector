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

# Log the final configuration that will be used
logger.info(f"Final configuration: camera_entity={CAMERA_ENTITY}, " +
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
    
    # Log whether we have an Edge Impulse API key
    if self.ei_api_key:
        logger.info("Edge Impulse API key provided, will use Edge Impulse for detection")
    else:
        logger.warning("No Edge Impulse API key provided, detection may not work")
        
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
            
    async def preprocess_image(self, image_data):
    """Preprocess the image before sending to Edge Impulse."""
    # This is a simple implementation that passes the image unchanged
    # You may need to resize, convert format, etc. depending on your Edge Impulse model
    return image_data        
            
    async def detect_with_edge_impulse(self, image_data):
    """Detect people using Edge Impulse API."""
    if image_data is None:
        return False, 0.0
        
    if not self.ei_api_key:
        logger.warning("No Edge Impulse API key provided, cannot perform detection")
        return False, 0.0
    
    try:
        # Preprocess the image
        processed_image = await self.preprocess_image(image_data)
        
        url = "https://api.edgeimpulse.com/v1/classification/classify"
        headers = {
            "x-api-key": self.ei_api_key,
            "Content-Type": "application/octet-stream"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=processed_image) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Edge Impulse response: {result}")
                    
                    # Process classification results
                    if "classification" in result:
                        # Look for a "person" class in the results
                        person_confidence = 0.0
                        for item in result["classification"]["results"]:
                            if "person" in item["label"].lower():
                                person_confidence = item["value"]
                                break
                        
                        # Determine if a person is detected based on confidence threshold
                        person_detected = person_confidence >= self.confidence_threshold
                        
                        return person_detected, person_confidence
                    else:
                        logger.warning("No classification results in Edge Impulse response")
                else:
                    logger.error(f"Edge Impulse API error: {response.status}")
                    logger.error(await response.text())
                    
        return False, 0.0
    except Exception as e:
        logger.error(f"Error in Edge Impulse detection: {str(e)}")
        return False, 0.0
        
    async def detect_with_fallback(self, image_data):
    """Try to detect with Edge Impulse, fall back to simulation if it fails."""
    if not self.ei_api_key:
        # No API key, use simulation
        logger.info("No Edge Impulse API key, using simulation mode")
        return await self.simulate_detection(image_data)
    
    try:
        # Try Edge Impulse first
        person_detected, confidence = await self.detect_with_edge_impulse(image_data)
        return person_detected, confidence
    except Exception as e:
        logger.error(f"Edge Impulse detection failed: {str(e)}, falling back to simulation")
        # Fall back to simulation
        return await self.simulate_detection(image_data)    
    
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
                # Use detection with fallback
                person_detected, confidence = await self.detect_with_fallback(image_data)
                
                # Only update state if it changed or on first run
                if self.last_state is None or self.last_state != person_detected:
                    await self.publish_state(person_detected, confidence)
                    self.last_state = person_detected
                    
                    # Log detection
                    if person_detected:
                        logger.info(f"Person DETECTED with {confidence*100:.1f}% confidence")
                    else:
                        logger.info(f"No person detected (confidence: {confidence*100:.1f}%)")
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