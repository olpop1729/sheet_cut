#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 15:13:34 2021

@author: omkar
"""
import json
import sys
import pandas as pd
import os
import itertools
#  Tools definition section



class Config:
    OFFSET_F0 = 0
    OFFSET_FP45 = 0
    OFFSET_FM45 = 0
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
                     'fm45':['Full Cut -45',4],
                     'fp45':['Full Cut +45',3],
                     'f0':['Full Cut 0',5],
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


class PandasWriterReader:
    
    def writeExcel(fname='Trial', **kwargs):
        if len(kwargs.keys()) < len(Config.EXCEL_COLUMN_NAMES):
            sys.exit(0)
        cut_feed = list(itertools.zip_longest(kwargs['feed'], kwargs['v_axis'],kwargs['sec_feed'],
                    kwargs['operation'], kwargs['tool_number'], 
                    kwargs['start_index'], kwargs['end_index'], 
                    kwargs['job_shape'], kwargs['number_of_steps'], 
                    kwargs['sheet_count'], kwargs['p45_overcut'], 
                    kwargs['m45_overcut'], kwargs['yoke_len'],
                    kwargs['leg_len'], kwargs['cl_len']))
        df = pd.DataFrame(data = cut_feed, columns=Config.EXCEL_COLUMN_NAMES)
        df.index += 1
        temp = pd.ExcelWriter('../cut_program_output/' + fname + '.xlsx')
        df.to_excel(temp)
        temp.save()




#user input tool list
class ToolList:
    
    def __init__(self, **kwargs):
        #initialze tool with json file
        if 'from_json' in kwargs:
            data = self._fromJson(kwargs['from_json'])
            self._populate_data(data)
            
        #initalize tool from a db like object
        elif 'from_db' in kwargs:
            print('Yet to be implemented.')
        
        #If none of the above, initialize an empty object.
        else:
            #show error message here after wards
            if 'data' in kwargs:
                try:
                    self._steplap_distances = kwargs['d_list']
                    self._length_list = kwargs['l_list']
                    self._populate_data(kwargs['data'])
                    print('Data recieved successfully.')
                except KeyError as err:
                    print('Incorrect arguments passed.')
                    print(err)
            else:
                print('Uh oh, no data passed.')
            
            self._ready_steplaps()
            pass
        
    def _ready_steplaps(self):
        self._stepcount = max([i.steplap_count for i in self._tool_list])
        if not self._stepcount:
            self._stepcount = 1
        for i in self._tool_list:
            
            i._generate_steplap_vector()
            i._set_steplap_counter()
            
        for i in self._tool_list:
            i.show()
            
        self._lengthyfy()
            
            
    
    #read from json and assgin to attributes
    def _populate_data(self, data):
        #first validate the data
        self._validate_data(data)
        
        if not data:
            print('Data input error')
            sys.exit()
        tl = [] # the loaded tool list
        for i in data:
            tl.append(Tool(data[i]))
         
        d_counter = 0
        for i in tl:
            if i.steplap_count > 1:
                i._steplap_distance = self._steplap_distances[d_counter]
                d_counter += 1
        self._tool_list = tl
        

            
    #method for validating the data
    def _validate_data(self,data):
        #check if the sequencing of the cut is proper i.e. according to the 
        #given justified pattern
        return
            
    
    
    #get the data dictionary from the json file
    def _fromJson(self, name):
        data = {}
        path = '../cut_program_input/' + name
        try:
            with open(path, 'r') as fp:
                data = json.load(fp)
            return data
        except FileNotFoundError as err:
            print(err)
            return None
        raise(Exception)
        
    #export the data to json if necessary (for logging)
    def _toJson(self, data):
        try:
            with open('output.json', 'w') as fp:
                fp.write(json.dumps(data, indent=4))
            return None
        except IOError as err:
            print(err)
            return
        raise(Exception)
        
        
    #returns an ExecutableTool object which is execution ready
    def _lengthyfy(self):
        #there must be a better way to this find it.
        nl = []
        #nl is the list of tuple corresponding to the respective steplap types
        #their values
        
        l = self._length_list
        t = self._tool_list
        for j in range(self._stepcount):
            for i in range(len(l)):
                temp = t[i]
                if temp.steplap_type  == 0:
                    nl.append([l[i],0])
                elif temp.steplap_type == 1:
                    if temp.name == 'h':
                        #remember to throw an error if open code = 0 here!!!!
                        
                        #if temp.open_code in [1, 2, 7, 8]:
                        if  temp.open_code in [1, 2]:
                            nl[-1][0] += temp.steplap_vector[temp.rear_counter]
                            nl.append([l[i] + temp.steplap_vector[temp.front_counter], 0])
                            temp._increment_steplap_counter()
                        elif temp.open_code in [3, 4, 5, 6]:
                            pass
                        #not need for hole cut
                        # elif temp.open_code in [3, 4, 5, 6]:
                        #     nl[-1][0] += temp.steplap_vector[temp.rear_counter]
                        #     nl.append([l[i] + temp.steplap_vector[temp.front_counter], 0])
                        #     temp._increment_steplap_counter()
                            
                        # elif temp.open_code in [9, 10]:
                        #     nl[-1][0] += temp.steplap_vector[temp.rear_counter]
                        #     temp._increment_steplap_counter()
                            
                            
                    elif temp.name == 'v':
                        #remember to throw an error if open code = 0 here!!!!
                        
                        if  temp.open_code in [1, 2]:
                            nl[-1][0] += temp.steplap_vector[temp.rear_counter]
                            nl.append([l[i] + temp.steplap_vector[temp.front_counter], 0])
                            temp._increment_steplap_counter()
                        elif temp.open_code in [3, 4, 5, 6]:
                            pass
                        
                        # if temp.open_code in [1, 2, 7, 8]:
                        #     nl.append([l[i] + temp.steplap_vector[temp.front_counter], 0])
                        #     temp._increment_steplap_counter()
                            
                        # elif temp.open_code in [3, 4, 5, 6]:
                        #     nl[-1][0] += temp.steplap_vector[temp.rear_counter]
                        #     nl.append([l[i] + temp.steplap_vector[temp.front_counter], 0])
                        #     temp._increment_steplap_counter()
                            
                        # elif temp.open_code in [9, 10]:
                        #     nl[-1][0] += temp.steplap_vector[temp.rear_counter]
                        #     temp._increment_steplap_counter()
                            
                            
                    elif temp.name in ['fm45', 'fp45', 'f0']:
                        #remember to throw an error if open code = 0 here!!!!
                        
                        if temp.open_code in [1, 2, 7, 8]:
                            nl.append([l[i] + temp.steplap_vector[temp.front_counter], 0])
                            temp._increment_steplap_counter()
                            
                        elif temp.open_code in [3, 4, 5, 6]:
                            # nl[-1][0] += temp.steplap_vector[temp.rear_counter]
                            nl.append([l[i] + temp.steplap_vector[temp.front_counter], 0])
                            temp._increment_steplap_counter()
                            
                        elif temp.open_code in [9, 10]:
                            nl[-1][0] += temp.steplap_vector[temp.rear_counter]
                            temp._increment_steplap_counter()
                            
                            
                elif temp.steplap_type == 2:
                    if temp.name == 'v':
                        if temp.open_code in [1, 2]:
                            nl.append([l[i], temp.steplap_vector[temp.front_counter]])
                            temp._increment_steplap_counter()

                #is there a better way to do this last outlier?
                #outliers are necessary for the bound cases
                if i == len(l) - 1:
                    temp = t[i+1]
                    if temp.steplap_type == 0:
                        continue
                    elif temp.steplap_type == 1:
                        if temp.name in ['fm45', 'fp45', 'f0']:
                                
                            if temp.open_code in [1, 2]:
                                nl[-1][0] += temp.steplap_vector[temp.front_counter]
                                temp._increment_steplap_counter()
                    elif temp.steplap_type == 2:
                        #this case should not happening in any of the current scenarios
                        #that are currently being looked upon
                        pass
                    
                    
                    
                        
        self._nl = nl
        #send the following to the execution unit.
        #print(nl)
        self.createExecutable()
        self._exe()
        
    def createExecutable(self):
        inner = []
        pos = 0
        dtt = 0
        modulo = len(self._tool_list) - 1
        
        for i in range(len(self._nl)):
            dtt = pos + Config.TOOL_DISTANCE_MAP[self._tool_list[i % modulo].name]
            inner.append([self._tool_list[i % modulo].name, dtt, self._nl[i][1]])
            pos += self._nl[i][0]
        self._pl = pos
        self._exe_tl = inner
        print(inner)
        
    def _exe(self):
        terminate = 0
        operation = []
        tool_number = []
        feed = []
        v_axis = []
        repeat_flag = False
        sheet_count = []
        sheet_counter = -1
        while terminate < Config.COIL_LENGTH:
            closest_cut = min([i[1] for i in self._exe_tl])
            for i in self._exe_tl:
                if i[1] == closest_cut:
                    i[1] = self._pl
                    if repeat_flag:
                        feed.append(0)
                    else:
                        feed.append(closest_cut)
                        repeat_flag = True
                    v_axis.append(i[2])
                    operation.append(i[0])
                    tool_number.append(Config.TOOL_NAME_MAP[i[0]][-1])
                    sheet_count.append(sheet_counter)
                    if i[0] == self._exe_tl[0][0]:
                        sheet_counter += 1
                else:
                    i[1] -= closest_cut
            repeat_flag = False
            terminate += closest_cut
        start_index = 0
        end_index = 0
        for i in range(len(operation)):
            if operation[i][0] == 'f':
                start_index = i
                break
        start_index += 2
        end_index = start_index + len(self._nl) - 1
        feed = feed[:end_index]
        operation = operation[:end_index]
        v_axis = v_axis[:end_index]
        tool_number = tool_number[:end_index]
        sheet_count = sheet_count[:end_index]
        start_index = [start_index]
        end_index = [end_index]
        sec_feed = []
        number_of_steps = []
        p45_overcut = []
        m45_overcut = []
        yoke_len = []
        leg_len = []
        cl_len = []
        job_shape = []
        PandasWriterReader.writeExcel(feed=feed, v_axis=v_axis, 
                                                  sec_feed=sec_feed, 
                                                  operation=operation, 
                                                  tool_number=tool_number, 
                                                  start_index=start_index, 
                                                  end_index=end_index, 
                                                  job_shape=job_shape, 
                                                  number_of_steps=number_of_steps, 
                                                  sheet_count=sheet_count, 
                                                  p45_overcut=p45_overcut,
                                                  m45_overcut=m45_overcut, 
                                                  yoke_len=yoke_len, 
                                                  leg_len=leg_len, cl_len=cl_len)

    
class Tool:
    
    def __init__(self, data):
        
        self.long_pos = 0
        self.lat_pos = 0
        
        if data:
        
            self.name = data['name']
            self.steplap_count = data['steplap_count']
            self._steplap_distance = data['_steplap_distance']
            self.steplap_type = data['steplap_type']
            self.open_code = data['open_code']
            
        else:
            print('Input data empty. Please add read data from the json file only.')
            
    def _set_slp_distance(self, dist):
        if dist:
            self._steplap_distance = dist
        else:
            self._steplap_distance = 0
        
            
    def _generate_steplap_vector(self):
        d = self._steplap_distance
        n = self.steplap_count
        #vector for even step count
        if n > 1:
            if n % 2 == 0:
                self.steplap_vector = [i*d for i in range(-n//2 + 1, n//2 + 1) if i != 0]
            #vector for odd step count
            else:
                self.steplap_vector = [i*d for i in range(-n//2 + 1, n//2 + 1) ]
            
    
    
    def _set_steplap_counter(self):
        #1 is treated the same 3. The diffenrece lies in the implementaion
        #of the lengthyfy for the different tools
        #open starts with the highest value in the vector
        if self.open_code in [4, 1, 7, 10]:
            self.front_counter = 0
            self.rear_counter = self.steplap_count - 1
        #same story as above
        #closed starts with the sammlest value in the vector
        elif self.open_code in [2, 5, 8, 9]:
            self.front_counter = self.steplap_count - 1
            self.rear_counter = 0
        elif self.open_code == 3:
            self.front_counter = 0
            self.rear_counter = 0
        elif self.open_code == 6:
            self.front_counter == self.steplap_count - 1
            self.rear_counter == self.steplap_count - 1
            
    
    #steping to next steplap distance
    def _increment_steplap_counter(self):
        #variable names for simplicity
        f = self.front_counter
        r = self.rear_counter
        n = self.steplap_count
        
        #open increment implies moving forward in the vector
        if self.open_code == 1 or self.open_code == 4:
            f = ( f + 1 ) % n
            r = ( r - 1 ) % n
        #closed increment imples moving backward in the vector
        elif self.open_code == 2 or self.open_code == 5:
            f = ( f - 1 ) % n
            r = ( r + 1 ) % n
        elif self.open_code == 3:
            f = ( f + 1 ) % n
            r = ( r + 1 ) % n
        elif self.open_code == 6:
            f = ( f - 1 ) % n
            r = ( r - 1 ) % n
        self.front_counter = f
        self.rear_counter = r
    #update indices after increment
           
        
    def show(self):
        print(vars(self))
        
    def _step(self):
        #return (long_pos f, laong_pos r, lat_pos)
        pass
    
                
if __name__ == '__main__':
    tl = ToolList(from_json = 'trial.json')
    
        
    