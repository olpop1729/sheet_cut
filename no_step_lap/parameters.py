#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 10:39:49 2021

@author: omkar

Parameters module. Uses the shared Config and tool_constants modules.
"""

import sys
import os

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import Offset
from shared.tool_constants import TOOL_ALIASES

# Export commonly used constants for backwards compatibility
SHEET_LENGTH = 100000
DISTANCE_HOLE_VNOTCH = int(Offset.DISTANCE_HOLE_VNOTCH)
DISTANCE_SHEAR_VNOTCH = int(Offset.DISTANCE_SHEAR_VNOTCH)

# Tool aliases for backwards compatibility
TOOL_HOLE = TOOL_ALIASES['HOLE']
TOOL_V_NOTCH = TOOL_ALIASES['V_NOTCH']
TOOL_P45 = TOOL_ALIASES['P45']
TOOL_M45 = TOOL_ALIASES['M45']
TOOL_F0 = TOOL_ALIASES['F0']

#-------------------------------------------
# directories

OUTPUT_CUT_PROGRAM_DIRECTORY = 'cut_program_output/'
CONFIG_FILE_NAME = 'cfg/config.txt'

#-------------------------------------------