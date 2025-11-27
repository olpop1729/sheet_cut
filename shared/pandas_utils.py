#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pandas utilities for reading and writing Excel files in the sheet_cut application.
"""

import itertools
import os
import pandas as pd


class PandasModule:
    """
    Basic Pandas utility class for file operations.
    """
    
    def __init__(self):
        self.file_name = ''
    
    def checkFileName(self, name, output_dir='../cut_program_output/'):
        """
        Check if a file name already exists in the output directory.
        
        Args:
            name: The file name to check
            output_dir: The directory to check in
            
        Returns:
            True if the name is available (not in use), False otherwise
        """
        if not os.path.exists(output_dir):
            return True
        onlyfiles = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
        return name not in onlyfiles


class PandasWriterReader:
    """
    Utility class for writing cut program data to Excel files.
    """
    
    # Default Excel column names
    EXCEL_COLUMN_NAMES = [
        'Feed Dist', 'Vnotch Trav Dist', 'After Shear feed Tip Cut',
        'Tool', 'Tool no', 'Start Index', 'End Index',
        'Job Shape', 'No of Steps', 'Sheet Count', 'P45 OverCut',
        'M45 OverCut', 'Yoke Len', 'Leg Len', 'Cnetral Limb Len'
    ]
    
    @staticmethod
    def writeExcel(fname='Trial', output_dir='../cut_program_output/', **kwargs):
        """
        Write cut program data to an Excel file.
        
        Args:
            fname: Output file name (without extension)
            output_dir: Output directory path
            **kwargs: Data columns to write. Expected keys:
                - feed: Feed distances
                - v_axis: V-notch axis values
                - sec_feed: Secondary feed values
                - operation: Operation names
                - tool_number: Tool numbers
                - start_index: Start indices
                - end_index: End indices
                - job_shape: Job shape values
                - number_of_steps: Number of steps
                - sheet_count: Sheet counts
                - p45_overcut: +45 overcut values
                - m45_overcut: -45 overcut values
                - yoke_len: Yoke lengths
                - leg_len: Leg lengths
                - cl_len: Central limb lengths
        
        Returns:
            The path to the written file
        """
        # Validate that we have enough columns
        expected_keys = [
            'feed', 'v_axis', 'sec_feed', 'operation', 'tool_number',
            'start_index', 'end_index', 'job_shape', 'number_of_steps',
            'sheet_count', 'p45_overcut', 'm45_overcut', 'yoke_len',
            'leg_len', 'cl_len'
        ]
        
        if len(kwargs.keys()) < len(PandasWriterReader.EXCEL_COLUMN_NAMES):
            print(f'Warning: Expected {len(PandasWriterReader.EXCEL_COLUMN_NAMES)} columns, got {len(kwargs.keys())}')
        
        # Create data using itertools.zip_longest to handle varying lengths
        cut_feed = list(itertools.zip_longest(
            kwargs.get('feed', []),
            kwargs.get('v_axis', []),
            kwargs.get('sec_feed', []),
            kwargs.get('operation', []),
            kwargs.get('tool_number', []),
            kwargs.get('start_index', []),
            kwargs.get('end_index', []),
            kwargs.get('job_shape', []),
            kwargs.get('number_of_steps', []),
            kwargs.get('sheet_count', []),
            kwargs.get('p45_overcut', []),
            kwargs.get('m45_overcut', []),
            kwargs.get('yoke_len', []),
            kwargs.get('leg_len', []),
            kwargs.get('cl_len', [])
        ))
        
        df = pd.DataFrame(data=cut_feed, columns=PandasWriterReader.EXCEL_COLUMN_NAMES)
        df.index += 1  # Make index 1-based for Excel
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, fname + '.xlsx')
        with pd.ExcelWriter(output_path) as writer:
            df.to_excel(writer)
        
        return output_path
    
    @staticmethod
    def writeExcelSimple(fname, feed, vaxis, operation, output_dir='../cut_program_output/'):
        """
        Write a simple cut program with just feed, v-axis, and operation data.
        
        Args:
            fname: Output file name (without extension)
            feed: List of feed values
            vaxis: List of v-axis values
            operation: List of operation names
            output_dir: Output directory path
            
        Returns:
            The path to the written file
        """
        cut_feed = list(zip(feed, vaxis, operation))
        df = pd.DataFrame(data=cut_feed, columns=['Feed', 'V-Axis', 'Operation'])
        df.index += 1
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, fname + '.xlsx')
        with pd.ExcelWriter(output_path) as writer:
            df.to_excel(writer)
        
        return output_path
