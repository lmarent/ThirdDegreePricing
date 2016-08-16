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
from ContinuosMixTechnologyPolicy import Policy  
from OptimalPolicy import OptimalPolicy

class Policy_time_average(OptimalPolicy):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super(Policy, self).__init__()
        
    def update_price(self, time, relative_time, cycle_time, flow_assigned, backhaul_quantity, service):
        time_left = (cycle_time * 2 ) - ( relative_time / backHaulCycleTimeMethods.MINUTES_PER_HOUR)
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
             
        price = (service.get_potential_market_at_time(time) - discount_by_time - flow_assigned ) / service.get_price_sensitivity()
        service.update_price(time, price) 
        if (service.get_name() == "VozIp"):
            print ':time:' + str(time) + ':flow_assignment:' + str(flow_assigned)  + ':price:' + str(price) #':time_left:' + str(time_left) 


    def calculate_modified_optimal_flow(self, potential_market, technology_cost, price_sensitivity, time_sensitivity, time_average, backhaul_cost, remaining_time):
        bt = potential_market - (time_sensitivity * time_average)
        value1 = (bt - (technology_cost*price_sensitivity))/2
        value2 = ((time_average / (2 * remaining_time))*price_sensitivity)*(technology_cost-backhaul_cost)
        return_value = value1 + value2
        return return_value
    
    def calculate_backhaul_enough_flow(self, potential_market, price_sensitivity, time_sensitivity, time_average, technology_cost, backhaul_cost, remaining_time ):
        bt = potential_market - (time_sensitivity * time_average)
        value1 = bt / 2
        value2 = (technology_cost * price_sensitivity) / 2
        value3 = time_average*price_sensitivity*(technology_cost - backhaul_cost)
        value3 = value3 / (remaining_time * 2)
        value4 = value1 - value2 + value3
        value4 = ( value4 * time_average ) / remaining_time
        return value4
    
    def calculate_gamma_reduced_cost_enough_flow(self, technology_cost, backhaul_cost, remaining_time):
        return (technology_cost - backhaul_cost) /  remaining_time
    
    def calculate_backhaul_non_enough_flow(self, flow_acum, time_average, remaining_time):
        return ( flow_acum * time_average ) / remaining_time
        
    def calculate_gamma_reduced_cost_non_enough_flow(self, flow_acum, potential_market, price_sensitivity, time_sensitivity, time_average, backhaul_cost, remaining_time): 
        bt = potential_market - (time_sensitivity * time_average)
        value1 = bt  /  price_sensitivity
        value2 = (2 * flow_acum) / price_sensitivity
        value2 = (value2 * remaining_time)
        value2 = value2 / math.pow(remaining_time - time_average, 2) 
        value3 = backhaul_cost / (remaining_time - time_average ) 
        value4 = value1 - value2 - value3
        return value4
    
    def calculate_capacity_reduced_cost_non_enough_capacity(self, flow_acum, potential_market, price_sensitivity, time_sensitivity, time_average, remaining_time, technology_cost, gamma):
        bt = potential_market - (time_sensitivity * time_average)
        value1 = bt / price_sensitivity 
        value2 = (2 * flow_acum) / price_sensitivity
        value2 = value2 * remaining_time
        value2 = value2 / ( remaining_time - time_average )
        value3 = gamma * time_average
        reduced_cost = value1 - value2 - technology_cost +  value3
        return reduced_cost
          
    def update_assignments(self, time, relative_time, cycle_time, flow_assigned,  queue_assigments, technologies, service):
        backhaul_flow = 0
        while True:
            try:
                assigment = queue_assigments.popleft()
                technology = technologies[assigment.get_technology()]
                technology.update_capacity(time, assigment.get_value())
                if (technology.get_type() == Technologies.BACKHAULTYPE):
                    backhaul_flow = backhaul_flow + assigment.get_value()                                    
                service.update_assigment(time, assigment.get_value())
                service.add_assigment_detail(time,assigment)
            except IndexError:
                break   
        self.update_price( time, relative_time, cycle_time, flow_assigned, backhaul_flow, service) 
        
    def apply_policy_with_user_time_average(self, service_index, service, potential_market, price_sensitivity, 
                                            time_sensitivity, technologies_container, 
                                            cycle_time, time_average, backhaul_cost,  
                                            remaining_time, time):
        queue_assigments = deque()
        flow_acum= 0
        #print 'remaining value:'  + str(remaining_time) +  ':time_averagae:' + str(time_average)
        #if (service_index == "VozIp"):
        #    print 'potential_market:' + str(potential_market) + ':price sensitivity:' + str(price_sensitivity) 
        # We have to figure out which is the cheapest technology, which is to compare the after time sensitivity of the backhaul against other technologies   
        p = 0
        k = 0
        I = len(technologies_container.get_realtime_technologies())
        # The following lines found the index p and k described in the paper. 
        for item in technologies_container.get_realtime_technologies():
            technology = technologies_container.get_technologies()[item]
            technology_cost = technology.get_cost() 
            remaining_capacity = technology.get_remaining_capacity(time)
            optimal_flow = self.calculate_modified_optimal_flow(potential_market, technology_cost, price_sensitivity, 
                                                                time_sensitivity, time_average, backhaul_cost, remaining_time)
            if (optimal_flow > 0):
                if (remaining_capacity == 0):
                    p = p + 1  
                else:
                    test_value = (remaining_capacity + flow_acum) * ( remaining_time / (remaining_time - time_average))
                    if ((test_value) > optimal_flow):
                        break
                    else:
                        flow_acum = flow_acum + remaining_capacity
                k = k + 1
            else:
                break
        backhaul = technologies_container.get_backhaul_technology()
        backhaul_tech = technologies_container.get_technologies()[backhaul]
        backhaul_cost = backhaul_tech.get_cost() 
        if (optimal_flow <= 0):
            bt = ( potential_market - (time_average * time_sensitivity))
            if backhaul_cost > (bt / price_sensitivity):
                reduced_cost = backhaul_cost - (bt / price_sensitivity)
                gamma = 0
                queue_assigments.append(Assignment(Assignment.NON_SERVICE, service_index, backhaul, self._generic_customer, time, 0, 0, reduced_cost, gamma))
                for technology_index in technologies_container.get_realtime_technologies():
                    technology = technologies_container.get_technologies()[technology_index]
                    reduced_cost = technology.get_cost() - (bt / price_sensitivity) 
                    queue_assigments.append(Assignment(Assignment.NON_SERVICE, service_index, technology_index, self._generic_customer, time, 0, 0, reduced_cost, gamma ))
                
            else: 
                reduced_cost = 0
                gamma = (( bt / price_sensitivity) - backhaul_cost ) 
                gamma = gamma  / (remaining_time - time_average)
                queue_assigments.append(Assignment(Assignment.NON_SERVICE, service_index, backhaul, time, 0, 0, reduced_cost, gamma))
                for technology_index in technologies_container.get_realtime_technologies():
                    technology = technologies_container.get_technologies()[technology_index]
                    reduced_cost =  technology.get_cost() - (bt / price_sensitivity)  -  (gamma*time_average)   
                    queue_assigments.append(Assignment(Assignment.NON_SERVICE, service_index, technology_index, self._generic_customer, time, 0, 0, reduced_cost, gamma ))
        else:
            # The following lines make the optimal assignment
            if (k < I):
                flow_acum = 0
                flow_backhaul = self.calculate_backhaul_enough_flow(potential_market, price_sensitivity, time_sensitivity, time_average, technology_cost, backhaul_cost, remaining_time)
                gamma = self.calculate_gamma_reduced_cost_enough_flow(technology_cost, backhaul_cost, remaining_time)
                queue_assigments.append(Assignment(Assignment.SERVICE, service_index, backhaul, self._generic_customer, time, flow_backhaul, backhaul_cost, 0, gamma ))
                flow_acum += flow_backhaul
                index = 0
                while (index < I):
                    techn_index = technologies_container.get_realtime_technologies()[index] 
                    tech_cost_i = technologies_container.get_technologies()[techn_index].get_cost()
                    if (index < p):
                        queue_assigments.append(Assignment(Assignment.NON_SERVICE, service_index, techn_index, self._generic_customer, time, 0, 0, technology_cost - tech_cost_i, gamma ))
                    if (p  <= index) and (index <= k):
                        remaining_capacity = technologies_container.get_technologies()[techn_index].get_remaining_capacity(time)
                        test_value = ( remaining_time / (remaining_time - time_average))
                        if ( flow_acum + remaining_capacity ) >= (optimal_flow / test_value ): 
                            flow_technology = optimal_flow - flow_acum 
                            queue_assigments.append(Assignment(Assignment.SERVICE, service_index, techn_index, self._generic_customer, time, flow_technology, tech_cost_i, 0, gamma ))
                            flow_acum = flow_acum + flow_technology  
                        else:
                            flow_technology = remaining_capacity
                            queue_assigments.append(Assignment(Assignment.SERVICE, service_index, techn_index, self._generic_customer, time, flow_technology, tech_cost_i, technology_cost - tech_cost_i, gamma ))
                    if (index > k):
                        reduced_cost = tech_cost_i + (2 * optimal_flow / price_sensitivity ) - ((potential_market - time_sensitivity*time_average)/price_sensitivity)
                        queue_assigments.append(Assignment(Assignment.NON_SERVICE, service_index, techn_index, self._generic_customer, time, 0, 0, reduced_cost, gamma ))
                    index = index + 1
                # sets the rest of the reduced technology an capacity costs        
            else: # K = I - This means that there is not enough capacity to fullfill the optimal demand.
                flow_backhaul = self.calculate_backhaul_non_enough_flow(flow_acum, time_average, remaining_time)
                gamma = self.calculate_gamma_reduced_cost_non_enough_flow(flow_acum, potential_market, price_sensitivity, time_sensitivity, time_average, backhaul_cost, remaining_time)
                index = 0
                while (index < I):
                    techn_index = technologies_container.get_realtime_technologies()[index] 
                    tech_cost_i = technologies_container.get_technologies()[techn_index].get_cost()
                    remaining_capacity = technologies_container.get_technologies()[techn_index].get_remaining_capacity(time)
                    reduced_cost = self.calculate_capacity_reduced_cost_non_enough_capacity(flow_acum, potential_market, price_sensitivity, 
                                                                                                time_sensitivity, time_average, remaining_time,
                                                                                                technology_cost, gamma)
                    if (remaining_capacity == 0):                                                                            
                        queue_assigments.append(Assignment(Assignment.NON_SERVICE, service_index, techn_index, self._generic_customer, time, 0, 0, reduced_cost, gamma ))
                    else:
                        queue_assigments.append(Assignment(Assignment.SERVICE, service_index, techn_index, self._generic_customer, time, remaining_capacity, 
                                                           tech_cost_i, reduced_cost, gamma ))
                    index = index + 1
     
        self.update_assignments(time, remaining_time, cycle_time, flow_acum, queue_assigments, technologies_container.get_technologies(), service)
        #TODO: Verificar que los precios quedan bien calculados para esta politica  
     
    def is_constrained(self, technologies_container, service, time, relative_time, cycle_time, time_average):
        val_return = False
        back_cost = 0
        remaining_time = cycle_time * 2
        if (technologies_container.is_using_backhaul_technology() == True):
            backhaul = technologies_container.get_backhaul_technology()
            back_tech = technologies_container.get_technologies()[backhaul]
            back_cost = back_tech.get_cost()
            if (technologies_container.is_using_real_technologies() == True):
                # The test must be only against the cheapest technology
                index = technologies_container.get_realtime_technologies()[0]
                real_tech = technologies_container.get_technologies()[index]
                if (back_cost >= real_tech):
                    val_return = False  
                else:
                    # Calculates the remaining time
                    remaining_time = (cycle_time * 2 ) - ( relative_time / backHaulCycleTimeMethods.MINUTES_PER_HOUR) 
                    if time_average < remaining_time:
                        # In this case the time and the costs satisfied the conditions defined.
                        val_return = True  
                    else:
                        val_return = False 
            else:
                val_return = False
             
        return val_return , back_cost, remaining_time          
                
    def calculateOptimalPolicyByCycle(self, parameters):
        
        # get the parameters from the dictionary
        general_parameters =  parameters['general_parameters'] 
        technologies_container = parameters['technologies_container']
        service_container = parameters['service_container']
        cycle_time = parameters['cycle_time']
        hour_init = parameters['hour_init']
        hour_end = parameters['hour_end']
        minute_init = parameters['minute_init']
        minute_end = parameters['minute_end']
        detail = parameters['detail']
        cluster_index = parameters['cluster_index']
        
        # Parameters backhaul and real_technologies are indexes to technology repository which is the parameters technologies 
        services = service_container.get_services()
        assigment_container = AssignmentContainer(AssignmentContainer.TYPE_CYCLE) 
        dtnCoreTimeMethods = backHaulCycleTimeMethods()  
        without_time_average = Policy()          
        # Initialize capacities and assignments for services and technologies
        technologies_container.initialize_technology_capacities(hour_init, hour_end, minute_init, minute_end)
        service_container.initialize_services_assigments()
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
                        time_sensitivity = service.get_time_sensitivity()
                        time_average = service.get_time_average()
                        if (service.get_type() == Services.DELAY_TOLERANT):
                            # Evaluates conditions for being constrained by time average given as parameter. If both are satisfied it applies that policy
                            # otherwise, it just apply the normal policy
                            constrained, backhaul_cost, remaining_time = self.is_constrained( technologies_container, service, time, 
                                                                                              relative_time, cycle_time, time_average)
                            if (constrained == True):
                                
                                self.apply_policy_with_user_time_average(service_index, service, potential_market, 
                                                                         price_sensitivity, time_sensitivity, 
                                                                         technologies_container, cycle_time, 
                                                                         time_average, backhaul_cost, remaining_time, time)
                            else:
                                without_time_average.apply_policy_without_user_time_average(service_index, service, potential_market, 
                                                                                        price_sensitivity, technologies_container, 
                                                                                        cycle_time, relative_time, time)
                        else:
                            # If service is real time it uses the real time policy.
                            without_time_average.apply_policy_without_user_time_average(service_index, service, potential_market, 
                                                                                        price_sensitivity, technologies_container, 
                                                                                        cycle_time, relative_time, time)
                    
                    except IndexError:
                        break            
        for service_index in services:  
            service = services[service_index]
            dic_return = service.get_summary_assigments_statistics()
            if detail:
                detail_assigments = service.get_detail_assigments()
            else:
                detail_assigments = {}
            # for testing purposes 
            if service_index == "Http_DTN":
                detail_assigments = service.get_detail_assigments()
                list_flow = []
                list_price = []
                list_technology_asig = []
                list_flow_reduced_cost = []
                list_capacity_reduced_cost = []
                for time in detail_assigments:
                    detail_assignment = detail_assigments[time]
                    list_flow.append(detail_assignment['demand'])
                    list_price.append(detail_assignment['price'])
                    for item in detail_assignment['detail']:
                        if item.get_technology() == "Backhaul":
                            print item.__str__()
                            list_technology_asig.append(item.get_value())
                            list_flow_reduced_cost.append(item.get_flow_reduced_cost())
                            list_capacity_reduced_cost.append(item.get_capacity_reduced_cost())
                              
                print 'flow'
                print list_flow
#                print 'price'
#                print list_price
#                print 'assign_technology'
#                print list_technology_asig
#                print 'flow reduced cost'
#                print list_flow_reduced_cost
#                print 'capacity reduced cost'
#                print list_capacity_reduced_cost
            
            dict_node = {}
            for item in dic_return:
                dict_node[item] = dic_return[item]
            dict_node['detail'] = detail_assigments
            assigment_container.append_assigment_to_container(service_index, dict_node)
        return assigment_container
                    
