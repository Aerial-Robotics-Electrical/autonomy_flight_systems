#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
© Copyright 2015-2016, 3D Robotics.
mission_basic.py: Example demonstrating basic mission operations including creating, clearing and monitoring missions.

Full documentation is provided at http://python.dronekit.io/examples/mission_basic.html
"""
from __future__ import print_function

from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command
import time
import math
from pymavlink import mavutil
import threading


#Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Demonstrates basic mission operations.')
parser.add_argument('--connect', 
                   help="vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
sitl = None


#Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()


# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)


def supply_mission_command(conn, name , m):
    print("Got  request for mission item: %s" % (str(m),))

    vehicle.add_message_listener('MISSION_ACK', check_mission_commands)
    vehicle.add_message_listener('MISSION_REQUEST', supply_mission_command)

    loc = vehicle.location.global_relative_frame
#    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, 10)) # ignored!
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, loc.lat+1, loc.lon, 10)) # ignored

    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, loc.lat, loc.lon, 10))
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, loc.lat+0.01, loc.lon, 10))
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_LOITER_UNLIM, 0, 0, 0, 0, 0, 0, loc.lat+0.01, loc.lon, 10))

    print(" Upload new commands to vehicle")
    cmds.upload()


mav_lock = threading.Lock() # FIXME; move locking into MAVSystem













def arm_and_takeoff(vehicle, aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Taking off!")
    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print("Arming motors")
        mav_lock.acquire()
        vehicle.armed = True
        mav_lock.release()
        time.sleep(0.5)

    # set mode to auto
    while vehicle.mode != 'AUTO':
        print("Setting mode AUTO")
        mav_lock.acquire()
        vehicle.mode = VehicleMode("AUTO")
        mav_lock.release()
        time.sleep(0.5)

    global takeoff_complete
    # wait for the vehicle to finish takeoff:
    takeoff_complete = False
    def wait_for_takeoff(conn, name, m):
        global takeoff_complete
        print("Got message: %s" % (str(m),))
        if m.text.find("Takeoff complete") != -1:
            print("Found it")
            takeoff_complete = True

    vehicle.add_message_listener('STATUSTEXT', wait_for_takeoff)
    print("Waiting for takeoff-complete")
    while not takeoff_complete:
        time.sleep(0.1)

    print("Takeoff is complete")







def watch_things_for_a_while(duration=30):
    start = time.time()

    while time.time() - start < duration:
        for i in range(0,len(vehicles)):
            vehicle = vehicles[i]
            print("Vehicle %d (%s) Lat=%f Lon=%f Alt=%f MODE=%s Hdg=%f" % (target_systems[i], vehicle.mode, vehicle.location.global_frame.lat, vehicle.location.global_frame.lon, vehicle.location.global_relative_frame.alt, str(vehicle.mode), vehicle.heading))
time.sleep(1)












