'''
Created on Dec 13, 2012

@author: luis Andres Marentes Cubillos
'''

import math
import numpy

def probabilityCalculation(alpha, numServers, maxServers):
    
    probabilities = numpy.zeros(numServers + 2, dtype=float)
    for i in range(0, numServers + 1 ):
        probabilities[0] = probabilities[0] + (math.pow(alpha, i) / math.factorial(i))
    
    probabilities[0] = math.pow(probabilities[0], -1)
    totalSum = probabilities[0];
    
    for i in range(1, numServers + 1):
        probabilities[i] = (math.pow(alpha, i) / math.factorial(i)) * probabilities[0] 
        if (i < numServers):
            totalSum = totalSum + probabilities[i]    
   
    probabilities[numServers + 1] = totalSum
    #print probabilities
    return probabilities
         
#probabilityCalculation(10, 16, 20)     
