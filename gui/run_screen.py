#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  1 18:06:25 2021

@author: omkar
"""

from tkinter import Tk, Button, Entry, Listbox, END, Label, messagebox
from tkinter import ttk
from os import listdir
from display_screen import DisplayWindow
from central_limb_v2 import TooList_CL
import json, re, sys
sys.path.insert(1, '../step_lap/')
from step_lap_v4 import ToolList

class AutoCompleteEntry:
    
    def __init__(self, db, parent, master):
        self.master = master
        self.e = Entry(parent)
        self.e.bind('<KeyRelease>', self._on_keyrelease)
        self.db = db
        self.lb = Listbox(parent)
        for i in db:
            self.lb.insert('end', i)
        self.lb.bind('<<ListboxSelect>>', self._on_select)
        self.e.grid(row = 0, column=1)
        self.lb.grid(row = 1, column = 1)
        
    def _matches(fieldValue, acListEntry):
        pattern = re.compile(re.escape(fieldValue) + '.*', re.IGNORECASE)
        return re.match(pattern, acListEntry)
        
    def _on_select(self, event):
        # print('(event) previous:', event.widget.get('active'))
        # print('(event)  current:', event.widget.get(event.widget.curselection()))
        # print('---')
        selection = event.widget.curselection()
        if selection:
            self.e.delete(0, 'end')
            self.e.insert('end', event.widget.get(event.widget.curselection()))
            self.master._get_params()
        
    def _on_keyrelease(self, event):
        value = event.widget.get()
        if value == '':
            data = self.db
        else:
            data = []
            for item in self.db:
                if value in item:
                    data.append(item)
                    
        self.lb.delete(0, 'end')
        for i in data:
            self.lb.insert('end', i)


class RunScreen:
    
    #initial display screen for the main execution parent screen
    #if not throw an error message onto the parent screen
    def __init__(self):
        self._tk = Tk()
        self._file_names = self._get_file_names()
        self._init_screen(self._tk)
        self._ptype = 1 # default profile - type (normal profiles ie. sidelimb yoke)
    
    #passive display of filenames, only invoked at the initialization.
    #does not, recursively, check for the file changes.
    def _get_file_names(self):
        path = '../cut_program_input/'
        return [i for i in listdir(path) if i.endswith('.json')]


    #parent screen initializaion     
    def _init_screen(self, parent):
        parent.geometry('900x400')
        content = {}
        
        parent.title('Run program')
        # frame row 0
        content['btn_frame'] = ttk.Frame(parent)
        content['btn_frame'].grid(row=0, column = 1)
         
        content['display_btn'] = Button(content['btn_frame'], text='Display', 
                                        command=self._display_program)
        content['display_btn'].grid(row=0, column=0)
        
        content['get_lens'] = Button(content['btn_frame'], text='Get Lengths', 
                                     command=self._get_params)
        content['get_lens'].grid(row=0, column=1)
        
        
        #frame row 1
        content['output_frame'] = ttk.Frame(parent)
        content['output_frame'].grid(row=1, column=0)
        
        
        content['execution_frame'] = ttk.Frame(parent)
        
        content['output_entry'] = Entry(content['execution_frame'])
        content['output_entry'].insert(END, 'file_name')
        content['output_entry'].grid(row=1, column=0)
        content['output_btn'] = Button(content['execution_frame'], text='Execute', 
                                       command=self._execute_prog)
        content['output_btn'].grid(row=1, column=1)
        
        content['execution_frame'].grid(row=2, column = 1)
        
        content['search_entry'] = AutoCompleteEntry(self._file_names, 
                                                    content['output_frame'], self)
        
                
        self.content = content
        
        
    #get all the parameters from the input screen then pass on to the executing
    #object
    def _execute_prog(self):
            
        
        content = self.content
        slp_dlist = []
        #get the steplap distances
        for i in content['steplap_ds']:
            d = i.get()
            if not d:
                slp_dlist.append(0)
            else:
                slp_dlist.append(float(d))
                
        l_list = []
        #get the lengths from the input screen
        for i in content['li_entries']:
            l = i.get()
            if not l:
                l_list.append(0)
            else:
                l_list.append(float(l))
                
                
        #get the scrap lenght if necessary
        scrap_length = 0
        if self._ptype == 3:
            scrap_length = int(self.content['scrap_entry'].get())
            
            if scrap_length < 0:
                messagebox.showwarning("showwarning", "Scrap length cannot be 0.")
                return
        
        
        file_name = self.content['output_entry'].get()
        
        if file_name == 'file_name' or file_name == None:
            messagebox.showwarning("showwarning", "Please enter a valid file name.")
            return

            
        s_no = int(self.content['start_sheet'].get())
        
        if s_no <= 0:
            messagebox.showwarning("showwarning", "Initial sheet count starts at 1.")
            return 
            
        layers = int(self.content['layer_input'].get())
        if layers != 1:
            messagebox.showwarning("showwarning", "Layer count cannot be 0 (Supports only one layer in this update).")
            return
        
            
        if self._ptype in [3, 4, 5]:
            messagebox.showinfo("showinfo", "You are running a centralimb profile.")
            self._run_clprofile(self.data, slp_dlist, l_list, file_name, s_no,
                                scrap_length, self._ptype, layers)
            
        elif self._ptype == 2:
            messagebox.showinfo("showinfo","You are running a split-yoke profile.")
            self._run_syprofile(self.data, slp_dlist, l_list, file_name, s_no)
        
        else:
            messagebox.showinfo("showinfo", "You are running a side-limb yoke profile.")
            self._run_slyprofile(self.data, slp_dlist, l_list, file_name, s_no)
        
    #run side limb profile
    def _run_slyprofile(self, data, d, l, fn, sno):
        
        if self._ptype == 1:
            a = ToolList(data = data, d_list = d, l_list = l, f_name = fn, s_no=sno)
            if a :
                messagebox.showinfo("showinfo", "Profile build successful.")
            #eProfile(a)
            
            
    # run central limb profile
    def _run_clprofile(self, data, d, l, fn, sno, scrap_l, p_type, layers):
        a = TooList_CL(data = data , d_list = d, l_list = l , 
                       f_name = fn, s_no = sno, scrap_length = scrap_l, 
                       p_type = self._ptype, layers = layers)
        if a :
            messagebox.showinfo("showinfo", "Profile build successful.")
    
    
    # run split yoke profile
    def _run_syprofile(self):
        pass
        
        
    #initialize the input parameter fields
    def _get_params(self):
        path = '../cut_program_input/'
        if 'li_labels' in self.content :
            for i in self.content['li_labels']:
                i.destroy()
            for i in self.content['li_entries']:
                i.destroy()
                
            del self.content['li_labels']
            del self.content['li_entries']
            
        if 'steplap_ds' in self.content:
            for i in self.content['steplap_ds']:
                i.destroy()
            for i in self.content['steplap_label']:
                i.destroy()
                
            del self.content['steplap_ds']
            del self.content['steplap_label']
        
        #try making the file paths more modular
        file_name = path + self.content['search_entry'].e.get()
        new_frame = ttk.Frame(self._tk)
        data = {}
        with open(file_name, 'r') as fp:
            data = json.load(fp)
        self.data = data
        n = len(data.keys())
        labels = []
        entries = []
        for i in range(n-1):
            labels.append(Label(new_frame, text=f'L{i+1}'))
            entries.append(Entry(new_frame))

        new_frame.grid(row=1, column=1)        
        for i in range(n-1):
            labels[i].grid(row = i, column = 0)
            entries[i].grid(row=i, column=1)
            
        self.content['li_labels'] = labels
        self.content['li_entries'] = entries
        
        #step-lap associated with each tools
        
        self.content['steplap_ds'] = []
        self.content['steplap_label'] = []
        self.content['param_frame'] = ttk.Frame(self._tk)
        
        
        # ptype mapping done here
        for i in data:
            if data[i]['name'] == 's':
                if data[i]['steplap_type'] == 2:
                    self._ptype = 4
                    break
                else:
                    self._ptype = 3
            elif data[i]['name'] == 'ys':
                self._ptype = 2
                break
            
            else:
                self._ptype = 1
                
        for i in data:
            if data[i]['name'] in ['fish_head', 'fish_tail']:
                if data[i]['steplap_type'] == 2:
                    self._ptype = 5
                    break
                
        for i in data:
            if data[i]['steplap_count'] > 1:
                self.content['steplap_label'].append(Label(self.content['param_frame'], 
                                                           text=f'Step-lap distance for {data[i]["name"]}({int(i)+1}) '))
                self.content['steplap_ds'].append(Entry(self.content['param_frame']))
                self.content['steplap_ds'][-1].insert(END, 0)

                
        for i in range(len(self.content['steplap_ds'])):
            self.content['steplap_label'][i].grid(row=i, column=0)
            self.content['steplap_ds'][i].grid(row=i, column=1)
            
        if ('layer_label' in self.content.keys()):
            self.content['layer_label'].destroy()
            del self.content['layer_label']
            
        if ('layer_input' in self.content.keys()):
            self.content['layer_input'].destroy()
            del self.content['layer_input']
            
        if ('start_sheet' in self.content.keys()):
            self.content['start_sheet'].destroy()
            del self.content['start_sheet']
            
        if ('starts_label' in self.content.keys()):
            self.content['starts_label'].destroy()
            del self.content['starts_label']
            
        if ('scrap_entry' in self.content.keys()):
            print('deleting scrap')
            self.content['scrap_entry'].destroy()
            del self.content['scrap_entry']
            
        if ('scrap_label' in self.content.keys()):
            self.content['scrap_label'].destroy()
            del self.content['scrap_label']
            
            
        if ('steplap_ds' in self.content):
            row_no = len(self.content['steplap_ds'])
        else:
            row_no = 0
        self.content['layer_label'] = Label(self.content['param_frame'], 
                                            text='Layers')
        self.content['layer_label'].grid(row=row_no, column=0)
        
        self.content['layer_input'] = Entry(self.content['param_frame'])
        self.content['layer_input'].insert(END, 0)
        self.content['layer_input'].grid(row = row_no, column=1)
        
        self.content['start_sheet'] = Entry(self.content['param_frame'])
        self.content['start_sheet'].insert(END, 1)
        self.content['start_sheet'].grid(row=row_no+1, column=1)
        
        self.content['starts_label'] = Label(self.content['param_frame'], 
                                             text='Start Sheet')
        self.content['starts_label'].grid(row=row_no+1, column=0)
        
        if self._ptype in [3, 4, 5]:
            self.content['scrap_entry'] = Entry(self.content['param_frame'])
            self.content['scrap_entry'].insert(END, 0)
            self.content['scrap_entry'].grid(row=row_no+2, column=1)
            
            self.content['scrap_label'] = Label(self.content['param_frame'], 
                                             text='Scrap Length')
            self.content['scrap_label'].grid(row=row_no+2, column=0)
            
            
            
        self.content['param_frame'].grid(row=1, column=2)
        
                
                
    def _display_program(self):
        name = self.content['search_entry'].e.get()
        if not name:
            print('nothing here')
            return
        else:
            try:
                path ='../cut_program_input/'+name
                with open(path, 'r') as fp:
                    data = json.load(fp)
                DisplayWindow(data)
            except FileNotFoundError as err:
                print(err)
                return

            
        
        