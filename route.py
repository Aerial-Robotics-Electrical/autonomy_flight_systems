# Library containing methods for navigation of drones to given waypoints

import json

class Route:
    def __init__(self, waypoint_list_path='waypoints.json', debug=False):
        # Load waypoints for lead to follow and chase to receive
        self.waypoints = json.load(open(waypoint_list_path, 'rb'))


if __name__ == "__main__":
    route = Route(waypoint_list_path='waypoints.json')
    for waypoint in route.waypoints["points"]:
        print(waypoint)
    for i, waypoint in enumerate(route.waypoints["points"]):
        print(i, waypoint)