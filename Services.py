'''
Created on Mar 12, 2014

@author: luis
'''
from __future__ import division
import math
from collections import OrderedDict
from os import path
from numpy import genfromtxt
from collections import deque
from operator import itemgetter
from DTNCoreProcedures import backHaulCycleTimeMethods

class Services(object):
    '''
    classdocs
    '''
    DELAY_TOLERANT = 1
    REAL_TIME = 2
    UNDEFINED = 0
    UNLIMITED_MARKET_PRICE = 100000

    def __init__(self, name, service_type, price_sensitivity, time_sensitivity, elasticity, load_MB_mi, usage_percentage, price_access, price_use, time_average):
        '''
        Constructor
        '''
        # potential market is a structure with the following structure
        # hour, data as a key that agregates all minute information and then minute
        self._name = name
        self._potential_market = {} 
        self._price_sensitivity = price_sensitivity
        self._time_sensitivity = time_sensitivity
        self._type = service_type
        self._elasticity = elasticity
        self._load_MB_mi = load_MB_mi
        # This value is between 0 and 100
        self._usage_percentage = usage_percentage
        self._price_access = price_access
        self._price_use = price_use
        self._time_average = time_average
        self._assigments = {}
        self._assigments_detail = {}
        # These variables will carry the information for the consolidation process 
        self._prices ={}
        self._potential_market_contribution = 1
        #TODO: Verify that values make sense
    
    def __str__(self):
        str_return = 'name:' + self._name + 'price_sensitivity:' + str(self._price_sensitivity) + 'time_sensitivity:' + str(self._time_sensitivity) \
                      + 'type:' +  str(self._type) + 'elasticity:' + str(self._elasticity) + 'usage_percentage:' + str(self._usage_percentage)
        return str_return
    
    def set_potential_market(self, potential_market):
        sensitivity_price = 0
        elements = 0
        for hour in potential_market:
            dictionaryReturnHour = potential_market[hour]
            sensitivity_price += dictionaryReturnHour['betaPrice']
            elements += 1  
            for minute in dictionaryReturnHour['data']:
                data_minute = dictionaryReturnHour['data'][minute]
                value = data_minute['potentialMarket']
                time = (hour * 60) + minute
                self._potential_market[time] = value
        if elements <> 0:
            sensitivity_price = sensitivity_price / elements
        self._price_sensitivity = sensitivity_price
        #print self._name
        print self._potential_market
        #print self._price_sensitivity
    
    def get_name(self):
        return self._name
    
    def get_potential_market_at_time(self,  time):
        return self._potential_market[time]

    def get_price_sensitivity(self):
        return self._price_sensitivity
    
    def get_time_sensitivity(self):
        return self._time_sensitivity
    
    def get_loadMB_Minutes(self):
        return self._load_MB_mi
    
    def get_elasticity(self):
        return self._elasticity
    
    def get_usage_percentage(self):
        return ( self._usage_percentage / 100 )
    
    def get_time_average(self):
        return self._time_average
    
    def update_assigment(self, time, remaining_time, cycle_time, value ):
        # If time already exist, this code updates the assignment. Otherwise it is added.
        self._assigments.setdefault(time,0)
        self._assigments[time] += value
    
    def update_price(self, time, value):
        self._prices[time] = value
    
    def add_assigment_detail(self, time, assigment):
        self._assigments_detail.setdefault(time,[])
        self._assigments_detail[time].append(assigment)
    
    def get_assigment(self, time):
        return self._assigments[time]
    
    def get_detail_assigment(self,time):
        return self._assigments_detail[time]

    def clear_assigments(self):
        self._assigments.clear()
        self._assigments_detail.clear()
        self._prices.clear()

    def get_summary_assigment_statistics(self, time):
        cost = 0
        reduced_capacity_cost = 0
        technology_assignment_tmp = {}
        for item in self._assigments_detail[time]:
            cost += item.get_cost() * item.get_value()
            reduced_capacity_cost +=item.get_capacity_reduced_cost()
            technology_assignment_tmp.setdefault(item.get_technology(),0)
            technology_assignment_tmp[item.get_technology()] += item.get_value() 
        flow = self._assigments[time]
        income = flow * self._prices[time]
        profit = income - cost
        dict_return = {'demand': flow, 'income' : income, 'cost': cost, 'profit': profit, 'reduced_capacity_cost' : reduced_capacity_cost}
        #for technology in technology_assignment_tmp:
        #    dict_return[technology] = technology_assignment_tmp[technology]
        return dict_return
    
    def get_summary_assigments_statistics(self):
        dict_return = {}
        for time in self._assigments:
            val_return = self.get_summary_assigment_statistics(time)
            for element in val_return:
                dict_return.setdefault(element,0)
                dict_return[element] += val_return[element] 
        return dict_return 
    
    def get_detail_assigments(self):
        dic_return = {}
        for time in self._assigments:
            node = {'demand': self._assigments[time], 'price' : self._prices[time], 'detail' : self.get_detail_assigment(time)}
            dic_return[time] = node
        return dic_return 
    
    def get_prices(self):
        return self._prices
    
    def get_assigments(self):
        return self._assigments
    
    def get_type(self):
        return self._type

    def decrement_potential_market_contribution(self,value):
        self._potential_market -= value
    
    def get_potential_market_contribution(self):
        return self._potential_market

class Services_Container(object):        
    def __init__(self):
        self._services = {}

    def verify_type(self,service_type):
        type_return = Services.UNDEFINED
        if service_type == "N":
            type_return = Services.REAL_TIME
        if service_type == "Y":
            type_return = Services.DELAY_TOLERANT
        return type_return    
    
    def verify_names(self,names):
        error = False
        error_description = 'None'
        nonrepeted = list(OrderedDict.fromkeys(names))
        num_elements = nonrepeted.__len__()
        if num_elements < len(names):
            error = True
            error_description = 'Duplicate names for services, they must be unique'
        return error, error_description    
  
    def read_services_from_file(self, relative_path, file_name):
        fname = path.expanduser('~/' + relative_path + '/' + file_name)
        service_name = genfromtxt(fname, delimiter=';', usecols=0, dtype=str, skip_header=1)
        serviceData = genfromtxt(fname,skip_header=1, delimiter=';')
        delayTolerant = genfromtxt(fname, delimiter=';', usecols=13, dtype=str, skip_header=1)
        error = False
        error_description = 'None'
        if service_name.size == 0:
            error = True
            error_description = 'No services have been defined'
        else:
            if service_name.size == 1:
                service_type = self.verify_type(delayTolerant)
                service = Services(service_name, service_type, serviceData[11], serviceData[12], serviceData[8], 
                                   serviceData[9], serviceData[5], serviceData[6], serviceData[7], serviceData[9])
                service_name = service_name[()]
                self._services[service_name] = service
            else:
                usage_percentage = serviceData[:,5]
                price_access = serviceData[:,6]
                price_use = serviceData[:,7]    
                elasticity = serviceData[:,8]
                loadMBMin = serviceData[:,9]  
                betaPrice = serviceData[:,11]
                betaTime = serviceData[:,12]
                time_average = serviceData[:,14]
                error, error_description = self.verify_names(service_name)
                if (error == False):
                    for index in range(len(service_name)):
                        service_type = self.verify_type(delayTolerant[index])
                        service = Services(service_name[index], service_type, betaPrice[index], betaTime[index], elasticity[index], 
                                           loadMBMin[index], usage_percentage[index], price_access[index], price_use[index], time_average[index])
                        self._services[service_name[index]] = service
        return error, error_description
    
    def get_services(self):
        return self._services

    def get_ordered_services(self, time):
        # This function order services on the value as(t)/ beta_price for every moment in time
        # the precondition is that time is included in market potential.
        service_values = []
        service_values_dict = {}
        queue_services = deque()  
        for service_index in self._services:
            mar_potential = self._services[service_index].get_potential_market_at_time(time)
            price_sensitivity =  self._services[service_index].get_price_sensitivity();
            #print 'Time:' + str(time) + service_index + 'Market Potential:' + str(mar_potential) + 'price Sensitivity:' + str(price_sensitivity)
            if (price_sensitivity == 0):
                value_service = int(mar_potential * Services.UNLIMITED_MARKET_PRICE * 1000000) / 1000000.0  # a real big number
            else:
                value_service = int((mar_potential* 1000000) / price_sensitivity ) / 1000000.0
            service_temp = {'service_index' : service_index, 'value': value_service}
            service_values.append(service_temp)
        sorted_services = sorted(service_values, key=itemgetter('value','service_index'), reverse=True)
        #print 'Time:' + str(time) + str(sorted_services) 
        for value_service in sorted_services:
            item = value_service['service_index']
            queue_services.append(item)
        #print queue_services 
        return queue_services


    def get_ordered_services_quality(self, time):
        # This function order services on the value as(t)/ beta_price for every moment in time
        # the precondition is that time is included in market potential.
        service_values = []
        service_values_dict = {}
        queue_services = deque()  
        for service_index in self._services:
            mar_potential = self._services[service_index].get_potential_market_at_time(time)
            time_sensitivity =  self._services[service_index].get_time_sensitivity()
            if (time_sensitivity == 0):
                value_service = int(mar_potential * Services.UNLIMITED_MARKET_PRICE * 1000000 ) / 1000000.0 # a real big number
            else:
                value_service = int((mar_potential * 1000000) / time_sensitivity ) / 1000000.0
            service_temp = {'service_index' : service_index, 'value': value_service}
            service_values.append(service_temp)
        #print  service_values
        sorted_services = sorted(service_values, key=itemgetter('value','service_index'), reverse=True)
        for value_service in sorted_services:
            item = value_service['service_index']
            queue_services.append(item)
        #print queue_services 
        return queue_services
    
    def initialize_services_assigments(self):
        for service_index in self._services:
            self._services[service_index].clear_assigments()
# For test purposes
#print error
#print error_description
#dict = serv_container.get_services()
#for serv in dict:
#    service = dict[serv]
#    print service.__str__()    