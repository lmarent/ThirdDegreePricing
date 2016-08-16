'''
Created on Mar 12, 2014

@author: luis
'''

from __future__ import division
from DTNCoreProcedures import backHaulCycleTimeMethods
from Technologies import Technologies
import math
from collections import deque
from Assigment import Assignment
from Assigment import AssignmentContainer
from Services import Services
from OptimalPolicy import OptimalPolicy

class Policy(OptimalPolicy):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super(Policy, self).__init__()
        

    def calculate_optimal_flow(self, maketPotential, technologyCost, priceSensitivity ):
        return (maketPotential - (technologyCost*priceSensitivity)) / 2

    def update_price(self, service, time,  price):
        service.update_price(time, price) 
        
    def calculate_price(self, flow_assigned, backhaul_quantity, service, time, remaining_time, cycle_time, potential_market):
        time_left = (cycle_time * 2 ) - ( remaining_time / backHaulCycleTimeMethods.MINUTES_PER_HOUR)
        # There we actually flow assignment, otherwise it put a zero value and the price will be the potential market 
        # divided by the price sensitivity
        if flow_assigned > 0:
            quantity_rel = backhaul_quantity / flow_assigned
        else:
            quantity_rel = 0
        # Only calculates a discount by time for delay tolerant services        
        if (service.get_type() == Services.DELAY_TOLERANT):
            t_avg = quantity_rel *time_left
            discount_by_time = service.get_time_sensitivity() * t_avg
        else:
            discount_by_time = 0
             
        price = (potential_market - discount_by_time - flow_assigned ) / service.get_price_sensitivity()
        return price 
        
    def update_assignments_enough_capacity(self, time, relative_time, cycle_time, flow_assigned,  queue_assigments, technologies, service,technology_cost, potential_market):
        backhaul_flow = 0
        while True:
            try:
                assigment = queue_assigments.popleft()
                assigment.update_reduced_cost(technology_cost)
                technology = technologies[assigment.get_technology()]
                technology.update_capacity(time, assigment.get_value())
                if (technology.get_type() == Technologies.BACKHAULTYPE):
                    backhaul_flow = backhaul_flow + assigment.get_value()                    
                service.update_assigment(time, relative_time, cycle_time, assigment.get_value())
                service.add_assigment_detail(time,assigment)
            except IndexError:
                break  
        price = self.calculate_price(flow_assigned, backhaul_flow, service, time, relative_time, cycle_time, potential_market)
        self.update_price( service, time, price )  
        
    def update_assignments_not_enough_capacity(self, time, relative_time, cycle_time, flow_assigned, queue_assigments, technologies, service, cost_value, potential_market):
        backhaul_flow = 0
        while True:
            try:
                assigment = queue_assigments.popleft()
                assigment.update_reduced_cost(cost_value)
                technology = technologies[assigment.get_technology()]
                technology.update_capacity(time, assigment.get_value())
                if (technology.get_type() == Technologies.BACKHAULTYPE):
                    backhaul_flow = backhaul_flow + assigment.get_value()                                    
                service.update_assigment(time, relative_time, cycle_time, assigment.get_value())                
                service.add_assigment_detail(time,assigment)
            except IndexError:
                break
        price = self.calculate_price(flow_assigned, backhaul_flow, service, time, relative_time, cycle_time, potential_market)
        self.update_price( service, time, price )  
    
    def calculate_profits(self, time, relative_time, cycle_time, flow_assigned, queue_assigments, technologies, service, potential_market):
        backhaul_flow = 0
        total_cost = 0
        while True:
            try:
                assigment = queue_assigments.popleft()
                technology = technologies[assigment.get_technology()]
                total_cost += assigment.get_value() * technology.get_cost() 
                if (technology.get_type() == Technologies.BACKHAULTYPE):
                    backhaul_flow = backhaul_flow + assigment.get_value()                                    
            except IndexError:
                break
        price = self.calculate_price(flow_assigned, backhaul_flow, service, time, relative_time, cycle_time, potential_market)
        profits = (flow_assigned * price ) -total_cost
        return  profits            
    
    def order_technologies(self, technologies_container, service, cycle_time, remaining_time, time):
        List_return = []
        is_using_backhaul = technologies_container.is_using_backhaul_technology()
        if (is_using_backhaul == False) or (service._type == Services.REAL_TIME):
            for technology_index in technologies_container.get_realtime_technologies():
                technology = technologies_container.get_technologies()[technology_index]
                technology_cost = technology.get_cost()
                node = {'index': technology_index, 'cost' : technology_cost}
                List_return.append(node) 
        else:
            price_sensitivity = service.get_price_sensitivity()
            time_sensitivity = service.get_time_sensitivity()
            backhaul = technologies_container.get_backhaul_technology()
            back_tech = technologies_container.get_technologies()[backhaul]
            remaining_time = (cycle_time * 2 ) - ( remaining_time / backHaulCycleTimeMethods.MINUTES_PER_HOUR)
            back_cost = back_tech.get_cost()
            over_technology_cost = back_cost + ((time_sensitivity / price_sensitivity )* remaining_time)
            not_found = True
            i = 0
            while (not_found) and (i < len(technologies_container.get_realtime_technologies())):    
                tech_index = technologies_container.get_realtime_technologies()[i]
                technology_cost = technologies_container.get_technologies()[tech_index].get_cost()
                if (technology_cost > over_technology_cost):
                    back_node = {'index': backhaul, 'cost' : over_technology_cost}
                    List_return.append(back_node)
                    for j in range(i, len(technologies_container.get_realtime_technologies())):
                        index_technology = technologies_container.get_realtime_technologies()[j]
                        node = {'index': index_technology, 'cost' : technologies_container.get_technologies()[index_technology].get_cost()}
                        List_return.append(node)
                        not_found = False
                else:
                    index_technology = technologies_container.get_realtime_technologies()[i]
                    node = {'index': index_technology, 'cost' : technologies_container.get_technologies()[index_technology].get_cost()}
                    List_return.append(node)
                i = i + 1
            if (not_found == True):
                back_node = {'index': backhaul, 'cost' : over_technology_cost}
                List_return.append(back_node)
        return List_return
                
       
    def applyPolicyService(self, service, service_index,technology_index, technology, technology_cost, time, queue_assigments, potentialMarket, price_sensitivity, flow_assigned, assigned):        
        flow_acum = flow_assigned
        if assigned==False:
            # It is more expensive to offer service than the possible price. 
            if technology_cost >= (potentialMarket / price_sensitivity ):
                #print 'Entro 1'
                optimal_flow = 0
                reduced_cost = technology_cost -  potentialMarket / service.get_price_sensitivity()
                queue_assigments.append(Assignment(Assignment.NON_SERVICE, service_index, technology_index, self._generic_customer, time, optimal_flow, 0, reduced_cost, 0 ))
                technology_cost_k = technology_cost
                assigned = True
            else:
                #print 'Entro 2'
                remaining_capacity = technology.get_remaining_capacity(time)
                #if (service_index == "Http_NDTN"):
                    # print 'time' + str(time) +  'potentialMarket:' + str(potentialMarket) + 'technology_cost:' + str(technology_cost) + 'price_sensitivity:' + str(price_sensitivity) + 'remaining_capacity' + str(remaining_capacity)  
                optimal_flow = self.calculate_optimal_flow(potentialMarket, technology_cost, price_sensitivity )
                if optimal_flow > (flow_acum + remaining_capacity):
                    reduced_cost = technology_cost * -1
                    queue_assigments.append(Assignment(Assignment.SERVICE, service_index, technology_index, self._generic_customer, time, remaining_capacity, technology_cost, reduced_cost, 0))
                    flow_acum += remaining_capacity
                    technology_cost_k = 0
                else:
                    # We have two cases here.
                    # 1. The optimal flow is less than the assigned capacity, so we have to increase the flow reduced cost - First if.
                    # 2. The optimal flow is greater than the assigned capacity, so we have to assign additional capacity with the new technology. Else
                    if (optimal_flow <= flow_acum ):
                        reduced_cost = (((2 * flow_acum)/ price_sensitivity) + technology_cost) - (potentialMarket / price_sensitivity) 
                        queue_assigments.append(Assignment(Assignment.NON_SERVICE_2, service_index, technology_index, self._generic_customer, time, 0, technology_cost, reduced_cost, 0))
                        technology_cost_k = technology_cost - reduced_cost
                        assigned = True
                    else:                    
                        # The reduce costs is created with the negative cost of the technology. After, when it is updated the assignment reduced 
                        # costs it is put again in the zero value if there is enough capacity.
                        reduced_cost = technology_cost * -1
                        queue_assigments.append(Assignment(Assignment.SERVICE, service_index, technology_index, self._generic_customer, time, optimal_flow - flow_acum, technology_cost, reduced_cost, 0))
                        flow_acum += (optimal_flow - flow_acum)
                        technology_cost_k = technology_cost
                        assigned = True
        else:
            reduced_cost = technology_cost + (( 2 * flow_acum) / price_sensitivity) - (potentialMarket / price_sensitivity)
            queue_assigments.append(Assignment(Assignment.NON_SERVICE, service_index, technology_index, self._generic_customer, time, 0, 0, reduced_cost, 0 ))
            technology_cost_k = 0
        return assigned, flow_acum, technology_cost_k 

    def confirm_policy(self, fully_assigned, potential_market, price_sensitivity, time, relative_time, cycle_time, flow_acum, queue_assigments, technologies, service, technology_cost_k):
        # the capacity is not enough for optimal service offering
        if (fully_assigned == False):
            cost_update = (potential_market - (2 * flow_acum)) / price_sensitivity
            self.update_assignments_not_enough_capacity(time, relative_time, cycle_time, flow_acum, queue_assigments, technologies, service, cost_update, potential_market)
        else:
            if fully_assigned == True:
                technology_cost = technology_cost_k
            if flow_acum > 0:
                self.update_assignments_enough_capacity(time, relative_time, cycle_time, flow_acum, queue_assigments, technologies, service, technology_cost, potential_market)
            else:
                # Reduced costs are already in the correct value.
                self.update_assignments_enough_capacity(time, relative_time, cycle_time, flow_acum, queue_assigments, technologies, service, 0, potential_market)    


    def apply_policy_service(self, service_index, service, potential_market, price_sensitivity, technologies_container, cycle_time, relative_time, time, mode, period):
        queue_assigments = deque()
        fully_assigned = False 
        flow_acum= 0
        technologies = technologies_container.get_technologies()
        #if (service_index == "Http"):
        #    print 'time:' + str(time) + ':potential_market:' + str(potential_mMarket) + ':price sensitivity:' + str(price_sensitivity) 
        # We have to figure out which is the cheapest technology, which is to compare the after time sensitivity of the backhaul against other technologies   
        ordered_technologies = self.order_technologies(technologies_container, service, cycle_time, relative_time, time)
        technology_cost_k = 0
        profits = 0
        for node in ordered_technologies:
            technology = technologies[node['index']]
            technology_cost = node['cost']                 
            fully_assigned, flow_acum, technology_costk = self.applyPolicyService(service, service_index, node['index'],
                                                                                  technology, technology_cost, time, queue_assigments,
                                                                                  potential_market, price_sensitivity, flow_acum, fully_assigned)
            # It is needed only the first time that the flow is assigned
            #if (period == 45) and (service_index == "Real_traffic"):
            #    print 'service_index:' + service_index + ':Technology:' + technology._name +  ':Time:' + str(time) +  ':Capacity:' + str(technology.get_remaining_capacity(time)) + ':Flow acum:' + str(flow_acum) + ':Technology cost:' + str(technology_cost) + ':Poten:' + str(potential_market) + ':Price_se:'+ str(price_sensitivity) + ':Value:' + str( potential_market/ price_sensitivity) 
            if (fully_assigned == True) and (technology_cost_k == 0):
                technology_cost_k = technology_costk
                                
        if (mode == self.MODE_UPDATE):
            self.confirm_policy( fully_assigned, potential_market, price_sensitivity, time, relative_time, cycle_time, flow_acum, 
                              queue_assigments, technologies, service, technology_cost_k)
        else:
            profits = self.calculate_profits(time, relative_time, cycle_time, flow_acum, queue_assigments, technologies, service, potential_market)
        return profits    
                    
    def calculateOptimalPolicyByCycle(self,parameters):
        # Parameters backhaul and real_technologies are indexes to technology repository which is the parameters technologies 
        #print 'calculateOptimalPolicyByCycle:' + ':period:' + str(parameters['period']) + ':cluster_index:'+ str(parameters['cluster_index']) + ':cycle:' + str(parameters['hour_init'])
        
        # Read parameters from the dictionary
        period =  parameters['period']
        cluster_index = parameters['cluster_index']
        general_parameters = parameters['general_parameters']
        technologies_container = parameters['technologies_container']
        service_container = parameters['service_container']
        cycle_time = parameters['cycle_time']
        hour_init = parameters['hour_init']
        hour_end = parameters['hour_end']
        minute_init = parameters['minute_init']
        minute_end = parameters['minute_end']
        detail = parameters['detail']
        
        technologies_container.initialize_technology_capacities(hour_init, hour_end, minute_init, minute_end)
        service_container.initialize_services_assigments()
        services = service_container.get_services() 
        dtnCoreTimeMethods = backHaulCycleTimeMethods()    
        # Initialize capacities and assignments for services and technologies
        init_time = dtnCoreTimeMethods.calculate_time(hour_init,minute_init)
        for hour in range(int(hour_init), int(hour_end)):
            init_minute_range,  end_minute_range = dtnCoreTimeMethods.get_minute_interval(hour, hour_init, hour_end, minute_init, minute_end)
            for minute in range (init_minute_range, end_minute_range):            
                time = dtnCoreTimeMethods.calculate_time(hour,minute)  
                queue_services = service_container.get_ordered_services(time) 
                while True:
                    try:
                        service_index = queue_services.popleft()
                        service = services[service_index]
                        relative_time = time - init_time
                        potential_market = service.get_potential_market_at_time(time) 
                        price_sensitivity = service.get_price_sensitivity()
                        #if (period == 45) and ( 0.026 >  ( potential_market / price_sensitivity) ):
                        #    print 'service_index:' + service_index +  'Time:' + str(time) + 'potential_market:' + str(potential_market) + 'price_sensitivity:' +  str(price_sensitivity) 
                        self.apply_policy_service(service_index, service, potential_market, price_sensitivity, technologies_container, cycle_time, relative_time, time, self.MODE_UPDATE, period)
                    except IndexError:
                        break            
        assigment_container = self.summary_statistics(services, detail, period, cluster_index, hour_init, False)    
        return assigment_container
                    
