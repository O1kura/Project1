from http.client import NETWORK_AUTHENTICATION_REQUIRED
from platform import mac_ver
from re import I, M
import pandas as pd
import csv
import math
import matplotlib.pyplot as plt
import numpy as np


class CS_IFS(object):
    def __init__(self, filename):
        self.trainPath          = "Train_" + filename  #save the name of the train set for process data in PreProcessing method
        self.testPath           = "Test_" + filename   #save the name of the test set for predicting
        self.data               = None      #save the data extract from the csv file by using pandas
        self.test               = None      #save the data extract from the test set
        self.dataValue          = None      #save the value of all cells in csv table 
        self.testValue          = None      #save the value of all cells in the test set
        self.dataHeader         = None      #save the name of all columns in csv table
        self.numberOfHeader     = None      #save the number of columns in csv file without the label columns
        self.numberOfLabel      = None      #save the label of cases in csv table
        self.label              = None      #save the name of labels
        self.labelValue         = None      #save the label of all instances in csv table
        self.TlabelValue        = None      #save the label of all instances in the test set
        self.predictLabel       = None      #save the predict label of all instances in csv table by using cs_ifs method
        self.predictLabelT      = None      #save the predict label of all instances in test set
        self.numberOfInstances  = None      #save the number of instances in csv table
        self.numberOfTest       = None      #save the number of instances in the test set
        self.weights            = None      #save the weights of all features in the cs_ifs model
        self.result             = None      #save the distance between the instances with each center in center list
        self.Tresult            = None      #save the distance between the instances with each center in center list
        self.RelTableTrain      = None      #save the result of IF function in the train set
        self.SurgenoTableTrain  = None      #save the result of NON_IF function in the train set
        self.RelTableVal        = None      #save the result of IF function in the validate set
        self.SurgenoTableVal    = None      #save the result of NON_IF function in the validate set
        self.RelTableTest       = None      #save the result of IF function in the test set
        self.SurgenoTableTest   = None      #save the result of NON_IF function in the test set
        self.RelCenterTable     = None      #save the result of IF function of center list
        self.SurgenoCenterTable = None      #save the result of NON_IF function of center list
        self.accuracy           = 0         #save the accuracy of cs_ifs model with the csv file
        self.accuracyV          = 0         #save the accuracy of cs_ifs model with the validation set
        self.accuracyT          = 0         #save the accuracy of cs_ifs model with the test set
        self.time               = 0         #save total time to updating the weights
        self.measure            = "Euclid"  #save the measurement to evaluate the distance between 2 points in the csv file
    
    #Process the raw data to suitable data
    def PreProcessingCSV(self, isTrain = True):
        if isTrain == True:
            self.data = pd.read_csv(self.trainPath, delimiter = None)
            self.dataHeader = self.data.columns.values
            self.numberOfHeader = len(self.dataHeader.tolist()) - 1
            self.dataHeader = [self.dataHeader[idxHeader].strip() for idxHeader in range(self.numberOfHeader + 1)]
            self.label =  list(set(self.data[self.dataHeader[self.numberOfHeader]].values.tolist()))
            self.numberOfLabel = len(self.label)
            self.dataValue = self.data[self.dataHeader[:self.numberOfHeader]].values.tolist()
            self.labelValue = self.data[self.dataHeader[self.numberOfHeader]].values.tolist()
            self.numberOfInstances = len(self.dataValue)
        else:
            self.test = pd.read_csv(self.testPath, delimiter = None)
            self.testValue = self.test[self.dataHeader[:self.numberOfHeader]].values.tolist()
            self.TlabelValue = self.test[self.dataHeader[self.numberOfHeader]].values.tolist()
            self.numberOfTest = len(self.testValue)

    #Create two table using two function below to use for the next steps
    def CreateFuzzyTable(self, isTrain = True):
        if isTrain == True:
            RelTable = [[0 for i in range(self.numberOfHeader)] for j in range(self.numberOfInstances)]
            SurgenoTable = [[0 for i in range(self.numberOfHeader)] for j in range(self.numberOfInstances)]
        else:
            RelTable = [[0 for i in range(self.numberOfHeader)] for j in range(self.numberOfTest)]
            SurgenoTable = [[0 for i in range(self.numberOfHeader)] for j in range(self.numberOfTest)]
        for columnName in self.dataHeader[:self.numberOfHeader]:
            self.RelFunction(columnName, RelTable, isTrain = isTrain)
            self.SurgenoFunction(columnName, SurgenoTable, RelTable, isTrain = isTrain)
        return RelTable, SurgenoTable
    
    # Step 1: Include 2 main method RelFunction and Surgeno Function which use for calculate the 
    # reliability function and surgeno function based on 2 function
    # Reliability function: y[i, j] = (r[i, j] - min r[i, j]) / (max r[i, j] - min r[i, j]) (with j = 1, 2, ... m) (1)
    # Surgeno function:     n[i, j] = (1 - y[i, j]) / (1 + y[i, j]) (2)
    
    #Calculation Reliability function
    def RelFunction(self, columnName, RelTable, isCalCenter = False, centerValue = [[]], isTrain = True):
        if isTrain == True:
            number = self.numberOfInstances
            columnData = self.data[columnName].values.tolist()
        else:
            number = self.numberOfTest
            columnData = self.test[columnName].values.tolist()
        minValue = min(columnData)
        maxValue = max(columnData)
        idxColumn = self.dataHeader.index(columnName)
        if isCalCenter == False:
            for idx in range(number):
                RelTable[idx][idxColumn] = (columnData[idx] - minValue) / (maxValue - minValue) 
        else:
            for idxLabel in range(self.numberOfLabel):
                RelTable[idxLabel][idxColumn] = (centerValue[idxLabel][idxColumn] - minValue) / (maxValue - minValue)
    
    #Calculation Surgeno fuction
    def SurgenoFunction(self, columnName, SurgenoTable, RelTable, isCalCenter = False, isTrain = True):
        idxColumn = self.dataHeader.index(columnName)
        if isCalCenter == False:
            if isTrain == True:
                length = self.numberOfInstances
            else:
                length = self.numberOfTest
        else:
            length = self.numberOfLabel
        for idx in range(length):
            SurgenoTable[idx][idxColumn] = (1 - RelTable[idx][idxColumn]) / (1 + RelTable[idx][idxColumn])

    
    def CalWeights(self, RelTable, SurgenoTable, criterion = 10 **(-4)):
        self.weights = [1 / self.numberOfHeader for i in range(self.numberOfHeader)]
        passCriterion = 0
        while passCriterion < self.numberOfHeader:
            passCriterion = 0
            newWeight = [0 for i in range(self.numberOfHeader)]
            componentT = [self.CalWeightsComponentT(idxColumn, RelTable, SurgenoTable) for idxColumn in range(self.numberOfHeader)]
            denominatorW = 0
            for idx in range(self.numberOfHeader):
                denominatorW += self.weights[idx] * componentT[idx]
            for idx in range(self.numberOfHeader):
                newWeight[idx] = self.weights[idx] * componentT[idx] / denominatorW
                dif = abs(newWeight[idx] - self.weights[idx])
                if dif < criterion:
                    passCriterion += 1
                self.weights[idx] = newWeight[idx]
            self.time += 1
            
        
    
    # Calculation T component with the function below:
    # T[j] = |S(y[i, j], n[i, j]) - S(n[i, j], y[i, j])| / m 
    # with: m is the number of instances
    #       i = 1, 2, ..., m
    
    def CalWeightsComponentT(self, idxColumn, RelTable, SurgenoTable):
        numeratorT = 0
        for idx in range(self.numberOfInstances):
            y = RelTable[idx][idxColumn]
            n = SurgenoTable[idx][idxColumn]
            numeratorT += abs(self.CalWeightsComponentS(y, n) - self.CalWeightsComponentS(n, y))
        componentT = numeratorT / self.numberOfInstances
        return componentT
    
    # Calculation S component with the function below:
    # S(y[i, j], n[i, j]) = (3 + 2 * y[i, j] + y[i, j] ^ 2 - n[i, j] - 2 * n[i, j] ^ 2) * exp(2 * y[i, j] - 2 * n[i, j] - 2) / 6 (5)

    def CalWeightsComponentS(self, y, n):
        componentS = (3 + 2 * y + (y) ** 2 - n - 2 * (n) ** 2) * math.exp(2 * y - 2 * n - 2) / 6
        return componentS
    
    def CalClusterCenter(self):
        dictLabel = {}
        dictCenterLabel = {}
        dictElementsLabel = {}
        for label in self.label:
            dictLabel[label] = []
            dictCenterLabel[label] = [0 for i in range(self.numberOfHeader)]
            dictElementsLabel[label] = 0
        for instance in range(self.numberOfInstances):
            for label in self.label:
                if label == self.labelValue[instance]:
                    dictLabel[label].append(instance)
                    dictCenterLabel[label] = [dictCenterLabel[label][idx] \
                        + self.dataValue[instance][idx] for idx in range(self.numberOfHeader)]
                    dictElementsLabel[label] += 1
        RelCenterTable = [[0 for i in range(self.numberOfHeader)] for j in range(self.numberOfLabel)]
        SurgenoCenterTable = [[0 for i in range(self.numberOfHeader)] for j in range(self.numberOfLabel)]
        centerValue = []
        for eachLabel in self.label:
            dictCenterLabel[eachLabel] = [dictCenterLabel[eachLabel][idx] / dictElementsLabel[eachLabel] for idx in range(self.numberOfHeader)]
            centerValue.append(dictCenterLabel[eachLabel])
        for columnName in self.dataHeader[:self.numberOfHeader]:
            self.RelFunction(columnName = columnName, RelTable = RelCenterTable, isCalCenter = True, centerValue = centerValue)
            self.SurgenoFunction(columnName = columnName, SurgenoTable = SurgenoCenterTable, RelTable = RelCenterTable, isCalCenter = True)
        return RelCenterTable, SurgenoCenterTable
    
    #Calculation the distance between each instance and the labels in the label list
    def CalDistance(self, isTrain = True, measure = "Default"):
        self.measure = measure
        if isTrain == True:
            length = self.numberOfInstances
        else:
            length = self.numberOfTest
        result = [[0 for idx in range(self.numberOfLabel)] for j in range(length)]
        if self.measure == "Default":
            for idx in range(length):
                for idxLabel in range(self.numberOfLabel):
                    distance = 0
                    for idxCol in range(self.numberOfHeader):
                        if isTrain == True:
                            distance += self.weights[idxCol] * abs(self.CalWeightsComponentS(self.RelTableTrain[idx][idxCol], self.SurgenoTableTrain[idx][idxCol]) - self.CalWeightsComponentS(self.RelCenterTable[idxLabel][idxCol], self.SurgenoCenterTable[idxLabel][idxCol]))
                        else:
                            distance += self.weights[idxCol] * abs(self.CalWeightsComponentS(self.RelTableTest[idx][idxCol], self.SurgenoTableTest[idx][idxCol]) - self.CalWeightsComponentS(self.RelCenterTable[idxLabel][idxCol], self.SurgenoCenterTable[idxLabel][idxCol]))
                    result[idx][idxLabel] = distance
        if isTrain == True:
            self.result = result
        else:
            self.Tresult = result
    
    #Classification the label of instances again
    def ClassificationLabel(self, isTrain = True):
        if isTrain == True:
            length = self.numberOfInstances
        else:
            length = self.numberOfTest
        predictLabel = [0 for i in range(length)]
        for idx in range(length):
            if isTrain == True:
                minDistance = min(self.result[idx])
                k = self.result[idx].index(minDistance)
            else:
                minDistance = min(self.Tresult[idx])
                k = self.Tresult[idx].index(minDistance)
            predictLabel[idx] = self.label[k]
        if isTrain == True:
            self.predictLabel = predictLabel
        else:
            self.predictLabelT = predictLabel
    
    def Accuracy(self, isTrain = True):
        trueClass = 0
        if isTrain == True:
            length = self.numberOfInstances
            for idx in range(length):
                if self.labelValue[idx] == self.predictLabel[idx]:
                    trueClass += 1
                else:
                    continue
            self.accuracy = (trueClass / length) * 100
        else:
            length = self.numberOfTest
            for idx in range(length):
                if self.TlabelValue[idx] == self.predictLabelT[idx]:
                    trueClass += 1
                else:
                    continue
            self.accuracyT = (trueClass / length) * 100
        
    def fit(self, criterion = 10 ** (-4)):
        self.PreProcessingCSV()
        self.RelTableTrain, self.SurgenoTableTrain = self.CreateFuzzyTable()
        self.CalWeights(self.RelTableTrain, self.SurgenoTableTrain, criterion = criterion)
        self.RelCenterTable, self.SurgenoCenterTable = self.CalClusterCenter()
        self.CalDistance()
        self.ClassificationLabel()
        self.Accuracy()
        print("The result of CS_IFS algorithm in the train set: ", self.accuracy, "%")
        return self.accuracy

        
    def writeFile(self):
        return None
    
    def predict(self):
        self.PreProcessingCSV(isTrain = False)
        self.RelTableTest, self.SurgenoTableTest = self.CreateFuzzyTable(isTrain = False)
        self.CalDistance(isTrain = False)
        self.ClassificationLabel(isTrain = False)
        self.Accuracy(isTrain = False)
        print("The result of CS_IFS algorithm in the test set: ", self.accuracyT, "%")
        return self.accuracyT


class SpaceSearch(object):
    def __init__(self, model, _range):
        self.model = model
        self.range = _range
        
    def BestResutl(self):
        result = []
        weight_lst = []
        for criterion in self.range:
            result.append(self.model.fit(criterion))
        max_res = max(result)
        k_idx = result.index(max_res)
        print("*____________________Best Train result____________________*")
        res = self.model.fit(self.range[k_idx])
        print("The result of CS_IFS algorithm in the train set: ", res, "%")
        print("Optimal weight:", self.model.weights)
        print("*__________Result of best weight in training set__________*")      
        tes = self.model.predict()
        print("The result of CS_IFS algorithm in the testing set: ", tes, "%")
        
        
lst = [1, 0.1, 0.01, 0.001, 0.0001, 1e-05, 1e-06]

