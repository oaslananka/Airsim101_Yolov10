# utils/common.py
import numpy as np

def distance(pt1: tuple, pt2: tuple) -> float:
    """
    Calculate the Euclidean distance between two points.

    Args:
        pt1 (tuple): The coordinates of the first point in the form (x1, y1).
        pt2 (tuple): The coordinates of the second point in the form (x2, y2).

    Returns:
        float: The Euclidean distance between the two points.
    """
    return np.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)

def get_heading_from_quaternion(quaternion) -> float:
    """
    Calculates the heading (yaw) angle in degrees from a quaternion.

    Args:
        quaternion: A quaternion object representing the orientation.

    Returns:
        The heading angle in degrees.

    """
    w = quaternion.w_val
    x = quaternion.x_val
    y = quaternion.y_val
    z = quaternion.z_val
    yaw = np.arctan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))
    return np.rad2deg(yaw)
