import time
import pandas as pd
import numpy as np
from pandas.core.arrays import ExtensionArray


def upload_file(dfData,method):
    # tao File Dai Dien Lop
    st = time.time()
    listColumns = dfData.columns.to_list()

    dfDataTB = pd.DataFrame()

    averageSeriesAttr = []

    for j in range(len(listColumns)):
        averageSeriesAttr.append([])

    columnsLabelName = listColumns[len(listColumns) - 1]

    listLabel = dfData[columnsLabelName].unique().tolist()

    for i in range(len(listLabel)):
        for j in range(len(listColumns)):
            label = listLabel[i]
            if j == len(listColumns) - 1:
                averageSeriesAttr[j].append(label)
            else:
                averageSeriesAttr[j].append(
                    round(dfData.loc[dfData[columnsLabelName].eq(label), listColumns[j]].mean(), 3))
    for j in range(len(listColumns)):
        seri = pd.Series(averageSeriesAttr[j])
        dfDataTB = pd.concat([dfDataTB, seri], axis=1)
    dfDataTB.columns = listColumns
    print(dfDataTB)
    dfDataTB.to_csv('DataTblop.csv', index=False)

    # ket thuc tao FIle dai dien lop va ghi ra taoFileDaiDienLop.csv

    # bài toán mahanta

    attribute = dfData.columns.drop([dfData.columns[len(dfData.columns) - 1]])
    df = dfData[attribute]

    # Mờ hóa dữ liệu: chuyển aij
    # thành (yij , nij) (if, non_if)
    df_min = df.min(axis=0)
    df_max_min = (df.max(axis=0) - df.min(axis=0))
    print('ham thuoc:')
    IF_mem = round(((df - df_min) / df_max_min), 4)
    print(IF_mem)
    print('ham khong thuoc thuoc:')
    IF_non_mem = round((1 - IF_mem) / (1 + IF_mem), 4)
    print(IF_non_mem)
    # Tinh Sa (S(y,n))
    print('Caculat Score Syn:')
    Syn = round((3 + 2 * IF_mem + IF_mem * IF_mem - IF_non_mem - 2 * IF_non_mem *
                 IF_non_mem) * np.exp(2 * IF_mem - 2 * IF_non_mem - 2) / 6, 4)
    print(Syn)
    # Tinh Sca (S(n,y))
    print('Caculat Score Sny:')
    Sny = round((3 + 2 * IF_non_mem + IF_non_mem * IF_non_mem - IF_mem - 2 *
                 IF_mem * IF_mem) * np.exp(2 * IF_non_mem - 2 * IF_mem - 2) / 6, 4)
    print(Sny)
    # Tính matran khoảng cách các phần tử giữa A và A^C duncg cho tính weigh classification
    dt = np.abs(Syn - Sny)
    print(dt)

    # Weight ban đầu cho bài toán phân lớp
    w = []
    print('Tinh weigt:')
    for i in range(len(attribute)):
        w.append(1 / (len(attribute)))
    w0 = w

    # Tính weitgh có đk dừng dùng cho bài toán classification (dừng khi weight ko đổi)
    dw = dt * w0
    d1 = dw.sum(axis=0) / (len(dt))

    print(d1)
    w1 = round(d1 / d1.sum(axis=0), 4)
    tw = w1 - w
    tw1 = abs(tw.min(axis=0))
    while tw1 != 0:
        d = dt * w1
        d1 = d.sum(axis=0) / (len(dt))
        w1 = round(d1 / d1.sum(axis=0), 4)
        tw = w1 - w
        w = w1
        tw1 = abs(tw.min(axis=0))

    # Chạy dữ liệu train mới
    print("w* :")
    print(w)

    w_train: ExtensionArray = pd.Series(w, name="w_train").array
    w_trainToCsv = pd.DataFrame()
    w_trainToCsv = pd.concat([w_trainToCsv, pd.Series(w, name="w_train")], axis=1)
    w_trainToCsv.to_csv('w_train.csv', index=False)

    # Quá trình phân lớp
    # Mờ hóa các tâm
    dfDataTBvalue = dfDataTB[attribute]
    print('ham thuoc:')
    IF_tesT = round((dfDataTBvalue - df_min) / df_max_min, 4)
    print(IF_tesT)
    print('ham khong thuoc thuoc:')
    IF_non_Test = round((1 - IF_tesT) / (1 + IF_tesT), 4)
    print(IF_non_Test)
    T_test = round((3 + 2 * IF_tesT + IF_tesT * IF_tesT - IF_non_Test - 2 *
                    IF_non_Test * IF_non_Test) * np.exp(2 * IF_tesT - 2 * IF_non_Test - 2) / 6, 4)  # Syn Class

    print("T_test: ")
    print(T_test)

    lbl = dfDataTB[dfDataTB.columns[len(dfData.columns) - 1]].unique().tolist()  # List chứa tên các lớp

    # Tính khoảng cách từ mỗi đối tượng đến tâm của các lớp

    ghep = pd.DataFrame()  # DataFrame chứa khoảng cách từ mỗi đối tượng đến các lớp và kết luận đối tượng đó thuộc lớp nào
    for i in range(0, len(T_test)):
        # Tính khoảng cách đến lớp
        if method == 'Hamming distance(2)':
            ti1 = IF_tesT.loc[i]
            ti2 = IF_non_Test.loc[i]
            di = w_train * (abs(IF_mem - ti1)+abs(IF_non_mem - ti2))/2
        elif method == 'Mahanta distance':
            ti1 = IF_tesT.loc[i]
            ti2 = IF_non_Test.loc[i]
            di = w_train * ((abs(IF_mem - ti1)+abs(IF_non_mem - ti2))/(IF_mem + ti1 + IF_non_mem + ti2))
        elif method == 'Hamming distance(3)':
            ti1 = IF_tesT.loc[i]
            ti2 = IF_non_Test.loc[i]
            di = w_train * (abs(IF_mem - ti1) + abs(IF_non_mem - ti2) + abs(IF_non_mem + IF_mem - ti1 - ti2)) / 2
        elif method == 'Ngan distance':
            ti1 = IF_tesT.loc[i]
            ti2 = IF_non_Test.loc[i]

            def maxRow(data,series):
                for att in attribute:
                    data.loc[data[att]<series[att],att]=series[att]
                return data

            dd1 = (abs(IF_mem - ti1)+abs(IF_non_mem - ti2))/4
            dd2 = abs(maxRow(IF_mem,ti2) - maxRow(IF_non_mem,ti1))/2
            di = w_train * (dd1+dd2)/3
        else:
            ti = T_test.loc[i]
            di = w_train * abs(Syn - ti)
        d_i = di.sum(axis=1)
        d_i = pd.Series(d_i, name=lbl[i])

        ghep = pd.concat([ghep, d_i], axis=1)

    # Mảng Chỉ số của kết quả phân lớp

    index_ghep = np.argmin(np.asarray(ghep.loc[:]), axis=1)

    # Mảng chứa các kết luận về lớp giữa các đối tượng sau khi được tính toán
    conclusion = []

    for i in range(0, len(index_ghep)):
        conclusion.append(lbl[index_ghep[i]])

    ghep = pd.concat([ghep, pd.Series(conclusion, name="Ket Luan")], axis=1)
    ghep = ghep.round(decimals=3)

    et = time.time()
    final_res = round((et-st)*1000,4)

    ghep.to_csv('ket_qua.csv', index=False)
    d_Class = dfData[dfData.columns[len(dfData.columns) - 1]]
    index_Class = []
    index_d_Class = np.asarray(d_Class)

    for i in index_d_Class:
        index_Class.append(lbl.index(i))

    dem = 0
    test_value = []

    for k in range(len(index_Class)):
        if index_Class[k] == index_ghep[k]:
            dem = dem + 1
            test_value.append(1)
        else:
            test_value.append(0)

    chinhxac = round(dem / len(d_Class), 2) * 100
    string2 = 'Correct Prediction : ' + str(dem)
    string3 = 'Accuracy : ' + str(chinhxac) + '%'
    string1 = 'Size of data : ' + str(len(dfData))
    string4 = 'Time: '+ str(final_res) + ' milliseconds'

    return (string2,string3,string1,w,conclusion,string4)
