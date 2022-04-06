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
        
        if data:
            #if the initialization is done noramllywith the mandatory data given
            try:
                width = len(data.keys())
                fig, self.ax = plt.subplots(figsize=(width+3, 5))
                self._data_plot(data)
                plt.show()
                
            except Exception as err :
                messagebox.showwarning("showwarning", err)
            return 
        
        elif on_screen:
            #initialization with partial data given(from createScreen)
            try:
                width = len(on_screen.keys())
                fig, self.ax = plt.subplots(figsize=(width+3, 5))
                self._data_plot(on_screen)
                plt.show(block=False)
                
            except Exception as err :
                messagebox.showwarning("showwarning", err)
            return 
        
        else:
            #throw out the error message that will alert the user
            messagebox.showwarning("showwarning", "Cannot display empty object")
            return
        #pass
        
    def _data_plot(self, data):
        mult = 0
        position = 0
        is_front = False
        
        for i in data:
            position = (mult*3 + 2)
            if data[i]['name'] == 'fp45':
                self._plotFp45(pos=position, linestyle=None)
                
            elif data[i]['name'] == 'fm45':
                self._plotFm45(pos=position, linestyle=None)
                
            elif data[i]['name'] == 'h':
                self._plotH(pos=position, ax=self.ax)
                
            elif data[i]['name'] == 'v':
                self._plotV(pos=position)
                
            elif data[i]['name'] == 'f0':
                self._plotF0(pos=position, linestyle=None)
                
            elif data[i]['name'] == 's':
                self._plotSpear(pos=position, is_front=is_front, 
                                linestyle=None)
                is_front = not is_front
            mult+=1
        
        top = [1] * (position + 3)
        bot = [-1] * (position + 3)
        mid = [0] * (position + 3)

        x = [i for i in range(position + 3)]
        plt.plot(x, top , color = 'black')
        plt.plot( x, bot, color = 'black')
        plt.plot(x, mid , 'b-.', linewidth=1)
        
        plt.xlim(-3, position + 5)
        plt.ylim(-4, 4)
        plt.axis('off')
        
    
    def _plotFm45(self, **kwargs):
        #logic for the plotting goes here inside this function
        pos = kwargs['pos']
        y = np.linspace(-1, 1, 10)
        if kwargs['linestyle']:
            plt.plot(y+pos, y, color='grey', linestyle=kwargs['linestyle'])
        else:
            if pos - int(pos) == 0:
                plt.plot(y+pos, y, color='black')
            else:
                plt.plot(y+pos, y, color='grey')
             
    
    def _plotFp45(self, **kwargs):
        
        y = np.linspace(-1, 1, 10)
        if kwargs['linestyle']:
            plt.plot(-y+kwargs['pos'], y, color='grey', linestyle=kwargs['linestyle'])
        else:
            if kwargs['pos'] - int(kwargs['pos']) == 0:
                plt.plot(-y+kwargs['pos'], y, color='black')
            else:
                plt.plot(-y+kwargs['pos'], y, color='grey')
                
        

    
    def _plotH(self, **kwargs):
        pos = kwargs['pos']
        kwargs['ax'].add_patch(plt.Circle((pos,0), 0.2,color='green', fill=False))
    
    def _plotV(self, **kwargs):
        pos = kwargs['pos']
        
        y = np.linspace(0,1, 5)

        plt.plot(-y+pos, y, color = 'red', linewidth=1)
        plt.plot(y+pos, y, color = 'red', linewidth=1)
    
    def _plotF0(self, **kwargs):
        linestyle = kwargs['linestyle']
        pos = kwargs['pos']
        
        y = np.linspace(-1, 1, 10)
        if linestyle:
            plt.plot([pos]*10, y, color='cyan', linestyle=linestyle)
        else:
            if pos - int(pos) == 0:
                plt.plot([pos]*10, y, color='black')
            else:
                plt.plot([pos]*10, y, color='cyan')
                
    def _plotSpear(self, **kwargs):
        pos = kwargs['pos']
        h = 0
        linestyle= kwargs['linestyle']
        is_front = kwargs['is_front']
        
        y1 = np.linspace(h, 1, 5)
        y2 = np.linspace(-1, h, 5)
        if is_front:
            if linestyle:
                plt.plot(pos-y1+h, y1, color='cyan', linestyle=linestyle)
                plt.plot(pos+y2-h, y2, color='cyan', linewidth=linestyle)
            else:
                if pos == int(pos):
                    plt.plot(pos-y1+h, y1, color='black')
                    plt.plot(pos+y2-h, y2, color='black')
                else:
                    plt.plot(pos-y1+h, y1, color='cyan')
                    plt.plot(pos+y2-h, y2, color='cyan')
        else:
            if linestyle:
                plt.plot(pos + y1 - h, y1, linestyle=linestyle)
                plt.plot(pos - y2 + h, y2, linestyle = linestyle)
            else :
                if pos == int(pos):
                    plt.plot(pos + y1 - h, y1, color='black')
                    plt.plot(pos - y2 + h, y2, color='black')
                else:
                    plt.plot(pos + y1 - h, y1, color='cyan')
                    plt.plot(pos - y2 + h, y2, color='cyan')
                    
    def _plotFishHead(self, **kwargs):
        pass
        
        
    
    def _annotate(self, **kwargs):
        #universal common logic that follows the L labels for all the
        #constituents of the cut profile.
        
        pass
    
