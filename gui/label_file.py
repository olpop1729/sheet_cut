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
                        'Vertical (Lateral)':2, 'Skewed (Lateral)':3}
    attr_map = {''}
    open_code_map = {'NA':0, 'Open':1, 'Closed':2, 'Front Open, Rear Open':3,
                     'Front Open, Rear Closed':4, 'Front Closed, Rear Open':5,
                     'Front Closed, Rear Closed':6, 'Front Open':7, 'Front Closed':8,
                     'Rear Open':9, 'Rear Closed':10}

    create_frame_cols  = ['PNR', 'Tool name', 'Step-lap type','Step-lap count',
                            'Open-Close config', 'Skewed'] # Added Skewed
    
    # gui help for this thing
    tool_name_tuple = ('fm45', 'fp45', 'f0', 'v', 'h', 's', 'ys', 
                       'fish_head', 'fish_tail','prrp45',
                       'pfrm45', 'prrf0', 'pfrf0', 'prlm45', 'prlf0',
                       'pflp4', 'pflf0')
    
    color_cyan = 'cyan'
    color_black = 'black'
    color_grey = 'grey'
    color_green = 'green'
    color_red = 'red'
    
    name = 'name'
    pos = 'pos'
    is_front = 'is_front'
    is_rear = 'is_rear'
    end = 'end'
    linestyle = 'linestyle'
    from_json = 'from_json'
    from_db = 'from_db'
    main_frame = 'main_frame'
    reset = 'reset'
    update = 'update'
    Reset = 'Reset'
    Update = 'update'
    data = 'data'
    steplap_count = 'steplap_count'
    open_code = 'open_code'
    steplap_distance = 'steplap_distance'
    
    
    msgbox_showwarning = 'showwarning'
    msgbox_showinfo = 'showinfo'
    
    warnmsg_empty_object = 'Cannot display empty object.'
    infomsg_run_sy_profile = 'You are running a split-yoke profile.'
    infomsg_run_cl_profile = 'You are running a central-limb profile.'
    infomsg_run_sly_profile = 'You are running a sidelimb-yoke profile.'
    infomsg_build_successful = 'Profile build successful.'
    
    path_gui = '../gui/'
    path_program_input = '../cut_program_input/'
    
    title_param_update = 'Parameter Update Screen'
    
    label_skewed = "Skewed"
    
    
    
    
    