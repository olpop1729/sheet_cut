#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  1 23:15:04 2021

@author: omkar
"""

import matplotlib.pyplot as plt
import numpy as np
from tkinter import messagebox
from label_file import Labels


class labels:
    
    steplap_code = 'steplap_code'


class DisplayWindow:
    
    def __init__(self, data=None, on_screen=None, ax=None): # Added ax parameter
        self.ax = ax
        self.fig = None
        if self.ax:
            self.fig = self.ax.get_figure()

        if data:
            #if the initialization is done noramllywith the mandatory data given
            try:
                width = len(data.keys())
                if self.ax is None: # If no ax provided, create new figure and show it
                    self.fig, self.ax = plt.subplots(figsize=(max(width,1)+3, 5))
                    self._data_plot(data)
                    plt.show()
                else: # If ax is provided, plot on it (do not call plt.show())
                    self._data_plot(data)
            except Exception as err :
                messagebox.showwarning("Display Error", f"Error plotting data: {str(err)}")
            return 
        
        elif on_screen:
            #initialization with partial data given(from createScreen)
            try:
                width = len(on_screen.keys())
                if self.ax is None:
                    self.fig, self.ax = plt.subplots(figsize=(max(width,1)+3, 5))
                    self._data_plot(on_screen)
                    plt.show(block=False) # Non-blocking for Tkinter if separate window
                else:
                    self._data_plot(on_screen) # Plot on existing ax
            except Exception as err :
                messagebox.showwarning("Display Error", f"Error plotting on_screen data: {str(err)}")
            return 
        
        else:
            #throw out the error message that will alert the user
            if self.ax is None:
                messagebox.showwarning("Display Warning", Labels.warnmsg_empty_object)
            elif self.ax and not data and not on_screen: # If ax exists but no data, clear it
                self._data_plot(data) # This will effectively clear if data is None/empty
            return
        #pass
        
    def _data_plot(self, data):
        mult = 0
        position = 0
        is_front = False
        
        keys = [str(i) for i in range(len(data.keys()))]
        keys = keys[::-1]
        
        # Clear the axes before drawing new plot if an ax is provided
        if self.ax:
            self.ax.clear()
            # current_fig = self.ax.get_figure() # Not strictly needed here
        
        for i in data:
            
            prev = 3 * (mult + 1) + 2
            position = mult * 3 + 2
            
            
            if data[i][Labels.name] == 'fp45':
                self._plotFp45(pos=position, linestyle=None)
                
            elif data[i][Labels.name] == 'fm45':
                self._plotFm45(pos=position, linestyle=None)
                
            elif data[i][Labels.name] == 'h':
                self._plotH(pos=position, ax=self.ax)
                
            elif data[i][Labels.name] == 'v':
                self._plotV(pos=position)
                
            elif data[i][Labels.name] == 'f0':
                self._plotF0(pos=position, linestyle=None)
                
            elif data[i][Labels.name] == 's':
                self._plotSpear(pos=position, is_front=is_front, 
                                linestyle=None)
                is_front = not is_front
                
            elif data[i][Labels.name] == 'fish_head':
                self._plotFishHead(pos=position, is_front=is_front, 
                                   open_code=data[i]['open_code'])
                is_front = not is_front
                
            elif data[i][Labels.name] == 'fish_tail':
                self._plotFishTail(pos=position, is_front=is_front, 
                                   open_code=data[i]['open_code'])
                is_front = not is_front
                
                
            elif data[i][Labels.name] == 'ys':
                self._plotSplitYoke(pos=position)
            
                
            self._annotate( position, prev, int(keys[mult]))
            
            mult+=1
        
        top = [1] * (position + 3)
        bot = [-1] * (position + 3)
        mid = [0] * (position + 3)

        x = [i for i in range(position + 3)]
        self.ax.plot(x, top , color = Labels.color_black)
        self.ax.plot( x, bot, color = Labels.color_black)
        self.ax.plot(x, mid , 'b-.', linewidth=1)
        
        self.ax.annotate('', xy=(position + 5, 0), xytext=(position + 3, 0),
                     arrowprops=dict(arrowstyle='->'))
        
        self.ax.set_xlim(-3, position + 5)
        self.ax.set_ylim(-4, 4)
        self.ax.axis('off')
        
    
    def _plotFm45(self, **kwargs):
        #logic for the plotting goes here inside this function
        pos = kwargs['pos']
        y = np.linspace(-1, 1, 10)
        if kwargs[Labels.linestyle]:
            self.ax.plot(y+pos, y, color=Labels.color_grey, linestyle=kwargs[Labels.linestyle]) # Corrected typo from linstyle
        else:
            if pos - int(pos) == 0:
                self.ax.plot(y+pos, y, color=Labels.color_black)
            else:
                self.ax.plot(y+pos, y, color=Labels.color_grey)
             
    
    def _plotFp45(self, **kwargs):
        
        y = np.linspace(-1, 1, 10)
        if kwargs[Labels.linestyle]:
            self.ax.plot(-y+kwargs[Labels.pos], y, color=Labels.color_grey, linestyle=kwargs[Labels.linestyle])
        else:
            if kwargs[Labels.pos] - int(kwargs[Labels.pos]) == 0:
                self.ax.plot(-y+kwargs[Labels.pos], y, color=Labels.color_black)
            else:
                self.ax.plot(-y+kwargs[Labels.pos], y, color=Labels.color_grey)
                
        

    
    def _plotH(self, **kwargs):
        pos = kwargs[Labels.pos]
        self.ax.add_patch(plt.Circle((pos,0), 0.2,color=Labels.color_green, fill=False))
    
    def _plotV(self, **kwargs):
        pos = kwargs[Labels.pos]
        
        y = np.linspace(0,1, 5)

        self.ax.plot(-y+pos, y, color = Labels.color_red, linewidth=1)
        self.ax.plot(y+pos, y, color = Labels.color_red, linewidth=1)
        
    def _plotSplitYoke(self, **kwargs):
        pos = kwargs[Labels.pos]
        y1 = np.linspace(-1, 1, 10)
        y2 = np.linspace(0, 1, 5)
        self.ax.plot(pos+y2, y2, color=Labels.color_black)
        self.ax.plot(pos-y1, y1, color=Labels.color_black)
    
    def _plotF0(self, **kwargs):
        linestyle = kwargs[Labels.linestyle]
        pos = kwargs[Labels.pos]
        
        y = np.linspace(-1, 1, 10)
        if linestyle:
            self.ax.plot([pos]*10, y, color=Labels.color_cyan, linestyle=linestyle) # Used Labels.color_cyan
        else:
            if pos - int(pos) == 0:
                self.ax.plot([pos]*10, y, color=Labels.color_black)
            else:
                self.ax.plot([pos]*10, y, color=Labels.color_cyan)
                
    def _plotSpear(self, **kwargs):
        pos = kwargs['pos']
        h = 0
        linestyle= kwargs['linestyle']
        is_front = kwargs['is_front']
        
        y1 = np.linspace(h, 1, 5)
        y2 = np.linspace(-1, h, 5)
        if is_front:
            if linestyle:
                self.ax.plot(pos-y1+h, y1, color=Labels.color_cyan, linestyle=linestyle)
                self.ax.plot(pos+y2-h, y2, color=Labels.color_cyan, linestyle=linestyle) # was linewidth=linestyle
            else:
                if pos == int(pos):
                    self.ax.plot(pos-y1+h, y1, color=Labels.color_black)
                    self.ax.plot(pos+y2-h, y2, color=Labels.color_black)
                else:
                    self.ax.plot(pos-y1+h, y1, color=Labels.color_cyan)
                    self.ax.plot(pos+y2-h, y2, color=Labels.color_cyan)
        else:
            if linestyle:
                self.ax.plot(pos + y1 - h, y1, color=Labels.color_cyan, linestyle=linestyle)
                self.ax.plot(pos - y2 + h, y2, color=Labels.color_cyan, linestyle = linestyle)
            else :
                if pos == int(pos):
                    self.ax.plot(pos + y1 - h, y1, color=Labels.color_black)
                    self.ax.plot(pos - y2 + h, y2, color=Labels.color_black)
                else:
                    self.ax.plot(pos + y1 - h, y1, color=Labels.color_cyan)
                    self.ax.plot(pos - y2 + h, y2, color=Labels.color_cyan)
                    
    def _plotFishHead(self, **kwargs):
        is_front = kwargs['is_front']
        pos = kwargs['pos']
        if not is_front:
            for i in range(3):
                y1 = np.linspace(0.5 +(i/10), 1, 5)
                y2 = np.linspace(-1, 0.5 +(i/10), 5)
                self.ax.plot(y1 - (i/10) - 1 + pos, y1 , color=Labels.color_black)
                self.ax.plot(-y2 + (i/10) + pos, y2 , color=Labels.color_black)
        
        else:
            
            for i in range(3):
                y1 = np.linspace(0.5 + (i/10), 1, 5)
                y2 = np.linspace(-1, 0.5 + (i/10), 5)
                self.ax.plot(-y1 + (i/10) + 1 + pos, y1 , color=Labels.color_black)
                self.ax.plot(y2 - (i/10) + pos, y2 , color=Labels.color_black)
            
            
    def _plotFishTail(self, **kwargs):
        is_front = kwargs['is_front']
        pos = kwargs['pos']
        
        if not is_front:
            for i in range(3):
                y1 = np.linspace(-0.5 + (i/10), 1, 5)
                y2 = np.linspace(-1, -0.5+ (i/10), 5)
                self.ax.plot(y1 - (i/10) + pos, y1 , color=Labels.color_black)
                self.ax.plot(-y2 + (i/10) - 1 + pos, y2 , color=Labels.color_black)
        
        else:
        
            for i in range(3):
                y1 = np.linspace(-0.5 + (i/10), 1, 5)
                y2 = np.linspace(-1, -0.5 + (i/10), 5)
                self.ax.plot(-y1 + (i/10) + pos, y1 , color=Labels.color_black)
                self.ax.plot(y2 - (i/10) + 1 + pos, y2 , color=Labels.color_black)

    
    
    def _annotate(self, a, b, count):
        if count > 0:
            self.ax.annotate('', xy=(b,-2), xytext=(a,-2), arrowprops=dict(arrowstyle='<->'))
            self.ax.annotate('L'+str(count),xy=(b,-2.5), xytext=((a+b)/2 - 0.15,-2.5) )

        
        
    
