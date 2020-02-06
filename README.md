# Autonomy Flight Systems

Flight Control Software for the IEEE Aerial Robotics team.

## System Architecture

The primary structure of our flight system revolves around the PixHawk 4 and Raspberry Pi 4, acting in tandem as a flight controller and flight control unit respectively. Please view the diagram below for a visual representation of the full system.

## Primary Features

1. Autonomous flight given GPS waypoint coordinates with a tolerance of less then 100 feet radially from the given GPS point.
2. Automatic detection and deconfliction with other aircraft.
3. Autonomous routing around objects within the specified mission area. (Currently seen as cylinders of infinite height and radial distance for UAS competition)
4. Autonomous search algorithm with ability to avoid objects on map. (Augmentation of point 3)
