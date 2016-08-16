'''
Created on Apr 17, 2014

@author: luis
'''

from __future__ import division
import math
from Assigment import Assignment
from Assigment import AssignmentContainer
from Services import Services
from DTNCoreProcedures import backHaulCycleTimeMethods
from collections import deque
from DemandMarketEquilibriumAlgorithm import Algorithm
from Technologies import Technologies
from OptimalPolicy import OptimalPolicy
import ContinuosMixTechnologyPolicy

class Policy(OptimalPolicy):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super(Policy, self).__init__()
    
    def calculate_lambda_costraint(self, param_q, restricted_capacity,  optimal_flow):
        total_flow = 0
        for item in optimal_flow:
            total_flow +=  optimal_flow[item]
        lamda = (2*total_flow) + (2*restricted_capacity) - param_q
        return lamda     
        

    def update_assignments(self, time, relative_time, cycle_time, flow_assigned,  queue_assigments, technologies, service,technology_cost, profits,customer):
        backhaul_flow = 0
        total_cost = 0
        while True:
            try:
                assigment = queue_assigments.popleft()
                technology = technologies[assigment.get_technology()]
                total_cost += assigment.get_value() * assigment.get_cost()
                technology.update_capacity(time, assigment.get_value())
                if (technology.get_type() == Technologies.BACKHAULTYPE):
                    backhaul_flow = backhaul_flow + assigment.get_value()                    
                service.update_assigment(time, relative_time, cycle_time, assigment.get_value())
                service.add_assigment_detail(time,assigment)
            except IndexError:
                break  
        #print 'service:' + service.get_name() + 'Sigma:' + str(customer.get_sigma())
        price = ((profits * ( customer.get_sigma() +  1 )) + total_cost ) / flow_assigned    
        service.update_price(time, price) 
  
    def apply_policy_service(self, service_index, customer_service, service, potential_market, price_sensitivity, technologies_container, cycle_time, relative_time, time, profits, customer, mode ):
        
        queue_assigments = deque()
        # We have to apply the Market Equilibrium algorithm for this specific setting
        param_q = 2 * potential_market
        param_r = 2
        algor = Algorithm(param_q, param_r)
        technologies = technologies_container.get_technologies()
        # The algorithm goes likes this:
        # First it optimally assign the traffic. Then it verify that assigned capacity conforms the capacity constraints
        # for those variables not satisfying capacity constraints it assign the remaining capacity and reduce the param_r in that value
        # after it execute again the market demand algorithm. If all variables does not satisfied the capacity constraints then
        # we set lambda equal to 2*(maximal flow) - 2*param_r and determine Ui= 2*param_r - param_hi - 2 param_gi remaining_capacity  - 2*maximal flow    
        
        #Part 0. Executes the algorithm assuming full capacity
        for technology_index in technologies:
            technology = technologies[technology_index]
            param_h = technology.get_cost() * price_sensitivity
            if technology.get_type() == Technologies.BACKHAULTYPE: 
                remaining_time = (cycle_time * 2 ) - ( relative_time / backHaulCycleTimeMethods.MINUTES_PER_HOUR)
                param_g = 2 * customer_service.get_time_sensitivity() * math.pow(( customer_service.get_time_average() - remaining_time),2)
            else:
                remaining_time = 0
                param_g = 2 * customer_service.get_time_sensitivity() * math.pow(( customer_service.get_time_average() - remaining_time),2)
            algor.add_path(technology_index,param_h,param_g)
        result = algor.execute()
        technologies_with_capacity = []
        technologies_without_capacity = []
        execute_again = False
        total_capacity_assigned = 0
        # Part two. Verify if all capacities assigned satisfied the capacity constraint
        for item in result:
            remaining_capacity = technologies[item].get_remaining_capacity(time)
            if remaining_capacity >= result[item]:
                technologies_with_capacity.append(item)
            else:
                execute_again = True
                technologies_without_capacity.append(item)
                total_capacity_assigned += remaining_capacity 
        # Part 3. We have to execute again the algorithm because some technologies do not satisfy constraints 
        if (execute_again == True):
            if (len(technologies_without_capacity) == len(result)):
                lambda_constraint = (2 * total_capacity_assigned) - param_q  
            else:
                param_q_prima = param_q - (2 * total_capacity_assigned)
                algor2 = Algorithm(param_q_prima, param_r)
                for technology_index in technologies_with_capacity:
                    parameters = algor.get_path(technology_index)
                    algor2.add_path(technology_index,parameters['h'],parameters['g'])
                result2 = algor2.execute()
                lambda_constraint = self.calculate_lambda_costraint(param_q, total_capacity_assigned,  result2)
        # Create the assignments based on executions        
        flow_acum = 0
        for item in result:
            if (execute_again == True):
                if (item in result2):
                    technology_cost = technologies[item].get_cost()
                    if (technologies[item].get_type() == Technologies.BACKHAULTYPE):
                        technology_cost -= technologies[item].get_theta_zero()
                    reduced_cost = 0
                    time_avg_reduced_cost = 0
                    queue_assigments.append(Assignment(Assignment.SERVICE, service_index, item, customer, time, result2[item], technology_cost, reduced_cost, time_avg_reduced_cost))
                    flow_acum += result2[item]
                else:
                    parameters = algor.get_path(item)
                    remaining_capacity = technologies[item].get_remaining_capacity(time)
                    technology_cost = technologies[item].get_cost()
                    if (technologies[item].get_type() == Technologies.BACKHAULTYPE):
                        technology_cost -= technologies[item].get_theta_zero()
                    reduced_cost = -(parameters['h']) - (parameters['g']*remaining_capacity) - lambda_constraint
                    time_avg_reduced_cost = 0
                    queue_assigments.append(Assignment(Assignment.SERVICE, service_index, item, customer, time, remaining_capacity, technology_cost, reduced_cost, time_avg_reduced_cost))
                    flow_acum += remaining_capacity
                    
            else:
                technology_cost = technologies[item].get_cost()
                if (technologies[item].get_type() == Technologies.BACKHAULTYPE):
                    technology_cost -= technologies[item].get_theta_zero()
                reduced_cost = 0
                time_avg_reduced_cost = 0
                queue_assigments.append(Assignment(Assignment.SERVICE, service_index, item, customer, time, result[item], technology_cost, reduced_cost, time_avg_reduced_cost))
                flow_acum += result[item]
        
        if (mode == self.MODE_UPDATE): 
            self.update_assignments(time, relative_time, cycle_time, flow_acum, queue_assigments, technologies, service, technology_cost, profits, customer)

    def calculateOptimalPolicyByCycle(self,parameters):
        
        print 'in calculateOptimalPolicyByCycle'
        # Get parameters from dictionary
        period =  parameters['period']
        technologies_container = parameters['technologies_container']
        service_container = parameters['service_container']
        customer = parameters['customer']
        cycle_time = parameters['cycle_time']
        hour_init = parameters['hour_init']
        hour_end = parameters['hour_end']
        minute_init = parameters['minute_init']
        minute_end = parameters['minute_end']
        detail = parameters['detail']
        cluster_index = parameters['cluster_index']
        
        # Initialize capacities and assignments for services and technologies
        technologies_container.initialize_technology_capacities(hour_init, hour_end, minute_init, minute_end)
        service_container.initialize_services_assigments()
        services = service_container.get_services()
        dtnCoreTimeMethods = backHaulCycleTimeMethods()            
        init_time = dtnCoreTimeMethods.calculate_time(hour_init,minute_init)
        without_time_average = ContinuosMixTechnologyPolicy.Policy()          
                        
        # Executes the policy by hour and minute within the cycle time.
        for hour in range(int(hour_init), int(hour_end)):
            init_minute_range,  end_minute_range = dtnCoreTimeMethods.get_minute_interval(hour, hour_init, hour_end, minute_init, minute_end)
            for minute in range (init_minute_range, end_minute_range):            
                time = dtnCoreTimeMethods.calculate_time(hour,minute)  
                queue_services = service_container.get_ordered_services_quality(time)
                while True:
                    try:
                        service_index = queue_services.popleft()
                        service = services[service_index]
                        relative_time = time - init_time
                        potential_market = service.get_potential_market_at_time(time) 
                        price_sensitivity = service.get_price_sensitivity()                        
                        if (service.get_type() == Services.DELAY_TOLERANT):
                            # Calculates the optimal profit waited for the operator.
                            customer_potential_market = potential_market * customer.get_market_share()   
                            profits = without_time_average.apply_policy_service(service_index, service, customer_potential_market, price_sensitivity, technologies_container, 
                                                                                        cycle_time, relative_time, time, self.MODE_SIMULATE, period)
                            
                                                                                
                            customer_service = customer.get_customer_service(service_index)
                            price_sensitivity = price_sensitivity
                            # TODO: Review what to do with this parameter
                            #print 'service:' + service_index + 'get_price_sensitivity:' + str(price_sensitivity)                           
                            self.apply_policy_service(service_index, customer_service, service, customer_potential_market, price_sensitivity, 
                                                      technologies_container, cycle_time, relative_time, time, profits, customer, self.MODE_UPDATE)
                            
                        else:
                            # If service is real time it uses the real time policy.
                            customer_potential_market = potential_market * customer.get_market_share()
                            without_time_average.apply_policy_service(service_index, service, customer_potential_market, price_sensitivity, technologies_container, 
                                                                                        cycle_time, relative_time, time, self.MODE_UPDATE, period)
                                                
                    except IndexError:
                        break            

        
        assigment_container = self.summary_statistics(services, detail, period, cluster_index, hour_init, True)    
        return assigment_container
        