import json
from dronekit import LocationGlobalRelative

class Route:
    """
    This class contains the methods and data used for routing the aircraft

    Expected input: mission_data - path to the .json file containing the mission data
    """
    def __init__(self, mission_data):
        self.data = json.load(open(mission_data, 'rb'))
        self.currentDest = None #This will contain a LocationGlobalRelative object for the current destination
        self.waypoints = [] #Contains the provided mission waypoints in the form of [latitude, longitude, altitude]
        self.boundarypoints = [] #Contains the provided mission boundary points in the form of [latitude, longitude]
        self.searchGridPoints = [] #Contains the provided search grid points in the form of [latitude, longitude]

        #Looping through the waypoint dicts to load GPS cords
        for waypoint in self.data["waypoints"]:
            self.waypoints += [[waypoint["latitude"], waypoint["longitude"], waypoint["altitude"]]]
        
        #Looping through the flyzone boundary dicts to load proper GPS cords
        for boundarypoint in self.data["flyZones"][0]["boundaryPoints"]:
            self.boundarypoints += [[boundarypoint["latitude"], boundarypoint["longitude"]]]

        #Looping through the search grid dict to load GPS coords
        for searchpoint in self.data["searchGridPoints"]:
            self.searchGridPoints += [[searchpoint["latitude"], searchpoint["longitude"]]]

    def generateWaypoint(self, plane, coordinate):
        """
        This will take in GPS coordinates and feed it to the drone.

        Expected input: plane (connection.py Object) - object containing the Dronekit vehicle. Used to feed the destination to the drone
            coordinate (tuple) - a tuple containing the desired ending GPS coordinates [latitude, longitude, altitude]

        Expected output: Returns a waypoint that can be fed to dronekit (sets the current destination to the provided coordinate)
        """
        self.currentDest = LocationGlobalRelative(coordinate[0], coordinate[1], coordinate[2])
        return self.currentDest

    def breakWaypoints(self, waypointOne, waypointTwo, breakAmount = 10):
        """
        This method will take in two waypoints and break it up into multiple waypoints along a line connecting the
        original two waypoints.

        Expected input: waypointOne (tuple) - a tuple containing the starting GPS coordinates [latitude, longitude, altitude]
            waypointTwo (tuple) - a tuple containing the desired ending GPS coordinates [latitude, longitude, altitude]
            breakAmount (int) - describes how many addional waypoints are wanted. By default, the function create ten extra points. 

        Expected output: returns a list containing all the new waypoints in order of occurance along the line between the two points
        """
        waypointList = []
        for stepNumber in range(1, breakAmount + 1):
            waypointList.append([waypointOne[0] + stepNumber * ((waypointTwo[0] - waypointOne[0]) / float(breakAmount)), 
                waypointOne[1] + stepNumber * ((waypointTwo[1] - waypointOne[1]) / float(breakAmount)), 
                waypointOne[2] + stepNumber * ((waypointTwo[2] - waypointOne[2]) / float(breakAmount))])

        return waypointList
    
    def changeRoute(self, route, targetWaypoint, newRoute):
        """
        This method will take in a list, targetWaypoint (coordiantes), and a new list. It will chop the original list at the specified
        waypoint and input the new list tuples after that point. It will finally return this newly created list.

        Expected input: route (list) - a list that needs to be changed containing tuples containing GPS coordinates [latitude, longitude, altitude]
            waypoint (tuple) - a tuple containing the desired chopping GPS coordinates [latitude, longitude, altitude]
            newRoute (list) - a new list that will replace tuples following chopPoint containing tuples containing GPS coordinates [latitude, longitude, altitude]

        Expected output: returns a list containing all the new waypoints in order of occurance along the line between the two points, or False if the target is not in the route.
        """
        if targetWaypoint in route:
            return (route[0:route.index(targetWaypoint)] + newRoute)
        else:
            return False

if __name__ == "__main__":
    route = Route("interop_example.json")
    print(route.boundarypoints)
    print(route.waypoints)
    print(route.searchGridPoints)
