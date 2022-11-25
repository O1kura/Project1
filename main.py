# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import tkinter.font
from tkinter import *
from tkinter import filedialog, ttk
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

gui.columnconfigure(0, weight=4)
#gui.columnconfigure(1, weight=1)
gui.rowconfigure(1, weight=1)

####################################
# Frame de thuc hien import file data
topFrame = Frame(gui, background="#25FFE3")
topFrame.grid(row=0, column=0,
              columnspan=2,
              sticky=N+W+E)
topFrame.columnconfigure(1, weight=1)
topFrame.rowconfigure(0, weight=1)

# Mo file explorer
def importFileName():
    global data, filename
    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Select a File",
                                          filetypes=(("Data files",
                                                      ["*.xlsx","*.csv"]),
                                                     ("all files",
                                                      "*.*")))
    if filename[-5:] == ".xlsx":
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

# Tao menu cho chuot phai
table_menu = Menu(leftFrame,tearoff=0)
table_selected_col = ''
table_menu.add_command(label='Delete Column',
                       command=lambda: delete_col(table_selected_col))
# Hien thi menu (Xoa) o phan heading ma khong phai nhan
def popup(event):
    global table_selected_col

    region = table.identify_region(event.x,event.y)
    if region == 'heading':
        selected_col1 = table.identify_column(event.x)
        col1 = table.column(selected_col1).get('id')
        data_col = data.columns.tolist()

        if data_col[-1] != col1:
            try:
                table_menu.tk_popup(event.x_root,event.y_root)
                table_selected_col = col1
            finally:
                table_menu.grab_release()

# Thuc hien xoa
def delete_col(col1):
    data.drop(columns=col1, axis=1, inplace=True)
    createDataTableUI(data)

# Bind phan popup vao nut chuot trai
table.bind('<Button-3>', popup)

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
# Cac nut chuc nang
rightFrame = Frame(gui)
rightFrame.grid(row=1,column=1,sticky=S+E+N+W,padx=5,pady=5)

trainBtn = Button(rightFrame, text='Train', height=1, width=10, command = lambda:updateResult(data=data))
trainBtn.grid(row=1,column=0,padx = 5,pady = 5)


restoreBtn = Button(rightFrame, text='Restore', height=1, width=10, command = lambda: restore())
restoreBtn.grid(row=1,column=2,padx = 5,pady = 5)


restoreBtn = Button(rightFrame, text='Delete', height=1, width=10, command = lambda:delete())
restoreBtn.grid(row=1,column=1,padx = 5,pady = 5)

distance_label = Label(rightFrame,text='Measure:')
distance_label.grid(row=0,column=0,pady=5,padx=5)

# OptionMenu cho viec thay doi do do
distance_list = ['Euler distance','Hamming distance(2)','Hamming distance(3)','Ngan distance','Mahanta distance']
distance_method = StringVar(rightFrame)
distance_method.set('Euler distance')

distance_menu = OptionMenu(rightFrame,distance_method,*distance_list)
distance_menu.grid(row=0,column=1,pady=5,padx=5,columnspan=2,sticky=E+W)

# Cac label hien thi ket qua
resultLabel = Label(rightFrame,text='Result',width=20,anchor='center',borderwidth=1,relief='solid')
resultLabel.grid(row=2,column=0,columnspan=3,padx=5,pady=5,sticky=E+W)

numberLabel = Label(rightFrame,text='Data size: ',width=20,anchor=W)
numberLabel.grid(row=3,column=0,columnspan=3,padx=5,pady=5,sticky=E+W)

correctLabel = Label(rightFrame,text='Correct Prediction: ',width=20,anchor=W)
correctLabel.grid(row=4,column=0,columnspan=3,padx=5,pady=5,sticky=E+W)

accuracyLabel = Label(rightFrame,text='Accuracy: ',width=20,anchor=W)
accuracyLabel.grid(row=5,column=0,columnspan=3,padx=5,pady=5,sticky=E+W)

timeLabel = Label(rightFrame,text='Time executed: ',width=20,anchor=W)
timeLabel.grid(row=6,column=0,columnspan=3,padx=5,pady=5,sticky=E+W)

weightLabel = Label(rightFrame,text='Weight: ',width=20,anchor=W)
weightLabel.grid(row=7,column=0,columnspan=3,padx=5,pady=5,sticky=E+W)

weightLabel2 = Label(rightFrame,anchor=W)
weightLabel2.grid(row=8,column=0,columnspan=3,padx=5,pady=5,sticky=E+W+S)
# Cac chuc nang
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
        (str1,str2,str3,df,conclusion,time_str)=test.upload_file(data,distance_method.get())

        numberLabel.configure(text=str3)
        correctLabel.configure(text=str1)
        accuracyLabel.configure(text=str2)
        timeLabel.configure(text=time_str)

        string1 = df.to_string(index=True)
        weightLabel2.configure(text=string1)

        data = pandas.concat([data,pandas.Series(conclusion,name='Prediction')],axis=1)

        createDataTableUI(data,True)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    gui.mainloop()
