#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 11:39:24 2022

@author: omkar
"""

from config import Config
import itertools
import pandas as pd
import sys

class PandasWriterReader:
    
    def writeExcel(fname='Trial', **kwargs):
        if len(kwargs.keys()) < len(Config.EXCEL_COLUMN_NAMES):
            sys.exit(0)
        cut_feed = list(itertools.zip_longest(kwargs['feed'], kwargs['v_axis'],kwargs['sec_feed'],
                    kwargs['operation'], kwargs['tool_number'], 
                    kwargs['start_index'], kwargs['end_index'], 
                    kwargs['job_shape'], kwargs['number_of_steps'], 
                    kwargs['sheet_count'], kwargs['p45_overcut'], 
                    kwargs['m45_overcut'], kwargs['yoke_len'],
                    kwargs['leg_len'], kwargs['cl_len']))
        df = pd.DataFrame(data = cut_feed, columns=Config.EXCEL_COLUMN_NAMES)
        df.index += 1
        temp = pd.ExcelWriter('../cut_program_output/' + fname + '.xlsx')
        df.to_excel(temp)
        temp.save()