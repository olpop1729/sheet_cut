#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 17:10:07 2022

@author: omkar
"""

import json
from pandas_writer import PandasWriterReader
from config import Config
from label_file import Labels

#this is temporary, will be removed when parameters are loaded

global conf
conf = Config()

class TooList_CL:
    
    
    def __init__(self, **kwargs):
        
        
        #initialze tool with json file
        # not yet complete
        if Labels.from_json in kwargs:
            data = self._fromJson(kwargs[Labels.from_json])
            print(data)
            
            
        #initalize tool from a db like object
        elif Labels.from_db in kwargs:
            print('Yet to be implemented.')
            
         
        # generic initialization
        else:
            #show error message here after wards
            if 'data' in kwargs:
                try:
                    self._steplap_distances = kwargs['d_list']
                    self._length_list = kwargs['l_list']
                    self._fn = kwargs['f_name']
                    self._sno = kwargs['s_no']
                    self._layers = kwargs['layers']
                    self._scrap_length = kwargs['scrap_length']
                    self._ptype = kwargs['p_type']
                    self.data = kwargs['data']
                    self._ptype_decider()
                    
                except KeyError as err:
                    print('Incorrect arguments passed.')
                    print(err)
            else:
                print('No data passed.')

        
   #yet to be implemented 
    def _param_init(self):
        pass
    
    
    def _ptype_decider(self):
        steplap_count = self.data['0']['steplap_count']
        open_code = self.data['0']['open_code']
        
        # todo add a kwarg for layers
        # spear horizontal steplap
        if self._ptype == 3:
            SpearH(steplap_distance = self._steplap_distances[0], 
                   scrap_length = self._scrap_length, 
                   len_list = self._length_list, 
                   steplap_count = steplap_count, 
                   open_code = open_code, 
                   file_name = self._fn, 
                   layers = self._layers
                   )
            
        # symmetric fishand asymmetric fish types
        # fish shapes are most formula centric
        elif self._ptype in [4, 5]:
            a = SpearV(steplap_distance = self._steplap_distances[0],
                       len_list = self._length_list, 
                       steplap_count = steplap_count, 
                       file_name = self._fn, 
                       layers = self._layers,
                       ptype = self._ptype
                       )
           
        
        
    
    
    
    #get the data dictionary from the json file
    def _fromJson(self, name):
        data = {}
        path = Labels.path_program_input + name
        try:
            with open(path, 'r') as fp:
                data = json.load(fp)
            return data
        except FileNotFoundError as err:
            print(err)
            return None
        raise(Exception)
        
        
#fish with head and tail near the center line
class SpearV:
    
    def __init__(self, **kwargs):
        self.steplap_distance = kwargs['steplap_distance']
        self.length_list = kwargs['len_list']
        self.layers = kwargs['layers']
        self.steplap_count = kwargs['steplap_count']
        self._fn = kwargs['file_name']
        self.ptype = kwargs['ptype']
        
        self.create_hole_list()
        self.create_dict()
        self.execute()
        
        
    def create_hole_list(self):
        pos = 0
        ret = []
        if len(self.length_list) > 1:
            for i in range(len(self.length_list)-1):
                pos = pos + self.length_list[i]
                ret.append(pos)
        self.hole = ret

        
        if self.ptype == 4:
            self.k = self.steplap_count // 2
        elif self.ptype == 5:
            self.k = self.steplap_count - 1
        
        self.fish_len = sum(self.length_list)
        
        
        
    def create_dict(self):
        
        exe = []
        d = self.steplap_distance
        k = self.k
        l = self.fish_len
        m = self.layers
        n = self.steplap_count
        mult = 1
        for i in range(n * m):
            if len(self.hole) > 0:
                for j in self.hole:
                    #exe.append(['h', j + (2*self.k - i + 2*self.k*i)*self.step_lap_distance + i*self.fish_len])
                    #exe.append(['h',j + i*self.fish_len + self.step_lap_distance*(2*self.k*i + 2*self.k - i)])
                    exe.append(['h', i*(l+mult*(n - 1)*d) + j + (2*k - i//m)*d])
            #exe.append(['fm45', i*self.fish_len + (3+(i//m))*self.k*self.step_lap_distance])
            #exe.append(['fp45',((i//m) + 1)*self.fish_len + (3+(i//m))*self.k*self.step_lap_distance])
            exe.append(['fm45', (3*k-2*(i//m))*d + (l+mult*k*d)*i])
            exe.append(['fp45', (k-2*(i//m))*d + ((l+mult*(n-1)*d)*(i+1))])
            exe.append(['v', i*(self.fish_len + mult * (self.steplap_count - 1) * self.steplap_distance)])
        self.exe = exe
        self.pattern_length = round(n * ( l + mult * ( n - 1 ) * d ) * m, 5)
    
    
        
    def execute(self):
        for i in self.exe:
            if i[0] == 'fp45':
                i[1] += conf.DISTANCE_SHEAR_VNOTCH + conf.OFFSET_FP45
            elif i[0] == 'fm45':
                i[1] += conf.DISTANCE_SHEAR_VNOTCH + conf.OFFSET_FM45
            elif i[0] == 'h':
                i[1] += conf.DISTANCE_HOLE_VNOTCH
            i[1] = round(i[1], 5)
        terminate = 500
        feed = []
        vaxis = []
        operation = []
        tool_number = []
        
        for i in sorted(self.exe, key = lambda x: x[1]):

            print(i[0], '--', i[1])
        print('pattern length - ', self.pattern_length)
        
        while terminate > 0:
            terminate -= 1
            close = min([i[1] for i in self.exe])
            repeat = False
            
            for i in self.exe:
                if i[1] == close:
                    if i[0] == 'v':
                        vaxis.append(self.k * self.steplap_distance)
                    else:
                        vaxis.append(0)
                    if repeat:
                        feed.append(0)
                    else:
                        feed.append(close)
                    operation.append(i[0])
                    tool_number.append(conf.TOOL_NAME_MAP[i[0]][-1])
                    i[1] = self.pattern_length
                    repeat = True
                else:
                    i[1] -= close
                    i[1] = round(i[1], 5)
                    
           
        for i in range(len(operation)):
            if operation[i][0] == 'f':
                start_index = i
                break
        start_index += 2
        end_index = start_index + len(self.exe) - 1
                    
        sec_feed = []
        number_of_steps = []
        p45_overcut = []
        m45_overcut = []
        yoke_len = []
        leg_len = []
        cl_len = []
        job_shape = []
        
        
        sheet_count = []
        start_index = [start_index]
        end_index = [end_index]
        
        #cut_feed = list(zip(feed, vaxis,operation))
        
        PandasWriterReader.writeExcel(fname=self._fn,feed=feed, v_axis=vaxis, 
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
        # cut_feed = list(zip(feed, vaxis,operation))
        # df = pd.DataFrame(data = cut_feed, columns=['Feed','V-Axis','Operation'])
        # df.index += 1
        # temp = pd.ExcelWriter('../cut_program_output/FishyFish_0.xlsx')
        # df.to_excel(temp)
        # temp.save()



class SpearH:
    
    def __init__(self, **kwargs):
        
        self.steplap_distance = kwargs['steplap_distance']
        self.scrap_length = kwargs['scrap_length']
        self.len_list = kwargs['len_list']
        self.steplap_count = kwargs['steplap_count']
        self.open = kwargs['open_code']
        self._fn = kwargs['file_name']
        self._layers = kwargs['layers']
        
        self.gen_hole_list()
        self.gen_steplap_vector()
        
        self.create_dict()
        self.execute()
        
        
    def gen_hole_list(self):
        ll = self.len_list
        ret = []
        for i in range(len(ll) - 1):
            ret.append(sum(ll[:i+1]))
        self.hole_list = ret
        
        
    def gen_steplap_vector(self):
        n = self.steplap_count // 2
        d = self.steplap_distance
        if self.steplap_count % 2 == 0:
            self.steplap_vector = [round((i - i/(2*abs(i)))*d, 5) 
                                   for i in range(n , -n-1, -1) if i != 0]
        else:
            self.steplap_vector = [i*d for i in range(n , -n-1, -1)]

        if self.open == 1:
            return
        elif self.open == 2:
            self.steplap_vector = self.steplap_vector[::-1]
            
            
    def create_dict(self):
        n = self.steplap_count
        dn = self.steplap_vector
        #m = self.layers
        m = self._layers
        hl = self.hole_list
        x = self.scrap_length
        l = sum(self.len_list)
        exe = []
        vtv = 0
        for i in range(n * m):

            vtv = sum(2*dn[:i]) + i * (l + 2*x)
            vtv = round(vtv, 5)

            if len(hl) > 0:
                for j in hl:
                    exe.append(['h', 
                                round(vtv + j + x + dn[i], 5), 0])
            exe.append(['v', vtv, x])
            exe.append(['fp45', round(vtv - x, 5), 0])
            exe.append(['fm45', round(vtv + x, 5), 0])

        self.exe = exe
        for i in sorted(exe, key = lambda x: x[1]):

            print(i[0], '--', i[1])
        self.pl = round(( l + 2 * x ) * m * n, 5)
        
        
    def execute(self):
        exe = self.exe
        pl = self.pl

        for i in exe:
            if i[0] in ['fm45']:
                i[1] += conf.DISTANCE_SHEAR_VNOTCH + conf.OFFSET_FM45
            elif i[0] in ['fp45']:
                i[1] += conf.DISTANCE_SHEAR_VNOTCH + conf.OFFSET_FP45
            elif i[0] == 'h':
                i[1] += conf.DISTANCE_HOLE_VNOTCH
            elif i[0] == 0:
                i[1] += 0
                
            i[1] = round(i[1], 5)

        term = 200

        feed = []
        operation = []
        vaxis = []
        tool_number = []

        while term > 0:
            term -= 1
            cc = min([i[1] for i in exe])
            repeat = False
            for i in exe:
                if i[1] == cc:
                    vaxis.append(i[2])
                    operation.append(i[0])
                    tool_number.append(conf.TOOL_NAME_MAP[i[0]][-1])
                    if repeat:
                        feed.append(0)
                    else:
                        feed.append(cc)
                        repeat = True

                    i[1] = pl

                else:
                    i[1] -= cc
                    i[1] = round(i[1], 5)

        start_index = 0
        end_index = 0

            
        sec_feed = []
        number_of_steps = []
        p45_overcut = []
        m45_overcut = []
        yoke_len = []
        leg_len = []
        cl_len = []
        job_shape = []
        
        for i in range(len(operation)):
            if operation[i][0] == 'f':
                start_index = i
                break
        start_index += 2
        end_index = start_index + len(self.exe) - 1
        
        sheet_count = []
        start_index = [start_index]
        end_index = [end_index]
        
        #cut_feed = list(zip(feed, vaxis,operation))
        
        PandasWriterReader.writeExcel(fname=self._fn,feed=feed, v_axis=vaxis, 
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
        

        
        
        
        
        
        
        
        