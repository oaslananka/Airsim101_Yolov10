#!/usr/bin/env python3
"""
examples/validate_image_grab.py

Smoke-test script for Issue #2 'simGetImage' error fix.
Quick validation that image retrieval works robustly.

Usage:
    cd examples
    python validate_image_grab.py

Expected result: Should successfully grab images without crashing
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

import airsim
import cv2
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_connection():
    """Quick connection test."""
    logger.info("🔍 Testing AirSim connection...")
    try:
        client = airsim.CarClient()
        client.confirmConnection()
        logger.info("✅ Connection established")
        return client
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return None


def test_image_grab_methods(client):
    """Test both old (problematic) and new (fixed) image grab methods."""
    
    logger.info("🔍 Testing image retrieval methods...")
    
    # Import after path setup
    from detection.object_detection import get_image_robust
    
    results = {}
    
    # Test 1: Fixed robust method
    logger.info("Testing robust wrapper method...")
    try:
        img_robust = get_image_robust(
            client=client,
            camera="0",
            retries=2,
            sleep_time=0.1,
            compress=True
        )
        
        if img_robust is not None and img_robust.size > 0:
            logger.info(f"✅ Robust method: SUCCESS (shape: {img_robust.shape})")
            results['robust'] = True
        else:
            logger.warning("⚠️ Robust method: FAILED (None or empty)")
            results['robust'] = False
            
    except Exception as e:
        logger.error(f"❌ Robust method: ERROR ({e})")
        results['robust'] = False
    
    # Test 2: Legacy method (should fail on problematic setups)
    logger.info("Testing legacy method...")
    try:
        result = client.simGetImage("FrontCenter", airsim.ImageType.Scene)
        import numpy as np
        raw_image = np.frombuffer(result, np.int8)  # Original problematic code
        img_legacy = cv2.imdecode(raw_image, cv2.IMREAD_UNCHANGED)
        
        if img_legacy is not None and img_legacy.size > 0:
            logger.info("✅ Legacy method: SUCCESS (lucky!)")
            results['legacy'] = True
        else:
            logger.warning("⚠️ Legacy method: FAILED (decode issue)")
            results['legacy'] = False
            
    except Exception as e:
        logger.warning(f"⚠️ Legacy method: FAILED ({e}) - This is expected!")
        results['legacy'] = False
    
    # Test 3: Alternative cameras
    logger.info("Testing alternative camera configurations...")
    camera_tests = ["0", "1", "FrontCenter"]
    working_cameras = []
    
    for camera in camera_tests:
        try:
            img = get_image_robust(client, camera=camera, retries=1, sleep_time=0.1)
            if img is not None:
                working_cameras.append(camera)
                logger.info(f"✅ Camera '{camera}': Working")
            else:
                logger.info(f"⚠️ Camera '{camera}': Not available")
        except Exception as e:
            logger.info(f"⚠️ Camera '{camera}': Error ({e})")
    
    results['working_cameras'] = working_cameras
    return results


def test_object_detection_pipeline(client):
    """Test the complete object detection pipeline."""
    logger.info("🔍 Testing object detection pipeline...")
    
    try:
        from detection.object_detection import yolov10_object_detection
        
        # Test a few iterations
        success_count = 0
        total_tests = 3
        
        for i in range(total_tests):
            logger.info(f"Detection test {i+1}/{total_tests}")
            
            try:
                result = yolov10_object_detection(client)
                if result:
                    success_count += 1
                    logger.info(f"✅ Detection test {i+1}: SUCCESS")
                    
                    # Close any opened windows to prevent accumulation
                    cv2.destroyAllWindows()
                else:
                    logger.info(f"⚠️ Detection test {i+1}: STOPPED (user quit)")
                    break
                    
            except Exception as e:
                logger.warning(f"⚠️ Detection test {i+1}: ERROR ({e})")
                
            time.sleep(0.5)  # Brief pause
        
        cv2.destroyAllWindows()  # Cleanup
        
        success_rate = (success_count / total_tests) * 100 if total_tests > 0 else 0
        logger.info(f"Detection pipeline success rate: {success_rate:.1f}%")
        
        return success_rate >= 66  # 2/3 success rate acceptable
        
    except Exception as e:
        logger.error(f"❌ Object detection test failed: {e}")
        return False


def main():
    """Main smoke test function."""
    print("=" * 60)
    print("🧪 SMOKE TEST: Issue #2 'simGetImage' Error Fix")
    print("=" * 60)
    
    # Test connection
    client = test_connection()
    if not client:
        print("❌ SMOKE TEST FAILED: Cannot connect to AirSim")
        return False
    
    try:
        # Enable API control
        client.enableApiControl(True)
        
        # Test image retrieval
        print("\n" + "=" * 40)
        retrieval_results = test_image_grab_methods(client)
        
        # Test object detection pipeline
        print("\n" + "=" * 40)
        detection_success = test_object_detection_pipeline(client)
        
        # Results summary
        print("\n" + "=" * 60)
        print("📋 SMOKE TEST RESULTS")
        print("=" * 60)
        
        print(f"Robust image retrieval: {'✅ PASS' if retrieval_results.get('robust', False) else '❌ FAIL'}")
        print(f"Legacy method (expected to fail): {'⚠️ WORKS' if retrieval_results.get('legacy', False) else '✅ FAILS (good!)'}")
        print(f"Working cameras: {retrieval_results.get('working_cameras', [])}")
        print(f"Object detection pipeline: {'✅ PASS' if detection_success else '❌ FAIL'}")
        
        # Overall assessment
        robust_works = retrieval_results.get('robust', False)
        has_cameras = len(retrieval_results.get('working_cameras', [])) > 0
        overall_success = robust_works and has_cameras and detection_success
        
        print(f"\n🎯 OVERALL RESULT: {'✅ SMOKE TEST PASSED' if overall_success else '❌ SMOKE TEST FAILED'}")
        
        if overall_success:
            print("\n✅ Issue #2 fix is working correctly!")
            print("✅ Image retrieval is robust and reliable")
            print("✅ Object detection pipeline is functional")
        else:
            print("\n❌ Some issues detected:")
            if not robust_works:
                print("  - Robust image retrieval is not working")
            if not has_cameras:
                print("  - No working cameras found")
            if not detection_success:
                print("  - Object detection pipeline has issues")
        
        return overall_success
        
    except Exception as e:
        logger.error(f"Smoke test execution failed: {e}")
        return False
        
    finally:
        # Cleanup
        try:
            client.enableApiControl(False)
            cv2.destroyAllWindows()
            print("\n🧹 Cleanup completed")
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")


if __name__ == "__main__":
    success = main()
    print(f"\n{'✅ SMOKE TEST COMPLETED SUCCESSFULLY' if success else '❌ SMOKE TEST FAILED'}")
    sys.exit(0 if success else 1)
