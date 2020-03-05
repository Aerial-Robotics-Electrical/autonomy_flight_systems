# Autonomy Flight Systems

Flight Control Software for the IEEE Aerial Robotics team.

## System Architecture

The primary structure of our flight system revolves around the PixHawk 4 and Raspberry Pi 4, acting in tandem as a flight controller and flight control unit respectively. Please view the diagram below for a visual representation of the full system.

## Primary Features

1. Autonomous flight given GPS waypoint coordinates with a tolerance of less then 100 feet radially from the given GPS point.
2. Automatic detection and deconfliction with other aircraft.
3. Autonomous routing around objects within the specified mission area. (Currently seen as cylinders of infinite height and radial distance for UAS competition)
4. Autonomous search algorithm with ability to avoid objects on map. (Augmentation of point 3)

## Set Up

To begin working with the Flight Control system, please perform the following steps:

1. Clone this repository using: `git clone https://github.com/Aerial-Robotics-Electrical/autonomy_flight_systems.git`
2. Install the necessary dependencies utilizing virtualenv or conda environments.
  a. For VirutalEnv, perform the following steps:
    1. Install virutalenv using `pip install virutalenv`
    2. Create a new virutal environment with `virtualenv name_of_env`. This will create the virtual environment.
    3. Once, installed, please go to the document called `requirements.txt` and utilize pip to install all packages.
  b. For Conda, perform the following steps:
    1. Create a conda environment by utilizing `conda create --name myenv --python=2.7`. Please ensure you do this using Python 2.7!
    2. Install all requirements in `requirements.txt` using Pip or conda package installer.
3. Clone ArduPilots repository (the main one that houses ArduPlane) from the GitHub page [here](https://github.com/ArduPilot/ardupilot).
4. Follow directions for your development environment for creating the ArduPlane binaries, which must be compiled on your own computer. Remember the path where you save this information! [Documentation for building Plane](https://ardupilot.org/dev/docs/building-the-code.html)
5. Run the simulator using the following command: `dronekit-sitl .PATH_TO_ARDUPILOT/ardupilot/build/sitl/bin/arduplane --home=lat,lon,altitude,heading(yaw) --model=plane --defaults PATH_TO_THIS_REPOSITORY/plane.param`
6. Run the main python script to activate the plane and fly a mission.

## Testing
Each class shown in this repository has separate unit tests. Please utilize these unit tests when developing for the ground station.
