#!/usr/bin/env python3
"""
Test script for Issue #2 'simGetImage' error fix.
This script validates the robustness of the improved image retrieval system.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

import airsim
import time
import logging
from detection.object_detection import get_image_robust, yolov10_object_detection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_connection():
    """Test basic AirSim connection."""
    logger.info("Testing AirSim connection...")
    
    try:
        client = airsim.CarClient()
        client.confirmConnection()
        logger.info("✅ AirSim connection successful")
        return client
    except Exception as e:
        logger.error(f"❌ AirSim connection failed: {str(e)}")
        return None


def test_image_retrieval_methods(client):
    """Test different image retrieval methods."""
    logger.info("Testing image retrieval methods...")
    
    test_cases = [
        # (camera, compress, description)
        ("0", True, "Camera '0' with compression"),
        ("0", False, "Camera '0' without compression"),
        ("FrontCenter", True, "Camera 'FrontCenter' with compression"), 
        ("FrontCenter", False, "Camera 'FrontCenter' without compression"),
        ("1", True, "Camera '1' with compression"),
    ]
    
    results = {}
    
    for camera, compress, description in test_cases:
        logger.info(f"Testing: {description}")
        
        try:
            img = get_image_robust(
                client=client,
                camera=camera,
                retries=2,  # Reduced retries for faster testing
                sleep_time=0.1,
                compress=compress
            )
            
            if img is not None:
                logger.info(f"✅ {description}: SUCCESS (shape: {img.shape})")
                results[description] = "SUCCESS"
            else:
                logger.warning(f"⚠️ {description}: FAILED (None returned)")
                results[description] = "FAILED"
                
        except Exception as e:
            logger.error(f"❌ {description}: ERROR ({str(e)})")
            results[description] = f"ERROR: {str(e)}"
    
    return results


def test_object_detection(client):
    """Test the complete object detection pipeline."""
    logger.info("Testing object detection pipeline...")
    
    try:
        # Test multiple iterations
        success_count = 0
        total_iterations = 5
        
        for i in range(total_iterations):
            logger.info(f"Object detection iteration {i+1}/{total_iterations}")
            
            result = yolov10_object_detection(client)
            
            if result:
                success_count += 1
                logger.info(f"✅ Iteration {i+1}: SUCCESS")
            else:
                logger.warning(f"⚠️ Iteration {i+1}: FAILED")
            
            time.sleep(0.5)  # Brief pause between iterations
        
        success_rate = (success_count / total_iterations) * 100
        logger.info(f"Object detection success rate: {success_rate:.1f}% ({success_count}/{total_iterations})")
        
        return success_rate >= 80  # Consider 80%+ success rate as good
        
    except Exception as e:
        logger.error(f"❌ Object detection test failed: {str(e)}")
        return False


def test_error_scenarios(client):
    """Test error handling scenarios."""
    logger.info("Testing error handling scenarios...")
    
    error_tests = [
        ("invalid_camera", True, "Invalid camera name"),
        ("999", True, "Non-existent camera ID"),
    ]
    
    for camera, compress, description in error_tests:
        logger.info(f"Testing error scenario: {description}")
        
        try:
            img = get_image_robust(
                client=client,
                camera=camera,
                retries=1,  # Single retry for error testing
                sleep_time=0.1,
                compress=compress
            )
            
            if img is None:
                logger.info(f"✅ {description}: Properly handled (returned None)")
            else:
                logger.warning(f"⚠️ {description}: Unexpected success")
                
        except Exception as e:
            logger.info(f"✅ {description}: Exception properly caught ({str(e)})")


def main():
    """Main test function."""
    logger.info("=" * 60)
    logger.info("Starting Issue #2 'simGetImage' Error Fix Tests")
    logger.info("=" * 60)
    
    # Test connection
    client = test_connection()
    if not client:
        logger.error("Cannot proceed without AirSim connection")
        return False
    
    try:
        # Enable API control
        client.enableApiControl(True)
        
        # Run tests
        logger.info("\n" + "=" * 40)
        retrieval_results = test_image_retrieval_methods(client)
        
        logger.info("\n" + "=" * 40)
        detection_success = test_object_detection(client)
        
        logger.info("\n" + "=" * 40)
        test_error_scenarios(client)
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("TEST SUMMARY")
        logger.info("=" * 60)
        
        logger.info("Image Retrieval Results:")
        for method, result in retrieval_results.items():
            status_icon = "✅" if result == "SUCCESS" else "❌"
            logger.info(f"  {status_icon} {method}: {result}")
        
        detection_icon = "✅" if detection_success else "❌"
        logger.info(f"\nObject Detection Pipeline: {detection_icon} {'PASSED' if detection_success else 'FAILED'}")
        
        # Determine overall result
        successful_retrievals = sum(1 for r in retrieval_results.values() if r == "SUCCESS")
        overall_success = successful_retrievals > 0 and detection_success
        
        logger.info(f"\nOVERALL RESULT: {'✅ PASSED' if overall_success else '❌ FAILED'}")
        
        return overall_success
        
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        return False
        
    finally:
        # Cleanup
        try:
            client.enableApiControl(False)
            logger.info("Test cleanup completed")
        except Exception as e:
            logger.warning(f"Cleanup warning: {str(e)}")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
