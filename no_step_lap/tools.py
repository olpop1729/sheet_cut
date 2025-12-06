#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 10:37:05 2021

@author: omkar

Tool constants module. Uses the shared ToolNameMap class.
"""

import sys
import os

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.tool_constants import ToolNameMap
from shared.config import Offset

# For backwards compatibility, create TOOL_NAME_MAP using default values
DISTANCE_HOLE_VNOTCH = Offset.DISTANCE_HOLE_VNOTCH
DISTANCE_SHEAR_VNOTCH = Offset.DISTANCE_SHEAR_VNOTCH

TOOL_NAME_MAP = ToolNameMap.get_default(DISTANCE_HOLE_VNOTCH, DISTANCE_SHEAR_VNOTCH)

