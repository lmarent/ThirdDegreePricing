'''
Created on Mar 12, 2014

@author: luis
'''
from __future__ import division

from DTNCoreProcedures import backHaulCycleTimeMethods
from DTNCoreProcedures import CoreMethods
from os import path
from numpy import genfromtxt
from collections import OrderedDict
from operator import itemgetter

class Technologies(object):    
    UNDEFINED = 0
    REALTYPE = 1
    BACKHAULTYPE = 2
    
    def __init__(self, name, technologytime, capacity, cost, monthly_cost, index):
        self._name = name
        self._type = technologytime
        self._capacity = capacity
        self._init_capacity = capacity
        self._cost = cost # This is the cost by MB
        self._init_monthly_cost = monthly_cost
        self._monthly_cost = monthly_cost
        self._index = index
        # Capacity will be a variable time dependant
        self._remaining_capacities = {}
    
    def get_type(self):
        return self._type

    def get_capacity(self):
        return self._capacity
    
    def initialize_capacity(self,init_hour, end_hour, init_minute, end_minute):
        #print 'initialize capacity' + self._name
        # This method handles the capacity within the cycle for the continous policy
        if (self._type == Technologies.BACKHAULTYPE):
            self._remaining_capacities['cycle'] = self._capacity
        else:
            for hour in range(init_hour, end_hour):
                init_minute_range,  end_minute_range = backHaulCycleTimeMethods().get_minute_interval(hour,init_hour, end_hour, init_minute, end_minute)
                for minute in range(init_minute_range,end_minute_range):
                    time = ( hour * backHaulCycleTimeMethods.MINUTES_PER_HOUR ) + minute
                    self._remaining_capacities[time] = self._capacity
            
    def update_capacity(self, time, update_value): 
        if (self._type == Technologies.BACKHAULTYPE):
            self._remaining_capacities.setdefault('cycle', self._capacity)
            #self._remaining_capacities['cycle'] -= update_value
        else:
            self._remaining_capacities.setdefault(time, self._capacity)
            old_value = self._remaining_capacities[time]
            self._remaining_capacities[time] -= update_value
            # print 'update_capacity' + 'time' + str(time) + 'Old Value:' + str(old_value) + str(update_value) + 'New value:' + str(self._remaining_capacities[time])

    def get_remaining_capacity(self, time):
        if (self._type == Technologies.BACKHAULTYPE):
            return self._remaining_capacities['cycle']
        else:
            return self._remaining_capacities[time]

    def calculate_used_capacity(self):
        totalValue = 0
        for assigment in self._assigments:
            totalValue += self._assigments[assigment]
        return totalValue
    
    def __str__(self):
        string_return = ':name:' + self._name + ':type:' + str(self._type) + ':capacity:' + str(self._capacity) + ':cost:' + str(self._cost)
        return string_return   

    def set_cost(self, monthly_cost, cost):
        self._monthly_cost = monthly_cost
        self._cost =cost
    
    def get_init_monthly_cost(self):
        return self._init_monthly_cost
    
    def get_monthly_cost(self):
        return self._monthly_cost
    
    def set_capacity(self, capacity):
        self._capacity = capacity
    
    def get_init_capacity(self):
        return self._init_capacity
          
class BackHaulTechnology(Technologies): 
    def __init__(self,name, technologytime, capacity, cost, montly_cost, index):        
        self._theta0 = 0
        super(BackHaulTechnology, self).__init__(name, technologytime, capacity, cost, montly_cost, index)
 
    def get_cost(self):
        cost_return = (self._cost + self._theta0 )
        return cost_return
 
    def set_theta_zero(self, value):
        self._theta0 = value

    def get_theta_zero(self):
        return self._theta0             
            
class RealTimeTechnology(Technologies):
    def __init__(self, name, technologytime, capacity, cost, montly_cost, index ):        
        self._cost = 0
        super(RealTimeTechnology, self).__init__(name, technologytime, capacity, cost, montly_cost, index)
    
    def get_cost(self):
        return self._cost
     
class Technology_Container(object):
    def __init__(self, general_parameters):
        self._technologies = {}
        self._sortedTechnologies = []
        self._backhaul_technology_used = False
        self._real_technologies_used = False
        self._backhaul = ""
        self._general_parameters = general_parameters
    
    def verify_type(self,technology_type):
        type_return = Technologies.UNDEFINED
        if technology_type == "Real":
            type_return = Technologies.REALTYPE
        if technology_type == "BackHaul":
            type_return = Technologies.BACKHAULTYPE
        return type_return     
    
    def verify_names(self,names):
        error = False
        error_description = 'None'
        nonrepeted = list(OrderedDict.fromkeys(names))
        num_elements = nonrepeted.__len__()
        if num_elements < len(names):
            error = True
            error_description = 'Duplicate names for technologies, they must be unique'
        return error, error_description   
    
    def read_technologies_from_file(self, relative_path, file_name):
        fname = path.expanduser('~/' + relative_path + '/' + file_name)
        names = genfromtxt(fname,usecols=0, dtype=str, skip_header=1, delimiter=';')
        types = genfromtxt(fname,usecols=1, dtype=str, skip_header=1, delimiter=';')
        data = genfromtxt(fname,skip_header=1, delimiter=';')
        dictionary = {}
        error = False
        error_description = 'None'
        if (names.size == 0):
            error = True
            error_description = 'No technologies have been defined'
        else:
            if (names.size == 1):
                name = names[()]
                type_technology = types[()]
                node = {'name': name, 'type': type_technology, 'capacity': data[2], 'cost' : data[3] }
                dictionary[names.size] = node
            else:
                for index in range(len(names)):
                    name = names[index]
                    type_technology = types[index]
                    node = {'name': name, 'type': type_technology, 'capacity': data[index, 2], 'cost' : data[index, 3] }
                    dictionary[index] = node
                error, error_description = self.verify_names(names)
                 
        cost_realTime = []
        if (error==False):
            for index in dictionary:
                technology_type = self.verify_type(dictionary[index]['type'])
                if (technology_type <> Technologies.UNDEFINED):    
                    capacity = dictionary[index]['capacity']
                    cost = dictionary[index]['cost']
                    if (technology_type == Technologies.BACKHAULTYPE):
                        self._backhaul = dictionary[index]['name']
                        mega_byte_cost = CoreMethods().calculateBackhaulCostByMegaByte(capacity, cost, self._general_parameters.get_cycle_time(), 
                                                                                       self._general_parameters.get_init_working_hour(),
                                                                                       self._general_parameters.get_final_working_hour())
                        technology = BackHaulTechnology(dictionary[index]['name'], technology_type, capacity, mega_byte_cost, cost, index)     
                        self._backhaul_technology_used = True            
                    if (technology_type == Technologies.REALTYPE):
                        mega_byte_cost = CoreMethods().calculateRealTimeCostByMegaByte(self._general_parameters.MIN_CHANNEL, 
                                                                      self._general_parameters.K_BITS_SECOND,
                                                                      self._general_parameters.MBYTES,
                                                                      self._general_parameters.get_init_working_hour(),
                                                                      self._general_parameters.get_final_working_hour(), cost )
                        technology = RealTimeTechnology(dictionary[index]['name'], technology_type, capacity, mega_byte_cost, cost,  index)      
                        technology_temp = {'technology_index' : dictionary[index]['name'], 'value': mega_byte_cost, 'index' : index}
                        cost_realTime.append(technology_temp)
                        self._real_technologies_used = True
                    self._technologies[dictionary[index]['name']] = technology
                else:
                    error = True
                    error_description = 'Technology:' + dictionary[index]['name'] + ' has an undefined type'
            if error == False:
                sorted_cost = sorted(cost_realTime, key=itemgetter('value', 'index'))
                for cost_item in sorted_cost:
                    item = cost_item['technology_index']
                    self._sortedTechnologies.append(item)
        #print self._sortedTechnologies        
        return error, error_description

    def is_using_backhaul_technology(self):
        return self._backhaul_technology_used
    
    def is_using_real_technologies(self):
        return self._real_technologies_used

    def get_backhaul_technology(self):
        return  self._backhaul
    
    def get_realtime_technologies(self):
        return self._sortedTechnologies

    def get_technologies(self):
        return self._technologies
    
    def __str__(self):
        str_return = ''
        for technology_index in self._technologies:
            technology = self._technologies[technology_index]
            str_return += technology.__str__()
        return str_return
    
    def initialize_technology_capacities(self, init_hour, end_hour, init_minute, end_minute ):
        for technology_index in self._technologies:
            technology = self._technologies[technology_index]
            technology.initialize_capacity(init_hour, end_hour, init_minute, end_minute)
    
    def set_real_time_technology_costs(self, percentage):
        if self.is_using_real_technologies() == True:
            for item in self._sortedTechnologies:
                real_technology = self._technologies[item]
                tech_cost = real_technology.get_init_monthly_cost()
                tech_cost = tech_cost * percentage / 100 
                Mb_cost = CoreMethods().calculateRealTimeCostByMegaByte(self._general_parameters.MIN_CHANNEL, 
                                                                          self._general_parameters.K_BITS_SECOND,
                                                                          self._general_parameters.MBYTES,
                                                                          self._general_parameters.get_init_working_hour(),
                                                                          self._general_parameters.get_final_working_hour(), tech_cost )
                real_technology.set_cost(tech_cost, Mb_cost)
    
    def set_backhaul_technology_costs(self, percentage):
        if self._backhaul_technology_used == True:
            backhaul_index = self.get_backhaul_technology()
            backhaul_tech= self._technologies[backhaul_index]
            tech_cost = backhaul_tech.get_init_monthly_cost()
            tech_cost = tech_cost * percentage / 100 
            Mb_cost = CoreMethods().calculateBackhaulCostByMegaByte(backhaul_tech.get_capacity(), tech_cost, 
                                                                                  self._general_parameters.get_cycle_time(), 
                                                                                  self._general_parameters.get_init_working_hour(),
                                                                                  self._general_parameters.get_final_working_hour())
            backhaul_tech.set_cost(tech_cost, Mb_cost)
    
    def increment_real_time_capacity(self):
        if self.is_using_real_technologies() == True:
            for item in self._sortedTechnologies:
                real_technology = self._technologies[item]
                min_channel = self._general_parameters.MIN_CHANNEL
                KbPerSecond = self._general_parameters.K_BITS_SECOND
                bitsPerSecond = KbPerSecond * min_channel
                bitsPerMinute = bitsPerSecond * 60
                MegaBytesPerMinute = bitsPerMinute / self._general_parameters.MBYTES
                capacity = real_technology.get_capacity()
                capacity += MegaBytesPerMinute
                real_technology.set_capacity(capacity)
            return capacity 

    def decrement_real_time_capacity(self):
        if self.is_using_real_technologies() == True:
            for item in self._sortedTechnologies:
                real_technology = self._technologies[item]
                min_channel = self._general_parameters.MIN_CHANNEL
                KbPerSecond = self._general_parameters.K_BITS_SECOND
                bitsPerSecond = KbPerSecond * min_channel
                bitsPerMinute = bitsPerSecond * 60
                MegaBytesPerMinute = bitsPerMinute / self._general_parameters.MBYTES
                capacity = real_technology.get_capacity()
                capacity -= MegaBytesPerMinute
                real_technology.set_capacity(capacity)
            return capacity


    def restate_real_time_technology_capacity(self):
        if self.is_using_real_technologies() == True:
            for item in self._sortedTechnologies:
                real_technology = self._technologies[item]
                capacity = real_technology.get_init_capacity()
                real_technology.set_capacity(capacity)

    def get_montly_costs(self):
        total_cost =0
        if self._backhaul_technology_used == True:
            backhaul_index = self.get_backhaul_technology()
            backhaul_tech= self._technologies[backhaul_index]
            tech_cost = backhaul_tech.get_monthly_cost()
            total_cost += tech_cost

        if self.is_using_real_technologies() == True:
            for item in self._sortedTechnologies:
                real_technology = self._technologies[item]
                min_channel = self._general_parameters.MIN_CHANNEL
                KbPerSecond = self._general_parameters.K_BITS_SECOND
                bitsPerSecond = KbPerSecond * min_channel
                bitsPerMinute = bitsPerSecond * 60
                megabytes = self._general_parameters.MBYTES
                MegaBytesPerMinute = bitsPerMinute / megabytes 
                capacity = real_technology.get_capacity()
                num_servers= capacity / MegaBytesPerMinute
                tech_cost = real_technology.get_monthly_cost()
                total_cost += (tech_cost*num_servers)  
        return total_cost
         

#For testing purposes    
#tech_container = Technology_Container()
#error, error_description = tech_container.read_technologies_from_file(relative_path, 'TechnologyParameters.csv')
#print tech_container.get_realtime_technologies()
#print tech_container.get_backhaul_technology()
#technologies = tech_container.get_technologies()
#print technologies[tech_container.get_backhaul_technology()]
#print error
#print error_description     