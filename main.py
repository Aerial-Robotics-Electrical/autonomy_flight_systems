import dronekit_sitl, dronekit, time
from dronekit import LocationGlobalRelative, connect, Vehicle
from route import Route
from plane_commands import PlaneCommand
from map_route import MapRoute

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

route = Route(WAYPOINT_FILE_PATH)

"""
Use the following if you are not running a simulator:
sitl = dronekit_sitl.start_default(40.371338, -86.863988)
connection_string = sitl.connection_string()
"""

# Connect to the Vehicle.
print("Connecting to vehicle on: {connect}".format(connect = CONNECTION_STRING))
vehicleConnection = connect(CONNECTION_STRING, wait_ready = True)

plane = PlaneCommand(vehicleConnection)
printStateData(plane.vehicle)

if (plane.vehicle.armed != True and plane.vehicle.mode.name != 'GUIDED'):
    plane.arm()
    plane.takeoff(TARGET_ALTITUDE)
else:
    plane.vehicle.mode = dronekit.VehicleMode("GUIDED")
    plane.takeoff(TARGET_ALTITUDE)

while True:
    print(" Altitude: {altitude}".format(altitude = plane.vehicle.location.global_relative_frame.alt))
    #print(" Mode: {mode}".format(mode=plane.vehicle.mode.name))

    #Break and return from function just below target altitude.
    if (plane.vehicle.location.global_relative_frame.alt >= TARGET_ALTITUDE * 0.95):
        print("Reached target altitude")
        break
    time.sleep(.5)

target_location = route.generateWaypoint(plane, [TARGET_LATITUDE, TARGET_LONGITUDE, TARGET_ALTITUDE])
plane.vehicle.simple_goto(target_location)
# or plane.vehicle.simple_goto(route.currentDest) if you want to use the waypoint in the object

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

#Map the data
new_map = MapRoute(MAP_PATH)
new_map.create_dataframe(flight_data)
new_map.create_boundary_box()
new_map.create_and_show_plt

# Close vehicle object before exiting script
plane.vehicle.close()

# Shut down simulator
# sitl.stop()

print("Completed")
