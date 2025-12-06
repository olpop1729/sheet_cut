#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 11:39:24 2022

@author: omkar

Pandas utilities for GUI. Uses the shared PandasWriterReader class.
"""

import sys
import os

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.pandas_utils import PandasWriterReader, PandasModule

# Re-export for backwards compatibility
__all__ = ['PandasWriterReader', 'PandasModule']
