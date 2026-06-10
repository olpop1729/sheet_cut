#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 18:47:29 2022

@author: omkar

Labels module for GUI. Uses the shared Labels class.
"""

import sys
import os

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.labels import Labels, Names, bcolors

# Re-export for backwards compatibility
__all__ = ['Labels', 'Names', 'bcolors']
