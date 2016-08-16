'''
Created on Dec 13, 2012

@author: luis Andres Marentes Cubillos
'''

import math
import numpy
import QueueModelling

def memoize(f):
    cache_queueModelling = {}

    def memoizedFunction(*args):
        if (args) not in cache_queueModelling:
            cache_queueModelling[(args)] = f(*args)
        #print cache_queueModelling
        return cache_queueModelling[(args)]
    
    memoizedFunction.cache_queueModelling = cache_queueModelling
    return memoizedFunction

@memoize
def findRequiredServers(alpha, probServicio, minServers, maxServers):
    #print 'findRequiredServers Initial Parameters' + ' ' + str(alpha) + ' ' + str(probServicio) + ' ' + str(minServers) + ' ' + str(maxServers)
    retorno = {}
    probabilities = numpy.zeros(maxServers,dtype=float)
    if maxServers < minServers:
        retorno['numServers'] = -1
        retorno['probabilities'] = numpy.zeros(maxServers,dtype=float)
    else:
        if (alpha >  0):
            while (( minServers + 1 ) < maxServers ):
                #print 'minServers' + str(minServers)
                midServers = int(math.floor((maxServers + minServers ) / 2))
                probabilities = QueueModelling.probabilityCalculation(alpha, midServers, maxServers)
                if (probabilities[midServers + 1 ] > probServicio):
                    maxServers = midServers
                else:
                   if ( probabilities[midServers + 1 ] == probServicio ):
                       minServers = midServers
                       maxServers = midServers
                   else:
                       minServers = midServers;
    #         In this point the solution could be the value in the variable minServers or the value in the 
    #         variable maxServers, so it is needed to test for both values.
            serversRequired = int(minServers)
            #print serversRequired
            probabilities = QueueModelling.probabilityCalculation(alpha, serversRequired, maxServers)
            if ( probabilities[serversRequired + 1 ] < probServicio ):
                serversRequired = maxServers
                probabilities = QueueModelling.probabilityCalculation(alpha, serversRequired, maxServers)
                if ( probabilities[serversRequired + 1 ] < probServicio ):
    #               There is no factible solution for the marKov chain
                    retorno['numServers'] = -1
                    retorno['probabilities'] = numpy.zeros(maxServers,dtype=float)
                else:
                    retorno['numServers']  = serversRequired
                    retorno['probabilities']  = probabilities
            else:
                    retorno['numServers']  = serversRequired
                    retorno['probabilities']  = probabilities            
        else:
            retorno['numServers']  = 0
            probabilities = numpy.zeros(2, dtype=float)
            probabilities[0] = 1
            probabilities[1] = 1
            retorno['probabilities']  = probabilities
                       
    #print 'findRequiredServers - Init Outputs:'  
    #print retorno
    #print 'findRequiredServers - End Outputs:'  
    return retorno

def findNetworkAverageCapacity(alpha, minServers, maxServers, numServers):
#===============================================================================
# return: a dictionary with three elements: average elements, varianceElements and probabilities
# This function calculates the probabilities, average elements, and variances 
# for one Queue with the number of servers equal to:numServers and traffic intesity:alpha.
# 
# The parameter maxServers gives a constraint to the number of servers available.  
#===============================================================================
    retorno = {}
    probabilities = numpy.zeros(maxServers,dtype=float)
    if maxServers < minServers:
        retorno['numServers'] = -1
        retorno['averageElements'] = 0 
        retorno['varianceElements'] = -1       
        retorno['probabilities'] = numpy.zeros(maxServers,dtype=float)
    elif numServers > maxServers or numServers < minServers:
        retorno['numServers'] = -1
        retorno['averageElements'] = 0        
        retorno['varianceElements'] = -1       
        retorno['probabilities'] = numpy.zeros(maxServers,dtype=float)        
    else:
        retorno['numServers'] = numServers
        probabilities = QueueModelling.probabilityCalculation(alpha, numServers, maxServers)
        averageElements = 0
        varianceElements = 0 
        for i in range(0, numServers + 1):
            averageElements = averageElements + ( i * probabilities[i] )   
            varianceElements = varianceElements + (math.pow(i, 2) * probabilities[i] )  
        retorno['averageElements'] = averageElements   
        retorno['varianceElements'] =  varianceElements - math.pow(averageElements, 2)    
        retorno['probabilities']  = probabilities
    return retorno             

def findprobabilityStaticticsForOneService(alpha, probServicio, maxServers):
    retorno = {}
    averageElements = numpy.zeros(maxServers + 1,dtype=float)
    varianceElements = numpy.ones(maxServers + 1,dtype=float) 
    nonBlockingProbabilities = numpy.zeros(maxServers + 1,dtype=float)
    requiredServers = findRequiredServers(alpha, probServicio, 1, maxServers)
    requir= requiredServers['numServers']
    # We establish when there is not required servers a variance of -1
    for i in range(0,int(requir)):
        varianceElements[i] = varianceElements[i] * -1
    for i in range(int(requir), int(maxServers + 1)):
        requiredServers = findNetworkAverageCapacity(alpha, requir, maxServers, i)
        averageElements[i] = requiredServers['averageElements'] 
        varianceElements[i] = requiredServers['varianceElements']
        probabilities = requiredServers['probabilities']
        nonBlockingProbabilities[i] = probabilities[i + 1]
    retorno['average'] = averageElements
    retorno['variance'] = varianceElements
    retorno['nonBlockProbability'] = nonBlockingProbabilities
    return retorno

def findProbabilityStatisticsforServices(serviceParameters, maxServers):
    #===========================================================================
    # serviceParameters is a Python list, every element of this list is a dictionary
    # with three elements: alpha, probServicio, maxServers.
    #===========================================================================
    retorno = {}    
       
    numServices = len(serviceParameters)
    shape = (numServices,maxServers + 1)
    averageElements = numpy.zeros(shape ,dtype=float)
    nonBlockProbability = numpy.zeros(shape ,dtype=float)
    for item in serviceParameters:
        itemParameter =  serviceParameters[item]
        index = itemParameter['index']
        probServicio = itemParameter['probServicio']
        clusterParameters = itemParameter['clusterParameters']
        clusterAverageReturn = {} 
        clusterNonBlockProbabilityReturn = {}
        for clusterName in clusterParameters:
            clusterItem = clusterParameters[clusterName]
            if clusterItem['execute'] == True:
                alpha = clusterItem['alpha']
                averageElementsbytypeofService =  findprobabilityStaticticsForOneService(alpha, 
                                                                               probServicio, 
                                                                               maxServers)
                clusterAverageReturn[clusterName] = averageElementsbytypeofService['average']  
                clusterNonBlockProbabilityReturn[clusterName] = averageElementsbytypeofService['nonBlockProbability']
        retorno[item] = {'averageElements': clusterAverageReturn, 'nonBlockingProbabilities': clusterNonBlockProbabilityReturn}
    # print retorno    
    return retorno     


#serviceParameters  = []
#serviceParam ={}
#serviceParam['alpha'] = 10
#serviceParam['probServicio'] = 0.90
#serviceParameters.append(serviceParam)


# tests
#requiredServers = findprobabilityStaticticsForOneService(10, 0.95, 30)
#print 'required servers'
#print requiredServers

#retorno = findProbabilityStatisticsforServices(serviceParameters, 25)
#print retorno