#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 11:02:45 2021

@author: omkar
"""
#input file
from tools import tool_list


def getStepLapDistance():
        step_lap_dist = input('Enter Step-Lap Distance - ')
        if step_lap_dist.lower() == 'na':
            return 0
        return int(step_lap_dist)
    
def getName():
    while True:
        name = input('Enter tool name - ')
        if name not in tool_list:
            print('Invalid tool name')
            continue
        return name
    
def getStepLap():
    step_lap = input('Enter step-lap - ')
    if step_lap.lower() == 'na':
        return 0
    return int(step_lap)