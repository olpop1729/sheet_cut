#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 10:37:05 2021

@author: omkar
"""
from parameters import DISTANCE_HOLE_VNOTCH,DISTANCE_SHEAR_VNOTCH

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
