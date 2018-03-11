import math
import sys
import os
import copy
import time


def main(argv):
    #start counting time
    start_time = time.time()
    #time limit is current time + 10 minutes
    time_limit = time.time() + 600
    
    # Get the file name from the command line argument
    filename = os.path.splitext(sys.argv[-1])[0]

    # List to hold all the data from the file
    data = readInput(filename) 
    
    graph = createGraph(data)
    
    walk = nearestNeighbor(graph)
    
    distance = totalLength(walk, graph)
    print("Before 2 opt")
    print(walk)
    print(distance)
    ##print (time.time())
    ##print(time_limit)
    if time.time() < time_limit:
        improvedTour = twoOptTour(walk, graph, filename,time_limit)
        walk = improvedTour
        distance = totalLength(improvedTour, graph)
        print("After 2 opt")
        print(walk)
        print(distance)
        
    time_taken = time.time() - start_time
    print("Time taken: %d" %time_taken)
    writeOutput(distance, walk, filename)

   
# This function takes a filename and returns a list of tuples containing (city number, x-coordinate, y-coordinate)
def readInput(filename):

    data = []

    with open(filename + ".txt", "r") as inputFile:
        for line in inputFile:
            source, sourceXCoordinate, sourceYCoordinate = (int(i) for i in line.split())
            data.append(tuple([source, sourceXCoordinate, sourceYCoordinate]))
            #https://stackoverflow.com/questions/11354544/read-lines-containing-integers-from-a-file-in-python
    inputFile.close()

    return data

# This function will write the tour length and each city in tour list
def writeOutput(tourLength, tourList, filename):
    filename = filename + ".txt.tour"
    
    with open(filename, "w") as outputFile:
        outputFile.write("%d\n" %tourLength)

        # Write each city in tour. Exclude writing the last city
        # since each city should only appear once. Last city is a repeated vertex
        lastElement = len(tourList) - 1

        for city in tourList[0:lastElement]:
            outputFile.write("%d\n" %city)
    
    outputFile.close()


# Will take a list of tuples representing city name, xCoordinate, y-Coordinate and create an adjacency list
def createGraph(data):
    # Graph will be represented by an adjacency list
    graph = {}
    distanceTable = [[0 for i in range(len(data))]for j in range(len(data))]
    start_time = time.clock()
    # Create an adjacency list like
    # {City1: {neighbor1: distance, neighbor2: distance} 

    # Iterate over each location
    for source, xCoordinate, yCoordinate in data:
        currentSource = source
        currentX = xCoordinate
        currentY = yCoordinate
        # Create a dictionary consisting of all neighbors of currentSource and the distance to currentSource
        neighbors = {}
        for dest, destX, destY in data:

            # Don't calculate the distance from one location to the same location
            if dest != currentSource:
               # print "distanceTable[%d][%d]" % (source, dest)
                if distanceTable[source][dest] > 0:
                    distance = distanceTable[source][dest]
                   # print "Looked up distanceTable[%d][%d] = %d" % (source, dest, distance)
                else:
                    distance = calculateDistance(currentX, destX, currentY, destY)
                    distanceTable[source][dest] = distance
                    distanceTable[dest][source] = distance
                neighbors.update({dest: distance})
                graph[currentSource] = neighbors
                   # testValue = distanceTable[source][dest]
                   # reverseTest = distanceTable[dest][source]
                   # print "distanceTable[%d][%d] = %d" % (source, dest, testValue)
                   # print "distanceTable[%d][%d] = %d" % (dest, source, reverseTest)
    return graph

# This function returns the euclidean distance between two points given x and y coordinates
def calculateDistance(x1, x2, y1, y2):
    x_diff = x1 - x2
    y_diff = y1 - y2

    distance = math.sqrt(x_diff * x_diff + y_diff * y_diff)

    # Return the distance rounded to the nearest integer
    return int(round(distance))

def nearestNeighbor(graph):
    cities = graph.keys()
    citiesVisited = 0
    currentCity = 0
    
    order = [0]

    while(citiesVisited < len(cities)): 
       # print "Current city is: %d" % (currentCity)
        
        minDistance = sorted(graph[currentCity], key=graph[currentCity].get)
       # print "minDistance from %d: %s" % (currentCity, minDistance)
        
        for city in minDistance:
           # print "Checking %d" % (city)
            if city in order:
               # print "%d is in minDistance" % (city)
                continue
            else:
               # print "%d has not been visited, adding to tour" % (city)
                nearest = city
                order.append(nearest)
                break
       # print "Order is now %s" % (order)
        citiesVisited += 1
       # print "citiesVisited: %d" % (citiesVisited)
        currentCity = nearest
        
    order.append(order[0])
    return order

# calculate tour length
def totalLength(walk, graph):
    totalDistance = 0
    walkLength = (len(walk)-1)
    
    # iterate through all walk items
    
    for i in range(walkLength):
        sourceCity = walk[i]
        if (i+1) > (walkLength):    # fixes out of range
            destCity = walk[0]
        else:
            destCity = walk[i+1]
        
        # look up distance between source city and destination city in graph    
        distance = graph[sourceCity][destCity]
        totalDistance += distance
        
    return totalDistance



# This function will use the two opt local search algorithm to improve TSP solution
# https://en.wikipedia.org/wiki/2-opt
def twoOptTour(tour, graph, filename,time_limit):
    bestDistance = totalLength(tour, graph)
    madeChange = True

    # Keep creating a new tour if a previous call to create new tour created a better solution
    # Otherwise return the tour
    while(madeChange == True):
        #print("while")
        if time.time() > time_limit:
            break
        madeChange, tour = createNewTour(tour, graph, filename,time_limit)
        
    return tour

 
def createNewTour(tour, graph,filename,time_limit):
    bestDistance = totalLength(tour, graph)

    # Start at city m that is not the start and perform swaps from m+1 to length of the tour - 1
    # since last city cannot be swapped either

    for m in xrange(1, len(tour) - 1):
        for n in xrange(m + 1, len(tour) - 1):
            #if time limit has been reached end loop
            if time.time() > time_limit:
                break
            #print("1")
            #create a new tour and get its distance
            newTour = twoOptSwap(tour, m, n)
            newDistance = totalLength(newTour, graph)
            #print(newDistance)
            #print(bestDistance)
            # If the new distance is better than best distance, assign tour to the new improved tour
            if(newDistance < bestDistance):
                #print("2")
                tour = newTour
                writeOutput(newDistance, tour, filename)
                return True, tour
    return False, tour #Indicate no changes was made

    
# Perform a 2-opt swap when given a tour and cities m and n
# https://en.wikipedia.org/wiki/2-opt
def twoOptSwap(tour, m, n):
    newTour = []
    # take tour from start to city m - 1 and add it to new tour
    newTour.extend(tour[:m])

    # take tour m to n and add them in reverse order
    index = n
    while(index >= m):
        newTour.append(tour[index])
        index -= 1

    # take the rest of the tour after m and add it to the new tour
    newTour.extend(tour[n+1:])

    return newTour




if __name__ == "__main__":
    main(sys.argv)
