#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on [Current Date]

@author: [Your Name/Omkar]
"""

from tkinter import Tk, Button, Entry, Listbox, END, Label, Toplevel, messagebox, Frame
from tkinter import ttk
from os import listdir
import os
from matplotlib.figure import Figure # Keep Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # Keep FigureCanvasTkAgg
import matplotlib.pyplot as plt # Import pyplot for plt.close()
from visualize import visualize_cnc_operations # Import the Matplotlib visualization function


class AutoCompleteExcelEntry:
    def __init__(self, db_files, parent_frame, master_screen):
        self.master_screen = master_screen
        self.entry_widget = Entry(parent_frame)
        self.entry_widget.pack(fill='x', padx=5, pady=2)
        self.entry_widget.bind('<KeyRelease>', self._on_keyrelease)

        self.db_files = db_files
        self.listbox_widget = Listbox(parent_frame)
        self.listbox_widget.pack(fill='both', expand=True, padx=5, pady=2)
        for item in db_files:
            self.listbox_widget.insert('end', item)
        self.listbox_widget.bind('<<ListboxSelect>>', self._on_select)

    def _on_select(self, event):
        selection = event.widget.curselection()
        if selection:
            selected_file = event.widget.get(selection[0])
            self.entry_widget.delete(0, 'end')
            self.entry_widget.insert('end', selected_file)
            self.master_screen.display_visualization(selected_file)

    def _on_keyrelease(self, event):
        value = event.widget.get()
        if value == '':
            data = self.db_files
        else:
            data = []
            for item in self.db_files:
                if item.lower().startswith(value.lower()):
                    data.append(item)
        
        self.listbox_widget.delete(0, 'end')
        for item in data:
            self.listbox_widget.insert('end', item)

class VerifyOutputScreen:
    OUTPUT_DIR = os.path.join('..', 'cut_program_output')

    def __init__(self, parent_tk):
        self.parent_tk = parent_tk
        self.toplevel = Toplevel(parent_tk)
        self.toplevel.title("Verify CNC Output")
        self.toplevel.geometry("1000x700") # Adjusted size
        self.toplevel.protocol("WM_DELETE_WINDOW", self._on_close) # Custom close handler

        # --- Main PanedWindow for resizable sections ---
        paned_window = ttk.PanedWindow(self.toplevel, orient='horizontal')
        paned_window.pack(fill='both', expand=True, padx=10, pady=10)

        # --- Left Frame for File Selection ---
        left_frame = ttk.Frame(paned_window, width=250)
        paned_window.add(left_frame, weight=1)

        Label(left_frame, text="Select Excel File:").pack(pady=5)
        excel_files = self._get_excel_files()
        self.autocomplete_entry = AutoCompleteExcelEntry(excel_files, left_frame, self)

        # --- Right Frame for Matplotlib Canvas ---
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=4)
        self.right_frame = right_frame

        # Configure grid for right_frame to manage canvas and scrollbars
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # --- Matplotlib Canvas Setup ---
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.plot_ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.right_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky='nsew')

        # --- Scrollbars ---
        self.h_scrollbar = ttk.Scrollbar(self.right_frame, orient='horizontal', command=self._on_horizontal_scroll)
        self.h_scrollbar.grid(row=1, column=0, sticky='ew')
        self.v_scrollbar = ttk.Scrollbar(self.right_frame, orient='vertical', command=self._on_vertical_scroll)
        self.v_scrollbar.grid(row=0, column=1, sticky='ns')

        # Store full data extents
        self.full_xlim_data = (0, 1) # Default/initial
        self.full_ylim_data = (0, 1) # Default/initial

        self.canvas.draw()
        self._update_scrollbars() # Initialize scrollbars

    def _get_excel_files(self):
        try:
            if not os.path.exists(self.OUTPUT_DIR):
                os.makedirs(self.OUTPUT_DIR, exist_ok=True) # Create if not exists
                messagebox.showinfo("Info", f"Output directory created: {self.OUTPUT_DIR}", parent=self.toplevel)
                return []
            return [f for f in listdir(self.OUTPUT_DIR) if f.endswith('.xlsx')]
        except Exception as e:
            messagebox.showerror("Error", f"Could not list files from {self.OUTPUT_DIR}: {e}", parent=self.toplevel)
            return []

    def display_visualization(self, filename):
        if not filename:
            self.plot_ax.clear()
            self.full_xlim_data = self.plot_ax.get_xlim() # Get default xlim after clear
            self.full_ylim_data = self.plot_ax.get_ylim() # Get default ylim after clear
            self._update_scrollbars()
            self.canvas.draw()
            return

        filepath = os.path.join(self.OUTPUT_DIR, filename)
        visualize_cnc_operations(filepath, ax=self.plot_ax)

        if hasattr(self.plot_ax, 'total_data_extent_x_calculated') and \
           hasattr(self.plot_ax, 'total_data_extent_y_calculated'):
            self.full_xlim_data = self.plot_ax.total_data_extent_x_calculated
            self.full_ylim_data = self.plot_ax.total_data_extent_y_calculated
        else: # Fallback if attributes not set
            # Use current plot limits as full extent if attributes are missing
            self.full_xlim_data = self.plot_ax.get_xlim()
            self.full_ylim_data = self.plot_ax.get_ylim()
            print("Warning: Could not retrieve total_data_extent from plot_ax. Scroll range might be incorrect.")

        self._update_scrollbars()
        self.canvas.draw()

    def _update_scrollbars(self):
        current_xlim = self.plot_ax.get_xlim()
        current_ylim = self.plot_ax.get_ylim()

        data_min_x, data_max_x = self.full_xlim_data
        data_min_y, data_max_y = self.full_ylim_data

        data_width = data_max_x - data_min_x
        data_height = data_max_y - data_min_y

        view_width = current_xlim[1] - current_xlim[0]
        view_height = current_ylim[1] - current_ylim[0]

        # Horizontal scrollbar
        if data_width <= 0 or view_width >= data_width: # view is wider or equal to data
            self.h_scrollbar.grid_remove() # Hide if not needed
            print(f"H-Scrollbar: REMOVED. Ismapped: {self.h_scrollbar.winfo_ismapped()}")
        else:
            self.h_scrollbar.grid() # Show if needed
            first_x = (current_xlim[0] - data_min_x) / data_width
            last_x = (current_xlim[1] - data_min_x) / data_width
            self.h_scrollbar.set(max(0.0, first_x), min(1.0, last_x))
            # Force an update to ensure geometry is processed before checking ismapped
            self.h_scrollbar.update_idletasks() 
            print(f"H-Scrollbar: SHOWING, set to: ({max(0.0, first_x)}, {min(1.0, last_x)}). Ismapped: {self.h_scrollbar.winfo_ismapped()}")

        # Vertical scrollbar
        if data_height <= 0 or view_height >= data_height: # view is taller or equal to data
            self.v_scrollbar.grid_remove() # Hide if not needed
            print(f"V-Scrollbar: REMOVED. Ismapped: {self.v_scrollbar.winfo_ismapped()}")
        else:
            self.v_scrollbar.grid() # Show if needed
            # Note: Matplotlib's y-axis can be inverted, but scrollbars typically expect 0 at top.
            # Assuming standard y-axis for scrollbar logic (0 at bottom for data).
            # The fractions are relative to the data range.
            first_y = (current_ylim[0] - data_min_y) / data_height
            last_y = (current_ylim[1] - data_min_y) / data_height
            self.v_scrollbar.set(max(0.0, first_y), min(1.0, last_y))
            self.v_scrollbar.update_idletasks()
            print(f"V-Scrollbar: SHOWING, set to: ({max(0.0, first_y)}, {min(1.0, last_y)}). Ismapped: {self.v_scrollbar.winfo_ismapped()}")
        print(f"--- end _update_scrollbars ---")

    def _on_horizontal_scroll(self, action, value_str, units=None):
        current_xlim = list(self.plot_ax.get_xlim())
        view_width = current_xlim[1] - current_xlim[0]
        data_min_x, data_max_x = self.full_xlim_data
        data_width = data_max_x - data_min_x

        if data_width <= 0 or view_width >= data_width: return # No scrolling needed

        new_x_start = current_xlim[0]
        if action == 'moveto':
            new_x_start = data_min_x + float(value_str) * (data_width - view_width)
        elif action == 'scroll':
            value = int(value_str)
            if units == 'units':
                delta = value * (view_width / 10) # Scroll by 1/10th of view width
            elif units == 'pages':
                delta = value * view_width * 0.9 # Scroll by 90% of view width
            else:
                return
            new_x_start += delta
        else:
            return

        # Clamp new_x_start
        new_x_start = max(data_min_x, min(new_x_start, data_max_x - view_width))
        self.plot_ax.set_xlim(new_x_start, new_x_start + view_width)
        self.canvas.draw()
        self._update_scrollbars()

    def _on_vertical_scroll(self, action, value_str, units=None):
        current_ylim = list(self.plot_ax.get_ylim())
        view_height = current_ylim[1] - current_ylim[0]
        data_min_y, data_max_y = self.full_ylim_data
        data_height = data_max_y - data_min_y

        if data_height <= 0 or view_height >= data_height: return # No scrolling needed

        new_y_start = current_ylim[0]
        if action == 'moveto':
            new_y_start = data_min_y + float(value_str) * (data_height - view_height)
        elif action == 'scroll':
            value = int(value_str)
            if units == 'units':
                delta = value * (view_height / 10)
            elif units == 'pages':
                delta = value * view_height * 0.9
            else:
                return
            new_y_start += delta
        else:
            return

        new_y_start = max(data_min_y, min(new_y_start, data_max_y - view_height))
        self.plot_ax.set_ylim(new_y_start, new_y_start + view_height)
        self.canvas.draw()
        self._update_scrollbars()

    def _on_close(self):
        """Handles the closing of the VerifyOutputScreen Toplevel window."""
        try:
            # Destroy the canvas widget first.
            if hasattr(self, 'canvas_widget') and self.canvas_widget and self.canvas_widget.winfo_exists():
                self.canvas_widget.destroy()
            self.canvas_widget = None # Clear reference

            # Explicitly close the Matplotlib figure.
            if hasattr(self, 'figure') and self.figure:
                plt.close(self.figure)
            self.figure = None # Clear reference
            
            # Clear other Matplotlib related references
            self.plot_ax = None
            # self.canvas is the FigureCanvasTkAgg instance. Destroying its widget handles its Tk parts.
            self.canvas = None

        except Exception as e:
            print(f"Error during Matplotlib cleanup in VerifyOutputScreen: {e}")
        finally:
            # Ensure the Toplevel window is destroyed.
            if hasattr(self, 'toplevel') and self.toplevel and self.toplevel.winfo_exists():
                self.toplevel.destroy()
            self.toplevel = None # Clear reference