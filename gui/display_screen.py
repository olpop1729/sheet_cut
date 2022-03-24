#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  1 23:15:04 2021

@author: omkar
"""

import matplotlib.pyplot as plt
import numpy as np
from tkinter import messagebox


class labels:
    
    steplap_code = 'steplap_code'


class DisplayWindow:
    
    def __init__(self, data=None, on_screen=None):
        
        fig, ax = plt.subplots(figsize=(10, 5))

        if data:
            #if the initialization is done noramllywith the mandatory data given
            
            pass
        elif on_screen:
            pass
        else:
            #throw out the error message that will alert the user
            messagebox.showwarning("showwarning", "Cannot display empty object")
        #pass
    
    def _plotFm45(self, **kwargs):
        if labels.steplap_code in kwargs:
             #logic for the plotting goes here inside this function
            print('found')
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
    
