#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 13:28:35 2021

@author: omkar
"""


from tkinter import Tk, Button
from run_screen import RunScreen
from update_param import UpdateParamScreen
from create_cut_program import CreateCutProgramScreen
import sys

class labels:
    steplap_type_map = {'No step-lap':0, 'Horizontal (Longitudinal)':1,
                        'Vertical (Lateral)':2, 'Skewed (Lateral)':3}
    attr_map = {''}
    open_code_map = {'NA':0, 'Open':1, 'Closed':2, 'Front Open, Rear Open':3,
                     'Front Open, Rear Closed':4, 'Front Closed, Rear Open':5,
                     'Front Closed, Rear Closed':6, 'Front Open':7, 'Front Closed':8,
                     'Rear Open':9, 'Rear Closed':10}

    create_frame_cols  =['PNR', 'Tool name', 'Step-lap type','Step-lap count',
                            'Open-Close config']

    tool_name_tuple = ('fm45', 'fp45', 'f0', 'v', 'h', 's', 'y', 'prrp45',
                       'pfrm45', 'prrf0', 'pfrf0', 'prlm45', 'prlf0',
                       'pflp4', 'pflf0')



class MainWindow:

    def __init__(self):
        self._tk = Tk()
        self._content = {}
        self.__initScreen(self._tk)

    def __initScreen(self, parent):
        parent.geometry("500x200")
        parent.title('Main Window')
        content = {}

        content['frames'] = []


        content['buttons'] = []
        content['buttons'].append(Button(parent, text='Create',
                                         command=self._createScreen))
        content['buttons'].append(Button(parent, text='Run',
                                         command=self._run_screen))
        content['buttons'].append(Button(parent, text='Paramters',
                                         command=self._update_parameters))


        content['labels'] = []

        self.content = content
        for i in content:
            for j in content[i]:
                j.pack()

        parent.mainloop()

    def _update_parameters(self):
        UpdateParamScreen()

    def _run_screen(self):
        RunScreen()

    def _createScreen(self):
        CreateCutProgramScreen()


mw = MainWindow()
sys.exit()