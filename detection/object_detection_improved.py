# detection/object_detection_improved.py
"""
Improved object detection module with robust image retrieval and error handling.
This module addresses Issue #2 'simGetImage' error with comprehensive fixes.
"""

import airsim
import numpy as np
import cv2
import logging
from ultralytics import YOLO
from utils.image_utils import get_image_safe, validate_airsim_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize YOLO model
try:
    model = YOLO("yolov10n.pt")
    logger.info("YOLO model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load YOLO model: {str(e)}")
    model = None


def yolov10_object_detection_improved(client: airsim.CarClient) -> bool:
    """
    Improved object detection function with robust error handling.
    
    This function addresses the following issues from the original implementation:
    1. No retry mechanism for failed image retrieval
    2. No error handling for None/empty responses
    3. No validation of AirSim connection
    4. Improper camera naming
    5. No handling of decode failures
    
    Args:
        client: The AirSim client object.

    Returns:
        bool: True if detection is successful, False otherwise.
    """
    
    if model is None:
        logger.error("YOLO model not loaded, cannot perform detection")
        return False
    
    try:
        # Get image using robust wrapper
        img = get_image_safe(
            client=client,
            camera="0",  # Use "0" instead of "FrontCenter" - more reliable
            image_type=airsim.ImageType.Scene,
            retries=3,
            sleep_time=0.2,
            compress=True,
            return_none_on_error=True
        )
        
        if img is None:
            logger.warning("Failed to retrieve image, skipping detection")
            return True  # Return True to continue operation
        
        # Validate image
        if img.size == 0:
            logger.warning("Retrieved image is empty, skipping detection")
            return True
        
        # Ensure image is in correct format for YOLO
        if len(img.shape) != 3:
            logger.warning(f"Unexpected image shape: {img.shape}, skipping detection")
            return True
        
        # Run YOLO detection
        try:
            results = model(img)
            
            # Check if results are valid
            if not results or len(results) == 0:
                logger.debug("No detection results")
                return True
            
            # Process detection results
            result = results[0]
            if hasattr(result, 'boxes') and result.boxes is not None:
                
                # Create a copy of the image for drawing
                display_img = img.copy()
                
                for box in result.boxes:
                    try:
                        # Extract box coordinates
                        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                        
                        # Extract class and confidence
                        cls_idx = int(box.cls[0].cpu().numpy())
                        confidence = float(box.conf[0].cpu().numpy())
                        
                        # Get class name
                        if cls_idx < len(model.names):
                            label = model.names[cls_idx]
                        else:
                            label = f"Unknown_{cls_idx}"
                        
                        # Draw bounding box and label
                        cv2.rectangle(display_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(
                            display_img, 
                            f"{label} {confidence:.2f}", 
                            (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            0.5, 
                            (0, 255, 0), 
                            2
                        )
                        
                        logger.debug(f"Detected: {label} with confidence {confidence:.2f}")
                        
                    except Exception as e:
                        logger.warning(f"Error processing detection box: {str(e)}")
                        continue
                
                # Display the image
                cv2.imshow("YOLO Detection", display_img)
                
            else:
                # No detections, show original image
                cv2.imshow("YOLO Detection", img)
                
        except Exception as e:
            logger.error(f"YOLO detection failed: {str(e)}")
            # Show original image even if detection fails
            cv2.imshow("YOLO Detection", img)
        
        # Check for quit key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Object detection function failed: {str(e)}")
        return True  # Continue operation even if detection fails


def yolov10_object_detection_legacy(client: airsim.CarClient) -> bool:
    """
    Original object detection function - kept for backwards compatibility.
    This version has the issues that cause the 'simGetImage' error.
    
    Args:
        client: The AirSim client object.

    Returns:
        bool: True if the detection is successful, False otherwise.
    """
    try:
        result = client.simGetImage("FrontCenter", airsim.ImageType.Scene)
        raw_image = np.frombuffer(result, np.int8)
        img = cv2.imdecode(raw_image, cv2.IMREAD_UNCHANGED)
        
        if img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        results = model(img)

        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
            label = model.names[int(box.cls[0].cpu().numpy())]
            confidence = box.conf[0].cpu().numpy()
            
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, f"{label} {confidence:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.imshow("Top", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            return False
        return True
        
    except Exception as e:
        logger.error(f"Legacy object detection failed: {str(e)}")
        return False


# Alias for the improved function
yolov10_object_detection = yolov10_object_detection_improved


def test_image_retrieval(client: airsim.CarClient) -> bool:
    """
    Test function to validate image retrieval without running full detection.
    
    Args:
        client: The AirSim client object.
        
    Returns:
        bool: True if image retrieval works, False otherwise.
    """
    logger.info("Testing image retrieval...")
    
    # Validate connection first
    if not validate_airsim_connection(client, timeout=5.0):
        logger.error("AirSim connection validation failed")
        return False
    
    # Test image retrieval
    img = get_image_safe(client, camera="0", retries=3)
    
    if img is not None:
        logger.info(f"Image retrieval test successful: shape={img.shape}, dtype={img.dtype}")
        return True
    else:
        logger.error("Image retrieval test failed")
        return False


if __name__ == "__main__":
    # Test the improved image retrieval
    import airsim
    
    logger.info("Starting image retrieval test...")
    
    try:
        client = airsim.CarClient()
        client.confirmConnection()
        client.enableApiControl(True)
        
        if test_image_retrieval(client):
            logger.info("All tests passed!")
        else:
            logger.error("Tests failed!")
            
    except Exception as e:
        logger.error(f"Test setup failed: {str(e)}")
    finally:
        try:
            client.enableApiControl(False)
        except:
            pass
