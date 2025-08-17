# core/main.py
import sys
from pathlib import Path

current_directory = Path(__file__).resolve().parent
parent_directory = current_directory.parent
sys.path.append(str(parent_directory))

import threading
import airsim
from config.graph import graph
from core.astar import astar
from core.control import control_vehicle
from utils.robust_image import validate_connection

def main():
    """
    The main function controls the execution flow of the program.
    It initializes the start and goal coordinates, finds the path using the A* algorithm,
    connects to the AirSim CarClient, controls the vehicle, and handles keyboard interrupts.
    
    Enhanced with connection validation to prevent Issue #2.
    """
    start_coord = (0, 0)
    goal_coord = (126, 126)

    path = astar(graph, start_coord, goal_coord)

    client = airsim.CarClient()
    client.confirmConnection()
    
    # Validate connection before proceeding (fixes Issue #2)
    if not validate_connection(client, timeout=10.0):
        print("❌ Failed to validate AirSim connection")
        return
    
    client.enableApiControl(True)
    client.reset()

    car_controls = airsim.CarControls()
    control_thread = threading.Thread(target=control_vehicle, args=(client, car_controls, path))
    control_thread.start()

    try:
        while control_thread.is_alive():
            control_thread.join(0.1)
        print("The vehicle has reached the destination")
    except KeyboardInterrupt:
        print("KeyboardInterrupt has been caught")
    finally:
        try:
            client.enableApiControl(False)
        except:
            pass

if __name__ == "__main__":
    main()


def validate_airsim_connection(client, timeout=10.0):
    """
    Validate AirSim connection before starting main operations.
    
    Args:
        client: AirSim CarClient object
        timeout: Maximum time to wait for connection validation
    
    Returns:
        bool: True if connection is ready, False otherwise
    """
    try:
        start_time = time.time()
        
        logger.info("Validating AirSim connection...")
        
        while time.time() - start_time < timeout:
            try:
                # Test basic API calls
                client.getCarState()
                
                # Test image API specifically (this addresses Issue #2)
                test_response = client.simGetImages([
                    airsim.ImageRequest("0", airsim.ImageType.Scene, False, True)
                ])
                
                if test_response and len(test_response) > 0:
                    logger.info("AirSim connection and image API validated successfully")
                    return True
                    
            except Exception as e:
                logger.debug(f"Connection validation attempt failed: {str(e)}")
                time.sleep(0.5)
        
        logger.error("AirSim connection validation timed out")
        return False
        
    except Exception as e:
        logger.error(f"AirSim connection validation failed: {str(e)}")
        return False


def main():
    """
    The main function controls the execution flow of the program.
    It initializes the start and goal coordinates, finds the path using the A* algorithm,
    connects to the AirSim CarClient, controls the vehicle, and handles keyboard interrupts.
    
    Improvements in this version:
    1. Added connection validation to prevent Issue #2
    2. Added proper error handling and logging
    3. Added graceful shutdown handling
    4. Added retry mechanism for connection issues

    Parameters:
        None

    Returns:
        None
    """
    logger.info("Starting Airsim101_Yolov10 application...")
    
    start_coord = (0, 0)
    goal_coord = (126, 126)

    try:
        # Generate path using A* algorithm
        logger.info(f"Calculating path from {start_coord} to {goal_coord}")
        path = astar(graph, start_coord, goal_coord)
        
        if not path:
            logger.error("Failed to find path with A* algorithm")
            return
        
        logger.info(f"Path calculated successfully with {len(path)} waypoints")

        # Initialize AirSim client with retry mechanism
        max_connection_attempts = 3
        client = None
        
        for attempt in range(max_connection_attempts):
            try:
                logger.info(f"Connecting to AirSim (attempt {attempt + 1}/{max_connection_attempts})...")
                client = airsim.CarClient()
                client.confirmConnection()
                
                # Validate connection thoroughly (addresses Issue #2)
                if validate_airsim_connection(client, timeout=10.0):
                    break
                else:
                    logger.warning("Connection validation failed, retrying...")
                    client = None
                    
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_connection_attempts - 1:
                    logger.info("Retrying in 2 seconds...")
                    time.sleep(2)
                client = None
        
        if client is None:
            logger.error("Failed to establish valid AirSim connection after all attempts")
            return

        # Initialize vehicle controls
        logger.info("Initializing vehicle controls...")
        client.enableApiControl(True)
        client.reset()

        car_controls = airsim.CarControls()
        
        # Start vehicle control in separate thread
        logger.info("Starting vehicle control thread...")
        control_thread = threading.Thread(target=control_vehicle, args=(client, car_controls, path))
        control_thread.daemon = True  # Allow main thread to exit
        control_thread.start()

        # Main monitoring loop
        try:
            while control_thread.is_alive():
                control_thread.join(0.1)
            logger.info("The vehicle has reached the destination")
            
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received, shutting down gracefully...")
            
        finally:
            # Cleanup
            try:
                if client:
                    logger.info("Cleaning up AirSim connection...")
                    car_controls.throttle = 0
                    car_controls.brake = 1
                    client.setCarControls(car_controls)
                    client.enableApiControl(False)
                    logger.info("AirSim cleanup completed")
            except Exception as e:
                logger.warning(f"Error during cleanup: {str(e)}")

    except Exception as e:
        logger.error(f"Fatal error in main function: {str(e)}")
        raise

    finally:
        logger.info("Application shutdown complete")


if __name__ == "__main__":
    main()
