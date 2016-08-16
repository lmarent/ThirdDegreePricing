'''
Created on Apr 18, 2014

@author: luis
'''
from Customer import Customer 
from Services import Services
from Assigment import AssignmentContainer
from DTNCoreProcedures import backHaulCycleTimeMethods
from collections import OrderedDict

class OptimalPolicy(object):
    '''
    classdocs
    '''

    MODE_SIMULATE = 1
    MODE_UPDATE = 2 

    def __init__(self):
        '''
        Constructor
        '''
        self._generic_customer = Customer('Generic', 0)

    def calculateOptimalInventoryReduceCost(self, technologies_container, service_container, cycle_time):
        if (technologies_container.is_using_backhaul_technology() == True):
            backhaul = technologies_container.get_backhaul_technology()
            backhaul_tech = technologies_container.get_technologies()[backhaul]
            capacity = backhaul_tech.get_capacity()
            services = service_container.get_services()
            price_sensitivity = 0   
            used_capacity = 0 
            for service in services:
                if (services[service].get_type() == Services.DELAY_TOLERANT):
                    price_sensitivity += services[service].get_price_sensitivity()
                    # This part calculates the used capacity for the backhaul technology 
                    detail_assigments = services[service].get_detail_assigments()
                    for time in detail_assigments:
                        detail_assignment = detail_assigments[time]
                        for item in detail_assignment['detail']:
                            if item.get_technology() == backhaul:
                                used_capacity += item.get_value()
            #print 'used capacity:' + str(used_capacity)
            if price_sensitivity > 0:
                theta_0 = ((capacity - used_capacity )*2 ) / (cycle_time*price_sensitivity)
                if theta_0 > 0:
                    theta_0 = 0
                else:
                    theta_0 = (theta_0 * -1 ) / backHaulCycleTimeMethods.MINUTES_PER_HOUR 
            else:
                # This means that none of the services were delay tolerant
                theta_0 = 0
        else:
            theta_0 = 0
        #print 'theta_0:' + str(theta_0)
        return theta_0   

    def summary_statistics(self,services, detail, period, cluster_index, hour_init, debug):
        assigment_container = AssignmentContainer(AssignmentContainer.TYPE_CYCLE)
        for service_index in services:  
            service = services[service_index]
            dic_return = service.get_summary_assigments_statistics()
            if detail:
                detail_assigments = service.get_detail_assigments()
            else:
                detail_assigments = {}
            if debug:    
                detail_assigments = OrderedDict(sorted(service.get_detail_assigments().items(), key=lambda t: t[0] ))
                list_potential_market = []
                list_flow = []
                list_price = []
                list_income = []
                list_technology_asig = []
                real_list_technology_asig =[]
                list_flow_reduced_cost = []
                list_capacity_reduced_cost = []
                for time in detail_assigments:
                    detail_assignment = detail_assigments[time]
                    
                    list_flow.append(detail_assignment['demand'])
                    list_price.append(detail_assignment['price'])
                    list_income.append(detail_assignment['demand'] * detail_assignment['price'])
                    list_potential_market.append(service.get_potential_market_at_time(time))
                    for item in detail_assignment['detail']:
                        if item.get_technology() == "Backhaul":
                            #print item.__str__()
                            list_technology_asig.append(item.get_value())
                            list_flow_reduced_cost.append(item.get_flow_reduced_cost())
                            #list_capacity_reduced_cost.append(item.get_capacity_reduced_cost())                        
                        if item.get_technology() == "Satellite":
                            real_list_technology_asig.append(item.get_value())
                            list_capacity_reduced_cost.append(item.get_capacity_reduced_cost())
                            #print item.get_capacity_reduced_cost()
    
                try:
                    # This will update the file
                    if (period == 10) and ((debug == True) and (detail == True)):
                        file = open("debug.txt", "a")
                        file.writelines('period:' + str(period) + '\n')
                        #print service_index
                        file.writelines('service:' + service_index)
                        file.writelines('cluster_index:' + str(cluster_index) + '\n') 
                        file.writelines('hour_init '+ str(hour_init) + '\n')
                        #file.writelines('income' + '\n')
                        #file.writelines(list_income.__str__() + '\n')
                        #file.writelines('potential_market' + '\n')
                        #file.writelines(list_potential_market.__str__() + '\n')  
                        file.writelines('flow' + '\n') 
                        file.writelines(list_flow.__str__() + '\n') 
                        file.writelines('price' + '\n')
                        file.writelines(list_price.__str__() + '\n') 
                        file.writelines('backhaul assign_technology' + '\n')
                        file.writelines(list_technology_asig.__str__() + '\n')
                        #file.writelines('capacity reduced cost' + '\n')
                        #file.writelines(list_capacity_reduced_cost.__str__() + '\n')                
                        file.close()

                except IOError:
                    pass

                
            dict_node = {}
            for item in dic_return:
                dict_node[item] = dic_return[item]
            dict_node['detail'] = detail_assigments            
            assigment_container.append_assigment_to_container(service_index, dict_node)
        return assigment_container
