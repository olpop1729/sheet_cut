#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  1 18:06:25 2021

@author: omkar
"""

from tkinter import Tk, Button, Entry, Listbox, END, Label, Toplevel, messagebox
from tkinter import ttk
from os import listdir
from display_screen import DisplayWindow
from matplotlib.figure import Figure # Keep Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from central_limb_v2 import TooList_CL
from label_file import Labels
import json, re, sys, os # Added os for path joining

sys.path.insert(1, '../step_lap/')
from step_lap_v4 import ToolList
import matplotlib.pyplot as plt # Import pyplot for plt.close()

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
        
    @staticmethod
    def _matches(fieldValue, acListEntry):
        pattern = re.compile(r'^' + re.escape(fieldValue) + r'.*', re.IGNORECASE) # Ensure starts with
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
                # Use "startswith" for typical autocomplete behavior
                if item.lower().startswith(value.lower()):
                    data.append(item)
                    
        self.lb.delete(0, 'end')
        for i in data:
            self.lb.insert('end', i)


class RunScreen:
    BASE_PROGRAM_INPUT_PATH = '../cut_program_input/'
    BASE_DATA_PATH = '../data/'
    
    def __init__(self, parent_tk):
        self.parent_tk = parent_tk
        self.toplevel = Toplevel(parent_tk)
        self.toplevel.protocol("WM_DELETE_WINDOW", self._on_close) # Handle window close
        self.data = None # Initialize self.data
        self._ptype = 1 # default profile - type (normal profiles ie. sidelimb yoke)
        self._file_names = self._get_file_names()
        # Initialize Matplotlib embedding attributes
        self.figure = None
        self.plot_ax = None
        self.canvas = None
        self.canvas_widget = None # To store the Tk widget from the canvas
        self._init_screen(self.toplevel)
        # self._ptype = 1 # default profile - type (normal profiles ie. sidelimb yoke) # Already initialized

    
    #passive display of filenames, only invoked at the initialization.

    def _get_file_names(self):
        try:
            return [f for f in listdir(RunScreen.BASE_PROGRAM_INPUT_PATH) if f.endswith('.json')]
        except FileNotFoundError:
            messagebox.showerror("Error", f"Directory not found: {RunScreen.BASE_PROGRAM_INPUT_PATH}", parent=self.toplevel if hasattr(self, 'toplevel') else self.parent_tk)
            return []

    #parent screen initialization
    def _init_screen(self, parent):
        # Increased height from 400 to 600
        parent.geometry('900x600')
        content = {}
        
        parent.title('Run program')
        # frame row 0
        # Configure grid weights for main window to allow display_frame's row/columns to expand
        parent.grid_rowconfigure(3, weight=1) # Row for display_frame
        parent.grid_columnconfigure(0, weight=1) # display_frame spans col 0,1,2
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_columnconfigure(2, weight=1)

        content['btn_frame'] = ttk.Frame(parent)
        content['btn_frame'].grid(row=0, column = 1, columnspan=2, sticky="ew")
         
        content['display_btn'] = Button(content['btn_frame'], text='Display', 
                                        command=self._display_program)
        content['display_btn'].grid(row=0, column=0)
        
        content['get_lens'] = Button(content['btn_frame'], text='Get Lengths', 
                                     command=self._get_lengths)
        content['get_lens'].grid(row=0, column=1)
        
        
        #frame row 1
        content['output_frame'] = ttk.Frame(parent)
        content['output_frame'].grid(row=1, column=0, sticky="ns")
        
        
        content['execution_frame'] = ttk.Frame(parent)
        
        content['output_entry'] = Entry(content['execution_frame'])
        content['output_entry'].insert(END, 'file_name')
        content['output_entry'].grid(row=1, column=0)
        content['output_btn'] = Button(content['execution_frame'], text='Execute', 
                                       command=self._execute_prog)
        content['output_btn'].grid(row=1, column=1)
        
        content['execution_frame'].grid(row=2, column=0, columnspan=3, sticky="ew")

        # Add a frame in the main window to display the plot
        content['display_frame'] = ttk.Frame(parent)
        content['display_frame'].grid(row=3, column=0, columnspan=3, sticky="nsew")
        
        content['search_entry'] = AutoCompleteEntry(self._file_names, 
                                                    content['output_frame'], self)
        
                
        self.content = content

    def _get_float_entry_value(self, entry_widget, field_name="Field", default_value=0.0):
        try:
            val_str = entry_widget.get()
            if not val_str:
                return default_value
            return float(val_str)
        except ValueError:
            messagebox.showerror("Input Error", f"Invalid numeric value for {field_name}.", parent=self.toplevel)
            return None # Indicates error

    def _get_int_entry_value(self, entry_widget, field_name="Field", allow_zero_or_negative=False, default_value=0):
        try:
            val_str = entry_widget.get()
            if not val_str: # If empty, return default
                return default_value
            val_int = int(val_str)
            if not allow_zero_or_negative and val_int <= 0:
                messagebox.showerror("Input Error", f"{field_name} must be a positive integer.", parent=self.toplevel)
                return None # Indicates error
            return val_int
        except ValueError:
            messagebox.showerror("Input Error", f"Invalid integer value for {field_name}.", parent=self.toplevel)
            return None # Indicates error

    #get all the parameters from the input screen then pass on to the executing
    #object
    def _execute_prog(self):
        if not self.data:
            messagebox.showerror("Error", "No program data loaded. Please select a file and click 'Display' or 'Get Lengths'.", parent=self.toplevel)
            return

        save_obj = {}
        content = self.content

        slp_dlist = []
        for idx, entry_widget in enumerate(content.get('steplap_ds', [])):
            val = self._get_float_entry_value(entry_widget, f"Steplap Distance {idx+1}")
            if val is None: return # Error occurred
            slp_dlist.append(val)
        save_obj['slp_dlist'] = slp_dlist
                
        l_list = []
        for idx, entry_widget in enumerate(content.get('li_entries', [])):
            val = self._get_float_entry_value(entry_widget, f"Length L{idx+1}")
            if val is None: return # Error occurred
            l_list.append(val)
        save_obj['l_list'] = l_list
                
        save_obj['_ptype'] = self._ptype

        scrap_length = 0
        if self._ptype in [3,4,5] and 'scrap_entry' in content: # Check if scrap_entry exists
            scrap_length = self._get_int_entry_value(content['scrap_entry'], "Scrap Length", allow_zero_or_negative=True) # Scrap can be 0
            if scrap_length is None: return # Error occurred
            if scrap_length < 0: # Specific check for negative if not covered by allow_zero_or_negative
                messagebox.showerror("Input Error", "Scrap length cannot be negative.", parent=self.toplevel)
                return
        save_obj['scrap_length'] = scrap_length
        
        file_name = self.content['output_entry'].get()
        if not file_name.strip() or file_name == 'file_name':
            messagebox.showerror("Input Error", "Please enter a valid output file name.", parent=self.toplevel)
            return

        s_no = self._get_int_entry_value(content['start_sheet'], "Start Sheet No.", allow_zero_or_negative=False)
        if s_no is None: return # Error occurred
        save_obj['s_no'] = s_no
            
        layers = self._get_int_entry_value(content['layer_input'], "Layers", allow_zero_or_negative=False)
        if layers is None: return # Error occurred
        save_obj['layers'] = layers
        
        
        #saving lengths/slp/layer info
        try:
            selected_program_file = self.content['search_entry'].e.get()
            if not selected_program_file:
                messagebox.showwarning("Warning", "No program file selected to save parameters against.", parent=self.toplevel)
            else:
                save_param_path = os.path.join(RunScreen.BASE_DATA_PATH, selected_program_file)
                os.makedirs(os.path.dirname(save_param_path), exist_ok=True)
                with open(save_param_path, 'w') as fp:
                    fp.write(json.dumps(save_obj, indent=4))
        except (IOError, OSError, json.JSONDecodeError) as err:
            messagebox.showerror("Save Error", f"Could not save parameters: {err}", parent=self.toplevel)
        except Exception as err: # Catch any other unexpected error
            messagebox.showerror("Save Error", f"An unexpected error occurred while saving parameters: {err}", parent=self.toplevel)
            
        if self._ptype in [3, 4, 5]:
            messagebox.showinfo("showinfo", f"You are running a centralimb profile. Program type - {self._ptype}", parent=self.toplevel)
            self._run_clprofile(self.data, slp_dlist, l_list, file_name, s_no,
                                scrap_length, self._ptype, layers)
            
        elif self._ptype == 2:
            messagebox.showinfo("showinfo","You are running a split-yoke profile.", parent=self.toplevel)
            self._run_syprofile(self.data, slp_dlist, l_list, file_name, s_no)
        
        else:
            messagebox.showinfo("showinfo", "You are running a side-limb yoke profile.", parent=self.toplevel)
            self._run_slyprofile(self.data, slp_dlist, l_list, file_name, s_no, layers)
        
    #run side limb profile
    def _run_slyprofile(self, data, d, l, fn, sno, layers):
        
        if self._ptype == 1:
            a = ToolList(data = data, d_list = d, l_list = l, f_name = fn, s_no=sno, 
                         layers = layers)
            if a :
                messagebox.showinfo("showinfo", "Profile build successful.", parent=self.toplevel)
            #eProfile(a)
            
            
    # run central limb profile
    def _run_clprofile(self, data, d, l, fn, sno, scrap_l, p_type, layers):
        a = TooList_CL(data = data , d_list = d, l_list = l , 
                       f_name = fn, s_no = sno, scrap_length = scrap_l, 
                       p_type = self._ptype, layers = layers)
        if a :
            messagebox.showinfo("showinfo", "Profile build successful.", parent=self.toplevel)
    
    
    # run split yoke profile
    def _run_syprofile(self):
        pass
    
    #get pre-existing values from the db
    def _get_lengths(self):
        selected_file = self.content['search_entry'].e.get()
        if not selected_file:
            # This can be an info message as it's not strictly an error if no file is selected yet
            # messagebox.showinfo("Info", "Select a program file to load its saved parameters.")
            return

        param_file_path = os.path.join(RunScreen.BASE_DATA_PATH, selected_file)
        try:
            with open(param_file_path, 'r') as fp:
                data = json.load(fp)

            l_list = data.get('l_list', [])
            if 'li_entries' in self.content:
                for i, entry_widget in enumerate(self.content['li_entries']):
                    if i < len(l_list) and entry_widget.winfo_exists():
                        entry_widget.delete(0, END)
                        entry_widget.insert(END, str(l_list[i]))
                    
            slp_dlist = data.get('slp_dlist', [])
            if 'steplap_ds' in self.content:
                for i, entry_widget in enumerate(self.content['steplap_ds']):
                    if i < len(slp_dlist) and entry_widget.winfo_exists():
                        self.content['steplap_ds'][i].delete(0, END)
                        self.content['steplap_ds'][i].insert(END, slp_dlist[i])
                
            if 'layer_input' in self.content and self.content['layer_input'].winfo_exists():
                self.content['layer_input'].delete(0, END)
                self.content['layer_input'].insert(END, str(data.get('layers', 0)))
            
            if 'start_sheet' in self.content and self.content['start_sheet'].winfo_exists():
                self.content['start_sheet'].delete(0, END)
                self.content['start_sheet'].insert(END, str(data.get('s_no', 1)))
            
            if data.get('_ptype') in [3,4,5] and 'scrap_entry' in self.content and self.content['scrap_entry'].winfo_exists():
                scrap_length = data.get('scrap_length', 0)
                self.content['scrap_entry'].delete(0, END)
                self.content['scrap_entry'].insert(END, str(scrap_length))

        except FileNotFoundError:
            messagebox.showinfo("Info", f"No saved parameters found for {selected_file}.", parent=self.toplevel)
            # Clear fields if no params found or if desired
            if 'li_entries' in self.content:
                for entry_widget in self.content['li_entries']: entry_widget.delete(0,END)
            if 'steplap_ds' in self.content:
                for entry_widget in self.content['steplap_ds']: entry_widget.delete(0,END)
            if 'layer_input' in self.content: self.content['layer_input'].delete(0,END)
            if 'start_sheet' in self.content: self.content['start_sheet'].delete(0,END)
            if 'scrap_entry' in self.content: self.content['scrap_entry'].delete(0,END)

        except (json.JSONDecodeError, KeyError) as err:
            messagebox.showerror("Error", f"Error reading parameter file {selected_file}: {err}", parent=self.toplevel)
        except Exception as err: # Catch-all for other unexpected errors
            messagebox.showerror("Error", f"An unexpected error occurred while loading lengths: {err}", parent=self.toplevel)

    def _clear_widget_list_from_content(self, content_key):
        if content_key in self.content:
            for widget in self.content[content_key]:
                if widget and widget.winfo_exists():
                    widget.destroy()
            del self.content[content_key]

    def _clear_single_widget_from_content(self, content_key):
        if content_key in self.content and self.content[content_key]:
            widget = self.content[content_key]
            if isinstance(widget, list): # Should not be a list for single widget
                for w_item in widget:
                    if w_item and w_item.winfo_exists(): w_item.destroy()
            elif widget and widget.winfo_exists():
                widget.destroy()
            del self.content[content_key]

    #initialize the input parameter fields
    def _get_params(self):
        # 1. Destroy and remove old frames that host dynamic widgets
        if 'li_frame' in self.content and self.content.get('li_frame'):
            if self.content['li_frame'].winfo_exists():
                self.content['li_frame'].destroy()
            del self.content['li_frame']
        
        # param_frame hosts steplap_ds, layers, etc. Clear its children.
        if 'param_frame' in self.content and self.content.get('param_frame'):
            if self.content['param_frame'].winfo_exists():
                for widget in self.content['param_frame'].winfo_children():
                    widget.destroy()
            # Keep self.content['param_frame'] if it exists, otherwise create below
        else:
            self.content['param_frame'] = ttk.Frame(self.toplevel)
            self.content['param_frame'].grid(row=1, column=2, sticky="ns", padx=5, pady=5)

        # 2. Clear specific widget references from self.content dictionary
        self._clear_widget_list_from_content('li_labels')
        self._clear_widget_list_from_content('li_entries')
        self._clear_widget_list_from_content('steplap_label')
        self._clear_widget_list_from_content('steplap_ds')
        for key in ['layer_label', 'layer_input', 'starts_label', 'start_sheet', 'scrap_label', 'scrap_entry']:
            self._clear_single_widget_from_content(key)

        selected_file = self.content['search_entry'].e.get()
        if not selected_file:
            messagebox.showwarning("Selection Error", "Please select a program file first.", parent=self.toplevel)
            return

        program_file_path = os.path.join(RunScreen.BASE_PROGRAM_INPUT_PATH, selected_file)
        try:
            with open(program_file_path, 'r') as fp:
                self.data = json.load(fp)
        except FileNotFoundError:
            messagebox.showerror("Error", f"Program file not found: {program_file_path}", parent=self.toplevel)
            self.data = None
            return
        except json.JSONDecodeError:
            messagebox.showerror("Error", f"Invalid JSON in program file: {program_file_path}", parent=self.toplevel)
            self.data = None
            return
        except Exception as e:
            messagebox.showerror("Error", f"Could not load program file: {e}", parent=self.toplevel)
            self.data = None
            return

        # 3. Recreate frames and widgets
        self.content['li_frame'] = ttk.Frame(self.toplevel)
        self.content['li_frame'].grid(row=1, column=1, sticky="ns", padx=5, pady=5)
        
        param_frame_ref = self.content['param_frame'] # Ensured to exist

        # Populate L_i entries in li_frame
        n_tools = len(self.data.keys())
        num_lengths = max(0, n_tools - 1)
        
        li_labels_list = []
        li_entries_list = []
        for i in range(num_lengths):
            lbl = Label(self.content['li_frame'], text=f'L{i+1}')
            ent = Entry(self.content['li_frame'])
            lbl.grid(row=i, column=0, sticky="w", padx=2, pady=2)
            ent.grid(row=i, column=1, sticky="ew", padx=2, pady=2)
            li_labels_list.append(lbl)
            li_entries_list.append(ent)
        self.content['li_labels'] = li_labels_list
        self.content['li_entries'] = li_entries_list
        
        # Determine ptype based on self.data
        self._ptype = 1 # Default
        for tool_idx_str, tool_data_dict in self.data.items():
            tool_name = tool_data_dict.get('name')
            steplap_type_val = tool_data_dict.get('steplap_type') # This is the mapped integer value
            is_skewed_flag = tool_data_dict.get('is_skewed', False) # Get from JSON

            if tool_name == 's':
                if steplap_type_val == 2: # 'Vertical (Lateral)' in Labels.steplap_type_map
                    if is_skewed_flag:
                        self._ptype = 5 # Asymmetric/Skewed fish
                    else:
                        self._ptype = 4 # Symmetric fish
                elif steplap_type_val == 3: # 'Skewed (Lateral)' in Labels.steplap_type_map
                    self._ptype = 5 # Asymmetric/Skewed fish (inherently skewed by type)
                else: # Other steplap types for 's' (e.g., Horizontal or No step-lap)
                    self._ptype = 3 # Default for 's', typically SpearH (Horizontal steplap)
                break 
            elif tool_name == 'ys':
                self._ptype = 2; break
        
        # Populate steplap_ds in param_frame_ref
        steplap_ds_list = []
        steplap_label_list = []
        current_param_row = 0
        for tool_idx_str, tool_data_dict in self.data.items():
            if tool_data_dict.get('steplap_count', 0) > 1:
                lbl = Label(param_frame_ref, text=f'Step-lap for {tool_data_dict.get("name", "Tool")}({int(tool_idx_str)+1})')
                ent = Entry(param_frame_ref)
                ent.insert(END, "0") # Default to string "0"
                lbl.grid(row=current_param_row, column=0, sticky="w", padx=2, pady=2)
                ent.grid(row=current_param_row, column=1, sticky="ew", padx=2, pady=2)
                steplap_label_list.append(lbl)
                steplap_ds_list.append(ent)
                current_param_row += 1
        self.content['steplap_label'] = steplap_label_list
        self.content['steplap_ds'] = steplap_ds_list
            
        # Populate layers, start_sheet, scrap_entry in param_frame_ref
        self.content['layer_label'] = Label(param_frame_ref, text='Layers')
        self.content['layer_label'].grid(row=current_param_row, column=0, sticky="w", padx=2, pady=2)
        self.content['layer_input'] = Entry(param_frame_ref)
        self.content['layer_input'].insert(END, "1") # Default to 1 layer
        self.content['layer_input'].grid(row=current_param_row, column=1, sticky="ew", padx=2, pady=2)
        current_param_row += 1
        
        self.content['starts_label'] = Label(param_frame_ref, text='Start Sheet')
        self.content['starts_label'].grid(row=current_param_row, column=0, sticky="w", padx=2, pady=2)
        self.content['start_sheet'] = Entry(param_frame_ref)
        self.content['start_sheet'].insert(END, "1") # Default to start sheet 1
        self.content['start_sheet'].grid(row=current_param_row, column=1, sticky="ew", padx=2, pady=2)
        current_param_row += 1
        
        if self._ptype in [3, 4, 5]: # Central limb types might need scrap length
            self.content['scrap_label'] = Label(param_frame_ref, text='Scrap Length')
            self.content['scrap_label'].grid(row=current_param_row, column=0, sticky="w", padx=2, pady=2)
            self.content['scrap_entry'] = Entry(param_frame_ref)
            self.content['scrap_entry'].insert(END, "0") # Default to 0 scrap
            self.content['scrap_entry'].grid(row=current_param_row, column=1, sticky="ew", padx=2, pady=2)
            
        self._get_lengths() # Load saved values into these newly created entries

    def _display_program(self):
        name = self.content['search_entry'].e.get()
        if not name:
            messagebox.showwarning("Selection Error", "No program file selected to display.", parent=self.toplevel)
            return
        
        program_file_path = os.path.join(RunScreen.BASE_PROGRAM_INPUT_PATH, name)
        try:
            with open(program_file_path, 'r') as fp:
                data_to_display = json.load(fp)

            if not self.canvas: # First time displaying
                # Adjusted figsize for better fit in initial window
                # Increase the height (second value) for less vertical squishing
                self.figure = Figure(figsize=(6.5, 3.5), dpi=100) 
                self.plot_ax = self.figure.add_subplot(111)
                self.canvas = FigureCanvasTkAgg(self.figure, master=self.content['display_frame'])
                self.canvas_widget = self.canvas.get_tk_widget() # Store the widget
                self.canvas_widget.pack(side='top', fill='both', expand=True)
            else: # Subsequent displays
                self.plot_ax.clear()

            # Use DisplayWindow to plot on the existing axes
            DisplayWindow(data=data_to_display, ax=self.plot_ax)
            self.figure.tight_layout() # Adjust plot layout to fit figure

            self.canvas.draw()

        except FileNotFoundError:
            messagebox.showerror("File Error", f"Program file not found: {program_file_path}", parent=self.toplevel)
        except json.JSONDecodeError:
            messagebox.showerror("File Error", f"Error decoding JSON from {name}.", parent=self.toplevel)
        except Exception as err:
            messagebox.showerror("Display Error", f"An unexpected error occurred during display: {err}", parent=self.toplevel)

    def _on_close(self):
        """Handles the closing of the RunScreen Toplevel window."""
        try:
            # Destroy the canvas widget first.
            if hasattr(self, 'canvas_widget') and self.canvas_widget and self.canvas_widget.winfo_exists():
                self.canvas_widget.destroy()
            self.canvas_widget = None

            # Explicitly close the Matplotlib figure.
            if hasattr(self, 'figure') and self.figure:
                plt.close(self.figure)
            self.figure = None
            
            self.plot_ax = None
            self.canvas = None

        except Exception as e:
            print(f"Error during Matplotlib cleanup in RunScreen: {e}")
        finally:
            if hasattr(self, 'toplevel') and self.toplevel and self.toplevel.winfo_exists():
                self.toplevel.destroy()
            self.toplevel = None