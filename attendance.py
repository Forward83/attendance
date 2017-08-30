# -*- coding: utf-8 -*-
"""
Created on Sun Mar 19 12:40:12 2017

@author: IukhymchukS
"""

from config import config

import mysql.connector
import tkinter
from mysql.connector import errorcode
from tkinter.messagebox import askokcancel, showerror
from itertools import groupby
from operator import itemgetter
from PIL import ImageTk
from collections import OrderedDict
from datetime import date, datetime

######################################################################################################
# Loading initial data and combining its to list                                                     #
######################################################################################################

def connecting_to_db(**config):     #connecting to DB, return connection object
    try:
        cnx=mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        if err.errno==errorcode.ER_ACCESS_DENIED_ERROR:
            print("Wrong username/passwrod credential")
        elif err.errno==errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    return cnx

def execute_SQL(sql, *param, change=True):
#    print(param)
    cnx=connecting_to_db(**config)
    cursor =cnx.cursor()
#    print(sql)
    try:
        cursor.execute(sql, param)
    except mysql.connector.errors.DataError:
        showerror('Type error','Incorrect data type')
    else:
        if change:
            if askokcancel('SQL changes','Commit changes?'):
                cnx.commit()
            else: 
                cnx.rollback()
            cursor.close()
            cnx.close()
        else:
            res=cursor.fetchall()
            cursor.close()
            cnx.close()
            return res

def selection_join(a,b):
    L = a + b
    L.sort(key=itemgetter(0))
    for _, group in groupby(L,itemgetter(0)):
        row_a, row_b = next(group), next(group,('0',''))
        if row_b is not None:
            yield row_a + row_b[1:]
                
emp_sql="""
SHOW columns FROM employee
"""
emp_desc = dict(enumerate([el[0] for el in execute_SQL(emp_sql,change=False)]))

init_gen = 'SELECT '+ emp_desc[0] + ',' + emp_desc[1] + ',' + emp_desc[2] + ' FROM employee'

init_toff="""
SELECT E.idEmp, toff.timeoff_avail FROM employee E
INNER JOIN (SELECT idEmp, max(date_of_change) as max_date from timeoff GROUP BY idEmp) last_toff
INNER JOIN timeoff toff
ON E.idEmp=toff.idEmp and toff.idEmp=last_toff.idEmp and toff.date_of_change=last_toff.max_date;
"""

init_inf_vac="""
SELECT E.idEmp, inf_vac.inf_vac_available FROM employee E
INNER JOIN (SELECT idEmp, max(date_of_change) as max_date from informal_vacation GROUP BY idEmp) last_iv
INNER JOIN informal_vacation inf_vac
ON E.idEmp=inf_vac.idEmp and inf_vac.idEmp=last_iv.idEmp and inf_vac.date_of_change=last_iv.max_date; 
"""

init_vac="""
SELECT E.idEmp, vac.vacation_avail FROM employee E
INNER JOIN (SELECT idEmp, max(date_of_change) as max_date from vacation GROUP BY idEmp) last_vac
INNER JOIN vacation vac
ON E.idEmp=vac.idEmp and vac.idEmp=last_vac.idEmp and vac.date_of_change=last_vac.max_date;
"""

empl = execute_SQL(init_gen, change=False)
toff = execute_SQL(init_toff, change=False)
inf_vac = execute_SQL(init_inf_vac, change=False)
vac = execute_SQL(init_vac, change=False)

gen = empl
for i in (toff,inf_vac,vac):
    gen = list(selection_join(gen,i))

print(gen)

######################################################################################################
# GUI part                                                                                           #
######################################################################################################

class DialogWindow:
    def __init__(self, title, sql, callback):
        self.wind = tkinter.Toplevel(root)
        self.wind.title(title)
        self.sql = sql
        callback(self)
        
    def onAddEmp(self):
        self.ent_dict={}
        field_list=['Full name', 'Date of Employee', 'Date of birsday', 'Salary', 'Commission percent', 'Time off', 'Informal Vacation', 'Vacation']
        for row, field in enumerate(field_list):
            tkinter.Label(self.wind, text=field, justify='right', width=15).grid(row=row, column=0)
            entry_var=tkinter.StringVar()
            tkinter.Entry(self.wind, textvariable=entry_var, width=30).grid(row=row, column=1)
            self.ent_dict[field] = entry_var
#        year = date.year(date_of_ch)
        addEmp_sql = """
                     INSERT INTO employee (fullName, dateOfEmp, dob) VALUES (%s, %s, %s);
                     SET @last_id_in_employee = LAST_INSERT_ID();
                     INSERT INTO salary (idEmp, current, date_of_change) VALUES (@last_id_in_employee, %s, %s);
                     INSERT INTO commission (idEmp, comm_percent, date_of_change, year) VALUES (@last_id_in_employee, %s, %s, %s);
                     INSERT INTO timeoff (idEmp, date_of_change, description, timeoff_avail) VALUES (@last_id_in_employee, %s, 'Date of employment',0);
                     INSERT INTO informal_vacation (idEmp, date_of_change, description, inf_vac_available) VALUES (@last_id_in_employee, %s, 'Date of employment',0);
                     INSERT INTO vacation (idEmp, date_of_change, description, vacation_avail) VALUES (@last_id_in_employee, %s, 'Date of employment',0);
                     """
#        addparam = (ent_dict['Full name'].get(), ent_dict['Date of Employee'].get(), ent_dict['Date of birsday'].get(),
 #                   ent_dict['Salary'].get(), date_of_ch,
  #                  ent_dict['Commission percent'], date_of_ch, year,
   #                 date_of_ch,
    #                date_of_ch,
     #               date_of_ch)
        
        frm=tkinter.Frame(self.wind)
        frm.grid(row=len(field_list)+1, column=1, columnspan=2)
        tkinter.Button(frm, text='Ok', command=lambda: self.addEmployee(addEmp_sql,addEmp_sql)).pack(side='left',padx=5, pady=1)
        tkinter.Button(frm, text='Cancel', command=self.wind.destroy).pack(side='right', padx=5, pady=1)

    def addEmployee(self, sql, *param):
        date_of_ch = self.ent_dict['Date of Employee'].get()
        date_of_ch = datetime.strptime(date_of_ch,'%Y-%m-%d').date()       
        print (date_of_ch, date_of_ch.year)
#    execute_SQL(sql,*param)
#    rowcount += 1    
    pass

######################################################################################################
# GUI part. Main table                                                                                           #
######################################################################################################

def create_entry(row, col, width, justify='center', var=False):
    if var:
        st_var=tkinter.StringVar()
        ent=tkinter.Entry(root, textvariable=st_var, bg='white', relief='sunken', justify=justify)
        ent.grid(row=row+1, column=col+1, sticky='NSEW')
        ent.config(width=width)
        ent.insert(0,gen[row][col])
        cols_var.append((st_var, row, col))
        ent.bind('<Return>',lambda _: onEdit(st_var,row,col))
    else:
        ent=tkinter.Entry(root, bg='white', relief='sunken', justify=justify)
        ent.grid(row=row+1, column=col+1,sticky='NSEW')
        ent.config(width=width)
        ent.insert(0,gen[row][col])
        ent.config(state='readonly')
    root.columnconfigure(col+1,weight=1)
    
def create_label (row, col, text, width):
    lab = tkinter.Label(root, text=text, width=width, relief='groove')
    lab.grid(row=row, column=col, sticky='NSEW')
    lab.config(font=(None, '10','bold'))
    root.columnconfigure(col, weight=1)
    
def create_toolbar(row, toolbar, width="10"):
    for key in toolbar:
        colspan=1
        bwidth=width
        if key == '1':
            bwidth = "25"
            colspan=2
        frm_button = tkinter.Frame(root)
        frm_button.grid(row=row, column=int(key), columnspan=colspan, sticky='we')
        for button in toolbar[key]:
            if button:
                btn1 = tkinter.Button(frm_button, text=button[0], width=bwidth, command=button[2])   
                if button[0] == 'History':
                    btn1.pack(side=button[1], expand='YES', fill='x')
                else:
                    btn1.pack(side=button[1], pady='1')
    
def onCheckAll():                                                               # check/unchek all checkbar items
    if cblist[0].get():
        [el.set(1) for el in cblist]
    else:
        [el.set(0) for el in cblist]

def onEdit(field, row, col):                                                    # Edit data in main table                
    if field.get() != gen[row][col]:
        onEdit_sql = 'UPDATE employee SET ' + emp_desc[col] + ' = %s WHERE ' + emp_desc[0] + ' = %s'
        try:
            execute_SQL(onEdit_sql, field.get(), gen[row][0])
        except mysql.connector.errors.DataError:
            if col == 1:
                showerror('Type error','String is too long (up to 45 chars)')
            else:
                showerror('Type error','Incorrect Date format')
        else:
            empl = execute_SQL(init_gen, change=False)

def onRefresh():    #TBD
    pass


def onRemEmp():
    pass

def onAddToff():
    pass

def onRemToff():
    pass

def onAddInf_vac():
    pass

def onRemInf_vac():
    pass    

def onAddVac():
    pass

def onRemVac():
    pass      

def onSalary():
    pass

def onCommission():
    pass

def onToffHistory():
    pass

def onInf_VacHistory():
    pass

def onVacHistory():
    pass      

rowcount = len(gen)                  # numbers of row without labels and toolbar
colcount = max(len(i) for i in gen)  # numers of column without checkbar
root = tkinter.Tk()

sync_b = tkinter.Button(root, command=onRefresh, justify='center', width="25", height="20")    #refresh button
syn_img = ImageTk.PhotoImage(file='./arrow_refresh.png')
sync_b.config(image=syn_img)
img_b = syn_img
sync_b.grid(column=1, row=0)

create_label(0, 2, 'Full Name', 40)              # Column's name as label
create_label(0, 3, 'Date of Employee', 15)
create_label(0, 4, 'Timeoff', 15)
create_label(0, 5, 'Inf_vacation (w.d.)', 15)
create_label(0, 6, 'Vacation', 15)
root.rowconfigure(0, weight=1)

cblist = []                                         # Entries grid
for i in range(rowcount+1):
    var = tkinter.IntVar()    
    cb=tkinter.Checkbutton(root,variable=var)
    cb.grid(row=i,column=0)
    cblist.append(var)
    if i == 0:
        cb.config(command=onCheckAll)
rows_var = []
for row in range(rowcount):
    for col in range(colcount):
        cols_var = []
        if col == 0:
            create_entry(row, col, 5)
        elif col == 1:
            create_entry(row, col, 40, 'left', True)            
        elif col == 2:
            create_entry(row, col, 15, var=True)
        else:
            create_entry(row, col, 15)
        rows_var.append(cols_var)
        root.rowconfigure(row,weight=1)

toolbar1 = {'1': (('Add Empl', 'left', lambda: DialogWindow('New eployee',DialogWindow.onAddEmp)), ('Rem Empl', 'right', onRemEmp)),
            '4': (('Add', 'left', onAddToff), ('Rem', 'right', onAddToff)),
            '5': (('Add', 'left', onAddInf_vac), ('Rem', 'right', onRemInf_vac)),
            '6': (('Add', 'left', onAddVac), ('Rem', 'right', onRemVac))}
toolbar2 = {'1': (('Salary', 'left', onSalary), ('Commission', 'right', onCommission)), 
            '4': (('History', 'left', onToffHistory),),
            '5': (('History', 'left', onInf_VacHistory),),
            '6': (('History', 'left', onVacHistory),)}
create_toolbar(rowcount+2, OrderedDict(sorted(toolbar1.items())))
create_toolbar(rowcount+3, OrderedDict(sorted(toolbar2.items())))
root.mainloop()