#!/usr/bin/env python3.5

from CubicalComplex import DIM_EDGE, DIM_VERTEX
from CubicalComplex import CubicalComplex

def generatePossibleConfigurations(element, configurations, cComplex):
    # To generate configurations from node's move is more expensive
    # that is why we create two different functions
    if(cComplex.dim[element] == DIM_EDGE):
        return generatePossibleEdgeConfigurations(element, configurations, cComplex)
    else:
        return generatePossibleNodeConfigurations(element, configurations, cComplex)

def generatePossibleNodeConfigurations(element, configuration, cComplex):
    # Produces the list of all the possible configurations we can reach in
    # one move, starting from 'configuration'
    possibleConfigurations = [] # A list of configuration
   
    # Append 'configuration' that is the easiest case, element connects to itself
    possibleConfigurations.append(configuration)

    for neighbour in cComplex.neighbours[element]:
        # The neighbour is in loop, so we can connect to it.
        # If an element has an out connection, it can't have an in one
        if(configuration[neighbour] == neighbour):
            # Check if all the multivectors are proper
            # TODO: improve the performance of the check
            conf = list(configuration)
            conf[element] = neighbour
            elements = {}
            for i in range(0, len(conf)):
                elements[i] = []
            for i in range(0, len(conf)):
                elements[conf[i]].append(i)
            founded = False
            for el in elements.values():
                if(len(el) > 0):
                    if(not cComplex.isProperSet(set(el))):
                        founded = True
                        break
            if(not founded):
                possibleConfigurations.append( conf )
                    
    return possibleConfigurations
    
def generatePossibleEdgeConfigurations(element, configuration, cComplex):
    # Produces the list of all the possible configurations we can reach in
    # one move, starting from 'configuration'
    possibleConfigurations = [] # A list of configuration
    # Element connect to itself
    possibleConfigurations.append(configuration)

    for neighbour in cComplex.neighbours[element]:
        # The neighbour is in loop, so we can connect to it.
        # If an element has an out connection, it can't have an in one
        conf = list(configuration)
        conf[element] = neighbour
        possibleConfigurations.append( conf )

    return possibleConfigurations

def iterativeCMFGeneration(cComplex, cConf, i, elementsList, confPerProc):
    result = []
    confStack = []
    confStack.append((i, cConf))
    while (len(confStack) > 0):
        current = confStack.pop()
        el = current[0]+1
        last = el == len(elementsList) - 1
        for configuration in generatePossibleConfigurations (elementsList[el], current[1], cComplex):
            if(last):
                result.append((None, str(configuration)))
                if(confPerProc > 0 and len(result) == confPerProc):
                    return result
            else:
                confStack.append((el, configuration))
    return result
    
def generateCMF(sc, n, m, monoProcLimit = 1, confPerProc = -1, monop = False):
    cComplex = CubicalComplex(n,m)
    # Loop configuration
    baseConfiguration = [i for i in range(0, cComplex.cellsNumber)]
    # Create the elements list, where the edges are at the head of the list
    # we don't need to check square, they are implcicit in the loop configuration
    elementsList = []
    for i in range(1, cComplex.cellsNumber, 2):
        elementsList.append(i)
    for i in range(0, cComplex.cellsNumber, 2):
        if(cComplex.dim[i] == DIM_VERTEX):
            elementsList.append(i)
    if(not monop): # Debug variable, if it's True the computation is on one process

    # The list of the configurations reachable from the baseConfiguration 
    # moving the 0-th element
        baseConfs = generatePossibleConfigurations(
                    elementsList[0], baseConfiguration, cComplex
                )
    
    # Generate the configuration tree until a certain cell, monoProcLimit
    # So that we can take advantage of the parallelism
    # baseConfs will contain the configurations we should iterate through
        element = 1
        if(monoProcLimit > len(elementsList)):
            monoProcLimit = 2
        while (element < monoProcLimit):
            startConfs = []
            for i in range(len(baseConfs)):
                startConfs.extend( 
                    generatePossibleConfigurations(
                        elementsList[element], baseConfs[i], cComplex
                    )
                )
            element = element + 1
            baseConfs = startConfs.copy()
        # Parallelize the list with spark
        parCmfs = sc.parallelize(baseConfs)
        # flatMap allows us to have just one list with all the configurations
        return parCmfs.flatMap(lambda cmf: iterativeCMFGeneration(cComplex, cmf, element-1, elementsList, confPerProc))
    else:
        return sc.parallelize(iterativeCMFGeneration(cComplex, baseConfiguration, -1, elementsList, confPerProc))

    
