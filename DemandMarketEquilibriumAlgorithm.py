'''
Created on Apr 17, 2014

@author: luis
'''
from __future__ import division
from operator import itemgetter

class Algorithm(object):
    '''
    classdocs
    '''
    def __init__(self, paramq, paramr):
        '''
        Constructor
        '''
        self._pathlist = []
        self._param_q = paramq
        self._param_r = paramr
        self._ordered_pathlist = []
    
    def add_path(self, label, h, g):
        data = {'label': label, 'h' : h , 'g' : g}
        self._pathlist.append(data)
    
    def get_path(self, label):
        val_return = {}
        for index in range(len(self._pathlist)):
            if label == self._pathlist[index]['label']:
                val_return = self._pathlist[index]
                index = len(self._pathlist)
        return val_return
         
    
    def sort(self):
        self._ordered_pathlist = sorted(self._pathlist, key=itemgetter('h'))
        
    def execute(self):
        result = {}
        self.sort()
        to_continue = True
        hi = self._ordered_pathlist[0]['h']
        if (self._param_q <= hi):
            i = 0
            while i < len(self._ordered_pathlist):
                label = self._ordered_pathlist[i]['label']
                result[label] = 0
                i = i + 1
        else:
            v = 0
            sumhoverg = 0
            sumoneoverg = 0
            while to_continue:
                sumhoverg += (self._ordered_pathlist[v]['h'] / self._ordered_pathlist[v]['g'])
                sumoneoverg += (1 / self._ordered_pathlist[v]['g'])
                pv = sumhoverg + (self._param_q / self._param_r)
                pv = pv / (sumoneoverg + (1/self._param_r) )
                if (len(self._ordered_pathlist) > (v+1) ):
                    if ((self._ordered_pathlist[v]['h'] >= pv) or (pv >= self._ordered_pathlist[v+1]['h']) ):
                        v = v + 1
                    else:
                        to_continue = False
                else:
                    to_continue = False     
            vprima = v
            i = 0 
            while (i <= vprima):
                label = self._ordered_pathlist[i]['label']
                result[label] = (pv - self._ordered_pathlist[i]['h']) / self._ordered_pathlist[i]['g']
                i = i + 1
            while (vprima+1) <= i and i < len(self._ordered_pathlist):
                label = self._ordered_pathlist[i]['label']
                result[label] = 0
                i = i + 1
        return result
    
# Code for testing
param_q = 2.569733358 
param_r = 2
algor = Algorithm(param_q, param_r)
label = 'backhaul'
param_h = 0.034359889
param_g= 1.747203556 
algor.add_path(label,param_h,param_g)
label = 'Satellite'
param_h = 1.047158512
param_g = 0.0128
algor.add_path(label,param_h,param_g)
result = algor.execute()
print result 
         
            