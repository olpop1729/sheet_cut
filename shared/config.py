#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration module for sheet_cut application.
Contains machine offset constants and configuration settings.
"""

import json
import os


class Offset:
    """
    Tool offset constants. These values represent machine-specific calibration offsets.
    """
    # Default offset values (can be overridden by config file)
    FP45 = -1.665
    FM45 = 0.865
    F0 = 0.0
    V_LAT = 0.0
    
    # Distance constants
    DISTANCE_HOLE_VNOTCH = 1250.0
    DISTANCE_SHEAR_VNOTCH = 4335.0


class Config:
    """
    Main configuration class that can load settings from a JSON config file
    or use default values.
    """
    # Directory paths
    CUT_PROGRAM_OUTPUT_DIRECTORY = '../cut_program_output'
    CONFIG_DIRECTORY = '../gui/config.json'
    
    # Coil settings
    COIL_START_POSITION = 0.0  # w.r.t. V_Notch
    COIL_LENGTH = 400000.0
    
    # Output settings
    OUTPUT_FILE_NAME = 'CutFeed_'
    
    # User input validation lists
    LIST_NO = ['no', 'n', 'not', '0', 'negative', 'incorrect']
    LIST_YES = ['yes', 'y', 'affirmative', 'correct', '1']
    
    # Excel output column names
    EXCEL_COLUMN_NAMES = [
        'Feed Dist', 'Vnotch Trav Dist', 'After Shear feed Tip Cut',
        'Tool', 'Tool no', 'Start Index', 'End Index',
        'Job Shape', 'No of Steps', 'Sheet Count', 'P45 OverCut',
        'M45 OverCut', 'Yoke Len', 'Leg Len', 'Central Limb Len'
    ]
    
    def __init__(self, config_path=None):
        """
        Initialize configuration, optionally loading from a JSON file.
        
        Args:
            config_path: Path to the JSON configuration file. If None, 
                        uses default CONFIG_DIRECTORY path.
        """
        self.data = {}
        
        # Initialize with default values from Offset class
        self.OFFSET_V_LAT = Offset.V_LAT
        self.OFFSET_F0 = Offset.F0
        self.OFFSET_FP45 = Offset.FP45
        self.OFFSET_FM45 = Offset.FM45
        self.DISTANCE_HOLE_VNOTCH = Offset.DISTANCE_HOLE_VNOTCH
        self.DISTANCE_SHEAR_VNOTCH = Offset.DISTANCE_SHEAR_VNOTCH
        self.COIL_LENGTH = Config.COIL_LENGTH
        
        # Try to load from config file
        path = config_path or Config.CONFIG_DIRECTORY
        if os.path.exists(path):
            try:
                with open(path, 'r') as fp:
                    self.data = json.load(fp)
                self._load_from_data()
            except (FileNotFoundError, json.JSONDecodeError) as err:
                print(f"Warning: Could not load config from {path}: {err}")
        
        # Build tool maps based on current configuration
        self._build_tool_maps()
    
    def _load_from_data(self):
        """Load configuration values from parsed JSON data."""
        if 'OFFSET_V_LAT' in self.data:
            self.OFFSET_V_LAT = self.data['OFFSET_V_LAT']
        if 'OFFSET_F0' in self.data:
            self.OFFSET_F0 = self.data['OFFSET_F0']
        if 'OFFSET_FP45' in self.data:
            self.OFFSET_FP45 = self.data['OFFSET_FP45']
        if 'OFFSET_FM45' in self.data:
            self.OFFSET_FM45 = self.data['OFFSET_FM45']
        if 'DISTANCE_HOLE_VNOTCH' in self.data:
            self.DISTANCE_HOLE_VNOTCH = self.data['DISTANCE_HOLE_VNOTCH']
        if 'DISTANCE_SHEAR_VNOTCH' in self.data:
            self.DISTANCE_SHEAR_VNOTCH = self.data['DISTANCE_SHEAR_VNOTCH']
        if 'COIL_LENGTH' in self.data:
            self.COIL_LENGTH = self.data['COIL_LENGTH']
    
    def _build_tool_maps(self):
        """Build tool name and distance maps based on current configuration."""
        self.TOOL_NAME_MAP = {
            'h': ['Hole Punch', self.DISTANCE_HOLE_VNOTCH, 2],
            'v': ['V Notch', self.DISTANCE_SHEAR_VNOTCH, 1],
            'fm45': ['Full Cut -45', 5],
            'fp45': ['Full Cut +45', 4],
            'f0': ['Full Cut 0', 3],
            'pfr': ['Partial Front Right'],
            'pfl': ['Partial Front Left'],
            'prr': ['Partial Rear Right'],
            'prl': ['Partial Rear Left']
        }
        
        self.TOOL_DISTANCE_MAP = {
            'h': self.DISTANCE_HOLE_VNOTCH + self.COIL_START_POSITION,
            'v': self.COIL_START_POSITION,
            'fm45': self.DISTANCE_SHEAR_VNOTCH + self.COIL_START_POSITION + self.OFFSET_FM45,
            'fp45': self.DISTANCE_SHEAR_VNOTCH + self.COIL_START_POSITION + self.OFFSET_FP45,
            'f0': self.DISTANCE_SHEAR_VNOTCH + self.COIL_START_POSITION + self.OFFSET_F0
        }
    
    @staticmethod
    def findName(name) -> str:
        """Placeholder for name finding functionality."""
        pass
