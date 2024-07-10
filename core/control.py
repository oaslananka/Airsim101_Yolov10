# core/control.py
import time
import numpy as np
from utils.common import distance, get_heading_from_quaternion
from core.sensors import get_distance_sensors
from detection.object_detection import yolov10_object_detection


import numpy as np

def pure_pursuit_control(current_position: tuple, current_heading: float, target_position: tuple, ld: float = 4) -> float:
    """
    Calculates the steering angle for a pure pursuit control algorithm.

    Args:
        current_position (tuple): The current position of the vehicle (x, y).
        current_heading (float): The current heading of the vehicle in degrees.
        target_position (tuple): The target position to track (x, y).
        ld (float, optional): The look-ahead distance. Defaults to 4.

    Returns:
        float: The calculated steering angle in radians.
    """
    dx = target_position[0] - current_position[0]
    dy = target_position[1] - current_position[1]
    angle_to_target = np.arctan2(dy, dx)
    angle_front_car = np.deg2rad(current_heading)
    alpha = angle_to_target - angle_front_car
    steering_angle = np.arctan(2 * 2.5 * np.sin(alpha) / ld)
    max_steering_angle = np.deg2rad(30)
    return np.clip(steering_angle, -max_steering_angle, max_steering_angle)


def go_reverse(client, car_controls, current_position: tuple, target_position: tuple):
    """
    Moves the car in reverse until a certain distance is covered.

    Args:
        client: The AirSim client object.
        car_controls: The car controls object.
        current_position: The current position of the car as a tuple (x, y).
        target_position: The target position to reach as a tuple (x, y).
    """
    reverse_distance = 5
    reverse_speed = -0.3
    distance_covered = 0
    car_controls.throttle = reverse_speed
    car_controls.is_manual_gear = True
    car_controls.manual_gear = -1

    while distance_covered < reverse_distance:
        car_state = client.getCarState()
        car_pos = car_state.kinematics_estimated.position
        new_position = (car_pos.x_val, car_pos.y_val)
        steering_angle = pure_pursuit_control(new_position, 180, target_position)
        car_controls.steering = steering_angle
        client.setCarControls(car_controls)
        distance_covered += distance(current_position, new_position)
        current_position = new_position
        time.sleep(0.05)

    car_controls.is_manual_gear = False
    car_controls.manual_gear = 0
    car_controls.throttle = 0
    client.setCarControls(car_controls)
    time.sleep(1)


def control_vehicle(client, car_controls, path: list):
    """
    Controls the vehicle to follow a given path using pure pursuit control algorithm.

    Args:
        client: The AirSim client object.
        car_controls: The car controls object.
        path (list): A list of waypoints representing the desired path.

    Returns:
        None
    """
    stuck_counter = 0
    stuck_position = None

    for waypoint in path:
        while True:
            yolov10_object_detection(client)
            car_state = client.getCarState()
            car_pos = car_state.kinematics_estimated.position
            car_orientation = car_state.kinematics_estimated.orientation
            car_heading = get_heading_from_quaternion(car_orientation)
            current_position = (car_pos.x_val, car_pos.y_val)
            steering_angle = pure_pursuit_control(current_position, car_heading, waypoint)
            car_controls.steering = steering_angle
            car_controls.throttle = 0.3
            front_distance, front_left_distance, front_right_distance, rear_distance, rear_left_distance, rear_right_distance, left_distance, right_distance = get_distance_sensors(client)

            if front_distance < 4:
                car_controls.throttle = 0
                client.setCarControls(car_controls)
                go_reverse(client, car_controls, current_position, waypoint)
            elif left_distance < 1 or front_left_distance < 2:
                car_controls.steering = np.deg2rad(30)
            elif right_distance < 1 or front_right_distance < 2:
                car_controls.steering = np.deg2rad(-30)

            client.setCarControls(car_controls)

            if distance(current_position, waypoint) < 5:
                break

            if stuck_position is None or distance(current_position, stuck_position) > 1:
                stuck_position = current_position
                stuck_counter = 0
            else:
                stuck_counter += 1

            if stuck_counter > 100:
                go_reverse(client, car_controls, current_position, waypoint)
                stuck_counter = 0
                stuck_position = None

            time.sleep(0.05)

    car_controls.throttle = 0
    car_controls.brake = 1
    client.setCarControls(car_controls)
    time.sleep(1)
    client.enableApiControl(False)
