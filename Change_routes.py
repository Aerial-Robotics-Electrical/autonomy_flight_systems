import time

def changeRouteList(routeList, chopPoint, newList):
    # This method takes an input of a routes, chops it off at a specified point,
    # and inserts a new route after that point
    
    # In this configuration, we must loop through every waypoint to find the one
    # that we want. This can take N + 1 number of tries, with every interation having to perform
    # the equality check.
    for waypoint in routeList:
        if (waypoint == chopPoint):
            routeList = routeList[0:routeList.index(waypoint)]   #Chop routelist off at chopping point
            # When we loop through each value in the list, we must both access that item in memory
            # then perform the append action, which could have a N + 1 append actions. We only want
            # to perform this operation once.
            for newCoordinate in newList:
                routeList.append(newCoordinate)   #Add new route to end of list
            break
    return (routeList)

def changeRouteRevised(route, targetWaypoint, newRoute):
    # performs the check to see if the waypoint is on the route
    if targetWaypoint in route:
        # Find the index
        targetIndex = route.index(targetWaypoint)
        # Slice the route
        oldRoute = route[0:targetIndex]
        # Return the list by appending the 2 together.
        # This is the fastest way to append 2 lists. We also
        # don't want to create a variable, as this takes memory
        # to save the variable.
        return (oldRoute + newRoute)
    else:
        return False

rL = [(1,2,3,4),(5,4,6,7),(6,7,8,3),(3,7,4,9),(2,5,1,7)]
cP = (6,7,8,3)
nL = [(3,3,3,3),(4,4,4,4),(5,5,5,5)]

start_time = time.time()
changeList = changeRouteList(rL,cP,nL)
end_time = time.time()
print(changeList)
print("Time: {time} secs".format(time=(end_time - start_time)))
start_time = time.time()
changeRoute = changeRouteRevised(rL, cP, nL)
end_time = time.time()
print(changeRoute)
print("Time: {time} secs".format(time=(end_time - start_time)))
print(changeList == changeRoute)