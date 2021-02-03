import json
import matplotlib.pyplot as plt
import numpy as np
import math
import time
from Mapping import Map

class PathPlanner:
    """
    resolution: float meters between each vertex in the cardinal directions
    mission_data: string path of json file of mission data
    buffer: float length of safety "buffer" around obstacles

    """
    def __init__(self, resolution, mission_data, buffer):
        file = json.load(open(mission_data, 'rb'))
        self.waypoints = []
        boundarypoints = []
        obstacles = []
        for waypoint in file["waypoints"]:
                self.waypoints += [[waypoint["latitude"],
                                    waypoint["longitude"], waypoint["altitude"]]]

        for boundarypoint in file['flyZones'][0]['boundaryPoints']:
            boundarypoints += [[boundarypoint["latitude"],
                                boundarypoint["longitude"]]]
        boundarypoints.append(list(boundarypoints[0]))

        for obstacle in file["stationaryObstacles"]:
            obstacles += [[obstacle["latitude"],
                            obstacle["longitude"], obstacle["radius"]]]

        self.map = Map(resolution, boundarypoints, obstacles, buffer)
        self.motion = [[1, 0, 1],                  # [x direction, y direction, cost]
                        [0, 1, 1],
                        [-1, 0, 1],
                        [0, -1, 1],
                        [-1, -1, math.sqrt(2)],
                        [-1, 1, math.sqrt(2)],
                        [1, -1, math.sqrt(2)],
                        [1, 1, math.sqrt(2)]]
        self.path = {"waypoints": []}               # dict to dump final waypoints

        
    class Node:
        def __init__(self, x, y, cost, parent_index):
            self.x = x
            self.y = y
            self.cost = cost
            self.parent_index = parent_index

    def calc_distance(self, gnode, snode):
        distance1 = math.hypot(gnode.x - snode.x, gnode.y - snode.y)
        return distance1

    def calc_grid_index(self, node):
        return (node.y) * self.map.map_x_width + (node.x)

    def a_star(self, sx, sy, gx, gy):        
        snode =  self.Node(round(self.map.transform_to_map_index(sx)), round(self.map.transform_to_map_index(sy)), 0.0, -1)
        gnode = self.Node(round(self.map.transform_to_map_index(gx)), round(self.map.transform_to_map_index(gy)), 0.0, -1)
        open_set, closed_set = dict(), dict()
        open_set[self.calc_grid_index(snode)] = snode
        rough_path_x = []
        rough_path_y = []
        while 1:
            if len(open_set) == 0:
                print("something went wrong")
                break
            current_id = min(open_set, key = lambda o: open_set[o].cost + self.calc_distance(gnode, open_set[o])) # finds the open node with lowest cost
            current = open_set[current_id]
            
    # uncomment to plot a star algorithm
            # plt.plot(current.lat, current.lon, "xc")
            # plt.gcf().canvas.mpl_connect('key_release_event',
            #                                 lambda event: [exit(
            #                                     0) if event.key == 'escape' else None])
            # if len(closed_set.keys()) % 10 == 0:
            #     plt.pause(0.001)
            
            if current.x == gnode.x  and current.y == gnode.y:
                gnode.parent_index = current.parent_index
                gnode.cost = current.cost
                break
            del open_set[current_id]
            closed_set[current_id] = current    # moves current node to closed set
            for i in range(len(self.motion)):
                node = self.Node(current.x + self.motion[i][0],
                                 current.y + self.motion[i][1],
                                 current.cost + self.motion[i][2], current_id)
                new_id = self.calc_grid_index(node)
                if not self.verify_node(node):
                    continue
                if new_id in closed_set:
                    continue
                if new_id not in open_set:
                    open_set[new_id] = node
                else:
                    if open_set[new_id].cost > node.cost:
                        open_set[new_id] = node

        rough_path_x.append(self.map.transform_to_cart_position(gnode.x))
        rough_path_y.append(self.map.transform_to_cart_position(gnode.y))
        parent_index = gnode.parent_index
        
        while parent_index != -1:
            node = closed_set[parent_index]
            rough_path_x.append(self.map.transform_to_cart_position(node.x))
            rough_path_y.append(self.map.transform_to_cart_position(node.y))
            parent_index = node.parent_index
        rough_path_x[0] = gx
        rough_path_x[len(rough_path_x) - 1] = sx
        rough_path_y[0] = gy
        rough_path_y[len(rough_path_y) - 1] = sy
        return rough_path_x, rough_path_y
    
    def calc_path(self, swaypoint, gwaypoint):
        alt = []
        startx, starty = self.map.decimal_to_cartesian(swaypoint[0], swaypoint[1], self.map.min_lat, self.map.min_lon)
        goalx, goaly = self.map.decimal_to_cartesian(gwaypoint[0], gwaypoint[1], self.map.min_lat, self.map.min_lon)
        rx, ry = self.a_star(startx, starty, goalx, goaly) 
        cx, cy = self.calc_critical_nodes(rx,ry)
        fx, fy = self.calc_smooth_line(cx, cy)
        fx.reverse()
        fy.reverse()

    # uncomment to plot paths
        # plt.plot(rx,ry, '-r')
        # plt.plot(cx,cy, '.b')
        # plt.plot(fx, fy, 'g-s')

        pitch = self.calc_pitch(swaypoint[2], gwaypoint[2], fx, fy)
        alt.append(swaypoint[2])
        for i, (x,y) in enumerate(zip(fx, fy)):
            if i > 0:
                alt.append(self.calc_altitude(pitch, fx[i - 1], fy[i-1], x, y, alt[i - 1]))
                
        for i, (x,y) in enumerate(zip(fx, fy)):    
            fx[i], fy[i] = self.map.cartesian_to_decimal(x, y, self.map.min_lat, self.map.min_lon)
        if len(self.path['waypoints']) > 0:
            fx.pop(0)
            fy.pop(0)
            alt.pop(0)
        for i in range(len(fx)):
            self.path['waypoints'].append({'latitude': fx[i], 'longitude': fy[i], 'altitude': alt[i]})
        return fx, fy       

    def verify_node(self, node):
        px = self.map.transform_to_cart_position(node.x)
        py = self.map.transform_to_cart_position(node.y)
        if px <= 0: 
            return False
        elif py <= 0:
            return False
        elif px >= self.map.cart_max_x:
            return False
        elif py >= self.map.cart_max_y:
            return False
        if self.map.obstacle_map[node.x][node.y]:
            return False
        return True
    
    def calc_pitch(self, startalt, goalalt, fx, fy):
        dalt = goalalt - startalt
        x = np.diff(fx)
        y = np.diff(fy)
        distance = 0
        for dx, dy in zip(x,y):
            distance += math.hypot(dx, dy)
        return math.atan(dalt / distance)
    
    def calc_altitude(self, pitch, sx, sy, gx, gy, startalt):
        dx = gx - sx
        dy = gy -sy
        return round(math.hypot(dx,dy) * math.tan(pitch),2) + startalt

    def calc_critical_nodes(self, xlist, ylist):
        criticalx = []
        criticaly = []
        m = np.diff(ylist)/np.diff(xlist)    
        for i in range(m.size):
            if(i  == 0):
                criticalx.append(xlist[i])
                criticaly.append(ylist[i])
                continue
            if(m[i] != m[i-1]):
                criticalx.append(xlist[i])
                criticaly.append(ylist[i])
        criticalx.append(xlist[len(xlist) - 1])
        criticaly.append(ylist[len(ylist) - 1])                
        return criticalx, criticaly

    def verify_line_obstacle(self, x1, y1, x2, y2):
        mx = float((x2 - x1) / 100)
        my = float((y2 - y1) / 100)

        for t in range(0,100):
            x = int(self.map.transform_to_map_index(int(round(mx * t)) + x1))
            y = int(self.map.transform_to_map_index(int(round(my * t)) + y1, ))

            if self.map.obstacle_map[x][y] == True:
                return True
        return False
    
    def calc_smooth_line(self, criticalx, criticaly):
        finalx = []
        finaly = []
        current = 0
        while current < len(criticalx):
            finalx.append(criticalx[current])
            finaly.append(criticaly[current])
            for check in range(current + 1, len(criticalx)):
                if(self.verify_line_obstacle(criticalx[current], criticaly[current], criticalx[check], criticaly[check])):
                    current = check - 1 
                    break
                elif(check == len(criticalx) - 1):
                    current = len(criticalx)
        finalx.append(criticalx[len(criticalx) - 1])
        finaly.append(criticaly[len(criticaly) - 1])
        return finalx, finaly
    
    def dump_path(self):
        with open("routepath.json", "w") as file:
            json.dump(self.path, file)

def main():
    mission_data = 'interop_example.json'
    resolution = 10
    buffer = 10
    plan = PathPlanner(resolution, mission_data, buffer)

# uncomment to plot cartesian map
    # invalid = []
    # for x in range(len(plan.map.obstacle_map)):
    #     for y in range(len(plan.map.obstacle_map[x])):
    #         if plan.map.obstacle_map[x][y]:
    #             invalid.append([plan.map.transform_to_cart_position(x), plan.map.transform_to_cart_position(y)])
    # for node in invalid:
    #     plt.plot(node[0], node[1], '.k')
    # plt.grid(True)
    # plt.axis("equal")
    start_time = time.time();
    for i, waypoint in enumerate(plan.waypoints):
        try:
            plan.calc_path(plan.waypoints[i], plan.waypoints[i+1])
        except IndexError:
            pass
    print(f"time taken: {time.time() - start_time}")
    plan.dump_path()
    plt.show()


if __name__ == "__main__":
    main()

            

    