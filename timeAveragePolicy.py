'''
Created on Feb 22, 2014

@author: luis
'''
from __future__ import division
import DTNCoreProcedures as dtnCore
import math

class timeAveragePolicy:
    
    def calculeZt(self, cycleTime, timeAverage, currentTime ):
        #print 'method:' + 'calculeZt' + 'Parameters:' + 'cycleTime:' + str(cycleTime) + 'timeAverage:' + str(timeAverage) + 'currentTime:' + str(currentTime)
        valReturn = 0
        if timeAverage > 0:
            valReturn = ( (2*cycleTime) - currentTime) / timeAverage
        else:
            valReturn = 0
        #print 'outputs calculeZt' + str(valReturn)
        return valReturn   
    
    def calculateD1(self, bt, costoBackHaul, tetha0, betaP):
        #print 'method:' + 'calculateD1' + 'Parameters:' + 'bt:' + str(bt) + 'tetha0' + str(tetha0) + 'betaP:' + str(betaP)
        if bt >= (tetha0*betaP):
            valReturn = (bt - ( (costoBackHaul + tetha0) *betaP )) / 2
        else:
            valReturn = 0
        #print 'outputs calculateD1:' + str(valReturn)
        return valReturn
    
    def calculateD2(self, bt, costoRealTime, betaP):
        #print 'method:' + 'calculateD2' + 'Parameters:' + 'bt:' + str(bt) + 'costoRealTime' + str(costoRealTime) + 'betaP:' + str(betaP)
        if (bt >= (costoRealTime*betaP)):
            valReturn = (bt - (costoRealTime*betaP)) / 2
        else:
            valReturn = 0 
        #print 'outputs calculateD2:' + str(valReturn)
        return valReturn
    
    def calculateD3(self, bt, Zt,  k1, k2, costBackHaul, tetha0, costoRealTime, betaP):
        #print 'method:' + 'calculateD3' + 'Parameters:' + 'bt:' + str(bt) + 'Zt:' + str(Zt) + 'k1:'+ str(k1) + 'k2:' + str(k2) + 'costBackHaul:' + str(costBackHaul) + 'costoRealTime' + str(costoRealTime) + 'betaP:' + str(betaP)
        value1 = ( bt * Zt )
        value2 = costoRealTime * (Zt - 1)
        value3 = costBackHaul + tetha0 
        value4 = ( value2 + value3 ) * betaP
        value5 = value1 - value4
        valReturn = value5 / (2 * Zt)
        if valReturn < 0:
            valReturn = 0
        #print 'outputs calculateD2:' + str(valReturn)
        return  valReturn
            
    def calculateT1(self, cycleTime, k1, k2, timeAverage):
        #print 'method:' + 'calculateT1' + 'Parameters:' + 'k1:' + str(k1) + 'k2' + str(k2) + 'timeAverage:' + str(timeAverage)
        if k1 > 0:
            t1calc = 2*cycleTime - (timeAverage*((k2/k1)+1)) 
            valReturn = max(0, t1calc)
        else:
            valReturn = 0 
        
        #print 'outputs calculateT1:' + str(valReturn)
        return valReturn
    
    def calculateT2(self, cycleTime, k1, k2, timeAverage):
        #print 'method:' + 'calculateT2' + 'Parameters:' + 'cycleTime:' + str(cycleTime) + 'k1:' + str(k1) + 'k2' + str(k2) + 'timeAverage:' + str(timeAverage)
        t2 = (2 * cycleTime) - timeAverage
        #print 'outputs calculateT2:' + str(t2)
        return t2 
       
    def calculateCaseOneModelWithoutTimeConstraint(self, bt, k1, k2, costoBackchaul, tetha0, costoRealTime, betaP):
        retorno = {}
        retorno['price'] = (bt + (( costoBackchaul + tetha0 ) * betaP ))/ (2*betaP)
        retorno['backHaul'] = (bt - ((costoBackchaul + tetha0)*betaP))/2
        retorno['realTime'] = 0
        retorno['demand'] = ((bt - ((costoBackchaul + tetha0)*betaP)))/2
        return retorno

    def calculateCaseTwoModelWithoutTimeConstraint(self, bt, k1, k2, tetha0, costoRealTime, betaP):
        retorno = {}
        retorno['price'] = (bt - k1)/(betaP)
        retorno['backHaul'] = k1
        retorno['realTime'] = 0
        retorno['demand'] = k1
        return retorno

    def calculateCaseThreeModelWithoutTimeConstraint(self, bt, k1, k2, tetha0, costoRealTime, betaP):
        retorno = {}
        if bt >= ((costoRealTime*betaP) - (2*k1)):
            retorno['price'] = (bt + (costoRealTime* betaP))/(2*betaP)
            retorno['backHaul'] = k1
            retorno['realTime'] = (bt - (costoRealTime*betaP) - (2*k1))/2
            retorno['demand'] = (bt - costoRealTime*betaP)/2
        else:
            retorno['price'] = bt / betaP
            retorno['backHaul'] = 0
            retorno['realTime'] = 0
            retorno['demand'] = 0                    
        return retorno

    def calculateCaseFourModelWithoutTimeConstraint(self, bt, k1, k2, tetha0, costoRealTime, betaP):
        retorno = {}
        retorno['price'] = (bt - k1 - k2) /  betaP
        retorno['backHaul'] = k1
        retorno['realTime'] = k2
        retorno['demand'] = k1 + k2
        return retorno

    def calculateCaseFiveModelWithoutTimeConstraint(self, bt, k1, k2, tetha0, costoRealTime, betaP):
        retorno = {}
        retorno['price'] = (bt - k2) /  betaP
        retorno['backHaul'] = 0
        retorno['realTime'] = k2
        retorno['demand'] = k2
        return retorno
        
    def calculateCaseSixModelWithoutTimeConstraint(self, bt, k1, k2, tetha0, costoRealTime, betaP, optimalD2):
        retorno = {}
        if optimalD2 > 0:
            retorno['price'] = (bt + (costoRealTime*betaP) ) / (2* betaP)
            retorno['backHaul'] = 0
            retorno['realTime'] = (bt - (costoRealTime*betaP))/2
            retorno['demand'] = (bt - (costoRealTime*betaP))/2
        else:
            retorno['price'] = bt / betaP
            retorno['backHaul'] = 0
            retorno['realTime'] = 0
            retorno['demand'] = 0                    
        return retorno
    
    def calculateCaseOneModelWithTimeConstraint(self, bt, Zt,  k1, k2, costBackHaul, tetha0, costoRealTime, betaP, optimalD3):
        retorno = {}
        if optimalD3 > 0: 
            value1 = ( bt * Zt )
            value2 = costoRealTime * (Zt - 1)
            value3 = costBackHaul + tetha0 
            value4 = ( value2 + value3 ) * betaP
            value5 = value1 - value4
            value6 = value5 * (Zt - 1)
            gStart = value6 / (2*math.pow(Zt, 2))
             
            retorno['price'] = (bt/betaP) - (gStart*Zt)/(betaP*(Zt - 1))
            retorno['backHaul'] = gStart / (Zt - 1)
            retorno['realTime'] = gStart
            retorno['demand'] = gStart + (gStart / (Zt - 1))
        else:
            retorno['price'] = bt / betaP
            retorno['backHaul'] = 0
            retorno['realTime'] = 0
            retorno['demand'] = 0        
        #print retorno
        return retorno

    def calculateCaseTwoModelWithTimeConstraint(self, bt, Zt,  k1, k2, costBackHaul, tetha0, costoRealTime, betaP, optimalD3):
        retorno = {}
        gStart = k2
        retorno['price'] = (bt/betaP) - (gStart*Zt)/(betaP*(Zt - 1))
        retorno['backHaul'] = gStart / (Zt - 1)
        retorno['realTime'] = gStart
        retorno['demand'] = gStart + (gStart / (Zt - 1))
        #print retorno 
        return retorno

    def calculateCaseThreeModelWithTimeConstraint(self, bt, Zt,  k1, k2, costBackHaul, tetha0, costoRealTime, betaP, optimalD3):
        retorno = {}
        gStart = k1
        retorno['price'] =  (bt - (Zt*gStart))/ betaP
        retorno['backHaul'] = gStart
        retorno['realTime'] = ((Zt - 1) * gStart)
        retorno['demand'] = (Zt * gStart)
        #print retorno
        return retorno
    
    def calculateCaseFourModelWithTimeConstraint(self, bt, Zt,  k1, k2, costBackHaul, tetha0, costoRealTime, betaP, optimalD3):
        retorno = {}
        if optimalD3 > 0: 
            value1 = ( bt * Zt )
            value2 = costoRealTime * (Zt - 1)
            value3 = costBackHaul + tetha0 
            value4 = ( value2 + value3 ) * betaP
            value5 = value1 - value4
            gStart = value5 / (2*math.pow(Zt, 2))
            retorno['price'] =  (bt - (Zt*gStart))/ betaP
            retorno['backHaul'] = gStart
            retorno['realTime'] = ((Zt - 1) * gStart)
            retorno['demand'] = (Zt * gStart)
        else:
            retorno['price'] = bt / betaP
            retorno['backHaul'] = 0
            retorno['realTime'] = 0
            retorno['demand'] = 0        
        #print retorno
        return retorno
               
    def calculateCaseOneWithTimeConstraint(self, k1, k2, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, costRealTime, betaP, acumBasedOnk2, Zt, t1, t2, optimalD1, optimalD2, optimalD3):
        # acumBasedOnK2 represents the value K2Z(t) /( Z(t) -1 )
        #print 'method:' + 'calculateCaseOne' + 'Parameters:' + 'k1:' + str(k1) + 'k2:' + str(k2) + 'cycleTime:' + str(cycleTime) + 'timeAverage:' + str(timeAverage)  + 'currentTime:' + str(currentTime) +  'bt:' + str(bt) + 'tetha0:' + str(tetha0)  + 'costoRealTime:' + str(costoRealTime) + 'betaP:' + str(betaP) + 'acumBasedOnk2:' + str(acumBasedOnk2) + 'Zt:' + str(Zt) + 't1:' + str(t1) + 'optimalD1:' + str(optimalD1) + 'optimalD2:' + str(optimalD2)
        valueReturn = {}
        if (acumBasedOnk2 >= optimalD3) and (currentTime <= t1):
            retorno = self.calculateCaseOneModelWithTimeConstraint( bt, Zt,  k1, k2, costBackhaul, tetha0, costRealTime, betaP, optimalD3)                                            
            valueReturn['found'] = True
            valueReturn['result'] = retorno
        else:
            valueReturn['found'] = False
            valueReturn['result'] = {}
        #print 'outputs calculateCaseOne:' + retorno.__str__()
        return valueReturn
                   
    def calculateCaseTwoWithTimeConstraint(self, k1, k2, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, costRealTime, betaP, acumBasedOnk2, Zt, t1, t2, optimalD1, optimalD2, optimalD3):
        #print 'method:' + 'calculateCaseTwo' + 'Parameters:' + 'k1:' + str(k1) + 'k2:' + str(k2) + 'cycleTime:' + str(cycleTime) + 'timeAverage:' + str(timeAverage)  + 'currentTime:' + str(currentTime) +  'bt:' + str(bt) + 'tetha0:' + str(tetha0)  + 'costoRealTime:' + str(costoRealTime) + 'betaP:' + str(betaP) + 'acumBasedOnk2:' + str(acumBasedOnk2) + 'Zt:' + str(Zt) + 't1:' + str(t1) + 'optimalD1:' + str(optimalD1) + 'optimalD2:' + str(optimalD2)
        valueReturn = {}
        if (acumBasedOnk2 <= optimalD3) and (currentTime <= t1):
            retorno = self.calculateCaseTwoModelWithTimeConstraint( bt, Zt,  k1, k2, costBackhaul, tetha0, costRealTime, betaP, optimalD3)
            valueReturn['found'] = True
            valueReturn['result'] = retorno
        else:
            valueReturn['found'] = False
            valueReturn['result'] = {}
        #print 'outputs calculateCaseTwo:' + valueReturn.__str__()
        return valueReturn

    def calculateCaseThreeWithTimeConstraint(self, k1, k2, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, costRealTime, betaP, acumBasedOnk2, Zt, t1, t2, optimalD1, optimalD2, optimalD3):
        #print 'method:' + 'calculateCaseThree' + 'Parameters:' + 'k1:' + str(k1) + 'k2:' + str(k2) + 'cycleTime:' + str(cycleTime) + 'timeAverage:' + str(timeAverage)  + 'currentTime:' + str(currentTime) +  'bt:' + str(bt) + 'tetha0:' + str(tetha0)  + 'costoRealTime:' + str(costoRealTime) + 'betaP:' + str(betaP) + 'acumBasedOnk2:' + str(acumBasedOnk2) + 'Zt:' + str(Zt) + 't1:' + str(t1) + 'optimalD1:' + str(optimalD1) + 'optimalD2:' + str(optimalD2)
        valueReturn = {}
        maxflowU1 = Zt * k1
        if (maxflowU1 <= optimalD3) and (currentTime >= t1 and currentTime <= t2):
            retorno = self.calculateCaseThreeModelWithTimeConstraint( bt, Zt,  k1, k2, costBackhaul, tetha0, costRealTime, betaP, optimalD3)
            valueReturn['found'] = True
            valueReturn['result'] = retorno
        else:
            valueReturn['found'] = False
            valueReturn['result'] = {}
        #print 'outputs calculateCaseThree:' + retorno.__str__()
        return valueReturn

    def calculateCaseFourWithTimeConstraint(self, k1, k2, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, costRealTime, betaP, acumBasedOnk2, Zt, t1, t2, optimalD1, optimalD2, optimalD3):
        #print 'method:' + 'calculateCaseFour' + 'Parameters:' + 'k1:' + str(k1) + 'k2:' + str(k2) + 'cycleTime:' + str(cycleTime) + 'timeAverage:' + str(timeAverage)  + 'currentTime:' + str(currentTime) +  'bt:' + str(bt) + 'tetha0:' + str(tetha0)  + 'costoRealTime:' + str(costoRealTime) + 'betaP:' + str(betaP) + 'acumBasedOnk2:' + str(acumBasedOnk2) + 'Zt:' + str(Zt) + 't1:' + str(t1) + 'optimalD1:' + str(optimalD1) + 'optimalD2:' + str(optimalD2)        
        valueReturn = {}
        maxflowU1 = Zt * k1
        if (maxflowU1 > optimalD3) and (currentTime >= t1 and currentTime <= t2):
            retorno = self.calculateCaseFourModelWithTimeConstraint( bt, Zt,  k1, k2, costBackhaul, tetha0, costRealTime, betaP, optimalD3)
            valueReturn['found'] = True
            valueReturn['result'] = retorno
        else:
            valueReturn['found'] = False
            valueReturn['result'] = {}
        #print 'outputs calculateCaseFour:' + retorno.__str__()
        return valueReturn
           
    def calculateCaseOneWithoutTimeConstraint(self, k1, k2, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, costRealTime, betaP, t1, t2, optimalD1, optimalD2):
        #print 'method:' + 'calculateCaseOne' + 'Parameters:' + 'k1:' + str(k1) + 'k2:' + str(k2) + 'cycleTime:' + str(cycleTime) + 'timeAverage:' + str(timeAverage)  + 'currentTime:' + str(currentTime) +  'bt:' + str(bt) + 'tetha0:' + str(tetha0)  + 'costoRealTime:' + str(costoRealTime) + 'betaP:' + str(betaP) + 'acumBasedOnk2:' + str(acumBasedOnk2) + 'Zt:' + str(Zt) + 't1:' + str(t1) + 'optimalD1:' + str(optimalD1) + 'optimalD2:' + str(optimalD2)
        valueReturn = {}
        if (k1 >= optimalD1):
            if currentTime >= t1 and currentTime >= t2:
                retorno = self.calculateCaseOneModelWithoutTimeConstraint(bt, k1, k2, costBackhaul, tetha0, costRealTime, betaP)                                    
                valueReturn['found'] = True
                valueReturn['result'] = retorno
            else:
                valueReturn['found'] = False
                valueReturn['result'] = {}                            
        else:
            valueReturn['found'] = False
            valueReturn['result'] = {}
        #print 'outputs calculateCaseOne:' + retorno.__str__()
        return valueReturn
                   
    def calculateCaseTwoWithoutTimeConstraint(self, k1, k2, cycleTime, timeAverage, currentTime, bt, costBackhaul,  tetha0, costRealTime, betaP, t1,t2,  optimalD1, optimalD2):
        #print 'method:' + 'calculateCaseThree' + 'Parameters:' + 'k1:' + str(k1) + 'k2:' + str(k2) + 'cycleTime:' + str(cycleTime) + 'timeAverage:' + str(timeAverage)  + 'currentTime:' + str(currentTime) +  'bt:' + str(bt) + 'tetha0:' + str(tetha0)  + 'costoRealTime:' + str(costoRealTime) + 'betaP:' + str(betaP) + 'acumBasedOnk2:' + str(acumBasedOnk2) + 'Zt:' + str(Zt) + 't1:' + str(t1) + 'optimalD1:' + str(optimalD1) + 'optimalD2:' + str(optimalD2)
        valueReturn = {}
        if (k1 <= optimalD1) and (optimalD2 <= k1 ):
            if currentTime >= t1 and currentTime >= t2:
                retorno = self.calculateCaseTwoModelWithoutTimeConstraint(bt, k1, k2, tetha0, costRealTime, betaP)
                valueReturn['found'] = True
                valueReturn['result'] = retorno
            else:
                valueReturn['found'] = False
                valueReturn['result'] = {}                            
        else:
            valueReturn['found'] = False
            valueReturn['result'] = {}
        #print 'outputs calculateCaseThree:' + retorno.__str__()
        return valueReturn
  
    def calculateCaseThreeWithoutTimeConstraint(self, k1, k2, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, costRealTime, betaP, t1, t2, optimalD1, optimalD2):
        #print 'method:' + 'calculateCaseFive' + 'Parameters:' + 'k1:' + str(k1) + 'k2:' + str(k2) + 'cycleTime:' + str(cycleTime) + 'timeAverage:' + str(timeAverage)  + 'currentTime:' + str(currentTime) +  'bt:' + str(bt) + 'tetha0:' + str(tetha0)  + 'costoRealTime:' + str(costoRealTime) + 'betaP:' + str(betaP) + 'acumBasedOnk2:' + str(acumBasedOnk2) + 'Zt:' + str(Zt) + 't1:' + str(t1) + 'optimalD1:' + str(optimalD1) + 'optimalD2:' + str(optimalD2)
        valueReturn = {}
        if (k1 <= optimalD2) and (k1 + k2 >= optimalD2 ):
            if currentTime >= t1 and currentTime >= t2:
                retorno = self.calculateCaseThreeModelWithoutTimeConstraint(bt, k1, k2, tetha0, costRealTime, betaP)    
                valueReturn['found'] = True
                valueReturn['result'] = retorno
            else:
                valueReturn['found'] = False
                valueReturn['result'] = {}                            
        else:
            valueReturn['found'] = False
            valueReturn['result'] = {}
        #print 'outputs calculateCaseFive:' + retorno.__str__()
        return valueReturn

    def calculateCaseFourWithoutTimeConstraint(self, k1, k2, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, costRealTime, betaP, t1, t2, optimalD1, optimalD2):
        #print 'method:' + 'calculateCaseSeven' + 'Parameters:' + 'k1:' + str(k1) + 'k2:' + str(k2) + 'cycleTime:' + str(cycleTime) + 'timeAverage:' + str(timeAverage)  + 'currentTime:' + str(currentTime) +  'bt:' + str(bt) + 'tetha0:' + str(tetha0)  + 'costoRealTime:' + str(costoRealTime) + 'betaP:' + str(betaP) + 'acumBasedOnk2:' + str(acumBasedOnk2) + 'Zt:' + str(Zt) + 't1:' + str(t1) + 'optimalD1:' + str(optimalD1) + 'optimalD2:' + str(optimalD2)
        valueReturn = {}
        if (k1 + k2  <= optimalD2 ):
            if currentTime >= t1 and currentTime >= t2:
                retorno = self.calculateCaseFourModelWithoutTimeConstraint(bt, k1, k2, tetha0, costRealTime, betaP)    
                valueReturn['found'] = True
                valueReturn['result'] = retorno
            else:
                valueReturn['found'] = False
                valueReturn['result'] = {}
        else:
            valueReturn['found'] = False
            valueReturn['result'] = {}
        #print 'outputs calculateCaseSeven:' + retorno.__str__()
        return valueReturn

    def calculateCaseFiveWithoutTimeConstraint(self, k1, k2, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, costRealTime, betaP, t1, t2, optimalD1, optimalD2):
        #print 'method:' + 'calculateCaseEight' + 'Parameters:' + 'k1:' + str(k1) + 'k2:' + str(k2) + 'cycleTime:' + str(cycleTime) + 'timeAverage:' + str(timeAverage)  + 'currentTime:' + str(currentTime) +  'bt:' + str(bt) + 'tetha0:' + str(tetha0)  + 'costoRealTime:' + str(costoRealTime) + 'betaP:' + str(betaP) + 'acumBasedOnk2:' + str(acumBasedOnk2) + 'Zt:' + str(Zt) + 't1:' + str(t1) + 'optimalD1:' + str(optimalD1) + 'optimalD2:' + str(optimalD2)
        valueReturn = {}
        if (k1 == 0) and (k2 <= optimalD2):
            if currentTime >= t1 and currentTime >= t2:
                retorno = self.calculateCaseFiveModelWithoutTimeConstraint(bt, k1, k2, tetha0, costRealTime, betaP)
                valueReturn['found'] = True
                valueReturn['result'] = retorno
            else:
                valueReturn['found'] = False
                valueReturn['result'] = {}            
        else:
            valueReturn['found'] = False
            valueReturn['result'] = {}
        #print 'outputs calculateCaseEight:' + retorno.__str__()
        return valueReturn

    def calculateCaseSixWithoutTimeConstraint(self, k1, k2, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, costRealTime, betaP, t1, t2, optimalD1, optimalD2):
        #print 'method:' + 'calculateCaseNine' + 'Parameters:' + 'k1:' + str(k1) + 'k2:' + str(k2) + 'cycleTime:' + str(cycleTime) + 'timeAverage:' + str(timeAverage)  + 'currentTime:' + str(currentTime) +  'bt:' + str(bt) + 'tetha0:' + str(tetha0)  + 'costoRealTime:' + str(costoRealTime) + 'betaP:' + str(betaP) + 'acumBasedOnk2:' + str(acumBasedOnk2) + 'Zt:' + str(Zt) + 't1:' + str(t1) + 'optimalD1:' + str(optimalD1) + 'optimalD2:' + str(optimalD2)
        valueReturn = {}
        if (k1 == 0) and (k2 > optimalD2):
            if currentTime >= t1 and currentTime >= t2:
                retorno = self.calculateCaseSixModelWithoutTimeConstraint(bt, k1, k2, tetha0, costRealTime, betaP, optimalD2)
                valueReturn['found'] = True
                valueReturn['result'] = retorno
            else:
                valueReturn['found'] = False
                valueReturn['result'] = {}                
        else:
            valueReturn['found'] = False
            valueReturn['result'] = {}
        #print 'outputs calculateCaseNine:' + retorno.__str__()
        return valueReturn   
    
    def applyOptimalPolicy(self, k1, k2, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, costRealTime, betaP):
        #print 'method:' + 'applyOptimalPolicy' + 'Parameters:' + 'k1' + str(k1) + 'k2'  + str(k2) + 'cycleTime' +  str(cycleTime) + 'timeAverage' + str(timeAverage)  + 'currentTime' + str(currentTime)  + 'bt' + str(bt)  + 'tetha0' + str(tetha0)+ 'costoRealTime' + str(costoRealTime) + 'betaP' + str(betaP)
        turnResultEnd ={}
        found= False
        Zt = self.calculeZt(cycleTime, timeAverage, currentTime)
        D1 = self.calculateD1(bt, costBackhaul, tetha0, betaP)
        D2 = self.calculateD2(bt, costRealTime, betaP)
        D3 = self.calculateD3(bt, Zt,  k1, k2, costBackhaul, tetha0, costRealTime, betaP)
        t1 = self.calculateT1( cycleTime, k1, k2, timeAverage)
        t2 = self.calculateT2( cycleTime, k1, k2, timeAverage)
        if Zt > 1: 
            acumBasedOnk2 = (k2 * Zt)  / (Zt - 1)
            if found == False:
                result = self.calculateCaseOneWithTimeConstraint(k1, k2, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, costRealTime, betaP, acumBasedOnk2, Zt, t1, t2, D1, D2, D3)
                if result['found'] == True:
                    turnResultEnd = result['result']
                    found = result['found']
            if found == False:
                result = self.calculateCaseTwoWithTimeConstraint(k1, k2, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, costRealTime, betaP, acumBasedOnk2, Zt, t1, t2, D1, D2, D3)
                if result['found'] == True:
                    turnResultEnd = result['result']
                    found = result['found']
            if found == False:
                result = self.calculateCaseThreeWithTimeConstraint(k1, k2, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, costRealTime, betaP, acumBasedOnk2, Zt, t1, t2, D1, D2, D3)
                if result['found'] == True:
                    turnResultEnd = result['result']
                    found = result['found']
            if found == False:
                result = self.calculateCaseFourWithTimeConstraint(k1, k2, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, costRealTime, betaP, acumBasedOnk2, Zt, t1, t2, D1, D2, D3)
                if result['found'] == True:
                    turnResultEnd = result['result']
                    found = result['found']
        else: 
            if found == False:
                result = self.calculateCaseOneWithoutTimeConstraint(k1, k2, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, costRealTime, betaP, t1, t2, D1, D2)
                if result['found'] == True:
                    turnResultEnd = result['result']
                    found = result['found']
            if found == False:
                result = self.calculateCaseTwoWithoutTimeConstraint(k1, k2, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, costRealTime, betaP, t1, t2, D1, D2)
                if result['found'] == True:
                    turnResultEnd = result['result']
                    found = result['found']
            if found == False:
                result = self.calculateCaseThreeWithoutTimeConstraint(k1, k2, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, costRealTime, betaP, t1, t2, D1, D2)
                if result['found'] == True:
                    turnResultEnd = result['result']
                    found = result['found']
            if found == False:
                result = self.calculateCaseFourWithoutTimeConstraint(k1, k2, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, costRealTime, betaP, t1, t2, D1, D2)
                if result['found'] == True:
                    turnResultEnd = result['result']
                    found = result['found']
            if found == False:
                result = self.calculateCaseFiveWithoutTimeConstraint(k1, k2, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, costRealTime, betaP, t1, t2, D1, D2)
                if result['found'] == True:
                    turnResultEnd = result['result']
                    found = result['found']
            if found == False:
                result = self.calculateCaseSixWithoutTimeConstraint(k1, k2, cycleTime, timeAverage, currentTime, bt, costBackhaul, tetha0, costRealTime, betaP, t1, t2, D1, D2)
                if result['found'] == True:
                    turnResultEnd = result['result']
                    found = result['found']
        
        #print 'method:' + 'applyOptimalPolicy' + 'Output:' + turnResultEnd.__str__()
        return turnResultEnd

    def calculateOptimalInventoryReduceCost(self,constants, k1, k2, totalInventory, betaPrice ):
        # Calculates the value of the reduced cost associated with the backhaul inventory
        #print 'method:' + 'calculateTheta0' + 'totalInventory' + str(totalInventory) + 'betaPrice' + str(betaPrice) + 't2' + str(t2)
        
        t2 = self.calculateT2( constants['cycleTime'], k1, k2, constants['timeAverage'])
        
        valTheta0 = 0
        megaBytesContact = constants['MbytesContact']
        valueToSubtract = megaBytesContact - totalInventory
        if valueToSubtract < 0:
            val1 = (betaPrice * math.pow(constants['timeAverage'], 2)) / 2
            val2 = constants['cycleTime'] * constants['phro']
            val3 = val2 - t2
            val4 = (val1/val3) - (val1/val2) 
            val5 = (betaPrice*(constants['cycleTime'] - t2)) / 2 
            valTheta0 = valueToSubtract / (val4 + val5)
            valTheta0 = valTheta0 * -1
        valTheta0 = valTheta0 / 60
        valReturn = {'theta0' : valTheta0}                 
        #print 'method:' + 'calculateTheta0' + str(valTheta0)
        return valReturn


    def calculateOptimalPolicyByServiceCycle(self, k1, tetha0, constants, service, period, continuosData, season, k2, betaTime, hourInit, hourEnd, minuteInit, minuteEnd, pricePolicy):
        #print 'method:' + 'calculateOptimalPolicyByService' + 'Parameters:' + 'service' + str(service) + 'period' + str(period) + 'season' + str(season) + 'serversAssigned' + str(serversAssigned) + 'betaTime' + str(betaTime) + ' k1:' + str(k1) + 'tetha0:' + str(tetha0)
        #print 'value for k2:' + str(k2)
                
        dtn = dtnCore.CoreMethods()       
                
        cycleTime = constants['cycleTime']
        timeAverage = constants['timeAverage']
        costRealTime = dtn.calculateRealTimeCostByMegaByte(constants) 
        costBackhaul = dtn.calculateBackhaulCostByMegaByte(constants)
        maxK2 = 0
        serviceDataPeriod = continuosData[service][period]
        betaPrice = serviceDataPeriod['betaPrice' + season]   # betaPrice by day - according to tests, this is the correct one.
        serviceDataPeriod = serviceDataPeriod[season]   
        t1 = self.calculateT1(cycleTime, k1, k2, timeAverage)     
        incomeCycle = 0
        costCycle = 0
        demandCycle = 0
        inventoryCycle = 0
        dictionaryReturn = {}
        for hour in range(int(hourInit), int(hourEnd)): 
            #betaPrice = serviceDataPeriod[hour]['betaPrice'] # betaPrice by hour
            data = serviceDataPeriod[hour]['data'] 
            incomeHour = 0
            demandHour = 0
            inventoryHour = 0
            costHour = 0 
            dictionaryReturnHour = {}
            for minute in range (int(minuteInit),int(minuteEnd)):
                potentialMarket = data[minute]['potentialMarket']
                #betaPrice = data[minute]['betaPrice'] # betaPrice by minute
                b_t = potentialMarket - (betaTime * (timeAverage/60))
                currentTime = hour - constants['initWorkingHour']
                currentTime = currentTime + (minute / 60)
                currentTime = math.fmod(currentTime, cycleTime)    
                turnResultEndBd = self.applyOptimalPolicy(k1, k2, cycleTime, timeAverage, currentTime, b_t, costBackhaul, tetha0, costRealTime, betaPrice)
                dictionaryReturnHour[minute] = { 'price' : turnResultEndBd['price'], 'backHaul' :  turnResultEndBd['backHaul'], 'realTime': turnResultEndBd['realTime'], 'optDemand' : turnResultEndBd['demand'], 'potentialMarket' : potentialMarket, 'betaPrice' : betaPrice }
                if turnResultEndBd['realTime'] > maxK2:
                    maxK2 = turnResultEndBd['realTime']
                incomeHour = incomeHour +  ( turnResultEndBd['price'] * turnResultEndBd['demand']) 
                costHour = costHour + ( turnResultEndBd['backHaul'] * costBackhaul ) + ( turnResultEndBd['realTime'] *  costRealTime)
                demandHour = demandHour + turnResultEndBd['demand']
                inventoryHour = inventoryHour + turnResultEndBd['backHaul']
            incomeCycle = incomeCycle + incomeHour
            demandCycle = demandCycle + demandHour
            costCycle = costCycle + costHour 
            inventoryCycle = inventoryCycle + inventoryHour
            dictionaryReturn[hour] = {'data': dictionaryReturnHour, 'income:' : incomeHour, 'betaPrice': betaPrice}
        dictionaryReturnItem = {season: dictionaryReturn,  'income' : incomeCycle, 'cost' : costCycle,  'demand' : demandCycle, 'inventory' : inventoryCycle, 'betaPrice': betaPrice, 'timeOne' : t1, 'maxk2' : maxK2 }
        return dictionaryReturnItem                 