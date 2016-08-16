
from __future__ import division
import math
import numpy
from os import path
#import usageConfigurations as usage_config

import numpy as np

'''
Created on Mar 13, 2014

@author: luis
'''

class GeneralParameters(object):
    '''
    classdocs
    '''
    K_BITS_SECOND = 1024
    MBYTES = 8388608
    MIN_CHANNEL = 32 

    def __init__(self):
        '''
        Constructor
        '''
        self._init_working_hour = 0
        self._final_working_hour = 0
        self._annual_investment_rate = 0
        self._monthly_investment_rate = 0
        self._monthly_fixed_cost = 0
        self._max_investment_period = 0 
        self._cycle_time = 0
        self._base_price = 0
        # The  initial demand percentage is a value between 0 and 100
        self._inital_demand_percentage = 0
        #self._optimal_policy = 'AnchorCustomerPolicy'
        self._optimal_policy = 'ContinuosMixTechnologyPolicy' 
        self._result_relative_path = 'workspace/NetworkOptimization/Optimization/Results'
        self._general_results_statistics = 'fileResultStochastic.txt'
        self._detail_results_statistics = 'detail.txt'

    def calculateMonthlyInvestmentRate(self):
        rate = 1 + self._annual_investment_rate
        periods = float(1.0 / 12.0)
        self._monthly_investment_rate = math.pow(rate, periods)
        self._monthly_investment_rate = self._monthly_investment_rate  - 1  
    
    def read_from_file(self, relative_path, file_name):
        fname = path.expanduser('~/' + relative_path + '/' + file_name)
        constantsName = np.genfromtxt(fname, delimiter=';', usecols=0, dtype=str, skip_header=1)
        constantsData = numpy.genfromtxt(fname,skip_header=1, delimiter=';')[:,1:]
        constants = {}
        for index in range(len(constantsName)):
            constants[constantsName[index]] = constantsData[index][0]        
        # convert the values from numpy float to an integer
        self._init_working_hour = np.asscalar(np.int16(constants['initWorkingHour']))
        self._final_working_hour = np.asscalar(np.int16(constants['finalWorkingHour']))
        self._annual_investment_rate = constants['annualReturnOnInvestmentRate']
        self._monthly_fixed_cost = constants['monthlyFixedCosts']
        self._max_investment_period = int(constants['maxInvestementPeriods'])
        self._cycle_time = constants['cycleTime']
        self._base_price = constants['basePrice']
        self._inital_demand_percentage = constants['initialDemandPercentage']
    
    def get_optimal_policy_module(self):
        return self._optimal_policy
    
    def get_init_working_hour(self):
        return self._init_working_hour
        
    def get_final_working_hour(self):
        return self._final_working_hour
    
    def get_annual_investment_rate(self):
        return self._annual_investment_rate
        
    def get_monthly_investment_rate(self):
        return self._monthly_investment_rate
    
    def get_monthly_fixed_cost(self):
        return self._monthly_fixed_cost
    
    def get_max_investment_period(self):
        return self._max_investment_period
    
    def get_cycle_time(self):
        return self._cycle_time

    def get_base_price(self):
        return self._base_price

    def get_inital_demand_percentage(self):
        return self._inital_demand_percentage / 100 
    
    def set_annual_investment_rate(self, invetment_rate):
        self._annual_investment_rate = invetment_rate
    
    def get_results_relative_path(self):
        return self._result_relative_path    
    
    def get_general_file_results(self):
        return self._general_results_statistics
    
    def get_detail_file_results(self):
        return self._detail_results_statistics
       
def loadCapacityIncrements(capacityIncrements):
    # Load Channel characteristics, this channels are in Kbps (Kilo bits per second)
    fname = path.expanduser('~/workspace/NetworkOptimization/Optimization/Parameters/Channels.csv')
    channels = numpy.genfromtxt(fname,dtype=float, skip_header=1, delimiter=';', usecols=0)
    #print channels
    # checks if channels are well configurated
    capacity = -1
    error = 0
    for index in range(len(channels)):
        capacityTmp = channels[index]
        if capacity >= capacityTmp:
            error = 1
        else:
            capacity = capacityTmp
    if error == 0:
        for item in channels:
            capacityIncrements.insert(len(capacityIncrements), item)
    return error    

def loadDemandIncreasePattern():
    # the form of the file must be first column: cluster 
    #                              second column: first period
    #                              third column: second period and so on.
    #                              element i,j of the table is cluster i period j-1    
    demandData = {}
    fname = path.expanduser('~/workspace/NetworkOptimization/Optimization/Parameters/estimatedDemand.csv')
    clusters = numpy.genfromtxt(fname, delimiter=';', dtype=str, skip_header=0)[0,:]
    load = numpy.genfromtxt(fname, delimiter=';', dtype=str, skip_header=0)[1,:]
    demandDataTmp = numpy.genfromtxt(fname,skip_header=2, delimiter=';')
    for index  in range(0,len(clusters)):
        if load[index] == 'Y':
            demandData[clusters[index]] = demandDataTmp[:,index]
    #print demandData
    return demandData

def loadServiceParameters(serviceParameters):
    # Load services labels
    error = False
    error_message = 'None'
    fname = path.expanduser('~/workspace/NetworkOptimization/Optimization/Parameters/ServiceParameters.csv')
    services = numpy.genfromtxt(fname, delimiter=';', usecols=0, dtype=str, skip_header=1)
    delayTolerant = numpy.genfromtxt(fname, delimiter=';', usecols=13, dtype=str, skip_header=1)
    # Load the rest of parameters: Min Value, Max Value, Increment
    serviceData = numpy.genfromtxt(fname,skip_header=1, delimiter=';')
    dictServicio ={}
    if services.size == 0:
        error = True
        error_message = 'No services have been defined'
    else:
        if services.size == 1:
            serviceData = serviceData[1:]
            dictServicio["name"] = services
            dictServicio["minValue"]= serviceData[0]
            dictServicio["maxValue"]= serviceData[1]
            dictServicio["increment"]= serviceData[2]
            dictServicio["serviceProbability"]= serviceData[3]
            dictServicio["usagePercentage"]= serviceData[4]
            dictServicio["priceAccess"]= serviceData[5]
            dictServicio["priceUse"]= serviceData[6]
            dictServicio["elasticity"]= serviceData[7]
            dictServicio["load"]= serviceData[8]            
            dictServicio["requiredCapacity"]= serviceData[9]
            dictServicio["betaPrice"] = serviceData[10]
            dictServicio["betaTime"] = serviceData[11]
            dictServicio["delayTolerant"] = delayTolerant
        else:
            serviceData = serviceData[:,1:]
            for index in range(len(services)):
                dictServicio ={}
                dictServicio["index"] = index
                dictServicio["name"] = services[index]
                dictServicio["minValue"]= serviceData[index,0]
                dictServicio["maxValue"]= serviceData[index,1]
                dictServicio["increment"]= serviceData[index,2]
                dictServicio["serviceProbability"]= serviceData[index,3]
                dictServicio["usagePercentage"]= serviceData[index,4]
                dictServicio["priceAccess"]= serviceData[index,5]
                dictServicio["priceUse"]= serviceData[index,6]
                dictServicio["elasticity"]= serviceData[index,7]
                dictServicio["load"]= serviceData[index,8]            
                dictServicio["requiredCapacity"]= serviceData[index,9]
                dictServicio["betaPrice"] = serviceData[index,10]
                dictServicio["betaTime"] = serviceData[index,11]
                dictServicio["delayTolerant"] = delayTolerant[index]
                serviceParameters[index] = dictServicio
        
#        serviceProbability = serviceData[:,3]
#        usagePercentage = serviceData[:,4]
#        # Check if service probability and usage percentages are well defined
#        error = 0
#        totalUsage = 0
#        for index in range(len(services)):
#            serviceProbTmp = serviceProbability[index]
#            usagePercenTmp = usagePercentage[index]
#            totalUsage = totalUsage + usagePercenTmp 
#            if ( serviceProbTmp < 0 ) or (serviceProbTmp > 1 ):
#                error = 1
#                print 'Service probability must be between 0 and 1 for service:' + services[index]
#            if (usagePercenTmp < 0) or (usagePercenTmp > 100):
#                error = 1      
#                print 'Usage percentage must be between 0 and 100 for service:' + services[index]
#        if totalUsage <> 100:
#            error = 1
#            print 'Total usage must be equal to 100:'
            
    return error , error_message        


def loadConstants(constants):
    # define constants for problem calculation
    fname = path.expanduser('~/workspace/NetworkOptimization/Optimization/Parameters/constants.csv')
    constantsName = np.genfromtxt(fname, delimiter=';', usecols=0, dtype=str, skip_header=1)
    constantsData = numpy.genfromtxt(fname,skip_header=1, delimiter=';')[:,1:]
    #my_consts={"nValue":3, "minServers":1, "maxServers":15, "KbitsSecond": 1024, "MBytes": 8388608  } 
    #print constantsData
    for index in range(len(constantsName)):        
        constants[constantsName[index]] = constantsData[index][0]
    
    # convert the values from numpy float to an integer
    constants['initWorkingHour'] = np.asscalar(np.int16(constants['initWorkingHour']))
    constants['finalWorkingHour'] = np.asscalar(np.int16(constants['finalWorkingHour']))

    # Reads the software configuration parameters
    fname = path.expanduser('~/workspace/NetworkOptimization/Optimization/Parameters/softwareConfiguration.csv')
    constantsName = np.genfromtxt(fname, delimiter=';', usecols=0, dtype=str, skip_header=1)
    constantsData = numpy.genfromtxt(fname,skip_header=1, delimiter=';', dtype=str)[:,1:]
    for index in range(len(constantsName)):        
        constants[constantsName[index]] = constantsData[index][0]
  

def loadParameters( constants, clusterData, serviceParameters, listaEjecucion):    


    # load Traffic demand - Demand traffic is in Megabytes for hour
    fname = path.expanduser('~/workspace/NetworkOptimization/Optimization/Parameters/demandaGeneral.csv')
    data = numpy.genfromtxt(fname,skip_header=1, delimiter=';')
    cluster = data[:,0]
    totalTrafficWeekDays = data[:,1]
    totalTrafficWeekends = data[:,2]
    
    #usage_config.createConfigurations(constants, serviceParameters, totalTrafficWeekDays, totalTrafficWeekends,  listaEjecucion)       


