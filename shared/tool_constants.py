#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool constants and mappings used across the sheet_cut application.
"""

# Tool alias lists for user input parsing
TOOL_ALIASES = {
    'HOLE': ['hole', 'h', 0],
    'V_NOTCH': ['v notch', 'vnotch', 'v', 1],
    'P45': ['full cut +45', '+45', '45', 'fp45', 'p45', 2],
    'M45': ['full cut -45', '-45', 'fm45', 'm45', 3],
    'F0': ['full cut', '0', '0 shear', 'shear', 'zero', 'f0', 'full cut 0', 4],
}

# Convenience access to tool aliases
TOOL_HOLE = TOOL_ALIASES['HOLE']
TOOL_V_NOTCH = TOOL_ALIASES['V_NOTCH']
TOOL_P45 = TOOL_ALIASES['P45']
TOOL_M45 = TOOL_ALIASES['M45']
TOOL_F0 = TOOL_ALIASES['F0']


class ToolNameMap:
    """
    Provides tool name mappings with associated distances and tool numbers.
    Can be used as a factory or with default values.
    """
    
    @staticmethod
    def get_default(distance_hole_vnotch=1250.0, distance_shear_vnotch=4335.0):
        """
        Get the default tool name map with specified distances.
        
        Args:
            distance_hole_vnotch: Distance from hole to vnotch position
            distance_shear_vnotch: Distance from shear to vnotch position
            
        Returns:
            Dictionary mapping tool codes to [name, distance/number, ...]
        """
        return {
            'h': ['Hole Punch', distance_hole_vnotch, 0],
            'v': ['V Notch', distance_shear_vnotch, 1],
            'fm45': ['Full Cut -45', 2],
            'fp45': ['Full Cut +45', 3],
            'f0': ['Full Cut 0', 4],
            'pfr': ['Partial Front Right'],
            'pfl': ['Partial Front Left'],
            'prr': ['Partial Rear Right'],
            'prl': ['Partial Rear Left']
        }


class ToolDistanceMap:
    """
    Provides tool distance mappings for calculating absolute positions.
    """
    
    @staticmethod
    def get_default(distance_hole_vnotch=1250.0, distance_shear_vnotch=4335.0,
                    coil_start_position=0.0, offset_fm45=0.0, offset_fp45=0.0, offset_f0=0.0):
        """
        Get the default tool distance map with specified parameters.
        
        Args:
            distance_hole_vnotch: Distance from hole to vnotch position
            distance_shear_vnotch: Distance from shear to vnotch position
            coil_start_position: Starting position of the coil
            offset_fm45: Offset for -45 degree full cut
            offset_fp45: Offset for +45 degree full cut
            offset_f0: Offset for 0 degree full cut
            
        Returns:
            Dictionary mapping tool codes to their absolute distances
        """
        return {
            'h': distance_hole_vnotch + coil_start_position,
            'v': coil_start_position,
            'fm45': distance_shear_vnotch + coil_start_position + offset_fm45,
            'fp45': distance_shear_vnotch + coil_start_position + offset_fp45,
            'f0': distance_shear_vnotch + coil_start_position + offset_f0
        }
