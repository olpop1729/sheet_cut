#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 21:55:23 2021

@author: omkar
"""

import pandas as pd
import os, sys
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
    TOOL_NAME_MAP = {'h':['Hole Punch', DISTANCE_HOLE_VNOTCH,0],
                     'v':['V Notch', DISTANCE_SHEAR_VNOTCH,1],
                     'fm45':['Full Cut -45',2],
                     'fp45':['Full Cut +45',3],
                     'f0':['Full Cut 0',4],
                     'pfr':['Partial Front Right'],
                     'pfl':['Partial Front Left'],
                     'prr':['Partial Rear Right'],
                     'prl':['Partial Rear Left']
                     }
    TOOL_DISTANCE_MAP = {'h':DISTANCE_HOLE_VNOTCH + COIL_START_POSITION,
                         'v':COIL_START_POSITION,
                         'fm45':DISTANCE_SHEAR_VNOTCH + COIL_START_POSITION,
                         'fp45':DISTANCE_SHEAR_VNOTCH + COIL_START_POSITION,
                         'f0': DISTANCE_SHEAR_VNOTCH + COIL_START_POSITION
                         }


class Spear():
    
    def __init__(self, var_dict=None):
        self.name = 's'
        self.pos = 0
        self.step_lap_count = 1
        self.step_lap_counter = 0
        self.step_lap_distance = 0
        self.step_lap_vector = None
        self.is_open = True
        self.is_front = True
        if var_dict:
            self.loadFromDict(var_dict)
            
    def loadFromDict(self, var):
        self.pos = var['pos']
        self.step_lap_count = var['step_lap_count']
        self.step_lap_distance = var['step_lap_distance']
        self.step_lap_vector = var['step_lap_vector']
        self.step_lap_counter = var['step_lap_counter']
        self.is_open = var['is_open']
        self.is_front = var['is_front']
        
    def incrementStepLapCounter(self):
        if self.is_open:
            self.step_lap_counter += 1
        else:
            self.step_lap_counter -= 1
        self.step_lap_counter = self.step_lap_counter  % self.step_lap_count
    
    def getIsOpen(self):
        if input('Open : ').lower() in ['y','yes']:
            self.is_open = True
        else:
            self.is_open = False
        
    def getIsFront(self):
        if input('Front : ').lower() in ['y','yes']:
            self.is_front = True
        else:
            self.is_front = False
        
    def generateStepLapVector(self):
        self.step_lap_vector = [i * self.step_lap_distance for i in 
                                range(self.step_lap_count//2 ,
                                      -self.step_lap_count//2, -1)]
        if self.is_open:
            self.step_lap_counter = 0
            return
        else:
            self.step_lap_counter = self.step_lap_count - 1
        return
        
    def getStepLapCount(self):
        while True:
            try:
                self.step_lap_count = int(input('Enter step-lap count : '))
                if self.step_lap_count <= 1:
                    return False
                return True
            except ValueError as err:
                print(f'Error : {err}')
    
    def getStepLapDistance(self):
        while True:
            try:
                self.step_lap_distance = int(input('Enter step-lap distance : '))
                return
            except ValueError as err:
                print(f'Error : {err}')
                
class Hole():
    
    def __init__(self, var_dict=None):
        self.name = 'h'
        self.pos = 0
        if var_dict:
            self.loadFromDict(var_dict)
            
    def loadFromDict(self, var):
        self.pos = var['pos']
        
class Vnotch():
    
    def __init__(self, var_dict=None):
        self.name = 'v'
        self.pos = 0
        
        if var_dict:
            self.loadFromDict(var_dict)
            
    def loadFromDict(self, var):
        self.pos = var['pos']
        
        
class JobProfile():
    
    def __init__(self):
        self.tool_list = None
        self.length_list = None
        self.step_lap = 1
        self.pattern_length = 0
        self.executable_tool_list = None
        self.executable_length_list = None
        self.layers = 1
        
    def getLayers(self):
        while True:
            try:
                self.layers = int(input('Enter layers : '))
                return
            except ValueError as err:
                print(f'Error : {err}')
        
    # getToolList is equivalent to the cut program
    def getToolList(self):
        tool_list = []
        end_counter = 0
        while end_counter < 2:
            #cmd = input('Add tool? : ').lower()
            #if cmd in ['y', 'a']:
            name = input('Enter tool name : ').lower()
            if name in ['spear', 's']:
                end_counter += 1
                tool_list.append(Spear())
                if end_counter == 1:
                    tool_list[-1].is_front = True
                else:
                    tool_list[-1].is_front = False
                #tool_list[-1].getIsFront()
                if tool_list[-1].getStepLapCount():
                    tool_list[-1].getStepLapDistance()
                    tool_list[-1].getIsOpen()
                    tool_list[-1].generateStepLapVector()
            elif name in ['hole','h']:
                tool_list.append(Hole())
            elif name in ['vnotch', 'v']:
                tool_list.append(Vnotch())
                
            else:
                print('Invalid tool name.')
                
        self.tool_list = tool_list
        self.dumpCutProgram(tool_list)
        
    def dumpCutProgram(self, tl):
        data = {}
        folder_path = '../cut_program_input/central_limb/'
        names = os.listdir(folder_path)
        name = ''
        while True:
            name =  input('Enter file name : ')
            if name in names:
                con = input('File name already exists. Do you want to overwrite ? (y or n) - ')
                if con == 'y':
                    break
                continue
            break

        with open(folder_path+name+'.json', 'w') as fp:
            for i in range(len(tl)):
                data[i] = vars(tl[i])
            fp.write(json.dumps(data, indent=4))
                    
                
        
    def getLengthList(self):
        while True:
            try:
                self.length_list = [float(i) for i in input('Enter lengths : ').split()]
                if len(self.length_list) != len(self.tool_list) - 1:
                    print('Incorrect length list.')
                    continue
                return
            except ValueError as err:
                print(f'Error : {err}')
                sys.exit()
                
    def hasSteplap(self):
        for i in self.tool_list:
            if isinstance(i, Spear):
                if i.step_lap_count > 1:
                    self.step_lap = i.step_lap_count
                    return True
        self.step_lap = 1
        return False
        
    def updateLengthList(self):
        updated_list = []
        if self.hasSteplap():
            for i in range(self.step_lap):
                new_list = []
                for j in range(len(self.length_list)):
                    temp = self.tool_list[j]
                    new_len = self.length_list[j]
                    if isinstance(temp, Spear):
                        if temp.is_front:
                            new_len += temp.step_lap_vector[temp.step_lap_counter]
                            temp.incrementStepLapCounter()
                    new_list.append(new_len)
                    if j == len(self.length_list) - 1:
                        temp = self.tool_list[j+1]
                        if isinstance(temp, Spear):
                            if not temp.is_front:
                                new_list[-1] += temp.step_lap_vector[temp.step_lap_counter]
                                temp.incrementStepLapCounter()
                updated_list.extend(new_list * self.layers)
            self.length_list = updated_list
    
    def createExecutableTools(self):
        inner = []
        position = 0
        modulo = len(self.tool_list) - 1
        for i in range(len(self.length_list)):
            tool = self.tool_list[i % modulo]
            
            if isinstance(tool, Spear):
                inner.append(['fp45', position + Config.DISTANCE_SHEAR_VNOTCH + 
                              + Config.COIL_START_POSITION])
                inner.append(['fm45', position + Config.DISTANCE_SHEAR_VNOTCH] + 
                             Config.COIL_START_POSITION)
                inner.append(['v',position + Config.COIL_START_POSITION])
                
            elif isinstance(tool, Hole):
                inner.append(['h', position + Config.DISTANCE_HOLE_VNOTCH
                              + Config.COIL_START_POSITION])
                
            elif isinstance(tool, Vnotch):
                inner.append(['v', position + Config.COIL_START_POSITION])
                
            position += self.length_list[i]
        self.pattern_length = position
        self.executable_tool_list = inner
        
    def execute(self):
        terminate = 0
        operation = []
        feed = []
        repeat_flag = False
        while terminate < 1000000:
            closest_cut = min([i[1] for i in self.executable_tool_list])
            for i in self.executable_tool_list:
                if i[1] == closest_cut:
                    i[1] = self.pattern_length
                    if repeat_flag:
                        feed.append(0)
                    else:
                        feed.append(closest_cut)
                        repeat_flag = True
                    operation.append(i[0])
                else:
                    i[1] -= closest_cut
            repeat_flag = False
            terminate += closest_cut
        cut_feed = list(zip(feed, operation))
        df = pd.DataFrame(data = cut_feed, columns=['Feed','Operation'])
        df.index += 1
        temp = pd.ExcelWriter('../cut_program_output/CentralLimb_0.xlsx')
        df.to_excel(temp)
        temp.save()
            

def main():
    cmd = input(' 1 - CLI.\v 2 - Json encoded file.\n Enter option number : ')
    if cmd == '1':
        jp = JobProfile()
        jp.getToolList()
        jp.getLengthList()
        jp.getLayers()
        jp.updateLengthList()
        jp.createExecutableTools()
        jp.execute()
    elif cmd == '2':
        jp.JobProfile()
        


if __name__ == '__main__':
    main()
    
