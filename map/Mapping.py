import json
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import math
import numpy as np
 
class Map:
    """
    Class that uses Json file path of boundaries and obstacles
    to create a environment space
    """
    def __init__(self, resolution, boundarypoints, obstacles, buffer):
        """
        Initialize grid map for a star planning

        resolution: grid resolution [m]
        boundarypoints: list of points that make up a polygonal fence
        obstacles: list of points and respective radiuses 
        buffer: buffer around obstacles
        """ 

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
    mission_data = "interop_example.json"
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
    map = Map(resolution, boundarypoints, obstacles, buffer)
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
    
