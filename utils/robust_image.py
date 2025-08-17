# utils/robust_image.py
"""
Robust image retrieval wrapper for AirSim - Fixes Issue #2 'simGetImage' error.

This module provides a robust wrapper around AirSim's image retrieval APIs
with comprehensive error handling, retry mechanisms, and fallback strategies.
"""

import airsim
import numpy as np
import cv2
import time
import logging
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

class ImageRetrievalError(Exception):
    """Custom exception for image retrieval failures."""
    pass


def get_image(client: airsim.CarClient, 
              camera: str = "0", 
              image_type: airsim.ImageType = airsim.ImageType.Scene,
              retries: int = 3, 
              sleep: float = 0.2, 
              compress: bool = True) -> Optional[np.ndarray]:
    """
    Robust image retrieval with retry mechanism and comprehensive error handling.
    
    Fixes Issue #2 'simGetImage' error by implementing:
    - Retry mechanism with configurable attempts
    - Multiple retrieval methods (compressed/uncompressed)
    - Proper error handling and validation
    - Camera name optimization ("0" vs "FrontCenter")
    - Data type fixes (uint8 vs int8)
    
    Args:
        client: AirSim CarClient object
        camera: Camera name/ID (default: "0" - more reliable than "FrontCenter")
        image_type: Type of image to retrieve (Scene, DepthVis, etc.)
        retries: Number of retry attempts (default: 3)
        sleep: Sleep time between retries in seconds (default: 0.2)
        compress: Whether to use compression (default: True)
    
    Returns:
        np.ndarray: Decoded image as numpy array
        None: If all retry attempts failed
    
    Raises:
        ImageRetrievalError: If all retry attempts fail and strict mode
    """
    
    last_error = None
    
    for attempt in range(retries):
        try:
            logger.debug(f"Image retrieval attempt {attempt + 1}/{retries} (camera={camera}, compress={compress})")
            
            # Method 1: Use simGetImages with compression (more reliable)
            if compress:
                response = client.simGetImages([
                    airsim.ImageRequest(camera, image_type, False, True)
                ])
                
                # Validate response
                if not response or len(response) == 0:
                    raise ImageRetrievalError("Empty response from simGetImages")
                
                img_data = response[0]
                if img_data.image_data_uint8 is None or len(img_data.image_data_uint8) == 0:
                    raise ImageRetrievalError("Empty image data in response")
                
                # Convert compressed data to image
                nparr = np.frombuffer(img_data.image_data_uint8, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
            # Method 2: Use simGetImage without compression (fallback)
            else:
                result = client.simGetImage(camera, image_type)
                
                # Validate result
                if result is None or len(result) == 0:
                    raise ImageRetrievalError("Empty result from simGetImage")
                
                # Convert uncompressed data to image (FIX: use uint8 instead of int8)
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
            last_error = e
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            
            # Don't sleep on last attempt
            if attempt < retries - 1:
                time.sleep(sleep)
                
                # Switch strategy on first failure
                if attempt == 0 and compress:
                    compress = False
                    logger.debug("Switching to uncompressed method for next attempt")
    
    # All attempts failed
    error_msg = f"Failed to retrieve image after {retries} attempts. Last error: {str(last_error)}"
    logger.error(error_msg)
    return None


def get_image_safe(client: airsim.CarClient, **kwargs) -> Optional[np.ndarray]:
    """
    Safe wrapper that never raises exceptions - returns None on failure.
    
    Args:
        client: AirSim CarClient object
        **kwargs: Arguments passed to get_image()
    
    Returns:
        np.ndarray or None: Image or None if failed
    """
    try:
        return get_image(client, **kwargs)
    except Exception as e:
        logger.error(f"Image retrieval failed: {str(e)}")
        return None


def validate_connection(client: airsim.CarClient, timeout: float = 5.0) -> bool:
    """
    Validate AirSim connection is ready for image operations.
    
    Args:
        client: AirSim CarClient object
        timeout: Maximum time to wait for validation
    
    Returns:
        bool: True if connection is ready, False otherwise
    """
    try:
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Test basic connection
                client.getCarState()
                
                # Test image API specifically
                test_img = get_image(client, retries=1, sleep=0.1)
                if test_img is not None:
                    logger.info("AirSim connection and image API validated")
                    return True
                    
            except Exception as e:
                logger.debug(f"Connection validation attempt failed: {str(e)}")
                time.sleep(0.1)
        
        logger.error("Connection validation timed out")
        return False
        
    except Exception as e:
        logger.error(f"Connection validation failed: {str(e)}")
        return False
