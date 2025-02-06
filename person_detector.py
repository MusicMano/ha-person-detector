#!/usr/bin/env python3
import asyncio
import aiohttp
import cv2
import numpy as np
import json
import argparse
import os
from pathlib import Path

class PersonDetector:
    def __init__(self, camera_entity, confidence_threshold, scan_interval):
        self.camera_entity = camera_entity
        self.confidence_threshold = confidence_threshold
        self.scan_interval = scan_interval
        self.supervisor_token = os.environ.get('SUPERVISOR_TOKEN')
        
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
                return None

    def prepare_image(self, image):
        """Prepare image for Edge Impulse model."""
        resized = cv2.resize(image, (640, 480))
        if len(resized.shape) == 2:
            resized = cv2.cvtColor(resized, cv2.COLOR_GRAY2RGB)
        normalized = resized.astype(np.float32) / 255.0
        return normalized.flatten().tolist()

    async def run_detection(self):
        """Main detection loop."""
        print(f"Starting detection with camera: {self.camera_entity}")
        while True:
            try:
                image = await self.get_camera_image()
                if image is not None:
                    features = self.prepare_image(image)
                    # Run inference using Edge Impulse
                    # TODO: Add Edge Impulse inference code here
                    person_detected = False  # Placeholder until we add inference
                    
                    # Publish results to Home Assistant
                    await self.publish_state(person_detected)
                    
            except Exception as e:
                print(f"Error in detection loop: {str(e)}")
                
            await asyncio.sleep(self.scan_interval)

    async def publish_state(self, is_person_detected):
        """Publish state to Home Assistant via MQTT."""
        url = "http://supervisor/core/api/states/binary_sensor.person_detector"
        headers = {
            "Authorization": f"Bearer {self.supervisor_token}",
            "content-type": "application/json",
        }
        payload = {
            "state": "on" if is_person_detected else "off",
            "attributes": {
                "device_class": "occupancy",
                "friendly_name": "Person Detector"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            await session.post(url, headers=headers, json=payload)

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", required=True)
    parser.add_argument("--confidence", type=float, default=0.7)
    parser.add_argument("--interval", type=int, default=1)
    args = parser.parse_args()

    print(f"Starting with camera={args.camera}, confidence={args.confidence}, interval={args.interval}")
    detector = PersonDetector(args.camera, args.confidence, args.interval)
    await detector.run_detection()

if __name__ == "__main__":
    asyncio.run(main())