'''
Created on Feb 22, 2014

@author: luis
'''
from __future__ import division
import DTNCoreProcedures as dtnCore
import math

class timeAveragePolicy:
    
    def calculateD1(self, bt, k2, costBackhaul, tetha0, costRealTime, betaP, phro, maxPrice):
        #print 'method:' + 'calculateD1' + 'Parameters:' + 'bt:' + str(bt) + 'costBackhaul' +  costBackhaul + 'costoRealTime' + str(costoRealTime) + 'betaP:' + str(betaP) + 'phro:' + phro
        value1 = bt / (2*( 1+ phro))
        value2 = ( ( costBackhaul + tetha0 ) + (phro * costRealTime)) * betaP
        value2 = value2 / math.pow((1+phro), 2)
        value2 = value2 / 2
        if (value1 > value2):
            valReturn = value1 - value2
        else:
            valReturn = 0 
        #print 'outputs calculateD2:' + str(valReturn)
        return valReturn

    def calculateCaseFourModel(self, bt, k2, costBackchaul, tetha0, costRealTime, betaP, phro, maxPrice):
        # This case represents the condition when the algorithm constrained by k2, but backhaul costs plus 
        # shadow prices makes less expensive to send flow for the real time connection, and it is also constrained by the maximal price
        retorno = {}
        retorno['price'] = maxPrice
        retorno['backHaul'] = bt - (betaP * maxPrice) - k2
        retorno['realTime'] = k2 
        retorno['demand'] = retorno['backHaul'] + retorno['realTime']   
        return retorno

    def calculateCaseSevenModel(self, bt, k2, costBackchaul, tetha0, costRealTime, betaP, phro, maxPrice):
        # This case represents the condition when the algorithm is constrained by K2, but it is possible. 
        retorno = {}
        retorno['price'] = (( bt / betaP )) - ((k2*( 1 + phro)) / ( phro * betaP )) 
        retorno['backHaul'] = k2 / phro
        retorno['realTime'] = k2
        retorno['demand'] = retorno['backHaul'] + retorno['realTime']   
        return retorno


    def calculateCaseEightModel(self, bt, k2, costBackchaul, tetha0, costRealTime, betaP, phro, maxPrice):
        # This case represents the condition when the algorithm constrained by k2, but backhaul costs plus 
        # shadow prices makes less expensive to send flow for the real time connection
        retorno = {}
        if (bt / betaP)  > (costBackchaul + tetha0):
            retorno['price'] = (bt / (2 * betaP)) + ((costBackchaul + tetha0) / 2 ) 
            retorno['backHaul'] = (bt - ((costBackchaul + tetha0)*betaP) - ( 2 * k2 )) / 2
            retorno['realTime'] = k2 
            retorno['demand'] = retorno['backHaul'] + retorno['realTime']
        else:
            retorno['price'] = (bt / betaP) 
            retorno['backHaul'] = 0
            retorno['realTime'] = 0 
            retorno['demand'] = retorno['backHaul'] + retorno['realTime']               
        return retorno

    def calculateCaseNonFeasible(self, bt, k2, costBackchaul, tetha0, costRealTime, betaP, phro, maxPrice):
        # This case represents the condition when the algorithm is not feasible, in this case we put all in zero. 
        retorno = {}
        retorno['price'] = 0
        retorno['backHaul'] = 0 
        retorno['realTime'] = 0 
        retorno['demand'] = 0  
        return retorno

    def calculateCaseTwelveModel(self,bt, k2, costBackchaul, tetha0, costRealTime, betaP, phro, maxPrice):   
        retorno = {}
        retorno['price'] = maxPrice
        demand = bt - (maxPrice*betaP)
        if (demand >=0):
            if k2 >= demand: 
                retorno['backHaul'] = 0
                retorno['realTime'] = bt - (maxPrice*betaP)
            else:
                retorno['backHaul'] = k2 - demand
                retorno['realTime'] = k2
            retorno['demand'] = retorno['backHaul'] + retorno['realTime']   
        else:
            retorno= self.calculateCaseNonFeasible(self, bt, k2, costBackchaul, tetha0, costRealTime, betaP, phro, maxPrice)
            
        return retorno

    def calculateCaseSixteenModel(self,bt, k2, costBackchaul, tetha0, costRealTime, betaP, phro, maxPrice):   
        retorno = {}
        retorno['price'] = (bt + (costRealTime*betaP)) / (2*betaP)
        demand = (bt - (costRealTime*betaP))/ 2
        if (demand >=0): 
            if k2 >= demand: 
                retorno['backHaul'] = 0
                retorno['realTime'] = demand
            else:
                retorno['backHaul'] = k2 - demand
                retorno['realTime'] = k2
            retorno['demand'] = retorno['backHaul'] + retorno['realTime']
        else:
            retorno= self.calculateCaseNonFeasible(self, bt, k2, costBackchaul, tetha0, costRealTime, betaP, phro, maxPrice)
           
        return retorno
    
    def calculateCaseThirteenModel(self,bt, k2, costBackchaul, tetha0, costRealTime, betaP, phro, maxPrice):
        retorno = {}
        retorno['price'] = bt / betaP
        retorno['backHaul'] = 0
        retorno['realTime'] = 0
        retorno['demand'] = retorno['backHaul'] + retorno['realTime']
        return retorno 
    
    def calculateCaseNineModel(self,bt, k2, costBackchaul, tetha0, costRealTime, betaP, phro, maxPrice):
        retorno = {}
        retorno['price'] = maxPrice
        retorno['backHaul'] = 0
        retorno['realTime'] = 0
        retorno['demand'] = retorno['backHaul'] + retorno['realTime']
        return retorno 

    def calculateCaseElevenModel(self, bt, k2, costBackchaul, tetha0, costRealTime, betaP, phro, maxPrice):
        # This case represents the condition when the algorithm is not constrained by k2, but it is constrained by the maximal price. 
        retorno = {}
        retorno['price'] = maxPrice
        retorno['backHaul'] = ( bt - ( betaP * maxPrice ) ) / ( 1 + phro) 
        retorno['realTime'] = phro * retorno['backHaul'] 
        retorno['demand'] = retorno['backHaul'] + retorno['realTime']  
        return retorno


    def calculateCaseFifteenModel(self, bt, k2, costBackchaul, tetha0, costRealTime, betaP, phro, maxPrice):
        # This case represents the condition when the algorithm is not constrained by k2 and it is not constrained by the maximal price as well.  
        D1 = self.calculateD1(bt, k2, costBackchaul, tetha0, costRealTime, betaP, phro, maxPrice)
        retorno = {}
        retorno['price'] = (bt - (D1*(1+phro)) ) / betaP
        retorno['backHaul'] = D1
        retorno['realTime'] = D1 * phro 
        retorno['demand'] = retorno['backHaul'] + retorno['realTime']  
        return retorno
              
   
    def applyOptimalPolicy(self, k1, k2, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, costRealTime, betaP, phro, maxPrice):
        #print 'method:' + 'applyOptimalPolicy' + 'Parameters:' + 'k1' + str(k1) + 'k2'  + str(k2) + 'cycleTime' +  str(cycleTime) + 'timeAverage' + str(timeAverage)  + 'currentTime' + str(currentTime)  + 'bt' + str(bt)  + 'tetha0' + str(tetha0)+ 'costoRealTime' + str(costoRealTime) + 'betaP' + str(betaP)
        turnResultEnd ={}
        found= False
        # The constraint in the backhaul inventory is not so strong that show prices increases so much.
        costOperateTrafficUnit = ( (costBackhaul + tetha0) + (phro *costRealTime) ) / (1 + phro)
        if ( costOperateTrafficUnit > (bt/betaP) ):
            # It is not profiatble to enter in the market, the provider put a really high price and do not sell anything
            turnResultEnd = self.calculateCaseThirteenModel(bt, k2, costBackhaul, tetha0, costRealTime, betaP, phro, maxPrice) # tested
        elif (costOperateTrafficUnit > maxPrice ):
            # The maximal price is so low that is not possible to sell
            turnResultEnd = self.calculateCaseNineModel(bt, k2, costBackhaul, tetha0, costRealTime, betaP, phro, maxPrice) # tested
        else:      
            if (costBackhaul + tetha0 ) < costRealTime:
                D1 = self.calculateD1(bt, k2, costBackhaul, tetha0, costRealTime, betaP, phro, maxPrice) # tested
                if k2 >= (phro * D1):
                    # case when we are not constrained by the maximal capacity in K2 
                    price = (bt - (( 1 + phro ) * D1  )) / betaP
                    if (price > maxPrice): 
                        valueF2 = (phro * ( bt - (betaP * maxPrice) )) /( 1+ phro)
                        if (valueF2 > k2):
                            # Not feasible
                            turnResultEnd = self.calculateCaseNonFeasible(bt, k2, costBackhaul, tetha0, costRealTime, betaP, phro, maxPrice) # tested
                        else:
                            # This is the same case eleven in the model but case three appears when k2 calculated is equal to the constraint value k2.
                            turnResultEnd = self.calculateCaseElevenModel( bt, k2, costBackhaul, tetha0, costRealTime, betaP, phro, maxPrice) # tested
                    else:
                        # This is the non constrained problem in which it tries to use as much as possible the backhaul channel  
                        turnResultEnd = self.calculateCaseFifteenModel(bt, k2, costBackhaul, tetha0, costRealTime, betaP, phro, maxPrice) # tested    
                else: 
                    price = ( bt / betaP ) - (k2 * ( 1 + phro ))/ (phro * betaP)
                    if (price > maxPrice):
                        valueF2 = (phro * ( bt - (betaP * maxPrice) )) /( 1+ phro)
                        if (valueF2 > k2):
                            # Not feasible
                            turnResultEnd = self.calculateCaseNonFeasible(bt, k2, costBackhaul, tetha0, costRealTime, betaP, phro, maxPrice) # tested 
                        else:
                            turnResultEnd = self.calculateCaseElevenModel( bt, k2, costBackhaul, tetha0, costRealTime, betaP, phro, maxPrice)
                    else: 
                        turnResultEnd = self.calculateCaseSevenModel(bt, k2, costBackhaul, tetha0, costRealTime, betaP, phro, maxPrice) # tested 
            
            if (costBackhaul + tetha0 ) == costRealTime: # both technologies behave as only one
                price = (bt / (2 * betaP)) + ((costBackhaul + tetha0) / 2 )
                # Two identified cases, when the prices is high and when the optimal price is higher than the minimum price and when it is greater
                if (price > maxPrice):
                    turnResultEnd = self.calculateCaseTwelveModel(bt, k2, costBackhaul, tetha0, costRealTime, betaP, phro, maxPrice) # tested
                else:
                    turnResultEnd = self.calculateCaseSixteenModel(bt, k2, costBackhaul, tetha0, costRealTime, betaP, phro, maxPrice) # tested
                
            if (costBackhaul + tetha0 ) > costRealTime: # it is less expensive to send flow by the real time connection
                price = (bt / (2 * betaP)) + ((costBackhaul + tetha0) / 2 )
                # The price is too high to sell, so we have to decrease the price to the maximal value
                if (price > maxPrice):
                    backhaul = bt - (betaP * maxPrice) - k2
                    if (backhaul < 0):
                        # Selling on those prices produces losses.
                        turnResultEnd = self.calculateCaseNonFeasible(bt, k2, costBackhaul, tetha0, costRealTime, betaP, phro, maxPrice) # tested
                    else:
                        # Even that the price is low there is an optimal solution.
                        turnResultEnd = self.calculateCaseFourModel(bt, k2, costBackhaul, tetha0, costRealTime, betaP, phro, maxPrice) # tested
                else:
                    # The optimal price is under the maximal price.
                    turnResultEnd = self.calculateCaseEightModel(bt, k2, costBackhaul, tetha0, costRealTime, betaP, phro, maxPrice) # tested
        #print 'method:' + 'applyOptimalPolicy' + 'Output:' + turnResultEnd.__str__()
        return turnResultEnd

    def calculateOptimalInventoryReduceCost(self, constants, k1, k2, totalInventory, betaPrice ):
        # Calculates the value of the reduced cost associated with the backhaul inventory
        #print 'method:' + 'calculateTheta0' + 'totalInventory' + str(totalInventory) + 'betaPrice' + str(betaPrice) + 't2' + str(t2)
                
        # Temporal code to prove how the policy goes
        valTheta0 = 0
        megaBytesContact = constants['MbytesContact']
        valueToSubtract = megaBytesContact - totalInventory
        if valueToSubtract < 0:
            val1 = valueToSubtract * 2 * math.pow((1+constants['phro']), 2)
            val2 = val1 / constants['cycleTime'] * betaPrice
            valTheta0 = val2 * -1
        valTheta0 = valTheta0 / 60
        valReturn = {'theta0' : valTheta0}                 
        #print 'method calculateOptimalInventoryReduceCost:' + 'calculatedTheta0' + str(valTheta0)
        return valReturn


    def calculateOptimalPolicyByServiceCycle(self, k1, tetha0, constants, service, period, continuosData, season, k2, betaTime, hourInit, hourEnd, minuteInit, minuteEnd, pricePolicy):
        #print 'method:' + 'calculateOptimalPolicyByService' + 'Parameters:' + 'service' + str(service) + 'period' + str(period) + 'season' + str(season) + 'serversAssigned' + str(serversAssigned) + 'betaTime' + str(betaTime) + ' k1:' + str(k1) + 'tetha0:' + str(tetha0)
        #print 'value for k2:' + str(k2)
                
        dtn = dtnCore.CoreMethods()       
                
        cycleTime = constants['cycleTime']
        phro = constants['phro']
        maxPrice = constants['maxPrice']
        timeAverage = constants['timeAverage']
        costRealTime = dtn.calculateRealTimeCostByMegaByte(constants) 
        costBackhaul = dtn.calculateBackhaulCostByMegaByte(constants)
        maxK2 = 0
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
                b_t = potentialMarket - (betaTime * (timeAverage/60))
                currentTime = hour - constants['initWorkingHour']
                currentTime = currentTime + (minute / 60)
                currentTime = math.fmod(currentTime, cycleTime)    
                turnResultEndBd = self.applyOptimalPolicy(k1, k2, cycleTime, timeAverage, currentTime, b_t, costBackhaul, tetha0, costRealTime, betaPrice, phro, maxPrice)
                dictionaryReturnHour[minute] = { 'price' : turnResultEndBd['price'], 'backHaul' :  turnResultEndBd['backHaul'], 'realTime': turnResultEndBd['realTime'], 'optDemand' : turnResultEndBd['demand'], 'potentialMarket' : potentialMarket, 'betaPrice' : betaPrice }
                if turnResultEndBd['realTime'] > maxK2:
                    maxK2 = turnResultEndBd['realTime']
                incomeHour = incomeHour +  ( turnResultEndBd['price'] * turnResultEndBd['demand']) 
                costHour = costHour + ( turnResultEndBd['backHaul'] * costBackhaul ) + ( turnResultEndBd['realTime'] *  costRealTime)
                demandHour = demandHour + turnResultEndBd['demand']
                inventoryHour = inventoryHour + turnResultEndBd['backHaul']
            incomeCycle = incomeCycle + incomeHour
            demandCycle = demandCycle + demandHour
            costCycle = costCycle + costHour 
            inventoryCycle = inventoryCycle + inventoryHour
            dictionaryReturn[hour] = {'data': dictionaryReturnHour, 'income:' : incomeHour, 'betaPrice': betaPrice}
        dictionaryReturnItem = {season: dictionaryReturn,  'income' : incomeCycle, 'cost' : costCycle,  'demand' : demandCycle, 'inventory' : inventoryCycle, 'betaPrice': betaPrice, 'timeOne' : 0, 'maxk2' : maxK2 }
        #print season + ':income:' + str(incomeCycle) + ':cost:' + str(costCycle) + ':costBackhaul: ' + str(costBackhaul) + ':costRealTime:' + str(costRealTime)
        return dictionaryReturnItem                 