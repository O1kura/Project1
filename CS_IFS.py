from http.client import NETWORK_AUTHENTICATION_REQUIRED
from platform import mac_ver
from re import I, M
import pandas as pd
import csv
import math
import matplotlib.pyplot as plt
import numpy as np


# class này dùng để điều chỉnh phương thức đánh giá
class Evaluate(object):
    def __init__(self, truth_label, predicted_label, set_label, evaluation):
        self.truth = truth_label  # save the truth labels
        self.predict = predicted_label  # save the predicted labels
        self.setLabel = set_label  # save the set of labels
        self.numberOfLabel = len(self.setLabel)  # save the number of labels
        self.method = evaluation  # save the evaluation
        self.defuseMatrix = None  # save the the defuse matrix
        self.numberOfInstances = len(self.truth)  # save the number of instances
        self.TP = 0  # save the number of TP labels
        self.FP = 0  # save the number of FP labels
        self.FN = 0  # save the number of FN labels
        self.TN = 0  # save the number of TN labels (only for binary classification)
        self.maxLen = max(max([len(str(label)) for label in self.setLabel]), 7) + 5
        self.binary = False
        self.input = None
        self.all = 0

    def createDefuseMatrix(self):
        if len(self.setLabel) == 2:
            self.binary = True
        self.defuseMatrix = [[0 for col in range(self.numberOfLabel)] for row in range(self.numberOfLabel)]
        for i in range(self.numberOfInstances):
            k = self.setLabel.index(self.truth[i])
            j = self.setLabel.index(self.predict[i])
            if k == j:
                self.defuseMatrix[k][j] += 1
                if self.binary == True and k != 0:
                    self.TN += 1
                else:
                    self.TP += 1
            else:
                self.defuseMatrix[j][k] += 1
                if j < k:
                    self.FN += 1
                elif j > k:
                    self.FP += 1

    def getMatrix(self, matrix, isDefuseMatrix=False):
        # takeFloat = False
        # if isDefuseMatrix == False:
        #     takeFloat = True
        # print(" " * self.maxLen, end=" ")
        # for i in range(self.numberOfLabel):
        #     k = len(str(self.setLabel[i]))
        #     # print(self.setLabel[i], end=" " * (self.maxLen - k))
        # print()
        # for i in range(self.numberOfLabel):
        #     k = len(str(self.setLabel[i]))
        #     print(self.setLabel[i], end=" " * (self.maxLen - k + 1))
        #     for j in range(self.numberOfLabel):
        #         s = len(str("{:.3f}".format(matrix[i][j])))
        #         if takeFloat == False:
        #             print(matrix[i][j], end=" " * (self.maxLen - s))
        #         else:
        #             print("{:.3f}".format(matrix[i][j]), end=" " * (self.maxLen - s))
        #     print()
        return self.defuseMatrix

    def accuracy(self):
        if self.binary == True:
            return (self.TP + self.TN) / (self.numberOfInstances)
        return self.TP / self.numberOfInstances

    def sensitivity(self):
        return self.TP / (self.TP + self.FN)

    def specificity(self):
        return self.TN / (self.TN + self.FP)

    def precision(self):
        return self.TP / (self.TP + self.FP)

    def f1_score(self):
        return (2 * self.TP) / (self.TP * 2 + self.FP + self.FN)

    def Matthews_correlation_coef(self):
        nume = self.TP * self.TN + self.FP * self.FN
        deno = (self.TP + self.FP) * (self.TP + self.FN) * (self.TN + self.FP) * (self.TN + self.FN)
        return nume / (deno) ** (1 / 2)

    def Fowlkes_Mallows(self):
        if self.binary == True:
            return self.TP / ((self.TP + self.FP) * (self.TP + self.FN)) ** (1 / 2)
        result = [[0 for col in range(self.numberOfLabel)] for row in range(self.numberOfLabel)]
        for i in range(self.numberOfLabel):
            result[i][i] = 1
            for j in range(i + 1, self.numberOfLabel):
                TP = self.defuseMatrix[i][i] + self.defuseMatrix[j][j]
                FP = self.defuseMatrix[j][i]
                FN = self.defuseMatrix[i][j]
                res = TP / ((TP + FP) * (TP + FN)) ** (1 / 2)
                result[i][j] = res
                result[j][i] = res
        return result

    def getFowlkes_Mallows(self):
        res = self.Fowlkes_Mallows()
        self.getMatrix(res)

    def Run(self):
        self.createDefuseMatrix()
        method = self.method.lower().strip()
        result = 0
        if method == "accuracy":
            result = self.accuracy()
        elif method == "sensitivity":
            result = self.sensitivity()
        elif method == "specificity":
            result = self.specificity()
        elif method == "precision":
            result = self.precision()
        elif method == "f1_score":
            result = self.f1_score()
        elif method == "matthews_correlation_coef":
            result = self.Matthews_correlation_coef()
        return result

    def to_return_list(self):
        ret_list = [self.accuracy(), self.specificity(), self.sensitivity(), self.f1_score(), self.precision(),
                    self.Matthews_correlation_coef()]
        return ret_list


class CS_IFS(object):
    def __init__(self, filename):
        self.trainPath = "Train_" + filename  # save the name of the train set for process data in PreProcessing method
        self.testPath = "Test_" + filename  # save the name of the test set for predicting
        self.data = None  # save the data extract from the csv file by using pandas
        self.test = None  # save the data extract from the test set
        self.dataValue = None  # save the value of all cells in csv table
        self.testValue = None  # save the value of all cells in the test set
        self.dataHeader = None  # save the name of all columns in csv table
        self.numberOfHeader = None  # save the number of columns in csv file without the label columns
        self.numberOfLabel = None  # save the label of cases in csv table
        self.label = None  # save the name of labels
        self.labelValue = None  # save the label of all instances in csv table
        self.TlabelValue = None  # save the label of all instances in the test set
        self.predictLabel = None  # save the predict label of all instances in csv table by using cs_ifs method
        self.predictLabelT = None  # save the predict label of all instances in test set
        self.numberOfInstances = None  # save the number of instances in csv table
        self.numberOfTest = None  # save the number of instances in the test set
        self.weights = None  # save the weights of all features in the cs_ifs model
        self.result = None  # save the distance between the instances with each center in center list
        self.Tresult = None  # save the distance between the instances with each center in center list
        self.RelTableTrain = None  # save the result of IF function in the train set
        self.SurgenoTableTrain = None  # save the result of NON_IF function in the train set
        self.RelTableVal = None  # save the result of IF function in the validate set
        self.SurgenoTableVal = None  # save the result of NON_IF function in the validate set
        self.RelTableTest = None  # save the result of IF function in the test set
        self.SurgenoTableTest = None  # save the result of NON_IF function in the test set
        self.RelCenterTable = None  # save the result of IF function of center list
        self.SurgenoCenterTable = None  # save the result of NON_IF function of center list
        self.accuracy = 0  # save the accuracy of cs_ifs model with the csv file
        self.accuracyV = 0  # save the accuracy of cs_ifs model with the validation set
        self.accuracyT = 0  # save the accuracy of cs_ifs model with the test set
        self.time = 0  # save total time to updating the weights
        self.measure = "Default"  # save the measurement to evaluate the distance between 2 points in the csv file
        self.evaluation = "Accuracy"  # save the method to evaluate the result of cs-ifs model
        self.modelEvaluation = None
        self.TmodelEvaluation = None
        self.p = 1

    # Process the raw data to suitable data
    def PreProcessingCSV(self, isTrain=True):
        if isTrain == True:
            self.data = pd.read_csv(self.trainPath, delimiter=None)
            self.dataHeader = self.data.columns.values
            self.numberOfHeader = len(self.dataHeader.tolist()) - 1
            self.dataHeader = [self.dataHeader[idxHeader].strip() for idxHeader in range(self.numberOfHeader + 1)]
            self.label = list(set(self.data[self.dataHeader[self.numberOfHeader]].values.tolist()))
            self.numberOfLabel = len(self.label)
            self.dataValue = self.data[self.dataHeader[:self.numberOfHeader]].values.tolist()
            self.labelValue = self.data[self.dataHeader[self.numberOfHeader]].values.tolist()
            self.numberOfInstances = len(self.dataValue)
        else:
            self.test = pd.read_csv(self.testPath, delimiter=None)
            self.testValue = self.test[self.dataHeader[:self.numberOfHeader]].values.tolist()
            self.TlabelValue = self.test[self.dataHeader[self.numberOfHeader]].values.tolist()
            self.numberOfTest = len(self.testValue)

    # Create two table using two function below to use for the next steps
    def CreateFuzzyTable(self, isTrain=True):
        if isTrain == True:
            RelTable = [[0 for i in range(self.numberOfHeader)] for j in range(self.numberOfInstances)]
            SurgenoTable = [[0 for i in range(self.numberOfHeader)] for j in range(self.numberOfInstances)]
        else:
            RelTable = [[0 for i in range(self.numberOfHeader)] for j in range(self.numberOfTest)]
            SurgenoTable = [[0 for i in range(self.numberOfHeader)] for j in range(self.numberOfTest)]
        for columnName in self.dataHeader[:self.numberOfHeader]:
            self.RelFunction(columnName, RelTable, isTrain=isTrain)
            self.SurgenoFunction(columnName, SurgenoTable, RelTable, isTrain=isTrain)
        return RelTable, SurgenoTable

    # Step 1: Include 2 main method RelFunction and Surgeno Function which use for calculate the
    # reliability function and surgeno function based on 2 function
    # Reliability function: y[i, j] = (r[i, j] - min r[i, j]) / (max r[i, j] - min r[i, j]) (with j = 1, 2, ... m) (1)
    # Surgeno function:     n[i, j] = (1 - y[i, j]) / (1 + y[i, j]) (2)

    # Calculation Reliability function
    def RelFunction(self, columnName, RelTable, isCalCenter=False, centerValue=[[]], isTrain=True):
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

    # Calculation Surgeno fuction
    def SurgenoFunction(self, columnName, SurgenoTable, RelTable, isCalCenter=False, isTrain=True):
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

    def CalWeights(self, RelTable, SurgenoTable, criterion=10 ** (-4)):
        self.weights = [1 / self.numberOfHeader for i in range(self.numberOfHeader)]
        passCriterion = 0
        while passCriterion < self.numberOfHeader:
            passCriterion = 0
            newWeight = [0 for i in range(self.numberOfHeader)]
            componentT = [self.CalWeightsComponentT(idxColumn, RelTable, SurgenoTable) for idxColumn in
                          range(self.numberOfHeader)]
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
    # i = 1, 2, ..., m

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
        """Calculating the values of each features for all center points
        Returns:
            _list_: there are 2 tables as follow: membership and surgeno table which are corresponding
            as 2 main function that recommend above.
        """
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
            dictCenterLabel[eachLabel] = [dictCenterLabel[eachLabel][idx] / dictElementsLabel[eachLabel] \
                                          for idx in range(self.numberOfHeader)]
            centerValue.append(dictCenterLabel[eachLabel])
        for columnName in self.dataHeader[:self.numberOfHeader]:
            self.RelFunction(columnName=columnName, RelTable=RelCenterTable, isCalCenter=True, centerValue=centerValue)
            self.SurgenoFunction(columnName=columnName, SurgenoTable=SurgenoCenterTable, RelTable=RelCenterTable,
                                 isCalCenter=True)
        return RelCenterTable, SurgenoCenterTable

    # Calculation the distance between each instance and the labels in the label list
    def CalDistance(self, isTrain=True, measure="Default"):
        """This method will calculate the distance between a pair of points with different
            measurement like: Default, Hamming, Manhattan, Hamming3Funciton, Manhattan, Ngân, Mincowski
        Args:
            isTrain (bool, optional): check that this measurement use for training set or testing set. Defaults to True.
            measure (str, optional): You can choose one of measurement distance as above. Defaults to "Default".
            p (int, optional): the degree of Mincowski measurement. Defaults to 1.
        """
        self.measure = measure.lower().strip()
        if isTrain == True:
            length = self.numberOfInstances
        else:
            length = self.numberOfTest
        result = [[0 for idx in range(self.numberOfLabel)] for j in range(length)]
        if self.measure == "default":
            for idx in range(length):
                for idxLabel in range(self.numberOfLabel):
                    distance = 0
                    for idxCol in range(self.numberOfHeader):
                        if isTrain == True:
                            distance += self.weights[idxCol] * abs(
                                self.CalWeightsComponentS(self.RelTableTrain[idx][idxCol], \
                                                          self.SurgenoTableTrain[idx][
                                                              idxCol]) - self.CalWeightsComponentS(
                                    self.RelCenterTable[idxLabel][idxCol], \
                                    self.SurgenoCenterTable[idxLabel][idxCol]))
                        else:
                            distance += self.weights[idxCol] * abs(
                                self.CalWeightsComponentS(self.RelTableTest[idx][idxCol], \
                                                          self.SurgenoTableTest[idx][
                                                              idxCol]) - self.CalWeightsComponentS(
                                    self.RelCenterTable[idxLabel][idxCol], \
                                    self.SurgenoCenterTable[idxLabel][idxCol]))
                    result[idx][idxLabel] = distance
        elif self.measure == "hamming":
            for idx in range(length):
                for idxLabel in range(self.numberOfLabel):
                    distance = 0
                    for idxCol in range(self.numberOfHeader):
                        if isTrain == True:
                            distance += self.weights[idxCol] * (
                                        abs(self.RelTableTrain[idx][idxCol] - self.RelCenterTable[idxLabel][idxCol]) \
                                        + abs(self.SurgenoTableTrain[idx][idxCol] - self.SurgenoCenterTable[idxLabel][
                                    idxCol])) / 2
                        else:
                            distance += self.weights[idxCol] * (
                                        abs(self.RelTableTest[idx][idxCol] - self.RelCenterTable[idxLabel][idxCol]) \
                                        + abs(
                                    self.SurgenoTableTest[idx][idxCol] - self.SurgenoCenterTable[idxLabel][idxCol])) / 2
                    result[idx][idxLabel] = distance
        elif self.measure == "hamming3funtion":
            for idx in range(length):
                for idxLabel in range(self.numberOfLabel):
                    distance = 0
                    for idxCol in range(self.numberOfHeader):
                        if isTrain == True:
                            distance += self.weights[idxCol] * (
                                        abs(self.RelTableTrain[idx][idxCol] - self.RelCenterTable[idxLabel][idxCol]) \
                                        + abs(
                                    self.SurgenoTableTrain[idx][idxCol] - self.SurgenoCenterTable[idxLabel][idxCol]) + \
                                        abs(self.RelTableTrain[idx][idxCol] + self.SurgenoTableTrain[idx][idxCol] - \
                                            self.RelCenterTable[idxLabel][idxCol] - self.SurgenoCenterTable[idxLabel][
                                                idxCol])) / 2
                        else:
                            distance += self.weights[idxCol] * (
                                        abs(self.RelTableTest[idx][idxCol] - self.RelCenterTable[idxLabel][idxCol]) \
                                        + abs(
                                    self.SurgenoTableTest[idx][idxCol] - self.SurgenoCenterTable[idxLabel][idxCol]) \
                                        + abs(self.RelTableTest[idx][idxCol] + self.SurgenoTableTest[idx][idxCol] \
                                              - self.RelCenterTable[idxLabel][idxCol] -
                                              self.SurgenoCenterTable[idxLabel][idxCol])) / 2
                    result[idx][idxLabel] = distance
        elif self.measure == "manhanta":
            for idx in range(length):
                for idxLabel in range(self.numberOfLabel):
                    distance = 0
                    for idxCol in range(self.numberOfHeader):
                        if isTrain == True:
                            distance += self.weights[idxCol] * (
                                        abs(self.RelTableTrain[idx][idxCol] - self.RelCenterTable[idxLabel][idxCol]) \
                                        + abs(
                                    self.SurgenoTableTrain[idx][idxCol] - self.SurgenoCenterTable[idxLabel][idxCol])) / \
                                        (self.RelTableTrain[idx][idxCol] + self.SurgenoTableTrain[idx][idxCol] \
                                         + self.RelCenterTable[idxLabel][idxCol] + self.SurgenoCenterTable[idxLabel][
                                             idxCol])
                        else:
                            distance += self.weights[idxCol] * (
                                        abs(self.RelTableTest[idx][idxCol] - self.RelCenterTable[idxLabel][idxCol]) \
                                        + abs(
                                    self.SurgenoTableTest[idx][idxCol] - self.SurgenoCenterTable[idxLabel][idxCol])) / \
                                        (self.RelTableTest[idx][idxCol] + self.SurgenoTableTest[idx][idxCol] \
                                         + self.RelCenterTable[idxLabel][idxCol] + self.SurgenoCenterTable[idxLabel][
                                             idxCol])
                    result[idx][idxLabel] = distance
        elif self.measure == "ngân":
            for idx in range(length):
                for idxLabel in range(self.numberOfLabel):
                    distance = 0
                    for idxCol in range(self.numberOfHeader):
                        if isTrain == True:
                            distance += self.weights[idxCol] * (
                                        (abs(self.RelTableTrain[idx][idxCol] - self.RelCenterTable[idxLabel][idxCol]) \
                                         + abs(self.SurgenoTableTrain[idx][idxCol] - self.SurgenoCenterTable[idxLabel][
                                                    idxCol])) / 4 \
                                        + abs(
                                    max(self.RelTableTrain[idx][idxCol], self.SurgenoCenterTable[idxLabel][idxCol]) \
                                    - max(self.RelCenterTable[idxLabel][idxCol],
                                          self.SurgenoTableTrain[idx][idxCol])) / 2) / 3
                        else:
                            distance += self.weights[idxCol] * (
                                        (abs(self.RelTableTest[idx][idxCol] - self.RelCenterTable[idxLabel][idxCol]) \
                                         + abs(self.SurgenoTableTest[idx][idxCol] - self.SurgenoCenterTable[idxLabel][
                                                    idxCol])) / 4 \
                                        + abs(
                                    max(self.RelTableTest[idx][idxCol], self.SurgenoCenterTable[idxLabel][idxCol]) \
                                    - max(self.RelCenterTable[idxLabel][idxCol],
                                          self.SurgenoTableTest[idx][idxCol])) / 2) / 3
                    result[idx][idxLabel] = distance
        elif self.measure == "mincowski":
            for idx in range(length):
                for idxLabel in range(self.numberOfLabel):
                    distance = 0
                    for idxCol in range(self.numberOfHeader):
                        if isTrain == True:
                            VAdistance = abs(abs(self.CalWeightsComponentS(self.RelTableTrain[idx][idxCol], \
                                                                           self.SurgenoTableTrain[idx][
                                                                               idxCol]) - self.CalWeightsComponentS(
                                self.RelCenterTable[idxLabel][idxCol], \
                                self.SurgenoCenterTable[idxLabel][idxCol])))
                            distance += self.weights[idxCol] * (VAdistance ** self.p)
                        else:
                            VAdistance = abs(abs(self.CalWeightsComponentS(self.RelTableTest[idx][idxCol], \
                                                                           self.SurgenoTableTest[idx][
                                                                               idxCol]) - self.CalWeightsComponentS(
                                self.RelCenterTable[idxLabel][idxCol], \
                                self.SurgenoCenterTable[idxLabel][idxCol])))
                            distance += self.weights[idxCol] * (VAdistance ** self.p)
                    result[idx][idxLabel] = distance ** (1 / self.p)
        if isTrain == True:
            self.result = result
        else:
            self.Tresult = result

    # Classification the label of instances again
    def ClassificationLabel(self, isTrain=True):
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

    def EvaluationMethod(self, isTrain=True, evaluation="Accuracy"):
        self.evaluation = evaluation
        if isTrain == True:
            self.modelEvaluation = Evaluate(self.labelValue, self.predictLabel, self.label, self.evaluation)
            self.accuracy = self.modelEvaluation.Run()
        else:
            self.TmodelEvaluation = Evaluate(self.TlabelValue, self.predictLabelT, self.label, self.evaluation)
            self.accuracyT = self.TmodelEvaluation.Run()

    # khi người dùng ấn train thì chạy method này
    def fit(self, criterion=10 ** (-4), measure="Default", evaluation="accuracy", _p=1):
        self.p = _p
        self.PreProcessingCSV()
        self.RelTableTrain, self.SurgenoTableTrain = self.CreateFuzzyTable()
        self.CalWeights(self.RelTableTrain, self.SurgenoTableTrain, criterion=criterion)
        self.RelCenterTable, self.SurgenoCenterTable = self.CalClusterCenter()
        self.CalDistance(measure=measure)
        self.ClassificationLabel()
        self.EvaluationMethod(evaluation=evaluation)
        # print("The result of CS_IFS algorithm in the training set: ", "{:.4f}".format(self.accuracy))
        return self.accuracy

    def writeFile(self):
        return None

    # khi người dùng ấn test thì chạy method này
    def predict(self):
        self.PreProcessingCSV(isTrain=False)
        self.RelTableTest, self.SurgenoTableTest = self.CreateFuzzyTable(isTrain=False)
        self.CalDistance(isTrain=False, measure=self.measure)
        self.ClassificationLabel(isTrain=False)
        self.EvaluationMethod(isTrain=False, evaluation=self.evaluation)
        # print("The result of CS_IFS algorithm in the testing set: ", "{:.4f}".format(self.accuracyT))
        return self.accuracyT

    def getDefuseMatrix(self, isTrain=True):
        if isTrain == True:
            return self.modelEvaluation.getMatrix(matrix=self.modelEvaluation.defuseMatrix, isDefuseMatrix=True)
        else:
            return self.TmodelEvaluation.getMatrix(matrix=self.TmodelEvaluation.defuseMatrix, isDefuseMatrix=True)


# class naỳ chỉ để demo
class SpaceSearch(object):
    def __init__(self, model, _range):
        self.model = model
        self.range = _range

    def BestResutl(self):
        result = []
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


# lst = [0.0001]
# filename = "Train_KAHRAMAN.csv"
# model = CS_IFS(filename)
# model.fit(measure="mincowski", evaluation="f1_score", _p=2)
# model.getDefuseMatrix()
# model.predict()
# matrix = model.getDefuseMatrix()
# model.getDefuseMatrix(False)
# print(len(matrix))
