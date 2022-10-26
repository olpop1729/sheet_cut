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
import os

PATH = '/Users/omkar/Omkar/Trash/cut_program/sheet_cut/gui'
os.chdir(PATH)

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
