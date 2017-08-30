# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 12:27:57 2017

@author: IukhymchukS
"""

def func(**args):
    param = args
    print(param)

toff = {}
toff['title'] = 'Changing time off info'
toff['fields'] = ['Time off q-ty:', "Date of change", 'Status (add/rem):', 'Description']
toff['table_name'] = 'timeoff'
toff['colnum'] = 4

func(operat ='add', **toff)
