import asyncio
import json
import csv
import numpy as np

from mavsdk.mission import (MissionItem, MissionPlan)
from mavsdk import System
from route import Route
from comp_mission import CompMission


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

async def run():

    drone = System()
    await drone.connect()

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Drone discovered with UUID: {state.uuid}")
            break
    
    with open('waypoints_test.json', 'r') as f:
        waypoints = json.load(f)
    
    print_mission_progress_task = asyncio.ensure_future(print_mission_progress(drone))

    running_tasks = [print_mission_progress_task]

    termination_task = asyncio.ensure_future(observe_is_in_air(drone, running_tasks))

    new_mission = CompMission(waypoints, "infil")
    new_mission.generate_intermediate_waypoints()

    print(len(new_mission.primary_route))

    mission_plan = MissionPlan(new_mission.primary_route)

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            print("Global position estimate ok")
            break

    await drone.mission.set_return_to_launch_after_mission(True)

    print("-- Uploading mission")
    await drone.mission.upload_mission(mission_plan)

    print("-- Arming")
    await drone.action.arm()

    print("-- Taking off")
    await drone.action.takeoff()

    print("-- Starting mission")
    await drone.mission.start_mission()

    await termination_task

    print("-- Landing")
    await drone.action.land()

async def print_mission_progress(drone):
    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: "
              f"{mission_progress.current}/"
              f"{mission_progress.total}")


async def observe_is_in_air(drone, running_tasks):
    """ Monitors whether the drone is flying or not and
    returns after landing """

    was_in_air = False

    async for is_in_air in drone.telemetry.in_air():
        if is_in_air:
            was_in_air = is_in_air

        if was_in_air and not is_in_air:
            for task in running_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            await asyncio.get_event_loop().shutdown_asyncgens()

            return

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())