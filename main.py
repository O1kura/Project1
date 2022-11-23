# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from tkinter import *
from tkinter import filedialog,ttk
import pandas
import test

filename = ''
data = pandas.DataFrame
col = []

gui = Tk()

screen_width = gui.winfo_screenwidth()
screen_height = gui.winfo_screenheight()

gui.geometry("%dx%d+%d+%d" % (screen_width/2, screen_height/2, screen_width/4, screen_height/4))
gui.title('Project1GUI')
gui.configure(background="#A5A8EC")

gui.columnconfigure(0,weight=4)
gui.columnconfigure(1,weight=1)
gui.rowconfigure(1,weight=1)

####################################
# Frame de thuc hien import file data
topFrame = Frame(gui,background="#25FFE3")
topFrame.grid(row = 0,column=0,
              columnspan=2,
              sticky= N+W+E)
topFrame.columnconfigure(1,weight=1)
topFrame.rowconfigure(0,weight=1)

# Mo file explorer
def importFileName():
    global data, filename
    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Select a File",
                                          filetypes=(("Data files",
                                                      ["*.xlsx","*.csv"]),
                                                     ("all files",
                                                      "*.*")))
    if filename[-5:]==".xlsx":
        browseLabel.configure(text="File: " + filename)
        data = pandas.read_excel(filename)
        createDataTableUI(data)

    elif filename[-4:] == ".csv":
        browseLabel.configure(text="File: " + filename)
        data = pandas.read_csv(filename)
        createDataTableUI(data)
    else:
        browseLabel.configure(text="Not a correct data file")
# Nut import
browseBtn = Button(topFrame, text='Import', height=1, width=10, command=importFileName)
browseBtn.grid(column=0,
               row=0,
               padx=5,
               pady=5,
               sticky=W
               )
# Hien thi ten file da mo
browseLabel = Label(topFrame)
browseLabel.grid(column=1,
                 row=0,
                 #rowspan=2,
                 padx=5,
                 pady=5,
                 ipady=2,
                 ipadx=2,
                 sticky=W+E
                 )

##################################
# Frame de hien thi Du lieu dau vao
leftFrame = Frame(gui)
leftFrame.grid(row=1,
               column=0,
               padx=5,
               pady=5,
               sticky=N+S+W+E
               )
leftFrame.columnconfigure(0, weight=1)
leftFrame.rowconfigure(0, weight=1)

tableFrame = Frame(leftFrame)
tableFrame.grid(row=0,column=0,sticky='news')

table = ttk.Treeview(tableFrame,show='headings')
table.place(relx=0,rely=0,relheight=1,relwidth=1)
# Tao scrollbar
table_scroll = Scrollbar(leftFrame)
table_scroll.grid(row=0,column=1,sticky=N+S)

table_scroll1 = Scrollbar(leftFrame,orient="horizontal")
table_scroll1.grid(row=1,column=0,sticky=W+E)

table_scroll.config(command=table.yview)
table_scroll1.config(command=table.xview)

table.config(yscrollcommand=table_scroll.set,xscrollcommand=table_scroll1.set)

leftFrame.columnconfigure(0, weight=1)
leftFrame.rowconfigure(0, weight=1)
def delete_col(event):
    region = table.identify_region(event.x,event.y)
    if region == 'heading':
        selected_col = table.identify_column(event.x)
        col1 = table.column(selected_col).get('id')
        data_col = data.columns.tolist()

        if data_col[-1] != col1:
            data_col.remove(col1)
            data.drop(columns=col1,axis=1,inplace=True)
            createDataTableUI(data)

table.bind('<Button-3>',delete_col)
# Hien thi data
def createDataTableUI(data,trained = False):
    if data.empty:
        browseLabel.configure(text='Empty data')
    else:
        col = data.columns.tolist()

        for i in table.get_children():
            table.delete(i)

        table.config(columns=col)

        # Tao cot cua bang
        for i in range(len(col)):
            table.column(col[i],
                         minwidth=100,
                         width=100,
                         anchor='e')
            table.heading(col[i],text=col[i],anchor=CENTER)

        for row in data.itertuples(index= False):
            # Gan tag 'wrong' cho nhung dong sai sau khi ap dung thuat toan
            if trained and row[-1]!=row[-2]:
                table.insert(parent='',index='end',values=row,tags='wrong')
            else:
                table.insert(parent='',index='end',values=row)

        # Highlight dong co tag 'wrong'
        if trained:
            table.tag_configure('wrong',background='yellow')

#########################################
# Frame de hien thi ket qua cua thuat toan
rightFrame = Frame(gui)
rightFrame.grid(row=1,column=1,sticky=S+E+N+W,padx=5,pady=5)

trainBtn = Button(rightFrame, text='Train', height=1, width=10, command = lambda:updateResult(data=data))
trainBtn.grid(row=0,column=0,padx = 5,pady = 5)

restoreBtn = Button(rightFrame, text='Restore', height=1, width=10, command = lambda: restore())
restoreBtn.grid(row=0,column=1,padx = 5,pady = 5)

restoreBtn = Button(rightFrame, text='Delete', height=1, width=10, command = lambda:delete())
restoreBtn.grid(row=0,column=2,padx = 5,pady = 5)

resultLabel = Label(rightFrame,text='Result:',width=20,anchor=W)
resultLabel.place(x=10,y=50)

numberLabel = Label(rightFrame,text='Data size: ',width=20,anchor=W)
numberLabel.place(x=10,y=90)

correctLabel = Label(rightFrame,text='Correct Prediction: ',width=20,anchor=W)
correctLabel.place(x=10 ,y = 130)

accuracyLabel = Label(rightFrame,text='Accuracy: ',width=20,anchor=W)
accuracyLabel.place(x=10,y=170)

weightLabel = Label(rightFrame,text='Weight: ',width=20,anchor=W)
weightLabel.place(x=10,y=210)

weightLabel2 = Label(rightFrame,anchor=W)
weightLabel2.place(x=10,y=240)
# XOa item hay cot
def delete():
    if data.empty:
        browseLabel.configure(text='Empty data')
    else:
        # Dua ra gia tri cua item duoc xoa
        for item in table.selection():

            item_value = table.item(item)['values']

            col = data.columns.tolist()
            # So sanh tung gia tri mot cua tung cot thuoc tinh
            # de lay duoc index cua thuoc tinh can xoa
            index_def = data[data[col[0]]==float(item_value[0])].index
            for i in range(1,len(col)-1):
                index_def = set(index_def).intersection(
                    data[data[col[i]]==float(item_value[i])].index
                )
            # Xoa trong treeview
            table.delete(item)

            # Xoa trong data
            data.drop(index=index_def,inplace=True)
            data.reset_index(drop = True,inplace = True)

# Quay tro lai data ban dau
def restore():
    global data
    if filename[-5:] == ".xlsx":
        data = pandas.read_excel(filename)
        createDataTableUI(data)
    elif filename[-4:] == ".csv":
        data = pandas.read_csv(filename)
        createDataTableUI(data)
    else:
        browseLabel.configure(text="Not a correct data file")
    createDataTableUI(data)
# Hien thi ket qua
def updateResult(data):

    if data.empty:
        browseLabel.configure(text='Empty data')
    else:
        (str1,str2,str3,df,conclusion)=test.upload_file(data)

        numberLabel.configure(text=str3)
        correctLabel.configure(text=str1)
        accuracyLabel.configure(text=str2)

        string1 = df.to_string(index=True)
        weightLabel2.configure(text=string1)

        data = pandas.concat([data,pandas.Series(conclusion,name='Prediction')],axis=1)

        createDataTableUI(data,True)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    gui.mainloop()
