#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 23:09:40 2021

@author: omkar
"""

import pandas as pd 
import os

class PandasModule():
    def __init__(self):
        self.file_name = ''
        
    def checkFileName(self, name):
        pass
            
    
class JobProfile():
    def __init__(self):
        self.pattern_length = 0
        self.step_lap_count = 1
        self.k = 0
        self.step_lap_distance = 0
        self.tool_list = []
        self.length_list = []
        self.fish_len = 0
        self.hole = []
            
    
    def getStepLapInfo(self):
        self.step_lap_count = int(input('Enter step-lap count : '))
        self.k = self.step_lap_count // 2
        self.step_lap_distance = float(input('Enter step-lap distance : '))
        
    def getLengthList(self):
        self.length_list = [int(i) for i in input('Enter lengths : ').split()]
        self.fish_len = sum(self.length_list)
        self.createHoleList()
        
    def createHoleList(self):
        pos = 0
        ret = []
        if len(self.length_list) > 1:
            for i in range(len(self.length_list)-1):
                pos = pos + self.length_list[i]
                ret.append(pos)
        self.hole = ret
    
    def createDict(self):
        exe = []
        self.pattern_length = self.step_lap_count*(self.fish_len + (self.step_lap_count - 1)*self.step_lap_distance )
        for i in range(self.step_lap_count):
            if len(self.hole) > 0:
                for j in self.hole:
                    exe.append(['h', j + (2*self.k - i + 2*self.k*i)*self.step_lap_distance + i*self.fish_len])
            exe.append(['fm45', i*self.fish_len + (3+i)*self.k*self.step_lap_distance])
            exe.append(['fp45',(i+1)*self.fish_len + (3+i)*self.k*self.step_lap_distance])
            exe.append(['v', i*(self.fish_len + (self.step_lap_count - 1) * self.step_lap_distance)])
        self.exe = exe
        
    def execute(self):
        for i in self.exe:
            if i[0][0] == 'f':
                i[1] += 4335
            elif i[0] == 'h':
                i[1] += 1250
        terminate = 100
        feed = []
        vaxis = []
        operation = []
        while terminate > 0:
            terminate -= 1
            close = min([i[1] for i in self.exe])
            repeat = False
            
            for i in self.exe:
                if i[1] == close:
                    if i[0] == 'v':
                        vaxis.append(self.k * self.step_lap_distance)
                    else:
                        vaxis.append(0)
                    if repeat:
                        feed.append(0)
                    else:
                        feed.append(close)
                    operation.append(i[0])
                    i[1] = self.pattern_length
                    repeat = True
                else:
                    i[1] -= close
        cut_feed = list(zip(feed, vaxis,operation))
        df = pd.DataFrame(data = cut_feed, columns=['Feed','V-Axis','Operation'])
        df.index += 1
        temp = pd.ExcelWriter('../cut_program_output/FishyFish_0.xlsx')
        df.to_excel(temp)
        temp.save()
        
jp = JobProfile()
jp.getStepLapInfo()
jp.getLengthList()
jp.createDict()
# for i in sorted(jp.exe, key = lambda x: x[1]):
#     print(i[0], '--', i[1])
jp.execute()
