#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 18:45:53 2022

@author: omkar
"""

from tkinter import Tk, Button, Label, Entry, Toplevel, messagebox, StringVar, BooleanVar
from tkinter import ttk
import json
import os # Added for os.path.join
from label_file import Labels
from display_screen import DisplayWindow
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class CreateCutProgramScreen:

    def __init__(self, parent_tk):
        self.parent_tk = parent_tk
        self.toplevel = Toplevel(parent_tk)
        self._content = {}
        # self._tools = Labels.tool_name_tuple # Not directly used now
        # Original data columns + Skewed, PNR is now a label
        self._data_field_labels = Labels.create_frame_cols 
        # Headers for the grid table display
        self._grid_column_headers = ['#'] + self._data_field_labels[1:-1] + [Labels.label_skewed] + ['Actions', ''] 

        self._index_map = {0:'name', 1:'steplap_type', 2:'steplap_count',
                           3:'open_code', 4:'is_skewed', 5:'_steplap_distance'} # Adjusted for is_skewed


        self.plot_flag = False
        self.__initScreen(self.toplevel)
        self.toplevel.protocol("WM_DELETE_WINDOW", self.toplevel.destroy)

    def __initScreen(self, parent):
        parent.title('Create program screen.')

        content = {}

        frame = ttk.Frame(self.toplevel) # Parent to self.toplevel
        frame.pack()
        content['frame_table'] = frame

        content['func_frame'] = ttk.Frame(self.toplevel) # Parent to self.toplevel

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

        content['save_frame'] = ttk.Frame(self.toplevel) # Parent to self.toplevel

        content['button_save'] = Button(content['save_frame'], text='Save',
                                        command=self._save)
        content['button_save'].grid(row=0, column=0)
        content['file_name'] = Entry(content['save_frame'])
        content['file_name'].grid(row=0, column=1)

        content['entries'] = []
        content['column_labels'] = []
        content['skewed_vars'] = [] # To store BooleanVars for skewed checkboxes
        # content['combo_values'] = [] # Seems unused

        for i, header_text in enumerate(self._grid_column_headers):
            label = Label(content['frame_table'],text = header_text)
            label.grid(row= 0, column = i)
            content['column_labels'].append(label)

        content['display_frame'] = ttk.Frame(self.toplevel) # Parent to self.toplevel

        self.content = content # Set self.content before calling methods that use it
        self._insert_new_blank_row(0) # Add initial row
        # self._redraw_all_rows() # _insert_new_blank_row calls redraw

        content['func_frame'].pack()
        content['save_frame'].pack()
        content['display_frame'].pack()

        self.content = content

        # parent.mainloop() # Main loop is handled by the root Tk instance

    def _build_row_widget_list(self, list_index_for_command_context):
        """Creates and returns a list of widgets for a single logical row."""
        row_widgets = []
        target_frame = self.content['frame_table']

        # Column 0: PNR Label
        pnr_label = Label(target_frame, text=str(list_index_for_command_context + 1))
        row_widgets.append(pnr_label)

        # Data Entry Widgets (Tool Name, Step-lap type, Step-lap count, Open-Close config)
        # Column 1: Tool Name (corresponds to self._data_field_labels[1])
        tn_values = StringVar()
        tn_combo = ttk.Combobox(target_frame, textvariable=tn_values, values=Labels.tool_name_tuple, state='readonly')
        tn_combo.bind("<<ComboboxSelected>>", lambda event, r_idx=list_index_for_command_context: self._update_skewed_checkbox_state(r_idx))
        row_widgets.append(tn_combo)

        # Column 2: Step-lap type (corresponds to self._data_field_labels[2])
        slt_values = StringVar()
        slt_combo = ttk.Combobox(target_frame, textvariable=slt_values, values=tuple(Labels.steplap_type_map.keys()), state='readonly')
        slt_combo.current(0)
        slt_combo.bind("<<ComboboxSelected>>", lambda event, r_idx=list_index_for_command_context: self._update_skewed_checkbox_state(r_idx))
        row_widgets.append(slt_combo)

        # Column 3: Step-lap count (corresponds to self._data_field_labels[3])
        slc_entry = Entry(target_frame)
        row_widgets.append(slc_entry)

        # Column 4: Open-Close config (corresponds to self._data_field_labels[4])
        occ_values = StringVar()
        occ_combo = ttk.Combobox(target_frame, textvariable=occ_values, values=tuple(Labels.open_code_map.keys()), state='readonly')
        occ_combo.current(0)
        row_widgets.append(occ_combo)

        # Column 5: Skewed Checkbox
        skewed_var = BooleanVar()
        skewed_checkbox = ttk.Checkbutton(target_frame, variable=skewed_var, state='disabled')
        skewed_checkbox.associated_var = skewed_var # Attach the BooleanVar
        row_widgets.append(skewed_checkbox)

        # Action Buttons
        # Column 6: Delete Button
        del_button = Button(target_frame, text="Del", command=lambda idx=list_index_for_command_context: self._delete_row_at_index(idx))
        row_widgets.append(del_button)

        # Column 7: Insert Above Button
        ins_button = Button(target_frame, text="Ins", command=lambda idx=list_index_for_command_context: self._insert_new_blank_row(idx))
        row_widgets.append(ins_button)
        
        return row_widgets

    def _update_skewed_checkbox_state(self, row_index):
        """Updates the state of the skewed checkbox based on tool and step-lap type."""
        if not (0 <= row_index < len(self.content['entries'])):
            return

        widget_row = self.content['entries'][row_index]
        tool_name_widget = widget_row[1]    # Tool Name Combobox
        steplap_type_widget = widget_row[2] # Step-lap Type Combobox
        skewed_checkbox_widget = widget_row[5] # Skewed Checkbutton

        tool_name = tool_name_widget.get()
        steplap_type_key = steplap_type_widget.get() # e.g., "Vertical (Lateral)"

        if tool_name == 's' and steplap_type_key == 'Vertical (Lateral)':
            skewed_checkbox_widget.config(state='normal')
        else:
            skewed_checkbox_widget.config(state='disabled')
            # Set the associated BooleanVar to False
            if hasattr(skewed_checkbox_widget, 'associated_var'):
                 skewed_checkbox_widget.associated_var.set(False)

    def _extract_and_validate_data(self):
        """Extracts data from UI entries, validates, and returns a data dictionary or None."""
        rows = self.content['entries']
        tools_data_list = []
        for row_index, row_entries in enumerate(rows):
            tool_values = []
            # PNR Label is row_entries[0]
            # Data widgets start from row_entries[1]
            
            # Tool Name (widget at index 1)
            tool_name_widget = row_entries[1]
            if not tool_name_widget.get():
                messagebox.showwarning("Input Error", f"Tool name in row {row_index + 1} is empty. Please fill or remove empty rows.", parent=self.toplevel)
                return None
            
            # Extract PNR text (from Label at index 0)
            tool_values.append(row_entries[0].cget("text")) 
            # Extract data from actual input widgets (indices 1 to 4)
            tool_values.append(row_entries[1].get())  # Tool name
            tool_values.append(row_entries[2].get())  # Step-lap type
            tool_values.append(row_entries[3].get())  # Step-lap count
            tool_values.append(row_entries[4].get())  # Open-Close config
            
            # Skewed Checkbox (widget at index 5)
            skewed_checkbox_widget = row_entries[5]
            is_skewed = skewed_checkbox_widget.instate(['selected']) if skewed_checkbox_widget.instate(['!disabled']) else False
            tool_values.append(is_skewed)

            tools_data_list.append(tool_values)

        processed_data = {}
        for i, tool_row in enumerate(tools_data_list):
            datum = {}
            try:
                # tool_row[0] is PNR text, tool_row[1] is Tool Name value, etc.
                datum[self._index_map[0]] = tool_row[1]  # Tool name value
                datum[self._index_map[1]] = Labels.steplap_type_map[tool_row[2]] # steplap_type value
                if not tool_row[3]: # steplap_count value
                    datum[self._index_map[2]] = 1
                else:
                    datum[self._index_map[2]] = int(tool_row[3]) # steplap_count value
                datum[self._index_map[3]] = Labels.open_code_map[tool_row[4]] # open_code value
                datum[self._index_map[4]] = tool_row[5] # is_skewed value
                datum[self._index_map[5]] = 0 # _steplap_distance (defaulted)
            except ValueError:
                messagebox.showwarning("Input Error", f"Invalid 'Step-lap count' in row {i + 1}. It must be a number.", parent=self.toplevel)
                return None
            except KeyError as e:
                messagebox.showwarning("Input Error", f"Invalid selection for 'Step-lap type' or 'Open-Close config' in row {i + 1}: {e}", parent=self.toplevel)
                return None
            processed_data[i] = datum
        return processed_data

    def _save(self):
        file_name = self.content['file_name'].get()
        if not file_name:
            messagebox.showwarning("showwarning", "File name is required.", parent=self.toplevel)
            return

        data = self._extract_and_validate_data()
        if data is None:
            return

        self._clump_data(data)

        # Ensure the directory exists, though typically it should
        output_dir = os.path.join('..', 'cut_program_input')
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, file_name + '.json')

        try:
            with open(path, 'w') as fp:
                fp.write(json.dumps(data, indent=4))
            messagebox.showinfo("showinfo", f"{file_name}.json saved succesfully.", parent=self.toplevel)
        except (IOError, OSError) as e:
            messagebox.showerror("Save Error", f"Could not save file: {e}", parent=self.toplevel)

    def _clump_data(self, data):

        #cycle through the data and find the corrresponding partial sequences
        #for i in data:
        #    #partial cut name start with pr or pf, use them as identifiers
        #    if data[i].name == 'pr' or data[i].name == 'pf':
        # pass
        pass

    def _redraw_all_rows(self):
        """Clears and redraws all entry rows in the table."""

        # 1. Extract data from existing widgets before destroying them
        old_data_values = []
        # Check if self.content['entries'] contains widget lists or was pre-filled with data dicts
        if self.content['entries'] and isinstance(self.content['entries'][0], list) and len(self.content['entries'][0]) > 1 and hasattr(self.content['entries'][0][1], 'get'):
            for widget_row in self.content['entries']:
                row_values = {
                    'tool_name': widget_row[1].get(),
                    'steplap_type': widget_row[2].get(),
                    'steplap_count': widget_row[3].get(),
                    'open_close_config': widget_row[4].get(),
                    'is_skewed': widget_row[5].instate(['selected']) # Skewed checkbox at index 5
                }
                old_data_values.append(row_values)
        elif self.content['entries'] and isinstance(self.content['entries'][0], dict): # Data was pre-filled
            old_data_values = list(self.content['entries']) # Make a copy
        else: # Initial call or empty
            old_data_values = []

        # Clear existing entry rows (widgets with grid_info()['row'] > 0)
        for widget in self.content['frame_table'].winfo_children():
            grid_info = widget.grid_info()
            if grid_info and grid_info['row'] > 0: # 0 is for column headers
                widget.destroy()
        
        # 2. Rebuild rows and repopulate with extracted data
        self.content['entries'] = [] # Clear the old widget references

        for list_idx, preserved_values in enumerate(old_data_values):
            new_widget_row = self._build_row_widget_list(list_idx)
            
            # Repopulate with preserved data
            new_widget_row[1].set(preserved_values['tool_name'])
            new_widget_row[2].set(preserved_values['steplap_type'])
            new_widget_row[3].insert(0, preserved_values['steplap_count'])
            new_widget_row[4].set(preserved_values['open_close_config'])
            # Skewed checkbox (widget at index 5 - new_widget_row[5])
            # Set its state using the associated BooleanVar
            if hasattr(new_widget_row[5], 'associated_var'):
                if preserved_values.get('is_skewed', False):
                    new_widget_row[5].associated_var.set(True)
                else:
                    new_widget_row[5].associated_var.set(False)

            self.content['entries'].append(new_widget_row)
            for col_idx, widget_to_grid in enumerate(new_widget_row):
                widget_to_grid.grid(row=list_idx + 1, column=col_idx, sticky="ew" if isinstance(widget_to_grid, (Entry, ttk.Combobox)) else "")
            self._update_skewed_checkbox_state(list_idx) # Update state after gridding

    def _insert_new_blank_row(self, at_list_index):
        """Inserts a new blank row's widget list into self.content['entries'] and redraws."""
        # 1. Get current data values from widgets
        current_widget_data = []
        for widget_row in self.content['entries']:
            current_widget_data.append({
                'tool_name': widget_row[1].get(), 'steplap_type': widget_row[2].get(),
                'steplap_count': widget_row[3].get(), 'open_close_config': widget_row[4].get(),
                'is_skewed': widget_row[5].instate(['selected'])
            })
        # 2. Insert a blank data dictionary for the new row
        blank_row_data = {'tool_name': '', 
                          'steplap_type': tuple(Labels.steplap_type_map.keys())[0], 
                          'steplap_count': '', 
                          'open_close_config': tuple(Labels.open_code_map.keys())[0],
                          'is_skewed': False}
        current_widget_data.insert(at_list_index, blank_row_data)
        # 3. Set self.content['entries'] to this list of data dictionaries. _redraw_all_rows will use it.
        self.content['entries'] = current_widget_data
        self._redraw_all_rows()

    def _delete_row_at_index(self, list_index):
        """Removes a row's widget list from self.content['entries'] and redraws."""
        if 0 <= list_index < len(self.content['entries']):
            self.content['entries'].pop(list_index)
            self._redraw_all_rows()

    def _addRow(self):
        """Command for the bottom 'Add row' button."""
        self._insert_new_blank_row(len(self.content['entries']))

    def _delete_last(self):
        """Command for the bottom 'Delete last' button."""
        if self.content['entries']: # Check if there are any rows
            self._delete_row_at_index(len(self.content['entries']) - 1)
        else:
            messagebox.showinfo("Info", "No rows to delete.", parent=self.toplevel)

    def _display(self):
        data = self._extract_and_validate_data()
        if data is None or not data:
            messagebox.showinfo("Display Info", "No valid data to display.", parent=self.toplevel)
            if self.plot_flag: # Clear previous plot if data is invalid/empty
                self.display_plot.clear()
                self.canvas.draw()
            return

        width = len(data.keys())

        if not self.plot_flag:
            self.display_fig = Figure(figsize = (max(width, 1) + 3, 5), # Ensure min width
                                      dpi = 100)
            self.display_plot = self.display_fig.add_subplot(111)

            self.canvas = FigureCanvasTkAgg(self.display_fig,
                                       master = self.content['display_frame'])
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(side='top', fill='both', expand=True)
            self.plot_flag = True
        else:
            self.display_plot.clear()

        # Use DisplayWindow to plot on the existing axes
        DisplayWindow(data=data, ax=self.display_plot) # This will use the ax and not call plt.show()

        self.display_fig.set_size_inches(max(width,1) + 3, 5) # Adjust size after plotting
        self.canvas.draw()
