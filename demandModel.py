'''
Created on Jan 18, 2013

@author: luis
'''
from __future__ import division
import numpy as np
from os import path
from numpy import genfromtxt
from math import exp
from math import pow
from collections import OrderedDict
from Parameters import GeneralParameters 
#import matplotlib.pyplot as plt

class DifussionModel(object):
    def __init__(self): pass
        
        
class TonicModel(DifussionModel):
    def __init__(self):
        # The class expects a list with the list of parameters, in this case it expects three parameters 0,1,2
        self._parameter_a = 0
        self._parameter_b = 0
        self._parameter_c = 0
        super(TonicModel, self).__init__()
    
    def set_parameters(self, parameters):
        self._parameter_a = parameters[0]
        self._parameter_b = parameters[1]
        self._parameter_c = parameters[2]
    
    def __str__(self):
        str_return = 'parameter_a:' + str(self._parameter_a) + 'parameter_b:' + str(self._parameter_b) + \
                      'parameter_c:' + str(self._parameter_c)
        return str_return
        
    def calculate_estimated_demand_value(self, parameters):
        saturation_point = parameters[0]
        period = parameters[1]
        exponent = self._parameter_a + (self._parameter_b * period)
        divisor = ( 1 + exp(exponent))
        divisor = pow(divisor, self._parameter_c) 
        val_return = saturation_point / divisor
        return val_return 


class BassModelDiscrete(DifussionModel):
    def __init__(self):
        # The class expects a list with the list of parameters, in this case it expects three parameters 0,1,2
        # p value from the model
        self._innovation_coef = 0
        # q value from the model   
        self._immitation_coef = 0
        # m value from the model
        self._potential_market = 0
        super(BassModelDiscrete, self).__init__()

    def set_parameters(self, parameters):
        self._innovation_coef = parameters[0]
        self._immitation_coef = parameters[1]
        self._potential_market = parameters[2]


    def calculate_estimated_demand_value(self, parameters):
        # correspond to the previous cumulative adapters with respect to the potential market
        previous_adopters = parameters[0]
        #print 'Imitation Coeficient:' + str(self._immitation_coef) + ',Innovation Coeficient:' + str(self._innovation_coef) + ', Potential Market:' + str(self._potential_market) + ', Previous adopters:' + str(previous_adopters) 
        value1 = self._innovation_coef * self._potential_market
        value2 = ( self._immitation_coef - self._innovation_coef) * previous_adopters
        value3 = ( self._immitation_coef / self._potential_market) * pow(previous_adopters, 2)
        val_return = value1 + value2 - value3
        return val_return 

class DemandFunctions(object):
    def __init(self): pass

    def demandChangeFunction(self, x, Pk, Pmax, n, A, lamdai):
        print 'demandChangeFunction initial parameters'
        print str(x) + ' ' + str(Pk) + ' ' + str(Pmax) + ' ' + str(n) + ' ' + str(A) + ' ' + str(lamdai)
        print 'demandChangeFunction End parameters'
        k = A 
        if (0 <= x) and (x <= Pk):
            PMiddle = Pk/2
            if (0 <= x) and (x <= PMiddle): 
                porcentage = (PMiddle -x )/ PMiddle 
                xprima = porcentage *-6  
            else:
                porcentage = (x - PMiddle )/ PMiddle 
                xprima = porcentage * 6 
            y = 1 / (1 + np.power(np.e,-xprima))
            y = (1-y) * k
        else:
            PMiddle = Pk + (Pk/2)
            if (Pk <= x) and (x <= PMiddle): 
                porcentage = (PMiddle -x )/ ( PMiddle - Pk ) 
                xprima = porcentage *-6  
            else:
                porcentage = (x - PMiddle )/ ( PMiddle - Pk ) 
                xprima = porcentage * 6 
            y = 1 / (1 + np.power(np.e,-xprima))
            y = -y * lamdai  
        print 'demandChangeFunction initial Output'
        print 'y:' + str(y)
        print 'demandChangeFunction End Output'
        return y


    def demandChangeFunction2(self, x, Pk, Pmax, n, A, lamdai):
        #print 'demandChangeFunction initial parameters'
        #print str(x) + ' ' + str(Pk) + ' ' + str(Pmax) + ' ' + str(n) + ' ' + str(A) + ' ' + str(lamdai)
        #print 'demandChangeFunction End parameters'
        y = 0
        if (0 <= x) and (x <= Pmax):
            PMiddle = Pmax/2
            if (0 <= x) and (x <= PMiddle): 
                porcentage = (PMiddle -x ) / PMiddle 
                xprima = porcentage *-6  
            else:
                porcentage = (x - PMiddle ) / PMiddle 
                xprima = porcentage * 6 
            y = 1 / (1 + np.power(np.e,-xprima))
            y = (1-y) * A
        #print 'demandChangeFunction initial Output'
        #print 'y:' + str(y)
        #print 'demandChangeFunction End Output'
        return y

    def demandChangeFunction3(self, newPrice, oldPrice, oldDemand, elasticity):
        #print 'demandChangeFunction initial parameters'
        #print str(newPrice) +  ' ' + str(oldDemand) + ' ' + str(oldPrice) + ' ' + str(elasticity)
        #print 'demandChangeFunction End parameters'
        
        if oldPrice <> 0:
            percentagePrice = (newPrice - oldPrice) / oldPrice
            newDemand = oldDemand - (percentagePrice * elasticity * oldDemand)
        else:
            newDemand = 0 
        if newDemand < 0:
            newDemand = 0
        return newDemand


    def inverseDemandFuntion3(self, newDemand, oldDemand, oldPrice, elasticity):
        #print 'inverseDemandFuntion3 initial parameters'
        #print str(newDemand) +  ' ' + str(oldDemand) + ' ' + str(oldPrice) + ' ' + str(elasticity)
        #print 'inverseDemandFuntion3 End parameters'
        
        if oldDemand <> 0:
            percentageDemand = (newDemand - oldDemand) / oldDemand
            newPrice = oldPrice - (( percentageDemand* oldPrice ) / elasticity )
        else:    
            newPrice = 0
        return newPrice

    

class DemandCluster(object):
    def __init__(self, name, repetitions):
        self._cluster_name = name
        self._cluster_repetitions = repetitions 
        self._hour_demand = {}
    
    def get_name(self):
        return self._cluster_name
    
    def get_repetitions(self):
        return self._cluster_repetitions

    def load_cluster_demand(self, cluster_name, relative_path, file_name, init_hour, end_hour):
        fname = path.expanduser('~/' + relative_path + '/' + file_name)
        clusters_names =  genfromtxt(fname,usecols=0, dtype=str, skip_header=1, delimiter=';')
        demand_data = genfromtxt(fname, delimiter=';')[:,1:]
        hours = demand_data[0,:]
        total_demand = 0
        for cluster in range(len(clusters_names)):
            name = clusters_names[cluster]
            if (cluster_name == name):
                for hour in range(len(hours)): 
                    self._hour_demand[hour] =  demand_data[cluster+1, hour]
                    if hour in range(init_hour, end_hour):
                        total_demand = total_demand  + demand_data[cluster+1, hour] 
            print 'cluster:' + cluster_name + 'demand:' + str(total_demand)
        return total_demand
                    

    def __str__(self):
        str_return = 'name:' + self._cluster_name + ' Demand by hour:' + self._hour_demand.__str__()
        return str_return 
    
    def get_actual_demand(self, contraction_parameter):
        actual_demand = {}
        for hour in self._hour_demand:
            demand_value = self._hour_demand[hour] * contraction_parameter
            actual_demand[hour]= demand_value    
        #print actual_demand
        return actual_demand 

    def exploit_cluster_demand(self, service, demand_function, hour_demand, init_hour, end_hour, base_price):
        # This method return the demand at the minute level, depending on the service demand is given in MBs or minutes.
        #print base_price
        newPrice = 0
        data_by_hour = {}
        for hour in range(init_hour, end_hour):
            if hour < 23: 
                nextHour = hour + 1
            else:
                nextHour = 0  
            # Bring the demand point and the following point. 
            # Demand must be expressed in the units of traffic ( Megabytes)
            demandNew = (hour_demand[nextHour] * service.get_usage_percentage()) 
            demandNew = demandNew / 60 # we want the demand by minute in this case. 
            # Demand must be expressed in the units of traffic ( Megabytes)
            demand = (hour_demand[hour] * service.get_usage_percentage())
            demand = demand / 60
            #print service.get_name() + ':hour:' + str(hour) + ':demand:' + str(demand) + ':demandNew:' + str(demandNew)
            # Calculate the Slope and intercept
            slope = ( demandNew - demand ) # the step size in x is 1 hour, so that why we don't divide by X1 - Xo
            # This intercept is the result that demand is a line that start at the zero hour of the day, so it must be 
            # suffer a translation. 
            intercept = demand - ((demandNew - demand)* hour) 
            # construct the demand by minute               
            data_by_minute = {}
            sumBetaPriceHour = 0
            demandHour = 0                        
            for minute in range (0,60):
                horaMinute = float(hour + (minute / 60))
                demand = (slope * horaMinute) + intercept
                potentialMarket = demand_function.demandChangeFunction3(newPrice, base_price, demand, service.get_elasticity())
                betaPriceValue = (potentialMarket - demand) / base_price
                data_by_minute[minute] = { 'demand': demand, 'potentialMarket': potentialMarket, 'betaPrice' : betaPriceValue }
                #if (service.get_name() == 'Mail') and (5 <= hour) and  (hour <= 13):
                #if (service.get_name() == 'Mail') and (hour >= 14):     
                #    print service.get_name() + ':' + str(horaMinute) + ':hour:' + str(hour) + ':minute:' + str(minute) + ':demand:' + str(demand) + ':potentialMarket:' + str(potentialMarket)  + ':betaPrice:' + str(betaPriceValue)                
                sumBetaPriceHour = sumBetaPriceHour + betaPriceValue
                demandHour = demandHour + demand  
            sumBetaPriceHour = sumBetaPriceHour / 60
            #print 'hour:' + str(hour) + ':beta price:' + str(sumBetaPriceHour)
            data_by_hour[hour] = {'data' :data_by_minute , 'slope' : slope, 'intercept' : intercept, 
                                  'betaPrice' : sumBetaPriceHour, 'income' : 0.0, 'totDemand' : demandHour}
         
        #try:
        #    # This will create a new file or **overwrite an existing file**.
        #    file = open("debug.txt", "a")
        #    if service._name == "Http":
        #        file.writelines('service:' + service.get_name() + 'init_hour:' + str(init_hour) + 'end_hour:' + str(end_hour))
        #        file.writelines(self.printDemandResults(data_by_hour, 'potentialMarket').__str__()  + '\n')
        #        file.writelines(self.printDemandResults(data_by_hour, 'demand').__str__() + '\n')
        #        file.writelines(self.printDemandResults(data_by_hour, 'betaPrice').__str__() + '\n')
        #        file.close()
        #except IOError:
        #        pass
                
        return data_by_hour

    def printDemandResults(self, dictionary, desiredElement):
        # this method is for debug and testing purposes. it contruct a list with one specific element of the policy\
        listResult = []
        for hour in dictionary:
            dictionaryReturnHour = dictionary[hour]
            for minute in dictionaryReturnHour['data']:
                dictionaryReturnMinute = dictionaryReturnHour['data'][minute]
                value = dictionaryReturnMinute[desiredElement]
                listResult.append(value)
        return listResult  

class ClustersContainer(object):
    def __init__(self, difussion_class_name, demand_function, general_parameters):
        self._clusters = {}
        diffusionn_class =  globals()[difussion_class_name]
        self._difussion_model = diffusionn_class()
        self._demand_function = demand_function
        self._demand_function_instance =  DemandFunctions()
        self._general_parameters = general_parameters
        # The diffusion process is calculated against  the total traffic in all clusters. 
        self._total_demand = 0
        # This structure contain the demand evolution in time given by the difussion process
        # the demand evolution is given as a percentage of the total demand.
        self._demand_evolution = {}

    def verify_names(self,names):
        error = False
        error_description = 'None'
        nonrepeted = list(OrderedDict.fromkeys(names))
        num_elements = nonrepeted.__len__()
        if num_elements < len(names):
            error = True
            error_description = 'Duplicate names for demand cluster, they must be unique'
        return error, error_description      

    def read_from_file(self, relative_path, file_name, file_name_demand):
        fname = path.expanduser('~/' + relative_path + '/' + file_name)
        names = genfromtxt(fname,usecols=0, dtype=str, skip_header=1, delimiter=';')
        clusterRepetitions = genfromtxt(fname, delimiter=';', usecols=1, skip_header=1)
        error = False
        error_description = 'None'
        if (names.size == 0):
            error = True
            error_description = 'No clusters have been defined'
        else:
            # The reason to divide the cases in 0,1 and more data is because numpy handled different 
            # arrays as they have different number of elements. 
            if (names.size == 1):
                name = names[()]
                cluter_repetitions = clusterRepetitions[()] 
                cluster = DemandCluster(name, cluter_repetitions)
                cluster_demand = cluster.load_cluster_demand(name, relative_path, file_name_demand, 
                                                             self._general_parameters.get_init_working_hour(), 
                                                             self._general_parameters.get_final_working_hour())
                self._clusters[name] = cluster
                self._total_demand += (cluster_demand * cluster.get_repetitions())
            else:
                error, error_description = self.verify_names(names)
                if (error==False):
                    for index in range(len(names)):
                        name = names[index]
                        repetition = clusterRepetitions[index] 
                        cluster = DemandCluster(name, repetition)
                        cluster_demand = cluster.load_cluster_demand(name, relative_path, file_name_demand, 
                                                    self._general_parameters.get_init_working_hour(), 
                                                    self._general_parameters.get_final_working_hour())
                        self._clusters[name] = cluster
                        self._total_demand += (cluster_demand * cluster.get_repetitions())
        return error, error_description
    
    def get_difussion_model(self):
        return self._difussion_model
                          
    def get_demand_function(self):
        return self._demand_function_instance

    def get_total_demand(self):
        return self._total_demand

    def generate_diffusion_estimated_demand(self):    
        parameters =  []
        print 'total demand ' + str(self._total_demand)
        parameters.append(self._total_demand * self._general_parameters.get_inital_demand_percentage())
        for period in range(self._general_parameters.get_max_investment_period()):
            self._demand_evolution[period] = parameters[0] / self._total_demand
            new_traffic = self._difussion_model.calculate_estimated_demand_value(parameters)
            parameters[0] += new_traffic
            

    def get_clusters(self):
        return self._clusters
    
    def get_demand_evolution(self):
        return self._demand_evolution


#x = np.linspace(0,194,30)
#vecfunc = np.vectorize(demandChangeFunction2)
#vecFunc2 = np.vectorize(demandChangeFunction3)
#Pk=60 
#Pmax = 174
#n = 3 
#A = 697.089 
#lamdai = 9.16827303506
#y1 = vecfunc(x, Pk, Pmax, n, A, lamdai)
##y2 = vecFunc2(x)
##print y2
## Create the plot
#plt.plot(x,y1)
##plt.plot(x,y2)
##
## Save the figure in a separate file
#plt.savefig('sine_function_plain.png')
## Draw the plot to the screen
#plt.show()
#####
### print demandChangeFunction2(72.8, 104, 120, 3, 15, 9.16827303506)

#demand = DemandFunctions()
#potential_market1 = demand.demandChangeFunction3(0, 0.02, 0.8, 1.6)
#potential_market2 = demand.demandChangeFunction3(0, 0.02, (0.8 * 0.3), 1.6)
#print 'potential_market1:' + str(potential_market1)
#print 'potential_market2:' + str(potential_market2)
