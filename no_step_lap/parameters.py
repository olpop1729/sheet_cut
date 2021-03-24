#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 10:39:49 2021

@author: omkar
"""

SHEET_LENGTH = 100000
DISTANCE_HOLE_VNOTCH = 1250
DISTANCE_SHEAR_VNOTCH = 4335



TOOL_HOLE = ['hole','h',0]
TOOL_V_NOTCH = ['v notch', 'vnotch','v',1]
TOOL_P45 = ['full cut +45','+45','45','fp45','p45',2]
TOOL_M45 = ['full cut -45','-45','fm45','m45',3]
TOOL_F0 = ['full cut', '0','0 shear','shear','zero','f0',4]



#-------------------------------------------
# directories

OUTPUT_CUT_PROGRAM_DIRECTORY = 'cut_program_output/'
CONFIG_FILE_NAME = 'cfg/config.txt'

#-------------------------------------------