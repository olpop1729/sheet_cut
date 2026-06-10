#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 22 22:31:33 2021

@author: omkar
"""




import pandas as pd
# The executable tools class for exportin to the excel sheet.



class IdentityMap:
    pass



class eTool:
    
    # tool initiaization here
    def __init__(self, name, long, lat, count):
        self.name = name
        self.long = long
        self.lat = lat
        self.count = count
    
    
class eProfile:
    
    def __init__(self):
        self.lens = []
        self.etl = []