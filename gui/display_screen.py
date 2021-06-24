#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  1 23:15:04 2021

@author: omkar
"""

from tkinter import ttk, Tk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
                                               NavigationToolbar2Tk)


class labels:
    
    steplap_code = 'steplap_code'


class DisplayWindow:
    
    def __init__(self, data=None):
        self._tk = Tk()       
        self.fig = Figure(figsize = (5, 5), dpi = 100)
        if data:
            #if the initialization is done noramllywith the mandatory data given
            #declareing an internal private function just make thing more modular?
            self._tk.title('Display Screen')
            self._initialize(data)
        else:
            #throw out the error message that will alert the user
            messagebox.showwarning("showwarning", "Cannot display empty object")
        #pass
    
    def _initialize(self, data):
        #initial window creation, window name, 
        canvas = FigureCanvasTkAgg(self.fig, master=self._tk)  # A tk.DrawingArea.
        self._canvas = canvas
        canvas.draw()
        canvas.get_tk_widget().pack()
        toolbar = NavigationToolbar2Tk(canvas,self._tk)
        toolbar.update()
        canvas.get_tk_widget().pack()
        pass
    
    def _plotFm45(self, **kwargs):
        if labels.steplap_code in kwargs:
            #logic for the plotting goes here inside this function
            print('found')
            x = np.linspace(10,100, 1)
        pass
    
    def _plotFp45(self, **kwargs):
        if labels.steplap_code in kwargs:
            #logic for the plotting goes here inside this function
            pass
        pass
    
    def _plotH(self, **kwargs):
        if labels.steplap_code in kwargs:
            #logic for the plotting goes here inside this function
            pass
        pass
    
    def _plotV(self, **kwargs):
        if labels.steplap_code in kwargs:
            #logic for the plotting goes here inside this function
            pass
        pass
    
    def _plotF0(self, **kwargs):
        if labels.steplap_code in kwargs:
            #logic for the plotting goes here inside this function
            pass
        pass
    
    def _annotate(self, **kwargs):
        #universal common logic that follows the L labels for all the
        #constituents of the cut profile.
        
        pass
    
