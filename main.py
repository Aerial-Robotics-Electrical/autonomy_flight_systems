# import dronekit_sitl, dronekit, time
# from dronekit import LocationGlobalRelative, connect, Vehicle
from mavsdk import System
# from route import Route
# from plane_command import PlaneCommand
# from map_route import MapRoute
# from mission import Mission
import json
import csv
import numpy as np


def printStateData(vehicle):
    print("Get some vehicle attribute values:")
    print(" GPS: {gps}".format(gps = vehicle.gps_0))
    print(" Battery: {bat}".format(bat = vehicle.battery))
    print(" Last Heartbeat: {time}".format(time = vehicle.last_heartbeat))
    print(" Is Armable?: {arm}".format(arm = vehicle.is_armable))
    print(" System status: {state}".format(state = vehicle.system_status.state))
    print(" Mode: {mode}".format(mode = vehicle.mode.name))
    print(" Ground Speed: {v}".format(v = vehicle.groundspeed))
    print(" Heading: {h}".format(h = vehicle.heading))


def create_flight_data_log(flight_data, file_name):
    with open(file_name + '.csv', 'w') as f:
        for key in flight_data.keys():
            f.write("%s\t"%(key))
        f.write("\n")
        for lat, lon, speed in zip(flight_data['latitude'], flight_data['longitude'], flight_data['ground_speed']):
            f.write("%s\t%s\t%s"%(lat, lon, speed))
            f.write("\n")


import asyncio
from mavsdk import System


async def run():

    drone = System()
    await drone.connect()

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Drone discovered with UUID: {state.uuid}")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            print("Global position estimate ok")
            break

    print("-- Arming")
    await drone.action.arm()

    print("-- Taking off")
    await drone.action.takeoff()

    await asyncio.sleep(5)

    print("-- Landing")
    await drone.action.land()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())