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
                # Use Edge Impulse for detection
                person_detected, confidence = await self.detect_with_edge_impulse(image_data)
                
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