'''
Created on Nov 16, 2013

@author: luis
'''

from __future__ import division
import matplotlib as cm
import matplotlib.pyplot as plt
from matplotlib.mlab import griddata
import pylab 
import matplotlib.gridspec as gridspec
from matplotlib.collections import LineCollection
from matplotlib.path import Path
import matplotlib.patches as patches
from  matplotlib import rc
import numpy as np
import proportionalDTNPricing as pricing 
import DTNCoreProcedures as DtnCore
import math
import datetime, time, calendar
import matplotlib.dates as mdates
import itertools
import pylab, random
from datetime import datetime, timedelta
from os import path
from matplotlib.ticker import FormatStrFormatter

class graphicClass:

    def fillArrayInformationBySeason(self, constants, season, optimalPoliciyDTN):
        model = pricing.pricingModel()
        timeMethods = DtnCore.backHaulCycleTimeMethods()
        numCycles = timeMethods.calculateNumberOfCycles(constants)
        
        time = np.zeros((constants['finalWorkingHour'] - constants['initWorkingHour']) * 60)
        price = np.zeros((constants['finalWorkingHour'] - constants['initWorkingHour']) * 60)
        backhaul = np.zeros( (constants['finalWorkingHour'] - constants['initWorkingHour']) * 60)
        realTime = np.zeros( (constants['finalWorkingHour'] - constants['initWorkingHour']) * 60)
        potentialMarket = np.zeros( (constants['finalWorkingHour'] - constants['initWorkingHour']) * 60)
        
        t1Array = np.zeros(numCycles)

        for cycle in range(numCycles):
            interval = timeMethods.calculateTimeIntervalByCycle(constants, cycle )
            cycleData =  optimalPoliciyDTN[cycle]
            cycleDetails = cycleData['cycleDetails']
            for keyCycle in cycleDetails:
                optimalvalueData = cycleDetails[season]
                t1Cycle = cycleDetails['timeOne'] 
                t1Array[cycle] = t1Cycle                  
                for hour in range(int(interval['initHour']), int(interval['endHour'])):
                    optimalvalueDataDetail = optimalvalueData[hour]['data']
                    for minute in optimalvalueDataDetail:
                        hourMinute = (( hour - constants['initWorkingHour'] ) *60) + (minute)
                        time[hourMinute] = hour + ((minute) / 60)
                        backhaul[hourMinute] = optimalvalueDataDetail[minute]['backHaul']
                        price[hourMinute] = optimalvalueDataDetail[minute]['price']
                        realTime[hourMinute] = optimalvalueDataDetail[minute]['realTime']
                        potentialMarket[hourMinute] = optimalvalueDataDetail[minute]['potentialMarket'] 

        result = {'time' : time, 'price': price, 'backhaul': backhaul, 'realTime' : realTime, 'potentialMarket' : potentialMarket, 't1Array' : t1Array}
        return result
    
    def graphDTNOptimalPolicy(self, constants, season1, optimalPoliciyDTN1, season2, optimalPoliciyDTN2):
                         
        timeMethods = DtnCore.backHaulCycleTimeMethods()
        fig = plt.figure()
        ax = fig.add_subplot(131)
        valReturn1 = self.fillArrayInformationBySeason(constants, season1, optimalPoliciyDTN1)
        valReturn2 = self.fillArrayInformationBySeason(constants, season2, optimalPoliciyDTN2)
        
        
        potentialMarket1 = np.max(valReturn1['potentialMarket'])
        potentialMarket2 = np.max(valReturn2['potentialMarket'])
        if potentialMarket1 >= potentialMarket2:
            potentialMarket = potentialMarket1
        else:
            potentialMarket = potentialMarket2
            
        maxHour = np.max(valReturn1['time']) + 0.1
                
        ax.plot( valReturn1['time'], valReturn1['potentialMarket'], linestyle='dotted', color='0', label=r'Potential Market $b(t)$')
        ax.plot( valReturn1['time'], valReturn1['backhaul'], linestyle='dashed', color='0', label=r'Backhaul $U_1(t)$')
        ax.plot( valReturn1['time'], valReturn1['realTime'], linestyle='solid', color='0', label=r'Real Time $U_2(t)$')
        
        ax.legend(bbox_to_anchor=(0., 1.07, 1., .102), loc=3,ncol=1, prop={'size':11}, mode="expand", borderaxespad=0.)
        ax.axis([np.min(valReturn1['time']), maxHour , 0, potentialMarket ])       
        ax.set_xlabel( "Day Hour" )
        ax.set_ylabel( "Traffic (MBytes)" )
        ax.set_title('Business Days')

        #Draw the initial of the cycle, the end and t1 lines 
        numCycles = timeMethods.calculateNumberOfCycles(constants)
        for cycle in range(numCycles):
            initHour = int (constants['cycleTime'] * cycle ) + constants['initWorkingHour'] 
            endHour = int (constants['cycleTime'] * ( cycle + 1 ))  + constants['initWorkingHour']
            print 'initHour:' + str(initHour) + 'endHour:' + str(endHour)
            ax.axvline(x=endHour, ymin=0.46, ymax=0.52,  color='k' )
            ax.axhline(y=1, color='k', linestyle='dashed' )
            t1Cycle = valReturn1['t1Array'][cycle]
            t1Cycle = t1Cycle + constants['initWorkingHour'] + ( cycle * constants['cycleTime'])
            t1CycleStr = str(t1Cycle)[:4] 
            ax.axvline(x=t1Cycle, color='b', linestyle='dashed')
            ax.text(t1Cycle , 1.90, '$t^1_{C_' +str(cycle + 1) +'}=' + t1CycleStr + '$', fontsize=13)

        ax.text(9, 1.01, 'Cycle 1', fontsize=10)
        ax.text(15, 1.01, 'Cycle 2', fontsize=10)

        ax = fig.add_subplot(132)
        #ax.plot( valReturn2['time'], valReturn2['demand'], label=r'Demand')
        ax.plot( valReturn2['time'], valReturn2['potentialMarket'], linestyle='dotted', color='0', label=r'Potential Market $b(t)$')
        ax.plot( valReturn2['time'], valReturn2['backhaul'], linestyle='dashed', color='0', label=r'Backhaul $U_1(t)$')
        ax.plot( valReturn2['time'], valReturn2['realTime'], linestyle='solid', color='0', label=r'Real Time $U_2(t)$')
        #ax.grid(True)
        ax.axis([np.min(valReturn1['time']), maxHour , 0, potentialMarket ])
        ax.axis(fontsize = 10)
        ax.legend(bbox_to_anchor=(0., 1.07, 1., .102), loc=3,ncol=1,prop={'size':11}, mode="expand", borderaxespad=0.)
        ax.set_xlabel( "Day Hour" )
        ax.set_ylabel( "Traffic (MBytes)" )
        ax.set_title('Weekends')
        #Draw the initial of the cycle, the end and t1 lines 
        numCycles = timeMethods.calculateNumberOfCycles(constants)
        for cycle in range(numCycles):
            initHour = int ( constants['cycleTime'] * cycle ) + constants['initWorkingHour']
            endHour = int (constants['cycleTime'] * ( cycle + 1 )) + constants['initWorkingHour']
            ax.axvline(x=endHour, ymin=0.46, ymax=0.52,  color='k' )
            ax.axhline(y=1, color='k', linestyle='dashed' )
            t1Cycle = valReturn2['t1Array'][cycle]
            t1Cycle = t1Cycle + constants['initWorkingHour'] + ( cycle * constants['cycleTime'])
            ax.axvline(x=t1Cycle, color='b', linestyle='dashed')
            t1CycleStr = str(t1Cycle)[:4] 
            ax.axvline(x=t1Cycle, color='b', linestyle='dashed')
            ax.text(t1Cycle, 1.90, '$t^1_{C_' +str(cycle + 1) +'}=' + t1CycleStr + '$', fontsize=13)
        ax.text(9, 1.01, 'Cycle 1', fontsize=10)
        ax.text(15, 1.01, 'Cycle 2', fontsize=10)

        ax = fig.add_subplot(133)
        ax.plot( valReturn1['time'], valReturn1['price'], linestyle='dotted', color='0', label=r'Business Days', )
        ax.plot( valReturn2['time'], valReturn2['price'], linestyle='solid', color='0', label=r'Week Ends')
        ax.legend(bbox_to_anchor=(0., 1.07, 1., .102), loc=3,ncol=1, prop={'size':11},  mode="expand", borderaxespad=0.)
        ax.set_xlabel( "Day Hour" )
        ax.set_ylabel( "Traffic (US Dollars)" )
        ax.set_title('Prices')

        #Draw the initial of the cycle, the end and t1 lines 
        numCycles = timeMethods.calculateNumberOfCycles(constants)
        for cycle in range(numCycles):
            initHour = int (constants['cycleTime'] * cycle ) + constants['initWorkingHour'] 
            endHour = int (constants['cycleTime'] * ( cycle + 1 ))  + constants['initWorkingHour']
            print 'initHour:' + str(initHour) + 'endHour:' + str(endHour)
            ax.axvline(x=endHour, ymin=0.022, ymax=0.024,  color='k' )
            ax.axhline(y=0.0225, color='k', linestyle='dashed' )
            t1Cycle = valReturn1['t1Array'][cycle]
            t1Cycle = t1Cycle + constants['initWorkingHour'] + ( cycle * constants['cycleTime'])
            t1CycleStr = str(t1Cycle)[:4] 
            ax.axvline(x=t1Cycle, color='b', linestyle='dashed')
            ax.text(t1Cycle, 0.0265, '$t^1_{C_' +str(cycle + 1) +'}=' + t1CycleStr + '$', fontsize=13)

        ax.text(9, 0.0227, 'Cycle 1', fontsize=10)
        ax.text(15, 0.0227, 'Cycle 2', fontsize=10)

        plt.show()
    
    def fillArrayInformationBySeasonCycle(self, optimalPolicy, initValue, endValue, Increment, season, cycle):
        
        lenght = (endValue - initValue)/Increment
        parameter = np.zeros(lenght + 1)
        demandArray =  np.zeros(lenght + 1)
        incomeArray = np.zeros(lenght + 1)
        parameterValue = initValue
        counter = 0
        while round(endValue - parameterValue, 3) >= 0 :
            print parameterValue.__repr__()
            data = optimalPolicy[parameterValue][season]
            demand = data[cycle]['maxDemand']
            income = data[cycle]['income']
            parameter[counter] = parameterValue
            demandArray[counter] = demand
            incomeArray[counter] = income
            parameterValue = round(parameterValue + round(Increment, 3),3)
            counter = counter + 1
        valReturn = {'parameter' : parameter , 'demand': demandArray, 'income' : incomeArray}
        return valReturn
           
    def graphDemandIncomeAgaintsParameter(self, constants, data):
        
        # Obtains the number of parameters to graph
        count = 0
        for key in data:
            count = count + 1
        
        fig = plt.figure()        
        for key in data:
            dataParam = data[key]
            optimalPolicy = dataParam['optimalPolicy'] 
            initValue = dataParam['initValue'] 
            endValue = dataParam['endValue']
            Increment = dataParam['increment']
            textXAxis= dataParam['textXAxis']
            textYAxis=dataParam['textYAxis']
            model = pricing.backHaulInventory()
            numCycles = model.calculateNumberOfCycles(constants)
            for cycle in range(numCycles):
                season = 'businessDays'
                valReturnBusinessDays = self.fillArrayInformationBySeasonCycle(optimalPolicy, initValue, endValue, Increment, season, cycle)
                season = 'weekEnds'
                valReturnWeekeEnds  = self.fillArrayInformationBySeasonCycle(optimalPolicy, initValue, endValue, Increment, season, cycle)
                if cycle == 0:
                    demandBusinessDaysArray = valReturnBusinessDays['demand']
                    demandWeekendsArray = valReturnWeekeEnds['demand']
                    incomeBusinessDaysArray = valReturnBusinessDays['income']
                    incomeWeekendsArray = valReturnWeekeEnds['income']
                else:
                    demandBusinessDaysArray = np.add(demandBusinessDaysArray, valReturnBusinessDays['demand'])
                    demandWeekendsArray = np.add(demandWeekendsArray, valReturnWeekeEnds['demand'])
                    incomeBusinessDaysArray = np.add(incomeBusinessDaysArray, valReturnBusinessDays['income'])
                    incomeWeekendsArray = np.add(incomeWeekendsArray, valReturnWeekeEnds['income'])
                
            
            max1 = np.max(incomeBusinessDaysArray)
            max2 = np.max(incomeWeekendsArray)
            if max1 >= max2:
                maxIncome = max1
            else:
                maxIncome = max2
    
            max1 = np.max(demandBusinessDaysArray)
            max2 = np.max(demandWeekendsArray)
            if max1 >= max2:
                maxDemand = max1
            else:
                maxDemand = max2
            
            minX = np.min(valReturnBusinessDays['parameter'])
            maxX = np.max(valReturnBusinessDays['parameter'])
            ax = fig.add_subplot(2,count, key)
            ax.axis([minX , maxX , 0, maxDemand ])
            ax.plot(valReturnBusinessDays['parameter'], demandBusinessDaysArray, linestyle='dashed', color='0', label=r'BusinessDays' )
            ax.plot(valReturnWeekeEnds['parameter'], demandWeekendsArray, linestyle='solid', color='0', label=r'WeekEnds')
            ax.legend(bbox_to_anchor=(0., 1.07, 1., .102), loc=3,ncol=2, prop={'size':11}, mode="expand", borderaxespad=0.)
            
            if key == 1:
                ax.set_ylabel( textYAxis['1'], fontsize=11 )
    
    
            ax = fig.add_subplot(2,count,count + key)
            ax.axis([minX, maxX , 0, maxIncome ])
            ax.plot(valReturnBusinessDays['parameter'], incomeBusinessDaysArray, linestyle='dashed', color='0',  label=r'BusinessDays' )
            ax.plot(valReturnWeekeEnds['parameter'], incomeWeekendsArray, linestyle='solid', color='0', label=r'WeekEnds' )
            ax.set_xlabel( textXAxis )

            if key == 1:
                ax.set_ylabel( textYAxis['2'],  )
            
        plt.show()
   
    def graphProfitChange(self, filename1):
    
        data1 = np.genfromtxt(filename1,dtype=float, skip_header=2, delimiter=';')
 
        plt.close('all')
        fig = plt.figure()
        
        ax = fig.add_subplot(2,1,1)
        ax.grid(True)
        N = len(data1)        
        ## necessary variables
        usedCapacityColumn = 0 
        ind = np.arange(N)  # the x locations for the groups
        width = 0.2                     # the width of the bars
    
        meanColumn = 1 
        stdColumn = 2 
        meanProfitBh = np.divide(data1[:, meanColumn], 1000)
        StdProfitBh =  np.divide(data1[:,stdColumn],1000)
        ## the bars
        rects1 = ax.bar(ind, meanProfitBh, width,color='0.3',
                        #yerr=StdProfitBh,
                        error_kw=dict(elinewidth=0.8,ecolor='black'), label = "Mixed connection") 
        yMin = np.min(meanProfitBh) 
        yMax = np.max(meanProfitBh)          
        meanColumn = 3 
        stdColumn = 4
        meanProfitBh2 = np.divide(data1[:, meanColumn],1000)
        StdProfitBh2 =  np.divide( data1[:,stdColumn], 1000)
        ## the bars
        rects2  = ax.bar(ind+width, meanProfitBh2, width,color='0.6',
                         #yerr=StdProfitRt,
                         error_kw=dict(elinewidth=0.8,ecolor='black'), label="Single Connection") 

        if yMin >  np.min(meanProfitBh2):
            yMin = np.min(meanProfitBh2)
        
        if yMax < np.max(meanProfitBh2):
            yMax = np.max(meanProfitBh2)    

        width = 0.2  
        meanColumn = 5 
        stdColumn = 6
        meanProfitRt = np.divide(data1[:, meanColumn],1000)
        StdProfitRt =  np.divide( data1[:,stdColumn], 1000)
        ## the bars
        rects3  = ax.bar(ind+ 2*width, meanProfitRt, width,color='0.9',
                         #yerr=StdProfitRt,
                         error_kw=dict(elinewidth=0.8,ecolor='black'), label="Single Connection") 

        
        if yMin >  np.min(meanProfitRt):
            yMin = np.min(meanProfitRt)
        
        if yMax < np.max(meanProfitRt):
            yMax = np.max(meanProfitRt)    
        
        # axes and labels
        yMin = yMin - 10
        yMax = yMax + 10  
        ax.set_xlim(np.min(ind),np.max(ind) + 0.9)
        ax.set_ylim(yMin,yMax)
        #ax.set_ylabel('Kbps')
        #ax.set_xlabel('Minutes per call')
        #ax.set_title('Model B(2.0 P)', fontdict={'size':11})
        #ax.grid(True)
        #xTickMarks = data1[:,0]
        ax.set_xticks([])
        #xtickNames = ax.set_xticklabels(xTickMarks)
        #plt.setp(xtickNames, rotation=45, fontsize=9)
    
        ## add a legend
        ax.set_title('Average')
        ax.set_ylabel( "Net Profit (US Dollars)" )
        ax.text(0, yMax+ 1, '$10^{3}$', fontsize=13)
        ax.legend((rects1[0], rects2[0], rects3[0]), ('DTN & Real Time ($C_{rt}$=150 Usd)', 'DTN & Real Time ($C_{rt}$=100 Usd)',  'Real Time only'), bbox_to_anchor=(0., 1.2, 1., .102), loc=3,ncol=2, prop={'size':11}, mode="expand", borderaxespad=0.)



        ax = fig.add_subplot(2,1,2)


        N = len(data1)        
        ## necessary variables
        usedCapacityColumn = 0 
        ind = np.arange(N)  # the x locations for the groups
        width = 0.2                     # the width of the bars
    
        meanColumn = 1 
        stdColumn = 2 
        meanProfitBh = np.divide(data1[:, meanColumn], 1000)
        StdProfitBh =  np.divide(data1[:,stdColumn],1000)
        ## the bars
        rects1 = ax.bar(ind, StdProfitBh, width,color='0.3',
                        #yerr=StdProfitBh,
                        error_kw=dict(elinewidth=0.8,ecolor='black')) 
        yMin = np.min(StdProfitBh) 
        yMax = np.max(StdProfitBh)          
        meanColumn = 3 
        stdColumn = 4
        meanProfitBh2 = np.divide(data1[:, meanColumn],1000)
        StdProfitBh2 =  np.divide( data1[:,stdColumn], 1000)
        ## the bars
        rects2  = ax.bar(ind+width, StdProfitBh2, width,color='0.6',
                         #yerr=StdProfitRt,
                         error_kw=dict(elinewidth=0.8,ecolor='black')) 
        
        if yMin >  np.min(StdProfitBh2):
            yMin = np.min(StdProfitBh2)
        
        if yMax < np.max(StdProfitBh2):
            yMax = np.max(StdProfitBh2)    

        width = 0.2                    # the width of the bars
        meanColumn = 5 
        stdColumn = 6
        meanProfitRt = np.divide(data1[:, meanColumn], 1000)
        StdProfitRt =  np.divide(data1[:,stdColumn],1000)
        ## the bars
        rects3 = ax.bar(ind+ 2*width, StdProfitRt, width,color='0.9',
                        #yerr=StdProfitBh,
                        error_kw=dict(elinewidth=0.8,ecolor='black')) 

        if yMin >  np.min(StdProfitRt):
            yMin = np.min(StdProfitRt)
        
        if yMax < np.max(StdProfitRt):
            yMax = np.max(StdProfitRt)    
        
        # axes and labels
        yMin = yMin - 10
        yMax = yMax + 10  
        ax.set_xlim(np.min(ind),np.max(ind) + 0.9)
        ax.set_ylim(yMin,yMax)
        ax.grid(True)
        xTickMarks = data1[:,0]
        ax.set_xticks(ind+width)
        xtickNames = ax.set_xticklabels(xTickMarks)
        plt.setp(xtickNames, fontsize=12)
    
        ## add a legend
        ax.text(0, yMax+ 1, '$10^{3}$', fontsize=13)
        #ax.legend( (rects1[0], rects2[0], rects3[0]), ('DTN & Real Time(150 Usd)', 'DTN & Real Time(100 Usd)','Real Time only') , prop={'size':12})
        ax.set_title('Standard deviation')
        ax.set_ylabel( "Net Profits (US Dollars)" )
        ax.set_xlabel( "MB Consumed by service Http" )
        
        plt.show()


    def graphDemandAgaintsParameter(self, relative_path, file_name):
        

        fname = path.expanduser('~/' + relative_path + '/' + file_name)

        matrix_data = np.genfromtxt(fname,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[1:, 1:] # All rows from column 1 to the end column
        periods = matrix_data[0,1:] # row 0 all columns
        print plot_data 
 
        plt.close('all')
        fig = plt.figure(figsize=(10,5), facecolor='w', edgecolor='k')
        plt.subplots_adjust(left=0.1,right=0.95,bottom=0.1,top=0.90)
        plt.rcParams['axes.linewidth'] = 0.8  
            
        minPeriod = np.min(periods)
        maxPeriod = np.max(periods) + 1
        minDemand = np.min(plot_data) - (np.min(plot_data) * 0.05) 
        maxDemand = np.max(plot_data) + (np.min(plot_data) * 0.05)
        ax = fig.add_subplot(1,1,1)
        ax.grid(True)
        
        ax.axis([minPeriod , maxPeriod , minDemand, maxDemand ])
        ax.plot(periods, plot_data[0,], color='b',  label=r'$q=0.1$'  )
        ax.plot(periods, plot_data[1,], color='g', marker ='+', label=r'$q=0.125$' )
        ax.plot(periods, plot_data[2,], color='r', marker ='.', label=r'$q=0.15$'  )
        ax.plot(periods, plot_data[3,], color='c', marker ='p', label=r'$q=0.175$'  )
        ax.plot(periods, plot_data[4,], color='m', marker ='^', label=r'$q=0.2$'  )
        ax.plot(periods, plot_data[5,], color='y', marker ='x', label=r'$q=0.225$'  )
        ax.plot(periods, plot_data[6,], color='0.5', marker ='s', label=r'$q=0.25$'  )
        ax.set_ylabel( "Traffic(MBs)" )
        ax.set_xlabel( "Months" )
        plt.xticks(range(int(minPeriod),int(maxPeriod),5))
        ax.legend(loc=4,ncol=2, prop={'size':12})
#            b', 'g', 'r', 'c', 'm', 'y', 'k'
#        if key == 1:
#            ax.set_ylabel( textYAxis['1'], fontsize=11 )
#    
#    
#        ax = fig.add_subplot(2,count,count + key)
#        ax.axis([minX, maxX , 0, maxIncome ])
#        ax.plot(valReturnBusinessDays['parameter'], incomeBusinessDaysArray, linestyle='dashed', color='0',  label=r'BusinessDays' )
#        ax.plot(valReturnWeekeEnds['parameter'], incomeWeekendsArray, linestyle='solid', color='0', label=r'WeekEnds' )
#        ax.set_xlabel( textXAxis )
#
#        if key == 1:
#            ax.set_ylabel( textYAxis['2'],  )
#            
        plt.show()

    def graphTrafficByServiceOldData(self, relative_path, file_name):
  
        plt.close('all')
        fig = plt.figure(figsize=(7,5), facecolor='w', edgecolor='k')
        plt.rcParams['axes.linewidth'] = 0.8  
       
        fname1 = path.expanduser('~/' + relative_path + '/' + file_name + '.csv')

        ax1 = fig.add_subplot(1,1,1)
        ax1.grid(True)        
        matrix_data1 = np.genfromtxt(fname1,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data1[1:, 1:] # from row 1 to the end, from column 1 to the end column
        periods = matrix_data1[0,1:] # row 0 from columns 1
             
        minPeriod = np.min(periods)
        maxPeriod = np.max(periods) + 2
        minDemand = np.min(plot_data)
        maxDemand = np.max(plot_data) + 1000
        
        ax1.axis([minPeriod , maxPeriod , minDemand, maxDemand ])
        ax1.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax1.ticklabel_format(style='sci', axis='y')
        ax1.plot(periods, plot_data[0,], color='b',  label=r'Http'  )
        ax1.plot(periods, plot_data[1,], color='g', marker ='+', label=r'E-mail' )
        ax1.plot(periods, plot_data[2,], color='r', marker ='.', label=r'Voice'  )
        ax1.set_ylabel( "Traffic (MBs)" )
        plt.xticks(range(int(minPeriod),int(maxPeriod),5))
        ax1.legend(loc=0, prop={'size':10})
        ax1.set_xlabel( "Months" )

        plt.show()

    def graphTrafficByService(self, relative_path, file_name):
 
 
        plt.close('all')
        fig = plt.figure(figsize=(14,5), facecolor='w', edgecolor='k')
        plt.subplots_adjust(left=0.06,right=0.95,bottom=0.1,top=0.9, hspace = 0.3, wspace = 0.1)
        plt.rcParams['axes.linewidth'] = 0.8  
       

        fname1 = path.expanduser('~/' + relative_path + '/' + file_name + '_60.csv')


        ax1 = fig.add_subplot(2,2,1)
        #ax1.grid(True)        
        matrix_data1 = np.genfromtxt(fname1,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data1[1:, 1:] # from row 1 to the end, from column 1 to the end column
        periods = matrix_data1[0,1:] # row 0 from columns 1
             
        minPeriod = np.min(periods)
        maxPeriod = np.max(periods) + 2
        minDemand = np.min(plot_data)
        maxDemand = np.max(plot_data) + 1000
        
        ax1.axis([minPeriod , maxPeriod , minDemand, maxDemand ])
        ax1.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax1.set_title('Real time cost: 60 Usd', fontsize=10) 
        ax1.ticklabel_format(style='sci', axis='y')
        ax1.plot(periods, plot_data[0,], color='b',  label=r'DTN enabled'  )
        ax1.plot(periods, plot_data[1,], color='g', marker ='+', label=r'Quality assured' )
        ax1.plot(periods, plot_data[2,], color='r', marker ='.', label=r'Real time'  )
        ax1.set_ylabel( "Traffic (MBs)" )
        plt.xticks(range(int(minPeriod),int(maxPeriod),5))
        ax1.legend(loc=0, prop={'size':10})

        fname2 = path.expanduser('~/' + relative_path + '/' + file_name + '_105.csv')

        ax2 = fig.add_subplot(2,2,2)
        #ax2.grid(True)        
        matrix_data = np.genfromtxt(fname2,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[1:, 1:] # from row 1 to the end, from column 1 to the end column
        periods = matrix_data[0,1:] # row 0 from columns 1
             
        minPeriod = np.min(periods)
        maxPeriod = np.max(periods) + 2
        minDemand = np.min(plot_data)
        maxDemand = np.max(plot_data) + 1000
        
        ax2.axis([minPeriod , maxPeriod , minDemand, maxDemand ])
        ax2.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax2.ticklabel_format(style='sci', axis='y')
        ax2.set_title('Real time cost: 105 Usd', fontsize=10)
        ax2.plot(periods, plot_data[0,], color='b',  label=r'DTN enabled'  )
        ax2.plot(periods, plot_data[1,], color='g', marker ='+', label=r'Quality assured' )
        ax2.plot(periods, plot_data[2,], color='r', marker ='.', label=r'Real time'  )
        plt.xticks(range(int(minPeriod),int(maxPeriod),5))
        ax2.legend(loc=0, prop={'size':10})
        

        fname3 = path.expanduser('~/' + relative_path + '/' + file_name + '_130.csv')

        ax3 = fig.add_subplot(2,2,3)
        #ax3.grid(True)        
        matrix_data = np.genfromtxt(fname3,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[1:, 1:] # from row 1 to the end, from column 1 to the end column
        periods = matrix_data[0,1:] # row 0 from columns 1
             
        minPeriod = np.min(periods)
        maxPeriod = np.max(periods) + 2
        minDemand = np.min(plot_data)
        maxDemand = np.max(plot_data) + 1000
        
        ax3.axis([minPeriod , maxPeriod , minDemand, maxDemand ])
        ax3.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax3.ticklabel_format(style='sci', axis='y')
        ax3.set_title('Real time cost: 130 Usd', fontsize=10)
        ax3.plot(periods, plot_data[0,], color='b',  label=r'DTN enabled'  )
        ax3.plot(periods, plot_data[1,], color='g', marker ='+', label=r'Quality assured' )
        ax3.plot(periods, plot_data[2,], color='r', marker ='.', label=r'Real time'  )
        ax3.set_ylabel( "Traffic (MBs)" )
        ax3.set_xlabel( "Months" )
        plt.xticks(range(int(minPeriod),int(maxPeriod),5))
        ax3.legend(loc=0, prop={'size':10})


        fname4 = path.expanduser('~/' + relative_path + '/' + file_name + '_150.csv')

        ax4 = fig.add_subplot(2,2,4)
        #ax4.grid(True)        
        matrix_data = np.genfromtxt(fname4,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[1:, 1:] # from row 1 to the end, from column 1 to the end column
        periods = matrix_data[0,1:] # row 0 from columns 1
             
        minPeriod = np.min(periods)
        maxPeriod = np.max(periods) + 2
        minDemand = np.min(plot_data)
        maxDemand = np.max(plot_data) + 1000
        
        ax4.axis([minPeriod , maxPeriod , minDemand, maxDemand ])
        ax4.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax4.ticklabel_format(style='sci', axis='y')
        ax4.set_title('Real time cost: 150 Usd (WCS)', fontsize=10)
        ax4.plot(periods, plot_data[0,], color='b',  label=r'DTN enabled'  )
        ax4.plot(periods, plot_data[1,], color='g', marker ='+', label=r'Quality assured' )
        ax4.plot(periods, plot_data[2,], color='r', marker ='.', label=r'Real time'  )
        ax4.set_xlabel( "Months" )
        plt.xticks(range(int(minPeriod),int(maxPeriod),5))
        ax4.legend(loc=0, prop={'size':10})
        plt.rc('font', size=10)
        
        plt.show()



    def graphOptimalAssigment01(self, relative_path, file_name):
        
        plt.close('all')
        fig = plt.figure(figsize=(7,12), facecolor='w', edgecolor='k')
        
        plt.subplots_adjust(left=None,right=None,bottom=None,top=None, hspace = 0.3, wspace = 0.25)
        plt.rcParams['axes.linewidth'] = 0.8  

        ax = fig.add_subplot(4,1,1)
        fname = path.expanduser('~/' + relative_path + '/' + file_name + '_10_40.csv')

        matrix_data = np.genfromtxt(fname,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[1:, 1:] # from row 1 to the end, from column 1 to the end column
        periods = matrix_data[0,1:] # row 0 from columns 1
             
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        pl1 = ax.plot( plot_data[1,], color='darkgray', marker='^', markevery=110,  label=r'$D(t)$ DTN enabled' )
        pl2 = ax.plot( plot_data[3,], color='b', marker='^', markevery=110, label=r'$D(t)$ Real time'  )
        pl3 = ax.plot( plot_data[5,], color='black', marker='^', markevery=110, label=r'$D(t)$ Quality assured'  )
        ax.set_ylabel( "Traffic(MBs)" )
        ax.set_xticklabels(['5.00','6.40','8.20','10.00','11.40','13.20','15.00','16.40','18.20'])
        ax.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax.ticklabel_format(style='sci', axis='y')         
        ax.set_title('Period:10 - real time cost:60 Usd')  
        ax2 = ax.twinx()
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        pl4= ax2.plot( plot_data[0,], color='darkgray', marker='*', markevery=100,   label=r'$P(t)$ DTN enabled'  )
        pl5 =ax2.plot( plot_data[2,], color='b', marker='*', markevery=100, label=r'$P(t)$ Real time'  )
        pl6 = ax2.plot( plot_data[4,], color='black', marker='*', markevery=100, label=r'$P(t)$ Quality assured'  )
        ax2.set_ylabel( "USD / MB" )
        ax2.set_xticklabels(['5.00','6.40','8.20','10.00','11.40','13.20','15.00','16.40','18.20'])
        ax2.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax2.ticklabel_format(style='sci', axis='y') 
        


        ax = fig.add_subplot(4,1,2)
        fname2 = path.expanduser('~/' + relative_path + '/' + file_name + '_45_40.csv')

        matrix_data = np.genfromtxt(fname2,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[1:, 1:] # from row 1 to the end, from column 1 to the end column
        periods = matrix_data[0,1:] # row 0 from columns 1
             
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        pl1 = ax.plot( plot_data[1,], color='darkgray', marker='^', markevery=110,  label=r'$D(t)$ DTN enabled' )
        pl2 = ax.plot( plot_data[3,], color='b', marker='^', markevery=110, label=r'$D(t)$ Real time'  )
        pl3 = ax.plot( plot_data[5,], color='black', marker='^', markevery=110, label=r'$D(t)$ Quality assured'  )
        ax.set_ylabel( "Traffic(MBs)" )
        ax.set_xticklabels(['5.00','6.40','8.20','10.00','11.40','13.20','15.00','16.40','18.20'])
        ax.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax.ticklabel_format(style='sci', axis='y')         
        ax.set_title('Period: 45 - real time cost: 60 Usd')  
        ax2 = ax.twinx()
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        pl4= ax2.plot( plot_data[0,], color='darkgray', marker='*', markevery=100,   label=r'$P(t)$ DTN enabled'  )
        pl5 =ax2.plot( plot_data[2,], color='b', marker='*', markevery=100, label=r'$P(t)$ Real time'  )
        pl6 = ax2.plot( plot_data[4,], color='black', marker='*', markevery=100, label=r'$P(t)$ Quality assured'  )
        ax2.set_ylabel( "USD / MB" )
        print periods
        ax2.set_xticklabels(['5.00','6.40','8.20','10.00','11.40','13.20','15.00','16.40','18.20'])
        ax2.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax2.ticklabel_format(style='sci', axis='y') 



        ax3 = fig.add_subplot(4,1,3)
        fname2 = path.expanduser('~/' + relative_path + '/' + file_name + '_10_90.csv')

        matrix_data = np.genfromtxt(fname2,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[1:, 1:] # from row 1 to the end, from column 1 to the end column
        periods = matrix_data[0,1:] # row 0 from columns 1
             
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        pl1 = ax3.plot( plot_data[1,], color='darkgray', marker='^', markevery=110,  label=r'$D(t)$ DTN enabled' )
        pl2 = ax3.plot( plot_data[3,], color='b', marker='^', markevery=110, label=r'$D(t)$ Real time'  )
        pl3 = ax3.plot( plot_data[5,], color='black', marker='^', markevery=110, label=r'$D(t)$ Quality assured'  )
        #ax3.set_ylabel( "Traffic(MBs)" )
        ax3.set_xlabel( "Hour.Minute" )
        ax3.set_xticklabels(['5.00','6.40','8.20','10.00','11.40','13.20','15.00','16.40','18.20'])
        ax3.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax3.ticklabel_format(style='sci', axis='y')         
        ax3.set_title('Period: 10 - real time cost: 135 Usd')
        ax4 = ax3.twinx()
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        pl4= ax4.plot( plot_data[0,], color='darkgray', marker='*', markevery=100,   label=r'$P(t)$ DTN enabled'  )
        pl5 =ax4.plot( plot_data[2,], color='b', marker='*', markevery=100, label=r'$P(t)$ Real time'  )
        pl6 = ax4.plot( plot_data[4,], color='black', marker='*', markevery=100, label=r'$P(t)$ Quality assured'  )
        ax4.set_ylabel( "USD / MB" )
        #ax4.set_xlabel( "Hour.Minute" )
        ax4.set_xticklabels(['5.00','6.40','8.20','10.00','11.40','13.20','15.00','16.40','18.20'])
        ax4.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax4.ticklabel_format(style='sci', axis='y') 

        ax5 = fig.add_subplot(4,1,4)
        fname2 = path.expanduser('~/' + relative_path + '/' + file_name + '_45_90.csv')

        matrix_data = np.genfromtxt(fname2,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[1:, 1:] # from row 1 to the end, from column 1 to the end column
        periods = matrix_data[0,1:] # row 0 from columns 1
             
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        pl1 = ax5.plot( plot_data[1,], color='darkgray', marker='^', markevery=110,  label=r'$D(t)$ DTN enabled' )
        pl2 = ax5.plot( plot_data[3,], color='b', marker='^', markevery=110, label=r'$D(t)$ Real time'  )
        pl3 = ax5.plot( plot_data[5,], color='black', marker='^', markevery=110, label=r'$D(t)$ Quality assured'  )
        ax5.set_ylabel( "Traffic(MBs)" )
        ax5.set_xlabel( "Hour.Minute" )
        ax5.set_xticklabels(['5.00','6.40','8.20','10.00','11.40','13.20','15.00','16.40','18.20'])
        ax5.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax5.ticklabel_format(style='sci', axis='y')         
        ax5.set_title('Period:45 - real time cost: 135 Usd')
        ax6 = ax5.twinx()
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        pl4= ax6.plot( plot_data[0,], color='darkgray', marker='*', markevery=100,   label=r'$P(t)$ DTN enabled'  )
        pl5 =ax6.plot( plot_data[2,], color='b', marker='*', markevery=100, label=r'$P(t)$ Real time'  )
        pl6 = ax6.plot( plot_data[4,], color='black', marker='*', markevery=100, label=r'$P(t)$ Quality assured'  )
        ax6.set_ylabel( "USD / MB" )
        ax6.set_xlabel( "Hour.Minute" )
        ax6.set_xticklabels(['5.00','6.40','8.20','10.00','11.40','13.20','15.00','16.40','18.20'])
        ax6.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax6.ticklabel_format(style='sci', axis='y') 

        
        # added these three lines
        #lns = pl1+pl2+pl3
        #labs = [l.get_label() for l in lns]
        #ax6.legend(lns, labs, bbox_to_anchor=(0., -0.35, 1., .102), loc=5,ncol=3,prop={'size':8}, mode="expand", borderaxespad=0.)
        
        lns = pl1+pl2+pl3+pl4+pl5+pl6
        labs = [l.get_label() for l in lns]
        ax6.legend(lns, labs, bbox_to_anchor=(0., -0.35, 1., .102), loc=5,ncol=3,prop={'size':8}, mode="expand", borderaxespad=0.)
        plt.rc('font', size=8)        
        plt.show()


    def graphOptimalAssigmentTraffic(self, relative_path, file_name):
        
        plt.close('all')
        fig = plt.figure(figsize=(10,7), facecolor='w', edgecolor='k')
        
        plt.subplots_adjust(left=None,right=None,bottom=None,top=None, hspace = 0.3, wspace = 0.25)
        plt.rcParams['axes.linewidth'] = 0.8  

        ax = fig.add_subplot(2,2,1)
        fname = path.expanduser('~/' + relative_path + '/' + file_name + '_10_40.csv')

        matrix_data = np.genfromtxt(fname,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[1:, 1:] # from row 1 to the end, from column 1 to the end column
        periods = matrix_data[0,1:] # row 0 from columns 1
             
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        pl1 = ax.plot( plot_data[1,], color='darkgray', marker='*', markevery=110,  label=r'$D(t)$ DTN enabled' )
        pl2 = ax.plot( plot_data[3,], color='b', marker='^', markevery=110, label=r'$D(t)$ Real time'  )
        pl3 = ax.plot( plot_data[5,], color='black', marker='+', markevery=110, label=r'$D(t)$ Quality assured'  )
        ax.set_ylabel( "Traffic(MBs)" )
        ax.set_xlabel( "Hour.Minute" )
        ax.set_xticklabels(['5.00','6.40','8.20','10.00','11.40','13.20','15.00','16.40','18.20'])
        ax.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax.ticklabel_format(style='sci', axis='y')         
        ax.set_title('Period:10 - real time cost:60 Usd')  
        

        ax2 = fig.add_subplot(2,2,2)
        fname2 = path.expanduser('~/' + relative_path + '/' + file_name + '_45_40.csv')

        matrix_data = np.genfromtxt(fname2,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[1:, 1:] # from row 1 to the end, from column 1 to the end column
        periods = matrix_data[0,1:] # row 0 from columns 1
             
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        pl1 = ax2.plot( plot_data[1,], color='darkgray', marker='*', markevery=110,  label=r'$D(t)$ DTN enabled' )
        pl2 = ax2.plot( plot_data[3,], color='b', marker='^', markevery=110, label=r'$D(t)$ Real time'  )
        pl3 = ax2.plot( plot_data[5,], color='black', marker='+', markevery=110, label=r'$D(t)$ Quality assured'  )
        ax2.set_ylabel( "Traffic(MBs)" )
        ax2.set_xlabel( "Hour.Minute" )
        ax2.set_xticklabels(['5.00','6.40','8.20','10.00','11.40','13.20','15.00','16.40','18.20'])
        ax2.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax2.ticklabel_format(style='sci', axis='y')         
        ax2.set_title('Period: 45 - real time cost: 60 Usd')  
        

        ax3 = fig.add_subplot(2,2,3)
        fname2 = path.expanduser('~/' + relative_path + '/' + file_name + '_10_90.csv')

        matrix_data = np.genfromtxt(fname2,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[1:, 1:] # from row 1 to the end, from column 1 to the end column
        periods = matrix_data[0,1:] # row 0 from columns 1
             
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        pl1 = ax3.plot( plot_data[1,], color='darkgray', marker='*', markevery=110,  label=r'$D(t)$ DTN enabled' )
        pl2 = ax3.plot( plot_data[3,], color='b', marker='^', markevery=110, label=r'$D(t)$ Real time'  )
        pl3 = ax3.plot( plot_data[5,], color='black', marker='+', markevery=110, label=r'$D(t)$ Quality assured'  )
        ax3.set_ylabel( "Traffic(MBs)" )
        ax3.set_xlabel( "Hour.Minute" )
        ax3.set_xticklabels(['5.00','6.40','8.20','10.00','11.40','13.20','15.00','16.40','18.20'])
        ax3.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax3.ticklabel_format(style='sci', axis='y')         
        ax3.set_title('Period: 10 - real time cost: 135 Usd')
        
        ax4 = fig.add_subplot(2,2,4)
        fname2 = path.expanduser('~/' + relative_path + '/' + file_name + '_45_90.csv')

        matrix_data = np.genfromtxt(fname2,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[1:, 1:] # from row 1 to the end, from column 1 to the end column
        periods = matrix_data[0,1:] # row 0 from columns 1
             
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        pl1 = ax4.plot( plot_data[1,], color='darkgray', marker='*', markevery=110,  label=r'$D(t)$ DTN enabled' )
        pl2 = ax4.plot( plot_data[3,], color='b', marker='^', markevery=110, label=r'$D(t)$ Real time'  )
        pl3 = ax4.plot( plot_data[5,], color='black', marker='+', markevery=110, label=r'$D(t)$ Quality assured'  )
        ax4.set_ylabel( "Traffic(MBs)" )
        ax4.set_xlabel( "Hour.Minute" )
        ax4.set_xticklabels(['5.00','6.40','8.20','10.00','11.40','13.20','15.00','16.40','18.20'])
        ax4.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax4.ticklabel_format(style='sci', axis='y')         
        ax4.set_title('Period:45 - real time cost: 135 Usd')

        
        # added these three lines
        #lns = pl1+pl2+pl3
        #labs = [l.get_label() for l in lns]
        #ax6.legend(lns, labs, bbox_to_anchor=(0., -0.35, 1., .102), loc=5,ncol=3,prop={'size':8}, mode="expand", borderaxespad=0.)
        
        lns = pl1+pl2+pl3
        labs = [l.get_label() for l in lns]
        fig.legend(lns, labs,  loc = 'lower center' ,ncol=3,prop={'size':8})
        plt.rc('font', size=8)        
        plt.show()

    def graphOptimalAssigmentPrice(self, relative_path, file_name):
        
        plt.close('all')
        fig = plt.figure(figsize=(12,7), facecolor='w', edgecolor='k')
        
        plt.subplots_adjust(left=None,right=None,bottom=None,top=None, hspace = 0.3, wspace = 0.25)
        plt.rcParams['axes.linewidth'] = 0.8  

        ax = fig.add_subplot(2,2,1)
        fname = path.expanduser('~/' + relative_path + '/' + file_name + '_10_40.csv')

        matrix_data = np.genfromtxt(fname,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[1:, 1:] # from row 1 to the end, from column 1 to the end column
        periods = matrix_data[0,1:] # row 0 from columns 1
             
                
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        pl4= ax.plot( plot_data[0,], color='darkgray', marker='*', markevery=100,   label=r'$P(t)$ DTN enabled'  )
        pl5 =ax.plot( plot_data[2,], color='b', marker='^', markevery=100, label=r'$P(t)$ Real time'  )
        pl6 = ax.plot( plot_data[4,], color='black', marker='+', markevery=100, label=r'$P(t)$ Quality assured'  )
        ax.set_ylabel( "USD / MB" )
        ax.set_xticklabels(['5.00','6.40','8.20','10.00','11.40','13.20','15.00','16.40','18.20'])
        ax.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax.ticklabel_format(style='sci', axis='y') 
        ax.set_title('Period:10 - real time cost:60 Usd')  
        ax.set_xlabel( "Hour.Minute" )
        


        ax2 = fig.add_subplot(2,2,2)
        fname2 = path.expanduser('~/' + relative_path + '/' + file_name + '_45_40.csv')

        matrix_data = np.genfromtxt(fname2,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[1:, 1:] # from row 1 to the end, from column 1 to the end column
        periods = matrix_data[0,1:] # row 0 from columns 1
             
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        pl4= ax2.plot( plot_data[0,], color='darkgray', marker='*', markevery=100,   label=r'$P(t)$ DTN enabled'  )
        pl5 =ax2.plot( plot_data[2,], color='b', marker='^', markevery=110, label=r'$P(t)$ Real time'  )
        pl6 = ax2.plot( plot_data[4,], color='black', marker='+', markevery=100, label=r'$P(t)$ Quality assured'  )
        ax2.set_ylabel( "USD / MB" )
        ax2.set_xticklabels(['5.00','6.40','8.20','10.00','11.40','13.20','15.00','16.40','18.20'])
        ax2.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax2.ticklabel_format(style='sci', axis='y') 
        ax2.set_title('Period: 45 - real time cost: 60 Usd')  
        ax2.set_xlabel( "Hour.Minute" )


        ax3 = fig.add_subplot(2,2,3)
        fname2 = path.expanduser('~/' + relative_path + '/' + file_name + '_10_90.csv')

        matrix_data = np.genfromtxt(fname2,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[1:, 1:] # from row 1 to the end, from column 1 to the end column
        periods = matrix_data[0,1:] # row 0 from columns 1
             
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        pl4= ax3.plot( plot_data[0,], color='darkgray', marker='*', markevery=100,   label=r'$P(t)$ DTN enabled'  )
        pl5 =ax3.plot( plot_data[2,], color='b', marker='^', markevery=100, label=r'$P(t)$ Real time'  )
        pl6 = ax3.plot( plot_data[4,], color='black', marker='+', markevery=100, label=r'$P(t)$ Quality assured'  )
        ax3.set_ylabel( "USD / MB" )
        #ax4.set_xlabel( "Hour.Minute" )
        ax3.set_xticklabels(['5.00','6.40','8.20','10.00','11.40','13.20','15.00','16.40','18.20'])
        ax3.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax3.ticklabel_format(style='sci', axis='y') 
        ax3.set_title('Period: 10 - real time cost: 135 Usd')
        ax3.set_xlabel( "Hour.Minute" )


        ax4 = fig.add_subplot(2,2,4)
        fname2 = path.expanduser('~/' + relative_path + '/' + file_name + '_45_90.csv')

        matrix_data = np.genfromtxt(fname2,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[1:, 1:] # from row 1 to the end, from column 1 to the end column
        periods = matrix_data[0,1:] # row 0 from columns 1
        
             
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
       
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        pl4= ax4.plot( plot_data[0,], color='darkgray', marker='*', markevery=100,   label=r'$P(t)$ DTN enabled'  )
        pl5 =ax4.plot( plot_data[2,], color='b', marker='^', markevery=100, label=r'$P(t)$ Real time'  )
        pl6 = ax4.plot( plot_data[4,], color='black', marker='+', markevery=100, label=r'$P(t)$ Quality assured'  )
        ax4.set_ylabel( "USD / MB" )
        ax4.set_xlabel( "Hour.Minute" )
        ax4.set_xticklabels(['5.00','6.40','8.20','10.00','11.40','13.20','15.00','16.40','18.20'])
        ax4.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax4.ticklabel_format(style='sci', axis='y') 
        ax4.set_title('Period:45 - real time cost: 135 Usd')

        
        # added these three lines
        #lns = pl1+pl2+pl3
        #labs = [l.get_label() for l in lns]
        #ax6.legend(lns, labs, bbox_to_anchor=(0., -0.35, 1., .102), loc=5,ncol=3,prop={'size':8}, mode="expand", borderaxespad=0.)
        
        lns = pl4+pl5+pl6
        labs = [l.get_label() for l in lns]
        fig.legend(lns, labs,  loc = 'lower center' ,ncol=3,prop={'size':8})
        plt.rc('font', size=8)        
        plt.show()


    def graphEconomiesScale(self, relative_path, file_name):
        

        fname = path.expanduser('~/' + relative_path + '/' + file_name)

        matrix_data = np.genfromtxt(fname,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[0:, 3:] # from row 1 to the end, from column 1 to the end column
 
        plt.close('all')
        fig = plt.figure(figsize=(7,12), facecolor='w', edgecolor='k')
        plt.subplots_adjust(left=0.05,right=0.95,bottom=0.3,top=1.0)
        plt.rcParams['axes.linewidth'] = 0.8  
            
        ax = fig.add_subplot(2,1,1)
        ax.grid(True)
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        ax.plot( plot_data[0,], color='k', label=r'$x=y$'  )
        ax.plot( plot_data[1,], color='r', marker='^', label=r'$K_1$ Cons' )
        ax.plot( plot_data[2,], color='r', marker='o', label=r'$K_1$ Cons'  )
        ax.plot( plot_data[3,], color='g', marker='^', label=r'$K_1$ Var- $C_1$ Cons'  )
        ax.plot( plot_data[4,], color='g', marker='o', label=r'$K_1$ Var- $C_1$ Cons'  )
        ax.plot( plot_data[5,], color='b', marker='^', label=r'$K_1$ Var- $C_1$ Var'  )
        ax.plot( plot_data[6,], color='b', marker='o', label=r'$K_1$ Var- $C_1$ Var'  )
        
        ax.set_ylabel( "Growth in profits" )
        ax.set_xlabel( "Growth in demand" )
        ax.set_xticklabels(plot_data[0,])
        #plt.xticks(range(int(minPeriod),int(maxPeriod),5))
        ax.legend(bbox_to_anchor=(0., -0.3, 1., .102), loc=5,ncol=3,prop={'size':12}, mode="expand", borderaxespad=0.)
        #ax.legend(loc=0, ncol=3, prop={'size':12})
  
        ax.set_title('(a) Analysis on economies of scale (profits)')

        ax2 = fig.add_subplot(2,1,2)
        ax2.grid(True)
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        ax2.plot( plot_data[0,], color='k', label=r'$x=y$'  )
        ax2.plot( plot_data[7,], color='r', marker='^',  label=r'$K_1$ Cons' )
        ax2.plot( plot_data[8,], color='r', marker='o',  label=r'$K_1$ Cons'  )
        ax2.plot( plot_data[9,], color='g', marker='^',  label=r'$K_1$ Var- $C_1$ Cons'  )
        ax2.plot( plot_data[10,], color='g', marker='o', label=r'$K_1$ Var- $C_1$ Cons'  )
        ax2.plot( plot_data[11,], color='b', marker='^', label=r'$K_1$ Var- $C_1$ Var'  )
        ax2.plot( plot_data[12,], color='b', marker='o', label=r'$K_1$ Var- $C_1$ Var'  )
        ax2.set_ylabel( "Growth in Traffic" )
        ax2.set_xlabel( "Growth in demand" )
        ax2.set_xticklabels(plot_data[0,])
        #plt.xticks(range(int(minPeriod),int(maxPeriod),5))
        #left, bottom, width, height
        ax2.legend(bbox_to_anchor=(0., -0.3, 1., .102), loc=5,ncol=3,prop={'size':12}, mode="expand", borderaxespad=0.)
        #ax.legend(loc=0, ncol=3, prop={'size':12})
        ax2.set_title('(b) Analysis on economies of scale (traffic)')
        plt.show()


    def graphEconomiesScaleProfits(self, relative_path, file_name):
        

        fname = path.expanduser('~/' + relative_path + '/' + file_name)

        matrix_data = np.genfromtxt(fname,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[0:, 3:] # from row 1 to the end, from column 1 to the end column
 
        plt.close('all')
        fig = plt.figure(figsize=(7,7), facecolor='w', edgecolor='k')
        plt.rcParams['axes.linewidth'] = 0.8  
            
        ax = fig.add_subplot(1,1,1)
        ax.grid(True)
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        ax.plot( plot_data[0,], color='k', label=r'$x=y$'  )
        ax.plot( plot_data[1,], color='r', marker='^', label=r'$K_1$ Cons' )
        ax.plot( plot_data[2,], color='r', marker='o', label=r'$K_1$ Cons'  )
        ax.plot( plot_data[3,], color='g', marker='^', label=r'$K_1$ Var- $C_1$ Cons'  )
        ax.plot( plot_data[4,], color='g', marker='o', label=r'$K_1$ Var- $C_1$ Cons'  )
        ax.plot( plot_data[5,], color='b', marker='^', label=r'$K_1$ Var- $C_1$ Var'  )
        ax.plot( plot_data[6,], color='b', marker='o', label=r'$K_1$ Var- $C_1$ Var'  )
        
        ax.set_ylabel( "Growth in profits" )
        ax.set_xlabel( "Growth in demand" )
        ax.set_xticklabels(plot_data[0,])
        #plt.xticks(range(int(minPeriod),int(maxPeriod),5))
        ax.legend(bbox_to_anchor=(0., -0.3, 1., .102), loc=5,ncol=3,prop={'size':12}, mode="expand", borderaxespad=0.)
        #ax.legend(loc=0, ncol=3, prop={'size':12})
        plt.show()

    def graphEconomiesScaleTraffic(self, relative_path, file_name):
        

        fname = path.expanduser('~/' + relative_path + '/' + file_name)

        matrix_data = np.genfromtxt(fname,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[0:, 3:] # from row 1 to the end, from column 1 to the end column
 
        plt.close('all')
        fig = plt.figure(figsize=(7,7), facecolor='w', edgecolor='k')
        plt.rcParams['axes.linewidth'] = 0.8  
            
        ax2 = fig.add_subplot(1,1,1)
        ax2.grid(True)
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        ax2.plot( plot_data[0,], color='k', label=r'$x=y$'  )
        ax2.plot( plot_data[7,], color='r', marker='^',  label=r'$K_1$ Cons' )
        ax2.plot( plot_data[8,], color='r', marker='o',  label=r'$K_1$ Cons'  )
        ax2.plot( plot_data[9,], color='g', marker='^',  label=r'$K_1$ Var- $C_1$ Cons'  )
        ax2.plot( plot_data[10,], color='g', marker='o', label=r'$K_1$ Var- $C_1$ Cons'  )
        ax2.plot( plot_data[11,], color='b', marker='^', label=r'$K_1$ Var- $C_1$ Var'  )
        ax2.plot( plot_data[12,], color='b', marker='o', label=r'$K_1$ Var- $C_1$ Var'  )
        ax2.set_ylabel( "Growth in Traffic" )
        ax2.set_xlabel( "Growth in demand" )
        ax2.set_xticklabels(plot_data[0,])
        #plt.xticks(range(int(minPeriod),int(maxPeriod),5))
        #left, bottom, width, height
        ax2.legend(bbox_to_anchor=(0., -0.3, 1., .102), loc=5,ncol=3,prop={'size':12}, mode="expand", borderaxespad=0.)
        #ax.legend(loc=0, ncol=3, prop={'size':12})
        plt.show()


    def graphBehaviourMixedOperators(self, relative_path, file_name_profit, file_name_traffic):
        

        fname = path.expanduser('~/' + relative_path + '/' + file_name_profit)

        matrix_data = np.genfromtxt(fname,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[0:, 1:] # from row 1 to the end, from column 1 to the end column
 
        plt.close('all')
        fig = plt.figure(figsize=(14,5), facecolor='w', edgecolor='k')
        plt.subplots_adjust(left=0.05,right=0.95,bottom=0.1,top=0.9)
        plt.rcParams['axes.linewidth'] = 0.8  
            
        ax = fig.add_subplot(1,2,1)
        ax.grid(True)
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        ax.plot( plot_data[1,], color='b', marker='.', label=r'$q=0.1$'  )
        ax.plot( plot_data[2,], color='g', marker='^', label=r'$q=0.15$' )
        ax.plot( plot_data[3,], color='b', marker='D', label=r'$q=0.175$'  )
        ax.plot( plot_data[4,], color='g', marker='o', label=r'$q=0.2$'  )
        
        labels = ['2%', '8%', '14%']
        ax.set_ylabel( "US Dollars" )
        ax.set_xlabel( "Annual investment rate" )
        ax.set_xticks(np.arange(0,3,1))
        ax.set_xticklabels(labels)
        ax.legend(loc=0,prop={'size':12})
        ax.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax.ticklabel_format(style='sci', axis='y') 
        #ax.legend(loc=0, ncol=3, prop={'size':12})
  
        ax.set_title('(a) Gross profit by annual investment rate')

        fname = path.expanduser('~/' + relative_path + '/' + file_name_traffic)
        matrix_data = np.genfromtxt(fname,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[0:,1:] # from row 1 to the end, from column 1 to the end column
        
        
        ax2 = fig.add_subplot(1,2,2)
        ax2.grid(True)
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        ax2.plot( plot_data[1,], color='k', label=r'$x=y$'  )
        ax2.set_ylabel( "Traffic(MBs)" )
        ax2.set_xlabel( "Innovator's influence on followers($q$)" )
        ax2.set_xticklabels(plot_data[0,])
        ax2.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax2.ticklabel_format(style='sci', axis='y') 
        #plt.xticks(range(int(minPeriod),int(maxPeriod),5))
        #left, bottom, width, height
        #ax2.legend(bbox_to_anchor=(0., -0.3, 1., .102), loc=5,ncol=3,prop={'size':12}, mode="expand", borderaxespad=0.)
        #ax.legend(loc=0, ncol=3, prop={'size':12})
        ax2.set_title('(b) Consolidate traffic')
        plt.show()

    def autolabel(self, ax1, data, rects, legend):
        i = 0
        for rect in rects:
            h = data[i]
            ax1.text(rect.get_x()+rect.get_width()/2., 1.01*h, '%d'%int(legend),
                ha='center', va='bottom', fontsize =8)
            i = i + 1 


    def graphBehaviourMixedOperators2(self, relative_path, file_name_profit, file_name_traffic):
        

        fname = path.expanduser('~/' + relative_path + '/' + file_name_profit)
        matrix_data = np.genfromtxt(fname,dtype=float, skip_header=0, delimiter=';')
        investment_rates =[0.02, 0.08, 0.14]
        ind = np.arange(5)
        figure = plt.figure()
        figure.set_size_inches(5, 6)
        width = 0.1
        width2 = 0.2
        colors = {0.02: 'c', 0.08: 'm', 0.14: 'y', 4: 'c', 5: 'm', 6: 'y', 7: 'a', 8: 'd', 9: 's', 10: 'h'}
        
        # Real Time costs: 40 USD
        
        ax1 = figure.add_subplot(2,2,1)
        #ax1.set_xlabel("q", fontsize=8)
        ax1.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax1.ticklabel_format(style='sci', axis='y') 
        ax1.set_xlim( 0, 4.9 )
        ax1.set_ylim( 30000, 140000 )        
        ax1.set_xticks(ind+ 0.5)
        ax1.set_title('Real time cost: 60 Usd', fontsize=10) 
        ax1.set_xticklabels( ('0.08', '0.09', '0.1','0.11','0.13'), fontsize=9 )
        ax1.set_ylabel( "Profits(Usd)", fontsize=10 )
        groups = []
        labels = []
        backhaul15_002 = np.array( [ 96755.67, 103549.52 , 109312.54, 114205.20, 121965.55  ])
        backhaul15_008 = np.array( [ 81254.75, 87078.84, 92066.33, 96340.59, 103206.10 ] )
        backhaul15_014 = np.array( [ 69213.08, 74266.88, 78632.73, 82406.69, 88538.89 ])

        backhaul25_002 = np.array( [  96191.30, 102984.67, 108746.60, 113638.87, 121397.22 ] )
        backhaul25_008 = np.array([  80762.58, 86586.22, 91572.65, 95846.54, 102710.10 ])
        backhaul25_014 = np.array([ 68778.04, 73831.40, 78196.24, 81969.84, 88100.14 ])

        backhaul35_002 = np.array([ 95626.77, 102418.60, 108179.72, 113070.95, 120828.55 ])
        backhaul35_008 = np.array([ 80270.33, 86092.50, 91078.16, 95351.05, 102213.90 ])
        backhaul35_014 = np.array([ 68342.99, 73394.94, 77759.03, 81531.68, 87661.29 ])
        
        sc1 = plt.bar(ind+width , tuple(backhaul15_014), width2, color='#F4561D', hatch="/")
        groups.append(sc1[0])
        labels.append('IR:14% ')
        lastdata=backhaul15_014
        sc2 = plt.bar(ind+width, backhaul15_008 - backhaul15_014, width2, color='#F1911E', hatch="//", bottom = backhaul15_014)
        groups.append(sc2[0])
        labels.append('IR:8% ')
        lastdata=backhaul15_008
        sc3 = plt.bar(ind+width, backhaul15_002 - backhaul15_008, width2, color='#F1BD1A', bottom = backhaul15_008)
        groups.append(sc3[0])
        labels.append('IR:2% ')
        self.autolabel( ax1, backhaul15_002, sc3, 15)
        
        width = width + 0.25 
        sc4 = plt.bar(ind+width, backhaul25_014, width2, color='#F4561D', hatch="/" )
        sc5 = plt.bar(ind+width, backhaul25_008 - backhaul25_014, width2, color='#F1911E', hatch="//", bottom = backhaul25_014)
        sc6 = plt.bar(ind+width , backhaul25_002 - backhaul25_008, width2, color='#F1BD1A', bottom = backhaul25_008)
        self.autolabel( ax1, backhaul25_002, sc6, 25)
        
        width = width + 0.25
        sc7 = plt.bar(ind+width, backhaul35_014, width2, color='#F4561D', hatch="/" )
        sc8 = plt.bar(ind+width, backhaul35_008 - backhaul35_014, width2, color='#F1911E', hatch="//", bottom = backhaul35_014)
        sc9 = plt.bar(ind+width, backhaul35_002 - backhaul35_008, width2, color='#F1BD1A', bottom = backhaul35_008)
        self.autolabel( ax1, backhaul35_002, sc9, 35)

        ax1.legend(tuple(groups), tuple(labels), loc='upper left', prop={'size':8})

        # Real Time costs: 90 USD
        # creates the second figure 
        width = 0.1
        ax2 = figure.add_subplot(2,2,2)
        #ax2.set_xlabel("q", fontsize=8)
        ax2.yaxis.major.formatter.set_powerlimits((0,0))
        ax2.ticklabel_format(style='sci', axis='y') 
        ax2.set_xlim( 0, 4.9 )
        ax2.set_ylim( 30000, 140000 )        
        ax2.set_xticks(ind+ 0.5)
        ax2.set_title('Real time cost: 105 Usd', fontsize=10) 
        ax2.set_xticklabels( ('0.08', '0.09', '0.1','0.11','0.13') ,fontsize=9)
        groups = []
        labels = []
        backhaul15_002 = np.array( [  82399.45 ,     87995.29  ,    92725.04  ,    96730.59  ,    103071.86   ])
        backhaul15_008 = np.array( [  69167.35 ,     73986.95  ,    78098.50  ,    81612.29  ,    87243.07  ] )
        backhaul15_014 = np.array( [ 58882.08  ,    63083.37   ,   66698.06   ,   69813.01   ,   74860.30 ])

        backhaul25_002 = np.array( [  81825.48 ,     87421.33  ,    92151.03  ,    96156.55  ,    102497.77  ] )
        backhaul25_008 = np.array([  68665.73  ,    73485.34   ,   77596.85   ,   81110.61   ,   86741.36  ])
        backhaul25_014 = np.array([  58437.72  ,    62639.02   ,   66253.69   ,   69368.62   ,   74415.89  ])

        backhaul35_002 = np.array([  81250.40  ,    86846.24  ,    91575.86   ,   95581.34   ,   101922.49  ])
        backhaul35_008 = np.array([  68163.12  ,    72982.74  ,    77094.19   ,   80607.92   ,   86238.62  ])
        backhaul35_014 = np.array([  57992.48  ,    62193.80  ,    65808.42   ,   68923.33   ,   73970.56  ])
        
        sc21 = plt.bar(ind+width , tuple(backhaul15_014), width2, color='#F4561D', hatch="/" )
        groups.append(sc1[0])
        labels.append('IR:14% ')
        lastdata=backhaul15_014
        sc22 = plt.bar(ind+width, backhaul15_008 - backhaul15_014, width2, color='#F1911E', hatch="//" , bottom = backhaul15_014)
        groups.append(sc2[0])
        labels.append('IR:8% ')
        lastdata=backhaul15_008
        sc23 = plt.bar(ind+width, backhaul15_002 - backhaul15_008, width2, color='#F1BD1A' , bottom = backhaul15_008)
        groups.append(sc3[0])
        labels.append('IR:2% ')
        self.autolabel( ax2, backhaul15_002, sc23, 15)
        
        width = width + 0.25 
        sc24 = plt.bar(ind+width, backhaul25_014, width2, color='#F4561D', hatch="/" )
        sc25 = plt.bar(ind+width, backhaul25_008 - backhaul25_014, width2, color='#F1911E', hatch="//" , bottom = backhaul25_014)
        sc26 = plt.bar(ind+width , backhaul25_002 - backhaul25_008, width2, color='#F1BD1A' , bottom = backhaul25_008)
        self.autolabel( ax2, backhaul25_002, sc26, 25)
        
        width = width + 0.25
        sc27 = plt.bar(ind+width, backhaul35_014, width2, color='#F4561D', hatch="/" )
        sc28 = plt.bar(ind+width, backhaul35_008 - backhaul35_014, width2, color='#F1911E', hatch="//" , bottom = backhaul35_014)
        sc29 = plt.bar(ind+width, backhaul35_002 - backhaul35_008, width2, color='#F1BD1A' , bottom = backhaul35_008)
        self.autolabel( ax2, backhaul35_002, sc29, 35)

        ax2.legend(tuple(groups), tuple(labels), loc='upper left', prop={'size':8})


        # Real Time costs: 120 USD
        # creates the second figure 
        width = 0.1
        ax3 = figure.add_subplot(2,2,3)
        ax3.set_xlabel("Parameter q", fontsize=10)
        ax3.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax3.ticklabel_format(style='sci', axis='y')
        ax3.set_title('Real time cost: 130 Usd', fontsize=10) 
        ax3.set_xlim( 0, 4.9 )
        ax3.set_ylim( 30000, 140000 )
        ax3.set_xticks(ind+ 0.5)
        ax3.set_xticklabels( ('0.08', '0.09', '0.1','0.11','0.13') ,fontsize=9)
        ax3.set_ylabel( "Profits(Usd)", fontsize=10 )
        groups = []
        labels = []
        backhaul15_002 = np.array( [  75949.29 ,     81057.31  ,    85374.93   ,   89032.05  ,    94816.48  ])
        backhaul15_008 = np.array( [  63705.78 ,     68118.72  ,    71881.63   ,   75096.91  ,    80244.11  ] )
        backhaul15_014 = np.array( [  54187.46 ,     58045.55  ,    61361.98   ,   64218.50  ,    68841.74  ])

        backhaul25_002 = np.array( [  75375.32 ,     80483.34  ,    84800.92   ,   88458.01  ,    94242.39  ] )
        backhaul25_008 = np.array([  63204.16  ,    67617.10   ,   71379.98    ,  74595.23   ,   79742.40  ])
        backhaul25_014 = np.array([  53743.10  ,    57601.21   ,   60917.61    ,  63774.11   ,   68397.33  ])

        backhaul35_002 = np.array([  74800.24  ,    79908.25   ,   84225.75  ,    87882.80   ,   93667.12  ])
        backhaul35_008 = np.array([  62701.55  ,    67114.50   ,   70877.32  ,    74092.54   ,   79239.66  ])
        backhaul35_014 = np.array([  53297.86  ,    57155.99   ,   60472.33  ,    63328.82   ,   67952.00  ])
        
        sc31 = plt.bar(ind+width , tuple(backhaul15_014), width2, color='#F4561D', hatch="/" )
        groups.append(sc1[0])
        labels.append('IR:14% ')
        lastdata=backhaul15_014
        sc32 = plt.bar(ind+width, backhaul15_008 - backhaul15_014, width2, color='#F1911E', hatch="//" , bottom = backhaul15_014)
        groups.append(sc2[0])
        labels.append('IR:8% ')
        lastdata=backhaul15_008
        sc33 = plt.bar(ind+width, backhaul15_002 - backhaul15_008, width2, color='#F1BD1A', bottom = backhaul15_008)
        groups.append(sc3[0])
        labels.append('IR:2% ')
        self.autolabel( ax3, backhaul15_002, sc33, 15)
        
        width = width + 0.25 
        sc34 = plt.bar(ind+width, backhaul25_014, width2, color='#F4561D', hatch="/" )
        sc35 = plt.bar(ind+width, backhaul25_008 - backhaul25_014, width2, color='#F1911E', hatch="//" , bottom = backhaul25_014)
        sc36 = plt.bar(ind+width , backhaul25_002 - backhaul25_008, width2, color='#F1BD1A', bottom = backhaul25_008)
        self.autolabel( ax3, backhaul25_002, sc36, 25)
        
        width = width + 0.25
        sc37 = plt.bar(ind+width, backhaul35_014, width2, color='#F4561D', hatch="/" )
        sc38 = plt.bar(ind+width, backhaul35_008 - backhaul35_014, width2, color='#F1911E', hatch="//" , bottom = backhaul35_014)
        sc39 = plt.bar(ind+width, backhaul35_002 - backhaul35_008, width2, color='#F1BD1A', bottom = backhaul35_008)
        self.autolabel( ax3, backhaul35_002, sc39, 35)

        ax3.legend(tuple(groups), tuple(labels), loc='upper left', prop={'size':8})


        # Real Time costs: 150 USD
        # creates the second figure 
        width = 0.1
        ax4 = figure.add_subplot(2,2,4)
        ax4.set_xlabel("Parameter q", fontsize=10)
        ax4.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax4.ticklabel_format(style='sci', axis='y', fontsize=9) 
        ax4.set_xlim( 0, 4.9 )
        ax4.set_ylim( 30000, 140000 )
        ax4.set_xticks(ind+ 0.5)
        ax4.set_title('Real time cost: 150 Usd (WCS)', fontsize=10) 
        ax4.set_xticklabels( ('0.08', '0.09', '0.1','0.11','0.13'),fontsize=9 )
        groups = []
        labels = []
        backhaul15_002 = np.array( [  71444.27  ,    76282.68  ,    80355.08  ,   83793.63   ,   88646.47])
        backhaul15_008 = np.array( [  59861.46  ,    64050.56  ,    67608.21  ,    70638.85  ,    75479.68  ] )
        backhaul15_014 = np.array( [  50857.21  ,    54527.27  ,    57669.87  ,    60368.63  ,    64726.53 ])

        backhaul25_002 = np.array( [  70870.31  ,    75708.72  ,    79781.07  ,    83219.58  ,   88646.47  ] )
        backhaul25_008 = np.array([  59359.84   ,   63548.94   ,   67106.57   ,   70137.18   ,   74977.98  ])
        backhaul25_014 = np.array([  50412.85   ,   54082.93   ,   57225.50   ,   59924.25   ,   64282.12  ])

        backhaul35_002 = np.array([  70295.22   ,   75133.63   ,   79205.90   ,   82644.37   ,   88071.20  ])
        backhaul35_008 = np.array([   58857.23  ,    63046.34  ,   66603.90   ,   69634.49   ,   74475.23 ])
        backhaul35_014 = np.array([  49967.61   ,   53637.71   ,   56780.23  ,    59478.95   ,   63836.79  ])
        
        sc41 = plt.bar(ind+width , tuple(backhaul15_014), width2, color='#F4561D', hatch="/" )
        groups.append(sc41[0])
        labels.append('IR:14% ')
        lastdata=backhaul15_014
        sc42 = plt.bar(ind+width, backhaul15_008 - backhaul15_014, width2, color='#F1911E', hatch="//" , bottom = backhaul15_014)
        groups.append(sc42[0])
        labels.append('IR:8% ')
        lastdata=backhaul15_008
        sc43 = plt.bar(ind+width, backhaul15_002 - backhaul15_008, width2, color='#F1BD1A', bottom = backhaul15_008)
        groups.append(sc43[0])
        labels.append('IR:2% ')
        self.autolabel( ax4, backhaul15_002, sc43, 15)
        
        width = width + 0.25 
        sc44 = plt.bar(ind+width, backhaul25_014, width2, color='#F4561D', hatch="/" )
        sc45 = plt.bar(ind+width, backhaul25_008 - backhaul25_014, width2, color='#F1911E', hatch="//" , bottom = backhaul25_014)
        sc46 = plt.bar(ind+width , backhaul25_002 - backhaul25_008, width2, color='#F1BD1A', bottom = backhaul25_008)
        self.autolabel( ax4, backhaul25_002, sc46, 25)
        
        width = width + 0.25
        sc47 = plt.bar(ind+width, backhaul35_014, width2, color='#F4561D', hatch="/" )
        sc48 = plt.bar(ind+width, backhaul35_008 - backhaul35_014, width2, color='#F1911E', hatch="//" , bottom = backhaul35_014)
        sc49 = plt.bar(ind+width, backhaul35_002 - backhaul35_008, width2, color='#F1BD1A', bottom = backhaul35_008)
        self.autolabel( ax4, backhaul35_002, sc49, 35)
        plt.rc('font', size=10)
        ax4.legend(tuple(groups), tuple(labels), loc='upper left', prop={'size':8})

        plt.show()


    def graphBehaviourMixedOperators3(self, relative_path, file_name_profit, file_name_traffic):
        

        fname = path.expanduser('~/' + relative_path + '/' + file_name_profit)
        matrix_data = np.genfromtxt(fname,dtype=float, skip_header=0, delimiter=';')
        investment_rates =[0.02, 0.08, 0.14]
        ind = np.arange(5)
        figure = plt.figure()
        figure.set_size_inches(6, 8)
        width = 0.1
        width2 = 0.2
        colors = {0.02: 'b', 0.08: 'g', 0.14: 'r', 4: 'c', 5: 'm', 6: 'y', 7: 'a', 8: 'd', 9: 's', 10: 'h'}
        
        # Real Time costs: 40 USD
        
        ax1 = figure.add_subplot(2,2,1)
        #ax1.set_xlabel("q", fontsize=8)
        ax1.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax1.ticklabel_format(style='sci', axis='y') 
        ax1.set_xlim( 0, 4.9 )
        ax1.set_ylim( 2000000, 5500000 )        
        ax1.set_xticks(ind+ 0.5)
        ax1.set_title('Real time cost: 60 Usd', fontsize=10) 
        ax1.set_xticklabels( ('0.08', '0.09', '0.1','0.11','0.13'), fontsize=9 )
        ax1.set_ylabel( "Traffic(MB)", fontsize=10 )
        groups = []
        labels = []
        backhaul15 = np.array( [ 4047575   ,   4298268   ,   4500901   ,   4680476  ,   4976891 ])
        backhaul25 = np.array( [ 4041863   ,   4292533   ,   4495042   ,   4674513  ,   4970797  ] )
        backhaul35 = np.array([  4036157   ,   4286804   ,   4489161   ,   4668555  ,   4964708  ])
        
        sc1 = plt.bar(ind+width , tuple(backhaul15), width2, color='#F4561D', hatch="/")
        groups.append(sc1[0])
        labels.append('15 Usd ')
        
        width = width + 0.25 
        sc2 = plt.bar(ind+width, backhaul25, width2, color='#F1911E', hatch="//" )
        groups.append(sc2[0])
        labels.append('25 Usd ')
        
        width = width + 0.25
        sc3 = plt.bar(ind+width, backhaul35, width2, color='#F1BD1A' )
        groups.append(sc3[0])
        labels.append('35 Usd ')

        ax1.legend(tuple(groups), tuple(labels), loc='upper left', prop={'size':8})

        # Real Time costs: 90 USD
        # creates the second figure 
        width = 0.1
        ax2 = figure.add_subplot(2,2,2)
        #ax2.set_xlabel("q", fontsize=8)
        ax2.yaxis.major.formatter.set_powerlimits((0,0))
        ax2.ticklabel_format(style='sci', axis='y') 
        ax2.set_xlim( 0, 4.9 )
        ax2.set_ylim( 2000000, 5500000 )        
        ax2.set_xticks(ind+ 0.5)
        ax2.set_title('Real time cost: 105 Usd', fontsize=10) 
        ax2.set_xticklabels( ('0.08', '0.09', '0.1','0.11','0.13') ,fontsize=9)
        groups = []
        labels = []
        backhaul15 = np.array( [ 3422091   ,   3592325  ,    3731412   ,   3867797  ,    4092328  ])

        backhaul25 = np.array( [ 3416289   ,   3586510  ,    3725479   ,   3861766  ,    4086174  ] )

        backhaul35 = np.array([  3410488   ,  3580694   ,   3719518  ,    3855735  ,    4080020  ])
        
        sc21 = plt.bar(ind+width , tuple(backhaul15), width2, color='#F4561D', hatch="/" )
        groups.append(sc21[0])
        labels.append('15 Usd ')
        
        width = width + 0.25 
        sc22 = plt.bar(ind+width, backhaul25, width2, color='#F1911E', hatch="//" )
        groups.append(sc22[0])
        labels.append('25 Usd ')
        
        width = width + 0.25
        sc23 = plt.bar(ind+width, backhaul35, width2, color='#F1BD1A' )
        groups.append(sc23[0])
        labels.append('35 Usd ')

        ax2.legend(tuple(groups), tuple(labels), loc='upper left', prop={'size':8})


        # Real Time costs: 120 USD
        # creates the second figure 
        width = 0.1
        ax3 = figure.add_subplot(2,2,3)
        ax3.set_xlabel("Parameter q", fontsize=10)
        ax3.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax3.ticklabel_format(style='sci', axis='y')
        ax3.set_title('Real time cost: 130 Usd', fontsize=10) 
        ax3.set_xlim( 0, 4.9 )
        ax3.set_ylim( 2000000, 5500000 )
        ax3.set_xticks(ind+ 0.5)
        ax3.set_xticklabels( ('0.08', '0.09', '0.1','0.11','0.13') ,fontsize=9)
        ax3.set_ylabel( "Traffic(MB)", fontsize=10 )
        groups = []
        labels = []
        backhaul15 = np.array( [  3111647  ,    3257364   ,   3391266  ,    3501241   ,   3679266  ])
        backhaul25 = np.array( [  3105846  ,    3251548   ,   3385332  ,    3495210   ,   3673112  ] )
        backhaul35 = np.array([  3100044   ,   3245733    ,  3379371   ,   3489179    ,  3666958  ])
        
        sc31 = plt.bar(ind+width , tuple(backhaul15), width2, color='#F4561D', hatch="/" )
        groups.append(sc31[0])
        labels.append('15 Usd ')
        
        width = width + 0.25 
        sc32 = plt.bar(ind+width, backhaul25, width2, color='#F1911E', hatch="//" )
        groups.append(sc32[0])
        labels.append('25 Usd ')
        
        width = width + 0.25
        sc33 = plt.bar(ind+width, backhaul35, width2, color='#F1BD1A' )
        groups.append(sc33[0])
        labels.append('35 Usd ')

        ax3.legend(tuple(groups), tuple(labels), loc='upper left', prop={'size':8})


        # Real Time costs: 150 USD
        # creates the second figure 
        width = 0.1
        ax4 = figure.add_subplot(2,2,4)
        ax4.set_xlabel("Parameter q", fontsize=10)
        ax4.yaxis.major.formatter.set_powerlimits((0,0)) 
        ax4.ticklabel_format(style='sci', axis='y', fontsize=9) 
        ax4.set_xlim( 0, 4.9 )
        ax4.set_ylim( 2000000, 5500000 )
        ax4.set_xticks(ind+ 0.5)
        ax4.set_title('Real time cost: 150 Usd (WCS)', fontsize=10) 
        ax4.set_xticklabels( ('0.08', '0.09', '0.1','0.11','0.13'),fontsize=9 )
        groups = []
        labels = []
        backhaul15 = np.array( [  2896944  ,    3015964  ,    3109389  ,    3183874  ,    4976891  ])
        backhaul25 = np.array( [  2891143  ,    3010149  ,    3103455  ,    3177843  ,    3304176  ] )
        backhaul35 = np.array([  2885342   ,   3004334   ,   3097494   ,   3171811   ,   3298022  ])
        
        sc41 = plt.bar(ind+width , tuple(backhaul15), width2, color='#F4561D', hatch="/" )
        groups.append(sc41[0])
        labels.append('15 Usd ')
        
        width = width + 0.25 
        sc42 = plt.bar(ind+width, backhaul25, width2, color='#F1911E', hatch="//" )
        groups.append(sc42[0])
        labels.append('25 Usd ')
        
        width = width + 0.25
        sc43 = plt.bar(ind+width, backhaul35, width2, color='#F1BD1A' )
        groups.append(sc43[0])
        labels.append('35 Usd ')

        
        plt.rc('font', size=10)
        ax4.legend(tuple(groups), tuple(labels), loc='upper left', prop={'size':8})

        plt.show()



    def graphOptimalAssigmentAnchorCustomer(self, relative_path, file_name):
        

        fname = path.expanduser('~/' + relative_path + '/' + file_name)

        matrix_data = np.genfromtxt(fname,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[1:, 1:] # from row 1 to the end, from column 1 to the end column
        periods = matrix_data[0,1:] # row 0 from columns 1
        print plot_data 
 
        plt.close('all')
        fig = plt.figure(figsize=(14,5.5), facecolor='w', edgecolor='k')
        plt.subplots_adjust(left=0.05,right=0.95,bottom=0.3,top=0.9)
        plt.rcParams['axes.linewidth'] = 0.8  
            
        ax = fig.add_subplot(1,2,1)
        ax.grid(True)
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        ax.plot( plot_data[0,], color='b', marker='.', markevery=50,   label=r'Backhaul Cost (USD/MB)'  )
        ax.plot( plot_data[1,], color='b', marker='^', markevery=50,   label=r'Real Time Cost (USD/MB)'  )
        ax.plot( plot_data[2,], color='g', marker='^', markevery=50,  label=r'$\sigma = 0$' )
        ax.plot( plot_data[3,], color='g', marker='.', markevery=50, label=r'$\sigma$ = $10\%$'  )
        ax.plot( plot_data[4,], color='y', marker='^', markevery=50, label=r'$\sigma$ = $20\%$'  )
        
        ax.set_ylabel( "USD /MB" )
        ax.set_xlabel( "Hour.Minute" )
        print periods
        ax.set_xticklabels(['5.00','6.40','8.20','10.00','11.40','13.20','15.00','16.40','18.20'])
        #ax.yaxis.major.formatter.set_powerlimits((0,0)) 
        #ax.ticklabel_format(style='sci', axis='y', fontsize=9) 
        
        #plt.xticks(range(int(minPeriod),int(maxPeriod),5))
        ax.legend(bbox_to_anchor=(0., -0.3, 1., .102), loc=5,ncol=3,prop={'size':12}, mode="expand", borderaxespad=0.)
        #ax.legend(loc=0, ncol=3, prop={'size':12})
  
        ax.set_title('(a) DTN enabled price evolution for different $\sigma$ values')

        ax2 = fig.add_subplot(1,2,2)
        ax2.grid(True)
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        ax2.plot( plot_data[5,], color='k', marker='.', markevery=50,   label=r'Total'  )
        ax2.plot( plot_data[6,], color='b', marker='o', markevery=50, label=r'Backhaul'  )
        ax2.plot( plot_data[7,], color='g', marker='^', markevery=50, label=r'Real Time'  )
        ax2.set_ylabel( "Traffic(MBs)" )
        ax2.set_xlabel( "Hour.Minute" )
        print periods
        ax2.set_xticklabels(['5.00','6.40','8.20','10.00','11.40','13.20','15.00','16.40','18.20'])
        #ax2.yaxis.major.formatter.set_powerlimits((0,0)) 
        #ax2.ticklabel_format(style='sci', axis='y', fontsize=9) 
        #plt.xticks(range(int(minPeriod),int(maxPeriod),5))
        #left, bottom, width, height
        ax2.legend(bbox_to_anchor=(0., -0.3, 1., .102), loc=5,ncol=3,prop={'size':10}, mode="expand", borderaxespad=0.)
        #ax.legend(loc=0, ncol=3, prop={'size':12})
        ax2.set_title('(b) Optimal flow assignment for anchor customers')
        
        plt.rc('font', size=10)
        plt.show()


    def graphOptimalAssigmentFlow(self, relative_path, file_name):
        

        fname = path.expanduser('~/' + relative_path + '/' + file_name)

        matrix_data = np.genfromtxt(fname,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[1:, 1:] # from row 1 to the end, from column 1 to the end column
        periods = matrix_data[0,1:] # row 0 from columns 1
        print plot_data 
 
        plt.close('all')
        fig = plt.figure(figsize=(12,5.5), facecolor='w', edgecolor='k')
        plt.rcParams['axes.linewidth'] = 0.8  
            
        ax = fig.add_subplot(1,1,1)
        ax.grid(True)
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        ax.plot( plot_data[0,], color='b', marker='*', markevery=50,   label=r'a(t) Voice'  )
        ax.plot( plot_data[3,], color='g', marker='*', markevery=50,   label=r'a(t) Http'  )
        ax.plot( plot_data[6,], color='y', marker='*', markevery=50,   label=r'a(t) Mail'  )
        
        ax.plot( plot_data[2,], color='b', marker='^', markevery=50,   label=r'D(t) Voice'  )
        ax.plot( plot_data[5,], color='g', marker='^', markevery=50,   label=r'D(t) Http'  )
        ax.plot( plot_data[8,], color='y', marker='^', markevery=50,   label=r'D(t) Mail'  )
        
               
        ax.set_ylabel( "Traffic (MBs)" )
        ax.set_xlabel( "Hour.Minute" )
        print periods
        ax.set_xticklabels(['5.00','6.40','8.20','10.00','11.40','13.20','15.00','16.40','18.20'])
        #ax.yaxis.major.formatter.set_powerlimits((0,0)) 
        #ax.ticklabel_format(style='sci', axis='y', fontsize=9) 
        
        #plt.xticks(range(int(minPeriod),int(maxPeriod),5))
        ax.legend(bbox_to_anchor=(0., -0.3, 1., .102), loc=5,ncol=3,prop={'size':12}, mode="expand", borderaxespad=0.)
        #ax.legend(loc=0, ncol=3, prop={'size':12})
  
        plt.show()

    def graphOptimalAssigmentPrice(self, relative_path, file_name):
        

        fname = path.expanduser('~/' + relative_path + '/' + file_name)

        matrix_data = np.genfromtxt(fname,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[1:, 1:] # from row 1 to the end, from column 1 to the end column
        periods = matrix_data[0,1:] # row 0 from columns 1
        print plot_data 
 
        plt.close('all')
        fig = plt.figure(figsize=(12,5.5), facecolor='w', edgecolor='k')
        plt.rcParams['axes.linewidth'] = 0.8  
            
        ax = fig.add_subplot(1,1,1)
        ax.grid(True)
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        ax.plot( plot_data[1,], color='b', marker='*', markevery=50,   label=r'P(t) Voice'  )
        ax.plot( plot_data[4,], color='g', marker='*', markevery=50,   label=r'P(t) Http'  )
        ax.plot( plot_data[7,], color='y', marker='^', markevery=80,   label=r'P(t) Mail'  )
                
               
        ax.set_ylabel( "USD / MB" )
        ax.set_xlabel( "Hour.Minute" )
        print periods
        ax.set_xticklabels(['5.00','6.40','8.20','10.00','11.40','13.20','15.00','16.40','18.20'])
        #ax.yaxis.major.formatter.set_powerlimits((0,0)) 
        #ax.ticklabel_format(style='sci', axis='y', fontsize=9) 
        
        #plt.xticks(range(int(minPeriod),int(maxPeriod),5))
        ax.legend(bbox_to_anchor=(0., -0.3, 1., .102), loc=5,ncol=3,prop={'size':12}, mode="expand", borderaxespad=0.)
        #ax.legend(loc=0, ncol=3, prop={'size':12})
  
        plt.show()
        

    def graphOptimalAssigmentAnchorCustomerPrice(self, relative_path, file_name):
        

        fname = path.expanduser('~/' + relative_path + '/' + file_name)

        matrix_data = np.genfromtxt(fname,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[1:, 1:] # from row 1 to the end, from column 1 to the end column
        periods = matrix_data[0,1:] # row 0 from columns 1
        print plot_data 
 
        plt.close('all')
        fig = plt.figure(figsize=(14,5.5), facecolor='w', edgecolor='k')
        plt.rcParams['axes.linewidth'] = 0.8  
            
        ax = fig.add_subplot(1,1,1)
        ax.grid(True)
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        ax.plot( plot_data[0,], color='b', marker='.', markevery=50,   label=r'Backhaul Cost (USD/MB)'  )
        ax.plot( plot_data[1,], color='b', marker='^', markevery=50,   label=r'Real Time Cost (USD/MB)'  )
        ax.plot( plot_data[2,], color='g', marker='^', markevery=50,  label=r'$\sigma = 0$' )
        ax.plot( plot_data[3,], color='g', marker='.', markevery=50, label=r'$\sigma$ = $10\%$'  )
        ax.plot( plot_data[4,], color='y', marker='^', markevery=50, label=r'$\sigma$ = $20\%$'  )
        
        ax.set_ylabel( "USD /MB" )
        ax.set_xlabel( "Hour.Minute" )
        print periods
        ax.set_xticklabels(['5.00','6.40','8.20','10.00','11.40','13.20','15.00','16.40','18.20'])
        #ax.yaxis.major.formatter.set_powerlimits((0,0)) 
        #ax.ticklabel_format(style='sci', axis='y', fontsize=9) 
        
        #plt.xticks(range(int(minPeriod),int(maxPeriod),5))
        ax.legend(bbox_to_anchor=(0., -0.3, 1., .102), loc=5,ncol=3,prop={'size':12}, mode="expand", borderaxespad=0.)
        #ax.legend(loc=0, ncol=3, prop={'size':12})
  
        plt.show()

    def graphOptimalAssigmentAnchorCustomerFlow(self, relative_path, file_name):
        

        fname = path.expanduser('~/' + relative_path + '/' + file_name)

        matrix_data = np.genfromtxt(fname,dtype=float, skip_header=0, delimiter=';')
        plot_data = matrix_data[1:, 1:] # from row 1 to the end, from column 1 to the end column
        periods = matrix_data[0,1:] # row 0 from columns 1
        print plot_data 
 
        plt.close('all')
        fig = plt.figure(figsize=(7,5.5), facecolor='w', edgecolor='k')
        plt.rcParams['axes.linewidth'] = 0.8  
                    
        ax2 = fig.add_subplot(1,1,1)
        ax2.grid(True)
        
        #ax.axis([0 , maxPeriod , minDemand, maxDemand ])
        ax2.plot( plot_data[5,], color='k', marker='.', markevery=50,   label=r'Total'  )
        ax2.plot( plot_data[6,], color='b', marker='o', markevery=50, label=r'Backhaul'  )
        ax2.plot( plot_data[7,], color='g', marker='^', markevery=50, label=r'Real Time'  )
        ax2.set_ylabel( "Traffic(MBs)" )
        ax2.set_xlabel( "Hour.Minute" )
        print periods
        ax2.set_xticklabels(['5.00','6.40','8.20','10.00','11.40','13.20','15.00','16.40','18.20'])
        #ax2.yaxis.major.formatter.set_powerlimits((0,0)) 
        #ax2.ticklabel_format(style='sci', axis='y', fontsize=9) 
        #plt.xticks(range(int(minPeriod),int(maxPeriod),5))
        #left, bottom, width, height
        ax2.legend(bbox_to_anchor=(0., -0.3, 1., .102), loc=5,ncol=3,prop={'size':10}, mode="expand", borderaxespad=0.)
        #ax.legend(loc=0, ncol=3, prop={'size':12})
        
        plt.rc('font', size=10)
        plt.show()
