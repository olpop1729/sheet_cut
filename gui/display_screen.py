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
        
        keys = [str(i) for i in range(len(data.keys()))]
        keys = keys[::-1]
        
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
        plt.plot(x, top , color = Labels.color_black)
        plt.plot( x, bot, color = Labels.color_black)
        plt.plot(x, mid , 'b-.', linewidth=1)
        
        plt.annotate('', xy=(position + 5, 0), xytext=(position + 3, 0), 
                     arrowprops=dict(arrowstyle='->'))
        
        plt.xlim(-3, position + 5)
        plt.ylim(-4, 4)
        plt.axis('off')
        
    
    def _plotFm45(self, **kwargs):
        #logic for the plotting goes here inside this function
        pos = kwargs['pos']
        y = np.linspace(-1, 1, 10)
        if kwargs[Labels.linestyle]:
            plt.plot(y+pos, y, color=Labels.color_grey, linestyle=kwargs[Labels.linstyle])
        else:
            if pos - int(pos) == 0:
                plt.plot(y+pos, y, color=Labels.color_black)
            else:
                plt.plot(y+pos, y, color=Labels.color_grey)
             
    
    def _plotFp45(self, **kwargs):
        
        y = np.linspace(-1, 1, 10)
        if kwargs[Labels.linestyle]:
            plt.plot(-y+kwargs[Labels.pos], y, color=Labels.color_grey, linestyle=kwargs[Labels.linestyle])
        else:
            if kwargs[Labels.pos] - int(kwargs[Labels.pos]) == 0:
                plt.plot(-y+kwargs[Labels.pos], y, color=Labels.color_black)
            else:
                plt.plot(-y+kwargs[Labels.pos], y, color=Labels.color_grey)
                
        

    
    def _plotH(self, **kwargs):
        pos = kwargs[Labels.pos]
        kwargs['ax'].add_patch(plt.Circle((pos,0), 0.2,color=Labels.color_green, fill=False))
    
    def _plotV(self, **kwargs):
        pos = kwargs[Labels.pos]
        
        y = np.linspace(0,1, 5)

        plt.plot(-y+pos, y, color = Labels.color_red, linewidth=1)
        plt.plot(y+pos, y, color = Labels.color_red, linewidth=1)
        
    def _plotSplitYoke(self, **kwargs):
        pos = kwargs[Labels.pos]
        y1 = np.linspace(-1, 1, 10)
        y2 = np.linspace(0, 1, 5)
        plt.plot(pos+y2, y2, color=Labels.color_black)
        plt.plot(pos-y1, y1, color=Labels.color_black)
    
    def _plotF0(self, **kwargs):
        linestyle = kwargs[Labels.linestyle]
        pos = kwargs[Labels.pos]
        
        y = np.linspace(-1, 1, 10)
        if linestyle:
            plt.plot([pos]*10, y, color=Labels.cyan, linestyle=linestyle)
        else:
            if pos - int(pos) == 0:
                plt.plot([pos]*10, y, color=Labels.color_black)
            else:
                plt.plot([pos]*10, y, color=Labels.color_cyan)
                
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
        is_front = kwargs['is_front']
        pos = kwargs['pos']
        if not is_front:
            for i in range(3):
                y1 = np.linspace(0.5 +(i/10), 1, 5)
                y2 = np.linspace(-1, 0.5 +(i/10), 5)
                plt.plot(y1 - (i/10) - 1 + pos, y1 , color='black')
                plt.plot(-y2 + (i/10) + pos, y2 , color='black')
        
        else:
            
            for i in range(3):
                y1 = np.linspace(0.5 + (i/10), 1, 5)
                y2 = np.linspace(-1, 0.5 + (i/10), 5)
                plt.plot(-y1 + (i/10) + 1 + pos, y1 , color='black')
                plt.plot(y2 - (i/10) + pos, y2 , color='black')
            
            
    def _plotFishTail(self, **kwargs):
        is_front = kwargs['is_front']
        pos = kwargs['pos']
        
        if not is_front:
            for i in range(3):
                y1 = np.linspace(-0.5 + (i/10), 1, 5)
                y2 = np.linspace(-1, -0.5+ (i/10), 5)
                plt.plot(y1 - (i/10) + pos, y1 , color='black')
                plt.plot(-y2 + (i/10) - 1 + pos, y2 , color='black')
        
        else:
        
            for i in range(3):
                y1 = np.linspace(-0.5 + (i/10), 1, 5)
                y2 = np.linspace(-1, -0.5 + (i/10), 5)
                plt.plot(-y1 + (i/10) + pos, y1 , color='black')
                plt.plot(y2 - (i/10) + 1 + pos, y2 , color='black')

    
    
    def _annotate(self, a, b, count):
        if count > 0:
            plt.annotate('', xy=(b,-2), xytext=(a,-2), arrowprops=dict(arrowstyle='<->'))
            plt.annotate('L'+str(count),xy=(b,-2.5), xytext=((a+b)/2 - 0.15,-2.5) )

        
        
    
