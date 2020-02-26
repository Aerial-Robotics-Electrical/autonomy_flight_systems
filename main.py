import dronekit_sitl, dronekit, time
from dronekit import LocationGlobal
from route import Route
from connection import PlaneCommand
from map_route import MapRoute

WAPOINT_FILE_PATH = 'waypoints.json'
MAP_PATH = '/Users/tyler/Desktop/lafayette_map_2.png'
TARGET_ALTITUDE = 30
TARGET_LATITUDE = 40.373434
TARGET_LONGITUDE = -86.866277

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
sitl = dronekit_sitl.start_default(40.371338, -86.863988)
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

if plane.vehicle.armed != True and plane.vehicle.mode.name != 'GUIDED':
    plane.arm()
    plane.takeoff(TARGET_ALTITUDE)
else:
    plane.vehicle.mode = dronekit.VehicleMode("GUIDED")
    plane.takeoff(TARGET_ALTITUDE)

while True:
    print(" Altitude: %s" % plane.vehicle.location.global_relative_frame.alt)
    # print(" Mode: {mode}".format(mode=plane.vehicle.mode.name))
    #Break and return from function just below target altitude.
    if plane.vehicle.location.global_relative_frame.alt>=TARGET_ALTITUDE*0.95:
        print("Reached target altitude")
        break
    time.sleep(.5)

target_location = route.generateWaypoint(plane, [TARGET_LATITUDE, TARGET_LONGITUDE, TARGET_ALTITUDE])
plane.vehicle.simple_goto(route.currentDest)
# or plane.vehicle.simple_goto(target_location) if you want to save the waypoint locally in main.py

flight_data = {'latitude': [], 'longitude': []}

target_reached = False
start_time = time.time()
while target_reached == False:
    current_location = plane.vehicle.location.global_relative_frame
    print(" Altitude: %s" % current_location.alt)
    print(" Latitude: {lat}: Longitude: {lon}".format(lat=current_location.lat, lon=current_location.lon))
    flight_data['latitude'].append(current_location.lat)
    flight_data['longitude'].append(current_location.lon)
    #Break and return from function just below target altitude.
    if plane.confirm_waypoint(route.currentDest, current_location.lat, current_location.lon):
        print("Reached target")
        end_time = time.time()
        target_reached = True
    time.sleep(.5)

total_time = end_time - start_time
minutes = total_time / 60
seconds = total_time - (minutes * 60)
print("Total Route Time: {mins}:{secs}".format(mins=round(minutes, 4), secs=round(seconds, 4)))

new_map = MapRoute(MAP_PATH)
new_map.create_dataframe(flight_data)
new_map.create_boundary_box()
new_map.create_and_show_plt

#printStateData(plane.vehicle)

# Close vehicle object before exiting script
plane.vehicle.close()

# Shut down simulator
# sitl.stop()
print("Completed")