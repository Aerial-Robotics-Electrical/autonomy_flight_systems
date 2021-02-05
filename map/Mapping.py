import json
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import math
import numpy as np 
from mavsdk.mission import (MissionItem, MissionPlan)

class Map:
    """
    Class that uses Json file path of boundaries and obstacles
    to create a environment space
    """
    def __init__(self, resolution, mission_data, buffer):
        """
        Initialize grid map for a star planning

        resolution: grid resolution [m]
        boundarypoints: list of points that make up a polygonal fence
        obstacles: list of points and respective radiuses 
        buffer: buffer around obstacles
        """ 

        file = json.load(open(mission_data, 'rb'))
        # This will contain a LocationGlobalRelative object for the current destination
        self.currentDest = None
        waypoints = []
        boundarypoints = []
        searchGridPoints = []
        obstacles = []
        # Looping through the waypoint dicts to load GPS cords
        for waypoint in file["waypoints"]:
            waypoints += [[waypoint["latitude"],
                           waypoint["longitude"], waypoint["altitude"]]]

        # Looping through the flyzone boundary dicts to load proper GPS cords
        for boundarypoint in file["flyZones"][0]["boundaryPoints"]:
            boundarypoints += [[boundarypoint["latitude"],
                                boundarypoint["longitude"]]]

        # Looping through the search grid dict to load GPS coords
        for searchpoint in file["searchGridPoints"]:
            searchGridPoints += [[searchpoint["latitude"],
                                  searchpoint["longitude"]]]

        for obstacle in file["stationaryObstacles"]:
            obstacles += [[obstacle["latitude"],
                            obstacle["longitude"], obstacle["radius"]]]


        # Contains flight data in a dict with easy access coords
        self.data = {"waypoints": waypoints,
                "boundary": boundarypoints, "searchGrid": searchGridPoints, "stationaryObstacles": obstacles}

        min = np.amin(boundarypoints, axis = 0)
        self.min_lat = min[0]
        self.min_lon = min[1]

        # transforms decimal coordinates to cartesian plane with (0,0) at (min_lat, min_lon)
        for point in boundarypoints:
            point[0], point[1] = self.decimal_to_cartesian(point[0], point[1], self.min_lat, self.min_lon)
        for obstacle in obstacles:
            obstacle[0], obstacle[1] = self.decimal_to_cartesian(obstacle[0], obstacle[1], self.min_lat, self.min_lon)

        self.map_x_width, self.map_y_width = 0, 0                       # widths of transformed obstacle map
        self.cart_max_x, self.cart_max_y = 0, 0                         # maxes of cartesian coordiantes                     
        self.resolution = resolution                                    # resolution (meters)
        self.buffer = buffer                                            # buffer
        self.calc_grid_bounds(boundarypoints)                           # finds values for max and map widths 
        self.obstacle_map = None                                        # map of obstacles (initialized to none)
        self.calc_obstacle_map(obstacles, boundarypoints, buffer)       # creates map of obstacles and boundaries, stores it into a 2D list in obstacle_map
 

    def generateWaypoint(self, plane, coordinate):
        """
        This will take in GPS coordinates and feed it to the drone.

        Expected input: plane (connection.py Object) - object containing the Dronekit vehicle. Used to feed the destination to the drone
            coordinate (tuple) - a tuple containing the desired ending GPS coordinates [latitude, longitude, altitude]

        Expected output: Returns a waypoint that can be fed to dronekit (sets the current destination to the provided coordinate)
        """
        self.currentDest = MissionItem(coordinate[0], coordinate[1], coordinate[2],
                                       10,
                                       True,
                                       float('nan'),
                                       float('nan'),
                                       MissionItem.CameraAction.NONE,
                                       float('nan'),
                                       float('nan'))
        return self.currentDest

    def breakWaypoints(self, waypointOne, waypointTwo, breakAmount=10):
        """
        This method will take in two waypoints and break it up into multiple waypoints along a line connecting the
        original two waypoints.

        Expected input: waypointOne (tuple) - a tuple containing the starting GPS coordinates [latitude, longitude, altitude]
            waypointTwo (tuple) - a tuple containing the desired ending GPS coordinates [latitude, longitude, altitude]
            breakAmount (int) - describes how many addional waypoints are wanted. By default, the function create ten extra points. 

        Expected output: returns a list containing all the new waypoints in order of occurance along the line between the two points
        """
        waypointList = []
        for stepNumber in range(1, breakAmount + 1):
            waypointList.append({"latitude": self.generateStep(stepNumber, waypointOne["latitude"], waypointTwo["latitude"], breakAmount),
                                 "longitude": self.generateStep(stepNumber, waypointOne["longitude"], waypointTwo["longitude"], breakAmount),
                                 "altitude": self.generateStep(stepNumber, waypointOne["altitude"], waypointTwo["latitude"], breakAmount)})

        return waypointList

    def generateStep(self, stepNumber, paramPointOne, paramPointTwo, breakAmount):
        return paramPointOne + round((stepNumber * (paramPointTwo - paramPointOne) / float(breakAmount)), 8)

    def changeRoute(self, route, targetWaypoint, newRoute):
        """
        This method will take in a list, targetWaypoint (coordiantes), and a new list. It will chop the original list at the specified
        waypoint and input the new list tuples after that point. It will finally return this newly created list.

        Expected input: route (list) - a list that needs to be changed containing tuples containing GPS coordinates [latitude, longitude, altitude]
            waypoint (tuple) - a tuple containing the desired chopping GPS coordinates [latitude, longitude, altitude]
            newRoute (list) - a new list that will replace tuples following chopPoint containing tuples containing GPS coordinates [latitude, longitude, altitude]

        Expected output: returns a list containing all the new waypoints in order of occurance along the line between the two points, or False if the target is not in the route.
        """
        if targetWaypoint in route:
            return (route[0:route.index(targetWaypoint)] + newRoute)
        else:
            return False

    def calc_bearing(self, lat1, lon1, lat2, lon2):
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)
        dlat = lat2 - lat1
        dlon = lon2- lon1
        return math.atan2(math.sin(dlon) * math.cos(lat2), math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon))

    def calc_haversine(self, lat1, lon1, lat2, lon2):
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)
        dlat = lat2 - lat1
        dlon = lon2- lon1
        a = pow(math.sin(dlat / 2),2) + math.cos(lat1) * math.cos(lat2) * pow(math.sin(dlon / 2), 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = 6371e3 * c  #  meters
        return d

    def decimal_to_cartesian(self, lat1, lon1, lat2, lon2):
        d = self.calc_haversine(lat2, lon2, lat1, lon1)
        bearing = self.calc_bearing(lat2, lon2, lat1, lon1)
        x = d * math.cos(bearing)
        y = d * math.sin(bearing)
        return x, y
    
    def cartesian_to_decimal(self, x, y, lat1, lon1):
        bearing = math.atan(y / x)
        d = x / math.cos(bearing)
        r = 6371e3
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.degrees(math.asin(math.sin(lat1) * math.cos(d / r) +
                            math.cos(lat1) * math.sin(d / r) * math.cos(bearing)))
        lon2 =  math.degrees(lon1 + math.atan2(math.sin(bearing) * math.sin(d / r) * math.cos(lat1),
                                    math.cos(d / r) - math.sin(lat1) * math.sin(math.radians(lat2))))
        return lat2, lon2
    
    def transform_to_cart_position(self, index):
        """
        transforms index to corresponding cartesian position 
        """ 
        position = index * self.resolution
        return position

    def transform_to_map_index(self, position):
        """
        transforms cartesian position to corresponding index position 
        """ 
        index = position / self.resolution
        return index

    def calc_grid_bounds(self, boundarypoints):
        for boundarypoint in boundarypoints:
            if boundarypoint[0] > self.cart_max_x:
                self.cart_max_x = boundarypoint[0]
            if boundarypoint[1] > self.cart_max_y:
                self.cart_max_y = boundarypoint[1]
        self.map_y_width = round(self.cart_max_y / self.resolution)
        self.map_x_width = round(self.cart_max_x / self.resolution)

    def calc_obstacle_map(self, obstacles, boundarypoints, buffer):
        boundaryPath = mpath.Path(boundarypoints)
        self.obstacle_map = [[False for _ in range(self.map_y_width)] for _ in range(self.map_x_width)]
        for initial_x in range(self.map_x_width):
            x = self.transform_to_cart_position(initial_x)
            for initial_y in range(self.map_y_width):
                y = self.transform_to_cart_position(initial_y)
                if not boundaryPath.contains_point([x,y]):
                    self.obstacle_map[initial_x][initial_y] = True
                else:
                    for obstacle in obstacles:
                        if math.hypot(obstacle[0] - x, obstacle[1] - y) - self.buffer <= obstacle[2] * 0.3048:
                            self.obstacle_map[initial_x][initial_y] = True
                            break
    
def main():
    mission_data = "..//interop_example.json"
    resolution = 10
    buffer = 0
    file = json.load(open(mission_data, 'rb'))
    waypoints = []
    boundarypoints = []
    obstacles = []
    for waypoint in file["waypoints"]:
            waypoints += [[waypoint["latitude"],
                                waypoint["longitude"], waypoint["altitude"]]]

    for boundarypoint in file['flyZones'][0]['boundaryPoints']:
        boundarypoints += [[boundarypoint["latitude"],
                            boundarypoint["longitude"]]]
    boundarypoints.append(list(boundarypoints[0]))

    for obstacle in file["stationaryObstacles"]:
        obstacles += [[obstacle["latitude"],
                        obstacle["longitude"], obstacle["radius"]]]
    map = Map(resolution, mission_data, buffer)
    valid = []
    for x in range(len(map.obstacle_map)):
        for y in range(len(map.obstacle_map[x])):
            if map.obstacle_map[x][y]:
                valid.append([x, y])
    fig, ax = plt.subplots()

    for node in valid:
        plt.plot(node[0], node[1], '.k')
    plt.grid(True)
    plt.axis("equal")
    plt.show()

if __name__ == "__main__":
    main()    
    
