'''
Created on Apr 17, 2014

@author: luis
'''

from Services import Services_Container
from Services import Services

class Customer(object):
    '''
    classdocs
    '''


    def __init__(self, name, market_share):
        '''
        Constructor
        '''
        self._name = name
        self._market_share = market_share
        self._services = Services_Container()
        self._sigma = 0
    
    def add_service(self, service, price_sensitivity, time_sensitivity, optimal_quality_value):
        # We put in the time average the optimal quality value desired.
        service_add = Services(service.get_name(), service.get_type(), price_sensitivity, time_sensitivity,  service.get_elasticity(),
                               service.get_loadMB_Minutes(), service.get_usage_percentage(), 0, 0, optimal_quality_value )
        self._services._services[service.get_name()] = service_add
    
    def get_customer_service(self, index):
        return self._services._services[index]
    
    def get_market_share(self):
        return self._market_share

    def set_sigma(self, sigma):
        self._sigma = sigma
    
    def get_sigma(self):
        return self._sigma