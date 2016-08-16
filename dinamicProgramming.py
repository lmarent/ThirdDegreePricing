'''
Created on Jan 15, 2013

@author: luis
'''

import numpy as np
import NetworkCapacity
import scenarioOptimization
import demandModel
import networkx as nx
import parameter as param
import globalVariables
import functools
import datetime
import numpy
import csv as csvImport
import ast
import QueueModelling
import math



class memoized(object):
       """Decorator that caches a function's return value each time it is called.
       If called later with the same arguments, the cached value is returned, and
       not re-evaluated.
       """
       def __init__(self, func):
          self.func = func
          self.cache = {}
       def __call__(self, *args):
          try:
             return self.cache[args[1],args[2]]
          except KeyError:
             value = self.func(*args)
             self.cache[(args[1],args[2])] = value
             return value
          except TypeError:
             # uncachable -- for instance, passing a list as an argument.
             # Better to not cache than to blow up entirely.
             return self.func(*args)
       def __repr__(self):
          """Return the function's docstring."""
          return self.func.__doc__
       def __get__(self, obj, objtype):
          """Support instance methods."""
          fn = functools.partial(self.__call__, obj)
          fn.reset = self._reset
          return fn
       def _reset(self):
          self.cache = {}


class dinamicAlgorithm: 
    
    Salida = {}
    
    def baseconvert(self, n, base, m):
        """convert positive decimal integer n to equivalent in another base (2-36) and returns a string with m characters"""
        digits = "0123456789abcdefghijklmnopqrstuvwxyz"
        try:
            n = int(n)
            base = int(base)
        except:
            return ""
        if n < 0 or base < 2 or base > 36:
            return ""
        s = ""
        while 1:
            r = n % base
            s = digits[r] + s
            n = n / base
            if n == 0:
                break
        retorno = ""    
        additionalCharacters = m - len(s)
        if additionalCharacters > 0: 
            retorno = '0' * additionalCharacters 
        retorno = retorno + s
        return retorno

    def findDecision(self, index):
        #print 'findDecision init parameters'
        #print index
        #print 'findDecision End parameters'
        retorno = 0
        if index == "0":
            retorno = 0
        elif (index == "1"):
            retorno = -1
        else:
            retorno = 1
        return retorno

    def calculateServiceTimeForService(self, period,direcServicio, constants ):    
        bitsByMinute = constants["minChannel"] * constants["KbitsSecond"] * 60 
        meanMBytesPerService = direcServicio["configuration"] * direcServicio["load"] 
        meanBitsPerService = meanMBytesPerService * constants["MBytes"]
        serviceTimeMinute = meanBitsPerService / bitsByMinute
        muService = 60 / serviceTimeMinute
        return muService 
        

    def calculateDemandForService(self, period,direcServicio, constants, demandInformation ):
        # The field configuration carries the payload by service, in the case of http and e-mail this value is in MB 
        # in the case of voice over ip this value is in minutes.
        # Because configuration means something depending on the service we use the load field in order to traduce the 
        # value to MB
        lambdaService = {}   
        for item in demandInformation:   
            demand = demandInformation[item]
            meanMBytesPerService = direcServicio["configuration"] * direcServicio["load"] 
            serviceUsagePerc = direcServicio["usagePercentage"]
            demandParameter = demand[period] 
            serviceMBytesHour = demandParameter * (serviceUsagePerc / 100 )  
            lambdaService[item] = serviceMBytesHour / meanMBytesPerService
        return lambdaService

    def calculateDemandIncreaseForService(self, period,direcServicio,demandInformation):
        if globalVariables.progDebug == True: 
            try: 
                file = open("debug.txt", "a+")
                file.writelines('start:' + ' calculateDemandIncreaseForService') 
                file.writelines('period:' + str(period)) 
                file.writelines('direcServicio: ' )
                file.writelines(direcServicio.__str__())
                file.writelines('demandInformation: ' )
                file.writelines(demandInformation.__str__())
                file.close()
            except IOError:
                pass
                    
        lambdaService = {}   
        for item in demandInformation:
            demand = demandInformation[item]
            meanMBytesPerService = direcServicio["configuration"] * direcServicio["load"] 
            serviceUsagePerc = direcServicio["usagePercentage"] 
            demandParameter = demand[period * 4] 
            serviceMBytesHourPerActual = demandParameter * (serviceUsagePerc / 100 )
            demandParameter = demand[(period + 1) * 4]  
            serviceMBytesHourNewPeriod = demandParameter * (serviceUsagePerc / 100 )
            serviceMBytesHour = serviceMBytesHourNewPeriod - serviceMBytesHourPerActual  
            lambdaService[item] = serviceMBytesHour / meanMBytesPerService
    
        if globalVariables.progDebug == True: 
            try: 
                file = open("debug.txt", "a+")
                file.writelines('end:' + ' calculateDemandIncreaseForService') 
                file.writelines('lambdaService:' ) 
                file.writelines(lambdaService.__str__() )
                file.close()
            except IOError:
                pass
        return lambdaService


    def sumLambdasForService(self, clusterParameters, lambdaServiceIncrease):
        if globalVariables.progDebug == True: 
            try: 
                fileDebug = open("debug.txt", "a+")
                fileDebug.writelines('start:' + ' sumLambdasForService') 
                fileDebug.writelines('clusterParameters:' + clusterParameters.__str__() ) 
                fileDebug.writelines('lambdaServiceIncrease: ' + lambdaServiceIncrease.__str__() )
                fileDebug.close()
            except IOError:
                pass
            
        retorno = {}
        for item in clusterParameters:
            clusterParameter = clusterParameters[item]
            newLambda = clusterParameter['lambda'] + lambdaServiceIncrease[item]
            newAlpha = newLambda / clusterParameter['mu'] 
            retorno[item] = { 'lambda': newLambda, 'alpha': newAlpha, 'mu':  clusterParameter['mu'], 'execute': clusterParameter['execute'] }
        if globalVariables.progDebug == True: 
            try: 
                fileDebug = open("debug.txt", "a+")
                fileDebug.writelines('end:' + ' sumLambdasForService') 
                fileDebug.writelines('retorno:' + retorno.__str__() ) 
                fileDebug.close()
            except IOError:
                pass
        return retorno     

    def buildClusterParameters(self, lambdaServices, mu ):
        retorno = {}
        for item in lambdaServices:
            execute = True
            if item == "maximum":
                execute = False 
            alpha = lambdaServices[item] / mu
            retorno[item] = { 'lambda': lambdaServices[item], 'alpha': alpha, 'mu': mu, 'execute': execute }
        return retorno

    def findRequiredServers(self, probServicio, minServers, maxSevers,clusterParameters):
        retorno = 0
        for item in clusterParameters:
            alpha = clusterParameters[item]['alpha']
            requiredServers = NetworkCapacity.findRequiredServers(alpha, probServicio, minServers, maxSevers)
            if retorno < requiredServers['numServers']:
                retorno = requiredServers['numServers']
        return retorno    

    def caculateNewDemand(self, newPrice, parameters, actualState, demandChangeFunction ):
        if globalVariables.progDebug == True: 
            try: 
                fileDebug = open("debug.txt", "a+")
                fileDebug.writelines('start:' + ' caculateNewDemand') 
                fileDebug.writelines('newPrice:' + str(newPrice)) 
                fileDebug.writelines('parameters:' + parameters.__str__() ) 
                fileDebug.writelines('actualState:' + actualState.__str__() ) 
                fileDebug.writelines('demandChangeFunction:' + demandChangeFunction ) 
                fileDebug.close()
            except IOError:
                pass
        
        retorno = {}
        oldPrice = actualState['price']
        clusterParameters = actualState['clusterParameters']
        for item in clusterParameters:
            execute = True
            clusterParameter = clusterParameters[item]
            currentLambda = clusterParameter['lambda']  
            if demandChangeFunction == "demandChangeFunction2":
                newLambda = demandModel.demandChangeFunction2(newPrice, oldPrice , parameters['maxPrice'], parameters['nValue'], parameters['maxLambda'], currentLambda)
                pass
            elif demandChangeFunction == "demandChangeFunction3":
                newLambda = demandModel.demandChangeFunction3(newPrice, oldPrice, currentLambda, parameters['elasticity'])
                pass
            if item == "maximum":
                execute = False 
            alpha = newLambda / parameters['mu']
            retorno[item] = { 'lambda': newLambda, 'alpha': alpha, 'mu': parameters['mu'], 'execute': execute }
        if globalVariables.progDebug == True: 
            try: 
                fileDebug = open("debug.txt", "a+")
                fileDebug.writelines('end:' + ' caculateNewDemand') 
                fileDebug.writelines('retorno:' + retorno.__str__() ) 
                fileDebug.close()
            except IOError:
                pass
        return retorno    
        

    def calculatePossibleDecisions(self, n, paramTypeOfService, actualVariableState, percentage, capacityIncrements, totalInstalledCapacity, maxCapacity, demandData, demandChangeFunction):
        # The parameters of this function are: 
        # paramTypeOfService which has the parameters to shape the demand curve
        # actualvariableState: in each position it has the current lambda and price for the type of technology
    
        if globalVariables.progDebug == True:
            try: 
                fileDebug = open("debug.txt", "a+")
                fileDebug.writelines('Start calculatePossibleDecisions:' ) 
                fileDebug.writelines('period:' + str(n))
                fileDebug.writelines('actualVariableState:' + actualVariableState.__str__() )
                fileDebug.writelines('totalInstalledCapacity:' + str(totalInstalledCapacity))
                 
                fileDebug.close()
            except IOError:
                pass
        
        #print 'calculatePossibleDecisions - Init Parameters:'  
        #print paramTypeOfService
        #print actualVariableState
        #print percentage
        #print capacityIncrements
        #print maxCapacity
        #print 'calculatePossibleDecisions - End Parameters:'  
        alternativePriceChoose = 3
        longitud = len(paramTypeOfService)
        # The number of different scenarios is equal to the number of price changes possible powered by the number of
        # type of services 
        totallen = np.power(alternativePriceChoose, longitud)
        escenariosTmp = []
        # In order to specify each price change scenario, I made a map between the total number of scenarios and the corresponding
        # value in the base given by the number of different type of services.  
        for i in range(totallen):
            priceChange = list(self.baseconvert(i,3,longitud))
            #print 'priceChange' + str(priceChange)
            capacityRequired = 0
            newPriceList = ['']*len(paramTypeOfService)
            scenarioParameters = {}
            for typeOfService in iter(sorted(paramTypeOfService.iterkeys())):
                # The following line of code gives the decision in price for each type of service
                parameters =  paramTypeOfService[typeOfService]
                index = parameters['index'] 
                decision = self.findDecision(priceChange[index]) 
                actualState = actualVariableState[typeOfService]
                newPrice = ( 1 + (decision * percentage)) * actualState['price']
                newPriceList[index] = str(newPrice) 
                newClusterParameters = self.caculateNewDemand(newPrice, parameters, actualState, demandChangeFunction )
                increaseLambda = self.calculateDemandIncreaseForService(n ,parameters, demandData)
                clusterParameters = self.sumLambdasForService(newClusterParameters, increaseLambda)
                serviceParameters = {'probServicio': parameters['probServicio'], 'priceUse': newPrice, 'priceAccess': parameters["priceAccess"], 'configuration': parameters["configuration"], 'index': parameters['index'], 'clusterParameters':  clusterParameters}
                scenarioParameters[typeOfService] = serviceParameters 
                requiredServers = self.findRequiredServers(parameters['probServicio'], parameters['minServers'], parameters['maxServers'],  clusterParameters)
                capacityRequired = capacityRequired + (requiredServers * parameters['requiredCapacity'])
            escenariosTmp.append({'key': newPriceList, 'capacity': capacityRequired, 'scenarioParameters': scenarioParameters } )
                 
        if globalVariables.progDebug == True:
            try: 
                fileDebug = open("debug.txt", "a+")
                fileDebug.writelines('scenario Paramters:' + escenariosTmp.__str__() ) 
                fileDebug.close()
            except IOError:
                pass
            
            print "scenario Paramters:" 
            print escenariosTmp
        # This part of the code calculates the possible decision in terms of capacity
        scenarios = {}
        for scenarioTmp in escenariosTmp:
            scenarioParameters = scenarioTmp['scenarioParameters']
            capacityRequired = scenarioTmp['capacity']
            if capacityRequired <= maxCapacity:
                for j in  capacityIncrements: # one possible capacity increment is zero
                    capacity = totalInstalledCapacity + j
                    if (capacity >= capacityRequired) and (capacity <= maxCapacity):
                        listaKey = list(scenarioTmp['key'])
                        listaKey.append(str(j))
                        scenarios[','.join(listaKey)] = {'additonalCapacity' : j, 'scenarioParameters': scenarioParameters }
        if globalVariables.progDebug == True:
            try: 
                fileDebug = open("debug.txt", "a+")
                fileDebug.writelines('calculatePossibleDecisions - outputs' ) 
                fileDebug.writelines('scenarios:' + scenarios.__str__() ) 
                fileDebug.close()
            except IOError:
                pass
        return scenarios


    def calculateNewState(self, scenario, optimalSolution):
        actualVariableState = {}
        scenarioParameters = scenario['scenarioParameters']
        assigment = optimalSolution['assignment']
        for scenarioItem in scenarioParameters: 
            scenarioParameter = scenarioParameters[scenarioItem]
            state = {}
            state['price'] = scenarioParameter["priceUse"] 
            state['clusterParameters'] = scenarioParameter['clusterParameters']
            state['numServers'] = assigment.get(scenarioItem)
            actualVariableState[scenarioItem] = state
        #file.write("actual Variable State: %s" %actualVariableState)
        return actualVariableState
    
    def verifyOptimality( self, value, assignment, solution, scenarioKey, goal):
        #print 'verifyOptimality Initial parameters'
        #print value
        #print solution
        #print scenarioKey
        #print goal
        #print 'verifyOptimality End parameters'
        if goal == "min":
            if solution['valueAssigned'] == False:
                solution['value'] = value
                solution['assignment'] = assignment
                solution['decision'] = scenarioKey
                solution['valueAssigned'] = True
            else:
                if value < solution['value']:
                    solution['value'] = value
                    solution['decision'] = scenarioKey
                    solution['assignment'] = assignment
        else:
            if solution['valueAssigned'] == False:
                solution['value'] = value
                solution['decision'] = scenarioKey
                solution['valueAssigned'] = True
                solution['assignment'] = assignment
            else:
                if value > solution['value']:
                    solution['value'] = value   
                    solution['decision'] = scenarioKey 
                    solution['assignment'] = assignment
        return solution



    @memoized
    def capacityExtensionForeward(self, n, stateKey, actualVariableState, installedCapacity,  paramTypeOfService, maxCapacity, maxServers, capacityUpgradePaths, variationPercentage, maxPeriods,minChannel, goal, demandData, demandChangeFunction, clusterData, configurationDic):
        if globalVariables.progDebug == True:
            try: 
                fileDebug = open("debug.txt", "a+")
                fileDebug.writelines('capacityExtensionForeward - Init parameters'  )
                fileDebug.writelines('Period: ' + str(n))
                fileDebug.writelines('stateKey: ' + stateKey.__str__())
                fileDebug.writelines('installedCapacity: ' + installedCapacity.__str__())
                fileDebug.writelines('maxCapacity: ' + str(maxCapacity))
                fileDebug.writelines('capacityUpgradePaths: ' + capacityUpgradePaths.__str__())
                fileDebug.writelines('variationPercentage: ' + str(variationPercentage))
                fileDebug.writelines('variationPercentage: ' + str(variationPercentage))
                fileDebug.close()
            except IOError:
                pass
        initNodeKey = ''.join((str(n),stateKey))
        solution ={}
        solution['decision'] = 'Not feasible'
        solution['value'] = -1
        solution['assignment'] = {}
        solution['valueAssigned'] = False
        if n==maxPeriods:
            lista = []
            for typeOfService in actualVariableState:
                state = actualVariableState[typeOfService]
                lista.append(str(state['price']))
            lista.append(str(0))    
            solution['decision'] = ','.join(lista)
            solution['value'] = 0
            solution['assignment'] = {}
            solution['valueAssigned'] = True
        else:
            minCost = 0
            mincostDefined = 0
            scenarios = self.calculatePossibleDecisions(n,  paramTypeOfService, actualVariableState, variationPercentage, capacityUpgradePaths, installedCapacity, maxCapacity, demandData, demandChangeFunction)
            for stateNewKey in scenarios:
                scenario = scenarios[stateNewKey]
                nodekey = ''.join((str(n+1),stateNewKey))
                newParameters = scenario['scenarioParameters'] 
                optimalSolution = scenarioOptimization.optimizeScenarioInterface(nodekey, scenario,installedCapacity,maxServers, minChannel, clusterData)
                newInstalledCapacity = installedCapacity + scenario['additonalCapacity']            
                newVariableState = self.calculateNewState(scenario, optimalSolution)
                valorRetornado= self.capacityExtensionForeward(n + 1, stateNewKey, newVariableState, newInstalledCapacity,paramTypeOfService, maxCapacity, maxServers,  capacityUpgradePaths, variationPercentage, maxPeriods, minChannel, goal, demandData, demandChangeFunction, clusterData, configurationDic)
                totalValue= optimalSolution['optimalValue'] + valorRetornado['value'] 
                solution = self.verifyOptimality(totalValue, optimalSolution['assignment'], solution, stateNewKey, goal)
                            
        line = 'capacityExtensionForeward - Init Output ' + str(n) + ' ' + stateKey + 'Decision: ' + solution['decision'] + 'Value:' +  str(solution['value']) + str(solution['assignment']) +  '\n'
        self.Salida[str(n) + ',' + stateKey] = {'decision': str(n+1) + ',' + solution['decision'], 'assignment': solution['assignment']}
        try:
            # This will create a new file or **overwrite an existing file**.
            fileName = "Configuration" + '-Mail-' + str(configurationDic['Mail'])  + 'Http-' + str(configurationDic['Http']) + 'VozIp-' + str(configurationDic['VozIp']) + '2' + '.txt'
            file = open(fileName, "a+")
            file.write(str(line) + '\n')
            file.close()
        except IOError:
            pass

        return solution 
    
    def execute(self, listaEjecucion, constants, demandData, capacityIncrements, clusterData):

        for item in listaEjecucion:
            paramList = listaEjecucion[item]
            configurationDic = eval(item)
                
            if ((configurationDic['Mail'] == 0.5) and (configurationDic['Http'] == 3.0) and (configurationDic['VozIp'] == 2.0)):
                # loop throught all services in order to build the initial state; this process is as follows:
                   # 1. bring service paramters in order to establish prices 
                   # 2. establish current lambda (demand in the first period for the configuration) 
                   # 3. establish the number of servers as the capacity required to process all the demand 
                configurationDic = eval(item)
                ActualStateList = {}
                totalInstalledCapacity = 0
                stateKeyList = [''] * len(paramList)
                try:
                    # This will create a new file or **overwrite an existing file**.
                    fileName = "Configuration" + '-Mail-' + str(configurationDic['Mail'])  + 'Http-' + str(configurationDic['Http']) + 'VozIp-' + str(configurationDic['VozIp']) + '.txt'
                    file = open(fileName, "w")
                    file.write(str(datetime.datetime.now()) + '\n')
                    file.close()
                except IOError:
                    pass
                 
                for servicio in paramList:
                    state = {} 
                    direcServicio = paramList[servicio]
                    direcServicio["configuration"] = configurationDic[direcServicio["name"]]
                    lambdaService = self.calculateDemandForService(0,direcServicio, constants, demandData  )
                    muService = self.calculateServiceTimeForService(0,direcServicio, constants )
                    clusterParameters = self.buildClusterParameters(lambdaService,  muService)
                    numServers = self.findRequiredServers(direcServicio['probServicio'], direcServicio['minServers'], direcServicio['maxServers'],  clusterParameters)   
                    totalInstalledCapacity = totalInstalledCapacity + (numServers * direcServicio["requiredCapacity"] )
                    state['price'] = direcServicio["priceUse"] 
                    state['clusterParameters'] = clusterParameters
                    state['numServers'] = numServers
                    stateKeyList[direcServicio["index"]] = str(direcServicio["priceUse"])
                    ActualStateList[direcServicio["name"]] = state
                    
                print 'capacidad instalada:' + str(totalInstalledCapacity)
                stateKey = ','.join(stateKeyList)
                nodekey = ','.join((str(0),stateKey))
                retorno = self.capacityExtensionForeward(0, stateKey, ActualStateList, totalInstalledCapacity,  paramList, constants["maxCapacity"], constants["maxServers"], capacityIncrements, constants["variationPercentage"], constants["maxPeriods"], constants["minChannel"],"max", demandData, 'demandChangeFunction3', clusterData, configurationDic)
                executeOutput ={}
                key = nodekey
                for i in range(int(constants["maxPeriods"]) + 1):
                    salidaItem = self.Salida[key]
                    executeOutput[str(i)] = salidaItem
                    key = salidaItem['decision']  
                print executeOutput
                self.Salida = {}
                try:
                    # This will create a new file or **overwrite an existing file**.
                    fileName = "Configuration" + '-Mail-' + str(configurationDic['Mail'])  + 'Http-' + str(configurationDic['Http']) + 'VozIp-' + str(configurationDic['VozIp']) + '.txt'
                    file = open(fileName, "a+")
                    file.write(str(executeOutput) + '\n')
                    file.write(str(datetime.datetime.now()) + '\n')
                    file.close()
                except IOError:
                    pass
                
                self.capacityExtensionForeward.reset()
                print 'termino' 



    



