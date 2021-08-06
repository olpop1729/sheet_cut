#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 13:28:35 2021

@author: omkar
"""

from tkinter import Tk, Button, Label, Entry, messagebox, StringVar
from tkinter import ttk
import json
from run_screen import RunScreen
from update_param import UpdateParamScreen

class labels:
    steplap_type_map = {'No step-lap':0, 'Horizontal (Longitudinal)':1, 
                        'Vertical (Lateral)':2, 'Skewed (Lateral)':3}
    attr_map = {''}
    open_code_map = {'NA':0, 'Open':1, 'Closed':2, 'Front Open, Rear Open':3, 
                     'Front Open, Rear Closed':4, 'Front Closed, Rear Open':5, 
                     'Front Closed, Rear Closed':6, 'Front Open':7, 'Front Closed':8, 
                     'Rear Open':9, 'Rear Closed':10}
    
    create_frame_cols  =['PNR', 'Tool name', 'Step-lap type','Step-lap count', 
                            'Open-Close config']
    
    tool_name_tuple = ('fm45', 'fp45', 'f0', 'v', 'h', 's', 'y')
    
    

class MainWindow:
    
    def __init__(self):
        self._tk = Tk()
        self._content = {}
        self.__initScreen(self._tk)
        
    def __initScreen(self, parent):
        parent.geometry("500x200")
        parent.title('Main Window')
        content = {}
        
        content['frames'] = []
        
        
        content['buttons'] = []
        content['buttons'].append(Button(parent, text='Create',
                                         command=self._createScreen))
        content['buttons'].append(Button(parent, text='Run', 
                                         command=self._run_screen))
        content['buttons'].append(Button(parent, text='Paramters', 
                                         command=self._update_parameters))
        
        
        content['labels'] = []
        
        self.content = content
        for i in content:
            for j in content[i]:
                j.pack()
        
        parent.mainloop()
        
    def _update_parameters(self):
        UpdateParamScreen()
        
    def _run_screen(self):
        RunScreen()
        
    def _createScreen(self):
        CreateCutProgramScreen()

class CreateCutProgramScreen:

    def __init__(self):
        self._tk = Tk()
        self._content = {}
        self._tools = labels.tool_name_tuple
        self._frame_cols = labels.create_frame_cols
        self._index_map = {0:'name', 1:'steplap_type', 2:'steplap_count', 
                           3:'open_code', 4:'_steplap_distance'}
        
        self.__initScreen(self._tk)
        
    def __initScreen(self, parent):
        parent.title('Create program screen.')
        
        content = {}
        
        frame = ttk.Frame(parent)
        frame.pack()
        content['frame_table'] = frame
        
        
        content['button_addrow'] = Button(parent, text='Add row', command=self._addRow)
        content['button_addrow'].pack(side='left')
        
        content['button_del_last'] = Button(parent, text='Delete last', 
                                            command=self._delete_last)
        content['button_del_last'].pack(side='left')
        
        content['save_frame'] = ttk.Frame(parent)
        
        content['button_save'] = Button(content['save_frame'], text='Save',
                                        command=self._save)
        content['button_save'].grid(row=0, column=0)
        content['file_name'] = Entry(content['save_frame'])
        content['file_name'].grid(row=0, column=1)
        
        
        content['entries'] = []
        content['column_labels'] = []
        content['combo_values'] = []
        
        for i in range(len(self._frame_cols)):
            label = Label(content['frame_table'],text = self._frame_cols[i])
            label.grid(row= 0, column = i)
            content['column_labels'].append(label)
        
        for i in range(1):
            row = []
            for j in range(len(self._frame_cols)):
                if j == 1:
                    values = StringVar()
                    e = ttk.Combobox(content['frame_table'], textvariable = values)
                    e['values'] = ('fm45', 'fp45', 'f0', 'h', 'v', 
                                   's', 'ys', 'prr')
                    e.grid(row = i+1, column=j)
                elif j == len(self._frame_cols) - 1:
                    values = StringVar()
                    e = ttk.Combobox(content['frame_table'], textvariable=values)
                    e['values'] = tuple(i for i in labels.open_code_map.keys())
                    e.grid(row=i+1, column=j)
                    e.current(0)
                elif j == 2:
                    e = ttk.Combobox(content['frame_table'], textvariable=StringVar())
                    e['values'] = tuple(i for i in labels.steplap_type_map.keys())
                    e.grid(row=i+1, column=j)
                    e.current(0)
                else:
                    e = Entry(content['frame_table'])
                    e.grid(row = i+1, column = j)
                row.append(e)
                
            content['entries'].append(row)
                
        self.content = content
        content['save_frame'].pack()
        parent.mainloop()
        
    def _save(self):
        file_name = self.content['file_name'].get()
        if not file_name:
            messagebox.showwarning("showwarning", "File name is required.")
            return
        rows = self.content['entries']
        tools = []
        for row in rows:
            tool = []
            for i in range(len(row)):
                if not row[1].get():
                    messagebox.showwarning("showwarning", "Please remove empty rows.")
                    return
                tool.append(row[i].get())
            tools.append(tool)
            
        self._process_input(tools, file_name)
        
    def _process_input(self, tools, fn):
        data = {}
        for i in range(len(tools)):
            datum = {}
            datum[self._index_map[0]] = tools[i][1]
            datum[self._index_map[1]] = labels.steplap_type_map[tools[i][2]]
            if not tools[i][3]:
                datum[self._index_map[2]] = 1
            else:
                datum[self._index_map[2]] = int(tools[i][3])
            datum[self._index_map[3]] = labels.open_code_map[tools[i][4]]
            
            #access to this datum entry should be hidden from the user.
            datum[self._index_map[4]] = 0
            
            data[i] = datum
        
        self._clump_data(data)
        
        path = '../cut_program_input/' + fn + '.json'
        
        with open( path , 'w') as fp:
            fp.write(json.dumps(data, indent=4))
        #print('write successfull')   
        
    def _clump_data(self, data):
        
        # add a verifier here
        
        # data = self.content
        # for i in range(10):
        #     list_d = data[i]
        #     for j in list_d:
        #         if j._has_steplap():
        #             return False
        pass
        
    def _addRow(self):
        last_row = len(self.content['entries'])+1
        row = []
        for i in range(len(self._frame_cols)):
            if i == 1:
                values = StringVar()
                e = ttk.Combobox(self.content['frame_table'], textvariable = values)
                e['values'] = ('fm45', 'fp45', 'f0', 'h', 'v', 
                               's', 'ys')
                e.grid(row = last_row, column=i)

            elif i == len(self._frame_cols) - 1:
                values = StringVar()
                e = ttk.Combobox(self.content['frame_table'], textvariable=values)
                e['values'] = tuple(i for i in labels.open_code_map.keys())
                e.grid(row=last_row, column=i)
                e.current(0)
                e.state(['readonly'])
            elif i == 2:
                e = ttk.Combobox(self.content['frame_table'], textvariable=StringVar())
                e['values'] = tuple(i for i in labels.steplap_type_map.keys())
                e.grid(row=last_row, column=i)
                e.current(0)
                e.state(['readonly'])
                
            else:
                e = Entry(self.content['frame_table'])
                e.grid(row=last_row, column=i)
            row.append(e)
        self.content['entries'].append(row)
        
    def _delete_last(self):
        if self.content['entries']:
            for i in range(len(self._frame_cols)):
                self.content['entries'][-1][-1-i].destroy()
            self.content['entries'].pop()
        else:
            print('No row to delete.')
            
 
mw = MainWindow()