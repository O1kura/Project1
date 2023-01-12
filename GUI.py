import os
import time
import tkinter
import shutil
from tkinter import *
from tkinter import filedialog, ttk
import tkinterdnd2
from tkinterdnd2 import DND_FILES
import tkinter.scrolledtext as st
from pathlib import Path
import pandas
import Algorithm
import TrainAndTestSplitting

data = pandas.DataFrame
calculated_weight = pandas.Series
path_map = []
gui = tkinterdnd2.Tk()

screen_width = gui.winfo_screenwidth()
screen_height = gui.winfo_screenheight()

gui.geometry("%dx%d+%d+%d" % (screen_width * 2 / 3, screen_height / 2, screen_width / 6, screen_height / 4))
gui.title('Project1GUI')
gui.configure(background="#A5A8EC")

gui.columnconfigure(1, weight=1)
gui.rowconfigure(1, weight=1)


# Doc tat ca cac file csv, xlsx tu folder cua project
def read_folder():
    path = os.getcwd()
    os.chdir(path)
    for file_path in os.listdir():
        if file_path in ['w_train.csv', 'ket_qua.csv', 'DataTblop.csv']:
            continue
        if file_path.endswith(".xlsx") or file_path.endswith(".csv"):
            path_object = Path(file_path)
            file_name = path_object.name
            file_names_listbox.insert("end", file_name)
            path_map.append(file_name)


####################################
# Frame cho drag va drop + danh sach file
leftFrame = Frame(gui)
leftFrame.grid(row=1,
               column=0,
               padx=5,
               pady=5,
               sticky=N + S + W + E)


# Thuc hien keo tha vao frame
def drop_inside_list_box(event):
    file_paths = _parse_drop_files(event.data)
    current_listbox_items = set(file_names_listbox.get(0, "end"))
    for file_path in file_paths:
        if file_path.endswith(".xlsx") or file_path.endswith(".csv"):
            path_object = Path(file_path)
            file_name = path_object.name

            shutil.copy(path_object, file_name)

            if file_name not in current_listbox_items:
                file_names_listbox.insert("end", file_name)
                path_map.append(file_name)


# Hien thi file
def _display_file(event):
    global data
    if file_names_listbox.curselection() != ():
        file_name = file_names_listbox.get(file_names_listbox.curselection())
        if file_name.endswith(".xlsx"):
            browseLabel.configure(text="File: " + file_name)
            data = pandas.read_excel(file_name)
        elif file_name.endswith(".csv"):
            browseLabel.configure(text="File: " + file_name)
            data = pandas.read_csv(file_name)
        create_table(data)


# phan tich duong dan file
def _parse_drop_files(filename):
    size = len(filename)
    res = []  # list of file paths
    name = ""
    idx = 0
    while idx < size:
        if filename[idx] == "{":
            j = idx + 1
            while filename[j] != "}":
                name += filename[j]
                j += 1
            res.append(name)
            name = ""
            idx = j
        elif filename[idx] == " " and name != "":
            res.append(name)
            name = ""
        elif filename[idx] != " ":
            name += filename[idx]
        idx += 1
    if name != "":
        res.append(name)
    return res


file_names_listbox = Listbox(leftFrame, selectmode=SINGLE, relief='solid')
file_names_listbox.grid(row=1, sticky=N + E + S + W)
file_names_listbox.drop_target_register(DND_FILES)
file_names_listbox.dnd_bind("<<Drop>>", drop_inside_list_box)
file_names_listbox.bind("<Double-1>", _display_file)

label1 = Label(leftFrame, text='Files', width=20, anchor='w', background='#C0C0C0', borderwidth=1, relief='solid')
label1.grid(row=0, sticky=S + W + E)

leftFrame.rowconfigure(1, weight=1)
leftFrame.columnconfigure(0, weight=1)

###################################
# Frame de thuc hien import file data
topFrame = Frame(gui, background="#25FFE3")
topFrame.grid(row=0, column=0,
              columnspan=3,
              sticky=N + W + E)
topFrame.columnconfigure(1, weight=1)
topFrame.rowconfigure(0, weight=1)


# Mo file explorer
def import_to_gui(filepath,current_listbox_items):
    path_object = Path(filepath)
    file_name = path_object.name
    file_names_listbox.select_clear(0, 'end')

    shutil.copy(filepath, file_name)

    if file_name not in current_listbox_items:
        file_names_listbox.insert("end", file_name)
        file_names_listbox.selection_set('end')
        file_names_listbox.activate('end')
        path_map.append(file_name)
    else:
        index = list(path_map).index(file_name)
        file_names_listbox.selection_set(index)
        file_names_listbox.activate(index)
        file_names_listbox.see(index)
        file_names_listbox.selection_anchor(index)
    create_table(data)


def import_file():
    global data
    filepath = filedialog.askopenfilename(initialdir="/",
                                          title="Select a File",
                                          filetypes=(("Data files",
                                                      ["*.xlsx", "*.csv"]),
                                                     ("all files",
                                                      "*.*")))

    current_listbox_items = set(file_names_listbox.get(0, "end"))

    if filepath[-5:] == ".xlsx":
        browseLabel.configure(text="File: " + filepath)
        data = pandas.read_excel(filepath)

        import_to_gui(filepath, current_listbox_items)

    elif filepath[-4:] == ".csv":
        browseLabel.configure(text="File: " + filepath)
        data = pandas.read_csv(filepath)

        import_to_gui(filepath,current_listbox_items)
    else:
        browseLabel.configure(text="Not a correct data file")


# Nut import
browseBtn = Button(topFrame, text='Import', height=1, width=10, command=import_file)
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
                 padx=5,
                 pady=5,
                 ipady=2,
                 ipadx=2,
                 sticky=W + E
                 )

##################################
# Frame de hien thi Du lieu dau vao
MiddleFrame = Frame(gui)
MiddleFrame.grid(row=1,
                 column=1,
                 pady=5,
                 sticky=N + S + W + E
                 )
MiddleFrame.columnconfigure(0, weight=1)
MiddleFrame.rowconfigure(0, weight=1)

tableFrame = Frame(MiddleFrame)
tableFrame.grid(row=0, column=0, sticky='news')

table = ttk.Treeview(tableFrame, show='headings')
table.place(relx=0, rely=0, relheight=1, relwidth=1)

style = ttk.Style(MiddleFrame)
style.theme_use("clam")
style.configure("Treeview.Heading", background="#C0C0C0")

canvas_frame = Frame(MiddleFrame, height=150)
canvas_frame.grid(row=1, column=0, sticky=W+E)

canvas = Canvas(canvas_frame)

# Tao scrollbar
table_scroll = Scrollbar(MiddleFrame)
table_scroll.grid(row=0, column=1, sticky=N + S)

table_scroll1 = Scrollbar(MiddleFrame, orient="horizontal")
table_scroll1.grid(row=2, column=0, sticky=W + E)

table_scroll.config(command=table.yview)
table_scroll1.config(command=table.xview)

table.config(yscrollcommand=table_scroll.set, xscrollcommand=table_scroll1.set)

MiddleFrame.columnconfigure(0, weight=1)
MiddleFrame.rowconfigure(0, weight=1)

# Tao menu cho chuot phai
table_menu = Menu(MiddleFrame, tearoff=0)
table_selected_col = ''
table_menu.add_command(label='Delete Column',
                       command=lambda: delete_col(table_selected_col))


# Hien thi menu (Xoa) o phan heading ma khong phai nhan
def popup(event):
    global table_selected_col

    region = table.identify_region(event.x, event.y)
    if region == 'heading':
        selected_col1 = table.identify_column(event.x)
        col1 = table.column(selected_col1).get('id')
        data_col = data.columns.tolist()

        if data_col[-1] != col1:
            try:
                table_menu.tk_popup(event.x_root, event.y_root)
                table_selected_col = col1
            finally:
                table_menu.grab_release()


# Thuc hien xoa
def delete_col(col1):
    data.drop(columns=col1, axis=1, inplace=True)
    create_table(data)


# Bind phan popup vao nut chuot trai
table.bind('<Button-3>', popup)


# Hien thi data
def create_table(data1, trained=False):
    if data1.empty:
        browseLabel.configure(text='Empty data')
    else:
        col = data1.columns.tolist()

        for i in table.get_children():
            table.delete(i)

        table.config(columns=col)

        width = int(table.winfo_width()/len(col))
        width = max(width, 100)

        # Tao cot cua bang
        for i in range(len(col)):
            table.column(col[i],
                         minwidth=width,
                         width=width,
                         anchor='e')
            table.heading(col[i], text=col[i], anchor=CENTER)

        for row in data1.itertuples(index=False):
            # Gan tag 'wrong' cho nhung dong sai sau khi ap dung thuat toan
            if trained and row[-1] != row[-2]:
                table.insert(parent='', index='end', values=row, tags='wrong')
            else:
                table.insert(parent='', index='end', values=row)
        initial_detail(table)
        # Highlight dong co tag 'wrong'
        if trained:
            table.tag_configure('wrong', background='yellow')


def initial_detail(given_table):
    cols = data.columns.tolist()
    x_cor = 0

    for child in canvas_frame.winfo_children():
        child.destroy()

    for col in cols:
        width = given_table.column(col, 'width')
        inside_canvas = Canvas(canvas_frame, width=width, height=150)
        inside_canvas.place(x=x_cor, relheight=1)
        label = Label(inside_canvas, text=col, anchor='center', background="magenta")
        label.place(relx=0.1, relwidth=0.8, rely=0.1, relheight=0.8)
        x_cor = x_cor + width


#########################################
# Frame de hien thi ket qua cua thuat toan
# Cac nut chuc nang
rightFrame = Frame(gui)
rightFrame.grid(row=1, column=2, sticky=S + E + N + W, padx=5, pady=5)
rightFrame.rowconfigure(9, weight=1)

trainBtn = Button(rightFrame, text='Train', height=1, width=8, command=lambda: update_result(data1=data))
trainBtn.grid(row=1, column=0, padx=5, pady=5)

restoreBtn = Button(rightFrame, text='Restore', height=1, width=8, command=lambda: restore())
restoreBtn.grid(row=2, column=1, padx=5, pady=5)

del_Btn = Button(rightFrame, text='Delete', height=1, width=8, command=lambda: delete())
del_Btn.grid(row=2, column=0, padx=5, pady=5)

splitBtn = Button(rightFrame, text='Split', height=1, width=8, command=lambda: split())
splitBtn.grid(row=1, column=1, padx=5, pady=5)

test_btn = Button(rightFrame, text='Test', height=1, width=8,
                  command=lambda: update_result(data1=data, weight=True))
test_btn.grid(row=1, column=2, pady=5, padx=5)

detail_btn = Button(rightFrame, text='Details', height=1, width=8,
                    command=lambda: graph_detail())
detail_btn.grid(row=2, column=2, padx=5, pady=5)

distance_label = Label(rightFrame, text='Measure:')
distance_label.grid(row=0, column=0, pady=5, padx=5)

# OptionMenu cho viec thay doi do do
distance_list = ['Euler distance', 'Hamming distance(2)', 'Hamming distance(3)', 'Ngan distance', 'Mahanta distance']
distance_method = StringVar(rightFrame)
distance_method.set('Euler distance')

distance_menu = OptionMenu(rightFrame, distance_method, *distance_list)
distance_menu.grid(row=0, column=1, pady=5, padx=5, columnspan=2, sticky=E + W)
distance_menu.configure(width=18, anchor='w')

# Cac label hien thi ket qua
resultLabel = Label(rightFrame, text='Result', width=20, anchor='center', borderwidth=1, relief='solid')
resultLabel.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky=E + W)

numberLabel = Label(rightFrame, text='Data size: ', width=20, anchor=W)
numberLabel.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky=E + W)

correctLabel = Label(rightFrame, text='Correct Prediction: ', width=20, anchor=W)
correctLabel.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky=E + W)

accuracyLabel = Label(rightFrame, text='Accuracy: ', width=20, anchor=W)
accuracyLabel.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky=E + W)

timeLabel = Label(rightFrame, text='Time executed: ', width=20, anchor=W)
timeLabel.grid(row=7, column=0, columnspan=3, padx=5, pady=5, sticky=E + W)

weightLabel = Label(rightFrame, text='Weight: ', width=20, anchor=W)
weightLabel.grid(row=8, column=0, columnspan=3, padx=5, pady=5, sticky=E + W + N)

weightLabel1 = st.ScrolledText(rightFrame, width=20)
weightLabel1.grid(row=9, column=0, columnspan=3, padx=5, pady=5, sticky=E + W + N + S)


# Cac chuc nang
# XOa item
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

            def is_float(element: any):
                try:
                    float(element)
                    return float(element)
                except ValueError:
                    return element

            index_def = data[data[col[0]] == is_float(item_value[0])].index
            for i in range(1, len(col) - 1):
                index_def = set(index_def).intersection(
                    data[data[col[i]] == is_float(item_value[i])].index
                )
            # Xoa trong treeview
            table.delete(item)

            # Xoa trong data
            data.drop(index=index_def, inplace=True)
            data.reset_index(drop=True, inplace=True)


# Quay tro lai data ban dau
def restore():
    global data
    if file_names_listbox.curselection() != ():
        file_name = file_names_listbox.get(file_names_listbox.curselection())
        if file_name[-5:] == ".xlsx":
            data = pandas.read_excel(file_name)
            create_table(data)
        elif file_name[-4:] == ".csv":
            data = pandas.read_csv(file_name)
            create_table(data)


# Chia data thanh 2 set de train va test
def split():
    # Thuc hien chia data
    if file_names_listbox.curselection() != ():
        file_name = file_names_listbox.get(file_names_listbox.curselection())
        t = TrainAndTestSplitting.TrainAndTestSplitting(file_name)
        split_list = t.trainAndTestSplitting(train_size=0.8, test_size=0.2, method="stratified")
    # Them vao pathmap
    # Them vao file_names_listbox
        current_listbox_items = set(file_names_listbox.get(0, "end"))
        for file in split_list:
            if file not in current_listbox_items:
                path_map.append(file)
                file_names_listbox.insert(file_names_listbox.curselection()[0]+1, file)
        browseLabel.configure(text="Done splitting data")


# Hien thi chi tiet cac chi so
def graph_detail():
    # TODO
    # Tao popup window
    # Hien thi cac chi so can thiet
    return None


# Hien thi ket qua
def update_result(data1, weight=False):
    if data1.empty:
        browseLabel.configure(text='Empty data')
    else:
        global calculated_weight
        try:
            if weight:
                attribute = data1.columns.drop([data1.columns[len(data1.columns) - 1]])
                if not calculated_weight.empty and calculated_weight.index.equals(attribute):
                    start_time = time.time()
                    (str1, str2, str3, df, conclusion) = \
                        Algorithm.upload_file(data1, distance_method.get(), calculated_weight)
                    et = time.time()
                    calculated_weight = df
                    final_res = round((et - start_time) * 1000, 4)
                    numberLabel.configure(text=str3)
                    correctLabel.configure(text=str1)
                    accuracyLabel.configure(text=str2)
                    timeLabel.configure(text=('Time: ' + str(final_res) + ' ms'))

                    data1 = pandas.concat([data1, pandas.Series(conclusion, name='Prediction')], axis=1)
                    create_table(data1, True)

                    browseLabel.configure(text='Tested')
                else:
                    browseLabel.configure(text='Train model first')
            else:
                start_time = time.time()
                (str1, str2, str3, df, conclusion) = Algorithm.upload_file(data1, distance_method.get())
                et = time.time()
                calculated_weight = df
                final_res = round((et - start_time) * 1000, 4)
                numberLabel.configure(text=str3)
                correctLabel.configure(text=str1)
                accuracyLabel.configure(text=str2)
                timeLabel.configure(text=('Time: ' + str(final_res) + ' ms'))

                weightLabel1.configure(state='normal')
                weightLabel1.delete('1.0', tkinter.END)
                weight_str = df.to_string(index=True)
                weightLabel1.insert(tkinter.INSERT, weight_str)
                weightLabel1.configure(state='disabled')

                data1 = pandas.concat([data1, pandas.Series(conclusion, name='Prediction')], axis=1)
                create_table(data1, True)

                browseLabel.configure(text='Trained')

        except TypeError:
            browseLabel.configure(text='Value Error (Numeric only)')


def Run():
    read_folder()
    gui.mainloop()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    Run()
