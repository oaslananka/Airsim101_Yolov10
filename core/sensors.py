# core/sensors.py

def get_distance_sensors(client) -> tuple:
    """
    Retrieves distance sensor data from the client for various sensor positions.

    Args:
        client: The client object used to communicate with the vehicle.

    Returns:
        A tuple containing the distance sensor data for the following positions:
        - front_distance: Distance from the front sensor.
        - front_left_distance: Distance from the front left sensor.
        - front_right_distance: Distance from the front right sensor.
        - rear_distance: Distance from the rear sensor.
        - rear_left_distance: Distance from the rear left sensor.
        - rear_right_distance: Distance from the rear right sensor.
        - left_distance: Distance from the left sensor.
        - right_distance: Distance from the right sensor.
    """
    front_distance = client.getDistanceSensorData(vehicle_name='Car1', distance_sensor_name='FrontDistance').distance
    front_left_distance = client.getDistanceSensorData(vehicle_name='Car1', distance_sensor_name='FrontLeftDistance').distance
    front_right_distance = client.getDistanceSensorData(vehicle_name='Car1', distance_sensor_name='FrontRightDistance').distance
    rear_distance = client.getDistanceSensorData(vehicle_name='Car1', distance_sensor_name='RearDistance').distance
    rear_left_distance = client.getDistanceSensorData(vehicle_name='Car1', distance_sensor_name='RearLeftDistance').distance
    rear_right_distance = client.getDistanceSensorData(vehicle_name='Car1', distance_sensor_name='RearRightDistance').distance
    left_distance = client.getDistanceSensorData(vehicle_name='Car1', distance_sensor_name='LeftDistance').distance
    right_distance = client.getDistanceSensorData(vehicle_name='Car1', distance_sensor_name='RightDistance').distance
    return front_distance, front_left_distance, front_right_distance, rear_distance, rear_left_distance, rear_right_distance, left_distance, right_distance
