#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 14:58:56 2021

@author: omkar
"""
import os
import pandas as pd
import itertools

# user inputs. always keep the case lower. keep the encodings at last
TOOL_HOLE = ['hole','h',0]
TOOL_V_NOTCH = ['v notch', 'vnotch','v',1]
TOOL_P45 = ['full cut +45','+45','45','fp45','p45',2]
TOOL_M45 = ['full cut -45','-45','fm45','m45',3]
TOOL_F0 = ['full cut', '0','0 shear','shear','zero','f0',4]

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
    
    def findName(name) -> str:
        while True:
            break
        pass


class Names:
    HOLE = 'h'
    V_NOTCH = 'v'
    FP45 = 'fp45'
    FM45 = 'fm45'
    F0 = 'f0'

class Labels:
    ERROR = 'ERROR: '
    WARNING = 'WARNING: '
    add_tool = 'Add tool ? (y or n) : '
    get_name = 'Enter tool name : '
    get_step_lap_count = 'Enter step-lap count : '
    get_step_lap_distance = 'Enter step-lap Distance : '
    get_is_open = 'Open : '
    get_is_front = 'Front : '
    get_is_rear = 'Rear : '
    get_rear_open = 'Rear Open : '
    get_front_open = 'Front Open : '
    get_lateral_shift_count = 'Enter lateral-shift count : '
    get_length_list = 'Enter lengths seperated by spaces : '
    get_layers = 'Enter no. of layers : '
    get_lateral_shift_distance = 'Enter lateral-shift distance : '
    confirm = 'Continue ? : '
    incorrect_tool_input = 'Incorrect tool input. Last tool does not match the first tool.'
    
    def printError(err):
        print(f'{bcolors.FAIL}{Labels.WARNING}{err}{bcolors.ENDC}')
        
    def warnOddCount():
        print(f'{bcolors.FAIL}{Labels.ERROR} Please enter an odd count.{bcolors.ENDC}')
    
    def warnNegativeCount():
        print(f'{bcolors.FAIL}{Labels.ERROR} Count should not be negative.{bcolors.ENDC}')
        
    def warnHighStepLapCount():
         print(f'{bcolors.WARNING}{Labels.WARNING}step-lap has high value. May affect the accuracy of the output.{bcolors.ENDC}')
         
    def warnNegativeDistance():
        print(f'{bcolors.FAIL}{Labels.ERROR}Distances should not be zero or negative.{bcolors.ENDC}')
    
    def warnHighDistanceValue():
        print(f'{bcolors.WARNING}{Labels.WARNING}high distance value. May affect the accuracy of the output.{bcolors.ENDC}')
        
    def warnHighLateralShiftCount():
        print(f'{bcolors.WARNING}{Labels.WARNING}high Lateral-count. May affect the accuracy of the output.{bcolors.ENDC}')
    
    def warnNameNotFound():
        print(f'{bcolors.FAIL}{Labels.ERROR}Name not found.{bcolors.ENDC}')
    
    def warnNegativeLayers():
        print(f'{bcolors.FAIL}{Labels.WARNING}No. of layers cannot be negative!{bcolors.ENDC}')
    
    
###############################################################################
###############################################################################
###############################################################################

#                       THE TOOL CLASSES

class Tool():
    def __init__(self, pos=0):
        self.pos = pos
        self.step_lap_count = 1
        self.step_lap_distance = 0
        self.step_lap_vector = []
        self.step_lap_counter = 0
        self.is_front = False
        self.is_rear = False
        
    def getIsFront( self ):
        is_front = input( Labels.get_is_front )
        if is_front in Config.LIST_NO:
            self.is_front = False
        else:
            self.is_front = True
            
    def getIsRear( self ):
        is_rear = input( Labels.get_is_rear )
        if is_rear in Config.LIST_NO:
            self.is_rear = False
        else:
            self.is_rear = True
        
    def hasStepLap(self):
        if self.step_lap_count > 1:
            return True
        return False
        
    def getStepLapCount(self):
        while True:
            try:
                val = int(input(Labels.get_step_lap_count))
                if val < 0:
                    Labels.warnNegativeCount()
                    continue
                if val % 2 == 0:
                    Labels.warnOddCount()
                    continue
                elif val % 2 == 1 and val > 1:
                    if val > 9:
                        Labels.warnHighStepLapCount()
                    self.step_lap_count = val
                    return val
                elif val == 1:
                    return 0
            except Exception as err:
                Labels.printError(err)
                
    def getStepLapDistance(self):
        while True:
            try:
                step_lap_distance = int(input(Labels.get_step_lap_distance))
                if step_lap_distance <= 0:
                    Labels.warnNegativeDistance()
                    continue
                else:
                    if step_lap_distance > 20:
                        Labels.warnHighDistanceValue()
                    self.step_lap_distance = step_lap_distance
                    return step_lap_distance
            except Exception as err:
                Labels.printError(err)
                
    def generateStepLapVector(self):
        self.step_lap_vector = [i * self.step_lap_distance for i in 
                                range(self.step_lap_count//2 ,
                                      -self.step_lap_count//2, -1)]
                
    def setStepLapCounter(self):
        if self.is_open:
            self.step_lap_counter = 0
        else:
            self.step_lap_counter = self.step_lap_count - 1
        
    def incrementSteplapCounter(self):
        if self.is_open:
            self.step_lap_counter += 1
            self.step_lap_counter = self.step_lap_counter % self.step_lap_count 
        else:
            self.step_lap_counter -= 1
            self.step_lap_counter = self.step_lap_counter % self.step_lap_count
        
class Hole(Tool):
    def __init__(self):
        super().__init__()
        self.name = Names.HOLE
        self.is_open = False
    
        
class Vnotch(Tool):
    def __init__(self):
        super().__init__()
        self.name = Names.V_NOTCH
        self.lateral_shift_count = 1
        self.lateral_shift_counter = 0
        self.lateral_shift_vector = []
        self.lateral_shift_distance = 0
        self.rear_step_lap_counter = 0
        self.is_open = False
        
    def incremenLateralShiftCounter(self):
        if self.is_open:
            self.lateral_shift_counter += 1
            self.lateral_shift_counter = self.lateral_shift_counter % self.lateral_shift_count
        else:
            self.lateral_shift_counter -= 1
            self.lateral_shift_counter = self.lateral_shift_counter % self.lateral_shift_count
        
    def incrementSteplapCounter(self):
        if self.is_open and self.is_front and not self.is_rear:
            self.step_lap_counter += 1
            self.step_lap_counter = self.step_lap_counter % self.step_lap_count 
        elif self.is_open and not self.is_front and self.is_rear:
            self.rear_step_lap_counter += 1
            self.rear_step_lap_counter = self.rear_step_lap_counter % self.step_lap_count
        elif not self.is_open and self.is_front and not not self.is_rear:
            self.step_lap_counter -= 1
            self.step_lap_counter = self.step_lap_counter % self.step_lap_count 
        elif self.is_open and not self.is_front and self.is_rear:
            self.rear_step_lap_counter -= 1
            self.rear_step_lap_counter = self.rear_step_lap_counter % self.step_lap_count
    
    def getIsOpen(self):
        is_open = input(Labels.get_is_open)
        if is_open in Config.LIST_NO:
            self.is_open = False
        elif is_open in Config.LIST_YES:
            self.is_open = True
            
    def getLateralShiftDistance(self):
        while True:
            try:
                self.lateral_shift_distance = int(input(Labels.get_lateral_shift_distance))
                return
            except ValueError as err:
                Labels.printError(err)
            
    def setStepLapCounter(self):
        if self.is_open and self.is_rear and not self.is_front:
            self.rear_step_lap_counter = 0
        elif self.is_open and self.is_front and not self.is_rear:
            self.step_lap_counter = 0
        elif not self.is_open and self.is_rear and not self.is_front:
            self.rear_step_lap_counter = self.step_lap_count - 1
        elif not self.is_open and self.is_front and not self.is_rear:
            self.step_lap_counter = self.step_lap_count - 1
        elif self.is_front and self.is_rear and self.is_open:
            self.step_lap_counter = 0
            self.rear_step_lap_counter = self.step_lap_count - 1
        elif not self.is_front and self.is_rear and self.is_open:
            self.step_lap_counter = self.step_lap_count - 1
            self.rear_step_lap_counter = 0
    
    def getLateralShiftCount(self):
        while True:
            try:
                count = int(input(Labels.get_lateral_shift_count))
                if count <=0:
                    Labels.warnNegativeCount()
                elif count == 1:
                    return 0
                else:
                    if count > 9:
                        Labels.warnHighLateralShiftCount()
                    self.lateral_shift_count = count
                    return count
            except Exception as err:
                Labels.printError(err)
                
    def setLateralShiftCounter(self):
        if self.is_open:
            self.lateral_shift_counter = 0
        else:
            self.lateral_shift_counter = self.lateral_shift_count - 1
    
    def generateLateralShiftVector(self):
        self.lateral_shift_vector = [i*self.lateral_shift_distance for i in 
                                range(-self.lateral_shift_count//2 + 1,
                                      self.lateral_shift_count//2 + 1)]
        
class FullCut(Tool):
    def __init__(self, is_front=False, is_rear=False, 
                 front_open=False, rear_open=False):
        super().__init__()
        self.front_open = front_open
        self.rear_open = rear_open
        self.rear_step_lap_counter = 0
        
    # def generateStepLapVector(self):
    #     pass
        
    def setStepLapCounter(self):
        if self.front_open and self.rear_open:
            self.step_lap_counter = 0
            self.rear_step_lap_counter = 0
        elif self.front_open and not self.rear_open:
            self.rear_step_lap_counter = self.step_lap_count - 1
            self.step_lap_counter = 0
        elif not self.front_open and self.rear_open:
            self.step_lap_counter = self.step_lap_count - 1
            self.rear_step_lap_counter = 0
        else:
            self.rear_step_lap_counter = self.step_lap_count - 1
            self.step_lap_counter = self.step_lap_count - 1
        
    def incrementSteplapCounter(self):
        if self.front_open:
            self.step_lap_counter += 1
            self.step_lap_counter = self.step_lap_counter % self.step_lap_count 
        elif not self.front_open and self.is_front:
            self.step_lap_counter -= 1
            self.step_lap_counter = self.step_lap_counter % self.step_lap_count
        if self.rear_open:
            self.rear_step_lap_counter += 1
            self.rear_step_lap_counter = self.rear_step_lap_counter % self.step_lap_count
        elif not self.rear_open and self.is_rear:
            self.rear_step_lap_counter -= 1
            self.rear_step_lap_counter = self.rear_step_lap_counter % self.step_lap_count
            
    def getFrontOpen( self ):
        front_open = input( Labels.get_front_open )
        if front_open in Config.LIST_NO:
            self.front_open = False
        else:
            self.front_open = True
            
    def getRearOpen( self ):
        rear_open = input( Labels.get_rear_open )
        if rear_open in Config.LIST_NO:
            self.rear_open = False
        else:
            self.rear_open = True
            
class Fm45(FullCut):
    def __init__(self):
        super().__init__()
        self.name = Names.FM45
        
        
class Fp45(FullCut):
    def __init__(self):
        super().__init__()
        self.name = Names.FP45
        
class F0(FullCut):
    def __init__(self):
        super().__init__()
        self.name = Names.F0

###############################################################################
###############################################################################
###############################################################################
        

#                           THE JOB PROFILE


class JobProfile():
    
    def __init__(self):
        self.tool_list = None
        self.length_list = None
        self.step_lap = 1
        self.executable_tool_list = None
        self.pattern_length = 0
        self.vnotch_axis = 0
        self.layers = 1
        
    def getLayers(self):
        while True:
            try:
                layers = int(input(Labels.get_layers))
                if layers < 0:
                    Labels.warnNegativeLayers()
                    continue
                elif layers == 0:
                    self.layers = 1
                    return
                else:
                    self.layers = layers
                    return
            except ValueError as err:
                Labels.printError(err)
        
    def showTools(self):
        for i in self.tool_list:
            for j in vars(i).keys():
                print(j, vars(i)[j])
    
    def updateStepLap(self):
        self.step_lap = max([i.step_lap_count for i in self.tool_list])
                
    def getLengthList(self):
        while True:
            try:
                l_i = [int(i) for i in input(Labels.get_length_list).split()]
                print(l_i)
                check = input(Labels.confirm)
                if check in Config.LIST_NO:
                    continue
                self.length_list = l_i
                return
            except Exception as err:
                Labels.printError(err)
        
    def getToolList(self):
        tool_list = []
        while True:
            cmd_input = input(Labels.add_tool).lower()
            if cmd_input not in Config.LIST_NO:
                name = input(Labels.get_name).lower()
                if name in TOOL_HOLE:
                    hole = Hole()
                    if hole.getStepLapCount():
                        hole.getStepLapDistance()
                        hole.generateStepLapVector()
                    tool_list.append(hole)
                elif name in TOOL_V_NOTCH:
                    vnotch = Vnotch()
                    vnotch.getIsFront()
                    vnotch.getIsRear()
                    vnotch.getIsOpen()
                    if not vnotch.getStepLapCount():
                        if vnotch.getLateralShiftCount():
                            vnotch.getLateralShiftDistance()
                            vnotch.generateLateralShiftVector()
                    else:
                        vnotch.getStepLapDistance()
                        vnotch.generateStepLapVector()
                    tool_list.append(vnotch)
                elif name in TOOL_P45:
                    fp45 = Fp45()
                    fp45.getIsFront()
                    fp45.getIsRear()
                    fp45.getFrontOpen()
                    fp45.getRearOpen()
                    if fp45.getStepLapCount():
                        fp45.getStepLapDistance()
                        fp45.generateStepLapVector()
                        fp45.setStepLapCounter()
                    tool_list.append(fp45)
                    
                elif name in TOOL_M45:
                    fm45 = Fm45()
                    fm45.getIsFront()
                    fm45.getIsRear()
                    fm45.getFrontOpen()
                    fm45.getRearOpen()
                    if fm45.getStepLapCount():
                        fm45.getStepLapDistance()
                        fm45.generateStepLapVector()
                        fm45.setStepLapCounter()
                    tool_list.append(fm45)
                else:
                    Labels.warnNameNotFound()
            else:
                break
        self.tool_list = tool_list
        if tool_list[-1].name != tool_list[0].name:
            Labels.printError(Labels.incorrect_tool_input)
            os.exit()
        
    def updateLengths(self):
        final_vnotch_axis = []
        final_length_list = []
        if self.step_lap > 1:
            for i in range(self.step_lap):
                new_l_i = []
                vnotch_axis = []
                for j in range(len(self.length_list)):
                    temp = self.tool_list[j]
                    if isinstance(temp, Vnotch):
                        if temp.lateral_shift_count > 1:
                            vnotch_axis.append(temp.lateral_shift_vector[temp.lateral_shift_counter])
                            temp.incremenLateralShiftCounter()
                        else:
                            vnotch_axis.append(0)
                    else:
                        vnotch_axis.append(0)
                    if temp.hasStepLap():
                        if temp.is_front and not temp.is_rear:
                            new_l_i.append(self.length_list[j] + 
                                       temp.step_lap_vector[temp.step_lap_counter])
                            temp.incrementSteplapCounter()
                        elif temp.is_rear and temp.is_front:
                            #new_l_i[-1] = self.length_list[j] + temp.step_lap_vector[temp.rear_step_lap_counter]
                            new_l_i[-1] += temp.step_lap_vector[temp.rear_step_lap_counter]
                            new_l_i.append(self.length_list[j] + 
                                       temp.step_lap_vector[temp.step_lap_counter])
                            temp.incrementSteplapCounter()
                        elif temp.is_rear and not temp.is_front:
                            new_l_i[-1] += temp.step_lap_vector[temp.rear_step_lap_counter]
                            new_l_i.append(0)
                            temp.incrementSteplapCounter()
                    else:
                        new_l_i.append(self.length_list[j])
                    if j == len(self.length_list) - 1:
                        if self.tool_list[j+1].step_lap_count > 1:
                            #new_l_i[-1] = self.length_list[j] + self.tool_list[j+1].step_lap_vector[self.tool_list[j+1].rear_step_lap_counter]
                            new_l_i[-1] += self.tool_list[j+1].step_lap_vector[self.tool_list[j+1].rear_step_lap_counter]
                            self.tool_list[j+1].incrementSteplapCounter()    
                    
                final_length_list.extend(new_l_i*self.layers)
                final_vnotch_axis.extend(vnotch_axis*self.layers)
            
            #lastly update the profile length list
            self.vnotch_axis = final_vnotch_axis
            self.length_list = final_length_list
    
    def createExecutableToolList(self):
        inner = []
        position = 0
        distance_to_tool = 0
        modulo = len(self.tool_list) - 1
        for i in range(len(self.length_list)):
            distance_to_tool = position + Config.TOOL_DISTANCE_MAP[self.tool_list[i % modulo].name]
            inner.append([self.tool_list[i % modulo].name, distance_to_tool, self.vnotch_axis[i]])
            position += self.length_list[i]
        self.pattern_length = position
        self.executable_tool_list = inner
        
        ## start building positions
        position = 0
        
    def execute(self):
        terminate = 0
        operation = []
        feed = []
        v_axis = []
        repeat_flag = False
        while terminate < Config.COIL_LENGTH:
            closest_cut = min([i[1] for i in self.executable_tool_list])
            for i in self.executable_tool_list:
                if i[1] == closest_cut:
                    i[1] = self.pattern_length
                    if repeat_flag:
                        feed.append(0)
                        v_axis.append(i[2])
                    else:
                        feed.append(closest_cut)
                        v_axis.append(i[2])
                        repeat_flag = True
                    operation.append(i[0])
                else:
                    i[1] -= closest_cut
            repeat_flag = False
            terminate += closest_cut
        cut_feed = list(zip(feed,v_axis, operation))
        df = pd.DataFrame(data = cut_feed, columns=['Feed','V-Axis','Operation'])
        df.index += 1
        temp = pd.ExcelWriter('../cut_program_output/CutFeed_1.xlsx')
        df.to_excel(temp)
        temp.save()
        

###############################################################################
###############################################################################
###############################################################################

#                           EXECUTION BLOCK

job_profile = JobProfile()
job_profile.getToolList()
job_profile.updateStepLap()
job_profile.getLengthList()
job_profile.getLayers()
job_profile.updateLengths()
job_profile.createExecutableToolList()

job_profile.execute()













