import dronekit_sitl, dronekit, time
from route import Route
from connection import PlaneCommand

WAPOINT_FILE_PATH = 'waypoints.json'
TARGET_ALTITUDE = 20

def printStateData(vehicle):
    print("Get some vehicle attribute values:")
    print(" GPS: %s" % vehicle.gps_0)
    print(" Battery: %s" % vehicle.battery)
    print(" Last Heartbeat: %s" % vehicle.last_heartbeat)
    print(" Is Armable?: %s" % vehicle.is_armable)
    print(" System status: %s" % vehicle.system_status.state)
    print(" Mode: %s" % vehicle.mode.name)
        
# Starting the flight simulator
print("Start simulator (SITL)")
# sitl.launch([])
sitl = dronekit_sitl.start_default()
connection_string = sitl.connection_string()

route = Route(WAPOINT_FILE_PATH)

# Connect to the Vehicle.
print("Connecting to vehicle on: %s" % (connection_string,))
vehicleConnection = dronekit.connect(connection_string, wait_ready=False)

plane = PlaneCommand(vehicleConnection)

printStateData(plane.vehicle)

# Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
        #  after Vehicle.simple_takeoff will execute immediately).

printStateData(plane.vehicle)

plane.arm()
plane.takeoff(TARGET_ALTITUDE)

while True:
    print(" Altitude: %s" % plane.vehicle.location.global_relative_frame.alt)
    #Break and return from function just below target altitude.
    if plane.vehicle.location.global_relative_frame.alt>=TARGET_ALTITUDE*0.95:
        print("Reached target altitude")
        break
    time.sleep(1)

printStateData(plane.vehicle)

# Close vehicle object before exiting script
plane.vehicle.close()

# Shut down simulator
# sitl.stop()
print("Completed")