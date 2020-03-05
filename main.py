import dronekit_sitl, dronekit, time
from dronekit import LocationGlobalRelative, connect, Vehicle
from route import Route
from plane_commands import PlaneCommand
from map_route import MapRoute
from mission import Mission
import json

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
TARGET_ALTITUDE = 30
TARGET_LATITUDE = 40.373434
TARGET_LONGITUDE = -86.866277
CONNECTION_STRING = 'tcp:127.0.0.1:5760'

<<<<<<< HEAD
route = Route(WAYPOINT_FILE_PATH)

"""
Use the following if you are not running a simulator:
sitl = dronekit_sitl.start_default(40.371338, -86.863988)
connection_string = sitl.connection_string()
"""
=======
def printStateData(vehicle):
    print("Get some vehicle attribute values:")
    print(" GPS: %s" % vehicle.gps_0)
    print(" Battery: %s" % vehicle.battery)
    print(" Last Heartbeat: %s" % vehicle.last_heartbeat)
    print(" Is Armable?: %s" % vehicle.is_armable)
    print(" System status: %s" % vehicle.system_status.state)
    print(" Mode: %s" % vehicle.mode.name)
        
# Start the dronekit-sitl plane simulator utilizing the following command:
# dronekit-sitl ./../ardupilot/build/sitl/bin/arduplane --home=lat,lon,altitude,heading(yaw) --model=plane 
>>>>>>> Add in missions. Set up sitl for param testing

# Connect to the Vehicle.
print("Connecting to vehicle on: {connect}".format(connect = CONNECTION_STRING))
vehicleConnection = connect(CONNECTION_STRING, wait_ready = True)

plane = PlaneCommand(vehicleConnection)
printStateData(plane.vehicle)

<<<<<<< HEAD
if (plane.vehicle.armed != True and plane.vehicle.mode.name != 'GUIDED'):
=======
# Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
        #  after Vehicle.simple_takeoff will execute immediately).

printStateData(plane.vehicle)

file = open(WAPOINT_FILE_PATH, 'rb')
waypoint_list = json.loads(file.read())

mission_1 = Mission(waypoint_list["waypoints"], 'infil', takeoff_required=True)
mission_1.generate_intermediate_waypoints()
mission_1.add_take_off_command()
print(mission_1.command_sequence[0])
mission_1.build_mission_command_sequence()

if plane.vehicle.armed != True and plane.vehicle.mode.name != 'AUTO':
    plane.load_command_sequence(mission_1)
>>>>>>> Add in missions. Set up sitl for param testing
    plane.arm()
    time.sleep(0.5)
    print(plane.vehicle.mode.name)
    print(plane.vehicle.armed)
    cmds = plane.vehicle.commands
    for command in cmds:
        print(command)
else:
    exit

while True:
    print(" Altitude: {altitude}".format(altitude = plane.vehicle.location.global_relative_frame.alt))
    #print(" Mode: {mode}".format(mode=plane.vehicle.mode.name))

    #Break and return from function just below target altitude.
    if (plane.vehicle.location.global_relative_frame.alt >= TARGET_ALTITUDE * 0.95):
        print("Reached target altitude")
        break
    time.sleep(.5)

flight_data = {'latitude': [], 'longitude': []}
target_reached = False
start_time = time.time()

#Loop while the plane is in route...
while target_reached == False:
    #Record location data of the aircraft
    current_location = plane.vehicle.location.global_relative_frame
    print(" Altitude: {alt}".format(alt = current_location.alt))
    print(" Latitude: {lat}: Longitude: {lon}".format(lat=current_location.lat, lon=current_location.lon))
    flight_data['latitude'].append(current_location.lat)
    flight_data['longitude'].append(current_location.lon)

    #Break and return from loop just below target altitude.
    if plane.confirm_waypoint(route.currentDest, current_location.lat, current_location.lon):
        print("Reached target")
        end_time = time.time()
        target_reached = True

    time.sleep(.5)

#Determining travel time
total_time = end_time - start_time
minutes = total_time / 60
seconds = total_time - (minutes * 60)
print("Total Route Time: {mins}:{secs}".format(mins = round(minutes, 4), secs = round(seconds, 4)))

<<<<<<< HEAD
#Map the data
new_map = MapRoute(MAP_PATH)
new_map.create_dataframe(flight_data)
new_map.create_boundary_box()
new_map.create_and_show_plt
=======
printStateData(plane.vehicle)
>>>>>>> Add in missions. Set up sitl for param testing

# Close vehicle object before exiting script
plane.vehicle.close()

# Shut down simulator
# sitl.stop()

print("Completed")
