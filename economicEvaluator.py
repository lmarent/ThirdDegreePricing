'''
Created on Nov 15, 2013

@author: luis
'''
from __future__ import division

import numpy as np
import ast
import QueueModelling
import math
import proportionalDTNPricing as pricing 
from os import path
from Parameters import GeneralParameters
from DTNCoreProcedures import CoreMethods
from DTNCoreProcedures import backHaulCycleTimeMethods 
from ContinuosMixTechnologyPolicy import Policy
from ContinuosMixTechnologiesWithPricePolicy import Policy_time_average
from Technologies import Technology_Container
from Assigment import AssignmentContainer
import importlib

class ContinuousEconomicModel(object):
    def __init__(self): pass

    def construct_policy_parameters(self, period, cluster_index, general_parameters, technologies_container, service_container, cycle_time, 
                                    hour_init, hour_end, minute_init, minute_end, customer, detail):
        parameters = {}
        parameters['period'] = period
        parameters['cluster_index'] = cluster_index
        parameters['general_parameters'] = general_parameters
        parameters['technologies_container'] = technologies_container 
        parameters['service_container'] = service_container
        parameters['cycle_time'] = cycle_time
        parameters['hour_init'] = hour_init 
        parameters['hour_end'] = hour_end
        parameters['minute_init'] = minute_init
        parameters['minute_end'] = minute_end
        parameters['detail'] = detail
                
        if (general_parameters.get_optimal_policy_module() == 'AnchorCustomerPolicy'):
            parameters['customer'] = customer

        return parameters
    
    def write_detail_results(self, relative_path, file_name, configuration, period, cluster_index, init_hour, assignments):
        print 'In detail'
        fname = path.expanduser('~/' + relative_path + '/' + file_name)
        try:
            fileResult = open(fname, "a")
            for item in assignments._assigns_container_by_time:
                item_value = assignments._assigns_container_by_time[item]
                line = configuration +  ':period:' + str(period) + ':cluster:' + str(cluster_index) + ':cycle:'+  str(init_hour) + ':service:'+ item + item_value.__str__() + "\n" 
                fileResult.writelines(line) 
            fileResult.close()                
        except IOError:
            pass            
        
    def executeDailyPolicy(self,configuration, period, cluster_index, general_parameters, technologies_container, service_container, customer, registerDetails):
        timeMethods = backHaulCycleTimeMethods()
        module = general_parameters.get_optimal_policy_module()
        policy_module = importlib.import_module(module)
        policy = policy_module.Policy()
        assigment_container = AssignmentContainer(AssignmentContainer.TYPE_CLUSTER)       
        numCycles = timeMethods.calculateNumberOfCycles(general_parameters.get_cycle_time(), 
                                                        general_parameters.get_init_working_hour(), 
                                                        general_parameters.get_final_working_hour())
        #print 'numCycles:' + str(numCycles) 
        for cycle in range(numCycles):
            interval = timeMethods.calculateTimeIntervalByCycle(general_parameters.get_cycle_time(), 
                                                                general_parameters.get_init_working_hour(),
                                                                general_parameters.get_final_working_hour(),
                                                                cycle)
            if (technologies_container.is_using_backhaul_technology() == True):
                technologies_container.get_technologies()[technologies_container.get_backhaul_technology()].set_theta_zero(0)
            parameters = self.construct_policy_parameters( period, cluster_index, general_parameters, technologies_container, service_container, general_parameters.get_cycle_time(), 
                                                      interval['initHour'], interval['endHour'], interval['initMinute'], interval['endMinute'], customer, False)
            assignments = policy.calculateOptimalPolicyByCycle(parameters)
            
            if (technologies_container.is_using_backhaul_technology() == True):
                thetha_0 = policy.calculateOptimalInventoryReduceCost(technologies_container, service_container, general_parameters.get_cycle_time())
                if thetha_0 > 0:
                    technologies_container.get_technologies()[technologies_container.get_backhaul_technology()].set_theta_zero(thetha_0)
                    parameters = self.construct_policy_parameters( period, cluster_index, general_parameters, technologies_container, service_container, general_parameters.get_cycle_time(), 
                                                                   interval['initHour'], interval['endHour'], interval['initMinute'], interval['endMinute'], customer, False)
                    assignments = policy.calculateOptimalPolicyByCycle(parameters)
                    #print period + str(thetha_0)
            # This set of lines show the detail of the optimal policy.
            if registerDetails == True:
                self.write_detail_results( general_parameters.get_results_relative_path(),  general_parameters.get_detail_file_results(), 
                                       configuration, period, cluster_index, interval['initHour'], assignments)
            
            #print assignments
            # At this point we have the assignments made in the assignment container. We also have
            # in the service object the optimal price and flows and in the technology the used capacity. 
            # All that information will be saved on the assignment container.
            dict_node = assignments.get_summary_statistics()
            dict_node['detail'] = assignments
            assigment_container.append_assigment_to_container(cycle, dict_node)
        return assigment_container        

    def build_configuration(self, general_parameters, technologies_container):
        configuration = ':InvestmentRate:' + str(general_parameters.get_annual_investment_rate())  
        if technologies_container.is_using_backhaul_technology():
            backhaul_tech = technologies_container.get_technologies()[technologies_container.get_backhaul_technology()]
            configuration = configuration + ':backhaul:' + backhaul_tech.__str__()
        if technologies_container.is_using_real_technologies():
            cheapest_tech = technologies_container.get_realtime_technologies()[0]
            real_tech = technologies_container.get_technologies()[cheapest_tech]
            configuration = configuration + ':Realtime:' + real_tech.__str__()
        return configuration

    def write_results(self,relative_path, file_name, configuration,  dict_node):
        fname = path.expanduser('~/' + relative_path + '/' + file_name)
        try:
            fileResult = open(fname, "a")
            line = configuration + ':' + dict_node.__str__() + "\n" 
            fileResult.writelines(line)
            fileResult.close()
        except IOError:
            pass

    def execute_period_policy(self, general_parameters, cluster_container, technologies_container, service_container, period, configuration, customer, registerDetails):
        services = service_container.get_services()
        init_hour = general_parameters.get_init_working_hour()
        end_hour = general_parameters.get_final_working_hour()
        base_price = general_parameters.get_base_price()
        clusters = cluster_container.get_clusters()
        contraction_parameter = cluster_container.get_demand_evolution()[period]
        #print 'period' + str(period) +':contraction_parameter:' + str(contraction_parameter)
        assigment_container_period = AssignmentContainer(AssignmentContainer.TYPE_PERIOD)
        for cluster_index in clusters:
            # Brings demand for the cluster in the period.
            #print 'cluster:' + cluster_index
            cluster = clusters[cluster_index] 
            hour_demand = cluster.get_actual_demand(contraction_parameter)
            # Exploits the demand at the minute level for each of the services.
            for service_index in services:
                service = services[service_index]
                # All prices must be handled in the traffic unit that is MegaBytes. Is easier to do it in this way 
                # that put everything in terms of the unit of each service. 
                base_price_service = base_price / service.get_loadMB_Minutes() 
                hour_potential_market = cluster.exploit_cluster_demand(service, cluster_container.get_demand_function(), hour_demand, init_hour, end_hour, base_price_service)
                service.set_potential_market(hour_potential_market)
            # Execute the policy for all cycles in the same cluster
            assignments = self.executeDailyPolicy(configuration, period, cluster_index, general_parameters, technologies_container, service_container, customer, registerDetails)
            dict_node = assignments.get_summary_statistics()
            # As one cluster is repited a number of times per period, the algorithm multiplies 
            # the accumulated statistics by those number of time  
            #print 'period:' + str(period) + ':cluster:' + str(cluster_index) + ':results' + dict_node.__str__()
            for elements in dict_node:
                if elements == "profit" or elements == "income" or elements == "cost":
                    dict_node[elements] = (dict_node[elements] * cluster.get_repetitions()) / math.pow( 1 + general_parameters.get_monthly_investment_rate(), period)
                else:
                    dict_node[elements] = dict_node[elements] * cluster.get_repetitions() 
            dict_node['detail'] = assignments
            #if registerDetails: 
            #    print dict_node 
            #print dict_node 
            assigment_container_period.append_assigment_to_container(cluster_index, dict_node)
        return assigment_container_period



        
    def executeLongTermScenario(self, general_parameters, cluster_container, technologies_container, service_container, customer):
        assigment_container_horizon = AssignmentContainer(AssignmentContainer.TYPE_HORIZON)
        technologies_container.restate_real_time_technology_capacity()
        for period in range(general_parameters.get_max_investment_period()):
            #for period in range(20,general_parameters.get_max_investment_period()):    
            maximal_found = False
            maximum = -1
            i = 1            
            while maximal_found == False: 
                configuration = self.build_configuration( general_parameters, technologies_container)
                assigment_container_period = self.execute_period_policy(general_parameters, cluster_container, technologies_container, service_container, period, configuration, customer, False)
                dict_node = assigment_container_period.get_summary_statistics()
                if maximal_found == False:
                    rental_monthly_cost = technologies_container.get_montly_costs() / math.pow( 1 + general_parameters.get_monthly_investment_rate(), period)
                    profit = dict_node['income'] - rental_monthly_cost
                    print 'Period:' + str(period) + 'Profit:' + str(profit)
                    if profit > maximum:
                        # increments the capacity on real time technology
                        capacity = technologies_container.increment_real_time_capacity()
                        #print 'New capacity:' + str(capacity)
                        maximum = profit
                    else:
                        maximal_found = True
                        # left the capacity in the optimal value, one step before stop
                        capacity = technologies_container.decrement_real_time_capacity()
                        #print 'Period:' + str(period) + 'Final Capacity:' + str(capacity)
                #print 'finding maximum:' + str(i) + 'profit:' + str(profit)
                i = i + 1
            # This additional execution is made in order to register the correct detail statistics
            configuration = self.build_configuration( general_parameters, technologies_container)
            assigment_container_period = self.execute_period_policy(general_parameters, cluster_container, technologies_container, service_container, period, configuration, customer,  True)
            dict_node = assigment_container_period.get_summary_statistics()
            rental_monthly_cost = technologies_container.get_montly_costs() / math.pow( 1 + general_parameters.get_monthly_investment_rate(), period)
            print technologies_container.__str__() +  'total lease cost:'  + str(rental_monthly_cost)
            dict_node['profit'] = dict_node['income'] - rental_monthly_cost
            dict_node['recalc_cost'] = rental_monthly_cost
            dict_node['detail'] = assigment_container_period            
            print 'final assigment:' + ':period:' + str(period) + ':Profit:' + str(dict_node['profit']) + technologies_container.__str__()
            assigment_container_horizon.append_assigment_to_container(period, dict_node)
            
        dict_node = assigment_container_horizon.get_summary_statistics()
        self.write_results(general_parameters.get_results_relative_path(), general_parameters.get_general_file_results(), configuration, dict_node)

class economicModel:

        # Obtains the configuration
        # Bring the calculed traffic by period hour and day of the week ( weekdays) 
            # Multiply by the corresponding percentage assigned to the service type
            # Calculate lamda and mu
            # Calculate the loss probability
            # Multiply ( 1 - loss probability ) lambda * price
        # Add these values 

        # Bring the calculed traffic by period hour and day of the week ( weekends) 
            # Multiply by the corresponding percentage assigned to the service type
            # Calculate lamda and mu
            # Calculate the loss probability
            # Multiply ( 1 - loss probability ) lambda * price
        # Add these values 
        

    def calculateDemandForService(self, configuration, paramService, constants, demand ):
        # The field configuration carries the payload by service, in the case of http and e-mail this value is in MB 
        # in the case of voice over ip this value is in minutes.
        # Because configuration means something depending on the service we use the load field in order to traduce the 
        # value to MB
            
        meanMBytesPerService = configuration * paramService["load"] 
        serviceUsagePerc = paramService["usagePercentage"]
        serviceMBytesHour = demand * (serviceUsagePerc / 100 )  
        lambdaService = serviceMBytesHour / meanMBytesPerService
        return lambdaService

    def calculateServiceTimeForService(self, configuration, paramService, constants ):    
        bitsByMinute = constants["minChannel"] * constants["KbitsSecond"] * 60 
        meanMBytesPerService = configuration * paramService["load"] 
        meanBitsPerService = meanMBytesPerService * constants["MBytes"]
        serviceTimeMinute = meanBitsPerService / bitsByMinute
        muService = 60 / serviceTimeMinute
        return muService 
    
    def calculateIncomeByHourService(self, service, demand, season,  paramService, configuration, period, constants, continuosDemandData, optimizationOutput):
        valReturn = {}
        valueService = 0
        lambdaService = self.calculateDemandForService( configuration, paramService, constants, demand ) 
        muService = self.calculateServiceTimeForService(configuration, paramService, constants )
        dinamicPeriod = np.floor(period / constants['MonthsByRevisionPeriod'])
        if dinamicPeriod >= constants['maxPeriods']:
            dinamicPeriod = constants['maxPeriods'] - 1
        periodDecision = optimizationOutput[str(int(dinamicPeriod))]
        assigment = periodDecision['assignment']  
        decision = periodDecision['decision']
        decisionOut = decision.split(',') 
        serversForService = assigment[service]
        alpha = lambdaService / muService   
        probabilities = QueueModelling.probabilityCalculation(alpha, serversForService, paramService['maxServers'])
        blockProbability = probabilities[serversForService]
        numServices = lambdaService * ( 1 - blockProbability)
        priceService = float(decisionOut[paramService['index'] + 1]) 
        valueService = (numServices * priceService * configuration ) + (paramService['priceAccess'] *  numServices )
        valTraffic = numServices * configuration
        valReturn = {'valueService' : valueService, 'traffic' : valTraffic}
        return valReturn
   
    def getServiceForServer(self, service, period, constants, optimizationOutput):
        dinamicPeriod = np.floor(period / constants['MonthsByRevisionPeriod'])
        if dinamicPeriod >= constants['maxPeriods']:
            dinamicPeriod = constants['maxPeriods'] - 1
        periodDecision = optimizationOutput[str(int(dinamicPeriod))]
        assigment = periodDecision['assignment']  
        serversForService = assigment[service]
        return serversForService
   
    def calculateIncomeByService2(self, service, demand, paramService, configuration, period):
        valueService = 0
        demandService = demand * paramService['usagePercentage'] / 100
        numServices = math.ceil(demandService / ( configuration * paramService['load']))
        valueService = ( numServices * paramService['priceAccess'] ) + ( numServices * configuration * paramService['priceUse'] )
        valReturn = {'income' : valueService, 'traffic' : demandService} 
        return valReturn 
    
    def calculateProfitsNonStochasticByService(self, configuration, service, period, paramService, constants, demandDataBusinessDays, demandDataWeekends):      
        valueServiceBusinessDays = 0
        valueServiceWeekends = 0
        trafficBusinessDays = 0
        trafficWeekends = 0
        for hour in range(constants['initWorkingHour'],constants['finalWorkingHour']):
            demand = demandDataBusinessDays[hour][period + 1]                                  
            valReturn = self.calculateIncomeByService2( service, demand, paramService, configuration, period)
            valueServiceBusinessDays = valueServiceBusinessDays + valReturn['income']
            trafficBusinessDays = trafficBusinessDays + valReturn['traffic']
            demand = demandDataWeekends[hour][period + 1]
            valReturn = self.calculateIncomeByService2( service, demand, paramService, configuration, period)
            valueServiceWeekends = valueServiceWeekends + valReturn['income']
            trafficWeekends = trafficWeekends + valReturn['traffic']
        income = ( valueServiceBusinessDays * 20 ) + (valueServiceWeekends * 10)
        traffic = ( trafficBusinessDays * 20 ) + ( trafficWeekends * 10 )
        valReturn = {'income' : income, 'traffic' : traffic}
        return valReturn
    
    def calculateMonthlyInvestmentRate(self, constant):
        rate = 1 + constant['annualReturnOnInvestmentRate']
        periods = float(1.0 / 12.0)
        monthlyRate = math.pow(rate, periods)
        monthlyRate = monthlyRate - 1  
        #print 'monthlyRate:' +  str(monthlyRate) 
        constant['monthlyReturnOnInvestmentRate'] = monthlyRate 
    
    def executeNoStochastic(self, listaEjecucion, constants, demandDataBusinessDays, demandDataWeekends):
        self.calculateMonthlyInvestmentRate(constants)
        try:
            # This will create a new file or **overwrite an existing file**.
            filename = 'fileResultNoStochastic' + str(constants['annualReturnOnInvestmentRate']) + '.txt'
            fileResult = open(filename, "a")        
            for item in listaEjecucion:
                paramList = listaEjecucion[item]
                configurationDic = eval(item)
                discountedValue = 0
                traffic={}
                profits ={}
                for service in paramList:
                    paramService = paramList[service]
                    discountedValueService = 0 
                    discountedCostService = 0
                    trafficService = 0
                    for period in range(int(constants['maxInvestementPeriods'])):
                        valueServiceBusinessDays = 0
                        valueServiceWeekends = 0
                        configuration = configurationDic[service]
                        valReturn = self.calculateProfitsNonStochasticByService( configuration, service, period, paramService, constants, demandDataBusinessDays, demandDataWeekends)
                        #valReturn = {'income' : 0, 'traffic' :0 }
                        valueService = valReturn['income']
                        trafficService = trafficService + valReturn['traffic']
                        discountedValueService = discountedValueService + (valueService / math.pow( 1 + constants['monthlyReturnOnInvestmentRate'], period))
                        discountedCostService = discountedCostService + (( constants['monthlyFixedCosts'] * paramService['usagePercentage'] / 100)  / math.pow( 1 + constants['monthlyReturnOnInvestmentRate'], period)) 
                    profits[paramService['name']] = discountedValueService - discountedCostService
                    traffic[paramService['name']] = trafficService 
                line = "Configuration" + ','  'InvestmentRate:,' +  str(constants['annualReturnOnInvestmentRate']) + ',Backhaul:,' + str(constants['costBackhaul']) +  ',Realtime:,' + str(constants['costByChannel']) + ',0.6'  + ',' + str(configurationDic['Http']) + ',' + str(configurationDic['VozIp'])  + ',' + 'profit,' +  str(profits) + ',' + 'traffic' + ',' + str(traffic) + "\n"
                fileResult.writelines(line) # Write a sequence of strings to a file                              
            fileResult.close()
        except IOError:
            pass
    
    def calculateProfitByService(self, constants, demandDataBusinessDays, demandDataWeekends, period, configuration, service, paramService, continuosDemandData, optimizationOutput):

        valueProfitBusinessDays = 0
        valueTrafficBusinessDays = 0
        valueProfitWeekEnd = 0
        valueTrafficWeekEnd = 0
        valReturn = 0
        returnDict = {} 
        if paramService['delayTolerant'] == 'N':
            for hour in range(constants['initWorkingHour'],constants['finalWorkingHour']):
                demand = demandDataBusinessDays[hour][period + 1]                                  
                varReturn = self.calculateIncomeByHourService( service, demand, 'businessDays', paramService, configuration, period, constants, continuosDemandData, optimizationOutput)
                valueProfitBusinessDays = valueProfitBusinessDays + varReturn['valueService']
                valueTrafficBusinessDays = valueTrafficBusinessDays + varReturn['traffic']
                demand = demandDataWeekends[hour][period + 1]
                varReturn = self.calculateIncomeByHourService( service, demand, 'weekEnds',paramService, configuration, period, constants, continuosDemandData, optimizationOutput)
                valueProfitWeekEnd = valueProfitWeekEnd + varReturn['valueService']
                valueTrafficWeekEnd = valueTrafficWeekEnd + varReturn['traffic']

            valueService = ( valueProfitBusinessDays * 20 ) + ( valueProfitWeekEnd * 10 )
            trafficService = ( valueTrafficBusinessDays * 20 ) + ( valueTrafficWeekEnd * 10 )
            discountedValueService = (valueService / math.pow( 1 + constants['monthlyReturnOnInvestmentRate'], period))
            numSevers = self.getServiceForServer( service, period, constants, optimizationOutput)
            costService = ( constants['monthlyFixedCosts'] * paramService['usagePercentage'] / 100 ) + ( numSevers * constants['costByChannel']  )
            discountedCostService = ( costService   / math.pow( 1 + constants['monthlyReturnOnInvestmentRate'], period))
            profit = discountedValueService - discountedCostService 
            returnDict = {'profit' : profit, 'trafficService': trafficService}
            #print service + 'period:' + str(period) +  ':' + str(valReturn)
                         
        else:
            dinamicPeriod = np.floor(period / constants['MonthsByRevisionPeriod'])
            if dinamicPeriod >= constants['maxPeriods']:
                dinamicPeriod = constants['maxPeriods'] - 1
            
            periodDecision = optimizationOutput[str(int(dinamicPeriod))]
            assigment = periodDecision['assignment']  
            decision = periodDecision['decision']
            decisionOut = decision.split(',') 
            serversForService = assigment[service]
            model = pricing.pricingModel()
            maxProfit = 0
            i = serversForService   
            maxServer = 0
            serverResults ={}
            while (i >= 0):
                season = 'businessDays'
                optimalPoliciyDTNBusinessDays = model.calculateOptimalAssignmentByDay( paramService, period, constants, continuosDemandData, season, i, True)
                incomeDtn = optimalPoliciyDTNBusinessDays['income']
                #profitDtn = optimalPoliciyDTNBusinessDays['profit']
                trafficBusinessDays = optimalPoliciyDTNBusinessDays['demand']
                k2businessDays = optimalPoliciyDTNBusinessDays['maxK2']
                meanMBytesPerService = configuration * paramService["load"]
                #print 'meanMBytesPerService:' + str(meanMBytesPerService) + str(configuration)
                servicesDtn = math.ceil(trafficBusinessDays /  meanMBytesPerService)
                # the total profits is equal to profits plus access' income
                valueServiceBusinessDays = ( incomeDtn ) + (paramService['priceAccess'] * servicesDtn  )
                #print 'businessDays:' + 'profit:' +str(profitDtn) + ' income:' + str(incomeDtn) +  'Traffic:' + str(trafficBusinessDays) + 'valueServiceBusinessDays:' + str(valueServiceBusinessDays)
                        
                season = 'weekEnds'
                optimalPoliciyDTNWeekEnds = model.calculateOptimalAssignmentByDay( paramService, period, constants, continuosDemandData, season, i, True)
                incomeDtn = optimalPoliciyDTNWeekEnds['income']
                profitDtn = optimalPoliciyDTNWeekEnds['profit']
                trafficWeekEnds = optimalPoliciyDTNWeekEnds['demand']
                k2WeekEnds = optimalPoliciyDTNWeekEnds['maxK2']
                meanMBytesPerService = configuration * paramService["load"]
                servicesDtn = math.ceil(trafficWeekEnds /  meanMBytesPerService)
                # the total profits is equal to profits plus access' income
                valueServiceWeekends =  ( incomeDtn ) + (paramService['priceAccess'] * servicesDtn  )
                #print 'weekEnds:' + 'profit:' + str(profitDtn) + 'income:' + str(incomeDtn) + 'Traffic:' + str(trafficWeekEnds) + 'valueServiceBusinessDays:' + str(valueServiceWeekends)

                if k2WeekEnds > k2businessDays:
                    k2Max = k2WeekEnds
                else:
                    k2Max = k2businessDays
                channels = model.numberOfServersRequired(constants, k2Max)
                #print 'k2businessDays:' + str(k2businessDays) + 'k2WeekEnds:' + str(k2WeekEnds)

                valueService = (valueServiceBusinessDays * 20 ) + (valueServiceWeekends * 10) - (i * constants['costByChannel']) - constants['costBackhaul']
                #print 'i' + str(i)  + 'valueService:' + str(valueService)
                traffic = (trafficBusinessDays * 20 ) + (trafficWeekEnds * 10)
                discountedValueService = (valueService / math.pow( 1 + constants['monthlyReturnOnInvestmentRate'], period))
                costService = constants['monthlyFixedCosts'] * paramService['usagePercentage'] / 100 
                discountedCostService = ( costService   / math.pow( 1 + constants['monthlyReturnOnInvestmentRate'], period)) 
                profit = discountedValueService - discountedCostService
                #print 'Period:,' + 'valueService:' + str(valueService) + str(period) + ',number of servers:' + str(i) + ',profit:,' + str(profit) + ',traffic:,' + str(traffic)
                serverResults[i] = {'profit':profit, 'trafficService':traffic} 
                if (i == serversForService):
                    maxProfit = profit
                    maxServer = i
                else:
                    if (profit > maxProfit):
                        maxProfit = profit
                        maxServer = i
                i = i - 1         
            
            #print 'Period:' + str(period) + 'maxServer:' + str(maxServer) + ' Profit:' + str(serverResults[maxServer]['profit']) + ' Traffic:' + str(serverResults[maxServer]['trafficService'])
            returnDict = {'profit':serverResults[maxServer]['profit'], 'trafficService':serverResults[maxServer]['trafficService']}
                
            #if period == 0: 
            #    grap = gra.graphicClass()
            #    grap.graphDTNOptimalPolicy(constants, 'businessDays', optimalPoliciyDTNBusinessDays, 'weekEnds', optimalPoliciyDTNWeekEnds)

            #print service + 'period:' + str(period) +  ':' + str(valReturn)
        return returnDict

    def executeStochastic(self, listaEjecucion, constants, demandDataBusinessDays, demandDataWeekends, continuosDemandData):
        self.calculateMonthlyInvestmentRate(constants)

        try:
            # This will create a new file or **overwrite an existing file**.
            filename = 'fileResultStochastic' + str(constants['annualReturnOnInvestmentRate']) + '.txt'
            fileResult = open(filename, "a")
            for item in listaEjecucion:
                paramList = listaEjecucion[item]
                configurationDic = eval(item)
                if( True ): # This if is created to control configurations.
                    configurationDic = eval(item)
                    try:
                        path = path.expanduser('~/workspace/NetworkOptimization/Optimization/optimalFiles/') 
                        fileName = path +  "Configuration" + '-Mail-' + '0.6'  + 'Http-' + str(configurationDic['Http']) + 'VozIp-' + str(configurationDic['VozIp']) + '.txt'
                        file = open(fileName, "r")
                        optimizationOutput = file.readline() # this line corresponds to start date-time
                        optimizationOutput = ast.literal_eval(file.readline()) # this is the dictionary result
                        traffic={}
                        profits ={}
                        prices ={}
                        betaTime = {}
                        for service in paramList:
                            paramService = paramList[service]
                            discountedValue = 0
                            trafficValue = 0
                            for period in range(int(constants['maxInvestementPeriods'])):
                                configuration = configurationDic[service]
                                valReturn = self.calculateProfitByService(constants, demandDataBusinessDays, demandDataWeekends, period, configuration, service, paramService, continuosDemandData, optimizationOutput)
                                #valReturn = {'profit': 0, 'trafficService' : 0}
                                discountedValue = discountedValue + valReturn['profit'] 
                                trafficValue = trafficValue + valReturn['trafficService']
                            prices[paramService['name']] = paramService['priceAccess']
                            betaTime[paramService['name']] = paramService['betaTime']
                            profits[paramService['name']] = discountedValue
                            traffic[paramService['name']] = trafficValue 
                        #print discountedValue
                        file.close()            
                    except IOError:
                        pass
                    #line = "Configuration" + ',' + str(configurationDic['Mail'])  + ',' + str(configurationDic['Http']) + ',' + str(configurationDic['VozIp'])  + ',' + 'profit,' +  str(profits) + ',' + 'traffic' + ',' + str(traffic) + "\n"
                    line = "Configuration" + ','  'InvestmentRate:,' +  str(constants['annualReturnOnInvestmentRate']) + ',Backhaul:,' + str(constants['costBackhaul']) +  ',Realtime:,' + str(constants['costByChannel']) + ',Phro:,' + str(constants['phro']) + ',0.6'  + ',' + str(configurationDic['Http']) + ',' + str(configurationDic['VozIp'])  + ',' + 'price,' + str(prices) + ',' + ', betaTime,' + str(betaTime) + ','  'profit,' +  str(profits) + ',' + 'traffic' + ',' + str(traffic) + "\n"
                    fileResult.writelines(line) # Write a sequence of strings to a file
            fileResult.close()
        except IOError:
            pass
        
    def generateCapacityPrice(self, listaEjecucion, constants):
        for item in listaEjecucion:
            paramList = listaEjecucion[item]
            configurationDic = eval(item)
            #if( configurationDic['Mail'] == 0.6  ): 
            if ( ( configurationDic['Mail'] == 0.6  ) or (configurationDic['Mail'] == 1.0 ) or (configurationDic['Mail'] == 2.0 ) or (configurationDic['Mail'] == 4.0 ) or ( configurationDic['Mail'] == 6.0  ) or ( configurationDic['Mail'] == 10.0  ) ) :
                configurationDic = eval(item)
                try:
                    pathText = path.expanduser('~/workspace/NetworkOptimization/Optimization/optimalFiles/') 
                    fileName = pathText + "Configuration" + '-Mail-' + str(configurationDic['Mail'])  + 'Http-' + str(configurationDic['Http']) + 'VozIp-' + str(configurationDic['VozIp']) + '.txt'
                    file = open(fileName, "r")
                    print fileName
                    optimizationOutput = file.readline() # this line corresponds to start date-time
                    optimizationOutput = ast.literal_eval(file.readline()) # this is the dictionary result
                    for service in paramList:
                        paramService = paramList[service]
                        try:
                            # This will create a new file or **overwrite an existing file**.
                            fileNameCapacity = "fileResultCapacity" + service
                            fileResult = open(fileNameCapacity, "a+")
                            lineService = ''
                            for period in range(int(constants['maxPeriods'])):
                                periodDecision = optimizationOutput[str(int(period))]
                                assigment = periodDecision['assignment']  
                                decision = periodDecision['decision']
                                decisionOut = decision.split(',') 
                                priceService = float(decisionOut[paramService['index'] + 1])
                                lineService = lineService + ',' + str(period) + ',' + str(assigment[service]) + ',' + str(priceService) 
                            line = "Configuration" + ',' + str(configurationDic['Mail'])  + ',' + str(configurationDic['Http']) + ',' + str(configurationDic['VozIp'])  + "," + lineService + "\n"
                            fileResult.writelines(line) # Write a sequence of strings to a file
                            fileResult.close()

                        except IOError:
                            pass
                     
                except IOError:
                    pass

  
