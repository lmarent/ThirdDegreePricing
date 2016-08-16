__docformat__ = "restructuredtext en"
import NetworkCapacity
import QueueModelling
import numpy
from numpy.core.numeric import dtype
from openopt import MILP
import globalVariables
import sys
from gurobipy import *

def dense_optimize(rows, cols, c, A, sense, rhs, lb, ub, vtype, solution):

  model = Model()
  model.setParam( 'OutputFlag', False )

  # Add variables to model
  for j in range(int(cols)):
    model.addVar(lb=lb[j], ub=ub[j], vtype=vtype[j])
  model.update()
  vars = model.getVars()

  # Populate A matrix
  for i in range(int(rows)):
    expr = LinExpr()
    for j in range(int(cols)):
      if A[i][j] != 0:
        expr += A[i][j]*vars[j]
    model.addConstr(expr, sense[i], rhs[i])

  # Populate objective
  obj = LinExpr()
  for j in range(int(cols)):
      obj += c[j]*vars[j]
  model.setObjective(obj, GRB.MAXIMIZE)

  # Write model to a file
  model.update()

  # Solve/opt/gurobi502/linux32/lib/
  model.optimize()

  retorno = {}
  if model.status == GRB.OPTIMAL:
    for i in range(int(cols)):
      solution[i] = vars[i].x
    retorno['status'] = True
    retorno['optimalValue'] = model.objVal
    retorno['variableValues'] = solution
    if globalVariables.progDebug == True:
        try: 
            fileDebug = open("debug.txt", "a+")
            fileDebug.writelines('\n' )
            fileDebug.writelines('Gurobi - End parameters' + '\n' )
            fileDebug.writelines('optimal value' + str(model.objVal) +  '\n' )
            fileDebug.writelines(' variables: ' +  solution.__str__() )
            fileDebug.close()
        except IOError:
            pass
    return retorno
  else:
    retorno['status'] = False
    retorno['optimalValue'] = -1
    retorno['variableValues'] = solution
    return retorno




def optimizeScenario(nodekey, listaParametros, maxServers, CmaxCapacity, clusterData):

        
    queueElements = NetworkCapacity.findProbabilityStatisticsforServices(listaParametros, maxServers)

#    try:
#        # This will create a new file or **overwrite an existing file**.
#        nodekeyFile = nodekey + ".txt" 
#        fileOptimization = open(nodekeyFile, "a+")
#        try:
#
#            fileOptimization.write("param maxChannels := ")
#            fileOptimization.write("%s;" %maxServers)
#            fileOptimization.write("\n")
#
#            fileOptimization.write("param Cmax := ")
#            fileOptimization.write("%s;" %CmaxCapacity)
#            fileOpparametertimization.write("\n")
#
#            for i in listaParametros:
#                fileOptimization.write("set SERVICETYPE :=  ")
#                fileOptimization.write("%s "%i['typeOfService'])
#                fileOptimization.write(" ")
#                
#            fileOptimization.write(";\n")
#            
#            for i in listaParametros:
#                fileOptimization.write("param:  prices:= ")
#                fileOptimization.write("\n")
#                fileOptimization.write("%s "%i['typeOfService'])
#                fileOptimization.write("      ")
#                fileOptimization.write("%s "%i['price'])
#                fileOptimization.write("\n")
#            fileOptimization.write(";\n")    
#                
#            fileOptimization.write("param events:")
#            fileOptimization.write("\n")
#            for i in range(int(maxServers + 1)):
#                fileOptimization.write("%s   " %i)
#            fileOptimization.write("    :=")
#            for index_i in range(len(listaParametros)):
#                fileOptimization.write("\n")                 
#                fileOptimization.write(listaParametros[index_i]['typeOfService'])
#                fileOptimization.write("    ")
#                for index_j in range(int(maxServers + 1)):
#                    fileOptimization.write("%s  " %averageElements[index_i][index_j])            
#            fileOptimization.write(";")
#            
#            #fileOptimization.write("averageElements %s" %averageElements) # Write a string to a file
#            #fileOptimization.write("\n")
#        finally:
#            fileOptimization.close()
#    except IOError:
#        pass
    
    shape = (len(listaParametros),maxServers + 1)
    coefObjetive =  numpy.zeros(shape ,dtype=float)
    for item in listaParametros:
        itemParameter =  listaParametros[item]
        clusterParameters = itemParameter['clusterParameters']
        serviceQueueItems = queueElements[item]
        serviceNonBlockingProbabilities = serviceQueueItems['nonBlockingProbabilities']
        index_i = itemParameter['index']  
        for index_j in range(int(maxServers + 1)):
            expectedClusterRevenue = 0
            for clusterName in clusterParameters:
                clusterParameter = clusterParameters[clusterName]
                if  clusterParameter['execute'] == True:
                    clusterNonBlockingProbabilities = serviceNonBlockingProbabilities[clusterName]
                    repetitions = clusterData[clusterName]
                    numServices = numpy.ceil( clusterNonBlockingProbabilities[index_j] * clusterParameter['lambda'] ) * repetitions
                    expectedClusterRevenue =  expectedClusterRevenue + ( itemParameter['configuration'] * itemParameter['priceUse'] * numServices ) + ( itemParameter['priceAccess'] * numServices )    
            coefObjetive[index_i][index_j]=  expectedClusterRevenue
    totalCoeficients = len(listaParametros) * (maxServers + 1)
    coeficFinal = numpy.reshape(coefObjetive, totalCoeficients, order='C')
    #print 'coefObjetivos Matrix'
    #print coefObjetive  
    #print 'End coefObjetivos Matrix'
    #
    #Constraints Building
    #
    # Constraint 1. The system must restrict that only operates the service type i with and only with 
    #               one number of servers 
    matrizA_retriccionUno = numpy.zeros((len(listaParametros),totalCoeficients),dtype=float)
    vectorB_retriccionUno = numpy.zeros(len(listaParametros),dtype=float)
    for index_i in range(len(listaParametros)):
        restriccion = numpy.zeros(shape,dtype=float)
        for index_j in range(int(maxServers + 1)):
                restriccion[index_i][index_j] = 1
        matrizA_retriccionUno[index_i] = numpy.reshape(restriccion, totalCoeficients,order='C')
        vectorB_retriccionUno[index_i] = 1
    #print 'ConstraintOne Matrix'
    #print matrizA_retriccionUno
    #print 'End ConstraintOne Matrix'
    #print 'VectorB constraint One'
    #print vectorB_retriccionUno
    #print ' End VectorB constraint One'
    # -------------------------------------------------
    # Constraint two. The system could not use more than installed capacity
    #-------------------------------------------------
    matrizb_restriccionDos = numpy.zeros((1,totalCoeficients),dtype=float)
    vectorB_restriccionDos = numpy.zeros(1,dtype=float)
    restriccion = numpy.zeros(shape,dtype=float)
    for index_i in range(len(listaParametros)):    
        for index_j in range(int(maxServers + 1)):
                restriccion[index_i][index_j] = index_j
    matrizb_restriccionDos[0] = numpy.reshape(restriccion, totalCoeficients,order='C')
    vectorB_restriccionDos[0] = CmaxCapacity
    #print 'Matrix constraint two'
    #print matrizb_restriccionDos
    #print 'End Matrix constraint two'
    #print 'VectorB constraint two'
    #print vectorB_restriccionDos
    #print 'End VectorB constraint two' 
    
    
    #-------------------------------------------------------
    # Constraint Three. The system could choose the number of servers for each type of service 
    #                   between those that permit operation with the minimum threshold of operation  for each cluster
    #-------------------------------------------------------        
#    for index_i in range(len(listaParametros)):
    matrizP =  numpy.ones((len(listaParametros),(maxServers + 1)),dtype=float)   
    for item in listaParametros:
        itemParameter =  listaParametros[item]
        index_i = itemParameter['index']  
        clusterParameters = itemParameter['clusterParameters']
        serviceQueueItems = queueElements[item]
        serviceNonBlockingProbabilities = serviceQueueItems['nonBlockingProbabilities']
        for index_j in range(int(maxServers + 1)):
            for clusterName in clusterParameters:
                clusterParameter = clusterParameters[clusterName]
                if  clusterParameter['execute'] == True:                
                    clusterNonBlockingProbabilities = serviceNonBlockingProbabilities[clusterName]
                    if clusterNonBlockingProbabilities[index_j] == 0:
                        matrizP[index_i][index_j] = 0   
    #print matrizP


#    try:
#        # This will create a new file or **overwrite an existing file**.
#        nodekeyFile = nodekey + ".txt" 
#        fileOptimization = open(nodekeyFile, "a+")
#        try:
#            fileOptimization.write("\n")
#            fileOptimization.write("param channelPossibility:")
#            fileOptimization.write("\n")
#            for i in range(int(maxServers + 1)):
#                fileOptimization.write("%s   " %i)
#            fileOptimization.write("    :=")                
#            for index_i in range(len(listaParametros)):
#                fileOptimization.write("\n")                 
#                fileOptimization.write(listaParametros[index_i]['typeOfService'])
#                fileOptimization.write("    ")
#                for index_j in range(int(maxServers + 1)):
#                    fileOptimization.write("%s  " %matrizP[index_i][index_j])            
#            fileOptimization.write(";")        
#        finally:
#            fileOptimization.close()
#    except IOError:
#        pass

    totalRestriccionesTres = len(listaParametros) * (maxServers + 1)
    matrizb_restriccionTres = numpy.zeros((totalRestriccionesTres,totalCoeficients),dtype=float)
    vectorB_restriccionTres = numpy.zeros(totalRestriccionesTres,dtype=float)
    restriccion = numpy.zeros(shape,dtype=float)
    for index_i in range(len(listaParametros)):    
        for index_j in range(int(maxServers + 1)):
            restriccion[index_i][index_j] = 1
            constraintIndex = ( index_i*(maxServers + 1) ) + index_j
            matrizb_restriccionTres[constraintIndex] = numpy.reshape(restriccion, totalCoeficients,order='C')
            vectorB_restriccionTres[constraintIndex] = matrizP[index_i][index_j] 
            restriccion = numpy.zeros(shape,dtype=float)
                 
    # This part of the code creates the A matrix required in the solver
    shapeMatrixA = (matrizb_restriccionTres.shape[0] + matrizb_restriccionDos.shape[0], matrizb_restriccionTres.shape[1])
    matrixA = numpy.zeros(shapeMatrixA,dtype=float)
    vectorB = numpy.zeros(matrixA.shape[0], dtype=float)
    for index_r2 in range(matrizb_restriccionDos.shape[0]):
        matrixA[index_r2] = matrizb_restriccionDos[index_r2]
        vectorB[index_r2] = vectorB_restriccionDos[index_r2]
    for index_r3 in range(matrizb_restriccionTres.shape[0]):
        matrixA[matrizb_restriccionDos.shape[0] + index_r3] = matrizb_restriccionTres[index_r3]
        vectorB[matrizb_restriccionDos.shape[0] + index_r3] = vectorB_restriccionTres[index_r3]

    # this part of the code creates the A matrix for Gurobi Solver
    shapeMatrixAGurobi = (matrizA_retriccionUno.shape[0] + matrizb_restriccionDos.shape[0] + matrizb_restriccionTres.shape[0], matrizb_restriccionTres.shape[1])
    matrixAGurobi = numpy.zeros(shapeMatrixAGurobi,dtype=float)
    vectorBGurobi = numpy.zeros(matrixAGurobi.shape[0], dtype=float)
    sense = [GRB.LESS_EQUAL]*matrixAGurobi.shape[0] 
    for index_r1 in range(matrizA_retriccionUno.shape[0]):
        matrixAGurobi[index_r1] = matrizA_retriccionUno[index_r1]
        vectorBGurobi[index_r1] = vectorB_retriccionUno[index_r1]
        sense[index_r1] = GRB.EQUAL
    for index_r2 in range(matrizb_restriccionDos.shape[0]):
        matrixAGurobi[matrizA_retriccionUno.shape[0] + index_r2] = matrizb_restriccionDos[index_r2]
        vectorBGurobi[matrizA_retriccionUno.shape[0] + index_r2] = vectorB_restriccionDos[index_r2]
        sense[matrizA_retriccionUno.shape[0] + index_r2] = GRB.LESS_EQUAL
    for index_r3 in range(matrizb_restriccionTres.shape[0]):
        matrixAGurobi[matrizA_retriccionUno.shape[0] + matrizb_restriccionDos.shape[0] + index_r3] = matrizb_restriccionTres[index_r3]
        vectorBGurobi[matrizA_retriccionUno.shape[0] + matrizb_restriccionDos.shape[0] + index_r3] = vectorB_restriccionTres[index_r3]
        sense[matrizA_retriccionUno.shape[0] + matrizb_restriccionDos.shape[0] + index_r2] = GRB.LESS_EQUAL
    
    #numpy.set_printoptions(threshold = numpy.nan)
    #print "matrixA"
    #print  matrixA   
    #print "vectorB"
    #print vectorB
    lb = numpy.zeros(totalCoeficients)
    ub = numpy.ones(totalCoeficients)
    # In this code it is defined the variables
    myintVars = [int(totalCoeficients - 1)]

# The general formulation is:    
#max Fx
# subject to
# lb <= x <= lu
# Ax <= b
# AeqX = Beq
# X in booleand or integers      

    
    cols = totalCoeficients 
    solution = [0]*cols
    vtype = [GRB.BINARY]* totalCoeficients
    retorno = dense_optimize(matrixAGurobi.shape[0] , cols, coeficFinal, matrixAGurobi, sense, vectorBGurobi, lb, ub, vtype, solution)
    
    

#    try:
#        # This will create a new file or **overwrite an existing file**.
#        nodekeyFile = nodekey + ".txt" 
#        fileOptimization = open(nodekeyFile, "a+")
#        try:
#            fileOptimization.write("\n")
#            fileOptimization.write("\n")
#            fileOptimization.write("param optimalValue:=")
#            fileOptimization.write("%s;"%r.ff)        
#        finally:
#            fileOptimization.close()
#    except IOError:
#        pass

    
    return retorno

def optimizeScenarioInterface(nodekey, scenario, installedCapacity, maxServers, minChannel, clusterData):
    if globalVariables.progDebug == True:
        try: 
            fileDebug = open("debug.txt", "a+")
            fileDebug.writelines('optimizeScenarioInterface - Init parameters'  )
            fileDebug.writelines(' scenario: ' +  scenario.__str__())
            fileDebug.writelines(' installedCapacity: ' +  str(installedCapacity))
            fileDebug.writelines(' maxServers: ' +  str(maxServers))
            fileDebug.close()
        except IOError:
            pass
    
    
#    try:
#        # This will create a new file or **overwrite an existing file**.
#        nodekeyFile = nodekey + ".txt" 
#        fileOptimization = open(nodekeyFile, "w")
#        try:
#            fileOptimization.write("data;" ) # Write a string to a file
#            fileOptimization.write("\n")
#            fileOptimization.write("\n")
#        finally:
#            fileOptimization.close()
#    except IOError:
#        pass
    
    
    addtionalCapacity = scenario['additonalCapacity']
    CmaxCapacity = installedCapacity + addtionalCapacity 
    CmaxCapacity = CmaxCapacity / minChannel
    scenarioParameters = scenario['scenarioParameters']
    optimalResult = optimizeScenario(nodekey, scenarioParameters, maxServers, CmaxCapacity, clusterData)
    if optimalResult['status'] == True:
        shape = (len(scenarioParameters),maxServers + 1)
        numServers = {}
        variables = numpy.reshape(optimalResult['variableValues'], shape, order='C')
        TotalServers = 0
        #print variables
        for item in scenarioParameters:
            itemParameter =  scenarioParameters[item]
            index = itemParameter['index']
            found = False
            for j in range(int(maxServers + 1)):
                assignedValue = variables[index][j]
                if numpy.abs(assignedValue - 1) <= 0.0001:
                      numServers[item] = j
                      TotalServers = TotalServers + j 
                      found = True
            if (found == False):
                numServers[item] = 0 
        retorno = {}
        retorno['optimalValue'] = (optimalResult['optimalValue']) - (TotalServers * 150) 
        retorno['assignment'] = numServers
    else:
        retorno = {}
        retorno['optimalValue'] = -1 
        retorno['assignment'] = {}
        
    if globalVariables.progDebug == True:
        try: 
            fileDebug = open("debug.txt", "a+")
            fileDebug.writelines('optimizeScenarioInterface - End parameters' + '\n' )
            fileDebug.writelines(' Server number: ' +  str(TotalServers) )
            fileDebug.writelines(' Optimal value: ' +  str(retorno['optimalValue']) + "\n" )
            fileDebug.writelines(' assignment: ' +  str(retorno['assignment']) )
            fileDebug.writelines(' variables: ' +  variables.__str__() )
            fileDebug.close()
        except IOError:
            pass

    

#    try:
#        # This will create a new file or **overwrite an existing file**.
#        nodekeyFile = nodekey + ".txt" 
#        fileOptimization = open(nodekeyFile, "a+")
#        try:
#
#            fileOptimization.write("\n")
#            fileOptimization.write("param:  numServersAssigned:= ")
#            fileOptimization.write("\n")
#            for i in listaParametros:
#                fileOptimization.write(i['typeOfService'])
#                fileOptimization.write("   %s"%numServers[i['typeOfService']]) 
#            fileOptimization.write(";")
#        finally:
#            fileOptimization.close()
#    except IOError:
#        pass

    
    #print 'capacityExtensionForeward - Init Output'
    #print retorno
    #print 'capacityExtensionForeward - End Output'
    return retorno 
        


#listaParametros = []
#
#
## Parametros generales
#
##Prices
#CmaxCapacity = 14
#
## Tecnologia 1, 
#
##lamda representa la cantidad de llegadas al sistema por unidad de tiempo
## inicialmente va a ser por minuto
#lamda = 1.5
## Mu representa el inverso del promedio de tiempo en que se tarda en atender un servicio solicitado 
#mu = 1
#maxCapacity = 15
#maxServers = 10
#probServicio = 0.95
#alpha = lamda / mu
#
#
#
#
#print parametros['alpha']
#listaParametros.append(parametros)
#
##Tecnologia 2
#lamda = 6
#mu = 1
#maxServers = 10
#probServicio = 0.95
#alpha = lamda / mu
#
#
#parametros = {}
#parametros['price'] = 80 
#parametros['alpha'] = alpha
#parametros['probServicio'] = probServicio
#
#
#listaParametros.append(parametros)
#
#print optimizeScenario(listaParametros, maxServers, CmaxCapacity)
