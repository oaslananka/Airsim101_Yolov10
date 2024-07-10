# core/astar.py

import heapq
import math
from config.coordinates import coordinates
from config.graph import graph


def heuristic(coord1: tuple, coord2: tuple) -> float:
    """
    Calculates the Euclidean distance between two coordinates.

    Args:
        coord1 (tuple): The first coordinate in the form (x1, y1).
        coord2 (tuple): The second coordinate in the form (x2, y2).

    Returns:
        float: The Euclidean distance between the two coordinates.
    """
    (x1, y1) = coord1
    (x2, y2) = coord2
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def astar(graph: dict, start_coord: tuple, goal_coord: tuple) -> list:
    """
    A* algorithm implementation to find the shortest path between two points in a graph.

    Args:
        graph (dict): A dictionary representing the graph where each key is a node and the value is a list of neighboring nodes.
        start_coord (tuple): The coordinates of the starting point.
        goal_coord (tuple): The coordinates of the goal point.

    Returns:
        list: A list of coordinates representing the shortest path from the starting point to the goal point.
              If no path is found, an empty list is returned.
    """
    start_node = min(coordinates, key=lambda node: heuristic(start_coord, coordinates[node]))
    goal_node = min(coordinates, key=lambda node: heuristic(goal_coord, coordinates[node]))

    open_list = [(0, start_node)]
    came_from = {node: None for node in coordinates}
    g_score = {node: float('infinity') for node in coordinates}
    g_score[start_node] = 0
    f_score = {node: float('infinity') for node in coordinates}
    f_score[start_node] = heuristic(start_coord, coordinates[goal_node])

    while open_list:
        _, current_node = heapq.heappop(open_list)

        if current_node == goal_node:
            path = []
            while current_node:
                path.append(coordinates[current_node])
                current_node = came_from[current_node]
            return path[::-1]

        for neighbor in graph[current_node]:
            neighbor_coord = coordinates[neighbor]
            tentative_g_score = g_score[current_node] + heuristic(coordinates[current_node], neighbor_coord)

            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current_node
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor_coord, coordinates[goal_node])
                heapq.heappush(open_list, (f_score[neighbor], neighbor))

    return []
