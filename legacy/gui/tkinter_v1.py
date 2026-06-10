#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 13:28:35 2021

@author: omkar
"""


from tkinter import Tk, Button
from run_screen import RunScreen
from update_param import UpdateParamScreen
from create_cut_program import CreateCutProgramScreen # Assuming this is correct
from verify_output_screen import VerifyOutputScreen # Import the new screen


class MainWindow:

    def __init__(self):
        self._tk = Tk()
        self._content = {}
        self.__initScreen(self._tk)

    def __on_main_window_close(self):
        """Handles closing of the main Tkinter window."""
        if self._tk:
            self._tk.destroy() # Destroy all widgets
            self._tk.quit()    # Explicitly stop the Tkinter mainloop

    def __initScreen(self, parent):
        parent.geometry("500x200")
        parent.title('Main Window')
        content = {}

        content['buttons'] = []
        content['buttons'].append(Button(parent, text='Create',
                                         command=self._createScreen))
        content['buttons'].append(Button(parent, text='Run',
                                         command=self._run_screen))
        content['buttons'].append(Button(parent, text='Paramters',
                                         command=self._update_parameters))
        content['buttons'].append(Button(parent, text='Verify Output',
                                         command=self._verify_output_screen)) # New button

        self.content = content
        # Explicitly pack buttons
        for j in content['buttons']:
                j.pack()

        parent.protocol("WM_DELETE_WINDOW", self.__on_main_window_close)

        parent.mainloop()

    def _update_parameters(self):
        UpdateParamScreen(self._tk)

    def _run_screen(self):
        RunScreen(self._tk)

    def _createScreen(self):
        CreateCutProgramScreen(self._tk)

    def _verify_output_screen(self): # Method for the new screen
        VerifyOutputScreen(self._tk)

mw = MainWindow()
