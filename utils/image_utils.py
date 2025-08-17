# utils/image_utils.py
import airsim
import numpy as np
import cv2
import time
import logging
from typing import Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageRetrievalError(Exception):
    """Custom exception for image retrieval errors"""
    pass

def get_image(
    client: airsim.CarClient, 
    camera: str = "0", 
    image_type: airsim.ImageType = airsim.ImageType.Scene,
    retries: int = 3, 
    sleep_time: float = 0.2, 
    compress: bool = True
) -> Optional[np.ndarray]:
    """
    Robust wrapper for AirSim simGetImage with retry mechanism and error handling.
    
    Args:
        client: AirSim CarClient object
        camera: Camera name/ID (default: "0" which is more reliable than "FrontCenter")
        image_type: Type of image to retrieve (Scene, DepthVis, etc.)
        retries: Number of retry attempts (default: 3)
        sleep_time: Sleep time between retries in seconds (default: 0.2)
        compress: Whether to use compression (default: True)
    
    Returns:
        np.ndarray: Decoded image as numpy array, or None if all attempts failed
    
    Raises:
        ImageRetrievalError: If all retry attempts fail
    """
    
    # Validate camera name - common AirSim camera names
    valid_cameras = ["0", "1", "2", "3", "FrontCenter", "FrontLeft", "FrontRight", "BackCenter"]
    if camera not in valid_cameras:
        logger.warning(f"Camera '{camera}' may not be valid. Valid cameras: {valid_cameras}")
    
    last_exception = None
    
    for attempt in range(retries):
        try:
            logger.debug(f"Attempt {attempt + 1}/{retries} to get image from camera '{camera}'")
            
            # Get raw image data
            if compress:
                # Use compressed format - more reliable
                response = client.simGetImages([
                    airsim.ImageRequest(camera, image_type, False, True)
                ])
                
                if not response or len(response) == 0:
                    raise ImageRetrievalError("Empty response from simGetImages")
                
                img_data = response[0]
                if img_data.image_data_uint8 is None or len(img_data.image_data_uint8) == 0:
                    raise ImageRetrievalError("Empty image data in response")
                
                # Convert to numpy array and decode
                nparr = np.frombuffer(img_data.image_data_uint8, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
            else:
                # Use uncompressed format - fallback method
                result = client.simGetImage(camera, image_type)
                
                if result is None or len(result) == 0:
                    raise ImageRetrievalError("Empty result from simGetImage")
                
                # Convert byte array to numpy array
                raw_image = np.frombuffer(result, np.uint8)
                img = cv2.imdecode(raw_image, cv2.IMREAD_UNCHANGED)
            
            # Validate decoded image
            if img is None:
                raise ImageRetrievalError("Failed to decode image data")
            
            if img.size == 0:
                raise ImageRetrievalError("Decoded image is empty")
            
            # Convert BGRA to BGR if necessary
            if len(img.shape) == 3 and img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            logger.debug(f"Successfully retrieved image: shape={img.shape}, dtype={img.dtype}")
            return img
            
        except Exception as e:
            last_exception = e
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < retries - 1:  # Don't sleep on last attempt
                time.sleep(sleep_time)
            
            # Try different approach on next attempt
            if attempt == 0 and compress:
                compress = False  # Try uncompressed on second attempt
                logger.info("Switching to uncompressed format for next attempt")
    
    # All attempts failed
    error_msg = f"Failed to retrieve image after {retries} attempts. Last error: {str(last_exception)}"
    logger.error(error_msg)
    raise ImageRetrievalError(error_msg)


def get_image_safe(
    client: airsim.CarClient, 
    camera: str = "0", 
    image_type: airsim.ImageType = airsim.ImageType.Scene,
    retries: int = 3, 
    sleep_time: float = 0.2, 
    compress: bool = True,
    return_none_on_error: bool = True
) -> Optional[np.ndarray]:
    """
    Safe version of get_image that returns None instead of raising exceptions.
    
    Args:
        client: AirSim CarClient object
        camera: Camera name/ID
        image_type: Type of image to retrieve
        retries: Number of retry attempts
        sleep_time: Sleep time between retries
        compress: Whether to use compression
        return_none_on_error: If True, returns None on error; if False, raises exception
    
    Returns:
        np.ndarray or None: Decoded image or None if failed and return_none_on_error=True
    """
    try:
        return get_image(client, camera, image_type, retries, sleep_time, compress)
    except ImageRetrievalError as e:
        if return_none_on_error:
            logger.error(f"Image retrieval failed, returning None: {str(e)}")
            return None
        else:
            raise


def validate_airsim_connection(client: airsim.CarClient, timeout: float = 5.0) -> bool:
    """
    Validate that AirSim connection is ready for image retrieval.
    
    Args:
        client: AirSim CarClient object
        timeout: Maximum time to wait for connection validation
    
    Returns:
        bool: True if connection is ready, False otherwise
    """
    try:
        start_time = time.time()
        
        # Try to get a simple test image to validate connection
        while time.time() - start_time < timeout:
            try:
                # Test with minimal parameters
                test_response = client.simGetImages([
                    airsim.ImageRequest("0", airsim.ImageType.Scene, False, True)
                ])
                
                if test_response and len(test_response) > 0:
                    logger.info("AirSim connection validated successfully")
                    return True
                    
            except Exception as e:
                logger.debug(f"Connection validation attempt failed: {str(e)}")
                time.sleep(0.1)
        
        logger.error("AirSim connection validation timed out")
        return False
        
    except Exception as e:
        logger.error(f"AirSim connection validation failed: {str(e)}")
        return False
