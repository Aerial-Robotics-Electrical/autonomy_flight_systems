def changeRouteList(routeList, chopPoint, newList):
    #This method takes an input of a routes, chops it off at a specified point, and inserts a new route after that point
    
    for route in routeList:
        if (route == chopPoint):
            routeList = routeList[0:routeList.index(route)]   #Chop routelist off at chopping point
            for newCoordinate in newList:
                routeList.append(newCoordinate)   #Add new route to end of list
            break
    return (routeList)
rL = [(1,2,3,4),(5,4,6,7),(6,7,8,3),(3,7,4,9),(2,5,1,7)]
cP = (6,7,8,3)
nL = [(3,3,3,3),(4,4,4,4),(5,5,5,5)]

changeList = changeRouteList(rL,cP,nL)
print(changeList)