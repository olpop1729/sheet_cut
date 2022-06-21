#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  8 19:26:43 2021

@author: omkar
"""

from tkinter import Tk, Button, Entry, END, Label, messagebox
from tkinter import ttk
import json
from config import Config
from label_file import Labels


class UpdateParamScreen:
    Config = Config()
    
    def __init__(self):
        
        #load existing presets first.
        #self.load_params()
        #self.show_params()
        
        self._tk = Tk()
        
        self._init_screen(self._tk)
        #if none exist create new (to be added later)
        
        
    def _init_screen(self, parent):
        parent.geometry('900x400')
        
        content = {}
        
        parent.title(Labels.title_param_update)
        
        content['main_frame'] = ttk.Frame(parent)
        

        content['e_v_to_hole'] = Entry(content[Labels.main_frame])
        content['l_v_to_hole'] = Label(content[Labels.main_frame], 
                                       text='V to Hole distance')
        content['u_v_to_hole'] = Label(content[Labels.main_frame], 
                                       text='mm')
        
        content['e_v_to_fm45'] = Entry(content[Labels.main_frame])
        content['l_v_to_fm45'] = Label(content[Labels.main_frame], 
                                       text='V to FullCut distance')
        content['u_v_to_fm45'] = Label(content[Labels.main_frame], 
                                       text='mm')
        
        content['e_fm45_offset'] = Entry(content[Labels.main_frame])
        content['l_fm45_offset'] = Label(content[Labels.main_frame], 
                                         text='FM45 Offset')
        content['u_fm45_offset'] = Label(content[Labels.main_frame], 
                                       text='mm')
        
        
        content['e_fp45_offset'] = Entry(content[Labels.main_frame])
        content['l_fp45_offset'] = Label(content[Labels.main_frame], 
                                         text='FP45 Offset')
        content['u_fp45_offset'] = Label(content[Labels.main_frame], 
                                       text='mm')
        
        content['e_f0_offset'] = Entry(content[Labels.main_frame])
        content['l_f0_offset'] = Label(content[Labels.main_frame], 
                                       text='F0 Offset')
        content['u_f0_offset'] = Label(content[Labels.main_frame], 
                                       text='mm')
        
        content['e_h_offset'] = Entry(content[Labels.main_frame])
        content['l_h_offset'] = Label(content[Labels.main_frame], 
                                      text='Hole Offset')
        content['u_h_offset'] = Label(content[Labels.main_frame], 
                                       text='mm')
        
        content['e_v_lat_offset'] = Entry(content[Labels.main_frame])
        content['l_v_lat_offset'] = Label(content[Labels.main_frame], 
                                          text='V Lateral Offset')
        content['u_v_lat_offset'] = Label(content[Labels.main_frame], 
                                       text='mm')
        
        content['e_output_directory'] = Entry(content[Labels.main_frame])
        content['l_output_directory'] = Label(content[Labels.main_frame], 
                                          text='Output Directory')
        
        content['e_coil_start_pos'] = Entry(content[Labels.main_frame])
        content['l_coil_start_pos'] = Label(content[Labels.main_frame], 
                                          text='Coil Start Position')
        content['u_coil_start_pos'] = Label(content[Labels.main_frame], 
                                       text='mm')
        
        content['e_coil_length'] = Entry(content[Labels.main_frame])
        content['l_coil_length'] = Label(content[Labels.main_frame], 
                                          text='Coil Length')
        content['u_coil_length'] = Label(content[Labels.main_frame], 
                                       text='mm')
        
        
       
        content['u_v_to_hole'].grid(row=1, column=2)
        content['e_v_to_hole'].grid(row=1, column=1)
        content['l_v_to_hole'].grid(row=1, column=0)
        
        content['u_v_to_fm45'].grid(row=2, column=2)
        content['e_v_to_fm45'].grid(row=2, column=1)
        content['l_v_to_fm45'].grid(row=2, column=0)
        
        content['u_fm45_offset'].grid(row=3, column=2)
        content['e_fm45_offset'].grid(row=3, column=1)
        content['l_fm45_offset'].grid(row=3, column=0)
        
        content['u_fp45_offset'].grid(row=4, column=2)
        content['e_fp45_offset'].grid(row=4, column=1)
        content['l_fp45_offset'].grid(row=4, column=0)
        
        content['u_f0_offset'].grid(row=5, column=2)
        content['e_f0_offset'].grid(row=5, column=1)
        content['l_f0_offset'].grid(row=5, column=0)
        
        content['u_v_lat_offset'].grid(row=6, column=2)
        content['e_v_lat_offset'].grid(row=6, column=1)
        content['l_v_lat_offset'].grid(row=6, column=0)
        
        content['e_output_directory'].grid(row=7, column=1)
        content['l_output_directory'].grid(row=7, column=0)
        
        content['u_coil_start_pos'].grid(row=8, column=2)
        content['e_coil_start_pos'].grid(row=8, column=1)
        content['l_coil_start_pos'].grid(row=8, column=0)
        
        content['u_coil_length'].grid(row=9, column=2)
        content['e_coil_length'].grid(row=9, column=1)
        content['l_coil_length'].grid(row=9, column=0)
        
        
        content['main_frame'].grid()
        
        
        content[Labels.reset] = Button(content[Labels.main_frame], text=Labels.Reset, 
                                  command= lambda : self._reset())
        
        content[Labels.update] = Button(content[Labels.main_frame], text=Labels.Update, 
                                  command= lambda : self._update())
        
        content[Labels.reset].grid(row=0, column=0)
        content[Labels.update].grid(row=0, column=1)
        
        self.content = content
        
        self.load_params()

        
    def _reset(self):
        print('Reset logic here.')
    
    def _update(self):
        
        conf = {}
        conf['OFFSET_FM45'] = float(self.content['e_fm45_offset'].get())
        conf['OFFSET_V_LAT'] = float(self.content['e_v_lat_offset'].get())
        conf['DISTANCE_HOLE_VNOTCH'] = float(self.content['e_v_to_hole'].get())
        conf['DISTANCE_SHEAR_VNOTCH'] = float(self.content['e_v_to_fm45'].get())
        conf['CUT_PROGRAM_OUTPUT_DIRECTORY'] = self.content['e_output_directory'].get()
        conf['COIL_START_POSITION'] = float(self.content['e_coil_start_pos'].get())
        conf['COIL_LENGTH'] = float(self.content['e_coil_length'].get())
        conf['OFFSET_FP45'] = float(self.content['e_fp45_offset'].get())
        conf['OFFSET_F0'] = float(self.content['e_f0_offset'].get())
        
        path = 'config.json'
        
        with open( path , 'w') as fp:
            fp.write(json.dumps(conf, indent=4))
        #print('write successfull')
        messagebox.showinfo("showinfo", " Parameters updated")
            
        self._tk.destroy()
        
   
    def load_params(self):
        path = 'config.json'
        with open(path, 'r') as fp:
            params = json.load(fp)
        
        self.params = params
        
        self.content['e_fm45_offset'].insert(END, self.params['OFFSET_FM45'])
        self.content['e_fp45_offset'].insert(END, self.params['OFFSET_FP45'])
        self.content['e_f0_offset'].insert(END, self.params['OFFSET_F0'])
        self.content['e_v_lat_offset'].insert(END, self.params['OFFSET_V_LAT'])
        self.content['e_v_to_hole'].insert(END, self.params['DISTANCE_HOLE_VNOTCH'])
        self.content['e_v_to_fm45'].insert(END, self.params['DISTANCE_SHEAR_VNOTCH'])
        self.content['e_output_directory'].insert(END, self.params['CUT_PROGRAM_OUTPUT_DIRECTORY'])
        self.content['e_coil_start_pos'].insert(END, self.params['COIL_START_POSITION'])
        self.content['e_coil_length'].insert(END, self.params['COIL_LENGTH'])
        
        
    
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