#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  8 19:26:43 2021

@author: omkar
"""

from tkinter import Tk, Button, Entry, Listbox, END, Label, messagebox
from tkinter import ttk
from os import listdir
import json, re, sys


class UpdateParamScreen:
    
    config_file_name = 'config.json'
    
    def __init__(self):
        print('initial param screen check.')
        
        #load existing presets first.
        #self.load_params()
        #self.show_params()
        
        self._tk = Tk()
        
        self._init_screen(self._tk)
        #if none exist create new (to be added later)
        
        
    def _init_screen(self, parent):
        parent.geometry('900x400')
        
        content = {}
        
        parent.title('Parameter update screen.')
        
        content['main_frame'] = ttk.Frame(parent)
        
        content['reset'] = Button(content['main_frame'], text="Reset", 
                                  command=self._reset())
        
        content['update'] = Button(content['main_frame'], text="Update", 
                                  command=self._update())
        
        content['e_v_to_hole'] = Entry(content['main_frame'])
        content['l_v_to_hole'] = Label(content['main_frame'], 
                                       text='V to Hole distance')
        
        content['e_v_to_fm45'] = Entry(content['main_frame'])
        content['l_v_to_fm45'] = Label(content['main_frame'], 
                                       text='V to FM45 distance')
        
        content['e_fm45_offset'] = Entry(content['main_frame'])
        content['l_fm45_offset'] = Label(content['main_frame'], 
                                         text='FM45 Offset')
        
        content['e_fp45_offset'] = Entry(content['main_frame'])
        content['l_fp45_offset'] = Label(content['main_frame'], 
                                         text='FP45 Offset')
        
        content['e_f0_offset'] = Entry(content['main_frame'])
        content['l_f0_offset'] = Label(content['main_frame'], 
                                       text='F0 Offset')
        
        content['e_h_offset'] = Entry(content['main_frame'])
        content['l_h_offset'] = Label(content['main_frame'], 
                                      test='Hole Offset')
        
        content['e_v_to_hole'].grid(row=1, column=1)
        content['l_v_to_hole'].grid(row=1, column=0)
        
        content['e_v_to_fm45'].grid(row=2, column=1)
        content['l_v_to_fm45'].grid(row=2, column=0)
        
        content['e_fm45_offset'].grid(row=3, column=1)
        content['l_fm45_offset'].grid(row=3, column=0)
        
        content['e_fp45_offset'].grid(row=4, column=1)
        content['l_fp45_offset'].grid(row=4, column=0)
        
        content['e_f0_offset'].grid(row=5, column=1)
        content['l_f0_offset'].grid(row=5, column=0)
        
        
        content['reset'].grid(row=0, column=0)
        content['update'].grid(row=0, column=1)
        
        content['main_frame'].grid()
        
        self.content = content
        
        #self.load_params()

        
    def _reset(self):
        print('Reset logic here.')
    
    def _update(self):
        print('Update logic here.')
        
   
    def load_params(self):
        with open(UpdateParamScreen.config_file_name, 'r') as fp:
            print('file pointer created successfully.')
            params = json.load(fp)
        
        self.params = params
        
        self.content['e_fm45_offset'].insert(END, self.params['fm45_offset'])
        self.content['e_f945_offset'].insert(END, self.params['fp45_offset'])
        self.content['e_f0_offset'].insert(END, self.params['f0_offset'])
    
    def create_params(self):
        name = ''
        if name in self.params.keys():
            print('Parameter with name already exists. Please change name.')
    
    #create integer parameters
    def show_params(self):
        for i in self.params:
            print(i, ' - ', self.params[i])
            
    
    
    
class ConfigHolder:
    
    def __init__(self):
        pass