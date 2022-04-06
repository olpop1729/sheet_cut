#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 18:47:29 2022

@author: omkar
"""


class Labels:
    
    def __init__(self):
        pass
    
    steplap_type_map = {'No step-lap':0, 'Horizontal (Longitudinal)':1,
                        'Vertical (Lateral)':2}
    attr_map = {''}
    open_code_map = {'NA':0, 'Open':1, 'Closed':2, 'Front Open, Rear Open':3,
                     'Front Open, Rear Closed':4, 'Front Closed, Rear Open':5,
                     'Front Closed, Rear Closed':6, 'Front Open':7, 'Front Closed':8,
                     'Rear Open':9, 'Rear Closed':10}

    create_frame_cols  =['PNR', 'Tool name', 'Step-lap type','Step-lap count',
                            'Open-Close config']
    
    # gui help for this thing
    tool_name_tuple = ('fm45', 'fp45', 'f0', 'v', 'h', 's', 'ys', 
                       'fish_head', 'fish_tail','prrp45',
                       'pfrm45', 'prrf0', 'pfrf0', 'prlm45', 'prlf0',
                       'pflp4', 'pflf0')