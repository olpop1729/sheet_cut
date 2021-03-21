#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 15:48:55 2021

@author: omkar
"""
#import pandas as pd
import copy as cp

# user inputs. always keep the case lower. keep the encodings at last
TOOL_HOLE = ['hole','h',0]
TOOL_V_NOTCH = ['v notch', 'vnotch','v',1]
TOOL_P45 = ['full cut +45','+45','45','fp45','p45',2]
TOOL_M45 = ['full cut -45','-45','fm45','m45',3]
TOOL_F0 = ['full cut', '0','0 shear','shear','zero','f0',4]

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

class JobProfile():
    
    def __init__(self,operation_list=None,step_lap=1,lateral_shift=1):
        self.operation_list = operation_list
        self.has_steplap = step_lap
        self.has_lateral_shift = lateral_shift
        self.coil_start_distance = 0 # coil start position w.r.t. v notch
        self.sheet_counter = 0
        self.layers = 1
        self.pattern_length = 0
        self.l_i = []
        
    def makeToolDistances(self):
        self.l_i = [i for i in operation_list if i.next_tool_distance is not None]
        
    def printJobProfile(self):
        for i in self.operation_list:
            print('**************')
            i.prettyPrintObject()
        
    def incrementSheetCounter(self):
        self.sheet_counter += 1
        
    def updateProfile(self):
        new_profile_operations = []
        if self.has_steplap:
            for i in range( self.has_steplap ):                
                for i in self.operation_list:
                    temp_tool = i.copyTool()
                    if i.hasStepLap():
                        i.incrementStepLapCounter()
                        i.next_tool_distance += -self.step_lap_vector[i.step_lap_counter]
                    new_profile_operations.append(temp_tool)
                    del temp_tool
            self.operation_list = new_profile_operations
            del new_profile_operations
        
    def updatePositions(self):
        position = 0
        for i in self.operation_list:
            i.pos = position
            if not i.next_tool_distance:
                break
            position += i.next_tool_distance
        return position
        
    def initializeDistances(self):
        for i in self.operation_list:
            if i.name == 'h':
                i.pos += DISTANCE_HOLE_VNOTCH + self.coil_start_distance
            elif i.name == 'v':
                i.pos += self.coil_start_distance
            elif i.name[0] == 'f' or i.name[0] == 'p':
                i.pos += DISTANCE_SHEAR_VNOTCH + self.coil_start_distance
                
    
    def execute(self):
        pass

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
    def __init__(self,next_tool_distance=None, step_lap_count=1):
        self.next_tool_distance = next_tool_distance
        self.is_open = False
        self.name = None
        self.step_lap_count = step_lap_count
        self.step_lap_distance = 0
        self.step_lap_counter = 0
        self.step_lap_vector = []
        self.tipcut_width = 0
        self.lateral_shift_count = 0
        self.lateral_shift_vector = []
        self.lateral_shift_counter = 0
        self.lateral_shift_distance = 0
        self.pos = 0
        self.active = True
    
    def incrementStepLapCounter(self):
        self.step_lap_counter += 1
        self.step_lap_counter = (self.step_lap_counter % self.step_lap_count)
                
    def longname(self):
        return TOOL_NAME_MAP[self.name][0]
    
#generators
    def generateStepLapVector(self):
        if self.step_lap_count > 1:
            for i in range( self.step_lap_count ):
                self.step_lap_vector.append( i * self.step_lap_distance )
                
    def generateLateralShiftVector(self):
        if self.lateral_shift_count > 1:
            for i in range( self.lateral_shift_count ):
                self.lateral_shift_vector.append( i * self.lateral_shift_distance )
#utilities                
    def isPartial(self):
        if self.name[0] == 'p':
            return True
        return False
    
    def hasStepLap(self):
        if self.step_lap_count > 1:
            return True
        return False
    
    def hasLateralShift(self):
        if self.lateral_shift_count > 1:
            return True
        return False

    def prettyPrintObject(self):
        pp = vars(self)
        for key in pp.keys():
            print( f'{key} : {pp[key]}' )
    
 # get user inputs   
        
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
                print(f'{bcolors.OKCYAN}Incorrect name. Please enter valid name.{bcolors.ENDC}')
                continue
            
    def getNextToolDistance(self):
        while True:
            next_tool_distance = input('Enter distance to next tool - ')
            if next_tool_distance.lower() == 'na':
                self.next_tool_distance = None
                return
            try:
                self.next_tool_distance = float(next_tool_distance)
                return
            except ValueError:
                print(f'{bcolors.OKCYAN}Please enter a valid distance value.{bcolors.ENDC}')
                continue
                
    def getStepLapCount(self):
        while True:
            step_lap_count = input('Enter step-lap count - ')
            if step_lap_count.lower() in ['na','\n',' ', None, '0', '1']:
                self.step_lap_count = 1
                return
            else:
                try:
                    temp = int(step_lap_count)
                    if temp % 2 == 1:
                        self.step_lap_count = temp
                    else:
                        raise(ValueError)
                    return
                except ValueError:
                    print( f'{bcolors.OKCYAN}Please enter a valid step-lap count.{bcolors.ENDC}')
                    
    def getStepLapDistance(self):
        while True:
            step_lap_distance = input('Enter step-lap distance - ')
            try:
                self.step_lap_distance = int(step_lap_distance)
                return
            except ValueError:
                print( f'{bcolors.OKCYAN}Please enter a valid step-lap distance.{bcolors.ENDC}' )
                continue
    
    def getIsOpen(self):
        is_open = input('Step-lap open ? (y or n) - ')
        if is_open.lower() in ['y','yes','1']:
            self.is_open = True
        else:
            self.is_open = False
        
    def getLateralCount( self) :
        while 1:
            lateral_count = input( 'Enter lateral count - ' )
            if lateral_count in [ 'na', 'n', '0', '1' ]:
                self.lateral_shift_count = 1
                return
            else:
                try:
                    temp = int( lateral_count )
                    if temp % 2 == 1:
                        self.lateral_shift_count = temp
                        return
                    else:
                        raise(ValueError)
                    return
                except ValueError:
                    print( f'{bcolors.OKCYAN}Please enter a valid later count.{bcolors.ENDC}' )
                    continue


    def getLateralShiftDistance( self ):
        while 1:
            lateral_shift_distance = input( 'Enter lateral shift distance - ' )
            try:
                self.lateral_shift_distance = int( lateral_shift_distance )
                return
            except ValueError:
                print( f'{bcolors.OKCYAN}Please enter a valid lateral-shift distance.{bcolors.ENDC}' )
                continue
            
    def copyTool(self):
        return cp.deepcopy(self)
## main block

# get inputs from user

operation_list = []

while True:
    cli_input = input('Add tool? (y or n) - ')
    if cli_input.lower() not in [ 'quit', 'q', 'exit', 'n', 'no', 'not']:
        tool = Tool()
        tool.getName()
        tool.getNextToolDistance()
        tool.getStepLapCount()
        
        if tool.hasStepLap():
            tool.getStepLapDistance()
            tool.generateStepLapVector()
            
        tool.getLateralCount()
        
        if tool.hasLateralShift():
            tool.getLateralShiftDistance()
            tool.generateLateralShiftVector()
        operation_list.append(tool)
        del tool
        continue
    else :
        break
        

#test inputs

# count = 1
# for i in operation_list:
#     print( f'Tool no - {count}' )
#     i.prettyPrintObject()
#     print( '********************' )
#     count += 1

#the job profile variable

test_profile = JobProfile(operation_list)
test_profile.initializeDistances()
test_profile.execute()
test_profile.makeToolDistances()
test_profile.printJobProfile()


#initial distances
# position = 0
# for i in operation_list:
#     i.pos = position
#     if not i.next_tool_distance:
#         break
#     position += i.next_tool_distance
    
#pattern_length = position

#check positions
# for i in operation_list:
#     print(i.pos)














