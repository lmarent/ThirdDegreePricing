'''
Created on Feb 22, 2014

@author: luis
'''
from __future__ import division
import DTNCoreProcedures as dtnCore
import math

class backHaulOperatorPolicy:
       
    def calculateD1(self, bt, costoBackHaul, tetha0, betaP):
        #print 'method:' + 'calculateD1' + 'Parameters:' + 'bt:' + str(bt) + 'tetha0' + str(tetha0) + 'betaP:' + str(betaP)
        if bt >= (tetha0*betaP):
            valReturn = (bt - ( (costoBackHaul + tetha0) *betaP )) / 2
        else:
            valReturn = 0
        #print 'outputs calculateD1:' + str(valReturn)
        return valReturn
               
    def calculateCaseOneModelWithoutTimeConstraint(self, bt, k1, costoBackchaul, tetha0,  betaP):
        retorno = {}
        retorno['price'] = (bt + (( costoBackchaul + tetha0 ) * betaP ))/ (2*betaP)
        retorno['backHaul'] = (bt - ((costoBackchaul + tetha0)*betaP))/2
        retorno['demand'] = ((bt - ((costoBackchaul + tetha0)*betaP)))/2
        return retorno

    def calculateCaseTwoModelWithoutTimeConstraint(self, bt, k1, costoBackchaul, tetha0, betaP):
        retorno = {}
        retorno['price'] = (bt - k1)/(betaP)
        retorno['backHaul'] = k1
        retorno['demand'] = k1
        return retorno

    def calculateCaseOneWithoutTimeConstraint(self, k1, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, betaP, optimalD1):
        #print 'method:' + 'calculateCaseOne' + 'Parameters:' + 'k1:' + str(k1) + 'k2:' + str(k2) + 'cycleTime:' + str(cycleTime) + 'timeAverage:' + str(timeAverage)  + 'currentTime:' + str(currentTime) +  'bt:' + str(bt) + 'tetha0:' + str(tetha0)  + 'costoRealTime:' + str(costoRealTime) + 'betaP:' + str(betaP) + 'acumBasedOnk2:' + str(acumBasedOnk2) + 'Zt:' + str(Zt) + 't1:' + str(t1) + 'optimalD1:' + str(optimalD1) + 'optimalD2:' + str(optimalD2)
        valueReturn = {}
        if (k1 >= optimalD1):
            retorno = self.calculateCaseOneModelWithoutTimeConstraint(bt, k1, costBackhaul, tetha0, betaP)                                    
            valueReturn['found'] = True
            valueReturn['result'] = retorno
        else:
            valueReturn['found'] = False
            valueReturn['result'] = {}
        #print 'outputs calculateCaseOne:' + retorno.__str__()
        return valueReturn
                   
    def calculateCaseTwoWithoutTimeConstraint(self, k1, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, betaP, optimalD1):
        #print 'method:' + 'calculateCaseThree' + 'Parameters:' + 'k1:' + str(k1) + 'k2:' + str(k2) + 'cycleTime:' + str(cycleTime) + 'timeAverage:' + str(timeAverage)  + 'currentTime:' + str(currentTime) +  'bt:' + str(bt) + 'tetha0:' + str(tetha0)  + 'costoRealTime:' + str(costoRealTime) + 'betaP:' + str(betaP) + 'acumBasedOnk2:' + str(acumBasedOnk2) + 'Zt:' + str(Zt) + 't1:' + str(t1) + 'optimalD1:' + str(optimalD1) + 'optimalD2:' + str(optimalD2)
        valueReturn = {}
        if (k1 <= optimalD1):
            retorno = self.calculateCaseTwoModelWithoutTimeConstraint(k1, costBackhaul, tetha0, betaP)
            valueReturn['found'] = True
            valueReturn['result'] = retorno
        else:
            valueReturn['found'] = False
            valueReturn['result'] = {}
        #print 'outputs calculateCaseThree:' + retorno.__str__()
        return valueReturn

    
    def applyOptimalPolicy(self, k1, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, betaP):
        #print 'method:' + 'applyOptimalPolicy' + 'Parameters:' + 'k1' + str(k1) + 'k2'  + str(k2) + 'cycleTime' +  str(cycleTime) + 'timeAverage' + str(timeAverage)  + 'currentTime' + str(currentTime)  + 'bt' + str(bt)  + 'tetha0' + str(tetha0)+ 'costoRealTime' + str(costoRealTime) + 'betaP' + str(betaP)
        turnResultEnd ={}
        found= False
        D1 = self.calculateD1(bt, costBackhaul, tetha0, betaP)
        if found == False:
            result = self.calculateCaseOneWithoutTimeConstraint(k1, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, betaP, D1)
            found = result['found']
            if result['found'] == True:
                turnResultEnd = result['result']
                found = result['found']
        if found == False:
            result = self.calculateCaseTwoWithoutTimeConstraint(k1, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, betaP, D1)
            if result['found'] == True:
                turnResultEnd = result['result']
                found = result['found']
        
        #print 'method:' + 'applyOptimalPolicy' + 'Output:' + turnResultEnd.__str__()
        return turnResultEnd

    def calculateOptimalPolicyByServiceCycle(self, k1, tetha0, constants, service, period, continuosData, season, k2, betaTime, hourInit, hourEnd, minuteInit, minuteEnd, pricePolicy):
        #print 'method:' + 'calculateOptimalPolicyByService' + 'Parameters:' + 'service' + str(service) + 'period' + str(period) + 'season' + str(season) + 'serversAssigned' + str(serversAssigned) + 'betaTime' + str(betaTime) + ' k1:' + str(k1) + 'tetha0:' + str(tetha0)
        #print 'value for k2:' + str(k2)
        
        dtn = dtnCore.CoreMethods()        
        cycleTime = constants['cycleTime']
        timeAverage = constants['timeAverage']
        costBackhaul = dtn.calculateBackhaulCostByMegaByte(constants)
        serviceDataPeriod = continuosData[service][period]
        betaPrice = serviceDataPeriod['betaPrice' + season]   # betaPrice by day - according to tests, this is the correct one.
        serviceDataPeriod = serviceDataPeriod[season]   
        incomeCycle = 0
        costCycle = 0
        demandCycle = 0
        inventoryCycle = 0
        dictionaryReturn = {}
        for hour in range(int(hourInit), int(hourEnd)): 
            #betaPrice = serviceDataPeriod[hour]['betaPrice'] # betaPrice by hour
            data = serviceDataPeriod[hour]['data'] 
            incomeHour = 0
            demandHour = 0
            inventoryHour = 0
            costHour = 0 
            dictionaryReturnHour = {}
            for minute in range (int(minuteInit),int(minuteEnd)):
                potentialMarket = data[minute]['potentialMarket']
                #betaPrice = data[minute]['betaPrice'] # betaPrice by minute
                b_t = potentialMarket - (betaTime * ((cycleTime * 2)/60)) 
                currentTime = hour - constants['initWorkingHour']
                currentTime = currentTime + (minute / 60)
                currentTime = math.fmod(currentTime, cycleTime)    
                turnResultEndBd = self.applyOptimalPolicy(k1, cycleTime, timeAverage, currentTime, b_t, costBackhaul, tetha0, betaPrice)
                dictionaryReturnHour[minute] = { 'price' : turnResultEndBd['price'], 'backHaul' :  turnResultEndBd['backHaul'], 'optDemand' : turnResultEndBd['demand'], 'realTime' : 0, 'potentialMarket' : potentialMarket, 'betaPrice' : betaPrice }
                incomeHour = incomeHour +  ( turnResultEndBd['price'] * turnResultEndBd['demand']) 
                costHour = costHour + ( turnResultEndBd['backHaul'] * costBackhaul )
                demandHour = demandHour + turnResultEndBd['demand']
                inventoryHour = inventoryHour + turnResultEndBd['backHaul']
            incomeCycle = incomeCycle + incomeHour
            demandCycle = demandCycle + demandHour
            costCycle = costCycle + costHour 
            inventoryCycle = inventoryCycle + inventoryHour
            dictionaryReturn[hour] = {'data': dictionaryReturnHour, 'income:' : incomeHour, 'betaPrice': betaPrice}
        dictionaryReturnItem = {season: dictionaryReturn,  'income' : incomeCycle, 'cost' : costCycle,  'demand' : demandCycle, 'inventory' : inventoryCycle, 'betaPrice': betaPrice, 'timeOne' : 0, 'maxk2' : 0}
        return dictionaryReturnItem                 


    def calculateOptimalInventoryReduceCost(self, constants, k1, k2, totalInventory, betaPrice ):
        # Calculates the value of the reduced cost associated with the backhaul inventory
        #print 'method:' + 'calculateTheta0' + 'totalInventory' + str(totalInventory) + 'betaPrice' + str(betaPrice) + 't2' + str(t2)
        valTheta0 = 0
        megaBytesContact = constants['MbytesContact']
        valueToSubtract = megaBytesContact - totalInventory
        if valueToSubtract < 0:
            val5 = (betaPrice*(constants['cycleTime'])) / 2 
            valTheta0 = valueToSubtract / val5
            valTheta0 = valTheta0 * -1
        valTheta0 = valTheta0 / 60
        valReturn = {'theta0' : valTheta0}                 
        #print 'method:' + 'calculateTheta0' + str(valTheta0)
        return valReturn