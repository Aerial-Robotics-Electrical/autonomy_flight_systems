from mission import Mission
from dronekit import Command
from pymavlink import mavutil
import unittest
import json

class TestMissionMethods(unittest.TestCase):
    def setUp(self):
        waypoint_dict = open('waypoints_test.json', 'rb')
        waypoint_list = json.loads(waypoint_dict.read())
        self.mission = Mission(waypoint_list["waypoints"], mission_type='regular_flight', takeoff_required=True)

    def test_intermidate_waypoint_generation(self):
        self.mission.generate_intermediate_waypoints()
        self.assertEqual(10, len(self.mission.primary_route))
    
    def test_take_off_command_added(self):
        first_waypoint = self.mission.initial_waypoint_list[0]
        self.mission.add_take_off_command()
        self.assertEqual(self.mission.command_sequence[1], Command(0,0,0,      
                                                            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                                                            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
                                                            0, 0, 0, 0, 0, 0,
                                                            first_waypoint["latitude"], first_waypoint["longitude"], first_waypoint["altitude"]))
    
    def test_command_sequence_generation(self):
        self.mission.generate_intermediate_waypoints()
        self.mission.add_take_off_command()
        self.mission.build_mission_command_sequence()
        self.assertEqual(10, len(self.mission.command_sequence))
        self.assertEqual(self.mission.command_sequence[9].x, 37.443188)
        self.assertEqual(self.mission.command_sequence[9].y, -95.5827334)
        self.assertEqual(self.mission.command_sequence[9].z, 25)
        self.assertEqual(self.mission.command_sequence[9].command, 16)


if __name__ == '__main__':
    unittest.main()