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
        self.assertEqual(self.mission.command_sequence[0], Command(0,0,0,      
                                                            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                                                            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
                                                            0, 0, 0, 0, 0, 0,
                                                            first_waypoint[0], first_waypoint[1], first_waypoint[2]))
    
    def test_command_sequence_generation(self):
        self.mission.generate_intermediate_waypoints()
        self.mission.add_take_off_command()
        self.mission.build_mission_command_sequence()
        self.assertEqual(10, len(self.mission.command_sequence))
        self.assertEqual(self.mission.command_sequence[9], Command(0,0,0,      
                                                            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                                                            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                                                            0, 0, 0, 0, 0, 0,
                                                            37.443188, -95.582733, 25))


if __name__ == '__main__':
    unittest.main()