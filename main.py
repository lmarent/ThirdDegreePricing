__docformat__ = "restructuredtext en"
import Parameters as param
import economicEvaluator as economicEval
import DTNCoreProcedures as coreDtn
import proportionalDTNPricing as pricing 
import graphics
import numpy as np
import math
import graphics as gra
import datetime
from Technologies import Technology_Container
from Services import Services_Container
from demandModel import ClustersContainer
from os import path
from DemandMarketEquilibriumAlgorithm import Algorithm
from Customer import Customer



def executeAlgorithm(general_parameters, technology_container, service_container, cluster_container, customer):
     
    # This value corresponds to the the percentage of the cost put on the technology parameters
    realTimeCostInit = 40
    realTimeCostIncr = 60
    realTimeCostEnd = 40
    
    continuousModel = economicEval.ContinuousEconomicModel()    
    realtimeValue = realTimeCostInit
    while (realtimeValue <= realTimeCostEnd):                  
        technology_container.set_real_time_technology_costs(realtimeValue)
        #print technology_container.__str__()
        continuousModel.executeLongTermScenario( general_parameters, cluster_container, technology_container, service_container, customer)            
        realtimeValue = realtimeValue + realTimeCostIncr
        

def executeContinuosModel(general_parameters, technology_container, service_container, cluster_container, customer):
    # This value corresponds to the the percentage of the cost put on the technology parameters  
    backHaulCostInit = 100
    backHaulCostIncr = 40
    backHaulCostEnd = 100
    
    InvestRateInit = 0.08
    InvestRateIncr = 0.06
    InvestRateEnd = 0.08
    investRateValue = InvestRateInit
    while (investRateValue <= InvestRateEnd): 
        # Creates a new file, with this part a previous file is erased.
        backHaulCostValue = backHaulCostInit
        while (backHaulCostValue <= backHaulCostEnd):                  
            general_parameters.set_annual_investment_rate(investRateValue)
            general_parameters.calculateMonthlyInvestmentRate()
            print general_parameters.get_monthly_investment_rate()
            technology_container.set_backhaul_technology_costs(backHaulCostValue)
            executeAlgorithm(general_parameters, technology_container, service_container, cluster_container, customer)
            backHaulCostValue = backHaulCostValue + backHaulCostIncr
        investRateValue = investRateValue + InvestRateIncr
        

def executeNoStochasticModel(listaEjecucion, constants, demandHourPeriodBusinessDays, demandHourPeriodWeekends):
    InvestRateInit = 0.02
    InvestRateIncr = 0.06
    InvestRateEnd = 0.14
    economic = economicEval.ContinuousEconomicModel()
    realTimeCostInit = 60
    realTimeCostIncr = 10
    realTimeCostEnd = 170
    
    
    investRateValue = InvestRateInit 
    while (investRateValue <= InvestRateEnd): 
        # Creates a new file, with this part a previous file is erased.
        try:
            filename = 'fileResultNoStochastic' + str(investRateValue) + '.txt'
            fileResult = open(filename, "w")
            fileResult.close()
        except IOError:
            pass             
        constants['annualReturnOnInvestmentRate'] = investRateValue
    
        realtimeValue = realTimeCostInit
        while (realtimeValue <= realTimeCostEnd):                  
            constants['monthlyFixedCosts'] = realtimeValue * 8 # they are using eight channels
            constants['costByChannel'] = realtimeValue
            economic.executeNoStochastic(listaEjecucion, constants, demandHourPeriodBusinessDays, demandHourPeriodWeekends)
            realtimeValue = realtimeValue + realTimeCostIncr
        investRateValue = investRateValue + InvestRateIncr


        
constants = {}
listaEjecucion = {}
capacityIncrements = []
serviceParameters = {}
clusterData = {}

# These line codes load required parameters and build running scenarios 
#demandData = param.loadDemandIncreasePattern()
#param.loadClusterParameters(clusterData)
#param.loadConstants(constants)
#error, error_description = param.loadServiceParameters(serviceParameters)
#if (error == False):
#    param.loadParameters(constants, clusterData, serviceParameters, listaEjecucion)
#    print 'Total Traffic'
#    print totalTrafficWeekDays
#    print totalTrafficWeekends
#error = param.loadCapacityIncrements(capacityIncrements)
#maxExecutions = 1
#numExecutions = 0
#algorithm = dinamicAlgorithm()
#algorithm.execute(listaEjecucion, constants, demandData)

# Establish the fixed cost by service 
#now = datetime.datetime.now()
#print "Current date and time using str method of datetime object:"
#print str(now)


#relative_path = 'workspace/NetworkOptimization/Optimization/Parameters'

#general_parameters = param.GeneralParameters()
#general_parameters.read_from_file(relative_path, 'constants.csv')

#technologies_container = Technology_Container(general_parameters)
#error, error_description = technologies_container.read_technologies_from_file(relative_path, 'TechnologyParameters.csv')
#print technologies_container.__str__()

#if error==False: 
#    service_container = Services_Container()
#    error, error_description = service_container.read_services_from_file(relative_path, 'ServiceParameters.csv')
# 
#    cluster_container = ClustersContainer('BassModelDiscrete', 'demandChangeFunction3', general_parameters)
#    cluster_container.read_from_file( relative_path, 'clusterInformation.csv', 'demandaGeneral.csv')
#    diffusion_parameters = []
#    diffusion_parameters.append(0.00001)
#    diffusion_parameters.append(0.13)
#    diffusion_parameters.append(cluster_container.get_total_demand())
#  
#    cluster_container.get_difussion_model().set_parameters(diffusion_parameters)
#    cluster_container.generate_diffusion_estimated_demand()
#    try:
#        # delete content of the results file.
#        relative_path = general_parameters.get_results_relative_path()
#        print relative_path
#        filename = general_parameters.get_general_file_results()
#        print filename 
#        fname = path.expanduser('~/' + relative_path + '/' + filename)
#        fileResult = open(fname, "w")    
#        fileResult.close()
#               
#        relative_path = general_parameters.get_results_relative_path()
#        filename = general_parameters.get_detail_file_results()
#        fname = path.expanduser('~/' + relative_path + '/' + filename)
#        fileResult = open(fname, "w")    
#        fileResult.close()
#        customer = Customer('Hospital',1)
#        services = service_container.get_services()
#        for service_index in services:
#            service = services[service_index]
#            price_sensitivity = service.get_price_sensitivity()
#            time_sensitivity = service.get_time_sensitivity()
#            time_sensitivity = math.pow(service.get_time_sensitivity() * 2,2)
#            time_sensitivity = 0.05 
#            optimal_quality_value = 2
#            customer.add_service(service, price_sensitivity, time_sensitivity, optimal_quality_value)
#            customer.set_sigma(0) 
#        executeContinuosModel(general_parameters, technologies_container, service_container, cluster_container, customer)
#    except IOError:
#        pass             
#  
#else:
#    print error_description

relative_path = 'workspace/NetworkOptimization/Optimization/Graphics/2010_data'
#file_name = 'DiffusionData.csv'
file_name = 'TrafficEvolution'

#file_name = 'OptimalAssigment'
#file_name = 'EconomiesScale.csv'
#file_name_profit = 'BehaviourMixedProfits.csv'
#file_name_traffic = 'BehaviourMixedTraffic.csv'
#file_name_traffic = 'AnchorCustomerPriceEvolution.csv'
file_name = 'OptimalAssigment.csv'


graphic = gra.graphicClass()
#graphic.graphDemandAgaintsParameter(relative_path, file_name)
#graphic.graphEconomiesScale(relative_path, file_name)
#graphic.graphEconomiesScaleProfits(relative_path, file_name)
#graphic.graphEconomiesScaleTraffic(relative_path, file_name)
#graphic.graphTrafficByService(relative_path, file_name)
#graphic.graphTrafficByServiceOldData(relative_path, file_name)
#graphic.graphOptimalAssigmentPrice(relative_path, file_name)
#graphic.graphOptimalAssigmentTraffic(relative_path, file_name)
#graphic.graphBehaviourMixedOperators(relative_path, file_name_profit, file_name_traffic)
#graphic.graphBehaviourMixedOperators2(relative_path, file_name_profit, file_name_traffic)
#graphic.graphBehaviourMixedOperators3(relative_path, file_name_profit, file_name_traffic)
#graphic.graphOptimalAssigmentAnchorCustomer(relative_path, file_name_traffic)
#graphic.graphOptimalAssigmentAnchorCustomerPrice(relative_path, file_name_traffic)
#graphic.graphOptimalAssigmentAnchorCustomerFlow(relative_path, file_name_traffic)
#graphic.graphOptimalAssigmentFlow(relative_path, file_name)
graphic.graphOptimalAssigmentPrice(relative_path, file_name)

#economic.executeStochastic(listaEjecucion, constants, demandHourPeriodBusinessDays, demandHourPeriodWeekends, continuosDemandData)

#period = 0
#service = 'Http'
#season = 'businessDays'
#model.basicTestPolicy(constants, service, period, continuosDemandData, season)

#print continuosDemandData           
#filename = "/home/luis/Documents/Tesis/PaperElaborados/paperPricesDelayTolerantServices/generalResults.csv"          


#graphic.graphProfitChange(filename)          

#executeContinuosModel(listaEjecucion, constants, demandHourPeriodBusinessDays, demandHourPeriodWeekends, continuosDemandData)
# executeNoStochasticModel(listaEjecucion, constants, demandHourPeriodBusinessDays, demandHourPeriodWeekends)




now = datetime.datetime.now()
print "Current date and time using str method of datetime object:"
print str(now)


#economic.generateCapacityPrice(listaEjecucion, constants)


# This code is made in order to test specific functions


try:
        # This will create a new file or **overwrite an existing file**.
        file = open("debug.txt", "a")
        file.writelines('Inicio') # Write a sequence of strings to a file
        file.close()
except IOError:
    pass
