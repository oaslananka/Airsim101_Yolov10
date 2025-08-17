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
        except Exception:
            pass

if __name__ == "__main__":
    main()
