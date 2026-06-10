class Config:
    OFFSET_F0 = 1.25
    OFFSET_FP45 = -0.75
    OFFSET_FM45 = 0.75
    DISTANCE_HOLE_VNOTCH = 1250
    DISTANCE_SHEAR_VNOTCH = 4335
    COIL_LENGTH = 400000
    CUT_PROGRAM_OUTPUT_DIRECTORY = '../cut_program_output'
    COIL_START_POSITION = 0 # w.r.t. V_Notch.
    OUTPUT_FILE_NAME = 'CutFeed_'
    LIST_NO = ['no', 'n','not', '0','negative','incorrect']
    LIST_YES = ['yes', 'y', 'affirmative', 'correct', '1']
    EXCEL_COLUMN_NAMES = ['Feed Dist', 'Vnotch Trav Dist', 'After Shear feed Tip Cut',
                     'Tool', 'Tool no', 'Start Index', 'End Index',
                     'Job Shape', 'No of Steps', 'Sheet Count', 'P45 OverCut', 
                     'M45 OverCut', 'Yoke Len', 'Leg Len', 'Cnetral Limb Len']
    TOOL_NAME_MAP = {'h':['Hole Punch', DISTANCE_HOLE_VNOTCH,2],
                     'v':['V Notch', DISTANCE_SHEAR_VNOTCH,1],
                     'fm45':['Full Cut -45',5],
                     'fp45':['Full Cut +45',4],
                     'f0':['Full Cut 0',3],
                     'pfr':['Partial Front Right'],
                     'pfl':['Partial Front Left'],
                     'prr':['Partial Rear Right'],
                     'prl':['Partial Rear Left']
                     }
    TOOL_DISTANCE_MAP = {'h':DISTANCE_HOLE_VNOTCH + COIL_START_POSITION,
                         'v':COIL_START_POSITION,
                         'fm45':DISTANCE_SHEAR_VNOTCH + COIL_START_POSITION + OFFSET_FM45,
                         'fp45':DISTANCE_SHEAR_VNOTCH + COIL_START_POSITION + OFFSET_FP45,
                         'f0': DISTANCE_SHEAR_VNOTCH + COIL_START_POSITION + OFFSET_F0
                         }
    
    def findName(name) -> str:
        while True:
            break
        pass
    
    
    def update():
        Config.OFFSET_F0 = 2.0
        
print('Intital values - ', Config.OFFSET_F0)
