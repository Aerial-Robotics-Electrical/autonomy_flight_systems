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
        MISSION_TYPES = ['infil', 'exfil',
                         'waypoint_flight', 'ISR', 'drop', 'avoid']
        self.mavlink_commands = {"Takeoff": mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
                                 "Waypoint": mavutil.mavlink.MAV_CMD_NAV_WAYPOINT}
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
                intermediate_waypoint_list = self.breakWaypoints(
                    waypoint, self.initial_waypoint_list[i + 1])
                self.primary_route = self.primary_route + intermediate_waypoint_list
            except IndexError:
                pass

    def add_take_off_command(self):
        """
        Utilize the first waypoint in the initial waypoint list to allow
        plane to takeoff properly. The first point in the infil route will always
        be designated as the takeoff route. For the command sequence, the first point
        is always ignored so we add a basic point as the first point. We then repeat that
        point for takeoff

        input: Mission ojbect

        output: Boolean flag to assert that the takeoff command is added.
        """
        first_waypoint = self.initial_waypoint_list[0]
        self.command_sequence.append(self.create_command(
            first_waypoint, self.mavlink_commands["Waypoint"]))
        self.command_sequence.append(self.create_command(
            first_waypoint, self.mavlink_commands["Takeoff"]))
        return True

    def build_mission_command_sequence(self):
        """
        For any route generated by a mission, convert all waypoints into commands
        to upload to the simulator.

        Input: None

        Output: Mission command sequence generated and saved to object.
        """
        for i, waypoint in enumerate(self.primary_route):
            if i > 1:
                self.command_sequence.append(self.create_command(
                    waypoint, self.mavlink_commands["Waypoint"]))

    def create_command(self, waypoint, mav_link_command):
        """
        Generate a Mavlink command.

        Input: Waypoint, mavlink command.

        Output: DroneKit command object.

        """
        return Command(0, 0, 0,
                       mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                       mav_link_command,
                       0, 0, 0, 0, 0, 0,
                       waypoint["latitude"], waypoint["longitude"], waypoint["altitude"])

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
                                 "altitude": self.generateStep(stepNumber, waypointOne["altitude"], waypointTwo["altitude"], breakAmount)})

        return waypointList

    def generateStep(self, stepNumber, paramPointOne, paramPointTwo, breakAmount):
        return paramPointOne + round((stepNumber * (paramPointTwo - paramPointOne) / float(breakAmount)), 8)


if __name__ == '__main__':
    file = open('waypoints.json', 'rb')
    waypoint_list = json.loads(file.read())
    print(type(waypoint_list))
    print(waypoint_list)
    mission_1 = Mission(
        waypoint_list["waypoints"], mission_type='regular_flight', takeoff_required=True)
    print(mission_1.initial_waypoint_list)
    mission_1.generate_intermediate_waypoints()
    print(mission_1.primary_route)
    mission_1.add_take_off_command()
    print(mission_1.command_sequence[0])
    mission_1.build_mission_command_sequence()
    print(mission_1.command_sequence)
    print(mission_1.command_sequence[1])
