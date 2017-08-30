# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 17:05:30 2017

@author: IukhymchukS
"""

from tkinter.messagebox import showerror, showinfo, showwarning, askyesno
from PIL import ImageTk
import tkinter
from attendance_llo import emp_desc, execute_SQL, initialization
from datetime import datetime
from collections import OrderedDict


######################################################################################################
# GUI part                                                                                           #
######################################################################################################

class DialogWindow(tkinter.Toplevel):
    def __init__(self, callback, **param):
        tkinter.Toplevel.__init__(self)
#        self.wind = tkinter.Toplevel()
        self.param = param
        callback(self)
        
    def form_template (self, title, field_list, button_list):
        " Create GUI for Toplevel dialog window. Input parameters are list of entry names" \
        "and button parameters. Created widgets (vars of widget) append to class instance"
        
        self.ent_dict = {}
        self.but_dict = {}
        for row, field in enumerate(field_list): 
            tkinter.Label(self, text=field, justify='right', width=25).grid(row=row, column=0)
            entry_var = tkinter.StringVar()
            tkinter.Entry(self, textvariable=entry_var, width=30).grid(row=row, column=1)
            self.ent_dict[field] = entry_var
        frm=tkinter.Frame(self)
        frm.grid(row=len(field_list)+1, column=1, columnspan=2)
        for button in button_list:
            btn = tkinter.Button(frm, text=button[0], command = button[1]).pack(side=button[2], padx=5, pady=1)
            self.but_dict[button[0]] = btn
        self.title(title)
            
    def onaddempl(self):
        field_list = ['Full name', 'Date of Employee (DD.MM.YYYY)', 'Date of birsday (DD.MM.YYYY)', 'Position', 'Salary', 'Commission percent', 'Time off', 'Informal Vacation', 'Vacation']
        button_list = [('Ok', lambda: self.onaddok(field_list), 'left'), ('Cancel', self.destroy, 'right')]
        title = 'Add employee'
        self.form_template(title, field_list, button_list)        

    def onaddok(self, field_list):
        addEmp_sql = ["INSERT INTO employee (fullName, dateOfEmp, dob) VALUES (%s, %s, %s);", 
                      "SET @last_id_in_employee = LAST_INSERT_ID();",
                      "INSERT INTO position (idEmp, current_pos, date_of_change) VALUES (@last_id_in_employee, %s, %s);",
                      "INSERT INTO salary (idEmp, current, date_of_change) VALUES (@last_id_in_employee, %s, %s);",
                      "INSERT INTO commission (idEmp, comm_percent, date_of_change, year) VALUES (@last_id_in_employee, %s, %s, %s);",
                      "INSERT INTO timeoff (idEmp, date_of_change, description, timeoff_avail) VALUES (@last_id_in_employee, %s, 'Date of employment', 0);",
                      "INSERT INTO informal_vacation (idEmp, date_of_change, description, inf_vac_available) VALUES (@last_id_in_employee, %s, 'Date of employment', 0);",
                      "INSERT INTO vacation (idEmp, date_of_change, description, vacation_avail) VALUES (@last_id_in_employee, %s, 'Date of employment', 0);"]
        date_of_ch = self.ent_dict[field_list[1]].get()
        date_of_ch = datetime.strptime(date_of_ch, '%Y-%m-%d').date()
        addparam = [(self.ent_dict[field_list[0]].get(), date_of_ch, self.ent_dict[field_list[2]].get()), 
                    (),
                    (self.ent_dict[field_list[3]].get(), date_of_ch),
                    (self.ent_dict[field_list[4]].get(), date_of_ch),
                    (self.ent_dict[field_list[5]].get(), date_of_ch, date_of_ch.year),
                    (date_of_ch,),
                    (date_of_ch,),
                    (date_of_ch,)]
        execute_SQL(addEmp_sql, addparam)
        showinfo('Successful operation', "Employee was added successfully."\
                                          "Refresh main table")

    def onchange (self):
#        print(self.param)
        button_list = [('Commit', self.oncommit, 'left'), ('Cancel', self.destroy, 'right')]
        self.form_template(self.param['title'], self.param['fields'], button_list)

    def oncommit(self):
        ids = takeids(cb_list, rows_var)
        print(ids)
        if len(ids) > 1:
            showwarning('Selection WARNING', 'Select 1 Employee for this operation')
        elif not ids:
            showinfo('Selection info', 'Select Employee, please')
        else:
            row = ids[0][1] - 1
            if self.param['operation'] == 'add':
                val_avail = float(rows_var[row][self.param['colnum']].get()) + float(self.ent_dict[self.param['fields'][0]].get()) # first operand is current value, second typed in input form
#                print(val_avail)
            elif self.param['operation'] == 'remove':
                val_avail = float(rows_var[row][self.param['colnum']].get()) - float(self.ent_dict[self.param['fields'][0]].get()) # first operand is current value, second typed in input form
            format_string = ','.join(['%s'] * (len(self.param['fields'])+2))    # +2 explanation: 1 - for employee id, 1 for PK
            change_sql = "INSERT INTO " + self.param['table_name'] + " VALUES (%s)" % format_string
            field_list = self.param['fields']
# TBD Проверить, чтобы дата изменения была больше текущей даты
            change_param = [ids[0][0]] + [self.ent_dict[field_list[i]].get() for i in range(1,len(field_list))] + [val_avail]  #create list of parameters for sql query
            change_param.append(None)   # for PK field
#            print (change_param)
            res = execute_SQL(change_sql, change_param)
#            print(res)
            if res:
                rows_var[row][self.param['colnum']].set(str(val_avail))
            cb_list[ids[0][1]].set(0)
            root.focus()
            self.destroy()
            
class History(tkinter.Toplevel):
    """Dialog window for retrieving history on requested data by using table_name for source of history, labels for column name. 
        Inherit Toplevel __init__ method, use method request_dates for input parameter. """
    def __init__(self, **param):
        tkinter.Toplevel.__init__(self)
        self.param = param
        self.title('Date range')
        self.request_dates()
    
    def request_dates(self):
        row1 = tkinter.Frame(self)
        row1.pack(expand='YES', fill='both')        
        tkinter.Label(row1, text='Start date(YYYY-MM-D):', width=20).pack(side='left', expand='YES', fill='both')
        var1 = tkinter.StringVar()
        tkinter.Entry(row1, textvariable=var1, width=20).pack(side='right', expand='YES', fill='both')
        row2 = tkinter.Frame(self)
        row2.pack(expand='YES', fill='both')        
        tkinter.Label(row2, text='End date(YYYY-MM-D):', width=20).pack(side='left', expand='YES', fill='both')
        var2 = tkinter.StringVar()
        tkinter.Entry(row2, textvariable=var2, width=20).pack(side='right', expand='YES', fill='both')
        row3 = tkinter.Frame(self)
        row3.pack(pady=2)
        tkinter.Button(row3, text='Retrieve', command=self.onretrieve).pack(expand='YES', fill='both')
        self.dates = (var1, var2)
        
    def onretrieve(self):
        self.table = tkinter.Toplevel()
        title = '%s change history' % self.param['table_name']
        self.table.title(title)
#        button_list = [('close', self.table.destroy, 'left')]
        ids = takeids(cb_list, rows_var)
        labels = self.param['field_list']
        col_name_sql = 'SHOW columns FROM '+self.param['table_name']+';'
        col_desc = execute_SQL(col_name_sql, change=False)
        col_list = 't.'+col_desc[0][0] + ', e.fullName, ' + ', '.join(('t.'+i[0] for i in col_desc[1:-1]))   # don't display table PK 
        print(col_list)
        format_string = ','.join(['%s']*(len(ids)))
        print(format_string)
        select_sql = 'SELECT ' + col_list + ' FROM employee e '\
                    'INNER JOIN '+ self.param['table_name'] + ' t '\
                    'WHERE e.idEmp = t.idEmp and t.idEmp in (%s) and '\
                    '(t.date_of_change BETWEEN %s and %s) ORDER BY t.idEmp, t.date_of_change;'
        emp_ids = tuple(i[0] for i in ids)
        in_emp_ids = ', '.join(['%s']*len(emp_ids))
        select_sql = select_sql % (in_emp_ids, '%s', '%s')  # format string with count of %s = count of selected ids + start , end dates
        sql_parameters = []
        sql_parameters.extend(emp_ids)
        sql_parameters.append(self.dates[0].get())
        sql_parameters.append(self.dates[1].get())
#        print(select_sql)        
#        print(sql_parameters)
        if ids:
            selection = execute_SQL(select_sql, sql_parameters, change=False)
            rowcount = len(selection)
            colcount = max(len(i) for i in selection)
            create_gui(self.table, selection, labels, rowcount, colcount, cb_exist=False)
            btn = tkinter.Button(self.table, text='Close', command=(self.table.destroy))
            btn.grid(row=rowcount+2, column=1, columnspan=colcount)
        else:
            showwarning('Selection warning', 'Select at least one employee!')        
        
        

######################################################################################################
# GUI part. Main table                                                                                           #
######################################################################################################

def create_checkbar(root):
    global referenses
    cblist = []                   
    for i in range(rowcount+1):
        var = tkinter.IntVar()
        cb=tkinter.Checkbutton(root,variable=var)
        cb.grid(column=0, row=i)
        cblist.append(var)
        if i == 0:
            cb.config(command=lambda: onCheckAll(cblist))
        referenses['checkbar'].append((cb,i))
    return cblist

def create_entry(root, selection, cols_var, row, col, width, color='light grey', justify='center', cb_exist=True):
    """ Create etnries grid with data from main_d list. White cells are editable, grey not editable.
        If you eant change grey cell you should use button from toolbar respected column.
    """
    global referenses
    if cb_exist:
        colgrid = col+1
    else:
        colgrid = col
    st_var=tkinter.StringVar()
    ent=tkinter.Entry(root, textvariable=st_var, bg=color, relief='sunken', justify=justify)
    ent.grid(row=row+1, column=colgrid, sticky='NSEW')
    referenses['grids'].append((ent,row+1))
    ent.config(width=width)
    if selection[row][col] is None:
         ent.insert(0, '')
    else:
        ent.insert(0, selection[row][col])
#    cols_var.append((st_var, row, col))
    cols_var.append(st_var)
    if col in (1, 2):
        ent.config(bg='white')
        ent.bind('<Return>',lambda _: onEdit(st_var, row, col))
    else:
        ent.bind('<Key>',lambda _: onbindother(st_var, row, col))
#    else:
#        ent=tkinter.Entry(root, bg='white', relief='sunken', justify=justify)
#        ent.grid(row=row+1, column=col+1,sticky='NSEW')
#        ent.config(width=width)
#        ent.insert(0,main_d[row][col])
#        ent.config(state='readonly')
    root.columnconfigure(col+1,weight=1)
    

def create_label (root, label):
    lab = tkinter.Label(root, text=label[1], width=label[2], relief='groove')
    lab.grid(row=0, column=label[0], sticky='NSEW')
    lab.config(font=(None, '10','bold'))
    root.columnconfigure(label[0], weight=1)
    
def create_toolbar(root, row, toolbar, width="10"):
    global referenses
    for key in toolbar:
        colspan=1
        bwidth=width
        if key == '1':
            bwidth = "25"
            colspan=2
        frm_button = tkinter.Frame(root)
        frm_button.grid(row=row, column=int(key), columnspan=colspan, sticky='we')
        referenses['toolbar'].append((frm_button))
        for button in toolbar[key]:
            if button:
                btn1 = tkinter.Button(frm_button, text=button[0], width=bwidth, command=button[2])   
                if button[0] == 'History' or key =='4':
                    btn1.pack(side=button[1], expand='YES', fill='x')
                else:
                    btn1.pack(side=button[1], pady='1')
    
def create_gui(root, selection, labels, rowcount, colcount, cb_exist):
    for label in labels:
        create_label(root, label)
    root.rowconfigure(0, weight=1)
    rows_var = []
    cols_var = []
    for row in range(rowcount):
        cols_var = []
        for col in range(colcount):
            if col == 0:
                create_entry(root, selection, cols_var, row, col, 5, cb_exist=cb_exist)
            elif col == 1:
                create_entry(root, selection, cols_var, row, col, 40, color='white', justify='left', cb_exist=cb_exist)
            elif col == 2:
                create_entry(root, selection, cols_var, row, col, 15, color='white',cb_exist=cb_exist)
            else:
                create_entry(root, selection, cols_var, row, col, 15, cb_exist=cb_exist)
        rows_var.append(cols_var)
        root.rowconfigure(row+1, weight=1)
    return rows_var

def takeids(cblist, rows_var):
    """ Take check button list and returns Employee ids for continue operation.
    Show warning message if selected 'all' button for critical operation (flag warning).
    Return tuples of (id, rownum) of check button
    """

    rowsnum = tuple([i-1 for (i, var) in enumerate(cblist) if var.get()])
    ids = tuple([(int(rows_var[i][0].get()),i+1) for i in rowsnum])
    return ids

def onCheckAll(cblist):                                                               # check/unchek all checkbar items
    if cblist[0].get():
        [el.set(1) for el in cblist]
    else:
        [el.set(0) for el in cblist]

def onEdit(field, row, col):                                                 # Edit data in main table                
    print (col)
    if field.get() != main_d[row][col]:
        onEdit_sql = 'UPDATE employee SET ' + emp_desc[col] + ' = %s WHERE ' + emp_desc[0] + ' = %s'
        execute_SQL(onEdit_sql, field.get(), main_d[row][0])

def onbindother(field, row, col):
    print (col)
    val = field.get()
    if val != main_d[row][col]:
        showerror('Edit error', 'Cell editing is denied. Use button!')
    field.set(main_d[row][col])
    #TBD: Корректный метод обработки события. Например: возвращать значение в ячейку и выдавать ошибку при нажатии Return

def onRefresh(labels, toolbar1, toolbar2):    #TBD
    global main_d
    global rowcount, colcount
    global cb_list
    global rows_var
    main_d = initialization(emp_desc)
    print (main_d)
    rowcount = len(main_d)
    colcount = max(len(i) for i in main_d)
    cb_list = create_checkbar(root)
    rows_var = create_gui(root, main_d, labels, rowcount, colcount, cb_exist=True)
    create_toolbar(root, rowcount+1, OrderedDict(sorted(toolbar1.items())))
    create_toolbar(root, rowcount+2, OrderedDict(sorted(toolbar2.items())))
#    for item in root.grid_slaves():
#        if int(item.grid_info()['row'])>rowcount+2:
#            item.grid_forget()
#   TBD: Корректное удаление строки, например, сохранять ссылки на виджеты.
    

def ondelemp(cblist, rows_var):
    global referenses
    """Delete Employee from DB according to checked item.
    Input: check button list and array of variables from grid entries
    Output: """
    global main_d
    ids = takeids(cblist, rows_var)
    if len(ids) > 1:
        showwarning('Selection WARNING', 'Select 1 Employee for this operation')
    elif not ids:
        showinfo('Selection info', 'Select Employee, please')
    else:
#    print(ids)
        del_sql =  ["DELETE from position WHERE idEmp = %s;",
                    "DELETE from salary WHERE idEmp = %s;",
                    "DELETE from commission WHERE idEmp = %s;",
                    "DELETE from timeoff WHERE idEmp = %s;",
                    "DELETE from informal_vacation WHERE idEmp = %s;",
                    "DELETE from vacation WHERE idEmp = %s;",
                    "DELETE from employee WHERE idEmp = %s;"]
        args = [(ids[0][0],) for i in range(len(del_sql))]
#        print (args)
        execute_SQL(del_sql, args)
        [item[0].destroy() for item in referenses['checkbar'] if item[1] == ids[0][1]]
        [item[0].destroy() for item in referenses['grids'] if item[1] == ids[0][1]]
        showinfo('Successful operation', "Employee was delete successfully")
        root.update()

def onposchange():
    pass
  
def onSalary():
    pass

def onCommission():
    pass



main_d = initialization(emp_desc)       # list of tuples with main infromation
rowcount = len(main_d)                  # numbers of row without labels and toolbar
colcount = max(len(i) for i in main_d)  # numers of column without checkbar
root = tkinter.Tk()
referenses = {}
referenses['checkbar']=[]
referenses['grids'] = []
referenses['toolbar']=[]

sync_b = tkinter.Button(root, command=lambda: onRefresh(labels, toolbar1, toolbar2), justify='center', width="25", height="20")    #refresh button
syn_img = ImageTk.PhotoImage(file='./arrow_refresh.png')
sync_b.config(image=syn_img)
img_b = syn_img
sync_b.grid(column=1, row=0)
labels = ((2, 'Full Name', 40),(3, 'Date of Employee', 15), (4, 'Position', 15), (5, 'Timeoff', 15),(6, 'Inf_vacation (w.d.)', 15),(7, 'Vacation', 15))
toolbar1 = {'1': (('Add Empl', 'left', lambda: DialogWindow(DialogWindow.onaddempl)), ('Del Empl', 'right', lambda: ondelemp(cb_list,rows_var))),
            '4': (('Change', 'left',onposchange),),
            '5': (('Add', 'left', lambda: DialogWindow(DialogWindow.onchange, operation='add', **toff)), 
                  ('Rem', 'right', lambda: DialogWindow(DialogWindow.onchange, operation='remove', **toff))),
            '6': (('Add', 'left', lambda: DialogWindow(DialogWindow.onchange, operation='add', **inf_vac)), 
                  ('Rem', 'right', lambda: DialogWindow(DialogWindow.onchange, operation='remove', **inf_vac))),
            '7': (('Add', 'left', lambda: DialogWindow(DialogWindow.onchange, operation='add', **vac)), 
                  ('Rem', 'right', lambda: DialogWindow(DialogWindow.onchange, operation='remove', **vac)))}
toolbar2 = {'1': (('Salary', 'left', onSalary), ('Commission', 'right', onCommission)),
            '4': (('History', 'left', lambda: History(**pos)),),
            '5': (('History', 'left', lambda: History(**toff_hist)),),
            '6': (('History', 'left', lambda: History(**inf_vac_hist)),),
            '7': (('History', 'left', lambda: History(**vac_hist)),)}

#toff parameters
toff = {}
toff['title'] = 'Changing time off info'
toff['fields'] = ['Time off q-ty:', "Date of change", 'Status (add/rem):', 'Description']
toff['table_name'] = 'timeoff'
toff['colnum'] = 4

#informal vacation parameters
inf_vac = {}
inf_vac['title'] = 'Changing informal vacation info'
inf_vac['fields'] = ['Informal vacation q-ty (w.d.):', "Date of change", 'Description']
inf_vac['table_name'] = 'informal_vacation'
inf_vac['colnum'] = 5

#vacation parameters
vac = {}
vac['title'] = 'Changing informal vacation info'
vac['fields'] = ['Vacation (c.d.):', "Date of change", "Status", 'Description']
vac['table_name'] = 'vacation'
vac['colnum'] = 6

# history position parameters
pos = {}
pos['table_name'] = 'position'
pos['field_list'] = [(0, 'ID', 5), (1, 'Full Name', 40), (2, 'Current position', 15), (3, 'Previous position', 15), (4, 'Date of change', 15)]

# history time off parameters
toff_hist = {}
toff_hist['table_name'] = 'timeoff'
toff_hist['field_list'] = [(0, 'ID', 5), (1, 'Full Name', 40), (2, 'Date of change', 15), (3, 'Status', 15), (4, 'Description', 40), (5, 'Available', 15)]

# history informal vacation parameters
inf_vac_hist = {}
inf_vac_hist['table_name'] = 'informal_vacation'
inf_vac_hist['field_list'] = [(0, 'ID', 5), (1, 'Full Name', 40), (2, 'Date of change', 15), (3, 'Description', 15), (4, 'Available', 15)]

# history vacation parameters
vac_hist = {}
vac_hist['table_name'] = 'vacation'
vac_hist['field_list'] = [(0, 'ID', 5), (1, 'Full Name', 40), (2, 'Date of change', 15), (3, 'Status', 15), (4, 'Description', 15), (5, 'Available', 15)]

cb_list = create_checkbar(root)
rows_var = create_gui(root, main_d, labels, rowcount, colcount, cb_exist=True)
create_toolbar(root, rowcount+1, OrderedDict(sorted(toolbar1.items())))
create_toolbar(root, rowcount+2, OrderedDict(sorted(toolbar2.items())))
root.mainloop()
    
