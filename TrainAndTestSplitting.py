import pandas as pd
import numpy as np
import csv
import math
import random as rand


class TrainAndTestSplitting(object):

    def __init__(self, filename):
        self.filename = filename  # save the filename of the csv file
        self.data = None  # save the data of whole csv file
        self.dataTrainPos = []  # save the position of data train in the csv file
        self.dataTrain = []  # save the data training of the csv file
        self.dataValidatePos = []  # save the data validating of the csv file
        self.dataValidate = []  # save the data validation of the csv file
        self.dataTestingPos = []  # save the data testing of the csv file
        self.dataTest = []  # save the data testing of the csv file
        self.numberOfInstances = 0  # save the number of instances in whole csv file
        self.numberOfTrain = 0  # save the number of instances in the training set
        self.numberOfValidate = 0  # save the number of instances in the validation set
        self.numberOfTest = 0  # save the number of instances in the testing set
        self.train_size = 0  # save the percentage of training set in the csv file
        self.validate_size = 0  # save the percentage of validation set in the csv file
        self.test_size = 0  # save the percentage of testing set in the csv file
        self.dataHeader = None  # save the name of all columns in the csv file
        self.label = None  # save the name of all labels in the csv file
        self.numberOfLabel = 0  # save the number of labels in the label list
        self.position = {}  # save the position of all label in the labels list
        self.method = ""  # save the method to splitting the data

    def readCSV(self):
        self.data = pd.read_csv(self.filename)
        self.dataHeader = self.data.columns.values
        self.numberOfHeader = len(self.dataHeader.tolist()) - 1
        self.dataHeader = [self.dataHeader[idxHeader].strip() for idxHeader in range(self.numberOfHeader + 1)]
        self.label = list(set(self.data[self.dataHeader[self.numberOfHeader]].values.tolist()))
        self.numberOfLabel = len(self.label)
        self.dataValue = self.data[self.dataHeader[:self.numberOfHeader + 1]].values.tolist()
        self.labelValue = self.data[self.dataHeader[self.numberOfHeader]].values.tolist()
        self.numberOfInstances = len(self.dataValue)

    # this function will divide the initially csv file into 2 csv files: Train and Test or 3 csv files: Train, Validate and Test
    def writeCSV(self, type="all"):
        headName = []
        writeData = []
        ret_list = []
        if type.strip().lower() == "train":
            headName.append("Train_")
            writeData.append(self.dataTrain)
        elif type.strip().lower() == "validate":
            headName.append("Validate_")
            writeData.append(self.dataValidate)
        elif type.strip().lower() == "test":
            headName.append("Test_")
            writeData.append(self.dataTest)
        else:
            headName = ["Train_", "Validate_", "Test_"]
            writeData = [self.dataTrain, self.dataValidate, self.dataTest]
        for idx in range(len(headName)):
            filename = headName[idx] + self.filename
            if self.validate_size == 0 and headName == "Validate_":
                continue
            ret_list.append(filename)
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.dataHeader)
                writer.writerows(writeData[idx])
        return ret_list

    def trainAndTestSplitting(self, train_size=0.7, validate_size=0, test_size=0.3, method="Random"):
        self.readCSV()
        if (train_size + test_size + validate_size > 1):
            return "ERROR: Train set and test size are too big!!!"
        self.train_size = train_size
        self.validate_size = validate_size
        self.test_size = test_size
        self.numberOfTrain = int(train_size * self.numberOfInstances)
        self.numberOfValidate = int(validate_size * self.numberOfInstances)
        self.numberOfTest = self.numberOfInstances - self.numberOfTrain - self.numberOfValidate
        self.countData()
        self.method = method
        if self.method.strip().lower() == "random":
            self.RandomSplitting()
        elif self.method.strip().lower() == "stratified":
            self.StratifiedSplitting()
        else:
            self.RandomSplitting()
        ret_list = self.writeCSV()
        return ret_list

    def countData(self):
        for label in self.label:
            self.position[label] = [[], 0]
        for idx in range(self.numberOfInstances):
            label = self.labelValue[idx]
            self.position[label][0].append(idx)
            self.position[label][1] += 1

    def RandomSplitting(self):
        shuffleList = [i for i in range(0, self.numberOfInstances)]
        rand.shuffle(shuffleList)
        for idxTrain in range(self.numberOfTrain):
            self.dataTrain.append(self.dataValue[shuffleList[idxTrain]])
        for idxValidate in range(self.numberOfValidate):
            self.dataValidate.append(self.dataValue[shuffleList[idxValidate + self.numberOfTrain]])
        for idxTest in range(self.numberOfTest):
            self.dataTest.append(self.dataValue[shuffleList[self.numberOfTrain + self.numberOfValidate + idxTest]])

    def StratifiedSplitting(self):
        for label in self.label:
            self.position[label][1] /= self.numberOfInstances
            rand.shuffle(self.position[label][0])
            k = int(self.numberOfTrain * self.position[label][1])
            self.dataTrainPos.extend(self.position[label][0][: k])
            self.dataValidatePos.extend(self.position[label][0][k: k + self.numberOfValidate])
            self.dataTestingPos.extend(self.position[label][0][k + self.numberOfValidate:])
        for idxTrain in self.dataTrainPos:
            self.dataTrain.append(self.dataValue[idxTrain])
        for idxValidate in self.dataValidatePos:
            self.dataValidate.append(self.dataValue[idxValidate])
        for idxTest in self.dataTestingPos:
            self.dataTest.append(self.dataValue[idxTest])


# t = TrainAndTestSplitting('BreastCancerWisconsin.csv')
# t.trainAndTestSplitting(train_size=0.8, test_size=0.2, method="stratified")
