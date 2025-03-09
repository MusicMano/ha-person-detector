#!/usr/bin/env python3
import asyncio
import aiohttp
import cv2
import numpy as np
import json
import argparse
import os
from pathlib import Path
import requests  # For Edge Impulse API calls

# Get configuration from environment variables with defaults
CAMERA_ENTITY = os.environ.get('CAMERA_ENTITY', 'camera.front_door')
CONFIDENCE_THRESHOLD = float(os.environ.get('CONFIDENCE_THRESHOLD', '0.7'))
SCAN_INTERVAL = int(os.environ.get('SCAN_INTERVAL', '1'))
EDGE_IMPULSE_API_KEY = os.environ.get('EDGE_IMPULSE_API_KEY', '')

class PersonDetector:
    def __init__(self, camera_entity, confidence_threshold, scan_interval, ei_api_key=None):
        self.camera_entity = camera_entity
        self.confidence_threshold = confidence_threshold
        self.scan_interval = scan_interval
        self.supervisor_token = os.environ.get('SUPERVISOR_TOKEN')
        self.ei_api_key = ei_api_key or os.environ.get('EDGE_IMPULSE_API_KEY')
        
        # Keep track of state to avoid redundant updates
        self.last_state = None
        
        # Create output directory for debug images
        self.debug_dir = Path("/config/www/person_detector")
        self.debug_dir.mkdir(exist_ok=True, parents=True)

    async def get_camera_image(self):
        """Get image from Home Assistant camera."""
        url = f"http://supervisor/core/api/camera_proxy/{self.camera_entity}"
        headers = {
            "Authorization": f"Bearer {self.supervisor_token}",
            "content-type": "application/json",
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    image_bytes = await response.read()
                    nparr = np.frombuffer(image_bytes, np.uint8)
                    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                else:
                    print(f"Failed to get camera image: {response.status}")
                    return None

    def prepare_image(self, image):
        """Prepare image for Edge Impulse model."""
        # Save original image for debugging
        timestamp = int(asyncio.get_event_loop().time())
        cv2.imwrite(str(self.debug_dir / f"original_{timestamp}.jpg"), image)
        
        # Resize to the dimensions expected by your model
        resized = cv2.resize(image, (96, 96))  # Update size to match your model
        
        if len(resized.shape) == 2:
            resized = cv2.cvtColor(resized, cv2.COLOR_GRAY2RGB)
            
        # Save processed image for debugging
        cv2.imwrite(str(self.debug_dir / f"processed_{timestamp}.jpg"), resized)
        
        return resized

    async def run_edge_impulse_inference(self, image):
        """Run inference using Edge Impulse API."""
        if not self.ei_api_key:
            print("Edge Impulse API key not provided")
            return False, 0.0
            
        # Convert image to bytes
        _, img_encoded = cv2.imencode('.jpg', image)
        img_bytes = img_encoded.tobytes()
        
        # Use Edge Impulse API for inference
        url = "https://api.edgeimpulse.com/v1/classification/my-project/predict"  # Replace with your project
        headers = {
            "x-api-key": self.ei_api_key,
            "Content-Type": "application/octet-stream"
        }
        
        try:
            # Use aiohttp for async HTTP request
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=img_bytes) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Log the full response for debugging
                        print(f"Edge Impulse response: {result}")
                        
                        # Process based on whether it's object detection or classification
                        if 'bounding_boxes' in result:
                            # Object detection model
                            person_detected = False
                            max_confidence = 0.0
                            
                            for box in result['bounding_boxes']:
                                if box['label'] == 'person' and box['value'] > max_confidence:
                                    max_confidence = box['value']
                                    if max_confidence >= self.confidence_threshold:
                                        person_detected = True
                                        
                            return person_detected, max_confidence
                        else:
                            # Classification model
                            for prediction in result['predictions']:
                                if prediction['label'] == 'person':
                                    confidence = prediction['value']
                                    person_detected = confidence >= self.confidence_threshold
                                    return person_detected, confidence
                            
                            return False, 0.0
                    else:
                        print(f"Edge Impulse API error: {response.status}")
                        return False, 0.0
        except Exception as e:
            print(f"Error calling Edge Impulse API: {e}")
            return False, 0.0

    async def run_detection(self):
        """Main detection loop."""
        print(f"Starting detection with camera: {self.camera_entity}")
        
        while True:
            try:
                image = await self.get_camera_image()
                
                if image is not None:
                    # Prepare image for detection
                    processed_image = self.prepare_image(image)
                    
                    # Run inference using Edge Impulse
                    person_detected, confidence = await self.run_edge_impulse_inference(processed_image)
                    
                    # Publish results to Home Assistant if state changed or significant confidence change
                    if self.last_state is None or self.last_state != person_detected:
                        await self.publish_state(person_detected, confidence)
                        self.last_state = person_detected
                        
                        # Log detection event
                        event = "DETECTED" if person_detected else "NO DETECTION"
                        print(f"{event}: Confidence = {confidence:.2f}")
                else:
                    print("Failed to get camera image")
                    
            except Exception as e:
                print(f"Error in detection loop: {str(e)}")
                
            await asyncio.sleep(self.scan_interval)

    async def publish_state(self, is_person_detected, confidence):
        """Publish state to Home Assistant via API."""
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
        
        async with aiohttp.ClientSession() as session:
            await session.post(url, headers=headers, json=payload)
            
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
        
        async with aiohttp.ClientSession() as session:
            await session.post(url, headers=headers, json=confidence_payload)

aasync def main():
    print(f"Starting with camera={CAMERA_ENTITY}, confidence={CONFIDENCE_THRESHOLD}, interval={SCAN_INTERVAL}")
    
    detector = PersonDetector(
        CAMERA_ENTITY, 
        CONFIDENCE_THRESHOLD, 
        SCAN_INTERVAL,
        EDGE_IMPULSE_API_KEY
    )
    
    await detector.run_detection()

if __name__ == "__main__":
    asyncio.run(main())