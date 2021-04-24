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
    
    def __init__(self, name, path):
        self.path = path
        self.data = self.getData(name)
        
    def getData(self, name):
        data = {}
        with open(self.path+name) as file:
            data = json.load(file)
        if data:
            return data
        print('Unable to load data. Data object empty.')
        sys.exit()
        

def listCutPrograms(path):
    names = [i for i in listdir(path) if i.endswith('json')]
    for i in range(len(names)):
        print(f'{i+1} - {names[i]}')
    return names


def plotYokeSplitter(pos):
    y1 = np.linspace(-1, 1, 10)
    y2 = np.linspace(0, 1, 5)
    plt.plot(pos+y2, y2, color='black')
    plt.plot(pos-y1, y1, color='black')

def plotSpear(is_front, pos, h=0,linestyle = None):
    y1 = np.linspace(h, 1, 5)
    y2 = np.linspace(-1, h, 5)
    if not is_front:
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
            

            

def plotFm45(pos, linestyle=None):
    y = np.linspace(-1, 1, 10)
    if linestyle:
        plt.plot(y+pos, y, color='cyan', linestyle=linestyle)
    else:
        if pos - int(pos) == 0:
            plt.plot(y+pos, y, color='black')
        else:
            plt.plot(y+pos, y, color='cyan')
    
def plotFp45(pos, linestyle=None):
    y = np.linspace(-1, 1, 10)
    if linestyle:
        plt.plot(-y+pos, y, color='cyan', linestyle=linestyle)
    else:
        if pos - int(pos) == 0:
            plt.plot(-y+pos, y, color='black')
        else:
            plt.plot(-y+pos, y, color='cyan')
            
def plotF0(pos, linestyle=None):
    y = np.linspace(-1, 1, 10)
    if linestyle:
        plt.plot([pos]*10, y, color='cyan', linestyle=linestyle)
    else:
        if pos - int(pos) == 0:
            plt.plot([pos]*10, y, color='black')
        else:
            plt.plot([pos]*10, y, color='cyan')
    
def plotVnotch(pos,ls=0, linestyle=None):
    y = np.linspace(0 + ls,1, 5)
    if ls != 0:
        if linestyle:
            
            plt.plot(-y+pos, y, color = 'cyan', linestyle='dotted')
            plt.plot(y+pos, y, color = 'cyan', linestyle='dotted')
        else:
            plt.plot(-y+pos, y, color = 'cyan', linewidth=1)
            plt.plot(y+pos, y, color = 'cyan', linewidth=1)
            
    else:
        plt.plot(-y+pos, y, color = 'black', linewidth=1)
        plt.plot(y+pos, y, color = 'black', linewidth=1)
    
def plotHole(pos, ax):
    ax.add_patch(plt.Circle((pos,0), 0.2,color='black', fill=False))
    
def annotate(a, b, count):
    if count > 0:
        plt.annotate('', xy=(b,-2), xytext=(a,-2), arrowprops=dict(arrowstyle='<->'))
        plt.annotate('L'+str(count),xy=(b,-2.5), xytext=((a+b)/2 - 0.15,-2.5) )
        
def main(path=None):
    while 1:
        names = listCutPrograms(path)
        file_index = input('\n Enter index (q to exit): ')
        if file_index == 'q':
            print('Bye ...')
            return
            #sys.exit()
        file_index = int(file_index)
        x = [i for i in range(100)]
        top = [1]*100
        bot = [-1]*100
        mid = [0]*100
        cp = CutProgram(names[file_index-1], path)
        data = cp.data
        
        width = len(data.keys())
        fig, ax = plt.subplots(figsize=(width+3, 5))
        pos, prev = 0, 0
        for i in range(len(data.keys())):
            prev = pos
            pos = 3*i + 2
            curr_tool = data[str(i)]
            if curr_tool['name'] == 'fm45':
                if curr_tool['step_lap_count'] > 1:
                    if curr_tool['is_front'] and not curr_tool['is_rear']:
                        if curr_tool['front_open']:
                            plotFm45(pos - 0.2)
                            plotFm45(pos - 0.4)
                        else:
                            plotFm45(pos + 0.2, 'dotted')
                            plotFm45(pos + 0.4, 'dotted')
                    elif curr_tool['is_rear'] and not curr_tool['is_front']:
                        if curr_tool['rear_open']:
                            plotFm45(pos + 0.2)
                            plotFm45(pos + 0.4)
                        else:
                            plotFm45(pos - 0.2, 'dotted')
                            plotFm45(pos - 0.4, 'dotted')
                    elif curr_tool['is_front'] and curr_tool['is_rear']:
                        if curr_tool['front_open']:
                            plotFm45(pos + 0.2)
                            plotFm45(pos + 0.4)
                        else:
                            plotFm45(pos + 0.2, 'dotted')
                            plotFm45(pos + 0.4, 'dotted')
                        if curr_tool['rear_open']:
                            plotFm45(pos - 0.2)
                            plotFm45(pos - 0.4)
                        else:
                            plotFm45(pos - 0.2, 'dotted')
                            plotFm45(pos - 0.4, 'dotted')
                plotFm45(pos)
                
            elif curr_tool['name'] == 'fp45':
                if curr_tool['step_lap_count'] > 1:
                    if curr_tool['is_front'] and not curr_tool['is_rear']:
                            if curr_tool['front_open']:
                                plotFp45(pos - 0.2)
                                plotFp45(pos - 0.4)
                            else:
                                plotFp45(pos + 0.2, 'dotted')
                                plotFp45(pos + 0.4, 'dotted')
                    elif curr_tool['is_rear'] and not curr_tool['is_front']:
                        if curr_tool['rear_open']:
                            plotFp45(pos + 0.2)
                            plotFp45(pos + 0.4)
                        else:
                            plotFp45(pos - 0.2, 'dotted')
                            plotFp45(pos - 0.4, 'dotted')
                    elif curr_tool['is_front'] and curr_tool['is_rear']:
                        if curr_tool['front_open']:
                            plotFp45(pos + 0.2)
                            plotFp45(pos + 0.4)
                        else:
                            plotFp45(pos + 0.2, 'dotted')
                            plotFp45(pos + 0.4, 'dotted')
                        if curr_tool['rear_open']:
                            plotFp45(pos - 0.2)
                            plotFp45(pos - 0.4)
                        else:
                            plotFp45(pos - 0.2, 'dotted')
                            plotFp45(pos - 0.4, 'dotted')
                plotFp45(pos)
                
                
            elif curr_tool['name'] == 'v':
                if curr_tool['lateral_shift_count'] > 1:
                    if curr_tool['is_open']:
                        plotVnotch(pos, 0.1)
                        plotVnotch(pos, 0.2)
                    else:
                        plotVnotch(pos, 0.1, 'dotted')
                        plotVnotch(pos, 0.2, 'dotted')
                        
                plotVnotch(pos)
                
                
            elif curr_tool['name'] == 'f0':
                if curr_tool['step_lap_count'] > 1:
                    if curr_tool['is_front'] and not curr_tool['is_rear']:
                            if curr_tool['front_open']:
                                plotF0(pos - 0.2)
                                plotF0(pos - 0.4)
                            else:
                                plotF0(pos + 0.2, 'dotted')
                                plotF0(pos + 0.4, 'dotted')
                    elif curr_tool['is_rear'] and not curr_tool['is_front']:
                        if curr_tool['rear_open']:
                            plotF0(pos + 0.2)
                            plotF0(pos + 0.4)
                        else:
                            plotF0(pos - 0.2, 'dotted')
                            plotF0(pos - 0.4, 'dotted')
                    elif curr_tool['is_front'] and curr_tool['is_rear']:
                        if curr_tool['front_open']:
                            plotF0(pos + 0.2)
                            plotF0(pos + 0.4)
                        else:
                            plotF0(pos + 0.2, 'dotted')
                            plotF0(pos + 0.4, 'dotted')
                        if curr_tool['rear_open']:
                            plotF0(pos - 0.2)
                            plotF0(pos - 0.4)
                        else:
                            plotF0(pos - 0.2, 'dotted')
                            plotF0(pos - 0.4, 'dotted')
                plotF0(pos)
                
                
            elif curr_tool['name'] == 'h':
                plotHole(pos, ax)
            annotate(prev, pos, i)
                
        plt.plot(x, top , color = 'black')
        plt.plot( x, bot, color = 'black')
        plt.plot(x, mid , 'b-.', linewidth=1)
        
        plt.annotate('', xy=(-1,0), xytext=(-2,0), arrowprops=dict(arrowstyle='<-'))
        
        plt.xlim(-3, pos+3)
        plt.ylim(-4,4)
        plt.axis('off')
        plt.show()
    return
        
        
def main2(path):
    while 1:
        names = listCutPrograms(path)
        file_index = input('\n Enter index (q to exit): ')
        if file_index == 'q':
            print('Bye ...')
            return
            #sys.exit()
        file_index = int(file_index)
        x = [i for i in range(100)]
        top = [1]*100
        bot = [-1]*100
        mid = [0]*100
        cp = CutProgram(names[file_index-1], path)
        data = cp.data
        
        width = len(data.keys())
        fig, ax = plt.subplots(figsize=(width+3, 5))
        pos, prev, front_c = 0, 0, 0
        for i in range(len(data.keys())):
            prev = pos
            pos = 3*i + 2
            ct = data[str(i)]
            if ct['name'] == 'fm45':
                plotFm45(pos)
                if ct['slp_count'] > 1:
                    if ct['open']:
                        if front_c == 0:
                            front_c+=1
                            plotFm45( pos - 0.2 )
                            plotFm45(pos - 0.4)
                        else :
                            plotFm45( pos + 0.2 )
                            plotFm45(pos + 0.4)
                    else:
                        if front_c == 0:
                            front_c+=1
                            plotFm45(pos + 0.2, 'dotted')
                            plotFm45(pos + 0.4, 'dotted')
                        else:
                            plotFm45(pos - 0.2, 'dotted')
                            plotFm45(pos - 0.4, 'dotted')
                            
            elif ct['name'] == 'fp45':
                plotFp45(pos)
                if ct['slp_count'] > 1:
                    if ct['open']:
                        if front_c == 0:
                            plotFp45( pos - 0.2 )
                            plotFp45(pos - 0.4)
                        else :
                            plotFp45( pos + 0.2 )
                            plotFp45(pos + 0.4)
                    else:
                        if front_c == 0:
                            plotFp45(pos + 0.2, 'dotted')
                            plotFp45(pos + 0.4, 'dotted')
                        else:
                            plotFp45(pos - 0.2, 'dotted')
                            plotFp45(pos - 0.4, 'dotted')
                            
            elif ct['name'] == 's':
                if ct['step_lap_count'] > 1:
                    if ct['is_open']:
                        if ct['is_front']:
                            plotSpear(True, pos)
                            plotSpear(True, pos + 0.2)
                            plotSpear(True, pos + 0.4)
                        else:
                            plotSpear(False, pos)
                            plotSpear(False, pos - 0.2)
                            plotSpear(False, pos - 0.4)
                    else:
                        if ct['is_front']:
                            plotSpear(True, pos)
                            plotSpear(True, pos + 0.2, linestyle='dotted')
                            plotSpear(True, pos + 0.4, linestyle='dotted')
                        else:
                            plotSpear(False, pos)
                            plotSpear(False, pos - 0.2, linestyle='dotted')
                            plotSpear(False, pos - 0.4, linestyle='dotted')
                            
            elif ct['name'] == 'ys':
                plotYokeSplitter(pos)
                
            elif ct['name'] == 'h':
                plotHole(pos, ax)
            annotate(prev, pos, i)
        plt.plot(x, top , color = 'black')
        plt.plot( x, bot, color = 'black')
        plt.plot(x, mid , 'b-.', linewidth=1)
        
        plt.annotate('', xy=(-1,0), xytext=(-2,0), arrowprops=dict(arrowstyle='<-'))
        
        plt.xlim(-3, pos+3)
        plt.ylim(-4,4)
        plt.axis('off')
        plt.show()
    return

                    
                
if __name__ == "__main__":
    while 1:
        print('1 - Simple step-lap')
        print('2 - Central Limb')
        print('3 - Split yoke')
        opt = input('Enter option : ')
        if opt == '1':
            
            main('../cut_program_input/')
            
        elif opt == '2':
            main2('../cut_program_input/central_limb/')
            
        elif opt == '3':
            main2('../cut_program_input/split_yoke/')
        elif opt == 'q':
            break