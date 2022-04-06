#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 17:10:07 2022

@author: omkar
"""

import json
from pandas_writer import PandasWriterReader
from config import Config

#this is temporary, will be removed when parameters are loaded
class offset:
    fm45 = 0.0
    fp45 = 0.0

class TooList_CL:
    
    
    def __init__(self, **kwargs):
        
        
        #initialze tool with json file
        # not yet complete
        if 'from_json' in kwargs:
            data = self._fromJson(kwargs['from_json'])
            print(data)
            
            
        #initalize tool from a db like object
        elif 'from_db' in kwargs:
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
                    self._scrap_length = kwargs['scrap_length']
                    self._ptype = kwargs['p_type']
                    self.data = kwargs['data']
                    self._ptype_decider()
                    print('Data recieved successfully.')
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
        if self._ptype == 3:
            SpearH(steplap_distance = self._steplap_distances[0], 
                   scrap_length = self._scrap_length, 
                   len_list = self._length_list, 
                   steplap_count = steplap_count, 
                   open_code = open_code, 
                   file_name = self._fn
                   )
    
    
    
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



class SpearH:
    
    def __init__(self, **kwargs):
        
        self.steplap_distance = kwargs['steplap_distance']
        self.scrap_length = kwargs['scrap_length']
        self.len_list = kwargs['len_list']
        self.steplap_count = kwargs['steplap_count']
        self.open = kwargs['open_code']
        self._fn = kwargs['file_name']
        
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
            self.steplap_vector = [i*d for i in range(n , -n-1, -1) if n != 0]
        else:
            self.steplap_vector = [i*d for i in range(n , -n-1, -1)]

        if self.open:
            return
        else:
            self.steplap_vector = self.steplap_vector[::-1]
            
            
    def create_dict(self):
        n = self.steplap_count
        dn = self.steplap_vector
        #m = self.layers
        m = 1
        hl = self.hole_list
        x = self.scrap_length
        l = sum(self.len_list)
        exe = []
        vtv = 0
        for i in range(n):

            vtv = sum(2*dn[:i]) + i * (l + 2*x)

            if len(hl) > 0:
                for j in hl:
                    exe.append(['h', vtv + j + x + dn[i], 0])
            exe.append(['v', vtv, x])
            exe.append(['fp45', vtv - x, 0])
            exe.append(['fm45', vtv + x, 0])

        self.exe = exe
        self.pl = ( l + 2*x ) * m * n
        
        
    def execute(self):
        exe = self.exe
        pl = self.pl

        for i in exe:
            if i[0] in ['fm45']:
                i[1] += 4335 + offset.fm45
            elif i[0] in ['fp45']:
                i[1] += 4335 + offset.fp45
            elif i[0] == 'h':
                i[1] += 1250
            elif i[0] == 0:
                i[1] += 0

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
                    tool_number.append(Config.TOOL_NAME_MAP[i[0]][-1])
                    if repeat:
                        feed.append(0)
                    else:
                        feed.append(cc)
                        repeat = True

                    i[1] = pl

                else:
                    i[1] -= cc

        start_index = 0
        end_index = 0
        for i in range(len(operation)):
            if operation[i][0] == 'f':
                start_index = i
                break
            
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
        

        
        
        
        
        
        
        
        