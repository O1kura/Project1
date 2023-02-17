import os
import time
import tkinter
import shutil
from tkinter import *
from tkinter import filedialog, ttk
import tkinterdnd2
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinterdnd2 import DND_FILES
import tkinter.scrolledtext as st
from pathlib import Path
import pandas
import Algorithm
import CS_IFS
import EDA
import TrainAndTestSplitting

# Cac bien toan cuc
save_location = "Result/"   # Duong dan luu ket qua
data = pandas.DataFrame     # Data chinh de xu ly trong gui
path_map = []               # Danh sach cac duong dan cua file du lieu trong folder hoac duoc them vao
gui = tkinterdnd2.Tk()      # GUI
current_file_name = ''      # Ten file se duoc su dung
fig_list = []               # Danh sach cac figure sau khi su dung eda

screen_width = gui.winfo_screenwidth()
screen_height = gui.winfo_screenheight()

gui.geometry("%dx%d+%d+%d" % (screen_width * 3 / 4, screen_height *3 / 4, screen_width / 8, screen_height / 8))
# gui.geometry("%dx%d+%d+%d" % (screen_width, screen_height, 0, 0))
# gui.state("zoomed")
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
    global data, current_file_name
    if file_names_listbox.curselection() != ():
        file_name = file_names_listbox.get(file_names_listbox.curselection())
        if current_file_name != file_name:
            current_file_name = file_name
            if file_name.endswith(".xlsx"):
                data = pandas.read_excel(file_name)
            elif file_name.endswith(".csv"):
                data = pandas.read_csv(file_name)
            reset_gui()
            draw(current_file_name, data)


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


# Them vao gui
def import_to_gui(filepath, current_listbox_items):
    global current_file_name
    path_object = Path(filepath)
    file_name = path_object.name
    file_names_listbox.select_clear(0, 'end')

    shutil.copy(filepath, file_name)
    current_file_name = file_name
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

    # Reset va ve gui
    reset_gui()
    draw(current_file_name, data)


# Mo file explorer
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

        import_to_gui(filepath, current_listbox_items)
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

outer_canvas = Canvas(MiddleFrame, height=200)
canvas_frame = Frame(outer_canvas)
canvas_frame.grid(sticky='news')


# Cho horizontal scrollbar (table_scroll1)
def multiview(*args):
    table.xview(*args)
    outer_canvas.xview(*args)


# Tao scrollbar
table_scroll = Scrollbar(MiddleFrame)
table_scroll.grid(row=0, column=1, sticky=N + S)

table_scroll1 = Scrollbar(MiddleFrame, orient="horizontal")
outer_canvas.configure(xscrollcommand=table_scroll1.set)
table_scroll1.grid(row=2, column=0, sticky=W + E)


# Scroll tren canvas trong frame
def scroll_func(event):
    outer_canvas.configure(scrollregion=outer_canvas.bbox("all"))


outer_canvas.grid(row=1, column=0, sticky=W + E)
outer_canvas.create_window((0, 0), window=canvas_frame, anchor='nw')
canvas_frame.bind("<Configure>", scroll_func)

table_scroll.config(command=table.yview)
table_scroll1.config(command=multiview)

table.config(yscrollcommand=table_scroll.set, xscrollcommand=table_scroll1.set)


# Tao menu cho chuot phai
# table_menu = Menu(MiddleFrame, tearoff=0)
# table_selected_col = ''
# table_menu.add_command(label='Delete Column',
#                        command=lambda: delete_col(table_selected_col))
#
#
# # Hien thi menu (Xoa) o phan heading ma khong phai nhan
# def popup(event):
#     global table_selected_col
#
#     region = table.identify_region(event.x, event.y)
#     if region == 'heading':
#         selected_col1 = table.identify_column(event.x)
#         col1 = table.column(selected_col1).get('id')
#         data_col = data.columns.tolist()
#
#         if data_col[-1] != col1:
#             try:
#                 table_menu.tk_popup(event.x_root, event.y_root)
#                 table_selected_col = col1
#             finally:
#                 table_menu.grab_release()
#
#
# # Thuc hien xoa
# def delete_col(col1):
#     data.drop(columns=col1, axis=1, inplace=True)
#     create_table(data)
#
#
# # Bind phan popup vao nut chuot trai
# table.bind('<Button-3>', popup)


# Hien thi data
def create_table(data1, trained=False):
    if data1.empty:
        browseLabel.configure(text='Empty data')
    else:
        string3 = 'Size of data : ' + str(len(data1))
        numberLabel.configure(text=string3)

        col = data1.columns.tolist()

        for i in table.get_children():
            table.delete(i)

        table.config(columns=col)

        width = int(table.winfo_width() / len(col))
        width = max(width, 200)

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
        # Highlight dong co tag 'wrong'
        if trained:
            table.tag_configure('wrong', background='yellow')


# Danh sach canvas hien thi do thi trong main gui
canvas_list = []


# Ham tra lai cua event click chuot trong canvas
def call(event):
    for i in range(len(canvas_list)):
        if event.widget == canvas_list[i].get_tk_widget():
            if len(toplevel_in_use) == 1:
                toplevel_in_use[0].destroy()
                toplevel_in_use.pop()
            if fig_list[i].get_axes():
                top = Toplevel(gui)
                top.title("Graph")
                toplevel_in_use.append(top)
                canvas = FigureCanvasTkAgg(fig_list[i], top)
                width = screen_width/3
                canvas.get_tk_widget().configure(height=width, width=width)
                canvas.get_tk_widget().pack()


outer_canvas.bind("<Button-1>", call, "")


# Hien thi cac do thi ra trong cac canvas con khac nhau
def initial_detail():
    cols = data.columns.tolist()

    for child in canvas_frame.winfo_children():
        child.destroy()

    for i in range(len(cols)):
        width = table.column(cols[i], 'width')

        inside_canvas = FigureCanvasTkAgg(fig_list[i], canvas_frame)
        inside_canvas.new_manager(fig_list[i], 0)
        inside_canvas.draw_idle()
        inside_canvas.get_tk_widget().grid(column=i, row=0, sticky=N + W + E + S)
        inside_canvas.get_tk_widget().configure(height=200, width=width)
        canvas_list.append(inside_canvas)

        bindtags = list(inside_canvas.get_tk_widget().bindtags())
        bindtags.insert(1, outer_canvas)
        inside_canvas.get_tk_widget().bindtags(tuple(bindtags))


# Ve ra gui
def draw(file_name, data2):
    browseLabel.configure(text="Loading...")
    browseLabel.update_idletasks()
    if data.empty:
        browseLabel.configure(text='Empty data')
    else:
        # Goi ham eda
        eda_gui = EDA.EDA(file_name)
        eda_gui.PreProcessing()

        cols = data.columns.tolist()

        # Luu cac figure duoc tao ra vao fig_list
        for i in range(len(cols)):
            fig = eda_gui.Using(i)
            fig_list.insert(i, fig)

        create_table(data2)
        initial_detail()
        browseLabel.configure(text="File: " + file_name)


#########################################
# Frame de hien thi ket qua cua thuat toan
# Cac nut chuc nang
rightFrame = Frame(gui)
rightFrame.grid(row=1, column=2, sticky=S + E + N + W, padx=5, pady=5)
rightFrame.rowconfigure(15, weight=1)

trainBtn = Button(rightFrame, text='Train', height=1, width=8, command=lambda: train_nhom2(data1=data))
trainBtn.grid(row=2, column=0, padx=5, pady=5)

# restoreBtn = Button(rightFrame, text='Group 1', height=1, width=8, command=lambda: train_nhom1(data1=data))
# restoreBtn.grid(row=3, column=1, padx=5, pady=5)
#
# del_Btn = Button(rightFrame, text='', height=1, width=8)  # , command=lambda: delete())
# del_Btn.grid(row=3, column=0, padx=5, pady=5)

splitBtn = Button(rightFrame, text='Split', height=1, width=8, command=lambda: split())
splitBtn.grid(row=2, column=1, padx=5, pady=5)

test_btn = Button(rightFrame, text='Test', height=1, width=8,
                  command=lambda: train_nhom2(data1=data, test=True))
test_btn.grid(row=2, column=2, pady=5, padx=5)

# detail_btn = Button(rightFrame, text='Def matrix', height=1, width=8,
#                     command=lambda: graph_detail())
# detail_btn.grid(row=3, column=2, padx=5, pady=5)

distance_label = Label(rightFrame, text='Measure:')
distance_label.grid(row=0, column=0, pady=5, padx=5)

eval_label = Label(rightFrame, text='Evaluation:')
eval_label.grid(row=1, column=0, pady=5, padx=5)

# OptionMenu cho viec thay doi do do
distance_list = ['Default', 'Hamming', 'Hamming 3 function', 'Ngân', 'Manhanta', 'Mincowski']
distance_method = StringVar(rightFrame)
distance_method.set('default')

distance_menu = OptionMenu(rightFrame, distance_method, *distance_list)
distance_menu.grid(row=0, column=1, pady=5, padx=5, columnspan=2, sticky=E + W)
distance_menu.configure(width=18, anchor='w')

# OptionMenu cho viec thay doi cach danh gia
eval_list = ['accuracy', 'specificity', 'sensitivity', 'f1_score', 'precision', 'matthews_correlation_coef']
eval_method = StringVar(rightFrame)
eval_method.set('accuracy')

eval_menu = OptionMenu(rightFrame, eval_method, *eval_list)
eval_menu.grid(row=1, column=1, pady=5, padx=5, columnspan=2, sticky=E + W)
eval_menu.configure(width=18, anchor='w')

# Cac label hien thi ket qua
resultLabel = Button(rightFrame, text='Export Result', width=20, anchor='center', command=lambda: export_result())
resultLabel.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky=E + W)

matrixBtn = Button(rightFrame, text='Defuse Matrix', width=20, anchor='center', state='disabled',
                   command=lambda: create_toplevel())
matrixBtn.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky=E + W)

numberLabel = Label(rightFrame, text='Data size: ', width=20, anchor=W)
numberLabel.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky=E + W)

specLabel = Label(rightFrame, text='Specificity: ', width=20, anchor=W)
specLabel.grid(row=8, column=0, columnspan=3, padx=5, pady=5, sticky=E + W)

f1Label = Label(rightFrame, text='F1_score: ', width=20, anchor=W)
f1Label.grid(row=10, column=0, columnspan=3, padx=5, pady=5, sticky=E + W)

precLabel = Label(rightFrame, text='Precision: ', width=20, anchor=W)
precLabel.grid(row=11, column=0, columnspan=3, padx=5, pady=5, sticky=E + W)

senLabel = Label(rightFrame, text='Sensitivity: ', width=20, anchor=W)
senLabel.grid(row=9, column=0, columnspan=3, padx=5, pady=5, sticky=E + W)

accuracyLabel = Label(rightFrame, text='Accuracy: ', width=20, anchor=W)
accuracyLabel.grid(row=7, column=0, columnspan=3, padx=5, pady=5, sticky=E + W)

matLabel = Label(rightFrame, text='Matthews_correlation_coef: ', width=20, anchor=W)
matLabel.grid(row=12, column=0, columnspan=3, padx=5, pady=5, sticky=E + W)

timeLabel = Label(rightFrame, text='Time executed: ', width=20, anchor=W)
timeLabel.grid(row=13, column=0, columnspan=3, padx=5, pady=5, sticky=E + W)

weightLabel = Label(rightFrame, text='Weight: ', width=20, anchor=W)
weightLabel.grid(row=14, column=0, columnspan=3, padx=5, pady=5, sticky=E + W + N)

weightLabel1 = st.ScrolledText(rightFrame, width=20)
weightLabel1.grid(row=15, column=0, columnspan=3, padx=5, pady=5, sticky=E + W + N + S)

train_data = pandas.DataFrame(index=eval_list)
test_data = pandas.DataFrame(index=eval_list)


# Cac chuc nang

# XOa item
# def delete():
#     if data.empty:
#         browseLabel.configure(text='Empty data')
#     else:
#         # Dua ra gia tri cua item duoc xoa
#         for item in table.selection():
#
#             item_value = table.item(item)['values']
#
#             col = data.columns.tolist()
#
#             # So sanh tung gia tri mot cua tung cot thuoc tinh
#             # de lay duoc index cua thuoc tinh can xoa
#
#             def is_float(element: any):
#                 try:
#                     float(element)
#                     return float(element)
#                 except ValueError:
#                     return element
#
#             index_def = data[data[col[0]] == is_float(item_value[0])].index
#             for i in range(1, len(col) - 1):
#                 index_def = set(index_def).intersection(
#                     data[data[col[i]] == is_float(item_value[i])].index
#                 )
#             # Xoa trong treeview
#             table.delete(item)
#
#             # Xoa trong data
#             data.drop(index=index_def, inplace=True)
#             data.reset_index(drop=True, inplace=True)
#
#         string3 = 'Size of data : ' + str(len(data))
#         numberLabel.configure(text=string3)


# Reset gui
def reset_gui():
    global test_data, train_data
    matrixBtn.configure(state="disabled")
    accuracyLabel.configure(text="Accuracy:")
    specLabel.configure(text="Specificity:")
    senLabel.configure(text="Sensitivity:")
    f1Label.configure(text="F1 score:")
    precLabel.configure(text="Precision:")
    matLabel.configure(text="Matthews_correlation_coef")
    weightLabel1.delete('1.0', tkinter.END)
    fig_list.clear()
    canvas_list.clear()
    test_data = test_data.iloc[0:0]
    train_data = train_data.iloc[0:0]


# Quay tro lai data ban dau
def restore():
    global data
    if file_names_listbox.curselection() != ():
        if current_file_name[-5:] == ".xlsx":
            data = pandas.read_excel(current_file_name)
            create_table(data)
        elif current_file_name[-4:] == ".csv":
            data = pandas.read_csv(current_file_name)
            create_table(data)


# Chia data thanh 2 set de train va test
def split():
    if data.empty:
        browseLabel.configure(text='Empty data')
    # Thuc hien chia data
    elif file_names_listbox.curselection() != ():
        # file_name = file_names_listbox.get(file_names_listbox.curselection())
        t = TrainAndTestSplitting.TrainAndTestSplitting(current_file_name)
        split_list = t.trainAndTestSplitting(train_size=0.8, test_size=0.2, method="stratified")
        # Them vao pathmap
        # Them vao file_names_listbox
        current_listbox_items = set(file_names_listbox.get(0, "end"))
        for file in split_list:
            if file not in current_listbox_items:
                path_map.insert(file_names_listbox.curselection()[0] + 1, file)
                file_names_listbox.insert(file_names_listbox.curselection()[0] + 1, file)

        browseLabel.configure(text="Done splitting data")


# Hien thi chi tiet cac chi so
def graph_detail():
    # TODO
    # Tao popup window
    # Hien thi cac chi so can thiet
    return None


# Su dung cho viec tao ra toplevel va hien thi nhung thong so khac
toplevel_in_use = []
matrix_attribute = None
def_matrix = None
to_test = False


# Tao window hien thi defuse matrix
def create_toplevel():
    if len(toplevel_in_use) == 1:
        toplevel_in_use[0].destroy()
        toplevel_in_use.pop()

    top = Toplevel(gui)
    toplevel_in_use.append(top)

    if to_test:
        title = "Test Defuse Matrix"
    else:
        title = "Train Defuse Matrix"
    top.title(title)

    top_label = Label(top, text="def", height=3, width=10)
    top_label.grid(row=0, column=0)

    size = len(matrix_attribute)
    for i in range(size):
        j = i + 1
        top_label1 = Label(top, text=matrix_attribute[i], relief="ridge", height=3, width=10)
        top_label1.grid(row=0, column=j)

        top_label2 = Label(top, text=matrix_attribute[i], relief="ridge", height=3, width=10)
        top_label2.grid(row=j, column=0)

    for i in range(size):
        for j in range(size):
            top_label1 = Label(top, text=def_matrix[i][j], relief="ridge", height=3, width=10)
            top_label1.grid(row=i + 1, column=j + 1)

    top.mainloop()


# Hien thi ket qua train/test theo nhom 2
def train_nhom2(data1, test=False):
    if data1.empty:
        browseLabel.configure(text='Empty data')
    else:
        if len(toplevel_in_use) == 1:
            toplevel_in_use[0].destroy()
            toplevel_in_use.pop()
        try:
            model = CS_IFS.CS_IFS(current_file_name)
            start_time = time.time()
            evaluation = eval_method.get()
            model.fit(measure=distance_method.get(), evaluation=evaluation)
            if test:
                model.predict()
                modelEvaluation = model.TmodelEvaluation
                file_name = "Test_" + current_file_name
            else:
                modelEvaluation = model.modelEvaluation
                file_name = "Train_" + current_file_name

            # Tinh toan thoi gian thuc hien
            et = time.time()
            final_res = round((et - start_time) * 1000, 2)

            # Chi den file test hoac train tuong ung trong listbox
            file_names_listbox.select_clear(0, 'end')

            index = list(path_map).index(file_name)
            file_names_listbox.selection_set(index)
            file_names_listbox.activate(index)
            file_names_listbox.see(index)
            file_names_listbox.selection_anchor(index)

            # Hien thi file
            if file_name.endswith(".xlsx"):
                data2 = pandas.read_excel(file_name)
                draw(file_name, data2)
            elif file_name.endswith(".csv"):
                data2 = pandas.read_csv(file_name)
                draw(file_name, data2)

            # Cap nhat cac ket qua
            result_list = modelEvaluation.to_return_list()
            update_result(model.measure, result_list, test)

            accuracyLabel.configure(text=('Accuracy: ' + str(round(result_list[0] * 100, 2)) + ' %'))
            specLabel.configure(text=('Specificity: ' + str(round(result_list[1] * 100, 2)) + ' %'))
            senLabel.configure(text=('Sensitivity: ' + str(round(result_list[2] * 100, 2)) + ' %'))
            f1Label.configure(text=('F1 score: ' + str(round(result_list[3] * 100, 2)) + ' %'))
            precLabel.configure(text=('Precision: ' + str(round(result_list[4] * 100, 2)) + ' %'))
            matLabel.configure(text=('Matthews_correlation_coef: ' + str(round(result_list[5] * 100, 2)) + ' %'))
            timeLabel.configure(text=('Time: ' + str(final_res) + ' ms'))

            weights = model.weights
            attribute = data.columns.drop([data.columns[len(data.columns) - 1]])
            w = round(pandas.Series(weights, index=attribute), 4)

            weightLabel1.configure(state='normal')
            weightLabel1.delete('1.0', tkinter.END)
            weight_str = w.to_string(index=True)
            weightLabel1.insert(tkinter.INSERT, weight_str)
            weightLabel1.configure(state='disabled')

            global def_matrix, matrix_attribute, to_test
            def_matrix = model.getDefuseMatrix(not test)
            matrix_attribute = model.label
            to_test = test
            matrixBtn.configure(state='active')

        except FileNotFoundError:
            browseLabel.configure(text="Split data before using this function")

        except TypeError:
            browseLabel.configure(text='Value Error (Numeric only)')


# Hien thi ket qua theo nhom 1
def train_nhom1(data1):
    if data1.empty:
        browseLabel.configure(text='Empty data')
    else:
        restore()
        start_time = time.time()
        (str2, str3, df, conclusion) = \
            Algorithm.upload_file(data1, distance_method.get())
        et = time.time()

        final_res = round((et - start_time) * 1000, 4)
        numberLabel.configure(text=str3)
        accuracyLabel.configure(text=str2)
        timeLabel.configure(text=('Time: ' + str(final_res) + ' ms'))

        weightLabel1.configure(state='normal')
        weightLabel1.delete('1.0', tkinter.END)
        weight_str = df.to_string(index=True)
        weightLabel1.insert(tkinter.INSERT, weight_str)
        weightLabel1.configure(state='disabled')

        data1 = pandas.concat([data1, pandas.Series(conclusion, name='Prediction')], axis=1)
        create_table(data1, True)

        browseLabel.configure(text='Trained 1')


# Dien ket qua cua phep do vao train_data hoac test_data
def update_result(measure, value, test=False):
    if test:
        if measure not in test_data.columns:
            test_data.insert(0, measure, value)
    else:
        if measure not in train_data.columns:
            train_data.insert(0, measure, value)


# Export ket qua tu 2 train_data va test_data
def export_result():
    if not os.path.isdir(save_location):
        os.mkdir(save_location)
    if train_data.empty and test_data.empty:
        browseLabel.configure(text="You should train/test")
    else:
        filename = "Result/" + os.path.splitext(current_file_name)[0] + ".xlsx"
        with pandas.ExcelWriter(filename) as writer:
            if not train_data.empty:
                train_data.to_excel(writer, sheet_name='Train Result')
            if not test_data.empty:
                test_data.to_excel(writer, sheet_name='Test Result')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    read_folder()
    gui.mainloop()
