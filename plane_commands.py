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
        if abs(target_location[0] - lat) < .0003 and abs(target_location[1] - lon) < 0.0003:
            return True
        else:
            return False
    
    def load_command_sequence(self, mission):
        """
        Take the command sequence of hte mission and upload to Mavlink.

        Input: Mission object

        Output: None
        """
        print("Preparing commands to be uploaded")
        cmds = self.vehicle.commands
        cmds.clear()
        for command in mission.command_sequence:
            cmds.add(command)
        cmds.upload()
    
    def record_flight_data(self, mission, flight_data):
        """
        Monitor the route, checking to see whether we are at the
        waypoint on the route. Until we are, record the flight data
        so we can plot it on a map.

        Input: Current mission, Vehicle object and flight data dictionary.

        Output: Prints message confirming mission completed.

        This will, in the future, send a message to main that route is completed.
        """
        for i, waypoint in enumerate(mission.primary_route):
            # Ignore the first waypoint, as it is required only for loading
            # the command sequence.
            if i > 1:
                current_location = self.vehicle.location.global_relative_frame
                while not self.confirm_waypoint(waypoint, current_location.lat, current_location.lon):
                    current_location = self.vehicle.location.global_relative_frame
                    print(" Altitude: %s" % current_location.alt)
                    print(" Latitude: {lat}: Longitude: {lon}".format(lat=current_location.lat, lon=current_location.lon))
                    print(" Grond Speed: {speed}".format(speed=self.vehicle.groundspeed))
                    flight_data['latitude'].append(current_location.lat)
                    flight_data['longitude'].append(current_location.lon)
                    flight_data['ground_speed'].append(self.vehicle.groundspeed)
                    time.sleep(.5)
                print("\n Reached waypoint number: {number} \n".format(number= i + 1))
        print("All waypoints reached. Returning to base.")