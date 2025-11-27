#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Labels and constants used for UI, messages, and data mapping across the sheet_cut application.
"""


class bcolors:
    """ANSI color codes for terminal output formatting."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Names:
    """Standard tool name constants."""
    HOLE = 'h'
    V_NOTCH = 'v'
    FP45 = 'fp45'
    FM45 = 'fm45'
    F0 = 'f0'
    SPEAR = 's'
    YOKE_SPLITTER = 'ys'


class Labels:
    """
    UI labels, message templates, and data mappings used throughout the application.
    """
    
    # Error/Warning prefixes
    ERROR = 'ERROR: '
    WARNING = 'WARNING: '
    
    # Input prompts
    add_tool = 'Add tool ? (y or n) : '
    get_name = 'Enter tool name : '
    get_step_lap_count = 'Enter step-lap count : '
    get_step_lap_distance = 'Enter step-lap Distance : '
    get_is_open = 'Open : '
    get_is_front = 'Front : '
    get_is_rear = 'Rear : '
    get_rear_open = 'Rear Open : '
    get_front_open = 'Front Open : '
    get_lateral_shift_count = 'Enter lateral-shift count : '
    get_length_list = 'Enter lengths seperated by spaces : '
    get_layers = 'Enter no. of layers : '
    get_lateral_shift_distance = 'Enter lateral-shift distance : '
    confirm = 'Continue ? : '
    incorrect_tool_input = 'Incorrect tool input. Last tool does not match the first tool.'
    
    # Step-lap type mappings
    steplap_type_map = {
        'No step-lap': 0,
        'Horizontal (Longitudinal)': 1,
        'Vertical (Lateral)': 2,
        'Skewed (Lateral)': 3
    }
    
    # Open code mappings
    open_code_map = {
        'NA': 0,
        'Open': 1,
        'Closed': 2,
        'Front Open, Rear Open': 3,
        'Front Open, Rear Closed': 4,
        'Front Closed, Rear Open': 5,
        'Front Closed, Rear Closed': 6,
        'Front Open': 7,
        'Front Closed': 8,
        'Rear Open': 9,
        'Rear Closed': 10
    }
    
    # GUI table columns
    create_frame_cols = [
        'PNR', 'Tool name', 'Step-lap type', 'Step-lap count',
        'Open-Close config', 'Skewed'
    ]
    
    # Available tool names for GUI selection
    tool_name_tuple = (
        'fm45', 'fp45', 'f0', 'v', 'h', 's', 'ys',
        'fish_head', 'fish_tail', 'prrp45',
        'pfrm45', 'prrf0', 'pfrf0', 'prlm45', 'prlf0',
        'pflp4', 'pflf0'
    )
    
    # Color constants for visualization
    color_cyan = 'cyan'
    color_black = 'black'
    color_grey = 'grey'
    color_green = 'green'
    color_red = 'red'
    
    # Attribute names
    name = 'name'
    pos = 'pos'
    is_front = 'is_front'
    is_rear = 'is_rear'
    end = 'end'
    linestyle = 'linestyle'
    from_json = 'from_json'
    from_db = 'from_db'
    main_frame = 'main_frame'
    reset = 'reset'
    update = 'update'
    Reset = 'Reset'
    Update = 'update'
    data = 'data'
    steplap_count = 'steplap_count'
    open_code = 'open_code'
    steplap_distance = 'steplap_distance'
    
    # Message box types
    msgbox_showwarning = 'showwarning'
    msgbox_showinfo = 'showinfo'
    
    # Warning/Info messages
    warnmsg_empty_object = 'Cannot display empty object.'
    infomsg_run_sy_profile = 'You are running a split-yoke profile.'
    infomsg_run_cl_profile = 'You are running a central-limb profile.'
    infomsg_run_sly_profile = 'You are running a sidelimb-yoke profile.'
    infomsg_build_successful = 'Profile build successful.'
    
    # Directory paths
    path_gui = '../gui/'
    path_program_input = '../cut_program_input/'
    
    # Window titles
    title_param_update = 'Parameter Update Screen'
    
    # Additional labels
    label_skewed = "Skewed"
    
    @staticmethod
    def printError(err):
        """Print an error message with formatting."""
        print(f'{bcolors.FAIL}{Labels.ERROR}{err}{bcolors.ENDC}')
    
    @staticmethod
    def warnOddCount():
        """Print warning for odd count requirement."""
        print(f'{bcolors.FAIL}{Labels.ERROR} Please enter an odd count.{bcolors.ENDC}')
    
    @staticmethod
    def warnNegativeCount():
        """Print warning for negative count."""
        print(f'{bcolors.FAIL}{Labels.ERROR} Count should not be negative.{bcolors.ENDC}')
    
    @staticmethod
    def warnHighStepLapCount():
        """Print warning for high step-lap count."""
        print(f'{bcolors.WARNING}{Labels.WARNING}step-lap has high value. May affect the accuracy of the output.{bcolors.ENDC}')
    
    @staticmethod
    def warnNegativeDistance():
        """Print warning for negative distance."""
        print(f'{bcolors.FAIL}{Labels.ERROR}Distances should not be zero or negative.{bcolors.ENDC}')
    
    @staticmethod
    def warnHighDistanceValue():
        """Print warning for high distance value."""
        print(f'{bcolors.WARNING}{Labels.WARNING}high distance value. May affect the accuracy of the output.{bcolors.ENDC}')
    
    @staticmethod
    def warnHighLateralShiftCount():
        """Print warning for high lateral shift count."""
        print(f'{bcolors.WARNING}{Labels.WARNING}high Lateral-count. May affect the accuracy of the output.{bcolors.ENDC}')
    
    @staticmethod
    def warnNameNotFound():
        """Print warning for name not found."""
        print(f'{bcolors.FAIL}{Labels.ERROR}Name not found.{bcolors.ENDC}')
    
    @staticmethod
    def warnNegativeLayers():
        """Print warning for negative layers."""
        print(f'{bcolors.FAIL}{Labels.WARNING}No. of layers cannot be negative!{bcolors.ENDC}')
