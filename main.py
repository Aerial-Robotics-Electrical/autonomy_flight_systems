import dronekit_sitl, dronekit, time
from dronekit import LocationGlobalRelative, connect, Vehicle
from route import Route
from plane_commands import PlaneCommand
from map_route import MapRoute
from mission import Mission
import json
import csv

def printStateData(vehicle):
    print("Get some vehicle attribute values:")
    print(" GPS: {gps}".format(gps = vehicle.gps_0))
    print(" Battery: {bat}".format(bat = vehicle.battery))
    print(" Last Heartbeat: {time}".format(time = vehicle.last_heartbeat))
    print(" Is Armable?: {arm}".format(arm = vehicle.is_armable))
    print(" System status: {state}".format(state = vehicle.system_status.state))
    print(" Mode: {mode}".format(mode = vehicle.mode.name))
        
"""
Start the dronekit-sitl plane simulator utilizing the following command:
    dronekit-sitl ./../ardupilot/build/sitl/bin/arduplane --home=40.371338,-86.863988,0,0 --model=plane --defaults (path)
"""

WAYPOINT_FILE_PATH = 'interop_example.json'
MAP_PATH = 'resources/lafayette_map_2.png'
TARGET_ALTITUDE = 60
TARGET_LATITUDE = 40.373434
TARGET_LONGITUDE = -86.866277
CONNECTION_STRING = 'tcp:127.0.0.1:5760'
FLIGHT_DATA_FILE_NAME = 'test_flight_03_12_2020'

def printStateData(vehicle):
    print("Get some vehicle attribute values:")
    print(" GPS: %s" % vehicle.gps_0)
    print(" Battery: %s" % vehicle.battery)
    print(" Last Heartbeat: %s" % vehicle.last_heartbeat)
    print(" Is Armable?: %s" % vehicle.is_armable)
    print(" System status: %s" % vehicle.system_status.state)
    print(" Mode: %s" % vehicle.mode.name)
    print(" Ground Speed: %s" % vehicle.groundspeed)
    print(" Heading: %s" % vehicle.heading)

def create_flight_data_log(flight_data, file_name):
    with open(file_name + '.csv', 'w') as f:
        for key in flight_data.keys():
            f.write("%s\t"%(key))
        f.write("\n")
        for lat, lon, speed in zip(flight_data['latitude'], flight_data['longitude'], flight_data['ground_speed']):
            f.write("%s\t%s\t%s"%(lat, lon, speed))
            f.write("\n")
        
# Start the dronekit-sitl plane simulator utilizing the following command:
# dronekit-sitl ./../ardupilot/build/sitl/bin/arduplane --home=lat,lon,altitude,heading(yaw) --model=plane
# --defaults PATH_TO_DIRECTORY/plane.parm

# Connect to the Vehicle.
print("Connecting to vehicle on: {connect}".format(connect = CONNECTION_STRING))
vehicleConnection = connect(CONNECTION_STRING, wait_ready = True)

# Generate command menu
plane = PlaneCommand(vehicleConnection)
printStateData(plane.vehicle)

# Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
        #  after Vehicle.simple_takeoff will execute immediately).

printStateData(plane.vehicle)


file = open(WAPOINT_FILE_PATH, 'rb')
waypoint_list = json.loads(file.read())

# Generate the take-off mission
mission_1 = Mission(waypoint_list["waypoints"], 'infil', takeoff_required=True)
mission_1.generate_intermediate_waypoints()
mission_1.add_take_off_command()
mission_1.build_mission_command_sequence()

if plane.vehicle.armed != True and plane.vehicle.mode.name != 'AUTO':
    plane.load_command_sequence(mission_1)
    plane.arm()
    time.sleep(0.5)
    print(plane.vehicle.mode.name)
    print(plane.vehicle.armed)
    cmds = plane.vehicle.commands
    for command in cmds:
        print(command)
else:
    # We don't want to do anything if the vehicle is already armed.
    exit

while True:
    print(" Altitude: {altitude}".format(altitude = plane.vehicle.location.global_relative_frame.alt))
    #print(" Mode: {mode}".format(mode=plane.vehicle.mode.name))

    #Break and return from function just below target altitude.
    if (plane.vehicle.location.global_relative_frame.alt >= TARGET_ALTITUDE * 0.95):
        print("Reached target altitude")
        break
    time.sleep(.5)

flight_data = {'latitude': [], 'longitude': [], 'ground_speed': []}

start_time = time.time()
plane.record_flight_data(mission_1, flight_data)
end_time = time.time()
total_time = end_time - start_time
minutes = total_time / 60
seconds = total_time - (minutes * 60)

print("Total Route Time: {mins} mins {secs} secs".format(mins=round(minutes, 4), secs=round(seconds, 4)))


create_flight_data_log(flight_data, FLIGHT_DATA_FILE_NAME)

printStateData(plane.vehicle)

# Close vehicle object before exiting script
plane.vehicle.close()

print("Completed")
