#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 14:58:56 2021

@author: omkar
"""
import os, sys
import pandas as pd
import itertools
import json

# user inputs. always keep the case lower. keep the encodings at last
TOOL_HOLE = ['hole','h',0]
TOOL_V_NOTCH = ['v notch', 'vnotch','v',1]
TOOL_P45 = ['full cut +45','+45','45','fp45','p45',2]
TOOL_M45 = ['full cut -45','-45','fm45','m45',3]
TOOL_F0 = ['full cut', '0','0 shear','shear','zero','f0','full cut 0',4]

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
    OFFSET_F0 = 0
    OFFSET_FP45 = 0
    OFFSET_FM45 = 0
    DISTANCE_HOLE_VNOTCH = 1250
    DISTANCE_SHEAR_VNOTCH = 4335.25
    COIL_LENGTH = 400000
    CUT_PROGRAM_OUTPUT_DIRECTORY = '../cut_program_output'
    COIL_START_POSITION = 0 # w.r.t. V_Notch.
    OUTPUT_FILE_NAME = 'CutFeed_'
    LIST_NO = ['no', 'n','not', '0','negative','incorrect']
    LIST_YES = ['yes', 'y', 'affirmative', 'correct', '1']
    EXCEL_COLUMN_NAMES = ['Feed Dist', 'Vnotch Trav Dist', 'After Shear feed Tip Cut',
                     'Tool', 'Tool no', 'Start Index', 'End Index',
                     'Job Shape', 'No of Steps', 'Sheet Count', 'P45 OverCut', 
                     'M45 OverCut', 'Yoke Len', 'Leg Len', 'Cnetral Limb Len']
    TOOL_NAME_MAP = {'h':['Hole Punch', DISTANCE_HOLE_VNOTCH,2],
                     'v':['V Notch', DISTANCE_SHEAR_VNOTCH,1],
                     'fm45':['Full Cut -45',4],
                     'fp45':['Full Cut +45',3],
                     'f0':['Full Cut 0',5],
                     'pfr':['Partial Front Right'],
                     'pfl':['Partial Front Left'],
                     'prr':['Partial Rear Right'],
                     'prl':['Partial Rear Left']
                     }
    TOOL_DISTANCE_MAP = {'h':DISTANCE_HOLE_VNOTCH + COIL_START_POSITION,
                         'v':COIL_START_POSITION,
                         'fm45':DISTANCE_SHEAR_VNOTCH + COIL_START_POSITION + OFFSET_FM45,
                         'fp45':DISTANCE_SHEAR_VNOTCH + COIL_START_POSITION + OFFSET_FP45,
                         'f0': DISTANCE_SHEAR_VNOTCH + COIL_START_POSITION + OFFSET_F0
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
    SPEAR = 's'

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
    
    
    
class PandasWriterReader:
    
    def writeExcel(**kwargs):
        if len(kwargs.keys()) < len(Config.EXCEL_COLUMN_NAMES):
            print(f'{bcolors.FAIL}{Labels.ERROR}Insufficient column inputs{bcolors.ENDC}')
            os.exit()
        cut_feed = list(itertools.zip_longest(kwargs['feed'], kwargs['v_axis'],kwargs['sec_feed'],
                    kwargs['operation'], kwargs['tool_number'], 
                    kwargs['start_index'], kwargs['end_index'], 
                    kwargs['job_shape'], kwargs['number_of_steps'], 
                    kwargs['sheet_count'], kwargs['p45_overcut'], 
                    kwargs['m45_overcut'], kwargs['yoke_len'],
                    kwargs['leg_len'], kwargs['cl_len']))
        df = pd.DataFrame(data = cut_feed, columns=Config.EXCEL_COLUMN_NAMES)
        df.index += 1
        while True:
            file_name = input('Enter output-file name : ')
            if file_name in os.listdir('../cut_program_output/'):
                con = input('File already exists do you want to overwrite ? (y or n) : ' )
                if con in ['y', 'yes']:
                    break
                else:
                    continue
            else:
                break
        temp = pd.ExcelWriter('../cut_program_output/' + file_name + '.xlsx')
        df.to_excel(temp)
        temp.save()
        

###############################################################################
###############################################################################
###############################################################################

#                       THE TOOL CLASSES

class Tool():
    def __init__( self ):
        self.pos = 0
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
        
    def hasStepLap( self ):
        if self.step_lap_count > 1:
            return True
        return False
        
    def getStepLapCount( self ):
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
    def __init__(self, var_dict = None):
        super().__init__()
        self.name = Names.HOLE
        self.is_open = False
        if var_dict:
            self.name = var_dict['name']
            self.is_open = var_dict['is_open']
            self.pos = var_dict['pos']
            self.step_lap_distance = var_dict['step_lap_distance']
            self.step_lap_count = var_dict['step_lap_count']
            self.step_lap_vector = var_dict['step_lap_vector']
            self.step_lap_counter = var_dict['step_lap_counter']
            self.is_front = var_dict['is_front']
            self.is_rear = var_dict['is_rear']
    
        
class Vnotch(Tool):
    def __init__(self, var_dict = None):
        super().__init__()
        self.name = Names.V_NOTCH
        self.lateral_shift_count = 1
        self.lateral_shift_counter = 0
        self.lateral_shift_vector = []
        self.lateral_shift_distance = 0
        self.rear_step_lap_counter = 0
        self.is_open = False
        
        if var_dict:
            self.name = var_dict['name']
            self.is_open = var_dict['is_open']
            self.pos = var_dict['pos']
            self.step_lap_distance = var_dict['step_lap_distance']
            self.step_lap_count = var_dict['step_lap_count']
            self.step_lap_vector = var_dict['step_lap_vector']
            self.step_lap_counter = var_dict['step_lap_counter']
            self.is_front = var_dict['is_front']
            self.is_rear = var_dict['is_rear']
            self.lateral_shift_count = var_dict['lateral_shift_count']
            self.lateral_shift_counter = var_dict['lateral_shift_counter']
            self.lateral_shift_vector = var_dict['lateral_shift_vector']
            self.lateral_shift_distance = var_dict['lateral_shift_distance']
            self.rear_step_lap_counter = var_dict['rear_step_lap_counter']
        
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

        if self.is_front and self.is_rear and self.is_open:
            self.step_lap_counter = 0
            self.rear_step_lap_counter = self.step_lap_count - 1
            
        elif not self.is_open and self.is_front and self.is_rear:
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
    def __init__( self ):
        super().__init__()
        self.front_open = False
        self.rear_open = False
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
    def __init__(self, var_dict=None):
        super().__init__()
        self.name = Names.FM45
        if var_dict:
            self.name = var_dict['name']
            self.pos = var_dict['pos']
            self.step_lap_distance = var_dict['step_lap_distance']
            self.step_lap_count = var_dict['step_lap_count']
            self.step_lap_vector = var_dict['step_lap_vector']
            self.step_lap_counter = var_dict['step_lap_counter']
            self.is_front = var_dict['is_front']
            self.is_rear = var_dict['is_rear']
            self.front_open = var_dict['front_open']
            self.rear_open = var_dict['rear_open']
            self.rear_step_lap_counter = var_dict['rear_step_lap_counter']
        
        
class Fp45(FullCut):
    def __init__(self, var_dict=None):
        super().__init__()
        self.name = Names.FP45
        if var_dict:
            self.name = var_dict['name']
            self.pos = var_dict['pos']
            self.step_lap_distance = var_dict['step_lap_distance']
            self.step_lap_count = var_dict['step_lap_count']
            self.step_lap_vector = var_dict['step_lap_vector']
            self.step_lap_counter = var_dict['step_lap_counter']
            self.is_front = var_dict['is_front']
            self.is_rear = var_dict['is_rear']
            self.front_open = var_dict['front_open']
            self.rear_open = var_dict['rear_open']
            self.rear_step_lap_counter = var_dict['rear_step_lap_counter']
        
class F0(FullCut):
    def __init__(self, var_dict=None):
        super().__init__()
        self.name = Names.F0
        if var_dict:
            self.name = var_dict['name']
            self.pos = var_dict['pos']
            self.step_lap_distance = var_dict['step_lap_distance']
            self.step_lap_count = var_dict['step_lap_count']
            self.step_lap_vector = var_dict['step_lap_vector']
            self.step_lap_counter = var_dict['step_lap_counter']
            self.is_front = var_dict['is_front']
            self.is_rear = var_dict['is_rear']
            self.front_open = var_dict['front_open']
            self.rear_open = var_dict['rear_open']
            self.rear_step_lap_counter = var_dict['rear_step_lap_counter']
            
            
class Spear(Tool):
    def __init__(self, var_dict=None):
        super().__init__()
        self.name = Names.SPEAR
        if var_dict:
            self.name = var_dict['name']
            self.pos = var_dict['pos']
            self.step_lap_distance = var_dict['step_lap_distance']
            self.step_lap_count = var_dict['step_lap_count']
            self.step_lap_vector = var_dict['step_lap_vector']
            self.step_lap_counter = var_dict['step_lap_counter']
            self.is_front = var_dict['is_front']
            self.is_rear = var_dict['is_rear']
            self.front_open = var_dict['front_open']
            self.rear_open = var_dict['rear_open']
            self.rear_step_lap_counter = var_dict['rear_step_lap_counter']
    
    def lengthyfy(self):
        return ['v', self.pos], ['f', self.pos]
    

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
        self.vnotch_axis = []
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
                l_i = [float(i) for i in input(Labels.get_length_list).split()]
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
        end_counter = 0
        while end_counter < 3:
            # cmd_input = input(Labels.add_tool).lower()
            # if cmd_input not in Config.LIST_NO:
            name = input(Labels.get_name).lower()
            
            if name in TOOL_HOLE:
                hole = Hole()
                if hole.getStepLapCount():
                    hole.getStepLapDistance()
                    hole.generateStepLapVector()
                tool_list.append(hole)
                
            elif name in TOOL_V_NOTCH:
                vnotch = Vnotch()
                vnotch.is_front = True
                vnotch.is_rear = True
                #vnotch.getIsFront()
                #vnotch.getIsRear()
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
                if end_counter == 0:
                    fp45.is_front = True
                    fp45.is_rear = False
                    fp45.getFrontOpen()
                elif end_counter == 1:
                    fp45.is_front = True
                    fp45.is_rear = True
                    fp45.getRearOpen()
                    fp45.getFrontOpen()
                elif end_counter == 2:
                    fp45.is_front = False
                    fp45.is_rear = True
                    fp45.getRearOpen()
                    
                if fp45.getStepLapCount():
                    fp45.getStepLapDistance()
                    fp45.generateStepLapVector()
                    fp45.setStepLapCounter()
                tool_list.append(fp45)
                end_counter+=1
                
            elif name in TOOL_M45:
                fm45 = Fm45()
                if end_counter == 0:
                    fm45.is_front = True
                    fm45.is_rear = False
                    fm45.getFrontOpen()
                elif end_counter == 1:
                    fm45.is_front = True
                    fm45.is_rear = True
                    fm45.getFrontOpen()
                    fm45.getRearOpen()
                elif end_counter == 2:
                    fm45.is_front = False
                    fm45.is_rear = True
                    fm45.getRearOpen()
                    
                if fm45.getStepLapCount():
                    fm45.getStepLapDistance()
                    fm45.generateStepLapVector()
                    fm45.setStepLapCounter()
                tool_list.append(fm45)
                end_counter+=1
                
            elif name in TOOL_F0:
                f0 = F0()
                if end_counter == 0:
                    f0.is_front = True
                    f0.is_rear = False
                    f0.getFrontOpen()
                elif end_counter == 1:
                    f0.is_front = True
                    f0.is_rear = True
                    f0.getFrontOpen()
                    f0.getRearOpen()
                elif end_counter == 2:
                    f0.is_front = False
                    f0.is_rear = True
                    f0.getRearOpen()
                    
                if f0.getStepLapCount():
                    f0.getStepLapDistance()
                    f0.generateStepLapVector()
                    f0.setStepLapCounter()
                tool_list.append(f0)
                end_counter+=1
            
            else:
                Labels.warnNameNotFound()
            # else:
            #     break
        self.tool_list = tool_list
        if tool_list[-1].name != tool_list[0].name:
            Labels.printError(Labels.incorrect_tool_input)
            sys.exit()
        self.dumpCutProgram(tool_list)
        
    def loadCutProgram(self, name):
        tool_list = []
        with open('../cut_program_input/' + name, 'r') as fp:
            data = json.load(fp)
        print('Program looks like :')
        for i in data:
            #print(i ,'--' , data[i])
            if data[i]['name'] == Names.HOLE:
                print(' o ', end='')
                tool_list.append(Hole(data[i]))
            elif data[i]['name'] == Names.F0:
                print(' | ', end='')
                tool_list.append(F0(data[i]))
            elif data[i]['name'] == Names.V_NOTCH:
                print(' v ', end='')
                tool_list.append(Vnotch(data[i]))
            elif data[i]['name'] == Names.FM45:
                print('\\', end='')
                tool_list.append(Fm45(data[i]))
            elif data[i]['name'] == Names.FP45:
                print('/', end='')
                tool_list.append(Fp45(data[i]))
        print()
                
        self.tool_list = tool_list
        
    
    def dumpCutProgram(self, tool_list):
        data = {}
        names = os.listdir('../cut_program_input/')
        name = ''
        while True:
            name =  input('Enter file name : ')
            if name in names:
                con = input('File name already exists. Do you want to continue ? (y or n) - ')
                if con == 'y':
                    break
                continue
            else:
                with open('../cut_program_input/'+name+'.json', 'w') as fp:
                    for i in range(len(tool_list)):
                        data[i] = vars(tool_list[i])
                    fp.write(json.dumps(data, indent=4))
                    
                break
            
        
    def updateLengths(self):
        final_vnotch_axis = []
        final_length_list = []
        self.vnotch_axis = [0]*len(self.length_list)
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
        
        
    def execute(self):
        terminate = 0
        operation = []
        tool_number = []
        feed = []
        v_axis = []
        repeat_flag = False
        sheet_count = []
        sheet_counter = -1
        while terminate < Config.COIL_LENGTH:
            closest_cut = min([i[1] for i in self.executable_tool_list])
            for i in self.executable_tool_list:
                if i[1] == closest_cut:
                    i[1] = self.pattern_length
                    if repeat_flag:
                        feed.append(0)
                    else:
                        feed.append(closest_cut)
                        repeat_flag = True
                    v_axis.append(i[2])
                    operation.append(i[0])
                    tool_number.append(Config.TOOL_NAME_MAP[i[0]][-1])
                    sheet_count.append(sheet_counter)
                    if i[0] == self.executable_tool_list[0][0]:
                        sheet_counter += 1
                else:
                    i[1] -= closest_cut
            repeat_flag = False
            terminate += closest_cut
        start_index = 0
        end_index = 0
        for i in range(len(operation)):
            if operation[i][0] == 'f':
                start_index = i
                break
        start_index += 2
        end_index = start_index + len(self.length_list) - 1
        feed = feed[:end_index]
        operation = operation[:end_index]
        v_axis = v_axis[:end_index]
        tool_number = tool_number[:end_index]
        sheet_count = sheet_count[:end_index]
        start_index = [start_index]
        end_index = [end_index]
        sec_feed = []
        number_of_steps = []
        p45_overcut = []
        m45_overcut = []
        yoke_len = []
        leg_len = []
        cl_len = []
        job_shape = []
        PandasWriterReader.writeExcel(feed=feed, v_axis=v_axis, 
                                                  sec_feed=sec_feed, 
                                                  operation=operation, 
                                                  tool_number=tool_number, 
                                                  start_index=start_index, 
                                                  end_index=end_index, 
                                                  job_shape=job_shape, 
                                                  number_of_steps=number_of_steps, 
                                                  sheet_count=sheet_count, 
                                                  p45_overcut=p45_overcut,
                                                  m45_overcut=m45_overcut, 
                                                  yoke_len=yoke_len, 
                                                  leg_len=leg_len, cl_len=cl_len)
                
        

###############################################################################
###############################################################################
###############################################################################

#                           EXECUTION BLOCK

def main():
    jp = JobProfile()
    opt = input('1 - Input from CLI.\n2 - Input from json.\n\nEnter Option no. : ')
    if opt == '1':
        jp.getToolList()
    elif opt == '2':
        names = [i for i in os.listdir('../cut_program_input/') if i.endswith('json')]
        while True:
            for i in range(len(names)):
                print((i+1) , ' - ',  names[i])
            name = input('\nEnter file index/name : ')
            try:
    
                name = int(name)
                jp.loadCutProgram(names[name-1])
                inp = input('Continue ? (y or n) : ').lower()
                if inp in ['y','yes','1']:
                    break
                continue
    
            except ValueError:
                try:
                    jp.loadCutProgram(name)
                    inp = input('Continue ? (y or n) : ').lower()
                    if inp in ['y','yes','1']:
                        break
                except IOError as ioerr:
                    print(ioerr)
    
    jp.updateStepLap()
    jp.getLengthList()
    jp.getLayers()
    jp.updateLengths()
    print(jp.tool_list)
    print(jp.length_list)
    jp.createExecutableToolList()
    jp.execute()
    

if __name__ == "__main__":
    main()
