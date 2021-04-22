#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 15:13:34 2021

@author: omkar
"""

#assuming compliance with compatible endings.
import os
import json

class Config:
    DISTANCE_HOLE_VNOTCH = 1250
    DISTANCE_SHEAR_VNOTCH = 4335
    COIL_LENGTH = 4000000
    CUT_PROGRAM_OUTPUT_DIRECTORY = '../cut_program_output'
    COIL_START_POSITION = 0 # w.r.t. V_Notch.
    OUTPUT_FILE_NAME = 'CutFeed_'
    LIST_NO = ['no', 'n','not', '0','negative','incorrect']
    LIST_YES = ['yes', 'y', 'affirmative', 'correct', '1']
    SHEET_SEPERATORS = ['fish', 'fm45', 'fp45', 's', 'f0']
    TOOL_NAME_MAP = {'h':['Hole Punch', DISTANCE_HOLE_VNOTCH,2],
                     'v':['V Notch', DISTANCE_SHEAR_VNOTCH,1],
                     'fm45':[f'Full Cut -45{chr(176)}',4],
                     'fp45':[f'Full Cut +45{chr(176)}',3],
                     'f0':[f'Full Cut 0{chr(176)}',5],
                     'pfrm45':[f'Partial Front Right -45{chr(176)}'],
                     'pfr0':[f'Partial Front Right 0{chr(176)}'],
                     'pflp45':[f'Partial Front Left +45{chr(176)}'],
                     'pfl0':[f'Partial Front Left 0{chr(176)}'],
                     'prrp45':[f'Partial Rear Right +45{chr(176)}'],
                     'prr0':[f'Partial Rear Right 0{chr(176)}'],
                     'prlm45':[f'Partial Rear Left -45{chr(176)}'],
                     'prl0':[f'Partial Rear Left 0{chr(176)}']
                     }
    TOOL_DISTANCE_MAP = {'h':DISTANCE_HOLE_VNOTCH + COIL_START_POSITION,
                         'v':COIL_START_POSITION,
                         'fm45':DISTANCE_SHEAR_VNOTCH + COIL_START_POSITION,
                         'fp45':DISTANCE_SHEAR_VNOTCH + COIL_START_POSITION,
                         'f0': DISTANCE_SHEAR_VNOTCH + COIL_START_POSITION
                         }

class Names:
    HOLE = 'h'
    V_NOTCH = 'v'
    FP45 = 'fp45'
    FM45 = 'fm45'
    F0 = 'f0'
    FISH = 'fish'
    SPEAR = 's'
    
class Labels:
    get_h_step_lap_count = 'Enter horizontal step-lap count : '
    
    negative_step_count = 'Step count cannot be negative or zero.'
    
class FileHandler():
    
    def __init__(self):
         self.names = os.listdir()
         
    def availableName(self, name):
        if name in self.names:
            return True
        return False
    
    def write(self, data):
        with open('name', 'r+') as file_object:
            file_object.write(json.dumps(data))
        return

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

#common attributes for the different operations
class Tool():
    
    def __init__(self):
        self.relative_position = 0
        self.h_step_lap_count = 1
        self.h_step_lap_distance = 0
        self.h_step_lap_counter = 0
        self.h_step_lap_vector = []
        self.end_marker = False
        
    def getHorizontalStepLapCount(self):
        while True:
            try:
                count = int(input(Labels.get_h_step_lap_count))
                if count <=0 :
                    print(Labels.negative_step_count)
                    continue
                self.h_step_lap_count = count
                return
            except ValueError as err:
                print(err)
                
    def getHorizontalStepLapDistance(self):
        while True:
            try:
                distance = float(input('Enter step-lap distance : '))
                self.h_step_lap_distance = distance
                return
            except ValueError as err:
                print(err)
                
    def generateHorizontalStepLapVector(self):
        pass

#-----------------------------------------------------------------------------

class Hole(Tool):
    def __init__(self):
        pass
    
    def lengthyfy(self, pos=0) -> list:
        pass

#-----------------------------------------------------------------------------

class VNotch(Tool):
    def __init__(self):
        self.v_step_lap_count = 1
        self.v_step_lap_distance = 0
        self.v_step_lap_vector = []
        self.v_step_lap_counter = 0
        
    def lengthyfy(self, pos=0) -> list:
        pass
        
    def getVerticalStepLapCount(self):
        while True:
            count = input('Enter vertical step-lap count : ')
            try:
                count = int(count)
                self.v_step_lap_count = count
                return
            except ValueError as err:
                print(err)
                
    def getVerticalStepLapDistance(self):
        while True:
            dist = input('Enter vertical step-lap distance : ')
            try:
                dist = float(dist)
                self.v_step_lap_distance = dist
                return
            except ValueError as err:
                print(err)
                
    def generateVerticalStepLapVector(self):
        self.v_step_lap_vector = [i * self.v_step_lap_distance for i in 
                                  range(self.v_step_lap_count//2 ,
                                      -self.v_step_lap_count//2, -1)]
    
#-----------------------------------------------------------------------------

class Fm45(Tool):
    
    def __init__(self):
        pass
    
    def lengthyfy(self, pos=0) -> list:
        pass

#-----------------------------------------------------------------------------

class Fp45(Tool):
    
    def __init__(self):
        pass
    
    def lengthyfy(self, pos=0) -> list:
        pass

#-----------------------------------------------------------------------------

class Spear(Tool):
    def __init__(self):
        self.v_step_lap_count = 1
        self.v_step_lap_distance = 0
        self.v_step_lap_vector = []
        self.v_step_lap_counter = 0
        self.distance_from_eq = 0
        self.major_cut = []
        #self.distance_from_edge = 0
        
    def lengthyfy(self, pos=0) -> list:
        pass
        
    def setMajorCut(self):
        if self.distance_from_eq > 0:
            self.major_cut = [-45]
        elif self.distance_from_eq < 0:
            self.major_cut = [45]
        else:
            self.major_cut = [-45, 45]
            
    def getVerticalStepLapDistance(self):
        self.v_step_lap_distance = float(input('Enter step-lap distance : '))
        
    def generateVerticalStepLapVector(self):
        vector = [i * self.v_step_lap_distance for i in 
                                  range(self.v_step_lap_count//2 ,
                                      -self.v_step_lap_count//2, -1)]
        self.v_step_lap_vector = [i + self.distance_from_eq for i in vector]
        
        
    def getVerticalStepLapCount(self):
        while True:
            try :
                count = int(input('Enter vertical step-lap count : '))
                self.v_step_lap_count = count
                return
            except ValueError as err:
                print(err)
                
    def getDistanceFromEq(self):
        self.distance_from_eq = float(input('Enter distance from EQ : '))
        self.setMajorCut()
    
    
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

class ExecutableTool():
    def __init__(self,curr_pos = 0,lo_d=0, la_d=0, pl=0, name=None):
        self.current_position = curr_pos
        self.longitudinal_distance = lo_d
        self.lateral_distance = la_d
        self.repeat_distance = pl
        self.name = name
        
    def resetDistance(self):
        self.current_position = self.repeat_distance
        
    def feed(self, feed_distance):
        self.current_position -= feed_distance
        
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
     
class JobProfile():
    def __init__(self):
        self.coil_width = 0
        self.raw_tool_list = []
        
    def checkCompatible(self):
        pass
        
    def getRawToolList(self):
        while True:
            cmd = input('Add tool ? : ')
            if cmd in ['y', 'a']:
                name = input('Enter tool name : ')
                if name == 's':
                    tool = Spear()
                    tool.getDistanceFromEq()
                    tool.getHorizontalStepLapCount()
                    if tool.h_step_lap_count > 1:
                        tool.getHorizontalStepLapDistance()
                        tool.generateHorizontalStepLapVector()
                    else:
                        tool.getVerticalStepLapCount()
                        if tool.v_step_lap_count > 1:
                            tool.getVerticalStepLapDistance()
                            tool.generateVerticalStepLapVector()
                elif name == 'h':
                    tool = Hole()
                else:
                    print('Incorrect name.')
                    
            else:
                break
