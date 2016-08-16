'''
Created on Nov 15, 2013

@author: luis
'''
from __future__ import division
import math
import graphics as gra
import timeAveragePolicy as timeAvgPolicy
import backHaulOperatorPolicy as backHaulPolicy
import backHaulPriceContrainedOperatorPolicy as backhaulConsPolicy
import mixTechnologyPolicy as mixPolicy
import DTNCoreProcedures


class pricingModel:
           
    def printPolicyResults(self, dictionaryReturnItem, season, desiredElement):
        # this method is for debug and testing purposes. it contruct a list with one specific element of the policy\
        listResult = []
        dataForSeason = dictionaryReturnItem[season]
        for hour in dataForSeason:
            dictionaryReturnHour = dataForSeason[hour]
            for minute in dictionaryReturnHour['data']:
                dictionaryReturnMinute = dictionaryReturnHour['data'][minute]
                value = dictionaryReturnMinute[desiredElement]
                listResult.append(value)
        
        return listResult       
                      
    def basicTestPolicy(self, constants, service, period, continuosData, season): 
        #--- Particular Tests for this class, when executed with the rest of the packages must be in comments
        # These lines of code serve to prove this functionality alone, They must be executed after loading the demand and the continuous demand ( normally they go in the main program )     

        k1 = 1
        k2 =0.5
        tetha0 = 0  
        betaTime = 0.02
        totalInventory = 0

        timeMethods = DTNCoreProcedures.backHaulCycleTimeMethods()

        if (constants['backHaulPricingPolicy'] == 'timeAveragePolicy'): # original policy 
            policyModel = timeAvgPolicy.timeAveragePolicy()
        if (constants['backHaulPricingPolicy'] == 'backHaulOperatorPolicy'):
            policyModel = backHaulPolicy.backHaulOperatorPolicy()
        if (constants['backHaulPricingPolicy'] == 'backHaulPriceContrainedOperatorPolicy'):
            policyModel = backhaulConsPolicy.backHaulOperatorPolicy()       
        if (constants['backHaulPricingPolicy'] == 'mixTechnologyPolicy'):
            policyModel = mixPolicy.timeAveragePolicy()
                 
        
        numCycles = timeMethods.calculateNumberOfCycles(constants)
        print numCycles
        for cycle in range(numCycles):
            tetha0 = 0
            if cycle > 1:
                break 
            interval = timeMethods.calculateTimeIntervalByCycle(constants, cycle )
            optimalDTNPolicy = policyModel.calculateOptimalPolicyByServiceCycle( k1, tetha0, constants, service, period, continuosData, season, k2, betaTime, interval['initHour'], interval['endHour'], interval['initMinute'], interval['endMinute'], policyModel )
            totalInventory = totalInventory + optimalDTNPolicy['inventory']
            print 'cycle:' + str(cycle) + 'Inventory:' + str(optimalDTNPolicy['inventory'])
            
            optimalValues = policyModel.calculateOptimalInventoryReduceCost(constants, k2, optimalDTNPolicy['inventory'], optimalDTNPolicy['betaPrice'] )
            if optimalValues['theta0'] > 0: 
                tetha0 = optimalValues['theta0']
                optimalDTNPolicy = policyModel.calculateOptimalPolicyByServiceCycle( k1, tetha0, constants, service, period, continuosData, season, k2, betaTime, interval['initHour'], interval['endHour'], interval['initMinute'], interval['endMinute'] ) 
            listResult = self.printPolicyResults(optimalDTNPolicy, season, 'potentialMarket')
            print 'cycle:' + str(cycle) + 'potentialMarket:'
            print listResult
            listResult = self.printPolicyResults( optimalDTNPolicy, season, 'betaPrice')
            print 'cycle:' + str(cycle) + 'betaPrice:'
            print listResult
            listResult = self.printPolicyResults(optimalDTNPolicy, season, 'price')
            print 'cycle:' + str(cycle) + 'price:'
            print listResult
            listResult = self.printPolicyResults(optimalDTNPolicy, season, 'backHaul')
            print 'cycle:' + str(cycle) + 'backHaul:'
            print listResult
                 
            print optimalValues

        print 'totalInventory:' + str(totalInventory)  


       
    def calculateOptimalAssignmentByDay(self, serviceParam, period, constants, continuosDemandData, season, serversAssigned, details):
        # the details parameter is used to identify if the user want all the policies generated or just the optimal income and demand (True: include, False: not include )
        #print 'method:' + 'setParametersForOptimalAssignment' + 'Parameters:' + 'period:' + str(period) + 'season:' + str(season) + 'serversAssigned' + str(serversAssigned) + str(details)

        timeMethods = DTNCoreProcedures.backHaulCycleTimeMethods(constants['cycleTime'], constants['initWorkingHour'], constants['finalWorkingHour'])
        coreMethod = DTNCoreProcedures.CoreMethods()
        
        if (constants['backHaulPricingPolicy'] == 'timeAveragePolicy'):
            policyModel = timeAvgPolicy.timeAveragePolicy()
        if (constants['backHaulPricingPolicy'] == 'backHaulOperatorPolicy'):
            policyModel = backHaulPolicy.backHaulOperatorPolicy()
        if (constants['backHaulPricingPolicy'] == 'backHaulPriceContrainedOperatorPolicy'):
            policyModel = backhaulConsPolicy.backHaulOperatorPolicy()
        if (constants['backHaulPricingPolicy'] == 'mixTechnologyPolicy'):
            policyModel = mixPolicy.timeAveragePolicy()
        
        model = pricingModel()
        seviceName = serviceParam['name'] 
        betaTime = serviceParam['betaTime']
        # process Information for business Days
        dataPeriod =  continuosDemandData[seviceName][period][season] 
        numCycles = timeMethods.calculateNumberOfCycles(constants)
        optimalPolicyReturn = {}
        totalIncome = 0
        totalProfit = 0
        totalDemand = 0
        maxK2 = 0
        theta0 = 0
        for cycle in range(numCycles):
            k1 = coreMethod.findMaximalBackhaulCapacity( dataPeriod, constants, serviceParam )  
            k2 = coreMethod.calculateCapacityRealTime(constants, serversAssigned)
            interval = timeMethods.calculateTimeIntervalByCycle(constants, cycle )
            optimalDTNPolicy = policyModel.calculateOptimalPolicyByServiceCycle( k1, theta0, constants, seviceName, period, continuosDemandData, season, k2, betaTime, interval['initHour'], interval['endHour'], interval['initMinute'], interval['endMinute'], policyModel )
            optimalValues = policyModel.calculateOptimalInventoryReduceCost(constants, k1,  k2, optimalDTNPolicy['inventory'], optimalDTNPolicy['betaPrice'] )
            if optimalValues['theta0'] > 0:
                optimalDTNPolicy = policyModel.calculateOptimalPolicyByServiceCycle( k1, optimalValues['theta0'], constants, seviceName, period, continuosDemandData, season, k2, betaTime, interval['initHour'], interval['endHour'], interval['initMinute'], interval['endMinute'], policyModel )
            # This part is for testing and to be used in the policy's figures generation      
            if details:
                bestOptimalPociy = optimalDTNPolicy
            else:
                bestOptimalPociy = {}
            maxProfit = optimalDTNPolicy['income'] - optimalDTNPolicy['cost'] 
            maxincome = optimalDTNPolicy['income']
            maxDemand = optimalDTNPolicy['demand']
            optimalPolicyReturn[cycle] = { 'income': maxincome,  'profit': maxProfit, 'maxDemand': maxDemand, 'cycleDetails' : bestOptimalPociy}
            totalIncome = totalIncome + maxincome
            totalProfit = totalProfit + maxProfit
            totalDemand = totalDemand + maxDemand
            if optimalDTNPolicy['maxk2'] > maxK2:
                maxK2 = optimalDTNPolicy['maxk2']
            # for debuging purpose
            #print 'season' + season + 'cycle:' + str(cycle) + 'totalProfit' + str(maxProfit) +'total Traffic:' + str(totalDemand)
            #print model.printPolicyResults( bestOptimalPociy, season, 'price')
            #print model.printPolicyResults( bestOptimalPociy, season, 'backHaul')
            #print model.printPolicyResults( bestOptimalPociy, season, 'realTime')
            #print model.printPolicyResults( bestOptimalPociy, season, 'potentialMarket')
            #print model.printPolicyResults( bestOptimalPociy, season, 'betaPrice')  
        optimalPolicyReturn['income'] = totalIncome
        optimalPolicyReturn['profit'] = totalProfit
        optimalPolicyReturn['demand'] = totalDemand
        optimalPolicyReturn['maxK2'] = maxK2
        #print 'totalIncome:' + str(totalIncome) + 'totalDemand:' + str(totalDemand)
        #print optimalPolicyReturn.__str__()
        return optimalPolicyReturn

    def numberOfServersRequired(self, constants, k2):
        # This procedure calculates the number of channels required, it takes the maximum real time rate which is expressed as MB/minute
        MBytesPerSecond = k2 / 60
        MbitsPerSecond = MBytesPerSecond* 8
        KbitsPerSecond = MbitsPerSecond * 1024
        channels = math.ceil(KbitsPerSecond / constants['minChannel'])
        return channels     
          

class DtnSensitivityAnalysis:

    def calculateOptimalPolicyAgainstServers(self, constants, serviceParameters, continuosData):
        model = pricingModel()
        dictionaryReturn = {}
        for item in serviceParameters:
            serviceParams = serviceParameters[item]
            #print serviceParams.__str__()
            if serviceParams['delayTolerant'] == 'Y': 
                for period in range(int(constants['maxInvestementPeriods'])):
                    for servers in range (1,10):
                        season = 'businessDays'
                        optimalPoliciyDTNBusinessDays = model.calculateOptimalAssignmentByDay( serviceParams, period, constants, continuosData, season, servers, False)

                        season = 'weekEnds'
                        optimalPoliciyDTNWeekEnds = model.calculateOptimalAssignmentByDay( serviceParams, period, constants, continuosData, season, servers, False)
                        dictionaryReturn[servers] = {'businessDays' : optimalPoliciyDTNBusinessDays, 'weekEnds' : optimalPoliciyDTNWeekEnds}    
                
        grap = gra.graphicClass()
        grap.graphDemandIncomeAgaintsServers(constants, dictionaryReturn, 10)
        return dictionaryReturn

    def calculateOptimalPolicyAgainstAverageTime(self, constants, serviceParameters, continuosData):
        dictionaryReturnTmp = {}
        model = pricingModel()
        initValue = 5.0
        endValue = 8.0
        increment = 0.2
        for item in serviceParameters:
            serviceParams = serviceParameters[item]
            #print serviceParams.__str__()
            if serviceParams['delayTolerant'] == 'Y': 
                for period in range(int(constants['maxInvestementPeriods'])):
                    server = 4
                    averageTime = initValue
                    while averageTime <= endValue:
                        #print 'averageTime:' + str(averageTime) 
                        constants['timeAverage'] = averageTime 
                        season = 'businessDays'
                        optimalPoliciyDTNBusinessDays = model.calculateOptimalAssignmentByDay( serviceParams, period, constants, continuosData, season, server, False)

                        season = 'weekEnds'
                        optimalPoliciyDTNWeekEnds = model.calculateOptimalAssignmentByDay( serviceParams, period, constants, continuosData, season, server, False)
                        dictionaryReturnTmp[averageTime] = {'businessDays' : optimalPoliciyDTNBusinessDays, 'weekEnds' : optimalPoliciyDTNWeekEnds}
                        averageTime = round(averageTime + increment, 3)   
                
        textXAxis = 'Average Time $T_{avg}$ (Hour)'
        textYAxis = {'1': 'Total Demand (MBytes)', '2' : 'Total Income(US Dollars)'}        
        dictionaryReturn= {'optimalPolicy': dictionaryReturnTmp, 'initValue' : initValue, 'endValue' : endValue, 'increment' : increment, 'textXAxis': textXAxis, 'textYAxis' : textYAxis}
        return dictionaryReturn

    def calculateOptimalPolicyAgainstBetaTime(self, constants, serviceParameters, continuosData):
        dictionaryReturnTmp = {}
        model = pricingModel()
        initValue = 0.1
        endValue = 1.0
        increment = 0.1
        for item in serviceParameters:
            serviceParams = serviceParameters[item]
            #print serviceParams.__str__()
            if serviceParams['delayTolerant'] == 'Y': 
                for period in range(int(constants['maxInvestementPeriods'])):
                    server = 3
                    betaTime = initValue
                    while betaTime <= endValue:
                        serviceParams['betaTime'] = betaTime 
                        season = 'businessDays'
                        optimalPoliciyDTNBusinessDays = model.calculateOptimalAssignmentByDay( serviceParams, period, constants, continuosData, season, server, False)

                        season = 'weekEnds'
                        optimalPoliciyDTNWeekEnds = model.calculateOptimalAssignmentByDay( serviceParams, period, constants, continuosData, season, server, False)
                        dictionaryReturnTmp[betaTime] = {'businessDays' : optimalPoliciyDTNBusinessDays, 'weekEnds' : optimalPoliciyDTNWeekEnds}
                        betaTime = round(betaTime + increment, 3)   
                
        textXAxis = 'Time sensitivity $B_{T}$'
        textYAxis = {'1': 'Total Demand (MBytes)', '2' : 'Total Income(US Dollars)'}        
        dictionaryReturn= {'optimalPolicy': dictionaryReturnTmp, 'initValue' : initValue, 'endValue' : endValue, 'increment' : increment, 'textXAxis': textXAxis, 'textYAxis' : textYAxis}
        return dictionaryReturn

    def calculateOptimalPolicyAgainstRealTimeCost(self, constants, serviceParameters, continuosData):
        dictionaryReturnTmp = {}
        model = pricingModel()
        initValue = 70
        endValue = 200
        increment = 5
        for item in serviceParameters:
            serviceParams = serviceParameters[item]
            #print serviceParams.__str__()
            if serviceParams['delayTolerant'] == 'Y': 
                for period in range(int(constants['maxInvestementPeriods'])):
                    server = 3
                    realTimeCost = initValue
                    while realTimeCost <= endValue:
                        constants['costByChannel'] = realTimeCost 
                        season = 'businessDays'
                        optimalPoliciyDTNBusinessDays = model.calculateOptimalAssignmentByDay( serviceParams, period, constants, continuosData, season, server, False)

                        season = 'weekEnds'
                        optimalPoliciyDTNWeekEnds = model.calculateOptimalAssignmentByDay( serviceParams, period, constants, continuosData, season, server, False)
                        dictionaryReturnTmp[realTimeCost] = {'businessDays' : optimalPoliciyDTNBusinessDays, 'weekEnds' : optimalPoliciyDTNWeekEnds}
                        realTimeCost = realTimeCost + increment  
                
        textXAxis = 'Real Time Cost $C_{rt}$ (US Dollars)'
        textYAxis = {'1': 'Total Demand (MBytes)', '2' : 'Total Income(US Dollars)'}
        dictionaryReturn= {'optimalPolicy': dictionaryReturnTmp, 'initValue' : initValue, 'endValue' : endValue, 'increment' : increment, 'textXAxis': textXAxis, 'textYAxis' : textYAxis}
        return dictionaryReturn
        

class backHaulInventory:
    
    def calculatePureConditionInventory(self, intervalInit, intervalEnd, case, K1, K2, costBackhaul, theta0, costoRealTime, betaPrice, cycleTime, timeAverage, slope, intercept):
        #print 'method:' + 'calculatePureConditionInventory' + 'Parameters:' + 'intervalInit' + str(intervalInit) + 'intervalEnd' + str(intervalEnd) + 'case' + str(case) + 'K1'+ str(K1) + 'K2' + str(K2) + 'theta0' + str(theta0) + 'costoRealTime' + str(costoRealTime) + 'betaPrice' + str(betaPrice) + 'cycleTime' + str(cycleTime) + 'timeAverage' + str(timeAverage) + 'slope'  + str(slope) + 'intercept' + str(intercept) 
        model = pricingModel() 
        inventory = 0
        if case == 1:
            init = math.fmod(intervalInit, timeAverage) 
            end =  math.fmod(intervalEnd, timeAverage)
            za = model.calculeZt( cycleTime, timeAverage, init )
            zb = model.calculeZt( cycleTime, timeAverage, end )
            value = (za - 1 ) / (zb - 1) 
            inventory = K2 * timeAverage * math.log(value) * 60 
        if case == 2:
            var1 = ((2 * cycleTime) - intervalInit)
            var2 = ((2 * cycleTime) - intervalEnd)
            log = math.log((var1 / var2))
            part1 = slope * (intervalInit - intervalEnd)
            value = (2 * slope * cycleTime)
            value = value + intercept
            value = value - (costoRealTime * betaPrice)
            value = value * log
            value = value + part1
            value = (value * (timeAverage ) ) / 2
            inventory = value * 60
        if case == 3:
            inventory = ( K1 * (intervalEnd - intervalInit) )  * 60 
        if case == 4:  
            value1 = math.pow(intervalEnd, 2) - math.pow(intervalInit, 2)
            inventory = ( slope *  value1   )/ 4
            valRange = intervalEnd - intervalInit
            value = ( valRange * (intercept - ((costBackhaul + theta0) * betaPrice)))/2
            inventory = (inventory + value) * 60
        return inventory
    
    def calculateTAsteriskWithContraint(self, K1, K2, betaPrice, theta0, slope, intercept, costoRealTime, cycleTime, timeAverage):
        #print 'method:' + 'calculateTAsteriskWithContraint' + 'Parameters:' + 'K1' + str(K1) + 'K2' + str(K2) + 'betaPrice' + str(betaPrice) + 'theta0' + str(theta0) + 'slope' + str(slope) + 'intercept' + str(intercept) + 'costoRealTime' + str(costoRealTime) + 'cycleTime' + str(cycleTime) + 'timeAverage' + str(timeAverage)
        valReturn = {}
        b = ( 2 * cycleTime * slope ) + ( 2 * K2 ) - intercept + (costoRealTime* betaPrice ) - (slope * timeAverage)
        a = slope * -1
        c = (costoRealTime* betaPrice*timeAverage) - (intercept*timeAverage) - (2*cycleTime*costoRealTime*betaPrice) + (2*cycleTime*intercept) - (4*K2*cycleTime)
        bCuadrado = math.pow(b,2)
        if ( bCuadrado - (4*a*c) > 0):
            realRoot1 = ((b*-1) + math.sqrt(bCuadrado - (4*a*c)))/(2*a)
            realroot2 = ((b*-1) - math.sqrt(bCuadrado - (4*a*c)))/(2*a)
            valReturn = {'rootOne' : realRoot1 , 'rootTwo' : realroot2} 
        #print 'method:' + 'calculateTAsteriskWithContraint' + 'ourput:' + valReturn.__str__()
        return valReturn
    
    def calculateTAsteriskWithoutContraint(self, K1, betaPrice, theta0, intercept, slope):
        # The result of this method is in relative time 
        #print 'method:' + 'calculateTAsteriskWithoutContraint' + 'Parameters:' + 'K1:' + str(K1) + 'betaPrice:' + str(betaPrice) + 'theta0:' + str(theta0) + 'intercept:' + str(intercept) + 'slope:' + str(slope)
        value = (2 * K1)
        value = value + (theta0 * betaPrice) - intercept
        value = value / slope
        #print 'method:' + 'calculateTAsteriskWithoutContraint' + 'Output:' + str(value)
        return value   
    
    def calculateInventorywithinTimeConstraint(self, relativehourInit, relativehourEnd, absoluteHourInit, absoluteHourEnd, initHour,  K1, K2, costBackhaul, theta0, costoRealTime, betaPrice, betaTime, cycleTime, timeAverage, btInit, btEnd, slopePotentialMarket, interceptPotentialMarket): 
        model = pricingModel()   
        d2Init = model.calculateD2(btInit, costoRealTime, betaPrice)
        d2Fin = model.calculateD2(btEnd, costoRealTime, betaPrice)
        # calculates the functions K2(z)/z-1
        zInit = model.calculeZt( cycleTime, timeAverage, relativehourInit )
        zEnd = model.calculeZt( cycleTime, timeAverage, relativehourEnd )
        k2ZInit = (K2 * zInit) / (zInit - 1) 
        k2ZEnd =  (K2 * zEnd) / (zEnd - 1) 
        if slopePotentialMarket >= 0:
            if (k2ZInit <=  d2Init) and (k2ZEnd <= d2Fin):
                valreturn = self.calculatePureConditionInventory(relativehourInit, relativehourEnd, 1, K1, K2, costBackhaul, theta0, costoRealTime, betaPrice, cycleTime, timeAverage, slopePotentialMarket, interceptPotentialMarket)
            if (k2ZInit <=  d2Init) and (k2ZEnd >= d2Fin):
                tAsteriskReturn = self.calculateTAsteriskWithContraint(K1, K2, betaPrice, theta0, slopePotentialMarket, interceptPotentialMarket, costoRealTime, cycleTime, timeAverage)
                if (relativehourInit <= tAsteriskReturn['rootOne']) and (tAsteriskReturn['rootOne'] <= relativehourEnd):
                    tAsterisk = tAsteriskReturn['rootOne']
                if (relativehourInit <= tAsteriskReturn['rootTwo']) and (tAsteriskReturn['rootTwo'] <= relativehourEnd):
                    tAsterisk = tAsteriskReturn['rootTwo']
                valreturn = self.calculatePureConditionInventory(relativehourInit, tAsterisk, 1, K1, K2, costBackhaul, theta0, costoRealTime, betaPrice, cycleTime, timeAverage, slopePotentialMarket, interceptPotentialMarket)
                valreturn = valreturn + self.calculatePureConditionInventory(tAsterisk, relativehourEnd, 2, K1, K2, costBackhaul, theta0, costoRealTime, betaPrice, cycleTime, timeAverage, slopePotentialMarket, interceptPotentialMarket)
            if  (k2ZInit >=  d2Init) and (k2ZEnd <= d2Fin): 
                tAsteriskReturn = self.calculateTAsteriskWithContraint(K1, K2, betaPrice, theta0, slopePotentialMarket, interceptPotentialMarket, costoRealTime, cycleTime, timeAverage)
                if (relativehourInit <= tAsteriskReturn['rootOne']) and (tAsteriskReturn['rootOne'] <= relativehourEnd):
                    tAsterisk = tAsteriskReturn['rootOne']
                if (relativehourInit <= tAsteriskReturn['rootTwo']) and (tAsteriskReturn['rootTwo'] <= relativehourEnd):
                    tAsterisk = tAsteriskReturn['rootTwo']
                valreturn = self.calculatePureConditionInventory(relativehourInit, tAsterisk, 2, K1, K2, costBackhaul, theta0, costoRealTime, betaPrice, cycleTime, timeAverage, slopePotentialMarket, interceptPotentialMarket)
                valreturn = valreturn + self.calculatePureConditionInventory(tAsterisk, relativehourEnd, 1, K1, K2, costBackhaul, theta0, costoRealTime, betaPrice, cycleTime, timeAverage, slopePotentialMarket, interceptPotentialMarket)
            if  (k2ZInit >=  d2Init) and (k2ZEnd >= d2Fin):
                valreturn = self.calculatePureConditionInventory(relativehourInit, relativehourEnd, 2, K1, K2, costBackhaul, theta0, costoRealTime, betaPrice, cycleTime, timeAverage, slopePotentialMarket, interceptPotentialMarket)             
        else:    
            if (k2ZInit >=  d2Init):
                valreturn = self.calculatePureConditionInventory(relativehourInit, relativehourEnd, 2, K1, K2, costBackhaul, theta0, costoRealTime, betaPrice, cycleTime, timeAverage, slopePotentialMarket, interceptPotentialMarket)
            if (k2ZEnd <= d2Fin):
                valreturn = self.calculatePureConditionInventory(relativehourInit, relativehourEnd, 1, K1, K2, costBackhaul, theta0, costoRealTime, betaPrice, cycleTime, timeAverage, slopePotentialMarket, interceptPotentialMarket)
            if (k2ZInit <=  d2Init) and (k2ZEnd >= d2Fin):
                tAsteriskReturn = self.calculateTAsteriskWithContraint(K1, K2, betaPrice, theta0, slopePotentialMarket, interceptPotentialMarket, costoRealTime, cycleTime, timeAverage)
                if (relativehourInit <= tAsteriskReturn['rootOne']) and (tAsteriskReturn['rootOne'] <= relativehourEnd):
                    tAsterisk = tAsteriskReturn['rootOne']
                if (relativehourInit <= tAsteriskReturn['rootTwo']) and (tAsteriskReturn['rootTwo'] <= relativehourEnd):
                    tAsterisk = tAsteriskReturn['rootTwo']
                valreturn = self.calculatePureConditionInventory(relativehourInit, tAsterisk, 1, K1, K2, costBackhaul, theta0, costoRealTime, betaPrice, cycleTime, timeAverage, slopePotentialMarket, interceptPotentialMarket)
                valreturn = valreturn + self.calculatePureConditionInventory(tAsterisk, relativehourEnd, 2, K1, K2, costBackhaul, theta0, costoRealTime, betaPrice, cycleTime, timeAverage, slopePotentialMarket, interceptPotentialMarket)
        return valreturn
    
    def calculateInventoryNoTimeConstraint(self, relativehourInit, relativehourEnd, absoluteHourInit, absoluteHourEnd, initHour,  K1, K2, costBackhaul, theta0, costoRealTime, betaPrice, betaTime, cycleTime, timeAverage, btInit, btEnd, slopePotentialMarket, interceptPotentialMarket):
        #print 'method:' + 'calculateInventoryNoTimeConstraint' + 'Parameters:' 
        model = pricingModel()   
        d1Init = model.calculateD1( btInit, theta0, betaPrice)
        d1Fin = model.calculateD1( btEnd, theta0, betaPrice)
            
        if slopePotentialMarket >= 0:
            if (K1 >= d1Fin):
                valreturn = self.calculatePureConditionInventory(relativehourInit, relativehourEnd, 4, K1, K2, costBackhaul, theta0, costoRealTime, betaPrice, cycleTime, timeAverage, slopePotentialMarket, interceptPotentialMarket)
            if (K1 <= d1Init):
                valreturn = self.calculatePureConditionInventory(relativehourInit, relativehourEnd, 3, K1, K2, costBackhaul, theta0, costoRealTime, betaPrice, cycleTime, timeAverage, slopePotentialMarket, interceptPotentialMarket)
            if (d1Init < K1) and ( K1 < d1Fin ):
                tAsterisk = self.calculateTAsteriskWithoutContraint(K1, betaPrice, theta0, interceptPotentialMarket, slopePotentialMarket)
                valreturn = self.calculatePureConditionInventory(relativehourInit, tAsterisk, 4, K1, K2, costBackhaul, theta0, costoRealTime, betaPrice, cycleTime, timeAverage, slopePotentialMarket, interceptPotentialMarket)
                valreturn = valreturn + self.calculatePureConditionInventory(tAsterisk, relativehourEnd, 3, K1, K2, costBackhaul, theta0, costoRealTime, betaPrice, cycleTime, timeAverage, slopePotentialMarket, interceptPotentialMarket)    
        else:
            if (K1 <= d1Fin):   
                valreturn = self.calculatePureConditionInventory(relativehourInit, relativehourEnd, 3, K1, K2, costBackhaul, theta0, costoRealTime, betaPrice, cycleTime, timeAverage, slopePotentialMarket, interceptPotentialMarket)
            if (K1 >= d1Init):
                valreturn = self.calculatePureConditionInventory(relativehourInit, relativehourEnd, 4, K1, K2, costBackhaul, theta0, costoRealTime, betaPrice, cycleTime, timeAverage, slopePotentialMarket, interceptPotentialMarket)
            if (d1Init > K1 > d1Fin):
                tAsterisk = self.calculateTAsteriskWithoutContraint(K1, betaPrice, theta0, interceptPotentialMarket, slopePotentialMarket)
                valreturn = self.calculatePureConditionInventory(relativehourInit, tAsterisk, 3, K1, K2, costBackhaul, theta0, costoRealTime, betaPrice, cycleTime, timeAverage, slopePotentialMarket, interceptPotentialMarket)
                valreturn = valreturn + self.calculatePureConditionInventory(tAsterisk, relativehourEnd, 4, K1, K2, costBackhaul, theta0, costoRealTime, betaPrice, cycleTime, timeAverage, slopePotentialMarket, interceptPotentialMarket)
        return valreturn
            
    def calculateInventoryForHour(self, relativehourInitParam, relativehourEndParam, absoluteHourInit, absoluteHourEnd, constants, K1, K2, theta0, betaPrice, betaTime, elasticity, demandSlope, demandIntercept):
        #print 'method:' + 'calculateInventoryForHour' + 'Parameters:'
        model = pricingModel()   
        
        #define values stored in the constant array
        initHour = constants['initWorkingHour']
        costRealTime = model.calculateRealTimeCostByMegaByte(constants)
        costBackhaul = model.calculateBackhaulCostByMegaByte(constants)
        cycleTime = constants['cycleTime']
        timeAverage = constants['timeAverage']
        
        # We use two hours for defining the interval. The relative hours are with respect to cycle time ( so they initiate as the cycle time is less than one day )
        # the absolute hours corresponds to the demand hour used for forecast. 
        
        # Calculates the corresponding slope and intercept taking as parameters the corresponding values for the demand.
        slopePotentialMarket = demandSlope * ( 1 + elasticity )
        interceptPotentialMarket = demandIntercept * ( 1 + elasticity )
        divisor = math.floor((absoluteHourInit - initHour) /  cycleTime )
        hoursToMultiply = (divisor * cycleTime)  +  initHour
        interceptPotentialMarket = interceptPotentialMarket + (slopePotentialMarket * hoursToMultiply)  
        interceptPotentialMarket = interceptPotentialMarket - ( betaTime* (timeAverage / 60))
        t1 = model.calculateT1(cycleTime, K1, K2, timeAverage)
        # Calculates all the required variables for both extremes of the interval. 
        valreturn1 =0
        valreturn2 = 0 
        if (relativehourInitParam <= t1) and (t1 <= relativehourEndParam):
            relativehourInit = relativehourInitParam
            relativehourEnd = t1
        else:
            relativehourInit = relativehourInitParam
            relativehourEnd = relativehourEndParam      
        btInit = (slopePotentialMarket * relativehourInit) + interceptPotentialMarket 
        btEnd =  (slopePotentialMarket * relativehourEnd) + interceptPotentialMarket
        # Condition for establish the correct part of the policy that must be applied.        
        if relativehourInit <= t1 and relativehourEnd <= t1:
            d2Init = (btInit - (costRealTime*betaPrice)) / 2
            d2End = (btEnd - (costRealTime*betaPrice)) / 2
            # This lines of code take care of the case of negative optimal demand
            if (d2Init < 0):
                if slopePotentialMarket > 0:
                    relativehourInit =  (( costRealTime*betaPrice ) -  interceptPotentialMarket) / slopePotentialMarket
                if slopePotentialMarket < 0:
                    relativehourInit = relativehourEnd
                btInit = (slopePotentialMarket * relativehourInit) + interceptPotentialMarket 
            if (d2End < 0):
                if slopePotentialMarket > 0:
                    relativehourEnd = relativehourInit
                if slopePotentialMarket < 0:
                    relativehourEnd =  (( costRealTime*betaPrice ) -  interceptPotentialMarket) / slopePotentialMarket
                btEnd =  (slopePotentialMarket * relativehourEnd) + interceptPotentialMarket
            if (relativehourInit < relativehourEnd):
                valreturn1 = self.calculateInventorywithinTimeConstraint( relativehourInit, relativehourEnd, absoluteHourInit, absoluteHourEnd, initHour,  K1, K2, costBackhaul, theta0, costRealTime, betaPrice, betaTime, cycleTime, timeAverage, btInit, btEnd, slopePotentialMarket, interceptPotentialMarket)

        if (relativehourInitParam <= t1) and (t1 <= relativehourEndParam):
            relativehourInit = t1
            relativehourEnd = relativehourEndParam
        else:
            relativehourInit = relativehourInitParam
            relativehourEnd = relativehourEndParam  
        btInit = (slopePotentialMarket * relativehourInit) + interceptPotentialMarket 
        btEnd =  (slopePotentialMarket * relativehourEnd) + interceptPotentialMarket
        # Optimal policy part two.
        if relativehourInit >= t1 and relativehourEnd >= t1:
            d1Init = (btInit - (theta0*betaPrice)) / 2
            d1End = (btEnd - (theta0*betaPrice)) / 2
            # This lines of code take care of the case of negative optimal demand
            if (d1Init < 0):
                if slopePotentialMarket > 0:
                    relativehourInit =  (( theta0*betaPrice ) -  interceptPotentialMarket) / slopePotentialMarket
                if slopePotentialMarket < 0:
                    relativehourInit = relativehourEnd 
                btInit = (slopePotentialMarket * relativehourInit) + interceptPotentialMarket                   
            if (d1End < 0):    
                if slopePotentialMarket > 0:
                    relativehourEnd = relativehourInit
                if slopePotentialMarket < 0:
                    relativehourEnd =  (( theta0*betaPrice ) -  interceptPotentialMarket) / slopePotentialMarket
                btEnd =  (slopePotentialMarket * relativehourEnd) + interceptPotentialMarket
            if (relativehourInit < relativehourEnd):
                valreturn2 = self.calculateInventoryNoTimeConstraint( relativehourInit, relativehourEnd, absoluteHourInit, absoluteHourEnd, initHour,  K1, K2, costBackhaul, theta0, costRealTime, betaPrice, betaTime, cycleTime, timeAverage, btInit, btEnd, slopePotentialMarket, interceptPotentialMarket)
        valreturn = valreturn1 + valreturn2
        return valreturn
 
    def calculateInventoryByDay(self,dataPeriod, K1, K2, costBackhaul, theta0, serviceParamItem,  constants):   
        
        totalInventory = 0 
        for hour in range(constants['initWorkingHour'],constants['finalWorkingHour']):
            dataPeriodHour = dataPeriod[hour]
            slope = dataPeriodHour['slope']
            intercept = dataPeriodHour['intercept']  
            betaPrice = dataPeriodHour['betaPrice'] 
            relativeHourInit = math.fmod(hour - constants['initWorkingHour'], constants['cycleTime'])
            if math.fmod(hour + 1  - constants['initWorkingHour'], constants['cycleTime']) == 0:
                relativeHourEnd = constants['cycleTime']
            else:
                relativeHourEnd =  math.fmod(hour + 1  - constants['initWorkingHour'], constants['cycleTime'])
            inventory = self.calculateInventoryForHour(relativeHourInit, relativeHourEnd, hour, hour + 1, constants, K1, K2, theta0, betaPrice, serviceParamItem['betaTime'], serviceParamItem['elasticity'] , slope, intercept)
            #print 'hour:' + str(hour) + 'inventory:' + str(inventory)
            totalInventory = totalInventory  + inventory
        return totalInventory                                                            

