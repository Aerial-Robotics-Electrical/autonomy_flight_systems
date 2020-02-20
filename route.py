import json

class Route:
    """
    This class contains the methods and data used for routing the aircraft

    Expected input: waypoint_list_path - path to the .json file containing a list of waypoints
    """
    def __init__(self, waypoint_list_path):
        self.data = json.load(open(waypoint_list_path, 'rb'))

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

if __name__ == "__main__":
    route = Route('waypoints.json')
    middlePoints = route.breakWaypoints(route.data["waypoints"][0], route.data["waypoints"][1])
    print(route.data["waypoints"][0], middlePoints, route.data["waypoints"][1])