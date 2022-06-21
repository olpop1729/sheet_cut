#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 11:39:39 2022

@author: omkar
"""

import json

class Config:
    # OFFSET_V_LAT = 0.0
    # OFFSET_F0 = 0.0
    # OFFSET_FP45 = -1.665
    # OFFSET_FM45 = 0.865
    # DISTANCE_HOLE_VNOTCH = 1250.125
    # DISTANCE_SHEAR_VNOTCH = 4334.5
    # COIL_LENGTH = 400000.0
    CUT_PROGRAM_OUTPUT_DIRECTORY = '../cut_program_output'
    CONFIG_DIRECTORY = '../gui/config.json'
    COIL_START_POSITION = 0.0 # w.r.t. V_Notch.
    OUTPUT_FILE_NAME = 'CutFeed_'
    LIST_NO = ['no', 'n','not', '0','negative','incorrect']
    LIST_YES = ['yes', 'y', 'affirmative', 'correct', '1']
    EXCEL_COLUMN_NAMES = ['Feed Dist', 'Vnotch Trav Dist', 'After Shear feed Tip Cut',
                     'Tool', 'Tool no', 'Start Index', 'End Index',
                     'Job Shape', 'No of Steps', 'Sheet Count', 'P45 OverCut', 
                     'M45 OverCut', 'Yoke Len', 'Leg Len', 'Cnetral Limb Len']
    # TOOL_NAME_MAP = {'h':['Hole Punch', DISTANCE_HOLE_VNOTCH,2],
    #                  'v':['V Notch', DISTANCE_SHEAR_VNOTCH,1],
    #                  'fm45':['Full Cut -45',5],
    #                  'fp45':['Full Cut +45',4],
    #                  'f0':['Full Cut 0',3],
    #                  'pfr':['Partial Front Right'],
    #                  'pfl':['Partial Front Left'],
    #                  'prr':['Partial Rear Right'],
    #                  'prl':['Partial Rear Left']
    #                  }
    # TOOL_DISTANCE_MAP = {'h':DISTANCE_HOLE_VNOTCH + COIL_START_POSITION,
    #                      'v':COIL_START_POSITION,
    #                      'fm45':DISTANCE_SHEAR_VNOTCH + COIL_START_POSITION + OFFSET_FM45,
    #                      'fp45':DISTANCE_SHEAR_VNOTCH + COIL_START_POSITION + OFFSET_FP45,
    #                      'f0': DISTANCE_SHEAR_VNOTCH + COIL_START_POSITION + OFFSET_F0
    #                      }
    
    def findName(name) -> str:
        while True:
            break
        pass
    
    def __init__(self):
        path = Config.CONFIG_DIRECTORY
        data = {}
        try:
            with open(path, 'r') as fp:
                data = json.load(fp)
        except FileNotFoundError as err:
            print(err)
        self.data = data
        
        # print('showing parameters ^^^^^^^^^^')
        # print(data)
        
        self.OFFSET_V_LAT = data['OFFSET_V_LAT']
        self.OFFSET_F0 = data['OFFSET_F0']
        self.OFFSET_FP45 = data['OFFSET_FP45']
        self.OFFSET_FM45 = data['OFFSET_FM45']
        self.DISTANCE_HOLE_VNOTCH = data['DISTANCE_HOLE_VNOTCH']
        self.DISTANCE_SHEAR_VNOTCH = data['DISTANCE_SHEAR_VNOTCH']
        self.COIL_LENGTH = data['COIL_LENGTH']
        
        
        self.TOOL_NAME_MAP = {'h':['Hole Punch', self.DISTANCE_HOLE_VNOTCH,2],
                         'v':['V Notch', self.DISTANCE_SHEAR_VNOTCH,1],
                         'fm45':['Full Cut -45',5],
                         'fp45':['Full Cut +45',4],
                         'f0':['Full Cut 0',3],
                         'pfr':['Partial Front Right'],
                         'pfl':['Partial Front Left'],
                         'prr':['Partial Rear Right'],
                         'prl':['Partial Rear Left']
                         }
        
        self.TOOL_DISTANCE_MAP = {'h':self.DISTANCE_HOLE_VNOTCH + self.COIL_START_POSITION,
                             'v':self.COIL_START_POSITION,
                             'fm45':self.DISTANCE_SHEAR_VNOTCH + self.COIL_START_POSITION + self.OFFSET_FM45,
                             'fp45':self.DISTANCE_SHEAR_VNOTCH + self.COIL_START_POSITION + self.OFFSET_FP45,
                             'f0': self.DISTANCE_SHEAR_VNOTCH + self.COIL_START_POSITION + self.OFFSET_F0
                             }
    
    
    
