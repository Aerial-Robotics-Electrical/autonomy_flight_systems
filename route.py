import json
from dronekit import LocationGlobalRelative
class Route:
    """
    This class contains the methods and data used for routing the aircraft

    Expected input: waypoint_list_path - path to the .json file containing a list of waypoints
    """
    def __init__(self, waypoint_list_path):
        self.data = json.load(open(waypoint_list_path, 'rb'))
        self.currentDest = None #This will contain a LocationGlobalRelative object for the current destination

    def generateWaypoint(self, plane, coordinate):
        """
        This will take in GPS coordinates and feed it to the drone.

        Expected input: plane (connection.py Object) - object containing the Dronekit vehicle. Used to feed the destination to the drone
            coordinate (tuple) - a tuple containing the desired ending GPS coordinates [latitude, longitude, altitude]

        Expected output: No output (sets the current destination to the provided coordinate)
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
    
    def changeRouteList(self, routeList, chopPoint, newList):
        """
        This method will take in a list, chopping tuple, and a new list. It will chop the original list at the specified
        chopping point and input the new list tuples after that point. It will finally return this newly created list.

        Expected input: routeList (list) - a list that needs to be changed containing tuples containing GPS coordinates [latitude, longitude, altitude]
            chopPoint (tuple) - a tuple containing the desired chopping GPS coordinates [latitude, longitude, altitude]
            newList (list) - a new list that will replace tuples following chopPoint containing tuples containing GPS coordinates [latitude, longitude, altitude]

        Expected output: returns a list containing all the new waypoints in order of occurance along the line between the two points
        """
    def changeRouteRevised(route, targetWaypoint, newRoute):
    # performs the check to see if the waypoint is on the route
    if targetWaypoint in route:
        return (route[0:route.index(targetWaypoint)] + newRoute)
    else:
        return False

if __name__ == "__main__":
    route = Route('waypoints.json')
    middlePoints = route.breakWaypoints(route.data["waypoints"][0], route.data["waypoints"][1])
    print(route.data["waypoints"][0], middlePoints, route.data["waypoints"][1])