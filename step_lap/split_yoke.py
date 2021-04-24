#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 23:20:23 2021

@author: omkar
"""
import os, sys
import pandas as pd
import json

class YokeSplitter:
    
    def __init__(self, var_dict=None):
        self.name = 'ys'
        self.pos = 0
        self.slp_count = 1
        self.slp_distance = 0
        self.slp_vector = []
        self.slp_counter = 0
        self.front_open = False
        if var_dict:
            self.loadFromDict(var_dict)
            
    def loadFromDict(self, var):
        self.pos = var['pos']
        self.slp_count = var['slp_count']
        self.slp_distance = var['slp_distance']
        self.slp_vector = var['slp_vector']
        self.slp_counter = var['slp_counter']
        self.front_open = var['front_open']
        
    def lengthyfy(self):
        return 0
    
    def hasStepLap(self) -> bool:
        if self.slp_count > 1:
            return True
        return False
        
    def getSlpCount(self):
        self.slp_count = int(input('Enter step-lap count :'))
        
    def getSlpDistance(self):
        self.slp_distance = float(input('Enter step-lap distance : '))
        
    def generateSlpVector(self):
        n = self.slp_count
        d = self.slp_distance
        self.slp_vector = [i*d for i in range(n//2, -n//2,-1)]
        if self.front_open:
            self.slp_counter = 0
        else:
            self.slp_counter = n-1
        
    def incrementSlpCounter(self):
        if self.front_open:
            self.slp_counter += 1
            self.slp_counter %= self.slp_count
        else:
            self.slp_counter -= 1
            self.slp_counter %= self.slp_count
    
    def getFrontOpen(self):
        if input('Front open : ').lower() in ['y',  'yes']:
            self.front_open = True
        else:
            self.front_open = False
            

class Fm45:
    
    def __init__(self, var_dict=None):
        self.name = 'fm45'
        self.pos = 0
        self.slp_count = 1
        self.slp_distance = 0
        self.slp_vector = []
        self.slp_counter = 0
        self.open = False
        if var_dict:
            self.loadFromDict(var_dict)
            
    def loadFromDict(self, var):
        self.pos = var['pos']
        self.slp_count = var['slp_count']
        self.slp_distance = var['slp_distance']
        self.slp_vector = var['slp_vector']
        self.slp_counter = var['slp_counter']
        self.open = var['open']
        
    def lengthyfy(self):
        return 0
    
    def hasStepLap(self) -> bool:
        if self.slp_count > 1:
            return True
        return False
    
    def getOpen(self):
        if input('Open ? : ').lower() in ['y', 'yes']:
            self.open = True
        else:
            self.open = False
        
    def getSlpCount(self):
        self.slp_count = int(input('Enter step-lap count :'))
        
    def getSlpDistance(self):
        self.slp_distance = float(input('Enter step-lap distance : '))
        
    def generateSlpVector(self):
        n = self.slp_count
        d = self.slp_distance
        self.slp_vector = [i*d for i in range(n//2, -n//2,-1)]
        if self.open:
            self.slp_counter = 0
        else:
            self.slp_counter = n-1
    
    def incrementSlpCounter(self):
        if self.open:
            self.slp_counter += 1
            self.slp_counter %= self.slp_count
        else:
            self.slp_counter -= 1
            self.slp_counter %= self.slp_count   
                
class Fp45:
    
    def __init__(self, var_dict=None):
        self.name = 'fp45'
        self.pos = 0
        self.slp_count = 1
        self.slp_distance = 0
        self.slp_vector = []
        self.slp_counter = 0
        self.open = False
        if var_dict:
            self.loadFromDict(var_dict)
            
    def loadFromDict(self, var):
        self.pos = var['pos']
        self.slp_count = var['slp_count']
        self.slp_distance = var['slp_distance']
        self.slp_vector = var['slp_vector']
        self.slp_counter = var['slp_counter']
        self.open = var['open']
        
    def lengthyfy(self):
        return 0
    
    def hasStepLap(self) -> bool:
        if self.slp_count > 1:
            return True
        return False
    
    def getOpen(self):
        if input('Open ? : ').lower() in ['y', 'yes']:
            self.open = True
        else:
            self.open = False
        
    def getSlpCount(self):
        self.slp_count = int(input('Enter step-lap count :'))
        
    def getSlpDistance(self):
        self.slp_distance = float(input('Enter step-lap distance : '))
        
    def generateSlpVector(self):
        n = self.slp_count
        d = self.slp_distance
        self.slp_vector = [i*d for i in range(n//2, -n//2,-1)]
        if self.open:
            self.slp_counter = 0
        else:
            self.slp_counter = n-1
    
    def incrementSlpCounter(self):
        if self.open:
            self.slp_counter += 1
            self.slp_counter %= self.slp_count
        else:
            self.slp_counter -= 1
            self.slp_counter %= self.slp_count
            
class Hole:
    
    def __init__(self, var_dict=None):
        self.name = 'h'
        self.pos = 0
        if var_dict:
            self.loadFromDict(var_dict)
            
    def loadFromDict(self, var):
        self.name = var['name']
        self.pos = var['pos']
        
    def lengthyfy(self):
        return 0
    
    def hasStepLap(self) -> bool:
        return False
    
class JobProfile:
    
    def __init__(self,  tl = None):
        if tl:
            self.loadCutProgram()
        else:
            self.getToolList()
            
    def displayCutProgram(self, name):
        #dname = '../cut_program_input/split_yoke/' + name
        print('Display is yet to be implemented ...')
        return True
        #inputs = os.listdir(.)
            
    def showCutPrograms(self):
        names = [i for i in os.listdir('../cut_program_input/split_yoke/') if 
                 i.endswith('json')]
        while True:
            for index in range(len(names)):
                print(f'{index+1} : {names[index]}')
            index = input('Enter index or name : ')
            if index == 'q':
                sys.exit()
            try : 
                fi = int(index)
                if self.displayCutProgram(names[fi-1]):
                    return names[fi-1]
                else:
                    continue
                
            except ValueError:
                try :
                    if self.displayCutProgram(index):
                        return index
                    else :
                        continue
                except Exception as e:
                    print(e)
                    return                    
                
            
    def loadCutProgram(self):
        name = self.showCutPrograms()
        with open('../cut_program_input/split_yoke/' + name, 'r') as fp:
            data = json.load(fp)
        tool_list = []
        for i in data:
            if data[i]['name'] == 'h':
                tool = Hole(data[i])
            elif data[i]['name'] == 'v':
                tool = Hole(data[i])
            elif data[i]['name'] == 'ys':
                tool = YokeSplitter(data[i])
            elif data[i]['name'] == 'fm45':
                tool = Fm45(data[i])
            elif data[i] == 'fp45':
                tool = Fp45(data[i])
            else:
                print('Unrecognized tool. Please check json.')
                sys.exit()
            tool_list.append(tool)
        self.tool_list = tool_list
                
        
    def dumpCutProgram(self,tl):
        data = {}
        names = os.listdir('../cut_program_input/split_yoke/')
        name = ''
        while True:
            name =  input('Enter file name (without extension): ')
            if name.endswith('.json'):
                print('Do not enter the extension.')
                continue
            if name == 'q':
                sys.exit()
            if name in names:
                con = input('File name already exists. Do you want to overwrite ? (y or n) - ')
                if con == 'y':
                    break
                continue
            break
            
        with open('../cut_program_input/split_yoke/'+name+'.json', 'w') as fp:
            for i in range(len(tl)):
                data[i] = vars(tl[i])
            fp.write(json.dumps(data, indent=4))
                    
        
    def getToolList(self):
        
        tool_list = []
        counter = 0
        while counter < 2:
            
            tool_name = input('Enter tool name : ')
            if tool_name=='fp45':
                counter+=1
                tool = Fp45()
                tool.getSlpCount()
                if tool.hasStepLap():
                    tool.getSlpDistance()
                    tool.getOpen()
                    tool.generateSlpVector()
                
            elif tool_name == 'fm45':
                counter += 1
                tool = Fm45()
                tool.getSlpCount()
                if tool.hasStepLap():
                    tool.getSlpDistance()
                    tool.getOpen()
                    tool.generateSlpVector()

            elif tool_name == 'h':
                tool = Hole()
                
            elif tool_name == 'ys':
                tool = YokeSplitter()
                tool.getSlpCount()
                if tool.slp_count > 1:
                    tool.getSlpDistance()
                    tool.getFrontOpen()
                    tool.generateSlpVector()
                    
            else :
                print('Invalid tool name.')
                continue
                
            tool_list.append(tool)
            
        if tool_list[0].name != tool_list[-1].name:
            print('Start tool - end tool mismatch. Aborting ...')
            sys.exit()
        self.tool_list = tool_list
        self.dumpCutProgram(tool_list)
        
        con = input('Continue execution ? : ').lower()
        if con == 'y' or con == 'yes':
            return
        sys.exit()
        
    def getLengthList(self):
        self.length_list = [float(i) for i in input('Enter lengths : ').split()]
        
    def getLayers(self):
        self.layers = int(input('Enter no. of layers : '))
        
    def updateLengths(self):
        slp = max([i.slp_count for i in self.tool_list if i.hasStepLap()])
        ll = []
        for i in range(slp):
            for j in range(len(self.length_list)):
                curr = self.tool_list[j]
                if curr.hasStepLap():
                    if isinstance(curr, YokeSplitter):
                        ll[-1][1] += curr.slp_vector[curr.slp_counter]
                        ll.append([curr.name, self.length_list[j] - curr.slp_vector[curr.slp_counter]])
                        curr.incrementSlpCounter()
                        
                    elif isinstance(curr, Fm45) or isinstance(curr, Fp45):
                        ll.append([curr.name, self.length_list[j] + curr.slp_vector[curr.slp_counter]])
                        curr.incrementSlpCounter()
                else:
                    ll.append([curr.name, self.length_list[j]])
                
                if j == len(self.length_list) - 1:
                    curr = self.tool_list[j+1]
                    if curr.hasStepLap():
                        if isinstance(curr, Fm45) or isinstance(curr, Fp45):
                            ll[-1][1] += curr.slp_vector[curr.slp_counter]
                            curr.incrementSlpCounter()
                
            #ll = self.layers
        print('executable len')
        print(ll)
        print('-------')
        self.exe_l = ll
        
    def execute(self):
        exe = []
        pos = 0
        for i in self.exe_l:
            if i[0] == 'h':
                exe.append([i[0], pos + 1250])
            elif i[0] == 'ys':
                exe.append(['fp45', pos + 4335])
                exe.append(['v', pos])
            elif i[0][0] == 'f':
                exe.append([i[0], pos + 4335])
                
            pos += i[1]
        self.pl = pos
        print(exe)
        terminate = 300
        
        operation = []
        feed = []
        while terminate > 0:
            closest_cut = min([i[1] for i in exe])
            repeat = False
            for i in exe:
                if i[1] == closest_cut:
                    operation.append(i[0])
                    i[1] = self.pl
                    
                    if repeat:
                        feed.append(0)
                    else:
                        feed.append(closest_cut)
                        repeat = True
                else:
                    i[1] -= closest_cut
                    
            terminate -= 1
        data = list(zip(feed, operation))
        df = pd.DataFrame(data = data, columns=['feed', 'operation'])
        df.to_csv('../cut_program_output/split_yoke.csv')
       
        
       
        
def main():
    while True:
        cmd = input('\n 1 - CLI.\n 2 - Json encoded file.\n Enter Option : ')
        if cmd == '1':
            jp = JobProfile()
            jp.getLengthList()
            jp.getLayers()
            jp.updateLengths()
            jp.execute()
            return
        elif cmd == '2':
            jp = JobProfile(1)
            jp.getLengthList()
            jp.getLayers()
            jp.updateLengths()
            jp.execute()
            return
        elif cmd == 'q':
            return
        else:
            print('Incorrect option.')
            
            
if __name__ == "__main__":
    main()
                
                
                