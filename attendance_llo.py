# -*- coding: utf-8 -*-
"""
Created on Sun Mar 19 12:40:12 2017

@author: IukhymchukS
"""

from config import config
import mysql.connector
from mysql.connector import errorcode
from tkinter.messagebox import askokcancel, showerror
from itertools import groupby
from operator import itemgetter

######################################################################################################
# Loading initial data and combining its to list                                                     #
######################################################################################################

def connecting_to_db(**config): # connecting to DB, return connection object
    cnx = None
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
    cnx = connecting_to_db(**config)
    cursor = cnx.cursor()
    res = None
#    print(sql)
    if isinstance(sql, list) or isinstance(sql, tuple):
        for (sql_line, data) in zip(sql, *param):
            print (sql_line)
            print (data)
            try:
                res = cursor.execute(sql_line, data)
            except mysql.connector.errors.DataError:
                showerror('Type error','Incorrect data type')
        if change:
            if askokcancel('SQL changes','Commit changes?'):
                cnx.commit()
            else: 
                cnx.rollback()
        else:
            res = cursor.fetchall()
        cursor.close()
        cnx.close()
    else:
        try:
            print(*param)
            print(sql)
            res = cursor.execute(sql, *param)
        except mysql.connector.errors.DataError:
            showerror('Type error','Incorrect data type')
        else:
            if change:
                if askokcancel('SQL changes','Commit changes?'):
                    cnx.commit()
                    res = True
                else: 
                    cnx.rollback()
                    res = False
            else:
                res = cursor.fetchall()
        cursor.close()
        cnx.close()
        """print(*param)
        print(sql)
        res = cursor.execute(sql, *param)
        if change:
            if askokcancel('SQL changes','Commit changes?'):
                cnx.commit()
                res = True
            else: 
                cnx.rollback()
                res = False
        else:
            res = cursor.fetchall()
        cursor.close()
        cnx.close()"""
    return res
        

def selection_join(a,b):
    L = a + b
    L.sort(key=itemgetter(0))
    for _, group in groupby(L,itemgetter(0)):
        row_a, row_b = next(group), next(group,('0',''))
        if row_b is not None:
            yield row_a + row_b[1:]
                
def initialization(emp_desc):
    init_gen = 'SELECT '+ emp_desc[0] + ',' + emp_desc[1] + ',' + emp_desc[2] + ' FROM employee'
    
    init_pos = """
    SELECT E.idEmp, pos.current_pos FROM employee E
    INNER JOIN (SELECT idEmp, max(date_of_change) as max_date from position GROUP BY idEmp) last_pos
    INNER JOIN position pos
    ON E.idEmp=pos.idEmp and pos.idEmp=last_pos.idEmp and pos.date_of_change=last_pos.max_date;
    """
    
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
    pos = execute_SQL(init_pos, change=False)    
    toff = execute_SQL(init_toff, change=False)
    inf_vac = execute_SQL(init_inf_vac, change=False)
    vac = execute_SQL(init_vac, change=False)

    gen = empl
    for i in (pos, toff,inf_vac,vac):
        gen = list(selection_join(gen,i))
    return gen

emp_sql="""
    SHOW columns FROM employee
    """
emp_desc = dict(enumerate([el[0] for el in execute_SQL(emp_sql,change=False)]))
