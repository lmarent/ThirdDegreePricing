'''
Created on Mar 13, 2014

@author: luis
'''

from numpy import asarray  
from numpy import prod
from numpy import zeros
from numpy import repeat
from numpy import ceil
from numpy import linspace
from demandModel import DemandFunctions

def cartesian(arrays, out=None):
    """
    Generate a cartesian product of input arrays.

    Parameters
    ----------
    arrays : list of array-like
        1-D arrays to form the cartesian product of.
    out : ndarray
        Array to place the cartesian product in.

    Returns
    -------
    out : ndarray
        2-D array of shape (M, len(arrays)) containing cartesian products
        formed of input arrays.

    Examples
    --------
    >>> cartesian(([1, 2, 3], [4, 5], [6, 7]))
    array([[1, 4, 6],
           [1, 4, 7],
           [1, 5, 6],
           [1, 5, 7],
           [2, 4, 6],
           [2, 4, 7],
           [2, 5, 6],
           [2, 5, 7],
           [3, 4, 6],
           [3, 4, 7],
           [3, 5, 6],
           [3, 5, 7]])

    """

    arrays = [asarray(x) for x in arrays]
    dtype = arrays[0].dtype

    n = prod([x.size for x in arrays])
    if out is None:
        out = zeros([n, len(arrays)], dtype=dtype)

    m = n / arrays[0].size
    out[:,0] = repeat(arrays[0], m)
    if arrays[1:]:
        cartesian(arrays[1:], out=out[0:m,1:])
        for j in xrange(1, arrays[0].size):
            out[j*m:(j+1)*m,1:] = out[0:m,1:]
    return out


def createConfigurations(constants, serviceParameters, totalTrafficWeekDays, totalTrafficWeekends,  listaEjecucion):
    bitsByMinute = constants["minChannel"] * constants["KbitsSecond"] * 60
    # The information is OK, so we could start to calculate traffic rates
    listaEjecucion.clear()
    numConfigurations = 1
    configurationDimensions = list()
    for service in iter(sorted(serviceParameters.iterkeys())):
        paramService = serviceParameters[service]
        min_value = paramService["minValue"]
        max_value = paramService["maxValue"]
        increm = paramService["increment"]
        numElements = ceil((max_value - min_value) / increm) + 1
        serviceValues = linspace(min_value, max_value, numElements, endpoint=True)
        configurationDimensions.append(serviceValues)
        numConfigurations = numConfigurations * len(serviceValues)
    configurationSet = cartesian(configurationDimensions)
    for configuracion in configurationSet:
        configurationKey ={}
        listaParametros = {}
        for service in iter(sorted(serviceParameters.iterkeys())):
            # Service parameters given by the user
            paramService = serviceParameters[service]
            index = paramService["index"]
            name = paramService["name"]
            totalTrafficWd = totalTrafficWeekDays[12]
            totalTrafficWe = totalTrafficWeekends[12]
            serviceMBytesHour = totalTrafficWd * (paramService["usagePercentage"] / 100 )         
            # Builds the service parameters from data given by the user 
            meanMBytesPerService = configuracion[index] * paramService["load"]
            meanBitsPerService = meanMBytesPerService * constants["MBytes"]
            serviceTimeMinute = meanBitsPerService / bitsByMinute
            muService = 60 / serviceTimeMinute
            lambdaService = serviceMBytesHour / meanMBytesPerService
            maxlambdaService = lambdaService * 2
            parametros = {}
            for key in paramService.keys():
                parametros[key] = paramService[key]
                                      
            parametros['minServers'] = constants["minServers"]
            parametros['maxServers'] = constants["maxServers"]
            parametros['nValue'] = constants["nValue"]
            parametros['maxLambda'] = maxlambdaService
            parametros['maxPrice'] = DemandFunctions.inverseDemandFuntion3(0, lambdaService, paramService["priceUse"], paramService["elasticity"])
            parametros['mu'] = muService
            listaParametros[name] = parametros
            configurationKey[name] = configuracion[index]
        listaEjecucion[str(configurationKey)] =  listaParametros    
