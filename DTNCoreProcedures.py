'''
Created on Feb 22, 2014

@author: luis
'''
from __future__ import division
import demandModel as dm
import math

class backHaulCycleTimeMethods:
    
    # CONSTANTS DEFINITION
    MINUTES_PER_HOUR = 60
    SECONDS_PER_HOUR = 3600
    DAYS_PER_MONTH = 30
    
    
    # Static defined variables assigned by users in constants file
    def __init__(self): pass
                
    def get_minute_interval(self, hour, hour_init, hour_end, minute_init, minute_end):
        if (hour == hour_init):
            init_minute_range = minute_init
        else:
            init_minute_range = 0 
        if ((hour + 1) == hour_end):
            end_minute_range =  minute_end
        else:
            end_minute_range =  backHaulCycleTimeMethods.MINUTES_PER_HOUR
        return init_minute_range, end_minute_range           
    
    def calculateTimeIntervalByCycle(self, cycle_time, init_working_hour, final_working_hour, cycle ):
        #print 'method:' + 'calculateTimeIntervalByCycle' + 'cycle:' + str(cycle)
        initHourInt = int(math.floor( cycle_time * cycle ) + init_working_hour )
        endHourInt = int(math.ceil((cycle_time * ( cycle + 1 )) + init_working_hour ))
        initHour = (cycle_time * cycle ) + init_working_hour
        # This part handled the case when the cycle time is not exactly a multiple of the working hours 
        if (endHourInt > final_working_hour):
            endHourInt = final_working_hour
        # Calculates the last minute for the previous cycle
        if cycle > 0: 
            previousEndHourInt = int(math.ceil((cycle_time * ( cycle )) + init_working_hour ))
            previousInitHour =  (cycle_time * ( cycle - 1) ) + init_working_hour
            previuosEndMinute = (1 - ( previousEndHourInt - (previousInitHour + cycle_time ))) * self.MINUTES_PER_HOUR
        else:
            previuosEndMinute = self.MINUTES_PER_HOUR
        #This part calculates the the inital minute and the end minute 
        if (previuosEndMinute < self.MINUTES_PER_HOUR):
            initMinute = previuosEndMinute + 1
        else:
            initMinute = 0
        if endHourInt > (initHour + cycle_time):
            endMinute = (1 - ( endHourInt - (initHour + cycle_time ))) * self.MINUTES_PER_HOUR
        else:
            endMinute = self.MINUTES_PER_HOUR
        returnVal = {'initHour' : initHourInt, 'endHour' : endHourInt, 'initMinute': initMinute, 'endMinute' : endMinute}
        #print 'method:' + 'calculateTimeIntervalByCycle' + str(returnVal)
        return returnVal
    
    def calculateNumberOfCycles(self, cycle_time, init_working_hour, final_working_hour):
        numHours = final_working_hour - init_working_hour
        cycles = int(math.ceil(numHours / cycle_time)) 
        return cycles         
    
    def calculate_time(self, hour, minute):
        return (hour*self.MINUTES_PER_HOUR + minute)

    def calculate_remaining_cycle_time(self, cycle_time, hour, minute):
        total_time = cycle_time * 2
        total_time = total_time * self.MINUTES_PER_HOUR
        total_time -= ( hour*self.MINUTES_PER_HOUR )
        total_time -= minute
        print 'cycle_time' + str(cycle_time) + 'hour:' + str(hour) + 'minute:' + str(minute) + 'total_time:' + str(total_time)
        return total_time

class CoreMethods:

    def demandContinuosModel(self, listaEjecucion, constants, serviceParameters, demandDataBusinessDays, demandDataWeekends):
        # this function takes the parameters and calculates the demand for each of the services, the potential market and the 
        # corresponding average beta for the day.
        valueReturn = {}
        newPrice = 0
        for item in serviceParameters:
            itemParamters = serviceParameters[item]
            if itemParamters['delayTolerant'] == 'Y':
                valueReturnItem = {}
                maxPeriods = int(constants['maxInvestementPeriods'])
                for period in range(maxPeriods):
                    sumBetaPriceBusinessDays = 0
                    sumBetaPriceWeekends = 0
                    dataByHourBusinessDays= {}
                    dataByHourWeekends = {}
                    demandBusinessDaysDay = 0
                    demandWeekEndsDay = 0
                    # The range to optimize only take into account working hours ( from 6 to twenty)
                    # The function works by cycles so it is like the end of the working hour is the start of the following
                        
                    for hour in range(constants['initWorkingHour'],constants['finalWorkingHour']):
                        if hour < 23: 
                            nextHour = hour + 1
                        else:
                            nextHour = 0  
                        demandBusinessDaysNew = demandDataBusinessDays[nextHour][period + 1]
                        demandBusinessDaysNew = demandBusinessDaysNew * itemParamters['usagePercentage'] / 100
                        demandBusinessDaysNew = demandBusinessDaysNew / 60 # we want the demand by minute in this case. 
                        demandWeendsNew = demandDataWeekends[nextHour][period + 1]
                        demandWeendsNew = demandWeendsNew * itemParamters['usagePercentage'] / 100
                        demandWeendsNew = demandWeendsNew / 60 # we want the demand by minute in this case.
                        # business Days Slope and intercept 
                        demandBusinessDays = demandDataBusinessDays[hour][period + 1]
                        demandBusinessDays = demandBusinessDays * itemParamters['usagePercentage'] / 100
                        demandBusinessDays = demandBusinessDays / 60 
                        slopeBusinessDays = ( demandBusinessDaysNew - demandBusinessDays ) # the step size in x is 1 hour, so that why we don't divide by X1 - Xo
                        interceptBusinessDays = demandBusinessDays - ((demandBusinessDaysNew - demandBusinessDays)* hour) 
                        # Weekends Slope and intercept 
                        demandWeekends = demandDataWeekends[hour][period + 1]
                        demandWeekends = demandWeekends * itemParamters['usagePercentage'] / 100
                        demandWeekends = demandWeekends / 60 
                        slopeWeekends = ( demandWeendsNew - demandWeekends ) # the step size in x is 1 hour, so that why we don't divide by X1 - Xo
                        interceptWeekends = demandWeekends - ((demandWeendsNew - demandWeekends)* hour)
                        # construct the demand by minute               
                        dataByMinuteBusinessDays = {}
                        dataByMinuteWeekends = {}
                        sumBetaPriceBusinessHourDays = 0
                        sumBetaPriceHourWeekends = 0 
                        demandBusinessDaysHour = 0
                        demandWeekEndsHour = 0
                        
                        for minute in range (0,60):
                            horaMinute = float(hour + (minute / 60))
                            # Business Days
                            demand = (slopeBusinessDays * horaMinute) + interceptBusinessDays
                            #print 'demand:' + str(horaMinute) + 'hour:' + str(hour) + 'minute:' + str(minute) + 'demand:' + str(demand) 
                            potentialMarket =  dm.demandChangeFunction3(newPrice, itemParamters['priceUse'], demand, itemParamters['elasticity'])
                            betaPriceValue = (potentialMarket - demand) / itemParamters['priceUse']
                            dataByMinuteBusinessDays[minute] = { 'demand': demand, 'potentialMarket': potentialMarket, 'price': 0.0, 'backHaul' : 0.0, 'realTime' : 0.0, 'optDemand' : 0.0, 
                                                                'betaPrice' : betaPriceValue }
                            sumBetaPriceBusinessHourDays = sumBetaPriceBusinessHourDays + betaPriceValue
                            sumBetaPriceBusinessDays = sumBetaPriceBusinessDays + betaPriceValue
                            demandBusinessDaysHour = demandBusinessDaysHour + demand  
                            # Weekends
                            demand = (slopeWeekends * horaMinute) + interceptWeekends
                            potentialMarket =  dm.demandChangeFunction3(newPrice, itemParamters['priceUse'], demand, itemParamters['elasticity'])
                            betaPriceValue = (potentialMarket - demand) / itemParamters['priceUse']
                            dataByMinuteWeekends[minute] = { 'demand': demand, 'potentialMarket': potentialMarket, 'price': 0.0, 'backHaul' : 0.0, 'realTime' : 0.0, 'optDemand' : 0.0, 
                                                            'betaPrice' : betaPriceValue }
                            sumBetaPriceHourWeekends = sumBetaPriceHourWeekends + betaPriceValue
                            sumBetaPriceWeekends = sumBetaPriceWeekends + betaPriceValue
                            demandWeekEndsHour = demandWeekEndsHour + demand 
                        sumBetaPriceBusinessHourDays = sumBetaPriceBusinessHourDays / 60
                        sumBetaPriceHourWeekends = sumBetaPriceHourWeekends/ 60    
                        dataByHourBusinessDays[hour] = {'data' : dataByMinuteBusinessDays , 'slope' : slopeBusinessDays, 'intercept' : interceptBusinessDays, 
                                                        'betaPrice' : sumBetaPriceBusinessHourDays, 'income' : 0.0, 'totDemand' : demandBusinessDaysHour}
                        dataByHourWeekends[hour] = { 'data' : dataByMinuteWeekends, 'slope' : slopeWeekends , 'intercept' : interceptWeekends, 'betaPrice' : sumBetaPriceHourWeekends, 
                                                    'income': 0.0, 'totDemand' : demandWeekEndsHour}
                        demandBusinessDaysDay = demandBusinessDaysDay + demandBusinessDaysHour
                        demandWeekEndsDay = demandWeekEndsDay + demandWeekEndsHour
                        
                    # constructs two structures, one for businessDays and another for Weekends.    
                    
                    betaPriceBusinessDays = sumBetaPriceBusinessDays / (( constants['finalWorkingHour'] - constants['initWorkingHour'] ) * 60 )
                    betaPriceWeekends = sumBetaPriceWeekends / (( constants['finalWorkingHour'] - constants['initWorkingHour'] ) * 60 ) 
                    valueReturnItem[period] = {'businessDays' : dataByHourBusinessDays, 'betaPricebusinessDays': betaPriceBusinessDays,  'incomeBusinessDays' : 0.0, 
                                               'weekEnds' : dataByHourWeekends, 'betaPriceweekEnds' : betaPriceWeekends, 'incomeWeekDays' : 0.0, 
                                               'totDemandBusinessDays' : demandBusinessDaysDay, 'totDemandWeekEnds' : demandWeekEndsDay}
                valueReturn[serviceParameters[item]['name']] = valueReturnItem               
        #print 'continuous demand' + str(valueReturn)
        return valueReturn                    
    
    def calculateRealTimeCostByMegaByte(self, min_channel, Kbit_second, Mbytes, init_working_hour, end_working_hour, cost_param ):
        #print 'method:' + 'calculateRealTimeCostByMegaByte' + 'Parameters:' + constants.__str__()
        minChannel = min_channel
        cost = cost_param
        KbPerSecond = Kbit_second
        bitsPerSecond = KbPerSecond * minChannel
        bitsPerHour = bitsPerSecond* backHaulCycleTimeMethods.SECONDS_PER_HOUR
        MegaBytesPerHour = bitsPerHour / Mbytes
        workableHours = end_working_hour - init_working_hour
        megaBytesperMonth = workableHours * MegaBytesPerHour * backHaulCycleTimeMethods.DAYS_PER_MONTH
        megaByteCost = cost / megaBytesperMonth
        print 'method:' + 'calculateRealTimeCostByMegaByte' + 'Cost Param:' + str(cost_param) + 'Outputs:' + str(megaByteCost)
        return megaByteCost  
    
    def calculateBackhaulCostByMegaByte(self, mega_bytes_contact, cost_param, cycle_time, init_working_hour, final_working_hour):
        #print 'method:' + 'calculateBackhaulCostByMinute' + 'Parameters:' + constants.__str__()
        timeMethods = backHaulCycleTimeMethods()
        rentBackhaul = cost_param
        megaBytesContact = mega_bytes_contact
        numCycles = timeMethods.calculateNumberOfCycles(cycle_time, init_working_hour, final_working_hour)
        megaBytesPerDay = megaBytesContact * numCycles
        megaBytesPerMonth = megaBytesPerDay * backHaulCycleTimeMethods.DAYS_PER_MONTH
        if megaBytesPerMonth == 0:
            megaByteCost = 9999999 # Number more than three orders of magnitude greater than other values. In this way the user can track the error.  
        else: 
            megaByteCost = rentBackhaul / megaBytesPerMonth
        #print 'method:' + 'calculateBackhaulCostByMinute' + 'Outputs:' + str(megaByteCost) 
        return megaByteCost  
           
    def calculateCapacityRealTime(self,constants, serversAssigned):
        #print 'method:' + 'calculateCapacityRealTime' + 'Parameters:' + constants.__str__() + 'serversAssigned:' + str(serversAssigned)
        minChannel = constants['minChannel']
        KbPerSecond = constants['KbitsSecond']
        bitsPerSecond = KbPerSecond * minChannel * serversAssigned
        bitsPerMinute = bitsPerSecond * 60
        MegaBytesPerMinute = bitsPerMinute / constants['MBytes']
        #print 'method:' + 'calculateCapacityRealTime' + 'Output:' + str(MegaBytesPerMinute)
        return MegaBytesPerMinute

    def findMaximalBackhaulCapacity(self, dataPeriod, constants, serviceParam  ):
        #print 'method:' + 'findMaximalBackhaulCapacity' + 'Parameters:' 
        maxDemand = -1
        k1Max = 0
        hourMax = constants['initWorkingHour'] - 1
        for hour in range(constants['initWorkingHour'],constants['finalWorkingHour']):
            dataPeriodHour = dataPeriod[hour]
            slope = dataPeriodHour['slope']
            intercept = dataPeriodHour['intercept']  
            demand =  (slope * hour)  +  intercept
            if demand > maxDemand:
                hourMax = hour
                maxDemand = demand 
        if hourMax >= constants['initWorkingHour']:
            dataPeriodHour = dataPeriod[hourMax]
            slope = dataPeriodHour['slope'] * ( 1 + serviceParam['elasticity'])
            intercept = dataPeriodHour['intercept'] * ( 1 + serviceParam['elasticity'])
            bt = (slope * hourMax ) + intercept
            btMax = bt - ( (serviceParam['betaTime'] * constants['timeAverage'] ) / 60 )
            k1Max = btMax / 2         
        #print 'method:' + 'findMaximalBackhaulCapacity' + 'outputs:' + 'k1Max:' + str(k1Max) 
        return k1Max   