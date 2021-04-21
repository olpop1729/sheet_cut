#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 20:33:25 2021

@author: omkar
"""

import matplotlib.pyplot as plt
import json
import numpy as np
import sys
from os import listdir

class CutProgram:
    
    def __init__(self, name):
        self.data = self.getData(name)
        
    def getData(self, name):
        data = {}
        with open('../cut_program_input/'+name) as file:
            data = json.load(file)
        if data:
            return data
        print('Unable to load data. Data object empty.')
        sys.exit()
        

def listCutPrograms():
    names = [i for i in listdir('../cut_program_input/') if i.endswith('json')]
    for i in range(len(names)):
        print(f'{i+1} - {names[i]}')
    return names

def plotFm45(pos):
    y = np.linspace(-1, 1, 10)
    plt.plot(y+pos, y, color='blue')
    
def plotFp45(pos):
    y = np.linspace(-1, 1, 10)
    plt.plot(-y+pos, y, color='blue')
    
def plotF0(pos):
    y = np.linspace(-1, 1, 10)
    plt.plot(pos, y, color='blue')
    
def plotVnotch(pos):
    y = np.linspace(0,1, 5)
    plt.plot(-y+pos, y, color = 'blue', linewidth=1)
    plt.plot(y+pos, y, color = 'blue', linewidth=1)
    
def plotHole(pos, ax):
    ax.add_patch(plt.Circle((pos,0), 0.2,color='blue', fill=False))
    
def annotate(a, b, count):
    if count > 0:
        plt.annotate('', xy=(b,-2), xytext=(a,-2), arrowprops=dict(arrowstyle='<->'))
        plt.annotate('L'+str(count),xy=(b,-2.5), xytext=((a+b)/2 - 0.15,-2.5) )
        
def main():
    while 1:
        names = listCutPrograms()
        file_index = int(input('\n Enter index (q to exit): '))
        if file_index == 'q':
            print('Bye ...')
            sys.exit()
        x = [i for i in range(100)]
        top = [1]*100
        bot = [-1]*100
        mid = [0]*100
        fig, ax = plt.subplots()
        cp = CutProgram(names[file_index-1])
        data = cp.data
        pos, prev = 0, 0
        for i in range(len(data.keys())):
            prev = pos
            pos = 3*i + 1
            curr_tool = data[str(i)]
            if curr_tool['name'] == 'fm45':
                plotFm45(pos)
            elif curr_tool['name'] == 'fp45':
                plotFp45(pos)
            elif curr_tool['name'] == 'v':
                plotVnotch(pos)
            elif curr_tool['name'] == 'f0':
                plotF0(pos)
            elif curr_tool['name'] == 'h':
                plotHole(pos, ax)
            annotate(prev, pos, i)
                
        plt.plot(x, top , color = 'black')
        plt.plot( x, bot, color = 'black')
        plt.plot(x, mid , 'b-.', linewidth=1)
        plt.xlim(0, pos+1)
        plt.ylim(-4,4)
        plt.show()
                
                
if __name__ == "__main__":
    main()