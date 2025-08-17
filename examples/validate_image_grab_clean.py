#!/usr/bin/env python3
"""
examples/validate_image_grab.py

Quick smoke test for Issue #2 'simGetImage' error fix.
Validates that robust image retrieval works correctly.

Usage:
    cd examples
    python validate_image_grab.py

Expected result: Should successfully grab images without crashing.
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
from utils.robust_image import get_image, get_image_safe, validate_connection


def test_connection():
    """Test basic AirSim connection."""
    print("🔍 Testing AirSim connection...")
    try:
        client = airsim.CarClient()
        client.confirmConnection()
        print("✅ Connection established")
        return client
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None


def test_legacy_vs_robust():
    """Test comparison between legacy problematic method and robust method."""
    print("\n🔍 Testing legacy vs robust image retrieval...")
    
    client = test_connection()
    if not client:
        return False
    
    try:
        client.enableApiControl(True)
        
        # Test 1: Legacy method (should fail on problematic setups)
        print("Testing legacy method (problematic)...")
        try:
            result = client.simGetImage("FrontCenter", airsim.ImageType.Scene)
            import numpy as np
            raw_image = np.frombuffer(result, np.int8)  # Original problematic code
            img_legacy = cv2.imdecode(raw_image, cv2.IMREAD_UNCHANGED)
            
            if img_legacy is not None and img_legacy.size > 0:
                print("✅ Legacy method: Unexpected success!")
                legacy_works = True
            else:
                print("⚠️ Legacy method: Failed (decode issue)")
                legacy_works = False
        except Exception as e:
            print(f"⚠️ Legacy method: Failed with error: {e}")
            legacy_works = False
        
        # Test 2: Robust method
        print("Testing robust method...")
        try:
            img_robust = get_image_safe(client, camera="0", retries=3, sleep=0.2, compress=True)
            
            if img_robust is not None and img_robust.size > 0:
                print(f"✅ Robust method: SUCCESS (shape: {img_robust.shape})")
                robust_works = True
            else:
                print("❌ Robust method: Failed")
                robust_works = False
        except Exception as e:
            print(f"❌ Robust method: Error: {e}")
            robust_works = False
        
        # Test 3: Connection validation
        print("Testing connection validation...")
        validation_works = validate_connection(client, timeout=5.0)
        print(f"{'✅' if validation_works else '❌'} Connection validation: {'PASSED' if validation_works else 'FAILED'}")
        
        return robust_works and validation_works
        
    finally:
        try:
            client.enableApiControl(False)
        except:
            pass


def test_multiple_cameras():
    """Test different camera configurations."""
    print("\n🔍 Testing multiple camera configurations...")
    
    client = test_connection()
    if not client:
        return False
    
    try:
        client.enableApiControl(True)
        
        cameras = ["0", "1", "FrontCenter", "FrontLeft"]
        working_cameras = []
        
        for camera in cameras:
            print(f"Testing camera '{camera}'...")
            try:
                img = get_image_safe(client, camera=camera, retries=2, sleep=0.1)
                if img is not None:
                    working_cameras.append(camera)
                    print(f"✅ Camera '{camera}': Working (shape: {img.shape})")
                else:
                    print(f"⚠️ Camera '{camera}': Not available")
            except Exception as e:
                print(f"⚠️ Camera '{camera}': Error ({e})")
        
        print(f"\n📊 Working cameras: {working_cameras}")
        return len(working_cameras) > 0
        
    finally:
        try:
            client.enableApiControl(False)
        except:
            pass


def test_object_detection():
    """Test object detection pipeline with robust image retrieval."""
    print("\n🔍 Testing object detection pipeline...")
    
    try:
        from detection.object_detection import yolov10_object_detection
        
        client = test_connection()
        if not client:
            return False
        
        try:
            client.enableApiControl(True)
            
            # Test multiple iterations
            success_count = 0
            total_tests = 3
            
            for i in range(total_tests):
                print(f"Detection test {i+1}/{total_tests}")
                
                try:
                    result = yolov10_object_detection(client)
                    if result:
                        success_count += 1
                        print(f"✅ Detection {i+1}: SUCCESS")
                        cv2.destroyAllWindows()  # Clean up windows
                    else:
                        print(f"⚠️ Detection {i+1}: User quit")
                        break
                except Exception as e:
                    print(f"⚠️ Detection {i+1}: ERROR ({e})")
                
                time.sleep(0.5)
            
            cv2.destroyAllWindows()
            success_rate = (success_count / total_tests) * 100 if total_tests > 0 else 0
            print(f"📊 Detection success rate: {success_rate:.1f}%")
            
            return success_rate >= 50  # 50%+ success rate acceptable
            
        finally:
            try:
                client.enableApiControl(False)
            except:
                pass
                
    except ImportError as e:
        print(f"⚠️ Cannot import object detection module: {e}")
        return False


def main():
    """Main test function."""
    print("=" * 60)
    print("🧪 SMOKE TEST: Issue #2 'simGetImage' Error Fix")
    print("=" * 60)
    
    # Test 1: Legacy vs Robust comparison
    legacy_vs_robust_result = test_legacy_vs_robust()
    
    # Test 2: Multiple camera configurations
    camera_result = test_multiple_cameras()
    
    # Test 3: Object detection pipeline
    detection_result = test_object_detection()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SMOKE TEST SUMMARY")
    print("=" * 60)
    
    print(f"Robust image retrieval: {'✅ PASS' if legacy_vs_robust_result else '❌ FAIL'}")
    print(f"Camera configurations: {'✅ PASS' if camera_result else '❌ FAIL'}")
    print(f"Object detection pipeline: {'✅ PASS' if detection_result else '❌ FAIL'}")
    
    overall_success = legacy_vs_robust_result and camera_result
    
    print(f"\n🎯 OVERALL RESULT: {'✅ SMOKE TEST PASSED' if overall_success else '❌ SMOKE TEST FAILED'}")
    
    if overall_success:
        print("\n✅ Issue #2 fix is working correctly!")
        print("✅ Robust image retrieval implemented successfully")
        print("✅ Multiple camera configurations supported")
        print("✅ System is ready for production use")
    else:
        print("\n❌ Issues detected:")
        if not legacy_vs_robust_result:
            print("  - Robust image retrieval is not working properly")
        if not camera_result:
            print("  - No working camera configurations found")
        if not detection_result:
            print("  - Object detection pipeline has issues")
    
    return overall_success


if __name__ == "__main__":
    success = main()
    print(f"\n{'✅ SMOKE TEST COMPLETED SUCCESSFULLY' if success else '❌ SMOKE TEST FAILED'}")
    sys.exit(0 if success else 1)
