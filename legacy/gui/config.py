#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 11:39:39 2022

@author: omkar

Configuration module for GUI. Uses the shared Config class.
"""

import sys
import os

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import Config, Offset

# Re-export for backwards compatibility
__all__ = ['Config', 'Offset']

