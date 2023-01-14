import pandas as pd
import matplotlib.pyplot as plt


class EDA:
    def __init__(self, filename):
        self.filename = filename
        self.data = None
        self.dataheader = None
        self.numberOfHeader = None
        self.label = None
        self.numberOfLabel = None
        self.dataValue = None
        self.labelValue = None
        self.numberOfInstances = None
        self.dataDic = None

    def PreProcessing(self):
        self.data = pd.read_csv(self.filename, delimiter=None)
        self.dataHeader = self.data.columns.values
        self.numberOfHeader = len(self.dataHeader.tolist()) - 1
        self.dataHeader = [self.dataHeader[idxHeader].strip() for idxHeader in range(self.numberOfHeader + 1)]
        self.label = list(set(self.data[self.dataHeader[self.numberOfHeader]].values.tolist()))
        self.numberOfLabel = len(self.label)
        self.dataValue = self.data[self.dataHeader[:self.numberOfHeader]].values.tolist()
        self.labelValue = self.data[self.dataHeader[self.numberOfHeader]].values.tolist()
        self.numberOfInstances = len(self.dataValue)
        self.dataDic = [{} for i in range(self.numberOfHeader + 1)]
        self.idx = {1: "One", 2: "Two", 3: "Three", 4: 'Four', 5: 'Five', 6: 'Six', 7: 'Seven', 8: 'Eight', 9: "Nine"}

    def ReadyForBarPlot(self, colName):
        dataCol = self.data[colName].values
        k = self.dataHeader.index(colName)
        for _ins in range(self.numberOfInstances):
            if dataCol[_ins] not in self.dataDic[k]:
                self.dataDic[k][dataCol[_ins]] = 0
            self.dataDic[k][dataCol[_ins]] += 1
        courses = list(self.dataDic[k].keys())
        if k != self.numberOfHeader:
            courses.sort()
        newDic = {}
        for _course in courses:
            newDic[_course] = self.dataDic[k][_course]
        self.dataDic[k] = newDic

    def BarPlot(self, _keys, _values, colName, isLabel=False):
        if isLabel == False:
            # fig = plt.Figure(figsize=(10, 7))
            plt.bar(_keys, _values)
            # plt.xlabel(colName + " values")
            # plt.ylabel("Number of values")
            # plt.title("Bar plot of " + colName + " feature.")
            # plt.show()
        else:
            fig, ax = plt.subplots(figsize=(15, 8))
            ax.barh(_keys, _values)
            for s in ['top', 'bottom', 'left', 'right']:
                ax.spines[s].set_visible(False)
            ax.xaxis.set_ticks_position('none')
            ax.yaxis.set_ticks_position('none')
            ax.xaxis.set_tick_params(pad=5)
            ax.yaxis.set_tick_params(pad=10)
            ax.grid(b=True, color='grey',
                    linestyle='-.', linewidth=0.5,
                    alpha=0.2)
            ax.invert_yaxis()
            for i in ax.patches:
                plt.text(i.get_width() + 0.2, i.get_y() + 0.5,
                         str(round((i.get_width()), 2)),
                         fontsize=10, fontweight='bold',
                         color='grey')
            # ax.set_title('Classification label of ' + self.filename + " dataset.",
            #              loc='left', )
            fig.text(0.9, 0.15, 'Group2_P1', fontsize=12,
                     color='grey', ha='right', va='bottom',
                     alpha=0.7)
        # plt.show()

    def PieChart(self, _keys, _values, colName):
        s = sum(_values)
        for idx in range(len(_values)):
            _values[idx] = _values[idx] / s
        _explode = [0.2 for i in range(len(_values))]
        plt.pie(_values, labels=_keys, explode=_explode,
                autopct='%1.0f%%', shadow=True, startangle=90)
        plt.title("Classification label of " + self.filename + " dataset.")
        k = len(_values)
        if k < 10:
            k = self.idx[k]
        else:
            k = str(k)
        plt.legend(title=(k + " Labels: "), loc=0)
        # plt.show()

    def Tutorial(self):
        print("Name of colummns:")
        for k in range(self.numberOfHeader + 1):
            print(str(k + 1) + ". " + self.dataHeader[k])
        enter = int(input("Please enter the index:"))
        self.ReadyForBarPlot(self.dataHeader[enter - 1])
        des = self.data[self.dataHeader[enter - 1]].describe()
        print(des)
        count = des['count']
        mean = des['mean']
        std = des['std']
        min = des['min']
        max = des['max']
        print("_______________Statistical information______________")
        print("Count:", int(count))
        if enter != self.numberOfHeader + 1:
            print("Unique value:", self.data[self.dataHeader[enter - 1]].unique().size)
            print("Mean:", mean)
            print("Standard Deviation:", std)
            print("Min:", min)
            print("Max:", max)
        else:
            print("Number of label:", self.data[self.dataHeader[enter - 1]].unique().size)
        if ((min >= mean / 4) and (max <= mean * 4) and (enter != (self.numberOfHeader + 1))):
            self.BarPlot(self.dataDic[enter - 1].keys(), self.dataDic[enter - 1].values(), self.dataHeader[enter - 1])
        if (enter == self.numberOfHeader + 1):
            labelList = []
            for key in self.dataDic[enter - 1]:
                if int(key) == key:
                    labelList.append("Label " + str(key))
                else:
                    labelList.append(str(key))
            print("___________Type chart of classification label___________")
            print("1. Pie chart")
            print("2. Bar Chart")
            type_chart = int(input("Please enter your index: "))
            if type_chart == 2:
                self.BarPlot(labelList, list(self.dataDic[enter - 1].values()), "Label", isLabel=True)
            else:
                self.PieChart(labelList, list(self.dataDic[enter - 1].values()), "Label")

    def Using(self, enter):
        plt.close("all")
        enter = enter + 1
        self.ReadyForBarPlot(self.dataHeader[enter - 1])
        des = self.data[self.dataHeader[enter - 1]].describe()
        print(des)
        if enter != self.numberOfHeader + 1:
            mean = des['mean']
            min = des['min']
            max = des['max']
            if ((min >= mean / 4) and (max <= mean * 4) and (enter != (self.numberOfHeader + 1))):
                self.BarPlot(self.dataDic[enter - 1].keys(), self.dataDic[enter - 1].values(),
                             self.dataHeader[enter - 1])
        if (enter == self.numberOfHeader + 1):
            labelList = []

            def is_int(element: any):
                try:
                    int(element)
                    return int(element)
                except ValueError:
                    return element

            for key in self.dataDic[enter - 1]:
                if is_int(key):
                    labelList.append("Label " + str(key))
                else:
                    labelList.append(str(key))
            self.BarPlot(labelList, list(self.dataDic[enter - 1].values()), "Label", isLabel=True)

        return plt.gcf()
# filename = "Train_KAHRAMAN.csv"
# eda = EDA(filename)
# eda.PreProcessing()
# # for i in range(6):
# #     eda.Using(i)
# while(1):
#     eda.Tutorial()
