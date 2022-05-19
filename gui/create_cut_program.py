#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 18:45:53 2022

@author: omkar
"""

from tkinter import Tk, Button, Label, Entry, messagebox, StringVar
from tkinter import ttk
import json
from label_file import Labels
from display_screen import DisplayWindow
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)


class CreateCutProgramScreen:

    def __init__(self):
        self._tk = Tk()
        self._content = {}
        self._tools = Labels.tool_name_tuple
        self._frame_cols = Labels.create_frame_cols
        self._index_map = {0:'name', 1:'steplap_type', 2:'steplap_count',
                           3:'open_code', 4:'_steplap_distance'}

        self.plot_flag = False
        self.__initScreen(self._tk)
        

    def __initScreen(self, parent):
        parent.title('Create program screen.')

        content = {}

        frame = ttk.Frame(parent)
        frame.pack()
        content['frame_table'] = frame
        
        content['func_frame'] = ttk.Frame(parent)


        content['button_addrow'] = Button(content['func_frame'], 
                                          text='Add row', 
                                          command=self._addRow)
        content['button_addrow'].pack(side='left')

        content['button_del_last'] = Button(content['func_frame'], 
                                            text='Delete last',
                                            command=self._delete_last)
        content['button_del_last'].pack(side='left')
        
        content['button_display'] = Button(content['func_frame'], 
                                           text='Display', 
                                           command=self._display)
        content['button_display'].pack(side='left')

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
                    #e['values'] = ('fm45', 'fp45', 'f0', 'h', 'v',
                    #               's', 'ys', 'prr')
                    e['values'] = Labels.tool_name_tuple
                    e.grid(row = i+1, column=j)
                elif j == len(self._frame_cols) - 1:
                    values = StringVar()
                    e = ttk.Combobox(content['frame_table'], textvariable=values)
                    e['values'] = tuple(i for i in Labels.open_code_map.keys())
                    e.grid(row=i+1, column=j)
                    e.current(0)
                elif j == 2:
                    e = ttk.Combobox(content['frame_table'], textvariable=StringVar())
                    e['values'] = tuple(i for i in Labels.steplap_type_map.keys())
                    e.grid(row=i+1, column=j)
                    e.current(0)
                else:
                    e = Entry(content['frame_table'])
                    e.grid(row = i+1, column = j)
                row.append(e)

            content['entries'].append(row)
            
        content['display_frame'] = ttk.Frame(parent)

        content['func_frame'].pack()
        content['save_frame'].pack()
        content['display_frame'].pack()
        
        self.content = content
        
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
            datum[self._index_map[1]] = Labels.steplap_type_map[tools[i][2]]
            if not tools[i][3]:
                datum[self._index_map[2]] = 1
            else:
                datum[self._index_map[2]] = int(tools[i][3])
            datum[self._index_map[3]] = Labels.open_code_map[tools[i][4]]

            #access to this datum entry should be hidden from the user.
            datum[self._index_map[4]] = 0

            data[i] = datum

        self._clump_data(data)

        path = '../cut_program_input/' + fn + '.json'

        with open( path , 'w') as fp:
            fp.write(json.dumps(data, indent=4))
        #print('write successfull')
        messagebox.showinfo("showinfo", fn + " saved succesfully.")
        

    def _clump_data(self, data):

        #cycle through the data and find the corrresponding partial sequences
        #for i in data:
        #    #partial cut name start with pr or pf, use them as identifiers
        #    if data[i].name == 'pr' or data[i].name == 'pf':
        #        pass
    
        pass
    
    
    
    def _addRow(self):
        last_row = len(self.content['entries'])+1
        row = []
        for i in range(len(self._frame_cols)):
            if i == 1:
                values = StringVar()
                e = ttk.Combobox(self.content['frame_table'], textvariable = values)
                e['values'] = Labels.tool_name_tuple
                
                e.grid(row = last_row, column=i)

            elif i == len(self._frame_cols) - 1:
                values = StringVar()
                e = ttk.Combobox(self.content['frame_table'], textvariable=values)
                e['values'] = tuple(i for i in Labels.open_code_map.keys())
                e.grid(row=last_row, column=i)
                e.current(0)
                e.state(['readonly'])
            elif i == 2:
                e = ttk.Combobox(self.content['frame_table'], textvariable=StringVar())
                e['values'] = tuple(i for i in Labels.steplap_type_map.keys())
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
            
    def _display(self):
        tools = []
        rows = self.content['entries']
        for row in rows:
            tool = []
            for i in range(len(row)):
                if not row[1].get():
                    messagebox.showwarning("showwarning", "Please remove empty rows.")
                    return
                tool.append(row[i].get())
            tools.append(tool)
        data = {}
        for i in range(len(tools)):
            datum = {}
            datum[self._index_map[0]] = tools[i][1]
            datum[self._index_map[1]] = Labels.steplap_type_map[tools[i][2]]
            if not tools[i][3]:
                datum[self._index_map[2]] = 1
            else:
                datum[self._index_map[2]] = int(tools[i][3])
            datum[self._index_map[3]] = Labels.open_code_map[tools[i][4]]

            #access to this datum entry should be hidden from the user.
            datum[self._index_map[4]] = 0

            data[i] = datum
            
        width = len(data.keys())
        
        if not self.plot_flag:
            self.display_fig = Figure(figsize = (width + 3, 5), 
                                      dpi = 100)
            self.display_plot = self.display_fig.add_subplot(111)
            
            self.canvas = FigureCanvasTkAgg(self.display_fig, 
                                       master = self.content['display_frame'])
            
            self.plot_flag = True
        
        else:
            self.display_fig.set_figwidth(width + 6)
            self.canvas.config(width=width, height=5)
            self.display_plot.clear()
            
        y = [i**2 for i in range(101)]
        self.display_plot.plot(y)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()
            
        # def _tk_grapher(data, frame):
            
        #     if not data:
        #         return
            
        #     else:
        #         fig = Figure(figsize = (12, 5), dpi = 100)
        #         y = [i**2 for i in range(101)]
        #         plot1 = fig.add_subplot(111)
        #         plot1.plot(y)
        #         # fig.set_figheight(12)
        #         # fig.set_figwidth(3)
        #         canvas = FigureCanvasTkAgg(fig, 
        #                                     master = frame)
        #         canvas.draw()
        #         canvas.get_tk_widget().pack()
                
        #         toolbar = NavigationToolbar2Tk(canvas, 
        #                                         frame)
        #         toolbar.update()
        #         canvas.get_tk_widget().pack()

                
            
        # _tk_grapher(data, self.content['display_frame'])
        
        #DisplayWindow(on_screen=data)
        
        
        
        
        
        
        
        
        
        