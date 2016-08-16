'''
Created on Mar 12, 2014

@author: luis
'''

class Assignment(object):
    '''
    classdocs
    '''
    NON_SERVICE = 0
    SERVICE = 1
    NON_SERVICE_2 = 2

    def __init__(self, type, service, technology, customer, time, flow_value, cost, reduced_cost, time_avg_reduced_cost):
        '''
        Constructor
        Type can be SERVICE when operator will provide the service
                    NO_SERVICE When operator will no provide the services as it cost more that the potential market 
        '''
        self._type = type
        self._service = service
        self._technology = technology
        self._customer = customer
        self._time = time
        self._cost = cost
        self._flow_value = flow_value
        if (type == Assignment.NON_SERVICE):
            self._flow_reduced_cost = reduced_cost
            self._capacity_reduced_cost = 0.0
        if (type == Assignment.NON_SERVICE_2):
            self._flow_reduced_cost = reduced_cost
            self._capacity_reduced_cost = 0.0        
        if  (type == Assignment.SERVICE):
            self._flow_reduced_cost = 0.0 
            self._capacity_reduced_cost = reduced_cost
        self._time_avg_reduced_cost = time_avg_reduced_cost 

    def get_technology(self):
        return self._technology
    
    def get_service(self):
        return self._service

    def get_time(self):
        return self._time
    
    def get_value(self):
        return self._flow_value
    
    def get_cost(self):
        return self._cost
    
    def get_customer(self):
        return self._customer
    
    def update_reduced_cost(self, value):
        # When the update type is no_service_2 we don't have to change the reduced costs.
        if (self._type == Assignment.NON_SERVICE):
            self._flow_reduced_cost += value
        if  (self._type == Assignment.SERVICE):
            self._capacity_reduced_cost += value
            
    def get_flow_reduced_cost(self):
        return self._flow_reduced_cost
    
    def get_capacity_reduced_cost(self):
        return self._capacity_reduced_cost

    def __str__(self):
        str_return = ''
        str_return = str_return + 'type:' + str(self._type) + ','
        str_return = str_return + 'service:' + str(self._service) + ','
        str_return = str_return + 'technology:' + str(self._technology) + ','
        str_return = str_return + 'customer:' + str(self._customer) + ','
        str_return = str_return + 'time:' + str(self._time) + ','
        str_return = str_return + 'flow value:' + str(self._flow_value)  + ','
        str_return = str_return + 'flow reduced costs:' + str(self._flow_reduced_cost) + ','
        str_return = str_return + 'capacity costs:' + str(self._capacity_reduced_cost) + ','
        str_return = str_return + 'Gamma costs:' + str(self._time_avg_reduced_cost) 
        return str_return         

class AssignmentContainer(object):

    TYPE_CYCLE = 0
    TYPE_CLUSTER = 1
    TYPE_PERIOD = 2
    TYPE_HORIZON = 3

    def __init__(self, type):
        '''
        Constructor
        '''
        self._type = type
        # this dictionary storage temporarily the assignment information for a cycle.
        self._assigns_container_by_time = {}
               
    
    def get_summary_statistics(self):
        dict_return = {}
        for item in self._assigns_container_by_time:
            item_data = self._assigns_container_by_time[item]
            for element in item_data: 
                if element <> 'detail':
                    dict_return.setdefault(element,0)
                    dict_return[element] += item_data[element] 
        return dict_return  
                   
    def clear_assignment_information(self):
        self._assigns_container_by_cycle.clear()

    def get_assigments(self):
        return self._assigns_container_by_time
    
    def append_assigment_to_container(self, element, assignment_information):
        self._assigns_container_by_time[element] = assignment_information.copy()
            
    def __str__(self):
        str_return = 'type:' + str(self._type)
        for element in self._assigns_container_by_time:
            str_return = str_return +  str(element) + ':' + self._assigns_container_by_time[element].__str__() + '\n'
        return str_return 