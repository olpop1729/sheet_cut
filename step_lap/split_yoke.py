#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 23:20:23 2021

@author: omkar
"""
import os
import pandas as pd

class YokeSplitter:
    
    def __init__(self):
        self.name = 'ys'
        self.pos = 0
        self.slp_count = 1
        self.slp_distance = 0
        self.slp_vector = []
        self.slp_counter = 0
        self.front_open = False
        
    def lengthyfy(self):
        return 0
    
    def hasStepLap(self) -> bool:
        if self.slp_count > 1:
            return True
        return False
        
    def getSlpCount(self):
        self.slp_count = int(input('Enter step-lap count :'))
        
    def getSlpDistance(self):
        self.slp_distance = float(input('Enter step-lap distance : '))
        
    def generateSlpVector(self):
        n = self.slp_count
        d = self.slp_distance
        self.slp_vector = [i*d for i in range(n//2, -n//2,-1)]
        if self.front_open:
            self.slp_counter = 0
        else:
            self.slp_counter = n-1
        
    def incrementSlpCounter(self):
        if self.front_open:
            self.slp_counter += 1
            self.slp_counter %= self.slp_count
        else:
            self.slp_counter -= 1
            self.slp_counter %= self.slp_count
    
    def getFrontOpen(self):
        if input('Front open : ').lower() in ['y',  'yes']:
            self.front_open = True
        else:
            self.front_open = False
            

class Fm45:
    
    def __init__(self):
        self.name = 'fm45'
        self.pos = 0
        self.slp_count = 1
        self.slp_distance = 0
        self.slp_vector = []
        self.slp_counter = 0
        self.open = False
        
    def lengthyfy(self):
        return 0
    
    def hasStepLap(self) -> bool:
        if self.slp_count > 1:
            return True
        return False
    
    def getOpen(self):
        if input('Open ? : ').lower() in ['y', 'yes']:
            self.open = True
        else:
            self.open = False
        
    def getSlpCount(self):
        self.slp_count = int(input('Enter step-lap count :'))
        
    def getSlpDistance(self):
        self.slp_distance = float(input('Enter step-lap distance : '))
        
    def generateSlpVector(self):
        n = self.slp_count
        d = self.slp_distance
        self.slp_vector = [i*d for i in range(n//2, -n//2,-1)]
        if self.open:
            self.slp_counter = 0
        else:
            self.slp_counter = n-1
    
    def incrementSlpCounter(self):
        if self.open:
            self.slp_counter += 1
            self.slp_counter %= self.slp_count
        else:
            self.slp_counter -= 1
            self.slp_counter %= self.slp_count   
                
class Fp45:
    
    def __init__(self):
        self.name = 'fp45'
        self.pos = 0
        self.slp_count = 1
        self.slp_distance = 0
        self.slp_vector = []
        self.slp_counter = 0
        self.open = False
        
    def lengthyfy(self):
        return 0
    
    def hasStepLap(self) -> bool:
        if self.slp_count > 1:
            return True
        return False
    
    def getOpen(self):
        if input('Open ? : ').lower() in ['y', 'yes']:
            self.open = True
        else:
            self.open = False
        
    def getSlpCount(self):
        self.slp_count = int(input('Enter step-lap count :'))
        
    def getSlpDistance(self):
        self.slp_distance = float(input('Enter step-lap distance : '))
        
    def generateSlpVector(self):
        n = self.slp_count
        d = self.slp_distance
        self.slp_vector = [i*d for i in range(n//2, -n//2,-1)]
        if self.open:
            self.slp_counter = 0
        else:
            self.slp_counter = n-1
    
    def incrementSlpCounter(self):
        if self.open:
            self.slp_counter += 1
            self.slp_counter %= self.slp_count
        else:
            self.slp_counter -= 1
            self.slp_counter %= self.slp_count
            
class Hole:
    
    def __init__(self):
        self.name = 'h'
        self.pos = 0
        
    def lengthyfy(self):
        return 0
    
    def hasStepLap(self) -> bool:
        return False
    
class JobProfile:
    
    def __init__(self):
        self.getToolList()
        
    def getToolList(self):
        
        tool_list = []
        counter = 0
        while counter < 2:
            tool_name = input('Enter tool name : ')
            if tool_name=='fp45':
                counter+=1
                tool = Fp45()
                tool.getSlpCount()
                if tool.hasStepLap():
                    tool.getSlpDistance()
                    tool.getOpen()
                    tool.generateSlpVector()
                
            elif tool_name == 'fm45':
                counter += 1
                tool = Fm45()
                tool.getSlpCount()
                if tool.hasStepLap():
                    tool.getSlpDistance()
                    tool.getOpen()
                    tool.generateSlpVector()

            elif tool_name == 'h':
                tool = Hole()
                
            elif tool_name == 'ys':
                tool = YokeSplitter()
                tool.getSlpCount()
                if tool.slp_count > 1:
                    tool.getSlpDistance()
                    tool.getFrontOpen()
                    tool.generateSlpVector()
                    
            else :
                print('Invalid tool name.')
                continue
                
            tool_list.append(tool)
            
        if tool_list[0].name != tool_list[-1].name:
            print('Start tool - end tool mismatch. Aborting ...')
            os.exit()
        self.tool_list = tool_list
        
    def getLengthList(self):
        self.length_list = [float(i) for i in input('Enter lengths : ').split()]
        
    def getLayers(self):
        self.layers = int(input('Enter no. of layers : '))
        
    def updateLengths(self):
        slp = max([i.slp_count for i in self.tool_list if i.hasStepLap()])
        ll = []
        for i in range(slp):
            for j in range(len(self.length_list)):
                curr = self.tool_list[j]
                if curr.hasStepLap():
                    if isinstance(curr, YokeSplitter):
                        ll[-1][1] += curr.slp_vector[curr.slp_counter]
                        ll.append([curr.name, self.length_list[j] - curr.slp_vector[curr.slp_counter]])
                        curr.incrementSlpCounter()
                        
                    elif isinstance(curr, Fm45) or isinstance(curr, Fp45):
                        ll.append([curr.name, self.length_list[j] + curr.slp_vector[curr.slp_counter]])
                        curr.incrementSlpCounter()
                else:
                    ll.append([curr.name, self.length_list[j]])
                
                if j == len(self.length_list) - 1:
                    curr = self.tool_list[j+1]
                    if curr.hasStepLap():
                        if isinstance(curr, Fm45) or isinstance(curr, Fp45):
                            ll[-1][1] += curr.slp_vector[curr.slp_counter]
                            curr.incrementSlpCounter()
                
            #ll = self.layers
        print('executable len')
        print(ll)
        print('-------')
        self.exe_l = ll
        
    def execute(self):
        exe = []
        pos = 0
        for i in self.exe_l:
            if i[0] == 'h':
                exe.append([i[0], pos + 1250])
            elif i[0] == 'ys':
                exe.append(['fp45', pos + 4335])
                exe.append(['v', pos])
            elif i[0][0] == 'f':
                exe.append([i[0], pos + 4335])
                
            pos += i[1]
        self.pl = pos
        print(exe)
        terminate = 300
        
        operation = []
        feed = []
        while terminate > 0:
            closest_cut = min([i[1] for i in exe])
            repeat = False
            for i in exe:
                if i[1] == closest_cut:
                    operation.append(i[0])
                    i[1] = jp.pl
                    
                    if repeat:
                        feed.append(0)
                    else:
                        feed.append(closest_cut)
                        repeat = True
                else:
                    i[1] -= closest_cut
                    
            terminate -= 1
        data = list(zip(operation, feed))
        df = pd.DataFrame(data = data, columns=['feed', 'operation'])
        df.to_csv('../cut_program_output/split_yoke.csv')
        
jp = JobProfile()
jp.getLengthList()
jp.getLayers()
jp.updateLengths()
jp.execute()
        
                
                
                