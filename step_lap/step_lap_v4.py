#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 15:13:34 2021

@author: omkar
"""
import sys
sys.path.insert(1, '../gui/')


import json
import sys
from circuit import eTool
from pandas_writer import PandasWriterReader
from config import Config

#  Tools definition section

global conf
conf = Config()


#user input tool list
class ToolList:
    
    def __init__(self, **kwargs):
        
        #initialze tool with json file
        #not yet complete!
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
                    self._fn = kwargs['f_name']
                    self._sno = kwargs['s_no']
                    self._layers = kwargs['layers']
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

        
        l = self._length_list
        t = self._tool_list
    
        #final new list
        fnl = []
        for j in range(self._stepcount):
            #there must be a better way to this find it.
            nl = []
            #nl is the list of tuple corresponding to the respective steplap types
            #their values
            for i in range(len(l)):
                
                temp = t[i]
                print("####")
                temp.show()
                print('####')
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
                        #not needed for hole cut
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
                            nl[-1][0] += temp.steplap_vector[temp.rear_counter]
                            nl.append([l[i] + temp.steplap_vector[temp.front_counter], 0])
                            temp._increment_steplap_counter()
                            
                        elif temp.open_code in [9, 10]:
                            nl[-1][0] += temp.steplap_vector[temp.rear_counter]
                            temp._increment_steplap_counter()
                            
                    elif temp.name in ['prrp45, pflp45, prrf0, pfrf0, pfrm45']:
                        #adjust token lengths for scrap cut here
                        #nl[-1][0] += temp.step
                        pass
                            
                            
                elif temp.steplap_type == 2:
                    if temp.name == 'v':
                        if temp.open_code in [1, 2]:
                            nl.append([l[i], temp.steplap_vector[temp.rear_counter]])
                            temp._increment_steplap_counter()

                #is there a better way to do this last outlier?
                #outliers are necessary for the bounded cases
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
                    
            print("------")
            print(nl)
            print("------")  
            fnl.extend(nl*self._layers)    
                        
        self._nl = fnl
        #send the following to the execution unit.
        print("------")
        print(nl)
        print("------")
        self._map_exe()
        #self.createExecutable()
        self._exe()
        
        
    #maps the current logical tool cut sequence to the the actual physical equivivalent cut
    def _map_exe(self):
        
        start_sheet = self._sno - 1
        tl = self._tool_list
        modulo = len(self._tool_list) - 1
        long = 0
        sc = 0
        inner = []
        
        for i in range(len(self._nl)):
            if tl[i % modulo].name == 'h':
                inner.append(eTool('h', long, 0, 20))
            elif tl[i % modulo].name == 'v':
                inner.append(eTool('v', long, self._nl[i][1], 20))
            elif tl[i % modulo].name == 'fp45':
                sc += 1
                inner.append(eTool('fp45', long, 0, 20))
            elif tl[i % modulo].name == 'fm45':
                sc += 1
                inner.append(eTool('fm45', long, 0, 20))
            elif tl[i % modulo].name == 'f0':
                sc += 1
                inner.append(eTool('f0', long, 0, 20))
            elif tl[i % modulo].name == 's':
                sc += 1
                pass
            
            long += self._nl[i][0]
            long = round(long, 5)

        print('sheet-count - ', sc)
        long = float(round(long, 5))
        print('Long - ', long)
        
        #c = start_sheet // sc
        
        #total sheet count
        self.sc = sc
        
        rotation_pt = start_sheet % sc
        
        print('rotation - ', rotation_pt)
        
        
        temp = 0
        rot = 0
        
        for i in inner:
            if i.name[0] == 'f':
                if temp == rotation_pt:
                    rot = i.long
                    break
                temp += 1
                
        for i in inner:
            i.long -= rot
            #i.count = c
            if i.long < 0:
                i.long += long
            if i.long == 0:
                i.count += 1
        
        for i in inner:
            if i.name == 'fm45':
                i.long += conf.DISTANCE_SHEAR_VNOTCH + conf.OFFSET_FM45
                
            elif i.name == 'fp45':
                i.long += conf.DISTANCE_SHEAR_VNOTCH + conf.OFFSET_FP45
                
            elif i.name == 'f0':
                i.long += conf.DISTANCE_SHEAR_VNOTCH + conf.OFFSET_F0
                
            elif i.name == 'h':
                i.long += conf.DISTANCE_HOLE_VNOTCH
                
            i.long = round(i.long, 5)
                
        #add adjustable/dynamic parameters here
        
        for i in inner:
            print(i.name, '-', i.long, '-', i.count)
        
        self._new_pl = long
        self._new_etl = inner
        #self._new_exe()
        
        
    def _new_exe(self):
        
        def remove_null(l):
            remove = []
            for i in range(len(l)):
                if l[i].count <= 0:
                    remove.append(l[i])
                    
            for i in remove:
                l.remove(i)
                
            return l
        
        def _find_min(l):
            m = l[0].long
            for i in l:
                if i.long < m:
                    m = i.long
            return m
        
        feed = []
        #executable tool list
        op = []
        etl = self._new_etl
        
        repeat_flag = False
        
        while True:            
            etl = remove_null(etl)
            if not etl:
                break
            closest = _find_min(etl)
            for i in etl:
                if closest == i.long:
                    if repeat_flag:
                        feed.append(0)
                    else:
                        feed.append(closest)
                        repeat_flag = True
                    i.long = self._new_pl
                    op.append(i.name)
                    #i.count -= 1
                    
                else:
                    i.long -= closest
            repeat_flag = False
            
        for i in zip(feed, op):
            print(i)
            
        
        
    def createExecutable(self):
        inner = []
        pos = 0
        dtt = 0
        modulo = len(self._tool_list) - 1
        
        for i in range(len(self._nl)):
            dtt = pos + conf.TOOL_DISTANCE_MAP[self._tool_list[i % modulo].name]
            inner.append([self._tool_list[i % modulo].name, dtt, self._nl[i][1]])
            pos += self._nl[i][0]
        self._pl = pos
        self._exe_tl = inner
        
        # rotating the list about the coil dividing cuts
        
    # def _count_holes(self):
    #     h1, h2 = 0, 0
        
    #     #count sheet seperators here
        
    #     for i in self._tool_list:
    #         pass
    #     pass
        
    def _exe(self):
        
        #holes1, holes2 = self._count_holes()
        terminate = 200
        operation = []
        tool_number = []
        feed = []
        v_axis = []
        repeat_flag = False
        sheet_count = [self.sc]
        
        def _find_min(l):
            m = l[0].long
            for i in l:
                if i.long < m:
                    m = i.long
            return m
        
        def _feed_post(l):
            prev = None
            for i in range(len(l)):
                if l[i] == prev:
                    l[i] += 0.01 
                prev = l[i]
            return l
        
        
        while terminate > 0:
            closest_cut = _find_min(self._new_etl)
            for i in self._new_etl:
                if i.long == closest_cut:
                    i.long = self._new_pl
                    if repeat_flag:
                        feed.append(0)
                    else:
                        feed.append(closest_cut)
                        repeat_flag = True
                    if i.name == 'v':
                        v_axis.append(i.lat)
                    operation.append(i.name)
                    tool_number.append(conf.TOOL_NAME_MAP[i.name][-1])
                else:
                    i.long -= closest_cut
                    i.long = round(i.long, 5)
            repeat_flag = False
            terminate -= 1
        start_index = 0
        end_index = 0
        for i in range(len(operation)):
            if operation[i][0] == 'f':
                start_index = i
                break
        start_index += 2
        end_index = start_index + len(self._nl) - 1
        feed = feed[:end_index]
        feed = _feed_post(feed)
        operation = operation[:end_index]
        v_axis = v_axis[:self._stepcount]
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
        fn = self._fn
        PandasWriterReader.writeExcel(fname=fn,feed=feed, v_axis=v_axis, 
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
                                                  leg_len=leg_len, cl_len=cl_len,
                                                  )

    
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
        
        if n > 1:
            #vector for even step count
            if n % 2 == 0:
                self.steplap_vector = [(i - i/(2*abs(i)))*d for i in range( n//2 , -n//2 - 1, -1) if i != 0]
            #vector for odd step count
            else:
                self.steplap_vector = [i*d for i in range( n//2 , -n//2, -1) ]
            
    
    
    def _set_steplap_counter(self):
        #1 is treated the same 3. The diffenrece lies in the implementaion
        #of the lengthyfy for the different tools
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
            self.front_counter = self.steplap_count - 1
            self.rear_counter = self.steplap_count - 1
            
    
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
    
                
if __name__ == '__main__':
    #tl = ToolList(from_json = 'trial.json')
    b = Config()    
    
    