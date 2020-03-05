# Commands for the Plane simulator

import time
import dronekit

class PlaneCommand:
    def __init__(self, vehicleConnection):
        self.vehicle = vehicleConnection
        self.retry_max = 10


    def arm(self):
        print("Basic pre-arm checks")

        # Don't try to arm until autopilot is ready
        while not self.vehicle.is_armable:
            print(" Waiting for connection to initialise...")
            time.sleep(1)

        print("Arming motors")
        self.vehicle.mode = dronekit.VehicleMode("AUTO")
        self.vehicle.armed = True
        
        # Confirm vehicle armed before attempting to take off
        while not self.vehicle.armed:
            print(" Waiting for arming...")
            time.sleep(1)
        
        return True
    
    def confirm_waypoint(self, target_location, lat, lon):
        if abs(target_location.lat - lat) < .0003 and abs(target_location.lon - lon) < 0.0003:
            return True
        
    def takeoff(self):
        print("Taking off!")
        self.vehicle.mode = dronekit.VehicleMode("AUTO")
    
    def load_command_sequence(self, mission):
        print("Preparing commands to be uploaded")
        cmds = self.vehicle.commands
        cmds.clear()
        for command in mission.command_sequence:
            cmds.add(command)
        cmds.upload()   