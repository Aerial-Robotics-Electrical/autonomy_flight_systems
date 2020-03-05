# Class to contain the various mission types and any support methods or classes
# for generating and maintaining a mission.

import time
from dronekit import Command
from pymavlink import mavutil
import math
import uuid
import json
from route import Route

class Mission:
    def __init__(self, waypoint_list, mission_type, connection=None, takeoff_required=False):
        MISSION_TYPES = ['infil', 'exfil', 'waypoint_flight', 'ISR', 'drop', 'avoid']
        self.connection = connection
        self.initial_waypoint_list = waypoint_list
        self.mission_type = mission_type
        self.mission_id = uuid.uuid1()
        self.primary_route = list()
        self.command_sequence = list()
        self.takeoff_required = takeoff_required
    
    def generate_intermediate_waypoints(self):
        """
        Take a list of waypoints given for a particular mission and break up
        each waypoint section into 10 additional waypoints.

        Input: Mission object

        Output: Appended list of missions
        """
        for i, waypoint in enumerate(self.initial_waypoint_list):
            try:
                route = Route()
                intermediate_waypoint_list = route.breakWaypoints(waypoint, self.initial_waypoint_list[i + 1])
                self.primary_route = self.primary_route + intermediate_waypoint_list
            except Exception as error:
                print(error)
    
    def add_take_off_command(self):
        """
        Utilize the first waypoint in the initial waypoint list to allow
        plane to takeoff properly. The first point in the infil route will always
        be designated as the takeoff route.

        input: Mission ojbect

        output: Boolean flag to assert that the takeoff command is added.
        """
        first_waypoint = self.initial_waypoint_list[0]
        take_off_command = Command(0,0,0,      
                                   mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                                   mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
                                   0, 0, 0, 0, 0, 0,
                                   first_waypoint[0], first_waypoint[1], first_waypoint[2])
        self.command_sequence.append(take_off_command)
        return True
    
    def build_mission_command_sequence(self):
        for i, waypoint in enumerate(self.primary_route):
            if i > 0:
                self.command_sequence.append(Command(0,0,0,      
                                             mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                                             mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                                             0, 0, 0, 0, 0, 0,
                                             waypoint[0], waypoint[1], waypoint[2]))


if __name__ == '__main__':
    file = open('waypoints.json', 'rb')
    waypoint_list = json.loads(file.read())
    print(type(waypoint_list))
    print(waypoint_list)
    mission_1 = Mission(waypoint_list["waypoints"], mission_type='regular_flight', takeoff_required=True)
    print(mission_1.initial_waypoint_list)
    mission_1.generate_intermediate_waypoints()
    print(mission_1.primary_route)
    mission_1.add_take_off_command()
    print(mission_1.command_sequence[0])
    mission_1.build_mission_command_sequence()
    print(mission_1.command_sequence)
