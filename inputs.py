#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 11:02:45 2021

@author: omkar
"""
#input file
from tools import TOOL_NAME_MAP

def getStepLapDistance():
        step_lap_dist = input('Enter Step-Lap Distance - ')
        if step_lap_dist.lower() == 'na':
            return 0
        return int(step_lap_dist)
    
def getName():
    while True:
        name = input('Enter tool name - ')
        if name not in TOOL_NAME_MAP.keys():
            print('Invalid tool name')
            continue
        return name
    
def getStepLap():
    step_lap = input('Enter step-lap - ')
    if step_lap.lower() == 'na':
        return 0
    return int(step_lap)

def getDistanceList():
    while 1:
        try:
            return [int(i) for i in input('Enter l_i - ').split()]
        except Exception as err:
            print(err)
    