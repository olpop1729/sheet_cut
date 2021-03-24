#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 20 17:39:11 2021

@author: omkar
"""

# user inputs. always keep the case lower. keep the encodings at last
TOOL_HOLE = ['hole','h',0]
TOOL_V_NOTCH = ['v notch', 'vnotch','v',1]
TOOL_P45 = ['full cut +45','+45','45','fp45','p45',2]
TOOL_M45 = ['full cut -45','-45','fm45','m45',3]
TOOL_F0 = ['full cut', '0','0 shear','shear','zero','f0',4]

LIST_NO = ['no', 'n','not', '0','negative','incorrect']
LIST_YES = ['yes', 'y', 'affirmative', 'correct', '1']
#constant machine distances
DISTANCE_HOLE_VNOTCH = 1250
DISTANCE_SHEAR_VNOTCH = 4335

#internal tool names
TOOL_NAME_MAP = {'h':['Hole Punch',DISTANCE_HOLE_VNOTCH,0],
                 'v':['V Notch',DISTANCE_SHEAR_VNOTCH,1],
                 'fm45':['Full Cut -45',2],
                 'fp45':['Full Cut +45',3],
                 'f0':['Full Cut 0',4],
                 'pfr':['Partial Front Right'],
                 'pfl':['Partial Front Left'],
                 'prr':['Partial Rear Right'],
                 'prl':['Partial Rear Left']
                 }
#pretty colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Tool():
    def __init__(self, name=None ,is_front=False, is_rear=False , pos=0 ):
        self.name = name
        self.pos = pos
        self.is_front = is_front
        self.is_rear = is_rear
        self.has_steplap = False
        self.has_lateral_shift = False
        self.is_partial = False
        self.is_open = True
        
    def getIsFront(self):
        if input('Front? (y or n) - ') in LIST_YES:
            self.is_front = True
            return True
        self.is_front = False
        return False
    
    def getIsRear(self):
        if input('Rear? (y or n) - ') in LIST_YES:
            self.is_rear = True
            return True
        self.is_rear = False
        return False
        
    def getHasLateralShift(self):
        if input('Has lateral-shift? (y or n) - ') in LIST_YES:
            self.has_lateral_shift = True
            return True
        self.has_lateral_shift = False
        return False
        
    def getHasStepLap(self):
        if input('Has step-lap? (y or n) - ') in LIST_YES:
            self.has_steplap = True
            return True
        self.has_steplap = False
        return False
        
    def getName(self):
        while True:
            name = input('Enter Tool Name - ')
            if name.lower() in TOOL_HOLE:
                self.name = 'h'
                return
            elif name.lower() in TOOL_V_NOTCH:
                self.name = 'v'
                return
            elif name.lower() in TOOL_P45:
                self.name = 'fp45'
                return
            elif name.lower() in TOOL_M45:
                self.name = 'fm45'
                return
            elif name.lower() in TOOL_F0:
                self.name = 'f0'
                return
            else:
                print(f'{bcolors.WARNING}Incorrect name. Please enter valid name.{bcolors.ENDC}')
                continue
        
        
class JobProfile():
    def __init__(self):
        self.tool_list = []
        self.length_list = []
        self.v_notch_lateral_pos = 0
        self.step_lap_count = 1
        self.step_lap_distance = 0
        self.lateral_shift = 0
        
        
    def getLateralShiftDistance(self):
        while True:
            try:
                self.lateral_shift = int(input('Enter lateral-shift distance - '))
                return
            except Exception as err:
                print(f'{bcolors.WARNING}{err}{bcolors.ENDC}')
            
    
    def getStepLapDistance(self):
        while True:
            try:
                self.step_lap_distance = int(input('Enter step-lap distance - '))
                return
            except Exception as err:
                print(f'{bcolors.WARNING}{err}{bcolors.ENDC}')
        
    def getDistanceList(self):
        while True:
            try:
                self.length_list = [int(i) for i in input('Enter l_i - ').split()]
                return
            except Exception as err:
                print(f'{bcolors.WARNING}{err}{bcolors.ENDC}')
                
    def getStepLapCount(self):
        while True:
            try:
                self.step_lap_count = int(input('Enter step-lap count - '))
            except Exception as err:
                print(f'{bcolors.WARNING}{err}{bcolors.ENDC}')
                
    def getToolList(self):
        while True:
            cli_input = input('Add tool? (y or n) - ')
            if cli_input not in LIST_NO:
                temp_tool = Tool()
                temp_tool.getName()
                temp_tool.getIsFront()
                temp_tool.getIsRear()
                if temp_tool.getHasStepLap():
                    self.getStepLapCount()
                    self.getStepLapDistance()
                if not temp_tool.has_steplap:
                    if temp_tool.getHasLateralShift():
                        self.getLaterShiftCount()
                        self.getLateralShiftDistance()
            else:
                break
            
    def updateLengthList(self):
        indices = []
        out = []
        if self.step_lap_count > 1:
            for i in range(len(self.tool_list)):
                if self.tool_list[i].is_front:
                    indices.append(i)
                if self.tool_list[i].is_rear:
                    indices.append(i-1)
            for i in self.step_lap_count:
                for j in range(len(self.length_list)):
                    if j in indices:
                        out.append(self.length_list[j] - i * self.step_lap_distance)
            self.length_list = out

    def showToolPositions(self):
        for i in self.tool_list:
            print(f'{i.longname()} - {i.pos}')
        
    
jp = JobProfile()
jp.getToolList()
jp.getDistanceList()
                
            